"""Execution-clock reconstruction of historical H3/CIG/SENTRY expert routing.

NOT an old 74.4% CIG replication: all experts rebuilt for audited 09/17 TR labels.
2023/24 monthly history, 2025 & 2026 frozen at prior Jan 1; only actual
prior same-target fully matured direction outcomes may inform SENTRY/DART state.
"""
from __future__ import annotations
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as geo
import gold_execution_2020_2025_training_start_sensitivity_20261008 as old
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as shape
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as vix
NAME="GOLD_EXECUTION_2026_LEGACY_CIG_SENTRY_REBUILD_20261008"
EXPERTS=("BASE_LOGIT","SHAPE_GVZ_HGB","VIX_GVZ_HGB","CBR_REGIME_PATH")
POLICIES=("HGB_REFERENCE","EQUAL4","MEDIAN4","CIG4_UNANIMOUS","CIG3_DIVERSITY",
          "SENTRY63_PATH_FAILOVER","RESCUE_CONFIRMED_DOWN")
START=2021

def forecast_raw(z,source):
    out=[]
    z=vix.joined(z)
    for target in ("DAY","OVN"):
      eligible=z[z.target==target].sort_values("date").copy()
      cached={}
      for period,day in eligible[eligible.year>=2023].groupby(
                eligible.date.dt.to_period("M")):
        fit_before=period.to_timestamp() if period.year<=2024 else pd.Timestamp(f"{period.year}-01-01")
        tr=eligible[(eligible.date<fit_before)&(eligible.year>=START)]
        if target=="OVN":tr=tr[tr.next_date<=fit_before]
        if len(tr)<290 or tr.y.nunique()!=2:raise RuntimeError("TRAIN_HISTORY_INVALID")
        if not (tr.date<day.date.min()).all():raise RuntimeError("FORECAST_ORIGIN_LEAK")
        keys={
          "BASE_LOGIT":shape.BASE_DAY if target=="DAY" else shape.BASE_OVN,
          "SHAPE_GVZ_HGB":old.COLUMNS["SHAPE_GVZ_HGB"],
          "VIX_GVZ_HGB":old.COLUMNS["VIX_GVZ_HGB"],
        }
        cachekey=(target,str(fit_before))
        if cachekey not in cached:
            cached[cachekey]={
               name:old.method_fit(tr[cols].to_numpy(float),tr.y.to_numpy(int),name)
               for name,cols in keys.items()}
        ps={name:cached[cachekey][name].predict_proba(day[cols].to_numpy(float))[:,1]
            for name,cols in keys.items()}
        ps["CBR_REGIME_PATH"]=geo.analogue(tr,day,True)
        for i,r in enumerate(day.itertuples(index=False)):
            record={"source_test":source,"target":target,
                "date":r.date.strftime("%Y-%m-%d"),
                "next_date":r.next_date.strftime("%Y-%m-%d") if pd.notna(r.next_date) else None,
                "year":int(r.year),"month":str(period),"y":int(r.y),
                "fit_before":str(fit_before),"train_n":len(tr)}
            for name in EXPERTS:
                record[name]=float(np.clip(ps[name][i],1e-6,1-1e-6))
            out.append(record)
    p=pd.DataFrame(out)
    if p.duplicated(["target","date"]).any():raise RuntimeError("DUPLICATE_EXPERT_ORIGIN")
    return p

