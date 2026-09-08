from __future__ import annotations

import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1] / "data_pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

import macro_event_successor_v3_fomc_source_readiness as m


def meeting(date: str, rows: list[tuple[float, float, float]]) -> m.MeetingExpectation:
    return m.MeetingExpectation(
        meeting_date=date,
        buckets=tuple(m.RateBucket(*x) for x in rows),
    )


def test_expected_target_midpoint_uses_probability_weighted_range_midpoints():
    x = meeting("2026-09-16", [(4.00, 4.25, 0.25), (4.25, 4.50, 0.75)])
    assert abs(m.expected_target_midpoint_pct(x) - 4.3125) < 1e-12


def test_target_surprise_is_realized_minus_pre_expected_in_bps():
    x = meeting("2026-09-16", [(4.00, 4.25, 0.25), (4.25, 4.50, 0.75)])
    # Realized 4.00-4.25 midpoint = 4.125; pre expected = 4.3125.
    assert abs(m.target_surprise_bps(4.00, 4.25, x) - (-18.75)) < 1e-12


def test_future_path_shift_is_post_minus_pre_expected_midpoint():
    pre = meeting("2026-10-28", [(4.00, 4.25, 0.5), (4.25, 4.50, 0.5)])
    post = meeting("2026-10-28", [(3.75, 4.00, 0.5), (4.00, 4.25, 0.5)])
    assert abs(m.future_path_shift_bps(pre, post) - (-25.0)) < 1e-12


def test_distribution_must_sum_to_one():
    x = meeting("2026-09-16", [(4.00, 4.25, 0.2), (4.25, 4.50, 0.2)])
    try:
        m.expected_target_midpoint_pct(x)
    except ValueError as exc:
        assert str(exc).startswith("PROBABILITIES_DO_NOT_SUM_TO_ONE")
    else:
        raise AssertionError("invalid distribution must fail closed")


def test_future_path_meeting_mismatch_fails_closed():
    pre = meeting("2026-10-28", [(4.00, 4.25, 1.0)])
    post = meeting("2026-12-09", [(4.00, 4.25, 1.0)])
    try:
        m.future_path_shift_bps(pre, post)
    except ValueError as exc:
        assert str(exc) == "MEETING_DATE_MISMATCH"
    else:
        raise AssertionError("meeting mismatch must fail")


def test_no_cme_config_is_explicit_blocker():
    r = m.source_readiness_from_env({})
    assert r.status == "BLOCKED_CME_FEDWATCH_API_NOT_CONFIGURED"
    assert r.cme_api_configured is False
    assert r.path_method_state == "BLOCKED_PATH_FACTOR_METHOD_NOT_FROZEN"


def test_config_without_schema_does_not_guess_provider_json():
    r = m.source_readiness_from_env({
        "CME_FEDWATCH_API_URL": "https://licensed.example/api",
        "CME_FEDWATCH_API_KEY": "secret",
    })
    assert r.status == "BLOCKED_CME_FEDWATCH_SCHEMA_NOT_PROVEN"
    assert r.cme_schema_contract_configured is False


def test_full_config_is_still_not_an_access_pass():
    r = m.source_readiness_from_env({
        "CME_FEDWATCH_API_URL": "https://licensed.example/api",
        "CME_FEDWATCH_API_KEY": "secret",
        "CME_FEDWATCH_SCHEMA_VERSION": "provider-supplied-v1",
    })
    assert r.status == "CONFIG_PRESENT_ACCESS_NOT_YET_PROVEN"
    assert r.cme_api_configured is True
