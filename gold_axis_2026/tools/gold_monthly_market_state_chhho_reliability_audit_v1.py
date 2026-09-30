from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

DEV_START = "2022-04"
DEV_END = "2024-12"
T2025_START = "2025-01"
T2025_END = "2025-12"
T2026_START = "2026-01"
T2026_END = "2026-08"
TRANSPORT_START = "2025-01"
TRANSPORT_END = "2026-08"

CATEGORIES = ["NORMAL", "EXTREME", "TRANSITION", "BOTH", "DEFER"]


def load_json(path: str):
    return json.loads(Path(path).read_text())


def classify(extreme_row, transition_row):
    extreme = bool(extreme_row["extreme_flag"])
    transition = bool(transition_row["transition_flag"])
    status = str(extreme_row["extreme_status"])
    if extreme and transition:
        return "BOTH"
    if transition:
        return "TRANSITION"
    if extreme:
        return "EXTREME"
    if status == "NORMAL":
        return "NORMAL"
    if status == "DEFER":
        return "DEFER"
    raise RuntimeError(("UNKNOWN_STATE_COMBINATION", status, extreme, transition))


def direction_fields(rows):
    # origin actual price = actual price of row whose target equals current origin.
    target_actual = {r["target"]: float(r["actual"]) for r in rows}
    out = []
    for r in rows:
        z = dict(r)
        origin_actual = target_actual.get(r["origin"])
        z["origin_actual"] = origin_actual
        if origin_actual is None:
            z["predicted_direction"] = None
            z["actual_direction"] = None
            z["direction_correct"] = None
        else:
            pred_up = float(r["forecast"]) > origin_actual
            actual_up = float(r["actual"]) > origin_actual
            z["predicted_direction"] = "UP" if pred_up else "DOWN"
            z["actual_direction"] = "UP" if actual_up else "DOWN"
            z["direction_correct"] = bool(pred_up == actual_up)
        out.append(z)
    return out


def join_schedule(chhho_rows, extreme_rows, transition_rows, schedule):
    emap = {r["month"]: r for r in extreme_rows}
    tmap = {r["month"]: r for r in transition_rows}
    out = []
    for r in chhho_rows:
        origin = r["origin"]
        if origin not in emap or origin not in tmap:
            continue
        e = emap[origin]
        t = tmap[origin]
        z = dict(r)
        z["schedule"] = schedule
        z["state_category"] = classify(e, t)
        z["semantic_state"] = e["semantic_state"]
        z["semantic_label"] = e["semantic_label"]
        z["semantic_probability"] = float(e["semantic_probability"])
        z["extreme_status"] = e["extreme_status"]
        z["extreme_flag"] = bool(e["extreme_flag"])
        z["transition_v2_status"] = t["transition_status"]
        z["transition_v2_flag"] = bool(t["transition_flag"])
        z["extreme_active_signals"] = list(e["active_signals"])
        z["transition_current_flags"] = list(t.get("current_directional_flags", []))
        out.append(z)
    return direction_fields(out)


def subset(rows, start, end):
    return [r for r in rows if start <= r["target"] <= end]


def metrics(rows):
    n = len(rows)
    if n == 0:
        return {
            "n": 0,
            "sum_ae": None,
            "mae": None,
            "median_ae": None,
            "rmse": None,
            "mean_ape_pct": None,
            "median_ape_pct": None,
            "worst_ae": None,
            "severity_counts": {"HIGH": 0, "MEDIUM": 0, "NORMAL": 0},
            "high_rate": None,
            "medium_rate": None,
            "normal_rate": None,
            "direction_n": 0,
            "direction_correct": 0,
            "direction_accuracy": None,
        }

    ae = np.asarray([float(r["ae"]) for r in rows], float)
    ape = np.asarray([float(r["ape_pct"]) for r in rows], float)
    sev = Counter(r["severity"] for r in rows)
    dvals = [bool(r["direction_correct"]) for r in rows if r["direction_correct"] is not None]

    return {
        "n": n,
        "sum_ae": float(ae.sum()),
        "mae": float(ae.mean()),
        "median_ae": float(np.median(ae)),
        "rmse": float(np.sqrt(np.mean(ae ** 2))),
        "mean_ape_pct": float(ape.mean()),
        "median_ape_pct": float(np.median(ape)),
        "worst_ae": float(ae.max()),
        "severity_counts": {
            "HIGH": int(sev.get("HIGH", 0)),
            "MEDIUM": int(sev.get("MEDIUM", 0)),
            "NORMAL": int(sev.get("NORMAL", 0)),
        },
        "high_rate": float(sev.get("HIGH", 0) / n),
        "medium_rate": float(sev.get("MEDIUM", 0) / n),
        "normal_rate": float(sev.get("NORMAL", 0) / n),
        "direction_n": len(dvals),
        "direction_correct": int(sum(dvals)),
        "direction_accuracy": None if not dvals else float(np.mean(dvals)),
    }


