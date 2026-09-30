from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

SIGNALS = [
    "A", "B", "C", "D", "E", "G", "H", "I1", "I2", "T1_WGC",
    "T0_STANDARD", "ANY_VISIBLE",
]

PERIODS = {
    "DEV_2022_04_2024_12": ("2022-04", "2024-12"),
    "OPENED_2025": ("2025-01", "2025-12"),
    "OPENED_2026": ("2026-01", "2026-08"),
    "OPENED_2025_2026": ("2025-01", "2026-08"),
}


def load_json(path: str):
    return json.loads(Path(path).read_text())


def safe_rate(num: int, den: int):
    return None if den == 0 else float(num / den)


def live_cell(v2row: dict) -> str:
    label = str(v2row["semantic_label"])
    status = "TRANSITION" if bool(v2row["transition_flag"]) else "STABLE"
    if label not in {"R0", "R1", "R2"}:
        label = "BELIRSIZ"
    return f"{label}_{status}"


def posterior_bucket(v2row: dict) -> str:
    p = float(v2row["semantic_probability"])
    if p >= 0.80:
        return "HIGH_CONF"
    if p >= 0.60:
        return "MID_CONF"
    return "BELIRSIZ"


def build_reference_zone_set(v2: dict):
    zone = set()
    for e in v2.get("reference_events", []):
        zone.update(e.get("zone_months", []))
    return zone


def join_rows(alarm: dict, v2: dict):
    vmap = {r["month"]: r for r in v2["rows"]["EXPANDING_REFIT"]}
    zone = build_reference_zone_set(v2)

    out = []
    for r in alarm["rows"]:
        origin = r["origin"]
        if origin not in vmap:
            continue
        vr = vmap[origin]
        z = dict(r)
        z.update({
            "v2_semantic_state": vr["semantic_state"],
            "v2_semantic_label": vr["semantic_label"],
            "v2_semantic_probability": float(vr["semantic_probability"]),
            "v2_transition_flag": bool(vr["transition_flag"]),
            "v2_transition_status": vr["transition_status"],
            "v2_fast_branch": bool(vr.get("fast_branch", False)),
            "v2_persistent_branch": bool(vr.get("persistent_branch", False)),
            "v2_current_directional_votes": int(vr.get("current_directional_votes", 0)),
            "v2_current_directional_flags": list(vr.get("current_directional_flags", [])),
            "live_cell": live_cell(vr),
            "posterior_bucket": posterior_bucket(vr),
            "reference_transition_context": (
                "IN_REFERENCE_ZONE" if origin in zone else "OUTSIDE_REFERENCE_ZONE"
            ) if bool(vr["transition_flag"]) else "NOT_TRANSITION",
        })
        out.append(z)
    return out


def subset(rows, start: str, end: str):
    return [r for r in rows if start <= r["target"] <= end]


def signal_metrics(rows, signal: str):
    sev = Counter(r["severity"] for r in rows)
    outcomes = Counter(r[f"{signal}_outcome"] for r in rows)

    high_hits = int(outcomes.get("HIGH_HIT", 0))
    med_hits = int(outcomes.get("MEDIUM_HIT", 0))
    false_calls = int(outcomes.get("FALSE_CALL", 0))
    events = high_hits + med_hits + false_calls

    return {
        "n_target_months": len(rows),
        "high_targets": int(sev.get("HIGH", 0)),
        "medium_targets": int(sev.get("MEDIUM", 0)),
        "normal_targets": int(sev.get("NORMAL", 0)),
        "alarm_events": events,
        "high_hits": high_hits,
        "medium_hits": med_hits,
        "false_calls": false_calls,
        "high_recall": safe_rate(high_hits, int(sev.get("HIGH", 0))),
        "medium_recall": safe_rate(med_hits, int(sev.get("MEDIUM", 0))),
        "false_call_rate": safe_rate(false_calls, events),
        "useful_call_rate": safe_rate(high_hits + med_hits, events),
        "evidence_label": (
            "NO_EVENTS" if events == 0
            else "SMALL_N" if events < 3
            else "REPORTABLE"
        ),
    }


def by_group(rows, key: str):
    groups = defaultdict(list)
    for r in rows:
        groups[str(r[key])].append(r)
    return groups


def all_signal_metrics(rows):
    return {sig: signal_metrics(rows, sig) for sig in SIGNALS}


