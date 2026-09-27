#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
import optuna
import psycopg
import sklearn
from sklearn.ensemble import GradientBoostingRegressor

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage2_feature_representation_v1 as s2

DEV_START, DEV_END = "2022-04", "2024-12"
TRAIN_START = "2010-03"
INNER_VAL_MONTHS = 12
TRIALS = 80
BASE_SEED = 1701
REP = "DAILY_SUMMARY12"

BASELINE_PARAMS = {
    "max_depth": 2,
    "n_estimators": 100,
    "learning_rate": 0.10,
    "min_samples_leaf": 2,
    "subsample": 1.0,
    "max_features": None,
}
BASELINE_DEV_SUMAE_REF = 1500.42946858865
BASELINE_DEV_DIRECTION_REF = 22
CMAES_DEV_SUMAE_REF = 1650.1984960672644
CMAES_DEV_DIRECTION_REF = 18

def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def make_model(params):
    return GradientBoostingRegressor(
        loss="absolute_error",
        random_state=1701,
        **params,
    )

def build_origin_data(bundle, target):
    origin = base.month_shift(target, -1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh = bundle.gpr_vintages[origin]

    samples={}
    for t in base.month_range(TRAIN_START, origin):
        try:
            samples[t] = base.sample_for_target(bundle, t, gh, True)
        except RuntimeError:
            continue

    keys=sorted(k for k in samples if TRAIN_START <= k <= origin)
    if len(keys) < INNER_VAL_MONTHS + 36:
        raise RuntimeError(f"INNER_HISTORY_TOO_SMALL target={target} n={len(keys)}")

    split=len(keys)-INNER_VAL_MONTHS
    tr=keys[:split]
    va=keys[split:]

    Xtr=np.stack([s2.rep_feature(bundle,samples,k,REP) for k in tr])
    ytr=np.asarray([float(samples[k][1][0]) for k in tr],float)
    Xv=np.stack([s2.rep_feature(bundle,samples,k,REP) for k in va])
    actual_v=np.asarray([float(bundle.core_gold[k]) for k in va],float)
    prev_v=np.asarray([float(bundle.core_gold[base.month_shift(k,-1)]) for k in va],float)

    Xall=np.stack([s2.rep_feature(bundle,samples,k,REP) for k in keys])
    yall=np.asarray([float(samples[k][1][0]) for k in keys],float)
    xt=s2.rep_feature(bundle,samples,target,REP).reshape(1,-1)

    if not all(np.isfinite(x).all() for x in (Xtr,ytr,Xv,actual_v,prev_v,Xall,yall,xt)):
        raise RuntimeError(f"NONFINITE_DATA target={target}")

    return {
        "origin":origin,
        "keys":keys,
        "inner_train_keys":tr,
        "inner_val_keys":va,
        "Xtr":Xtr,
        "ytr":ytr,
        "Xv":Xv,
        "actual_v":actual_v,
        "prev_v":prev_v,
        "rw_ae":float(np.abs(prev_v-actual_v).sum()),
        "Xall":Xall,
        "yall":yall,
        "xt":xt,
        "anchor_prev":float(bundle.core_gold[origin]),
    }

def baseline_inner_loss(data):
    model=make_model(BASELINE_PARAMS)
    model.fit(data["Xtr"],data["ytr"])
    pred=np.asarray(model.predict(data["Xv"]),float).reshape(-1)
    fc=data["prev_v"]*np.exp(pred)
    ae=float(np.abs(fc-data["actual_v"]).sum())
    return float(ae/max(data["rw_ae"],1e-12))

def outer_forecast(data,params):
    model=make_model(params)
    model.fit(data["Xall"],data["yall"])
    pred=float(np.asarray(model.predict(data["xt"])).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_OUTER_PRED pred={pred}")
    fc=float(data["anchor_prev"]*math.exp(pred))
    return pred,fc

def tpe_optimize(data,target):
    seed = int((BASE_SEED + 1009 * sum(map(ord,target))) % 2147483000)
    sampler=optuna.samplers.TPESampler(
        seed=seed,
        n_startup_trials=10,
        multivariate=False,
        group=False,
        constant_liar=False,
    )
    study=optuna.create_study(direction="minimize",sampler=sampler)

    def objective(trial):
        params={
            "max_depth":trial.suggest_int("max_depth",1,5),
            "n_estimators":trial.suggest_int("n_estimators",50,500),
            "learning_rate":trial.suggest_float("learning_rate",0.01,0.20,log=True),
            "min_samples_leaf":trial.suggest_int("min_samples_leaf",1,10),
            "subsample":trial.suggest_float("subsample",0.60,1.00),
            "max_features":trial.suggest_float("max_features",0.60,1.00),
        }
        try:
            model=make_model(params)
            model.fit(data["Xtr"],data["ytr"])
            pred=np.asarray(model.predict(data["Xv"]),float).reshape(-1)
            if (not np.isfinite(pred).all()) or np.any(np.abs(pred)>=1.0):
                return 1e12
            fc=data["prev_v"]*np.exp(pred)
            ae=float(np.abs(fc-data["actual_v"]).sum())
            return float(ae/max(data["rw_ae"],1e-12))
        except Exception:
            return 1e12

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study.optimize(objective,n_trials=TRIALS,n_jobs=1,show_progress_bar=False,gc_after_trial=False)

    if len(study.trials)!=TRIALS:
        raise RuntimeError(f"TPE_TRIAL_COUNT_FAIL target={target} n={len(study.trials)}")
    best_params=dict(study.best_params)
    best_loss=float(study.best_value)
    return best_params,best_loss,TRIALS,seed

def metrics(rows,prefix=""):
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r[prefix+"forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a)
    rw_ae=np.abs(rw-a)
    dc=np.asarray([r[prefix+"direction_correct"] for r in rows],bool)
    wi=int(np.argmax(ae))
    return {
        "n":len(rows),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100.0),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100.0),
        "median_ae":float(np.median(ae)),
        "monthly_ae_std":float(np.std(ae,ddof=0)),
        "worst_ae":float(ae[wi]),
        "worst_month":rows[wi]["target"],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rw_ae.sum()),1e-12)),
        "direction_correct":int(dc.sum()),
        "direction_accuracy_pct":float(dc.mean()*100.0),
        "rw_sum_abs_error":float(rw_ae.sum()),
    }

