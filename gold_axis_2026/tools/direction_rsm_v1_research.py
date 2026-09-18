#!/usr/bin/env python3
"""DIRECTION_RSM_V1_RESEARCH

Pure, reproducible RSM-52 implementation for Gold Control.

Input CSV columns:
  observation_ts,value
Optional:
  retrieved_at,quality_status

The script does not tune any parameter. Frozen rules live in
GOLD_CONTROL_DIRECTION_RSM_V1_PREREG_2026-09-18.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
WINDOW = 52


@dataclass(frozen=True)
class WeeklyClose:
    week_start: date
    close_date: date
    close: float


@dataclass(frozen=True)
class Forecast:
    origin_week_start: date
    origin_close_date: date
    target_week_start: date
    p_up: float
    forecast_up: int
    actual_up: int
    previous_sign: int


def parse_ts(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        raise ValueError(f"observation_ts must be timezone-aware: {s}")
    return dt


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def load_weekly(path: Path) -> list[WeeklyClose]:
    # Deduplicate by observation_ts. If retrieved_at exists, keep latest retrieval.
    latest: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        required = {"observation_ts", "value"}
        if not required.issubset(rd.fieldnames or []):
            raise ValueError(f"CSV needs columns {sorted(required)}")
        for row in rd:
            ts_key = row["observation_ts"].strip()
            prior = latest.get(ts_key)
            if prior is None:
                latest[ts_key] = row
            elif row.get("retrieved_at", "") > prior.get("retrieved_at", ""):
                latest[ts_key] = row

    by_week: dict[date, tuple[date, float]] = {}
    for row in latest.values():
        if row.get("quality_status") and "APPROV" not in row["quality_status"].upper():
            continue
        dt_ny = parse_ts(row["observation_ts"]).astimezone(NY)
        d = dt_ny.date()
        if d.weekday() >= 5:  # Sat/Sun excluded.
            continue
        v = float(row["value"])
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"Invalid XAU value on {d}: {v}")
        ws = monday_of(d)
        prev = by_week.get(ws)
        if prev is None or d > prev[0]:
            by_week[ws] = (d, v)

    weeks = [
        WeeklyClose(week_start=ws, close_date=d, close=v)
        for ws, (d, v) in sorted(by_week.items())
    ]
    if len(weeks) < WINDOW + 2:
        raise ValueError("Insufficient weekly history for RSM-52.")
    return weeks


def build_forecasts(weeks: list[WeeklyClose]) -> list[Forecast]:
    signs: list[int | None] = [None]
    for i in range(1, len(weeks)):
        r = math.log(weeks[i].close / weeks[i - 1].close)
        signs.append(1 if r > 0 else 0)

    out: list[Forecast] = []
    # origin i forecasts target i+1; need signs i-51..i = 52 observed signs.
    for i in range(WINDOW, len(weeks) - 1):
        hist = signs[i - WINDOW + 1 : i + 1]
        if len(hist) != WINDOW or any(x is None for x in hist):
            continue
        p = sum(int(x) for x in hist) / WINDOW
        target = signs[i + 1]
        if target is None:
            continue
        out.append(
            Forecast(
                origin_week_start=weeks[i].week_start,
                origin_close_date=weeks[i].close_date,
                target_week_start=weeks[i + 1].week_start,
                p_up=p,
                forecast_up=1 if p >= 0.5 else 0,
                actual_up=int(target),
                previous_sign=int(signs[i]),
            )
        )
    return out


def metrics(rows: list[Forecast]) -> dict[str, float | int | None]:
    if not rows:
        return {"n": 0}

    n = len(rows)
    correct = sum(r.forecast_up == r.actual_up for r in rows)
    positives = sum(r.actual_up for r in rows)
    negatives = n - positives
    tp = sum(r.forecast_up == 1 and r.actual_up == 1 for r in rows)
    tn = sum(r.forecast_up == 0 and r.actual_up == 0 for r in rows)

    tpr = tp / positives if positives else None
    tnr = tn / negatives if negatives else None
    bal = (tpr + tnr) / 2 if tpr is not None and tnr is not None else None

    eps = 1e-12
    brier = sum((r.p_up - r.actual_up) ** 2 for r in rows) / n
    logloss = -sum(
        r.actual_up * math.log(min(max(r.p_up, eps), 1 - eps))
        + (1 - r.actual_up) * math.log(min(max(1 - r.p_up, eps), 1 - eps))
        for r in rows
    ) / n

    return {
        "n": n,
        "accuracy": correct / n,
        "balanced_accuracy": bal,
        "brier": brier,
        "log_loss": logloss,
        "actual_up": positives,
        "actual_down": negatives,
        "forecast_up": sum(r.forecast_up for r in rows),
        "forecast_down": n - sum(r.forecast_up for r in rows),
        "p_exact_0_5": sum(abs(r.p_up - 0.5) < 1e-15 for r in rows),
        "always_up_accuracy": positives / n,
        "previous_sign_accuracy": sum(r.previous_sign == r.actual_up for r in rows) / n,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--forecast-csv", type=Path, required=True)
    ap.add_argument("--summary-json", type=Path, required=True)
    args = ap.parse_args()

    weeks = load_weekly(args.input_csv)
    forecasts = build_forecasts(weeks)

    with args.forecast_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = list(asdict(forecasts[0]).keys()) if forecasts else [
            "origin_week_start", "origin_close_date", "target_week_start",
            "p_up", "forecast_up", "actual_up", "previous_sign"
        ]
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for r in forecasts:
            wr.writerow(asdict(r))

    by_year = {}
    years = sorted({r.target_week_start.year for r in forecasts})
    for y in years:
        by_year[str(y)] = metrics([r for r in forecasts if r.target_week_start.year == y])

    summary = {
        "identity": "DIRECTION_RSM_V1_RESEARCH",
        "window_weeks": WINDOW,
        "decision_rule": "UP iff p_up >= 0.5",
        "weekly_close_rule": "last actual Monday-Friday NY-local observation in calendar week; no fill/substitution",
        "all": metrics(forecasts),
        "by_target_year": by_year,
    }
    args.summary_json.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
