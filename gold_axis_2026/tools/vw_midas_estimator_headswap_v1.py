from __future__ import annotations

import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import Ridge
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "VW_MIDAS_ESTIMATOR_HEADSWAP_V1"
DEV_START = "2022-04"
DEV_END = "2024-12"
TRANSPORT_START = "2025-01"
TRANSPORT_END = "2025-12"
STRESS_START = "2026-01"
STRESS_END = "2026-07"
WINDOWS = (None, 36, 24)

def cfg_key(family, window, params):
    w = "EXPANDING" if window is None else f"W{window}"
    p = ",".join(f"{k}={params[k]}" for k in sorted(params))
    return f"{family}|{w}|{p}"

def train_arrays(samples, target, window):
    keys = sorted(k for k in samples if k < target)
    if window is not None:
        keys = keys[-int(window):]
    if len(keys) < 24:
        raise RuntimeError(f"TRAINING_ROWS_TOO_FEW {target} n={len(keys)} window={window}")
    X = np.stack([samples[k][0] for k in keys])
    Y = np.stack([samples[k][1] for k in keys])
    tx = samples[target][0][None, :]
    xm, xs = X.mean(0), X.std(0)
    ym, ys = Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)
    return keys, (X - xm) / xs, (Y - ym) / ys, (tx - xm) / xs, ym, ys

def predict_gold(samples, target, family, window, params):
    keys, X, Y, tx, ym, ys = train_arrays(samples, target, window)
    d = X.shape[1]
    if family == "MSVR":
        model = base.MSVR(
            C=float(params["C"]),
            epsilon=float(params["epsilon"]),
            gamma=float(params["gamma_scale"]) / d,
        ).fit(X, Y)
        predz = model.predict(tx)[0]
        gold = float(predz[0] * ys[0] + ym[0])
    elif family == "KRR_RBF":
        model = KernelRidge(
            alpha=float(params["alpha"]),
            kernel="rbf",
            gamma=float(params["gamma_scale"]) / d,
        ).fit(X, Y)
        predz = np.asarray(model.predict(tx))[0]
        gold = float(predz[0] * ys[0] + ym[0])
    elif family == "RIDGE":
        model = Ridge(alpha=float(params["alpha"]), fit_intercept=True).fit(X, Y)
        predz = np.asarray(model.predict(tx))[0]
        gold = float(predz[0] * ys[0] + ym[0])
    elif family == "PLS2":
        ncomp = min(int(params["n_components"]), X.shape[1], max(1, X.shape[0] - 1))
        model = PLSRegression(n_components=ncomp, scale=False, max_iter=1000).fit(X, Y)
        predz = np.asarray(model.predict(tx))[0]
        gold = float(predz[0] * ys[0] + ym[0])
    elif family == "SVR_GOLD":
        model = SVR(
            kernel="rbf",
            C=float(params["C"]),
            epsilon=float(params["epsilon"]),
            gamma=float(params["gamma_scale"]) / d,
        ).fit(X, Y[:, 0])
        gold = float(model.predict(tx)[0] * ys[0] + ym[0])
    elif family == "GPR_GOLD":
        gamma = float(params["gamma_scale"]) / d
        length_scale = math.sqrt(1.0 / (2.0 * gamma))
        kernel = ConstantKernel(1.0, constant_value_bounds="fixed") * RBF(
            length_scale=length_scale, length_scale_bounds="fixed"
        )
        model = GaussianProcessRegressor(
            kernel=kernel,
            alpha=float(params["alpha"]),
            optimizer=None,
            normalize_y=False,
            random_state=0,
        ).fit(X, Y[:, 0])
        gold = float(model.predict(tx)[0] * ys[0] + ym[0])
    else:
        raise ValueError(family)
    return gold, len(keys)

def row_from_prediction(bundle, target, pred_log_return_gold, train_rows, family, window, params):
    p = base.month_shift(target, -1)
    return {
        "target": target,
        "origin": p,
        "family": family,
        "window": "EXPANDING" if window is None else int(window),
        "params": params,
        "pred_log_return_gold": float(pred_log_return_gold),
        "forecast": float(bundle.core_gold[p] * math.exp(float(pred_log_return_gold))),
        "actual": float(bundle.core_gold[target]),
        "rw": float(bundle.core_gold[p]),
        "train_rows": int(train_rows),
    }

