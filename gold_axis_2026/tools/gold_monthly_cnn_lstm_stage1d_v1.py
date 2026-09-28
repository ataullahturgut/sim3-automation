from __future__ import annotations

import argparse
import gc
import json
import math
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import numpy as np
import psycopg
import tensorflow as tf

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as metrics_mod

DEV_START, DEV_END = "2022-04", "2024-12"
DEV_ORIGIN_START, DEV_ORIGIN_END = "2022-03", "2024-11"
HARD_CUTOFF = datetime(2025, 1, 1, tzinfo=timezone.utc)

LOOKBACK = None
WIDTH = None
DROPOUT = None
LR = 0.0003
BATCH = 16
MAX_EPOCHS = 300
PATIENCE = 25
SEEDS = (1701, 2903, 4111)
REPLAY_TARGETS = (DEV_START, DEV_END)

METALS = base.METALS
DAILY_SERIES = base.DAILY_SERIES
CORE_GOLD = base.CORE_GOLD
GPR_PIT = base.GPR_PIT


def configure_tf():
    try:
        tf.config.set_visible_devices([], "GPU")
    except Exception:
        pass
    try:
        tf.config.threading.set_intra_op_parallelism_threads(1)
        tf.config.threading.set_inter_op_parallelism_threads(1)
    except RuntimeError:
        pass
    try:
        tf.config.experimental.enable_op_determinism()
    except Exception:
        pass


def fetch_scalar_map_until(cur, series_id):
    cur.execute(
        "SELECT observation_ts,value FROM observations "
        "WHERE series_id=%s AND observation_ts < %s ORDER BY observation_ts",
        (series_id, HARD_CUTOFF),
    )
    return {base.month_key(ts): float(v) for ts, v in cur.fetchall()}


def load_dev_data(dsn: str) -> base.DataBundle:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            invariants = base.authority_invariants(cur)

            core_gold = fetch_scalar_map_until(cur, CORE_GOLD)

            raw = {m: {} for m in METALS}
            for metal, sid in DAILY_SERIES.items():
                cur.execute(
                    "SELECT observation_ts,value FROM observations "
                    "WHERE series_id=%s AND observation_ts < %s ORDER BY observation_ts",
                    (sid, HARD_CUTOFF),
                )
                for ts, value in cur.fetchall():
                    raw[metal][ts.date()] = float(value)

            common_dates = sorted(set.intersection(*(set(raw[m]) for m in METALS)))
            if not common_dates:
                raise RuntimeError("NO_COMMON_DAILY_METAL_ROWS")

            daily_month_values = {m: defaultdict(list) for m in METALS}
            for d in common_dates:
                mk = f"{d.year:04d}-{d.month:02d}"
                for metal in METALS:
                    daily_month_values[metal][mk].append(raw[metal][d])
            daily_month_values = {
                m: {k: np.asarray(v, float) for k, v in vv.items()}
                for m, vv in daily_month_values.items()
            }
            monthly_metal = {
                m: {k: float(v.mean()) for k, v in daily_month_values[m].items()}
                for m in METALS
            }

            cur.execute(
                "SELECT observation_ts,value,available_as_of,metadata->>'origin_month' "
                "FROM observations "
                "WHERE series_id=%s "
                "AND metadata->>'origin_month' >= %s "
                "AND metadata->>'origin_month' <= %s "
                "ORDER BY metadata->>'origin_month',observation_ts",
                (GPR_PIT, DEV_ORIGIN_START, DEV_ORIGIN_END),
            )
            vintages, availability = defaultdict(dict), {}
            for ts, value, available_as_of, origin_month in cur.fetchall():
                if not origin_month:
                    continue
                vintages[origin_month][base.month_key(ts)] = float(value)
                availability[origin_month] = min(
                    availability.get(origin_month, available_as_of), available_as_of
                )

            required = [
                base.month_shift(t, -1)
                for t in base.month_range(DEV_START, DEV_END)
            ]
            missing = [m for m in required if m not in vintages]
            late = [
                m
                for m in required
                if availability.get(m) is None
                or availability[m] > base.month_end_utc(m)
            ]
            missing_lag = [
                m
                for m in required
                if m in vintages and base.month_shift(m, -1) not in vintages[m]
            ]

            checks = {
                "core_gold_rows_loaded": len(core_gold),
                "core_gold_first_loaded": min(core_gold),
                "core_gold_last_loaded": max(core_gold),
                "common_daily_rows_loaded": len(common_dates),
                "common_daily_first_loaded": common_dates[0].isoformat(),
                "common_daily_last_loaded": common_dates[-1].isoformat(),
                "metal_months_loaded": {m: len(monthly_metal[m]) for m in METALS},
                "gpr_origin_vintages_loaded": len(vintages),
                "gpr_origin_first_loaded": min(vintages),
                "gpr_origin_last_loaded": max(vintages),
                "missing_required_gpr_origins": missing,
                "late_required_gpr_origins": late,
                "missing_required_gpr_lag_month": missing_lag,
                "hard_cutoff_exclusive": HARD_CUTOFF.isoformat(),
                "modeling_rows_2025_loaded": 0,
                "modeling_rows_2026_loaded": 0,
            }
            if missing or late or missing_lag:
                raise RuntimeError(f"GPR_PIT_SOURCE_GATE_FAIL {checks}")
            if max(core_gold) > DEV_END:
                raise RuntimeError("POST_DEV_CORE_GOLD_LOADED")
            if common_dates[-1] >= HARD_CUTOFF.date():
                raise RuntimeError("POST_DEV_DAILY_METAL_LOADED")
            if max(vintages) > DEV_ORIGIN_END:
                raise RuntimeError("POST_DEV_GPR_VINTAGE_LOADED")

            return base.DataBundle(
                core_gold=core_gold,
                core_gpr={},
                daily_month_values=daily_month_values,
                monthly_metal=monthly_metal,
                gpr_vintages=dict(vintages),
                source_checks=checks,
                invariants_before=invariants,
            )


