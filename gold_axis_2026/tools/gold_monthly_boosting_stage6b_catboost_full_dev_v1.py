#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
from pathlib import Path

import numpy as np
import sklearn
import xgboost
import lightgbm
import catboost

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import gold_monthly_boosting_stage6a_meta_screen_v1 as core

DEV_START = "2022-04"
DEV_END = "2024-12"
FINALISTS = ["VANILLA","PSO","MFO","DE_ABC","HHO","TLBO"]

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r["forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a)
    rw_ae=np.abs(rw-a)
    dirs=np.asarray([r["direction_correct"] for r in rows],bool)
    worst_i=int(np.argmax(ae))
    out={
        "n":len(rows),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100.0),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100.0),
        "median_ae":float(np.median(ae)),
        "monthly_ae_std":float(np.std(ae,ddof=0)),
        "worst_ae":float(ae[worst_i]),
        "worst_month":rows[worst_i]["target"],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rw_ae.sum()),1e-12)),
        "direction_correct":int(dirs.sum()),
        "direction_accuracy_pct":float(dirs.mean()*100.0),
        "rw_sum_abs_error":float(rw_ae.sum()),
    }
    yearly={}
    for y in ("2022","2023","2024"):
        yr=[r for r in rows if r["target"].startswith(y)]
        aa=np.asarray([r["actual"] for r in yr],float)
        ff=np.asarray([r["forecast"] for r in yr],float)
        dd=np.asarray([r["direction_correct"] for r in yr],bool)
        yae=np.abs(ff-aa)
        yearly[y]={
            "n":len(yr),
            "sum_abs_error":float(yae.sum()),
            "mae":float(yae.mean()),
            "direction_correct":int(dd.sum()),
            "direction_accuracy_pct":float(dd.mean()*100.0),
        }
    sums=np.asarray([yearly[y]["sum_abs_error"] for y in ("2022","2023","2024")],float)
    out["yearly_sum_abs_error_std"]=float(np.std(sums,ddof=0))
    return out,yearly

def run(method):
    if method not in FINALISTS:
        raise SystemExit(f"Unsupported finalist: {method}")
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle=core.base.load_data(dsn)
    targets=list(core.base.month_range(DEV_START,DEV_END))
    if len(targets)!=33:
        raise RuntimeError(f"DEV_TARGET_COUNT_FAIL n={len(targets)}")
    cache={t:core.base.all_samples_at_origin(bundle,t,governed=True) for t in targets}

    rows=[]
    for i,target in enumerate(targets,1):
        data=core.prepare_anchor(bundle,cache[target],target,"CATBOOST")
        vtheta,vloss,vcalls=core.run_optimizer("VANILLA","CATBOOST",target,data)

        if method=="VANILLA":
            theta,loss,calls=vtheta,vloss,vcalls
        else:
            theta,loss,calls=core.run_optimizer(method,"CATBOOST",target,data)

        diag=core.outer_diag("CATBOOST",data,theta)
        if diag["forecast"] is None or not math.isfinite(float(diag["forecast"])):
            raise RuntimeError(f"INVALID_FORECAST method={method} target={target}")

        previous=float(data["anchor_prev"])
        actual=float(data["anchor_actual"])
        forecast=float(diag["forecast"])
        row={
            "method":method,
            "target":target,
            "origin":core.base.month_shift(target,-1),
            "train_first":data["keys"][0],
            "train_last":data["keys"][-1],
            "train_rows":len(data["keys"]),
            "inner_train_n":len(data["inner_train_keys"]),
            "inner_val_n":len(data["inner_val_keys"]),
            "inner_val_first":data["inner_val_keys"][0],
            "inner_val_last":data["inner_val_keys"][-1],
            "inner_relative_sum_abs_error":float(loss),
            "vanilla_inner_relative_sum_abs_error":float(vloss),
            "inner_ratio_vs_vanilla":float(loss/max(vloss,1e-12)),
            "objective_calls":int(calls),
            "selected_params":diag["params"],
            "pred_log_return_gold":float(diag["pred_log_return_gold"]),
            "forecast":forecast,
            "actual":actual,
            "rw":previous,
            "absolute_error":float(abs(forecast-actual)),
            "pred_direction":int(np.sign(forecast-previous)),
            "actual_direction":int(np.sign(actual-previous)),
            "direction_correct":bool(diag["direction_correct"]),
        }
        rows.append(row)
        print(
            f"PROGRESS method={method} target={i}/33 month={target} "
            f"AE={row['absolute_error']:.6f} dir={int(row['direction_correct'])}",
            flush=True
        )

    after=core.read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    met,yearly=metrics(rows)
    if met["n"]!=33:
        raise RuntimeError("DEV_N_FAIL")
    if any(not (DEV_START <= r["target"] <= DEV_END) for r in rows):
        raise RuntimeError("NON_DEV_TARGET_FAIL")
    if method!="VANILLA" and any(r["objective_calls"]>core.MAX_EVALS for r in rows):
        raise RuntimeError("OBJECTIVE_BUDGET_FAIL")

    ratios=np.asarray([r["inner_ratio_vs_vanilla"] for r in rows],float)
    summary={
        "method":method,
        **met,
        "mean_inner_ratio_vs_vanilla":float(np.mean(ratios)),
        "median_inner_ratio_vs_vanilla":float(np.median(ratios)),
        "worst_inner_ratio_vs_vanilla":float(np.max(ratios)),
        "months_inner_better_than_vanilla":int(np.sum(ratios < 1.0-1e-12)),
        "total_objective_calls":int(sum(r["objective_calls"] for r in rows)),
    }

    digest=hashlib.sha256(
        json.dumps(rows,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()

    payload={
        "scope":"BOOSTING_STAGE6B_CATBOOST_FULL_DEV_NESTED_V1",
        "method":method,
        "finalist_freeze":"GOLD_MONTHLY_BOOSTING_STAGE6B_FINALIST_FREEZE_2026-09-27.json",
        "contract":{
            "dev":f"{DEV_START}..{DEV_END}",
            "dev_n":33,
            "lane":"CATBOOST",
            "representation":"CURRENT8",
            "target":"Gold next-month log return -> previous monthly Gold average * exp(pred)",
            "loss":"RMSE",
            "inner_validation_months":core.INNER_VAL_MONTHS,
            "optimizer_budget_per_origin":1 if method=="VANILLA" else core.MAX_EVALS,
            "optimizer_reselected_each_origin":method!="VANILLA",
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"NOT_OPENED_NOT_EVALUATED",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR",
        },
        "software":{
            "python":platform.python_version(),
            "numpy":np.__version__,
            "scikit_learn":sklearn.__version__,
            "xgboost":xgboost.__version__,
            "lightgbm":lightgbm.__version__,
            "catboost":catboost.__version__,
        },
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "summary":summary,
        "yearly":yearly,
        "rows":rows,
        "payload_sha256":digest,
    }
    out=Path(f"gold_monthly_boosting_stage6b_catboost_{method.lower()}_result.json")
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"method":method,"summary":summary,"yearly":yearly,"payload_sha256":digest},sort_keys=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=FINALISTS)
    args=ap.parse_args()
    run(args.method)

if __name__=="__main__":
    main()
