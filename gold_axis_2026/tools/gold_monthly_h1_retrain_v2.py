"""Run original ChHHO-ANFIS or DE-ABC-RBFNN with authoritative Neon H1 inputs.

Always research-only: 2026 historical StakTrakr prices are retroactively captured,
not original month-end first prints. Does not write database or change model registry.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import vw_midas_msvr_successor_v1 as base

FIRST_TARGET, LAST_TARGET = "2022-04", "2026-09"
MODEL_IDS = ("CHHHO", "DE_ABC")
CONTRACT = "NEON_STAKTRAKR_GPR_V2"


def source_gate(bundle):
    c = bundle.source_checks
    if c.get("source_class") != "PINNED_RESEARCH_GIT_NOT_ASOF_PROVEN":
        raise RuntimeError("H1_MODEL_UNAPPROVED_PRICE_SOURCE")
    if c.get("source_pit_verified") is not False:
        raise RuntimeError("H1_MODEL_FALSE_PRICE_ASOF_CLAIM")
    if not c.get("gpr_history_as_of_official_archive"):
        raise RuntimeError("H1_MODEL_GPR_VINTAGE_NOT_VERIFIED")
    if c.get("gpr_origin_vintages") != 55:
        raise RuntimeError("H1_MODEL_INCOMPLETE_GPR_VINTAGES")
    if bundle.core_gpr:
        raise RuntimeError("H1_MODEL_LEGACY_CORE5_GPR_FORBIDDEN")
    if bundle.core_gold != bundle.monthly_metal["Gold"]:
        raise RuntimeError("H1_MODEL_WRONG_XAU_TARGET_AUTHORITY")


def features_for_target(bundle, target):
    if not FIRST_TARGET <= target <= LAST_TARGET:
        raise RuntimeError("H1_MODEL_UNSUPPORTED_TARGET")
    origin = base.month_shift(target, -1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError("H1_MODEL_GPR_ORIGIN_MISSING")
    # Every train sample is constructed from the SAME version that was
    # available at this outer origin. No post-origin GPR revision is used.
    samples = base.all_samples_at_origin(bundle, target, governed=True)
    x, y = samples[target]
    if x.shape != (8,) or y.shape != (4,) or not np.isfinite(x).all():
        raise RuntimeError("H1_MODEL_CURRENT8_BAD_SHAPE")
    if not all(t <= target for t in samples):
        raise RuntimeError("H1_MODEL_FUTURE_SAMPLE_LEAK")
    if len([t for t in samples if t < target]) < 30:
        raise RuntimeError("H1_MODEL_TOO_FEW_TRAINING_MONTHS")
    return samples


def predict_target(bundle, target, model):
    if model not in MODEL_IDS:
        raise RuntimeError("H1_MODEL_UNKNOWN_ESTIMATOR")
    source_gate(bundle)
    samples = features_for_target(bundle, target)
    if model == "CHHHO":
        import vw_midas_anfis_stage3c_literature_v1 as anfis
        prediction, n_train, details = anfis.select(samples, target, "CHHHO")
    else:
        import vw_midas_rbfnn_stage1_v1 as rbfnn
        prediction, details = rbfnn.predict(samples, target, "DE_ABC")
        n_train = len([t for t in samples if t < target])
    prediction = np.asarray(prediction, dtype=float)
    if prediction.shape != (4,) or not np.isfinite(prediction).all():
        raise RuntimeError("H1_MODEL_INVALID_OUTPUT")
    origin = base.month_shift(target, -1)
    origin_level = float(bundle.core_gold[origin])
    realized = float(bundle.core_gold[target])
    projected = float(origin_level * math.exp(float(prediction[0])))
    if not (math.isfinite(projected) and projected > 0 and realized > 0):
        raise RuntimeError("H1_MODEL_INVALID_FORECAST")
    return {
        "target_month": target, "origin_month": origin, "model": model,
        "feature_contract": "CURRENT8_4x_MR1_VW_GPR_ORIGIN",
        "training_rows": int(n_train),
        "origin_gold_average": origin_level, "forecast_xau_average": projected,
        "actual_xau_average": realized, "absolute_error": abs(projected-realized),
        "absolute_percentage_error": 100*abs(projected-realized)/realized,
        "direction_correct": (projected > origin_level) == (realized > origin_level),
        "gpr_source_vintage_origin": origin,
        "data_provenance": "OFFICIAL_GPR_PIT_RECONSTRUCTION_AND_STAKTRAKR_RESEARCH_NOT_PRICE_PIT",
        "diagnostics": details,
    }


def run(dsn, targets, models, mode):
    if mode not in ("inputs", "replay"):
        raise RuntimeError("H1_INVALID_MODE")
    if os.environ.get("GOLD_MONTHLY_H1_DATA_CONTRACT") != CONTRACT:
        raise RuntimeError("H1_MODEL_SOURCE_MODE_NOT_SELECTED")
    bundle = base.load_data(dsn)
    source_gate(bundle)
    targets = list(dict.fromkeys(targets))
    for t in targets:
        if not FIRST_TARGET <= t <= LAST_TARGET:
            raise RuntimeError("H1_MODEL_UNSUPPORTED_TARGET")
    if mode == "inputs":
        result = []
        for t in targets:
            samples = features_for_target(bundle, t)
            x, _ = samples[t]
            result.append({
                "target_month": t, "origin_month": base.month_shift(t, -1),
                "current8": [float(v) for v in x],
                "gpr_origin_vintage_verified": True,
                "feature_count": 8,
                "training_rows": len([z for z in samples if z < t]),
            })
    else:
        result = [predict_target(bundle, t, model) for t in targets for model in models]
    return {
        "status": "RESEARCH_REPLAY_ONLY_NOT_ASOF_PRICE_CERTIFIED",
        "source_contract": CONTRACT,
        "target": "NEXT_CALENDAR_MONTH_XAU_USD_ARITHMETIC_MEAN",
        "no_legacy_core5_price_or_gpr": True,
        "prices_research_only": True,
        "gpr_official_origin_vintage": True,
        "mode": mode,
        "models": models,
        "rows": result,
        "database_writes": "NONE",
        "new_models_promoted": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["inputs", "replay"], default="inputs")
    p.add_argument("--models", default="CHHHO,DE_ABC")
    p.add_argument("--targets", default="2026-08,2026-09")
    p.add_argument("--output", default="gold_monthly_h1_neon_source_v2_result.json")
    args = p.parse_args()
    models = args.models.split(",")
    if not set(models) <= set(MODEL_IDS):
        raise RuntimeError("H1_INVALID_MODELS")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"] = CONTRACT
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL is required for live Neon input audit/replay")
    output = run(dsn, args.targets.split(","), models, args.mode)
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": output["status"], "mode": output["mode"],
                      "results": len(output["rows"]), "models": output["models"]}))


if __name__ == "__main__":
    main()
