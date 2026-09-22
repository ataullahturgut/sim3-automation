from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

IDENTITY = "SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_RESEARCH"
EXPECTED_ALARMS = {2023: 2, 2024: 17, 2025: 90}


def sign_label(x: float) -> str:
    if x > 0:
        return "UP"
    if x < 0:
        return "DOWN"
    return "NEUTRAL"


def load_momentum(path: Path) -> dict[str, dict]:
    out = {}
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            month = r["month"]
            mom = float(r["mom"])
            rw = float(r["rw"])
            if not (math.isfinite(mom) and math.isfinite(rw)):
                raise RuntimeError(f"BAD_MOMENTUM_ROW:{month}")
            direction = sign_label(mom - rw)
            if month in out:
                raise RuntimeError(f"DUPLICATE_MOMENTUM_MONTH:{month}")
            out[month] = {
                "target_month": month,
                "mom": mom,
                "rw": rw,
                "direction": direction,
            }
    return out


def load_parent(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            year = int(r["evaluation_year"])
            if year not in (2023, 2024, 2025):
                continue
            if int(r["sqrt_high_risk_alert"]) != 1:
                continue
            ret = float(r["target_close_return"])
            if ret == 0:
                raise RuntimeError(f"ZERO_TARGET_RETURN:{r['target_date']}")
            rows.append({
                "origin_date": r["origin_date"],
                "target_date": r["target_date"],
                "evaluation_year": year,
                "target_close_return": ret,
                "actual_direction": sign_label(ret),
                "actual_high_risk": int(r["actual_high_risk"]),
                "sqrt_normalized_risk_score": float(r["sqrt_normalized_risk_score"]),
                "high_risk_threshold": float(r["high_risk_threshold"]),
                "target_dr": float(r["target_dr"]),
            })
    return rows


def score(rows: list[dict]) -> dict:
    n = len(rows)
    accepted = [r for r in rows if r["momentum_direction"] != "NEUTRAL"]
    if not accepted:
        return {
            "n": n,
            "accepted": 0,
            "coverage": 0.0,
        }

    tp = sum(r["momentum_direction"] == "UP" and r["actual_direction"] == "UP" for r in accepted)
    fp = sum(r["momentum_direction"] == "UP" and r["actual_direction"] == "DOWN" for r in accepted)
    tn = sum(r["momentum_direction"] == "DOWN" and r["actual_direction"] == "DOWN" for r in accepted)
    fn = sum(r["momentum_direction"] == "DOWN" and r["actual_direction"] == "UP" for r in accepted)

    actual_up = tp + fn
    actual_down = tn + fp
    pred_up = tp + fp
    pred_down = tn + fn

    up_precision = tp / pred_up if pred_up else None
    up_recall = tp / actual_up if actual_up else None
    down_precision = tn / pred_down if pred_down else None
    down_recall = tn / actual_down if actual_down else None
    accuracy = (tp + tn) / len(accepted)
    balanced = (
        (up_recall + down_recall) / 2
        if up_recall is not None and down_recall is not None
        else None
    )

    return {
        "n": n,
        "accepted": len(accepted),
        "coverage": len(accepted) / n if n else None,
        "unique_target_months": len({r["target_month"] for r in rows}),
        "momentum_up": sum(r["momentum_direction"] == "UP" for r in rows),
        "momentum_down": sum(r["momentum_direction"] == "DOWN" for r in rows),
        "momentum_neutral": sum(r["momentum_direction"] == "NEUTRAL" for r in rows),
        "actual_up": actual_up,
        "actual_down": actual_down,
        "tp_up": tp,
        "fp_up": fp,
        "tn_down": tn,
        "fn_up": fn,
        "up_precision": up_precision,
        "up_recall": up_recall,
        "down_precision": down_precision,
        "down_recall": down_recall,
        "accuracy": accuracy,
        "balanced_accuracy": balanced,
        "p_actual_up_given_momentum_up": up_precision,
        "p_actual_down_given_momentum_down": down_precision,
    }


def month_anatomy(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for r in rows:
        groups[r["target_month"]].append(r)
    out = []
    for month in sorted(groups):
        rs = groups[month]
        d = rs[0]["momentum_direction"]
        if any(r["momentum_direction"] != d for r in rs):
            raise RuntimeError(f"MOMENTUM_DIRECTION_DRIFT_WITHIN_MONTH:{month}")
        out.append({
            "target_month": month,
            "momentum_direction": d,
            "sqrt_alarms": len(rs),
            "actual_up": sum(r["actual_direction"] == "UP" for r in rs),
            "actual_down": sum(r["actual_direction"] == "DOWN" for r in rs),
            "risk_hit_total": sum(r["actual_high_risk"] == 1 for r in rs),
            "risk_hit_up": sum(r["actual_high_risk"] == 1 and r["actual_direction"] == "UP" for r in rs),
            "risk_hit_down": sum(r["actual_high_risk"] == 1 and r["actual_direction"] == "DOWN" for r in rs),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", type=Path, required=True)
    ap.add_argument("--momentum", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    parent = load_parent(args.parent)
    momentum = load_momentum(args.momentum)
    integrity = []

    counts = Counter(r["evaluation_year"] for r in parent)
    for year, expected in EXPECTED_ALARMS.items():
        if counts[year] != expected:
            integrity.append(f"ALARM_{year}:{counts[year]}!={expected}")
    if counts[2023] + counts[2024] != 19:
        integrity.append(f"ALARM_2023_2024:{counts[2023]+counts[2024]}!=19")

    joined = []
    for r in parent:
        month = r["target_date"][:7]
        m = momentum.get(month)
        if m is None:
            integrity.append(f"MOMENTUM_MONTH_NOT_FOUND:{month}")
            continue
        # Locked replay contract: monthly H=1 target month forecast is issued
        # from the immediately previous origin month. That is necessarily
        # before any target-day origin inside the target month.
        y, mm = map(int, month.split("-"))
        prev_y = y if mm > 1 else y - 1
        prev_m = mm - 1 if mm > 1 else 12
        expected_origin_month = f"{prev_y:04d}-{prev_m:02d}"
        rr = dict(r)
        rr.update({
            "target_month": month,
            "momentum_origin_month": expected_origin_month,
            "momentum_forecast": m["mom"],
            "momentum_rw_reference": m["rw"],
            "momentum_direction": m["direction"],
        })
        joined.append(rr)

    for year in (2023, 2024, 2025):
        if sum(r["evaluation_year"] == year for r in joined) != EXPECTED_ALARMS[year]:
            integrity.append(f"JOINED_{year}_COUNT_MISMATCH")

    # Frozen 2025 parent fact from the SQRT parent result.
    risk_hits_2025 = sum(r["evaluation_year"] == 2025 and r["actual_high_risk"] == 1 for r in joined)
    if risk_hits_2025 != 66:
        integrity.append(f"RISK_HIT_2025:{risk_hits_2025}!=66")

    def block(rows):
        hit = [r for r in rows if r["actual_high_risk"] == 1]
        return {
            "all_sqrt_alarms": score(rows),
            "realized_high_risk_only": score(hit),
            "month_anatomy": month_anatomy(rows),
        }

    by_year = {
        str(year): block([r for r in joined if r["evaluation_year"] == year])
        for year in (2023, 2024, 2025)
    }
    primary = block([r for r in joined if r["evaluation_year"] in (2023, 2024)])
    descriptive_all = block(joined)

    result = {
        "identity": IDENTITY,
        "date": "2026-09-23",
        "rule": "SQRT alarm + MOMENTUM_3M monthly UP => daily UP; monthly DOWN => daily DOWN; NEUTRAL => ABSTAIN",
        "inputs": {
            "sqrt_parent_commit": "2926796b6a7e9048d2c091c9c571cb928b773e02",
            "sqrt_parent_artifact": "GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv",
            "momentum_artifact": "gold_axis_2026/patch_repro_v1/locked_replay_v7_daily_feature_pit_43.csv",
            "momentum_direction_semantics": "sign(mom - rw)",
        },
        "governance": {
            "random_split": False,
            "threshold_tuning": False,
            "2025_role": "LOCKED_RETROSPECTIVE_TRANSPORT_STRESS_ONLY",
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
            "cross_clock_warning": "MOMENTUM_3M remains monthly H=1 prior, not a next-day classifier",
            "cluster_warning": "daily alarm rows sharing a month are not independent trials",
        },
        "integrity_errors": integrity,
        "by_year": by_year,
        "primary_2023_2024": primary,
        "pooled_2023_2025_descriptive": descriptive_all,
        "status": "BLOCKED_INTEGRITY_MISMATCH" if integrity else "DESCRIPTIVE_AUDIT_COMPLETE",
    }

    json_path = args.out / "GOLD_CONTROL_SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_RESULT_2026-09-23.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    fields = [
        "evaluation_year","origin_date","target_date","target_month",
        "momentum_origin_month","momentum_direction","momentum_forecast",
        "momentum_rw_reference","actual_direction","actual_high_risk",
        "target_close_return","target_dr","high_risk_threshold",
        "sqrt_normalized_risk_score",
    ]
    with (args.out / "GOLD_CONTROL_SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_LEDGER_2026-09-23.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in joined:
            w.writerow({k:r.get(k,"") for k in fields})

    lines = [
        "# GOLD CONTROL — SQRT × MOMENTUM_3M CONDITIONAL-RESOLUTION AUDIT V1 RESULT",
        "",
        f"Integrity errors: {integrity if integrity else 'none'}",
        "",
        "## Summary",
        "",
        "| Window | Population | n | months | MOM UP | MOM DOWN | accuracy | balanced accuracy | UP precision | DOWN precision |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, obj in [
        ("2023","2023"),("2024","2024"),("2025 locked stress","2025")
    ]:
        for pop_key, pop_label in [
            ("all_sqrt_alarms","all alarms"),
            ("realized_high_risk_only","risk-hit only"),
        ]:
            m = by_year[obj][pop_key]
            lines.append(
                f"| {label} | {pop_label} | {m.get('n')} | {m.get('unique_target_months')} | "
                f"{m.get('momentum_up')} | {m.get('momentum_down')} | {m.get('accuracy')} | "
                f"{m.get('balanced_accuracy')} | {m.get('up_precision')} | {m.get('down_precision')} |"
            )

    for pop_key, pop_label in [
        ("all_sqrt_alarms","all alarms"),
        ("realized_high_risk_only","risk-hit only"),
    ]:
        m = primary[pop_key]
        lines.append(
            f"| 2023–2024 primary | {pop_label} | {m.get('n')} | {m.get('unique_target_months')} | "
            f"{m.get('momentum_up')} | {m.get('momentum_down')} | {m.get('accuracy')} | "
            f"{m.get('balanced_accuracy')} | {m.get('up_precision')} | {m.get('down_precision')} |"
        )

    lines += [
        "",
        "2025 is locked retrospective stress only and cannot tune the rule.",
        "MOMENTUM_3M remains a monthly H=1 prior; repeated daily alarms inside one month are clustered, not independent trials.",
    ]
    (args.out / "GOLD_CONTROL_SQRT_MOMENTUM3M_CONDITIONAL_RESOLUTION_AUDIT_V1_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(json.dumps({
        "integrity_errors": integrity,
        "primary_2023_2024": primary,
        "2025_locked_stress": by_year["2025"],
    }, indent=2))
    return 0 if not integrity else 2


if __name__ == "__main__":
    raise SystemExit(main())