def actual_gold_log_return(bundle, target):
    p = base.month_shift(target, -1)
    return float(math.log(bundle.monthly_metal["Gold"][target] / bundle.monthly_metal["Gold"][p]))

def candidate_grid():
    out = []
    for w in WINDOWS:
        for C in (0.1, 1.0, 10.0):
            for ep in (0.02, 0.05):
                for gm in (0.5, 1.0):
                    out.append(("MSVR", w, {"C": C, "epsilon": ep, "gamma_scale": gm}))
        for alpha in (0.01, 0.1, 1.0):
            for gm in (0.5, 1.0, 2.0):
                out.append(("KRR_RBF", w, {"alpha": alpha, "gamma_scale": gm}))
        for alpha in (0.01, 0.1, 1.0, 10.0):
            out.append(("RIDGE", w, {"alpha": alpha}))
        for nc in (1, 2, 4, 6):
            out.append(("PLS2", w, {"n_components": nc}))
        for C in (0.1, 1.0, 10.0):
            for ep in (0.02, 0.05):
                for gm in (0.5, 1.0):
                    out.append(("SVR_GOLD", w, {"C": C, "epsilon": ep, "gamma_scale": gm}))
        for alpha in (0.01, 0.1, 1.0):
            for gm in (0.5, 1.0):
                out.append(("GPR_GOLD", w, {"alpha": alpha, "gamma_scale": gm}))
    return out

def build_samples_cache(bundle):
    targets = list(base.month_range(DEV_START, STRESS_END))
    return {t: base.all_samples_at_origin(bundle, t, governed=True) for t in targets}

def score_candidate_dev(bundle, cache, spec):
    family, window, params = spec
    errs = []
    rows = []
    for t in base.month_range(DEV_START, DEV_END):
        pred, n = predict_gold(cache[t], t, family, window, params)
        errs.append(abs(pred - actual_gold_log_return(bundle, t)))
        rows.append(row_from_prediction(bundle, t, pred, n, family, window, params))
    return float(np.mean(errs)), rows

def select_family_specs(bundle, cache):
    grids = candidate_grid()
    by_family = {}
    all_scores = []
    for spec in grids:
        objective, rows = score_candidate_dev(bundle, cache, spec)
        family, window, params = spec
        rec = {
            "family": family,
            "window": "EXPANDING" if window is None else int(window),
            "params": params,
            "dev_mean_abs_gold_log_return_error": objective,
            "dev_price_metrics": base.metrics(rows),
            "_spec": spec,
        }
        all_scores.append(rec)
        by_family.setdefault(family, []).append(rec)

    selected = {}
    for family, recs in by_family.items():
        recs.sort(key=lambda r: (
            r["dev_mean_abs_gold_log_return_error"],
            str(r["window"]),
            json.dumps(r["params"], sort_keys=True),
        ))
        selected[family] = recs[0]

    overall = sorted(
        selected.values(),
        key=lambda r: (
            r["dev_mean_abs_gold_log_return_error"],
            r["family"],
        ),
    )[0]
    return selected, overall, all_scores

def evaluate_fixed_spec(bundle, cache, spec, start, end):
    family, window, params = spec
    rows = []
    for t in base.month_range(start, end):
        pred, n = predict_gold(cache[t], t, family, window, params)
        rows.append(row_from_prediction(bundle, t, pred, n, family, window, params))
    return rows

def metric_bundle(rows):
    if not rows:
        return {}
    return {
        "metrics": base.metrics(rows),
        "yearly": base.yearly(rows),
        "rows": rows,
    }

def strip_internal(rec):
    return {k: v for k, v in rec.items() if k != "_spec"}