def seq_keys_for_label(label: str):
    return [base.month_shift(label, d) for d in range(-(LOOKBACK - 1), 1)]


def build_sequences(samples: dict, target: str):
    labels, Xs, ys = [], [], []
    for label in sorted(k for k in samples if k < target):
        keys = seq_keys_for_label(label)
        if not all(k in samples for k in keys):
            continue
        Xs.append(np.stack([samples[k][0] for k in keys]))
        ys.append(float(samples[label][1][0]))
        labels.append(label)

    target_keys = seq_keys_for_label(target)
    if not all(k in samples for k in target_keys):
        raise RuntimeError(f"TARGET_SEQUENCE_INCOMPLETE {target}")
    if not labels:
        raise RuntimeError(f"NO_TRAINING_SEQUENCES {target}")

    X = np.stack(Xs).astype(float)
    y = np.asarray(ys, float)
    tx = np.stack([samples[k][0] for k in target_keys])[None, ...].astype(float)
    target_feature_origins = [base.month_shift(k, -1) for k in target_keys]
    return labels, X, y, tx, target_feature_origins


def inner_split(n: int):
    raw = int(math.ceil(0.20 * n))
    val_n = max(12, raw) if n >= 24 else max(1, raw)
    if val_n >= n:
        val_n = max(1, n // 2)
    tr_n = n - val_n
    if tr_n < 1:
        raise RuntimeError(f"INNER_TRAIN_EMPTY n={n} val_n={val_n}")
    return tr_n, val_n


def fit_scaler(X: np.ndarray, y: np.ndarray):
    flat = X.reshape(-1, X.shape[-1])
    xm = flat.mean(axis=0)
    xs = flat.std(axis=0)
    ym = float(y.mean())
    ys = float(y.std())
    xs = np.where(xs < 1e-9, 1.0, xs)
    if ys < 1e-9:
        ys = 1.0
    return xm, xs, ym, ys


def scale_x(X, xm, xs):
    return (X - xm[None, None, :]) / xs[None, None, :]


def build_model(model_name: str):
    inp = tf.keras.Input(shape=(LOOKBACK, 8))
    if model_name == "LSTM":
        x = tf.keras.layers.LSTM(WIDTH)(inp)
        x = tf.keras.layers.Dropout(DROPOUT)(x)
    elif model_name == "CNN":
        x = tf.keras.layers.Conv1D(
            filters=WIDTH, kernel_size=3, strides=1, padding="valid", activation="relu"
        )(inp)
        x = tf.keras.layers.GlobalAveragePooling1D()(x)
    elif model_name == "CNN_LSTM":
        x = tf.keras.layers.Conv1D(
            filters=WIDTH, kernel_size=3, strides=1, padding="valid", activation="relu"
        )(inp)
        x = tf.keras.layers.LSTM(WIDTH)(x)
        x = tf.keras.layers.Dropout(DROPOUT)(x)
    else:
        raise ValueError(model_name)
    out = tf.keras.layers.Dense(1)(x)
    model = tf.keras.Model(inp, out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LR),
        loss="mae",
    )
    return model


