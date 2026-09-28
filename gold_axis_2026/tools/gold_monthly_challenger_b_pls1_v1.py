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
from sklearn.cross_decomposition import PLSRegression

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "GOLD_MONTHLY_CHALLENGER_B_PLS1_V1"
FREEZE_FILE = "GOLD_MONTHLY_CHALLENGER_B_PLS1_FREEZE_2026-09-28.md"

TRAIN_START = "2010-05"
INNER_VAL_MONTHS = 12
MIN_INNER_TRAIN = 36
COMPONENTS = tuple(range(1, 9))

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
    {"model":"Huber V1","family":"Challenger-B","sum_abs_error":1530.1299616481554,"direction_correct":20,"approximate":False},
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

def fit_model(X, y, n_components: int):
    if n_components > min(X.shape[0], X.shape[1]):
        raise RuntimeError(f"PLS_COMPONENTS_INVALID n={n_components} shape={X.shape}")
    model = PLSRegression(
        n_components=int(n_components),
        scale=True,
        max_iter=2000,
        tol=1e-8,
        copy=True,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(X, y.reshape(-1, 1))
    return model, len(caught), [str(w.message) for w in caught]

def predict_return(X, y, Xtest, n_components):
    model, warning_count, warning_messages = fit_model(X, y, n_components)
    pred = np.asarray(model.predict(Xtest), dtype=float).reshape(-1)
    if not np.isfinite(pred).all() or np.any(np.abs(pred) >= 1.0):
        raise RuntimeError(f"PATHOLOGICAL_PLS1_PRED components={n_components}")
    return pred, model, warning_count, warning_messages

def choose_components(data):
    denom = max(float(data["inner_rw_sum_ae"]), 1e-12)
    scored = []
    for ncomp in COMPONENTS:
        pred, _, wc, wm = predict_return(
            data["Xtr"], data["ytr"], data["Xv"], ncomp
        )
        fc = data["prev_v"] * np.exp(pred)
        sae = float(np.abs(fc - data["actual_v"]).sum())
        scored.append({
            "n_components": int(ncomp),
            "inner_sum_abs_error": sae,
            "inner_relative_sum_abs_error_vs_rw": float(sae / denom),
            "warning_count": int(wc),
            "warning_messages": wm,
        })
    scored.sort(key=lambda r: (
        r["inner_relative_sum_abs_error_vs_rw"],
        r["n_components"],
    ))
    return int(scored[0]["n_components"]), scored

def forecast_one(bundle, target):
    d = build_origin_data(bundle, target)
    ncomp, scores = choose_components(d)
    model, wc, wm = fit_model(d["Xall"], d["yall"], ncomp)
    pred = float(np.asarray(model.predict(d["xt"]), dtype=float).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred) >= 1.0:
        raise RuntimeError(f"PATHOLOGICAL_OUTER_PRED target={target}")

    forecast = float(d["anchor_prev"] * math.exp(pred))
    if target not in bundle.core_gold:
        raise RuntimeError(f"SCORING_ACTUAL_MISSING {target}")
    actual = float(bundle.core_gold[target])
    rw = float(d["anchor_prev"])

    coef = np.asarray(model.coef_, dtype=float).reshape(-1)
    n_iter = getattr(model, "n_iter_", [])
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
        "selected_n_components": ncomp,
        "component_scores": scores,
        "pred_log_return_gold": pred,
        "forecast": forecast,
        "actual": actual,
        "rw": rw,
        "absolute_error": float(abs(forecast - actual)),
        "rw_absolute_error": float(abs(rw - actual)),
        "direction_correct": bool(
            int(np.sign(forecast - rw)) == int(np.sign(actual - rw))
        ),
        "coef_l2_norm": float(np.linalg.norm(coef)),
        "n_iter_per_component": [int(v) for v in n_iter],
        "warning_count_outer": int(wc),
        "warning_messages_outer": wm,
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
        "mean_coef_l2_norm": float(np.mean([r["coef_l2_norm"] for r in rows])),
        "outer_warning_count": int(sum(r["warning_count_outer"] for r in rows)),
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
            f"ncomp={row['selected_n_components']} AE={row['absolute_error']:.6f} "
            f"dir={int(row['direction_correct'])} warnings={row['warning_count_outer']}",
            flush=True,
        )
    return {
        "role": label,
        "metrics": metrics(rows),
        "yearly": yearly(rows),
        "selected_component_counts": dict(sorted(Counter(str(r["selected_n_components"]) for r in rows).items())),
        "rows": rows,
    }

def comparison(dev_metrics):
    pls = {
        "model":"PLS1 V1","family":"Challenger-B",
        "sum_abs_error":float(dev_metrics["sum_abs_error"]),
        "direction_correct":int(dev_metrics["direction_correct"]),
        "approximate":False,
    }
    all_rows = [dict(x) for x in FRONTIER] + [pls]
    ranked = sorted(all_rows, key=lambda r:(r["sum_abs_error"], -r["direction_correct"], r["model"]))
    for i, row in enumerate(ranked, 1):
        row["price_error_rank"] = i

    rank = next(r["price_error_rank"] for r in ranked if r["model"]=="PLS1 V1")
    dominators = [
        r["model"] for r in all_rows
        if r["model"] != "PLS1 V1"
        and r["sum_abs_error"] <= pls["sum_abs_error"]
        and r["direction_correct"] >= pls["direction_correct"]
        and (r["sum_abs_error"] < pls["sum_abs_error"] or r["direction_correct"] > pls["direction_correct"])
    ]
    return {
        "ranking_by_primary_sumae": ranked,
        "pls1_price_error_rank": rank,
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
            "training_target":"Gold next-month log return only (PLS1)",
            "representation":"CURRENT8",
            "training_start":TRAIN_START,
            "inner_validation_months":INNER_VAL_MONTHS,
            "n_components_grid":list(COMPONENTS),
            "component_selection":"per-origin last-12 pre-target months; min relative cumulative price AE vs RW",
            "tie_break":"lower objective, fewer components",
            "scaling":"PLSRegression(scale=True), fit on training fold only; no external scaler",
            "estimator":"sklearn.cross_decomposition.PLSRegression",
            "max_iter":2000,
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

    Path("gold_monthly_challenger_b_pls1_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    print("PLS1_CHALLENGER_OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "b0_gate_pass":b0["gate_pass"],
        "dev_metrics":dev["metrics"],
        "dev_component_counts":dev["selected_component_counts"],
        "pls1_price_error_rank":comp["pls1_price_error_rank"],
        "comparison_pool_n":comp["comparison_pool_n"],
        "pareto_dominated_by":comp["pareto_dominated_by"],
        "holdout_2025_metrics":holdout["metrics"],
        "stress_2026_metrics":stress["metrics"],
        "authority_invariants_unchanged":same,
        "result_payload_sha256":digest,
    },sort_keys=True),flush=True)

if __name__ == "__main__":
    main()
