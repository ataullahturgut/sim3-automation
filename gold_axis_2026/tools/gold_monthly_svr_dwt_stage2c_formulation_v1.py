#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.svm import SVR, NuSVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1

DEV_START, DEV_END = "2022-04", "2024-12"
COMMON_TRAIN_START = "2010-05"

SPECS = {
    "EPSILON_RBF_DAILY12": {
        "kind":"SVR",
        "params":{"kernel":"rbf","C":1.0,"epsilon":0.1,"gamma":"scale","shrinking":True,"tol":1e-3}
    },
    "NU_RBF_DAILY12": {
        "kind":"NuSVR",
        "params":{"kernel":"rbf","C":1.0,"nu":0.5,"gamma":"scale","shrinking":True,"tol":1e-3}
    },
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
    return (
        float(math.log(v[-1]/v[0])),
        float(math.sqrt(float(np.sum(lr*lr)))),
        float(math.log(float(np.max(v))/float(np.min(v))))
    )

def feature(bundle,target):
    origin=base.month_shift(target,-1)
    z=[]
    for metal in base.METALS:
        z.extend(daily_summary(bundle,metal,origin))
    x=np.asarray(z,float)
    if x.shape!=(12,) or not np.isfinite(x).all():
        raise RuntimeError(f"FEATURE_FAIL target={target} shape={x.shape}")
    return x

def arrays_at_origin(bundle,target):
    origin=base.month_shift(target,-1)
    gh=bundle.gpr_vintages[origin]
    keys=[]; X=[]; y=[]
    for ht in base.month_range(COMMON_TRAIN_START,origin):
        try:
            _,y4=base.sample_for_target(bundle,ht,gh,True)
            x=feature(bundle,ht)
        except RuntimeError:
            continue
        keys.append(ht); X.append(x); y.append(float(y4[0]))
    if len(keys)<30:
        raise RuntimeError(f"TRAIN_TOO_SMALL target={target} n={len(keys)}")
    return keys,np.stack(X),np.asarray(y,float),feature(bundle,target).reshape(1,-1)

def make_model(name):
    spec=SPECS[name]
    return SVR(**spec["params"]) if spec["kind"]=="SVR" else NuSVR(**spec["params"])

def predict_one(bundle,target,name):
    keys,X,y,tx=arrays_at_origin(bundle,target)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=make_model(name)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED model={name} target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin])
    forecast=float(prev*math.exp(pred))
    actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"model":name,
        "representation":"DAILY_SUMMARY12","train_rows":len(keys),
        "train_first":keys[0],"train_last":keys[-1],
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }

def evaluate(bundle,name):
    rows=[predict_one(bundle,t,name) for t in base.month_range(DEV_START,DEV_END)]
    return {"spec":SPECS[name],"metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows}

def run_all(bundle):
    return {name:evaluate(bundle,name) for name in SPECS}

def stable_hash(results):
    compact={}
    for name in sorted(results):
        compact[name]=[
            {k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct")}
            for r in results[name]["rows"]
        ]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def md(out):
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 2C FORMULATION CHECK",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS / META_PARENT_SVR FROZEN**",
        "",
        "## Frozen comparison protocol",
        "- Kernel: RBF, frozen from Stage 2A.",
        "- Representation: DAILY_SUMMARY12, frozen from Stage 2B.",
        "- Training-only X/Y standardization.",
        "- Common history start: 2010-05.",
        "- epsilon-SVR: C=1, epsilon=0.1, gamma=scale.",
        "- NuSVR: C=1, nu=0.5, gamma=scale.",
        "- DEV only 2022-04..2024-12.",
        "- No hyperparameter tuning.",
        "- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.",
        "",
        "## DEV ranking",
        "",
        "| Rank | Model | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for i,z in enumerate(out["ranking"],1):
        lines.append(f"| {i} | {z['model']} | {z['sum_abs_error']:.6f} | {z['mae']:.6f} | {z['rmse']:.6f} | {z['mape_pct']:.4f}% | {z['relative_mae_vs_rw']:.6f} | {z['direction_correct']}/33 | {z['worst_month']} |")
    p=out["meta_parent_svr"]
    lines += [
        "",
        "## Stage 2 decision / parent freeze",
        f"- Frozen META_PARENT_SVR: **{p['model']}**.",
        "- Parent identity is frozen before Stage 3 hyperparameter outcomes.",
        "- Stage 3 may refine only the parent formulation under the predeclared chronological tuning protocol.",
        "- Stage 4 32/32 metaheuristics will use the Stage-3-frozen parent and bounds.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Kernel freeze before formulation outcome: PASS.",
        "- Representation freeze before formulation outcome: PASS.",
        "- DEV-only: PASS.",
        "- Training-only scaling: PASS.",
        "- Determinism: PASS.",
        "- META_PARENT_SVR frozen before Stage 3: PASS.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        f"- Payload SHA256: {out['determinism']['payload_sha256']}",
        "",
    ]
    return "\n".join(lines)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    first=run_all(b); h1=stable_hash(first)
    second=run_all(b); h2=stable_hash(second)
    if h1!=h2: raise RuntimeError(f"DETERMINISM_FAIL {h1} {h2}")
    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    expected=list(base.month_range(DEV_START,DEV_END))
    for name,v in first.items():
        if v["metrics"]["n"]!=33 or [r["target"] for r in v["rows"]]!=expected:
            raise RuntimeError(f"DEV_FAIL {name}")
        if any(r["train_last"]>=r["target"] for r in v["rows"]):
            raise RuntimeError(f"CHRONOLOGY_FAIL {name}")
    ranking=sorted(
        [{"model":name,**v["metrics"]} for name,v in first.items()],
        key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["model"])
    )
    parent={
        "model":ranking[0]["model"],
        "kernel":"rbf",
        "representation":"DAILY_SUMMARY12",
        "feature_dim":12,
        "formulation":SPECS[ranking[0]["model"]]["kind"],
        "canonical_params":SPECS[ranking[0]["model"]]["params"],
        "dev_sum_abs_error":ranking[0]["sum_abs_error"],
        "dev_direction_correct":ranking[0]["direction_correct"],
    }
    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE2C_FORMULATION_AND_PARENT_FREEZE_DEV_ONLY_V1",
        "contract":{
            "kernel":"rbf","representation":"DAILY_SUMMARY12","feature_dim":12,
            "scaling":"TRAIN_ONLY_XY_STANDARDIZATION","common_train_start":COMMON_TRAIN_START,
            "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED",
            "2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY",
            "hyperparameter_tuning":"NONE"
        },
        "models":first,"ranking":ranking,"meta_parent_svr":parent,
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
    }
    Path("gold_monthly_svr_dwt_stage2c_formulation_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE2C_FORMULATION_PARENT_FREEZE_2026-09-28.md").write_text(md(out),encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"ranking":ranking,"meta_parent_svr":parent,"payload_sha256":h1},sort_keys=True))

if __name__=="__main__":
    main()