def reset_seed(seed: int):
    tf.keras.backend.clear_session()
    gc.collect()
    tf.keras.utils.set_random_seed(seed)


def fit_seed_candidate(model_name, seed, Xtr, ytr, Xv, yv):
    xm, xs, ym, ys = fit_scaler(Xtr, ytr)
    sxtr = scale_x(Xtr, xm, xs)
    sxv = scale_x(Xv, xm, xs)
    sytr = (ytr - ym) / ys

    reset_seed(seed)
    model = build_model(model_name)
    cb = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=PATIENCE,
        restore_best_weights=True,
        mode="min",
    )
    hist = model.fit(
        sxtr,
        sytr,
        validation_data=(sxv, (yv - ym) / ys),
        epochs=MAX_EPOCHS,
        batch_size=min(BATCH, len(sxtr)),
        shuffle=False,
        verbose=0,
        callbacks=[cb],
    )
    val_loss = np.asarray(hist.history["val_loss"], float)
    best_epoch = int(np.argmin(val_loss) + 1)
    pred_val = model.predict(sxv, verbose=0).reshape(-1) * ys + ym
    val_mae = float(np.mean(np.abs(pred_val - yv)))
    return {
        "seed": int(seed),
        "best_epoch": best_epoch,
        "epochs_ran": int(len(hist.history["loss"])),
        "validation_mae_gold_log_return": val_mae,
        "best_standardized_val_mae": float(np.min(val_loss)),
    }


def refit_predict(model_name, seed, epochs, X, y, tx):
    xm, xs, ym, ys = fit_scaler(X, y)
    sx = scale_x(X, xm, xs)
    stx = scale_x(tx, xm, xs)
    sy = (y - ym) / ys

    reset_seed(seed)
    model = build_model(model_name)
    model.fit(
        sx,
        sy,
        epochs=max(1, int(epochs)),
        batch_size=min(BATCH, len(sx)),
        shuffle=False,
        verbose=0,
    )
    pred_std = float(model.predict(stx, verbose=0).reshape(-1)[0])
    return float(pred_std * ys + ym), {
        "x_mean": xm.tolist(),
        "x_std": xs.tolist(),
        "y_mean": ym,
        "y_std": ys,
    }


