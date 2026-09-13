from __future__ import annotations

import numpy as np
import pandas as pd

from gold_axis_2026.v168_research import run_v168_regime_similarity_local as v168


def test_contract_frozen_and_scope_locked():
    c = v168.load_contract()
    assert c["status"] == "FROZEN_BEFORE_ANY_V168_SCORING"
    assert c["horizon"] == 3
    assert c["k_selection"]["grid"] == [40, 60, 80]
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert "state_vector_changes_after_scoring" in c["forbidden_in_v168"]
    assert "forecast_combination_between_blocks" in c["forbidden_in_v168"]


def test_target_is_three_rows_forward():
    panel = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=7, freq="D"),
        "close": [100, 101, 99, 102, 100, 98, 105],
    })
    z = v168.build_target_panel(panel)
    assert z["y"].tolist() == [1, 0, 0, 1]


def test_matured_history_is_strictly_before_origin():
    panel = pd.DataFrame({
        "target_date": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05"]),
        "y": [1, 0, 1],
    })
    h = v168.matured_history(panel, pd.Timestamp("2024-01-05"))
    assert len(h) == 2
    assert h["y"].tolist() == [1, 0]


def test_similarity_neighbours_choose_closest_standardized_states():
    hist = pd.DataFrame({
        "s1": [0.0, 1.0, 10.0],
        "s2": [0.0, 1.0, 10.0],
    })
    cur = pd.DataFrame({"s1": [1.2], "s2": [1.1]})
    idx, mean_dist = v168.similarity_indices(hist, cur, ["s1", "s2"], 2)
    assert set(idx.tolist()) == {0, 1}
    assert mean_dist is not None and np.isfinite(mean_dist)


def test_period_indices_keep_target_inside_period():
    panel = pd.DataFrame({
        "origin_date": pd.to_datetime(["2024-06-28", "2024-06-29", "2024-06-30"]),
        "target_date": pd.to_datetime(["2024-06-30", "2024-07-01", "2024-07-02"]),
    })
    idx = v168.period_indices(panel, "2024-06-01", "2024-06-30")
    assert idx == [0]
