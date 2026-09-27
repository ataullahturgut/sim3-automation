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
    {"lane":"CATBOOST_ORDERED__CURRENT8","model":"CATBOOST_ORDERED","rep":"CURRENT8","start":"2010-03",
     "losses":["RMSE","MAE"]},
    {"lane":"XGBOOST__RAW_LEVEL_LAGS8","model":"XGBOOST","rep":"RAW_LEVEL_LAGS8","start":"2010-03",
     "losses":["reg:squarederror","reg:absoluteerror"]},
    {"lane":"XGBOOST__CURRENT8_DIRECTION","model":"XGBOOST","rep":"CURRENT8","start":"2010-03",
     "losses":["reg:squarederror","reg:absoluteerror"]},
    {"lane":"GBRT__DAILY_SUMMARY12","model":"GBRT","rep":"DAILY_SUMMARY12","start":"2010-03",
     "losses":["squared_error","absolute_error","huber"]},
    {"lane":"LIGHTGBM__RAW_LEVEL_LAGS8","model":"LIGHTGBM","rep":"RAW_LEVEL_LAGS8","start":"2010-03",
     "losses":["regression","regression_l1","huber"]},
    {"lane":"LIGHTGBM__MIXED20_BALANCED","model":"LIGHTGBM","rep":"MIXED20","start":"2010-05",
     "losses":["regression","regression_l1","huber"]},
    {"lane":"RANDOM_FOREST_ANCHOR__DAILY_SUMMARY12","model":"RANDOM_FOREST_ANCHOR","rep":"DAILY_SUMMARY12","start":"2010-03",
     "losses":["native"]}
]
TARGETS=("LOGRET","DIRECT_PRICE")

BASELINE_REFS = {
    ("CATBOOST_ORDERED__CURRENT8","LOGRET","RMSE"):1460.433935309605,
    ("XGBOOST__RAW_LEVEL_LAGS8","LOGRET","reg:squarederror"):1695.55569760265,
    ("XGBOOST__CURRENT8_DIRECTION","LOGRET","reg:squarederror"):1778.0649251965765,
    ("GBRT__DAILY_SUMMARY12","LOGRET","squared_error"):1594.083510057147,
    ("LIGHTGBM__RAW_LEVEL_LAGS8","LOGRET","regression"):1719.8522417746606,
    ("LIGHTGBM__MIXED20_BALANCED","LOGRET","regression"):1720.4059274852286,
    ("RANDOM_FOREST_ANCHOR__DAILY_SUMMARY12","LOGRET","native"):1491.5506937156672
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def make_model(model, loss):
    p=dict(s1.PARAMS[model])
    if model=="GBRT":
        p["loss"]=loss
        if loss=="huber": p["alpha"]=0.9
        return GradientBoostingRegressor(**p)
    if model=="XGBOOST":
        p["objective"]=loss
        return XGBRegressor(**p)
    if model=="CATBOOST_ORDERED":
        p["loss_function"]=loss
        return CatBoostRegressor(**p)
    if model=="LIGHTGBM":
        p["objective"]=loss
        if loss=="huber": p["alpha"]=0.9
        return LGBMRegressor(**p)
    if model=="RANDOM_FOREST_ANCHOR":
        return RandomForestRegressor(**p)
    raise KeyError(model)

def arrays(bundle,samples,target,rep,start,target_mode):
    keys=sorted(k for k in samples if start <= k < target)
    if len(keys)<30: raise RuntimeError(f"TRAIN_TOO_SMALL {target} {rep} {start} n={len(keys)}")
    X=np.stack([s2.rep_feature(bundle,samples,k,rep) for k in keys])
    tx=s2.rep_feature(bundle,samples,target,rep).reshape(1,-1)
    if target_mode=="LOGRET":
        y=np.asarray([float(samples[k][1][0]) for k in keys],float)
    elif target_mode=="DIRECT_PRICE":
        y=np.asarray([float(bundle.core_gold[k]) for k in keys],float)
    else:
        raise KeyError(target_mode)
    if not (np.isfinite(X).all() and np.isfinite(tx).all() and np.isfinite(y).all()):
        raise RuntimeError(f"NONFINITE {target} {rep} {target_mode}")
    return keys,X,y,tx

def predict_one(bundle,samples,target,lane,target_mode,loss):
    keys,X,y,tx=arrays(bundle,samples,target,lane["rep"],lane["start"],target_mode)
    m=make_model(lane["model"],loss)
    m.fit(X,y)
    raw=float(np.asarray(m.predict(tx)).reshape(-1)[0])
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin]); actual=float(bundle.core_gold[target])
    if target_mode=="LOGRET":
        if not math.isfinite(raw) or abs(raw)>=1.0:
            raise RuntimeError(f"PATHOLOGICAL_LOGRET lane={lane['lane']} target={target} pred={raw}")
        forecast=float(prev*math.exp(raw))
        pred_logret=raw
    else:
        if not math.isfinite(raw) or raw<=0:
            raise RuntimeError(f"PATHOLOGICAL_PRICE lane={lane['lane']} target={target} pred={raw}")
        forecast=raw
        pred_logret=float(math.log(forecast/prev))
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"lane":lane["lane"],"model":lane["model"],
        "representation":lane["rep"],"train_start":lane["start"],"train_rows":len(keys),
        "target_mode":target_mode,"loss":loss,"raw_prediction":raw,
        "pred_log_return_gold":pred_logret,"forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }

