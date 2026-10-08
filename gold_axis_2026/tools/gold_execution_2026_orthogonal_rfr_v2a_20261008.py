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

def evaluate(p):
    rows=[]
    for (source,year),g in p.groupby(["source_test","year"]):
        pred=g.q_correct.to_numpy(float);y=g.y_rfr_correct.to_numpy(int)
        baseline=g.naive_p_correct.to_numpy(float)
        mse=np.mean((pred-y)**2);other=np.mean((baseline-y)**2)
        selection=g.decision_q_ge_055.to_numpy(bool)
        z=g[selection]
        if len(z):
            signal=z.rfr_pred.to_numpy(int);truth=z.actual_night_UP.to_numpy(int)
            d=truth==0;u=truth==1
            dr=float(np.mean(signal[d]==0)) if d.any() else None
            ur=float(np.mean(signal[u]==1)) if u.any() else None
            acc=float(np.mean(signal==truth))
            ba=float(.5*(dr+ur)) if dr is not None and ur is not None else None
        else:dr=ur=acc=ba=None
        rho=roc_auc_score(y,pred) if len(np.unique(y))==2 else None
        rows.append({"source_test":source,"year":int(year),"n_rfr_candidates":len(g),
          "RFR_unfiltered_accuracy":float(y.mean()),
          "Brier_reliability_model":float(mse),
          "Brier_same_history_matured_baseline":float(other),
          "relative_Brier_gain":float(1-mse/other),
          "reliability_AUC":rho,
          "reliability_logloss":float(np.mean(-y*np.log(pred)-(1-y)*np.log(1-pred))),
          "accepted_q055_n":len(z),"q055_coverage":float(selection.mean()),
          "q055_accuracy":acc,"q055_BA":ba,
          "q055_DOWN_recall":dr,"q055_UP_recall":ur,
          "q055_population_DOWN_capture":float(
              np.sum((z.rfr_pred.to_numpy(int)==0)&(z.actual_night_UP.to_numpy(int)==0))
              /max(1,np.sum(g.actual_night_UP.to_numpy(int)==0))),
          "q055_idealized_sum_signed_log_return":float(np.sum(
              np.where(z.rfr_pred.to_numpy(int)==1,1,-1)*z.signed_return_OVN.to_numpy(float))),
          "q055_large_wrong_ge1pct":int(np.sum(
              (z.rfr_pred!=z.actual_night_UP)&(z.signed_return_OVN.abs()>=.01))),
          "frozen_original_PRAMV_v1_NOT_full_replayed":True})
    return pd.DataFrame(rows)

def main():
    started=time.monotonic()
    q,t,sets=rfr.sources.source_sets()
    parts=[]
    for tag,px,ts in sets:
        qfull=pd.concat([q,px]).sort_index()
        if qfull.index.duplicated().any():raise RuntimeError("PRICE_SOURCE_DUPLICATE")
        tall=pd.concat([t,ts],ignore_index=True)
        if tall.date.duplicated().any():raise RuntimeError("TARGET_DATE_DUPLICATE")
        r=rfr.extract(qfull,tall)
        r["source_test"]=tag
        frame=early_features(qfull,r)
        parts.append(frame)
        print("RFR_EARLY_ORTHOGONAL_SOURCE_READY",tag,
           frame.groupby("year").size().to_dict(),flush=True)
    panel=pd.concat(parts,ignore_index=True)
    forecasts_df=forecasts(panel)
    result=evaluate(forecasts_df)
    report={"status":"ORIGINAL_PRAMV_V2A_ORTHOGONAL_RELIABILITY_ACTUALLY_EXECUTED",
      "retargeted_original":True,
      "forecast_object":"RFR_correct, not directly full UP-DOWN next-night",
      "early_origin":"14:00-16:00 TRT, disjoint from late reversal 16:00-17:00",
      "training_method":"exact previously proposed StandardScaler L2 Logistic C1",
      "year2023_2024":"monthly expanding prior-matured reversal successes",
      "year2025_2026":"frozen at prior Jan1, previously inspected retrospective not blind",
      "macro_PIT":"NOT certified for 2026; full PRAMV not run",
      "sources":"source-checked mirror and native direct separately",
      "q055_policy":"new preregistered challenger, not frozen PRAMV original",
      "no_2026_future_label_in_train":True,
      "bank_spread_PnL":False,"no_deployment":True,
      "elapsed_seconds":int(time.monotonic()-started)}
    path=str(AX/NAME)
    result.to_csv(path+"_METRICS.csv",index=False)
    forecasts_df.to_csv(path+"_PRIVATE_DATED.csv",index=False)
    Path(path+"_SUMMARY.json").write_text(json.dumps(report,indent=2)+"\n")
    print("REAL_PRAMV_V2A_RELIABILITY_METRICS",result.to_string(index=False),flush=True)
    print("REAL_PRAMV_V2A_STATE",json.dumps(report),flush=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        z=traceback.extract_tb(e.__traceback__)[-1]
        record={"status":"ORTHOGONAL_RFR_V2A_BLOCKED_NO_SCORE",
            "error":type(e).__name__,"message":str(e)[:130],
            "function":z.name,"line":z.lineno}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(record,indent=2)+"\n")
        print("RFR_V2A_RUN_FAILURE",json.dumps(record),flush=True)
