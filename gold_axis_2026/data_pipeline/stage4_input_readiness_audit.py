from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

import psycopg
from psycopg.rows import dict_row


SERIES = ("XAU_SPOT_XAUS", "XAU_DAILY_XAUS", "GVZ_CBOE")
FORECAST_TABLES = (
    "forecast_input_snapshots",
    "derived_feature_snapshots",
    "monthly_forecast_contracts",
)
DECISION_TABLES = ("decision_runs", "decision_signal_snapshots", "decision_events")


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _table_count(cur, name: str) -> int:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    if cur.fetchone()[0] is None:
        return -1
    cur.execute(f'SELECT count(*) FROM "{name}"')
    return int(cur.fetchone()[0])


def _series_meta(cur, series_id: str) -> dict[str, Any]:
    cur.execute(
        """
        SELECT series_id, source_name, source_symbol, source_tier, frequency,
               model_role, status, license_note
        FROM source_registry
        WHERE series_id=%s
        """,
        (series_id,),
    )
    registry = cur.fetchone()

    cur.execute(
        """
        SELECT
            count(*) AS n,
            min(observation_ts) AS first_observation_ts,
            max(observation_ts) AS last_observation_ts,
            max(retrieved_at) AS last_retrieval_ts,
            count(DISTINCT lineage_id) AS lineage_count,
            (array_agg(source ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_source,
            (array_agg(source_symbol ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_source_symbol,
            (array_agg(quality_status ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_quality_status,
            (array_agg(lineage_id ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_lineage_id
        FROM usable_observations
        WHERE series_id=%s
        """,
        (series_id,),
    )
    obs = cur.fetchone()

    out: dict[str, Any] = {"series_id": series_id}
    if registry:
        out.update({k: _jsonable(v) for k, v in registry.items()})
    else:
        out["registry_status"] = "NOT_FOUND"
    if obs:
        out.update({k: _jsonable(v) for k, v in obs.items()})
    return out


def _latest_run(cur, trigger_type: str) -> dict[str, Any] | None:
    cur.execute(
        """
        SELECT trigger_type, status, started_at, finished_at, pipeline_version, git_sha,
               observations_read, observations_written
        FROM retrieval_runs
        WHERE trigger_type=%s
        ORDER BY COALESCE(finished_at, started_at) DESC
        LIMIT 1
        """,
        (trigger_type,),
    )
    row = cur.fetchone()
    return None if row is None else {k: _jsonable(v) for k, v in row.items()}


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("STAGE4_INPUT_READINESS_AUDIT_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    try:
        with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")

                forecast_counts = {name: _table_count(cur, name) for name in FORECAST_TABLES}
                decision_counts = {name: _table_count(cur, name) for name in DECISION_TABLES}
                series = {sid: _series_meta(cur, sid) for sid in SERIES}
                runs = {
                    "hourly:xau": _latest_run(cur, "hourly:xau"),
                    "daily:xau": _latest_run(cur, "daily:xau"),
                    "daily:cboe": _latest_run(cur, "daily:cboe"),
                }
            conn.rollback()

        blockers: list[str] = []
        warnings: list[str] = []

        if forecast_counts.get("monthly_forecast_contracts", 0) <= 0:
            blockers.append("FORECAST_CONTRACT_NOT_ISSUED")
        if forecast_counts.get("forecast_input_snapshots", 0) <= 0:
            blockers.append("IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED")

        xau_daily = series["XAU_DAILY_XAUS"]
        if int(xau_daily.get("n") or 0) < 25:
            blockers.append("XAU_DAILY_INSUFFICIENT_FOR_FAST")
        contract_source = str(xau_daily.get("source_name") or "").lower()
        actual_source = str(xau_daily.get("latest_source") or "").lower()
        if contract_source and actual_source and contract_source not in actual_source and actual_source not in contract_source:
            blockers.append("XAU_DAILY_PERSISTED_SOURCE_DIFFERS_FROM_CONTRACT")

        xau_spot = series["XAU_SPOT_XAUS"]
        spot_contract = str(xau_spot.get("source_name") or "").lower()
        spot_actual = str(xau_spot.get("latest_source") or "").lower()
        if spot_contract and spot_actual and spot_contract not in spot_actual and spot_actual not in spot_contract:
            warnings.append("XAU_SPOT_PERSISTED_SOURCE_DIFFERS_FROM_CONTRACT")

        if runs.get("daily:xau") and runs["daily:xau"].get("status") != "SUCCESS":
            blockers.append("LATEST_DAILY_XAU_PIPELINE_NOT_SUCCESS")
        if runs.get("hourly:xau") and runs["hourly:xau"].get("status") != "SUCCESS":
            warnings.append("LATEST_HOURLY_XAU_PIPELINE_NOT_SUCCESS")
        if runs.get("daily:cboe") and runs["daily:cboe"].get("status") != "SUCCESS":
            blockers.append("LATEST_CBOE_PIPELINE_NOT_SUCCESS")

        if int(series["GVZ_CBOE"].get("n") or 0) <= 0:
            blockers.append("GVZ_NOT_AVAILABLE")

        if any(v != 0 for v in decision_counts.values() if v >= 0):
            warnings.append("DECISION_STORE_ALREADY_NONEMPTY_REVIEW_BEFORE_FIRST_PROSPECTIVE_ISSUANCE")

        readiness = "BLOCKED" if blockers else "READY_FOR_ISSUER_INTEGRATION"
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "read_only": True,
            "raw_market_values_logged": False,
            "forecast_store_counts": forecast_counts,
            "decision_store_counts": decision_counts,
            "series_metadata": series,
            "latest_pipeline_runs": runs,
            "blockers": sorted(set(blockers)),
            "warnings": sorted(set(warnings)),
            "stage4_readiness": readiness,
        }
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        print(
            "STAGE4_INPUT_READINESS_AUDIT_PASS "
            f"readiness={readiness} blockers={','.join(sorted(set(blockers))) or 'NONE'} "
            f"warnings={','.join(sorted(set(warnings))) or 'NONE'} raw_market_values_logged=NO"
        )
        return 0
    except Exception as exc:
        print(f"STAGE4_INPUT_READINESS_AUDIT_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
