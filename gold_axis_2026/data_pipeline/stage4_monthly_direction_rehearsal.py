from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.monthly import three_month_direction  # noqa: E402

SERIES_ID = "XAU_EOD_TWELVE_NY17"
QUALITY_STATUS = "APPROVED_CANONICAL_TWELVE_NY17"
FEATURE_NAME = "MONTHLY_DIRECTION_3M"
FEATURE_VERSION = "R4_1_3M_SIMPLE_RETURN_V1"
REQUIRED_MONTHS = ("2026-05", "2026-06", "2026-07", "2026-08")


def _month_key(ts) -> str:
    return ts.astimezone(timezone.utc).strftime("%Y-%m")


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
                SELECT id, series_id, observation_ts, value, source, source_symbol,
                       available_as_of, retrieved_at, lineage_id, quality_status
                FROM observations_as_of(%s)
                WHERE series_id=%s AND quality_status=%s
                  AND observation_ts >= timestamptz '2026-05-01 00:00:00+00'
                  AND observation_ts <  timestamptz '2026-09-01 23:59:59+00'
                ORDER BY observation_ts, retrieved_at, id
                """,
                (calc_ts, SERIES_ID, QUALITY_STATUS),
            )
            rows = [dict(r) for r in cur.fetchall()]
        conn.rollback()

    if not rows:
        raise RuntimeError("MONTHLY_DIRECTION_REHEARSAL_NO_CANONICAL_INPUTS")

    lineages = sorted({r["lineage_id"] for r in rows})
    sources = sorted({r["source"] for r in rows})
    if len(lineages) != 1:
        raise RuntimeError(f"MONTHLY_DIRECTION_REHEARSAL_LINEAGE_COUNT:{len(lineages)}")
    if sources != ["Twelve Data"]:
        raise RuntimeError("MONTHLY_DIRECTION_REHEARSAL_SOURCE_MISMATCH")

    # Latest completed canonical observation inside each month as known at calc_ts.
    month_rows: dict[str, dict] = {}
    for r in rows:
        if r["available_as_of"] > calc_ts or r["retrieved_at"] > calc_ts:
            raise RuntimeError("MONTHLY_DIRECTION_REHEARSAL_PIT_VIOLATION")
        key = r["observation_ts"].astimezone(timezone.utc).strftime("%Y-%m")
        if key in REQUIRED_MONTHS:
            current = month_rows.get(key)
            if current is None or r["observation_ts"] > current["observation_ts"]:
                month_rows[key] = r

    missing = [m for m in REQUIRED_MONTHS if m not in month_rows]
    if missing:
        raise RuntimeError("MONTHLY_DIRECTION_REHEARSAL_MISSING_MONTHS:" + ",".join(missing))

    ordered = [month_rows[m] for m in REQUIRED_MONTHS]
    prices = [float(r["value"]) for r in ordered]
    if any(not (x > 0) for x in prices):
        raise RuntimeError("MONTHLY_DIRECTION_REHEARSAL_INVALID_LEVEL")

    completed_returns = [prices[i] / prices[i - 1] - 1.0 for i in range(1, len(prices))]
    direction = three_month_direction(completed_returns).value

    # Bind the exact selected database rows without exposing raw values.
    fingerprint_payload = {
        "series_id": SERIES_ID,
        "feature_name": FEATURE_NAME,
        "feature_version": FEATURE_VERSION,
        "months": list(REQUIRED_MONTHS),
        "input_ids": [int(r["id"]) for r in ordered],
        "input_observation_ts": [r["observation_ts"].isoformat() for r in ordered],
        "lineage_id": lineages[0],
        "calculation_ts": calc_ts.isoformat(),
        "return_definition": "simple_close_to_close_monthly_return",
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    out = {
        "calculation_ts": calc_ts.isoformat(),
        "evidence_class": "LATE_BOOTSTRAP_SHADOW_CONTEXT_REHEARSAL",
        "feature_name": FEATURE_NAME,
        "feature_version": FEATURE_VERSION,
        "required_months": list(REQUIRED_MONTHS),
        "selected_observation_dates": [r["observation_ts"].date().isoformat() for r in ordered],
        "selected_input_ids": [int(r["id"]) for r in ordered],
        "lineage_count": len(lineages),
        "source": sources[0],
        "return_definition": "simple_close_to_close_monthly_return",
        "return_signs": ["POS" if r > 0 else "NEG" if r < 0 else "ZERO" for r in completed_returns],
        "direction": direction,
        "fingerprint": fingerprint,
        "raw_market_values_logged": False,
        "database_writes": "NONE",
        "h1_forecast_blocker_closed": False,
        "prospective_h1_claim": False,
    }
    print(json.dumps(out, indent=2))
    print("STAGE4_MONTHLY_DIRECTION_REHEARSAL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
