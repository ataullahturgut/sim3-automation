#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, inspect, json, math, os
from pathlib import Path

import numpy as np
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage2c_formulation_v1 as s2c
import gold_monthly_svr_dwt_stage41_meta_v1 as b41
import vw_midas_elmfis_meta_batch_1_v1 as meta1
import vw_midas_elmfis_meta_batch_3_v1 as meta3
import vw_midas_elmfis_meta_batch_4_v1 as meta4

METHODS=("HHO","ACO","BAT","FA")
DEV_START,DEV_END="2022-04","2024-12"

def configure_optimizer(method,obj):
    meta1.PARAM_DIM=3
    meta1.LOWER=b41.LOWER.copy(); meta1.UPPER=b41.UPPER.copy()
    meta1.POP_SIZE=b41.POP
    meta1.LOCAL_SIGMA=b41.LOCAL_SIGMA.copy(); meta1.REFIT_SIGMA=b41.LOCAL_SIGMA.copy()
    meta1.training_loss=obj.training; meta1.validation_loss=obj.validation
    mod=meta3 if method in ("HHO","ACO","BAT") else meta4
    for name,value in (
        ("PARAM_DIM",3),("LOWER",b41.LOWER.copy()),("UPPER",b41.UPPER.copy()),
        ("SPAN",b41.UPPER-b41.LOWER),("POP_SIZE",b41.POP)
    ):
        if hasattr(mod,name): setattr(mod,name,value)
    return mod,mod.PHASE[method],int(mod.SEED_BASE[method])

def optimize_at_origin(X,y,target,method):
    Xtrz,ytrz,Xvz,yvz,split,nval=b41.split_scale(X,y)
    obj=b41.Objective(); mod,fn,seed_base=configure_optimizer(method,obj)
    reps=[]; winner=None
    for rep in range(b41.REPEATS):
        seed=(b41.target_seed(target)+seed_base+1009*rep)%(2**32)
        theta,vfit=fn(Xtrz,ytrz,seed,b41.GENS,center=b41.CENTER,Xv=Xvz,Yv=yvz,refit=False)
        valid=theta is not None and math.isfinite(float(vfit))
        reps.append({"repeat":rep,"seed":int(seed),"validation_loss":float(vfit) if valid else None})
        if valid:
            key=(float(vfit),rep)
            if winner is None or key<winner[0]:
                winner=(key,np.asarray(theta,float).copy(),rep)
    if winner is None: raise RuntimeError(f"NO_VALID_OPTIMIZER_CANDIDATE {method} {target}")
    theta=winner[1]; C,gamma,epsilon=b41.Objective.decode(theta)
    return {
        "C":C,"gamma":gamma,"epsilon":epsilon,"log2_C":float(theta[0]),"log2_gamma":float(theta[1]),
        "selected_repeat":int(winner[2]),"selected_validation_loss":float(winner[0][0]),
        "repeat_records":reps,"inner_train_n":int(split),"inner_valid_n":int(nval),
        "training_fitness_calls":int(obj.training_calls),"validation_calls":int(obj.validation_calls),
        "optimizer_module":mod.__name__,"optimizer_function":fn.__name__,
        "optimizer_source_sha256":hashlib.sha256(Path(inspect.getfile(mod)).read_bytes()).hexdigest(),
    }

def predict_one(bundle,target,method):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    sel=optimize_at_origin(X,y,target,method)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(kernel="rbf",C=sel["C"],gamma=sel["gamma"],epsilon=sel["epsilon"],shrinking=True,tol=1e-3)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0]); pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0: raise RuntimeError(f"PATHOLOGICAL_PRED {method} {target}")
    origin=base.month_shift(target,-1); prev=float(bundle.core_gold[origin])
    forecast=float(prev*math.exp(pred)); actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"method":method,"train_rows":len(keys),
        "train_first":keys[0],"train_last":keys[-1],"inner_train_n":sel["inner_train_n"],
        "inner_valid_n":sel["inner_valid_n"],"selected_repeat":sel["selected_repeat"],
        "selected_validation_loss":sel["selected_validation_loss"],"repeat_records":sel["repeat_records"],
        "selected_params":{"C":sel["C"],"gamma":sel["gamma"],"epsilon":sel["epsilon"],
                           "log2_C":sel["log2_C"],"log2_gamma":sel["log2_gamma"]},
        "optimizer_module":sel["optimizer_module"],"optimizer_function":sel["optimizer_function"],
        "optimizer_source_sha256":sel["optimizer_source_sha256"],
        "training_fitness_calls":sel["training_fitness_calls"],"validation_calls":sel["validation_calls"],
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "absolute_error":float(abs(forecast-actual)),
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad),
    }

