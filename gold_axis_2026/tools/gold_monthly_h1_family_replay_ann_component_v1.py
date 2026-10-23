"""Frozen ANN component runner for FULL7/REDUCED4 migration.

Original ANN model functions come from gold_monthly_2026_aug_sep_topmodels_v1;
NO original optimizer, architecture, scaling, random seeds or ensemble weights
are changed. One family/component per process due optimizer global state.
The target Y is explicitly nulled before the prediction call.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import gold_monthly_h1_retrain_v2 as source
import gold_monthly_2026_aug_sep_topmodels_v1 as archived

COMPONENTS = (
    "VANILLA", "MPA", "SCA", "DE_ABC",
    "ADAPTIVE_TLBO", "TLBO_TUNED_PSO", "MPA_SCA",
)
CONTRACT = "NEON_STAKTRAKR_GPR_V2"
FIRST, LAST = "2022-04", "2026-09"


def predict_one(bundle, target: str, component: str) -> dict:
    if component not in COMPONENTS or not FIRST <= target <= LAST:
        raise RuntimeError("UNSUPPORTED_FROZEN_ANN_COMPONENT_OR_TARGET")
    source.source_gate(bundle)
    rows=source.features_for_target(bundle,target)
    provenance=source.input_audit(bundle,target,rows)
    x = rows[target][0].copy()
    history=bundle.gpr_vintages[base.month_shift(target,-1)]
    if not np.allclose(archived.forward_x(bundle,target,history),x,rtol=0,atol=1e-14):
        raise RuntimeError("ANN_ORIGINAL_FORWARD_X_NOT_EQUAL_SOURCE_V2")
    # Actual gold/other metal target labels are NOT passed to learner.
    rows[target]=(x,None)
    p,meta=archived.pred_component(rows,target,component)
    p=np.asarray(p,float)
    if p.shape!=(4,) or not np.isfinite(p).all():
        raise RuntimeError("ANN_BAD_FOUR_OUTPUT_RETURN")
    if abs(float(p[0]))>=1.0:
        raise RuntimeError(f"ANN_ABNORMAL_MONTHLY_LOG_RETURN {component} {target} {p[0]}")
    train_count=len([t for t in rows if t<target])
    if meta["train_rows"]!=train_count:
        raise RuntimeError("ANN_INNER_TRAIN_COUNT_MISMATCH")
    origin=base.month_shift(target,-1)
    previous=float(bundle.core_gold[origin])
    actual=float(bundle.core_gold[target])
    forecast=float(previous*math.exp(float(p[0])))
    if not (math.isfinite(forecast) and forecast>0):
        raise RuntimeError("ANN_NONFINITE_PRICE")
    return {
        "model_component":component,"target_month":target,"origin_month":origin,
        "feature_contract":"CURRENT8_4x_MR1_VW_GPR_ORIGIN",
        "source_contract":CONTRACT,
        "origin_feature_sha256":provenance["input_sha256"],
        "gpr_source_commit_sha":provenance["gpr_commit_sha"],
        "training_rows":train_count,
        "target_label_seen_by_learner":False,
        "origin_gold_average":previous,
        "actual_xau_average":actual,
        "forecast_xau_average":forecast,
        "absolute_error":abs(forecast-actual),
        "direction_correct":(forecast>previous)==(actual>previous),
        "source_firstprint_certified":False,
        "database_writes":"NONE",
        "original_component_diagnostics":meta,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--component",required=True,choices=COMPONENTS)
    ap.add_argument("--targets",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    targets=args.targets.split(",")
    if len(set(targets))!=len(targets) or not targets:
        raise RuntimeError("DUPLICATED_TARGET_MONTHS")
    if not os.getenv("NEON_DATABASE_URL"):
        raise RuntimeError("NEON_DATABASE_URL_REQUIRED")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"]=CONTRACT
    bundle=base.load_data(os.environ["NEON_DATABASE_URL"])
    source.source_gate(bundle)
    rows=[]
    for t in targets:
        r=predict_one(bundle,t,args.component)
        rows.append(r)
        print("ANN_FROZEN_COMPONENT_PASS",args.component,t,
              "forecast=",format(r["forecast_xau_average"],".6f"),
              "actual=",format(r["actual_xau_average"],".6f"),
              "train=",r["training_rows"],flush=True)
    payload={"status":"FROZEN_COMPONENT_REPLAY_PASS",
             "component":args.component,"source_contract":CONTRACT,
             "source_firstprint_certified":False,"original_algorithm_changes":"NONE",
             "database_writes":"NONE","rows":rows}
    Path(args.output).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":main()
