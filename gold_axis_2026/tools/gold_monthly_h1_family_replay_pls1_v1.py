"""Research-only, exact frozen PLS1 promotion into shared GOLD H1 comparison.

Does NOT alter sklearn PLS1 original code, 12-month inner validation,
model-component search, source tables, existing 54x2 run, or production.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_h1_retrain_v2 as authority
import gold_monthly_challenger_b_pls1_v1 as pls

MODEL_ID = "PLS1_V1_ALL4"
SOURCE = "NEON_STAKTRAKR_GPR_V2"
FIRST, LAST = "2022-04", "2026-09"


def predict(bundle, target):
    if not FIRST <= target <= LAST:
        raise RuntimeError("TARGET_OUTSIDE_FROZEN_EVALUATION_54")
    authority.source_gate(bundle)
    reference_samples = authority.features_for_target(bundle, target)
    audit = authority.input_audit(bundle, target, reference_samples)
    gpr_history = bundle.gpr_vintages[base.month_shift(target, -1)]
    independent_x = pls.current8_x_only(bundle, target, gpr_history)
    reference_x = reference_samples[target][0]
    if not np.allclose(independent_x, reference_x, rtol=0.0, atol=1e-14):
        raise RuntimeError("PLS1_ORIGIN_FEATURE_PARITY_FAILED")
    # Calls unchanged PLSRegression and its original 12m chronological inner
    # validation/component-selection; only the corrected data bundle is passed.
    r = pls.forecast_one(bundle, target)
    if r["representation"] != "CURRENT8" or r["feature_dim"] != 8:
        raise RuntimeError("PLS1_FEATURE_CONTRACT_CHANGED")
    if r["inner_val_n"] != pls.INNER_VAL_MONTHS:
        raise RuntimeError("PLS1_ORIGINAL_VALIDATION_CHANGED")
    if r["train_rows"] <= 30 or r["train_last"] != base.month_shift(target, -1):
        raise RuntimeError("PLS1_TRAIN_LAST_NOT_ORIGIN")
    if not (1 <= r["selected_n_components"] <= 8):
        raise RuntimeError("PLS1_ILLEGAL_COMPONENT_COUNT")
    if not math.isfinite(r["forecast"]) or r["forecast"] <= 0:
        raise RuntimeError("PLS1_INVALID_FORECAST")
    origin = base.month_shift(target, -1)
    if abs(r["actual"] - float(bundle.core_gold[target])) > 1e-8:
        raise RuntimeError("PLS1_ACTUAL_NOT_SHARED")
    return {
        "target_month":target, "origin_month":origin,
        "model":MODEL_ID, "feature_contract":"CURRENT8_4x_MR1_VW_GPR_ORIGIN",
        "source_contract":SOURCE, "origin_feature_sha256":audit["input_sha256"],
        "gpr_source_file":audit["gpr_file"],
        "gpr_source_commit_sha":audit["gpr_commit_sha"],
        "training_first_effective":r["train_first"],
        "training_last":r["train_last"],
        "training_rows":r["train_rows"],
        "inner_validation_first":r["inner_val_first"],
        "inner_validation_last":r["inner_val_last"],
        "inner_validation_rows":r["inner_val_n"],
        "selected_pls_components":r["selected_n_components"],
        "origin_gold_average":r["rw"],
        "forecast_xau_average":r["forecast"],
        "actual_xau_average":r["actual"],
        "absolute_error":r["absolute_error"],
        "absolute_percentage_error":100*r["absolute_error"]/r["actual"],
        "direction_correct":r["direction_correct"],
        "original_model_file":"gold_monthly_challenger_b_pls1_v1.py",
        "original_training_start_config":pls.TRAIN_START,
        "original_inner_validation_months":pls.INNER_VAL_MONTHS,
        "original_component_grid":list(pls.COMPONENTS),
        "original_solver_modified":False,
        "source_research_only":True,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--targets",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    targets=args.targets.split(",")
    if not targets or len(set(targets)) != len(targets) or any(not FIRST<=t<=LAST for t in targets):
        raise RuntimeError("INVALID_TARGET_LIST")
    if not os.getenv("NEON_DATABASE_URL"):
        raise RuntimeError("NO_DATABASE_SECRET")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"]=SOURCE
    bundle=base.load_data(os.environ["NEON_DATABASE_URL"])
    authority.source_gate(bundle)
    rows=[]
    for t in targets:
        r=predict(bundle,t); rows.append(r)
        print("PLS1_FROZEN_SOURCE_PASS",t,
              "forecast=",format(r["forecast_xau_average"],".6f"),
              "actual=",format(r["actual_xau_average"],".6f"),
              "train=",r["training_rows"],
              "inner_check=",r["inner_validation_rows"],flush=True)
    output={
        "status":"RESEARCH_ONLY_NO_PRODUCTION_WRITES",
        "model":MODEL_ID, "mode":"REPLAY",
        "source_contract":SOURCE,"original_solver_modified":False,
        "random_split":False,"database_writes":"NONE",
        "data_firstprint_certified":False,
        "rows":rows,
    }
    Path(args.output).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("PLS1_FROZEN_REPLAY_COMPLETE",len(rows),flush=True)


if __name__=="__main__": main()
