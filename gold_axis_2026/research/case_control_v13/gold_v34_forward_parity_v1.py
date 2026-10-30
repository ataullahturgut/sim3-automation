#!/usr/bin/env python3
"""Original V34 weekly MLP8 forward-only inference and strict historical parity.

The unchanged research ANN fits an expanding window at each origin, rather
than loading one timeless checkpoint. This adapter removes target-week actuals
from every input, reproduces the original 16D features and 2D targets, and
verifies numerical parity against the original retrospective fit_predict.
NO Neon writes, trading, live signals, or firstprint promotion.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import sys
import warnings
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import gold_weekly_h1_ann_4metal_v1 as original
import gold_v34_ann_replay as v34

EXPECTED = {
    "hidden_layer_sizes": [8], "activation": "tanh",
    "solver": "lbfgs", "alpha": 1.0, "max_iter": 180,
    "tol": 1e-5, "random_state": 1701, "early_stopping": False
}


def check(condition, code):
    if not condition:
        raise AssertionError("V34_FORWARD_GUARD_" + code)


def target_inputs(past_weeks, target_week):
    check(original.MODEL == "WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1", "MODEL_CHANGED")
    check(original.PARAMS == EXPECTED, "ORIGINAL_HYPERPARAMETERS_CHANGED")
    check(sorted(original.M) == sorted(("AU", "AG", "PT", "PD")), "METALS_CHANGED")
    target = date.fromisoformat(target_week)
    check(target.weekday() == 0, "TARGET_NOT_MONDAY")
    dic = {w["week_monday"]: w for w in past_weeks}
    check(len(dic) == len(past_weeks), "DUPLICATE_WEEK")
    check(all(w < target_week for w in dic), "TARGET_OR_FUTURE_VISIBLE")
    previous = (target - timedelta(days=7)).isoformat()
    check(previous in dic, "NO_COMPLETE_ORIGIN_WEEK")
    keys = sorted(k for k in dic if k < target_week
                  and original.features(dic, k) is not None)
    check(len(keys) > 550, "TRAINING_HISTORY_SHORT")
    x = np.stack([original.features(dic, k) for k in keys])
    previous_train = [(date.fromisoformat(k) - timedelta(days=7)).isoformat()
                      for k in keys]
    y = np.array([[math.log(dic[k]["means"][0] / dic[p]["means"][0]),
                   math.log(dic[k]["closes"][0] / dic[p]["closes"][0])]
                  for k, p in zip(keys, previous_train)], dtype=float)
    xt = original.features(dic, target_week)
    check(xt is not None and xt.shape == (16,), "FEATURE_SHAPE")
    check(x.shape == (len(keys), 16) and y.shape == (len(keys), 2),
          "TRAINING_SHAPE")
    check(np.isfinite(x).all() and np.isfinite(y).all()
          and np.isfinite(xt).all(), "NONFINITE_FEATURES")
    return keys, x, y, xt, dic[previous]


def infer(past_weeks, target_week):
    keys, x, y, xt, prev = target_inputs(past_weeks, target_week)
    a, b, z, mean, std = original.safe_standardize(x, y, xt)
    model = MLPRegressor(
        hidden_layer_sizes=(8,), activation="tanh", solver="lbfgs",
        alpha=1.0, max_iter=180, tol=1e-5,
        random_state=1701, early_stopping=False)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        model.fit(a, b)
    predictions = np.asarray(
        model.predict(z.reshape(1, -1))[0] * std + mean, dtype=float)
    check(np.isfinite(predictions).all()
          and np.max(abs(predictions)) < 0.50, "RETURN_OUTSIDE_ORIGINAL_GUARD")
    payload = json.dumps(
        {"target_week": target_week, "training_keys": keys, "X": x.tolist(),
         "y": y.tolist(), "forecast_X": xt.tolist(),
         "model_params": EXPECTED}, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()
    return {
        "target_week": target_week,
        "origin_week": (date.fromisoformat(target_week)
                        - timedelta(days=7)).isoformat(),
        "forecast_mean_xau": float(prev["means"][0] * math.exp(float(predictions[0]))),
        "forecast_close_xau": float(prev["closes"][0] * math.exp(float(predictions[1]))),
        "training_first_week": keys[0],
        "training_last_week": keys[-1],
        "training_n": len(keys),
        "feature_dim": 16,
        "fitted_iterations": int(model.n_iter_),
        "input_sha256": hashlib.sha256(payload).hexdigest(),
        "model": original.MODEL,
        "uses_target_week_actual": False,
        "source_firstprint_certified": False,
        "production_enabled": False,
        "writes_to_neon": False,
    }


def run_parity():
    snapshot = v34.weekly_snapshot()
    target = "2026-10-19"
    check(target in snapshot["targets"], "HISTORICAL_TARGET_NOT_IN_V34")
    historical = original.fit_predict(snapshot, target)
    past = [w for w in snapshot["week_summaries"]
            if w["week_monday"] < target]
    output = infer(past, target)
    # Strict parity with original V34 per-origin frozen implementation.
    for field in ("forecast_mean_xau", "forecast_close_xau"):
        check(abs(output[field] - historical[field]) <= 1e-8,
              "NUMERICAL_PARITY_" + field)
    check(output["training_n"] == historical["training_n"],
          "TRAIN_LENGTH_PARITY")
    check(output["training_last_week"] == historical["training_last_week"],
          "TRAIN_LAST_PARITY")
    check(output["origin_week"] == historical["origin_week"],
          "ORIGIN_PARITY")
    # Reintroducing target / far-future prices is forbidden in a forward input.
    poison = copy.deepcopy(past)
    future = next(w for w in snapshot["week_summaries"]
                  if w["week_monday"] == target)
    poison.append(future)
    try:
        infer(poison, target)
    except AssertionError as exc:
        check("TARGET_OR_FUTURE_VISIBLE" in str(exc), "POISON_NOT_CAUGHT")
    else:
        raise AssertionError("V34_FORWARD_GUARD_TARGET_POISON_ACCEPTED")
    result = {
        "status": "V34_ORIGINAL_FORWARD_PARITY_PASS_RESEARCH_ONLY",
        "target": target, "source_contract": "EXTERNAL_CLOSE_ONLY_SENSITIVITY_NOT_PIT",
        "historical_mean": historical["forecast_mean_xau"],
        "forward_mean": output["forecast_mean_xau"],
        "historical_close": historical["forecast_close_xau"],
        "forward_close": output["forecast_close_xau"],
        "training_n": output["training_n"],
        "target_week_prices_used": False,
        "production_live": False,
        "Neon_writes": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("historical-parity",), required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    result = run_parity()
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
