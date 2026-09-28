#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
import psycopg
import sklearn
import xgboost
from xgboost import XGBRegressor
import vmdpy
from vmdpy import VMD

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage5_regularization_v1 as s5

DEV_START, DEV_END = "2022-04", "2024-12"
HISTORY_START = "2010-01"
FEATURE_START = "2015-01"
MIN_HISTORY_MONTHS = 60
FEATURE_DIM = 4

VMD_ALPHA = 2000.0
VMD_TAU = 0.0
VMD_K = 3
VMD_DC = 0
VMD_INIT = 1
VMD_TOL = 1e-7

STAGE5_XGB_REF_SUMAE = 1583.8534958594905
STAGE5_XGB_REF_DIRECTION = 20
CATBOOST_CONTEXT_SUMAE = 1460.433935309605

XGB_PARAMS = {
    "objective": "reg:squarederror",
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 4,
    "min_child_weight": 1.0,
    "gamma": 0.001,
    "subsample": 0.80,
    "colsample_bytree": 0.80,
    "reg_alpha": 0.01,
    "reg_lambda": 5.0,
    "tree_method": "hist",
    "random_state": 1701,
    "n_jobs": 1,
    "verbosity": 0,
}

def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def make_xgb():
    return XGBRegressor(**XGB_PARAMS)

def months_between(start, end):
    return list(base.month_range(start, end))

def vmd_feature(bundle, target):
    origin = base.month_shift(target, -1)
    hist_months = months_between(HISTORY_START, origin)
    if len(hist_months) < MIN_HISTORY_MONTHS:
        raise RuntimeError(
            f"VMD_HISTORY_TOO_SHORT target={target} origin={origin} n={len(hist_months)}"
        )
    missing = [m for m in hist_months if m not in bundle.core_gold]
    if missing:
        raise RuntimeError(
            f"VMD_GOLD_HISTORY_MISSING target={target} first_missing={missing[0]} n={len(missing)}"
        )

    dropped_oldest = False
    original_start = hist_months[0]
    if len(hist_months) % 2 == 1:
        hist_months = hist_months[1:]
        dropped_oldest = True

    if hist_months[-1] != origin:
        raise RuntimeError(f"VMD_ORIGIN_ENDPOINT_LOST target={target} end={hist_months[-1]} origin={origin}")

    signal = np.asarray([float(bundle.core_gold[m]) for m in hist_months], float)
    if not np.isfinite(signal).all() or np.any(signal <= 0):
        raise RuntimeError(f"VMD_BAD_SIGNAL target={target}")
    if len(signal) % 2 != 0:
        raise RuntimeError(f"VMD_PARITY_FAIL target={target} n={len(signal)}")

    u, u_hat, omega = VMD(
        signal,
        VMD_ALPHA,
        VMD_TAU,
        VMD_K,
        VMD_DC,
        VMD_INIT,
        VMD_TOL,
    )
    u = np.asarray(u, float)
    u_hat = np.asarray(u_hat)
    omega = np.asarray(omega, float)

    if u.ndim != 2 or u.shape != (VMD_K, len(signal)):
        raise RuntimeError(f"VMD_MODE_SHAPE_FAIL target={target} shape={u.shape} n={len(signal)}")
    if not np.isfinite(u).all() or not np.isfinite(omega).all():
        raise RuntimeError(f"VMD_NONFINITE target={target}")

    residual = signal - np.sum(u, axis=0)
    recon = np.sum(u, axis=0) + residual
    max_abs_recon = float(np.max(np.abs(recon - signal)))
    scale = max(float(np.max(np.abs(signal))), 1.0)
    rel_recon = float(max_abs_recon / scale)
    if rel_recon > 1e-12:
        raise RuntimeError(
            f"VMD_RECON_FAIL target={target} max_abs={max_abs_recon} rel={rel_recon}"
        )

    feat = np.asarray([u[0,-1], u[1,-1], u[2,-1], residual[-1]], float)
    if feat.shape != (FEATURE_DIM,) or not np.isfinite(feat).all():
        raise RuntimeError(f"VMD_FEATURE_FAIL target={target} feat={feat}")

    residual_energy_ratio = float(
        np.sum(residual * residual) / max(float(np.sum(signal * signal)), 1e-12)
    )

    return {
        "target": target,
        "origin": origin,
        "requested_history_start": HISTORY_START,
        "original_history_start": original_start,
        "effective_history_start": hist_months[0],
        "history_end": origin,
        "history_n": len(hist_months),
        "dropped_oldest_for_even_length": dropped_oldest,
        "mode_count": int(u.shape[0]),
        "feature": feat,
        "mode_endpoints": [float(x) for x in u[:, -1]],
        "residual_endpoint": float(residual[-1]),
        "residual_energy_ratio": residual_energy_ratio,
        "omega_last": [float(x) for x in omega[-1]],
        "reconstruction_max_abs_error": max_abs_recon,
        "reconstruction_relative_error": rel_recon,
    }

