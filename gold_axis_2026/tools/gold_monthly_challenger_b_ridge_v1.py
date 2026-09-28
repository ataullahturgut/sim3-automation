#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg
import sklearn
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "GOLD_MONTHLY_CHALLENGER_B_RIDGE_V1"
FREEZE_FILE = "GOLD_MONTHLY_CHALLENGER_B_RIDGE_FREEZE_2026-09-28.md"

TRAIN_START = "2010-05"
INNER_VAL_MONTHS = 12
MIN_INNER_TRAIN = 36
ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0)

DEV_START, DEV_END = "2022-04", "2024-12"
HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"


def read_invariants(dsn: str) -> dict:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def current8_x_only(bundle, target: str, gpr_history: dict) -> np.ndarray:
    """Build CURRENT8 without reading target-month metal values."""
    p = base.month_shift(target, -1)
    pp = base.month_shift(target, -2)
    z = base.gpr_norm(gpr_history, pp)
    x = []
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"MONTHLY_METAL_FEATURE_MISSING metal={metal} target={target}")
        mr = math.log(float(M[p]) / float(M[pp]))
        vw = base.weighted_daily_return(bundle, metal, p, z)
        x.extend((mr, vw))
    out = np.asarray(x, dtype=float)
    if out.shape != (8,) or not np.isfinite(out).all():
        raise RuntimeError(f"CURRENT8_FEATURE_GATE_FAIL target={target} shape={out.shape}")
    return out


