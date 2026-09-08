from __future__ import annotations

import json
from pathlib import Path

from psycopg.rows import dict_row

import macro_event_successor_v3_historical_reaction_test_r1 as r1

EVENT_XAU_SERIES = "XAU_USD_MACRO_EVENT_REACTION_1M"
R2_TEST_ID = "MACRO_EVENT_SUCCESSOR_V3_HISTORICAL_REACTION_TEST_R2_2026-09-08"


def load_required_bars_r2(conn, events):
    times = set()
    for e in events:
        ts = e["event_ts"]
        times.update([ts - r1.timedelta(minutes=1), ts + r1.timedelta(minutes=4), ts + r1.timedelta(minutes=14), ts + r1.timedelta(minutes=29)])
    if not times:
        return {}
    ordered = list(sorted(times))
    out = {}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("select observation_ts,close from xau_intraday_research_cache_1m where observation_ts=any(%s)", (ordered,))
        for row in cur.fetchall():
            if row["close"] is not None:
                out[row["observation_ts"]] = float(row["close"])
        cur.execute("""
            select distinct on (observation_ts) observation_ts,value
            from observations
            where series_id=%s and observation_ts=any(%s)
            order by observation_ts,retrieved_at desc,id desc
        """, (EVENT_XAU_SERIES, ordered))
        for row in cur.fetchall():
            if row["value"] is not None:
                out[row["observation_ts"]] = float(row["value"])
    return out


def main() -> int:
    r1.load_required_bars = load_required_bars_r2
    r1.TEST_ID = R2_TEST_ID
    r1.PIPELINE_VERSION = R2_TEST_ID
    rc = r1.main()
    src = Path("macro_event_successor_v3_historical_reaction_test_r1_result.json")
    dst = Path("macro_event_successor_v3_historical_reaction_test_r2_result.json")
    payload = json.loads(src.read_text(encoding="utf-8"))
    payload["xau_source"] = "Neon xau_intraday_research_cache_1m + XAU_USD_MACRO_EVENT_REACTION_1M"
    payload["test_id"] = R2_TEST_ID
    dst.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