def feature_hash(feature_records):
    compact = {
        k: {
            "origin": v["origin"],
            "effective_history_start": v["effective_history_start"],
            "history_n": v["history_n"],
            "dropped_oldest_for_even_length": v["dropped_oldest_for_even_length"],
            "feature": [float(x) for x in v["feature"]],
            "omega_last": v["omega_last"],
            "reconstruction_relative_error": v["reconstruction_relative_error"],
        }
        for k, v in sorted(feature_records.items())
    }
    return hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

def build_feature_cache(bundle):
    targets = months_between(FEATURE_START, DEV_END)
    out = {}
    for i, target in enumerate(targets, 1):
        rec = vmd_feature(bundle, target)
        out[target] = rec
        if i == 1 or i % 12 == 0 or target == DEV_END:
            print(
                f"VMD_PROGRESS feature={i}/{len(targets)} target={target} "
                f"hist_n={rec['history_n']} dropped_oldest={int(rec['dropped_oldest_for_even_length'])} "
                f"res_energy={rec['residual_energy_ratio']:.6e}",
                flush=True,
            )
    return out

def direct_log_return(bundle, target):
    p = base.month_shift(target, -1)
    if p not in bundle.core_gold or target not in bundle.core_gold:
        raise RuntimeError(f"RETURN_LEVEL_MISSING target={target}")
    return float(math.log(float(bundle.core_gold[target]) / float(bundle.core_gold[p])))

def predict_vmd(bundle, feature_cache, target):
    if target not in feature_cache:
        raise RuntimeError(f"TARGET_FEATURE_MISSING {target}")
    keys = sorted(k for k in feature_cache if FEATURE_START <= k < target)
    if len(keys) < 36:
        raise RuntimeError(f"VMD_TRAIN_TOO_SMALL target={target} n={len(keys)}")
    if any(k >= target for k in keys):
        raise RuntimeError(f"VMD_TRAIN_LEAK target={target}")
    if any(feature_cache[k]["history_end"] != base.month_shift(k, -1) for k in keys):
        raise RuntimeError(f"VMD_PREFIX_LEAK target={target}")

    X = np.stack([feature_cache[k]["feature"] for k in keys])
    y = np.asarray([direct_log_return(bundle, k) for k in keys], float)
    tx = feature_cache[target]["feature"].reshape(1, -1)

    if X.shape[1] != FEATURE_DIM or tx.shape != (1, FEATURE_DIM):
        raise RuntimeError(f"VMD_DIM_FAIL target={target} X={X.shape} tx={tx.shape}")
    if not (np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(tx).all()):
        raise RuntimeError(f"VMD_TRAIN_NONFINITE target={target}")

    model = make_xgb()
    model.fit(X, y)
    pred = float(np.asarray(model.predict(tx)).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred) >= 1.0:
        raise RuntimeError(f"VMD_PATHOLOGICAL_PRED target={target} pred={pred}")

    origin = base.month_shift(target, -1)
    previous = float(bundle.core_gold[origin])
    forecast = float(previous * math.exp(pred))
    return {
        "target": target,
        "origin": origin,
        "feature_history_end": feature_cache[target]["history_end"],
        "feature_effective_history_start": feature_cache[target]["effective_history_start"],
        "feature_dropped_oldest": feature_cache[target]["dropped_oldest_for_even_length"],
        "train_first": keys[0],
        "train_last": keys[-1],
        "train_rows": len(keys),
        "feature_dim": FEATURE_DIM,
        "target_feature": [float(x) for x in feature_cache[target]["feature"]],
        "target_residual_energy_ratio": feature_cache[target]["residual_energy_ratio"],
        "pred_log_return_gold": pred,
        "forecast": forecast,
        "rw": previous,
    }

