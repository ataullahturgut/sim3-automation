#!/usr/bin/env python3
"""V46 PROSPECTIVE source-observation ledger, NEVER a live trading signal.

Polls public StakTrakr 15m snapshots, appends observed timestamp in Neon when
OUR collector first sees the quote; original provider-firstprint remains UNKNOWN.
2026 historical 15m backfills are NEVER retroactively called first observed.

IMPORTANT: the existing V22 risk shadow is is_production_signal=false.
Therefore this collector MUST NOT emit BUY/SELL/EXIT or promote V22, even if
4 metals and a 15m price are fresh. It records price provenance & readiness.
"""
from __future__ import annotations
import argparse,json,hashlib,os,sys
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from gold_axis_2026.data_pipeline.staktrakr_fourmetal_15min_research_ingest_v1 import (
  get_source,validate_snapshot,CODES
)
UTC=timezone.utc
NY=ZoneInfo("America/New_York")
SCHEMA="gold_weekly_live"
TABLE="gold_weekly_live.staktrakr_firstseen_15m_collector_shadow_v1"
EVIDENCE="FIRST_OBSERVED_COLLECTOR_NOT_PROVIDER_FIRSTPRINT"
MAX_AGE_SECONDS=45*60
MAX_CLOCK_FUTURE_SECONDS=30
CANDIDATE_WINDOWS=5
DDL="""
CREATE TABLE IF NOT EXISTS gold_weekly_live.staktrakr_firstseen_15m_collector_shadow_v1(
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 metal text NOT NULL CHECK(metal IN ('AU','AG','PT','PD')),
 window_start_utc timestamptz NOT NULL,
 source_quote_timestamp_utc timestamptz NOT NULL,
 spot_usd_oz numeric NOT NULL CHECK(spot_usd_oz>0),
 source_row_sha256 text NOT NULL CHECK(source_row_sha256~'^[0-9a-f]{64}$'),
 source_snapshot_sha256 text NOT NULL CHECK(source_snapshot_sha256~'^[0-9a-f]{64}$'),
 quote_source_url text NOT NULL,
 source_label text NOT NULL,
 provider_label text NOT NULL,
 first_observed_utc timestamptz NOT NULL DEFAULT now(),
 market_open_at_observation boolean NOT NULL,
 source_age_seconds_at_observation integer NOT NULL,
 source_recent_at_observation boolean NOT NULL,
 provenance_class text NOT NULL DEFAULT
 'FIRST_OBSERVED_COLLECTOR_NOT_PROVIDER_FIRSTPRINT',
 original_provider_firstprint_certified boolean NOT NULL DEFAULT false
    CHECK(original_provider_firstprint_certified=false),
 is_production_signal boolean NOT NULL DEFAULT false
    CHECK(is_production_signal=false),
 UNIQUE(metal,window_start_utc,source_row_sha256)
)
"""
INSERT="""
INSERT INTO gold_weekly_live.staktrakr_firstseen_15m_collector_shadow_v1(
 metal,window_start_utc,source_quote_timestamp_utc,spot_usd_oz,
 source_row_sha256,source_snapshot_sha256,quote_source_url,
 source_label,provider_label,market_open_at_observation,
 source_age_seconds_at_observation,source_recent_at_observation,
 provenance_class,original_provider_firstprint_certified,is_production_signal
) SELECT metal,window_start_utc,source_quote_timestamp_utc,spot_usd_oz,
 source_row_sha256,source_snapshot_sha256,quote_source_url,
 source_label,provider_label,market_open_at_observation,
 source_age_seconds_at_observation,source_recent_at_observation,
 'FIRST_OBSERVED_COLLECTOR_NOT_PROVIDER_FIRSTPRINT',false,false
 FROM jsonb_to_recordset(%s::jsonb) AS v(
  metal text,window_start_utc timestamptz,
  source_quote_timestamp_utc timestamptz,spot_usd_oz numeric,
  source_row_sha256 text,source_snapshot_sha256 text,quote_source_url text,
  source_label text,provider_label text,market_open_at_observation boolean,
  source_age_seconds_at_observation integer,source_recent_at_observation boolean
 )
 ON CONFLICT(metal,window_start_utc,source_row_sha256) DO NOTHING
"""
LATEST_RISK="""
SELECT origin_date,scenario,effective_review,recorded_utc,is_production_signal,
       evidence_class
FROM gold_weekly_live.staktrakr_v22_risk_shadow_v1
ORDER BY recorded_utc DESC LIMIT 12
"""
COUNTS="""
SELECT metal,count(*),min(first_observed_utc),max(first_observed_utc),
 count(*) FILTER(WHERE source_recent_at_observation AND market_open_at_observation)
FROM gold_weekly_live.staktrakr_firstseen_15m_collector_shadow_v1
GROUP BY 1 ORDER BY 1
"""