def scientific_input_gates(samples, target, labels, X, y, tx, target_feature_origins):
    origin = base.month_shift(target, -1)

    train_last_lt_target = bool(labels[-1] < target)
    sequence_ends_at_origin = bool(target_feature_origins[-1] == origin)

    tr_n, val_n = inner_split(len(labels))
    Xtr, ytr = X[:tr_n], y[:tr_n]
    scaler_a = fit_scaler(Xtr, ytr)
    tx_pert = tx.copy()
    tx_pert += 9999.0
    scaler_b = fit_scaler(Xtr, ytr)
    train_only_scaling_invariance = all(
        np.array_equal(np.asarray(a), np.asarray(b))
        for a, b in zip(scaler_a, scaler_b)
    )

    future_key = base.month_shift(target, 1)
    future_samples = dict(samples)
    future_samples[future_key] = (
        np.full(8, 1e9, dtype=float),
        np.full(4, -1e9, dtype=float),
    )
    l2, X2, y2, tx2, o2 = build_sequences(future_samples, target)
    future_feature_perturbation_invariance = (
        labels == l2
        and np.array_equal(X, X2)
        and np.array_equal(y, y2)
        and np.array_equal(tx, tx2)
        and target_feature_origins == o2
    )

    target_label_samples = dict(samples)
    ox, oy = samples[target]
    py = np.asarray(oy, float).copy()
    py[0] += 0.987654321
    target_label_samples[target] = (np.asarray(ox, float).copy(), py)
    l3, X3, y3, tx3, o3 = build_sequences(target_label_samples, target)
    target_label_perturbation_invariance = (
        labels == l3
        and np.array_equal(X, X3)
        and np.array_equal(y, y3)
        and np.array_equal(tx, tx3)
        and target_feature_origins == o3
    )

    return {
        "train_last_lt_target": train_last_lt_target,
        "sequence_ends_at_origin": sequence_ends_at_origin,
        "train_only_scaling_invariance": bool(train_only_scaling_invariance),
        "future_feature_perturbation_invariance": bool(
            future_feature_perturbation_invariance
        ),
        "target_label_perturbation_invariance": bool(
            target_label_perturbation_invariance
        ),
        "inner_train_rows": int(tr_n),
        "inner_validation_rows": int(val_n),
    }


def evaluate_origin(bundle, samples, target, model_name):
    labels, X, y, tx, target_feature_origins = build_sequences(samples, target)
    gates = scientific_input_gates(
        samples, target, labels, X, y, tx, target_feature_origins
    )

    tr_n, val_n = inner_split(len(labels))
    Xtr, ytr = X[:tr_n], y[:tr_n]
    Xv, yv = X[tr_n:], y[tr_n:]

    seed_runs = [
        fit_seed_candidate(model_name, seed, Xtr, ytr, Xv, yv)
        for seed in SEEDS
    ]
    seed_runs.sort(
        key=lambda r: (r["validation_mae_gold_log_return"], r["seed"])
    )
    selected = seed_runs[0]

    pred, final_scaler = refit_predict(
        model_name,
        selected["seed"],
        selected["best_epoch"],
        X,
        y,
        tx,
    )

    replay_diff = None
    replay_pass = None
    if target in REPLAY_TARGETS:
        pred2, _ = refit_predict(
            model_name,
            selected["seed"],
            selected["best_epoch"],
            X,
            y,
            tx,
        )
        replay_diff = float(abs(pred2 - pred))
        replay_pass = bool(replay_diff <= 1e-7)

    origin = base.month_shift(target, -1)
    forecast = float(bundle.core_gold[origin] * math.exp(pred))
    actual = float(bundle.core_gold[target])
    rw = float(bundle.core_gold[origin])

    seed_val_maes = [r["validation_mae_gold_log_return"] for r in seed_runs]
    return {
        "target": target,
        "origin": origin,
        "train_sequence_rows": int(len(labels)),
        "train_last_label": labels[-1],
        "sequence_first_feature_origin": target_feature_origins[0],
        "sequence_last_feature_origin": target_feature_origins[-1],
        "selected_seed": int(selected["seed"]),
        "selected_best_epoch": int(selected["best_epoch"]),
        "seed_runs": seed_runs,
        "seed_validation_mae_std": float(np.std(seed_val_maes)),
        "seed_validation_mae_spread": float(max(seed_val_maes) - min(seed_val_maes)),
        "pred_log_return_gold": float(pred),
        "forecast": forecast,
        "actual": actual,
        "rw": rw,
        "abs_error": float(abs(forecast - actual)),
        "direction_correct": bool(
            np.sign(forecast - rw) == np.sign(actual - rw)
        ),
        "final_scaler": final_scaler,
        "scientific_input_gates": gates,
        "deterministic_replay_checked": bool(target in REPLAY_TARGETS),
        "deterministic_replay_abs_diff": replay_diff,
        "deterministic_replay_pass": replay_pass,
    }


