from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from scipy.stats import beta as beta_dist
from scipy.stats import binom

from regime_v1_data import load_external, load_governed
from regime_v1_experts import build_common
from regime_v1_router_sqrt import ALPHA, DELTA, router_year, sqrt_rows

IDENTITY = "REGIME_GATED_SELECTIVE_DAMPENER_V1_RESEARCH"
OUT = Path("regime_dampener_out")

EXPECTED = {
    2020: {"alarms": 212, "router_up": 185, "overlap": 140, "good": 80, "bad": 60},
    2021: {"alarms": 28,  "router_up": 33,  "overlap": 2,   "good": 1,  "bad": 1},
    2022: {"alarms": 11,  "router_up": 22,  "overlap": 0,   "good": 0,  "bad": 0},
    2023: {"alarms": 2,   "router_up": 19,  "overlap": 0,   "good": 0,  "bad": 0},
    2024: {"alarms": 17,  "router_up": 42,  "overlap": 4,   "good": 3,  "bad": 1},
}
EXPECTED_COMMON = {
    "external": {2019: 260, 2020: 260, 2021: 258},
    "governed": {2021: 91, 2022: 205, 2023: 203, 2024: 205},
}
EXPECTED_LEGACY_UP = {
    2023: {"FAST_UP": 106, "SLOW_UP": 79, "MONTHLY_UP": 133},
    2024: {"FAST_UP": 124, "SLOW_UP": 111, "MONTHLY_UP": 205},
}


def yearly_metrics(rows: list[dict]) -> dict:
    alarms = len(rows)
    down = sum(1 for r in rows if r["actual_direction"] == "DOWN")
    up = alarms - down
    suppress = sum(1 for r in rows if r["action"] == "SUPPRESS_DOWN")
    watch = sum(1 for r in rows if r["action"] == "DOWN_WATCH")
    retain = alarms - suppress - watch
    good = sum(
        1 for r in rows
        if r["action"] == "SUPPRESS_DOWN" and r["actual_direction"] == "UP"
    )
    bad = sum(
        1 for r in rows
        if r["action"] == "SUPPRESS_DOWN" and r["actual_direction"] == "DOWN"
    )
    remain = alarms - suppress
    rem_down = down - bad
    return {
        "alarms": alarms,
        "actual_down": down,
        "actual_up": up,
        "retain": retain,
        "watch": watch,
        "suppress": suppress,
        "good_suppressions": good,
        "bad_suppressions": bad,
        "suppression_precision": good/suppress if suppress else None,
        "false_alarm_reduction": good/up if up else None,
        "true_down_retention": rem_down/down if down else None,
        "baseline_forced_down_precision": down/alarms if alarms else None,
        "remaining_forced_down_precision": rem_down/remain if remain else None,
        "precision_gain_pp": (
            ((rem_down/remain)-(down/alarms))*100
            if remain and alarms else None
        ),
        "extreme_alarm_count": sum(
            1 for r in rows if r["risk_regime"] == "EXTREME"
        ),
        "high_non_extreme_alarm_count": sum(
            1 for r in rows if r["risk_regime"] == "HIGH_NON_EXTREME"
        ),
        "router_up_extreme": sum(
            1 for r in rows
            if r["risk_regime"] == "EXTREME" and r["router_up"]
        ),
        "router_up_high_non_extreme": sum(
            1 for r in rows
            if r["risk_regime"] == "HIGH_NON_EXTREME" and r["router_up"]
        ),
    }


