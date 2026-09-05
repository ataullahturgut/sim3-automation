from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import uuid
from datetime import datetime, time as dtime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
from psycopg.rows import dict_row

from macro_event_successor_v1_alfred_construction_audit import SERIES as ALFRED_SERIES
from macro_event_successor_v1_alfred_construction_audit import asof_values
from macro_event_successor_v1_investing_coverage_audit import EVENTS, fetch_event_history, month_range

ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "source_contract_macro_event_successor_v1.json"
PIPELINE_VERSION = "MACRO_EVENT_SUCCESSOR_V1_RESEARCH_DATA_PLANE_R1"
AUTH_TOKEN = "USER_AUTH_2026_09_05_INVESTING_DOCTORAL_RESEARCH"
EXPECTED_CONTRACT_VERSION = "MACRO_EVENT_SUCCESSOR_V1_SOURCE_CONTRACT_2026-09-05_R4"
START_REFERENCE = "2016-01"
END_REFERENCE = "2026-08"
EXPECTED_COMPLETE_MONTHS = 126
DECISION_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)
ACTUAL_IDS = {
    "nfp": "MACRO_NFP_ACTUAL_FIRST_PRINT",
    "unemployment": "MACRO_UNEMP_ACTUAL_FIRST_PRINT",
    "ahe_mom": "MACRO_AHE_ACTUAL_FIRST_PRINT",
}
CONSENSUS_IDS = {
    "nfp": "MACRO_NFP_CONSENSUS_PIT",
    "unemployment": "MACRO_UNEMP_CONSENSUS_PIT",
    "ahe_mom": "MACRO_AHE_CONSENSUS_PIT",
}
ALL_SERIES_IDS = tuple(ACTUAL_IDS.values()) + tuple(CONSENSUS_IDS.values())


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return value


def fred_api_key() -> str:
    value = os.environ.get("FRED_API_KEY", "").strip()
    if not value:
        raise RuntimeError("FRED_API_KEY_NOT_SET")
    return value


def require_authority() -> None:
    if os.environ.get("MACRO_RESEARCH_INGESTION_AUTHORIZED", "").strip() != AUTH_TOKEN:
        raise RuntimeError("MACRO_RESEARCH_INGESTION_NOT_AUTHORIZED")
    if os.environ.get("GITHUB_REF_NAME", "").strip() not in {
        "gold-control-macro-event-successor-v1-source-contract",
        "gold-r4-direction-engine",
    }:
        raise RuntimeError("MACRO_RESEARCH_INGESTION_BRANCH_NOT_AUTHORIZED")


def git_sha() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        return os.environ.get("GITHUB_SHA")


def load_contract() -> dict:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if payload.get("version") != EXPECTED_CONTRACT_VERSION:
        raise RuntimeError(f"MACRO_SOURCE_CONTRACT_VERSION_MISMATCH:{payload.get('version')}")
    if payload.get("source_data_plane_writes") is not True:
        raise RuntimeError("MACRO_SOURCE_DATA_PLANE_NOT_AUTHORIZED_IN_CONTRACT")
    if payload.get("authority_store_writes") is not False:
        raise RuntimeError("MACRO_AUTHORITY_STORE_WRITE_LOCK_MISSING")
    if payload.get("model_score_authorized") is not False:
        raise RuntimeError("MACRO_MODEL_SCORE_LOCK_MISSING")
    if payload.get("direction_vote") is not False:
        raise RuntimeError("MACRO_DIRECTION_VOTE_LOCK_MISSING")
    coverage = payload.get("coverage_contract") or {}
    if coverage.get("audit_status") != "PASS_COVERAGE_RESEARCH_DATASET_ELIGIBLE":
        raise RuntimeError("MACRO_INVESTING_COVERAGE_NOT_PASS")
    if int(coverage.get("expected_complete_case_months_before_actual_quality_checks", -1)) != EXPECTED_COMPLETE_MONTHS:
        raise RuntimeError("MACRO_EXPECTED_COMPLETE_CASE_COUNT_MISMATCH")
    for sid in ALL_SERIES_IDS:
        if sid not in (payload.get("series") or {}):
            raise RuntimeError(f"MACRO_SOURCE_SERIES_MISSING:{sid}")
    return payload