def evaluate_current8_comparator(bundle):
    targets = list(base.month_range(DEV_START, DEV_END))
    cache = {t: base.all_samples_at_origin(bundle, t, governed=True) for t in targets}
    lane = next(x for x in s5.LANES if x["lane"] == "XGBOOST_DIRECTION")
    profile, reg = next(x for x in lane["profiles"] if x[0] == "X_R4_COMBO")
    return s5.evaluate(bundle, cache, lane, profile, reg)

def metrics(rows, forecast_key="forecast", direction_key="direction_correct"):
    a = np.asarray([r["actual"] for r in rows], float)
    f = np.asarray([r[forecast_key] for r in rows], float)
    rw = np.asarray([r["rw"] for r in rows], float)
    ae = np.abs(f - a)
    rw_ae = np.abs(rw - a)
    d = np.asarray([r[direction_key] for r in rows], bool)
    wi = int(np.argmax(ae))
    return {
        "n": len(rows),
        "sum_abs_error": float(ae.sum()),
        "mae": float(ae.mean()),
        "rmse": float(np.sqrt(np.mean((f - a) ** 2))),
        "mape_pct": float(np.mean(ae / np.maximum(np.abs(a), 1e-12)) * 100.0),
        "wape_pct": float(ae.sum() / np.maximum(np.abs(a).sum(), 1e-12) * 100.0),
        "median_ae": float(np.median(ae)),
        "monthly_ae_std": float(np.std(ae, ddof=0)),
        "worst_ae": float(ae[wi]),
        "worst_month": rows[wi]["target"],
        "relative_mae_vs_rw": float(ae.sum() / max(float(rw_ae.sum()), 1e-12)),
        "direction_correct": int(d.sum()),
        "direction_accuracy_pct": float(d.mean() * 100.0),
        "rw_sum_abs_error": float(rw_ae.sum()),
    }

def yearly(rows):
    out = {}
    for y in ("2022", "2023", "2024"):
        rr = [r for r in rows if r["target"].startswith(y)]
        out[y] = metrics(rr)
    return out

def smoke():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle = base.load_data(dsn)
    target = "2024-12"
    a = vmd_feature(bundle, target)
    b = vmd_feature(bundle, target)
    if not np.allclose(a["feature"], b["feature"], rtol=0.0, atol=1e-12):
        raise RuntimeError(f"VMD_DETERMINISM_FAIL a={a['feature']} b={b['feature']}")
    if a["mode_count"] != VMD_K or b["mode_count"] != VMD_K:
        raise RuntimeError("VMD_MODE_COUNT_FAIL")
    if a["history_end"] != "2024-11":
        raise RuntimeError("VMD_SMOKE_ENDPOINT_FAIL")
    print("VMD_SMOKE_GATE=PASS", flush=True)
    print(json.dumps({
        "target": target,
        "origin": a["origin"],
        "history_n": a["history_n"],
        "effective_history_start": a["effective_history_start"],
        "dropped_oldest_for_even_length": a["dropped_oldest_for_even_length"],
        "feature": [float(x) for x in a["feature"]],
        "residual_energy_ratio": a["residual_energy_ratio"],
        "omega_last": a["omega_last"],
        "reconstruction_relative_error": a["reconstruction_relative_error"],
    }, sort_keys=True), flush=True)

