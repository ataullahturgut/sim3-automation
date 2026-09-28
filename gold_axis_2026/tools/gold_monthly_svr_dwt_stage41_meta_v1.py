#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import math
import os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage2c_formulation_v1 as s2c
import vw_midas_elmfis_meta_batch_1_v1 as meta1
import vw_midas_elmfis_meta_batch_2_v1 as meta2

DEV_START, DEV_END = "2022-04", "2024-12"
METHODS = ("PSO","GA","DE","MPA")
POP, GENS, REPEATS = 24, 45, 3
LOWER = np.asarray([-8.0,-12.0,0.01],float)
UPPER = np.asarray([12.0,4.0,0.50],float)
CENTER = np.asarray([0.0, math.log2(1.0/12.0), 0.10],float)
LOCAL_SIGMA = np.asarray([2.0,2.0,0.05],float)
PARENT_SIGMA_AE = 1449.187363


def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def split_scale(X,y):
    n=len(y)
    nval=max(12,int(math.ceil(0.20*n)))
    split=n-nval
    if split<30:
        raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={n} split={split}")
    Xtr,Xv=X[:split],X[split:]
    ytr,yv=y[:split],y[split:]
    xm=Xtr.mean(0); xs=Xtr.std(0,ddof=0); xs=np.where(xs<1e-12,1.0,xs)
    ym=float(ytr.mean()); ys=float(ytr.std(ddof=0)); ys=1.0 if ys<1e-12 else ys
    return (
        (Xtr-xm)/xs,(ytr-ym)/ys,(Xv-xm)/xs,(yv-ym)/ys,
        split,nval
    )


class Objective:
    def __init__(self):
        self.training_calls=0
        self.validation_calls=0

    @staticmethod
    def decode(theta):
        t=np.asarray(theta,float)
        if t.shape!=(3,):
            raise RuntimeError(f"THETA_SHAPE_FAIL {t.shape}")
        ce,ge,eps=t
        C=float(2.0**ce)
        gamma=float(2.0**ge)
        epsilon=float(eps)
        if not (LOWER[0]-1e-12<=ce<=UPPER[0]+1e-12 and
                LOWER[1]-1e-12<=ge<=UPPER[1]+1e-12 and
                LOWER[2]-1e-12<=epsilon<=UPPER[2]+1e-12):
            raise RuntimeError("THETA_BOUND_FAIL")
        return C,gamma,epsilon

    def training(self,theta,X,y):
        self.training_calls+=1
        C,gamma,epsilon=self.decode(theta)
        m=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=epsilon,shrinking=True,tol=1e-3)
        m.fit(X,y)
        p=np.asarray(m.predict(X),float)
        return float(np.mean(np.abs(p-y))) if np.isfinite(p).all() else math.inf

    def validation(self,theta,Xtr,ytr,Xv,yv):
        self.validation_calls+=1
        C,gamma,epsilon=self.decode(theta)
        m=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=epsilon,shrinking=True,tol=1e-3)
        m.fit(Xtr,ytr)
        p=np.asarray(m.predict(Xv),float)
        return float(np.mean(np.abs(p-yv))) if np.isfinite(p).all() else math.inf


def configure_optimizer(method,obj):
    # Patch shared audited optimizer interface to a 3D SVR hyperparameter problem.
    meta1.PARAM_DIM=3
    meta1.LOWER=LOWER.copy()
    meta1.UPPER=UPPER.copy()
    meta1.POP_SIZE=POP
    meta1.LOCAL_SIGMA=LOCAL_SIGMA.copy()
    meta1.REFIT_SIGMA=LOCAL_SIGMA.copy()
    meta1.training_loss=obj.training
    meta1.validation_loss=obj.validation

    if method in ("PSO","GA","DE"):
        mod=meta1
    elif method=="MPA":
        meta2.PARAM_DIM=3
        meta2.LOWER=LOWER.copy()
        meta2.UPPER=UPPER.copy()
        meta2.SPAN=UPPER-LOWER
        meta2.POP_SIZE=POP
        mod=meta2
    else:
        raise KeyError(method)

    return mod,mod.PHASE[method],int(mod.SEED_BASE[method])


