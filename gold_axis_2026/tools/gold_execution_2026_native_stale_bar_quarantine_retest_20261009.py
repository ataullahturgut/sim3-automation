"""Strictly quote-driven quarantine of 2026 native source stale 00/01TR 4 M15
runs, exact carried price, BEFORE data labels are regenerated. Same frozen
original CBR/HGB 2021-start. Side-by-side first passage.
"""
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as geo
import gold_execution_2026_firstpassage_barrier_diagnostic_20261008 as passage
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as targets
NAME="GOLD_EXECUTION_2026_DIRECT_NATIVE_STALE_QUARANTINE_RETEST_20261009"
def source_quarantine(q,ts):
    cleaned=q.copy();remove=[];grouped=[]
    for row in ts.itertuples(index=False):
        d=pd.Timestamp(row.date)
        if d.year!=2026 or row.overnight_gate!="COMPLETE_SINGLE_SOURCE":continue
        if d.dayofweek>=4:continue
        origin=pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=14)
        for h in (21,22):
            grid=pd.date_range(pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=h),
                periods=4,freq="15min")
            if not all(a in cleaned.index for a in grid):continue
            prev=grid[0]-pd.Timedelta(minutes=15)
            if prev not in cleaned.index:continue
            bars=cleaned.reindex(grid)
            opens=bars.open.to_numpy(float);closes=bars.close.to_numpy(float)
            px=float(cleaned.loc[prev,"close"])
            if (np.isfinite(opens).all() and np.isfinite(closes).all()
                and np.all(opens==closes) and np.all(closes==closes[0])
                and float(opens[0])==px):
                remove.extend(list(grid))
                grouped.append({"date":d.strftime("%Y-%m-%d"),"hour_TRT":h-21,
                    "four_identical_stale_M15":True})
    remove=list(set(remove))
    if len(remove)<100:raise RuntimeError("EXPECTED_CARRY_FORWARD_BARS_NOT_FOUND")
    cleaned=cleaned.drop(index=remove)
    if cleaned.index.duplicated().any():raise RuntimeError("QUARANTINE_DUPLICATE_PRICE_KEY")
    return cleaned,grouped,len(remove)

def compare_frame(a,b):
    out=[]
    for target in ("DAY","OVN"):
        for method in ("CBR_REGIME_PATH","HGB_FROZEN_2021"):
            old=a[(a.year==2026)&(a.target==target)&(a.method==method)].set_index("date").sort_index()
            new=b[(b.year==2026)&(b.target==target)&(b.method==method)].set_index("date").sort_index()
            common=old.join(new,how="inner",lsuffix="_old",rsuffix="_new")
            if common.empty:raise RuntimeError("NO_PAIRED_CLEAN_PRICE_FORECAST")
            if not (common.y_old==common.y_new).all():
                raise RuntimeError("SOURCE_CORRECTION_CHANGED_ORIGINAL_MATURED_LABEL")
            pred0=common.pred_old.to_numpy(int);pred1=common.pred_new.to_numpy(int)
            y=common.y_old.to_numpy(int)
            dd=y==0;uu=y==1
            def calculate(p):
                return (float(np.mean(p==y)),
                   float(.5*(np.mean(p[dd]==0)+np.mean(p[uu]==1))) if dd.any() and uu.any() else None,
                   float(np.mean(p[dd]==0)) if dd.any() else None)
            acc0,ba0,down0=calculate(pred0);acc1,ba1,down1=calculate(pred1)
            out.append({"target":target,"method":method,
             "original_2026_score_n":len(old),"cleaned_2026_score_n":len(new),
             "same_paired_origins":len(common),"lost_original_dates":len(old)-len(common),
             "new_only_origins":len(new)-len(common),
             "paired_2026_y_changed":int(np.sum(common.y_old!=common.y_new)),
             "direction_changed_n":int(np.sum(pred0!=pred1)),
             "max_abs_probability_change":float(np.max(np.abs(common.p_up_old-common.p_up_new))),
             "original_acc":acc0,"corrected_acc":acc1,"original_BA":ba0,"corrected_BA":ba1,
             "original_DOWN_recall":down0,"corrected_DOWN_recall":down1,
             "not_a_new_model_and_not_bank_PnL":True})
    return pd.DataFrame(out)

