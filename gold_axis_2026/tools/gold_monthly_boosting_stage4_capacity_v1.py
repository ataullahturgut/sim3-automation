from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path
import numpy as np
import psycopg

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage1_canonical_v1 as s1
import gold_monthly_boosting_stage2_feature_representation_v1 as s2

DEV_START, DEV_END = "2022-04", "2024-12"

LANES = [
    {"lane":"CATBOOST_ORDERED__CURRENT8__RMSE","model":"CATBOOST_ORDERED","rep":"CURRENT8","start":"2010-03"},
    {"lane":"GBRT__DAILY_SUMMARY12__ABS","model":"GBRT","rep":"DAILY_SUMMARY12","start":"2010-03"},
    {"lane":"XGBOOST__RAW_LEVEL_LAGS8__L2","model":"XGBOOST","rep":"RAW_LEVEL_LAGS8","start":"2010-03"},
    {"lane":"XGBOOST__CURRENT8__L2_DIRECTION","model":"XGBOOST","rep":"CURRENT8","start":"2010-03"},
    {"lane":"LIGHTGBM__MIXED20__L1","model":"LIGHTGBM","rep":"MIXED20","start":"2010-05"},
    {"lane":"RF__DAILY_SUMMARY12","model":"RANDOM_FOREST_ANCHOR","rep":"DAILY_SUMMARY12","start":"2010-03"},
]

PROFILES = {
    "CATBOOST_ORDERED":[
        ("C0_SHALLOW_100",{"depth":4,"iterations":100,"learning_rate":0.03}),
        ("C1_SHALLOW_300",{"depth":4,"iterations":300,"learning_rate":0.03}),
        ("C2_BASELINE",{"depth":6,"iterations":100,"learning_rate":0.03}),
        ("C3_MEDIUM_300",{"depth":6,"iterations":300,"learning_rate":0.03}),
        ("C4_DEEP_LOWLR",{"depth":8,"iterations":300,"learning_rate":0.02}),
    ],
    "GBRT":[
        ("G0_SHALLOW",{"max_depth":2,"n_estimators":100,"learning_rate":0.10,"min_samples_leaf":2}),
        ("G1_SHALLOW_SLOW",{"max_depth":2,"n_estimators":300,"learning_rate":0.03,"min_samples_leaf":2}),
        ("G2_BASELINE",{"max_depth":3,"n_estimators":100,"learning_rate":0.10,"min_samples_leaf":1}),
        ("G3_MEDIUM_SLOW",{"max_depth":3,"n_estimators":300,"learning_rate":0.03,"min_samples_leaf":2}),
        ("G4_HIGHER_CAPACITY",{"max_depth":4,"n_estimators":300,"learning_rate":0.03,"min_samples_leaf":2}),
    ],
    "XGBOOST":[
        ("X0_SHALLOW_CONSERVATIVE",{"max_depth":2,"n_estimators":300,"learning_rate":0.03,"min_child_weight":3}),
        ("X1_SHALLOW_MEDIUM",{"max_depth":3,"n_estimators":300,"learning_rate":0.05,"min_child_weight":2}),
        ("X2_MEDIUM",{"max_depth":4,"n_estimators":200,"learning_rate":0.05,"min_child_weight":1}),
        ("X3_BASELINE",{"max_depth":6,"n_estimators":100,"learning_rate":0.30,"min_child_weight":1}),
        ("X4_DEEP_SLOW",{"max_depth":6,"n_estimators":300,"learning_rate":0.03,"min_child_weight":2}),
    ],
    "LIGHTGBM":[
        ("L0_SMALL",{"num_leaves":7,"max_depth":3,"min_child_samples":15,"n_estimators":300,"learning_rate":0.03}),
        ("L1_SHALLOW",{"num_leaves":15,"max_depth":4,"min_child_samples":15,"n_estimators":300,"learning_rate":0.03}),
        ("L2_MEDIUM",{"num_leaves":15,"max_depth":5,"min_child_samples":10,"n_estimators":200,"learning_rate":0.05}),
        ("L3_BASELINE",{"num_leaves":31,"max_depth":-1,"min_child_samples":20,"n_estimators":100,"learning_rate":0.10}),
        ("L4_HIGHER_CAPACITY",{"num_leaves":31,"max_depth":6,"min_child_samples":10,"n_estimators":300,"learning_rate":0.03}),
    ],
    "RANDOM_FOREST_ANCHOR":[
        ("R0_BASELINE",{"max_depth":None,"min_samples_leaf":1,"n_estimators":500}),
        ("R1_SHALLOW",{"max_depth":4,"min_samples_leaf":3,"n_estimators":500}),
        ("R2_MEDIUM",{"max_depth":6,"min_samples_leaf":2,"n_estimators":500}),
    ],
}

