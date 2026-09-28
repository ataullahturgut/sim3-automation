from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import tensorflow as tf

import gold_monthly_cnn_lstm_stage0_v1 as core
import gold_monthly_dev_snapshot_v1 as snapshot

MODEL_ID = "GOLD_MONTHLY_BILSTM_STRUCTURAL_V1"
LOOKBACK = 3
WIDTH = 32
DROPOUT = 0.10
LR = 0.001
BATCH = 16
MAX_EPOCHS = 300
PATIENCE = 25
SEEDS = (1701, 2903, 4111)

EXPECTED_SNAPSHOT_SHA256 = (
    "2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb"
)


def build_bilstm_model(_model_name: str):
    inp = tf.keras.Input(shape=(LOOKBACK, 8))
    x = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(WIDTH),
        merge_mode="concat",
    )(inp)
    x = tf.keras.layers.Dropout(DROPOUT)(x)
    out = tf.keras.layers.Dense(1)(x)
    model = tf.keras.Model(inp, out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LR),
        loss="mae",
    )
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if os.environ.get("NEON_DATABASE_URL"):
        raise RuntimeError("BILSTM_SNAPSHOT_RUN_MUST_NOT_HAVE_NEON_DATABASE_URL")

    bundle, snapshot_meta = snapshot.load_snapshot(args.snapshot)
    if snapshot_meta["payload_sha256"] != EXPECTED_SNAPSHOT_SHA256:
        raise RuntimeError(
            "BILSTM_SNAPSHOT_SHA_MISMATCH "
            f"got={snapshot_meta['payload_sha256']}"
        )

    core.LOOKBACK = LOOKBACK
    core.WIDTH = WIDTH
    core.DROPOUT = DROPOUT
    core.LR = LR
    core.BATCH = BATCH
    core.MAX_EPOCHS = MAX_EPOCHS
    core.PATIENCE = PATIENCE
    core.SEEDS = SEEDS
    core.build_model = build_bilstm_model
    core.configure_tf()

    rows = []
    for target in core.base.month_range(core.DEV_START, core.DEV_END):
        samples = core.base.all_samples_at_origin(
            bundle,
            target,
            governed=True,
        )
        rows.append(
            core.evaluate_origin(
                bundle,
                samples,
                target,
                "BILSTM",
            )
        )

    scientific_gate = core.build_gate(
        rows,
        bundle,
        dict(bundle.invariants_before),
    )
    checks = dict(scientific_gate["checks"])
    checks["snapshot_payload_hash_verified"] = (
        snapshot_meta["payload_sha256"] == EXPECTED_SNAPSHOT_SHA256
    )
    checks["no_database_connection_used"] = not bool(
        os.environ.get("NEON_DATABASE_URL")
    )
    scientific_gate = {
        **scientific_gate,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    if scientific_gate["status"] != "PASS":
        raise RuntimeError(f"BILSTM_SCIENTIFIC_GATE_FAIL {scientific_gate}")

    metrics = core.metrics_mod.active_metrics(rows)
    yearly = core.metrics_mod.yearly(rows)
    worst = max(rows, key=lambda r: r["abs_error"])
    seed_dispersion = core.summarize_seed_dispersion(rows)

    result = {
        "model_id": MODEL_ID,
        "stage": {
            "family": "CNN_LSTM",
            "phase": "STRUCTURAL_CHALLENGER",
            "model": "BiLSTM",
            "outcome_freeze": (
                "gold_axis_2026/"
                "GOLD_MONTHLY_BILSTM_STRUCTURAL_FREEZE_2026-09-28.md"
            ),
        },
        "snapshot": snapshot_meta,
        "authority": {
            "database_access": "NONE_OFFLINE_SNAPSHOT",
            "neon_is_authority": True,
            "snapshot_role": "EXECUTION_CACHE_ONLY",
            "feature_contract": "FROZEN_VW_MIDAS_CURRENT8",
            "target": "H=1 next-month Gold log return; reconstruct monthly XAU/USD",
            "selection_period": f"{core.DEV_START}..{core.DEV_END}",
            "2025_role": "LOCKED_NOT_PRESENT",
            "2026_role": "QUARANTINED_NOT_PRESENT",
            "random_split": "NONE",
        },
        "architecture": {
            "input_shape": [LOOKBACK, 8],
            "bidirectional_lstm_units_per_direction": WIDTH,
            "merge_mode": "concat",
            "dropout": DROPOUT,
            "dense_output_units": 1,
        },
        "frozen_training": {
            "optimizer": "Adam",
            "learning_rate": LR,
            "loss": "MAE_standardized_gold_log_return",
            "batch_size": BATCH,
            "max_epochs": MAX_EPOCHS,
            "early_stopping_patience": PATIENCE,
            "shuffle": False,
            "seeds": list(SEEDS),
            "seed_selection": (
                "chronological_inner_validation_"
                "natural_scale_gold_log_return_MAE"
            ),
            "final_refit": (
                "selected_seed_and_best_epoch_on_all_pre_target_sequences"
            ),
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
            "seed_dispersion": seed_dispersion,
            "rows": rows,
        },
        "scientific_gate": scientific_gate,
        "references": {
            "lstm_parent": {
                "sum_abs_error": 1589.9827200167367,
                "direction_correct": 19,
                "relative_mae_vs_rw": 0.9044270307262439,
            },
            "cnn_lstm_family_leader": {
                "sum_abs_error": 1528.5698506560245,
                "direction_correct": 20,
                "relative_mae_vs_rw": 0.8694936579385805,
            },
        },
    }

    Path(args.output).write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("BILSTM_SCIENTIFIC_GATE=PASS")
    print(
        json.dumps(
            {
                "model": "BiLSTM",
                "sum_abs_error": metrics["sum_abs_error"],
                "direction_correct": metrics["direction_correct"],
                "relative_mae_vs_rw": metrics["relative_mae_vs_rw"],
                "yearly": yearly,
                "worst_month": result["dev"]["worst_month"],
                "seed_dispersion": seed_dispersion,
                "snapshot_payload_sha256": snapshot_meta["payload_sha256"],
                "gate": scientific_gate["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
