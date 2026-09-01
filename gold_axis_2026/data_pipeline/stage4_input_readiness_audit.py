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
    cur.execute("SELECT to_regclass(%s) AS object_name", (f"public.{name}",))
    object_row = cur.fetchone()
    if object_row is None or object_row["object_name"] is None:
        return -1
    cur.execute(f'SELECT count(*) AS n FROM "{name}"')
    count_row = cur.fetchone()
    if count_row is None:
        raise RuntimeError(f"COUNT_RETURNED_NO_ROW:{name}")
    return int(count_row["n"])


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
            (array_agg(source ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_upstream_source,
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
        xau_spot = series["XAU_SPOT_XAUS"]
        if int(xau_daily.get("n") or 0) < 25:
            blockers.append("XAU_DAILY_INSUFFICIENT_FOR_FAST")

        # XAUS is the transport/series identity. The payload may disclose an upstream
        # provider (currently Yahoo for history / another provider for spot). That is
        # provenance, not by itself a silent transport substitution. The production
        # issue is authority: the frozen registry explicitly classifies daily XAU as
        # an operational cross-check and spot as indicative/non-settlement.
        daily_role = str(xau_daily.get("model_role") or "").lower()
        daily_status = str(xau_daily.get("status") or "").upper()
        spot_status = str(xau_spot.get("status") or "").upper()
        spot_quality = str(xau_spot.get("latest_quality_status") or "").upper()
        daily_authorized = daily_status == "APPROVED" and "cross-check" not in daily_role
        spot_authorized = (
            spot_status == "APPROVED"
            and "INDICATIVE" not in spot_quality
            and "NOT_SETTLEMENT" not in spot_quality
        )
        if not daily_authorized and not spot_authorized:
            blockers.append("NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE")

        daily_upstream = str(xau_daily.get("latest_upstream_source") or "").lower()
        daily_contract = str(xau_daily.get("source_name") or "").lower()
        if "yahoo" in daily_upstream and "yahoo" not in daily_contract:
            warnings.append("XAU_DAILY_UPSTREAM_PROVIDER_NOT_DOCUMENTED_IN_REGISTRY")

        spot_upstream = str(xau_spot.get("latest_upstream_source") or "").strip()
        if spot_upstream:
            warnings.append("XAU_SPOT_UPSTREAM_PROVIDER_DISCLOSED_INDICATIVE_ONLY")

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
