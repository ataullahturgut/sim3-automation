from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

from macro_event_successor_v3_source_readiness import (
    DIAGNOSTIC_WINDOW_MINUTES,
    PRIMARY_WINDOW_MINUTES,
    MacroFamilySignal,
    MarketShockEpisode,
    match_market_shock,
)

UTC = timezone.utc


def episode(ts: datetime) -> MarketShockEpisode:
    return MarketShockEpisode(started_at=ts, ended_at=ts + timedelta(minutes=5))


def signal(release: datetime, *, pit_ready: bool = True, strong: bool = True) -> MacroFamilySignal:
    return MacroFamilySignal(
        family="EMPLOYMENT",
        official_release_at=release,
        pit_ready=pit_ready,
        strong=strong,
        surprise_score=-1.4,
        direction_context="GOLD_ADVERSE",
    )


def test_windows_are_frozen_to_preregistered_values():
    assert PRIMARY_WINDOW_MINUTES == 10
    assert DIAGNOSTIC_WINDOW_MINUTES == 30


def test_no_macro_never_deletes_raw_market_shock():
    t = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    r = match_market_shock(episode(t), None)
    assert r.state == "NO_MACRO_EXPLANATION"
    assert r.macro_match is False
    assert r.raw_market_shock_preserved is True


def test_strong_pit_ready_event_inside_primary_window_confirms():
    release = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    r = match_market_shock(episode(release + timedelta(minutes=7)), signal(release))
    assert r.state == "MACRO_CONFIRMED"
    assert r.macro_match is True
    assert r.raw_market_shock_preserved is True


def test_not_strong_event_inside_window_does_not_confirm():
    release = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    r = match_market_shock(
        episode(release + timedelta(minutes=3)),
        signal(release, strong=False),
    )
    assert r.state == "MACRO_EVENT_PRESENT_BUT_NOT_STRONG"
    assert r.macro_match is False
    assert r.raw_market_shock_preserved is True


def test_pit_not_ready_cannot_confirm_even_if_strong():
    release = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    r = match_market_shock(
        episode(release + timedelta(minutes=2)),
        signal(release, pit_ready=False, strong=True),
    )
    assert r.state == "MACRO_DATA_NOT_PIT_READY"
    assert r.macro_match is False
    assert r.raw_market_shock_preserved is True


def test_pre_release_shock_is_never_retroactively_confirmed():
    release = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    r = match_market_shock(episode(release - timedelta(minutes=1)), signal(release))
    assert r.state == "PRE_RELEASE_SHOCK"
    assert r.macro_match is False
    assert r.raw_market_shock_preserved is True


def test_event_after_primary_but_inside_diagnostic_is_not_primary_confirmation():
    release = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    r = match_market_shock(episode(release + timedelta(minutes=20)), signal(release))
    assert r.state == "NO_MACRO_EXPLANATION"
    assert r.macro_match is False
    assert r.raw_market_shock_preserved is True


def test_naive_timestamp_is_rejected():
    release = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    try:
        match_market_shock(
            MarketShockEpisode(
                started_at=datetime(2026, 1, 1, 12, 1),
                ended_at=datetime(2026, 1, 1, 12, 6),
            ),
            signal(release),
        )
    except ValueError as exc:
        assert str(exc) == "TIMESTAMP_MUST_BE_TIMEZONE_AWARE"
    else:
        raise AssertionError("naive timestamp must fail closed")
