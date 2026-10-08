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

      # Target-readiness is based on source timestamps only, not price levels,
      # historical outcomes or any fit. UTC+3 Turkey session anchors.
      with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=15) as c:
        with c.cursor() as cur:
          cur.execute(f"""SELECT bar_start_utc FROM {TABLE} WHERE source_id=%s AND
                  bar_start_utc>='2026-01-01' AND bar_start_utc<='2026-10-08 13:45:00+00'
                  AND m1_matched=15 ORDER BY bar_start_utc""",(SOURCE,))
          stamps={x[0] for x in cur.fetchall()}
      import datetime as dt
      complete_day=0
      complete_ovn=0
      attempted=0
      for day_n in range((dt.date(2026,10,8)-dt.date(2026,1,1)).days+1):
        day=dt.date(2026,1,1)+dt.timedelta(days=day_n)
        if day.weekday()>=5:continue
        attempted+=1
        day0=dt.datetime.combine(day,dt.time(6,0),tzinfo=dt.timezone.utc)
        intervals={day0+dt.timedelta(minutes=i*15) for i in range(32)}
        if intervals.issubset(stamps):complete_day+=1
        if day.weekday()>=4:continue
        nextday=day+dt.timedelta(days=1)
        midnight=dt.datetime.combine(day,dt.time(14,0),tzinfo=dt.timezone.utc)
        nextend=dt.datetime.combine(nextday,dt.time(5,45),tzinfo=dt.timezone.utc)
        if midnight in stamps and nextend in stamps:
          expected=[midnight+dt.timedelta(minutes=i*15) for i in range(64)]
          if sum(ts in stamps for ts in expected)>=55:complete_ovn+=1
      r["issue_dates_examined"]=attempted
      r["complete_day_source_paths"]=complete_day
      r["complete_regular_overnight_source_paths"]=complete_ovn
      r["ready_to_score_2026_90_day_90_ovn_gate"]=bool(complete_day>=90 and complete_ovn>=90)
      r["full_calendar_coverage_verified"]=False
      r["model_score_from_this_audit"]=False
    except Exception as e:
      r["status"]="PRIVATE_SOURCE_NOT_YET_QUERYABLE"
      r["error_type"]=type(e).__name__
    OUT.write_text(json.dumps(r,indent=2)+"\n")
    print("DIRECT_2026_PRIVATE_SOURCE_STATUS",json.dumps(r),flush=True)
if __name__=="__main__":main()
