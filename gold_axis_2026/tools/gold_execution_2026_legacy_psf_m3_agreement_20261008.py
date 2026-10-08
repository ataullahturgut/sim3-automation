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
