#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_ensemble_e1_baselines_v1 as e1

DEV_START, DEV_END = "2022-04", "2024-12"
MIN_META_HISTORY = 6

POOLS = {
    "FULL5": ["CATBOOST_PRICE","CATBOOST_BALANCED","GBRT","LIGHTGBM","XGB_DIRECTION"],
    "REDUCED4": ["CATBOOST_PRICE","GBRT","LIGHTGBM","XGB_DIRECTION"],
}

E1_REFS = {
    "FULL5_MEDIAN_SUMAE": 1484.731330609916,
    "FULL5_MEDIAN_DIRECTION": 23,
    "REDUCED4_MEDIAN_SUMAE": 1490.6522619575326,
    "REDUCED4_MEDIAN_DIRECTION": 22,
    "CATBOOST_PRICE_SUMAE": 1460.433935309605,
    "CATBOOST_PRICE_DIRECTION": 20,
}

def equal_weights(m):
    return np.ones(m, float) / m

def solve_l1_simplex(P, actual):
    P=np.asarray(P,float)
    actual=np.asarray(actual,float)
    n,m=P.shape
    if n < 1:
        raise RuntimeError("LP_EMPTY_HISTORY")

    # Variables z = [w_1..w_m, e_1..e_n]
    # Min sum e_i
    c=np.concatenate([np.zeros(m), np.ones(n)])

    A1=np.hstack([ P, -np.eye(n)])
    b1=actual.copy()
    A2=np.hstack([-P, -np.eye(n)])
    b2=-actual.copy()
    A_ub=np.vstack([A1,A2])
    b_ub=np.concatenate([b1,b2])

    A_eq=np.zeros((1,m+n),float)
    A_eq[0,:m]=1.0
    b_eq=np.array([1.0])

    bounds=[(0.0,1.0)]*m + [(0.0,None)]*n

    res=linprog(
        c,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"LP_FAIL status={res.status} message={res.message}")

    w=np.asarray(res.x[:m],float)
    w=np.clip(w,0.0,1.0)
    s=float(w.sum())
    if s <= 0:
        raise RuntimeError("LP_ZERO_WEIGHT_SUM")
    w=w/s
    obj=float(np.abs(P@w-actual).sum())
    return w,obj

def prequential_simplex(P, actual, names):
    preds=[]
    hist=[]
    for t in range(len(actual)):
        if t < MIN_META_HISTORY:
            w=equal_weights(P.shape[1])
            fitted_obj=None
            fallback=True
        else:
            w,fitted_obj=solve_l1_simplex(P[:t],actual[:t])
            fallback=False
        pred=float(P[t]@w)
        preds.append(pred)
        hist.append({
            "target_index":int(t),
            "trained_on_prior_dev_origins":int(t),
            "fallback_equal":bool(fallback),
            "prior_fit_sigma_ae": fitted_obj,
            "weights":{n:float(x) for n,x in zip(names,w)},
        })
    return np.asarray(preds,float),hist

