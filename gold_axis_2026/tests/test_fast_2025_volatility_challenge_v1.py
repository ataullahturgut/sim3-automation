from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

TOOL = ROOT / "tools" / "run_fast_2025_volatility_challenge_v1.py"
spec = importlib.util.spec_from_file_location("fast_vol_v1", TOOL)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def test_fast_core_supports_up_down_and_mixed():
    assert mod.fast_state(list(range(1, 31))).value == "ROBUST_UP"
    assert mod.fast_state(list(range(31, 1, -1))).value == "ROBUST_DOWN"
    values = [100.0] * 20 + [101.0, 99.0]
    assert mod.fast_state(values).value == "MIXED"


def test_validate_daily_rejects_weekend_contamination():
    dates = pd.bdate_range("2025-01-01", periods=255)
    frame = pd.DataFrame({"date": dates, "close": range(1, 256)})
    frame.loc[0, "date"] = pd.Timestamp("2025-01-04")
    with pytest.raises(RuntimeError, match="NON_GOVERNED_WEEKEND_DATE"):
        mod.validate_daily(frame)


def test_frozen_event_inventory_cardinality():
    assert len(mod.EVENTS) == 19
    assert sum(tier == "EXTREME" for _, _, tier in mod.EVENTS) == 5
    assert sum(direction == "UP" for _, direction, _ in mod.EVENTS) == 14
    assert sum(direction == "DOWN" for _, direction, _ in mod.EVENTS) == 5


def test_new_robust_episode_is_transition_not_every_robust_day():
    timeline = pd.DataFrame(
        [
            {"date": "2025-01-02", "close": 100.0, "fast_state": "MIXED", "previous_fast_state": "ROBUST_DOWN", "new_robust_episode": False, "volatility_event": False, "event_direction": None, "event_tier": None},
            {"date": "2025-01-03", "close": 101.0, "fast_state": "ROBUST_UP", "previous_fast_state": "MIXED", "new_robust_episode": True, "volatility_event": False, "event_direction": None, "event_tier": None},
            {"date": "2025-01-06", "close": 102.0, "fast_state": "ROBUST_UP", "previous_fast_state": "ROBUST_UP", "new_robust_episode": False, "volatility_event": False, "event_direction": None, "event_tier": None},
        ]
    )
    assert int(timeline["new_robust_episode"].sum()) == 1


def test_summary_does_not_report_old_event_conditioned_hit_rate():
    timeline = pd.DataFrame(
        [{"date": "2025-01-02", "close": 100.0, "fast_state": "ROBUST_UP", "previous_fast_state": "MIXED", "new_robust_episode": True, "volatility_event": False, "event_direction": None, "event_tier": None}]
    )
    onsets = pd.DataFrame(
        [{
            "signal_date": "2025-01-02", "fast_state": "ROBUST_UP", "signal_direction": "UP", "close": 100.0,
            "next_volatility_event": None, "next_event_direction": None, "next_event_tier": None, "days_to_next_event": None,
            "next_same_direction_event": None, "next_same_direction_tier": None, "days_to_next_same_direction_event": None,
            "same_direction_event_day": False, "same_direction_early_within_1d": False,
            "same_direction_early_within_3d": False, "same_direction_early_within_5d": False,
            "same_direction_early_within_10d": False,
        }]
    )
    summary = mod.summarize(timeline, onsets)
    assert "segments" not in summary
    assert summary["withdrawn_metric"].startswith("EVENT_CONDITIONED_11_OF_19")
    assert summary["false_alarm_rate"].startswith("NOT_FROZEN")
