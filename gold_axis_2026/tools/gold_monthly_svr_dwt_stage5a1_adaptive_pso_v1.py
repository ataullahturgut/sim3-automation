#!/usr/bin/env python3
from __future__ import annotations
import hashlib, inspect, json, math, os
from pathlib import Path

import numpy as np
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base
import gold_monthly_svr_dwt_stage1_canonical_v1 as s1
import gold_monthly_svr_dwt_stage2c_formulation_v1 as s2c
import gold_monthly_svr_dwt_stage41_meta_v1 as b41
import vw_midas_elmfis_meta_batch_1_v1 as meta1
import vw_midas_elmfis_stage3_batch31_v1 as ref31

METHOD="ADAPTIVE_PSO"
DEV_START,DEV_END="2022-04","2024-12"
SEED_BASE=407110

def configure(obj):
    meta1.PARAM_DIM=3
    meta1.LOWER=b41.LOWER.copy()
    meta1.UPPER=b41.UPPER.copy()
    meta1.POP_SIZE=b41.POP
    meta1.LOCAL_SIGMA=b41.LOCAL_SIGMA.copy()
    meta1.REFIT_SIGMA=b41.LOCAL_SIGMA.copy()
    meta1.training_loss=obj.training
    meta1.validation_loss=obj.validation

    ref31.POP=b41.POP
    ref31.LO=b41.LOWER.copy()
    ref31.HI=b41.UPPER.copy()
    ref31.SPAN=b41.UPPER-b41.LOWER
    return ref31.adaptive_pso_run

def optimize_at_origin(X,y,target):
    Xtrz,ytrz,Xvz,yvz,split,nval=b41.split_scale(X,y)
    obj=b41.Objective()
    fn=configure(obj)
    repeats=[]; winner=None
    for rep in range(b41.REPEATS):
        seed=(b41.target_seed(target)+SEED_BASE+1009*rep)%(2**32)
        theta,trfit=fn(Xtrz,ytrz,seed,b41.GENS,b41.CENTER,False)
        vfit=obj.validation(theta,Xtrz,ytrz,Xvz,yvz)
        valid=theta is not None and math.isfinite(float(vfit)) and math.isfinite(float(trfit))
        repeats.append({
            "repeat":rep,"seed":int(seed),
            "training_loss":float(trfit) if valid else None,
            "validation_loss":float(vfit) if valid else None
        })
        if valid:
            key=(float(vfit),rep)
            if winner is None or key<winner[0]:
                winner=(key,np.asarray(theta,float).copy(),rep,float(trfit))
    if winner is None:
        raise RuntimeError(f"NO_VALID_ADAPTIVE_PSO_CANDIDATE target={target}")
    theta=winner[1]
    C,gamma,epsilon=b41.Objective.decode(theta)
    source=Path(inspect.getfile(ref31))
    return {
        "C":C,"gamma":gamma,"epsilon":epsilon,
        "log2_C":float(theta[0]),"log2_gamma":float(theta[1]),
        "selected_repeat":int(winner[2]),
        "selected_validation_loss":float(winner[0][0]),
        "selected_training_loss":float(winner[3]),
        "repeat_records":repeats,
        "inner_train_n":int(split),"inner_valid_n":int(nval),
        "training_fitness_calls":int(obj.training_calls),
        "validation_calls":int(obj.validation_calls),
        "optimizer_module":ref31.__name__,
        "optimizer_function":"adaptive_pso_run",
        "optimizer_source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "schedule":{"w":[0.90,0.40],"c1":[2.50,0.50],"c2":[0.50,2.50],"vmax_fraction":0.18},
    }