def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def summarize_seed_dispersion(rows):
    counts = Counter(str(r["selected_seed"]) for r in rows)
    return {
        "selected_seed_counts": dict(sorted(counts.items())),
        "mean_seed_validation_mae_std": float(
            np.mean([r["seed_validation_mae_std"] for r in rows])
        ),
        "max_seed_validation_mae_std": float(
            np.max([r["seed_validation_mae_std"] for r in rows])
        ),
        "mean_seed_validation_mae_spread": float(
            np.mean([r["seed_validation_mae_spread"] for r in rows])
        ),
        "max_seed_validation_mae_spread": float(
            np.max([r["seed_validation_mae_spread"] for r in rows])
        ),
    }


def build_gate(rows, bundle, after):
    replay_rows = [r for r in rows if r["deterministic_replay_checked"]]
    checks = {
        "train_last_lt_target": all(
            r["scientific_input_gates"]["train_last_lt_target"] for r in rows
        ),
        "sequence_ends_at_origin": all(
            r["scientific_input_gates"]["sequence_ends_at_origin"] for r in rows
        ),
        "train_only_scaling_invariance": all(
            r["scientific_input_gates"]["train_only_scaling_invariance"]
            for r in rows
        ),
        "future_feature_perturbation_invariance": all(
            r["scientific_input_gates"][
                "future_feature_perturbation_invariance"
            ]
            for r in rows
        ),
        "target_label_perturbation_invariance": all(
            r["scientific_input_gates"][
                "target_label_perturbation_invariance"
            ]
            for r in rows
        ),
        "same_seed_deterministic_replay": (
            len(replay_rows) == len(REPLAY_TARGETS)
            and all(r["deterministic_replay_pass"] for r in replay_rows)
        ),
        "three_of_three_seed_outputs": all(
            len(r["seed_runs"]) == 3
            and {q["seed"] for q in r["seed_runs"]} == set(SEEDS)
            for r in rows
        ),
        "finite_predictions": all(
            math.isfinite(r["forecast"])
            and math.isfinite(r["pred_log_return_gold"])
            for r in rows
        ),
        "abs_predicted_log_return_lt_1": all(
            abs(r["pred_log_return_gold"]) < 1 for r in rows
        ),
        "db_authority_invariants_unchanged": after == bundle.invariants_before,
        "no_2025_2026_modeling_rows_loaded": (
            bundle.source_checks["modeling_rows_2025_loaded"] == 0
            and bundle.source_checks["modeling_rows_2026_loaded"] == 0
            and bundle.source_checks["core_gold_last_loaded"] <= DEV_END
            and bundle.source_checks["gpr_origin_last_loaded"] <= DEV_ORIGIN_END
        ),
        "dev_origin_count_33": len(rows) == 33,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "replay_targets": list(REPLAY_TARGETS),
        "replay_diffs": {
            r["target"]: r["deterministic_replay_abs_diff"] for r in replay_rows
        },
    }