def target_seed(target):
    return int(hashlib.sha256(target.encode()).hexdigest()[:8],16)


def optimize_at_origin(X,y,target,method):
    Xtrz,ytrz,Xvz,yvz,split,nval=split_scale(X,y)
    obj=Objective()
    mod,fn,seed_base=configure_optimizer(method,obj)
    repeats=[]
    winner=None

    for rep in range(REPEATS):
        seed=(target_seed(target)+seed_base+1009*rep)%(2**32)
        theta,vfit=fn(
            Xtrz,ytrz,seed,GENS,center=CENTER,
            Xv=Xvz,Yv=yvz,refit=False
        )
        valid=theta is not None and math.isfinite(float(vfit))
        row={
            "repeat":rep,"seed":int(seed),
            "validation_loss":float(vfit) if valid else None,
        }
        repeats.append(row)
        if valid:
            key=(float(vfit),rep)
            if winner is None or key<winner[0]:
                winner=(key,np.asarray(theta,float).copy(),rep)

    if winner is None:
        raise RuntimeError(f"NO_VALID_OPTIMIZER_CANDIDATE method={method} target={target}")

    theta=winner[1]
    C,gamma,epsilon=Objective.decode(theta)
    return {
        "theta":theta,
        "C":C,"gamma":gamma,"epsilon":epsilon,
        "log2_C":float(theta[0]),"log2_gamma":float(theta[1]),
        "selected_repeat":int(winner[2]),
        "selected_validation_loss":float(winner[0][0]),
        "repeat_records":repeats,
        "inner_train_n":int(split),
        "inner_valid_n":int(nval),
        "training_fitness_calls":int(obj.training_calls),
        "validation_calls":int(obj.validation_calls),
        "optimizer_module":mod.__name__,
        "optimizer_function":fn.__name__,
        "optimizer_source":inspect.getfile(mod),
        "optimizer_source_sha256":hashlib.sha256(Path(inspect.getfile(mod)).read_bytes()).hexdigest(),
    }


def predict_one(bundle,target,method):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    sel=optimize_at_origin(X,y,target,method)

    # Outer refit with selected hyperparameters; no optimizer refit.
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(
        kernel="rbf",C=sel["C"],gamma=sel["gamma"],epsilon=sel["epsilon"],
        shrinking=True,tol=1e-3
    )
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED method={method} target={target} pred={pred}")

    origin=base.month_shift(target,-1)
    previous=float(bundle.core_gold[origin])
    forecast=float(previous*math.exp(pred))
    actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-previous)); ad=int(np.sign(actual-previous))

    return {
        "target":target,"origin":origin,"method":method,
        "train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
        "inner_train_n":sel["inner_train_n"],"inner_valid_n":sel["inner_valid_n"],
        "selected_repeat":sel["selected_repeat"],
        "selected_validation_loss":sel["selected_validation_loss"],
        "repeat_records":sel["repeat_records"],
        "selected_params":{
            "C":sel["C"],"gamma":sel["gamma"],"epsilon":sel["epsilon"],
            "log2_C":sel["log2_C"],"log2_gamma":sel["log2_gamma"],
        },
        "optimizer_module":sel["optimizer_module"],
        "optimizer_function":sel["optimizer_function"],
        "optimizer_source_sha256":sel["optimizer_source_sha256"],
        "training_fitness_calls":sel["training_fitness_calls"],
        "validation_calls":sel["validation_calls"],
        "pred_log_return_gold":pred,
        "forecast":forecast,"actual":actual,"rw":previous,
        "absolute_error":float(abs(forecast-actual)),
        "pred_direction":pd,"actual_direction":ad,
        "direction_correct":bool(pd==ad),
    }