def build_september_2026_pls2_reconstruction(bundle):
    # Historical-origin reconstruction only. Uses the exact frozen August four-metal
    # snapshot that underlies the governed VW/MSVR September reference.
    import csv
    snap_path = Path("gold_axis_2026/data_pipeline/myfxbook_four_metal_august_2026_reconstruction_snapshot.csv")
    rows = list(csv.DictReader(snap_path.open(encoding="utf-8")))
    if not rows:
        raise RuntimeError("AUGUST_SNAPSHOT_EMPTY")
    for metal in base.METALS:
        vals = np.array([float(r[metal]) for r in rows], float)
        bundle.daily_month_values[metal]["2026-08"] = vals
        bundle.monthly_metal[metal]["2026-08"] = float(vals.mean())

    # Build all matured training samples through Aug-2026 using the governed
    # 2026-08 origin vintage. Then construct Sep feature vector without Sep target data.
    samples = base.all_samples_at_origin(bundle, "2026-08", governed=True)
    p, pp = "2026-08", "2026-07"
    hist = bundle.gpr_vintages[p]
    z = base.gpr_norm(hist, pp)
    x = []
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        x.extend((
            math.log(M[p] / M[pp]),
            base.weighted_daily_return(bundle, metal, p, z),
        ))
    samples["2026-09"] = (np.array(x, float), np.zeros(4, float))

    pred, train_n = predict_gold(
        samples,
        "2026-09",
        "PLS2",
        None,
        {"n_components": 4},
    )
    gold_anchor = float(bundle.monthly_metal["Gold"]["2026-08"])
    return {
        "target": "2026-09",
        "origin": "2026-08-31T21:00:00Z",
        "evidence_class": "HISTORICAL_ORIGIN_RECONSTRUCTION_NOT_PROSPECTIVE",
        "family": "PLS2",
        "window": "EXPANDING",
        "params": {"n_components": 4},
        "train_rows": int(train_n),
        "august_common_days": len(rows),
        "gold_anchor_august_snapshot_mean": gold_anchor,
        "pred_log_return_gold": float(pred),
        "forecast_usd_oz": float(gold_anchor * math.exp(float(pred))),
        "uses_september_observations": False,
        "source_snapshot": str(snap_path),
    }