def category_metrics(rows):
    return {cat: metrics([r for r in rows if r["state_category"] == cat]) for cat in CATEGORIES}


def safe_diff(a, b):
    return None if a is None or b is None else float(a - b)


def safe_ratio(a, b):
    return None if a is None or b is None or b == 0 else float(a / b)


def contrasts(catm):
    normal = catm["NORMAL"]
    out = {}
    for cat in ["EXTREME", "TRANSITION", "DEFER", "BOTH"]:
        m = catm[cat]
        out[f"{cat}_vs_NORMAL"] = {
            "n_state": m["n"],
            "n_normal": normal["n"],
            "mae_ratio": safe_ratio(m["mae"], normal["mae"]),
            "mean_ape_pct_difference": safe_diff(m["mean_ape_pct"], normal["mean_ape_pct"]),
            "high_rate_difference": safe_diff(m["high_rate"], normal["high_rate"]),
            "direction_accuracy_difference": safe_diff(m["direction_accuracy"], normal["direction_accuracy"]),
        }
    return out


def bootstrap_mae_diff(a, b, seed=20260930, nboot=10000):
    aa = np.asarray(a, float)
    bb = np.asarray(b, float)
    rng = np.random.default_rng(seed)
    diffs = np.empty(nboot, float)
    for i in range(nboot):
        diffs[i] = rng.choice(aa, size=len(aa), replace=True).mean() - rng.choice(bb, size=len(bb), replace=True).mean()
    lo, hi = np.quantile(diffs, [0.025, 0.975])
    return {
        "observed_mae_difference": float(aa.mean() - bb.mean()),
        "bootstrap_95pct_ci": [float(lo), float(hi)],
        "bootstrap_resamples": nboot,
        "bootstrap_seed": seed,
    }


def statistical_diagnostic(rows, cat):
    a = [float(r["ae"]) for r in rows if r["state_category"] == cat]
    b = [float(r["ae"]) for r in rows if r["state_category"] == "NORMAL"]
    if len(a) < 3 or len(b) < 3:
        return {
            "state": cat,
            "n_state": len(a),
            "n_normal": len(b),
            "available": False,
            "reason": "n<3 in state or NORMAL",
        }
    u = mannwhitneyu(a, b, alternative="two-sided", method="auto")
    boot = bootstrap_mae_diff(a, b)
    return {
        "state": cat,
        "n_state": len(a),
        "n_normal": len(b),
        "available": True,
        "mann_whitney_u": float(u.statistic),
        "mann_whitney_two_sided_p": float(u.pvalue),
        **boot,
    }


def regime_stratified(rows):
    out = {}
    for regime in ["R0", "R1", "R2"]:
        out[regime] = {}
        for cat in CATEGORIES:
            rr = [r for r in rows if r["semantic_state"] == regime and r["state_category"] == cat]
            m = metrics(rr)
            m["evidence_label"] = "SMALL_N" if 0 < m["n"] < 3 else ("NO_EVENTS" if m["n"] == 0 else "REPORTABLE")
            out[regime][cat] = m
    return out


def period_report(rows, start, end):
    rr = subset(rows, start, end)
    cm = category_metrics(rr)
    return {
        "start_target": start,
        "end_target": end,
        "n": len(rr),
        "overall": metrics(rr),
        "by_state_category": cm,
        "contrasts_vs_normal": contrasts(cm),
        "state_category_counts": dict(Counter(r["state_category"] for r in rr)),
        "regime_stratified": regime_stratified(rr),
        "rows": rr,
    }


