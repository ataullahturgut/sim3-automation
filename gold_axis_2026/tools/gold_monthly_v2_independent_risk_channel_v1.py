from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PERIODS = {
    "DEV_2022_04_2024_12": ("2022-04", "2024-12"),
    "OPENED_2025": ("2025-01", "2025-12"),
    "OPENED_2026": ("2026-01", "2026-08"),
    "OPENED_2025_2026": ("2025-01", "2026-08"),
}


def load_json(path: str):
    return json.loads(Path(path).read_text())


def subset(rows, start, end):
    return [r for r in rows if start <= r["target"] <= end]


def safe_rate(num, den):
    return None if den == 0 else float(num / den)


def safe_ratio(a, b):
    if a is None or b is None or b == 0:
        return None
    return float(a / b)


def safe_diff(a, b):
    if a is None or b is None:
        return None
    return float(a - b)


def severity_summary(rows):
    c = Counter(r["severity"] for r in rows)
    n = len(rows)
    high = int(c.get("HIGH", 0))
    med = int(c.get("MEDIUM", 0))
    normal = int(c.get("NORMAL", 0))
    elev = high + med
    return {
        "n": n,
        "high": high,
        "medium": med,
        "elevated": elev,
        "normal": normal,
        "high_rate": safe_rate(high, n),
        "medium_rate": safe_rate(med, n),
        "elevated_rate": safe_rate(elev, n),
        "normal_rate": safe_rate(normal, n),
    }


def status_comparison(rows):
    stable = [r for r in rows if not r["v2_transition_flag"]]
    trans = [r for r in rows if r["v2_transition_flag"]]
    s = severity_summary(stable)
    t = severity_summary(trans)
    return {
        "STABLE": s,
        "TRANSITION": t,
        "transition_vs_stable": {
            "high_risk_ratio": safe_ratio(t["high_rate"], s["high_rate"]),
            "elevated_risk_ratio": safe_ratio(t["elevated_rate"], s["elevated_rate"]),
            "high_rate_difference": safe_diff(t["high_rate"], s["high_rate"]),
            "elevated_rate_difference": safe_diff(t["elevated_rate"], s["elevated_rate"]),
        },
    }


def quiet_slice(rows, alarm_field):
    no_alarm = [r for r in rows if not bool(r[alarm_field])]
    stable = [r for r in no_alarm if not r["v2_transition_flag"]]
    trans = [r for r in no_alarm if r["v2_transition_flag"]]
    return {
        "alarm_field": alarm_field,
        "NO_ALARM_STABLE": severity_summary(stable),
        "NO_ALARM_TRANSITION": severity_summary(trans),
        "transition_rows": [
            {
                "origin": r["origin"],
                "target": r["target"],
                "semantic_state": r["v2_semantic_state"],
                "semantic_label": r["v2_semantic_label"],
                "semantic_probability": r["v2_semantic_probability"],
                "severity": r["severity"],
                "ape_pct": float(r["ape_pct"]),
                "active_signals": list(r["active_signals"]),
            }
            for r in trans
        ],
    }


def union_metrics(rows, field=None, or_v2=False):
    if field is None:
        fired = [bool(r["v2_transition_flag"]) for r in rows]
    else:
        fired = [
            bool(r[field]) or (or_v2 and bool(r["v2_transition_flag"]))
            for r in rows
        ]

    event_rows = [r for r, f in zip(rows, fired) if f]
    sev = Counter(r["severity"] for r in rows)
    hh = sum(r["severity"] == "HIGH" for r in event_rows)
    mh = sum(r["severity"] == "MEDIUM" for r in event_rows)
    fc = sum(r["severity"] == "NORMAL" for r in event_rows)
    high_all = int(sev.get("HIGH", 0))
    elev_all = int(sev.get("HIGH", 0) + sev.get("MEDIUM", 0))
    n_events = len(event_rows)

    return {
        "events": n_events,
        "high_hits": int(hh),
        "medium_hits": int(mh),
        "false_calls": int(fc),
        "high_recall": safe_rate(hh, high_all),
        "elevated_recall": safe_rate(hh + mh, elev_all),
        "false_call_rate": safe_rate(fc, n_events),
        "useful_call_rate": safe_rate(hh + mh, n_events),
        "event_origins": [r["origin"] for r in event_rows],
        "event_targets": [r["target"] for r in event_rows],
    }


def union_report(rows):
    return {
        "V2_TRANSITION_ONLY": union_metrics(rows, field=None),
        "ANY_VISIBLE": union_metrics(rows, "ANY_VISIBLE", or_v2=False),
        "ANY_VISIBLE_OR_V2": union_metrics(rows, "ANY_VISIBLE", or_v2=True),
        "T0_STANDARD": union_metrics(rows, "T0_STANDARD", or_v2=False),
        "T0_STANDARD_OR_V2": union_metrics(rows, "T0_STANDARD", or_v2=True),
    }