def run():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL is required")

    bundle = base.load_data(dsn)

    # Exact current MSVR identity reproduction: sanity-only, never used to tune challengers.
    current_rows = base.build_governed_nested(bundle)
    current_metrics = base.metrics(current_rows)
    current_yearly = base.yearly(current_rows)

    cache = build_samples_cache(bundle)
    selected, overall, all_scores = select_family_specs(bundle, cache)

    families = {}
    for family, rec in selected.items():
        spec = rec["_spec"]
        dev_rows = evaluate_fixed_spec(bundle, cache, spec, DEV_START, DEV_END)
        transport_rows = evaluate_fixed_spec(bundle, cache, spec, TRANSPORT_START, TRANSPORT_END)
        stress_rows = evaluate_fixed_spec(bundle, cache, spec, STRESS_START, STRESS_END)
        families[family] = {
            "selection": strip_internal(rec),
            "dev_2022_04_to_2024_12": metric_bundle(dev_rows),
            "locked_2025_transport": metric_bundle(transport_rows),
            "retrospective_2026_stress": metric_bundle(stress_rows),
        }

    best_family = overall["family"]
    selected_counts = Counter(
        (r["cfg"][0], r["cfg"][1], r["cfg"][2]) for r in current_rows
    )

    # Deterministic compact leaderboard; ordering is PRE-2025 development only.
    leaderboard = []
    for family, block in families.items():
        leaderboard.append({
            "family": family,
            "selected_window": block["selection"]["window"],
            "selected_params": block["selection"]["params"],
            "dev_logret_mae": block["selection"]["dev_mean_abs_gold_log_return_error"],
            "dev_mape_pct": block["dev_2022_04_to_2024_12"]["metrics"]["mape_pct"],
            "transport_2025_mape_pct": block["locked_2025_transport"]["metrics"]["mape_pct"],
            "stress_2026_mape_pct": block["retrospective_2026_stress"]["metrics"]["mape_pct"],
            "transport_2025_relative_mae_vs_rw": block["locked_2025_transport"]["metrics"]["relative_mae_vs_rw"],
            "stress_2026_relative_mae_vs_rw": block["retrospective_2026_stress"]["metrics"]["relative_mae_vs_rw"],
            "transport_2025_direction_accuracy_pct": block["locked_2025_transport"]["metrics"]["direction_accuracy_pct"],
            "stress_2026_direction_accuracy_pct": block["retrospective_2026_stress"]["metrics"]["direction_accuracy_pct"],
        })
    leaderboard.sort(key=lambda x: (x["dev_logret_mae"], x["family"]))

    # Window sensitivity is diagnostic only. Hyperparameters stay frozen at the
    # PRE-2025 selected family values; 2025/2026 never choose a window.
    window_sensitivity = {}
    for family, rec in selected.items():
        params = dict(rec["_spec"][2])
        window_sensitivity[family] = {}
        for w0 in WINDOWS:
            spec0 = (family, w0, params)
            dev0 = evaluate_fixed_spec(bundle, cache, spec0, DEV_START, DEV_END)
            tr0 = evaluate_fixed_spec(bundle, cache, spec0, TRANSPORT_START, TRANSPORT_END)
            st0 = evaluate_fixed_spec(bundle, cache, spec0, STRESS_START, STRESS_END)
            label = "EXPANDING" if w0 is None else f"W{w0}"
            window_sensitivity[family][label] = {
                "dev_mape_pct": base.metrics(dev0)["mape_pct"],
                "transport_2025_mape_pct": base.metrics(tr0)["mape_pct"],
                "stress_2026_mape_pct": base.metrics(st0)["mape_pct"],
                "stress_2026_relative_mae_vs_rw": base.metrics(st0)["relative_mae_vs_rw"],
                "stress_2026_direction_accuracy_pct": base.metrics(st0)["direction_accuracy_pct"],
            }

    sep_pls2 = build_september_2026_pls2_reconstruction(bundle)

    result = {
        "model_id": MODEL_ID,
        "scope": "RESEARCH_ONLY_ESTIMATOR_HEAD_SWAP",
        "authority": {
            "base_branch": "gold-r4-direction-engine",
            "base_commit": "66fe1bac635e6135128d478aab9a6cba74883948",
            "database_access": "READ_ONLY",
            "feature_contract": "UNCHANGED_FROM_VW_MIDAS_MSVR_SUCCESSOR_V1",
            "target_contract": "UNCHANGED_H1_NEXT_MONTH_AVERAGE_XAU_USD",
            "selection_boundary": "NO_2025_OR_2026_OUTCOME_USED_FOR_HYPERPARAMETER_WINDOW_OR_FAMILY_SELECTION",
            "2025_role": "LOCKED_RETROSPECTIVE_TRANSPORT",
            "2026_role": "RETROSPECTIVE_STRESS_DIAGNOSTIC_ONLY",
        },
        "source_checks": bundle.source_checks,
        "september_2026_pls2_reconstruction": sep_pls2,
        "current_msvr_exact_reproduction": {
            "metrics_2023_01_to_2026_07": current_metrics,
            "yearly": current_yearly,
            "selected_cfg_counts": {str(k): v for k, v in sorted(selected_counts.items())},
        },
        "development_selection": {
            "period": f"{DEV_START}..{DEV_END}",
            "objective": "mean_absolute_gold_log_return_error",
            "selected_by_family": {k: strip_internal(v) for k, v in selected.items()},
            "pre2025_dev_best_family": best_family,
            "pre2025_dev_best_spec": strip_internal(overall),
        },
        "family_results": families,
        "window_sensitivity_fixed_pre2025_params": window_sensitivity,
        "leaderboard_pre2025_only": leaderboard,
        "interpretation_guard": [
            "2025 and 2026 results do not select or tune any candidate.",
            "2026 is not pristine OOS because the weakness was already researcher-visible before this experiment.",
            "A 2026 improvement is diagnostic evidence only; promotion requires future untouched origins.",
        ],
    }

    Path("vw_midas_estimator_headswap_v1_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Small CSV for inspection.
    import csv
    with open("vw_midas_estimator_headswap_v1_leaderboard.csv", "w", newline="", encoding="utf-8") as f:
        fields = [
            "family","selected_window","selected_params","dev_logret_mae","dev_mape_pct",
            "transport_2025_mape_pct","stress_2026_mape_pct",
            "transport_2025_relative_mae_vs_rw","stress_2026_relative_mae_vs_rw",
            "transport_2025_direction_accuracy_pct","stress_2026_direction_accuracy_pct"
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in leaderboard:
            rr = dict(row)
            rr["selected_params"] = json.dumps(rr["selected_params"], sort_keys=True)
            w.writerow(rr)

    print(json.dumps({
        "september_2026_pls2_forecast": sep_pls2["forecast_usd_oz"],
        "current_msvr_mape": current_metrics["mape_pct"],
        "current_msvr_2026_mape": current_yearly["2026"]["mape_pct"],
        "pre2025_dev_best_family": best_family,
        "leaderboard": leaderboard,
    }, sort_keys=True))

if __name__ == "__main__":
    run()
