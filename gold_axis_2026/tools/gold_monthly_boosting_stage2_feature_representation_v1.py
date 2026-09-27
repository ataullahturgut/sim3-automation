from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage1_canonical_v1 as s1

DEV_START, DEV_END = "2022-04", "2024-12"\nCOMMON_TRAIN_START = "2010-05"
METALS = ("Gold","Silver","Platinum","Palladium")
REPS = ("CURRENT8","RAW_LEVEL_LAGS8","SIMPLE_RETURNS8","DAILY_SUMMARY12","MIXED20")
EXPECTED_DIMS = {"CURRENT8":8,"RAW_LEVEL_LAGS8":8,"SIMPLE_RETURNS8":8,"DAILY_SUMMARY12":12,"MIXED20":20}

STAGE1_REFERENCE = {
    "CATBOOST_ORDERED": 1460.433935309605,
    "RANDOM_FOREST_ANCHOR": 1614.490797968875,
    "XGBOOST": 1778.0649251965765,
    "GBRT": 1801.8647954502123,
    "LIGHTGBM": 1832.5777025157429,
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def daily_summary(bundle, metal, origin):
    v=np.asarray(bundle.daily_month_values[metal].get(origin,[]),float)
    if len(v)<5:
        raise RuntimeError(f"DAILY_ROWS_TOO_FEW metal={metal} origin={origin} n={len(v)}")
    if np.any(v<=0) or not np.isfinite(v).all():
        raise RuntimeError(f"BAD_DAILY_LEVEL metal={metal} origin={origin}")
    lr=np.diff(np.log(v))
    oc=float(math.log(v[-1]/v[0]))
    rv=float(math.sqrt(float(np.sum(lr*lr))))
    rng=float(math.log(float(np.max(v))/float(np.min(v))))
    return oc,rv,rng

def rep_feature(bundle, samples, target, rep):
    p=base.month_shift(target,-1)
    pp=base.month_shift(target,-2)
    p3=base.month_shift(target,-4)

    if rep=="CURRENT8":
        x=np.asarray(samples[target][0],float)

    elif rep=="RAW_LEVEL_LAGS8":
        z=[]
        for m in METALS:
            M=bundle.monthly_metal[m]
            if p not in M or pp not in M: raise RuntimeError(f"MONTHLY_LEVEL_MISSING {m} {target}")
            z.extend((float(M[p]),float(M[pp])))
        x=np.asarray(z,float)

    elif rep=="SIMPLE_RETURNS8":
        z=[]
        for m in METALS:
            M=bundle.monthly_metal[m]
            for k in (p,pp,p3):
                if k not in M: raise RuntimeError(f"MONTHLY_RETURN_LEVEL_MISSING {m} {target} {k}")
            r1=float(math.log(M[p]/M[pp]))
            r3=float(math.log(M[p]/M[p3]))
            z.extend((r1,r3))
        x=np.asarray(z,float)

    elif rep=="DAILY_SUMMARY12":
        z=[]
        for m in METALS:
            z.extend(daily_summary(bundle,m,p))
        x=np.asarray(z,float)

    elif rep=="MIXED20":
        current=np.asarray(samples[target][0],float)
        levels=[]; mom3=[]; rv=[]
        for m in METALS:
            M=bundle.monthly_metal[m]
            if p not in M or p3 not in M: raise RuntimeError(f"MIXED_MONTHLY_MISSING {m} {target}")
            levels.append(float(M[p]))
            mom3.append(float(math.log(M[p]/M[p3])))
            rv.append(float(daily_summary(bundle,m,p)[1]))
        x=np.r_[current,np.asarray(levels),np.asarray(mom3),np.asarray(rv)].astype(float)

    else:
        raise KeyError(rep)

    if x.shape != (EXPECTED_DIMS[rep],):
        raise RuntimeError(f"REP_DIM_FAIL rep={rep} target={target} shape={x.shape}")
    if not np.isfinite(x).all():
        raise RuntimeError(f"REP_NONFINITE rep={rep} target={target}")
    return x

def arrays(bundle,samples,target,rep):
    keys=sorted(k for k in samples if COMMON_TRAIN_START <= k < target)
    if len(keys)<30: raise RuntimeError(f"TRAIN_TOO_SMALL target={target} n={len(keys)}")
    X=np.stack([rep_feature(bundle,samples,k,rep) for k in keys])
    y=np.asarray([float(samples[k][1][0]) for k in keys],float)
    tx=rep_feature(bundle,samples,target,rep).reshape(1,-1)
    if X.shape[1]!=EXPECTED_DIMS[rep] or tx.shape[1]!=EXPECTED_DIMS[rep]:
        raise RuntimeError(f"ARRAY_DIM_FAIL rep={rep} target={target}")
    return keys,X,y,tx

def predict_one(bundle,samples,target,name,rep):
    keys,X,y,tx=arrays(bundle,samples,target,rep)
    model=s1.make_model(name)
    model.fit(X,y)
    pred=float(np.asarray(model.predict(tx)).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED name={name} rep={rep} target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    previous=float(bundle.core_gold[origin]); actual=float(bundle.core_gold[target])
    forecast=float(previous*math.exp(pred))
    pd=int(np.sign(forecast-previous)); ad=int(np.sign(actual-previous))
    return {
        "target":target,"origin":origin,"model":name,"representation":rep,
        "feature_dim":EXPECTED_DIMS[rep],"train_rows":len(keys),
        "train_first":keys[0],"train_last":keys[-1],
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":previous,
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
        "direction_correct":int(d.sum()),"direction_accuracy_pct":float(d.mean()*100)
    }

def yearly(rows):
    out={}
    for y in ("2022","2023","2024"):
        rr=[r for r in rows if r["target"].startswith(y)]
        out[y]=metrics(rr)
    return out

def evaluate(bundle,cache,name,rep):
    rows=[predict_one(bundle,cache[t],t,name,rep) for t in base.month_range(DEV_START,DEV_END)]
    return {"params":s1.PARAMS[name],"representation":rep,"feature_dim":EXPECTED_DIMS[rep],
            "metrics":metrics(rows),"yearly":yearly(rows),"rows":rows}

def run_all(bundle,cache):
    out={}
    for name in s1.PARAMS:
        out[name]={}
        for rep in REPS:
            out[name][rep]=evaluate(bundle,cache,name,rep)
    return out

def stable_hash(results):
    compact={}
    for name in sorted(results):
        for rep in REPS:
            compact[f"{name}::{rep}"]=[
                {k:r[k] for k in ("target","pred_log_return_gold","forecast","actual","rw","direction_correct")}
                for r in results[name][rep]["rows"]
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

    # Separate reconciliation: re-run the exact Stage-1 CURRENT8 history to prove the code/data base is unchanged.
    reproduction={}
    for name,ref in STAGE1_REFERENCE.items():
        exact=s1.evaluate(b,cache,name)
        cur=float(exact["metrics"]["sum_abs_error"])
        diff=abs(cur-ref)
        reproduction[name]={"stage1_reference":ref,"stage1_exact_replay":cur,"abs_diff":diff}
        if diff>1e-8:
            raise RuntimeError(f"STAGE1_REPRO_FAIL {name} ref={ref} cur={cur} diff={diff}")

    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    comparison=[]
    promoted={}
    for name in s1.PARAMS:
        rows=[]
        for rep in REPS:
            m=first[name][rep]["metrics"]
            rows.append({"model":name,"representation":rep,"feature_dim":EXPECTED_DIMS[rep],**m})
            comparison.append(rows[-1])
        rows.sort(key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["representation"]))
        promoted[name]=rows[0]

    overall=sorted(comparison,key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["model"],z["representation"]))

    out={
        "family":"BOOSTING_STAGE2_FEATURE_REPRESENTATION_ABLATION_V1",
        "scope":"STAGE_2_ONLY_DEV_ONLY",
        "stage0_plan":"GOLD_MONTHLY_BOOSTING_AUTHORITY_AND_STAGE_PLAN_2026-09-27.md",
        "contract":{
            "target":"H=1 next-calendar-month average XAU/USD",
            "training_target":"Gold next-month log return only",
            "models":"same Stage-1 canonical estimators and hyperparameters",
            "representations":{
                "CURRENT8":"existing 8 VW-MIDAS predictors",
                "RAW_LEVEL_LAGS8":"p and p-1 monthly mean raw levels for 4 metals",
                "SIMPLE_RETURNS8":"1M log return and 3M log momentum for 4 metals",
                "DAILY_SUMMARY12":"origin-month open-close log return, realized volatility, log high-low range for 4 metals",
                "MIXED20":"CURRENT8 + origin raw level + 3M momentum + realized volatility for 4 metals"
            },
            "dev":f"{DEV_START}..{DEV_END}","random_split":"NONE",
            "hyperparameter_tuning":"NONE","target_loss_change":"NONE",
            "2025_role":"NOT_OPENED_NOT_EVALUATED","2026_role":"NOT_OPENED_NOT_EVALUATED",
            "database":"READ_ONLY","primary_metric":"DEV_PRICE_SUM_ABS_ERROR"
        },
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
        "stage1_exact_reconciliation":reproduction,
        "results":first,
        "comparison":comparison,
        "promoted_representation_by_model":promoted,
        "overall_ranking":overall,
        "legacy_results_used":False,\n        "common_training_history_start":COMMON_TRAIN_START
    }
    Path("gold_monthly_boosting_stage2_feature_representation_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "promoted":promoted,
        "top10":overall[:10],
        "stage1_reconciliation":reproduction,
        "determinism":out["determinism"],
        "authority_invariants_unchanged":after==b.invariants_before
    },sort_keys=True))

if __name__=="__main__":
    main()
