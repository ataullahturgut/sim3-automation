from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import emergency_reversal_volnorm_successor_v1 as m  # noqa: E402


def _series_from_returns(returns: list[float], start: str = "2024-01-02") -> pd.Series:
    dates = pd.bdate_range(start, periods=len(returns) + 1)
    prices = [2000.0]
    for r in returns:
        prices.append(prices[-1] * math.exp(r))
    return pd.Series(prices, index=dates, dtype=float)


def test_sigma_is_strictly_prior_only() -> None:
    rng = np.random.default_rng(7)
    base = _series_from_returns(rng.normal(0.0, 0.006, 40).tolist())
    a = m.prepare_daily_frame(base)
    changed = base.copy()
    changed.iloc[-1] *= 1.25
    b = m.prepare_daily_frame(changed)
    # The current close/return may change, but its own sigma may not.
    assert math.isclose(float(a.iloc[-1].sigma20), float(b.iloc[-1].sigma20), rel_tol=0, abs_tol=1e-15)


def test_detector_emits_single_transition_alert_not_persistent_alert() -> None:
    rng = np.random.default_rng(11)
    warmup = rng.normal(0.0, 0.004, 35).tolist()
    # Establish a strong up leg, make a new peak, then sharply reverse.
    returns = warmup + [0.030, 0.018, 0.010, -0.010, -0.035, -0.010, -0.002]
    s = _series_from_returns(returns)
    out = m.run_detector(s)
    alerts = out[out.alert != "OFF"]
    assert len(alerts) >= 1
    assert "DOWN_ALERT" in set(alerts.alert)
    down_positions = alerts.index[alerts.alert.eq("DOWN_ALERT")].tolist()
    for pos in down_positions:
        if pos + 1 < len(out):
            assert out.iloc[pos + 1].alert == "OFF"


def test_prefix_invariance() -> None:
    rng = np.random.default_rng(19)
    returns = rng.normal(0.0, 0.008, 120).tolist()
    full_series = _series_from_returns(returns)
    full = m.run_detector(full_series)
    prefix_n = 90
    prefix = m.run_detector(full_series.iloc[:prefix_n])
    compare_cols = [
        "date", "state", "state_age", "alert", "alert_score", "alert_severity", "reference_extreme_date", "eligible"
    ]
    pd.testing.assert_frame_equal(
        full.loc[: prefix_n - 1, compare_cols].reset_index(drop=True),
        prefix.loc[:, compare_cols].reset_index(drop=True),
        check_dtype=False,
    )


def test_determinism_exact() -> None:
    rng = np.random.default_rng(23)
    s = _series_from_returns(rng.normal(0.0, 0.007, 100).tolist())
    a = m.run_detector(s)
    b = m.run_detector(s)
    assert m.timeline_hash(a) == m.timeline_hash(b)


def test_no_monthly_forecast_dependency() -> None:
    import inspect

    params = set(inspect.signature(m.run_detector).parameters)
    assert params == {"closes", "config"}


def test_thresholds_are_frozen_project_tiers() -> None:
    cfg = m.Config()
    assert cfg.vol_window == 20
    assert cfg.leg_threshold == 2.0
    assert cfg.reversal_threshold == 2.0
    assert cfg.extreme_threshold == 3.0
