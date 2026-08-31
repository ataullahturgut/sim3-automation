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

RETRIEVAL_FLOOR_SERIES = REQUIRED_SERIES


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def main() -> int:
    report: dict = {}
    with psycopg.connect(db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("select value from system_metadata where key='schema_version'")
            schema_row = cur.fetchone()
            schema_version = schema_row["value"] if schema_row else None
            if schema_version != "GOLD_DATA_R2.6_2026-08-31":
                raise AssertionError(f"NEON_SCHEMA_VERSION:{schema_version}")

            cur.execute(
                """
                select
                    to_regprocedure('observations_as_of(timestamp with time zone)')::text as observations_fn,
                    to_regprocedure('latest_series_as_of(timestamp with time zone)')::text as latest_fn
                """
            )
            fn = cur.fetchone()
            if not fn["observations_fn"] or not fn["latest_fn"]:
                raise AssertionError(f"NEON_POINT_IN_TIME_FUNCTIONS_MISSING:{dict(fn)}")

            cur.execute(
                """
                select series_id,
                       count(*)::bigint as canonical_rows,
                       max(observation_ts) as latest_observation_ts,
                       max(retrieved_at) as latest_retrieved_at,
                       count(*) filter (where available_as_of is null)::bigint as null_available_as_of,
                       count(*) filter (where available_as_of < first_seen_at)::bigint as availability_before_first_seen
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

            bad_floor = {
                sid: int(by_series[sid]["availability_before_first_seen"])
                for sid in RETRIEVAL_FLOOR_SERIES
                if int(by_series[sid]["availability_before_first_seen"]) != 0
            }
            if bad_floor:
                raise AssertionError(f"NEON_AVAILABILITY_BEFORE_FIRST_SEEN:{bad_floor}")

            # Current Cboe canonical rows must be the corrected retrieval-floor
            # lineage, never the early R2 rows that equated date with availability.
            cur.execute(
                """
                select series_id,
                       count(*) filter (
                           where coalesce(metadata->>'availability_policy','')
                                 not in ('first_retrieval_floor','retrieval_time_floor')
                       )::bigint as bad_policy
                from canonical_latest
                where series_id in ('GVZ_CBOE','VIX_CBOE')
                group by series_id
                order by series_id
                """
            )
            cboe_policy = {r["series_id"]: int(r["bad_policy"]) for r in cur.fetchall()}
            if set(cboe_policy) != {"GVZ_CBOE", "VIX_CBOE"} or any(cboe_policy.values()):
                raise AssertionError(f"NEON_CBOE_AVAILABILITY_POLICY:{cboe_policy}")

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

            # Direct Fed history was first established on 2026-08-31. A timestamp
            # immediately before that first retrieval must expose zero direct-Fed
            # observations, even though the payload contains historical dates.
            cur.execute(
                """
                select min(first_seen_at) as first_seen
                from observations
                where series_id = any(%s)
                  and coalesce(metadata->>'availability_policy','') = 'first_retrieval_floor'
                """,
                (DIRECT_FED_SERIES,),
            )
            first_fed = cur.fetchone()["first_seen"]
            if first_fed is None:
                raise AssertionError("NEON_DIRECT_FED_FIRST_SEEN_MISSING")
            cur.execute(
                """
                select count(*)::bigint as n
                from observations_as_of(%s - interval '1 second')
                where series_id = any(%s)
                """,
                (first_fed, DIRECT_FED_SERIES),
            )
            pre_fed_count = int(cur.fetchone()["n"])
            if pre_fed_count != 0:
                raise AssertionError(f"POINT_IN_TIME_LEAK_DIRECT_FED:{pre_fed_count}")

            # Early Cboe rows are retained in raw observations for audit. Prove
            # that the point-in-time function excludes them in the gap before the
            # corrected retrieval-floor rows were first recorded.
            cur.execute(
                """
                select min(first_seen_at) as corrected_first_seen
                from observations
                where series_id in ('GVZ_CBOE','VIX_CBOE')
                  and coalesce(metadata->>'availability_policy','')
                      in ('first_retrieval_floor','retrieval_time_floor')
                """
            )
            cboe_corrected_first = cur.fetchone()["corrected_first_seen"]
            if cboe_corrected_first is None:
                raise AssertionError("NEON_CBOE_CORRECTED_FIRST_SEEN_MISSING")
            cur.execute(
                """
                select count(*)::bigint as n
                from observations_as_of(%s - interval '1 second')
                where series_id in ('GVZ_CBOE','VIX_CBOE')
                """,
                (cboe_corrected_first,),
            )
            pre_corrected_cboe_count = int(cur.fetchone()["n"])
            if pre_corrected_cboe_count != 0:
                raise AssertionError(f"POINT_IN_TIME_LEAK_LEGACY_CBOE:{pre_corrected_cboe_count}")

            cur.execute(
                """
                select distinct on (trigger_type)
                       trigger_type, status, observations_read, observations_written,
                       finished_at, pipeline_version, git_sha
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
    report["schema_version"] = schema_version
    report["point_in_time_checks"] = {
        "direct_fed_rows_before_first_retrieval": pre_fed_count,
        "legacy_cboe_rows_exposed_before_corrected_retrieval": pre_corrected_cboe_count,
    }
    report["required_series"] = {
        sid: {
            "canonical_rows": int(by_series[sid]["canonical_rows"]),
            "latest_observation_ts": by_series[sid]["latest_observation_ts"].isoformat(),
            "latest_retrieved_at": by_series[sid]["latest_retrieved_at"].isoformat(),
            "availability_before_first_seen": int(by_series[sid]["availability_before_first_seen"]),
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
