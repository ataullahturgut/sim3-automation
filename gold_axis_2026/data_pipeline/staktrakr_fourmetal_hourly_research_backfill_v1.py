#!/usr/bin/env python3
"""Backfill *actual* StakTrakr v2 hourly OHLC(A), four metals, to separate Neon research ledger.

Published v2 hourly day files exist from 2026-03-25 for XAU/XAG/XPT/XPD.
They are NOT 15-minute source bars and must not be called 4*15m OHLC.
StakTrakr historical day-file fallbacks can consist of ONE daily quote;
reject these as fake 'hourly' history. Immutable evidence, no source overwrites.
NO retroactive firstprint certification, no live forecasts/signals, no trading.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

CODES={"xau":"AU","xag":"AG","xpt":"PT","xpd":"PD"}
DATE_FLOOR=date(2026,3,25)
RAW_ROOT="https://raw.githubusercontent.com/lbruton/StakTrakrApi/api/data/v2/spot"
API_ROOT="https://api.staktrakr.com/data/v2/spot"
TABLE="gold_weekly_live.staktrakr_fourmetal_hourly_ohlca_research_v1"
EVIDENCE="STAKTRAKR_V2_HOURLY_HISTORICAL_RESEARCH_NOT_FIRSTPRINT"

DDL="""
CREATE TABLE IF NOT EXISTS gold_weekly_live.staktrakr_fourmetal_hourly_ohlca_research_v1 (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 metal text NOT NULL CHECK (metal IN ('AU','AG','PT','PD')),
 bar_start_utc timestamptz NOT NULL,
 spot_open_usd_oz numeric NOT NULL CHECK (spot_open_usd_oz>0),
 spot_high_usd_oz numeric NOT NULL CHECK (spot_high_usd_oz>0),
 spot_low_usd_oz numeric NOT NULL CHECK (spot_low_usd_oz>0),
 spot_close_usd_oz numeric NOT NULL CHECK (spot_close_usd_oz>0),
 spot_avg_usd_oz numeric NOT NULL CHECK (spot_avg_usd_oz>0),
 source_samples integer NOT NULL CHECK (source_samples>=2),
 source_generated_utc timestamptz NOT NULL,
 source_date date NOT NULL,
 source_url text NOT NULL,
 source_blob_sha256 text NOT NULL,
 source_row_sha256 text NOT NULL,
 ingested_at_utc timestamptz NOT NULL DEFAULT now(),
 evidence_class text NOT NULL DEFAULT 'STAKTRAKR_V2_HOURLY_HISTORICAL_RESEARCH_NOT_FIRSTPRINT',
 original_firstprint_certified boolean NOT NULL DEFAULT false CHECK (original_firstprint_certified=false),
 UNIQUE (metal,bar_start_utc,source_row_sha256)
);
"""
INSERT="""
INSERT INTO gold_weekly_live.staktrakr_fourmetal_hourly_ohlca_research_v1
(metal,bar_start_utc,spot_open_usd_oz,spot_high_usd_oz,spot_low_usd_oz,
 spot_close_usd_oz,spot_avg_usd_oz,source_samples,source_generated_utc,
 source_date,source_url,source_blob_sha256,source_row_sha256,evidence_class,
 original_firstprint_certified)
SELECT metal,bar_start_utc,spot_open_usd_oz,spot_high_usd_oz,spot_low_usd_oz,
       spot_close_usd_oz,spot_avg_usd_oz,source_samples,source_generated_utc,
       source_date,source_url,source_blob_sha256,source_row_sha256,
       'STAKTRAKR_V2_HOURLY_HISTORICAL_RESEARCH_NOT_FIRSTPRINT', false
FROM jsonb_to_recordset(%s::jsonb) AS v(
 metal text,bar_start_utc timestamptz,
 spot_open_usd_oz numeric,spot_high_usd_oz numeric,spot_low_usd_oz numeric,
 spot_close_usd_oz numeric,spot_avg_usd_oz numeric,
 source_samples integer,source_generated_utc timestamptz,source_date date,
 source_url text,source_blob_sha256 text,source_row_sha256 text)
