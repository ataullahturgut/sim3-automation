from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg
from psycopg.rows import dict_row

ENGINE_ID = "MACRO_EVENT_SUCCESSOR_V3"
EVIDENCE_CLASS = "RESEARCH_CHALLENGER_SOURCE_READINESS"

EMPLOYMENT_SERIES = (
    "MACRO_NFP_ACTUAL_FIRST_PRINT",
    "MACRO_NFP_CONSENSUS_PIT",
    "MACRO_UNEMP_ACTUAL_FIRST_PRINT",
    "MACRO_UNEMP_CONSENSUS_PIT",
    "MACRO_AHE_ACTUAL_FIRST_PRINT",
    "MACRO_AHE_CONSENSUS_PIT",
)
EMPLOYMENT_CONSENSUS = (
    "MACRO_NFP_CONSENSUS_PIT",
    "MACRO_UNEMP_CONSENSUS_PIT",
    "MACRO_AHE_CONSENSUS_PIT",
)

# These identities are preregistered V3 contracts. They are deliberately not
# substituted with nearby series if absent.
INFLATION_SERIES = (
    "MACRO_CPI_ACTUAL_FIRST_PRINT",
    "MACRO_CPI_CONSENSUS_PIT",
    "MACRO_CORE_CPI_ACTUAL_FIRST_PRINT",
    "MACRO_CORE_CPI_CONSENSUS_PIT",
)
FOMC_SERIES = (
    "MACRO_FOMC_TARGET_SURPRISE_PIT",
    "MACRO_FOMC_PATH_SURPRISE_PIT",
)

PRIMARY_WINDOW_MINUTES = 10
DIAGNOSTIC_WINDOW_MINUTES = 30


@dataclass(frozen=True)
class FamilyReadiness:
    family: str
    status: str
    required_series: tuple[str, ...]
    present_series: tuple[str, ...]
    missing_series: tuple[str, ...]
    details: dict[str, Any]


@dataclass(frozen=True)
class MacroFamilySignal:
    family: str
    official_release_at: datetime
    pit_ready: bool
    strong: bool
    surprise_score: float | None = None
    direction_context: str | None = None


@dataclass(frozen=True)
class MarketShockEpisode:
    started_at: datetime
    ended_at: datetime


@dataclass(frozen=True)
class MacroMatchResult:
    state: str
    macro_match: bool
    macro_family: str | None
    macro_strength: str | None
    macro_release_ts: str | None
    macro_surprise_score: float | None
    macro_direction_context: str | None
    raw_market_shock_preserved: bool = True


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return value


def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return dt.astimezone(timezone.utc)