def metric(rows):
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
        out[y]=metric(rr)
    return out

def evaluate(bundle,cache,lane,target_mode,loss):
    rows=[predict_one(bundle,cache[t],t,lane,target_mode,loss) for t in base.month_range(DEV_START,DEV_END)]
    return {"lane":lane["lane"],"model":lane["model"],"representation":lane["rep"],
            "train_start":lane["start"],"target_mode":target_mode,"loss":loss,
            "metrics":metric(rows),"yearly":yearly(rows),"rows":rows}

def run_all(bundle,cache):
    out={}
    for lane in LANES:
        out[lane["lane"]]={}
        for tm in TARGETS:
            for loss in lane["losses"]:
                key=f"{tm}__{loss}"
                out[lane["lane"]][key]=evaluate(bundle,cache,lane,tm,loss)
    return out

def stable_hash(results):
    compact={}
    for lane in sorted(results):
        for key in sorted(results[lane]):
            compact[f"{lane}::{key}"]=[
                {k:r[k] for k in ("target","forecast","actual","rw","direction_correct","raw_prediction")}
                for r in results[lane][key]["rows"]
            ]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in targets}

    first=run_all(b,cache)
    h1=stable_hash(first)
    second=run_all(b,cache)
    h2=stable_hash(second)
    if h1!=h2: raise RuntimeError(f"DETERMINISM_FAIL {h1} {h2}")

    reconcile={}
    for (lane,tm,loss),ref in BASELINE_REFS.items():
        key=f"{tm}__{loss}"
        cur=float(first[lane][key]["metrics"]["sum_abs_error"])
        diff=abs(cur-ref)
        reconcile[f"{lane}::{key}"]={"reference":ref,"stage3_replay":cur,"abs_diff":diff}
        if diff>1e-8:
            raise RuntimeError(f"BASELINE_REPRO_FAIL {lane} {key} ref={ref} cur={cur}")

    comparison=[]
    best_by_lane={}
    for lane in LANES:
        ls=lane["lane"]; rows=[]
        for key,v in first[ls].items():
            z={"lane":ls,"model":v["model"],"representation":v["representation"],
               "target_mode":v["target_mode"],"loss":v["loss"],**v["metrics"]}
            rows.append(z); comparison.append(z)
        rows.sort(key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["target_mode"],z["loss"]))
        best_by_lane[ls]=rows[0]

    overall=sorted(comparison,key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["lane"]))

    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "scope":"BOOSTING_STAGE3_TARGET_LOSS_ABLATION_V1",
        "dev":f"{DEV_START}..{DEV_END}",
        "contract":{
            "feature_lanes":"FROZEN_FROM_STAGE2",
            "capacity":"UNCHANGED_FROM_STAGE1",
            "regularization":"UNCHANGED_FROM_STAGE1",
            "hyperparameter_search":"NONE",
            "random_split":"NONE",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"NOT_OPENED_NOT_EVALUATED",
            "database":"READ_ONLY",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR"
        },
        "loss_authority":{
            "GBRT":["squared_error","absolute_error","huber alpha=0.9"],
            "XGBOOST":["reg:squarederror","reg:absoluteerror"],
            "CATBOOST_ORDERED":["RMSE","MAE"],
            "LIGHTGBM":["regression","regression_l1","huber alpha=0.9"],
            "RANDOM_FOREST_ANCHOR":["native"],
            "deferred":["XGBoost Pseudo-Huber: huber_slope scale-sensitive","CatBoost Huber: delta obligatory and scale-sensitive"]
        },
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
        "stage2_baseline_reconciliation":reconcile,
        "results":first,
        "comparison":comparison,
        "best_by_lane":best_by_lane,
        "overall_ranking":overall
    }
    Path("gold_monthly_boosting_stage3_target_loss_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "best_by_lane":best_by_lane,
        "top10":overall[:10],
        "baseline_reconciliation":reconcile,
        "determinism":out["determinism"],
        "authority_invariants_unchanged":after==b.invariants_before
    },sort_keys=True))

if __name__=="__main__":
    main()
