from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from regime_v1_data import load_external, load_governed
from regime_v1_router_sqrt import sqrt_rows

IDENTITY = "SQRT_ALARM_SEMANTIC_AUDIT_V1_RESEARCH"
OUT = Path("sqrt_semantic_audit_out")

EXPECTED_ALARMS = {2020: 212, 2021: 28, 2022: 11, 2023: 2, 2024: 17}
EXPECTED_POOLED_DOWN = 127
EXPECTED_POOLED_UP = 143


def direction(ret: float) -> str:
    if ret < 0:
        return "DOWN"
    if ret > 0:
        return "UP"
    return "FLAT"


def risk_confusion(rows: list[dict]) -> dict:
    tp = sum(r["sqrt_alarm"] and r["realized_high_risk"] for r in rows)
    fp = sum(r["sqrt_alarm"] and not r["realized_high_risk"] for r in rows)
    fn = sum((not r["sqrt_alarm"]) and r["realized_high_risk"] for r in rows)
    tn = sum((not r["sqrt_alarm"]) and (not r["realized_high_risk"]) for r in rows)
    alarms = tp + fp
    realized_high = tp + fn
    return {
        "n": len(rows),
        "risk_alarms": alarms,
        "realized_high_risk_targets": realized_high,
        "tp_high_risk": tp,
        "fp_high_risk": fp,
        "fn_high_risk": fn,
        "tn_low_risk": tn,
        "risk_precision": tp / alarms if alarms else None,
        "risk_recall": tp / realized_high if realized_high else None,
        "risk_specificity": tn / (tn + fp) if (tn + fp) else None,
        "risk_alarm_rate": alarms / len(rows) if rows else None,
        "realized_high_risk_rate": realized_high / len(rows) if rows else None,
    }


def alarm_anatomy(rows: list[dict]) -> dict:
    alarms = [r for r in rows if r["sqrt_alarm"]]
    c = Counter(r["alarm_semantic_category"] for r in alarms)
    up = [r for r in alarms if r["actual_direction"] == "UP"]
    down = [r for r in alarms if r["actual_direction"] == "DOWN"]
    up_hit = sum(r["realized_high_risk"] for r in up)
    down_hit = sum(r["realized_high_risk"] for r in down)
    return {
        "alarms": len(alarms),
        "actual_up": len(up),
        "actual_down": len(down),
        "RISK_HIT_DOWN_CLOSE": c["RISK_HIT_DOWN_CLOSE"],
        "RISK_HIT_UP_CLOSE": c["RISK_HIT_UP_CLOSE"],
        "RISK_MISS_DOWN_CLOSE": c["RISK_MISS_DOWN_CLOSE"],
        "RISK_MISS_UP_CLOSE": c["RISK_MISS_UP_CLOSE"],
        "risk_hit_total": c["RISK_HIT_DOWN_CLOSE"] + c["RISK_HIT_UP_CLOSE"],
        "risk_miss_total": c["RISK_MISS_DOWN_CLOSE"] + c["RISK_MISS_UP_CLOSE"],
        "risk_hit_rate_among_alarms": (
            (c["RISK_HIT_DOWN_CLOSE"] + c["RISK_HIT_UP_CLOSE"]) / len(alarms)
            if alarms else None
        ),
        "up_close_risk_hit_count": up_hit,
        "up_close_risk_miss_count": len(up) - up_hit,
        "share_up_close_alarms_that_are_realized_high_risk": (
            up_hit / len(up) if up else None
        ),
        "down_close_risk_hit_count": down_hit,
        "down_close_risk_miss_count": len(down) - down_hit,
        "share_down_close_alarms_that_are_realized_high_risk": (
            down_hit / len(down) if down else None
        ),
    }


