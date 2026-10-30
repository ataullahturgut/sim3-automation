#!/usr/bin/env python3
"""Official CFTC keyless disaggregated futures-only GC/SI -> isolated Neon ledger.

Rows in this source are Tuesday report dates, normally published Friday. We
never infer earlier firstprints: earliest_model_use_date is the later of
report+7d (original conservative proxy) and first actual UTC retrieval date.
Append-only revision-aware rows. Missing paired markets abort.
"""
import argparse
import hashlib
import json
import os
from datetime import date,datetime,timedelta,timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

ENDPOINT="https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
CODES={"088691":"GC","084691":"SI"}

def require(v,k):
    if not v: raise ValueError("CFTC_OFFICIAL_INGEST_"+k)

def fetch_rows(now):
    query={"$where":"cftc_contract_market_code in('088691','084691') AND report_date_as_yyyy_mm_dd >= '2026-08-01T00:00:00'",
           "$order":"report_date_as_yyyy_mm_dd DESC","$limit":"140"}
    url=ENDPOINT+"?"+urlencode(query)
    req=Request(url,headers={"User-Agent":"Gold-Control-Official-CFTC-COT/1.0",
                             "Accept":"application/json"})
    with urlopen(req,timeout=40) as res:
        raw=res.read(2_000_001)
    require(100<len(raw)<2_000_000,"OVERSIZE_OR_EMPTY")
    payload=json.loads(raw)
    require(isinstance(payload,list),"NOT_LIST")
    seen={}
    for item in payload:
        code=str(item["cftc_contract_market_code"])
        require(code in CODES,"UNEXPECTED_MARKET")
        m=CODES[code]
        d=date.fromisoformat(item["report_date_as_yyyy_mm_dd"][:10])
        require(d.weekday()==1 and d<now.date(),"REPORT_NOT_COMPLETED_TUESDAY")
        oi=Decimal(str(item["open_interest_all"]))
        lng=Decimal(str(item["m_money_positions_long_all"]))
        sh=Decimal(str(item["m_money_positions_short_all"]))
        require(oi>0 and lng>=0 and sh>=0,"INVALID_POSITION")
        require(all(x.is_finite() for x in (oi,lng,sh)),"NONFINITE")
        row_sha=hashlib.sha256(json.dumps(item,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        k=(d,m)
        require(k not in seen,"DUPLICATE_WEEKLY_REPORT")
        first=now.date()
        conservative=d+timedelta(days=7)
        usable=max(first,conservative)
        seen[k]={"market":m,"contract_code":code,
                 "report_date":d.isoformat(),
                 "open_interest":str(oi),
                 "managed_money_long":str(lng),
                 "managed_money_short":str(sh),
                 "managed_money_net_over_oi":str((lng-sh)/oi),
                 "managed_money_short_over_oi":str(sh/oi),
                 "raw_row_sha256":row_sha,
                 "earliest_model_use_date":usable.isoformat(),
                 "source_url":url}
    dates=sorted({d for d,m in seen})
    require(len(dates)>=8,"INSUFFICIENT_CFTC_WEEKLY_COVERAGE")
    for d in dates:
        require((d,"GC") in seen and (d,"SI") in seen,
                "UNPAIRED_GOLD_SILVER_REPORT_"+str(d))
    require((now.date()-dates[-1]).days<=18,"STALE_CFTC_OFFICIAL_PUB")
    return list(seen.values()),{"sourceSha256":hashlib.sha256(raw).hexdigest(),
            "sourceUrl":url,"reportDateMax":dates[-1].isoformat(),
            "alignedWeeks":len(dates),"rows":len(seen),
            "historicalFirstprintVerified":False,
            "earliestModelUseRule":"MAX(first_actual_UTC_fetch_date,report_date_plus_7_calendar_days)"}

def write(rows):
    import psycopg
    dsn=os.getenv("NEON_DATABASE_URL","")
    require(bool(dsn),"MISSING_NEON_DATABASE_URL")
    sql="""
       WITH staged AS (
         SELECT * FROM jsonb_to_recordset(%s::jsonb) AS r(
           market text,contract_code text,report_date date,open_interest numeric,
           managed_money_long numeric,managed_money_short numeric,
           managed_money_net_over_oi numeric,managed_money_short_over_oi numeric,
           raw_row_sha256 text,earliest_model_use_date date,source_url text)
       ), ins AS (
          INSERT INTO gold_weekly_live.cftc_gc_si_futuresonly_official_v1
          (market,contract_code,report_date,open_interest,managed_money_long,
           managed_money_short,managed_money_net_over_oi,managed_money_short_over_oi,
           raw_row_sha256,earliest_model_use_date,source_url)
          SELECT market,contract_code,report_date,open_interest,managed_money_long,
                 managed_money_short,managed_money_net_over_oi,managed_money_short_over_oi,
                 raw_row_sha256,earliest_model_use_date,source_url FROM staged
          ON CONFLICT (market,report_date,raw_row_sha256) DO NOTHING
          RETURNING id)
       SELECT count(*) FROM ins
    """
    with psycopg.connect(dsn,connect_timeout=15) as db:
        with db.cursor() as cur:
            cur.execute(sql,(json.dumps(rows),))
            n=int(cur.fetchone()[0])
        db.commit()
    return n

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    parser.add_argument("--out",default="gold_cftc_official_ledger_v1.json")
    args=parser.parse_args()
    now=datetime.now(timezone.utc)
    rows,report=fetch_rows(now)
    report.update({"status":"CFTC_OFFICIAL_GC_SI_PAIRED_CHECK_PASS",
                   "asOfUTC":now.isoformat(),"newRowsInserted":0,
                   "originalFrozenModelUnchanged":True})
    if args.write:report["newRowsInserted"]=write(rows)
    Path(args.out).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)

if __name__=="__main__":main()
