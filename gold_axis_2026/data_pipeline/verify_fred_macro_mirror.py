"""Proof that macro FRED mirrors are distinct, recent and chronology-safe."""
import json
import os
from datetime import datetime, timezone, timedelta
import psycopg
from psycopg.rows import dict_row

EXPECTED = {
    "DGS10_FRED": ("DGS10", "APPROVED", "percent", 5),
    "DEXCHUS_FRED": ("DEXCHUS", "APPROVED_WITH_AVAILABILITY_LAG", "CNY per USD", 6),
    "DTWEXBGS_FRED": ("DTWEXBGS", "APPROVED_PROXY_ONLY", "index", 6),
}

def business_lag(observed: datetime, today: datetime) -> int:
    day = observed.astimezone(timezone.utc).date()
    current = today.astimezone(timezone.utc).date()
    if day > current:
        raise AssertionError("FRED_MACRO_FUTURE_OBSERVATION")
    n = 0
    while day < current:
        day += timedelta(days=1)
        if day.weekday() < 5:
            n += 1
    return n

def audit():
    database_url = os.environ["NEON_DATABASE_URL"].strip()
    if not database_url:
        raise RuntimeError("NEON_DATABASE_URL missing")
    rows = []
    with psycopg.connect(database_url, row_factory=dict_row,
                         connect_timeout=12, options="-c default_transaction_read_only=on") as conn:
        with conn.cursor() as cur:
            cur.execute("""
              SELECT series_id, source_symbol, quality_status, unit,
                     MAX(observation_ts) AS latest, MIN(first_seen_at) AS first_seen,
                     COUNT(*) AS n,
                     COUNT(*) FILTER (
                       WHERE available_as_of IS NULL OR
                             available_as_of < first_seen_at
                     ) AS bad_firstprint
              FROM canonical_latest
              WHERE series_id = ANY(%s)
              GROUP BY series_id, source_symbol, quality_status, unit
            """, (list(EXPECTED),))
            rows = list(cur.fetchall())
            cur.execute("""
                SELECT trigger_type,status,finished_at,observations_written
                FROM retrieval_runs WHERE trigger_type='daily:fred_macro'
                ORDER BY started_at DESC LIMIT 1
            """)
            run = cur.fetchone()
    if not run or run["status"] != "SUCCESS":
        raise AssertionError("FRED_MACRO_RUN_NOT_SUCCESS:" + str(run))
    mapping = {r["series_id"]: r for r in rows}
    if set(mapping) != set(EXPECTED):
        raise AssertionError("FRED_MACRO_SERIES_MISSING_OR_DUPLICATE:" + str(sorted(mapping)))
    output = {}
    for name, (symbol, quality, unit, maxage) in EXPECTED.items():
        row = mapping[name]
        if (row["source_symbol"], row["quality_status"], row["unit"]) != (symbol, quality, unit):
            raise AssertionError("FRED_MACRO_PROVENANCE_MISMATCH:" + name)
        if int(row["bad_firstprint"]):
            raise AssertionError("FRED_MACRO_FIRST_ACCESS_LEAK:" + name)
        age = business_lag(row["latest"], datetime.now(timezone.utc))
        if age > maxage:
            raise AssertionError(f"FRED_MACRO_STALE:{name}:{age}")
        output[name] = {"latest": row["latest"].isoformat(),
                        "firstSeen": row["first_seen"].isoformat(),
                        "n": int(row["n"]), "businessDaysOld": age}
    print(json.dumps({"status": "PASS", "series": output, "lastRun": dict(run)},
                     default=str, indent=2))

if __name__ == "__main__":
    audit()
