from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import emergency_reversal_volnorm_successor_v1 as core
import emergency_reversal_volnorm_successor_v3 as m

HISTORY_YEARS = (2022, 2023, 2024, 2025)
EXPECTED_CONFIG_SHA = "fdb2c6238fc194afd9c5a253ae232790bdde5b6faa49cbcd96811972d5a83a84"
EXPECTED_IMPLEMENTATION_SHA = "4adcec3043b141babd38a7bef9ed854f3fdb868bd84a88a32e835fa1e6921cbd"


def _records(frame: pd.DataFrame) -> list[dict]:
    return frame.astype(object).where(pd.notna(frame), None).to_dict(orient="records")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="/tmp/emergency-reversal-volnorm-v3-2025")
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
    if any(pd.Timestamp(d).dayofweek >= 5 for d in closes.index):
        raise RuntimeError("ENGINE_WEEKEND_SOURCE_FAIL")

    source_2025 = evidence["coverage"][2025]
    if int(source_2025["selected"]) > int(source_2025["calendar_weekdays"]):
        raise RuntimeError(f"ENGINE_SELECTED_EXCEEDS_CALENDAR_WEEKDAYS:{source_2025}")
    if int(source_2025["calendar_weekdays"]) != 261:
        raise RuntimeError(f"UNEXPECTED_2025_CALENDAR_WEEKDAYS:{source_2025}")
    if float(source_2025["ratio"]) < 0.95:
        raise RuntimeError(f"BLOCKED_2025_DATA_COVERAGE:{source_2025}")

    full = m.run_detector(closes)
    dates = pd.to_datetime(full["date"])
    timeline = full.loc[dates.dt.year.eq(2025)].reset_index(drop=True)
    if timeline.empty:
        raise RuntimeError("EMPTY_2025_ENGINE_TIMELINE")
    parsed = pd.to_datetime(timeline["date"])
    if parsed.dt.dayofweek.ge(5).any():
        raise RuntimeError("ENGINE_TIMELINE_WEEKEND_FAIL")
    if len(timeline) != int(source_2025["selected"]):
        raise RuntimeError(f"ENGINE_SOURCE_ROW_RECONCILIATION_FAIL:{len(timeline)}:{source_2025}")

    alerts = timeline[timeline.alert != "OFF"].copy()
    records = _records(timeline)
    timeline_sha = core.stable_sha(records)
    payload = {
        "model_id": m.MODEL_ID,
        "stage": "ENGINE_FIRST_2025_FULL_WEEKDAY_TIMELINE",
        "volatility_inventory_loaded": False,
        "config_sha256": EXPECTED_CONFIG_SHA,
        "implementation_sha256": EXPECTED_IMPLEMENTATION_SHA,
        "timeline_sha256": timeline_sha,
        "source": evidence,
        "timeline": records,
    }
    summary = {
        "model_id": m.MODEL_ID,
        "stage": "ENGINE_FIRST_2025_FULL_WEEKDAY_TIMELINE",
        "volatility_inventory_loaded": False,
        "config_sha256": EXPECTED_CONFIG_SHA,
        "implementation_sha256": EXPECTED_IMPLEMENTATION_SHA,
        "timeline_sha256": timeline_sha,
        "source_2025_coverage": source_2025,
        "source_rejected_weekend_bars_all_years": int(evidence["rejected_weekend_bars"]),
        "engine_rows_2025": int(len(timeline)),
        "weekend_engine_rows_2025": int(parsed.dt.dayofweek.ge(5).sum()),
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