def choose(raw):
    outputs=[]
    for target,g in raw.groupby("target"):
      old_results=[]
      route="SHAPE_GVZ_HGB"
      for r in g.sort_values("date").itertuples(index=False):
        cutoff=pd.Timestamp(r.date)
        past=[x for x in old_results if pd.Timestamp(x["maturity"])<=cutoff]
        prior=past[-63:]
        benefit=sum(x["path_correct"]-x["base_correct"] for x in prior)
        disagreements=[x for x in past if x["disagree"]]
        if route=="SHAPE_GVZ_HGB" and len(prior)>=42 and benefit>=3:
            route="CBR_REGIME_PATH"
        elif route=="CBR_REGIME_PATH" and len(disagreements)>=8:
            if sum(x["path_correct"] for x in disagreements[-8:])<=1:
                route="SHAPE_GVZ_HGB"
        probs=np.array([getattr(r,m) for m in EXPERTS],float)
        dirs=(probs>=.5).astype(int)
        baseline=float(getattr(r,"SHAPE_GVZ_HGB"))
        variants={
           "HGB_REFERENCE":(baseline,True),
           "EQUAL4":(float(np.mean(probs)),True),
           "MEDIAN4":(float(np.median(probs)),True),
           "CIG4_UNANIMOUS":(float(np.mean(probs)),bool(len(set(dirs))==1)),
           "CIG3_DIVERSITY":(float(np.mean(probs[[0,2,3]])),
                                  bool(len(set(dirs[[0,2,3]]))==1)),
           "SENTRY63_PATH_FAILOVER":(float(getattr(r,route)),True),
           "RESCUE_CONFIRMED_DOWN":(
              float(getattr(r,"CBR_REGIME_PATH"))
              if (dirs[1]==1 and dirs[2]==0 and dirs[3]==0
                  and len(prior)>=42 and benefit>=3) else baseline,True)}
        for name,(p,active) in variants.items():
          outputs.append({"source_test":r.source_test,"target":target,
             "date":r.date,"month":r.month,"year":r.year,"policy":name,
             "y":int(r.y),"p_up":p,"pred":int(p>=.5) if active else None,
             "acted":bool(active),"route_state":route,
             "past_matured_count":len(prior),"past_net_path_rescues":benefit,
             "expert_confidence_span":float(max(probs)-min(probs)),
             "expert_agreement4":bool(len(set(dirs))==1),
             "expert_agreement3":bool(len(set(dirs[[0,2,3]]))==1)})
        maturity=r.next_date if target=="OVN" else r.date
        old_results.append({"maturity":maturity,"path_correct":int(dirs[3]==r.y),
               "base_correct":int(dirs[1]==r.y),"disagree":bool(dirs[1]!=dirs[3])})
    return pd.DataFrame(outputs)

def evaluate(results):
    summaries=[];matched=[]
    for (source,target,year),g in results.groupby(["source_test","target","year"]):
      base=g[g.policy=="HGB_REFERENCE"].set_index("date").sort_index()
      if len(base)<30:raise RuntimeError("YEAR_SOURCE_TOO_SPARSE")
      for name in POLICIES:
        allp=g[g.policy==name].set_index("date").sort_index()
        if not allp.index.equals(base.index) or not (allp.y==base.y).all():
          raise RuntimeError("POLICY_SCORED_ON_DIFFERENT_DATES")
        z=allp[allp.acted].copy()
        q=z.pred.to_numpy(int);y=z.y.to_numpy(int)
        p=z.p_up.to_numpy(float)
        ndown=int((y==0).sum());nup=int((y==1).sum())
        dn=float(np.mean(q[y==0]==0)) if ndown else None
        up=float(np.mean(q[y==1]==1)) if nup else None
        old=base.loc[z.index].pred.to_numpy(int)
        saves=int(np.sum((q==y)&(old!=y)))
        breaks=int(np.sum((q!=y)&(old==y)))
        bpred=base.loc[z.index].p_up.to_numpy(float)
        summaries.append({
          "source_test":source,"target":target,"year":int(year),"policy":name,
          "eligible_n":len(base),"acted_n":len(z),"coverage":len(z)/len(base),
          "acted_accuracy":float(np.mean(q==y)) if len(z) else None,
          "acted_BA":float(.5*(dn+up)) if dn is not None and up is not None else None,
          "acted_down_recall":dn,"acted_up_recall":up,
          "acted_Brier":float(np.mean((p-y)**2)) if len(z) else None,
          "same_act_dates_base_accuracy":float(np.mean(old==y)) if len(z) else None,
          "same_act_dates_base_Brier":float(np.mean((bpred-y)**2)) if len(z) else None,
          "population_DOWN_caught_fraction":float(
             np.sum((q==0)&(y==0))/max(1,np.sum(base.y.to_numpy(int)==0))),
          "rescues_vs_base":saves,"breaks_vs_base":breaks,"net_rescues":saves-breaks,
          "mcnemar_p":float(binomtest(saves,saves+breaks,.5).pvalue) if saves+breaks else 1.,
          "all_DOWN_n":int(np.sum(base.y.to_numpy(int)==0)),
          "acted_true_DOWN_n":ndown,"acted_true_UP_n":nup,
          "predicted_UP_frac":float(np.mean(q)) if len(z) else None,
          "selective_not_full_coverage":bool(len(z)<len(base))})
    return pd.DataFrame(summaries)

