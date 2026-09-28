#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_boosting_stage2_feature_representation_v1 as brep

DEV_START, DEV_END = "2022-04", "2024-12"
COMMON_TRAIN_START = "2010-05"
REPS = ("CURRENT8","RAW_LEVEL_LAGS8","SIMPLE_RETURNS8","DAILY_SUMMARY12","MIXED20")
EXPECTED_DIMS = dict(brep.EXPECTED_DIMS)
RBF_SPEC = {"kernel":"rbf","C":1.0,"epsilon":0.1,"gamma":"scale","shrinking":True,"tol":1e-3}


def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def rep_from_current8(bundle, target, rep, current8):
    p=base.month_shift(target,-1)
    pp=base.month_shift(target,-2)
    p3=base.month_shift(target,-4)

    if rep=="CURRENT8":
        x=np.asarray(current8,float)
    elif rep=="RAW_LEVEL_LAGS8":
        z=[]
        for m in base.METALS:
            M=bundle.monthly_metal[m]
            if p not in M or pp not in M:
                raise RuntimeError(f"MONTHLY_LEVEL_MISSING {m} {target}")
            z.extend((float(M[p]),float(M[pp])))
        x=np.asarray(z,float)
    elif rep=="SIMPLE_RETURNS8":
        z=[]
        for m in base.METALS:
            M=bundle.monthly_metal[m]
            for k in (p,pp,p3):
                if k not in M:
                    raise RuntimeError(f"MONTHLY_RETURN_LEVEL_MISSING {m} {target} {k}")
            z.extend((float(math.log(M[p]/M[pp])),float(math.log(M[p]/M[p3]))))
        x=np.asarray(z,float)
    elif rep=="DAILY_SUMMARY12":
        z=[]
        for m in base.METALS:
            z.extend(brep.daily_summary(bundle,m,p))
        x=np.asarray(z,float)
    elif rep=="MIXED20":
        levels=[]; mom3=[]; rv=[]
        for m in base.METALS:
            M=bundle.monthly_metal[m]
            if p not in M or p3 not in M:
                raise RuntimeError(f"MIXED_MONTHLY_MISSING {m} {target}")
            levels.append(float(M[p]))
            mom3.append(float(math.log(M[p]/M[p3])))
            rv.append(float(brep.daily_summary(bundle,m,p)[1]))
        x=np.r_[np.asarray(current8,float),np.asarray(levels),np.asarray(mom3),np.asarray(rv)].astype(float)
    else:
        raise KeyError(rep)

    if x.shape!=(EXPECTED_DIMS[rep],) or not np.isfinite(x).all():
        raise RuntimeError(f"REP_FAIL rep={rep} target={target} shape={x.shape}")
    return x


def arrays_at_origin(bundle,target,rep):
    origin=base.month_shift(target,-1)
    gh=bundle.gpr_vintages[origin]
    keys=[]; X=[]; y=[]
    for ht in base.month_range(COMMON_TRAIN_START,origin):
        try:
            cx,y4=base.sample_for_target(bundle,ht,gh,True)
            rx=rep_from_current8(bundle,ht,rep,cx)
        except RuntimeError:
            continue
        keys.append(ht); X.append(rx); y.append(float(y4[0]))
    if len(keys)<30:
        raise RuntimeError(f"TRAIN_TOO_SMALL rep={rep} target={target} n={len(keys)}")
    tx_current=s1.current8_x(bundle,target,gh)
    tx=rep_from_current8(bundle,target,rep,tx_current).reshape(1,-1)
    X=np.stack(X); y=np.asarray(y,float)
    return keys,X,y,tx


def predict_one(bundle,target,rep):
    keys,X,y,tx=arrays_at_origin(bundle,target,rep)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(**RBF_SPEC)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED rep={rep} target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin])
    forecast=float(prev*math.exp(pred))
    actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"representation":rep,
        "feature_dim":EXPECTED_DIMS[rep],"train_rows":len(keys),
        "train_first":keys[0],"train_last":keys[-1],
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }


def evaluate(bundle,rep):
    rows=[predict_one(bundle,t,rep) for t in base.month_range(DEV_START,DEV_END)]
    return {"representation":rep,"feature_dim":EXPECTED_DIMS[rep],
            "metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows}


def run_all(bundle):
    return {rep:evaluate(bundle,rep) for rep in REPS}


def stable_hash(results):
    compact={}
    for rep in REPS:
        compact[rep]=[
            {k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct")}
            for r in results[rep]["rows"]
        ]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def md(out):
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 2B REPRESENTATION ABLATION",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS**",
        "",
        "## Protocol",
        "- RBF epsilon-SVR frozen from Stage 2A.",
        "- C=1.0, epsilon=0.1, gamma=scale.",
        "- Training-only X/Y standardization.",
        "- Common training-history start: 2010-05 for representation fairness.",
        "- DEV only 2022-04..2024-12.",
        "- Representations: CURRENT8, RAW_LEVEL_LAGS8, SIMPLE_RETURNS8, DAILY_SUMMARY12, MIXED20.",
        "- No hyperparameter tuning.",
        "- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.",
        "",
        "## DEV ranking",
        "",
        "| Rank | Representation | Dim | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for i,z in enumerate(out["ranking"],1):
        lines.append(f"| {i} | {z['representation']} | {z['feature_dim']} | {z['sum_abs_error']:.6f} | {z['mae']:.6f} | {z['rmse']:.6f} | {z['mape_pct']:.4f}% | {z['relative_mae_vs_rw']:.6f} | {z['direction_correct']}/33 | {z['worst_month']} |")
    leader=out["ranking"][0]
    lines += [
        "",
        "## Decision",
        f"- Stage 2B representation leader under frozen RBF baseline: **{leader['representation']}**.",
        "- No META_PARENT_SVR is frozen yet; Stage 2C formulation remains mandatory.",
        "- All representation outcomes remain in the ledger even if weak.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Kernel frozen before representation outcomes: PASS.",
        "- Common training history: PASS.",
        "- Training-only scaling: PASS.",
        "- DEV-only: PASS.",
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
    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    expected=list(base.month_range(DEV_START,DEV_END))
    for rep,v in first.items():
        if v["metrics"]["n"]!=33 or [r["target"] for r in v["rows"]]!=expected:
            raise RuntimeError(f"DEV_FAIL {rep}")
        if any(r["train_last"]>=r["target"] for r in v["rows"]):
            raise RuntimeError(f"CHRONOLOGY_FAIL {rep}")
    ranking=sorted(
        [{"representation":rep,"feature_dim":EXPECTED_DIMS[rep],**v["metrics"]} for rep,v in first.items()],
        key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["representation"])
    )
    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE2B_REPRESENTATION_ABLATION_DEV_ONLY_V1",
        "contract":{
            "kernel":"rbf","C":1.0,"epsilon":0.1,"gamma":"scale",
            "scaling":"TRAIN_ONLY_XY_STANDARDIZATION","common_train_start":COMMON_TRAIN_START,
            "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED",
            "2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY",
            "hyperparameter_tuning":"NONE"
        },
        "representations":{k:EXPECTED_DIMS[k] for k in REPS},
        "results":first,"ranking":ranking,
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
    }
    Path("gold_monthly_svr_dwt_stage2b_representation_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE2B_REPRESENTATION_RESULT_2026-09-28.md").write_text(md(out),encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"ranking":ranking,"payload_sha256":h1},sort_keys=True))

if __name__=="__main__":
    main()
