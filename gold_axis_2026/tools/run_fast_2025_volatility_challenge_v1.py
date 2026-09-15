from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4 import FastState, fast_state  # noqa: E402

CHALLENGE_ID = "GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_V1"
RESEARCH_SERIES_ID = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"

# Frozen before this replay. EXTREME is a subset of MAJOR.
EVENTS: tuple[tuple[str, str, str], ...] = (
    ("2025-02-10", "UP", "MAJOR"),
    ("2025-02-14", "DOWN", "MAJOR"),
    ("2025-02-18", "UP", "MAJOR"),
    ("2025-03-13", "UP", "MAJOR"),
    ("2025-04-04", "DOWN", "EXTREME"),
    ("2025-04-09", "UP", "EXTREME"),
    ("2025-04-10", "UP", "MAJOR"),
    ("2025-07-21", "UP", "MAJOR"),
    ("2025-08-01", "UP", "MAJOR"),
    ("2025-09-02", "UP", "MAJOR"),
    ("2025-09-22", "UP", "MAJOR"),
    ("2025-09-29", "UP", "MAJOR"),
    ("2025-10-06", "UP", "MAJOR"),
    ("2025-10-13", "UP", "MAJOR"),
    ("2025-10-16", "UP", "MAJOR"),
    ("2025-10-17", "DOWN", "MAJOR"),
    ("2025-10-21", "DOWN", "EXTREME"),
    ("2025-12-22", "UP", "EXTREME"),
    ("2025-12-29", "DOWN", "EXTREME"),
)


def score_primary(previous_fast: str, event_direction: str) -> str:
    expected = f"ROBUST_{event_direction}"
    if previous_fast == expected:
        return "EARLY_HIT"
    if previous_fast in {FastState.ROBUST_UP.value, FastState.ROBUST_DOWN.value}:
        return "WRONG_DIRECTION"
    return "NO_SIGNAL"


def validate_daily(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "close"}
    if not required <= set(frame.columns):
        raise RuntimeError("FAST_REPLAY_SCHEMA_MISMATCH")
    x = frame.loc[:, ["date", "close"]].copy()
    x["date"] = pd.to_datetime(x["date"]).dt.normalize()
    x["close"] = pd.to_numeric(x["close"], errors="raise")
    x = x.sort_values("date").reset_index(drop=True)
    if x.empty or x["date"].duplicated().any():
        raise RuntimeError("FAST_REPLAY_EMPTY_OR_DUPLICATE_DATE")
    if (~x["close"].map(math.isfinite)).any() or (x["close"] <= 0).any():
        raise RuntimeError("FAST_REPLAY_INVALID_CLOSE")
    if (x["date"].dt.weekday >= 5).any():
        raise RuntimeError("FAST_REPLAY_NON_GOVERNED_WEEKEND_DATE")
    x2025 = x[(x["date"] >= pd.Timestamp("2025-01-01")) & (x["date"] <= pd.Timestamp("2025-12-31"))]
    if len(x2025) != 255:
        raise RuntimeError(f"FAST_REPLAY_2025_COVERAGE_MISMATCH:{len(x2025)}")
    event_dates = {pd.Timestamp(d) for d, _, _ in EVENTS}
    missing_events = sorted(d.date().isoformat() for d in event_dates - set(x2025["date"]))
    if missing_events:
        raise RuntimeError(f"FAST_REPLAY_EVENT_DATE_MISSING:{','.join(missing_events)}")
    return x


