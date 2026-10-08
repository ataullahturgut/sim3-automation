"""Earlier-path reliability challenger for frozen PRAMV RFR price component.

Exact V2A source-authority: early 14-16 Turkey price path disjoint
from fixed 16-17 price-rule inputs. Reliability q=P(RFR correct).
Source receipt and per-origin matured label required. No macro/M4 imputation.
"""
from __future__ import annotations
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_pramv_frozen_rfr_price_check_20261008 as rfr
import gold_execution_psf_ovn_20261007 as psf
NAME="GOLD_EXECUTION_2026_ORTHOGONAL_EARLY_PATH_RFR_RELIABILITY_20261008"
FEATURES=("early_ret2h","early_rv2h","early_semi_balance","early_tp_signature")
def early_features(q, candidate):
    out=[]
    for r in candidate.itertuples(index=False):
        utc=pd.Timestamp(r.date,tz="UTC")
        idx=pd.date_range(utc+pd.Timedelta(hours=11),periods=8,freq="15min")
        b=q.reindex(idx)[["open","close"]]
        if b.isna().any().any():continue
        opened=b.open.to_numpy(float);closes=b.close.to_numpy(float)
        if (opened<=0).any() or (closes<=0).any():continue
        cumulative=np.log(closes/opened[0])
        inc=np.diff(np.r_[0.,cumulative])
        rv=float(np.sqrt(np.sum(inc*inc)))
        positive=float(np.sqrt(np.sum(inc[inc>0]**2)))
        negative=float(np.sqrt(np.sum(inc[inc<0]**2)))
        row={"source_test":r.source_test,"date":r.date,"year":r.year,
             "label":int(r.label),"reversal":bool(r.reversal),
             "rfr_sign":int(r.first_sign),"return_OVN":float(r.signed_OVN),
             "early_ret2h":float(cumulative[-1]),"early_rv2h":rv,
             "early_semi_balance":(positive-negative)/(positive+negative+1e-12),
             "early_tp_signature":float(psf.timeprice_area(cumulative,rv))}
        out.append(row)
    z=pd.DataFrame(out)
    if z.empty or z.duplicated(["source_test","date"]).any():
        raise RuntimeError("EARLY_FEATURE_POPULATION_INVALID")
    z=z[z.reversal].copy().sort_values(["source_test","date"])
    z["success"]=(z.rfr_sign==z.label).astype(int)
    z["date"]=pd.to_datetime(z.date)
    z["maturity"]=z.date+pd.Timedelta(days=1)
    return z

def forecasts(z):
    out=[]
    for source,key in z.groupby("source_test"):
      k=key.sort_values("date")
      fit_cache={}
      for period,cur in k[k.year>=2023].groupby(k.date.dt.to_period("M")):
        cutoff=period.to_timestamp() if period.year<=2024 else pd.Timestamp(f"{period.year}-01-01")
        tr=k[(k.date<cutoff)&(k.maturity<=cutoff)]
        if len(tr)<80 or tr.success.nunique()!=2:continue
        kcache=str(cutoff)
        if kcache not in fit_cache:
            model=make_pipeline(StandardScaler(),
                 LogisticRegression(C=1.,penalty="l2",max_iter=3000))
            model.fit(tr[list(FEATURES)].to_numpy(float),tr.success.to_numpy(int))
            prior=(tr.success.sum()+1)/(len(tr)+2)
            fit_cache[kcache]=(model,float(prior),len(tr))
        model,prior,ntrain=fit_cache[kcache]
        pr=np.clip(model.predict_proba(cur[list(FEATURES)].to_numpy(float))[:,1],1e-6,1-1e-6)
        for r,p in zip(cur.itertuples(index=False),pr):
            out.append({"source_test":source,"date":r.date.strftime("%Y-%m-%d"),
              "year":int(r.year),"issue_month":str(period),
              "y_rfr_correct":int(r.success),"actual_night_UP":int(r.label),
              "rfr_pred":int(r.rfr_sign),"signed_return_OVN":float(r.return_OVN),
              "q_correct":float(p),"naive_p_correct":prior,
              "decision_q_ge_055":bool(p>=.55),"n_train":ntrain,
              "frozen_fit_before":str(cutoff),
              "PIT_published_macro_verified":False})
    p=pd.DataFrame(out)
    if p.empty or p.duplicated(["source_test","date"]).any():
        raise RuntimeError("RFR_RELIABILITY_NO_VALID_FORECASTS")
    return p
