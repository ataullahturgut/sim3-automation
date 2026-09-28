#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage2c_formulation_v1 as s2c

DEV_START, DEV_END = "2022-04", "2024-12"

C_EXP = (-8,-4,0,4,8,12)
G_EXP = (-12,-8,-4,0,4)
EPS = (0.01,0.05,0.10,0.20,0.50)
GRID = tuple((2.0**ce,2.0**ge,ep,ce,ge) for ce in C_EXP for ge in G_EXP for ep in EPS)
if len(GRID)!=150:
    raise RuntimeError("GRID_COUNT_FAIL")

PARENT_REF = 1449.187363

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def split_and_scale(X,y):
    n=len(y)
    nval=max(12,int(math.ceil(0.20*n)))
    if n-nval < 30:
        raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={n} nval={nval}")
    Xtr,Xv=X[:-nval],X[-nval:]
    ytr,yv=y[:-nval],y[-nval:]
    xm=Xtr.mean(0); xs=Xtr.std(0,ddof=0); xs=np.where(xs<1e-12,1.0,xs)
    ym=float(ytr.mean()); ys=float(ytr.std(ddof=0)); ys=1.0 if ys<1e-12 else ys
    Xtrz=(Xtr-xm)/xs; Xvz=(Xv-xm)/xs
    ytrz=(ytr-ym)/ys; yvz=(yv-ym)/ys
    if not (np.isfinite(Xtrz).all() and np.isfinite(Xvz).all() and np.isfinite(ytrz).all() and np.isfinite(yvz).all()):
        raise RuntimeError("INNER_SCALE_NONFINITE")
    return Xtrz,ytrz,Xvz,yvz,nval

def select_candidate(X,y):
    Xtrz,ytrz,Xvz,yvz,nval=split_and_scale(X,y)
    best=None
    for C,gamma,epsilon,ce,ge in GRID:
        model=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=epsilon,shrinking=True,tol=1e-3)
        model.fit(Xtrz,ytrz)
        pred=np.asarray(model.predict(Xvz),float)
        mae=float(np.mean(np.abs(pred-yvz)))
        if not math.isfinite(mae):
            raise RuntimeError(f"NONFINITE_INNER C={C} gamma={gamma} eps={epsilon}")
        key=(mae,C,epsilon,gamma)
        if best is None or key<best["key"]:
            best={"key":key,"inner_mae":mae,"C":C,"gamma":gamma,"epsilon":epsilon,
                  "log2_C":ce,"log2_gamma":ge,"inner_valid_n":nval,
                  "inner_train_n":len(y)-nval}
    return best

def predict_tuned(bundle,target):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    best=select_candidate(X,y)

    # Outer refit: scalers fit on ALL pre-target rows only.
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(kernel="rbf",C=best["C"],gamma=best["gamma"],epsilon=best["epsilon"],shrinking=True,tol=1e-3)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED target={target} pred={pred}")

    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin])
    forecast=float(prev*math.exp(pred))
    actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"model":"STAGE3A_COARSE_TUNED",
        "representation":"DAILY_SUMMARY12","train_rows":len(keys),
        "train_first":keys[0],"train_last":keys[-1],
        "selected":{"C":best["C"],"gamma":best["gamma"],"epsilon":best["epsilon"],
                    "log2_C":best["log2_C"],"log2_gamma":best["log2_gamma"],
                    "inner_mae":best["inner_mae"],"inner_train_n":best["inner_train_n"],
                    "inner_valid_n":best["inner_valid_n"]},
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }

def tuned_rows(bundle):
    return [predict_tuned(bundle,t) for t in base.month_range(DEV_START,DEV_END)]

def parent_rows(bundle):
    return [s2c.predict_one(bundle,t,"EPSILON_RBF_DAILY12") for t in base.month_range(DEV_START,DEV_END)]

def stable_hash(tuned,parent):
    compact={
        "tuned":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct","selected")} for r in tuned],
        "parent":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in parent],
    }
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def selection_summary(rows):
    counts=Counter((r["selected"]["log2_C"],r["selected"]["log2_gamma"],r["selected"]["epsilon"]) for r in rows)
    return [
        {"log2_C":k[0],"log2_gamma":k[1],"epsilon":k[2],"count":v}
        for k,v in sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]))
    ]

