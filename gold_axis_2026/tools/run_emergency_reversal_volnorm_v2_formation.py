from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import emergency_reversal_volnorm_successor_v2 as m

FORMATION_YEARS = (2022, 2023, 2024)


def _prefix_invariance(closes: pd.Series, full: pd.DataFrame) -> None:
    checkpoints = [80, 140, 220, 320, 450, max(60, len(closes) - 40)]
    cols = ["date", "state", "state_age", "alert", "alert_score", "alert_severity", "reference_extreme_date", "eligible"]
    for n in sorted(set(x for x in checkpoints if 40 < x < len(closes))):
        prefix = m.run_detector(closes.iloc[:n])
        pd.testing.assert_frame_equal(
            full.iloc[:n][cols].reset_index(drop=True),
            prefix[cols].reset_index(drop=True),
            check_dtype=False,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="/tmp/emergency-reversal-volnorm-v2-formation")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    closes, evidence = m.fetch_twelve_closes(FORMATION_YEARS)
    if closes.index.min() < pd.Timestamp("2022-01-01") or closes.index.max() >= pd.Timestamp("2025-01-01"):
        raise RuntimeError("FORMATION_BOUNDARY_FAIL")

    first = m.run_detector(closes)
    second = m.run_detector(closes)
    h1, h2 = m.timeline_hash(first), m.timeline_hash(second)
    if h1 != h2:
        raise RuntimeError("DETERMINISM_FAIL")
    _prefix_invariance(closes, first)

    eligible_n = int(first.eligible.sum())
    alerts = first[first.alert != "OFF"].copy()
    alert_n = int(len(alerts))
    if alert_n < 3:
        raise RuntimeError(f"REJECTED_FORMATION_DEGENERATE_TOO_FEW_ALERTS:{alert_n}")
    if eligible_n <= 0 or alert_n / eligible_n >= 0.20:
        raise RuntimeError(f"REJECTED_FORMATION_DEGENERATE_TOO_MANY_ALERTS:{alert_n}/{eligible_n}")

    summary = {
        "model_id": m.MODEL_ID,
        "status": "FORMATION_PASS_2025_NOT_READ",
        "formation_years": list(FORMATION_YEARS),
        "source": evidence,
        "config": m.config().as_dict() | {"selected_hour": m.SELECTED_HOUR, "min_year_coverage": m.MIN_YEAR_COVERAGE},
        "config_sha256": m.config_sha(),
        "implementation_sha256": m.implementation_hash(),
        "timeline_sha256": h1,
        "selected_closes": int(len(closes)),
        "eligible_post_warmup_rows": eligible_n,
        "reversal_alerts": alert_n,
        "up_alerts": int((alerts.alert == "UP_ALERT").sum()),
        "down_alerts": int((alerts.alert == "DOWN_ALERT").sum()),
        "extreme_alerts": int((alerts.alert_severity == "EXTREME").sum()),
        "alert_rate": alert_n / eligible_n,
        "last_input_date": closes.index.max().date().isoformat(),
        "future_2025_observations_consumed": 0,
        "production_write": "NONE",
    }

    first.to_csv(out / "formation_full_timeline.csv", index=False)
    alerts.to_csv(out / "formation_alerts.csv", index=False)
    closes.rename("close").to_csv(out / "formation_selected_closes.csv", index_label="date")
    (out / "formation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