def correlation(raw):
    result=[]
    for (src,target,year),g in raw.groupby(["source_test","target","year"]):
      ex=g[list(EXPERTS)].to_numpy(float)
      co=np.corrcoef(ex,rowvar=False)
      result.append({"source_test":src,"target":target,"year":int(year),
          "n":len(g),
          "HGB_shape_vs_HGB_vix_corr":float(co[1,2]),
          "HGB_shape_vs_CBR_path_corr":float(co[1,3]),
          "BASE_vs_CBR_path_corr":float(co[0,3]),
          "all4_direction_agreement":float(np.mean((ex>=.5).min(axis=1)==(ex>=.5).max(axis=1))),
          "diversity3_direction_agreement":float(np.mean(
             (ex[:,[0,2,3]]>=.5).min(axis=1)==(ex[:,[0,2,3]]>=.5).max(axis=1)))})
    return pd.DataFrame(result)

def main():
    tic=time.time()
    q,t,sets=geo.source_sets()
    outputs=[];expert=[]
    for name,quotes,labels in sets:
      features=geo.panel(q,t,quotes,labels)
      a=forecast_raw(features,name)
      out=choose(a)
      outputs.append(out);expert.append(a)
      print("LEGACY_EXPERTS_SAME_CLOCK",name,
          a.groupby(["target","year"]).size().to_dict(),flush=True)
    p=pd.concat(outputs,ignore_index=True)
    e=pd.concat(expert,ignore_index=True)
    metrics=evaluate(p);corr=correlation(e)
    if set(p.policy)!=set(POLICIES):raise RuntimeError("MISSING_POLICY")
    report={"status":"REBUILT_LEGACY_H3_ROUTING_ON_NEW_DAY_OVN_ACTUALLY_EXECUTED",
      "research":"Historical H3/CIG/SENTRY/DART design REBUILT on target 09TR-17TR and 17TR-next09TR",
      "not_original_CIG_model_predictions":True,
      "source_and_training":"EV Dukascopy-derived 2020-25 and two 2026 independently price-gated source populations",
      "2023_2024":"past-month training, fully matured labels",
      "2025_2026":"old experts trained only prior calendar years, not issue year",
      "2025_2026_inspected_not_blind":True,
      "expert_names":list(EXPERTS),"policies":list(POLICIES),
      "SENTRY_window":63,"SENTRY_min_mature":42,"SENTRY_net_rescue_entry":3,
      "DART_last8_disagreements_failure_exit":True,
      "anti_clone_correlation_report":True,
      "same_act_date_comparison":True,
      "no_champion_promoted":True,
      "no_real_Turkish_bank_bidask_spread_PnL":True,
      "elapsed_seconds":int(time.time()-tic)}
    stem=str(AX/NAME)
    Path(stem+"_SUMMARY.json").write_text(json.dumps(report,indent=2)+"\n")
    metrics.to_csv(stem+"_YEAR_METRICS.csv",index=False)
    corr.to_csv(stem+"_DIVERSITY.csv",index=False)
    p.to_csv(stem+"_PRIVATE_DATED_POLICIES.csv",index=False)
    e.to_csv(stem+"_PRIVATE_DATED_EXPERTS.csv",index=False)
    print("LEGACY_TRANSFER_METRICS",metrics.to_string(index=False),flush=True)
    print("EXPERT_DEPENDENCE",corr.to_string(index=False),flush=True)
    print("LEGACY_TRANSFER_REPORT",json.dumps(report),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
      import traceback
      z=traceback.extract_tb(e.__traceback__)[-1]
      a={"status":"LEGACY_CIG_SENTRY_REBUILD_BLOCKED","error_type":type(e).__name__,
         "function":z.name,"line":z.lineno,"reason":str(e)[:120],
         "no_claim_of_strategy_success":True}
      (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(a,indent=2)+"\n")
      print("LEGACY_REBUILD_FAILURE",json.dumps(a),flush=True)
