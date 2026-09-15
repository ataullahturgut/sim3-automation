from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import emergency_reversal_volnorm_successor_v1 as v1  # noqa: E402
import emergency_reversal_volnorm_successor_v2 as v2  # noqa: E402


def test_v2_changes_source_not_detector_thresholds() -> None:
    c1 = v1.Config()
    c2 = v2.config()
    assert c2.vol_window == c1.vol_window == 20
    assert c2.leg_threshold == c1.leg_threshold == 2.0
    assert c2.reversal_threshold == c1.reversal_threshold == 2.0
    assert c2.extreme_threshold == c1.extreme_threshold == 3.0
    assert v2.SELECTED_HOUR == 14
    assert v2.MIN_YEAR_COVERAGE == 0.95
    assert c2.model_id == "EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V2"
    assert c2.source_id == "XAU_TWELVE_1H_SELECT_14_00_NY_RESEARCH_V2"


def test_v2_has_no_monthly_forecast_input() -> None:
    import inspect
    assert set(inspect.signature(v2.run_detector).parameters) == {"closes"}
