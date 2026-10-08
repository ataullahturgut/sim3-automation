"""Frozen original 2023-25 RFR PRICE impulse, independently scored 2026.

NOT PRAMV V1: cannot assert signed macro-event absence or M4 availability.
This is a pure, always-frozen price-only mechanism decomposition.
"""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as sources
NAME="GOLD_EXECUTION_2026_FROZEN_RFR_PRICE_ONLY_CHECK_20261008"
def extract(q,t):
    rows=[];eligibility={}
    for row in t.itertuples(index=False):
        if row.overnight_gate!="COMPLETE_SINGLE_SOURCE" or pd.isna(row.ret_OVN):
            continue
        d=pd.Timestamp(row.date)
        if d.dayofweek>=4:continue
        # Istanbul 16:00 = UTC 13:00, 17:00 = 14:00, no DST change.
        utc=pd.Timestamp(d.date(),tz="UTC")
        bars=q.reindex(pd.date_range(utc+pd.Timedelta(hours=13),periods=4,freq="15min"))
        if bars[["open","close"]].isna().any().any():continue
        p1=float(np.log(float(bars.close.iloc[1])/float(bars.open.iloc[0])))
        p2=float(np.log(float(bars.close.iloc[3])/float(bars.open.iloc[2])))
        if not np.isfinite(p1) or not np.isfinite(p2):continue
        if p1==0 or p2==0:continue
        reversed_sign=(p1>0)!=(p2>0)
        y=int(row.ret_OVN>0)
        rows.append({"date":d.strftime("%Y-%m-%d"),
           "year":int(row.year),"label":y,"signed_OVN":float(row.ret_OVN),
           "reversal":reversed_sign,"first_sign":int(p1>0),
           "last_sign":int(p2>0),
           "preorigin_halfhour_first_bps":p1*10000,
           "preorigin_halfhour_last_bps":p2*10000})
    return pd.DataFrame(rows)
def calc(k):
    rows=[]
    for (source,year),g in k.groupby(["source_test","year"]):
      for state in ("REVERSAL_ONLY","ALL_PAIRED"):
        z=g[g.reversal] if state=="REVERSAL_ONLY" else g
        if z.empty:continue
        y=z.label.to_numpy(int);a=z.first_sign.to_numpy(int)
        alt=z.last_sign.to_numpy(int)
        d=y==0;u=y==1
        dr=float(np.mean(a[d]==0)) if d.any() else None
        ur=float(np.mean(a[u]==1)) if u.any() else None
        rescue=int(np.sum((a==y)&(alt!=y)))
        broken=int(np.sum((a!=y)&(alt==y)))
        rows.append({"source_test":source,"year":int(year),"cohort":state,
            "model":"FROZEN_PRE17_FIRST_IMPULSE_PRICE_ONLY",
            "n":len(z),"eligible_full_n":len(g),
            "coverage_of_complete_preorigin_pairs":len(z)/len(g),
            "accuracy":float(np.mean(a==y)),
            "BA":.5*(dr+ur) if dr is not None and ur is not None else None,
            "DOWN_recall":dr,"UP_recall":ur,
            "last_impulse_same_dates_accuracy":float(np.mean(alt==y)),
            "rescues_vs_last":rescue,"breaks_vs_last":broken,
            "mcnemar_exact_p":float(binomtest(rescue,rescue+broken,.5).pvalue) if rescue+broken else 1.,
            "idealized_sum_signed_log_return":float(np.sum(np.where(a==1,1,-1)*z.signed_OVN.to_numpy(float))),
            "large_wrong_events_ge_1pct":int(np.sum((a!=y)&(z.signed_OVN.abs().to_numpy()>=.01))),
            "DOWN_true_n":int(d.sum()),"UP_true_n":int(u.sum()),
            "not_M4_and_not_PIT_macro":True})
    return pd.DataFrame(rows)
def main():
    q,t,sets=sources.source_sets()
    x=[]
    for key,px,targets in sets:
        qa=pd.concat([q,px]).sort_index()
        if qa.index.duplicated().any():raise RuntimeError("DUPLICATE_SOURCE_BAR")
        ta=pd.concat([t,targets],ignore_index=True)
        if ta.date.duplicated().any():raise RuntimeError("DUPLICATE_ISSUE")
        a=extract(qa,ta)
        if a.empty:raise RuntimeError("NO_SOURCE_COMPLETE_PRICE_PATTERNS")
        a["source_test"]=key;x.append(a)
    allp=pd.concat(x,ignore_index=True)
    m=calc(allp)
    stem=str(AX/NAME)
    m.to_csv(stem+"_METRICS.csv",index=False)
    allp.to_csv(stem+"_PRIVATE_DATED.csv",index=False)
    report={"status":"FROZEN_PRAMV_RFR_PRICE_COMPONENT_ACTUALLY_TESTED",
         "macro_gate":"NOT_AVAILABLE_2026_CERTIFIED; DO_NOT INFER NO MACRO",
         "M4_signature_FPCA":"NOT_IN_THIS_TEST",
         "original_2023_25_PRAMV_accuracy_cannot_be_replaced":True,
         "first_halfhour_Turkey":"16:00-16:30",
         "second_halfhour_Turkey":"16:30-17:00",
         "label":"17:00->nexteligible09:00 only, weekday16h",
         "2026_unseen_holdout":False,"bank_real_spreads_PnL":False}
    Path(stem+"_SUMMARY.json").write_text(json.dumps(report,indent=2)+"\n")
    print("ACTUAL_RFR_PRICE_BRANCH_METRICS",m.to_string(index=False),flush=True)
    print("RFR_CAVEATS",json.dumps(report),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
      import traceback
      tb=traceback.extract_tb(e.__traceback__)[-1]
      state={"status":"RFR_PRICE_BRANCH_BLOCKED","type":type(e).__name__,
        "function":tb.name,"line":tb.lineno,"reason":str(e)[:90]}
      (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(state,indent=2)+"\n")
      print("RFR_PRICE_BRANCH_BLOCKED",json.dumps(state),flush=True)
