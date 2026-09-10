from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

FAST_LEVELS = ("MIXED", "ROBUST_DOWN", "ROBUST_UP")
SLOW_LEVELS = ("NOT_YET_ROBUST", "ROBUST_DOWN", "ROBUST_UP")
MONTHLY_LEVELS = ("NEUTRAL", "DOWN", "UP")
EMERGENCY_LEVELS = ("NEUTRAL", "DOWN", "UP")
REVERSAL_LEVELS = ("OFF", "DOWN_ALERT", "UP_ALERT")


@dataclass(frozen=True)
class TargetRow:
    origin_index: int
    target_index: int
    origin_date: pd.Timestamp
    target_date: pd.Timestamp
    horizon: int
    log_return: float
    y: int


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_role_replay(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    required = {
        "date", "close", "monthly_direction_3m", "fast_state", "slow_state",
        "emergency_level", "emergency_reversal",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(f"REQUIRED_COLUMNS_NOT_FOUND:{','.join(missing)}")
    if df["date"].duplicated().any() or not df["date"].is_monotonic_increasing:
        raise RuntimeError("NY17_ELIGIBLE_DATE_ORDER_INVALID")
    if df["close"].isna().any() or (df["close"] <= 0).any():
        raise RuntimeError("NY17_CLOSE_INVALID")
    allowed = {
        "fast_state": set(FAST_LEVELS),
        "slow_state": set(SLOW_LEVELS),
        "monthly_direction_3m": set(MONTHLY_LEVELS),
        "emergency_level": set(EMERGENCY_LEVELS),
        "emergency_reversal": set(REVERSAL_LEVELS),
    }
    for column, levels in allowed.items():
        actual = set(df[column].dropna().astype(str))
        if not actual <= levels:
            raise RuntimeError(f"UNFROZEN_STATE_LEVEL:{column}:{sorted(actual-levels)}")
    return df


def build_targets(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    if horizon not in (1, 3):
        raise ValueError("horizon must be 1 or 3 eligible NY17 observations")
    rows: list[dict] = []
    for i in range(len(df) - horizon):
        j = i + horizon
        r = float(np.log(float(df.at[j, "close"]) / float(df.at[i, "close"])))
        rows.append({
            "origin_index": i,
            "target_index": j,
            "origin_date": df.at[i, "date"],
            "target_date": df.at[j, "date"],
            "horizon": horizon,
            "log_return": r,
            "y": int(r > 0.0),
        })
    return pd.DataFrame(rows)


def one_hot_direction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fixed categorical contrasts; no invented ordinal/sign encoding."""
    out = pd.DataFrame(index=df.index)
    for column, levels, reference in (
        ("fast_state", FAST_LEVELS, "MIXED"),
        ("slow_state", SLOW_LEVELS, "NOT_YET_ROBUST"),
        ("monthly_direction_3m", MONTHLY_LEVELS, "NEUTRAL"),
    ):
        values = df[column].fillna("MISSING").astype(str)
        if (values == "MISSING").any():
            raise RuntimeError(f"BLOCKED_INVENTORY:MISSING_STATE:{column}")
        for level in levels:
            if level != reference:
                out[f"{column}__{level}"] = (values == level).astype(float)
    return out

