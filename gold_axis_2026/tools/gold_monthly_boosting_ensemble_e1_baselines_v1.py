#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage5_regularization_v1 as s5

DEV_START, DEV_END="2022-04","2024-12"
MIN_META_HISTORY=6

SPECS={
    "CATBOOST_PRICE":("CATBOOST_PRICE","CB_R0_BASELINE"),
    "CATBOOST_BALANCED":("CATBOOST_BALANCED","CB_R0_BASELINE"),
    "GBRT":("GBRT_PRICE_BALANCED","G_R0_BASELINE"),
    "LIGHTGBM":("LIGHTGBM_PRICE_BALANCED","L_R0_BASELINE"),
    "XGB_DIRECTION":("XGBOOST_DIRECTION","X_R1_L2_5"),
}
POOLS={
    "FULL5":["CATBOOST_PRICE","CATBOOST_BALANCED","GBRT","LIGHTGBM","XGB_DIRECTION"],
    "REDUCED4":["CATBOOST_PRICE","GBRT","LIGHTGBM","XGB_DIRECTION"],
}
REFS={
    "CATBOOST_PRICE":(1460.433935309605,20),
    "CATBOOST_BALANCED":(1481.261937710369,22),
    "GBRT":(1500.42946858865,22),
    "LIGHTGBM":(1534.6087211346264,22),
    "XGB_DIRECTION":(1679.8371517758826,23),
}

def read_components(bundle):
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in targets}
    out={}
    for name,(lane_name,profile_name) in SPECS.items():
        lane=next(x for x in s5.LANES if x["lane"]==lane_name)
        profile,reg=next(x for x in lane["profiles"] if x[0]==profile_name)
        r=s5.evaluate(bundle,cache,lane,profile,reg)
        refae,refdir=REFS[name]
        m=r["metrics"]
        if abs(float(m["sum_abs_error"])-refae)>1e-8:
            raise RuntimeError(f"COMPONENT_AE_REPRO_FAIL {name}")
        if int(m["direction_correct"])!=refdir:
            raise RuntimeError(f"COMPONENT_DIR_REPRO_FAIL {name}")
        out[name]=r
    return targets,out

def matrix(components,names):
    targets=[r["target"] for r in components[names[0]]["rows"]]
    P=np.column_stack([
        [float(r["forecast"]) for r in components[n]["rows"]]
        for n in names
    ])
    rows0=components[names[0]]["rows"]
    actual=np.asarray([float(r["actual"]) for r in rows0],float)
    rw=np.asarray([float(r["rw"]) for r in rows0],float)
    for n in names:
        if [r["target"] for r in components[n]["rows"]]!=targets:
            raise RuntimeError(f"TARGET_ALIGNMENT_FAIL {n}")
    return targets,P,actual,rw

def metrics(pred,actual,rw,targets):
    pred=np.asarray(pred,float); actual=np.asarray(actual,float); rw=np.asarray(rw,float)
    ae=np.abs(pred-actual)
    rw_ae=np.abs(rw-actual)
    dc=np.sign(pred-rw)==np.sign(actual-rw)
    wi=int(np.argmax(ae))
    out={
        "n":int(len(actual)),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((pred-actual)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(actual),1e-12))*100.0),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(actual).sum(),1e-12)*100.0),
        "median_ae":float(np.median(ae)),
        "monthly_ae_std":float(np.std(ae,ddof=0)),
        "worst_ae":float(ae[wi]),
        "worst_month":targets[wi],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rw_ae.sum()),1e-12)),
        "direction_correct":int(dc.sum()),
        "direction_accuracy_pct":float(dc.mean()*100.0),
        "rw_sum_abs_error":float(rw_ae.sum()),
    }
    yearly={}
    for y in ("2022","2023","2024"):
        idx=[i for i,t in enumerate(targets) if t.startswith(y)]
        yy_pred=pred[idx]; yy_actual=actual[idx]; yy_rw=rw[idx]
        yy_ae=np.abs(yy_pred-yy_actual); yy_dc=np.sign(yy_pred-yy_rw)==np.sign(yy_actual-yy_rw)
        yearly[y]={
            "n":len(idx),
            "sum_abs_error":float(yy_ae.sum()),
            "mae":float(yy_ae.mean()),
            "direction_correct":int(yy_dc.sum()),
            "direction_accuracy_pct":float(yy_dc.mean()*100.0),
        }
    out["yearly"]=yearly
    return out

def equal_weights(m):
    return np.ones(m,float)/m

def inverse_mae_weights(P,actual):
    mae=np.mean(np.abs(P-actual[:,None]),axis=0)
    inv=1.0/np.maximum(mae,1e-12)
    return inv/inv.sum()

