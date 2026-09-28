#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1

DEV_START, DEV_END = "2022-04", "2024-12"

SPECS = {
    "LINEAR_SVR":{"kernel":"linear","C":1.0,"epsilon":0.1,"shrinking":True,"tol":1e-3},
    "RBF_SVR":{"kernel":"rbf","C":1.0,"epsilon":0.1,"gamma":"scale","shrinking":True,"tol":1e-3},
    "POLY2_SVR":{"kernel":"poly","degree":2,"C":1.0,"epsilon":0.1,"gamma":"scale","coef0":0.0,"shrinking":True,"tol":1e-3},
    "POLY3_SVR":{"kernel":"poly","degree":3,"C":1.0,"epsilon":0.1,"gamma":"scale","coef0":0.0,"shrinking":True,"tol":1e-3},
    "SIGMOID_SVR":{"kernel":"sigmoid","C":1.0,"epsilon":0.1,"gamma":"scale","coef0":0.0,"shrinking":True,"tol":1e-3},
}

STAGE1_REF = {
    "LINEAR_SVR": 1535.115953,
    "RBF_SVR": 1524.500568,
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def predict_one(bundle,target,name):
    keys,X,y,tx=s1.training_arrays_at_origin(bundle,target)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(**SPECS[name])
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
        "train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
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
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 2A KERNEL ABLATION",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS**",
        "",
        "## Protocol",
        "- DEV only: 2022-04..2024-12, n=33.",
        "- CURRENT8 unchanged.",
        "- Training-only X/Y standardization.",
        "- epsilon-SVR, fixed C=1.0 and epsilon=0.1.",
        "- Kernels: linear, RBF, polynomial degree 2, polynomial degree 3, sigmoid.",
        "- RBF/poly/sigmoid gamma=scale; poly/sigmoid coef0=0.",
        "- No hyperparameter tuning.",
        "- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.",
        "",
        "## DEV ranking",
        "",
        "| Rank | Model | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for i,z in enumerate(out["ranking"],1):
        lines.append(f"| {i} | {z['model']} | {z['sum_abs_error']:.6f} | {z['mae']:.6f} | {z['rmse']:.6f} | {z['mape_pct']:.4f}% | {z['relative_mae_vs_rw']:.6f} | {z['direction_correct']}/33 | {z['worst_month']} |")
    leader=out["ranking"][0]
    lines += [
        "",
        "## Decision",
        f"- Stage 2A kernel leader: **{leader['model']}**.",
        "- This is not yet META_PARENT_SVR; Stage 2B and 2C remain mandatory.",
        "- No kernel is dropped from historical record.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Stage 1 linear/RBF reconciliation: PASS.",
        "- DEV-only: PASS.",
        "- Fixed canonical hyperparameters: PASS.",
        "- Training-only scaling: PASS.",
        "- Determinism: PASS.",
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

    reconcile={}
    for name,ref in STAGE1_REF.items():
        cur=float(first[name]["metrics"]["sum_abs_error"])
        diff=abs(cur-ref)
        reconcile[name]={"stage1_rounded_ref":ref,"stage2a":cur,"abs_diff":diff}
        if diff>1e-5: raise RuntimeError(f"STAGE1_RECONCILE_FAIL {name} {diff}")

    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    expected=list(base.month_range(DEV_START,DEV_END))
    for name,v in first.items():
        if [r["target"] for r in v["rows"]]!=expected: raise RuntimeError(f"TARGET_FAIL {name}")
        if v["metrics"]["n"]!=33: raise RuntimeError(f"N_FAIL {name}")
        if any(r["train_last"]>=r["target"] for r in v["rows"]): raise RuntimeError(f"CHRONOLOGY_FAIL {name}")

    ranking=sorted(
        [{"model":name,**v["metrics"]} for name,v in first.items()],
        key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["model"])
    )
    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE2A_KERNEL_ABLATION_DEV_ONLY_V1",
        "authority":"GOLD_MONTHLY_SVR_DWT_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md",
        "contract":{
            "representation":"CURRENT8","model":"epsilon-SVR",
            "C":1.0,"epsilon":0.1,"scaling":"TRAIN_ONLY_XY_STANDARDIZATION",
            "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED",
            "2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY",
            "hyperparameter_tuning":"NONE"
        },
        "stage1_reconciliation":reconcile,
        "models":first,"ranking":ranking,
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
    }
    Path("gold_monthly_svr_dwt_stage2a_kernel_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE2A_KERNEL_RESULT_2026-09-28.md").write_text(md(out),encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"ranking":ranking,"reconcile":reconcile,"payload_sha256":h1},sort_keys=True))

if __name__=="__main__":
    main()
