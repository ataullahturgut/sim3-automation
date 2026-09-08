from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg

from gold_axis_2026.tools import market_shock_challenger_v2 as v2

EXPECTED_ROWS = 482_734
EXPECTED_FIRST_TS = "2020-04-06T00:00:00+00:00"
EXPECTED_LAST_TS = "2026-08-31T23:55:00+00:00"


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


class CacheFiveMinuteClient:
    def earliest(self) -> str | None:
        with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
            cur.execute("select min(observation_ts) from xau_intraday_research_cache_5m")
            value = cur.fetchone()[0]
        return value.isoformat() if value else None

    def history(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
            cur.execute(
                """
                select observation_ts, close
                from xau_intraday_research_cache_5m
                where observation_ts between %s and %s
                order by observation_ts
                """,
                (start.to_pydatetime(), end.to_pydatetime()),
            )
            rows = cur.fetchall()
        frame = pd.DataFrame(
            {
                "ts": [pd.Timestamp(row[0]) for row in rows],
                "close": [float(row[1]) for row in rows],
            }
        )
        if len(frame) != EXPECTED_ROWS:
            raise RuntimeError(f"CACHE_ROW_COUNT_MISMATCH:{len(frame)}:{EXPECTED_ROWS}")
        first_ts = frame["ts"].min().isoformat()
        last_ts = frame["ts"].max().isoformat()
        if first_ts != EXPECTED_FIRST_TS:
            raise RuntimeError(f"CACHE_FIRST_TS_MISMATCH:{first_ts}:{EXPECTED_FIRST_TS}")
        if last_ts != EXPECTED_LAST_TS:
            raise RuntimeError(f"CACHE_LAST_TS_MISMATCH:{last_ts}:{EXPECTED_LAST_TS}")
        return frame


def _output_path() -> Path:
    if "--output" in sys.argv:
        i = sys.argv.index("--output")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return Path("market_shock_challenger_v2_neon_cache_report.json")


def main() -> int:
    original_client = v2.TwelveClient
    try:
        v2.TwelveClient = CacheFiveMinuteClient
        rc = v2.main()
    finally:
        v2.TwelveClient = original_client

    output = _output_path()
    if output.exists():
        report = json.loads(output.read_text(encoding="utf-8"))
        report["input_source"] = "NEON_RESEARCH_CACHE"
        report["cache_table"] = "xau_intraday_research_cache_5m"
        report["provider_requests_this_replay"] = 0
        report["cache_scope_check"] = {
            "expected_rows": EXPECTED_ROWS,
            "expected_first_ts": EXPECTED_FIRST_TS,
            "expected_last_ts": EXPECTED_LAST_TS,
        }
        report["evidence_class"] = "HISTORICAL_REPLAY"
        report["prospective_claim"] = False
        report["production_promotion"] = "BLOCKED_RESEARCH_CHALLENGER_ONLY"
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
