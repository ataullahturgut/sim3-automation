"""Read-only as-of 2026-10-08 direct Dukascopy M1->M15 private source coverage QC."""
from __future__ import annotations
import os,json,sys,datetime as dt
from pathlib import Path
import psycopg
AX=Path(__file__).resolve().parents[1]
TABLE="gold_research_dukascopy_2026_direct_m1_m15_bidask_v2"
SOURCE="DUKASCOPY_DIRECT_M1_BIDASK_2026_M15_NATIVE_FULL_V2"
OUT=AX/"GOLD_EXECUTION_2026_DIRECT_DUKASCOPY_MONTHLY_COVERAGE_STATUS_20261008.json"
def main():
    r={"asof":"2026-10-08","provider":"direct Dukascopy XAUUSD M1 BID ASK",
       "source_id":SOURCE,"raw_prices_published":False}
    try:
      with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=15) as c:
        with c.cursor() as cur:
          cur.execute(f"""SELECT to_char(bar_start_utc AT TIME ZONE 'UTC','YYYY-MM'),
                count(*),count(distinct (bar_start_utc AT TIME ZONE 'UTC')::date),
                count(*) FILTER (WHERE m1_matched=15)
              FROM {TABLE} WHERE source_id=%s
              GROUP BY 1 ORDER BY 1""",(SOURCE,))
          rows=cur.fetchall()
      r["status"]="READ_ONLY_PRIVATE_SOURCE_COVERAGE_REPORT"
      r["month_coverage"]=[{"month":str(m),"m15_rows":int(n),
                 "days_utc_with_data":int(d),"native15_completed":int(c)} for m,n,d,c in rows]
      r["total_verified_m15"]=sum(x["m15_rows"] for x in r["month_coverage"])
      r["total_month_utc_days"]=sum(x["days_utc_with_data"] for x in r["month_coverage"])
      r["full_calendar_coverage_verified"]=False
      r["model_score_from_this_audit"]=False
    except Exception as e:
      r["status"]="PRIVATE_SOURCE_NOT_YET_QUERYABLE"
      r["error_type"]=type(e).__name__
    OUT.write_text(json.dumps(r,indent=2)+"\n")
    print("DIRECT_2026_PRIVATE_SOURCE_STATUS",json.dumps(r),flush=True)
if __name__=="__main__":main()