def _series_inventory(conn, series_ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select sr.series_id,
                   sr.source_name,
                   sr.source_tier,
                   sr.status as registry_status,
                   count(o.id)::bigint as observation_count,
                   count(o.id) filter (where o.available_as_of is null)::bigint as missing_available_as_of,
                   count(o.id) filter (where o.lineage_id is null or o.lineage_id='')::bigint as missing_lineage,
                   count(o.id) filter (
                       where coalesce(o.metadata->>'provider_exact_pre_release_update_timestamp_proven','')='true'
                   )::bigint as provider_pre_release_timestamp_proven_count
            from source_registry sr
            left join observations o on o.series_id=sr.series_id
            where sr.series_id=any(%s)
            group by sr.series_id, sr.source_name, sr.source_tier, sr.status
            order by sr.series_id
            """,
            (list(series_ids),),
        )
        return {str(r["series_id"]): dict(r) for r in cur.fetchall()}


def audit_employment(conn) -> FamilyReadiness:
    inv = _series_inventory(conn, EMPLOYMENT_SERIES)
    present = tuple(sorted(inv))
    missing = tuple(s for s in EMPLOYMENT_SERIES if s not in inv)
    if missing:
        return FamilyReadiness(
            "EMPLOYMENT",
            "BLOCKED_SOURCE_NOT_ESTABLISHED",
            EMPLOYMENT_SERIES,
            present,
            missing,
            {"inventory": inv},
        )

    bad_availability = [s for s in EMPLOYMENT_SERIES if int(inv[s]["missing_available_as_of"]) > 0]
    bad_lineage = [s for s in EMPLOYMENT_SERIES if int(inv[s]["missing_lineage"]) > 0]
    if bad_availability or bad_lineage:
        return FamilyReadiness(
            "EMPLOYMENT",
            "BLOCKED_LINEAGE_OR_AVAILABILITY",
            EMPLOYMENT_SERIES,
            present,
            (),
            {
                "bad_availability": bad_availability,
                "bad_lineage": bad_lineage,
                "inventory": inv,
            },
        )

    # Exact V3 invariant: historical calendar consensus is not promoted to PIT
    # merely because available_as_of was reconstructed as release time.
    not_provider_proven = [
        s for s in EMPLOYMENT_CONSENSUS
        if int(inv[s]["provider_pre_release_timestamp_proven_count"]) < int(inv[s]["observation_count"])
    ]
    if not_provider_proven:
        return FamilyReadiness(
            "EMPLOYMENT",
            "BLOCKED_PIT_CONSENSUS_PROOF",
            EMPLOYMENT_SERIES,
            present,
            (),
            {
                "consensus_series_without_full_provider_pre_release_timestamp_proof": not_provider_proven,
                "inventory": inv,
            },
        )

    return FamilyReadiness(
        "EMPLOYMENT",
        "PASS_SOURCE_AND_PIT_READY",
        EMPLOYMENT_SERIES,
        present,
        (),
        {"inventory": inv},
    )


def audit_inflation(conn) -> FamilyReadiness:
    inv = _series_inventory(conn, INFLATION_SERIES)
    present = tuple(sorted(inv))
    missing = tuple(s for s in INFLATION_SERIES if s not in inv)
    if missing:
        return FamilyReadiness(
            "INFLATION",
            "BLOCKED_SOURCE_NOT_ESTABLISHED",
            INFLATION_SERIES,
            present,
            missing,
            {"inventory": inv},
        )
    return FamilyReadiness(
        "INFLATION",
        "BLOCKED_PENDING_FAMILY_PIT_AND_THRESHOLD_VALIDATION",
        INFLATION_SERIES,
        present,
        (),
        {"inventory": inv},
    )


def audit_fomc(conn) -> FamilyReadiness:
    inv = _series_inventory(conn, FOMC_SERIES)
    present = tuple(sorted(inv))
    missing = tuple(s for s in FOMC_SERIES if s not in inv)
    if missing:
        return FamilyReadiness(
            "FOMC",
            "BLOCKED_EXPECTATION_SOURCE",
            FOMC_SERIES,
            present,
            missing,
            {
                "required_method": "PIT_MARKET_IMPLIED_TARGET_AND_PATH_SURPRISE",
                "inventory": inv,
            },
        )
    return FamilyReadiness(
        "FOMC",
        "BLOCKED_PENDING_TARGET_PATH_VALIDATION",
        FOMC_SERIES,
        present,
        (),
        {"inventory": inv},
    )


def match_market_shock(episode: MarketShockEpisode, signal: MacroFamilySignal | None) -> MacroMatchResult:
    """Context-only match. Never deletes/suppresses the raw Market Shock episode."""
    if signal is None:
        return MacroMatchResult(
            state="NO_MACRO_EXPLANATION",
            macro_match=False,
            macro_family=None,
            macro_strength=None,
            macro_release_ts=None,
            macro_surprise_score=None,
            macro_direction_context=None,
        )

    start = _utc(episode.started_at)
    release = _utc(signal.official_release_at)

    if start < release:
        state = "PRE_RELEASE_SHOCK"
        matched = False
        strength = "STRONG" if signal.strong else "NOT_STRONG"
    elif not signal.pit_ready:
        state = "MACRO_DATA_NOT_PIT_READY"
        matched = False
        strength = "STRONG" if signal.strong else "NOT_STRONG"
    elif start <= release + timedelta(minutes=PRIMARY_WINDOW_MINUTES):
        if signal.strong:
            state = "MACRO_CONFIRMED"
            matched = True
            strength = "STRONG"
        else:
            state = "MACRO_EVENT_PRESENT_BUT_NOT_STRONG"
            matched = False
            strength = "NOT_STRONG"
    else:
        # Even if inside the diagnostic +30m window, this is not primary confirmation.
        state = "NO_MACRO_EXPLANATION"
        matched = False
        strength = "STRONG" if signal.strong else "NOT_STRONG"

    return MacroMatchResult(
        state=state,
        macro_match=matched,
        macro_family=signal.family,
        macro_strength=strength,
        macro_release_ts=release.isoformat(),
        macro_surprise_score=signal.surprise_score,
        macro_direction_context=signal.direction_context,
    )


def audit(conn) -> dict[str, Any]:
    families = [audit_employment(conn), audit_inflation(conn), audit_fomc(conn)]
    all_pass = all(f.status == "PASS_SOURCE_AND_PIT_READY" for f in families)
    return {
        "engine_id": ENGINE_ID,
        "status": "PASS_SOURCE_READINESS" if all_pass else "BLOCKED_SOURCE_READINESS",
        "evidence_class": EVIDENCE_CLASS,
        "scope": ["EMPLOYMENT", "INFLATION", "FOMC"],
        "market_shock_role": "CONTEXT_ONLY_NOT_HARD_GATE",
        "primary_match_window_minutes": PRIMARY_WINDOW_MINUTES,
        "diagnostic_window_minutes": DIAGNOSTIC_WINDOW_MINUTES,
        "raw_market_shock_episode_deletion_permitted": False,
        "families": [asdict(f) for f in families],
        "production_promotion": "BLOCKED_RESEARCH_CHALLENGER_ONLY",
    }


def main() -> int:
    with psycopg.connect(db_url()) as conn:
        report = audit(conn)
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    # Source blockers are scientific/governance results, not CI execution errors.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
