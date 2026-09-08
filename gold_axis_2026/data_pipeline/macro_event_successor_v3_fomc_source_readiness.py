from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from typing import Any, Iterable

ENGINE_ID = "MACRO_EVENT_SUCCESSOR_V3"
FAMILY = "FOMC"
PRIMARY_WINDOW_MINUTES = 10


@dataclass(frozen=True)
class RateBucket:
    lower_pct: float
    upper_pct: float
    probability: float

    @property
    def midpoint_pct(self) -> float:
        return (self.lower_pct + self.upper_pct) / 2.0


@dataclass(frozen=True)
class MeetingExpectation:
    meeting_date: str
    buckets: tuple[RateBucket, ...]


@dataclass(frozen=True)
class FomcSourceReadiness:
    status: str
    cme_api_configured: bool
    cme_api_url_configured: bool
    cme_api_key_configured: bool
    cme_schema_contract_configured: bool
    official_target_source: str
    target_method: str
    path_method_state: str
    production_db_write: bool = False
    market_shock_threshold_changed: bool = False
    raw_market_shock_episode_changed: bool = False


def validate_distribution(buckets: Iterable[RateBucket], *, tolerance: float = 1e-6) -> tuple[RateBucket, ...]:
    xs = tuple(buckets)
    if not xs:
        raise ValueError("EMPTY_RATE_PROBABILITY_DISTRIBUTION")
    for b in xs:
        if not all(math.isfinite(x) for x in (b.lower_pct, b.upper_pct, b.probability)):
            raise ValueError("NONFINITE_RATE_PROBABILITY_INPUT")
        if b.upper_pct < b.lower_pct:
            raise ValueError("INVALID_TARGET_RANGE")
        if b.probability < 0.0 or b.probability > 1.0:
            raise ValueError("INVALID_PROBABILITY")
    total = sum(b.probability for b in xs)
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"PROBABILITIES_DO_NOT_SUM_TO_ONE:{total}")
    return xs


def expected_target_midpoint_pct(expectation: MeetingExpectation) -> float:
    buckets = validate_distribution(expectation.buckets)
    return sum(b.probability * b.midpoint_pct for b in buckets)


def target_surprise_bps(realized_lower_pct: float, realized_upper_pct: float, pre: MeetingExpectation) -> float:
    if not all(math.isfinite(x) for x in (realized_lower_pct, realized_upper_pct)):
        raise ValueError("NONFINITE_REALIZED_TARGET")
    if realized_upper_pct < realized_lower_pct:
        raise ValueError("INVALID_REALIZED_TARGET_RANGE")
    realized_midpoint = (realized_lower_pct + realized_upper_pct) / 2.0
    expected_midpoint = expected_target_midpoint_pct(pre)
    return 100.0 * (realized_midpoint - expected_midpoint)


def future_path_shift_bps(pre: MeetingExpectation, post: MeetingExpectation) -> float:
    if pre.meeting_date != post.meeting_date:
        raise ValueError("MEETING_DATE_MISMATCH")
    return 100.0 * (expected_target_midpoint_pct(post) - expected_target_midpoint_pct(pre))


def future_path_vector_bps(
    pre_by_meeting: dict[str, MeetingExpectation],
    post_by_meeting: dict[str, MeetingExpectation],
) -> dict[str, float]:
    if not pre_by_meeting:
        raise ValueError("EMPTY_PRE_FUTURE_PATH")
    missing = sorted(set(pre_by_meeting) - set(post_by_meeting))
    if missing:
        raise ValueError(f"MISSING_POST_FUTURE_MEETINGS:{missing}")
    return {
        meeting: future_path_shift_bps(pre_by_meeting[meeting], post_by_meeting[meeting])
        for meeting in sorted(pre_by_meeting)
    }


def source_readiness_from_env(env: dict[str, str] | None = None) -> FomcSourceReadiness:
    e = os.environ if env is None else env
    url = bool(str(e.get("CME_FEDWATCH_API_URL", "")).strip())
    key = bool(str(e.get("CME_FEDWATCH_API_KEY", "")).strip())
    schema = bool(str(e.get("CME_FEDWATCH_SCHEMA_VERSION", "")).strip())
    configured = url and key and schema
    if not (url and key):
        status = "BLOCKED_CME_FEDWATCH_API_NOT_CONFIGURED"
    elif not schema:
        # Do not guess the licensed API JSON schema before a real sample/schema
        # from the subscribed CME Data Services account is available.
        status = "BLOCKED_CME_FEDWATCH_SCHEMA_NOT_PROVEN"
    else:
        # Configuration alone is not evidence of authenticated payload access.
        status = "CONFIG_PRESENT_ACCESS_NOT_YET_PROVEN"
    return FomcSourceReadiness(
        status=status,
        cme_api_configured=configured,
        cme_api_url_configured=url,
        cme_api_key_configured=key,
        cme_schema_contract_configured=schema,
        official_target_source="FEDERAL_RESERVE_FOMC_STATEMENT_AND_IMPLEMENTATION_NOTE",
        target_method="REALIZED_MIDPOINT_MINUS_PRE_RELEASE_CME_EXPECTED_MIDPOINT_BPS",
        path_method_state="BLOCKED_PATH_FACTOR_METHOD_NOT_FROZEN",
    )


def audit() -> dict[str, Any]:
    readiness = source_readiness_from_env()
    return {
        "engine_id": ENGINE_ID,
        "family": FAMILY,
        "status": readiness.status,
        "source_candidate": "CME_FEDWATCH_API",
        "source_basis": "30_DAY_FED_FUNDS_FUTURES_IMPLIED_FOMC_PROBABILITIES",
        "history_claimed_by_provider_from": 2015,
        "primary_window_minutes": PRIMARY_WINDOW_MINUTES,
        "readiness": asdict(readiness),
        "target_surprise_formula_frozen": True,
        "future_path_vector_formula_frozen": True,
        "scalar_path_factor_formula_frozen": False,
        "locked_2026_validation_authorized": False,
        "production_promotion": "BLOCKED_RESEARCH_CHALLENGER_ONLY",
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
