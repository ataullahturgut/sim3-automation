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
import gold_monthly_svr_dwt_stage3a_coarse_v1 as s3a

DEV_START, DEV_END = "2022-04", "2024-12"

REGION_A = {
    "log2_C": (-2,0,2),
    "log2_gamma": (-6,-4,-2),
    "epsilon": (0.01,0.03,0.05,0.075,0.10),
}
REGION_B = {
    "log2_C": (2,4,6),
    "log2_gamma": (-12,-10,-8),
    "epsilon": (0.01,0.03,0.05,0.10,0.15,0.20),
}
REGION_C = {
    "log2_C": (6,8,10),
    "log2_gamma": (-10,-8,-6),
    "epsilon": (0.03,0.05,0.075,0.10,0.15),
}

def region_points(region):
    out=[]
    for ce in region["log2_C"]:
        for ge in region["log2_gamma"]:
            for ep in region["epsilon"]:
                out.append((2.0**ce,2.0**ge,float(ep),int(ce),int(ge)))
    return out

GRID = tuple(sorted(set(region_points(REGION_A)+region_points(REGION_B)+region_points(REGION_C)),
                    key=lambda z:(z[3],z[4],z[2])))
if len(GRID)!=136:
    raise RuntimeError(f"LOCAL_GRID_COUNT_FAIL n={len(GRID)}")

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def select_candidate(X,y):
    Xtrz,ytrz,Xvz,yvz,nval=s3a.split_and_scale(X,y)
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
            best={
                "key":key,"inner_mae":mae,"C":C,"gamma":gamma,"epsilon":epsilon,
                "log2_C":ce,"log2_gamma":ge,
                "inner_valid_n":nval,"inner_train_n":len(y)-nval
            }
    return best

def predict_local(bundle,target):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    best=select_candidate(X,y)
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
        "target":target,"origin":origin,"model":"STAGE3B_LOCAL_TUNED",
        "representation":"DAILY_SUMMARY12","train_rows":len(keys),
        "train_first":keys[0],"train_last":keys[-1],
        "selected":{
            "C":best["C"],"gamma":best["gamma"],"epsilon":best["epsilon"],
            "log2_C":best["log2_C"],"log2_gamma":best["log2_gamma"],
            "inner_mae":best["inner_mae"],"inner_train_n":best["inner_train_n"],
            "inner_valid_n":best["inner_valid_n"]
        },
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }

def local_rows(bundle):
    return [predict_local(bundle,t) for t in base.month_range(DEV_START,DEV_END)]

def parent_rows(bundle):
    return [s2c.predict_one(bundle,t,"EPSILON_RBF_DAILY12") for t in base.month_range(DEV_START,DEV_END)]

def coarse_rows(bundle):
    return s3a.tuned_rows(bundle)

def stable_hash(local,parent,coarse):
    compact={
        "local":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct","selected")} for r in local],
        "parent":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in parent],
        "coarse":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct","selected")} for r in coarse],
    }
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def selection_summary(rows):
    counts=Counter((r["selected"]["log2_C"],r["selected"]["log2_gamma"],r["selected"]["epsilon"]) for r in rows)
    return [
        {"log2_C":k[0],"log2_gamma":k[1],"epsilon":k[2],"count":v}
        for k,v in sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]))
    ]

