"""Explain why full 64-bar XAU overnight HAR realized RV SOURCE gate fails.
No filling, interpolation, or outcomes used: only source quote timestamp coverage.
"""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as gold
NAME="GOLD_EXECUTION_2026_OVERNIGHT_M15_GAP_SHAPE_20261009"
def main():
    q,t,sets=gold.source_sets()
    reports=[];holes=[]
    for tag,px,ts in sets:
       prices=pd.concat([q,px]).sort_index()
       targets=pd.concat([t,ts],ignore_index=True)
       if prices.index.duplicated().any() or targets.date.duplicated().any():
           raise RuntimeError("DUPLICATED_SOURCE_BARS")
       for r in targets.itertuples(index=False):
           d=pd.Timestamp(r.date)
           if d.year<2023 or d.dayofweek>=4 or r.overnight_gate!="COMPLETE_SINGLE_SOURCE":continue
           origin=pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=14)
           v=prices.reindex(pd.date_range(origin,periods=64,freq="15min"))
           prev=prices.reindex(pd.date_range(origin-pd.Timedelta(hours=4),periods=16,freq="15min"))
           valid=v.open.notna() & v.close.notna()
           n=int(valid.sum())
           prevalid=int((prev.open.notna()&prev.close.notna()).sum())
           reports.append({"source":tag,"year":int(d.year),"night_bars_observed":n,
              "pre4h_bars_observed":prevalid,"complete64":n==64,"atleast60":n>=60,
              "atleast56":n>=56,"all_pre16":prevalid==16})
           for z in v.index[~valid.to_numpy()]:
               holes.append({"source":tag,"year":int(d.year),
                   "local_time":z.tz_convert("Europe/Istanbul").strftime("%H:%M")})
    a=pd.DataFrame(reports);g=a.groupby(["source","year"]).agg(
        nights=("night_bars_observed","size"),
        complete64=("complete64","sum"),atleast60=("atleast60","sum"),
        atleast56=("atleast56","sum"),preorigin_full=("all_pre16","sum"),
        median_night_bars=("night_bars_observed","median"),
        min_night_bars=("night_bars_observed","min"),
        median_pre4h_bars=("pre4h_bars_observed","median")).reset_index()
    g.to_csv(str(AX/NAME)+"_YEAR_QC.csv",index=False)
    miss=pd.DataFrame(holes)
    timecounts=(miss.groupby(["source","local_time"]).size().reset_index(name="missing_count")
        if not miss.empty else pd.DataFrame(columns=["source","local_time","missing_count"]))
    timecounts.to_csv(str(AX/NAME)+"_MISSING_CLOCK.csv",index=False)
    state={"status":"REAL_NATIVE_M15_QUOTE_COVERAGE_TIMES_AUDITED",
       "source":"bid paired open close presence only, no model targets fitted",
       "cannot_impute_off_market_gap":True,
       "original_exact64_rv_HAR_is_blocked":True}
    Path(str(AX/NAME)+"_SUMMARY.json").write_text(json.dumps(state,indent=2)+"\n")
    print("REAL_OVERNIGHT_M15_BAR_SOURCE_QC",g.to_string(index=False),flush=True)
    print("CLOCK_HOLE_TOP",timecounts.sort_values("missing_count",ascending=False).head(24).to_string(index=False),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        t=traceback.extract_tb(e.__traceback__)[-1]
        x={"status":"BAR_SOURCE_QC_BLOCKED","type":type(e).__name__,"reason":str(e)[:125],"line":t.lineno}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(x,indent=2)+"\n")
        print("BAR_QC_FAIL",json.dumps(x),flush=True)
