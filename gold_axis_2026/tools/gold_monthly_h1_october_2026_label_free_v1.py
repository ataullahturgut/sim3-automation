"""October 2026 H=1 forecast using completed September prices, without October labels.

Uses precisely the unchanged ChHHO-ANFIS / DE-ABC-RBFNN original solver,
the approved NEON_STAKTRAKR_GPR_V2 research bundle and the official
September 2026 GPR version. Runs no database mutations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

import gold_monthly_h1_retrain_v2 as runner
import vw_midas_msvr_successor_v1 as base

TARGET = "2026-10"
ORIGIN = "2026-09"
PREVIOUS = "2026-08"
CONTRACT = "NEON_STAKTRAKR_GPR_V2"


def feature_without_target_label(bundle, target: str, gpr_history: dict) -> np.ndarray:
    """Exact original 8 input formula, excluding target-month response y."""
    p, pp = base.month_shift(target, -1), base.month_shift(target, -2)
    if p not in bundle.core_gold or pp not in bundle.core_gold:
        raise RuntimeError("OCT26_ORIGIN_PRICE_MISSING")
    if target == TARGET and target in bundle.core_gold:
        raise RuntimeError("OCT26_TARGET_PRICE_FORBIDDEN")
    z = base.gpr_norm(gpr_history, pp)
    x = []
    for metal in base.METALS:
        monthly = bundle.monthly_metal[metal]
        if target == TARGET and target in monthly:
            raise RuntimeError("OCT26_TARGET_METAL_PRICE_FORBIDDEN")
        if p not in monthly or pp not in monthly:
            raise RuntimeError("OCT26_METAL_ORIGIN_MISSING_" + metal)
        x.extend([
            math.log(monthly[p] / monthly[pp]),
            base.weighted_daily_return(bundle, metal, p, z),
        ])
    arr = np.asarray(x, dtype=float)
    if arr.shape != (8,) or not np.isfinite(arr).all():
        raise RuntimeError("OCT26_INVALID_EIGHT_FEATURES")
    return arr


def prepare_samples(bundle) -> tuple[dict, dict]:
    runner.source_gate(bundle)
    if max(bundle.core_gold) != ORIGIN:
        raise RuntimeError("OCT26_PRICE_HISTORY_NOT_EXACT_SEPTEMBER")
    if set(bundle.gpr_vintages) != set(bundle.source_checks["gpr_origin_lineage"]):
        raise RuntimeError("OCT26_GPR_LINEAGE_INCOMPLETE")
    if ORIGIN not in bundle.gpr_vintages:
        raise RuntimeError("OCT26_MISSING_SEPTEMBER_GPR_SOURCE")
    lineage = bundle.source_checks["gpr_origin_lineage"][ORIGIN]
    if lineage["lag_month"] != PREVIOUS:
        raise RuntimeError("OCT26_INCORRECT_GPR_LAG")
    if lineage["official_source_file"] != "gpr_archive_files/data_gpr_export_202609.xls":
        raise RuntimeError("OCT26_WRONG_OFFICIAL_GPR_ARCHIVE")
    history = bundle.gpr_vintages[ORIGIN]

    # Pure local formula regression check against September's original code.
    september_original_x, _ = base.sample_for_target(
        bundle, ORIGIN, bundle.gpr_vintages[PREVIOUS], True
    )
    september_no_label_x = feature_without_target_label(
        bundle, ORIGIN, bundle.gpr_vintages[PREVIOUS]
    )
    if not np.array_equal(september_original_x, september_no_label_x):
        raise RuntimeError("OCT26_FEATURE_FORMULA_DIFFERS_FROM_ORIGINAL")

    # Reconstruct every earlier completed sample using the exact GPR vintage
    # available at the Sep-2026 forecast origin, as in all_samples_at_origin.
    samples = {}
    for t in base.month_range("2010-03", ORIGIN):
        try:
            samples[t] = base.sample_for_target(bundle, t, history, True)
        except RuntimeError as ex:
            if str(ex).startswith("GPR_HISTORY_NOT_AVAILABLE"):
                continue  # exactly as the original historical coverage rule
            raise
    if ORIGIN not in samples or len(samples) < 30:
        raise RuntimeError("OCT26_HISTORICAL_TRAINING_NOT_COMPLETE")
    x = feature_without_target_label(bundle, TARGET, history)
    samples[TARGET] = (x, None)   # Truly label-free, NOT a fake y or future price.
    if any(t > TARGET or (t < TARGET and samples[t][1] is None) for t in samples):
        raise RuntimeError("OCT26_FUTURE_LABEL_LEAK")
    if samples[TARGET][1] is not None:
        raise RuntimeError("OCT26_TARGET_LABEL_EXISTS")
    return samples, lineage


def predict(model: str, bundle) -> dict:
    samples, lineage = prepare_samples(bundle)
    x = samples[TARGET][0]
    if model == "CHHHO":
        import vw_midas_anfis_stage3c_literature_v1 as anfis
        log_returns, n_train, diagnostics = anfis.select(samples, TARGET, "CHHHO")
    elif model == "DE_ABC":
        import vw_midas_rbfnn_stage1_v1 as rbfnn
        log_returns, diagnostics = rbfnn.predict(samples, TARGET, "DE_ABC")
        n_train = len(samples) - 1
    else:
        raise RuntimeError("OCT26_UNKNOWN_MODEL")

    log_returns = np.asarray(log_returns, dtype=float)
    if log_returns.shape != (4,) or not np.isfinite(log_returns).all():
        raise RuntimeError("OCT26_BAD_MODEL_OUTPUT")
    level = float(bundle.core_gold[ORIGIN])
    forecast = float(level * math.exp(float(log_returns[0])))
    if not (math.isfinite(forecast) and forecast > 0):
        raise RuntimeError("OCT26_FORECAST_NONFINITE")

    provenance = {
        "target_month": TARGET,
        "origin_month": ORIGIN,
        "gpr_origin_archive": lineage["official_source_file"],
        "gpr_source_commit": lineage["official_commit_sha"],
        "gpr_lag_month": PREVIOUS,
        "gpr_lag_value": lineage["lag_value"],
        "current8": [float(v) for v in x],
        "origin_price_usd_oz": level,
    }
    sha = hashlib.sha256(
        json.dumps(provenance, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "model": model,
        "target_month": TARGET,
        "origin_month": ORIGIN,
        "source_contract": CONTRACT,
        "training_rows": int(n_train),
        "target_label": None,
        "target_realized_price_usd_oz": None,
        "input_eight_features_sha256": sha,
        "provenance": provenance,
        "origin_average_usd_oz": level,
        "predicted_october_average_usd_oz": forecast,
        "predicted_october_change_pct": 100.0 * (forecast / level - 1.0),
        "underlying_solver": (
            "ORIGINAL_CHHHO_ANFIS_UNCHANGED"
            if model == "CHHHO" else "ORIGINAL_DE_ABC_RBFNN_UNCHANGED"
        ),
        "research_status": "OCT_2026_LABEL_FREE_RETROSPECTIVE_REPLAY_NOT_ORIGINAL_FORECAST",
        "price_firstprint_certified": False,
        "data_from_after_september": False,
        "database_writes": 0,
        "diagnostics": diagnostics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("CHHHO", "DE_ABC"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL missing; cannot run true model")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"] = CONTRACT
    bundle = base.load_data(dsn)
    result = predict(args.model, bundle)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("OCT_2026_ACTUAL_MODEL_FORECAST", json.dumps({
        "model": args.model,
        "forecast_usd_oz": result["predicted_october_average_usd_oz"],
        "origin_usd_oz": result["origin_average_usd_oz"],
        "pct": result["predicted_october_change_pct"],
        "training_rows": result["training_rows"],
        "input_sha256": result["input_eight_features_sha256"],
        "target_label": None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
