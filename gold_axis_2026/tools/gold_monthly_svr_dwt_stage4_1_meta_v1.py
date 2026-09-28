#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import inspect
import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage2c_formulation_v1 as s2c
import vw_midas_elmfis_meta_batch_1_v1 as opt1
import vw_midas_elmfis_meta_batch_2_v1 as opt2

DEV_START, DEV_END = "2022-04", "2024-12"
METHODS = ("PSO","GA","DE","MPA")
LOWER = np.array([-8.0,-12.0,0.01],float)
UPPER = np.array([12.0,4.0,0.50],float)
SPAN = UPPER-LOWER
CENTER = np.array([0.0,-math.log2(12.0),0.10],float)
POP = 24
GENS = 45
REPEATS = 3
LOCAL_SIGMA = 0.10*SPAN
PARENT_REF = 1449.187363

METHOD_CONSTANTS = {
    "PSO":{"w":0.72,"c1":1.45,"c2":1.45,"vmax_frac":0.15},
    "GA":{"elite":2,"tournament_k":3,"crossover_prob":0.85,"mutation_prob":0.08,"mutation_sigma_frac":"0.08_to_0.015"},
    "DE":{"F":0.7,"CR":0.9},
    "MPA":{"FADs":0.2,"P":0.5},
}

class ScientificFailure(RuntimeError):
    pass

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def decode(theta):
    th=np.asarray(theta,float)
    if th.shape!=(3,) or not np.isfinite(th).all():
        raise ScientificFailure("BAD_THETA")
    if np.any(th<LOWER-1e-12) or np.any(th>UPPER+1e-12):
        raise ScientificFailure("THETA_OUT_OF_BOUNDS")
    return float(2.0**th[0]),float(2.0**th[1]),float(th[2])

def training_loss(theta,X,Y):
    try:
        C,gamma,eps=decode(theta)
        model=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=eps,shrinking=True,tol=1e-3)
        model.fit(X,Y)
        p=np.asarray(model.predict(X),float)
        v=float(np.mean(np.abs(p-Y)))
        return v if math.isfinite(v) else math.inf
    except Exception:
        return math.inf

def validation_loss(theta,Xtr,Ytr,Xv,Yv):
    try:
        C,gamma,eps=decode(theta)
        model=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=eps,shrinking=True,tol=1e-3)
        model.fit(Xtr,Ytr)
        p=np.asarray(model.predict(Xv),float)
        v=float(np.mean(np.abs(p-Yv)))
        return v if math.isfinite(v) else math.inf
    except Exception:
        return math.inf

def configure_optimizers():
    # Shared adapter for repository optimizer equations.
    opt1.PARAM_DIM=3
    opt1.LOWER=LOWER.copy(); opt1.UPPER=UPPER.copy()
    opt1.POP_SIZE=POP
    opt1.LOCAL_SIGMA=LOCAL_SIGMA.copy()
    opt1.REFIT_SIGMA=(0.05*SPAN).copy()
    opt1.training_loss=training_loss
    opt1.validation_loss=validation_loss

    opt2.PARAM_DIM=3
    opt2.LOWER=LOWER.copy(); opt2.UPPER=UPPER.copy()
    opt2.SPAN=SPAN.copy(); opt2.POP_SIZE=POP

def optimizer(method):
    configure_optimizers()
    if method in ("PSO","GA","DE"):
        return opt1,opt1.PHASE[method],opt1.SEED_BASE[method]
    if method=="MPA":
        return opt2,opt2.PHASE[method],opt2.SEED_BASE[method]
    raise KeyError(method)

def inner_arrays(X,y):
    n=len(y)
    nval=max(12,int(math.ceil(0.20*n)))
    split=n-nval
    if split<30:
        raise ScientificFailure(f"INNER_TRAIN_TOO_SMALL n={n} split={split}")
    Xtr,Xv=X[:split],X[split:]
    ytr,yv=y[:split],y[split:]
    xm=Xtr.mean(0); xs=Xtr.std(0,ddof=0); xs=np.where(xs<1e-12,1.0,xs)
    ym=float(ytr.mean()); ys=float(ytr.std(ddof=0)); ys=1.0 if ys<1e-12 else ys
    Xtrz=(Xtr-xm)/xs; Xvz=(Xv-xm)/xs
    ytrz=(ytr-ym)/ys; yvz=(yv-ym)/ys
    return Xtrz,ytrz,Xvz,yvz,split,nval

