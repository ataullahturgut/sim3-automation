"""Old exact PSF M3 path signature+FPCA vote on source-audited 2026 RFR.

Reuses original psf.build and psf.frozen_models, NEVER substitutes M3 for
unchanged macro-dependent M4/PRAMV V1 or treats missing news as known no event.
"""
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
from scipy.stats import fisher_exact
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_psf_ovn_20261007 as psf
import gold_execution_2026_full_trajectory_cbr_20261008 as source
NAME="GOLD_EXECUTION_2026_LEGACY_PSF_M3_PRICE_AGREEMENT_20261008"
START=2021
def price_only_panel(q,t,px,tx,label):
    history=pd.concat([q,px]).sort_index()
    if history.index.duplicated().any():raise RuntimeError("PRICE_SOURCE_DUPLICATION")
    events=pd.concat([t,tx],ignore_index=True)
    if events.date.duplicated().any():raise RuntimeError("ISSUE_DATE_DUPLICATION")
    original=psf.macro_features
    try:
        # Macro variables are neither observed nor inputs to M3. Never
        # interpret unavailable 2026 event series as a known event-free day.
        psf.macro_features=lambda *args:(np.nan,np.nan,np.nan)
        feat=psf.build(history,pd.DataFrame())
    finally:psf.macro_features=original
    truth=events[["date","next_date","ret_OVN","overnight_gate"]].copy()
    feat=feat.merge(truth,on="date",validate="one_to_one",suffixes=("","_reference"))
    feat=feat[(feat.overnight_gate=="COMPLETE_SINGLE_SOURCE")&
         feat.ret_OVN.notna() & (feat.date.dt.dayofweek<=3)].copy()
    if feat.empty:raise RuntimeError("M3_SOURCE_MATURED_EMPTY")
    if not (feat.next_date==feat.next_date_reference).all():
        raise RuntimeError("ORIGINAL_PATH_DATE_CHAIN_MISMATCH")
    feat["y"]=feat.ret_OVN.gt(0).astype(int)
    feat["rfr_candidate"]=(np.sign(feat.r1600_1630)!=np.sign(feat.r1630_1700))&(
        feat.r1600_1630.ne(0)&feat.r1630_1700.ne(0))
    feat["rfr_pred"]=feat.r1600_1630.gt(0).astype(int)
    feat["source_test"]=label
    return feat.sort_values("date")

def predict(g):
    # Mutate only an in-process original source code family mapping, not saved
    # settings; exact M3 implementation is reused by original source function.
    prev=psf.FAMILIES
    psf.FAMILIES={"M3_SIG_FPCA":prev["M3_SIG_FPCA"]}
    try:
      results=[]
      for period,te in g[g.year>=2023].groupby(g.date.dt.to_period("M")):
        before=period.to_timestamp() if period.year<=2024 else pd.Timestamp(f"{period.year}-01-01")
        tr=g[(g.date<before)&(g.next_date<=before)&(g.year>=START)].copy()
        if len(tr)<120 or tr.y.nunique()!=2:continue
        if not(tr.date<te.date.min()).all():raise RuntimeError("M3_TARGET_LEAK")
        probs=psf.frozen_models(tr,te)["M3_SIG_FPCA"]
        for row,p in zip(te.itertuples(index=False),probs):
          active=bool(row.rfr_candidate)
          agree=bool((p>=.5)==bool(row.rfr_pred))
          results.append({"source_test":row.source_test,
             "date":row.date.strftime("%Y-%m-%d"),"year":int(row.year),
             "y":int(row.y),"ret_OVN":float(row.ret_OVN),
             "m3_p_up":float(p),"m3_pred":int(p>=.5),
             "rfr_candidate":active,"rfr_pred":int(row.rfr_pred),
             "price_gate":bool(active and agree),"rfr_m3_agree":agree,
             "model_training_before":str(before),"n_train":len(tr)})
    finally:psf.FAMILIES=prev
    data=pd.DataFrame(results)
    if data.empty or data.duplicated(["source_test","date"]).any():
        raise RuntimeError("M3_FORECAST_SOURCE_CONFLICT")
    return data