def compare_barrier(q0,q1,t0,t1):
    q0full=q0
    q1full=q1
    o=t0[t0.year==2026].set_index("date")
    n=t1[t1.year==2026].set_index("date")
    data=[]
    for date in o.index.intersection(n.index):
        a=passage.per_night(q0full,o.loc[date])
        b=passage.per_night(q1full,n.loc[date])
        if a is None or b is None:continue
        if not a.get("accepted") or not b.get("accepted"):continue
        data.append({"date":date.strftime("%Y-%m-%d"),
          "old":a["first_hit"],"new":b["first_hit"],
          "old_native_bar_n":a["source_m15_closes"],
          "new_observed_bar_n":b["source_m15_closes"]})
    z=pd.DataFrame(data)
    return {"paired_firstpassage_n":len(z),
      "fixed_barrier_first_event_changed_n":int((z.old!=z.new).sum()) if len(z) else None,
      "old_median_quote_bar_n":float(z.old_native_bar_n.median()) if len(z) else None,
      "clean_median_quote_bar_n":float(z.new_observed_bar_n.median()) if len(z) else None}

def main():
    t0=time.time()
    q,t,sets=geo.source_sets()
    name,qnative,tnative=[x for x in sets if x[0]=="DIRECT_DUKASCOPY_NATIVE_THROUGH_OCT07"][0]
    cleaned,groups,removed=source_quarantine(qnative,tnative)
    tnew,sourceqc=targets.candidate_targets(t,cleaned)
    oldq=pd.concat([q,qnative]).sort_index()
    newq=pd.concat([q,cleaned]).sort_index()
    oldt=pd.concat([t,tnative],ignore_index=True).sort_values("date")
    newt=pd.concat([t,tnew],ignore_index=True).sort_values("date")
    a=geo.forecast(geo.panel(q,t,qnative,tnative),name)
    b=geo.forecast(geo.panel(q,t,cleaned,tnew),"DIRECT_DUKASCOPY_NATIVE_MIDNIGHT_QUARANTINED")
    metrics=compare_frame(a,b)
    barrier=compare_barrier(oldq,newq,tnative,tnew)
    receipt={"status":"PRE_REGISTERED_REAL_2026_NATIVE_STALE_4BAR_QUARANTINE_PAIRED_RETEST_COMPLETE",
      "stale_fourbar_groups":len(groups),"stale_native_2026_M15_removed":removed,
      "native_2026_M15_old_n":len(qnative),"native_2026_M15_clean_n":len(cleaned),
      "stale_slot_groups_by_local_hour":pd.DataFrame(groups).groupby("hour_TRT").size().to_dict(),
      "source_clean_target_gate":sourceqc,"barrier":barrier,
      "date_population_held_exact_when_matched":True,
      "no_retraining_on_2026_outcomes":True,"historical_2020_25_price_unchanged":True,
      "bar_00_01_zero_quote_stale_suspect_not_proven_native_tick_source":True,
      "elapsed_s":int(time.time()-t0)}
    base=str(AX/NAME)
    metrics.to_csv(base+"_PAIRED_METRICS.csv",index=False)
    Path(base+"_SUMMARY.json").write_text(json.dumps(receipt,indent=2,default=str)+"\n")
    print("NATIVE_STALE_SOURCE_CORRECTED_FORECASTS",metrics.to_string(index=False),flush=True)
    print("NATIVE_STALE_SOURCE_QUARANTINE_QC",json.dumps(receipt,default=str),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
       import traceback
       fr=traceback.extract_tb(e.__traceback__)[-1]
       a={"status":"RETEST_BLOCKED_NO_CLAIM_OF_CLEANED_DIRECTION",
          "reason":str(e)[:135],"type":type(e).__name__,"line":fr.lineno,
          "function":fr.name}
       (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(a,indent=2)+"\n")
       print("CLEAN_DATA_BAR_RETEST_FAILURE",json.dumps(a),flush=True)
