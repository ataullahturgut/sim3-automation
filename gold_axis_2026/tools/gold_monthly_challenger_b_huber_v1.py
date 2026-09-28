#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import StandardScaler

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "GOLD_MONTHLY_CHALLENGER_B_HUBER_V1"
FREEZE_FILE = "GOLD_MONTHLY_CHALLENGER_B_HUBER_FREEZE_2026-09-28.md"

TRAIN_START = "2010-05"
INNER_VAL_MONTHS = 12
MIN_INNER_TRAIN = 36
ALPHAS = (0.0, 0.0001, 0.001, 0.01, 0.1)
EPSILONS = (1.10, 1.20, 1.35, 1.50, 1.75, 2.00)

DEV_START, DEV_END = "2022-04", "2024-12"
HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

FRONTIER = [
    {"model":"ChHHO-ANFIS","family":"ANFIS","sum_abs_error":1413.029779,"direction_correct":23,"approximate":False},
    {"model":"RBFNN DE-ABC","family":"RBFNN","sum_abs_error":1415.8371,"direction_correct":25,"approximate":True},
    {"model":"GPR/MOGP LMC2_RBF_M32","family":"GPR/MOGP","sum_abs_error":1424.17,"direction_correct":19,"approximate":True},
    {"model":"FULL7 Equal ANN Ensemble","family":"ANN","sum_abs_error":1428.86,"direction_correct":22,"approximate":False},
    {"model":"REDUCED4 Equal ANN Ensemble","family":"ANN","sum_abs_error":1431.46,"direction_correct":24,"approximate":False},
    {"model":"SVR frozen parent","family":"SVR","sum_abs_error":1449.187363,"direction_correct":19,"approximate":False},
    {"model":"CatBoost PRICE","family":"Boosting","sum_abs_error":1460.433935309605,"direction_correct":20,"approximate":False},
    {"model":"Random Forest comparator","family":"RF","sum_abs_error":1491.550693715667,"direction_correct":20,"approximate":False},
    {"model":"Ridge V1","family":"Challenger-B","sum_abs_error":1520.9926031249222,"direction_correct":21,"approximate":False},
    {"model":"Elastic Net V1","family":"Challenger-B","sum_abs_error":1590.3570524947138,"direction_correct":16,"approximate":False},
]

def read_invariants(dsn: str) -> dict:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def current8_x_only(bundle, target: str, gpr_history: dict) -> np.ndarray:
    p = base.month_shift(target, -1)
    pp = base.month_shift(target, -2)
    z = base.gpr_norm(gpr_history, pp)
    x = []
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"MONTHLY_METAL_FEATURE_MISSING metal={metal} target={target}")
        x.extend((
            math.log(float(M[p]) / float(M[pp])),
            base.weighted_daily_return(bundle, metal, p, z),
        ))
    out = np.asarray(x, dtype=float)
    if out.shape != (8,) or not np.isfinite(out).all():
        raise RuntimeError(f"CURRENT8_FEATURE_GATE_FAIL target={target}")
    return out

def build_origin_data(bundle, target: str) -> dict:
    origin = base.month_shift(target, -1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh = bundle.gpr_vintages[origin]

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
    tr, va = keys[:split], keys[split:]

    Xtr = np.stack([samples[k][0] for k in tr])
    ytr = np.asarray([float(samples[k][1][0]) for k in tr], dtype=float)
    Xv = np.stack([samples[k][0] for k in va])
    prev_v = np.asarray([float(bundle.core_gold[base.month_shift(k, -1)]) for k in va], dtype=float)
    actual_v = np.asarray([float(bundle.core_gold[k]) for k in va], dtype=float)

    Xall = np.stack([samples[k][0] for k in keys])
    yall = np.asarray([float(samples[k][1][0]) for k in keys], dtype=float)
    xt = current8_x_only(bundle, target, gh).reshape(1, -1)

    for name, arr in {
        "Xtr": Xtr, "ytr": ytr, "Xv": Xv, "prev_v": prev_v,
        "actual_v": actual_v, "Xall": Xall, "yall": yall, "xt": xt,
    }.items():
        if not np.isfinite(arr).all():
            raise RuntimeError(f"NONFINITE_DATA target={target} field={name}")

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
        "inner_rw_sum_ae": float(np.abs(prev_v - actual_v).sum()),
        "Xall": Xall,
        "yall": yall,
        "xt": xt,
        "anchor_prev": float(bundle.core_gold[origin]),
    }