def md(out):
    tm=out["tuned"]["metrics"]; pm=out["parent"]["metrics"]
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3A COARSE NESTED GRID RESULT",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS**",
        "",
        "## Frozen search",
        "- Parent: epsilon-SVR / RBF / DAILY_SUMMARY12.",
        "- Grid: 150 combinations.",
        "- log2(C): -8,-4,0,4,8,12.",
        "- log2(gamma): -12,-8,-4,0,4.",
        "- epsilon: 0.01,0.05,0.10,0.20,0.50.",
        "- Inner validation: final 20% chronological pre-target tail, minimum 12 rows.",
        "- Inner scalers fit only on inner train.",
        "- Outer refit uses all pre-target rows only.",
        "- 2025 opened: NO. 2026 used: NO.",
        "",
        "## DEV result",
        "",
        "| Candidate | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        f"| Frozen Stage-2 parent | {pm['sum_abs_error']:.6f} | {pm['mae']:.6f} | {pm['rmse']:.6f} | {pm['mape_pct']:.4f}% | {pm['relative_mae_vs_rw']:.6f} | {pm['direction_correct']}/33 | {pm['worst_month']} |",
        f"| Stage-3A coarse tuned | {tm['sum_abs_error']:.6f} | {tm['mae']:.6f} | {tm['rmse']:.6f} | {tm['mape_pct']:.4f}% | {tm['relative_mae_vs_rw']:.6f} | {tm['direction_correct']}/33 | {tm['worst_month']} |",
        "",
        f"Delta tuned minus parent SigmaAE: **{tm['sum_abs_error']-pm['sum_abs_error']:+.6f}**.",
        "",
        "## Most frequent selected coarse points",
        "",
        "| log2(C) | log2(gamma) | epsilon | Outer origins |",
        "|---:|---:|---:|---:|",
    ]
    for z in out["selection_frequency"][:12]:
        lines.append(f"| {z['log2_C']} | {z['log2_gamma']} | {z['epsilon']:.2f} | {z['count']} |")
    lines += [
        "",
        "## Decision",
        "- Stage 3A is a coarse nested benchmark, not the final tuned freeze.",
        "- Stage 3B local refinement must be frozen separately before execution.",
        "- No Stage-4 metaheuristic execution is authorized yet.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Pre-outcome Stage-3A freeze respected: PASS.",
        "- Grid size exactly 150: PASS.",
        "- Inner chronology: PASS.",
        "- Inner scaling train-only: PASS.",
        "- Outer refit pre-target only: PASS.",
        "- Parent reconciliation: PASS.",
        "- Deterministic replay: PASS.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        f"- Payload SHA256: {out['determinism']['payload_sha256']}",
        "",
    ]
    return "\n".join(lines)

def run_once(bundle):
    tuned=tuned_rows(bundle)
    parent=parent_rows(bundle)
    return tuned,parent,stable_hash(tuned,parent)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)

    tuned,parent,h1=run_once(b)
    tuned2,parent2,h2=run_once(b)
    if h1!=h2: raise RuntimeError(f"DETERMINISM_FAIL {h1} {h2}")

    pm=s1.metrics(parent)
    if abs(pm["sum_abs_error"]-PARENT_REF)>1e-5:
        raise RuntimeError(f"PARENT_RECONCILE_FAIL {pm['sum_abs_error']}")

    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    expected=list(base.month_range(DEV_START,DEV_END))
    if [r["target"] for r in tuned]!=expected or [r["target"] for r in parent]!=expected:
        raise RuntimeError("TARGET_ALIGNMENT_FAIL")
    for r in tuned:
        s=r["selected"]
        if s["log2_C"] not in C_EXP or s["log2_gamma"] not in G_EXP or s["epsilon"] not in EPS:
            raise RuntimeError(f"GRID_MEMBERSHIP_FAIL {r['target']}")
        if r["train_last"]>=r["target"]:
            raise RuntimeError(f"CHRONOLOGY_FAIL {r['target']}")

    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE3A_COARSE_NESTED_GRID_DEV_ONLY_V1",
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE3A_COARSE_GRID_FREEZE_2026-09-28.md",
        "grid":{"log2_C":list(C_EXP),"log2_gamma":list(G_EXP),"epsilon":list(EPS),"candidate_count":len(GRID)},
        "inner_protocol":{"validation":"final_20pct_chronological","minimum_validation_rows":12,
                          "objective":"mean_absolute_standardized_gold_log_return_error",
                          "scaling":"INNER_TRAIN_ONLY"},
        "contract":{"parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
                    "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED",
                    "2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY"},
        "parent":{"metrics":pm,"yearly":s1.yearly(parent),"rows":parent},
        "tuned":{"metrics":s1.metrics(tuned),"yearly":s1.yearly(tuned),"rows":tuned},
        "selection_frequency":selection_summary(tuned),
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
    }
    Path("gold_monthly_svr_dwt_stage3a_coarse_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE3A_COARSE_RESULT_2026-09-28.md").write_text(md(out),encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"parent":pm,"tuned":out["tuned"]["metrics"],"selection_frequency":out["selection_frequency"][:12],"payload_sha256":h1},sort_keys=True))

if __name__=="__main__":
    main()
