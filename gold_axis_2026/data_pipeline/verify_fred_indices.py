from __future__ import annotations

import json
import os

import psycopg
from psycopg.rows import dict_row

REQUIRED = ["SP500_FRED", "DJIA_FRED", "NASDAQ100_FRED"]


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def main() -> int:
    report = {"status": "PASS", "series": {}}
    with psycopg.connect(db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select series_id,
                       count(*)::bigint as canonical_rows,
                       min(first_seen_at) as first_seen_at,
                       max(observation_ts) as latest_observation_ts,
                       max(retrieved_at) as latest_retrieved_at,
                       count(*) filter (where available_as_of is null)::bigint as null_available,
                       count(*) filter (where available_as_of < first_seen_at)::bigint as availability_before_first_seen
                from canonical_latest
                where series_id = any(%s)
                group by series_id
                order by series_id
                """,
                (REQUIRED,),
            )
            rows = cur.fetchall()
            by_series = {r["series_id"]: r for r in rows}
            missing = sorted(set(REQUIRED) - set(by_series))
            if missing:
                raise AssertionError(f"FRED_INDEX_REQUIRED_SERIES_MISSING:{missing}")

            bad_availability = {
                sid: {
                    "null_available": int(r["null_available"]),
                    "availability_before_first_seen": int(r["availability_before_first_seen"]),
                }
                for sid, r in by_series.items()
                if int(r["null_available"]) or int(r["availability_before_first_seen"])
            }
            if bad_availability:
                raise AssertionError(f"FRED_INDEX_BAD_AVAILABILITY:{bad_availability}")

            cur.execute(
                """
                select series_id, semantic_id, source_name, source_symbol, source_tier, status
                from source_registry
                where series_id = any(%s)
                order by series_id
                """,
                (REQUIRED,),
            )
            registry = cur.fetchall()
            registry_ids = {r["series_id"] for r in registry}
            missing_registry = sorted(set(REQUIRED) - registry_ids)
            if missing_registry:
                raise AssertionError(f"FRED_INDEX_REGISTRY_MISSING:{missing_registry}")

            # Prospective guard: nothing from these newly onboarded series may be
            # visible before the data plane first retrieved it.
            for sid, r in by_series.items():
                first_seen = r["first_seen_at"]
                cur.execute(
                    "select count(*)::bigint as n from observations_as_of(%s) where series_id=%s",
                    (first_seen - __import__("datetime").timedelta(microseconds=1), sid),
                )
                n = int(cur.fetchone()["n"])
                if n != 0:
                    raise AssertionError(f"FRED_INDEX_POINT_IN_TIME_LEAK:{sid}:{n}")

            cur.execute(
                """
                select trigger_type, status, observations_read, observations_written,
                       finished_at, pipeline_version, git_sha
                from retrieval_runs
                where trigger_type in ('daily:fred_indices','backfill:fred_indices')
                order by finished_at desc nulls last
                limit 1
                """
            )
            latest_run = cur.fetchone()
            if not latest_run:
                raise AssertionError("FRED_INDEX_INGESTION_RUN_MISSING")
            if latest_run["status"] != "SUCCESS":
                raise AssertionError(f"FRED_INDEX_LATEST_RUN_NOT_SUCCESS:{latest_run['status']}")

    for sid, r in by_series.items():
        report["series"][sid] = {
            "canonical_rows": int(r["canonical_rows"]),
            "first_seen_at": r["first_seen_at"].isoformat(),
            "latest_observation_ts": r["latest_observation_ts"].isoformat(),
            "latest_retrieved_at": r["latest_retrieved_at"].isoformat(),
            "point_in_time_pre_first_seen_rows": 0,
        }
    report["registry"] = [dict(r) for r in registry]
    report["latest_ingestion_run"] = {
        "trigger_type": latest_run["trigger_type"],
        "status": latest_run["status"],
        "observations_read": int(latest_run["observations_read"]),
        "observations_written": int(latest_run["observations_written"]),
        "finished_at": latest_run["finished_at"].isoformat() if latest_run["finished_at"] else None,
        "pipeline_version": latest_run["pipeline_version"],
        "git_sha": latest_run["git_sha"],
    }
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