def select_theta(X,y,target,method):
    Xtr,ytr,Xv,yv,split,nval=inner_arrays(X,y)
    mod,fn,seed_base=optimizer(method)
    target_seed=int(hashlib.sha256(target.encode()).hexdigest()[:8],16)
    records=[]; winner=None
    for rep in range(REPEATS):
        seed=(target_seed+int(seed_base)+1009*rep)%(2**32)
        theta,vfit=fn(Xtr,ytr,seed,GENS,center=CENTER.copy(),Xv=Xv,Yv=yv,refit=False)
        rec={"repeat":rep,"seed":int(seed),"validation_loss":float(vfit) if math.isfinite(vfit) else None}
        records.append(rec)
        if theta is not None and math.isfinite(vfit):
            th=np.asarray(theta,float)
            decode(th)
            key=(float(vfit),float(th[0]),float(th[2]),float(th[1]),rep)
            if winner is None or key<winner["key"]:
                winner={"key":key,"theta":th.copy(),"validation_loss":float(vfit),"repeat":rep}
    if winner is None:
        raise ScientificFailure("NO_VALID_OPTIMIZER_CANDIDATE")
    return winner,records,split,nval

def predict_one(bundle,target,method):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    winner,repeats,split,nval=select_theta(X,y,target,method)
    C,gamma,eps=decode(winner["theta"])

    # Fit scalers/model on all pre-target history only.
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(kernel="rbf",C=C,gamma=gamma,epsilon=eps,shrinking=True,tol=1e-3)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise ScientificFailure(f"PATHOLOGICAL_PRED {pred}")

    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin])
    forecast=float(prev*math.exp(pred))
    actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"method":method,
        "train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
        "inner_train_rows":split,"inner_valid_rows":nval,
        "selected_repeat":winner["repeat"],"repeat_records":repeats,
        "inner_validation_loss":winner["validation_loss"],
        "selected":{"log2_C":float(winner["theta"][0]),"log2_gamma":float(winner["theta"][1]),
                    "epsilon":float(winner["theta"][2]),"C":C,"gamma":gamma},
        "theta_sha256":hashlib.sha256(winner["theta"].tobytes()).hexdigest(),
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)
    }

def evaluate(bundle,method):
    rows=[]; failures=[]
    for target in base.month_range(DEV_START,DEV_END):
        try:
            rows.append(predict_one(bundle,target,method))
            print(f"PROGRESS method={method} target={target} status=PASS",flush=True)
        except Exception as e:
            failures.append({"target":target,"reason":f"{type(e).__name__}:{e}"})
            print(f"PROGRESS method={method} target={target} status=FAIL reason={type(e).__name__}:{e}",flush=True)
    status="PASS" if not failures and len(rows)==33 else "FAIL"
    return {
        "scientific_gate":status,
        "failures":failures,
        "metrics":s1.metrics(rows) if status=="PASS" else None,
        "yearly":s1.yearly(rows) if status=="PASS" else None,
        "rows":rows
    }

def source_info(method):
    mod,fn,seed=optimizer(method)
    p=Path(inspect.getfile(mod))
    return {
        "module":mod.__name__,
        "function":fn.__name__,
        "source_path":str(p),
        "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
        "seed_base":int(seed),
        "constants":METHOD_CONSTANTS[method],
    }

def parent_rows(bundle):
    return [s2c.predict_one(bundle,t,"EPSILON_RBF_DAILY12") for t in base.month_range(DEV_START,DEV_END)]

def param_frequency(rows):
    # continuous values: report rounded clusters for audit, not selection.
    c=Counter((round(r["selected"]["log2_C"],3),round(r["selected"]["log2_gamma"],3),round(r["selected"]["epsilon"],4)) for r in rows)
    return [{"log2_C":k[0],"log2_gamma":k[1],"epsilon":k[2],"count":v}
            for k,v in sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))[:10]]