def fit_model(X, y, alpha: float, epsilon: float):
    scaler = StandardScaler(with_mean=True, with_std=True)
    Xs = scaler.fit_transform(X)
    model = HuberRegressor(
        epsilon=float(epsilon),
        alpha=float(alpha),
        fit_intercept=True,
        max_iter=5000,
        tol=1e-8,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(Xs, y)
    convergence_warnings = sum(issubclass(w.category, ConvergenceWarning) for w in caught)
    return scaler, model, convergence_warnings

def predict_return(X, y, Xtest, alpha, epsilon):
    scaler, model, wc = fit_model(X, y, alpha, epsilon)
    pred = np.asarray(model.predict(scaler.transform(Xtest)), dtype=float).reshape(-1)
    if not np.isfinite(pred).all() or np.any(np.abs(pred) >= 1.0):
        raise RuntimeError(f"PATHOLOGICAL_HUBER_PRED alpha={alpha} epsilon={epsilon}")
    return pred, model, wc

def choose_params(data):
    denom = max(float(data["inner_rw_sum_ae"]), 1e-12)
    scored = []
    for alpha in ALPHAS:
        for epsilon in EPSILONS:
            pred, _, wc = predict_return(
                data["Xtr"], data["ytr"], data["Xv"], alpha, epsilon
            )
            fc = data["prev_v"] * np.exp(pred)
            sae = float(np.abs(fc - data["actual_v"]).sum())
            scored.append({
                "alpha": float(alpha),
                "epsilon": float(epsilon),
                "inner_sum_abs_error": sae,
                "inner_relative_sum_abs_error_vs_rw": float(sae / denom),
                "convergence_warning_count": int(wc),
            })
    scored.sort(key=lambda r: (
        r["inner_relative_sum_abs_error_vs_rw"],
        r["alpha"],
        r["epsilon"],
    ))
    best = scored[0]
    return float(best["alpha"]), float(best["epsilon"]), scored

def forecast_one(bundle, target):
    d = build_origin_data(bundle, target)
    alpha, epsilon, scores = choose_params(d)
    scaler, model, wc = fit_model(d["Xall"], d["yall"], alpha, epsilon)
    pred = float(np.asarray(model.predict(scaler.transform(d["xt"]))).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred) >= 1.0:
        raise RuntimeError(f"PATHOLOGICAL_OUTER_PRED target={target}")

    forecast = float(d["anchor_prev"] * math.exp(pred))
    if target not in bundle.core_gold:
        raise RuntimeError(f"SCORING_ACTUAL_MISSING {target}")
    actual = float(bundle.core_gold[target])
    rw = float(d["anchor_prev"])

    outlier_fraction = float(np.mean(np.asarray(model.outliers_, dtype=bool)))
    return {
        "target": target,
        "origin": d["origin"],
        "representation": "CURRENT8",
        "feature_dim": 8,
        "train_first": d["keys"][0],
        "train_last": d["keys"][-1],
        "train_rows": len(d["keys"]),
        "inner_train_n": len(d["inner_train_keys"]),
        "inner_val_n": len(d["inner_val_keys"]),
        "inner_val_first": d["inner_val_keys"][0],
        "inner_val_last": d["inner_val_keys"][-1],
        "selected_alpha": alpha,
        "selected_epsilon": epsilon,
        "param_scores": scores,
        "pred_log_return_gold": pred,
        "forecast": forecast,
        "actual": actual,
        "rw": rw,
        "absolute_error": float(abs(forecast - actual)),
        "rw_absolute_error": float(abs(rw - actual)),
        "direction_correct": bool(
            int(np.sign(forecast - rw)) == int(np.sign(actual - rw))
        ),
        "huber_scale": float(model.scale_),
        "outlier_fraction_training": outlier_fraction,
        "convergence_warning_count_outer": int(wc),
    }

def metrics(rows):
    a = np.asarray([r["actual"] for r in rows], dtype=float)
    f = np.asarray([r["forecast"] for r in rows], dtype=float)
    rw = np.asarray([r["rw"] for r in rows], dtype=float)
    ae = np.abs(f - a)
    rwae = np.abs(rw - a)
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
        "relative_mae_vs_rw": float(ae.sum() / max(float(rwae.sum()), 1e-12)),
        "rw_sum_abs_error": float(rwae.sum()),
        "direction_correct": int(dc.sum()),
        "direction_accuracy_pct": float(dc.mean() * 100.0),
        "mean_outlier_fraction_training": float(np.mean([r["outlier_fraction_training"] for r in rows])),
        "outer_convergence_warnings": int(sum(r["convergence_warning_count_outer"] for r in rows)),
    }

def yearly(rows):
    return {
        y: metrics([r for r in rows if r["target"].startswith(y)])
        for y in sorted({r["target"][:4] for r in rows})
    }

def run_period(bundle, start, end, label):
    rows = []
    targets = list(base.month_range(start, end))
    for i, target in enumerate(targets, 1):
        row = forecast_one(bundle, target)
        rows.append(row)
        print(
            f"PROGRESS period={label} target={i}/{len(targets)} month={target} "
            f"alpha={row['selected_alpha']:.4g} eps={row['selected_epsilon']:.2f} "
            f"AE={row['absolute_error']:.6f} dir={int(row['direction_correct'])} "
            f"outfrac={row['outlier_fraction_training']:.4f}",
            flush=True,
        )
    return {
        "role": label,
        "metrics": metrics(rows),
        "yearly": yearly(rows),
        "selected_alpha_counts": dict(sorted(Counter(str(r["selected_alpha"]) for r in rows).items())),
        "selected_epsilon_counts": dict(sorted(Counter(str(r["selected_epsilon"]) for r in rows).items())),
        "rows": rows,
    }

