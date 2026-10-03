from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

# Frozen integrity policy. These are data-quality thresholds, not forecast/model thresholds.
MULTI_ASSET_ABS_LOGRET = 0.25   # severe: >=25% one retained day move
MULTI_ASSET_COUNT = 2
SINGLE_ASSET_ABS_LOGRET = 0.35  # severe single-asset discontinuity
XAU_SOURCE_DIVERGENCE = 0.05    # >=5% level disagreement vs independent XAU
XAU_CONFIRM_TOLERANCE = 0.03    # <=3% agreement is considered corroborating
ROBUST_Z_TRIGGER = 12.0         # optional historical-context trigger


@dataclass(frozen=True)
class GateDecision:
    date: str
    status: str
    admit: bool
    reason: str
    severe_asset_n: int
    max_abs_logret: float
    gold_logret: float
    independent_xau: Optional[float]
    xau_level_divergence: Optional[float]
    independent_available: bool


def _safe_logret(cur: float, prev: float) -> float:
    if not (np.isfinite(cur) and np.isfinite(prev) and cur > 0 and prev > 0):
        return float("nan")
    return float(math.log(cur / prev))


def evaluate_row(
    current: dict,
    previous_accepted: dict,
    independent_xau: Optional[float],
    robust_z_max: Optional[float] = None,
) -> GateDecision:
    date = str(pd.Timestamp(current["date"]).date())
    metals = ["gold", "silver", "platinum", "palladium"]
    rets = {
        m: _safe_logret(float(current[m]), float(previous_accepted[m]))
        for m in metals
    }
    absrets = {m: abs(v) if np.isfinite(v) else float("inf") for m, v in rets.items()}
    severe_n = sum(v >= MULTI_ASSET_ABS_LOGRET for v in absrets.values())
    max_abs = max(absrets.values())
    gold_ret = rets["gold"]

    missing_or_invalid = any(
        not np.isfinite(float(current[m])) or float(current[m]) <= 0 for m in metals
    )
    if missing_or_invalid:
        return GateDecision(
            date, "QUARANTINE_INVALID_VALUE", False,
            "non-positive or non-finite metal value",
            severe_n, max_abs, gold_ret, independent_xau, None,
            independent_xau is not None and np.isfinite(independent_xau),
        )

    multi_trigger = severe_n >= MULTI_ASSET_COUNT
    single_trigger = max_abs >= SINGLE_ASSET_ABS_LOGRET
    robust_trigger = (
        robust_z_max is not None
        and np.isfinite(robust_z_max)
        and abs(float(robust_z_max)) >= ROBUST_Z_TRIGGER
    )
    triggered = multi_trigger or single_trigger or robust_trigger

    if not triggered:
        return GateDecision(
            date, "PASS_NORMAL", True, "no severe discontinuity trigger",
            severe_n, max_abs, gold_ret, independent_xau, None,
            independent_xau is not None and np.isfinite(independent_xau),
        )

    independent_ok = (
        independent_xau is not None
        and np.isfinite(independent_xau)
        and float(independent_xau) > 0
    )
    if not independent_ok:
        return GateDecision(
            date, "QUARANTINE_CONFIRMATION_UNAVAILABLE", False,
            "severe discontinuity requires independent XAU confirmation",
            severe_n, max_abs, gold_ret, independent_xau, None, False,
        )

    div = abs(float(math.log(float(current["gold"]) / float(independent_xau))))
    if div >= XAU_SOURCE_DIVERGENCE:
        return GateDecision(
            date, "QUARANTINE_XAU_SOURCE_DIVERGENCE", False,
            f"severe discontinuity and XAU source divergence {div:.6f} >= {XAU_SOURCE_DIVERGENCE}",
            severe_n, max_abs, gold_ret, independent_xau, div, True,
        )

    if div <= XAU_CONFIRM_TOLERANCE:
        return GateDecision(
            date, "PASS_SEVERE_XAU_CONFIRMED", True,
            f"severe discontinuity corroborated by independent XAU; divergence {div:.6f}",
            severe_n, max_abs, gold_ret, independent_xau, div, True,
        )

    return GateDecision(
        date, "QUARANTINE_AMBIGUOUS_CROSS_SOURCE", False,
        f"severe discontinuity with ambiguous XAU divergence {div:.6f}",
        severe_n, max_abs, gold_ret, independent_xau, div, True,
    )


def decision_dict(d: GateDecision) -> dict:
    return {
        "date": d.date,
        "integrity_status": d.status,
        "integrity_admit": bool(d.admit),
        "integrity_reason": d.reason,
        "severe_asset_n": int(d.severe_asset_n),
        "max_abs_logret": float(d.max_abs_logret),
        "gold_logret": float(d.gold_logret),
        "independent_xau": d.independent_xau,
        "xau_level_divergence": d.xau_level_divergence,
        "independent_available": bool(d.independent_available),
    }