def stable_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def release_ts_utc(release_date) -> datetime:
    local = datetime.combine(release_date, dtime(8, 30), tzinfo=ZoneInfo("America/New_York"))
    return local.astimezone(timezone.utc)


def ref_dates(reference_month: str) -> tuple[str, str]:
    y, m = map(int, reference_month.split("-"))
    ref = f"{y:04d}-{m:02d}-01"
    if m == 1:
        prev = f"{y-1:04d}-12-01"
    else:
        prev = f"{y:04d}-{m-1:02d}-01"
    return ref, prev


def alfred_retry(session, key: str, series_id: str, asof: str, start: str, end: str) -> dict[str, float]:
    last = None
    for attempt in range(5):
        try:
            return asof_values(session, key, series_id, asof, start, end)
        except Exception as exc:
            last = exc
            if attempt == 4:
                break
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"ALFRED_RETRY_EXHAUSTED:{series_id}:{asof}:{last}")


def fetch_investing_complete_panel() -> tuple[dict[str, dict], dict[str, dict]]:
    expected = month_range(START_REFERENCE, END_REFERENCE)
    rows_by_event: dict[str, dict] = {}
    meta_by_event: dict[str, dict] = {}
    for key, spec in EVENTS.items():
        rows, meta = fetch_event_history(spec["event_attr_id"], START_REFERENCE, END_REFERENCE)
        rows_by_event[key] = {row.reference_month: row for row in rows}
        meta_by_event[key] = meta
        if meta.get("endpoint_status") != "PASS_ENDPOINT_ACCESS":
            raise RuntimeError(f"INVESTING_ENDPOINT_NOT_PASS:{key}:{meta}")
        time.sleep(7.0)

    complete: dict[str, dict] = {}
    for month in expected:
        candidates = {k: rows_by_event[k].get(month) for k in EVENTS}
        if any(v is None or v.forecast is None for v in candidates.values()):
            continue
        release_dates = {v.release_date for v in candidates.values()}
        if len(release_dates) != 1:
            raise RuntimeError(f"INVESTING_EVENT_RELEASE_DATE_MISMATCH:{month}:{sorted(map(str, release_dates))}")
        complete[month] = candidates

    if len(complete) != EXPECTED_COMPLETE_MONTHS:
        raise RuntimeError(f"INVESTING_COMPLETE_CASE_COUNT:{len(complete)}/{EXPECTED_COMPLETE_MONTHS}")
    excluded = sorted(set(expected) - set(complete))
    if excluded != ["2020-08", "2025-10"]:
        raise RuntimeError(f"INVESTING_COMPLETE_CASE_EXCLUSION_DRIFT:{excluded}")
    return complete, meta_by_event


def build_actuals(complete: dict[str, dict]) -> tuple[dict[str, dict], list[str]]:
    import requests

    session = requests.Session()
    key = fred_api_key()
    actuals: dict[str, dict] = {}
    failures: list[str] = []
    for i, month in enumerate(sorted(complete), start=1):
        release_date = complete[month]["nfp"].release_date
        asof = release_date.isoformat()
        ref, prev = ref_dates(month)
        try:
            payems = alfred_retry(session, key, ALFRED_SERIES["nfp_level"], asof, prev, ref)
            unrate = alfred_retry(session, key, ALFRED_SERIES["unemployment_rate"], asof, ref, ref)
            ahe = alfred_retry(session, key, ALFRED_SERIES["ahe_level"], asof, prev, ref)
            if ref not in payems or prev not in payems or ref not in unrate or ref not in ahe or prev not in ahe:
                raise RuntimeError("REQUIRED_ASOF_VALUE_MISSING")
            actuals[month] = {
                "nfp": float(payems[ref] - payems[prev]),
                "unemployment": float(unrate[ref]),
                "ahe_mom": float(round((ahe[ref] / ahe[prev] - 1.0) * 100.0, 1)),
            }
        except Exception as exc:
            failures.append(f"{month}:{type(exc).__name__}:{exc}")
        if i % 10 == 0:
            time.sleep(0.4)

    if failures:
        raise RuntimeError(f"ALFRED_ACTUAL_RECONSTRUCTION_FAILURES:{len(failures)}:{failures[:5]}")
    if len(actuals) != EXPECTED_COMPLETE_MONTHS:
        raise RuntimeError(f"ALFRED_COMPLETE_ACTUAL_COUNT:{len(actuals)}/{EXPECTED_COMPLETE_MONTHS}")
    return actuals, failures


