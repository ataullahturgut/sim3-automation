from __future__ import annotations

import json
import os

import psycopg
from psycopg.rows import dict_row

REQUIRED_SERIES = [
    "XAU_SPOT_XAUS",
    "XAU_DAILY_XAUS",
    "GVZ_CBOE",
    "VIX_CBOE",
    "DGS10_FRB_H15",
    "DEXCHUS_FRB_H10",
    "DTWEXBGS_FRB_H10",
    "EFFR_NYFED",
    "GPR_OFFICIAL",
    "GPRT_OFFICIAL",
    "GPRA_OFFICIAL",
]

DIRECT_FED_SERIES = [
    "DGS10_FRB_H15",
    "DEXCHUS_FRB_H10",
    "DTWEXBGS_FRB_H10",
    "EFFR_NYFED",
]


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def main() -> int:
    report: dict = {}
    with psycopg.connect(db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select series_id,
                       count(*)::bigint as canonical_rows,
                       max(observation_ts) as latest_observation_ts,
                       max(retrieved_at) as latest_retrieved_at,
                       count(*) filter (where available_as_of is null)::bigint as null_available_as_of
                from canonical_latest
                where series_id = any(%s)
                group by series_id
                order by series_id
                """,
                (REQUIRED_SERIES,),
            )
            rows = cur.fetchall()
            by_series = {row["series_id"]: row for row in rows}
            missing = sorted(set(REQUIRED_SERIES) - set(by_series))
            if missing:
                raise AssertionError(f"NEON_REQUIRED_SERIES_MISSING:{missing}")

            null_availability = {
                sid: int(row["null_available_as_of"])
                for sid, row in by_series.items()
                if int(row["null_available_as_of"]) != 0
            }
            if null_availability:
                raise AssertionError(f"NEON_NULL_AVAILABLE_AS_OF:{null_availability}")

            cur.execute(
                """
                select series_id, semantic_id, source_name, source_symbol, source_tier, status
                from source_registry
                where series_id = any(%s)
                order by series_id
                """,
                (DIRECT_FED_SERIES,),
            )
            registry = cur.fetchall()
            registry_ids = {row["series_id"] for row in registry}
            registry_missing = sorted(set(DIRECT_FED_SERIES) - registry_ids)
            if registry_missing:
                raise AssertionError(f"NEON_DIRECT_FED_REGISTRY_MISSING:{registry_missing}")

            cur.execute(
                """
                select distinct on (trigger_type)
                       trigger_type, status, observations_read, observations_written, finished_at, pipeline_version, git_sha
                from retrieval_runs
                where trigger_type in ('daily:xau','daily:cboe','daily:fed','daily:gpr')
                order by trigger_type, finished_at desc nulls last
                """
            )
            latest_runs = cur.fetchall()
            run_map = {row["trigger_type"]: row for row in latest_runs}
            required_runs = {"daily:xau", "daily:cboe", "daily:fed", "daily:gpr"}
            missing_runs = sorted(required_runs - set(run_map))
            if missing_runs:
                raise AssertionError(f"NEON_LATEST_RUN_MISSING:{missing_runs}")
            bad_runs = {
                key: row["status"] for key, row in run_map.items() if row["status"] != "SUCCESS"
            }
            if bad_runs:
                raise AssertionError(f"NEON_LATEST_RUN_NOT_SUCCESS:{bad_runs}")

    report["status"] = "PASS"
    report["required_series"] = {
        sid: {
            "canonical_rows": int(by_series[sid]["canonical_rows"]),
            "latest_observation_ts": by_series[sid]["latest_observation_ts"].isoformat(),
            "latest_retrieved_at": by_series[sid]["latest_retrieved_at"].isoformat(),
        }
        for sid in REQUIRED_SERIES
    }
    report["direct_fed_registry"] = [dict(row) for row in registry]
    report["latest_ingestion_runs"] = {
        key: {
            "status": row["status"],
            "observations_read": int(row["observations_read"]),
            "observations_written": int(row["observations_written"]),
            "finished_at": row["finished_at"].isoformat() if row["finished_at"] else None,
            "pipeline_version": row["pipeline_version"],
            "git_sha": row["git_sha"],
        }
        for key, row in sorted(run_map.items())
    }
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
