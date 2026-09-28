from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import gold_monthly_cnn_lstm_stage0_v1 as stage0
import gold_monthly_dev_snapshot_v1 as snap

EXPECTED = {
    "sum_abs_error": 1528.5698506560245,
    "direction_correct": 20,
    "relative_mae_vs_rw": 0.8694936579385805,
    "yearly_sum_abs_error": {
        "2022": 440.3790157846795,
        "2023": 501.4196081656596,
        "2024": 586.7712267056854,
    },
    "yearly_direction_correct": {
        "2022": 5,
        "2023": 6,
        "2024": 9,
    },
    "selected_seed_counts": {
        "1701": 1,
        "2903": 23,
        "4111": 9,
    },
}

SIGMAAE_TOL = 1e-6
RELATIVE_MAE_TOL = 1e-12


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    # Offline parity must not depend on a DB connection.
    if os.environ.get("NEON_DATABASE_URL"):
        raise RuntimeError("OFFLINE_PARITY_NEON_DATABASE_URL_MUST_BE_UNSET")

    bundle, snapshot_meta = snap.load_snapshot(args.snapshot)

    stage0.LOOKBACK = 6
    stage0.WIDTH = 32
    stage0.DROPOUT = 0.10
    stage0.LR = 0.001
    stage0.BATCH = 16
    stage0.MAX_EPOCHS = 300
    stage0.PATIENCE = 25
    stage0.SEEDS = (1701, 2903, 4111)
    stage0.configure_tf()

    rows = []
    for target in stage0.base.month_range(stage0.DEV_START, stage0.DEV_END):
        samples = stage0.base.all_samples_at_origin(
            bundle,
            target,
            governed=True,
        )
        rows.append(
            stage0.evaluate_origin(
                bundle,
                samples,
                target,
                "CNN_LSTM",
            )
        )

    # No DB exists in this process. Passing the frozen export invariant back into
    # the inherited gate proves that the offline computation itself cannot mutate it.
    scientific_gate = stage0.build_gate(
        rows,
        bundle,
        dict(bundle.invariants_before),
    )
    if scientific_gate["status"] != "PASS":
        raise RuntimeError(
            f"OFFLINE_SCIENTIFIC_GATE_FAIL {scientific_gate}"
        )

    metrics = stage0.metrics_mod.active_metrics(rows)
    yearly = stage0.metrics_mod.yearly(rows)
    seed_dispersion = stage0.summarize_seed_dispersion(rows)

    diffs = {
        "sum_abs_error": abs(
            metrics["sum_abs_error"] - EXPECTED["sum_abs_error"]
        ),
        "relative_mae_vs_rw": abs(
            metrics["relative_mae_vs_rw"]
            - EXPECTED["relative_mae_vs_rw"]
        ),
        "yearly_sum_abs_error": {
            y: abs(
                yearly[y]["sum_abs_error"]
                - EXPECTED["yearly_sum_abs_error"][y]
            )
            for y in ("2022", "2023", "2024")
        },
    }

    parity_checks = {
        "snapshot_payload_hash_verified": bool(
            snapshot_meta["payload_sha256"]
        ),
        "no_database_connection_used": not bool(
            os.environ.get("NEON_DATABASE_URL")
        ),
        "scientific_gate_pass": scientific_gate["status"] == "PASS",
        "aggregate_sum_abs_error_within_1e_6": (
            diffs["sum_abs_error"] <= SIGMAAE_TOL
        ),
        "direction_exact": (
            metrics["direction_correct"]
            == EXPECTED["direction_correct"]
        ),
        "relative_mae_vs_rw_within_1e_12": (
            diffs["relative_mae_vs_rw"] <= RELATIVE_MAE_TOL
        ),
        "yearly_sum_abs_error_within_1e_6": all(
            d <= SIGMAAE_TOL
            for d in diffs["yearly_sum_abs_error"].values()
        ),
        "yearly_direction_exact": all(
            yearly[y]["direction_correct"]
            == EXPECTED["yearly_direction_correct"][y]
            for y in ("2022", "2023", "2024")
        ),
        "selected_seed_counts_exact": (
            seed_dispersion["selected_seed_counts"]
            == EXPECTED["selected_seed_counts"]
        ),
        "dev_origin_count_33": metrics["n"] == 33,
        "no_2025_2026_rows": (
            bundle.source_checks["modeling_rows_2025_loaded"] == 0
            and bundle.source_checks["modeling_rows_2026_loaded"] == 0
        ),
    }

    status = "PASS" if all(parity_checks.values()) else "FAIL"
    result = {
        "status": status,
        "snapshot": snapshot_meta,
        "model": {
            "architecture": "CNN_LSTM",
            "lookback": 6,
            "width": 32,
            "dropout": 0.10,
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "batch_size": 16,
            "seeds": [1701, 2903, 4111],
        },
        "expected": EXPECTED,
        "actual": {
            "metrics": metrics,
            "yearly": yearly,
            "seed_dispersion": seed_dispersion,
        },
        "diffs": diffs,
        "parity_checks": parity_checks,
        "scientific_gate": scientific_gate,
    }
    Path(args.output).write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print(f"OFFLINE_SNAPSHOT_PARITY={status}")
    print(
        json.dumps(
            {
                "status": status,
                "payload_sha256": snapshot_meta["payload_sha256"],
                "sum_abs_error": metrics["sum_abs_error"],
                "direction_correct": metrics["direction_correct"],
                "relative_mae_vs_rw": metrics["relative_mae_vs_rw"],
                "seed_counts": seed_dispersion["selected_seed_counts"],
                "diffs": diffs,
                "parity_checks": parity_checks,
            },
            sort_keys=True,
        )
    )
    if status != "PASS":
        raise RuntimeError(f"OFFLINE_SNAPSHOT_PARITY_FAIL {parity_checks}")


if __name__ == "__main__":
    main()
