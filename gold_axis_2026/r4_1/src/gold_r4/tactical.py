from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from .contracts import Direction, FastState, SlowState


def _raw_state(value: float, mean: float) -> Direction:
    if value > mean:
        return Direction.UP
    if value < mean:
        return Direction.DOWN
    return Direction.NEUTRAL


def fast_state(closes: Sequence[float], sma_days: int = 20, persistence_days: int = 2) -> FastState:
    if persistence_days != 2:
        raise ValueError("Frozen R4 contract requires fast persistence_days=2")
    s = pd.Series(list(closes), dtype="float64")
    ma = s.rolling(sma_days, min_periods=sma_days).mean()
    if len(s) < sma_days + 1 or pd.isna(ma.iloc[-1]) or pd.isna(ma.iloc[-2]):
        return FastState.INSUFFICIENT_DATA
    a = _raw_state(float(s.iloc[-2]), float(ma.iloc[-2]))
    b = _raw_state(float(s.iloc[-1]), float(ma.iloc[-1]))
    if a == b == Direction.UP:
        return FastState.ROBUST_UP
    if a == b == Direction.DOWN:
        return FastState.ROBUST_DOWN
    return FastState.MIXED


def slow_state(weekly_closes: Sequence[float], sma_weeks: int = 4, persistence_weeks: int = 2) -> SlowState:
    if persistence_weeks != 2:
        raise ValueError("Frozen R4 contract requires slow persistence_weeks=2")
    s = pd.Series(list(weekly_closes), dtype="float64")
    ma = s.rolling(sma_weeks, min_periods=sma_weeks).mean()
    if len(s) < sma_weeks:
        return SlowState.INSUFFICIENT_DATA
    current = _raw_state(float(s.iloc[-1]), float(ma.iloc[-1]))
    if len(s) < sma_weeks + 1 or pd.isna(ma.iloc[-2]):
        return SlowState.NOT_YET_ROBUST
    previous = _raw_state(float(s.iloc[-2]), float(ma.iloc[-2]))
    if previous == current == Direction.UP:
        return SlowState.ROBUST_UP
    if previous == current == Direction.DOWN:
        return SlowState.ROBUST_DOWN
    return SlowState.NOT_YET_ROBUST


def completed_weekly_closes(daily: pd.DataFrame, asof: pd.Timestamp) -> list[float]:
    x = daily.loc[daily["date"] <= asof, ["date", "close"]].copy()
    x = x.sort_values("date").set_index("date")
    weekly = x["close"].resample("W-FRI").last().dropna()
    if asof.weekday() < 4:
        current_week_end = asof.to_period("W-FRI").end_time.normalize()
        weekly = weekly.loc[weekly.index < current_week_end]
    return [float(v) for v in weekly.tolist()]
