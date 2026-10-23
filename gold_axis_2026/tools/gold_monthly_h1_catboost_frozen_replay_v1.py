"""CATBOOST_PRICE verified frozen original Stage1 ordered CatBoost from canonical research.

Uses SAME immutable 54-month origin sample snapshot as ANN and LMC2.
No live database access in fit jobs. Source is retrospective, not PIT firstprint.
Old model code unchanged; strict target label poison and future row tests.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import gold_monthly_h1_ann_frozen_snapshot_replay_v2 as snapshot
import gold_monthly_boosting_stage1_canonical_v1 as original
import gold_monthly_boosting_stage6b_catboost_full_dev_v1 as full_dev
import vw_midas_msvr_successor_v1 as base

ORIGINAL="CATBOOST_ORDERED"
MODEL="CATBOOST_PRICE"
PARAMETERS={
 "loss_function":"RMSE","iterations":100,"depth":6,
 "learning_rate":0.03,"l2_leaf_reg":3.0,
 "boosting_type":"Ordered","random_seed":1701,
 "allow_writing_files":False,"verbose":False,"thread_count":1,
}

def fail_if_false(ok,message):
    if not ok:raise RuntimeError("CATBOOST_FROZEN_SCIENTIFIC_GATE_FAIL "+message)

def attest():
    fail_if_false(original.PARAMS[ORIGINAL]==PARAMETERS,"CATBOOST_PARAMS_CHANGED")
    fail_if_false(original.SEED==1701,"ORIGINAL_SEED_CHANGED")
    fail_if_false(full_dev.FINALISTS[0]=="VANILLA","LEGACY_PRICE_ID_MISMATCH")
    fail_if_false("2010-03"==base.month_shift("2010-04",-1),"BAD_CHRONOLOGY_ENGINE")
    return {
       "model_name":MODEL,"source_legacy_model":ORIGINAL,
       "legacy_DEV_sum_abs_error":1460.433935309605,
       "frozen_hyperparameters":PARAMETERS,
       "feature_representation":"CURRENT8",
       "training_start":"2010-03",
       "source_model_sha256":hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest(),
       "source_stage6b_sha256":hashlib.sha256(Path(full_dev.__file__).read_bytes()).hexdigest(),
       "original_mathematical_model_changed":False,
       "source_firstprint_certified":False,
    }

def prepare(record):
    target=record["target_month"]
    data={}
    for m,(x,y) in record["samples"].items():
        data[m]=(np.asarray(x,dtype=float),None if y is None else np.asarray(y,dtype=float))
    fail_if_false(data[target][1] is None,"TARGET_LABEL_EXPOSED")
    keys,X,y,tx=original.arrays(data,target)
    fail_if_false(keys==list(base.month_range("2010-03",record["origin_month"])),"TRAINING_GAP_OR_FUTURE")
    fail_if_false(X.shape==(record["training_rows"],8),"BAD_TRAINING_DIMENSION")
    fail_if_false(tx.shape==(1,8),"BAD_FORECAST_FEATURES")
    fail_if_false(len(y)==len(keys),"BAD_TRAINING_TARGET_ROWS")
    fail_if_false(np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(tx).all(),"NONFINITE_INPUT")
    fail_if_false(record["training_first"]==keys[0],"RECORD_TRAINING_START_MISMATCH")
    fail_if_false(record["training_last"]==keys[-1],"RECORD_TRAINING_END_MISMATCH")
    fail_if_false(len(keys)==record["training_rows"],"RECORD_TRAINING_COUNT_MISMATCH")
    gold={record["origin_month"]:float(record["origin_gold_average"]),
          target:float(record["actual_xau_average"])}
    return SimpleNamespace(core_gold=gold),data,keys,X,y,tx

def prediction(record,poison=False):
    bundle,data,keys,X,y,tx=prepare(record)
    t=record["target_month"]
    if poison:
        # poison the entire target month label and a 2099 future observation.
        data[t]=(data[t][0].copy(),np.array([1e9,-1e9,1e9,-1e9]))
        data["2099-01"]=(np.full(8,1e12),np.full(4,1e12))
        bundle.core_gold[t]=bundle.core_gold[t]*10000
        bundle.core_gold["2099-01"]=1e15
        k2,X2,y2,tx2=original.arrays(data,t)
        fail_if_false(k2==keys and np.array_equal(X,X2) and np.array_equal(y,y2)
                      and np.array_equal(tx,tx2),
                      "FUTURE_OR_TARGET_LABEL_MUTATES_TRAINING_FEATURES")
    out=original.predict_one(bundle,data,t,ORIGINAL)
    fail_if_false(out["train_first"]=="2010-03" and out["train_last"]==record["origin_month"],
                  "ORIGINAL_MODEL_SAW_FUTURE_LABEL")
    fail_if_false(out["train_rows"]==record["training_rows"],"TRAIN_N_CHANGED")
    fail_if_false(math.isfinite(out["forecast"]) and out["forecast"]>0,
                  "BAD_MODEL_OUTPUT")
    return out

def metrics(rows):
    n=len(rows)
    fail_if_false(n>0,"EMPTY_PHASE")
    return {
      "n":n,
      "sum_abs_error":sum(r["absolute_error"] for r in rows),
      "mape_pct":sum(r["absolute_percentage_error"] for r in rows)/n,
      "directions_correct":sum(r["direction_correct"] for r in rows),
      "worst_month":max(rows,key=lambda x:x["absolute_error"])["target_month"],
    }

def run(mode,path,output):
    p=snapshot.read_snapshot(path)
    att=attest()
    rows=p["records"]
    fail_if_false(len(rows)==54 and rows[0]["target_month"]=="2022-04"
                  and rows[-1]["target_month"]=="2026-09","WRONG_SNAPSHOT_WINDOW")
    # identical SHA-256 provenance as all other model families
    att["common_snapshot_sha256"]=p["snapshot_sha256"]
    result={
       "status":"IN_PROGRESS","run_mode":mode,"model":MODEL,
       "model_contract":"NEON_STAKTRAKR_GPR_V2",
       "source_firstprint_certified":False,
       "original_algorithm_untouched":True,"database_reads":"NONE",
       "database_writes":"NONE","algorithm":att,
       "rows":[],
    }
    chosen=rows[:1] if mode=="pilot" else rows
    for i,r in enumerate(chosen,1):
        clean=prediction(r)
        if mode=="audit":
            altered=prediction(r,poison=True)
            fail_if_false(clean["forecast"]==altered["forecast"] and
                          clean["pred_log_return_gold"]==altered["pred_log_return_gold"],
                          "TARGET_MONTH_OR_FUTURE_POISON_CHANGED_PREDICTION "+r["target_month"])
            fail_if_false(clean["actual"]!=altered["actual"],"TARGET_ACTUAL_CANARY_NOT_EFFECTIVE")
        actual=float(clean["actual"])
        forecast=float(clean["forecast"])
        prev=float(clean["rw"])
        fail_if_false(actual==r["actual_xau_average"] and prev==r["origin_gold_average"],
                      "ACTUAL_OR_ORIGIN_INCONSISTENCY")
        m={
          "target_month":r["target_month"],"origin_month":r["origin_month"],
          "model":MODEL,"algorithm_source":ORIGINAL,
          "forecast_xau_average":forecast,"actual_xau_average":actual,
          "origin_gold_average":prev,
          "absolute_error":abs(forecast-actual),
          "absolute_percentage_error":100*abs(forecast-actual)/actual,
          "direction_correct":int((forecast>prev)==(actual>prev)),
          "training_first":clean["train_first"],
          "training_last":clean["train_last"],
          "training_rows":clean["train_rows"],
          "model_input_sha256":r["model_input_sha256"],
          "origin_feature_sha256":r["origin_feature_sha256"],
          "gpr_commit_sha":r["gpr_source_commit_sha"],
          "source_snapshot_sha256":p["snapshot_sha256"],
          "target_label_or_future_poison_no_effect":True if mode=="audit" else None,
        }
        result["rows"].append(m)
        print("CATBOOST_FROZEN_MONTH_PASS",mode,i,len(chosen),r["target_month"],
              format(forecast,".6f"),format(actual,".6f"),flush=True)
    if mode=="pilot":
        result["status"]="CATBOOST_FROZEN_PILOT_1_OF_1_PASS"
    elif mode=="audit":
        fail_if_false(len(result["rows"])==54,"AUDIT_INCOMPLETE")
        result["status"]="CATBOOST_TARGET_FUTURE_POISON_54_OF_54_PASS"
    else:
        fail_if_false(len(result["rows"])==54,"FULL_REPLAY_INCOMPLETE")
        result["status"]="CATBOOST_PRICE_54_OF_54_RESEARCH_PASS"
        rr=result["rows"]
        result["metrics"]={"DEV_2022_2024":metrics(rr[:33]),
                           "TEST_2025":metrics(rr[33:45]),
                           "STRESS_2026_01_09":metrics(rr[45:])}
        for name,val in result["metrics"].items():
            print("CATBOOST_PRICE_REPLAY_METRIC",name,json.dumps(val,sort_keys=True),flush=True)
    Path(output).write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("CATBOOST_RUN_RESULT",result["status"],flush=True)

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--mode",choices=("audit","pilot","full"),required=True)
    pa.add_argument("--snapshot",required=True)
    pa.add_argument("--output",required=True)
    args=pa.parse_args()
    run(args.mode,args.snapshot,args.output)

if __name__=="__main__":main()
