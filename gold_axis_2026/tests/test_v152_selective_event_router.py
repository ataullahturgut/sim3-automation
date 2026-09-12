from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from gold_axis_2026.v152_thesis import run_v152_selective_router as v

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v152_thesis/contracts/v152_selective_event_router_freeze_v1.json"


def contract():
    return json.loads(CONTRACT.read_text())


def test_contract_is_frozen_and_nonproduction():
    c = contract()
    assert c["status"] == "FROZEN_BEFORE_V152_SUCCESSOR_SCORING"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"


def test_primary_families_are_only_employment_and_inflation():
    c = contract()
    assert c["event_router"]["primary_families"] == ["EMPLOYMENT", "INFLATION"]
    assert c["event_router"]["separate_diagnostic_family"] == ["FOMC"]


def test_general_daily_lane_remains_no_signal():
    c = contract()
    assert c["master_policy"]["general_1d_3d"] == "NO_SIGNAL_UNLESS_SEPARATELY_PROVEN"


def test_router_does_not_treat_zero_score_as_signal():
    c = contract()
    d = pd.DataFrame({
        "family": ["EMPLOYMENT", "INFLATION", "FOMC", "EMPLOYMENT"],
        "score": [1.0, -1.0, 1.0, 0.0],
        "state": ["MACRO_MIXED_OR_SMALL"] * 4,
    })
    assert v.primary_router_mask(d, c).tolist() == [True, True, False, False]


def test_high_confidence_requires_primary_family_and_strong_state():
    c = contract()
    d = pd.DataFrame({
        "family": ["EMPLOYMENT", "INFLATION", "FOMC", "EMPLOYMENT"],
        "score": [1.0, -1.0, 1.0, 1.0],
        "state": ["GOLD_ADVERSE_MACRO_SHOCK", "MACRO_MIXED_OR_SMALL", "GOLD_SUPPORTIVE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"],
    })
    assert v.high_confidence_mask(d, c).tolist() == [True, False, False, True]
