#!/usr/bin/env python3
"""Collect real StakTrakr public 15-minute snapshot quotes for four metals.

Archive 2026-08 onward; separate, revision-preserving RESEARCH_ONLY Neon table.
Not from daily seed averages. The 'source=seed' field is the v1 exporter
label for Turso 15m spot_prices rows, NOT proof of a prospective capture.
No future leakage, synthetic missing hours, canonical overwrites, or trades.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date,datetime,timedelta,timezone
from decimal import Decimal
from hashlib import sha256
import json,os,sys
from pathlib import Path
from urllib.request import Request,urlopen

CODES={"Gold":"AU","Silver":"AG","Platinum":"PT","Palladium":"PD"}
FLOOR=date(2026,8,1)
URL="https://raw.githubusercontent.com/lbruton/StakTrakrApi/api/data/15min"
BACKUP="https://api.staktrakr.com/data/15min"
TABLE="gold_weekly_live.staktrakr_fourmetal_15m_snapshot_research_v1"
EVIDENCE="STAKTRAKR_PUBLIC_15M_SPOT_SNAPSHOT_RESEARCH_NOT_FIRSTPRINT"

DDL="""
CREATE TABLE IF NOT EXISTS gold_weekly_live.staktrakr_fourmetal_15m_snapshot_research_v1 (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  metal text NOT NULL CHECK(metal IN ('AU','AG','PT','PD')),
  window_start_utc timestamptz NOT NULL,
  source_quote_timestamp_utc timestamptz NOT NULL,
  spot_usd_oz numeric NOT NULL CHECK(spot_usd_oz>0),
  source_label text NOT NULL,
  provider_label text NOT NULL,
  raw_source_url text NOT NULL,
  snapshot_sha256 text NOT NULL,
  row_sha256 text NOT NULL,
  collected_at_utc timestamptz NOT NULL DEFAULT now(),
  evidence_class text NOT NULL DEFAULT 'STAKTRAKR_PUBLIC_15M_SPOT_SNAPSHOT_RESEARCH_NOT_FIRSTPRINT',
  original_firstprint_certified boolean NOT NULL DEFAULT false CHECK (original_firstprint_certified=false),
  UNIQUE(metal,window_start_utc,row_sha256)
)
"""
INSERT="""
INSERT INTO gold_weekly_live.staktrakr_fourmetal_15m_snapshot_research_v1(
metal,window_start_utc,source_quote_timestamp_utc,spot_usd_oz,source_label,
provider_label,raw_source_url,snapshot_sha256,row_sha256,evidence_class,
original_firstprint_certified)
SELECT metal,window_start_utc,source_quote_timestamp_utc,spot_usd_oz,source_label,
provider_label,raw_source_url,snapshot_sha256,row_sha256,
'STAKTRAKR_PUBLIC_15M_SPOT_SNAPSHOT_RESEARCH_NOT_FIRSTPRINT',false
FROM jsonb_to_recordset(%s::jsonb) AS v(
metal text,window_start_utc timestamptz,source_quote_timestamp_utc timestamptz,
spot_usd_oz numeric,source_label text,provider_label text,raw_source_url text,
snapshot_sha256 text,row_sha256 text)
ON CONFLICT(metal,window_start_utc,row_sha256) DO NOTHING
"""

def source_paths(day, minute):
    hhmm=f"{minute//60:02}{minute%60:02}"
    part=f"{day:%Y/%m/%d}/{hhmm}.json"
    return f"{URL}/{part}", f"{BACKUP}/{part}"

def get_source(day, minute):
    errors=[]
    for url in source_paths(day,minute):
        try:
            req=Request(url,headers={"User-Agent":"GoldControl-StakTrakr-15m-Research/1.0","Accept":"application/json"})
            with urlopen(req,timeout=12) as resp:
                data=resp.read(15_001)
            if not (100<len(data)<15_000):raise ValueError("BAD_BLOB_SIZE")
            return data,url
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:55]}")
    raise RuntimeError("; ".join(errors))

def check_day(day):
    if day<FLOOR or day>=datetime.now(timezone.utc).date():
        raise ValueError("DAY_NOT_IN_SOURCE_ARCHIVE_OR_INCOMPLETE")

def validate_snapshot(day,minute,data,url):
    if minute<0 or minute>=24*60 or minute%15:raise ValueError("BAD_QUARTER_HOUR")
    records=json.loads(data)
    if not isinstance(records,list):raise ValueError("NOT_ARRAY")
    label=day.isoformat()+" "+f"{minute//60:02}:{minute%60:02}"
    time_start=datetime.fromisoformat(label+":00+00:00")
    seen=set()
    rows=[]
    digest=sha256(data).hexdigest()
    for r in records:
        if not isinstance(r,dict) or r.get("metal") not in CODES:continue
        m=CODES[r["metal"]]
        if m in seen:raise ValueError("DUPLICATE_METAL_SNAPSHOT")
        seen.add(m)
        stamp=str(r.get("timestamp",""))
        quote=datetime.fromisoformat(stamp.replace("Z","+00:00"))
        if quote.tzinfo is None:quote=quote.replace(tzinfo=timezone.utc)
        if not(time_start<=quote<time_start+timedelta(minutes=15)):
            raise ValueError("QUOTE_OUTSIDE_15M_WINDOW")
        price=Decimal(str(r["spot"]))
        if not price.is_finite() or price<=0:raise ValueError("INVALID_PRICE")
        source=str(r.get("source") or "")
        provider=str(r.get("provider") or "")
        if not source or not provider:raise ValueError("MISSING_UPSTREAM_LABEL")
        canonical=[m,time_start.isoformat(),quote.isoformat(),format(price,"f"),source,provider]
        rowsha=sha256(json.dumps(canonical,separators=(",",":")).encode()).hexdigest()
        rows.append({"metal":m,"window_start_utc":time_start.isoformat(),
                     "source_quote_timestamp_utc":quote.isoformat(),
                     "spot_usd_oz":format(price,"f"),"source_label":source,
                     "provider_label":provider,"raw_source_url":url,
                     "snapshot_sha256":digest,"row_sha256":rowsha})
    if set(seen)!=set(CODES.values()):raise ValueError("NOT_FOUR_METAL_ALIGNED_SNAPSHOT")
    return rows

def fetch_one(t):
    d,q=t
    try:
        blob,url=get_source(d,q)
        return validate_snapshot(d,q,blob,url),None
    except Exception as exc:
        return [],{"day":str(d),"hhmm":f"{q//60:02}{q%60:02}",
                   "error":type(exc).__name__+":"+str(exc)[:120]}

def collect(start,end,workers):
    for dt in (start,end):check_day(dt)
    if start>end:raise ValueError("END_BEFORE_START")
    ndays=(end-start).days+1
    tasks=[(start+timedelta(days=i),q)
           for i in range(ndays) for q in range(0,24*60,15)]
    good=[]; bad=[]; n=0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(fetch_one,t) for t in tasks]
        for f in as_completed(futures):
            part,error=f.result()
            if error:bad.append(error)
            else:good.extend(part)
            n+=1
            if n%800==0:
                print(f"15M_SOURCE_SCAN {n}/{len(tasks)} snapshots, "
                      f"{len(good)} aligned metal rows, rejected={len(bad)}",flush=True)
    return good,bad,len(tasks)

def apply(rows):
    import psycopg
    uri=os.environ.get("NEON_DATABASE_URL","").strip()
    if not uri:raise RuntimeError("MISSING_NEON_DATABASE_URL")
    count=0
    with psycopg.connect(uri,connect_timeout=20) as db:
        with db.cursor() as c:
            c.execute(DDL)
            for i in range(0,len(rows),1200):
                batch=json.dumps(rows[i:i+1200],separators=(",",":"))
                c.execute(INSERT,(batch,))
                count+=c.rowcount
        db.commit()
    return count

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",default="2026-08-01")
    p.add_argument("--end",default=(datetime.now(timezone.utc).date()-timedelta(days=1)).isoformat())
    p.add_argument("--workers",type=int,default=20)
    p.add_argument("--mode",choices=["probe","apply"],required=True)
    p.add_argument("--out",default="staktrakr-15min-fourmetal-research-report.json")
    a=p.parse_args()
    if not 1<=a.workers<=24:raise ValueError("WORKER_LIMIT")
    start,end=date.fromisoformat(a.start),date.fromisoformat(a.end)
    rows,bad,total=collect(start,end,a.workers)
    days=sorted({x["window_start_utc"][:10] for x in rows})
    report={"schema":"STAKTRAKR_FOUR_METAL_15M_RESEARCH_BACKFILL_V1",
       "source":"lbruton/StakTrakrApi/api/data/15min",
       "start":str(start),"end":str(end),"mode":a.mode,
       "attemptedSnapshots":total,"alignedSnapshots":len(rows)//4,
       "retainedMetalRows":len(rows),"datesWithData":len(days),
       "firstDate":days[0] if days else None,"lastDate":days[-1] if days else None,
       "rejectedSnapshots":len(bad),"rejectedExamples":bad[:50],
       "sourceFirstprintCertified":False,"dataQuality":"HISTORICAL_SOURCE_LABEL_SEED_IS_EXPORTER_LABEL",
       "canonicalDailyDataUnchanged":True,"tradeSignalsUnchanged":True,
       "staktrakrHourlyLedgerUnchanged":True,
       "recordsInserted":0}
    if len(rows)//4<max(1,int(total*.65)):
        report["status"]="REJECTED_LOW_SOURCE_COVERAGE"
    else:
        report["status"]="HISTORICAL_SOURCE_ACCEPTED_RESEARCH_ONLY"
    if a.mode=="apply" and report["status"]=="HISTORICAL_SOURCE_ACCEPTED_RESEARCH_ONLY":
        report["recordsInserted"]=apply(rows)
        report["status"]="HISTORICAL_15M_LEDGER_APPENDED_RESEARCH_ONLY"
    Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as fh:
            fh.write("## StakTrakr original 15-minute four-metal research archive\n")
            fh.write(f"Accepted {report['alignedSnapshots']}/{total} "
                     f"four-metal aligned snapshots; inserted {report['recordsInserted']} rows.\n")
            fh.write("No firstprint, no trading or model output changes.\n")
    return 0 if report["status"] in("HISTORICAL_SOURCE_ACCEPTED_RESEARCH_ONLY",
          "HISTORICAL_15M_LEDGER_APPENDED_RESEARCH_ONLY") else 2

if __name__=="__main__":
    sys.exit(main())
