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


def test_primary_scoring_is_pre_event_only():
    assert mod.score_primary("ROBUST_UP", "UP") == "EARLY_HIT"
    assert mod.score_primary("ROBUST_DOWN", "UP") == "WRONG_DIRECTION"
    assert mod.score_primary("MIXED", "UP") == "NO_SIGNAL"
    assert mod.score_primary("ROBUST_DOWN", "DOWN") == "EARLY_HIT"


def test_fast_core_supports_up_down_and_mixed():
    assert mod.fast_state(list(range(1, 31))).value == "ROBUST_UP"
    assert mod.fast_state(list(range(31, 1, -1))).value == "ROBUST_DOWN"
    values = [100.0] * 20 + [101.0, 99.0]
    assert mod.fast_state(values).value == "MIXED"


def test_validate_daily_rejects_weekend_contamination():
    dates = pd.bdate_range("2025-01-01", periods=255)
    frame = pd.DataFrame({"date": dates, "close": range(1, 256)})
    # Coverage range is intentionally wrong before the weekend check is relevant,
    # so replace one in-range weekday with an explicit Saturday and ensure weekend
    # contamination is rejected first.
    frame.loc[0, "date"] = pd.Timestamp("2025-01-04")
    with pytest.raises(RuntimeError, match="NON_GOVERNED_WEEKEND_DATE"):
        mod.validate_daily(frame)


def test_frozen_event_inventory_cardinality():
    assert len(mod.EVENTS) == 19
    assert sum(tier == "EXTREME" for _, _, tier in mod.EVENTS) == 5
    assert sum(direction == "UP" for _, direction, _ in mod.EVENTS) == 14
    assert sum(direction == "DOWN" for _, direction, _ in mod.EVENTS) == 5
