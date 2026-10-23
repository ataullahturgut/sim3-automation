"""LMC2 frozen exact Gaussian Process replay on single verified V2 input snapshot.

Do not modify original gpr_lmc_experiment_v1.tune() or .forecast().
DEV: re-tune per origin, exactly as frozen 2026-09-26 spec.
2025/2026: tune ONCE with 2025-01 training, then freeze theta and scalers.
Source research-only and original price firstprint NOT certified.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path
import numpy as np
import gold_monthly_h1_ann_frozen_snapshot_replay_v2 as frozen_snapshot
import gpr_lmc_experiment_v1 as original
import gpr_lmc_core_v1 as core
import gpr_experiment_v1 as gp

MODEL="LMC2_RBF_M32"
SOURCE="NEON_STAKTRAKR_GPR_V2"
FIRST="2022-04"
DEV_END="2024-12"
TEST_START="2025-01"
LAST="2026-09"


def evidence_contract():
    root=Path("gold_axis_2026")
    closure=root/"GOLD_MONTHLY_GPR_STAGE3AB_CLOSURE_2026-09-26.json"
    frozen_doc=root/"GOLD_MONTHLY_GPR_STAGE3C_AUTHORITY_2026-09-26.md"
    j=json.loads(closure.read_text())
    if j["status"]!="COMPLETE" or not frozen_doc.exists():
        raise RuntimeError("ORIGINAL_GPR_3C_FREEZE_AUTHORITY_MISSING")
    if original.METHOD!=MODEL or core.PRIOR.shape!=(40,):
        raise RuntimeError("ORIGINAL_LMC2_MATH_SPEC_CHANGED")
    return {
        "original_runner_sha256":hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest(),
        "original_math_sha256":hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest(),
        "authority_sha256":hashlib.sha256(frozen_doc.read_bytes()).hexdigest(),
        "stage3ab_sha256":hashlib.sha256(closure.read_bytes()).hexdigest(),
        "frozen_algorithm_name":MODEL,
        "original_component_modified":False,
        "hyperparameter_tuning_uses_2025_2026_labels":False,
        "database_writes":"NONE",
        "data_source":SOURCE,
        "source_firstprint_certified":False,
    }


def samples_for(record):
    t=record["target_month"]
    s={}
    for k,(x,y) in record["samples"].items():
        s[k]=(np.asarray(x,dtype=float),None if y is None else np.asarray(y,dtype=float))
    assert s[t][1] is None
    assert record["training_last"]==record["origin_month"]
    assert len(s)-1==record["training_rows"]
    assert all(k<t for k in s if k!=t)
    return s


def getrow(record,frozen,selection):
    target=record["target_month"]
    origin=record["origin_month"]
    samples=samples_for(record)
    mu,var,diag=original.forecast(samples,target,frozen)
    if diag["train_rows"]!=record["training_rows"]:
        raise RuntimeError("LMC2_GOVERNED_HISTORY_MISMATCH")
    if diag["train_last"]!=origin:
        raise RuntimeError("LMC2_FUTURE_TRAINING_LABEL")
    if not (np.isfinite(mu).all() and np.isfinite(var).all() and np.all(var>0)
            and np.max(np.abs(mu))<1):
        raise RuntimeError("LMC2_BAD_POSTERIOR")
    prev=float(record["origin_gold_average"])
    act=float(record["actual_xau_average"])
    pred=float(prev*math.exp(float(mu[0])))
    if not math.isfinite(pred) or pred<=0:
        raise RuntimeError("LMC2_INVALID_XAU_FORECAST")
    interval=[
        float(prev*math.exp(float(mu[0])-1.959963984540054*np.sqrt(var[0]))),
        float(prev*math.exp(float(mu[0])+1.959963984540054*np.sqrt(var[0]))),
    ]
    return {
        "target_month":target,
        "origin_month":origin,
        "origin_input_sha256":record["origin_feature_sha256"],
        "source_snap_model_input_sha256":record["model_input_sha256"],
        "source_gpr_sha256":record["gpr_source_commit_sha"],
        "source_snapshot_sha256":selection["source_snapshot_sha256"],
        "forecast":pred,
        "actual":act,
        "rw":prev,
        "sum_abs_error":abs(pred-act),
        "absolute_percentage_error":100*abs(pred-act)/act,
        "direction_correct":int(np.sign(pred-prev)==np.sign(act-prev)),
        "prediction_gold_log_return":float(mu[0]),
        "training_rows":int(diag["train_rows"]),
        "training_first":record["training_first"],
        "training_last":diag["train_last"],
        "gpr_origin_vintage":origin,
        "diagnostic_theta_sha256":diag["theta_sha256"],
        "model_selection_role":selection["role"],
        "frozen_selection_until":selection["tuning_last"],
        "inner_validation_last":diag["validation_last"],
        "inner_train_last":diag["inner_train_last"],
        "condition_upper_bound":diag["condition_upper_bound"],
        "gold_interval95":interval,
        "variance_gold_return":float(var[0]),
        "optimizer_repeat_records":diag["repeat_records"] if selection["role"]=="DEV_ORIGIN_SELECTION" else None,
    }


def period_metrics(rows):
    if not rows:raise RuntimeError("NO_ROWS_FOR_PERIOD")
    return {
        "n":len(rows),
        "sum_abs_error":sum(r["sum_abs_error"] for r in rows),
        "mape_pct":sum(r["absolute_percentage_error"] for r in rows)/len(rows),
        "correct_directions":sum(r["direction_correct"] for r in rows),
        "max_condition_upper_bound":max(r["condition_upper_bound"] for r in rows),
        "interval95_coverage":sum(r["gold_interval95"][0]<=r["actual"]<=r["gold_interval95"][1] for r in rows)/len(rows),
    }


def run(snapshot_path,out_path,pilot):
    record=frozen_snapshot.read_snapshot(snapshot_path)
    contract=evidence_contract()
    if len(record["records"])!=54 or record["records"][0]["target_month"]!=FIRST or record["records"][-1]["target_month"]!=LAST:
        raise RuntimeError("LMC2_SNAPSHOT_NOT_54_MONTHS")
    contract["canonical_source_snapshot_sha256"]=record["snapshot_sha256"]
    selected=[record["records"][0]] if pilot else record["records"]
    results=[]
    stage="PILOT_ONLY" if pilot else "FULL_54_MONTHS"
    external_frozen=None
    external_meta=None
    for i,rr in enumerate(selected):
        target=rr["target_month"]
        samples=samples_for(rr)
        if target<=DEV_END:
            chosen=original.tune(samples,target,MODEL)
            sel={"role":"DEV_ORIGIN_SELECTION",
                 "tuning_last":chosen[2]["tuning_last"],
                 "source_snapshot_sha256":record["snapshot_sha256"]}
            if chosen[2]["tuning_last"]!=rr["origin_month"]:
                raise RuntimeError("DEV_TUNER_SEES_FUTURE")
        else:
            if external_frozen is None:
                if target!=TEST_START:
                    raise RuntimeError("EXTERNAL_FREEZE_NOT_FROM_JAN_2025")
                external_frozen=original.tune(samples,TEST_START,MODEL)
                external_meta={
                    "theta_sha256":hashlib.sha256(external_frozen[0].tobytes()).hexdigest(),
                    "scaler_sha256":hashlib.sha256(np.concatenate(external_frozen[1]).tobytes()).hexdigest(),
                    "tuning_last":external_frozen[2]["tuning_last"],
                    "inner_validation_last":external_frozen[2]["validation_last"],
                    "training_origin":TEST_START,
                }
                if external_meta["tuning_last"]!="2024-12":
                    raise RuntimeError("EXTERNAL_MODEL_FROZEN_AFTER_2024")
            chosen=external_frozen
            sel={"role":"EXTERNAL_2025_2026_FIXED_PARAMETERS",
                 "tuning_last":external_meta["tuning_last"],
                 "source_snapshot_sha256":record["snapshot_sha256"]}
        row=getrow(rr,chosen,sel)
        results.append(row)
        if row["source_snapshot_sha256"]!=record["snapshot_sha256"]:
            raise RuntimeError("INPUT_FINGERPRINT_CHANGED")
        if external_meta and target>=TEST_START and row["diagnostic_theta_sha256"]!=external_meta["theta_sha256"]:
            raise RuntimeError("EXTERNAL_THETA_DRIFT")
        print("LMC2_REAL_MODEL_FORECAST",stage,f"{i+1}/{len(selected)}",target,
              "forecast=",format(row["forecast"],".6f"),
              "actual=",format(row["actual"],".6f"),
              "direction=",row["direction_correct"],
              "train=",row["training_rows"],flush=True)
        # checkpoint: research only; not a passing score until all requirements
        payload={"status":"IN_PROGRESS","stage":stage,"method":MODEL,"contract":contract,
                 "external_freeze":external_meta,"rows":results}
        Path(out_path).write_text(json.dumps(gp.finite(payload),indent=2,sort_keys=True)+"\n")
    if not pilot and len(results)!=54:
        raise RuntimeError("INCOMPLETE_54_MONTH_LMC2_REPLAY")
    metrics={"DEV_2022_2024":period_metrics(results[:33]) if not pilot else None,
             "TEST_2025":period_metrics(results[33:45]) if not pilot else None,
             "STRESS_2026_01_09":period_metrics(results[45:54]) if not pilot else None}
    payload={"status":"PILOT_1_OF_1_PASS" if pilot else "FULL_54_OF_54_PASS",
             "stage":stage,"method":MODEL,
             "contract":contract,"external_freeze":external_meta,
             "metrics":metrics,"rows":results}
    Path(out_path).write_text(json.dumps(gp.finite(payload),indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("LMC2_FINAL_54_REPLAY_PASS" if not pilot else "LMC2_PILOT_1_PASS",flush=True)
    if not pilot:
        for period,mm in metrics.items():
            print("LMC2_PERIOD_METRICS",period,json.dumps(mm,sort_keys=True),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("pilot","full"),required=True)
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    run(args.snapshot,args.output,args.mode=="pilot")


if __name__=="__main__": main()
