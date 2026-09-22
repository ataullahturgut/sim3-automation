from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

from scipy.stats import beta as beta_dist
from scipy.stats import binom

from regime_v1_data import Daily, load_external, load_governed
from regime_v1_experts import build_common
from regime_v1_router_sqrt import ALPHA, DELTA, router_year, sqrt_rows

IDENTITY = "PERSISTENT_RISK_STATE_DAMPENER_V1_RESEARCH"
OUT = Path("persistent_regime_out")
LOOKBACK = 20
P0 = 0.20
ANOMALY_LEVEL = 0.01
K_PERSISTENT = 9

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


def state_for_origin(days: list[Daily], row: dict) -> dict:
    idx_by_date = {x.d.isoformat(): i for i, x in enumerate(days)}
    od = row["origin_date"]
    if od not in idx_by_date:
        raise RuntimeError(f"ORIGIN_NOT_IN_DAILY:{od}")
    i = idx_by_date[od]
    start = max(0, i - LOOKBACK + 1)
    hist = days[start:i + 1]
    n = len(hist)
    q80 = float(row["q80"])
    high_count = sum(int(x.dr >= q80) for x in hist)
    if n < LOOKBACK:
        state = "INSUFFICIENT_HISTORY"
    elif high_count >= K_PERSISTENT:
        state = "PERSISTENT_HIGH"
    else:
        state = "NON_PERSISTENT"
    return {
        "persistent_state": state,
        "recent20_n": n,
        "recent20_high_count": high_count,
    }


def policy_metrics(rows: list[dict]) -> dict:
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
    hist = Counter(int(r["recent20_high_count"]) for r in rows)
    return {
        "alarms": alarms,
        "actual_down": down,
        "actual_up": up,
        "retain": retain,
        "watch": watch,
        "suppress": suppress,
        "good_suppressions": good,
        "bad_suppressions": bad,
        "bad_suppression_rate": bad/down if down else None,
        "suppression_precision": good/suppress if suppress else None,
        "false_alarm_reduction": good/up if up else None,
        "true_down_retention": rem_down/down if down else None,
        "baseline_forced_down_precision": down/alarms if alarms else None,
        "remaining_forced_down_precision": rem_down/remain if remain else None,
        "precision_gain_pp": (
            ((rem_down/remain) - (down/alarms))*100
            if remain and alarms else None
        ),
        "persistent_alarm_count": sum(
            1 for r in rows if r["persistent_state"] == "PERSISTENT_HIGH"
        ),
        "nonpersistent_alarm_count": sum(
            1 for r in rows if r["persistent_state"] == "NON_PERSISTENT"
        ),
        "insufficient_history_alarm_count": sum(
            1 for r in rows if r["persistent_state"] == "INSUFFICIENT_HISTORY"
        ),
        "router_up_persistent": sum(
            1 for r in rows
            if r["persistent_state"] == "PERSISTENT_HIGH" and r["router_up"]
        ),
        "router_up_nonpersistent": sum(
            1 for r in rows
            if r["persistent_state"] == "NON_PERSISTENT" and r["router_up"]
        ),
        "router_up_insufficient": sum(
            1 for r in rows
            if r["persistent_state"] == "INSUFFICIENT_HISTORY" and r["router_up"]
        ),
        "recent20_high_count_histogram": {str(k): hist[k] for k in sorted(hist)},
    }


def with_actions(rows: list[dict], mode: str) -> list[dict]:
    out = []
    for r in rows:
        rr = dict(r)
        if mode == "NEW":
            if not rr["router_up"]:
                action = "RETAIN_DOWN"
            elif rr["persistent_state"] in ("PERSISTENT_HIGH", "INSUFFICIENT_HISTORY"):
                action = "DOWN_WATCH"
            else:
                action = "SUPPRESS_DOWN"
        elif mode == "UNIVERSAL_ROUTER_VETO":
            action = "SUPPRESS_DOWN" if rr["router_up"] else "RETAIN_DOWN"
        elif mode == "Q90_GATE":
            if not rr["router_up"]:
                action = "RETAIN_DOWN"
            elif rr["risk_regime"] == "EXTREME":
                action = "DOWN_WATCH"
            else:
                action = "SUPPRESS_DOWN"
        elif mode == "NO_SUPPRESSION":
            action = "RETAIN_DOWN"
        else:
            raise RuntimeError(f"UNKNOWN_MODE:{mode}")
        rr["action"] = action
        out.append(rr)
    return out


