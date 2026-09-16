from __future__ import annotations

import pandas as pd
import psycopg

import bocpd_hourly_candidate_b_v1_r1 as base


def load_daily_reference_governed_weekdays() -> pd.DataFrame:
    db_url = base._secret("NEON_DATABASE_URL")
    sql = """
        select observation_ts, value
        from canonical_latest
        where series_id = %s
          and observation_ts >= timestamptz '2024-12-15 00:00:00+00'
          and observation_ts < timestamptz '2026-01-01 00:00:00+00'
          and extract(isodow from observation_ts at time zone 'America/New_York') between 1 and 5
        order by observation_ts
    """
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (base.DAILY_SERIES_ID,))
            rows = cur.fetchall()
    frame = pd.DataFrame(rows, columns=["bar_start_utc", "value"])
    frame["bar_start_utc"] = pd.to_datetime(frame["bar_start_utc"], utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="raise").astype(float)
    frame["local_date"] = frame["bar_start_utc"].dt.tz_convert(base.NY_TZ).dt.strftime("%Y-%m-%d")
    return frame.sort_values("bar_start_utc").reset_index(drop=True)


def main() -> None:
    base.load_daily_reference = load_daily_reference_governed_weekdays
    base.main()


if __name__ == "__main__":
    main()
