#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
import psycopg
import sklearn
from sklearn.svm import SVR

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TRAIN_START = "2010-03"
FEATURES = (
    "GOLD_MR","GOLD_VW","SILVER_MR","SILVER_VW",
    "PLATINUM_MR","PLATINUM_VW","PALLADIUM_MR","PALLADIUM_VW",
)

SPECS = {
    "LINEAR_SVR": {
        "kernel": "linear",
        "C": 1.0,
        "epsilon": 0.1,
        "shrinking": True,
        "tol": 1e-3,
    },
    "RBF_SVR": {
        "kernel": "rbf",
        "C": 1.0,
        "epsilon": 0.1,
        "gamma": "scale",
        "shrinking": True,
        "tol": 1e-3,
    },
}


def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def current8_x(bundle, target, gpr_history):
    """Build target features from t-1/t-2 only; never reads target-month actual."""
    p = base.month_shift(target, -1)
    pp = base.month_shift(target, -2)
    z = base.gpr_norm(gpr_history, pp)
    x = []
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"FEATURE_MONTH_MISSING metal={metal} target={target}")
        x.extend((
            math.log(M[p] / M[pp]),
            base.weighted_daily_return(bundle, metal, p, z),
        ))
    x = np.asarray(x, float)
    if x.shape != (8,) or not np.isfinite(x).all():
        raise RuntimeError(f"TARGET_X_FAIL target={target} shape={x.shape}")
    return x


