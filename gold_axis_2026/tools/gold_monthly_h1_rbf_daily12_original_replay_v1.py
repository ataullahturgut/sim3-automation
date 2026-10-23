"""Frozen EPSILON_RBF_DAILY12 original SVR model audit + 54 month replay.

Important: the 1449.187363 legacy DEV price comparator is DAILY_SUMMARY12,
not CURRENT8. Its established frozen original is Stage2C
gold_monthly_svr_dwt_stage2c_formulation_v1.py.
No source/target modification, no production writes. Retrospective StakTrakr
market price history is not certified to be available at forecast time.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import gold_monthly_h1_retrain_v2 as provenance
import gold_monthly_svr_dwt_stage1_canonical_v1 as stage1
import gold_monthly_svr_dwt_stage2b_representation_v1 as stage2b
import gold_monthly_svr_dwt_stage2c_formulation_v1 as parent

MODEL="EPSILON_RBF_DAILY12"
SOURCE="NEON_STAKTRAKR_GPR_V2"
FIRST="2022-04"
LAST="2026-09"
ALL_TARGETS=list(base.month_range(FIRST,LAST))
SPEC={"kernel":"rbf","C":1.0,"epsilon":0.1,"gamma":"scale","shrinking":True,"tol":1e-3}

def require(check,why):
    if not check:
        raise RuntimeError("FROZEN_RBF_DAILY12_SCIENCE_GATE_FAIL "+why)

def lineage():
    require(parent.COMMON_TRAIN_START=="2010-05","ORIGINAL_2010_START_CHANGED")
    require(parent.SPECS[MODEL]["kind"]=="SVR","NOT_EPSILON_SVR")
    require(parent.SPECS[MODEL]["params"]==SPEC,"ORIGINAL_SVR_HYPERPARAMETERS_CHANGED")
    require(stage2b.RBF_SPEC==SPEC,"STAGE2B_AND_2C_FROZEN_SVR_NOT_EQUAL")
    require(parent.DEV_START==FIRST and parent.DEV_END=="2024-12","DEV_FREEZE_CHANGED")
    require(stage2b.EXPECTED_DIMS["DAILY_SUMMARY12"]==12,"DAILY12_DIMENSION_CHANGED")
    files={}
    for f in (parent,stage1,stage2b):
        p=Path(f.__file__)
        files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    return {"model":MODEL,"origin_family":"SVR_STAGE2C_FORMULATION_FROZEN_PARENT",
            "frozen_legacy_dev_sum_ae":1449.187363,
            "representation":"DAILY_SUMMARY12","features_per_metal":3,
            "metals":list(base.METALS),"model_parameters":SPEC,
            "first_effective_training_target":"2010-05","original_code_sha256":files,
            "original_implementation_modified":False,
            "prospective_price_firstprint_certified":False}

def datasource():
    require(bool(os.environ.get("NEON_DATABASE_URL")),"DATABASE_CREDENTIAL_MISSING")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"]=SOURCE
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    provenance.source_gate(b)
    return b

def poison_data(b,target):
    """Future and current-month data canaries; keep origin data identical."""
    cloned=copy.copy(b)
    cloned.core_gold=dict(b.core_gold)
    cloned.core_gold[target]=float(b.core_gold[target])*10000.0
    cloned.core_gold["2099-01"]=987654321.0
    cloned.monthly_metal={m:dict(v) for m,v in b.monthly_metal.items()}
    cloned.daily_month_values={m:dict(v) for m,v in b.daily_month_values.items()}
    for metal in base.METALS:
        cloned.monthly_metal[metal][target]=float(b.monthly_metal[metal][target])*10000
        cloned.monthly_metal[metal]["2099-01"]=987654321.0
        cloned.daily_month_values[metal][target]=np.full(20,99999999.0)
        cloned.daily_month_values[metal]["2099-01"]=np.full(20,99999999.0)
    return cloned

def audit_one(b,target,check_poison=True):
    origin=base.month_shift(target,-1)
    keys,X,y,xt=parent.arrays_at_origin(b,target)
    require(keys==list(base.month_range("2010-05",origin)),f"TRAINING_HISTORY_GAP {target}")
    require(keys[0]=="2010-05" and keys[-1]==origin,f"TRAINING_END_NOT_ORIGIN {target}")
    require(X.shape==(len(keys),12) and xt.shape==(1,12),f"FEATURE_SHAPE {target}")
    require(len(y)==len(keys),"LABEL_SHAPE")
    require(np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(xt).all(),"NONFINITE")
    require(all(k<target for k in keys),"TARGET_IN_TRAINING")
    sc8=stage1.current8_x(b,target,b.gpr_vintages[origin])
    independently=stage2b.rep_from_current8(b,target,"DAILY_SUMMARY12",sc8)
    require(np.array_equal(independently,xt[0]),f"STAGE2B_2C_FEATURE_PARITY {target}")
    Xs,yz,txs,scale=stage1.scale_train_only(X,y,xt)
    require(np.array_equal(txs,(xt-np.asarray(scale["x_mean"]))/np.asarray(scale["x_std"])),
            "SCALER_USES_TEST_DATA")
    require(np.isfinite(Xs).all() and np.isfinite(yz).all() and np.isfinite(txs).all(),"NONFINITE_SCALE")
    leakproof=None
    if check_poison:
        altered=poison_data(b,target)
        k2,x2,y2,tx2=parent.arrays_at_origin(altered,target)
        require(k2==keys and np.array_equal(X,x2) and np.array_equal(y,y2) and
                np.array_equal(xt,tx2),f"POISON_FUTURE_OR_CURRENT_CHANGES_MODEL_INPUT {target}")
        original=parent.predict_one(b,target,MODEL)
        tainted=parent.predict_one(altered,target,MODEL)
        require(original["forecast"]==tainted["forecast"] and
                original["pred_log_return_gold"]==tainted["pred_log_return_gold"],
                f"TARGET_OR_FUTURE_LEAK {target}")
        require(tainted["actual"]!=original["actual"],"POISON_CANARY_IGNORED")
        leakproof=True
    return {"target":target,"origin":origin,"train_first":keys[0],
            "train_last":keys[-1],"training_rows":len(keys),
            "feature_dim":12,"target_future_poison_invariance_pass":leakproof,
            "origin_gpr_sha":b.source_checks["gpr_origin_lineage"][origin]["official_commit_sha"]}

def prediction(b,target):
    # This directly calls frozen original model code. No algorithm rewrite.
    result=parent.predict_one(b,target,MODEL)
    require(result["train_first"]=="2010-05" and result["train_last"]==result["origin"],
            "ALGORITHM_TRAIN_CUTOFF_INVALID")
    require(result["model"]==MODEL and result["representation"]=="DAILY_SUMMARY12",
            "ALGORITHM_WRONG_FROZEN_IDENTITY")
    require(math.isfinite(result["forecast"]) and result["forecast"]>0,
            "ALGORITHM_PATHOLOGICAL_PREDICTION")
    return {**result,"absolute_error":abs(result["forecast"]-result["actual"]),
            "absolute_percentage_error":100*abs(result["forecast"]-result["actual"])/result["actual"]}

def metrics(rows):
    return {"n":len(rows),
            "sum_abs_error":sum(x["absolute_error"] for x in rows),
            "mape_pct":sum(x["absolute_percentage_error"] for x in rows)/len(rows),
            "direction_correct":sum(x["direction_correct"] for x in rows),
            "worst_month":max(rows,key=lambda r:r["absolute_error"])["target"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("audit","pilot","full"),required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    original=lineage()
    b=datasource()
    result={"status":"IN_PROGRESS","mode":args.mode,"source_contract":SOURCE,
            "algorithm":original,"database_writes":"NONE","source_firstprint_certified":False,
            "training_scope":"2010-05 through each completed origin month",
            "actual_month_target_not_used_during_fit":True}
    if args.mode=="audit":
        inspected=[]
        for i,t in enumerate(ALL_TARGETS,1):
            inspected.append(audit_one(b,t,True))
            print("RBF_DAILY12_V2_NO_LEAK_AUDIT_PASS",i,"/54",t,flush=True)
        require(len(inspected)==54,"NOT_ALL_ORIGINS")
        result.update({"status":"54_OF_54_ORIGIN_CHRONOLOGY_AND_ACTIVE_POISON_PASS",
                       "audited":inspected})
    else:
        selected=ALL_TARGETS[:1] if args.mode=="pilot" else ALL_TARGETS
        rows=[]
        for i,t in enumerate(selected,1):
            audit_one(b,t,check_poison=(args.mode=="pilot"))
            row=prediction(b,t)
            rows.append(row)
            print("RBF_DAILY12_FROZEN_MODEL_PREDICT",i,"/",len(selected),t,
                  "forecast=",format(row["forecast"],".6f"),
                  "actual=",format(row["actual"],".6f"),flush=True)
        result["rows"]=rows
        if args.mode=="pilot":
            result["status"]="PILOT_ORIGINAL_FROZEN_SVR_PASS"
        else:
            require(len(rows)==54,"MISSING_MONTHS")
            result["status"]="FULL_54_OF_54_ORIGINAL_FROZEN_SVR_PASS"
            result["metrics"]={
                "DEV_2022_2024":metrics(rows[:33]),
                "TEST_2025":metrics(rows[33:45]),
                "STRESS_2026_01_09":metrics(rows[45:]),
            }
            for k,v in result["metrics"].items():
                print("RBF_DAILY12_VALIDATED_METRICS",k,json.dumps(v,sort_keys=True),flush=True)
    Path(args.output).write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("RBF_DAILY12_SCIENCE_GATE",result["status"],flush=True)

if __name__=="__main__":
    main()