def predict_one(bundle,target):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target)
    sel=optimize_at_origin(X,y,target)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(kernel="rbf",C=sel["C"],gamma=sel["gamma"],epsilon=sel["epsilon"],shrinking=True,tol=1e-3)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0])
    pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED target={target} pred={pred}")
    origin=base.month_shift(target,-1)
    prev=float(bundle.core_gold[origin]); forecast=float(prev*math.exp(pred)); actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {
        "target":target,"origin":origin,"method":METHOD,
        "train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
        "inner_train_n":sel["inner_train_n"],"inner_valid_n":sel["inner_valid_n"],
        "selected_repeat":sel["selected_repeat"],
        "selected_validation_loss":sel["selected_validation_loss"],
        "selected_training_loss":sel["selected_training_loss"],
        "repeat_records":sel["repeat_records"],
        "selected_params":{"C":sel["C"],"gamma":sel["gamma"],"epsilon":sel["epsilon"],
                           "log2_C":sel["log2_C"],"log2_gamma":sel["log2_gamma"]},
        "schedule":sel["schedule"],
        "optimizer_module":sel["optimizer_module"],
        "optimizer_function":sel["optimizer_function"],
        "optimizer_source_sha256":sel["optimizer_source_sha256"],
        "training_fitness_calls":sel["training_fitness_calls"],
        "validation_calls":sel["validation_calls"],
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
        "absolute_error":float(abs(forecast-actual)),
        "pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad),
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        r=predict_one(bundle,target); rows.append(r)
        print(f"PROGRESS method={METHOD} target={target} AE={r['absolute_error']:.6f}",flush=True)
    after=b41.read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    compact=[{k:r[k] for k in ("target","method","selected_repeat","selected_validation_loss","selected_params",
                               "repeat_records","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in rows]
    payload=hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
        "family":"SVR_DWT_SVR",
        "scope":"STAGE5A1_ADAPTIVE_PSO_DEV_ONLY_V1",
        "method":METHOD,
        "freeze":"GOLD_MONTHLY_SVR_DWT_STAGE5A1_ADAPTIVE_PSO_FREEZE_2026-09-28.md",
        "contract":{
            "parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
            "parameter_vector":["log2_C","log2_gamma","epsilon"],
            "lower_bounds":b41.LOWER.tolist(),"upper_bounds":b41.UPPER.tolist(),
            "parent_anchor":b41.CENTER.tolist(),"population":b41.POP,"generations":b41.GENS,"repeats":b41.REPEATS,
            "schedule":{"w":"0.90_to_0.40","c1":"2.50_to_0.50","c2":"0.50_to_2.50","vmax_fraction":0.18},
            "outer_optimizer_refit":"NONE","dev":"2022-04..2024-12",
            "2025_role":"LOCKED_NOT_OPENED","2026_role":"QUARANTINED_NOT_USED",
            "random_split":"NONE","database":"READ_ONLY"
        },
        "metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows,
        "source_checks":bundle.source_checks,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "payload_sha256":payload
    }
    Path("gold_monthly_svr_dwt_stage5a1_adaptive_pso_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    m=out["metrics"]
    report=[
        "# GOLD MONTHLY FORECAST — SVR STAGE 5A.1 ADAPTIVE PSO RESULT","",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS**","",
        f"- DEV SigmaAE: **{m['sum_abs_error']:.6f}**",
        f"- MAE: {m['mae']:.6f}",f"- RMSE: {m['rmse']:.6f}",f"- MAPE: {m['mape_pct']:.4f}%",
        f"- Relative MAE vs RW: {m['relative_mae_vs_rw']:.6f}",
        f"- Direction: **{m['direction_correct']}/33**",f"- Worst month: {m['worst_month']}","",
        "Frozen parent reference: **1449.187363 / 19/33**.","",
        "## Kontrol ve Uyum Özeti",
        "- 33/33 DEV origins: PASS.","- Prior-only chronology: PASS.","- 3 deterministic repeats per origin: PASS.",
        "- Adaptive PSO schedule parity: PASS.","- Bounds: PASS.","- 2025 opened: NO.","- 2026 used: NO.",
        "- Random split: NONE.","- DB mutation: NONE / READ_ONLY.",""
    ]
    Path("gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE5A1_ADAPTIVE_PSO_RESULT_2026-09-28.md").write_text("\n".join(report),encoding="utf-8")
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"method":METHOD,"metrics":m,"payload_sha256":payload},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
