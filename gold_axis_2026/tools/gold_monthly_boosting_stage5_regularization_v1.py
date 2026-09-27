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
    {
        "lane":"CATBOOST_PRICE","model":"CATBOOST_ORDERED","rep":"CURRENT8","start":"2010-03",
        "capacity":{"depth":6,"iterations":100,"learning_rate":0.03},
        "profiles":[
            ("CB_R0_BASELINE",{}),
            ("CB_R1_L2_10",{"l2_leaf_reg":10.0}),
            ("CB_R2_RANDOM2",{"random_strength":2.0}),
            ("CB_R3_BERNOULLI80",{"bootstrap_type":"Bernoulli","subsample":0.80}),
            ("CB_R4_COMBO",{"l2_leaf_reg":10.0,"random_strength":2.0,"bootstrap_type":"Bernoulli","subsample":0.80}),
        ],
    },
    {
        "lane":"CATBOOST_BALANCED","model":"CATBOOST_ORDERED","rep":"CURRENT8","start":"2010-03",
        "capacity":{"depth":8,"iterations":300,"learning_rate":0.02},
        "profiles":[
            ("CB_R0_BASELINE",{}),
            ("CB_R1_L2_10",{"l2_leaf_reg":10.0}),
            ("CB_R2_RANDOM2",{"random_strength":2.0}),
            ("CB_R3_BERNOULLI80",{"bootstrap_type":"Bernoulli","subsample":0.80}),
            ("CB_R4_COMBO",{"l2_leaf_reg":10.0,"random_strength":2.0,"bootstrap_type":"Bernoulli","subsample":0.80}),
        ],
    },
    {
        "lane":"GBRT_PRICE_BALANCED","model":"GBRT","rep":"DAILY_SUMMARY12","start":"2010-03",
        "capacity":{"max_depth":2,"n_estimators":100,"learning_rate":0.10,"min_samples_leaf":2},
        "profiles":[
            ("G_R0_BASELINE",{}),
            ("G_R1_ROW90",{"subsample":0.90}),
            ("G_R2_ROW80",{"subsample":0.80}),
            ("G_R3_FEATURE80",{"max_features":0.80}),
            ("G_R4_COMBO80",{"subsample":0.80,"max_features":0.80}),
        ],
    },
    {
        "lane":"XGBOOST_PRICE","model":"XGBOOST","rep":"RAW_LEVEL_LAGS8","start":"2010-03",
        "capacity":{"max_depth":2,"n_estimators":300,"learning_rate":0.03,"min_child_weight":3},
        "profiles":[
            ("X_R0_BASELINE",{}),
            ("X_R1_L2_5",{"reg_lambda":5.0}),
            ("X_R2_L1_001",{"reg_alpha":0.01}),
            ("X_R3_SAMPLE80",{"subsample":0.80,"colsample_bytree":0.80}),
            ("X_R4_COMBO",{"reg_alpha":0.01,"reg_lambda":5.0,"gamma":0.001,"subsample":0.80,"colsample_bytree":0.80}),
        ],
    },
    {
        "lane":"XGBOOST_DIRECTION","model":"XGBOOST","rep":"CURRENT8","start":"2010-03",
        "capacity":{"max_depth":4,"n_estimators":200,"learning_rate":0.05,"min_child_weight":1},
        "profiles":[
            ("X_R0_BASELINE",{}),
            ("X_R1_L2_5",{"reg_lambda":5.0}),
            ("X_R2_L1_001",{"reg_alpha":0.01}),
            ("X_R3_SAMPLE80",{"subsample":0.80,"colsample_bytree":0.80}),
            ("X_R4_COMBO",{"reg_alpha":0.01,"reg_lambda":5.0,"gamma":0.001,"subsample":0.80,"colsample_bytree":0.80}),
        ],
    },
    {
        "lane":"LIGHTGBM_PRICE_BALANCED","model":"LIGHTGBM","rep":"MIXED20","start":"2010-05",
        "capacity":{"num_leaves":31,"max_depth":6,"min_child_samples":10,"n_estimators":300,"learning_rate":0.03},
        "profiles":[
            ("L_R0_BASELINE",{}),
            ("L_R1_L2_1",{"reg_lambda":1.0}),
            ("L_R2_L1_01",{"reg_alpha":0.1}),
            ("L_R3_BAG80",{"subsample":0.80,"subsample_freq":1}),
            ("L_R4_FEATURE80",{"colsample_bytree":0.80}),
            ("L_R5_COMBO",{"reg_alpha":0.1,"reg_lambda":1.0,"subsample":0.80,"subsample_freq":1,"colsample_bytree":0.80}),
        ],
    },
    {
        "lane":"RF_COMPARATOR","model":"RANDOM_FOREST_ANCHOR","rep":"DAILY_SUMMARY12","start":"2010-03",
        "capacity":{"max_depth":None,"min_samples_leaf":1,"n_estimators":500},
        "profiles":[("R_R0_BASELINE",{})],
    },
]