def checkpoint(rows, origins):
    return [
        {
            "origin": r["origin"],
            "target": r["target"],
            "state_category": r["state_category"],
            "semantic_state": r["semantic_state"],
            "semantic_label": r["semantic_label"],
            "extreme_status": r["extreme_status"],
            "transition_v2_status": r["transition_v2_status"],
            "ae": float(r["ae"]),
            "ape_pct": float(r["ape_pct"]),
            "severity": r["severity"],
            "forecast": float(r["forecast"]),
            "actual": float(r["actual"]),
            "origin_actual": r["origin_actual"],
            "direction_correct": r["direction_correct"],
        }
        for r in rows if r["origin"] in origins
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chhho-audit-json", required=True)
    ap.add_argument("--extreme-v1-json", required=True)
    ap.add_argument("--transition-v2-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    ch = load_json(args.chhho_audit_json)
    ex = load_json(args.extreme_v1_json)
    tr = load_json(args.transition_v2_json)

    if ch.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_CHHHO_AUDIT")
    if ex.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_EXTREME_V1")
    if tr.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_TRANSITION_V2")

    chrows = list(ch["rows"])

    schedules = {}
    for sched in ["EXPANDING_REFIT", "ANNUAL_ANCHORED"]:
        joined = join_schedule(
            chrows,
            ex["rows"][sched],
            tr["rows"][sched],
            sched,
        )
        schedules[sched] = joined

    periods = {
        "dev_2022_04_2024_12": (DEV_START, DEV_END),
        "transport_2025": (T2025_START, T2025_END),
        "stress_2026_jan_aug": (T2026_START, T2026_END),
        "opened_2025_2026": (TRANSPORT_START, TRANSPORT_END),
    }

    reports = {}
    for pname, (a, b) in periods.items():
        reports[pname] = {
            sched: period_report(rows, a, b)
            for sched, rows in schedules.items()
        }

    # Verify required row counts.
    expected = {
        "dev_2022_04_2024_12": 33,
        "transport_2025": 12,
        "stress_2026_jan_aug": 8,
        "opened_2025_2026": 20,
    }
    for pname, n in expected.items():
        for sched in schedules:
            got = reports[pname][sched]["n"]
            if got != n:
                raise RuntimeError(("UNEXPECTED_PERIOD_N", pname, sched, got, n))

    dev_exp = reports["dev_2022_04_2024_12"]["EXPANDING_REFIT"]
    stats = {
        "EXTREME_vs_NORMAL": statistical_diagnostic(dev_exp["rows"], "EXTREME"),
        "TRANSITION_vs_NORMAL": statistical_diagnostic(dev_exp["rows"], "TRANSITION"),
    }

    # Compact decision-neutral interpretation facts.
    ext = dev_exp["by_state_category"]["EXTREME"]
    nor = dev_exp["by_state_category"]["NORMAL"]
    tra = dev_exp["by_state_category"]["TRANSITION"]

    result = {
        "schema": "GOLD_MONTHLY_MARKET_STATE_CHHHO_RELIABILITY_AUDIT_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "join_contract": {
            "market_state_join_key": "origin month t",
            "forecast_target": "t+1",
            "target_month_state_used": False,
        },
        "primary_schedule": "EXPANDING_REFIT",
        "periods": reports,
        "dev_primary_statistics": stats,
        "dev_primary_key_facts": {
            "normal_n": nor["n"],
            "normal_mae": nor["mae"],
            "normal_high_rate": nor["high_rate"],
            "extreme_n": ext["n"],
            "extreme_mae": ext["mae"],
            "extreme_high_rate": ext["high_rate"],
            "extreme_vs_normal_mae_ratio": safe_ratio(ext["mae"], nor["mae"]),
            "extreme_vs_normal_high_rate_difference": safe_diff(ext["high_rate"], nor["high_rate"]),
            "transition_n": tra["n"],
            "transition_mae": tra["mae"],
            "transition_high_rate": tra["high_rate"],
            "transition_vs_normal_mae_ratio": safe_ratio(tra["mae"], nor["mae"]),
            "transition_vs_normal_high_rate_difference": safe_diff(tra["high_rate"], nor["high_rate"]),
        },
        "critical_2026_origin_to_target": {
            sched: checkpoint(rows, [
                "2025-12", "2026-01", "2026-02", "2026-03",
                "2026-04", "2026-05", "2026-06", "2026-07",
            ])
            for sched, rows in schedules.items()
        },
        "governance": {
            "upstream_thresholds_changed": False,
            "extreme_retrained": False,
            "transition_retrained": False,
            "forecast_modified": False,
            "alarm_definitions_changed": False,
            "alarm_selection_performed": False,
            "alarm_weighting_performed": False,
            "routing_tested": False,
            "target_month_state_used": False,
            "2025_2026_used_for_tuning": False,
            "statistical_tests_are_diagnostic_only": True,
        },
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    def compact_report(pr):
        return {
            "n": pr["n"],
            "overall": pr["overall"],
            "by_state_category": pr["by_state_category"],
            "contrasts_vs_normal": pr["contrasts_vs_normal"],
            "state_category_counts": pr["state_category_counts"],
        }

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "dev_primary_key_facts": result["dev_primary_key_facts"],
        "dev_primary_statistics": stats,
        "dev_expanding": compact_report(reports["dev_2022_04_2024_12"]["EXPANDING_REFIT"]),
        "transport_2025_expanding": compact_report(reports["transport_2025"]["EXPANDING_REFIT"]),
        "stress_2026_expanding": compact_report(reports["stress_2026_jan_aug"]["EXPANDING_REFIT"]),
        "opened_2025_2026_expanding": compact_report(reports["opened_2025_2026"]["EXPANDING_REFIT"]),
        "critical_2026": result["critical_2026_origin_to_target"]["EXPANDING_REFIT"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