def source_registry_tuple(series_id: str, spec: dict) -> tuple:
    metadata = {k: v for k, v in spec.items() if k not in {
        "semantic", "source", "symbol", "tier", "frequency", "unit", "role", "status", "license_note"
    }}
    return (
        series_id,
        spec["semantic"],
        spec["source"],
        spec.get("symbol"),
        spec["tier"],
        spec["frequency"],
        spec.get("unit"),
        spec.get("role"),
        spec["status"],
        spec.get("license_note"),
        json.dumps(metadata, sort_keys=True),
    )


def decision_counts(conn) -> dict[str, int]:
    out = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for table in DECISION_TABLES:
            cur.execute(f"select count(*)::bigint as n from {table}")
            out[table] = int(cur.fetchone()["n"])
    return out


def latest_map(conn) -> dict:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select distinct on (series_id, observation_ts, lineage_id)
                   series_id, observation_ts, lineage_id, value, quality_status, first_seen_at
            from observations
            where series_id = any(%s)
            order by series_id, observation_ts, lineage_id, retrieved_at desc
            """,
            (list(ALL_SERIES_IDS),),
        )
        return {
            (row["series_id"], row["observation_ts"].isoformat(), row["lineage_id"]): row
            for row in cur.fetchall()
        }


def build_observations(contract: dict, complete: dict[str, dict], actuals: dict[str, dict], run_id: str, retrieved_at: datetime) -> list[dict]:
    specs = contract["series"]
    out: list[dict] = []
    for month in sorted(complete):
        release_date = complete[month]["nfp"].release_date
        release_ts = release_ts_utc(release_date)
        release_iso = release_ts.isoformat()

        for key, series_id in ACTUAL_IDS.items():
            spec = specs[series_id]
            normalized = {
                "provider": "ALFRED_BLS_RELEASE_DATE_RECONSTRUCTION",
                "series_id": series_id,
                "reference_month": month,
                "release_date": release_date.isoformat(),
                "value": actuals[month][key],
            }
            lineage = stable_hash({k: v for k, v in normalized.items() if k != "value"})[:20]
            out.append({
                "run_id": run_id,
                "series_id": series_id,
                "observation_ts": release_ts,
                "value": actuals[month][key],
                "source": spec["source"],
                "source_symbol": spec.get("symbol"),
                "provider_as_of": release_ts,
                "available_as_of": release_ts,
                "first_seen_at": retrieved_at,
                "retrieved_at": retrieved_at,
                "frequency": spec["frequency"],
                "unit": spec.get("unit"),
                "transform": "RELEASE_VALUE",
                "quality_status": spec["status"],
                "lineage_id": lineage,
                "payload_hash": stable_hash(normalized),
                "metadata": {
                    "reference_month": month,
                    "release_date": release_date.isoformat(),
                    "official_release_time_rule": "08:30 America/New_York",
                    "historical_reconstruction_not_original_retrieval": True,
                    "current_vintage_substitution": False,
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                    "construction_method": "ALFRED_ASOF_RELEASE_DATE_LEVELS",
                    "model_score_run": False,
                    "direction_vote": False,
                },
            })

        for key, series_id in CONSENSUS_IDS.items():
            spec = specs[series_id]
            event = complete[month][key]
            forecast = float(event.forecast)
            normalized = {
                "provider": "Investing.com Economic Calendar",
                "event_attr_id": EVENTS[key]["event_attr_id"],
                "field": "Forecast",
                "series_id": series_id,
                "reference_month": month,
                "release_date": release_date.isoformat(),
                "value": forecast,
            }
            lineage = stable_hash({k: v for k, v in normalized.items() if k != "value"})[:20]
            out.append({
                "run_id": run_id,
                "series_id": series_id,
                "observation_ts": release_ts,
                "value": forecast,
                "source": spec["source"],
                "source_symbol": spec.get("symbol"),
                "provider_as_of": release_ts,
                "available_as_of": release_ts,
                "first_seen_at": retrieved_at,
                "retrieved_at": retrieved_at,
                "frequency": spec["frequency"],
                "unit": spec.get("unit"),
                "transform": "RELEASE_CONSENSUS",
                "quality_status": spec["status"],
                "lineage_id": lineage,
                "payload_hash": stable_hash(normalized),
                "metadata": {
                    "reference_month": month,
                    "release_date": release_date.isoformat(),
                    "official_release_time_rule": "08:30 America/New_York",
                    "provider_field": "Forecast",
                    "investing_event_attr_id": EVENTS[key]["event_attr_id"],
                    "provider_exact_pre_release_update_timestamp_proven": False,
                    "availability_policy": "NO_EARLIER_THAN_OFFICIAL_BLS_RELEASE_TIMESTAMP",
                    "historical_reconstruction_not_original_retrieval": True,
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                    "provider_scope": "DOCTORAL_RESEARCH_INTERNAL_USER_ACCEPTED_LICENSE_RISK",
                    "no_redistribution": True,
                    "model_score_run": False,
                    "direction_vote": False,
                },
            })
    if len(out) != EXPECTED_COMPLETE_MONTHS * 6:
        raise RuntimeError(f"MACRO_OBSERVATION_BUNDLE_COUNT:{len(out)}/{EXPECTED_COMPLETE_MONTHS * 6}")
    return out


def persist(contract: dict, observations: list[dict], investing_meta: dict) -> dict:
    started_at = min(o["retrieved_at"] for o in observations)
    finished_at = datetime.now(timezone.utc)
    run_id = observations[0]["run_id"]
    code_sha = git_sha()

    with psycopg.connect(db_url(), autocommit=False) as conn:
        before = decision_counts(conn)
        if any(before.values()):
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_NOT_EMPTY_BEFORE_MACRO_SOURCE_INGEST:{before}")

        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into source_registry
                (series_id, semantic_id, source_name, source_symbol, source_tier, frequency,
                 unit, model_role, status, license_note, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                on conflict (series_id) do update set
                  semantic_id=excluded.semantic_id,
                  source_name=excluded.source_name,
                  source_symbol=excluded.source_symbol,
                  source_tier=excluded.source_tier,
                  frequency=excluded.frequency,
                  unit=excluded.unit,
                  model_role=excluded.model_role,
                  status=excluded.status,
                  license_note=excluded.license_note,
                  metadata=excluded.metadata,
                  updated_at=now()
                """,
                [source_registry_tuple(sid, contract["series"][sid]) for sid in ALL_SERIES_IDS],
            )

        prior = latest_map(conn)
        to_insert = []
        for row in observations:
            key = (row["series_id"], row["observation_ts"].isoformat(), row["lineage_id"])
            previous = prior.get(key)
            if previous is None:
                to_insert.append(row)
                continue
            same = float(previous["value"]) == float(row["value"]) and str(previous["quality_status"]) == str(row["quality_status"])
            if same:
                continue
            raise RuntimeError(f"FROZEN_MACRO_RESEARCH_OBSERVATION_CHANGED:{row['series_id']}:{row['metadata']['reference_month']}")

        with conn.cursor() as cur:
            cur.execute(
                """
                insert into retrieval_runs
                (run_id, started_at, finished_at, pipeline_version, git_sha, trigger_type,
                 status, observations_read, observations_written, notes, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                """,
                (
                    run_id, started_at, finished_at, PIPELINE_VERSION, code_sha,
                    "macro_event_successor_v1_research_source_ingestion", "SUCCESS",
                    len(observations), len(to_insert),
                    "Investing.com doctoral-research consensus + ALFRED/BLS first-print reconstruction; no model score",
                    json.dumps({
                        "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
                        "contract_version": EXPECTED_CONTRACT_VERSION,
                        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                        "complete_case_months": EXPECTED_COMPLETE_MONTHS,
                        "known_excluded_reference_months": ["2020-08", "2025-10"],
                        "provider_scope": "DOCTORAL_RESEARCH_INTERNAL_USER_ACCEPTED_LICENSE_RISK",
                        "investing_page_hash_chains": {k: v.get("page_hash_chain") for k, v in investing_meta.items()},
                        "raw_investing_payload_stored": False,
                        "model_score_run": False,
                        "direction_vote": False,
                        "forecast_or_decision_write": False,
                    }, sort_keys=True),
                ),
            )
            if to_insert:
                cur.executemany(
                    """
                    insert into observations
                    (run_id, series_id, observation_ts, value, source, source_symbol,
                     provider_as_of, available_as_of, first_seen_at, retrieved_at,
                     frequency, unit, transform, quality_status, lineage_id, payload_hash, metadata)
                    values
                    (%(run_id)s, %(series_id)s, %(observation_ts)s, %(value)s, %(source)s, %(source_symbol)s,
                     %(provider_as_of)s, %(available_as_of)s, %(first_seen_at)s, %(retrieved_at)s,
                     %(frequency)s, %(unit)s, %(transform)s, %(quality_status)s, %(lineage_id)s,
                     %(payload_hash)s, %(metadata)s::jsonb)
                    """,
                    [{**o, "metadata": json.dumps(o["metadata"], sort_keys=True)} for o in to_insert],
                )

        after = decision_counts(conn)
        if after != before:
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED_DURING_MACRO_SOURCE_INGEST:{before}->{after}")

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select series_id, count(*)::bigint as rows,
                       count(distinct metadata->>'reference_month')::bigint as reference_months,
                       min(metadata->>'reference_month') as first_reference_month,
                       max(metadata->>'reference_month') as last_reference_month
                from observations
                where series_id = any(%s)
                group by series_id
                order by series_id
                """,
                (list(ALL_SERIES_IDS),),
            )
            coverage = [dict(x) for x in cur.fetchall()]
        if len(coverage) != 6 or any(int(x["reference_months"]) != EXPECTED_COMPLETE_MONTHS for x in coverage):
            raise RuntimeError(f"MACRO_PRODUCTION_RESEARCH_COVERAGE_INVALID:{coverage}")
        conn.commit()

    return {
        "status": "SUCCESS",
        "run_id": run_id,
        "observations_read": len(observations),
        "observations_written": len(to_insert),
        "complete_case_months": EXPECTED_COMPLETE_MONTHS,
        "series_count": 6,
        "coverage": coverage,
        "decision_counts_before": before,
        "decision_counts_after": after,
        "raw_investing_payload_stored": False,
        "model_score_run": False,
        "direction_vote": False,
        "forecast_or_decision_write": False,
    }


def main() -> int:
    require_authority()
    contract = load_contract()
    started = datetime.now(timezone.utc)
    complete, investing_meta = fetch_investing_complete_panel()
    actuals, _ = build_actuals(complete)
    run_id = str(uuid.uuid4())
    observations = build_observations(contract, complete, actuals, run_id, started)
    result = persist(contract, observations, investing_meta)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
