from __future__ import annotations

import json
import os
from datetime import timedelta

import psycopg
from psycopg.rows import dict_row

REQUIRED = {
    "NEM_TWELVEDATA": {"symbol": "NEM", "semantic": "NEM"},
    "BARRICK_B_TWELVEDATA": {"symbol": "B", "semantic": "BARRICK_NYSE"},
    "GLL_TWELVEDATA": {"symbol": "GLL", "semantic": "GLL"},
    "DZZ_TWELVEDATA": {"symbol": "DZZ", "semantic": "DZZ"},
    "HL_PB_TWELVEDATA": {"symbol": "HL.PR.B", "semantic": "HL_PB"},
}
EXPECTED_STATUS = "APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY"


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL missing")
    return value


def main() -> int:
    report = {"status": "PASS", "series": {}, "registry": [], "latest_ingestion_run": None}
    failures = []

    with psycopg.connect(db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            for sid, expected in REQUIRED.items():
                cur.execute(
                    """
                    select count(*) as n, min(first_seen_at) as first_seen_at,
                           max(observation_ts) as latest_observation_ts,
                           max(retrieved_at) as latest_retrieved_at
                    from usable_observations where series_id=%s
                    """,
                    (sid,),
                )
                row = cur.fetchone()
                if not row or row["n"] == 0:
                    failures.append(f"NO_USABLE_ROWS:{sid}")
                    continue

                first_seen = row["first_seen_at"]
                probe_origin = first_seen - timedelta(microseconds=1)
                cur.execute(
                    "select count(*) as n from observations_as_of(%s) where series_id=%s",
                    (probe_origin, sid),
                )
                pre_seen = cur.fetchone()["n"]
                if pre_seen != 0:
                    failures.append(f"POINT_IN_TIME_LEAK:{sid}:{pre_seen}")

                cur.execute(
                    """
                    select count(*) as n
                    from usable_observations
                    where series_id=%s
                      and observation_ts::date >= (now() at time zone 'America/New_York')::date
                    """,
                    (sid,),
                )
                same_day_eligible = cur.fetchone()["n"]
                if same_day_eligible != 0:
                    failures.append(f"INCOMPLETE_SESSION_EXPOSED:{sid}:{same_day_eligible}")

                report["series"][sid] = {
                    "usable_rows": row["n"],
                    "first_seen_at": first_seen.isoformat(),
                    "latest_eligible_observation_ts": row["latest_observation_ts"].isoformat(),
                    "latest_retrieved_at": row["latest_retrieved_at"].isoformat(),
                    "point_in_time_pre_first_seen_rows": pre_seen,
                    "same_exchange_day_eligible_rows": same_day_eligible,
                }

            cur.execute(
                """
                select series_id, semantic_id, source_name, source_symbol, source_tier, status
                from source_registry where series_id = any(%s) order by series_id
                """,
                (list(REQUIRED),),
            )
            registry = cur.fetchall()
            report["registry"] = [dict(x) for x in registry]
            if len(registry) != len(REQUIRED):
                failures.append(f"REGISTRY_COUNT:{len(registry)}")
            for row in registry:
                exp = REQUIRED[row["series_id"]]
                if row["source_name"] != "Twelve Data":
                    failures.append(f"SOURCE_MISMATCH:{row['series_id']}:{row['source_name']}")
                if row["source_symbol"] != exp["symbol"]:
                    failures.append(f"SYMBOL_MISMATCH:{row['series_id']}:{row['source_symbol']}")
                if row["semantic_id"] != exp["semantic"]:
                    failures.append(f"SEMANTIC_MISMATCH:{row['series_id']}:{row['semantic_id']}")
                if row["source_tier"] != "B":
                    failures.append(f"TIER_MISMATCH:{row['series_id']}:{row['source_tier']}")
                if row["status"] != EXPECTED_STATUS:
                    failures.append(f"STATUS_MISMATCH:{row['series_id']}:{row['status']}")

            cur.execute(
                """
                select trigger_type, status, observations_read, observations_written,
                       finished_at, pipeline_version, git_sha
                from retrieval_runs
                where trigger_type like '%%twelve_market:dedupe_replay'
                order by finished_at desc nulls last limit 1
                """
            )
            latest = cur.fetchone()
            if not latest:
                failures.append("NO_TWELVE_DEDUPE_REPLAY_RUN")
            else:
                report["latest_ingestion_run"] = dict(latest)
                if latest["status"] != "SUCCESS":
                    failures.append(f"LATEST_RUN_NOT_SUCCESS:{latest['status']}")
                if latest["observations_written"] != 0:
                    failures.append(f"DEDUPE_FAILED:{latest['observations_written']}")

    if failures:
        report["status"] = "FAIL"
        report["failures"] = failures
    print(json.dumps(report, indent=2, default=str))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
