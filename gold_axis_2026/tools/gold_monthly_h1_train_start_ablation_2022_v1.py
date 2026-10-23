"""Research-only 2022-start H1 A/B experiment against the frozen 2010 baseline.

Only the earliest allowed completed training target is changed. Current8
features, origin-specific official GPR histories, original solvers, internal
chronological validation and origin-to-target conversion remain unchanged.
One target/model per child process: optimizers mutate global state.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

import gold_monthly_h1_retrain_v2 as runner
import vw_midas_msvr_successor_v1 as base

START_2022 = "2022-04"
FIRST_TEST = "2026-01"
LAST_TEST = "2026-09"
MODELS = ("CHHHO", "DE_ABC")
CONTRACT = "NEON_STAKTRAKR_GPR_V2"


def predict_one(bundle, target, model):
    runner.source_gate(bundle)
    assert FIRST_TEST <= target <= LAST_TEST
    samples_full = runner.features_for_target(bundle, target)
    proof = runner.input_audit(bundle, target, samples_full)
    training_full = sorted(t for t in samples_full if t < target)
    # Preserve target feature EXACTLY. Change only training start.
    samples = {t: samples_full[t] for t in samples_full if t >= START_2022}
    training = sorted(t for t in samples if t < target)
    if len(training) < 45:
        raise RuntimeError("TRAINING_WINDOW_NOT_LARGE_ENOUGH_FOR_BOTH_SOLVERS")
    assert training[0] == START_2022
    assert training[-1] == base.month_shift(target, -1)
    assert np.array_equal(samples[target][0], samples_full[target][0])
    assert len(training) < len(training_full)
    if model == "CHHHO":
        import vw_midas_anfis_stage3c_literature_v1 as anfis
        pred, n, diag = anfis.select(samples, target, "CHHHO")
    elif model == "DE_ABC":
        import vw_midas_rbfnn_stage1_v1 as rbfnn
        pred, diag = rbfnn.predict(samples, target, "DE_ABC")
        n = len(training)
    else:
        raise RuntimeError("UNKNOWN_MODEL")
    if n != len(training):
        raise RuntimeError("TRAINING_LENGTH_MISMATCH")
    pred = np.asarray(pred, dtype=float)
    if pred.shape != (4,) or not np.isfinite(pred).all():
        raise RuntimeError("BAD_MODEL_RETURN_VECTOR")
    origin = base.month_shift(target, -1)
    origin_level = float(bundle.core_gold[origin])
    actual = float(bundle.core_gold[target])
    estimate = origin_level * math.exp(float(pred[0]))
    assert math.isfinite(estimate) and estimate > 0
    return {
        "model": model, "target_month": target, "origin_month": origin,
        "training_start": START_2022,
        "training_end": training[-1],
        "training_rows": n, "baseline_2010_training_rows": len(training_full),
        "feature_contract": "CURRENT8_4x_MR1_VW_GPR_ORIGIN",
        "source_contract": CONTRACT,
        "origin_feature_sha256": proof["input_sha256"],
        "gpr_source_vintage_origin": origin,
        "gpr_source_commit_sha": proof["gpr_commit_sha"],
        "forecast_xau_average": estimate,
        "actual_xau_average": actual,
        "origin_gold_average": origin_level,
        "absolute_error": abs(estimate - actual),
        "absolute_percentage_error": 100 * abs(estimate - actual) / actual,
        "direction_correct": (estimate > origin_level) == (actual > origin_level),
        "diagnostics": diag,
        "historical_test_only": True, "price_firstprint_certified": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=MODELS, required=True)
    p.add_argument("--targets", default=",".join(base.month_range(FIRST_TEST, LAST_TEST)))
    p.add_argument("--output", required=True)
    p.add_argument("--single", action="store_true")
    a = p.parse_args()
    targets = [t for t in a.targets.split(",") if t]
    if not targets or len(set(targets)) != len(targets) or not all(
        FIRST_TEST <= t <= LAST_TEST for t in targets
    ):
        raise RuntimeError("UNSUPPORTED_TARGETS")
    if not os.environ.get("NEON_DATABASE_URL"):
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"] = CONTRACT
    if a.single:
        bundle = base.load_data(os.environ["NEON_DATABASE_URL"])
        rows = [predict_one(bundle, t, a.model) for t in targets]
    else:
        rows = []
        with tempfile.TemporaryDirectory(prefix="h1_2022_start_") as d:
            for t in targets:
                file = str(Path(d) / (t + ".json"))
                subprocess.run([
                    sys.executable, str(Path(__file__).resolve()),
                    "--model", a.model, "--targets", t, "--output", file, "--single",
                ], check=True, env=os.environ.copy())
                obj = json.loads(Path(file).read_text())
                if len(obj["rows"]) != 1 or obj["rows"][0]["target_month"] != t:
                    raise RuntimeError("ISOLATED_CHILD_RESULT_MISMATCH")
                rows.append(obj["rows"][0])
    output = {
        "status": "RESEARCH_ONLY_2022_TRAINING_WINDOW",
        "model": a.model,
        "training_start": START_2022,
        "training_validation": "ORIGINAL_SOLVER_CHRONOLOGICAL_INNER_SPLIT",
        "model_changes": "NONE",
        "source_changes": "NONE",
        "origin_input_changes": "NONE",
        "source_contract": CONTRACT,
        "database_writes": "NONE",
        "rows": rows,
    }
    Path(a.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    for r in rows:
        print("GOLD_H1_2022_START_FORECAST", a.model, r["target_month"],
              format(r["forecast_xau_average"], ".6f"),
              "actual=", format(r["actual_xau_average"], ".6f"),
              "train=", r["training_rows"], flush=True)


if __name__ == "__main__":
    main()
