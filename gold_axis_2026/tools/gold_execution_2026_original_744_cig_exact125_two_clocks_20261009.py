"""Exact ORIGINAL 74.40% CIG-D1 consensus: rescore same 125 frozen predictions.

Zero changes to SAGE/V5/RIFT/VEGA, CIG votes, original date universe,
or historic training and model files. Compare to 09TR-17TR and regular
Mon-Thu 17TR-next09TR 2026 BID source-qualified labels on SAME DATES.
Original daily score 93/125, post-08:15NY 59/125 must replay exactly.

DAY target includes 09TR-15/16TR PRE actual governed 08NY issue, and is
INVALID as an executable-from-09 forecast. OVN starts after issuance
but bank spread & 17TR exact quote practical feasibility not established.
"""
from pathlib import Path
import sys,json,time
import pandas as pd,numpy as np
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as history
import gold_execution_2026_histdata_restricted_holdout_20261008 as independent
NAME="GOLD_EXECUTION_2026_CANONICAL_CIG_D1_74P4_SAME125_TWO_CLOCKS_20261009"
CIG=AX/"GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv"
def baseline():
    p=pd.read_csv(CIG,parse_dates=["issue_date"])
    if len(p)!=125 or p.issue_date.duplicated().any():raise RuntimeError("CIG_CANONICAL_125_COHORT_CHANGED")
    if not p.consensus.map(str).str.lower().eq("true").all():raise RuntimeError("NON_CONSENSUS_ROW")
    if not(p[["sage","v5","rift","vega"]].eq(p.consensus_pred,axis=0)).all().all():
        raise RuntimeError("ORIGINAL_4OF4_SAGE_V5_RIFT_VEGA_NOT_IDENTICAL")
    n=int((p.consensus_pred==p.actual_daily_label).sum())
    ny=int(((p.ret_0815_1600>0).astype(int)==p.consensus_pred).sum())
    if n!=93 or ny!=59:raise RuntimeError(f"CIG_74P4_OR_47P2_GUARD_FAIL_{n}_{ny}")
    if (p.issue_date.dt.year!=2026).any() or p.issue_date.min()<pd.Timestamp("2026-01-01") or p.issue_date.max()>pd.Timestamp("2026-07-31"):
        raise RuntimeError("CANONICAL_DATES_CHANGED")
    return p

def label_set(mirrors):
    oldq,oldt,sets=history.source_sets()
    labels=[]
    for name,q,z in sets:
        subset=z.copy()
        subset["source_test"]=name
        labels.append(subset)
    # DIFFERENT-VENDOR robustness only, no conflation with Dukascopy source.
    _,hist_targets,_=independent.load_q_t()
    alt=hist_targets[hist_targets.year==2026].copy()
    alt["source_test"]="HISTDATA_INDEPENDENT_VENDOR_RESTRICTED"
    labels.append(alt)
    return labels

def valid_scores(pair,src,target):
    n_total=len(pair)
    valid=pair[pair["eligible"]].copy()
    y=valid["y"].astype(int).to_numpy();pred=valid.consensus_pred.astype(int).to_numpy()
    U=y==1; D=y==0
    trueU=int(U.sum());trueD=int(D.sum())
    n=len(valid);right=int((pred==y).sum())
    return {"source_test":src,"window":target,
      "old_consensus_total_days":n_total,"matched_matured_days":n,
      "unmatched_or_unmatured_days":n_total-n,
      "consensus_UP_predictions":int((pred==1).sum()),
      "consensus_DOWN_predictions":int((pred==0).sum()),
      "actual_UP_days":trueU,"actual_DOWN_days":trueD,
      "correct":right,"wrong":n-right,
      "accuracy":right/n if n else None,
      "balanced_accuracy":(.5*((pred[U]==1).mean()+(pred[D]==0).mean())) if trueU and trueD else None,
      "actual_DOWN_recall":float((pred[D]==0).mean()) if trueD else None,
      "actual_UP_recall":float((pred[U]==1).mean()) if trueU else None,
      "UP_signal_precision":float((y[pred==1]==1).mean()) if (pred==1).any() else None,
      "DOWN_signal_precision":float((y[pred==0]==0).mean()) if (pred==0).any() else None,
      "TP":int(np.sum((pred==1)&U)),"TN":int(np.sum((pred==0)&D)),
      "FP":int(np.sum((pred==1)&D)),"FN":int(np.sum((pred==0)&U)),
      "legacy_old_daily_correct_on_exact_matched_dates":int((valid.consensus_pred==valid.actual_daily_label).sum()),
      "legacy_old_daily_accuracy_on_exact_matched_dates":float(np.mean(valid.consensus_pred==valid.actual_daily_label)) if n else None,
      "intraday_origin_09_precedes_CIG_governed_08NY_issuance":target=="DAY",
      "overnight_origins_after_issue":target=="OVN",
      "fee_spread_bank_profit_measured":False}