BASELINE_REFS = {
    "CATBOOST_ORDERED__CURRENT8__RMSE":1460.433935309605,
    "GBRT__DAILY_SUMMARY12__ABS":1568.1002319206916,
    "XGBOOST__RAW_LEVEL_LAGS8__L2":1695.55569760265,
    "XGBOOST__CURRENT8__L2_DIRECTION":1778.0649251965765,
    "LIGHTGBM__MIXED20__L1":1635.4055892431354,
    "RF__DAILY_SUMMARY12":1491.5506937156672,
}

BASELINE_PROFILE = {
    "CATBOOST_ORDERED":"C2_BASELINE",
    "GBRT":"G2_BASELINE",
    "XGBOOST":"X3_BASELINE",
    "LIGHTGBM":"L3_BASELINE",
    "RANDOM_FOREST_ANCHOR":"R0_BASELINE",
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def make_model(model, overrides):
    p=dict(s1.PARAMS[model])
    p.update(overrides)
    if model=="CATBOOST_ORDERED":
        p["loss_function"]="RMSE"
        return CatBoostRegressor(**p)
    if model=="GBRT":
        p["loss"]="absolute_error"
        return GradientBoostingRegressor(**p)
    if model=="XGBOOST":
        p["objective"]="reg:squarederror"
        return XGBRegressor(**p)
    if model=="LIGHTGBM":
        p["objective"]="regression_l1"
        return LGBMRegressor(**p)
    if model=="RANDOM_FOREST_ANCHOR":
        return RandomForestRegressor(**p)
    raise KeyError(model)

def arrays(bundle,samples,target,lane):
    keys=sorted(k for k in samples if lane["start"] <= k < target)
    if len(keys)<30:
        raise RuntimeError(f"TRAIN_TOO_SMALL lane={lane['lane']} target={target} n={len(keys)}")
    X=np.stack([s2.rep_feature(bundle,samples,k,lane["rep"]) for k in keys])
    y=np.asarray([float(samples[k][1][0]) for k in keys],float)
    tx=s2.rep_feature(bundle,samples,target,lane["rep"]).reshape(1,-1)
    if not (np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(tx).all()):
        raise RuntimeError(f"NONFINITE lane={lane['lane']} target={target}")
    return keys,X,y,tx

def predict_one(bundle,samples,target,lane,profile_name,overrides):
    keys,X,y,tx=arrays(bundle,samples,target,lane)
    model=make_model(lane["model"],overrides)
    model.fit(X,y)
    pred=float(np.asarray(model.predict(tx)).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED lane={lane['lane']} profile={profile_name} target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin]); actual=float(bundle.core_gold[target])
    forecast=float(prev*math.exp(pred))
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"lane":lane["lane"],"model":lane["model"],
        "representation":lane["rep"],"train_start":lane["start"],"train_rows":len(keys),
        "profile":profile_name,"overrides":overrides,"pred_log_return_gold":pred,
        "forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r["forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a); rw_ae=np.abs(rw-a)
    d=np.asarray([r["direction_correct"] for r in rows],bool)
    return {
        "n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
        "median_ae":float(np.median(ae)),"worst_ae":float(np.max(ae)),
        "relative_mae_vs_rw":float(ae.sum()/rw_ae.sum()),
        "direction_correct":int(d.sum()),"direction_accuracy_pct":float(d.mean()*100.0)
    }

