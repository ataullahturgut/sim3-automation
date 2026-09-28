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
PARENT_REF = 1449.187363
EPS_LOCAL = {
    0.01:(0.01,0.025,0.05),
    0.05:(0.025,0.05,0.075),
    0.10:(0.075,0.10,0.15),
    0.20:(0.15,0.20,0.35),
    0.50:(0.35,0.50),
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def local_grid(coarse):
    ce=int(coarse["log2_C"]); ge=int(coarse["log2_gamma"]); ep=float(coarse["epsilon"])
    ces=sorted(set(max(-8,min(12,ce+d)) for d in (-2,0,2)))
    ges=sorted(set(max(-12,min(4,ge+d)) for d in (-2,0,2)))
    eps=EPS_LOCAL[ep]
    return tuple((2.0**c,2.0**g,e,c,g) for c in ces for g in ges for e in eps)

def select_local(X,y):
    coarse=s3a.select_candidate(X,y)
    Xtrz,ytrz,Xvz,yvz,nval=s3a.split_and_scale(X,y)
    grid=local_grid(coarse)
    best=None
    for C,gamma,epsilon,ce,ge in grid:
        model=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=epsilon,shrinking=True,tol=1e-3)
        model.fit(Xtrz,ytrz)
        pred=np.asarray(model.predict(Xvz),float)
        mae=float(np.mean(np.abs(pred-yvz)))
        key=(mae,C,epsilon,gamma)
        if best is None or key<best["key"]:
            best={"key":key,"inner_mae":mae,"C":C,"gamma":gamma,"epsilon":epsilon,
                  "log2_C":ce,"log2_gamma":ge,"inner_valid_n":nval,
                  "inner_train_n":len(y)-nval}
    return coarse,best,len(grid)

def predict_local(bundle,target):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    coarse,best,grid_n=select_local(X,y)
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
        "coarse_center":{"log2_C":coarse["log2_C"],"log2_gamma":coarse["log2_gamma"],"epsilon":coarse["epsilon"]},
        "local_grid_n":grid_n,
        "selected":{"C":best["C"],"gamma":best["gamma"],"epsilon":best["epsilon"],
                    "log2_C":best["log2_C"],"log2_gamma":best["log2_gamma"],
                    "inner_mae":best["inner_mae"],"inner_train_n":best["inner_train_n"],
                    "inner_valid_n":best["inner_valid_n"]},
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
        "local":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct","coarse_center","selected")} for r in local],
        "parent":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in parent],
        "coarse":[{k:r[k] for k in ("target","forecast","actual","rw","pred_log_return_gold","direction_correct","selected")} for r in coarse],
    }
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def freq(rows):
    c=Counter((r["selected"]["log2_C"],r["selected"]["log2_gamma"],r["selected"]["epsilon"]) for r in rows)
    return [{"log2_C":k[0],"log2_gamma":k[1],"epsilon":k[2],"count":v}
            for k,v in sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))]

def md(out):
    pm=out["parent"]["metrics"]; cm=out["coarse"]["metrics"]; lm=out["local"]["metrics"]
    promoted=out["decision"]["promoted"]
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3B LOCAL REFINEMENT RESULT",
        "",
        "Date: 2026-09-28",
        f"Status: **COMPLETE / SCIENTIFIC GATE PASS / {'PROMOTED' if promoted else 'NOT PROMOTED'}**",
        "",
        "## DEV comparison",
        "",
        "| Candidate | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Frozen Stage-2 parent | {pm['sum_abs_error']:.6f} | {pm['mae']:.6f} | {pm['rmse']:.6f} | {pm['mape_pct']:.4f}% | {pm['relative_mae_vs_rw']:.6f} | {pm['direction_correct']}/33 |",
        f"| Stage-3A coarse | {cm['sum_abs_error']:.6f} | {cm['mae']:.6f} | {cm['rmse']:.6f} | {cm['mape_pct']:.4f}% | {cm['relative_mae_vs_rw']:.6f} | {cm['direction_correct']}/33 |",
        f"| Stage-3B local | {lm['sum_abs_error']:.6f} | {lm['mae']:.6f} | {lm['rmse']:.6f} | {lm['mape_pct']:.4f}% | {lm['relative_mae_vs_rw']:.6f} | {lm['direction_correct']}/33 |",
        "",
        f"Promotion rule: Stage-3B SigmaAE < {PARENT_REF:.6f}.",
        f"Decision: **{'PROMOTED' if promoted else 'NOT PROMOTED'}**.",
        "",
        "## Frequent Stage-3B selections",
        "",
        "| log2(C) | log2(gamma) | epsilon | Origins |",
        "|---:|---:|---:|---:|",
    ]
    for z in out["selection_frequency"][:12]:
        lines.append(f"| {z['log2_C']} | {z['log2_gamma']} | {z['epsilon']:.3f} | {z['count']} |")
    lines += [
        "",
        "## Stage-3 closure",
        f"- Final deterministic SVR reference: **{out['decision']['final_deterministic_reference']}**.",
        "- Continuous Stage-4 metaheuristic bounds must be frozen next.",
        "- 32/32 Stage-4 screen remains mandatory.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Stage-3B freeze respected: PASS.",
        "- Local neighborhoods derived only from Stage-3A coarse centers: PASS.",
        "- Inner chronology/scaling unchanged: PASS.",
        "- Parent and Stage-3A reconciliation: PASS.",
        "- Determinism: PASS.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        f"- Payload SHA256: {out['determinism']['payload_sha256']}",
        "",
    ]
    return "\n".join(lines)

