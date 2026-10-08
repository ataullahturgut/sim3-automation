"""No ex-post confidence choices. Two pre-declared overnight experts, 90-earlier-score
60th percentile selection; same-date simple baseline comparator and per-year metrics.
"""
from pathlib import Path
import json,sys,time
import numpy as np,pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import confusion_matrix
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as base
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as vix
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
NAME="GOLD_EXECUTION_CONFIDENCE_SELECTIVE_OVN_TEST_20261008"
OUTPUT=AX/(NAME+"_METRICS.csv")
SUMMARY=AX/(NAME+"_SUMMARY.json")
PRIVATE=AX/(NAME+"_PREDICTIONS_PRIVATE.csv")
ACTIVE=("SHAPE_GVZ_HGB","VIX_GVZ_HGB")
CONTROL="BASE_LOGIT"
Q=.60
LOOKBACK=90
MIN_HISTORY=60

def summarize(y,p,prob):
    if not len(y):return None
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    down=tn/(tn+fp) if tn+fp else None
    up=tp/(tp+fn) if tp+fn else None
    return {"accuracy":float(np.mean(p==y)),
            "ba":float(.5*(up+down)) if up is not None and down is not None else None,
            "up_recall":up,"down_recall":down,"brier":float(np.mean(np.square(prob-y))),
            "pred_up_share":float(np.mean(p)),"tn":tn,"fp":fp,"fn":fn,"tp":tp}

def main():
    start=time.time()
    q,t=src.source_load()
    z=vix.joined(base.features(q,t))
    # This subset is independent of the prior results; train all candidates anew
    # with same precise monthly-purged training, and 2025 frozen.
    old=base.predictions(z)
    new=vix.predict_vix(z)
    p=pd.concat([old,new],ignore_index=True)
    p=p[p.target.eq("OVN")].copy()
    if not set((*ACTIVE,CONTROL)).issubset(set(p.model)):
        raise RuntimeError("MISSING_MODEL_PRIOR_DECISION_ID")
    test=p[p.model.isin((*ACTIVE,CONTROL))].copy()
    if test.duplicated(["date","model"]).any():raise RuntimeError("DUPLICATE_SCORE")
    rows=[];selections=[]
    for model in ACTIVE:
        cand=test[test.model.eq(model)].sort_values("date").reset_index(drop=True)
        baseline=test[test.model.eq(CONTROL)].sort_values("date").set_index("date")
        if len(cand)!=len(baseline):raise RuntimeError("BASE_MISMATCH")
        dist=np.abs(cand.p_up.to_numpy(float)-.5)
        for i,r in enumerate(cand.itertuples(index=False)):
            if i<MIN_HISTORY: continue
            hist=dist[max(0,i-LOOKBACK):i]
            if len(hist)<MIN_HISTORY:raise RuntimeError("NO_PRIOR_SCORE_HISTORY")
            threshold=float(np.quantile(hist,Q))
            active=bool(dist[i]>=threshold)
            b=baseline.loc[r.date]
            if int(b.y)!=int(r.y):raise RuntimeError("SAME_DATE_LABEL_MISMATCH")
            selections.append({"model":model,"date":r.date,
                 "year":int(r.year),"y":int(r.y),"p_up":float(r.p_up),
                 "pred":int(r.pred),"base_pred":int(b.pred),"base_p":float(b.p_up),
                 "active":active,"historical_margin_cut":threshold,
                 "margin":float(dist[i])})
    s=pd.DataFrame(selections)
    if s.empty:raise RuntimeError("NO_SELECTIVITY_POPULATION")
    for (model,year),all_case in s.groupby(["model","year"]):
        group=all_case.loc[all_case.active]
        if len(group)==0:raise RuntimeError("NO_SIGNALS_"+str(year))
        for name,pcol,procol in [("SELECTED_SPECIALIST","pred","p_up"),
                                  ("BASE_LOGIT_SAME_DATES","base_pred","base_p")]:
            stat=summarize(group.y.to_numpy(int),group[pcol].to_numpy(int),group[procol].to_numpy(float))
            if stat is None:continue
            rows.append({"model":model,"year":int(year),"policy":name,
                "n_total_with_prior_confidence":len(all_case),
                "n_active":len(group),"coverage":float(len(group)/len(all_case)),
                **stat})
        y=group.y.to_numpy(int)
        new=group.pred.to_numpy(int);oldp=group.base_pred.to_numpy(int)
        saved=int(((new==y)&(oldp!=y)).sum())
        broken=int(((new!=y)&(oldp==y)).sum())
        rows.append({"model":model,"year":int(year),"policy":"PAIRED_RESCUE",
            "n_total_with_prior_confidence":len(all_case),"n_active":len(group),
            "coverage":float(len(group)/len(all_case)),
            "rescued":saved,"broken":broken,"net_rescued":saved-broken,
            "mcnemar_exact_p":float(binomtest(saved,saved+broken,.5).pvalue)
                 if saved+broken else 1.})
    m=pd.DataFrame(rows)
    if (m[(m.policy=="SELECTED_SPECIALIST")&(m.year==2025)].n_active<40).any():
        raise RuntimeError("2025_CONFIDENCE_COVERAGE_TOO_SPARSE")
    out={"status":"COMPLETED_BLIND_TO_CURRENT_LABEL_ROLLING_MARGIN_SELECTIVITY",
      "source_id":src.SOURCE,"total_bars":len(q),
      "policies":list(ACTIVE),
      "rule":"current abs(p_up-.5) >= 60th percentile of up to last 90 PREVIOUS forecast margins; min60 earlier signals",
      "learned_threshold_uses_realized_outcomes":False,
      "same_date_baseline":CONTROL,"roll_rule_quartile":Q,"lookback":LOOKBACK,
      "2023_2024":"historical_monthly_forward_dev","2025":"already_seen_frozen_2024_retro",
      "possible_bank_executable_profit_claim":False,"not_promoted":True,
      "all_statistics_reported_at_same_selected_dates":True,
      "elapsed_seconds":int(time.time()-start)}
    SUMMARY.write_text(json.dumps(out,indent=2)+"\n")
    OUTPUT.write_text(m.to_csv(index=False))
    PRIVATE.write_text(s.to_csv(index=False))
    print("COMPLETE_CONFIDENCE",json.dumps(out),flush=True)
    print(m.to_string(index=False),flush=True)
if __name__=="__main__":main()
