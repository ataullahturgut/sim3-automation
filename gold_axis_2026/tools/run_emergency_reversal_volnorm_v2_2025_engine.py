from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import emergency_reversal_volnorm_successor_v1 as core
import emergency_reversal_volnorm_successor_v2 as m

HISTORY_YEARS = (2022, 2023, 2024, 2025)
EXPECTED_CONFIG_SHA = "0419bd741d08f92c755e7ae8e26ebd6c1caf2619ed7518fda72b555bc7bdebdc"
EXPECTED_IMPLEMENTATION_SHA = "a35aeeed794ecd72e41036ce51178c38e8d29bc4ea1833e7dbfe3c0f03330a4e"


def _records(frame: pd.DataFrame) -> list[dict]:
    return frame.astype(object).where(pd.notna(frame), None).to_dict(orient="records")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="/tmp/emergency-reversal-volnorm-v2-2025")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if m.config_sha() != EXPECTED_CONFIG_SHA:
        raise RuntimeError(f"FROZEN_CONFIG_SHA_MISMATCH:{m.config_sha()}")
    if m.implementation_hash() != EXPECTED_IMPLEMENTATION_SHA:
        raise RuntimeError(f"FROZEN_IMPLEMENTATION_SHA_MISMATCH:{m.implementation_hash()}")

    closes, evidence = m.fetch_twelve_closes(HISTORY_YEARS)
    if closes.index.min() < pd.Timestamp("2022-01-01") or closes.index.max() >= pd.Timestamp("2026-01-01"):
        raise RuntimeError("ENGINE_SOURCE_BOUNDARY_FAIL")

    full = m.run_detector(closes)
    dates = pd.to_datetime(full["date"])
    timeline = full.loc[dates.dt.year.eq(2025)].reset_index(drop=True)
    if timeline.empty:
        raise RuntimeError("EMPTY_2025_ENGINE_TIMELINE")
    alerts = timeline[timeline.alert != "OFF"].copy()

    records = _records(timeline)
    timeline_sha = core.stable_sha(records)
    payload = {
        "model_id": m.MODEL_ID,
        "stage": "ENGINE_FIRST_2025_FULL_TIMELINE",
        "volatility_inventory_loaded": False,
        "config_sha256": EXPECTED_CONFIG_SHA,
        "implementation_sha256": EXPECTED_IMPLEMENTATION_SHA,
        "timeline_sha256": timeline_sha,
        "source": evidence,
        "timeline": records,
    }
    summary = {
        "model_id": m.MODEL_ID,
        "stage": "ENGINE_FIRST_2025_FULL_TIMELINE",
        "volatility_inventory_loaded": False,
        "config_sha256": EXPECTED_CONFIG_SHA,
        "implementation_sha256": EXPECTED_IMPLEMENTATION_SHA,
        "timeline_sha256": timeline_sha,
        "source_2025_coverage": evidence["coverage"][2025],
        "engine_rows_2025": int(len(timeline)),
        "eligible_rows_2025": int(timeline.eligible.sum()),
        "reversal_alerts_2025": int(len(alerts)),
        "up_alerts_2025": int((alerts.alert == "UP_ALERT").sum()),
        "down_alerts_2025": int((alerts.alert == "DOWN_ALERT").sum()),
        "major_alerts_2025": int((alerts.alert_severity == "MAJOR").sum()),
        "extreme_alerts_2025": int((alerts.alert_severity == "EXTREME").sum()),
        "first_2025_date": str(timeline.iloc[0].date),
        "last_2025_date": str(timeline.iloc[-1].date),
        "production_write": "NONE",
    }

    timeline.to_csv(out / "engine_2025_full_timeline.csv", index=False)
    alerts.to_csv(out / "engine_2025_alerts.csv", index=False)
    (out / "engine_2025_frozen_payload.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (out / "engine_2025_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