def regime_cells(rows):
    out = {}
    for regime in ["R0", "R1", "R2", "BELIRSIZ"]:
        for status in ["STABLE", "TRANSITION"]:
            if regime == "BELIRSIZ":
                rr = [
                    r for r in rows
                    if r["v2_semantic_label"] not in {"R0", "R1", "R2"}
                    and r["v2_transition_status"] == status
                ]
            else:
                rr = [
                    r for r in rows
                    if r["v2_semantic_label"] == regime
                    and r["v2_transition_status"] == status
                ]
            q = severity_summary(rr)
            q["evidence_label"] = (
                "NO_EVENTS" if q["n"] == 0
                else "SMALL_N" if q["n"] < 3
                else "REPORTABLE"
            )
            q["origins"] = [r["origin"] for r in rr]
            q["targets"] = [r["target"] for r in rr]
            out[f"{regime}_{status}"] = q
    return out


def period_report(rows):
    return {
        "n": len(rows),
        "status_comparison": status_comparison(rows),
        "no_any_visible": quiet_slice(rows, "ANY_VISIBLE"),
        "no_t0_standard": quiet_slice(rows, "T0_STANDARD"),
        "union_augmentation": union_report(rows),
        "regime_cells": regime_cells(rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.audit_json)
    if src.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_SOURCE")
    if src.get("primary_schedule") != "EXPANDING_REFIT":
        raise RuntimeError("INVALID_SCHEDULE")
    if src.get("join_contract", {}).get("target_month_v2_state_used") is not False:
        raise RuntimeError("BAD_JOIN_CONTRACT")

    rows = sorted(src["rows"], key=lambda r: r["origin"])
    if len(rows) != 58:
        raise RuntimeError(("ROW_COUNT", len(rows)))

    periods = {
        name: period_report(subset(rows, a, b))
        for name, (a, b) in PERIODS.items()
    }
    periods["FULL_COMMON"] = period_report(rows)

    dev = periods["DEV_2022_04_2024_12"]
    st = dev["status_comparison"]["STABLE"]
    tr = dev["status_comparison"]["TRANSITION"]
    no_any_tr = dev["no_any_visible"]["NO_ALARM_TRANSITION"]

    candidate_gate = {
        "high_rate_transition_gt_stable": bool(
            tr["high_rate"] is not None
            and st["high_rate"] is not None
            and tr["high_rate"] > st["high_rate"]
        ),
        "elevated_rate_transition_gt_stable": bool(
            tr["elevated_rate"] is not None
            and st["elevated_rate"] is not None
            and tr["elevated_rate"] > st["elevated_rate"]
        ),
        "incremental_dev_high_with_no_any_visible": bool(no_any_tr["high"] >= 1),
        "observed": {
            "stable_high_rate": st["high_rate"],
            "transition_high_rate": tr["high_rate"],
            "stable_elevated_rate": st["elevated_rate"],
            "transition_elevated_rate": tr["elevated_rate"],
            "v2_transition_no_any_visible_high_count": no_any_tr["high"],
        },
    }
    candidate_gate["candidate_pass"] = all([
        candidate_gate["high_rate_transition_gt_stable"],
        candidate_gate["elevated_rate_transition_gt_stable"],
        candidate_gate["incremental_dev_high_with_no_any_visible"],
    ])

    result = {
        "schema": "GOLD_MONTHLY_V2_INDEPENDENT_RISK_CHANNEL_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "primary_schedule": "EXPANDING_REFIT",
        "risk_channel": "V2_TRANSITION at origin t",
        "periods": periods,
        "dev_candidate_gate": candidate_gate,
        "transition_rows_full_common": [
            {
                "origin": r["origin"],
                "target": r["target"],
                "semantic_state": r["v2_semantic_state"],
                "semantic_label": r["v2_semantic_label"],
                "semantic_probability": r["v2_semantic_probability"],
                "severity": r["severity"],
                "ape_pct": float(r["ape_pct"]),
                "ANY_VISIBLE": bool(r["ANY_VISIBLE"]),
                "T0_STANDARD": bool(r["T0_STANDARD"]),
                "active_signals": list(r["active_signals"]),
            }
            for r in rows if r["v2_transition_flag"]
        ],
        "governance": {
            "v2_retuned": False,
            "v2_threshold_changed": False,
            "alarm_definitions_changed": False,
            "severity_thresholds_changed": False,
            "weight_model_fit": False,
            "existing_alarm_suppression_performed": False,
            "2025_2026_used_for_candidate_selection": False,
            "target_month_v2_state_used": False,
            "forecast_modified": False,
            "routing_tested": False,
        },
    }

    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "dev_candidate_gate": candidate_gate,
        "dev": periods["DEV_2022_04_2024_12"],
        "opened_2025": periods["OPENED_2025"],
        "opened_2026": periods["OPENED_2026"],
        "opened_2025_2026": periods["OPENED_2025_2026"],
        "full_common": periods["FULL_COMMON"],
        "transition_rows": result["transition_rows_full_common"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