def comparison(dev_metrics):
    huber = {
        "model":"Huber V1","family":"Challenger-B",
        "sum_abs_error":float(dev_metrics["sum_abs_error"]),
        "direction_correct":int(dev_metrics["direction_correct"]),
        "approximate":False,
    }
    all_rows = [dict(x) for x in FRONTIER] + [huber]
    ranked = sorted(all_rows, key=lambda r:(r["sum_abs_error"], -r["direction_correct"], r["model"]))
    for i, row in enumerate(ranked, 1):
        row["price_error_rank"] = i

    huber_rank = next(r["price_error_rank"] for r in ranked if r["model"]=="Huber V1")
    dominators = [
        r["model"] for r in all_rows
        if r["model"] != "Huber V1"
        and r["sum_abs_error"] <= huber["sum_abs_error"]
        and r["direction_correct"] >= huber["direction_correct"]
        and (r["sum_abs_error"] < huber["sum_abs_error"] or r["direction_correct"] > huber["direction_correct"])
    ]
    return {
        "ranking_by_primary_sumae": ranked,
        "huber_price_error_rank": huber_rank,
        "comparison_pool_n": len(ranked),
        "pareto_dominated_by": dominators,
        "pareto_nondominated_within_pool": len(dominators)==0,
        "note":"Ranking is by primary DEV SigmaAE only; project interpretation remains two-objective SigmaAE + direction.",
    }

def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    b0 = {
        "source_checks": bundle.source_checks,
        "current8_feature_contract": {
            "metals": list(base.METALS),
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
        raise RuntimeError("DEV_N_FAIL")
    holdout = run_period(bundle, HOLDOUT_START, HOLDOUT_END, "LOCKED_REPORT_ONLY")
    stress = run_period(bundle, STRESS_START, STRESS_END, "QUARANTINED_REPORT_ONLY")

    after = read_invariants(dsn)
    same = after == bundle.invariants_before
    if not same:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    comp = comparison(dev["metrics"])
    digest = hashlib.sha256(
        json.dumps({"dev":dev["rows"],"holdout":holdout["rows"],"stress":stress["rows"]},
                   sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()

    out = {
        "model_id": MODEL_ID,
        "freeze_file": FREEZE_FILE,
        "scientific_gate": "PASS",
        "contract": {
            "target":"H=1 next-calendar-month average XAU/USD",
            "training_target":"Gold next-month log return",
            "representation":"CURRENT8",
            "training_start":TRAIN_START,
            "inner_validation_months":INNER_VAL_MONTHS,
            "alpha_grid":list(ALPHAS),
            "epsilon_grid":list(EPSILONS),
            "parameter_selection":"per-origin last-12 pre-target months; min relative cumulative price AE vs RW",
            "tie_break":"lower objective, lower alpha, lower epsilon",
            "scaling":"StandardScaler fit on training fold only",
            "estimator":"sklearn.linear_model.HuberRegressor",
            "max_iter":5000,
            "tol":1e-8,
            "random_split":"NONE",
            "database":"READ_ONLY",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR",
            "2025_role":"LOCKED_REPORT_ONLY",
            "2026_role":"QUARANTINED_REPORT_ONLY",
            "metal_ablation":"NOT_IN_V1",
            "outer_target_metal_feature_access":"NONE",
        },
        "b0_audit": b0,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "authority_invariants_unchanged": same,
        "software": {
            "python":platform.python_version(),
            "numpy":np.__version__,
            "scikit_learn":sklearn.__version__,
        },
        "dev":dev,
        "holdout_2025":holdout,
        "stress_2026":stress,
        "challenger_a_comparison":comp,
        "result_payload_sha256":digest,
    }

    Path("gold_monthly_challenger_b_huber_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    print("HUBER_CHALLENGER_OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "b0_gate_pass":b0["gate_pass"],
        "dev_metrics":dev["metrics"],
        "dev_alpha_counts":dev["selected_alpha_counts"],
        "dev_epsilon_counts":dev["selected_epsilon_counts"],
        "huber_price_error_rank":comp["huber_price_error_rank"],
        "comparison_pool_n":comp["comparison_pool_n"],
        "pareto_dominated_by":comp["pareto_dominated_by"],
        "holdout_2025_metrics":holdout["metrics"],
        "stress_2026_metrics":stress["metrics"],
        "authority_invariants_unchanged":same,
        "result_payload_sha256":digest,
    },sort_keys=True),flush=True)

if __name__ == "__main__":
    main()
