from __future__ import annotations
import json, os, statistics
from collections import Counter
from pathlib import Path
import psycopg

PATTERNS = [
    "%XAU%","%XAG%","%XPT%","%XPD%","%GPR%","%GVZ%","%VIX%",
    "%SP500%","%SPX%","%DXY%","%USD%","%TREAS%","%YIELD%","%RATE%",
    "%OIL%","%WTI%","%BRENT%","%CPI%","%PPI%"
]
EXACT = [
    "XAU_STAKTRAKR_RESEARCH_DAILY_R1","XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "XPT_STAKTRAKR_RESEARCH_DAILY_R1","XPD_STAKTRAKR_RESEARCH_DAILY_R1",
    "GPR_OFFICIAL_GIT_PIT","CORE5_GOLD_USD_OZ_RESEARCH_R1","CORE5_GPR_ROUNDED_RESEARCH_R1"
]

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    out=[]
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only=on")
        cur.execute("SELECT DISTINCT series_id FROM observations ORDER BY series_id")
        ids=[r[0] for r in cur.fetchall()]
        wanted=[]
        for sid in ids:
            s=sid.upper()
            if sid in EXACT or any(p.strip("%").upper() in s for p in PATTERNS):
                wanted.append(sid)
        for sid in wanted:
            cur.execute("SELECT observation_ts FROM observations WHERE series_id=%s ORDER BY observation_ts",(sid,))
            ts=[r[0] for r in cur.fetchall()]
            if not ts: continue
            dates=sorted({x.date() for x in ts})
            gaps=[(dates[i]-dates[i-1]).days for i in range(1,len(dates))]
            med_gap=statistics.median(gaps) if gaps else None
            mode_gap=Counter(gaps).most_common(1)[0][0] if gaps else None
            # crude frequency class from unique calendar-date gaps
            if med_gap is None: freq="SINGLE"
            elif med_gap <= 1.5: freq="DAILY_OR_INTRADAY"
            elif med_gap <= 4: freq="BUSINESS_DAILY_OR_FEW_DAY"
            elif med_gap <= 10: freq="WEEKLY"
            elif med_gap <= 40: freq="MONTHLY"
            else: freq="LOWER_THAN_MONTHLY"
            out.append({
              "series_id":sid,"rows":len(ts),"unique_dates":len(dates),
              "first":ts[0].isoformat(),"last":ts[-1].isoformat(),
              "median_calendar_gap_days":med_gap,"mode_gap_days":mode_gap,
              "frequency_class":freq
            })
    exact=[x for x in out if x["series_id"] in EXACT]
    candidates=[x for x in out if x["series_id"] not in EXACT and x["frequency_class"] in ("DAILY_OR_INTRADAY","BUSINESS_DAILY_OR_FEW_DAY")]
    result={"identity":"GOLD_CONTROL_MIDAS_FREQUENCY_AVAILABILITY_AUDIT_V1","exact_midas_inputs":exact,"other_daily_candidate_series":candidates,"all_matching":out}
    Path("GOLD_CONTROL_MIDAS_FREQUENCY_AVAILABILITY_AUDIT_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"exact":exact,"other_daily_candidates":candidates},indent=2))
if __name__=="__main__":main()