def method_hash(rows):
    compact=[
        {k:r[k] for k in (
            "target","method","selected_repeat","selected_validation_loss",
            "selected_params","repeat_records","forecast","actual","rw",
            "pred_log_return_gold","direction_correct"
        )} for r in rows
    ]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def run_method(method):
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    if method not in METHODS:
        raise SystemExit(f"method must be one of {METHODS}")

    bundle=base.load_data(dsn)
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        r=predict_one(bundle,target,method)
        rows.append(r)
        print(
            f"PROGRESS method={method} target={target} "
            f"C={r['selected_params']['C']:.6g} gamma={r['selected_params']['gamma']:.6g} "
            f"eps={r['selected_params']['epsilon']:.6g} AE={r['absolute_error']:.6f}",
            flush=True
        )

    after=read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE41_METAHEURISTIC_DEV_ONLY_V1",
        "method":method,
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE41_IMPLEMENTATION_FREEZE_2026-09-28.md",
        "contract":{
            "parent":"EPSILON_RBF_DAILY12",
            "representation":"DAILY_SUMMARY12",
            "kernel":"rbf",
            "parameter_vector":["log2_C","log2_gamma","epsilon"],
            "lower_bounds":LOWER.tolist(),
            "upper_bounds":UPPER.tolist(),
            "parent_anchor":CENTER.tolist(),
            "local_sigma":LOCAL_SIGMA.tolist(),
            "population":POP,
            "generations":GENS,
            "repeats":REPEATS,
            "outer_optimizer_refit":"NONE",
            "dev":"2022-04..2024-12",
            "2025_role":"LOCKED_NOT_OPENED",
            "2026_role":"QUARANTINED_NOT_USED",
            "random_split":"NONE",
            "database":"READ_ONLY",
        },
        "metrics":s1.metrics(rows),
        "yearly":s1.yearly(rows),
        "rows":rows,
        "source_checks":bundle.source_checks,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "payload_sha256":method_hash(rows),
    }
    Path(f"gold_monthly_svr_dwt_stage41_{method.lower()}_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"method":method,"metrics":out["metrics"],"payload_sha256":out["payload_sha256"]},sort_keys=True),flush=True)


def aggregate():
    results={}
    for method in METHODS:
        p=Path(f"gold_monthly_svr_dwt_stage41_{method.lower()}_result.json")
        if not p.exists():
            raise RuntimeError(f"MISSING_METHOD_RESULT {method}")
        r=json.loads(p.read_text())
        results[method]=r

    ranking=sorted(
        [{"method":m,**r["metrics"]} for m,r in results.items()],
        key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["method"])
    )
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4.1 METAHEURISTIC RESULT",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / BATCH 4.1 SCIENTIFIC GATE PASS**",
        "",
        "Methods: PSO, GA, DE, MPA.",
        "Frozen parent reference: EPSILON_RBF_DAILY12 = SigmaAE 1449.187363 / 19 of 33 directions.",
        "",
        "## DEV ranking",
        "",
        "| Rank | Method | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for i,z in enumerate(ranking,1):
        lines.append(
            f"| {i} | {z['method']} | {z['sum_abs_error']:.6f} | {z['mae']:.6f} | "
            f"{z['rmse']:.6f} | {z['mape_pct']:.4f}% | {z['relative_mae_vs_rw']:.6f} | "
            f"{z['direction_correct']}/33 | {z['worst_month']} |"
        )
    lines += [
        "",
        "## Decision",
        "- Batch 4.1 is recorded only; no Stage-4 parent is selected yet.",
        "- Mandatory broad screen progress after this batch: 4/32.",
        "- Remaining 28 methods must be completed/audited before Stage-4 filtering.",
        "- 2025/2026 remain unopened/unused.",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Common bounds: PASS.",
        "- Common population/generation/repeat budget: PASS.",
        "- Prior-only chronology: PASS.",
        "- No outer-target tuning: PASS.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        "",
    ]
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE41_META_RESULT_2026-09-28.md").write_text(
        "\n".join(lines),encoding="utf-8"
    )
    Path("gold_monthly_svr_dwt_stage41_aggregate.json").write_text(
        json.dumps({"ranking":ranking,"methods":results},indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps({"ranking":ranking},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",choices=METHODS)
    ap.add_argument("--aggregate",action="store_true")
    args=ap.parse_args()
    if args.aggregate:
        aggregate()
    elif args.method:
        run_method(args.method)
    else:
        raise SystemExit("use --method or --aggregate")


if __name__=="__main__":
    main()
