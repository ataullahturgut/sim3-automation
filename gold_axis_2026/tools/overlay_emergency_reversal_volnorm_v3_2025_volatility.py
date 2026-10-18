from __future__ import annotations

import argparse
import json
from pathlib import Path

import emergency_reversal_volnorm_successor_v1 as core

EVENTS = [
    ("2025-02-10", "UP", "MAJOR", 2.3407),
    ("2025-02-14", "DOWN", "MAJOR", -2.2468),
    ("2025-02-18", "UP", "MAJOR", 2.1885),
    ("2025-03-13", "UP", "MAJOR", 2.1237),
    ("2025-04-04", "DOWN", "EXTREME", -3.3930),
    ("2025-04-09", "UP", "EXTREME", 3.2185),
    ("2025-04-10", "UP", "MAJOR", 2.3440),
    ("2025-07-21", "UP", "MAJOR", 2.0611),
    ("2025-08-01", "UP", "MAJOR", 2.5481),
    ("2025-09-02", "UP", "MAJOR", 2.6673),
    ("2025-09-22", "UP", "MAJOR", 2.6254),
    ("2025-09-29", "UP", "MAJOR", 2.3040),
    ("2025-10-06", "UP", "MAJOR", 2.7911),
    ("2025-10-13", "UP", "MAJOR", 2.5043),
    ("2025-10-16", "UP", "MAJOR", 2.9074),
    ("2025-10-17", "DOWN", "MAJOR", -2.0589),
    ("2025-10-21", "DOWN", "EXTREME", -4.1054),
    ("2025-12-22", "UP", "EXTREME", 4.0174),
    ("2025-12-29", "DOWN", "EXTREME", -6.6415),
]


