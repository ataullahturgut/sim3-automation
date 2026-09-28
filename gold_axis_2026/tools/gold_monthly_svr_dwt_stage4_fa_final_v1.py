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
import vw_midas_elmfis_meta_batch_4_v1 as meta4

METHOD="FA"
DEV_START,DEV_END="2022-04","2024-12"

def configure(obj):
    meta1.PARAM_DIM=3
    meta1.LOWER=b41.LOWER.copy(); meta1.UPPER=b41.UPPER.copy()
    meta1.POP_SIZE=b41.POP; meta1.LOCAL_SIGMA=b41.LOCAL_SIGMA.copy(); meta1.REFIT_SIGMA=b41.LOCAL_SIGMA.copy()
    meta1.training_loss=obj.training; meta1.validation_loss=obj.validation
    for name,value in (("PARAM_DIM",3),("LOWER",b41.LOWER.copy()),("UPPER",b41.UPPER.copy()),("SPAN",b41.UPPER-b41.LOWER),("POP_SIZE",b41.POP)):
        if hasattr(meta4,name): setattr(meta4,name,value)
    return meta4.PHASE[METHOD],int(meta4.SEED_BASE[METHOD])

def optimize_at_origin(X,y,target):
    Xtrz,ytrz,Xvz,yvz,split,nval=b41.split_scale(X,y)
    obj=b41.Objective(); fn,seed_base=configure(obj)
    repeats=[]; winner=None
    for rep in range(b41.REPEATS):
        seed=(b41.target_seed(target)+seed_base+1009*rep)%(2**32)
        theta,vfit=fn(Xtrz,ytrz,seed,b41.GENS,center=b41.CENTER,Xv=Xvz,Yv=yvz,refit=False)
        valid=theta is not None and math.isfinite(float(vfit))
        repeats.append({"repeat":rep,"seed":int(seed),"validation_loss":float(vfit) if valid else None})
        if valid:
            key=(float(vfit),rep)
            if winner is None or key<winner[0]: winner=(key,np.asarray(theta,float).copy(),rep)
    if winner is None: raise RuntimeError(f"NO_VALID_OPTIMIZER_CANDIDATE target={target}")
    theta=winner[1]; C,gamma,epsilon=b41.Objective.decode(theta)
    source=Path(inspect.getfile(meta4))
    return {"C":C,"gamma":gamma,"epsilon":epsilon,"log2_C":float(theta[0]),"log2_gamma":float(theta[1]),
            "selected_repeat":int(winner[2]),"selected_validation_loss":float(winner[0][0]),
            "repeat_records":repeats,"inner_train_n":int(split),"inner_valid_n":int(nval),
            "training_fitness_calls":int(obj.training_calls),"validation_calls":int(obj.validation_calls),
            "optimizer_module":meta4.__name__,"optimizer_function":"fa_phase",
            "optimizer_source_sha256":hashlib.sha256(source.read_bytes()).hexdigest()}

def predict_one(bundle,target):
    keys,X,y,tx=s2c.arrays_at_origin(bundle,target); sel=optimize_at_origin(X,y,target)
    Xs,yz,txs,scaler=s1.scale_train_only(X,y,tx)
    model=SVR(kernel="rbf",C=sel["C"],gamma=sel["gamma"],epsilon=sel["epsilon"],shrinking=True,tol=1e-3)
    model.fit(Xs,yz)
    pz=float(model.predict(txs)[0]); pred=float(pz*scaler["y_std"]+scaler["y_mean"])
    if not math.isfinite(pred) or abs(pred)>=1.0: raise RuntimeError(f"PATHOLOGICAL_PRED target={target} pred={pred}")
    origin=base.month_shift(target,-1); prev=float(bundle.core_gold[origin]); forecast=float(prev*math.exp(pred)); actual=float(bundle.core_gold[target])
    pd=int(np.sign(forecast-prev)); ad=int(np.sign(actual-prev))
    return {"target":target,"origin":origin,"method":METHOD,"train_rows":len(keys),"train_first":keys[0],"train_last":keys[-1],
            "inner_train_n":sel["inner_train_n"],"inner_valid_n":sel["inner_valid_n"],"selected_repeat":sel["selected_repeat"],
            "selected_validation_loss":sel["selected_validation_loss"],"repeat_records":sel["repeat_records"],
            "selected_params":{"C":sel["C"],"gamma":sel["gamma"],"epsilon":sel["epsilon"],"log2_C":sel["log2_C"],"log2_gamma":sel["log2_gamma"]},
            "optimizer_module":sel["optimizer_module"],"optimizer_function":sel["optimizer_function"],
            "optimizer_source_sha256":sel["optimizer_source_sha256"],"training_fitness_calls":sel["training_fitness_calls"],
            "validation_calls":sel["validation_calls"],"pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":prev,
            "absolute_error":float(abs(forecast-actual)),"pred_direction":pd,"actual_direction":ad,"direction_correct":bool(pd==ad)}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn); rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        r=predict_one(bundle,target); rows.append(r)
        print(f"PROGRESS method=FA target={target} AE={r['absolute_error']:.6f}",flush=True)
    after=b41.read_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    compact=[{k:r[k] for k in ("target","method","selected_repeat","selected_validation_loss","selected_params","repeat_records","forecast","actual","rw","pred_log_return_gold","direction_correct")} for r in rows]
    payload=hashlib.sha256(json.dumps(compact,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={"family":"SVR_DWT_SVR","scope":"STAGE4_FA_FINAL_DEV_ONLY_V1","method":"FA",
         "contract":{"parent":"EPSILON_RBF_DAILY12","representation":"DAILY_SUMMARY12","kernel":"rbf",
                     "parameter_vector":["log2_C","log2_gamma","epsilon"],"lower_bounds":b41.LOWER.tolist(),"upper_bounds":b41.UPPER.tolist(),
                     "parent_anchor":b41.CENTER.tolist(),"local_sigma":b41.LOCAL_SIGMA.tolist(),"population":b41.POP,"generations":b41.GENS,
                     "repeats":b41.REPEATS,"outer_optimizer_refit":"NONE","dev":"2022-04..2024-12",
                     "2025_role":"LOCKED_NOT_OPENED","2026_role":"QUARANTINED_NOT_USED","random_split":"NONE","database":"READ_ONLY"},
         "metrics":s1.metrics(rows),"yearly":s1.yearly(rows),"rows":rows,"source_checks":bundle.source_checks,
         "authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,"payload_sha256":payload}
    Path("gold_monthly_svr_dwt_stage4_fa_final_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"method":"FA","metrics":out["metrics"],"payload_sha256":payload},sort_keys=True),flush=True)
if __name__=="__main__": main()