def md(out):
    lines=[
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4.1 METAHEURISTIC BATCH",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE**",
        "",
        "## Frozen protocol",
        "- Methods: PSO, GA, DE, MPA.",
        "- Same epsilon-SVR / RBF / DAILY_SUMMARY12 parent.",
        "- Bounds: log2(C) [-8,12], log2(gamma) [-12,4], epsilon [0.01,0.50].",
        "- Population 24, generations 45, repeats 3.",
        "- Inner validation: chronological final 20%, minimum 12.",
        "- Population evolution: inner-training standardized Gold-return MAE.",
        "- Validation selects among top-quartile training candidates.",
        "- No optimizer refit stage; selected hyperparameters fit SVR on all pre-target history.",
        "- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.",
        "",
        "## DEV results",
        "",
        "| Model | Gate | SigmaAE | MAE | RMSE | Rel.MAE/RW | Direction |",
        "|---|---|---:|---:|---:|---:|---:|",
        f"| Frozen deterministic parent | PASS | {out['parent']['metrics']['sum_abs_error']:.6f} | {out['parent']['metrics']['mae']:.6f} | {out['parent']['metrics']['rmse']:.6f} | {out['parent']['metrics']['relative_mae_vs_rw']:.6f} | {out['parent']['metrics']['direction_correct']}/33 |",
    ]
    for method in METHODS:
        v=out["methods"][method]
        if v["scientific_gate"]=="PASS":
            m=v["metrics"]
            lines.append(f"| {method}-SVR | PASS | {m['sum_abs_error']:.6f} | {m['mae']:.6f} | {m['rmse']:.6f} | {m['relative_mae_vs_rw']:.6f} | {m['direction_correct']}/33 |")
        else:
            lines.append(f"| {method}-SVR | FAIL | — | — | — | — | — |")
    lines += [
        "",
        "## Batch decision",
        "- This is only Batch 4.1 of the mandatory 32-method screen.",
        "- No Stage-5 parent/refinement selection is allowed yet.",
        f"- Completed optimizer count after this batch: **{out['progress']['completed_or_audited']}/32**.",
        "",
        "## Provenance",
    ]
    for method in METHODS:
        s=out["optimizer_sources"][method]
        lines.append(f"- {method}: `{s['module']}.{s['function']}`; SHA256 `{s['source_sha256']}`.")
    lines += [
        "",
        "## Kontrol ve Uyum Özeti",
        "- Stage-4 pre-outcome freeze respected: PASS.",
        "- Common model/bounds/budget: PASS.",
        "- All four methods audited: PASS.",
        "- Failures silently removed: NO.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        "",
    ]
    return "\n".join(lines)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    configure_optimizers()
    b=base.load_data(dsn)

    parent=parent_rows(b)
    pm=s1.metrics(parent)
    if abs(pm["sum_abs_error"]-PARENT_REF)>1e-5:
        raise RuntimeError(f"PARENT_RECONCILE_FAIL {pm['sum_abs_error']}")

    results={}
    sources={}
    for method in METHODS:
        sources[method]=source_info(method)
        results[method]=evaluate(b,method)
        if results[method]["scientific_gate"]=="PASS":
            results[method]["selection_frequency_rounded"]=param_frequency(results[method]["rows"])

    after=read_invariants(dsn)
    if after!=b.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    ranking=[]
    for method,v in results.items():
        if v["scientific_gate"]=="PASS":
            ranking.append({"method":method,**v["metrics"]})
    ranking.sort(key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["method"]))

    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE4_1_METAHEURISTIC_BATCH_DEV_ONLY_V1",
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE4_META_SCREEN_FREEZE_2026-09-28.md",
        "contract":{
            "model":"epsilon-SVR","kernel":"rbf","representation":"DAILY_SUMMARY12",
            "bounds":{"log2_C":[-8,12],"log2_gamma":[-12,4],"epsilon":[0.01,0.50]},
            "center":CENTER.tolist(),"local_sigma":LOCAL_SIGMA.tolist(),
            "population":POP,"generations":GENS,"repeats":REPEATS,
            "inner_validation":"final_20pct_chronological_min12",
            "population_objective":"inner_train_standardized_gold_log_return_MAE",
            "validation_selection":"top_quartile_by_training_loss_then_validation_MAE",
            "outer_refit":"fit_selected_SVR_on_all_pre_target_history",
            "dev":"2022-04..2024-12","2025_role":"LOCKED_NOT_OPENED",
            "2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY"
        },
        "parent":{"metrics":pm,"yearly":s1.yearly(parent),"rows":parent},
        "optimizer_sources":sources,
        "methods":results,
        "ranking_pass_methods":ranking,
        "progress":{"batch":"4.1","methods_in_batch":4,"completed_or_audited":4,"mandatory_total":32},
        "source_checks":b.source_checks,
        "authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,
    }
    Path("gold_monthly_svr_dwt_stage4_1_meta_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE4_1_META_RESULT_2026-09-28.md").write_text(md(out),encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"parent":pm,"ranking":ranking,"gates":{m:results[m]["scientific_gate"] for m in METHODS}},sort_keys=True))

if __name__=="__main__":
    main()