def prequential_inverse(P,actual,names):
    m=P.shape[1]
    pred=[]; history=[]
    for t in range(len(actual)):
        if t<MIN_META_HISTORY:
            w=equal_weights(m)
            trained_on=t
            fallback=True
        else:
            w=inverse_mae_weights(P[:t],actual[:t])
            trained_on=t
            fallback=False
        pred.append(float(P[t]@w))
        history.append({
            "index":t,
            "trained_on_prior_dev_origins":int(trained_on),
            "fallback_equal":fallback,
            "weights":{n:float(x) for n,x in zip(names,w)},
        })
    return np.asarray(pred,float),history

def rows(targets,pred,actual,rw,weight_history=None):
    out=[]
    for i,t in enumerate(targets):
        row={
            "target":t,
            "forecast":float(pred[i]),
            "actual":float(actual[i]),
            "rw":float(rw[i]),
            "absolute_error":float(abs(pred[i]-actual[i])),
            "direction_correct":bool(
                int(np.sign(pred[i]-rw[i]))==int(np.sign(actual[i]-rw[i]))
            ),
        }
        if weight_history is not None:
            row["weight_state"]=weight_history[i]
        out.append(row)
    return out

def evaluate_pool(components,pool,names):
    targets,P,actual,rw=matrix(components,names)

    w=equal_weights(len(names))
    eq=P@w
    med=np.median(P,axis=1)
    inv,hist=prequential_inverse(P,actual,names)
    final_inv=inverse_mae_weights(P,actual)

    variants={
        "EQUAL_MEAN":{
            "metrics":metrics(eq,actual,rw,targets),
            "rows":rows(targets,eq,actual,rw),
            "fixed_weights":{n:float(x) for n,x in zip(names,w)},
        },
        "MEDIAN":{
            "metrics":metrics(med,actual,rw,targets),
            "rows":rows(targets,med,actual,rw),
            "weights":"NOT_APPLICABLE_MEDIAN",
        },
        "PREQUENTIAL_INVERSE_MAE":{
            "metrics":metrics(inv,actual,rw,targets),
            "rows":rows(targets,inv,actual,rw,hist),
            "final_all_dev_weights_context_only":{
                n:float(x) for n,x in zip(names,final_inv)
            },
        },
    }
    ranking=sorted(
        [{"variant":k,**v["metrics"]} for k,v in variants.items()],
        key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["variant"])
    )
    return {
        "pool":pool,
        "components":names,
        "variants":variants,
        "ranking":ranking,
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    targets,components=read_components(b)

    results={p:evaluate_pool(components,p,names) for p,names in POOLS.items()}

    allrank=[]
    for p,r in results.items():
        for z in r["ranking"]:
            allrank.append({"pool":p,**z})
    allrank.sort(key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["pool"],z["variant"]))

    best=allrank[0]
    after=s5.read_invariants(dsn)
    if after!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    # Confirm no external period has been constructed.
    if targets[0]!=DEV_START or targets[-1]!=DEV_END or len(targets)!=33:
        raise RuntimeError("DEV_TARGET_SCOPE_FAIL")

    compact={
        p:{
            v:{
                "metrics":r["variants"][v]["metrics"],
                "forecasts":[x["forecast"] for x in r["variants"][v]["rows"]],
            }
            for v in r["variants"]
        } for p,r in results.items()
    }
    digest=hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

    payload={
        "scope":"BOOSTING_ENSEMBLE_E1_BASELINES_V1",
        "pool_freeze":"GOLD_MONTHLY_BOOSTING_ENSEMBLE_POOL_FREEZE_2026-09-28.md",
        "contract":{
            "dev":f"{DEV_START}..{DEV_END}",
            "dev_n":33,
            "pool_frozen_before_ensemble_evaluation":True,
            "variants":["EQUAL_MEAN","MEDIAN","PREQUENTIAL_INVERSE_MAE"],
            "minimum_prior_dev_origins_before_inverse_mae":MIN_META_HISTORY,
            "early_prequential_fallback":"EQUAL_WEIGHTS",
            "optimized_simplex":"NOT_AUTHORIZED_NOT_RUN",
            "subset_search":"NONE",
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"QUARANTINED_NOT_USED",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR",
        },
        "component_metrics":{n:components[n]["metrics"] for n in components},
        "pools":results,
        "overall_ranking":allrank,
        "best_e1":best,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "payload_sha256":digest,
    }
    Path("gold_monthly_boosting_ensemble_e1_baselines_v1_result.json").write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "best_e1":best,
        "overall_ranking":allrank,
        "inverse_final_weights_context":{
            p:results[p]["variants"]["PREQUENTIAL_INVERSE_MAE"]["final_all_dev_weights_context_only"]
            for p in results
        },
        "payload_sha256":digest,
        "authority_invariants_unchanged":after==b.invariants_before,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