def yearly(rows,prefix=""):
    out={}
    for y in ("2022","2023","2024"):
        rr=[r for r in rows if r["target"].startswith(y)]
        out[y]=metrics(rr,prefix)
    return out

def run():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,DEV_END))
    if len(targets)!=33:
        raise RuntimeError(f"DEV_N_FAIL {len(targets)}")

    rows=[]
    for i,target in enumerate(targets,1):
        data=build_origin_data(bundle,target)

        base_inner=baseline_inner_loss(data)
        bp,bf=outer_forecast(data,BASELINE_PARAMS)

        params,tpe_inner,trials,seed=tpe_optimize(data,target)
        tp,tf=outer_forecast(data,params)

        if target not in bundle.core_gold:
            raise RuntimeError(f"DEV_ACTUAL_MISSING {target}")
        actual=float(bundle.core_gold[target])
        rw=float(data["anchor_prev"])

        row={
            "target":target,
            "origin":data["origin"],
            "train_first":data["keys"][0],
            "train_last":data["keys"][-1],
            "train_rows":len(data["keys"]),
            "inner_train_n":len(data["inner_train_keys"]),
            "inner_val_n":len(data["inner_val_keys"]),
            "inner_val_first":data["inner_val_keys"][0],
            "inner_val_last":data["inner_val_keys"][-1],
            "baseline_inner_relative_sum_abs_error":float(base_inner),
            "tpe_inner_relative_sum_abs_error":float(tpe_inner),
            "inner_ratio_vs_baseline":float(tpe_inner/max(base_inner,1e-12)),
            "tpe_trials":trials,
            "tpe_seed":seed,
            "selected_params":params,
            "baseline_params":BASELINE_PARAMS,
            "baseline_pred_log_return_gold":float(bp),
            "baseline_forecast":float(bf),
            "tpe_pred_log_return_gold":float(tp),
            "tpe_forecast":float(tf),
            "actual":actual,
            "rw":rw,
            "baseline_absolute_error":float(abs(bf-actual)),
            "tpe_absolute_error":float(abs(tf-actual)),
            "baseline_direction_correct":bool(int(np.sign(bf-rw))==int(np.sign(actual-rw))),
            "tpe_direction_correct":bool(int(np.sign(tf-rw))==int(np.sign(actual-rw))),
        }
        rows.append(row)
        print(
            f"PROGRESS target={i}/33 month={target} "
            f"baseAE={row['baseline_absolute_error']:.6f} tpeAE={row['tpe_absolute_error']:.6f} "
            f"ratio={row['inner_ratio_vs_baseline']:.6f}",
            flush=True
        )

    after=read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    base_met=metrics(rows,"baseline_")
    tpe_met=metrics(rows,"tpe_")
    base_year=yearly(rows,"baseline_")
    tpe_year=yearly(rows,"tpe_")

    if abs(base_met["sum_abs_error"]-BASELINE_DEV_SUMAE_REF)>1e-8:
        raise RuntimeError(f"BASELINE_REPRO_FAIL ref={BASELINE_DEV_SUMAE_REF} cur={base_met['sum_abs_error']}")
    if base_met["direction_correct"]!=BASELINE_DEV_DIRECTION_REF:
        raise RuntimeError(f"BASELINE_DIRECTION_REPRO_FAIL ref={BASELINE_DEV_DIRECTION_REF} cur={base_met['direction_correct']}")

    ratios=np.asarray([r["inner_ratio_vs_baseline"] for r in rows],float)
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()

    payload={
        "scope":"BOOSTING_STAGE6C_B_TPE_GBRT_FULL_DEV_NESTED_V1",
        "freeze_file":"GOLD_MONTHLY_BOOSTING_STAGE6C_B_TPE_GBRT_FREEZE_2026-09-27.md",
        "authority_source":{
            "doi":"10.28991/ESJ-2026-010-03-016",
            "adaptation":"origin-safe project adaptation; not exact reproduction",
        },
        "contract":{
            "dev":f"{DEV_START}..{DEV_END}",
            "dev_n":33,
            "model":"GradientBoostingRegressor",
            "representation":REP,
            "training_target":"Gold next-month log return",
            "loss":"absolute_error",
            "inner_validation_months":INNER_VAL_MONTHS,
            "tpe_trials_per_origin":TRIALS,
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"QUARANTINED_NOT_USED_IN_DEVELOPMENT",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR",
            "outer_target_actual_read_after_forecast_generation":True,
        },
        "sampler":{
            "type":"Optuna TPESampler",
            "n_startup_trials":10,
            "multivariate":False,
            "group":False,
            "constant_liar":False,
            "pruner":"NONE",
        },
        "search_space":{
            "max_depth":"integer 1..5",
            "n_estimators":"integer 50..500",
            "learning_rate":"log 0.01..0.20",
            "min_samples_leaf":"integer 1..10",
            "subsample":"continuous 0.60..1.00",
            "max_features":"continuous 0.60..1.00",
        },
        "software":{
            "python":platform.python_version(),
            "numpy":np.__version__,
            "scikit_learn":sklearn.__version__,
            "optuna":optuna.__version__,
        },
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "baseline":{
            "params":BASELINE_PARAMS,
            "metrics":base_met,
            "yearly":base_year,
        },
        "tpe":{
            "metrics":tpe_met,
            "yearly":tpe_year,
            "mean_inner_ratio_vs_baseline":float(np.mean(ratios)),
            "median_inner_ratio_vs_baseline":float(np.median(ratios)),
            "worst_inner_ratio_vs_baseline":float(np.max(ratios)),
            "months_inner_better_than_baseline":int(np.sum(ratios<1.0-1e-12)),
            "total_trials":int(sum(r["tpe_trials"] for r in rows)),
        },
        "cmaes_reference":{
            "sum_abs_error":CMAES_DEV_SUMAE_REF,
            "direction_correct":CMAES_DEV_DIRECTION_REF,
            "selection_use":"POST_RUN_CONTEXT_ONLY",
        },
        "rows":rows,
        "payload_sha256":digest,
    }

    Path("gold_monthly_boosting_stage6c_b_tpe_gbrt_result.json").write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "baseline":payload["baseline"],
        "tpe":payload["tpe"],
        "cmaes_reference":payload["cmaes_reference"],
        "payload_sha256":digest,
        "authority_invariants_unchanged":after==bundle.invariants_before,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    run()