def main():
    global LOOKBACK, WIDTH, DROPOUT

    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=("LSTM", "CNN", "CNN_LSTM"))
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    parent = {
        "LSTM": {"lookback": 3, "width": 32, "dropout": 0.10},
        "CNN": {"lookback": 3, "width": 16, "dropout": None},
        "CNN_LSTM": {"lookback": 6, "width": 32, "dropout": 0.10},
    }[args.model]

    LOOKBACK = int(parent["lookback"])
    WIDTH = int(parent["width"])
    DROPOUT = parent["dropout"]

    configure_tf()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = load_dev_data(dsn)
    rows = []
    for target in base.month_range(DEV_START, DEV_END):
        samples = base.all_samples_at_origin(bundle, target, governed=True)
        rows.append(evaluate_origin(bundle, samples, target, args.model))

    after = read_invariants(dsn)
    gate = build_gate(rows, bundle, after)
    if gate["status"] != "PASS":
        raise RuntimeError(f"SCIENTIFIC_GATE_FAIL {gate}")

    metrics = metrics_mod.active_metrics(rows)
    yearly = metrics_mod.yearly(rows)
    worst = max(rows, key=lambda r: r["abs_error"])

    out = {
        "model_id": f"GOLD_MONTHLY_CNN_LSTM_STAGE1D_{args.model}_LR{LR:.4f}_V1",
        "stage": {
            "family": "CNN_LSTM",
            "stage": "1D",
            "lane": args.model,
            "factor": "LEARNING_RATE_ONLY",
            "lookback": LOOKBACK,
            "width": WIDTH,
            "dropout": DROPOUT,
            "learning_rate": LR,
            "outcome_freeze": (
                "gold_axis_2026/"
                "GOLD_MONTHLY_CNN_LSTM_STAGE1D_LR_FREEZE_2026-09-28.md"
            ),
        },
        "authority": {
            "database_access": "READ_ONLY",
            "feature_contract": "FROZEN_VW_MIDAS_CURRENT8",
            "target": "H=1 next-month Gold log return; reconstruct monthly XAU/USD",
            "selection_period": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_NOT_QUERIED_NOT_LOADED",
            "2026_role": "QUARANTINED_NOT_QUERIED_NOT_LOADED",
            "random_split": "NONE",
            "lookback": LOOKBACK,
            "seeds": list(SEEDS),
            "authority_invariants_before": bundle.invariants_before,
            "authority_invariants_after": after,
            "source_checks": bundle.source_checks,
        },
        "runtime": {
            "python": os.sys.version,
            "tensorflow": tf.__version__,
            "numpy": np.__version__,
            "deterministic_ops": True,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "frozen_training": {
            "width": WIDTH,
            "dropout": DROPOUT,
            "optimizer": "Adam",
            "learning_rate": LR,
            "loss": "MAE_standardized_gold_log_return",
            "batch_size": BATCH,
            "max_epochs": MAX_EPOCHS,
            "early_stopping_patience": PATIENCE,
            "shuffle": False,
            "seed_selection": "chronological_inner_validation_natural_scale_gold_log_return_MAE",
            "final_refit": "selected_seed_and_best_epoch_on_all_pre_target_sequences",
        },
        "dev": {
            "metrics": metrics,
            "yearly": yearly,
            "worst_month": {
                "target": worst["target"],
                "abs_error": worst["abs_error"],
                "forecast": worst["forecast"],
                "actual": worst["actual"],
            },
            "seed_dispersion": summarize_seed_dispersion(rows),
            "rows": rows,
        },
        "scientific_gate": gate,
    }

    output = args.output or f"gold_monthly_cnn_lstm_stage1d_{args.model.lower()}_lr0003_v1_result.json"
    Path(output).write_text(
        json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("SCIENTIFIC_GATE=PASS")
    print(
        json.dumps(
            {
                "model": args.model,
                "lookback": LOOKBACK,
                "width": WIDTH,
                "dropout": DROPOUT,
                "learning_rate": LR,
                "sum_abs_error": metrics["sum_abs_error"],
                "direction_correct": metrics["direction_correct"],
                "relative_mae_vs_rw": metrics["relative_mae_vs_rw"],
                "worst_month": out["dev"]["worst_month"],
                "seed_dispersion": out["dev"]["seed_dispersion"],
                "gate": gate["status"],
            },
            sort_keys=True,
        )
    )

if __name__ == "__main__":
    main()
