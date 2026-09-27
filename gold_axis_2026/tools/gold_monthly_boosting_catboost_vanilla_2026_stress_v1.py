#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path
import numpy as np
from catboost import CatBoostRegressor

import vw_midas_msvr_successor_v1 as base

TARGETS = tuple(base.month_range("2026-01","2026-08"))
PARAMS = {
    "loss_function":"RMSE",
    "iterations":100,
    "depth":6,
    "learning_rate":0.03,
    "l2_leaf_reg":3.0,
    "random_strength":1.0,
    "boosting_type":"Ordered",
    "random_seed":1701,
    "allow_writing_files":False,
    "verbose":False,
    "thread_count":1,
}

def forward_x(bundle,target,gpr_history):
    p=base.month_shift(target,-1)
    pp=base.month_shift(target,-2)
    z=base.gpr_norm(gpr_history,pp)
    x=[]
    for metal in base.METALS:
        M=bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"FORWARD_FEATURE_MONTH_MISSING {metal} {target}")
        x.extend((math.log(M[p]/M[pp]), base.weighted_daily_return(bundle,metal,p,z)))
    return np.asarray(x,float)

def governed_train_and_x(bundle,target):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin]
    hist={}
    for t in base.month_range("2010-03",origin):
        try:
            hist[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError:
            continue
    keys=sorted(hist)
    if len(keys)<30:
        raise RuntimeError(f"TRAIN_TOO_SMALL target={target} n={len(keys)}")
    X=np.stack([hist[k][0] for k in keys])
    y=np.asarray([float(hist[k][1][0]) for k in keys],float)
    xt=forward_x(bundle,target,gh).reshape(1,-1)
    if X.shape[1]!=8 or xt.shape[1]!=8:
        raise RuntimeError("FEATURE_COUNT_FAIL")
    return keys,X,y,xt

def run():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    rows=[]
    for target in TARGETS:
        origin=base.month_shift(target,-1)
        keys,X,y,xt=governed_train_and_x(b,target)
        model=CatBoostRegressor(**PARAMS)
        model.fit(X,y)
        pred=float(np.asarray(model.predict(xt)).reshape(-1)[0])
        if not math.isfinite(pred) or abs(pred)>=1.0:
            raise RuntimeError(f"PATHOLOGICAL_PRED {target} {pred}")
        if origin not in b.core_gold:
            raise RuntimeError(f"ORIGIN_ACTUAL_MISSING {origin}")
        if target not in b.core_gold:
            raise RuntimeError(f"TARGET_ACTUAL_MISSING {target}")
        previous=float(b.core_gold[origin])
        forecast=float(previous*math.exp(pred))
        # Target actual is read only after the forecast has been produced.
        actual=float(b.core_gold[target])
        ae=float(abs(forecast-actual))
        pred_dir=int(np.sign(forecast-previous))
        actual_dir=int(np.sign(actual-previous))
        rows.append({
            "target":target,
            "origin":origin,
            "train_rows":len(keys),
            "train_first":keys[0],
            "train_last":keys[-1],
            "pred_log_return_gold":pred,
            "forecast":forecast,
            "actual":actual,
            "absolute_error":ae,
            "rw":previous,
            "pred_direction":pred_dir,
            "actual_direction":actual_dir,
            "direction_correct":bool(pred_dir==actual_dir),
        })
        print(f"PROGRESS target={target} forecast={forecast:.6f} actual={actual:.6f} AE={ae:.6f}",flush=True)

    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r["forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a)
    rw_ae=np.abs(rw-a)
    dirs=np.asarray([r["direction_correct"] for r in rows],bool)
    metrics={
        "n":len(rows),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
        "relative_mae_vs_rw":float(ae.sum()/max(float(rw_ae.sum()),1e-12)),
        "direction_correct":int(dirs.sum()),
        "direction_accuracy_pct":float(dirs.mean()*100),
    }

    after=base.authority_invariants
    import psycopg
    with psycopg.connect(dsn,autocommit=True) as cn:
        with cn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv_after=base.authority_invariants(cur)
    if inv_after!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
        "scope":"BOOSTING_CATBOOST_VANILLA_FROZEN_2026_STRESS_V1",
        "freeze_file":"GOLD_MONTHLY_BOOSTING_CATBOOST_VANILLA_FREEZE_BEFORE_2026_2026-09-27.json",
        "model":"CATBOOST_VANILLA_FROZEN",
        "targets":list(TARGETS),
        "target_window":"2026-01..2026-08 completed months only",
        "2026_role":"RETROSPECTIVE_STRESS_REPORT_ONLY_NO_TUNING",
        "forecast_feature_contract":"target X uses origin month p and p-1 only; target actual read only after forecast generation",
        "database":"READ_ONLY",
        "random_split":"NONE",
        "params":PARAMS,
        "metrics":metrics,
        "rows":rows,
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":inv_after,
        "payload_sha256":digest,
    }
    Path("gold_monthly_boosting_catboost_vanilla_2026_stress_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"metrics":metrics,"rows":rows,"payload_sha256":digest},sort_keys=True),flush=True)

if __name__=="__main__":
    run()