def run():
    t0=time.monotonic();p=baseline()
    out=[];month=[];dated=[]
    for z in label_set(None):
        source=str(z["source_test"].iloc[0])
        z=z.copy();z["date"]=pd.to_datetime(z.date)
        if z.date.duplicated().any():raise RuntimeError("2026_SAME_VENDOR_DUPLICATE_SESSION_DATE")
        for target,ret,gcol in (("DAY","ret_DAY","day_gate"),("OVN","ret_OVN","overnight_gate")):
            s=z[["date",ret,gcol]].rename(columns={"date":"issue_date","ret":"return"}).copy()
            full=p.merge(s,on="issue_date",how="left",validate="one_to_one",indicator=True)
            if len(full)!=125:raise RuntimeError("ALTERED_CANONICAL_125")
            full["eligible"]=(full["_merge"]=="both")&(full[gcol]=="COMPLETE_SINGLE_SOURCE")&full[ret].notna()
            full["y"]=np.where(full.eligible,(full[ret]>0).astype(int),np.nan)
            x=valid_scores(full,source,target)
            out.append(x)
            for mo,w in full.groupby(full.issue_date.dt.strftime("%Y-%m")):
                vals=valid_scores(w,source,target)
                vals["month"]=mo
                month.append(vals)
            full["source_test"]=source
            full["window"]=target
            full["pred"]=full.consensus_pred
            full["correct_intraday"]=np.where(full.eligible,full.pred==full.y,np.nan)
            dated.append(full[["issue_date","source_test","window","consensus_pred",
                 "actual_daily_label",ret,gcol,"eligible","y","correct_intraday"]].rename(columns={ret:"actual_session_logret",gcol:"target_source_gate"}))
    scores=pd.DataFrame(out);m=pd.DataFrame(month)
    private=pd.concat(dated,ignore_index=True)
    if len(scores)!=6:raise RuntimeError("MUST_HAVE_TWO_WINDOWS_X_THREE_SOURCES")
    path=str(AX/NAME)
    scores.to_csv(path+"_YEAR_METRICS.csv",index=False)
    m.to_csv(path+"_MONTH_METRICS.csv",index=False)
    private.to_csv(path+"_PRIVATE_SAME125_DATED.csv",index=False)
    summary={"status":"ACTUALLY_RESCORED_ORIGINAL_74P4_CIG125_BOTH_TURKEY_EXECUTION_WINDOWS",
      "identity":"CIG_D1_V1 frozen original 4 of 4 SAGE V2 RuleFlow V3-TG / HELIOS V5 DCE / RIFT / VEGA",
      "consensus_2026_Jan_to_July":125,"original_daily_reference_correct":93,
      "original_daily_reference_accuracy":.744,
      "frozen_cig_exact_newyork_0815_1600_correct":59,
      "original_model_historical_inputs_retrained":False,
      "model_predictions_recreated_or_changed":False,
      "old_source_quote_2026_preservation":"2026 Dukascopy upstream third-party M1 BID/ASK reverse reference plus direct native source; HistData independently restricted",
      "two_target_intervals_TRT":["09:00-17:00","17:00-next09:00 Monday-Thursday 16h"],
      "DAY_noncausal_to_09_entry":True,
      "CIG_issued_08NY":"15:00 Turkey during US DST, 16:00 during US standard; DAY opens earlier",
      "OVN_timing_after_governed_issue":True,
      "all_2026_125_days_retained_with_missing_explicit":True,
      "no_bank_PnL":True,
      "2026_already_inspected_not_new_holdout":True,
      "elapsed_seconds":int(time.monotonic()-t0)}
    Path(path+"_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("EXACT_ORIGINAL_74P4_CIG125_DAY_OVN_YEAR_TABLE",scores.to_string(index=False),flush=True)
    print("EXACT_ORIGINAL_74P4_CIG125_DAY_OVN_SOURCE_GOVERNANCE",json.dumps(summary),flush=True)
if __name__=="__main__":
    try:run()
    except Exception as e:
      import traceback
      fr=traceback.extract_tb(e.__traceback__)[-1]
      qc={"status":"CIG125_RETARGET_SOURCE_OR_IMPLEMENTATION_BLOCKED_NO_NEW_CLOCK_SCORE",
          "error_type":type(e).__name__,"reason":str(e)[:180],
          "line":fr.lineno,"function":fr.name}
      (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(qc,indent=2)+"\n")
      print("EXACT_CIG125_RESCORE_BLOCK",json.dumps(qc),flush=True)
