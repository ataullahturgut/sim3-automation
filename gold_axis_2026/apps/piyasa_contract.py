from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


TIMEFRAME_OFFSETS = {
    "1A": pd.DateOffset(months=1),
    "3A": pd.DateOffset(months=3),
    "6A": pd.DateOffset(months=6),
    "1Y": pd.DateOffset(years=1),
}


@dataclass(frozen=True)
class PriceDelta:
    absolute: float
    percent: float


def _finite_positive(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not pd.notna(out) or out <= 0:
        return None
    return out


def latest_completed_daily_row(
    history: pd.DataFrame,
    *,
    now_utc: pd.Timestamp | None = None,
) -> pd.Series | None:
    """Return the newest daily row strictly before the current UTC date.

    The Piyasa screen uses this only as an operational display reference. It is
    not promoted to the canonical R4.1 NY17 decision reference.
    """
    if history is None or history.empty or "date" not in history.columns or "close" not in history.columns:
        return None

    now = now_utc if now_utc is not None else pd.Timestamp.now(tz="UTC")
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    else:
        now = now.tz_convert("UTC")
    cutoff = now.normalize().tz_localize(None)

    frame = history[["date", "close"]].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce", utc=True).dt.tz_convert(None)
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna(subset=["date", "close"])
    frame = frame[(frame["date"] < cutoff) & (frame["close"] > 0)]
    if frame.empty:
        return None
    return frame.sort_values("date").iloc[-1]


def filter_history_timeframe(history: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Filter the approved 1-year daily display history to 1A/3A/6A/1Y."""
    if timeframe not in TIMEFRAME_OFFSETS:
        raise ValueError(f"UNAPPROVED_TIMEFRAME:{timeframe}")
    if history is None or history.empty or "date" not in history.columns:
        return pd.DataFrame(columns=getattr(history, "columns", ["date", "close"]))

    frame = history.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"]).sort_values("date")
    if frame.empty:
        return frame
    end = pd.Timestamp(frame["date"].max())
    start = end - TIMEFRAME_OFFSETS[timeframe]
    return frame[frame["date"] >= start].reset_index(drop=True)


def price_delta(live_price: Any, reference_close: Any) -> PriceDelta | None:
    live = _finite_positive(live_price)
    ref = _finite_positive(reference_close)
    if live is None or ref is None:
        return None
    absolute = live - ref
    return PriceDelta(absolute=absolute, percent=(absolute / ref) * 100.0)


def gvz_regime(value: Any, *, full_max: float, half_max: float) -> str:
    """Map only the frozen GVZ thresholds to the approved user-facing regimes."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    if not pd.notna(v):
        return "UNAVAILABLE"
    if v <= float(full_max):
        return "NORMAL"
    if v <= float(half_max):
        return "ELEVATED"
    return "PANIC"
