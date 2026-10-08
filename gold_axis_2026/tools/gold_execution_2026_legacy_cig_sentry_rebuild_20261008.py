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
