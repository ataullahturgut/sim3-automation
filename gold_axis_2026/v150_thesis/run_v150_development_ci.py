"""CI entrypoint for the frozen V1.50 development study.

This is an implementation-only adapter. It preserves the frozen V1.50
research contract and replaces SQL LIKE-percent literals that psycopg
misinterprets as placeholders with exact governed series-id mappings.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import run_v150_development as core


def load_event_rows_fixed(conn) -> pd.DataFrame:
    sql = """
    WITH ev AS (
      SELECT series_id,
             CASE series_id
               WHEN 'MACRO_EVENT_V3_EMPLOYMENT_SCORE' THEN 'EMPLOYMENT'
               WHEN 'MACRO_EVENT_V3_INFLATION_SCORE' THEN 'INFLATION'
               WHEN 'MACRO_EVENT_V3_FOMC_SCORE' THEN 'FOMC'
             END AS family,
             observation_ts AS event_ts,
             value AS score,
             metadata
      FROM observations
      WHERE series_id = ANY(%s)
        AND observation_ts >= '2023-01-01 00:00:00+00'
        AND observation_ts <  '2025-01-01 00:00:00+00'
    )
    SELECT e.*,
      p0.close AS p0, p5.close AS p5, p15.close AS p15, p30.close AS p30,
      ny1.close AS ny17_next
    FROM ev e
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts-interval '1 minute' LIMIT 1) p0 ON true
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts+interval '4 minute' LIMIT 1) p5 ON true
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts+interval '14 minute' LIMIT 1) p15 ON true
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts+interval '29 minute' LIMIT 1) p30 ON true
    LEFT JOIN LATERAL (
      SELECT close FROM xau_intraday_research_cache_1m x
      WHERE (x.observation_ts AT TIME ZONE 'America/New_York')::date > (e.event_ts AT TIME ZONE 'America/New_York')::date
        AND (x.observation_ts AT TIME ZONE 'America/New_York')::time='16:59:00'
      ORDER BY x.observation_ts LIMIT 1
    ) ny1 ON true
    ORDER BY e.event_ts, e.series_id
    """
    d = core.q(conn, sql, (core.MACRO_SERIES,))
    if d.empty:
        raise RuntimeError("BLOCKED_EVENT_DEVELOPMENT_EMPTY")
    d["event_ts"] = pd.to_datetime(d["event_ts"], utc=True)
    if (d["event_ts"] >= pd.Timestamp("2025-01-01", tz="UTC")).any():
        raise RuntimeError("OUTER_LOCK_VIOLATION_EVENT")
    d["state"] = d["metadata"].map(lambda x: (x or {}).get("state"))
    for label, col in [("R5", "p5"), ("R15", "p15"), ("R30", "p30"), ("EVENT_TO_NEXT_NY17", "ny17_next")]:
        d[label] = np.where((d["p0"] > 0) & (d[col] > 0), np.log(d[col] / d["p0"]), np.nan)
    return d


def main() -> None:
    core.load_event_rows = load_event_rows_fixed
    core.main()


if __name__ == "__main__":
    main()
