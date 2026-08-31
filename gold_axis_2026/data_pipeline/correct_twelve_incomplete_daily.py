from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

SERIES_IDS = [
    "NEM_TWELVEDATA",
    "BARRICK_B_TWELVEDATA",
    "GLL_TWELVEDATA",
    "DZZ_TWELVEDATA",
    "HL_PB_TWELVEDATA",
]
APPROVED = "APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY"
PIPELINE_VERSION = "GOLD_DATA_R2.7_2026-08-31"


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL missing")
    return value


def main() -> int:
    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    with psycopg.connect(db_url(), autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select *
                from canonical_latest
                where series_id = any(%s)
                  and source = 'Twelve Data'
                  and quality_status = %s
                  and observation_ts::date >= (retrieved_at at time zone 'America/New_York')::date
                order by series_id, observation_ts
                """,
                (SERIES_IDS, APPROVED),
            )
            rows = cur.fetchall()

            cur.execute(
                """
                insert into retrieval_runs
                (run_id, started_at, finished_at, git_sha, pipeline_version, trigger_type,
                 status, observations_read, observations_written, notes, metadata)
                values (%s,%s,%s,%s,%s,%s,'SUCCESS',%s,0,%s,%s::jsonb)
                """,
                (
                    run_id,
                    now,
                    now,
                    os.environ.get("GITHUB_SHA"),
                    PIPELINE_VERSION,
                    "correction:twelve_market_incomplete_daily",
                    len(rows),
                    "Append REJECTED revisions for same-exchange-day Twelve Data 1day bars; raw observations retained",
                    json.dumps({
                        "policy": "completed_session_only",
                        "exchange_timezone": "America/New_York",
                        "correction_code": "TWELVE_INCOMPLETE_DAILY_BAR_R2_7",
                    }),
                ),
            )

            inserted = 0
            for row in rows:
                metadata = dict(row.get("metadata") or {})
                metadata.update({
                    "correction_code": "TWELVE_INCOMPLETE_DAILY_BAR_R2_7",
                    "correction_reason": "daily bar observation date was not earlier than retrieval exchange-local date",
                    "corrected_at": now.isoformat(),
                    "raw_row_retained": True,
                })
                cur.execute(
                    """
                    insert into observations
                    (run_id, series_id, observation_ts, value, source, source_symbol,
                     provider_as_of, available_as_of, first_seen_at, retrieved_at,
                     frequency, unit, transform, quality_status, lineage_id, payload_hash, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'REJECTED',%s,%s,%s::jsonb)
                    """,
                    (
                        run_id,
                        row["series_id"],
                        row["observation_ts"],
                        row["value"],
                        row["source"],
                        row["source_symbol"],
                        row["provider_as_of"],
                        now,
                        row["first_seen_at"],
                        now,
                        row["frequency"],
                        row["unit"],
                        row["transform"],
                        row["lineage_id"],
                        row.get("payload_hash"),
                        json.dumps(metadata),
                    ),
                )
                inserted += 1

            cur.execute(
                "update retrieval_runs set observations_written=%s where run_id=%s",
                (inserted, run_id),
            )
        conn.commit()

    print(json.dumps({
        "status": "PASS",
        "run_id": run_id,
        "candidate_rows": len(rows),
        "rejected_revisions_written": inserted,
        "raw_rows_deleted": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