def training_arrays_at_origin(bundle, target):
    """Training rows end at t-1. No target-month label is constructed."""
    origin = base.month_shift(target, -1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING origin={origin}")
    gh = bundle.gpr_vintages[origin]

    keys, xs, ys = [], [], []
    for hist_target in base.month_range(TRAIN_START, origin):
        try:
            x, y4 = base.sample_for_target(bundle, hist_target, gh, True)
        except RuntimeError:
            continue
        keys.append(hist_target)
        xs.append(np.asarray(x, float))
        ys.append(float(y4[0]))

    if len(keys) < 30:
        raise RuntimeError(f"TRAIN_TOO_SMALL target={target} n={len(keys)}")

    X = np.stack(xs)
    y = np.asarray(ys, float)
    tx = current8_x(bundle, target, gh).reshape(1, -1)

    if X.shape[1] != 8 or tx.shape[1] != 8:
        raise RuntimeError(f"FEATURE_COUNT_FAIL target={target}")
    if not (np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(tx).all()):
        raise RuntimeError(f"NONFINITE_INPUT target={target}")

    return keys, X, y, tx


def scale_train_only(X, y, tx):
    xm = X.mean(axis=0)
    xs = X.std(axis=0, ddof=0)
    xs = np.where(xs < 1e-12, 1.0, xs)

    ym = float(y.mean())
    ys = float(y.std(ddof=0))
    if ys < 1e-12:
        ys = 1.0

    Xs = (X - xm) / xs
    txs = (tx - xm) / xs
    ys_train = (y - ym) / ys

    if not (np.isfinite(Xs).all() and np.isfinite(txs).all() and np.isfinite(ys_train).all()):
        raise RuntimeError("SCALING_NONFINITE")

    return Xs, ys_train, txs, {
        "x_mean": xm.tolist(),
        "x_std": xs.tolist(),
        "y_mean": ym,
        "y_std": ys,
    }


def predict_one(bundle, target, name):
    keys, X, y, tx = training_arrays_at_origin(bundle, target)
    Xs, yz, txs, scaler = scale_train_only(X, y, tx)

    model = SVR(**SPECS[name])
    model.fit(Xs, yz)
    pred_z = float(model.predict(txs)[0])
    pred = float(pred_z * scaler["y_std"] + scaler["y_mean"])

    if not math.isfinite(pred) or abs(pred) >= 1.0:
        raise RuntimeError(f"PATHOLOGICAL_PRED model={name} target={target} pred={pred}")

    # Forecast is completed before the target actual is read.
    origin = base.month_shift(target, -1)
    previous = float(bundle.core_gold[origin])
    forecast = float(previous * math.exp(pred))

    if target not in bundle.core_gold:
        raise RuntimeError(f"TARGET_ACTUAL_MISSING target={target}")
    actual = float(bundle.core_gold[target])

    pred_dir = int(np.sign(forecast - previous))
    actual_dir = int(np.sign(actual - previous))

    return {
        "target": target,
        "origin": origin,
        "model": name,
        "train_rows": len(keys),
        "train_first": keys[0],
        "train_last": keys[-1],
        "scaling": {
            "x": "TRAIN_ONLY_STANDARDIZATION",
            "y": "TRAIN_ONLY_STANDARDIZATION",
            "y_mean": scaler["y_mean"],
            "y_std": scaler["y_std"],
        },
        "pred_standardized_gold_log_return": pred_z,
        "pred_log_return_gold": pred,
        "forecast": forecast,
        "actual": actual,
        "rw": previous,
        "absolute_error": float(abs(forecast - actual)),
        "pred_direction": pred_dir,
        "actual_direction": actual_dir,
        "direction_correct": bool(pred_dir == actual_dir),
    }


def metrics(rows):
    a = np.asarray([r["actual"] for r in rows], float)
    f = np.asarray([r["forecast"] for r in rows], float)
    rw = np.asarray([r["rw"] for r in rows], float)
    ae = np.abs(f - a)
    rw_ae = np.abs(rw - a)
    d = np.asarray([r["direction_correct"] for r in rows], bool)
    wi = int(np.argmax(ae))
    return {
        "n": len(rows),
        "sum_abs_error": float(ae.sum()),
        "mae": float(ae.mean()),
        "rmse": float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct": float(np.mean(ae / np.maximum(np.abs(a), 1e-12)) * 100.0),
        "wape_pct": float(ae.sum() / np.maximum(np.abs(a).sum(), 1e-12) * 100.0),
        "median_ae": float(np.median(ae)),
        "worst_ae": float(ae[wi]),
        "worst_month": rows[wi]["target"],
        "relative_mae_vs_rw": float(ae.sum() / max(float(rw_ae.sum()), 1e-12)),
        "direction_correct": int(d.sum()),
        "direction_accuracy_pct": float(d.mean() * 100.0),
        "rw_sum_abs_error": float(rw_ae.sum()),
    }


def yearly(rows):
    out = {}
    for yy in ("2022", "2023", "2024"):
        rr = [r for r in rows if r["target"].startswith(yy)]
        out[yy] = metrics(rr)
    return out


def evaluate(bundle, name):
    rows = [predict_one(bundle, t, name) for t in base.month_range(DEV_START, DEV_END)]
    return {
        "spec": SPECS[name],
        "metrics": metrics(rows),
        "yearly": yearly(rows),
        "rows": rows,
    }


def run_models(bundle):
    return {name: evaluate(bundle, name) for name in SPECS}


def payload_hash(models):
    compact = {}
    for name in sorted(models):
        compact[name] = [
            {
                k: r[k]
                for k in (
                    "target","origin","train_rows","train_first","train_last",
                    "pred_log_return_gold","forecast","actual","rw","direction_correct"
                )
            }
            for r in models[name]["rows"]
        ]
    return hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def report_markdown(out):
    lines = [
        "# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 1 CANONICAL BASELINE",
        "",
        "Date: 2026-09-28",
        "Status: **COMPLETE / SCIENTIFIC GATE PASS**",
        "",
        "## Frozen protocol",
        "- DEV only: 2022-04..2024-12, n=33.",
        "- CURRENT8 origin-safe predictors.",
        "- Single-output next-month Gold log return.",
        "- Training-only X and y standardization.",
        "- Price reconstruction from previous completed-month Gold average.",
        "- epsilon-SVR; C=1.0; epsilon=0.1.",
        "- Linear kernel and RBF kernel (gamma=scale).",
        "- Random split: NONE.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- DB: READ_ONLY.",
        "",
        "## DEV results",
        "",
        "| Rank | Model | SigmaAE | MAE | RMSE | MAPE | WAPE | Rel.MAE/RW | Direction | Worst month | Worst AE |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for i, z in enumerate(out["dev_ranking"], 1):
        lines.append(
            f"| {i} | {z['model']} | {z['sum_abs_error']:.6f} | {z['mae']:.6f} | "
            f"{z['rmse']:.6f} | {z['mape_pct']:.4f}% | {z['wape_pct']:.4f}% | "
            f"{z['relative_mae_vs_rw']:.6f} | {z['direction_correct']}/33 | "
            f"{z['worst_month']} | {z['worst_ae']:.6f} |"
        )

    for name in ("LINEAR_SVR", "RBF_SVR"):
        v = out["models"][name]
        lines += [
            "",
            f"## {name} yearly",
            "",
            "| Year | SigmaAE | MAE | Direction |",
            "|---|---:|---:|---:|",
        ]
        for yy in ("2022", "2023", "2024"):
            m = v["yearly"][yy]
            lines.append(
                f"| {yy} | {m['sum_abs_error']:.6f} | {m['mae']:.6f} | "
                f"{m['direction_correct']}/{m['n']} |"
            )

    leader = out["dev_ranking"][0]
    lines += [
        "",
        "## Stage 1 decision",
        f"- Canonical Stage-1 price leader: **{leader['model']}**.",
        "- This is a baseline result only; no META_PARENT_SVR is frozen yet.",
        "- Stage 2 kernel / representation / formulation ablations remain mandatory.",
        "- 2025 remains locked.",
        "",
        "## Reproducibility",
        f"- Payload SHA256: {out['determinism']['payload_sha256']}",
        f"- Python: {out['software']['python']}",
        f"- NumPy: {out['software']['numpy']}",
        f"- scikit-learn: {out['software']['scikit_learn']}",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Stage-0 authority freeze respected: PASS.",
        "- DEV scope 2022-04..2024-12, n=33: PASS.",
        "- Target feature construction reads t-1/t-2 only: PASS.",
        "- Target actual read only after forecast creation: PASS.",
        "- Training-only X/Y scaling: PASS.",
        "- Deterministic replay: PASS.",
        "- Finite/pathological-prediction gate: PASS.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        "",
    ]
    return "\n".join(lines)


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)

    first = run_models(bundle)
    h1 = payload_hash(first)

    second = run_models(bundle)
    h2 = payload_hash(second)
    if h1 != h2:
        raise RuntimeError(f"DETERMINISM_FAIL first={h1} second={h2}")

    after = read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    expected_targets = list(base.month_range(DEV_START, DEV_END))
    for name, v in first.items():
        rows = v["rows"]
        if len(rows) != 33 or v["metrics"]["n"] != 33:
            raise RuntimeError(f"DEV_COUNT_FAIL model={name}")
        if [r["target"] for r in rows] != expected_targets:
            raise RuntimeError(f"DEV_TARGET_FAIL model={name}")
        if any(r["train_last"] >= r["target"] for r in rows):
            raise RuntimeError(f"CHRONOLOGY_FAIL model={name}")
        if any(r["origin"] != base.month_shift(r["target"], -1) for r in rows):
            raise RuntimeError(f"ORIGIN_FAIL model={name}")

    ranking = sorted(
        [{"model": name, **v["metrics"]} for name, v in first.items()],
        key=lambda z: (z["sum_abs_error"], -z["direction_correct"], z["rmse"], z["model"]),
    )

    out = {
        "family": "SVR_DWT_SVR",
        "scope": "STAGE1_CANONICAL_SVR_DEV_ONLY_V1",
        "stage0_freeze": "GOLD_MONTHLY_SVR_DWT_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md",
        "contract": {
            "target": "H=1 next-calendar-month average XAU/USD",
            "training_target": "Gold next-month log return only",
            "forecast_reconstruction": "previous completed-month Gold average * exp(predicted Gold log return)",
            "representation": "CURRENT8",
            "features": list(FEATURES),
            "feature_count": 8,
            "x_scaling": "TRAIN_ONLY_STANDARDIZATION",
            "y_scaling": "TRAIN_ONLY_STANDARDIZATION",
            "model": "epsilon-SVR",
            "dev_selection": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_NOT_OPENED",
            "2026_role": "QUARANTINED_NOT_USED",
            "database": "READ_ONLY",
            "random_split": "NONE",
            "hyperparameter_selection": "NONE_STAGE1_FIXED_CANONICAL",
            "primary_metric": "DEV_PRICE_SUM_ABS_ERROR",
            "target_actual_used_in_feature_or_fit": False,
            "multioutput": False,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "source_checks": bundle.source_checks,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "determinism": {"status": "PASS", "payload_sha256": h1},
        "models": first,
        "dev_ranking": ranking,
    }

    Path("gold_monthly_svr_dwt_stage1_canonical_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    Path(
        "gold_axis_2026/GOLD_MONTHLY_SVR_DWT_STAGE1_CANONICAL_RESULT_2026-09-28.md"
    ).write_text(report_markdown(out), encoding="utf-8")

    print("OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "ranking": ranking,
        "payload_sha256": h1,
        "authority_invariants_unchanged": after == bundle.invariants_before,
        "software": out["software"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
