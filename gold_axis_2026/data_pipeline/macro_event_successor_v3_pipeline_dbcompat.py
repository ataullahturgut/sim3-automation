from __future__ import annotations

from psycopg.rows import dict_row

import macro_event_successor_v3_pipeline as core


def fetch_existing_dbcompat(conn, series_ids: list[str]) -> list[dict]:
    """Read only columns that production canonical_latest actually exposes.

    payload_hash is intentionally not synthesized: existing Employment scoring only
    consumes series_id, observation_ts and value. Raw provenance remains in the
    underlying observations table.
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select series_id, observation_ts, value, available_as_of,
                   quality_status, lineage_id, metadata
            from canonical_latest
            where series_id = any(%s)
            order by observation_ts, series_id
            """,
            (series_ids,),
        )
        return [dict(x) for x in cur.fetchall()]


core.fetch_existing = fetch_existing_dbcompat

if __name__ == "__main__":
    raise SystemExit(core.main())