def write_ledger(path: Path, rows: list[dict]) -> None:
    fields = [
        "source_class", "origin_date", "target_date", "evaluation_year",
        "formation_n", "sqrt_forecast", "q80", "q90",
        "sqrt_normalized_risk_score", "risk_regime",
        "recent20_n", "recent20_high_count", "persistent_state",
        "actual_direction", "router_up", "selected_expert",
        "FAST_UP", "SLOW_UP", "MONTHLY_UP", "legacy_bucket", "action",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def safety_diagnostic(metrics: dict) -> dict:
    n_down = int(metrics["actual_down"])
    x_bad = int(metrics["bad_suppressions"])
    pval = float(binom.cdf(x_bad, n_down, ALPHA)) if n_down else 1.0
    cp_upper = (
        1.0 if x_bad >= n_down
        else float(beta_dist.ppf(1 - DELTA, x_bad + 1, n_down - x_bad))
    )
    return {
        "exact_ltt_alpha": ALPHA,
        "exact_ltt_delta": DELTA,
        "exact_lower_tail_p_value": pval,
        "exact_90pct_cp_upper_bad_suppression_rate": cp_upper,
        "retrospective_safety_diagnostic_pass": bool(pval <= DELTA),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ext = load_external()
    gov = load_governed()
    ext_common = build_common(ext)
    gov_common = build_common(gov)

    analytic_tail = float(binom.sf(K_PERSISTENT - 1, LOOKBACK, P0))
    previous_tail = float(binom.sf(K_PERSISTENT - 2, LOOKBACK, P0))
    threshold_integrity = (
        analytic_tail <= ANOMALY_LEVEL and previous_tail > ANOMALY_LEVEL
    )

    diagnostics = {
        "external_rows": len(ext),
        "governed_rows": len(gov),
        "persistent_state_definition": {
            "lookback": LOOKBACK,
            "nominal_q80_exceedance_probability": P0,
            "anomaly_level": ANOMALY_LEVEL,
            "k_persistent": K_PERSISTENT,
            "tail_at_k": analytic_tail,
            "tail_at_k_minus_1": previous_tail,
            "k_is_minimal_at_level": threshold_integrity,
            "window_includes_completed_origin_day": True,
            "current_target_used": False,
        },
        "common_counts": {
            "external": {
                str(y): sum(
                    date.fromisoformat(r["target_date"]).year == y
                    for r in ext_common
                )
                for y in (2019, 2020, 2021)
            },
            "governed": {
                str(y): sum(
                    date.fromisoformat(r["target_date"]).year == y
                    for r in gov_common
                )
                for y in (2021, 2022, 2023, 2024)
            },
        },
        "legacy_up_counts_governed": {},
    }
    for y in (2023, 2024):
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
    daily_source = {}
    for y in (2020, 2021):
        routers[y] = router_year(ext_common, y)
        parents[y] = sqrt_rows(ext, y)
        daily_source[y] = ext
    for y in (2022, 2023, 2024):
        routers[y] = router_year(gov_common, y)
        parents[y] = sqrt_rows(gov, y)
        daily_source[y] = gov

    integrity_errors = []
    if not threshold_integrity:
        integrity_errors.append(
            f"K_NOT_MINIMAL:{K_PERSISTENT}:tail={analytic_tail}:prev={previous_tail}"
        )

    for source_name, expected in EXPECTED_COMMON.items():
        got = diagnostics["common_counts"][source_name]
        for y, n in expected.items():
            if int(got[str(y)]) != n:
                integrity_errors.append(
                    f"COMMON_{source_name}_{y}:{got[str(y)]}!={n}"
                )
    for y, expected in EXPECTED_LEGACY_UP.items():
        got = diagnostics["legacy_up_counts_governed"][str(y)]
        for k, n in expected.items():
            if int(got[k]) != n:
                integrity_errors.append(f"LEGACY_{y}_{k}:{got[k]}!={n}")

    raw_ledger = []
    observed = {}
    for y in (2020, 2021, 2022, 2023, 2024):
        rmap = {r["target_date"]: r for r in routers[y]}
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

            state = state_for_origin(daily_source[y], s)
            raw_ledger.append({
                "source_class": (
                    "EXTERNAL_RESEARCH_V2" if y <= 2021 else "GOVERNED"
                ),
                **s,
                **state,
                "actual_direction": actual_direction,
                "router_up": router_up,
                "selected_expert": "" if rr is None else rr["selected_expert"],
                "FAST_UP": "" if rr is None else rr["FAST_UP"],
                "SLOW_UP": "" if rr is None else rr["SLOW_UP"],
                "MONTHLY_UP": "" if rr is None else rr["MONTHLY_UP"],
                "legacy_bucket": "" if rr is None else rr["legacy_bucket"],
            })

        observed[y] = {
            "alarms": len(alarms),
            "router_up": sum(r["router_up"] for r in routers[y]),
            "overlap": overlap,
            "good": good,
            "bad": bad,
        }
        for k, v in EXPECTED[y].items():
            if observed[y][k] != v:
                integrity_errors.append(
                    f"FROZEN_{y}_{k}:{observed[y][k]}!={v}"
                )

    new_ledger = with_actions(raw_ledger, "NEW")
    universal_ledger = with_actions(raw_ledger, "UNIVERSAL_ROUTER_VETO")
    q90_ledger = with_actions(raw_ledger, "Q90_GATE")
    baseline_ledger = with_actions(raw_ledger, "NO_SUPPRESSION")

    write_ledger(
        OUT / "GOLD_CONTROL_PERSISTENT_RISK_STATE_DAMPENER_V1_LEDGER_2026-09-22.csv",
        new_ledger,
    )

    by_year = {
        str(y): policy_metrics([
            r for r in new_ledger if int(r["evaluation_year"]) == y
        ])
        for y in (2020, 2021, 2022, 2023, 2024)
    }
    pooled = policy_metrics(new_ledger)
    pooled.update(safety_diagnostic(pooled))

    comparators = {
        "no_suppression_parent": policy_metrics(baseline_ledger),
        "universal_router_veto_rejected": policy_metrics(universal_ledger),
        "q80_q90_instantaneous_gate_rejected": policy_metrics(q90_ledger),
    }
    comparators["universal_router_veto_rejected"].update(
        safety_diagnostic(comparators["universal_router_veto_rejected"])
    )
    comparators["q80_q90_instantaneous_gate_rejected"].update(
        safety_diagnostic(comparators["q80_q90_instantaneous_gate_rejected"])
    )

    if integrity_errors:
        status = "BLOCKED_INTEGRITY_MISMATCH"
    elif not pooled["retrospective_safety_diagnostic_pass"]:
        status = "REJECTED_SAFETY"
    elif pooled["good_suppressions"] <= 0:
        status = "SAFE_BUT_NONUSEFUL"
    else:
        status = "RETROSPECTIVELY_PROMISING_NOT_CERTIFIED"

    result = {
        "identity": IDENTITY,
        "date": "2026-09-22",
        "preregistered_policy": (
            "On an existing SQRT alarm, frozen Router V2 UP may suppress only "
            "when the latest 20 completed origin-day DR observations contain "
            "fewer than 9 Q80 exceedances. At >=9 exceedances Router-UP becomes "
            "DOWN_WATCH and the parent DOWN alarm is retained."
        ),
        "governance": {
            "random_split": False,
            "2025_used": False,
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
            "external_2020_2021_authority": "RESEARCH_ONLY_SESSIONMASK_V2",
            "retrospective_hypothesis_stress": True,
        },
        "diagnostics": diagnostics,
        "frozen_reproduction": {str(k): v for k, v in observed.items()},
        "integrity_errors": integrity_errors,
        "by_year": by_year,
        "pooled_2020_2024": pooled,
        "comparators": comparators,
        "status": status,
        "interpretation_limit": (
            "Retrospective hypothesis stress only. The 2020 failure and prior "
            "controller failures were already researcher-visible; a pass is "
            "not prospective certification."
        ),
    }
    with (
        OUT / "GOLD_CONTROL_PERSISTENT_RISK_STATE_DAMPENER_V1_RESULT_2026-09-22.json"
    ).open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lines = [
        "# GOLD CONTROL — PERSISTENT RISK-STATE DAMPENER V1 RESULT",
        "",
        f"Status: {status}",
        "",
        "## Frozen state definition",
        "",
        f"- Lookback: {LOOKBACK} completed trading days ending at origin",
        f"- Q80 exceedance count cutoff: >= {K_PERSISTENT}",
        f"- Binomial(20,0.20) tail at K=9: {analytic_tail}",
        f"- K minimal at 0.01 level: {threshold_integrity}",
        "",
        "## Integrity",
        "",
        f"- Errors: {integrity_errors if integrity_errors else 'none'}",
        f"- Frozen reproduction: {observed}",
        "",
        "## Year-by-year",
        "",
        "| Year | alarms | persistent | suppress | watch | good | bad | FA reduction | DOWN retention | remaining precision |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for y in (2020, 2021, 2022, 2023, 2024):
        m = by_year[str(y)]
        lines.append(
            f"| {y} | {m['alarms']} | {m['persistent_alarm_count']} | "
            f"{m['suppress']} | {m['watch']} | "
            f"{m['good_suppressions']} | {m['bad_suppressions']} | "
            f"{m['false_alarm_reduction']} | {m['true_down_retention']} | "
            f"{m['remaining_forced_down_precision']} |"
        )

    lines += [
        "",
        "## Pooled 2020–2024",
        "",
        f"- Alarms: {pooled['alarms']}",
        f"- Persistent alarms: {pooled['persistent_alarm_count']}; non-persistent: {pooled['nonpersistent_alarm_count']}",
        f"- SUPPRESS: {pooled['suppress']}; WATCH: {pooled['watch']}; RETAIN: {pooled['retain']}",
        f"- Good suppressions: {pooled['good_suppressions']}; bad suppressions: {pooled['bad_suppressions']}",
        f"- Bad-suppression rate among actual DOWN alarms: {pooled['bad_suppression_rate']}",
        f"- Suppression precision: {pooled['suppression_precision']}",
        f"- False-alarm reduction: {pooled['false_alarm_reduction']}",
        f"- True-DOWN retention: {pooled['true_down_retention']}",
        f"- Remaining forced-DOWN precision: {pooled['remaining_forced_down_precision']}",
        f"- Precision gain pp: {pooled['precision_gain_pp']}",
        f"- Exact alpha/delta: {ALPHA}/{DELTA}; p={pooled['exact_lower_tail_p_value']}",
        f"- Exact 90% upper bad-suppression bound: {pooled['exact_90pct_cp_upper_bad_suppression_rate']}",
        "",
        "## Frozen comparators",
        "",
        f"- Universal Router veto: {comparators['universal_router_veto_rejected']}",
        f"- Q80-Q90 instantaneous gate: {comparators['q80_q90_instantaneous_gate_rejected']}",
        "",
        "Retrospective hypothesis stress only; not prospective certification.",
    ]
    (
        OUT / "GOLD_CONTROL_PERSISTENT_RISK_STATE_DAMPENER_V1_RESULT_2026-09-22.md"
    ).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(status)
    print(json.dumps({
        "integrity_errors": integrity_errors,
        "frozen_reproduction": observed,
        "state_definition": diagnostics["persistent_state_definition"],
        "pooled": pooled,
        "comparators": comparators,
    }, indent=2))


if __name__ == "__main__":
    main()
