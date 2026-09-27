from __future__ import annotations
import hashlib, json, math, os, platform
from pathlib import Path
import numpy as np
import psycopg
import sklearn
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import xgboost
from xgboost import XGBRegressor
import lightgbm
from lightgbm import LGBMRegressor
import catboost
from catboost import CatBoostRegressor

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
SEED = 1701
FEATURES = ("GOLD_MR","GOLD_VW","SILVER_MR","SILVER_VW",
            "PLATINUM_MR","PLATINUM_VW","PALLADIUM_MR","PALLADIUM_VW")

PARAMS = {
    "GBRT": {
        "loss":"squared_error","n_estimators":100,"learning_rate":0.10,
        "max_depth":3,"min_samples_leaf":1,"subsample":1.0,"random_state":SEED
    },
    "XGBOOST": {
        "objective":"reg:squarederror","n_estimators":100,"learning_rate":0.30,
        "max_depth":6,"min_child_weight":1.0,"gamma":0.0,"subsample":1.0,
        "colsample_bytree":1.0,"reg_alpha":0.0,"reg_lambda":1.0,
        "tree_method":"hist","random_state":SEED,"n_jobs":1,"verbosity":0
    },
    "CATBOOST_ORDERED": {
        "loss_function":"RMSE","iterations":100,"depth":6,"learning_rate":0.03,
        "l2_leaf_reg":3.0,"boosting_type":"Ordered","random_seed":SEED,
        "allow_writing_files":False,"verbose":False,"thread_count":1
    },
    "LIGHTGBM": {
        "objective":"regression","n_estimators":100,"learning_rate":0.10,
        "num_leaves":31,"max_depth":-1,"min_child_samples":20,
        "subsample":1.0,"colsample_bytree":1.0,"reg_alpha":0.0,"reg_lambda":0.0,
        "random_state":SEED,"n_jobs":1,"verbosity":-1,
        "deterministic":True,"force_col_wise":True
    },
    "RANDOM_FOREST_ANCHOR": {
        "n_estimators":500,"max_features":1.0,"bootstrap":True,
        "random_state":SEED,"n_jobs":1
    }
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def arrays(samples,target):
    keys=sorted(k for k in samples if k<target)
    if len(keys)<30:
        raise RuntimeError(f"TRAIN_TOO_SMALL target={target} n={len(keys)}")
    X=np.stack([np.asarray(samples[k][0],float) for k in keys])
    # Gold only: preserve the project's frozen monthly Gold log-return target.
    y=np.asarray([float(samples[k][1][0]) for k in keys],float)
    tx=np.asarray(samples[target][0],float).reshape(1,-1)
    if X.shape[1] != 8 or tx.shape[1] != 8:
        raise RuntimeError(f"FEATURE_COUNT_FAIL target={target} train={X.shape} test={tx.shape}")
    if not (np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(tx).all()):
        raise RuntimeError(f"NONFINITE_INPUT target={target}")
    return keys,X,y,tx

def make_model(name):
    p=dict(PARAMS[name])
    if name=="GBRT":
        return GradientBoostingRegressor(**p)
    if name=="XGBOOST":
        return XGBRegressor(**p)
    if name=="CATBOOST_ORDERED":
        return CatBoostRegressor(**p)
    if name=="LIGHTGBM":
        return LGBMRegressor(**p)
    if name=="RANDOM_FOREST_ANCHOR":
        return RandomForestRegressor(**p)
    raise KeyError(name)

def predict_one(bundle,samples,target,name):
    keys,X,y,tx=arrays(samples,target)
    model=make_model(name)
    model.fit(X,y)
    pred=float(np.asarray(model.predict(tx)).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED name={name} target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    previous=float(bundle.core_gold[origin])
    actual=float(bundle.core_gold[target])
    forecast=float(previous*math.exp(pred))
    actual_dir=int(np.sign(actual-previous))
    pred_dir=int(np.sign(forecast-previous))
    return {
        "target":target,"origin":origin,"model":name,
        "train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
        "pred_log_return_gold":pred,"forecast":forecast,
        "actual":actual,"rw":previous,
        "pred_direction":pred_dir,"actual_direction":actual_dir,
        "direction_correct":bool(pred_dir==actual_dir)
    }

def evaluate(bundle,cache,name):
    rows=[predict_one(bundle,cache[t],t,name) for t in base.month_range(DEV_START,DEV_END)]
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r["forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a); rw_ae=np.abs(rw-a)
    d=np.asarray([r["direction_correct"] for r in rows],bool)
    out={
        "n":len(rows),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
        "median_ae":float(np.median(ae)),
        "worst_ae":float(np.max(ae)),
        "relative_mae_vs_rw":float(ae.sum()/rw_ae.sum()),
        "direction_correct":int(d.sum()),
        "direction_accuracy_pct":float(d.mean()*100.0),
    }
    yearly={}
    for y in ("2022","2023","2024"):
        yr=[r for r in rows if r["target"].startswith(y)]
        aa=np.asarray([r["actual"] for r in yr],float); ff=np.asarray([r["forecast"] for r in yr],float)
        dd=np.asarray([r["direction_correct"] for r in yr],bool)
        yearly[y]={
            "n":len(yr),"sum_abs_error":float(np.abs(ff-aa).sum()),
            "mae":float(np.abs(ff-aa).mean()),"direction_correct":int(dd.sum()),
            "direction_accuracy_pct":float(dd.mean()*100.0)
        }
    return {"params":PARAMS[name],"metrics":out,"yearly":yearly,"rows":rows}

def payload_hash(models):
    compact={}
    for name,v in models.items():
        compact[name]=[
            {k:r[k] for k in ("target","origin","train_rows","pred_log_return_gold","forecast","actual","rw","direction_correct")}
            for r in v["rows"]
        ]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def run_models(bundle,cache):
    return {name:evaluate(bundle,cache,name) for name in PARAMS}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle=base.load_data(dsn)

    # DEV ONLY. No 2025/2026 target cache is constructed in this Stage.
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in targets}

    first=run_models(bundle,cache)
    h1=payload_hash(first)

    # Deterministic replay with fresh model instances.
    second=run_models(bundle,cache)
    h2=payload_hash(second)
    if h1 != h2:
        raise RuntimeError(f"DETERMINISM_FAIL first={h1} second={h2}")

    after=read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    for name,v in first.items():
        if v["metrics"]["n"] != 33 or len(v["rows"]) != 33:
            raise RuntimeError(f"DEV_COUNT_FAIL {name}")
        if any(not ("2022-04" <= r["target"] <= "2024-12") for r in v["rows"]):
            raise RuntimeError(f"NON_DEV_ROW_FAIL {name}")

    ranking=sorted(
        [{"model":name,**v["metrics"]} for name,v in first.items()],
        key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["model"])
    )

    out={
        "family":"BOOSTING_STAGE1_CANONICAL_BASELINES_V1",
        "scope":"STAGE_1_ONLY_DEV_ONLY",
        "stage0_freeze":"GOLD_MONTHLY_BOOSTING_STAGE0_FREEZE_2026-09-27.json",
        "contract":{
            "target":"H=1 next-calendar-month average XAU/USD",
            "training_target":"Gold next-month log return only",
            "forecast_reconstruction":"origin previous monthly Gold price * exp(predicted Gold log return)",
            "features":list(FEATURES),
            "feature_count":8,
            "feature_scaling":"NONE_RAW_TREE_INPUTS",
            "dev_selection":f"{DEV_START}..{DEV_END}",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"NOT_OPENED_NOT_EVALUATED",
            "database":"READ_ONLY",
            "random_split":"NONE",
            "hyperparameter_selection":"NONE_STAGE1_FIXED_CANONICAL",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR",
            "gold_only":True,
            "multioutput":False
        },
        "software":{
            "python":platform.python_version(),
            "numpy":np.__version__,
            "scikit_learn":sklearn.__version__,
            "xgboost":xgboost.__version__,
            "lightgbm":lightgbm.__version__,
            "catboost":catboost.__version__
        },
        "source_checks":bundle.source_checks,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
        "models":first,
        "dev_ranking":ranking,
        "legacy_results_used_for_training_or_selection":False
    }

    Path("gold_monthly_boosting_stage1_canonical_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "scope":out["scope"],
        "ranking":ranking,
        "software":out["software"],
        "source_checks":out["source_checks"],
        "authority_invariants_unchanged":after==bundle.invariants_before,
        "determinism":out["determinism"]
    },sort_keys=True))

if __name__=="__main__":
    main()