BASELINE_REFS = {
    "CATBOOST_PRICE":1460.433935309605,
    "CATBOOST_BALANCED":1481.261937710369,
    "GBRT_PRICE_BALANCED":1500.42946858865,
    "XGBOOST_PRICE":1673.0823484831108,
    "XGBOOST_DIRECTION":1724.9639029353484,
    "LIGHTGBM_PRICE_BALANCED":1534.6087211346264,
    "RF_COMPARATOR":1491.5506937156672,
}
BASELINE_PROFILE = {
    "CATBOOST_PRICE":"CB_R0_BASELINE",
    "CATBOOST_BALANCED":"CB_R0_BASELINE",
    "GBRT_PRICE_BALANCED":"G_R0_BASELINE",
    "XGBOOST_PRICE":"X_R0_BASELINE",
    "XGBOOST_DIRECTION":"X_R0_BASELINE",
    "LIGHTGBM_PRICE_BALANCED":"L_R0_BASELINE",
    "RF_COMPARATOR":"R_R0_BASELINE",
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def make_model(lane, reg):
    model=lane["model"]
    p=dict(s1.PARAMS[model])
    p.update(lane["capacity"])
    p.update(reg)

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

def predict_one(bundle,samples,target,lane,profile,reg):
    keys,X,y,tx=arrays(bundle,samples,target,lane)
    model=make_model(lane,reg)
    model.fit(X,y)
    pred=float(np.asarray(model.predict(tx)).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED lane={lane['lane']} profile={profile} target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin]); actual=float(bundle.core_gold[target])
    forecast=float(prev*math.exp(pred))
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"lane":lane["lane"],"model":lane["model"],
        "representation":lane["rep"],"train_start":lane["start"],"train_rows":len(keys),
        "capacity":lane["capacity"],"profile":profile,"regularization":reg,
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
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

def evaluate(bundle,cache,lane,profile,reg):
    rows=[predict_one(bundle,cache[t],t,lane,profile,reg)
          for t in base.month_range(DEV_START,DEV_END)]
    return {
        "lane":lane["lane"],"model":lane["model"],"representation":lane["rep"],
        "train_start":lane["start"],"capacity":lane["capacity"],
        "profile":profile,"regularization":reg,
        "metrics":metrics(rows),"yearly":yearly(rows),"rows":rows
    }

def run_all(bundle,cache):
    out={}
    for lane in LANES:
        out[lane["lane"]]={}
        for profile,reg in lane["profiles"]:
            out[lane["lane"]][profile]=evaluate(bundle,cache,lane,profile,reg)
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
        ls=lane["lane"]; prof=BASELINE_PROFILE[ls]
        cur=float(first[ls][prof]["metrics"]["sum_abs_error"])
        ref=float(BASELINE_REFS[ls]); diff=abs(cur-ref)
        reconcile[f"{ls}::{prof}"]={"reference":ref,"stage5_replay":cur,"abs_diff":diff}
        if diff>1e-8:
            raise RuntimeError(f"BASELINE_REPRO_FAIL lane={ls} profile={prof} ref={ref} cur={cur}")

    comparison=[]; best_by_lane={}; best_direction_by_lane={}
    for lane in LANES:
        ls=lane["lane"]; rows=[]
        for profile,v in first[ls].items():
            z={"lane":ls,"model":v["model"],"representation":v["representation"],
               "profile":profile,"capacity":v["capacity"],"regularization":v["regularization"],**v["metrics"]}
            rows.append(z); comparison.append(z)
        by_price=sorted(rows,key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["profile"]))
        by_dir=sorted(rows,key=lambda z:(-z["direction_correct"],z["sum_abs_error"],z["rmse"],z["profile"]))
        best_by_lane[ls]=by_price[0]
        best_direction_by_lane[ls]=by_dir[0]

    overall=sorted(comparison,key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["lane"],z["profile"]))

    after=read_invariants(dsn)
    if after!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "scope":"BOOSTING_STAGE5_REGULARIZATION_SUBSAMPLING_V1",
        "dev":f"{DEV_START}..{DEV_END}",
        "contract":{
            "feature_target_loss_capacity":"FROZEN_FROM_STAGE4",
            "regularization_profiles":"PREOUTCOME_FROZEN",
            "optimizer":"NONE",
            "early_stopping":"NONE",
            "random_split":"NONE",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"NOT_OPENED_NOT_EVALUATED",
            "database":"READ_ONLY",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR"
        },
        "lanes":LANES,
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
        "stage4_baseline_reconciliation":reconcile,
        "results":first,
        "comparison":comparison,
        "best_by_lane":best_by_lane,
        "best_direction_by_lane":best_direction_by_lane,
        "overall_ranking":overall
    }
    Path("gold_monthly_boosting_stage5_regularization_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "best_by_lane":best_by_lane,
        "best_direction_by_lane":best_direction_by_lane,
        "top12":overall[:12],
        "baseline_reconciliation":reconcile,
        "determinism":out["determinism"],
        "authority_invariants_unchanged":after==b.invariants_before
    },sort_keys=True))

if __name__=="__main__":
    main()
