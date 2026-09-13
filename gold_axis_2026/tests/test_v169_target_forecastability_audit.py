from __future__ import annotations

import numpy as np
import pandas as pd

from gold_axis_2026.v169_research import run_v169_target_forecastability_audit as v169


def test_contract_frozen_and_scope_locked():
    c = v169.load_contract()
    assert c["status"] == "FROZEN_BEFORE_ANY_V169_SCORING"
    assert c["horizons"] == [1, 3]
    assert c["model_lock"]["hyperparameter_search"] == "FORBIDDEN"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert "deadband_or_material_move_threshold_tuning" in c["forbidden_in_v169"]
    assert "2025_2026_based_feature_or_horizon_selection" in c["forbidden_in_v169"]


def test_targets_are_exact_log_returns_and_direction():
    panel = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5, freq="D"),
        "close": [100.0, 102.0, 101.0, 104.0, 103.0],
    })
    z1 = v169.build_target_panel(panel, 1)
    assert len(z1) == 4
    assert np.isclose(z1.iloc[0]["continuous_return"], np.log(1.02))
    assert z1["y"].tolist() == [1, 0, 1, 0]
    z3 = v169.build_target_panel(panel, 3)
    assert len(z3) == 2
    assert np.isclose(z3.iloc[0]["continuous_return"], np.log(1.04))
    assert z3["y"].tolist() == [1, 1]


def test_matured_history_strictly_excludes_same_day_target():
    panel = pd.DataFrame({
        "target_date": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]),
        "y": [1, 0, 1],
        "continuous_return": [0.01, -0.02, 0.03],
    })
    h = v169.matured_history(panel, pd.Timestamp("2024-01-05"))
    assert len(h) == 2
    assert h["y"].tolist() == [1, 0]


def test_period_boundary_requires_target_inside_period():
    panel = pd.DataFrame({
        "origin_date": pd.to_datetime(["2024-06-28", "2024-06-29", "2024-06-30"]),
        "target_date": pd.to_datetime(["2024-06-30", "2024-07-01", "2024-07-02"]),
    })
    assert v169.period_indices(panel, "2024-06-01", "2024-06-30") == [0]


def test_magnitude_thresholds_use_only_pre_bridge_matured_targets():
    values = np.arange(1, 31, dtype=float) / 1000.0
    panel = pd.DataFrame({
        "target_date": pd.date_range("2024-08-01", periods=30, freq="D"),
        "continuous_return": values,
    })
    q33, q67 = v169.magnitude_thresholds(panel)
    assert q33 > 0
    assert q67 > q33
