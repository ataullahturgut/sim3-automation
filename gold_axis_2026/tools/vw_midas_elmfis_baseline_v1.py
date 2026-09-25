from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.cluster import KMeans

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

N_RULES = 5
RIDGE_ALPHA = 1e-3
SPREAD_FLOOR = 0.20
KMEANS_N_INIT = 20
KMEANS_SEED = 1701


def arrays(samples, target):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < 30:
        raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")
    X = np.stack([samples[k][0] for k in keys])
    Y = np.stack([samples[k][1] for k in keys])
    tx = samples[target][0][None, :]

    xm, xs = X.mean(0), X.std(0)
    ym, ys = Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)

    return (
        keys,
        (X - xm) / xs,
        (Y - ym) / ys,
        (tx - xm) / xs,
        ym,
        ys,
    )


def fit_antecedents(X):
    km = KMeans(
        n_clusters=N_RULES,
        n_init=KMEANS_N_INIT,
        random_state=KMEANS_SEED,
        algorithm="lloyd",
    )
    labels = km.fit_predict(X)
    centers = np.asarray(km.cluster_centers_, float)

    global_std = np.std(X, axis=0)
    global_std = np.where(global_std < 1e-9, 1.0, global_std)

    spreads = np.empty_like(centers)
    for r in range(N_RULES):
        pts = X[labels == r]
        if len(pts) >= 2:
            s = np.std(pts, axis=0)
        else:
            s = global_std.copy()
        # Standardized-space floor prevents degenerate firing strengths
        # while retaining data-driven within-rule spreads.
        spreads[r] = np.maximum(s, SPREAD_FLOOR)

    return centers, spreads, labels


def normalized_firing(X, centers, spreads):
    # Bell/Gaussian membership used in the ELMFIS literature:
    # mu = exp(-((x-c)/alpha)^2)
    # Product AND is computed in log-space for numerical stability.
    z = (X[:, None, :] - centers[None, :, :]) / spreads[None, :, :]
    logw = -np.sum(z * z, axis=2)
    logw = logw - np.max(logw, axis=1, keepdims=True)
    w = np.exp(logw)
    den = np.sum(w, axis=1, keepdims=True)
    den = np.where(den < 1e-12, 1.0, den)
    return w / den


def tsk_design(X, centers, spreads):
    firing = normalized_firing(X, centers, spreads)
    basis = np.concatenate([np.ones((len(X), 1)), X], axis=1)
    # First-order TSK: normalized rule firing times [1, x_1, ..., x_d].
    return (firing[:, :, None] * basis[:, None, :]).reshape(len(X), -1)


def fit_consequents(X, Y, centers, spreads):
    H = tsk_design(X, centers, spreads)
    A = H.T @ H + RIDGE_ALPHA * np.eye(H.shape[1])
    B = H.T @ Y
    try:
        beta = np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        beta = np.linalg.pinv(A) @ B
    return beta


def predict_target(samples, target):
    keys, X, Y, tx, ym, ys = arrays(samples, target)
    centers, spreads, labels = fit_antecedents(X)
    beta = fit_consequents(X, Y, centers, spreads)
    pred_std = tsk_design(tx, centers, spreads) @ beta
    pred = pred_std[0] * ys + ym

    counts = [int(np.sum(labels == r)) for r in range(N_RULES)]
    return pred, len(keys), counts


def active_metrics(rows):
    m = dict(base.metrics(rows))
    actual = np.array([r["actual"] for r in rows], float)
    forecast = np.array([r["forecast"] for r in rows], float)
    ae = np.abs(forecast - actual)
    m["sum_abs_error"] = float(np.sum(ae))
    m["wape_pct"] = float(np.sum(ae) / np.sum(np.abs(actual)) * 100.0)
    m["direction_correct"] = int(
        sum(
            np.sign(r["forecast"] - r["rw"]) == np.sign(r["actual"] - r["rw"])
            for r in rows
        )
    )
    return m


def yearly(rows):
    years = sorted({r["target"][:4] for r in rows})
    return {y: active_metrics([r for r in rows if r["target"].startswith(y)]) for y in years}


def evaluate(bundle, cache, start, end):
    rows = []
    for target in base.month_range(start, end):
        pred, n, counts = predict_target(cache[target], target)
        origin = base.month_shift(target, -1)
        rows.append(
            {
                "target": target,
                "origin": origin,
                "train_rows": n,
                "rule_counts": counts,
                "pred_log_return_gold": float(pred[0]),
                "forecast": float(bundle.core_gold[origin] * math.exp(float(pred[0]))),
                "actual": float(bundle.core_gold[target]),
                "rw": float(bundle.core_gold[origin]),
            }
        )
    return rows


def read_authority_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    cache = {
        t: base.all_samples_at_origin(bundle, t, governed=True)
        for t in base.month_range(DEV_START, ST_END)
    }

    dev = evaluate(bundle, cache, DEV_START, DEV_END)
    tr = evaluate(bundle, cache, TR_START, TR_END)
    st = evaluate(bundle, cache, ST_START, ST_END)

    after = read_authority_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out = {
        "model_id": "VW_MIDAS_ELMFIS_BASELINE_V1",
        "canonical_elmfis": {
            "inputs": 8,
            "outputs": 4,
            "rules": N_RULES,
            "membership": "bell_gaussian_exp_minus_squared_distance",
            "and_operator": "product_logspace",
            "rule_normalization": True,
            "consequent": "first_order_TSK_linear",
            "consequent_fit": "analytic_ridge",
            "ridge_alpha": RIDGE_ALPHA,
            "antecedent_initialization": "training_only_kmeans",
            "spread_estimation": "within_rule_std_with_standardized_floor",
            "spread_floor": SPREAD_FLOOR,
        },
        "authority": {
            "database_access": "READ_ONLY",
            "feature_contract": "UNCHANGED_VW_MIDAS_8_FEATURE",
            "target": "NEXT_MONTH_AVERAGE_PRICE_VIA_4_RETURN_OUTPUTS",
            "random_split": "NONE",
            "selection_period": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_SELECTION",
            "primary_metrics": ["sum_abs_error", "direction_accuracy_pct"],
            "target_month_in_training": False,
            "authority_invariants_before": bundle.invariants_before,
            "authority_invariants_after": after,
        },
        "dev": {
            "metrics": active_metrics(dev),
            "yearly": yearly(dev),
            "rows": dev,
        },
        "transport_2025": {
            "metrics": active_metrics(tr),
            "rows": tr,
        },
        "stress_2026": {
            "metrics": active_metrics(st),
            "rows": st,
        },
    }

    Path("vw_midas_elmfis_baseline_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "model_id": out["model_id"],
                "dev": out["dev"]["metrics"],
                "transport_2025": out["transport_2025"]["metrics"],
                "stress_2026": out["stress_2026"]["metrics"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