def run_full():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    before = bundle.invariants_before

    feature_cache = build_feature_cache(bundle)
    fh = feature_hash(feature_cache)

    comparator = evaluate_current8_comparator(bundle)
    cm = comparator["metrics"]
    if abs(float(cm["sum_abs_error"]) - STAGE5_XGB_REF_SUMAE) > 1e-8:
        raise RuntimeError(
            f"STAGE5_XGB_REPRO_FAIL ref={STAGE5_XGB_REF_SUMAE} cur={cm['sum_abs_error']}"
        )
    if int(cm["direction_correct"]) != STAGE5_XGB_REF_DIRECTION:
        raise RuntimeError(
            f"STAGE5_XGB_DIR_REPRO_FAIL ref={STAGE5_XGB_REF_DIRECTION} cur={cm['direction_correct']}"
        )

    rows = []
    for i, target in enumerate(base.month_range(DEV_START, DEV_END), 1):
        pred = predict_vmd(bundle, feature_cache, target)

        if target not in bundle.core_gold:
            raise RuntimeError(f"DEV_ACTUAL_MISSING {target}")
        actual = float(bundle.core_gold[target])
        pred_dir = int(np.sign(pred["forecast"] - pred["rw"]))
        actual_dir = int(np.sign(actual - pred["rw"]))
        pred["actual"] = actual
        pred["absolute_error"] = float(abs(pred["forecast"] - actual))
        pred["pred_direction"] = pred_dir
        pred["actual_direction"] = actual_dir
        pred["direction_correct"] = bool(pred_dir == actual_dir)
        rows.append(pred)
        print(
            f"DEV_PROGRESS target={i}/33 month={target} "
            f"AE={pred['absolute_error']:.6f} dir={int(pred['direction_correct'])} "
            f"train_n={pred['train_rows']} res_energy={pred['target_residual_energy_ratio']:.6e}",
            flush=True,
        )

    if len(rows) != 33:
        raise RuntimeError(f"DEV_ROW_COUNT_FAIL n={len(rows)}")
    if any(not (DEV_START <= r["target"] <= DEV_END) for r in rows):
        raise RuntimeError("NON_DEV_TARGET_FAIL")
    if any(r["feature_history_end"] != r["origin"] for r in rows):
        raise RuntimeError("OUTER_FEATURE_PREFIX_FAIL")
    if any(r["train_last"] >= r["target"] for r in rows):
        raise RuntimeError("OUTER_TRAIN_LEAK_FAIL")

    after = read_invariants(dsn)
    if before != after:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    met = metrics(rows)
    yr = yearly(rows)
    recon = np.asarray([v["reconstruction_relative_error"] for v in feature_cache.values()], float)
    res_energy = np.asarray([v["residual_energy_ratio"] for v in feature_cache.values()], float)
    dropped = int(sum(bool(v["dropped_oldest_for_even_length"]) for v in feature_cache.values()))

    criterion_a = bool(met["sum_abs_error"] < STAGE5_XGB_REF_SUMAE)
    criterion_b = bool(
        met["direction_correct"] >= 22
        and met["sum_abs_error"] <= 1.05 * STAGE5_XGB_REF_SUMAE
    )
    proceed_d1 = bool(criterion_a or criterion_b)

    digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    payload = {
        "scope": "BOOSTING_STAGE6C_D0_CAUSAL_VMD_XGBOOST_V1",
        "freeze_file": "GOLD_MONTHLY_BOOSTING_STAGE6C_D0_CAUSAL_VMD_XGB_FREEZE_2026-09-28.md",
        "authority": {
            "gold_source": "Guo et al. 2025, DOI 10.1007/s10614-024-10736-9",
            "vmd_source": "Dragomiretskiy & Zosso 2014, DOI 10.1109/TSP.2013.2288675",
            "python_reference": "vmdpy 0.2",
            "gold_paper_standalone_d0_parameters": "NOT_FOUND",
            "parameter_strategy": "canonical reference-example parameters frozen pre-outcome",
        },
        "contract": {
            "dev": f"{DEV_START}..{DEV_END}",
            "dev_n": 33,
            "target": "Gold next-month log return -> previous monthly Gold average * exp(pred)",
            "representation": "CAUSAL_VMD_K3_MODES_PLUS_RESIDUAL_ENDPOINT",
            "feature_dim": FEATURE_DIM,
            "history_start": HISTORY_START,
            "feature_start": FEATURE_START,
            "min_history_months": MIN_HISTORY_MONTHS,
            "random_split": "NONE",
            "database": "READ_ONLY",
            "2025_role": "NOT_OPENED_NOT_EVALUATED",
            "2026_role": "QUARANTINED_NOT_USED_IN_DEVELOPMENT",
            "primary_metric": "DEV_PRICE_SUM_ABS_ERROR",
            "xgboost_tuning": "NONE",
            "vmd_tuning": "NONE",
            "global_decomposition": "BLOCKED",
            "odd_length_rule": "drop oldest sample, never origin endpoint",
            "outer_actual_read_after_forecast_generation": True,
        },
        "vmd": {
            "package": "vmdpy",
            "package_version": "0.2",
            "alpha": VMD_ALPHA,
            "tau": VMD_TAU,
            "K": VMD_K,
            "DC": VMD_DC,
            "init": VMD_INIT,
            "tol": VMD_TOL,
            "features_with_oldest_dropped_for_even_length": dropped,
            "max_reconstruction_relative_error": float(recon.max()),
            "residual_energy_ratio_mean": float(res_energy.mean()),
            "residual_energy_ratio_median": float(np.median(res_energy)),
            "residual_energy_ratio_max": float(res_energy.max()),
            "feature_payload_sha256": fh,
        },
        "xgboost_params": XGB_PARAMS,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "xgboost": xgboost.__version__,
        },
        "authority_invariants_before": before,
        "authority_invariants_after": after,
        "stage5_current8_comparator": {
            "reference_sum_abs_error": STAGE5_XGB_REF_SUMAE,
            "reference_direction_correct": STAGE5_XGB_REF_DIRECTION,
            "metrics": cm,
            "yearly": comparator["yearly"],
        },
        "vmd_xgboost": {
            "metrics": met,
            "yearly": yr,
            "delta_sum_abs_error_vs_current8": float(met["sum_abs_error"] - cm["sum_abs_error"]),
            "delta_direction_correct_vs_current8": int(met["direction_correct"] - cm["direction_correct"]),
        },
        "d1_gate": {
            "criterion_a_primary_improvement": criterion_a,
            "criterion_b_complementarity": criterion_b,
            "proceed_to_d1": proceed_d1,
            "rule": "A: SigmaAE < 1583.8534958594905 OR B: direction>=22/33 and SigmaAE<=1.05*1583.8534958594905",
        },
        "catboost_family_leader_context": {
            "sum_abs_error": CATBOOST_CONTEXT_SUMAE,
            "selection_use": "POST_RUN_CONTEXT_ONLY",
        },
        "rows": rows,
        "payload_sha256": digest,
    }

    Path("gold_monthly_boosting_stage6c_d0_causal_vmd_xgb_result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "stage5_current8": payload["stage5_current8_comparator"],
        "vmd_xgboost": payload["vmd_xgboost"],
        "vmd_audit": payload["vmd"],
        "d1_gate": payload["d1_gate"],
        "payload_sha256": digest,
        "authority_invariants_unchanged": before == after,
    }, sort_keys=True), flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        smoke()
    else:
        run_full()

if __name__ == "__main__":
    main()
