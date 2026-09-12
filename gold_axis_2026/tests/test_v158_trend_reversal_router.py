from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v158_thesis import run_v158_trend_reversal_router as core
from gold_axis_2026.v158_thesis import run_v158_entry as entry

ROOT = Path(__file__).resolve().parents[1]


def contract() -> dict:
    return json.loads((ROOT / "v158_thesis/contracts/v158_trend_reversal_router_freeze_v1.json").read_text())


def test_contract_is_frozen_research_only():
    c = contract()
    assert c["status"] == "FROZEN_BEFORE_V158_RETROSPECTIVE_SCORING"
    assert c["evidence_class"] == "RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"
    assert c["target"]["primary_horizon_sessions"] == 20


def test_emergency_research_geometry_is_context_and_month_resets():
    c = contract()
    d = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06", "2025-02-03"]),
        "close": [105.0, 110.0, 105.0, 100.0],
    })
    refs = {"2025-01": 100.0, "2025-02": 100.0}
    out = core.emergency_research_context(d, refs, c)
    assert out.loc[0, "emergency_level"] == 1
    assert out.loc[1, "emergency_level"] == 1
    assert out.loc[2, "emergency_reversal"] == -1
    assert out.loc[2, "emergency_alert_onset"] == -1
    assert out.loc[3, "emergency_reversal"] == 0
    assert out.loc[3, "emergency_alert_age"] == 0
    assert c["emergency_research_context"]["alert_is_context_not_direction_vote"] is True


def test_reversal_target_is_relative_to_trailing_trend():
    d = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=23, freq="D"),
        "close": np.r_[np.repeat(100.0, 20), [100.0, 90.0, 110.0]],
        "mom20": np.r_[np.repeat(0.10, 21), [-0.10, -0.10]],
        "fast_role": np.zeros(23),
        "slow_role": np.zeros(23),
        "monthly_direction_3m": np.zeros(23),
    })
    z = core.add_router_target(d, 1)
    assert z.loc[19, "trend_sign"] == 1
    assert z.loc[19, "future_direction"] == -1
    assert z.loc[19, "reversal_y"] == 1
    assert z.loc[20, "trend_sign"] == 1
    assert z.loc[20, "future_direction"] == 1
    assert z.loc[20, "reversal_y"] == 0


def test_mature_training_excludes_unmatured_targets():
    c = contract()
    n = 260
    d = pd.DataFrame({"reversal_y": np.tile([0, 1], n // 2), "trend_sign": np.ones(n, dtype=int)})
    idx = core.mature_training_indices(d, 220, 20, c)
    assert idx
    assert max(idx) + 20 <= 220
    assert len(idx) <= c["models"]["training"]["rolling_cap"]


def test_entry_trims_cross_period_target_maturity():
    c = contract()
    f = pd.DataFrame({
        "origin_date": pd.to_datetime(["2025-12-01", "2025-12-20", "2026-06-01", "2026-06-20"]),
        "target_date": pd.to_datetime(["2025-12-29", "2026-01-20", "2026-06-29", "2026-07-20"]),
        "x": [1, 2, 3, 4],
    })
    out = entry._within_frozen_period_maturity(f, c)
    assert out["x"].tolist() == [1, 3]


def test_router_selective_semantics_and_rtq_confirmation():
    c = contract()
    f = pd.DataFrame({
        "trend_sign": [1, 1, -1, -1, 1],
        "p_reversal": [0.70, 0.30, 0.70, 0.30, 0.50],
        "rtq_signal": [1, 1, -1, -1, 1],
    })
    out = core.apply_router(f, c)
    assert out["router_primary_dir"].tolist() == [-1, 1, 1, -1, 0]
    assert out["router_confirmed_dir"].tolist() == [-1, 1, 1, -1, 0]
    f2 = pd.DataFrame({"trend_sign": [1], "p_reversal": [0.30], "rtq_signal": [-1]})
    out2 = core.apply_router(f2, c)
    assert int(out2.loc[0, "router_primary_dir"]) == 1
    assert int(out2.loc[0, "router_confirmed_dir"]) == 0