def market_open(ts):
    """Conservative FX market-hours gate at 17:00 America/New_York."""
    x=ts.astimezone(NY)
    weekday=x.weekday() # Monday 0, Friday 4, Sunday 6
    if weekday==5:return False
    if weekday==6:return x.hour>=17
    if weekday==4:return x.hour<17
    return True

def windows(now):
    if now.tzinfo is None:raise ValueError("UTC_AWARE_TIME_REQUIRED")
    now=now.astimezone(UTC)
    floor=now.replace(minute=(now.minute//15)*15,second=0,microsecond=0)
    # At +7m offset the previous *completed* window is floor-15min.
    return [floor-timedelta(minutes=15*i) for i in range(1,CANDIDATE_WINDOWS+1)]

def quality(now,quote_utc):
    if now.tzinfo is None or quote_utc.tzinfo is None:raise ValueError("NAIVE_TIMESTAMP")
    delta=int((now-quote_utc).total_seconds())
    if delta < -MAX_CLOCK_FUTURE_SECONDS:raise ValueError("SOURCE_TIMESTAMP_FUTURE")
    is_market_open=market_open(quote_utc) and market_open(now)
    recent=(0<=delta<=MAX_AGE_SECONDS)
    return {"ageSeconds":delta,"marketOpen":is_market_open,
            "recent":recent,"eligibleForFutureMonitoring":recent and is_market_open}

def retrieve(now):
    errors=[]
    for w in windows(now):
        # At first run we do NOT backfill older windows into prospective
        # table unless that exact quote is first observed now. Age recorded.
        try:
            blob,url=get_source(w.date(),w.hour*60+w.minute)
            vals=validate_snapshot(w.date(),w.hour*60+w.minute,blob,url)
            if len(vals)!=4:raise ValueError("INCOMPLETE_METALS")
            examined=[]
            for v in vals:
                quote=datetime.fromisoformat(v["source_quote_timestamp_utc"])
                examined.append(quality(now,quote))
            if any(x["ageSeconds"] < -MAX_CLOCK_FUTURE_SECONDS for x in examined):
                raise ValueError("QUOTE_FUTURE")
            entries=[]
            for v,q in zip(vals,examined):
                entries.append({
                  "metal":v["metal"],"window_start_utc":v["window_start_utc"],
                  "source_quote_timestamp_utc":v["source_quote_timestamp_utc"],
                  "spot_usd_oz":v["spot_usd_oz"],
                  "source_row_sha256":v["row_sha256"],
                  "source_snapshot_sha256":v["snapshot_sha256"],
                  "quote_source_url":v["raw_source_url"],
                  "source_label":v["source_label"],
                  "provider_label":v["provider_label"],
                  "market_open_at_observation":q["marketOpen"],
                  "source_age_seconds_at_observation":q["ageSeconds"],
                  "source_recent_at_observation":q["recent"]
                })
            return entries,{"quoteWindow":w.isoformat(),
                "quoteUrl":url,"quotes":{v["metal"]:{
                   "spot":v["spot_usd_oz"],
                   **q} for v,q in zip(vals,examined)},
                "sourceSnapshotHash":hashlib.sha256(blob).hexdigest()},errors
        except Exception as e:
            errors.append({"window":w.isoformat(),"reason":type(e).__name__,
                           "message":str(e)[:180]})
    return [],None,errors

def apply(rows):
    import psycopg
    uri=os.getenv("NEON_DATABASE_URL","").strip()
    if not uri:raise RuntimeError("MISSING_NEON_DATABASE_URL")
    with psycopg.connect(uri,connect_timeout=20) as db:
        with db.cursor() as c:
            c.execute(DDL)
            if rows:
                c.execute(INSERT,(json.dumps(rows,separators=(",",":")),))
                inserted=c.rowcount
            else:inserted=0
            c.execute(LATEST_RISK)
            risk=[
              {"origin":str(r[0]),"scenario":r[1],
               "alert":bool(r[2]),"recorded":r[3].isoformat(),
               "production":bool(r[4]),"evidence":r[5]}
              for r in c.fetchall()
            ]
            c.execute(COUNTS)
            stat=[{"metal":r[0],"rows":r[1],
                "firstSeen":str(r[2]),"lastSeen":str(r[3]),
                "marketOpenRecentRows":r[4]} for r in c.fetchall()]
        db.commit()
    # At present this table contains only retrospective shadow risk models;
    # it cannot activate a live V22 gated EXIT (regardless of recency).
    gate="BLOCKED_NO_PRODUCTION_QUALIFIED_V22" if not any(
            x["production"] and x["alert"] for x in risk) else (
            "RISK_SOURCE_UNVERIFIED_FIRSTPRINT_BLOCKED")
    return inserted,risk,stat,gate

def run(mode,now,out):
    vals,source,errors=retrieve(now)
    record={
       "schema":"GOLD_V46_FIRST_OBSERVED_15M_SOURCE_AND_V22_FAIL_CLOSED_GATE",
       "collectorNowUTC":now.isoformat(),
       "mode":mode,
       "status":"NO_PUBLISHED_SNAPSHOT" if not vals else "SOURCE_OBSERVED",
       "marketReady":bool(source and
          all(v["eligibleForFutureMonitoring"] for v in source["quotes"].values())),
       "providerFirstprintCertified":False,
       "collectorFirstSeenMayBeLaterThanPublisher":True,
       "priceSource":"StakTrakr API four-metal 15min public price snapshots",
       "v22RiskProductionQualified":False,
       "v22ReadinessGate":"BLOCKED_NO_QUALIFIED_ORIGINAL_V22_FIRSTPRINT",
       "productionExitSignalsGenerated":0,
       "buySignalsGenerated":0,"ordersSent":0,
       "sourceEvidence":source,
       "fetchErrors":errors,
       "rowsInserted":0,"researchLedgerCounts":None
    }
    if mode=="apply":
        inserted,risk,stats,gate=apply(vals)
        record["rowsInserted"]=inserted
        record["researchLedgerCounts"]=stats
        record["v22ReadinessGate"]=gate
        record["v22LatestShadowRecord"]=risk[0] if risk else None
        record["status"]="APPENDED_COLLECTOR_OBSERVATION" if inserted else (
            "DEDUP_NO_NEW_ROWS" if vals else "NO_PUBLISHED_SNAPSHOT")
    Path(out).write_text(json.dumps(record,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
    print(json.dumps(record,ensure_ascii=False,indent=2,default=str),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## Gold 15m first OBSERVED research source capture (NOT firstprint)\n\n")
            f.write(f"Collector now {now.isoformat()}, status {record['status']}, "
                    f"new metal rows {record['rowsInserted']}.\n\n")
            f.write(f"V22 gate **{record['v22ReadinessGate']}**; "
                    "no exit/buy/trades. No provider-firstprint certification.\n")
    return record

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("probe","apply"),required=True)
    p.add_argument("--out",default="gold-firstobserved-15m-readiness-report.json")
    args=p.parse_args()
    run(args.mode,datetime.now(UTC),args.out)
if __name__=="__main__":main()