def md(out):
    pm=out["parent"]["metrics"]; cm=out["coarse"]["metrics"]; lm=out["local"]["metrics"]
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3B LOCAL REFINEMENT RESULT",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS**",
        "",
        "## Frozen local search",
        "- Frozen parent: epsilon-SVR / RBF / DAILY_SUMMARY12.",
        "- Frozen local union: 136 unique candidates.",
        "- Same nested chronological protocol as Stage 3A.",
        "- Inner validation final 20% pre-target tail, minimum 12 rows.",
        "- Inner scalers fit only on inner train.",
        "- Outer refit uses all pre-target rows only.",
        "- 2025 opened: NO. 2026 used: NO.",
        "",
        "## DEV comparison",
        "",
        "| Candidate | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        f"| Frozen Stage-2 parent | {pm['sum_abs_error']:.6f} | {pm['mae']:.6f} | {pm['rmse']:.6f} | {pm['mape_pct']:.4f}% | {pm['relative_mae_vs_rw']:.6f} | {pm['direction_correct']}/33 | {pm['worst_month']} |",
        f"| Stage-3A coarse tuned | {cm['sum_abs_error']:.6f} | {cm['mae']:.6f} | {cm['rmse']:.6f} | {cm['mape_pct']:.4f}% | {cm['relative_mae_vs_rw']:.6f} | {cm['direction_correct']}/33 | {cm['worst_month']} |",
        f"| Stage-3B local tuned | {lm['sum_abs_error']:.6f} | {lm['mae']:.6f} | {lm['rmse']:.6f} | {lm['mape_pct']:.4f}% | {lm['relative_mae_vs_rw']:.6f} | {lm['direction_correct']}/33 | {lm['worst_month']} |",
        "",
        f"Stage-3B delta vs parent SigmaAE: **{lm['sum_abs_error']-pm['sum_abs_error']:+.6f}**.",
        f"Stage-3B delta vs Stage-3A SigmaAE: **{lm['sum_abs_error']-cm['sum_abs_error']:+.6f}**.",
        "",
        "## Most frequent local selections",
        "",
        "| log2(C) | log2(gamma) | epsilon | Outer origins |",
        "|---:|---:|---:|---:|",
    ]
    for z in out["selection_frequency"][:12]:
        lines.append(f"| {z['log2_C']} | {z['log2_gamma']} | {z['epsilon']:.3f} | {z['count']} |")
    lines += [
        "",
        "## Decision",
        f"- Deterministic tuning promoted: **{out['decision']['deterministic_tuning_promoted']}**.",
        f"- Deterministic benchmark carried forward: **{out['decision']['carried_forward']}**.",
        "- No additional deterministic rescue tuning is authorized.",
        "- Next step is a separate pre-outcome Stage-4 bounds freeze for the mandatory 32/32 metaheuristic screen.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Stage-3B pre-outcome freeze respected: PASS.",
        "- Frozen local union size 136: PASS.",
        "- Inner chronology: PASS.",
        "- Inner scaling train-only: PASS.",
        "- Outer refit pre-target only: PASS.",
        "- Parent and Stage-3A reconciliation: PASS.",
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
    local=local_rows(bundle)
    parent=parent_rows(bundle)
    coarse=coarse_rows(bundle)
    return local,parent,coarse,stable_hash(local,parent,coarse)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)

    local,parent,coarse,h1=run_once(b)
    local2,parent2,coarse2,h2=run_once(b)
    if h1!=h2:
        raise RuntimeError(f"DETERMINISM_FAIL {h1} {h2}")

    pm=s1.metrics(parent); cm=s1.metrics(coarse); lm=s1.metrics(local)
    if abs(pm["sum_abs_error"]-1449.187363)>1e-5:
        raise RuntimeError(f"PARENT_RECONCILE_FAIL {pm['sum_abs_error']}")
    if abs(cm["sum_abs_error"]-1580.901050)>1e-5:
        raise RuntimeError(f"STAGE3A_RECONCILE_FAIL {cm['sum_abs_error']}")

    grid_keys={(ce,ge,ep) for _,_,ep,ce,ge in GRID}
    expected=list(base.month_range(DEV_START,DEV_END))
    if [r["target"] for r in local]!=expected:
        raise RuntimeError("TARGET_ALIGNMENT_FAIL")
    for r in local:
        s=r["selected"]
        if (s["log2_C"],s["log2_gamma"],s["epsilon"]) not in grid_keys:
            raise RuntimeError(f"GRID_MEMBERSHIP_FAIL {r['target']}")
        if r["train_last"]>=r["target"]:
            raise RuntimeError(f"CHRONOLOGY_FAIL {r['target']}")

    after=read_invariants(dsn)
    if after!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    candidates=[
        ("STAGE2_PARENT",pm["sum_abs_error"]),
        ("STAGE3A_COARSE",cm["sum_abs_error"]),
        ("STAGE3B_LOCAL",lm["sum_abs_error"]),
    ]
    carried=min(candidates,key=lambda x:x[1])[0]
    promoted=bool(lm["sum_abs_error"] < pm["sum_abs_error"])

    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE3B_LOCAL_REFINEMENT_DEV_ONLY_V1",
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE3B_LOCAL_REFINEMENT_FREEZE_2026-09-28.md",
        "local_grid":{
            "candidate_count":len(GRID),
            "region_A":REGION_A,
            "region_B":REGION_B,
            "region_C":REGION_C,
        },
        "inner_protocol":{
            "validation":"final_20pct_chronological",
            "minimum_validation_rows":12,
            "objective":"mean_absolute_standardized_gold_log_return_error",
            "scaling":"INNER_TRAIN_ONLY",
        },
        "contract":{
            "parent":"EPSILON_RBF_DAILY12",
            "representation":"DAILY_SUMMARY12",
            "kernel":"rbf",
            "dev":"2022-04..2024-12",
            "2025_role":"LOCKED_NOT_OPENED",
            "2026_role":"QUARANTINED_NOT_USED",
            "random_split":"NONE",
            "database":"READ_ONLY",
        },
        "parent":{"metrics":pm,"yearly":s1.yearly(parent),"rows":parent},
        "coarse":{"metrics":cm,"yearly":s1.yearly(coarse),"rows":coarse},
        "local":{"metrics":lm,"yearly":s1.yearly(local),"rows":local},
        "selection_frequency":selection_summary(local),
        "decision":{
            "deterministic_tuning_promoted":"YES" if promoted else "NO",
            "carried_forward":carried,
            "further_deterministic_rescue_tuning":"CLOSED_NOT_AUTHORIZED",
        },
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
    }

    Path("gold_monthly_svr_dwt_stage3b_local_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE3B_LOCAL_RESULT_2026-09-28.md").write_text(
        md(out),encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "parent":pm,"coarse":cm,"local":lm,
        "decision":out["decision"],
        "selection_frequency":out["selection_frequency"][:12],
        "payload_sha256":h1
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
