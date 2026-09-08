from __future__ import annotations

import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

import macro_event_successor_v3_inflation_source_audit as m


def test_scope_is_only_headline_and_core_cpi_mom():
    assert m.ALFRED_SERIES == {
        "cpi_level": "CPIAUCSL",
        "core_cpi_level": "CPILFESL",
    }
    assert set(m.TARGET_EVENT_NAMES) == {"CPI (MoM)", "Core CPI (MoM)"}


def test_mom_rounding_matches_release_semantics():
    assert m.pct_mom_1dp(100.6, 100.0) == 0.6
    assert m.pct_mom_1dp(99.6, 100.0) == -0.4


def test_invalid_level_fails_closed():
    try:
        m.pct_mom_1dp(0.0, 100.0)
    except ValueError as exc:
        assert str(exc) == "CPI_LEVEL_MUST_BE_POSITIVE"
    else:
        raise AssertionError("nonpositive CPI level must fail")


def test_historical_consensus_is_never_claimed_pit_by_discovery_contract():
    assert m.DISCOVERY_DATE == "2026-04-10"
    # The live discovery function may identify stable event IDs, but V3 requires
    # a separate prospective timestamped capture before consensus can be PIT-ready.
    assert "MACRO_CPI_CONSENSUS_PIT" in m.TARGET_EVENT_NAMES.values()
    assert "MACRO_CORE_CPI_CONSENSUS_PIT" in m.TARGET_EVENT_NAMES.values()
