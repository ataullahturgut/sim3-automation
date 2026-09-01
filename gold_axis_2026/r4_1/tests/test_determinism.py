from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from gold_r4 import Direction, FastState, ReversalAlert, SlowState, classify_state, gvz_risk
from gold_r4.emergency import EmergencyState
from scripts.replay_daily import run_replay


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "frozen_r4_1.json"


def _synthetic_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.bdate_range("2026-01-02", "2026-03-13")
    closes = []
    for i, d in enumerate(dates):
        # Deterministic path with trend, shock and reversal segments.
        if d < pd.Timestamp("2026-02-02"):
            close = 100.0 + i * 0.35
        elif d < pd.Timestamp("2026-02-20"):
            close = 108.0 + (i - 21) * 0.55
        else:
            close = 116.0 - (i - 35) * 0.45
        closes.append(round(close, 6))

    daily = pd.DataFrame(
        {
            "date": dates,
            "close": closes,
            "gvz": 25.0,
            "macro_event_down": False,
            "bocpd_context": "NONE",
        }
    )
    monthly = pd.DataFrame(
        [
            {"target_month": "2026-01", "vw_forecast": 100.0, "return_t1": -0.01, "return_t2": -0.02, "return_t3": 0.01},
            {"target_month": "2026-02", "vw_forecast": 104.0, "return_t1": 0.01, "return_t2": -0.02, "return_t3": -0.01},
            {"target_month": "2026-03", "vw_forecast": 110.0, "return_t1": 0.02, "return_t2": 0.01, "return_t3": -0.01},
        ]
    )
    return daily, monthly


def test_full_replay_is_exactly_repeatable():
    daily, monthly = _synthetic_inputs()
    a = run_replay(daily, monthly)
    b = run_replay(daily, monthly)
    assert_frame_equal(a, b, check_exact=True)


def test_prefix_state_is_invariant_to_future_rows():
    daily, monthly = _synthetic_inputs()
    prefix_n = 35

    full = run_replay(daily, monthly)
    prefix = run_replay(daily.iloc[:prefix_n].copy(), monthly)

    state_cols = [c for c in full.columns if c != "default_execution_session"]
    assert_frame_equal(
        full.iloc[:prefix_n][state_cols].reset_index(drop=True),
        prefix[state_cols].reset_index(drop=True),
        check_exact=True,
    )


def test_prefix_state_is_invariant_to_future_price_perturbation():
    daily, monthly = _synthetic_inputs()
    prefix_n = 35

    baseline = run_replay(daily, monthly)
    perturbed = daily.copy()
    perturbed.loc[prefix_n:, "close"] = perturbed.loc[prefix_n:, "close"] * 1.75
    changed_future = run_replay(perturbed, monthly)

    state_cols = [c for c in baseline.columns if c != "default_execution_session"]
    assert_frame_equal(
        baseline.iloc[:prefix_n][state_cols].reset_index(drop=True),
        changed_future.iloc[:prefix_n][state_cols].reset_index(drop=True),
        check_exact=True,
    )


def test_classification_priority_is_frozen_and_deterministic():
    common = dict(
        monthly_direction=Direction.DOWN,
        level_emergency=Direction.UP,
        fast=FastState.ROBUST_UP,
        slow=SlowState.ROBUST_UP,
    )
    assert classify_state(reversal_alert=ReversalAlert.OFF, macro_event_down=True, **common) == "MACRO_DOWN_RISK"
    assert classify_state(reversal_alert=ReversalAlert.DOWN_ALERT, macro_event_down=False, **common) == "REVERSAL_RISK_DOWN"
    assert classify_state(reversal_alert=ReversalAlert.OFF, macro_event_down=False, **common) == "ALIGNED_UP"


def test_emergency_state_resets_at_calendar_month_boundary():
    s = EmergencyState()
    s.update(pd.Timestamp("2026-01-29"), 110.0, 100.0)
    level, alert = s.update(pd.Timestamp("2026-01-30"), 105.0, 100.0)
    assert level == Direction.UP
    assert alert == ReversalAlert.DOWN_ALERT

    # New month must not inherit January peak/trough state.
    level2, alert2 = s.update(pd.Timestamp("2026-02-02"), 105.0, 100.0)
    assert level2 == Direction.UP
    assert alert2 == ReversalAlert.OFF


def test_frozen_config_matches_current_rule_defaults():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    emergency = EmergencyState()
    assert emergency.level_threshold_abs == cfg["emergency"]["level_threshold_abs"]
    assert emergency.reversal_threshold_abs == cfg["emergency"]["reversal_threshold_abs"]

    assert cfg["tactical"]["fast_sma_days"] == 20
    assert cfg["tactical"]["fast_persistence_days"] == 2
    assert cfg["tactical"]["slow_sma_weeks"] == 4
    assert cfg["tactical"]["slow_persistence_weeks"] == 2

    full = gvz_risk(cfg["gvz"]["full_cap_max"])
    elevated = gvz_risk(cfg["gvz"]["full_cap_max"] + 0.0001)
    panic = gvz_risk(cfg["gvz"]["panic_above"] + 0.0001)
    assert full.cap == cfg["gvz"]["caps"]["normal"] and full.panic is False
    assert elevated.cap == cfg["gvz"]["caps"]["elevated"] and elevated.panic is False
    assert panic.cap == cfg["gvz"]["caps"]["panic"] and panic.panic is True
