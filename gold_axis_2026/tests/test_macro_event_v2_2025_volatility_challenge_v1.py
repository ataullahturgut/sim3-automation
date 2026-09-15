from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "data_pipeline"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

TOOL = ROOT / "tools" / "run_macro_event_v2_2025_volatility_challenge_v1.py"
spec = importlib.util.spec_from_file_location("macro_v2_2025", TOOL)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def test_frozen_volatility_inventory_unchanged():
    assert len(mod.VOL_EVENTS) == 19
    assert sum(tier == "EXTREME" for _, _, tier in mod.VOL_EVENTS) == 5
    assert sum(direction == "UP" for _, direction, _ in mod.VOL_EVENTS) == 14
    assert sum(direction == "DOWN" for _, direction, _ in mod.VOL_EVENTS) == 5


def test_engine_timeline_has_no_volatility_event_argument():
    sig = inspect.signature(mod.build_engine_timeline)
    assert list(sig.parameters) == ["conn"]


def test_engine_direction_semantics():
    assert mod.engine_direction("GOLD_ADVERSE_MACRO_SHOCK") == "DOWN"
    assert mod.engine_direction("GOLD_SUPPORTIVE_MACRO_SHOCK") == "UP"
    assert mod.engine_direction("MACRO_MIXED_OR_SMALL") is None


def test_same_day_overlay_does_not_carry_macro_signal_forward():
    engine = [
        {
            "release_date": "2025-02-07",
            "state": "GOLD_SUPPORTIVE_MACRO_SHOCK",
            "signal_status": "STRONG_EVENT_SIGNAL",
            "signal_direction": "UP",
        },
        {
            "release_date": "2025-04-04",
            "state": "GOLD_ADVERSE_MACRO_SHOCK",
            "signal_status": "STRONG_EVENT_SIGNAL",
            "signal_direction": "DOWN",
        },
    ]
    release_rows, event_rows = mod.overlay_volatility(engine)
    feb10 = next(r for r in event_rows if r["event_date"] == "2025-02-10")
    apr04 = next(r for r in event_rows if r["event_date"] == "2025-04-04")
    assert feb10["status"] == "NOT_APPLICABLE"
    assert apr04["status"] == "SAME_EVENT_SIGNAL_DIRECTION_ALIGNED"
    feb07 = next(r for r in release_rows if r["release_date"] == "2025-02-07")
    assert feb07["challenge_status"] == "FALSE_WARNING_FOR_DAILY_VOLATILITY_CHALLENGE"


def test_mixed_state_on_same_volatility_day_is_no_signal():
    engine = [
        {
            "release_date": "2025-08-01",
            "state": "MACRO_MIXED_OR_SMALL",
            "signal_status": "NO_SIGNAL",
            "signal_direction": None,
        }
    ]
    _release_rows, event_rows = mod.overlay_volatility(engine)
    aug01 = next(r for r in event_rows if r["event_date"] == "2025-08-01")
    assert aug01["macro_eligible_release"] is True
    assert aug01["status"] == "NO_SIGNAL"


def test_calendar_2025_release_reference_contract():
    assert len(mod.EXPECTED_2025_RELEASE_REFS) == 11
    assert "2025-10" not in mod.EXPECTED_2025_RELEASE_REFS
    assert mod.EXPECTED_CANCELED_REF == "2025-10"
