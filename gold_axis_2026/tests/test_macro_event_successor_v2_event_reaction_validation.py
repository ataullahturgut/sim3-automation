from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))
PIPELINE = PIPELINE_DIR / "macro_event_successor_v2_event_reaction_validation.py"
spec = importlib.util.spec_from_file_location("macro_event_successor_v2_event_reaction_validation", PIPELINE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_reaction_pct():
    assert math.isclose(mod.reaction_pct(2000.0, 2010.0), 0.5, abs_tol=1e-12)
    assert math.isclose(mod.reaction_pct(2000.0, 1990.0), -0.5, abs_tol=1e-12)


def test_expected_signed_return_orientation():
    assert mod.expected_signed_return("GOLD_ADVERSE_MACRO_SHOCK", -0.2) == 0.2
    assert mod.expected_signed_return("GOLD_ADVERSE_MACRO_SHOCK", 0.2) == -0.2
    assert mod.expected_signed_return("GOLD_SUPPORTIVE_MACRO_SHOCK", 0.2) == 0.2
    assert mod.expected_signed_return("GOLD_SUPPORTIVE_MACRO_SHOCK", -0.2) == -0.2


def test_exact_sign_test_for_eight_events():
    assert math.isclose(mod.binom_one_sided_p(8, 8), 1 / 256, abs_tol=1e-15)
    assert math.isclose(mod.binom_one_sided_p(7, 8), 9 / 256, abs_tol=1e-15)
    assert math.isclose(mod.binom_one_sided_p(6, 8), 37 / 256, abs_tol=1e-15)
    assert mod.binom_one_sided_p(7, 8) <= 0.10
    assert mod.binom_one_sided_p(6, 8) > 0.10


def test_frozen_bar_times():
    assert mod.BAR_TIMES == ("08:29:00", "08:34:00", "08:44:00", "08:59:00")
    assert mod.EXPECTED_EVENT_COUNT == 8
