"""LMC2_RBF_M32 audit gate ONLY. No 54x optimizer fitting or results.

(1) verify unchanged frozen mathematical contract & chronology
(2) check 54 source origins after explicit V2 opt-in
(3) active poison test: target Y and 2099 future rows must not change GP
    training matrices, validation split, tuned results on synthetic data.
(4) verify variance/nll/gradients using original test_gpr_lmc_core_v1.py
"""
from __future__ import annotations
import argparse, ast, hashlib, importlib, json, math, os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_h1_retrain_v2 as authority
import gpr_experiment_v1 as gp
import gpr_lmc_experiment_v1 as lmc
import gpr_lmc_core_v1 as lc

FIRST,LAST="2022-04","2026-09"
V2="NEON_STAKTRAKR_GPR_V2"

def die(s):
    raise RuntimeError("LMC2_MODEL_AUDIT_BLOCKED: "+s)

def code_governance():
    frozen=Path(__file__).with_name("gpr_lmc_experiment_v1.py")
    body=frozen.read_text()
    nodes=ast.parse(body).body
    functions={f.name:f for f in nodes if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef))}
    if set(["tune","forecast","run"])-set(functions):die("FROZEN_ORIGINAL_ENTRYPOINT_MISSING")
    old=Path(__file__).with_name("gpr_experiment_v1.py").read_text()
    if "keys=sorted(k for k in samples if k<target)" not in old:
        die("INNER_SPLIT_STRICT_PAST_PREPARE_NOT_FOUND")
    if "keys=sorted(k for k in samples if k<target)" not in body:
        die("GP_POSTERIOR_STRICT_PAST_TRAINER_NOT_FOUND")
    for statement in [
        "frozen=tune(e.r.base.all_samples_at_origin(b,'2025-01',governed=True),'2025-01',METHOD)",
        "d['transport_2025']=e.evaluate(b,METHOD,'2025-01','2025-12',frozen)",
        "d['stress_2026']=e.evaluate(b,METHOD,'2026-01','2026-07',frozen)",
        "if not np.isfinite(mu).all()",
        "l.fit(theta,X,Y)",
    ]:
        if statement not in body:die("FROZEN_LMC_CODE_NOT_EXPECTED: "+statement)
    if not all((lc.PRIOR.shape==(40,),lc.LOW.shape==(40,),lc.HIGH.shape==(40,),
                np.all(lc.LOW<lc.HIGH),np.all(lc.PRIOR>=lc.LOW),np.all(lc.PRIOR<=lc.HIGH))):
        die("40_PARAM_FROZEN_HYPERPARAMETER_BOUNDS_CHANGED")
    if lmc.METHOD!="LMC2_RBF_M32":die("WRONG_GP_MODEL")
    return {
        "model":"LMC2_RBF_M32","original_solver_changed":False,
        "frozen_theta_parameters":40,"kernels":["ARD_RBF","ARD_M32"],
        "external_theta_scaler_freeze":"2024-12",
        "model_implementation_sha256":hashlib.sha256(body.encode()).hexdigest(),
        "core_implementation_sha256":hashlib.sha256(Path(lc.__file__).read_bytes()).hexdigest(),
        "source_original_technical_provenance":"test_gpr_lmc_core_v1.py",
    }

def source_and_leakage_audit():
    if not os.getenv("NEON_DATABASE_URL"):die("NEON_DATABASE_URL_MISSING")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"]=V2
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    authority.source_gate(b)
    rs=[]
    for t in base.month_range(FIRST,LAST):
        origin=base.month_shift(t,-1)
        samples=authority.features_for_target(b,t)
        proof=authority.input_audit(b,t,samples)
        keys,X,Y,split,sc=gp.prepare(samples,t)
        if not keys or keys[0]!="2010-03":
            die(f"EARLIEST_TRAIN_MONTH_NOT_2010_03 {t} {keys[0] if keys else None}")
        if keys[-1]!=origin:
            die(f"LATE_TRAINING_LABEL_OR_GAP {t} {keys[-1]}")
        if len(keys)!=int(round((int(origin[:4])-2010)*12+int(origin[5:])-3+1)):
            die(f"TRAINING_MONTH_COVERAGE_GAP {t} count={len(keys)}")
        if not (0<split<len(keys) and
                keys[split-1]<keys[split]<=origin):
            die("NON_CHRONOLOGICAL_INNER_SPLIT")
        if any(k>=t for k in keys):
            die("TARGET_OR_FUTURE_IN_LEARNER")
        if any(not np.isfinite(x).all() for x in (X,Y)):
            die("NONFINITE_TRAINING_FEATURES")
        if len(proof["gpr_commit_sha"])!=40:
            die("INVALID_OFFICIAL_GPR_PROVENANCE")
        hist=b.gpr_vintages[origin]
        if any(m>base.month_shift(origin,-1) for m in hist):
            die("FUTURE_GPR_OBSERVATION_IN_ORIGIN_ARCHIVE")
        poison=dict(samples)
        x=samples[t][0]
        poison[t]=(x.copy(),np.array([1e20,-1e20,1e20,-1e20]))
        poison["2099-01"]=(np.full(8,1e20),np.full(4,1e20))
        kp,XP,YP,sp,scp=gp.prepare(poison,t)
        if kp!=keys or sp!=split or not np.array_equal(X,XP) or not np.array_equal(Y,YP):
            die(f"POISON_TARGET_OR_FUTURE_ALTERS_GP_DATA {t}")
        if any(not np.array_equal(a,bb) for a,bb in zip(sc,scp)):
            die(f"POISON_TARGET_OR_FUTURE_ALTERS_SCALER {t}")
        rs.append({"target":t,"origin":origin,
            "training_first":keys[0],"training_last":keys[-1],
            "training_rows":len(keys),
            "inner_train_n":split,"inner_validation_n":len(keys)-split,
            "inner_validation_last":keys[-1],
            "gpr_commit_sha":proof["gpr_commit_sha"],
            "gpr_archive_path":proof["gpr_file"],
            "origin_input_sha256":proof["input_sha256"],
            "target_label_poison_invariant":True,
            "future_2099_record_invariant":True,
        })
        print("LMC2_V2_54_ORIGIN_LEAKAGE_GATE_PASS",t,len(keys),
             keys[0],keys[-1],flush=True)
    if len(rs)!=54:die("INCOMPLETE_54_TARGET_WINDOW")
    if len({r["target"] for r in rs})!=54:die("DUPLICATE_TARGETS")
    return rs,b.source_checks

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("static","source"),required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    audit=code_governance()
    payload={
        "status":"MODEL_AUDIT_ONLY_NO_TRAINING",
        "algorithm":audit,
        "database_writes":"NONE",
        "neon_price_firstprint_certified":False,
        "model_forecast_execution":"NOT_STARTED",
    }
    if args.mode=="source":
        rows,checks=source_and_leakage_audit()
        payload.update({
            "status":"MODEL_STATIC_AND_54_ORIGIN_INPUT_LEAK_AUDIT_PASS",
            "source_contract":V2,"n_checked":54,
            "all_training_start_in_2010":True,
            "all_inner_validation_chronological":True,
            "source_checks":checks,"rows":rows,
        })
    else:
        payload["status"]="MODEL_STATIC_FROZEN_SPEC_PASS"
    Path(args.output).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("LMC2_AUDIT_GATE_PASS",args.mode,payload["status"],flush=True)

if __name__=="__main__":main()
