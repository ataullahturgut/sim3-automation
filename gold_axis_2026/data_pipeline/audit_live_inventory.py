from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


OUT = Path(__file__).resolve().parent / "audits" / "GOLD_CONTROL_LIVE_DB_INVENTORY.json"


def _iso(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _jsonable_rows(rows):
    out = []
    for row in rows:
        out.append({k: _iso(v) for k, v in dict(row).items()})
    return out


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("AUDIT_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    try:
        with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # Binding safety rule: this audit is read-only and always rolled back.
                cur.execute("SET TRANSACTION READ ONLY")

                cur.execute(
                    """
                    SELECT
                        series_id,
                        min(observation_ts) AS first_observation_ts,
                        max(observation_ts) AS last_observation_ts,
                        min(first_seen_at) AS first_seen_at,
                        max(retrieved_at) AS last_retrieved_at,
                        max(provider_as_of) AS latest_provider_as_of,
                        count(*) AS usable_current_rows,
                        count(DISTINCT lineage_id) AS lineage_count,
                        (array_agg(source ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_source,
                        (array_agg(lineage_id ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_lineage_id,
                        (array_agg(quality_status ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_quality_status
                    FROM usable_observations
                    GROUP BY series_id
                    ORDER BY series_id
                    """
                )
                series = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT
                        run_id,
                        started_at,
                        finished_at,
                        git_sha,
                        pipeline_version,
                        trigger_type,
                        status,
                        observations_read,
                        observations_written
                    FROM retrieval_runs
                    ORDER BY COALESCE(finished_at, started_at) DESC
                    LIMIT 30
                    """
                )
                runs = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT key, value, updated_at
                    FROM system_metadata
                    ORDER BY key
                    """
                )
                metadata = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT
                        count(*) FILTER (WHERE severity = 'ERROR') AS quality_error_events,
                        count(*) FILTER (WHERE severity = 'WARNING') AS quality_warning_events,
                        max(event_ts) AS latest_quality_event_ts
                    FROM quality_events
                    """
                )
                quality_summary = _jsonable_rows(cur.fetchall())[0]

                # Metadata-only failure evidence. Messages/payloads are deliberately
                # excluded from the public audit artifact to avoid leaking provider
                # response details or sensitive context.
                cur.execute(
                    """
                    SELECT series_id, event_ts, severity, code
                    FROM quality_events
                    ORDER BY event_ts DESC, id DESC
                    LIMIT 30
                    """
                )
                recent_quality_events = _jsonable_rows(cur.fetchall())

            conn.rollback()

        payload = {
            "audit_version": "GOLD_CONTROL_LIVE_DB_INVENTORY_R1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "mode": "READ_ONLY_ROLLBACK",
            "contains_observation_values": False,
            "contains_quality_messages": False,
            "series": series,
            "recent_retrieval_runs": runs,
            "system_metadata": metadata,
            "quality_event_summary": quality_summary,
            "recent_quality_events": recent_quality_events,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"AUDIT_OK series={len(series)} runs={len(runs)} output={OUT.name}")
        return 0
    except Exception as exc:
        # Do not print DSN/provider connection details into public CI logs.
        print(f"AUDIT_FAILED:{type(exc).__name__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
