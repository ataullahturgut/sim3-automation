from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from regime_v1_data import load_external, load_governed
from regime_v1_experts import build_common
from regime_v1_router_sqrt import (
    ALPHA, DELTA, router_year, sqrt_rows, wilson_lcb,
)
from persistent_regime_v1_run import (
    EXPECTED, EXPECTED_COMMON, EXPECTED_LEGACY_UP,
    state_for_origin, policy_metrics, with_actions, safety_diagnostic,
)

IDENTITY = "PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_RESEARCH"
OUT = Path("conditional_competence_out")
MIN_CELL_N = 30
LCB_THRESHOLD = 0.50
Z90 = 1.2815515655446004

EXPECTED_REFERENCE = {
    "alarms": 270,
    "suppress": 8,
    "good_suppressions": 6,
    "bad_suppressions": 2,
}


def build_raw_ledger() -> tuple[list[dict], dict, dict]:
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
        "competence_rule": {
            "cell": ["selected_expert", "legacy_bucket"],
            "persistent_state_only": True,
            "matured_target_required": True,
            "min_cell_n": MIN_CELL_N,
            "wilson_one_sided_confidence": 0.90,
            "wilson_z": Z90,
            "lcb_threshold": LCB_THRESHOLD,
            "global_fallback": False,
            "neighbor_pooling": False,
        },
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
                integrity_errors.append(
                    f"LEGACY_{y}_{k}:{got[k]}!={n}"
                )

    raw = []
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
            raw.append({
                "source_class": (
                    "EXTERNAL_RESEARCH_V2" if y <= 2021 else "GOVERNED"
                ),
                **s,
                **state,
                "actual_direction": actual_direction,
                "router_up": router_up,
                "selected_expert": "" if rr is None else rr["selected_expert"],
                "selected_lcb_router": "" if rr is None else rr["selected_lcb"],
                "selected_precision_router": "" if rr is None else rr["selected_precision"],
                "selected_fpr_router": "" if rr is None else rr["selected_fpr"],
                "selected_history_source_router": "" if rr is None else rr["selected_history_source"],
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

    raw.sort(key=lambda r: (r["origin_date"], r["target_date"]))
    return raw, diagnostics, {
        "observed": observed,
        "integrity_errors": integrity_errors,
    }


def apply_conditional_controller(raw: list[dict]) -> list[dict]:
    out = []

    for i, r in enumerate(raw):
        rr = dict(r)
        competence_n = 0
        competence_tp = 0
        competence_precision = None
        competence_lcb = None
        competence_authorized = False

        if rr["router_up"] and rr["persistent_state"] == "PERSISTENT_HIGH":
            current_origin = date.fromisoformat(rr["origin_date"])
            hist = []
            for h in raw[:i]:
                if not h["router_up"]:
                    continue
                if h["persistent_state"] != "PERSISTENT_HIGH":
                    continue
                if h["selected_expert"] != rr["selected_expert"]:
                    continue
                if h["legacy_bucket"] != rr["legacy_bucket"]:
                    continue
                if date.fromisoformat(h["target_date"]) > current_origin:
                    continue
                hist.append(h)

            competence_n = len(hist)
            competence_tp = sum(
                1 for h in hist if h["actual_direction"] == "UP"
            )
            if competence_n:
                competence_precision = competence_tp / competence_n
                competence_lcb = wilson_lcb(competence_tp, competence_n)

            competence_authorized = bool(
                competence_n >= MIN_CELL_N
                and competence_lcb is not None
                and competence_lcb > LCB_THRESHOLD
            )

        if not rr["router_up"]:
            action = "RETAIN_DOWN"
            action_reason = "ROUTER_ABSTAIN"
        elif rr["persistent_state"] == "NON_PERSISTENT":
            action = "SUPPRESS_DOWN"
            action_reason = "NON_PERSISTENT_REFERENCE_AUTHORITY"
        elif rr["persistent_state"] == "INSUFFICIENT_HISTORY":
            action = "DOWN_WATCH"
            action_reason = "PERSISTENCE_HISTORY_INSUFFICIENT"
        elif competence_authorized:
            action = "SUPPRESS_DOWN"
            action_reason = "PERSISTENT_CELL_COMPETENCE_AUTHORIZED"
        else:
            action = "DOWN_WATCH"
            action_reason = "PERSISTENT_CELL_NOT_AUTHORIZED"

        rr.update({
            "competence_n": competence_n,
            "competence_tp": competence_tp,
            "competence_precision": competence_precision,
            "competence_lcb90": competence_lcb,
            "competence_authorized": int(competence_authorized),
            "action_reason": action_reason,
            "action": action,
        })
        out.append(rr)

    return out


def write_ledger(path: Path, rows: list[dict]) -> None:
    fields = [
        "source_class", "origin_date", "target_date", "evaluation_year",
        "formation_n", "sqrt_forecast", "q80", "q90",
        "sqrt_normalized_risk_score", "risk_regime",
        "recent20_n", "recent20_high_count", "persistent_state",
        "actual_direction", "router_up", "selected_expert",
        "legacy_bucket", "selected_lcb_router", "selected_precision_router",
        "selected_fpr_router", "selected_history_source_router",
        "competence_n", "competence_tp", "competence_precision",
        "competence_lcb90", "competence_authorized",
        "FAST_UP", "SLOW_UP", "MONTHLY_UP",
        "action_reason", "action",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def competence_summary(rows: list[dict]) -> dict:
    cells = defaultdict(lambda: {
        "persistent_router_up": 0,
        "actual_up": 0,
        "actual_down": 0,
        "authorized_decisions": 0,
        "authorized_good": 0,
        "authorized_bad": 0,
        "max_matured_n_seen": 0,
        "max_lcb_seen": None,
    })

    for r in rows:
        if not (r["router_up"] and r["persistent_state"] == "PERSISTENT_HIGH"):
            continue
        key = f"{r['selected_expert']}|{r['legacy_bucket']}"
        c = cells[key]
        c["persistent_router_up"] += 1
        if r["actual_direction"] == "UP":
            c["actual_up"] += 1
        else:
            c["actual_down"] += 1
        c["max_matured_n_seen"] = max(
            c["max_matured_n_seen"], int(r["competence_n"])
        )
        if r["competence_lcb90"] is not None:
            v = float(r["competence_lcb90"])
            c["max_lcb_seen"] = (
                v if c["max_lcb_seen"] is None else max(c["max_lcb_seen"], v)
            )
        if r["competence_authorized"]:
            c["authorized_decisions"] += 1
            if r["actual_direction"] == "UP":
                c["authorized_good"] += 1
            else:
                c["authorized_bad"] += 1

    return dict(cells)


def delta_vs_reference(new_rows: list[dict], ref_rows: list[dict]) -> dict:
    ref = {r["target_date"]: r for r in ref_rows}
    added = []
    removed = []

    for r in new_rows:
        b = ref[r["target_date"]]
        if r["action"] == "SUPPRESS_DOWN" and b["action"] != "SUPPRESS_DOWN":
            added.append(r)
        if r["action"] != "SUPPRESS_DOWN" and b["action"] == "SUPPRESS_DOWN":
            removed.append(r)

    return {
        "added_suppressions": len(added),
        "added_good": sum(r["actual_direction"] == "UP" for r in added),
        "added_bad": sum(r["actual_direction"] == "DOWN" for r in added),
        "removed_reference_suppressions": len(removed),
        "added_targets": [
            {
                "target_date": r["target_date"],
                "year": r["evaluation_year"],
                "actual_direction": r["actual_direction"],
                "selected_expert": r["selected_expert"],
                "legacy_bucket": r["legacy_bucket"],
                "competence_n": r["competence_n"],
                "competence_precision": r["competence_precision"],
                "competence_lcb90": r["competence_lcb90"],
            }
            for r in added
        ],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    raw, diagnostics, integrity = build_raw_ledger()
    integrity_errors = list(integrity["integrity_errors"])
    observed = integrity["observed"]

    reference_rows = with_actions(raw, "NEW")
    reference_metrics = policy_metrics(reference_rows)

    for k, v in EXPECTED_REFERENCE.items():
        if reference_metrics[k] != v:
            integrity_errors.append(
                f"REFERENCE_{k}:{reference_metrics[k]}!={v}"
            )

    rows = apply_conditional_controller(raw)
    write_ledger(
        OUT / "GOLD_CONTROL_PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_LEDGER_2026-09-22.csv",
        rows,
    )

    by_year = {
        str(y): policy_metrics([
            r for r in rows if int(r["evaluation_year"]) == y
        ])
        for y in (2020, 2021, 2022, 2023, 2024)
    }

    pooled = policy_metrics(rows)
    pooled.update(safety_diagnostic(pooled))
    delta = delta_vs_reference(rows, reference_rows)
    cells = competence_summary(rows)

    if integrity_errors:
        status = "BLOCKED_INTEGRITY_MISMATCH"
    elif not pooled["retrospective_safety_diagnostic_pass"]:
        status = "REJECTED_SAFETY"
    elif pooled["good_suppressions"] <= EXPECTED_REFERENCE["good_suppressions"]:
        status = "SAFE_NO_UTILITY_GAIN"
    else:
        status = "RETROSPECTIVE_UTILITY_GAIN_NOT_CERTIFIED"

    result = {
        "identity": IDENTITY,
        "date": "2026-09-22",
        "preregistered_policy": (
            "Keep N20/K9 persistence gate unchanged. Non-persistent Router-UP "
            "suppresses as in the safety reference. Persistent Router-UP may "
            "suppress only when its exact selected_expert x legacy_bucket cell "
            "has >=30 causally matured persistent SQRT-alarm Router-UP cases "
            "and one-sided 90% Wilson precision LCB > 0.50."
        ),
        "governance": {
            "random_split": False,
            "2025_used": False,
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
            "retrospective_hypothesis_stress": True,
            "external_2020_2021_authority": "RESEARCH_ONLY_SESSIONMASK_V2",
        },
        "diagnostics": diagnostics,
        "frozen_reproduction": {str(k): v for k, v in observed.items()},
        "integrity_errors": integrity_errors,
        "reference_persistent_v1": reference_metrics,
        "by_year": by_year,
        "pooled_2020_2024": pooled,
        "delta_vs_reference": delta,
        "persistent_cell_summary": cells,
        "status": status,
        "interpretation_limit": (
            "Retrospective hypothesis stress only. The policy was specified "
            "after the 2020 failure and persistence-reference result were visible."
        ),
    }

    with (
        OUT / "GOLD_CONTROL_PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_RESULT_2026-09-22.json"
    ).open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lines = [
        "# GOLD CONTROL — PERSISTENT CONDITIONAL-COMPETENCE DAMPENER V1 RESULT",
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

    for y in (2020, 2021, 2022, 2023, 2024):
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
        f"- Bad-suppression rate: {pooled['bad_suppression_rate']}",
        f"- Suppression precision: {pooled['suppression_precision']}",
        f"- False-alarm reduction: {pooled['false_alarm_reduction']}",
        f"- True-DOWN retention: {pooled['true_down_retention']}",
        f"- Remaining forced-DOWN precision: {pooled['remaining_forced_down_precision']}",
        f"- Precision gain pp: {pooled['precision_gain_pp']}",
        f"- Exact safety p: {pooled['exact_lower_tail_p_value']}",
        f"- Exact 90% upper bad-suppression bound: {pooled['exact_90pct_cp_upper_bad_suppression_rate']}",
        "",
        "## Delta vs frozen persistence reference",
        "",
        f"- Added suppressions: {delta['added_suppressions']}",
        f"- Added good: {delta['added_good']}",
        f"- Added bad: {delta['added_bad']}",
        f"- Removed reference suppressions: {delta['removed_reference_suppressions']}",
        "",
        "Retrospective hypothesis stress only; not prospective certification.",
    ]

    (
        OUT / "GOLD_CONTROL_PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_RESULT_2026-09-22.md"
    ).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(status)
    print(json.dumps({
        "integrity_errors": integrity_errors,
        "reference": reference_metrics,
        "pooled": pooled,
        "delta_vs_reference": delta,
        "cell_summary": cells,
    }, indent=2))


if __name__ == "__main__":
    main()
