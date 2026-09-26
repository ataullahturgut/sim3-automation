from __future__ import annotations

import json, math, os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.cluster import KMeans

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as metrics_mod

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

N_CENTERS = 8
MIN_TRAIN = 30
WIDTH_FLOOR = 0.10
WIDTH_CEIL = 10.0
KMEANS_N_INIT = 20


def scale_fit(X, Y):
    xm, xs = X.mean(0), X.std(0)
    ym, ys = Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)
    return xm, xs, ym, ys


def fit_centers_widths(X, seed):
    if len(X) < N_CENTERS:
        raise RuntimeError(f"TRAIN_LT_CENTERS n={len(X)} k={N_CENTERS}")
    km = KMeans(n_clusters=N_CENTERS, random_state=seed, n_init=KMEANS_N_INIT)
    labels = km.fit_predict(X)
    centers = km.cluster_centers_.astype(float)

    widths = np.zeros(N_CENTERS, float)
    for j in range(N_CENTERS):
        pts = X[labels == j]
        if len(pts) >= 2:
            d2 = np.sum((pts - centers[j]) ** 2, axis=1)
            w = float(np.sqrt(np.mean(d2)))
        else:
            other = np.delete(centers, j, axis=0)
            w = float(np.min(np.linalg.norm(other - centers[j], axis=1))) if len(other) else 1.0
        widths[j] = w

    positive = widths[np.isfinite(widths) & (widths > 1e-9)]
    fallback = float(np.median(positive)) if len(positive) else 1.0
    widths = np.where(np.isfinite(widths) & (widths > 1e-9), widths, fallback)
    widths = np.clip(widths, WIDTH_FLOOR, WIDTH_CEIL)
    counts = [int(np.sum(labels == j)) for j in range(N_CENTERS)]
    return centers, widths, counts


def design(X, centers, widths):
    diff = X[:, None, :] - centers[None, :, :]
    d2 = np.sum(diff * diff, axis=2)
    phi = np.exp(-0.5 * d2 / (widths[None, :] ** 2))
    return np.c_[np.ones(len(X)), phi]


def fit_ols(Phi, Y):
    beta, residuals, rank, s = np.linalg.lstsq(Phi, Y, rcond=None)
    cond = float(np.linalg.cond(Phi))
    return beta, {
        "design_rank": int(rank),
        "design_cols": int(Phi.shape[1]),
        "design_condition_number": cond,
        "min_singular_value": float(np.min(s)) if len(s) else 0.0,
        "max_singular_value": float(np.max(s)) if len(s) else 0.0,
    }


def predict_target(samples, target):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < MIN_TRAIN:
        raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")

    X0 = np.stack([samples[k][0] for k in keys])
    Y0 = np.stack([samples[k][1] for k in keys])
    tx0 = samples[target][0][None, :]

    xm, xs, ym, ys = scale_fit(X0, Y0)
    X = (X0 - xm) / xs
    Y = (Y0 - ym) / ys
    tx = (tx0 - xm) / xs

    seed = 91001 + sum(map(ord, target))
    centers, widths, counts = fit_centers_widths(X, seed)
    Phi = design(X, centers, widths)
    beta, diag = fit_ols(Phi, Y)
    pred_std = design(tx, centers, widths) @ beta
    pred = pred_std[0] * ys + ym

    diag.update({
        "train_rows": len(keys),
        "kmeans_seed": seed,
        "n_centers": N_CENTERS,
        "cluster_counts": counts,
        "width_min": float(np.min(widths)),
        "width_median": float(np.median(widths)),
        "width_max": float(np.max(widths)),
        "output_fit": "ordinary_least_squares_with_intercept",
        "regularization": "NONE",
    })
    return pred, diag


def evaluate(bundle, cache, start, end):
    rows = []
    for target in base.month_range(start, end):
        pred, diag = predict_target(cache[target], target)
        origin = base.month_shift(target, -1)
        rows.append({
            "target": target,
            "origin": origin,
            "model": "VANILLA_RBFNN",
            "rbfnn_diag": diag,
            "pred_log_return_gold": float(pred[0]),
            "forecast": float(bundle.core_gold[origin] * math.exp(float(pred[0]))),
            "actual": float(bundle.core_gold[target]),
            "rw": float(bundle.core_gold[origin]),
        })
    return rows


def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def finite_gate(rows):
    for r in rows:
        if not math.isfinite(r["forecast"]):
            raise RuntimeError(f"NONFINITE_FORECAST {r['target']}")
        if abs(r["pred_log_return_gold"]) >= 1:
            raise RuntimeError(f"PATHOLOGICAL_RETURN {r['target']} {r['pred_log_return_gold']}")


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
    finite_gate(dev + tr + st)

    after = read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out = {
        "model_id": "VW_MIDAS_RBFNN_VANILLA_V1",
        "canonical_rbfnn": {
            "inputs": 8,
            "outputs": 4,
            "hidden_basis": "Gaussian radial basis",
            "centers": N_CENTERS,
            "center_learning": "deterministic_kmeans_on_all_pre_target_training_rows",
            "width_learning": "per_cluster_RMS_distance_to_center; singleton_fallback_nearest_center_distance",
            "output_layer": "4-output linear OLS with intercept",
            "regularization": "NONE",
            "metaheuristic": "NONE",
            "hyperparameter_search": "NONE",
        },
        "authority": {
            "database_access": "READ_ONLY",
            "feature_contract": "UNCHANGED_VW_MIDAS_8_FEATURE",
            "target": "H=1 next-calendar-month average XAU/USD price via 4 jointly modeled metal returns",
            "random_split": "NONE",
            "target_month_in_training": False,
            "selection_period": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_SELECTION",
            "source_checks": bundle.source_checks,
            "authority_invariants_before": bundle.invariants_before,
            "authority_invariants_after": after,
        },
        "dev": {
            "metrics": metrics_mod.active_metrics(dev),
            "yearly": metrics_mod.yearly(dev),
            "rows": dev,
        },
        "transport_2025": {
            "metrics": metrics_mod.active_metrics(tr),
            "rows": tr,
        },
        "stress_2026": {
            "metrics": metrics_mod.active_metrics(st),
            "rows": st,
        },
    }

    Path("vw_midas_rbfnn_vanilla_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "dev": out["dev"]["metrics"],
        "transport_2025": out["transport_2025"]["metrics"],
        "stress_2026": out["stress_2026"]["metrics"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
