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
ROBUST_STATES = {FastState.ROBUST_UP.value, FastState.ROBUST_DOWN.value}

# Frozen before FAST replay. EXTREME is a subset of MAJOR.
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


def compute_states(daily: pd.DataFrame) -> pd.DataFrame:
    x = daily.copy().reset_index(drop=True)
    states: list[str] = []
    history: list[float] = []
    for close in x["close"].tolist():
        history.append(float(close))
        states.append(fast_state(history).value)
    x["fast_state"] = states
    return x


def build_2025_timeline(daily: pd.DataFrame) -> pd.DataFrame:
    states = compute_states(daily)
    event_map = {pd.Timestamp(d): (direction, tier) for d, direction, tier in EVENTS}
    rows: list[dict[str, Any]] = []
    for i, row in states.iterrows():
        day = row["date"]
        if not (pd.Timestamp("2025-01-01") <= day <= pd.Timestamp("2025-12-31")):
            continue
        state = str(row["fast_state"])
        previous_state = str(states.iloc[i - 1]["fast_state"]) if i > 0 else FastState.INSUFFICIENT_DATA.value
        is_onset = state in ROBUST_STATES and previous_state != state
        event_direction, event_tier = event_map.get(day, (None, None))
        rows.append(
            {
                "date": day.date().isoformat(),
                "close": float(row["close"]),
                "fast_state": state,
                "previous_fast_state": previous_state,
                "new_robust_episode": bool(is_onset),
                "volatility_event": event_direction is not None,
                "event_direction": event_direction,
                "event_tier": event_tier,
            }
        )
    out = pd.DataFrame(rows)
    if len(out) != 255:
        raise RuntimeError(f"FAST_TIMELINE_2025_CARDINALITY_MISMATCH:{len(out)}")
    return out


def governed_lead(index_by_date: dict[pd.Timestamp, int], start: pd.Timestamp, end: pd.Timestamp) -> int:
    return int(index_by_date[end] - index_by_date[start])


def build_onsets(timeline: pd.DataFrame) -> pd.DataFrame:
    event_rows = [(pd.Timestamp(d), direction, tier) for d, direction, tier in EVENTS]
    timeline_dates = [pd.Timestamp(d) for d in timeline["date"]]
    index_by_date = {d: i for i, d in enumerate(timeline_dates)}
    onsets: list[dict[str, Any]] = []
    for _, row in timeline[timeline["new_robust_episode"]].iterrows():
        signal_date = pd.Timestamp(row["date"])
        signal_direction = "UP" if row["fast_state"] == FastState.ROBUST_UP.value else "DOWN"
        future_any = [e for e in event_rows if e[0] >= signal_date]
        future_same = [e for e in future_any if e[1] == signal_direction]
        next_any = future_any[0] if future_any else None
        next_same = future_same[0] if future_same else None
        same_lead = governed_lead(index_by_date, signal_date, next_same[0]) if next_same else None
        any_lead = governed_lead(index_by_date, signal_date, next_any[0]) if next_any else None
        onsets.append(
            {
                "signal_date": signal_date.date().isoformat(),
                "fast_state": row["fast_state"],
                "signal_direction": signal_direction,
                "close": float(row["close"]),
                "next_volatility_event": next_any[0].date().isoformat() if next_any else None,
                "next_event_direction": next_any[1] if next_any else None,
                "next_event_tier": next_any[2] if next_any else None,
                "days_to_next_event": any_lead,
                "next_same_direction_event": next_same[0].date().isoformat() if next_same else None,
                "next_same_direction_tier": next_same[2] if next_same else None,
                "days_to_next_same_direction_event": same_lead,
                "same_direction_event_day": same_lead == 0 if same_lead is not None else False,
                "same_direction_early_within_1d": 1 <= same_lead <= 1 if same_lead is not None else False,
                "same_direction_early_within_3d": 1 <= same_lead <= 3 if same_lead is not None else False,
                "same_direction_early_within_5d": 1 <= same_lead <= 5 if same_lead is not None else False,
                "same_direction_early_within_10d": 1 <= same_lead <= 10 if same_lead is not None else False,
            }
        )
    out = pd.DataFrame(onsets)
    return out


def summarize(timeline: pd.DataFrame, onsets: pd.DataFrame) -> dict[str, Any]:
    return {
        "challenge_id": CHALLENGE_ID,
        "engine_id": "FAST",
        "evaluation_direction": "FULL_FAST_TIMELINE_THEN_OVERLAY_FROZEN_VOLATILITY_EVENTS",
        "withdrawn_metric": "EVENT_CONDITIONED_11_OF_19_DIRECTION_ALIGNMENT_IS_NOT_FAST_ALARM_PERFORMANCE",
        "daily_fast_rows_2025": int(len(timeline)),
        "frozen_volatility_event_days": len(EVENTS),
        "new_robust_episode_onsets": int(len(onsets)),
        "event_day_same_direction_onsets": int(onsets["same_direction_event_day"].sum()),
        "early_warning_sensitivity_not_frozen_window": {
            "within_1_governed_day": int(onsets["same_direction_early_within_1d"].sum()),
            "within_3_governed_days": int(onsets["same_direction_early_within_3d"].sum()),
            "within_5_governed_days": int(onsets["same_direction_early_within_5d"].sum()),
            "within_10_governed_days": int(onsets["same_direction_early_within_10d"].sum()),
        },
        "false_alarm_rate": "NOT_FROZEN_UNTIL_WARNING_WINDOW_IS_PREREGISTERED",
        "production_write": "NONE",
    }


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-daily-csv", type=Path)
    parser.add_argument("--out-onsets-csv", type=Path)
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    daily, evidence = load_and_validate(args.database_url)
    timeline = build_2025_timeline(daily)
    onsets = build_onsets(timeline)
    summary = summarize(timeline, onsets)
    payload = {
        "evidence": evidence,
        "summary": summary,
        "onsets": onsets.where(pd.notna(onsets), None).to_dict(orient="records"),
    }

    if args.out_json:
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_daily_csv:
        write_csv(args.out_daily_csv, timeline)
    if args.out_onsets_csv:
        write_csv(args.out_onsets_csv, onsets)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