def cell_report(rows):
    groups = by_group(rows, "live_cell")
    return {
        cell: {
            "n": len(rr),
            "severity_counts": dict(Counter(r["severity"] for r in rr)),
            "signals": all_signal_metrics(rr),
            "origins": [r["origin"] for r in rr],
        }
        for cell, rr in sorted(groups.items())
    }


def status_report(rows):
    out = {}
    for status in ["STABLE", "TRANSITION"]:
        rr = [r for r in rows if r["v2_transition_status"] == status]
        out[status] = {
            "n": len(rr),
            "severity_counts": dict(Counter(r["severity"] for r in rr)),
            "signals": all_signal_metrics(rr),
        }
    return out


def posterior_report(rows):
    out = {}
    for bucket in ["HIGH_CONF", "MID_CONF", "BELIRSIZ"]:
        for status in ["STABLE", "TRANSITION"]:
            rr = [
                r for r in rows
                if r["posterior_bucket"] == bucket
                and r["v2_transition_status"] == status
            ]
            key = f"{bucket}_{status}"
            out[key] = {
                "n": len(rr),
                "severity_counts": dict(Counter(r["severity"] for r in rr)),
                "signals": all_signal_metrics(rr),
            }
    return out


def same_regime_comparisons(rows):
    out = {}
    for regime in ["R0", "R1", "R2"]:
        stable = [
            r for r in rows
            if r["v2_semantic_label"] == regime
            and not r["v2_transition_flag"]
        ]
        trans = [
            r for r in rows
            if r["v2_semantic_label"] == regime
            and r["v2_transition_flag"]
        ]
        out[regime] = {}
        for sig in SIGNALS:
            ms = signal_metrics(stable, sig)
            mt = signal_metrics(trans, sig)

            def diff(a, b):
                if a is None or b is None:
                    return None
                return float(b - a)

            out[regime][sig] = {
                "stable": ms,
                "transition": mt,
                "transition_minus_stable_false_call_rate": diff(
                    ms["false_call_rate"], mt["false_call_rate"]
                ),
                "transition_minus_stable_useful_call_rate": diff(
                    ms["useful_call_rate"], mt["useful_call_rate"]
                ),
                "transition_minus_stable_high_recall": diff(
                    ms["high_recall"], mt["high_recall"]
                ),
                "comparison_label": (
                    "NO_COMPARISON"
                    if ms["alarm_events"] == 0 or mt["alarm_events"] == 0
                    else "SMALL_N"
                    if ms["alarm_events"] < 3 or mt["alarm_events"] < 3
                    else "REPORTABLE"
                ),
            }
    return out


def transition_reference_context_report(rows):
    trans = [r for r in rows if r["v2_transition_flag"]]
    out = {}
    for context in ["IN_REFERENCE_ZONE", "OUTSIDE_REFERENCE_ZONE"]:
        rr = [r for r in trans if r["reference_transition_context"] == context]
        out[context] = {
            "n": len(rr),
            "severity_counts": dict(Counter(r["severity"] for r in rr)),
            "signals": all_signal_metrics(rr),
            "rows": [
                {
                    "origin": r["origin"],
                    "target": r["target"],
                    "v2_semantic_state": r["v2_semantic_state"],
                    "v2_semantic_label": r["v2_semantic_label"],
                    "v2_semantic_probability": r["v2_semantic_probability"],
                    "severity": r["severity"],
                    "ape_pct": float(r["ape_pct"]),
                    "active_signals": list(r["active_signals"]),
                    "T0_STANDARD_outcome": r["T0_STANDARD_outcome"],
                    "ANY_VISIBLE_outcome": r["ANY_VISIBLE_outcome"],
                }
                for r in rr
            ],
        }
    return out


def union_summary(rows):
    return {
        sig: {
            "overall": signal_metrics(rows, sig),
            "stable": signal_metrics(
                [r for r in rows if not r["v2_transition_flag"]], sig
            ),
            "transition": signal_metrics(
                [r for r in rows if r["v2_transition_flag"]], sig
            ),
        }
        for sig in ["T0_STANDARD", "ANY_VISIBLE"]
    }


