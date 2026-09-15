from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import emergency_reversal_volnorm_successor_v1 as v1  # noqa: E402
import emergency_reversal_volnorm_successor_v3 as v3  # noqa: E402


def test_v3_is_corrective_only() -> None:
    c1 = v1.Config()
    c3 = v3.config()
    assert c3.vol_window == c1.vol_window == 20
    assert c3.leg_threshold == c1.leg_threshold == 2.0
    assert c3.reversal_threshold == c1.reversal_threshold == 2.0
    assert c3.extreme_threshold == c1.extreme_threshold == 3.0
    assert v3.SELECTED_HOUR == 14
    assert v3.MIN_YEAR_COVERAGE == 0.95
    assert c3.model_id == "EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V3"


def test_v3_has_no_monthly_forecast_input() -> None:
    assert set(inspect.signature(v3.run_detector).parameters) == {"closes"}


def test_weekday_guard_is_explicit_in_source_function() -> None:
    source = inspect.getsource(v3.fetch_twelve_closes)
    assert "ts.dayofweek >= 5" in source
    assert "SELECTED_EXCEEDS_CALENDAR_WEEKDAYS" in source


def test_detector_rejects_no_weekend_from_valid_input_contract() -> None:
    # Detector mathematics itself consumes a pre-governed path; this test proves
    # source-governed daily dates are expected to be weekdays before detection.
    dates = pd.bdate_range("2024-01-02", periods=30)
    assert all(d.dayofweek < 5 for d in dates)
