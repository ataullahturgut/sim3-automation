from __future__ import annotations

import numpy as np
import pandas as pd

from gold_axis_2026.v166_research import run_v166_3d_mechanism_isolation as v166


def test_contract_is_frozen_and_governance_locked():
    c = v166.load_contract()
    assert c["status"] == "FROZEN_BEFORE_ANY_V166_SCORING"
    assert c["horizon"] == 3
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["decision_lock"]["drift_detector_in_v166"] == "FORBIDDEN"
    assert c["decision_lock"]["selector_scoring_in_v166"] == "FORBIDDEN"


def test_recalibration_slope_is_positive():
    p = np.array([0.2, 0.3, 0.4, 0.6, 0.7, 0.8] * 10, dtype=float)
    y = np.array([0, 0, 0, 1, 1, 1] * 10, dtype=int)
    a, b, ok = v166.fit_constrained_recalibration(p, y, 2.0)
    assert ok
    assert np.isfinite(a)
    assert np.isfinite(b)
    assert b > 0.0


def test_causal_recalibration_uses_only_matured_history():
    c = v166.load_contract()
    n = 45
    df = pd.DataFrame({
        "origin_index": np.arange(n),
        "origin_date": pd.date_range("2025-01-01", periods=n, freq="D"),
        "target_date": pd.date_range("2025-01-04", periods=n, freq="D"),
        "horizon": 3,
        "y": np.arange(n) % 2,
        "STATIC": np.linspace(0.25, 0.75, n),
        "FORGET": np.linspace(0.3, 0.7, n),
        "FREQ": 0.5,
    })
    z = v166.causal_recalibrate(df, c)
    row = z.iloc[33]
    assert int(row["recal_support_n"]) == 31
    assert bool(row["recal_fitted"])


def test_recalibration_falls_back_before_minimum_support():
    c = v166.load_contract()
    n = 20
    df = pd.DataFrame({
        "origin_index": np.arange(n),
        "origin_date": pd.date_range("2025-01-01", periods=n, freq="D"),
        "target_date": pd.date_range("2025-01-04", periods=n, freq="D"),
        "horizon": 3,
        "y": np.arange(n) % 2,
        "STATIC": np.linspace(0.25, 0.75, n),
        "FORGET": np.linspace(0.3, 0.7, n),
        "FREQ": 0.5,
    })
    z = v166.causal_recalibrate(df, c)
    assert np.allclose(z["RECAL_ONLY"], z["STATIC"])
    assert not z["recal_fitted"].any()