def write_ledger(path: Path, rows: list[dict]) -> None:
    fields = [
        "source_class","origin_date","target_date","evaluation_year",
        "formation_n","sqrt_forecast","q80","q90",
        "sqrt_normalized_risk_score","risk_regime",
        "actual_direction","router_up","selected_expert",
        "FAST_UP","SLOW_UP","MONTHLY_UP","legacy_bucket","action",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ext = load_external()
    gov = load_governed()
    ext_common = build_common(ext)
    gov_common = build_common(gov)

    diagnostics = {
        "external_rows": len(ext),
        "governed_rows": len(gov),
        "common_counts": {
            "external": {
                str(y): sum(
                    date.fromisoformat(r["target_date"]).year == y
                    for r in ext_common
                )
                for y in (2019,2020,2021)
            },
            "governed": {
                str(y): sum(
                    date.fromisoformat(r["target_date"]).year == y
                    for r in gov_common
                )
                for y in (2021,2022,2023,2024)
            },
        },
        "legacy_up_counts_governed": {},
    }
    for y in (2023,2024):
        rr = [
            r for r in gov_common
            if date.fromisoformat(r["target_date"]).year == y
        ]
        diagnostics["legacy_up_counts_governed"][str(y)] = {
            "FAST_UP": sum(r["FAST_UP"] for r in rr),
            "SLOW_UP": sum(r["SLOW_UP"] for r in rr),
            "MONTHLY_UP": sum(r["MONTHLY_UP"] for r in rr),
        }

    routers = {}
    parents = {}
    for y in (2020,2021):
        routers[y] = router_year(ext_common, y)
        parents[y] = sqrt_rows(ext, y)
    for y in (2022,2023,2024):
        routers[y] = router_year(gov_common, y)
        parents[y] = sqrt_rows(gov, y)

    integrity_errors = []
    for source_name, expected in EXPECTED_COMMON.items():
        got = diagnostics["common_counts"][source_name]
        for y,n in expected.items():
            if int(got[str(y)]) != n:
                integrity_errors.append(
                    f"COMMON_{source_name}_{y}:{got[str(y)]}!={n}"
                )
    for y,expected in EXPECTED_LEGACY_UP.items():
        got = diagnostics["legacy_up_counts_governed"][str(y)]
        for k,n in expected.items():
            if int(got[k]) != n:
                integrity_errors.append(f"LEGACY_{y}_{k}:{got[k]}!={n}")

    ledger = []
    observed = {}
    for y in (2020,2021,2022,2023,2024):
        rmap = {r["target_date"]:r for r in routers[y]}
        alarms = [r for r in parents[y] if r["sqrt_alarm"]]
        overlap = good = bad = 0

        for s in alarms:
            rr = rmap.get(s["target_date"])
            router_up = 0 if rr is None else int(rr["router_up"])
            actual_direction = "DOWN" if s["target_return"] < 0 else "UP"

            if router_up:
                overlap += 1
                if actual_direction == "UP":
                    good += 1
                else:
                    bad += 1

            if not router_up:
                action = "RETAIN_DOWN"
            elif s["risk_regime"] == "EXTREME":
                action = "DOWN_WATCH"
            else:
                action = "SUPPRESS_DOWN"

            ledger.append({
                "source_class": (
                    "EXTERNAL_RESEARCH_V2" if y <= 2021 else "GOVERNED"
                ),
                **s,
                "actual_direction": actual_direction,
                "router_up": router_up,
                "selected_expert": "" if rr is None else rr["selected_expert"],
                "FAST_UP": "" if rr is None else rr["FAST_UP"],
                "SLOW_UP": "" if rr is None else rr["SLOW_UP"],
                "MONTHLY_UP": "" if rr is None else rr["MONTHLY_UP"],
                "legacy_bucket": "" if rr is None else rr["legacy_bucket"],
                "action": action,
            })

        observed[y] = {
            "alarms": len(alarms),
            "router_up": sum(r["router_up"] for r in routers[y]),
            "overlap": overlap,
            "good": good,
            "bad": bad,
        }
        for k,v in EXPECTED[y].items():
            if observed[y][k] != v:
                integrity_errors.append(
                    f"FROZEN_{y}_{k}:{observed[y][k]}!={v}"
                )

    write_ledger(
        OUT/"GOLD_CONTROL_REGIME_GATED_SELECTIVE_DAMPENER_V1_LEDGER_2026-09-22.csv",
        ledger,
    )

    by_year = {
        str(y): yearly_metrics([
            r for r in ledger if int(r["evaluation_year"]) == y
        ])
        for y in (2020,2021,2022,2023,2024)
    }
    pooled = yearly_metrics(ledger)
    n_down = pooled["actual_down"]
    x_bad = pooled["bad_suppressions"]
    pval = float(binom.cdf(x_bad, n_down, ALPHA)) if n_down else 1.0
    cp_upper = (
        1.0 if x_bad >= n_down
        else float(beta_dist.ppf(1-DELTA, x_bad+1, n_down-x_bad))
    )
    pooled.update({
        "exact_ltt_alpha": ALPHA,
        "exact_ltt_delta": DELTA,
        "exact_lower_tail_p_value": pval,
        "exact_90pct_cp_upper_bad_suppression_rate": cp_upper,
        "retrospective_safety_diagnostic_pass": bool(pval <= DELTA),
    })

    if integrity_errors:
        status = "BLOCKED_INTEGRITY_MISMATCH"
    elif pooled["retrospective_safety_diagnostic_pass"] and pooled["good_suppressions"] > 0:
        status = "RETROSPECTIVELY_PROMISING_NOT_CERTIFIED"
    elif pooled["bad_suppressions"]/pooled["actual_down"] > ALPHA:
        status = "REJECTED_SAFETY"
    else:
        status = "SAFE_BUT_NONUSEFUL"

    result = {
        "identity": IDENTITY,
        "date": "2026-09-22",
        "preregistered_policy": (
            "SUPPRESS only when SQRT alarm is in formation Q80-Q90 band "
            "and frozen Router V2=UP; Router-UP at or above formation Q90 "
            "is WATCH and keeps the DOWN alarm."
        ),
        "governance": {
            "random_split": False,
            "2025_used": False,
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
            "external_2020_2021_authority": "RESEARCH_ONLY_SESSIONMASK_V2",
        },
        "diagnostics": diagnostics,
        "frozen_reproduction": {str(k):v for k,v in observed.items()},
        "integrity_errors": integrity_errors,
        "by_year": by_year,
        "pooled_2020_2024": pooled,
        "status": status,
        "interpretation_limit": (
            "Retrospective hypothesis stress only. The broad hard-veto "
            "failure and 2020 crisis behavior were already researcher-visible."
        ),
    }
    with (
        OUT/"GOLD_CONTROL_REGIME_GATED_SELECTIVE_DAMPENER_V1_RESULT_2026-09-22.json"
    ).open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lines = [
        "# GOLD CONTROL — REGIME-GATED SELECTIVE DAMPENER V1 RESULT",
        "",
        f"Status: {status}",
        "",
        "## Integrity",
        "",
        f"- Errors: {integrity_errors if integrity_errors else 'none'}",
        f"- Frozen reproduction: {observed}",
        "",
        "## Year-by-year",
        "",
        "| Year | alarms | suppress | watch | good | bad | FA reduction | DOWN retention | remaining precision |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for y in (2020,2021,2022,2023,2024):
        m = by_year[str(y)]
        lines.append(
            f"| {y} | {m['alarms']} | {m['suppress']} | {m['watch']} | "
            f"{m['good_suppressions']} | {m['bad_suppressions']} | "
            f"{m['false_alarm_reduction']} | {m['true_down_retention']} | "
            f"{m['remaining_forced_down_precision']} |"
        )
    lines += [
        "",
        "## Pooled 2020–2024",
        "",
        f"- Alarms: {pooled['alarms']}",
        f"- SUPPRESS: {pooled['suppress']}; WATCH: {pooled['watch']}; RETAIN: {pooled['retain']}",
        f"- Good suppressions: {pooled['good_suppressions']}; bad suppressions: {pooled['bad_suppressions']}",
        f"- Suppression precision: {pooled['suppression_precision']}",
        f"- False-alarm reduction: {pooled['false_alarm_reduction']}",
        f"- True-DOWN retention: {pooled['true_down_retention']}",
        f"- Remaining forced-DOWN precision: {pooled['remaining_forced_down_precision']}",
        f"- Precision gain pp: {pooled['precision_gain_pp']}",
        f"- Exact alpha/delta: {ALPHA}/{DELTA}; p={pval}",
        f"- Exact 90% upper bad-suppression bound: {cp_upper}",
        "",
        "Retrospective hypothesis stress only; not prospective certification.",
    ]
    (
        OUT/"GOLD_CONTROL_REGIME_GATED_SELECTIVE_DAMPENER_V1_RESULT_2026-09-22.md"
    ).write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(status)
    print(json.dumps({
        "integrity_errors": integrity_errors,
        "frozen_reproduction": observed,
        "pooled": pooled,
    }, indent=2))


if __name__ == "__main__":
    main()