def build_origin_data(bundle, target: str) -> dict:
    origin = base.month_shift(target, -1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh = bundle.gpr_vintages[origin]

    # Only matured targets through the completed origin month are training rows.
    samples = {}
    for t in base.month_range(TRAIN_START, origin):
        try:
            samples[t] = base.sample_for_target(bundle, t, gh, True)
        except RuntimeError:
            continue

    keys = sorted(k for k in samples if TRAIN_START <= k <= origin)
    if len(keys) < INNER_VAL_MONTHS + MIN_INNER_TRAIN:
        raise RuntimeError(f"TRAIN_HISTORY_TOO_SMALL target={target} n={len(keys)}")

    split = len(keys) - INNER_VAL_MONTHS
    tr = keys[:split]
    va = keys[split:]

    Xtr = np.stack([samples[k][0] for k in tr])
    ytr = np.asarray([float(samples[k][1][0]) for k in tr], dtype=float)
    Xv = np.stack([samples[k][0] for k in va])
    prev_v = np.asarray([float(bundle.core_gold[base.month_shift(k, -1)]) for k in va], dtype=float)
    actual_v = np.asarray([float(bundle.core_gold[k]) for k in va], dtype=float)

    Xall = np.stack([samples[k][0] for k in keys])
    yall = np.asarray([float(samples[k][1][0]) for k in keys], dtype=float)

    # Explicit x-only outer path: no target-month metal level/return is dereferenced.
    xt = current8_x_only(bundle, target, gh).reshape(1, -1)

    for name, arr in {
        "Xtr": Xtr, "ytr": ytr, "Xv": Xv, "prev_v": prev_v,
        "actual_v": actual_v, "Xall": Xall, "yall": yall, "xt": xt,
    }.items():
        if not np.isfinite(arr).all():
            raise RuntimeError(f"NONFINITE_DATA target={target} field={name}")

    rw_ae = float(np.abs(prev_v - actual_v).sum())
    return {
        "origin": origin,
        "keys": keys,
        "inner_train_keys": tr,
        "inner_val_keys": va,
        "Xtr": Xtr,
        "ytr": ytr,
        "Xv": Xv,
        "prev_v": prev_v,
        "actual_v": actual_v,
        "inner_rw_sum_ae": rw_ae,
        "Xall": Xall,
        "yall": yall,
        "xt": xt,
        "anchor_prev": float(bundle.core_gold[origin]),
    }


def fit_predict_return(X_train, y_train, X_test, alpha: float) -> np.ndarray:
    scaler = StandardScaler(with_mean=True, with_std=True)
    Xs = scaler.fit_transform(X_train)
    Xt = scaler.transform(X_test)
    model = Ridge(alpha=float(alpha), fit_intercept=True)
    model.fit(Xs, y_train)
    pred = np.asarray(model.predict(Xt), dtype=float).reshape(-1)
    if not np.isfinite(pred).all() or np.any(np.abs(pred) >= 1.0):
        raise RuntimeError(f"PATHOLOGICAL_RIDGE_PRED alpha={alpha}")
    return pred


def choose_alpha(data: dict) -> tuple[float, list[dict]]:
    scored = []
    denom = max(float(data["inner_rw_sum_ae"]), 1e-12)
    for alpha in ALPHAS:
        pred = fit_predict_return(data["Xtr"], data["ytr"], data["Xv"], alpha)
        fc = data["prev_v"] * np.exp(pred)
        sum_ae = float(np.abs(fc - data["actual_v"]).sum())
        scored.append({
            "alpha": float(alpha),
            "inner_sum_abs_error": sum_ae,
            "inner_relative_sum_abs_error_vs_rw": float(sum_ae / denom),
        })
    scored.sort(key=lambda r: (r["inner_relative_sum_abs_error_vs_rw"], r["alpha"]))
    return float(scored[0]["alpha"]), scored


def forecast_one(bundle, target: str) -> dict:
    data = build_origin_data(bundle, target)
    alpha, alpha_scores = choose_alpha(data)

    pred = float(fit_predict_return(data["Xall"], data["yall"], data["xt"], alpha)[0])
    forecast = float(data["anchor_prev"] * math.exp(pred))

    # Post-forecast scoring only.
    if target not in bundle.core_gold:
        raise RuntimeError(f"SCORING_ACTUAL_MISSING {target}")
    actual = float(bundle.core_gold[target])
    rw = float(data["anchor_prev"])

    return {
        "target": target,
        "origin": data["origin"],
        "representation": "CURRENT8",
        "feature_dim": 8,
        "train_first": data["keys"][0],
        "train_last": data["keys"][-1],
        "train_rows": len(data["keys"]),
        "inner_train_n": len(data["inner_train_keys"]),
        "inner_val_n": len(data["inner_val_keys"]),
        "inner_val_first": data["inner_val_keys"][0],
        "inner_val_last": data["inner_val_keys"][-1],
        "selected_alpha": alpha,
        "alpha_scores": alpha_scores,
        "pred_log_return_gold": pred,
        "forecast": forecast,
        "actual": actual,
        "rw": rw,
        "absolute_error": float(abs(forecast - actual)),
        "rw_absolute_error": float(abs(rw - actual)),
        "direction_correct": bool(
            int(np.sign(forecast - rw)) == int(np.sign(actual - rw))
        ),
    }


def metrics(rows: list[dict]) -> dict:
    a = np.asarray([r["actual"] for r in rows], dtype=float)
    f = np.asarray([r["forecast"] for r in rows], dtype=float)
    rw = np.asarray([r["rw"] for r in rows], dtype=float)
    ae = np.abs(f - a)
    rw_ae = np.abs(rw - a)
    dc = np.asarray([r["direction_correct"] for r in rows], dtype=bool)
    wi = int(np.argmax(ae))
    return {
        "n": len(rows),
        "sum_abs_error": float(ae.sum()),
        "mae": float(ae.mean()),
        "rmse": float(np.sqrt(np.mean((f - a) ** 2))),
        "mape_pct": float(np.mean(ae / np.maximum(np.abs(a), 1e-12)) * 100.0),
        "wape_pct": float(ae.sum() / np.maximum(np.abs(a).sum(), 1e-12) * 100.0),
        "median_ae": float(np.median(ae)),
        "worst_ae": float(ae[wi]),
        "worst_month": rows[wi]["target"],
        "relative_mae_vs_rw": float(ae.sum() / max(float(rw_ae.sum()), 1e-12)),
        "rw_sum_abs_error": float(rw_ae.sum()),
        "direction_correct": int(dc.sum()),
        "direction_accuracy_pct": float(dc.mean() * 100.0),
    }


def yearly(rows: list[dict]) -> dict:
    years = sorted({r["target"][:4] for r in rows})
    return {y: metrics([r for r in rows if r["target"].startswith(y)]) for y in years}


def run_period(bundle, start: str, end: str, label: str) -> dict:
    targets = list(base.month_range(start, end))
    rows = []
    for i, target in enumerate(targets, 1):
        row = forecast_one(bundle, target)
        rows.append(row)
        print(
            f"PROGRESS period={label} target={i}/{len(targets)} month={target} "
            f"alpha={row['selected_alpha']:.4g} AE={row['absolute_error']:.6f} "
            f"dir={int(row['direction_correct'])}",
            flush=True,
        )
    return {
        "role": label,
        "metrics": metrics(rows),
        "yearly": yearly(rows),
        "selected_alpha_counts": dict(sorted(Counter(str(r["selected_alpha"]) for r in rows).items())),
        "rows": rows,
    }


def main() -> None:
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)

    b0 = {
        "source_checks": bundle.source_checks,
        "current8_feature_contract": {
            "metals": list(base.METALS),
            "features_per_metal": ["MR_previous_month_log_return", "VW_gpr_adaptive_weighted_daily_log_return"],
            "feature_dim": 8,
            "gpr_source": base.GPR_PIT,
            "outer_feature_builder": "X_ONLY_NO_TARGET_MONTH_METAL_DEREFERENCE",
        },
        "gate_pass": (
            not bundle.source_checks["missing_required_gpr_origins"]
            and not bundle.source_checks["late_required_gpr_origins"]
            and not bundle.source_checks["missing_required_gpr_lag_month"]
        ),
    }
    if not b0["gate_pass"]:
        raise RuntimeError(f"B0_SOURCE_GATE_FAIL {b0}")

    dev = run_period(bundle, DEV_START, DEV_END, "DEV_SELECTION_AUTHORITY")
    if dev["metrics"]["n"] != 33:
        raise RuntimeError(f"DEV_N_FAIL {dev['metrics']['n']}")

    # Method is frozen above; these periods are report-only and never feed back into selection.
    holdout = run_period(bundle, HOLDOUT_START, HOLDOUT_END, "LOCKED_REPORT_ONLY")
    stress = run_period(bundle, STRESS_START, STRESS_END, "QUARANTINED_REPORT_ONLY")

    after = read_invariants(dsn)
    invariant_same = after == bundle.invariants_before
    if not invariant_same:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    digest_payload = {
        "dev": dev["rows"],
        "holdout_2025": holdout["rows"],
        "stress_2026": stress["rows"],
    }
    digest = hashlib.sha256(
        json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    out = {
        "model_id": MODEL_ID,
        "freeze_file": FREEZE_FILE,
        "scientific_gate": "PASS",
        "contract": {
            "target": "H=1 next-calendar-month average XAU/USD",
            "training_target": "Gold next-month log return",
            "representation": "CURRENT8",
            "training_start": TRAIN_START,
            "inner_validation_months": INNER_VAL_MONTHS,
            "alpha_grid": list(ALPHAS),
            "alpha_selection": "per-origin last-12 pre-target months; min relative cumulative price AE vs RW; lower-alpha tie break",
            "scaling": "StandardScaler fit on training fold only",
            "estimator": "sklearn.linear_model.Ridge",
            "random_split": "NONE",
            "database": "READ_ONLY",
            "primary_metric": "DEV_PRICE_SUM_ABS_ERROR",
            "2025_role": "LOCKED_REPORT_ONLY",
            "2026_role": "QUARANTINED_REPORT_ONLY",
            "metal_ablation": "NOT_IN_V1",
            "outer_target_metal_feature_access": "NONE",
        },
        "b0_audit": b0,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "authority_invariants_unchanged": invariant_same,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "dev": dev,
        "holdout_2025": holdout,
        "stress_2026": stress,
        "result_payload_sha256": digest,
        "context_only_comparators": {
            "catboost_price_dev_sumae": 1460.433935309605,
            "catboost_price_dev_direction_correct": 20,
            "random_forest_dev_sumae": 1491.550693715667,
            "random_forest_dev_direction_correct": 20,
            "note": "Existing frozen results only; not used to tune Ridge.",
        },
    }

    Path("gold_monthly_challenger_b_ridge_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("RIDGE_CHALLENGER_OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "b0_gate_pass": b0["gate_pass"],
        "dev_metrics": dev["metrics"],
        "dev_alpha_counts": dev["selected_alpha_counts"],
        "holdout_2025_metrics": holdout["metrics"],
        "stress_2026_metrics": stress["metrics"],
        "authority_invariants_unchanged": invariant_same,
        "result_payload_sha256": digest,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
