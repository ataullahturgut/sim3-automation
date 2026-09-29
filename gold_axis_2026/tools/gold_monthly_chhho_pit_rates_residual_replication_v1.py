from __future__ import annotations

import argparse
import json
from pathlib import Path

import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_external_pit_residual_v1 as pit

EXPECTED_BASE = 1413.0299
EXPECTED_CORRECTED = 1370.9204
EXPECTED_DIRECTION = 23
TOL = 5e-4

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chhho", required=True)
    ap.add_argument("--external", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    snap, ext = pit.load_ext(a.external)
    m = core.load_model(a.chhho, "ChHHO-ANFIS")
    cols = pit.BLOCKS["PIT_RATES"]

    base_metrics = core.metrics(m["dev"])
    corr = core.prequential(m["dev"], ext, cols)
    corrected_metrics = core.metrics(corr, "corrected_forecast")
    gate = core.stability_gate(m["dev"], corr)
    diag = core.diagnostic(m["dev"], ext, cols)

    eligible = [r for r in corr if r["eligible"]]
    first_eligible = eligible[0]["target"] if eligible else None

    exact = (
        abs(base_metrics["sum_ae"] - EXPECTED_BASE) <= TOL
        and abs(corrected_metrics["sum_ae"] - EXPECTED_CORRECTED) <= TOL
        and corrected_metrics["direction_correct"] == EXPECTED_DIRECTION
        and gate.get("pass") is True
    )

    out = {
        "schema": "GOLD_MONTHLY_CHHHO_PIT_RATES_RESIDUAL_EXACT_REPLICATION_V1_2026-09-29",
        "authority": {
            "base_model_frozen": True,
            "base_artifact_id": 10989389723,
            "external_snapshot": "GOLD_MONTHLY_EXTERNAL_PIT_COMPACT_V1_2026-09-28",
            "block": "PIT_RATES",
            "columns": cols,
            "target_of_residual_model": "price residual = actual price - frozen base forecast price",
            "model": "Ridge",
            "ridge_alpha": core.RIDGE_ALPHA,
            "min_prior_residuals": core.MIN_HISTORY,
            "cap_multiple": core.CAP_MULT,
            "scaler": "StandardScaler fit on prior eligible residual rows only",
            "chronology": "prequential; prior DEV residuals only",
            "random_split": False,
            "2025_used_for_selection": False,
            "neon_reads": 0,
        },
        "external_snapshot_schema": snap["schema"],
        "external_evidence_class": snap["evidence_class"],
        "base_metrics": base_metrics,
        "corrected_metrics": corrected_metrics,
        "gate": gate,
        "diagnostics": diag,
        "rows": corr,
        "first_eligible_target": first_eligible,
        "expected": {
            "base_sum_ae": EXPECTED_BASE,
            "corrected_sum_ae": EXPECTED_CORRECTED,
            "corrected_direction": EXPECTED_DIRECTION,
            "tolerance": TOL,
        },
        "exact_replication_pass": exact,
    }

    Path(a.output).write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")

    print("CHHHO_PIT_RATES_REPLICATION_GATE=" + ("PASS" if exact else "FAIL"))
    print(json.dumps({
        "base_sum_ae": base_metrics["sum_ae"],
        "base_direction": base_metrics["direction_correct"],
        "corrected_sum_ae": corrected_metrics["sum_ae"],
        "corrected_direction": corrected_metrics["direction_correct"],
        "full_dev_improvement": base_metrics["sum_ae"] - corrected_metrics["sum_ae"],
        "gate": gate,
        "first_eligible_target": first_eligible,
        "exact_replication_pass": exact,
    }, sort_keys=True))

    if not exact:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
