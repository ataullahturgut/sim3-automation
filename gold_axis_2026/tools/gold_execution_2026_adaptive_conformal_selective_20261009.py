"""Gibbs-Candes adaptive conformal classification wrapper over OLD frozen 2021 HGB,
novel multiscale CBR for TURKEY DAY/OVN; online, past only. Not a new
directional HGB model, threshold is finite sample calibrated.
"""
from pathlib import Path
import sys,json,time,math
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as source
NAME="GOLD_EXECUTION_2026_ADAPTIVE_CONFORMAL_SELECTIVE_20261009"
METHODS=("CBR_REGIME_PATH","HGB_FROZEN_2021")
POLICIES=("STATIC_CONF80","ACI_CONF80")
ALPHA0=.20
ETA=.01
MIN_HISTORY=42
LOOKBACK=63

def quantile_conformal(scores,alpha):
    n=len(scores)
    k=int(math.ceil((n+1)*(1-float(alpha))))
    return float(np.sort(scores)[k-1]) if k<=n else float("inf")

def run_online(z,method,policy):
    a=z[z.method==method].sort_values("date").copy()
    if a.date.duplicated().any():raise RuntimeError("DUPLICATE_ISSUE")
    history=[];rows=[]
    alpha=ALPHA0
    for r in a.itertuples(index=False):
        prob=float(r.p_up); y=int(r.y)
        if not 0<prob<1 or y not in (0,1):raise RuntimeError("BAD_PROB_OR_LABEL")
        if len(history)>=MIN_HISTORY:
            past=np.array(history[-LOOKBACK:])
            q=quantile_conformal(past,alpha)
            include_down=bool(prob<=q)
            include_up=bool(1-prob<=q)
            setsz=int(include_down)+int(include_up)
            pred=(1 if include_up else 0) if setsz==1 else None
            truth_in=(include_up if y==1 else include_down)
            rows.append({"source_test":r.source_test,"target":r.target,
               "date":r.date,"year":int(r.year),"month":r.month,
               "method":method,"policy":policy,"y":y,
               "p_up":prob,"base_pred":int(prob>=.5),
               "singleton_pred":pred,"acted":setsz==1,
               "set_size":setsz,"true_in_set":bool(truth_in),
               "alpha_t":float(alpha),"conformal_quantile":q,
               "prior_matured_n":len(history),"prior_window_n":len(past)})
            if policy=="ACI_CONF80":
               alpha=float(np.clip(alpha+ETA*(ALPHA0-int(not truth_in)),.02,.45))
        # Now the 2026 result becomes usable only for NEXT issue. For
        # OVERNIGHT, correct prior night completes 09TR and next issue 17TR.
        history.append(float(1-(prob if y==1 else 1-prob)))
    return pd.DataFrame(rows)

def metrics(predictions):
    rows=[]
    for (source,target,year,method,policy),g in predictions.groupby(
        ["source_test","target","year","method","policy"]):
       v=g[g.acted].copy()
       truth=v.y.to_numpy(int)
       selected=v.singleton_pred.to_numpy(int)
       base=v.base_pred.to_numpy(int)
       ndown=int(np.sum(truth==0));nup=int(np.sum(truth==1))
       dn=float(np.mean(selected[truth==0]==0)) if ndown else None
       up=float(np.mean(selected[truth==1]==1)) if nup else None
       bdn=float(np.mean(base[truth==0]==0)) if ndown else None
       bup=float(np.mean(base[truth==1]==1)) if nup else None
       rescue=int(np.sum((selected==truth)&(base!=truth)))
       breaks=int(np.sum((selected!=truth)&(base==truth)))
       rows.append({"source_test":source,"target":target,"year":int(year),
         "method":method,"policy":policy,"source_score_n":len(g),
         "singleton_n":len(v),"decision_coverage":len(v)/len(g),
         "true_set_coverage":float(g.true_in_set.mean()),
         "mean_set_size":float(g.set_size.mean()),
         "singleton_UP_n":int(np.sum(selected==1)),
         "singleton_DOWN_n":int(np.sum(selected==0)),
         "singleton_acc":float(np.mean(selected==truth)) if len(v) else None,
         "singleton_BA":float(.5*(dn+up)) if dn is not None and up is not None else None,
         "singleton_DOWN_recall":dn,"singleton_UP_recall":up,
         "population_DOWN_capture":float(np.sum((selected==0)&(truth==0))/
              max(1,int(np.sum(g.y.to_numpy(int)==0)))),
         "same_action_dates_base_acc":float(np.mean(base==truth)) if len(v) else None,
         "same_action_dates_base_BA":float(.5*(bdn+bup)) if bdn is not None and bup is not None else None,
         "rescues_vs_base_on_actions":rescue,"breaks_vs_base_on_actions":breaks,
         "paired_mcnemar_exact_p":float(binomtest(rescue,rescue+breaks,.5).pvalue)
                        if rescue+breaks else 1.,
         "months_ge5_actions":int(sum(a.acted.sum()>=5 for _,a in g.groupby("month"))),
         "2026_inspected_retrospective":True})
    return pd.DataFrame(rows)

def main():
    t0=time.monotonic()
    q,t,sets=source.source_sets()
    all_predictions=[]
    for name,px,ts in sets:
        panel=source.panel(q,t,px,ts)
        preds=source.forecast(panel,name)
        for target in ("DAY","OVN"):
            z=preds[(preds.target==target)]
            for method in METHODS:
                for policy in POLICIES:
                    m=run_online(z,method,policy)
                    if m.empty:raise RuntimeError("NO_PREVIOUS_MATURED_CALIBRATION")
                    all_predictions.append(m)
    scores=pd.concat(all_predictions,ignore_index=True)
    agg=metrics(scores)
    prefix=str(AX/NAME)
    agg.to_csv(prefix+"_YEAR_METRICS.csv",index=False)
    scores.to_csv(prefix+"_PRIVATE_DATED.csv",index=False)
    details={"status":"REAL_CAUSAL_ONLINE_ADAPTIVE_CONFORMAL_SINGLETON_AUDIT",
      "provenance":"Gibbs and Candes NeurIPS 2021 alpha0 .2 eta .01",
      "base_models":list(METHODS),"policies":list(POLICIES),
      "strict_lookback":LOOKBACK,"min_matured":MIN_HISTORY,
      "2026_original_models_frozen_before_2026":True,
      "2026_outcomes_update_future_issues_only":True,
      "no_future_outcomes_in_prediction_sets":True,
      "not_real_bank_PnL":True,"not_broker_actionable_at_09_if_late_issuance":False,
      "2026_already_inspected":True,
      "outputs":"year metrics source by source, DATE predictions private",
      "elapsed_sec":int(time.monotonic()-t0)}
    Path(prefix+"_SUMMARY.json").write_text(json.dumps(details,indent=2)+"\n")
    print("CONFORMAL_REAL_SELECTIVE_METRICS",agg.to_string(index=False),flush=True)
    print("CONFORMAL_QC",json.dumps(details),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
       import traceback
       fr=traceback.extract_tb(e.__traceback__)[-1]
       qc={"status":"CONFORMAL_RESEARCH_NO_SCORE_FAILED",
           "reason_type":type(e).__name__,"reason":str(e)[:125],
           "function":fr.name,"line":fr.lineno}
       (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(qc,indent=2)+"\n")
       print("CONFORMAL_RUN_FAILURE",json.dumps(qc),flush=True)