def yearly(rows):
    out={}
    for y in ("2022","2023","2024"):
        rr=[r for r in rows if r["target"].startswith(y)]
        out[y]=metrics(rr)
    return out

def evaluate(bundle,cache,lane,profile_name,overrides):
    rows=[predict_one(bundle,cache[t],t,lane,profile_name,overrides)
          for t in base.month_range(DEV_START,DEV_END)]
    return {
        "lane":lane["lane"],"model":lane["model"],"representation":lane["rep"],
        "train_start":lane["start"],"profile":profile_name,"overrides":overrides,
        "metrics":metrics(rows),"yearly":yearly(rows),"rows":rows
    }

def run_all(bundle,cache):
    out={}
    for lane in LANES:
        out[lane["lane"]]={}
        for profile_name,overrides in PROFILES[lane["model"]]:
            out[lane["lane"]][profile_name]=evaluate(bundle,cache,lane,profile_name,overrides)
    return out

def stable_hash(results):
    compact={}
    for lane in sorted(results):
        for profile in sorted(results[lane]):
            compact[f"{lane}::{profile}"]=[
                {k:r[k] for k in ("target","forecast","actual","rw","direction_correct","pred_log_return_gold")}
                for r in results[lane][profile]["rows"]
            ]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in targets}

    first=run_all(b,cache)
    h1=stable_hash(first)
    second=run_all(b,cache)
    h2=stable_hash(second)
    if h1!=h2:
        raise RuntimeError(f"DETERMINISM_FAIL {h1} {h2}")

    reconcile={}
    for lane in LANES:
        ls=lane["lane"]; model=lane["model"]; prof=BASELINE_PROFILE[model]
        cur=float(first[ls][prof]["metrics"]["sum_abs_error"])
        ref=float(BASELINE_REFS[ls]); diff=abs(cur-ref)
        reconcile[f"{ls}::{prof}"]={"reference":ref,"stage4_replay":cur,"abs_diff":diff}
        if diff>1e-8:
            raise RuntimeError(f"BASELINE_REPRO_FAIL lane={ls} profile={prof} ref={ref} cur={cur}")

    comparison=[]; best_by_lane={}
    for lane in LANES:
        ls=lane["lane"]; rows=[]
        for profile,v in first[ls].items():
            z={"lane":ls,"model":v["model"],"representation":v["representation"],
               "profile":profile,"overrides":v["overrides"],**v["metrics"]}
            rows.append(z); comparison.append(z)
        rows.sort(key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["profile"]))
        best_by_lane[ls]=rows[0]

    overall=sorted(comparison,key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["lane"],z["profile"]))

    after=read_invariants(dsn)
    if after!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "scope":"BOOSTING_STAGE4_CAPACITY_SCAN_V1",
        "dev":f"{DEV_START}..{DEV_END}",
        "contract":{
            "feature_target_loss":"FROZEN_FROM_STAGE3",
            "regularization_subsampling_search":"NONE",
            "capacity_profiles":"PREOUTCOME_FROZEN",
            "random_split":"NONE",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"NOT_OPENED_NOT_EVALUATED",
            "database":"READ_ONLY",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR"
        },
        "profiles":PROFILES,
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
        "stage3_baseline_reconciliation":reconcile,
        "results":first,
        "comparison":comparison,
        "best_by_lane":best_by_lane,
        "overall_ranking":overall
    }
    Path("gold_monthly_boosting_stage4_capacity_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "best_by_lane":best_by_lane,
        "top12":overall[:12],
        "baseline_reconciliation":reconcile,
        "determinism":out["determinism"],
        "authority_invariants_unchanged":after==b.invariants_before
    },sort_keys=True))

if __name__=="__main__":
    main()