def run_once(bundle):
    local=local_rows(bundle); parent=parent_rows(bundle); coarse=coarse_rows(bundle)
    return local,parent,coarse,stable_hash(local,parent,coarse)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    local,parent,coarse,h1=run_once(b)
    local2,parent2,coarse2,h2=run_once(b)
    if h1!=h2: raise RuntimeError(f"DETERMINISM_FAIL {h1} {h2}")

    pm=s1.metrics(parent); cm=s1.metrics(coarse); lm=s1.metrics(local)
    if abs(pm["sum_abs_error"]-PARENT_REF)>1e-5:
        raise RuntimeError("PARENT_RECONCILE_FAIL")
    if abs(cm["sum_abs_error"]-1580.901050)>1e-5:
        raise RuntimeError("COARSE_RECONCILE_FAIL")

    expected=list(base.month_range(DEV_START,DEV_END))
    if [r["target"] for r in local]!=expected:
        raise RuntimeError("TARGET_ALIGNMENT_FAIL")
    for r in local:
        if r["train_last"]>=r["target"]: raise RuntimeError(f"CHRONOLOGY_FAIL {r['target']}")
        ce=r["coarse_center"]["log2_C"]; ge=r["coarse_center"]["log2_gamma"]; ep=float(r["coarse_center"]["epsilon"])
        if r["selected"]["log2_C"] not in sorted(set(max(-8,min(12,ce+d)) for d in (-2,0,2))):
            raise RuntimeError("LOCAL_C_FAIL")
        if r["selected"]["log2_gamma"] not in sorted(set(max(-12,min(4,ge+d)) for d in (-2,0,2))):
            raise RuntimeError("LOCAL_G_FAIL")
        if float(r["selected"]["epsilon"]) not in EPS_LOCAL[ep]:
            raise RuntimeError("LOCAL_EPS_FAIL")

    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    promoted=bool(lm["sum_abs_error"]<PARENT_REF)
    final_ref="STAGE3B_LOCAL_TUNED" if promoted else "EPSILON_RBF_DAILY12_STAGE2_PARENT"
    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE3B_LOCAL_REFINEMENT_DEV_ONLY_V1",
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE3B_LOCAL_FREEZE_2026-09-28.md",
        "contract":{"parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
                    "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED",
                    "2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY"},
        "local_rule":{"C_log2_offsets":[-2,0,2],"gamma_log2_offsets":[-2,0,2],"epsilon_map":{str(k):list(v) for k,v in EPS_LOCAL.items()}},
        "parent":{"metrics":pm,"yearly":s1.yearly(parent),"rows":parent},
        "coarse":{"metrics":cm,"yearly":s1.yearly(coarse),"rows":coarse},
        "local":{"metrics":lm,"yearly":s1.yearly(local),"rows":local},
        "selection_frequency":freq(local),
        "decision":{"promotion_threshold_sum_abs_error":PARENT_REF,"promoted":promoted,
                    "final_deterministic_reference":final_ref},
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
        "determinism":{"status":"PASS","payload_sha256":h1},
    }
    Path("gold_monthly_svr_dwt_stage3b_local_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE3B_LOCAL_RESULT_2026-09-28.md").write_text(md(out),encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"parent":pm,"coarse":cm,"local":lm,"decision":out["decision"],"selection_frequency":out["selection_frequency"][:12],"payload_sha256":h1},sort_keys=True))

if __name__=="__main__":
    main()
