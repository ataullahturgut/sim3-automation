from __future__ import annotations

import numpy as np
import pandas as pd

from gold_axis_2026.v167_research import run_v167_invariant_signal_screen as v167


def test_contract_is_frozen_and_forbids_post_score_escalation():
    c = v167.load_contract()
    assert c["status"] == "FROZEN_BEFORE_ANY_V167_SCORING"
    assert c["horizon"] == 3
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert "FOIL_or_other_deep_invariant_learning" in c["forbidden_in_v167"]
    assert "2025_2026_based_block_selection" in c["forbidden_in_v167"]
    assert c["model_lock"]["hyperparameter_search"] == "FORBIDDEN"


def test_target_is_exact_three_row_forward_direction():
    panel = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=7, freq="D"),
        "close": [100.0, 101.0, 99.0, 102.0, 100.0, 98.0, 105.0],
    })
    z = v167.build_target_panel(panel)
    assert len(z) == 4
    expected = [1, 0, 0, 1]
    assert z["y"].tolist() == expected
    assert z["target_date"].dt.strftime("%Y-%m-%d").tolist()[0] == "2024-01-04"


def test_causal_frequency_uses_only_strictly_matured_targets():
    panel = pd.DataFrame({
        "target_date": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06"]),
        "y": [1, 0, 1, 1],
    })
    origins = pd.Series(pd.to_datetime(["2024-01-05", "2024-01-07"]))
    p = v167.causal_frequency(panel, origins, min_support=1)
    # At Jan-05 only Jan-03 and Jan-04 are matured: mean=0.5.
    assert np.isclose(p[0], 0.5)
    # At Jan-07 all four are strictly earlier: mean=0.75.
    assert np.isclose(p[1], 0.75)


def test_environment_slice_requires_target_inside_boundary():
    panel = pd.DataFrame({
        "origin_date": pd.to_datetime(["2024-06-28", "2024-06-29", "2024-06-30"]),
        "target_date": pd.to_datetime(["2024-06-30", "2024-07-01", "2024-07-02"]),
        "y": [1, 0, 1],
    })
    z = v167.slice_period(panel, "2024-06-01", "2024-06-30", require_target_inside=True)
    assert len(z) == 1
    assert z.iloc[0]["origin_date"] == pd.Timestamp("2024-06-28")


def test_best_block_selection_uses_worst_skill_then_median_auc():
    eligibility = {
        "A": {"eligible": True, "worst_environment_brier_skill": 0.01, "median_auc": 0.60},
        "B": {"eligible": True, "worst_environment_brier_skill": 0.02, "median_auc": 0.54},
        "C": {"eligible": False, "worst_environment_brier_skill": 0.50, "median_auc": 0.90},
    }
    eligible, best = v167.choose_eligible_blocks(eligibility)
    assert eligible == ["A", "B"]
    assert best == "B"
