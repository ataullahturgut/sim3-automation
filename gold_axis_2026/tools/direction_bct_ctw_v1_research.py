#!/usr/bin/env python3
"""DIRECTION_BCT_CTW_V1_RESEARCH

Exact binary Bayesian Context Tree / Context Tree Weighting predictor.

Frozen contract:
  GOLD_CONTROL_DIRECTION_BCT_CTW_V1_PREREG_2026-09-18.md
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
D = 10
BETA = 0.5


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
    log_pw_train: float
    log_pw_append_down: float
    log_pw_append_up: float
    p_up: float
    forecast_up: int
    actual_up: int
    previous_sign: int


def logaddexp(a: float, b: float) -> float:
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


def log_pe(down: int, up: int) -> float:
    """Jeffreys Dirichlet(1/2,1/2) integrated local likelihood."""
    total = down + up
    return (
        math.lgamma(1.0)
        - math.lgamma(total + 1.0)
        + math.lgamma(down + 0.5)
        - math.lgamma(0.5)
        + math.lgamma(up + 0.5)
        - math.lgamma(0.5)
    )


def context_counts(window: tuple[int, ...]) -> dict[tuple[int, ...], list[int]]:
    """Counts for all suffix-context nodes up to depth D.

    The first D symbols are treated as fixed initial context. Each later symbol
    contributes once to every suffix of its preceding D-symbol history.
    Context tuples are newest-first to match tree traversal.
    """
    if len(window) < D + 1:
        raise ValueError("Need at least D+1 symbols.")

    counts: dict[tuple[int, ...], list[int]] = {}
    for t in range(D, len(window)):
        y = int(window[t])
        history = window[t - D : t]
        counts.setdefault((), [0, 0])[y] += 1
        for depth in range(1, D + 1):
            ctx = tuple(reversed(history[-depth:]))
            counts.setdefault(ctx, [0, 0])[y] += 1
    return counts


def ctw_log_likelihood(window: tuple[int, ...]) -> float:
    """Exact CTW prior-predictive log likelihood conditional on first D signs."""
    counts = context_counts(window)
    memo: dict[tuple[int, ...], float] = {}

    def rec(ctx: tuple[int, ...]) -> float:
        if ctx in memo:
            return memo[ctx]
        down, up = counts.get(ctx, [0, 0])
        local = log_pe(down, up)
        if len(ctx) == D:
            memo[ctx] = local
            return local

        child0 = rec(ctx + (0,))
        child1 = rec(ctx + (1,))
        split = child0 + child1

        value = logaddexp(
            math.log(BETA) + local,
            math.log(1.0 - BETA) + split,
        )
        memo[ctx] = value
        return value

    return rec(())


def predict_up_probability(window52: tuple[int, ...]):
    if len(window52) != WINDOW:
        raise ValueError(f"Expected {WINDOW} signs, got {len(window52)}.")

    base = ctw_log_likelihood(window52)
    log0 = ctw_log_likelihood(window52 + (0,))
    log1 = ctw_log_likelihood(window52 + (1,))

    # Normalize candidate predictive weights explicitly for numerical safety.
    norm = logaddexp(log0, log1)
    p_up = math.exp(log1 - norm)

    # Sequential-probability identity audit. Candidate weights should sum to
    # base prior-predictive mass up to floating-point tolerance.
    ratio_sum = math.exp(log0 - base) + math.exp(log1 - base)
    if abs(ratio_sum - 1.0) > 1e-9:
        raise RuntimeError(f"CTW predictive normalization failed: {ratio_sum}")

    return base, log0, log1, p_up


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
    latest: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        required = {"observation_ts", "value"}
        if not required.issubset(rd.fieldnames or []):
            raise ValueError(f"CSV needs columns {sorted(required)}")
        for row in rd:
            key = row["observation_ts"].strip()
            prior = latest.get(key)
            if prior is None or row.get("retrieved_at", "") > prior.get("retrieved_at", ""):
                latest[key] = row

    by_week: dict[date, tuple[date, float]] = {}
    for row in latest.values():
        if row.get("quality_status") and "APPROV" not in row["quality_status"].upper():
            continue
        dt_ny = parse_ts(row["observation_ts"]).astimezone(NY)
        d = dt_ny.date()
        if d.weekday() >= 5:
            continue
        value = float(row["value"])
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Invalid XAU value on {d}: {value}")
        week = monday_of(d)
        old = by_week.get(week)
        if old is None or d > old[0]:
            by_week[week] = (d, value)

    return [
        WeeklyClose(week_start=w, close_date=d, close=v)
        for w, (d, v) in sorted(by_week.items())
    ]


def build_forecasts(weeks: list[WeeklyClose]) -> list[Forecast]:
    signs: list[int | None] = [None]
    for i in range(1, len(weeks)):
        r = math.log(weeks[i].close / weeks[i - 1].close)
        signs.append(1 if r > 0 else 0)

    out: list[Forecast] = []
    for i in range(WINDOW, len(weeks) - 1):
        hist = signs[i - WINDOW + 1 : i + 1]
        if len(hist) != WINDOW or any(x is None for x in hist):
            continue
        seq = tuple(int(x) for x in hist)
        base, log0, log1, p_up = predict_up_probability(seq)
        actual = signs[i + 1]
        if actual is None:
            continue
        out.append(
            Forecast(
                origin_week_start=weeks[i].week_start,
                origin_close_date=weeks[i].close_date,
                target_week_start=weeks[i + 1].week_start,
                log_pw_train=base,
                log_pw_append_down=log0,
                log_pw_append_up=log1,
                p_up=p_up,
                forecast_up=1 if p_up >= 0.5 else 0,
                actual_up=int(actual),
                previous_sign=int(signs[i]),
            )
        )
    return out


def metrics(rows: list[Forecast]) -> dict[str, float | int | None]:
    if not rows:
        return {"n": 0}

    n = len(rows)
    actual_up = sum(r.actual_up for r in rows)
    actual_down = n - actual_up
    tp = sum(r.forecast_up == 1 and r.actual_up == 1 for r in rows)
    tn = sum(r.forecast_up == 0 and r.actual_up == 0 for r in rows)
    fp = sum(r.forecast_up == 1 and r.actual_up == 0 for r in rows)
    fn = sum(r.forecast_up == 0 and r.actual_up == 1 for r in rows)

    eps = 1e-12
    brier = sum((r.p_up - r.actual_up) ** 2 for r in rows) / n
    logloss = -sum(
        r.actual_up * math.log(min(max(r.p_up, eps), 1 - eps))
        + (1 - r.actual_up) * math.log(min(max(1 - r.p_up, eps), 1 - eps))
        for r in rows
    ) / n

    return {
        "n": n,
        "accuracy": (tp + tn) / n,
        "balanced_accuracy": ((tp / actual_up) + (tn / actual_down)) / 2
        if actual_up and actual_down else None,
        "brier": brier,
        "log_loss": logloss,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "forecast_up": tp + fp,
        "forecast_down": tn + fn,
        "up_sensitivity": tp / actual_up if actual_up else None,
        "down_sensitivity": tn / actual_down if actual_down else None,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "always_up_accuracy": actual_up / n,
        "previous_sign_accuracy": sum(r.previous_sign == r.actual_up for r in rows) / n,
        "mean_p_up": sum(r.p_up for r in rows) / n,
        "min_p_up": min(r.p_up for r in rows),
        "max_p_up": max(r.p_up for r in rows),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--forecast-csv", type=Path, required=True)
    ap.add_argument("--summary-json", type=Path, required=True)
    args = ap.parse_args()

    weeks = load_weekly(args.input_csv)
    rows = build_forecasts(weeks)

    with args.forecast_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = list(asdict(rows[0]).keys()) if rows else [
            "origin_week_start", "origin_close_date", "target_week_start",
            "log_pw_train", "log_pw_append_down", "log_pw_append_up",
            "p_up", "forecast_up", "actual_up", "previous_sign",
        ]
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for row in rows:
            wr.writerow(asdict(row))

    years = sorted({r.target_week_start.year for r in rows})
    summary = {
        "identity": "DIRECTION_BCT_CTW_V1_RESEARCH",
        "window_weeks": WINDOW,
        "max_depth_D": D,
        "beta": BETA,
        "prior": "Dirichlet(1/2,1/2)",
        "decision_rule": "UP iff p_up >= 0.5",
        "by_target_year": {
            str(y): metrics([r for r in rows if r.target_week_start.year == y])
            for y in years
        },
        "all": metrics(rows),
    }
    args.summary_json.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