def evaluate(p):
    rows=[]
    for (src,year),g in p.groupby(["source_test","year"]):
      y=g.y.to_numpy(int);m=g.m3_pred.to_numpy(int)
      probs=g.m3_p_up.to_numpy(float)
      rev=g[g.rfr_candidate]
      yes=rev[rev.rfr_m3_agree]
      no=rev[~rev.rfr_m3_agree]
      yy=yes.y.to_numpy(int);rr=yes.rfr_pred.to_numpy(int)
      def balance(yp,pr):
        if len(yp)==0:return (None,None,None)
        down=yp==0;up=yp==1
        dr=float(np.mean(pr[down]==0)) if down.any() else None
        ur=float(np.mean(pr[up]==1)) if up.any() else None
        return dr,ur,.5*(dr+ur) if dr is not None and ur is not None else None
      down,up,ba=balance(yy,rr)
      rec=list(yes.rfr_pred==yes.y)
      rejected=list(no.rfr_pred==no.y)
      fisher=fisher_exact([[sum(rec),len(rec)-sum(rec)],
          [sum(rejected),len(rejected)-sum(rejected)]])[1] if len(rec) and len(rejected) else None
      rows.append({"source_test":src,"year":int(year),"eligible_n":len(g),
        "m3_full_BA":balance(y,m)[2],
        "m3_full_Brier":float(np.mean((probs-y)**2)),
        "all_reversal_n":len(rev),"all_reversal_accuracy":float(np.mean(rev.rfr_pred==rev.y)) if len(rev) else None,
        "M3_reversal_agreed_n":len(yes),"M3_gate_coverage":len(yes)/len(g),
        "M3_gate_accuracy":float(np.mean(rr==yy)) if len(yes) else None,
        "M3_gate_BA":ba,"M3_gate_DOWN_recall":down,"M3_gate_UP_recall":up,
        "M3_rejected_n":len(no),
        "M3_rejected_RFR_accuracy":float(np.mean(no.rfr_pred==no.y)) if len(no) else None,
        "agree_minus_disagree_accuracy":float(np.mean(yes.rfr_pred==yes.y)-np.mean(no.rfr_pred==no.y))
              if len(yes) and len(no) else None,
        "agree_vs_disagree_Fisher_p_unadjusted":float(fisher) if fisher is not None else None,
        "idealized_rfr_signed_return_sum_no_bank_cost":float(np.sum(np.where(rr==1,1,-1)*yes.ret_OVN.to_numpy(float))),
        "large_wrong_ge1pct":int(np.sum((rr!=yy)&(yes.ret_OVN.abs().to_numpy(float)>=.01))),
        "PIT_2026_MACRO_GATE":"UNAVAILABLE_OR_UNCERTIFIED",
        "not_frozen_original_M4_PRAMV":True})
    return pd.DataFrame(rows)

def main():
    tic=time.time()
    q,t,source_sets=source.source_sets()
    out=[]
    for tag,px,tx in source_sets:
       feat=price_only_panel(q,t,px,tx,tag)
       preds=predict(feat)
       out.append(preds)
       print("EXACT_OLD_PSF_M3_SOURCE",tag,
          feat.groupby("year").size().to_dict(),flush=True)
    predictions=pd.concat(out,ignore_index=True)
    m=evaluate(predictions)
    obj={"status":"ORIGINAL_PSF_M3_SIG_FPCA_PLUS_RFR_PRICE_ONLY_ACTUALLY_REBUILT",
       "original_psf_code":"gold_execution_psf_ovn_20261007.py::build,frozen_models,leadlag_area,timeprice_area",
       "training_start":START,"monthly_matured_2023_24":True,
       "2025_2026_frozen_before_calendar_year":True,
       "gate":"opposite 16:00 and 16:30 halfhour signs AND M3 predicted same first sign",
       "2026_external_macro":"UNKNOWN - M4/V1 cannot be scored from this study",
       "no_new_2026_feature_threshold_selection":True,
       "vintage_2026_sources":"separate same-Dukascopy upstream price-gated mirror and original broker native M1",
       "2026_retrospective_already_inspected":True,
       "not_bank_executable":True,"runtime_s":int(time.time()-tic)}
    stem=str(AX/NAME)
    m.to_csv(stem+"_YEAR_METRICS.csv",index=False)
    predictions.to_csv(stem+"_PRIVATE_DATED.csv",index=False)
    Path(stem+"_SUMMARY.json").write_text(json.dumps(obj,indent=2)+"\n")
    print("EXACT_OLD_PSF_M3_RFR_AUDIT",m.to_string(index=False),flush=True)
    print("M3_REPLAY_STATUS",json.dumps(obj),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
      import traceback
      tb=traceback.extract_tb(e.__traceback__)[-1]
      obj={"status":"SOURCE_EXACT_M3_REBUILD_BLOCKED",
           "error_type":type(e).__name__,"function":tb.name,
           "line":tb.lineno,"reason":str(e)[:120]}
      (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(obj,indent=2)+"\n")
      print("M3_REPLAY_BLOCK",json.dumps(obj),flush=True)