def period_report(rows):
    return {
        "n": len(rows),
        "state_cell_counts": dict(Counter(r["live_cell"] for r in rows)),
        "transition_status_counts": dict(Counter(r["v2_transition_status"] for r in rows)),
        "severity_counts": dict(Counter(r["severity"] for r in rows)),
        "union_summary": union_summary(rows),
        "by_live_cell": cell_report(rows),
        "stable_vs_transition_by_regime": same_regime_comparisons(rows),
        "posterior_bucket_x_transition": posterior_report(rows),
        "transition_reference_context": transition_reference_context_report(rows),
    }


def primary_facts(periods):
    facts = {}
    for pname, pr in periods.items():
        facts[pname] = {}
        for sig in ["T0_STANDARD", "ANY_VISIBLE"]:
            facts[pname][sig] = {
                "stable": pr["union_summary"][sig]["stable"],
                "transition": pr["union_summary"][sig]["transition"],
            }
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alarm-audit-json", required=True)
    ap.add_argument("--transition-v2-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    alarm = load_json(args.alarm_audit_json)
    v2 = load_json(args.transition_v2_json)

    if alarm.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_ALARM_AUDIT")
    if v2.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_V2")

    rows = join_rows(alarm, v2)
    if len(rows) != len(alarm["rows"]):
        raise RuntimeError(("UNMATCHED_ALARM_ROWS", len(rows), len(alarm["rows"])))

    periods = {}
    for name, (a, b) in PERIODS.items():
        periods[name] = period_report(subset(rows, a, b))

    periods["FULL_COMMON"] = period_report(rows)

    result = {
        "schema": "GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "primary_schedule": "EXPANDING_REFIT",
        "join_contract": {
            "market_state_join_key": "forecast origin month t",
            "alarm_target": "t+1",
            "target_month_v2_state_used": False,
        },
        "signals": SIGNALS,
        "periods": periods,
        "primary_union_facts": primary_facts(periods),
        "transition_flagged_rows_full_common": [
            {
                "origin": r["origin"],
                "target": r["target"],
                "live_cell": r["live_cell"],
                "v2_semantic_probability": r["v2_semantic_probability"],
                "reference_transition_context": r["reference_transition_context"],
                "severity": r["severity"],
                "ape_pct": float(r["ape_pct"]),
                "active_signals": list(r["active_signals"]),
                "T0_STANDARD_outcome": r["T0_STANDARD_outcome"],
                "ANY_VISIBLE_outcome": r["ANY_VISIBLE_outcome"],
                "v2_directional_flags": r["v2_current_directional_flags"],
            }
            for r in rows if r["v2_transition_flag"]
        ],
        "rows": rows,
        "governance": {
            "v2_retrained_or_retuned": False,
            "alarm_thresholds_changed": False,
            "alarm_selection_performed": False,
            "alarm_weighting_performed": False,
            "forecast_correction_performed": False,
            "routing_tested": False,
            "target_month_v2_state_used": False,
            "2025_2026_used_for_tuning": False,
            "reference_transition_zone_used_for_detection": False,
            "reference_transition_zone_used_for_diagnostic_only": True,
        },
    }

    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )

    def compact_signal(m):
        return {
            k: m[k] for k in [
                "n_target_months", "high_targets", "medium_targets", "normal_targets",
                "alarm_events", "high_hits", "medium_hits", "false_calls",
                "high_recall", "false_call_rate", "useful_call_rate", "evidence_label",
            ]
        }

    summary = {
        "period_counts": {
            k: {
                "n": v["n"],
                "state_cell_counts": v["state_cell_counts"],
                "transition_status_counts": v["transition_status_counts"],
                "severity_counts": v["severity_counts"],
            }
            for k, v in periods.items()
        },
        "union_facts": {
            p: {
                sig: {
                    "stable": compact_signal(v["union_summary"][sig]["stable"]),
                    "transition": compact_signal(v["union_summary"][sig]["transition"]),
                }
                for sig in ["T0_STANDARD", "ANY_VISIBLE"]
            }
            for p, v in periods.items()
        },
        "dev_same_regime": periods["DEV_2022_04_2024_12"]["stable_vs_transition_by_regime"],
        "opened_same_regime": periods["OPENED_2025_2026"]["stable_vs_transition_by_regime"],
        "full_transition_context": periods["FULL_COMMON"]["transition_reference_context"],
        "transition_flagged_rows": result["transition_flagged_rows_full_common"],
    }

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