def rows(targets,pred,actual,rw,hist=None):
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
        if hist is not None:
            row["weight_state"]=hist[i]
        out.append(row)
    return out

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle=base.load_data(dsn)
    targets,components=e1.read_components(bundle)

    results={}
    for pool,names in POOLS.items():
        t,P,actual,rw=e1.matrix(components,names)
        if t!=targets:
            raise RuntimeError(f"TARGET_ALIGN_FAIL {pool}")

        preq,hist=prequential_simplex(P,actual,names)
        preq_metrics=e1.metrics(preq,actual,rw,targets)

        w_full,obj_full=solve_l1_simplex(P,actual)
        diag=P@w_full
        diag_metrics=e1.metrics(diag,actual,rw,targets)

        results[pool]={
            "components":names,
            "prequential_simplex":{
                "metrics":preq_metrics,
                "rows":rows(targets,preq,actual,rw,hist),
            },
            "full_dev_fit_diagnostic_only":{
                "weights":{n:float(x) for n,x in zip(names,w_full)},
                "lp_objective_sigma_ae":float(obj_full),
                "metrics":diag_metrics,
                "selection_evidence":False,
            },
        }

    # Frozen reference reconciliation from E1.
    full5_med = E1_REFS["FULL5_MEDIAN_SUMAE"]
    red4_med = E1_REFS["REDUCED4_MEDIAN_SUMAE"]
    cb_price = E1_REFS["CATBOOST_PRICE_SUMAE"]

    for p in results.values():
        for section in ("prequential_simplex","full_dev_fit_diagnostic_only"):
            if section=="prequential_simplex":
                pass
            else:
                w=np.array(list(p[section]["weights"].values()),float)
                if np.any(w < -1e-10) or abs(float(w.sum())-1.0)>1e-8:
                    raise RuntimeError("FINAL_WEIGHT_CONSTRAINT_FAIL")

    after=e1.s5.read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    comparison={
        "FULL5":{
            "e1_median_sum_abs_error":full5_med,
            "e1_median_direction":E1_REFS["FULL5_MEDIAN_DIRECTION"],
            "e2_prequential_sum_abs_error":results["FULL5"]["prequential_simplex"]["metrics"]["sum_abs_error"],
            "e2_prequential_direction":results["FULL5"]["prequential_simplex"]["metrics"]["direction_correct"],
        },
        "REDUCED4":{
            "e1_median_sum_abs_error":red4_med,
            "e1_median_direction":E1_REFS["REDUCED4_MEDIAN_DIRECTION"],
            "e2_prequential_sum_abs_error":results["REDUCED4"]["prequential_simplex"]["metrics"]["sum_abs_error"],
            "e2_prequential_direction":results["REDUCED4"]["prequential_simplex"]["metrics"]["direction_correct"],
        },
        "CATBOOST_PRICE":{
            "sum_abs_error":cb_price,
            "direction":E1_REFS["CATBOOST_PRICE_DIRECTION"],
        },
    }
    for pool in ("FULL5","REDUCED4"):
        comparison[pool]["delta_sigma_ae_vs_e1_median"]=float(
            comparison[pool]["e2_prequential_sum_abs_error"]-
            comparison[pool]["e1_median_sum_abs_error"]
        )
        comparison[pool]["beats_e1_median"]=bool(
            comparison[pool]["e2_prequential_sum_abs_error"]<
            comparison[pool]["e1_median_sum_abs_error"]
        )
        comparison[pool]["beats_catboost_price"]=bool(
            comparison[pool]["e2_prequential_sum_abs_error"]<cb_price
        )

    compact={
        p:{
            "preq":[r["forecast"] for r in results[p]["prequential_simplex"]["rows"]],
            "final_weights":results[p]["full_dev_fit_diagnostic_only"]["weights"],
        }
        for p in results
    }
    digest=hashlib.sha256(
        json.dumps(compact,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()

    payload={
        "scope":"BOOSTING_ENSEMBLE_E2_CONSTRAINED_SIMPLEX_V1",
        "freeze_file":"GOLD_MONTHLY_BOOSTING_ENSEMBLE_E2_SIMPLEX_FREEZE_2026-09-28.md",
        "contract":{
            "dev":f"{DEV_START}..{DEV_END}",
            "dev_n":33,
            "minimum_prior_dev_origins":MIN_META_HISTORY,
            "early_fallback":"EQUAL_WEIGHTS",
            "solver":"scipy.optimize.linprog(method=highs)",
            "objective":"CUMULATIVE_ABSOLUTE_PRICE_ERROR_SIGMA_AE",
            "weights":"NONNEGATIVE_SUM_TO_ONE",
            "intercept":"NONE",
            "subset_search":"NONE",
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"QUARANTINED_NOT_USED",
            "full_dev_fit_role":"DIAGNOSTIC_ONLY_NOT_SELECTION_EVIDENCE",
        },
        "results":results,
        "comparison":comparison,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "payload_sha256":digest,
    }

    Path("gold_monthly_boosting_ensemble_e2_simplex_v1_result.json").write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "comparison":comparison,
        "results":{
            p:{
                "prequential":results[p]["prequential_simplex"]["metrics"],
                "full_dev_diagnostic":results[p]["full_dev_fit_diagnostic_only"],
            } for p in results
        },
        "payload_sha256":digest,
        "authority_invariants_unchanged":after==bundle.invariants_before,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