def load_and_validate(database_url: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    import psycopg

    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
            cur.execute(
                """
                select (observation_ts at time zone 'America/New_York')::date as d,
                       value::double precision as close
                from observations
                where series_id=%s
                  and (observation_ts at time zone 'America/New_York')::date between date '2024-01-01' and date '2025-12-31'
                  and extract(isodow from (observation_ts at time zone 'America/New_York')) between 1 and 5
                order by d
                """,
                (RESEARCH_SERIES_ID,),
            )
            research = pd.DataFrame(cur.fetchall(), columns=["date", "close"])

            cur.execute(
                """
                with r as (
                    select (observation_ts at time zone 'America/New_York')::date d,
                           value::double precision close
                    from observations
                    where series_id=%s
                      and (observation_ts at time zone 'America/New_York')::date between date '2025-01-01' and date '2025-12-31'
                      and extract(isodow from (observation_ts at time zone 'America/New_York')) between 1 and 5
                ), x as (
                    select (observation_ts at time zone 'America/New_York')::date d,
                           close::double precision close
                    from xau_intraday_research_cache_1m
                    where (observation_ts at time zone 'America/New_York')::date between date '2025-01-01' and date '2025-12-31'
                      and (observation_ts at time zone 'America/New_York')::time = time '16:59:00'
                      and extract(isodow from (observation_ts at time zone 'America/New_York')) between 1 and 5
                )
                select count(*)::int as overlap_n,
                       coalesce(max(abs(r.close-x.close)),0)::double precision as max_abs_close_diff
                from r join x using(d)
                """,
                (RESEARCH_SERIES_ID,),
            )
            overlap_n, max_diff = cur.fetchone()

    daily = validate_daily(research)
    if int(overlap_n) < 190:
        raise RuntimeError(f"FAST_REPLAY_EXACT_OVERLAP_TOO_LOW:{overlap_n}")
    if float(max_diff) > 1e-8:
        raise RuntimeError(f"FAST_REPLAY_EXACT_CLOSE_MISMATCH:{max_diff}")
    evidence = {
        "research_series_id": RESEARCH_SERIES_ID,
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "research_usage": "HISTORICAL_REPLAY_ONLY_NOT_CANONICAL_RUNTIME_NY17",
        "weekday_rows_2025": int(((daily["date"] >= pd.Timestamp("2025-01-01")) & (daily["date"] <= pd.Timestamp("2025-12-31"))).sum()),
        "exact_1659_overlap_weekdays": int(overlap_n),
        "exact_1659_max_abs_close_diff": float(max_diff),
        "weekend_rows_used": 0,
        "production_write": "NONE",
    }
    return daily, evidence


def state_through(daily: pd.DataFrame, day: pd.Timestamp) -> str:
    history = daily.loc[daily["date"] <= day, "close"].tolist()
    return fast_state(history).value


def replay(daily: pd.DataFrame) -> list[dict[str, Any]]:
    dates = daily["date"].tolist()
    rows: list[dict[str, Any]] = []
    for event_date_text, direction, tier in EVENTS:
        event_date = pd.Timestamp(event_date_text)
        pos = dates.index(event_date)
        if pos == 0 or pos + 1 >= len(dates):
            raise RuntimeError(f"FAST_REPLAY_EVENT_BOUNDARY_FAIL:{event_date_text}")
        prev_date, next_date = dates[pos - 1], dates[pos + 1]
        prev_state = state_through(daily, prev_date)
        event_state = state_through(daily, event_date)
        next_state = state_through(daily, next_date)
        expected = f"ROBUST_{direction}"
        rows.append(
            {
                "event_date": event_date_text,
                "direction": direction,
                "tier": tier,
                "previous_governed_date": prev_date.date().isoformat(),
                "previous_fast_state": prev_state,
                "primary_status": score_primary(prev_state, direction),
                "event_fast_state": event_state,
                "same_event_confirm": event_state == expected,
                "next_governed_date": next_date.date().isoformat(),
                "next_fast_state": next_state,
                "next_day_confirm": next_state == expected,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def one(label: str, subset: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(subset)
        return {
            "segment": label,
            "n": n,
            "early_hit": sum(r["primary_status"] == "EARLY_HIT" for r in subset),
            "wrong_direction": sum(r["primary_status"] == "WRONG_DIRECTION" for r in subset),
            "no_signal": sum(r["primary_status"] == "NO_SIGNAL" for r in subset),
            "same_event_confirm": sum(bool(r["same_event_confirm"]) for r in subset),
            "next_day_confirm": sum(bool(r["next_day_confirm"]) for r in subset),
        }

    return {
        "challenge_id": CHALLENGE_ID,
        "engine_id": "FAST",
        "primary_rule": "previous governed day ROBUST state must match event direction",
        "segments": [
            one("ALL", rows),
            one("UP", [r for r in rows if r["direction"] == "UP"]),
            one("DOWN", [r for r in rows if r["direction"] == "DOWN"]),
            one("EXTREME", [r for r in rows if r["tier"] == "EXTREME"]),
        ],
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-csv", type=Path)
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    daily, evidence = load_and_validate(args.database_url)
    rows = replay(daily)
    summary = summarize(rows)
    payload = {"evidence": evidence, "summary": summary, "rows": rows}

    if args.out_json:
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_csv:
        write_csv(args.out_csv, rows)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
