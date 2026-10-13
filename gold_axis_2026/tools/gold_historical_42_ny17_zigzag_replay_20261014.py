#!/usr/bin/env python3
"""Reproduce 2023-2025 3%-reversal ZigZag V1 from private, uncommitted NY17 daily-close export.

No trading or forecasting. No private database credentials in repository.
1. Run SQL statement below against Neon Gold Control read-only with authorisation.
2. Export results to a PRIVATE CSV with columns day, old_mid, corrected_mid.
3. python gold_historical_42_ny17_zigzag_replay_20261014.py daily_private.csv old_atlas.csv

IMPORTANT: do not commit/private-share the 774-row vendor close export.
"""
import csv
import sys
from math import isclose

SQL = """
WITH b AS (
 SELECT bar_start_utc + INTERVAL '15 minutes' bar_end,
        (bid_close + ask_close) / 2.0 AS mid,
        DATE((bar_start_utc + INTERVAL '15 minutes') AT TIME ZONE 'America/New_York'
             + INTERVAL '7 hours') old_day,
        DATE((bar_start_utc + INTERVAL '15 minutes') AT TIME ZONE 'America/New_York'
             + INTERVAL '7 hours' - INTERVAL '1 microsecond') corrected_day
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc >= '2022-12-20' AND bar_start_utc < '2026-01-02'
), both AS (
 SELECT 'old' version, old_day day, mid, bar_end FROM b
 UNION ALL
 SELECT 'corrected', corrected_day, mid, bar_end FROM b
), daily AS (
 SELECT DISTINCT ON(version, day)
   version,day,mid,bar_end, COUNT(*) OVER(PARTITION BY version,day) bar_count
 FROM both WHERE EXTRACT(ISODOW FROM day) <= 5
 ORDER BY version,day,bar_end DESC
), paired AS (
 SELECT day::text AS day,
        MAX(mid) FILTER(WHERE version='old' AND bar_count >= 70) old_mid,
        MAX(mid) FILTER(WHERE version='corrected' AND bar_count >= 70) corrected_mid
 FROM daily WHERE day BETWEEN '2023-01-01' AND '2025-12-31'
 GROUP BY day
)
SELECT day,old_mid,corrected_mid FROM paired
WHERE old_mid IS NOT NULL AND corrected_mid IS NOT NULL ORDER BY day;
"""


def zigzag(daily, threshold=0.03):
    if not daily:
        raise ValueError("Empty daily panel")
    anchor = daily[0]
    extreme = anchor
    trend = 0
    swings = []
    def leg(first, last, direction, confirmed):
        return (first[0], last[0], direction,
                100 * (last[1] / first[1] - 1), confirmed)
    for day in daily[1:]:
        if trend == 0:
            if day[1] >= anchor[1] * (1 + threshold):
                trend, extreme = 1, day
            elif day[1] <= anchor[1] * (1 - threshold):
                trend, extreme = -1, day
        elif trend > 0:
            if day[1] > extreme[1]:
                extreme = day
            if day[1] <= extreme[1] * (1 - threshold):
                swings.append(leg(anchor, extreme, "UP", day[0]))
                anchor, extreme, trend = extreme, day, -1
        else:
            if day[1] < extreme[1]:
                extreme = day
            if day[1] >= extreme[1] * (1 + threshold):
                swings.append(leg(anchor, extreme, "DOWN", day[0]))
                anchor, extreme, trend = extreme, day, 1
    if trend:
        swings.append(leg(anchor, daily[-1], "UP" if trend > 0 else "DOWN", "OPEN"))
    return swings


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python script.py daily_private_export.csv legacy_event_atlas.csv")
    with open(sys.argv[1], newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    daily_old = [(r["day"], float(r["old_mid"])) for r in rows]
    daily_new = [(r["day"], float(r["corrected_mid"])) for r in rows]
    if len(rows) != 774:
        raise ValueError(f"expected 774 eligible paired days; got {len(rows)}")
    old, new = zigzag(daily_old), zigzag(daily_new)
    with open(sys.argv[2], newline="", encoding="utf-8") as file:
        atlas = list(csv.DictReader(file))
    if len(old) != len(new) or len(old) != len(atlas) or len(old) != 42:
        raise ValueError("nonreproduced 42-leg original algorithm; inspect data and source first")
    for index, (actual, legacy) in enumerate(zip(old, atlas), start=1):
        if not (actual[0] == legacy["start"] and actual[1] == legacy["end"]
                and actual[2] == legacy["dir"]
                and isclose(actual[3], float(legacy["pct"]), abs_tol=0.001)):
            raise AssertionError(f"original not reproduced at leg {index}")
    print("VALIDATED: 774 daily sessions and 42/42 original legs")
    changed = []
    for i, (before, after) in enumerate(zip(old, new), start=1):
        if before[:3] != after[:3]:
            changed.append((i, before[:3], after[:3], after[3]))
    print("Corrected count:", len(new))
    print("Changes:", changed)
    assert [c[0] for c in changed] == [28, 29, 38, 39]


if __name__ == "__main__":
    main()