def write_ledger(path: Path, rows: list[dict]) -> None:
    fields = [
        "source_class", "evaluation_year", "origin_date", "target_date",
        "formation_n", "q80", "sqrt_forecast", "sqrt_normalized_risk_score",
        "sqrt_alarm", "target_dr", "realized_high_risk", "target_return",
        "actual_direction", "alarm_semantic_category",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    ext = load_external()
    gov = load_governed()

    all_rows = []
    integrity_errors = []

    for year in (2020, 2021, 2022, 2023, 2024):
        src = ext if year <= 2021 else gov
        source_class = "EXTERNAL_RESEARCH_V2" if year <= 2021 else "GOVERNED"
        rows = sqrt_rows(src, year)

        for r in rows:
            rr = dict(r)
            rr["source_class"] = source_class
            rr["realized_high_risk"] = int(float(rr["target_dr"]) >= float(rr["q80"]))
            rr["actual_direction"] = direction(float(rr["target_return"]))

            if rr["sqrt_alarm"]:
                if rr["actual_direction"] == "FLAT":
                    raise RuntimeError(f"FLAT_ALARM_TARGET:{rr['target_date']}")
                hit = bool(rr["realized_high_risk"])
                if hit and rr["actual_direction"] == "DOWN":
                    cat = "RISK_HIT_DOWN_CLOSE"
                elif hit and rr["actual_direction"] == "UP":
                    cat = "RISK_HIT_UP_CLOSE"
                elif (not hit) and rr["actual_direction"] == "DOWN":
                    cat = "RISK_MISS_DOWN_CLOSE"
                else:
                    cat = "RISK_MISS_UP_CLOSE"
            else:
                cat = ""

            rr["alarm_semantic_category"] = cat
            all_rows.append(rr)

        n_alarm = sum(int(r["sqrt_alarm"]) for r in rows)
        if n_alarm != EXPECTED_ALARMS[year]:
            integrity_errors.append(
                f"ALARM_COUNT_{year}:{n_alarm}!={EXPECTED_ALARMS[year]}"
            )

    alarm_rows = [r for r in all_rows if r["sqrt_alarm"]]
    pooled_down = sum(r["actual_direction"] == "DOWN" for r in alarm_rows)
    pooled_up = sum(r["actual_direction"] == "UP" for r in alarm_rows)

    if len(alarm_rows) != 270:
        integrity_errors.append(f"POOLED_ALARMS:{len(alarm_rows)}!=270")
    if pooled_down != EXPECTED_POOLED_DOWN:
        integrity_errors.append(
            f"POOLED_DOWN:{pooled_down}!={EXPECTED_POOLED_DOWN}"
        )
    if pooled_up != EXPECTED_POOLED_UP:
        integrity_errors.append(
            f"POOLED_UP:{pooled_up}!={EXPECTED_POOLED_UP}"
        )

    by_year = {}
    for year in (2020, 2021, 2022, 2023, 2024):
        yr = [r for r in all_rows if int(r["evaluation_year"]) == year]
        by_year[str(year)] = {
            "risk_confusion_full_parent": risk_confusion(yr),
            "alarm_anatomy": alarm_anatomy(yr),
        }

    pooled = {
        "risk_confusion_full_parent": risk_confusion(all_rows),
        "alarm_anatomy": alarm_anatomy(all_rows),
    }

    anatomy = pooled["alarm_anatomy"]
    if integrity_errors:
        conclusion = "BLOCKED_INTEGRITY_MISMATCH"
    elif anatomy["RISK_HIT_UP_CLOSE"] > 0:
        conclusion = "DIRECTION_FALSE_ALARM_LABEL_CONFOUNDS_RISK_AND_DIRECTION"
    else:
        conclusion = "NO_UP_CLOSE_RISK_HITS_OBSERVED"

    result = {
        "identity": IDENTITY,
        "date": "2026-09-22",
        "definition": {
            "forecast_high_risk": "sqrt_forecast >= frozen yearly Q80",
            "realized_high_risk": "target_dr >= same frozen yearly Q80",
            "direction": "next-day close-to-close log return sign",
            "intraday_rebound_timing_claim": "NOT_PROVEN_BY_THIS_AUDIT",
        },
        "governance": {
            "random_split": False,
            "2025_used": False,
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
            "external_2020_2021_authority": "RESEARCH_ONLY_SESSIONMASK_V2",
        },
        "integrity_errors": integrity_errors,
        "by_year": by_year,
        "pooled_2020_2024": pooled,
        "semantic_conclusion": conclusion,
        "interpretation": (
            "An SQRT alarm is a downside-risk forecast, not a DOWN-close forecast. "
            "Any alarm with realized target DR >= Q80 is a realized high-risk hit "
            "even if the target close-to-close direction is UP. UP-close alone "
            "therefore cannot define a SQRT risk-sensor false alarm."
        ),
    }

    write_ledger(
        OUT / "GOLD_CONTROL_SQRT_ALARM_SEMANTIC_AUDIT_V1_LEDGER_2026-09-22.csv",
        all_rows,
    )

    with (
        OUT / "GOLD_CONTROL_SQRT_ALARM_SEMANTIC_AUDIT_V1_RESULT_2026-09-22.json"
    ).open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lines = [
        "# GOLD CONTROL — SQRT ALARM SEMANTIC AUDIT V1 RESULT",
        "",
        f"Semantic conclusion: {conclusion}",
        "",
        "## Integrity",
        "",
        f"- Errors: {integrity_errors if integrity_errors else 'none'}",
        f"- Alarm counts: {EXPECTED_ALARMS}",
        f"- Pooled alarm direction: DOWN={pooled_down}, UP={pooled_up}",
        "",
        "## Alarm anatomy by year",
        "",
        "| Year | alarms | hit+DOWN | hit+UP | miss+DOWN | miss+UP | alarm risk-hit rate | UP-close that are risk hits |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for year in (2020, 2021, 2022, 2023, 2024):
        a = by_year[str(year)]["alarm_anatomy"]
        lines.append(
            f"| {year} | {a['alarms']} | {a['RISK_HIT_DOWN_CLOSE']} | "
            f"{a['RISK_HIT_UP_CLOSE']} | {a['RISK_MISS_DOWN_CLOSE']} | "
            f"{a['RISK_MISS_UP_CLOSE']} | {a['risk_hit_rate_among_alarms']} | "
            f"{a['share_up_close_alarms_that_are_realized_high_risk']} |"
        )

    a = pooled["alarm_anatomy"]
    rc = pooled["risk_confusion_full_parent"]
    lines += [
        "",
        "## Pooled 2020–2024 alarm semantics",
        "",
        f"- Alarms: {a['alarms']}",
        f"- RISK_HIT_DOWN_CLOSE: {a['RISK_HIT_DOWN_CLOSE']}",
        f"- RISK_HIT_UP_CLOSE: {a['RISK_HIT_UP_CLOSE']}",
        f"- RISK_MISS_DOWN_CLOSE: {a['RISK_MISS_DOWN_CLOSE']}",
        f"- RISK_MISS_UP_CLOSE: {a['RISK_MISS_UP_CLOSE']}",
        f"- Risk-hit rate among alarms: {a['risk_hit_rate_among_alarms']}",
        f"- UP-close alarms: {a['actual_up']}",
        f"- UP-close alarms that were nevertheless realized high risk: {a['up_close_risk_hit_count']}",
        f"- Share of UP-close alarms that were realized high risk: {a['share_up_close_alarms_that_are_realized_high_risk']}",
        "",
        "## Full-parent risk-state diagnostics",
        "",
        f"- Rows: {rc['n']}",
        f"- Risk precision: {rc['risk_precision']}",
        f"- Risk recall: {rc['risk_recall']}",
        f"- Risk specificity: {rc['risk_specificity']}",
        "",
        "Do not equate UP-close with SQRT risk false alarm. Intraday rebound timing is not proven by this audit.",
    ]

    (
        OUT / "GOLD_CONTROL_SQRT_ALARM_SEMANTIC_AUDIT_V1_RESULT_2026-09-22.md"
    ).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(conclusion)
    print(json.dumps({
        "integrity_errors": integrity_errors,
        "pooled": pooled,
    }, indent=2))


if __name__ == "__main__":
    main()
