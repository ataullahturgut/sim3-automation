from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

import macro_event_successor_v3_prospective_consensus_capture as m


def test_scope_is_frozen_to_employment_and_inflation_calendar_consensus():
    assert set(m.FAMILY_EVENTS) == {"EMPLOYMENT", "INFLATION"}
    assert set(m.FAMILY_EVENTS["INFLATION"]) == {"CPI (MoM)", "Core CPI (MoM)"}
    assert set(m.FAMILY_EVENTS["EMPLOYMENT"]) == {
        "Nonfarm Payrolls",
        "Unemployment Rate",
        "Average Hourly Earnings (MoM)",
    }


def test_reference_month_suffix_normalization_is_narrow():
    assert m.normalize_event_name("CPI (MoM) (Mar)") == "CPI (MoM)"
    assert m.normalize_event_name("Core CPI (MoM) (Aug)") == "Core CPI (MoM)"
    assert m.normalize_event_name("Nonfarm Payrolls (Aug)") == "Nonfarm Payrolls"
    # Do not strip arbitrary parentheses or broaden the event identity.
    assert m.normalize_event_name("CPI (YoY) (Mar)") == "CPI (YoY)"
    assert m.normalize_event_name("Cleveland CPI (MoM) (Mar)") == "Cleveland CPI (MoM)"
    assert m.normalize_event_name("CPI (MoM) final") == "CPI (MoM) final"


def test_parse_number_units():
    assert m.parse_number("0.3%") == (0.3, "percent")
    assert m.parse_number("55K") == (55.0, "thousand")
    assert m.parse_number("1.2M") == (1200.0, "thousand")
    assert m.parse_number("-") == (None, None)


def test_capture_must_be_before_release_without_network_call():
    release = datetime(2026, 9, 11, 12, 30, tzinfo=timezone.utc)
    capture = datetime(2026, 9, 11, 12, 31, tzinfo=timezone.utc)
    try:
        m.capture("INFLATION", "2026-09-11", release, captured_at=capture)
    except RuntimeError as exc:
        assert str(exc) == "NOT_PRE_RELEASE_CAPTURE"
    else:
        raise AssertionError("post-release capture must fail closed")


def test_release_timestamp_must_be_aware():
    try:
        m.capture("INFLATION", "2026-09-11", datetime(2026, 9, 11, 8, 30))
    except ValueError as exc:
        assert str(exc) == "OFFICIAL_RELEASE_AT_MUST_BE_TIMEZONE_AWARE"
    else:
        raise AssertionError("naive release timestamp must fail closed")
