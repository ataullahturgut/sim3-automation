from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state  # noqa: E402

SERIES_ID = "XAU_EOD_TWELVE_NY17"
QUALITY_STATUS = "APPROVED_CANONICAL_TWELVE_NY17"


def main() -> int:
    calc_ts = datetime.now(timezone.utc)
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT id, observation_ts, value, source, available_as_of, retrieved_at, lineage_id
                FROM observations_as_of(%s)
                WHERE series_id=%s AND quality_status=%s
                  AND observation_ts >= timestamptz '2026-07-01 00:00:00+00'
                  AND observation_ts <  timestamptz '2026-09-02 00:00:00+00'
                ORDER BY observation_ts, retrieved_at, id
                """,
                (calc_ts, SERIES_ID, QUALITY_STATUS),
            )
            rows = [dict(r) for r in cur.fetchall()]
        conn.rollback()

    if len(rows) < 35:
        raise RuntimeError(f"TACTICAL_REHEARSAL_INSUFFICIENT_ROWS:{len(rows)}")
    lineages = sorted({r["lineage_id"] for r in rows})
    if len(lineages) != 1:
        raise RuntimeError(f"TACTICAL_REHEARSAL_LINEAGE_COUNT:{len(lineages)}")
    if sorted({r["source"] for r in rows}) != ["Twelve Data"]:
        raise RuntimeError("TACTICAL_REHEARSAL_SOURCE_MISMATCH")
    if any(r["available_as_of"] > calc_ts or r["retrieved_at"] > calc_ts for r in rows):
        raise RuntimeError("TACTICAL_REHEARSAL_PIT_VIOLATION")

    # observations_as_of already returns one revision per observation identity.
    rows = sorted(rows, key=lambda r: r["observation_ts"])
    closes = [float(r["value"]) for r in rows]
    if any(not (x > 0) for x in closes):
        raise RuntimeError("TACTICAL_REHEARSAL_INVALID_LEVEL")

    fast = fast_state(closes).value
    daily = pd.DataFrame({
        "date": [pd.Timestamp(r["observation_ts"]).tz_convert("UTC").tz_localize(None) for r in rows],
        "close": closes,
    })
    asof = daily["date"].max()
    weekly = completed_weekly_closes(daily, asof)
    slow = slow_state(weekly).value

    payload = {
        "series_id": SERIES_ID,
        "input_ids": [int(r["id"]) for r in rows],
        "input_observation_ts": [r["observation_ts"].isoformat() for r in rows],
        "lineage_id": lineages[0],
        "asof": asof.isoformat(),
        "fast_contract": "SMA20_2_MARKET_DAY_PERSISTENCE",
        "slow_contract": "COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE",
    }
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    print(json.dumps({
        "calculation_ts": calc_ts.isoformat(),
        "evidence_class": "LATE_BOOTSTRAP_SHADOW_CONTEXT_REHEARSAL",
        "asof_date": asof.date().isoformat(),
        "daily_input_count": len(rows),
        "completed_weekly_close_count": len(weekly),
        "lineage_count": len(lineages),
        "fast_state": fast,
        "slow_state": slow,
        "input_fingerprint": fingerprint,
        "raw_market_values_logged": False,
        "database_writes": "NONE",
        "prospective_h1_claim": False,
    }, indent=2))
    print("STAGE4_TACTICAL_REHEARSAL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