def _direction(alert: str) -> str | None:
    if alert == "UP_ALERT":
        return "UP"
    if alert == "DOWN_ALERT":
        return "DOWN"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="/tmp/emergency-reversal-volnorm-v3-2025")
    args = parser.parse_args()
    root = Path(args.input_dir)

    payload = json.loads((root / "engine_2025_frozen_payload.json").read_text(encoding="utf-8"))
    engine_summary = json.loads((root / "engine_2025_summary.json").read_text(encoding="utf-8"))
    if payload.get("model_id") != "EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V3":
        raise RuntimeError("ENGINE_IDENTITY_FAIL")
    if payload.get("volatility_inventory_loaded") is not False:
        raise RuntimeError("ENGINE_STAGE_SEPARATION_FAIL")
    if core.stable_sha(payload["timeline"]) != payload["timeline_sha256"]:
        raise RuntimeError("ENGINE_TIMELINE_HASH_FAIL")
    if engine_summary["timeline_sha256"] != payload["timeline_sha256"]:
        raise RuntimeError("ENGINE_SUMMARY_HASH_MISMATCH")
    if len(EVENTS) != 19 or len({x[0] for x in EVENTS}) != 19:
        raise RuntimeError("FROZEN_EVENT_INVENTORY_FAIL")

    rows_by_date = {row["date"]: row for row in payload["timeline"]}
    event_map = {d: {"direction": direction, "tier": tier, "z": z} for d, direction, tier, z in EVENTS}

    event_overlay = []
    for date, direction, tier, z in EVENTS:
        row = rows_by_date.get(date)
        if row is None:
            result = "NOT_TESTABLE_NO_ENGINE_SOURCE_DATE"
            alert = alert_direction = score = severity = state = reference_extreme_date = None
        else:
            alert = row["alert"]
            alert_direction = _direction(alert)
            score = row["alert_score"]
            severity = row["alert_severity"]
            state = row["state"]
            reference_extreme_date = row["reference_extreme_date"]
            if alert_direction is None:
                result = "NO_REVERSAL_ALERT"
            elif alert_direction == direction:
                result = "SAME_DAY_DIRECTION_ALIGNED"
            else:
                result = "SAME_DAY_DIRECTION_OPPOSED"
        event_overlay.append(
            {
                "date": date,
                "volatility_direction": direction,
                "volatility_tier": tier,
                "volatility_z": z,
                "engine_state": state,
                "engine_alert": alert,
                "engine_alert_direction": alert_direction,
                "engine_alert_score": score,
                "engine_alert_severity": severity,
                "reference_extreme_date": reference_extreme_date,
                "result": result,
            }
        )

    alert_overlay = []
    for row in payload["timeline"]:
        alert_direction = _direction(row["alert"])
        if alert_direction is None:
            continue
        event = event_map.get(row["date"])
        if event is None:
            result = "NO_SAME_DAY_VOLATILITY_OVERLAY"
        elif alert_direction == event["direction"]:
            result = "SAME_DAY_DIRECTION_ALIGNED"
        else:
            result = "SAME_DAY_DIRECTION_OPPOSED"
        alert_overlay.append(
            {
                "date": row["date"],
                "alert": row["alert"],
                "alert_direction": alert_direction,
                "alert_score": row["alert_score"],
                "alert_severity": row["alert_severity"],
                "reference_extreme_date": row["reference_extreme_date"],
                "same_day_volatility_event": event,
                "result": result,
            }
        )

    # Secondary descriptive proximity only; same-date comparison remains primary.
    ordered_dates = [row["date"] for row in payload["timeline"]]
    pos = {d: i for i, d in enumerate(ordered_dates)}
    alert_dates = [(a["date"], a["alert_direction"]) for a in alert_overlay]
    proximity = []
    for date, direction, tier, z in EVENTS:
        if date not in pos:
            proximity.append(
                {"date": date, "direction": direction, "nearest_aligned_distance": None, "nearest_opposed_distance": None}
            )
            continue
        p = pos[date]
        aligned = [abs(pos[d] - p) for d, a_dir in alert_dates if d in pos and a_dir == direction]
        opposed = [abs(pos[d] - p) for d, a_dir in alert_dates if d in pos and a_dir != direction]
        proximity.append(
            {
                "date": date,
                "direction": direction,
                "nearest_aligned_distance": min(aligned) if aligned else None,
                "nearest_opposed_distance": min(opposed) if opposed else None,
            }
        )

    summary = {
        "model_id": payload["model_id"],
        "stage": "POST_FREEZE_VOLATILITY_OVERLAY",
        "engine_timeline_sha256": payload["timeline_sha256"],
        "frozen_volatility_events": 19,
        "engine_alerts_2025": len(alert_overlay),
        "same_day_direction_aligned": sum(x["result"] == "SAME_DAY_DIRECTION_ALIGNED" for x in event_overlay),
        "same_day_direction_opposed": sum(x["result"] == "SAME_DAY_DIRECTION_OPPOSED" for x in event_overlay),
        "event_days_no_reversal_alert": sum(x["result"] == "NO_REVERSAL_ALERT" for x in event_overlay),
        "event_days_not_testable": sum(x["result"] == "NOT_TESTABLE_NO_ENGINE_SOURCE_DATE" for x in event_overlay),
        "alerts_no_same_day_volatility_overlay": sum(
            x["result"] == "NO_SAME_DAY_VOLATILITY_OVERLAY" for x in alert_overlay
        ),
        "aligned_within_1_observed_day": sum(
            x["nearest_aligned_distance"] is not None and x["nearest_aligned_distance"] <= 1 for x in proximity
        ),
        "aligned_within_3_observed_days": sum(
            x["nearest_aligned_distance"] is not None and x["nearest_aligned_distance"] <= 3 for x in proximity
        ),
        "production_write": "NONE",
    }
    result = {
        "summary": summary,
        "event_overlay": event_overlay,
        "alert_overlay": alert_overlay,
        "descriptive_proximity": proximity,
    }
    (root / "volatility_overlay.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