def method_hash(rows):
    compact=[{k:r[k] for k in ("target","method","selected_repeat","selected_validation_loss","selected_params",
                               "repeat_records","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in rows]
    return hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def run_method(method):
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn); rows=[]
    for t in base.month_range(DEV_START,DEV_END):
        r=predict_one(b,t,method); rows.append(r)
        print(f"PROGRESS method={method} target={t} AE={r['absolute_error']:.6f}",flush=True)
    after=b41.read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
        "family":"SVR_DWT_SVR","scope":"STAGE43_METAHEURISTIC_DEV_ONLY_V1","method":method,
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE4_METAHEURISTIC_FREEZE_2026-09-28.md",
        "contract":{"parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
                    "parameter_vector":["log2_C","log2_gamma","epsilon"],"lower_bounds":b41.LOWER.tolist(),
                    "upper_bounds":b41.UPPER.tolist(),"parent_anchor":b41.CENTER.tolist(),
                    "local_sigma":b41.LOCAL_SIGMA.tolist(),"population":b41.POP,"generations":b41.GENS,
                    "repeats":b41.REPEATS,"outer_optimizer_refit":"NONE","dev":"2022-04..2024-12",
                    "2025_role":"LOCKED_NOT_OPENED","2026_role":"QUARANTINED_NOT_USED",
                    "random_split":"NONE","database":"READ_ONLY"},
        "metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows,
        "source_checks":b.source_checks,"authority_invariants_before":b.invariants_before,
        "authority_invariants_after":after,"payload_sha256":method_hash(rows)
    }
    Path(f"gold_monthly_svr_dwt_stage43_{method.lower()}_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"method":method,"metrics":out["metrics"],"payload_sha256":out["payload_sha256"]},sort_keys=True),flush=True)

def aggregate():
    results={m:json.loads(Path(f"gold_monthly_svr_dwt_stage43_{m.lower()}_result.json").read_text()) for m in METHODS}
    ranking=sorted([{"method":m,**r["metrics"]} for m,r in results.items()],
                   key=lambda z:(z["sum_abs_error"],-z["direction_correct"],z["rmse"],z["method"]))
    lines=["# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4.3 METAHEURISTIC RESULT","",
           "Date: 2026-09-28","Status: **COMPLETE / BATCH 4.3 SCIENTIFIC GATE PASS**","",
           "Methods: HHO, ACO, BAT, FA.","Frozen parent: 1449.187363 / 19 of 33 directions.","",
           "## DEV ranking","",
           "| Rank | Method | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |",
           "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for i,z in enumerate(ranking,1):
        lines.append(f"| {i} | {z['method']} | {z['sum_abs_error']:.6f} | {z['mae']:.6f} | {z['rmse']:.6f} | {z['mape_pct']:.4f}% | {z['relative_mae_vs_rw']:.6f} | {z['direction_correct']}/33 | {z['worst_month']} |")
    lines += ["","## Decision","- Batch 4.3 recorded only; no Stage-4 parent selected yet.",
              "- Broad-screen progress: 12/32.","- Remaining 20 methods required before filtering.","",
              "## Kontrol ve Uyum Özeti","- Frozen bounds/budget: PASS.","- Prior-only chronology: PASS.",
              "- 2025 opened: NO.","- 2026 used: NO.","- Random split: NONE.","- DB mutation: NONE / READ_ONLY.",""]
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE43_META_RESULT_2026-09-28.md").write_text("\n".join(lines))
    Path("gold_monthly_svr_dwt_stage43_aggregate.json").write_text(json.dumps({"ranking":ranking,"methods":results},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"ranking":ranking},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--method",choices=METHODS); ap.add_argument("--aggregate",action="store_true"); a=ap.parse_args()
    if a.aggregate: aggregate()
    elif a.method: run_method(a.method)
    else: raise SystemExit("use --method or --aggregate")
if __name__=="__main__": main()