ON CONFLICT (metal,bar_start_utc,source_row_sha256) DO NOTHING
"""
def fail_if_bad_date(dt):
    if dt<DATE_FLOOR or dt>=datetime.now(timezone.utc).date():
        raise ValueError("DATE_BEFORE_REAL_HOURLY_SOURCE_FLOOR_OR_NOT_CLOSED")

def _urls(metal: str, day: date):
    part=f"{metal}/{day:%Y/%m/%d}.json"
    return [f"{RAW_ROOT}/{part}",f"{API_ROOT}/{part}"]

def get_raw(metal: str, day: date):
    errors=[]
    for url in _urls(metal,day):
        try:
            request=Request(url,headers={"Accept":"application/json",
                       "User-Agent":"GoldResearch-StakTrakr-4metal-hourly-20261030/1.0"})
            with urlopen(request,timeout=16) as response:
                raw=response.read(150_001)
                if not (50<=len(raw)<=150_000):
                    raise ValueError("BAD_SOURCE_SIZE")
                return raw,url
        except (Exception) as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:75]}")
    raise RuntimeError(";".join(errors))

def validate_day(metal: str, day: date, payload: bytes, source_url: str):
    if metal not in CODES: raise ValueError("UNKNOWN_METAL")
    blob=json.loads(payload)
    if not isinstance(blob,dict) or blob.get("v")!=2:
        raise ValueError("NOT_STAKTRAKR_V2_ENVELOPE")
    published=blob.get("generated_at")
    if not isinstance(published,str):raise ValueError("NO_SOURCE_GENERATED_TIME")
    gen=datetime.fromisoformat(published.replace("Z","+00:00"))
    if gen.tzinfo is None or gen.astimezone(timezone.utc).date()!=day:
        raise ValueError("GENERATED_DATE_DOES_NOT_MATCH_SOURCE_DAY")
    obs=blob.get("data")
    if not isinstance(obs,list) or not obs:raise ValueError("NO_HOURLY_SAMPLES")
    if len(obs)<8:
        raise ValueError("HOURLY_DATA_TOO_SPARSE_OR_DAILY_PLACEHOLDER")
    unique=set(); rows=[]; bad=0; source_sha=sha256(payload).hexdigest()
    for entry in obs:
        if not isinstance(entry,dict):raise ValueError("BAD_HOURLY_ENTRY")
        ts=datetime.fromisoformat(str(entry.get("t","")).replace("Z","+00:00"))
        if ts.tzinfo is None or ts.astimezone(timezone.utc).date()!=day or ts.minute!=0 or ts.second!=0:
            raise ValueError("HOUR_TIMESTAMP_INVALID")
        if ts in unique:raise ValueError("DUPLICATE_HOUR_IN_ONE_SOURCE")
        unique.add(ts)
        n=entry.get("n")
        if isinstance(n,bool) or not isinstance(n,int):raise ValueError("BAD_SAMPLE_COUNT")
        # n=1 may be derived from a DAILY backfill (explicit StakTrakr documentation).
        if n<2:
            bad+=1
            continue
        try:
            prices=[Decimal(str(entry[k])) for k in ("open","high","low","close","avg")]
        except (KeyError,InvalidOperation,TypeError) as exc:
            raise ValueError("INVALID_OHLC_PRICE") from exc
        o,h,l,c,avg=prices
        if any(not v.is_finite() or v<=0 for v in prices):
            raise ValueError("NONPOSITIVE_OR_NONFINITE_PRICE")
        if not (l<=o<=h and l<=c<=h and l<=avg<=h):
            raise ValueError("OHLC_PRICE_INCONSISTENT")
        if ts+timedelta(hours=1)>gen+timedelta(minutes=10):
            raise ValueError("HOUR_AFTER_SOURCE_GENERATION")
        fields=[CODES[metal],ts.isoformat(),*[format(v,"f") for v in prices],n,gen.isoformat()]
        rowhash=sha256(json.dumps(fields,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        rows.append({"metal":CODES[metal],"bar_start_utc":ts.isoformat(),
                     "spot_open_usd_oz":format(o,"f"),"spot_high_usd_oz":format(h,"f"),
                     "spot_low_usd_oz":format(l,"f"),"spot_close_usd_oz":format(c,"f"),
                     "spot_avg_usd_oz":format(avg,"f"),"source_samples":n,
                     "source_generated_utc":gen.isoformat(),"source_date":day.isoformat(),
                     "source_url":source_url,"source_blob_sha256":source_sha,
                     "source_row_sha256":rowhash})
    if len(rows)<6:
        raise ValueError("TOO_FEW_REAL_HOURLY_ROWS_REJECTED_DAILY_BACKFILL")
    return rows,{"metal":metal,"day":str(day),"retained":len(rows),"oneSampleSkipped":bad,
                 "sourceSha256":source_sha,"sourceGeneratedAt":gen.isoformat()}

def collect_job(t):
    metal,day=t
    try:
        raw,url=get_raw(metal,day)
        rows,meta=validate_day(metal,day,raw,url)
        return rows,meta,None
    except Exception as exc:
        return [],None,{"metal":metal,"date":str(day),
                         "error":type(exc).__name__+":"+str(exc)[:140]}

def collect(start:date,end:date,workers:int):
    if end<start:raise ValueError("END_BEFORE_START")
    for d in (start,end):fail_if_bad_date(d)
    all_dates=[start+timedelta(days=i) for i in range((end-start).days+1)]
    tasks=[(metal,day) for day in all_dates for metal in CODES]
    rows=[]; metas=[]; missing=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fs=[pool.submit(collect_job,t) for t in tasks]
        for i,f in enumerate(as_completed(fs),1):
            rr,meta,error=f.result()
            rows.extend(rr)
            if meta:metas.append(meta)
            if error:missing.append(error)
            if i%100==0:
                print(f"SOURCE_SCAN {i}/{len(tasks)} files, {len(rows)} real hourly bars,"
                      f" {len(missing)} missing/rejected files",flush=True)
    return rows,metas,missing,len(tasks)

def apply(rows):
    import psycopg
    uri=os.environ.get("NEON_DATABASE_URL","").strip()
    if not uri:raise RuntimeError("NEON_DATABASE_URL_MISSING")
    if not rows: raise ValueError("NO_VALID_ROWS")
    total=0
    with psycopg.connect(uri,connect_timeout=20) as db:
        with db.cursor() as cur:
            cur.execute(DDL)
            for i in range(0,len(rows),900):
                batch=json.dumps(rows[i:i+900],separators=(",",":"))
                cur.execute(INSERT,(batch,))
                total+=cur.rowcount
        db.commit()
    return total

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",default="2026-03-25")
    p.add_argument("--end",default=(datetime.now(timezone.utc).date()-timedelta(days=1)).isoformat())
    p.add_argument("--workers",type=int,default=14)
    p.add_argument("--mode",choices=["probe","apply"],required=True)
    p.add_argument("--out",default="staktrakr-fourmetal-hourly-2026-source-report.json")
    args=p.parse_args()
    if not (1<=args.workers<=20):raise ValueError("MAX_WORKERS_20")
    start,end=date.fromisoformat(args.start),date.fromisoformat(args.end)
    rows,metas,missing,files=collect(start,end,args.workers)
    days={m["day"] for m in metas}
    full=[d for d in sorted(days) if all(any(x["metal"]==metal and x["day"]==d for x in metas)
                                     for metal in CODES)]
    counts={metal:sum(1 for x in rows if x["metal"]==code) for metal,code in CODES.items()}
    report={
      "schema":"STAKTRAKR_2026_4METAL_TRUE_HOURLY_RESEARCH_INGEST_V1",
      "mode":args.mode,"start":str(start),"end":str(end),
      "attemptedFiles":files,"acceptedFiles":len(metas),
      "rejectedFiles":len(missing),"acceptedBars":len(rows),
      "barsByMetal":counts,"completeFourMetalDays":len(full),
      "firstCompleteFourMetalDay":full[0] if full else None,
      "lastCompleteFourMetalDay":full[-1] if full else None,
      "criticalDays":{str(d):str(d) in full for d in (date(2026,5,27),date(2026,5,28),
                                                     date(2026,9,16)) if start<=d<=end},
      "oneSampleBarsSkipped":sum(x["oneSampleSkipped"] for x in metas),
      "missingOrRejected":missing[:150],
      "rejectedTruncated":len(missing)>150,
      "origin":"lbruton/StakTrakrApi api branch public v2 spot OHLCA archive",
      "underlyingFeed":"StakTrakr MetalPriceAPI polled spot; NOT exchange-traded closing price",
      "resolution":"hourly aggregated OHLC from up to four 15-minute samples",
      "historicalBackfillNotFirstprint":True,
      "verifiedProspectiveCapture":False,
      "riskEngineModified":False,"liveSignalProduced":False,
      "canonicalDailyTablesModified":False,"ordersCreated":False,
      "rowsInserted":0,
    }
    if len(metas)<max(3,int(files*.70)):
        report["status"]="BLOCKED_TOO_MANY_MISSING_HOURLY_SOURCE_FILES"
    elif report["criticalDays"] and not all(report["criticalDays"].values()):
        report["status"]="BLOCKED_CRITICAL_EVENT_DATE_MISSING_FOUR_METAL_ALIGNMENT"
    else:
        report["status"]="RESEARCH_SOURCE_ACCEPTED_NOT_PIT"
    if args.mode=="apply" and report["status"]=="RESEARCH_SOURCE_ACCEPTED_NOT_PIT":
        report["rowsInserted"]=apply(rows)
        report["status"]="RESEARCH_HOURLY_LEDGER_APPENDED_NOT_PIT"
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as fh:
            fh.write(f"## Four metal StakTrakr REAL hourly OHLC research collection\n\n")
            fh.write(f"Source days {start} .. {end}; accepted: {len(metas)}/{files} files; "
                     f"{len(rows)} real hourly bars, {len(full)} shared days\n\n")
            fh.write(f"Written {report['rowsInserted']} immutable research rows. "
                     f"**No firstprint or live issue.**\n")
    return 0 if report["status"] in ("RESEARCH_SOURCE_ACCEPTED_NOT_PIT",
                                   "RESEARCH_HOURLY_LEDGER_APPENDED_NOT_PIT") else 2

if __name__=="__main__":
    sys.exit(main())
