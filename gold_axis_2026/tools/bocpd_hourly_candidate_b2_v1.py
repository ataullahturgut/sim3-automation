from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

import bocpd_hourly_candidate_b_v1_r1 as base

IDENTITY = "BOCPD_HOURLY_SELECTIVE_CANDIDATE_B2_V1_RESEARCH"
THRESHOLDS = [0.5, 0.7, 0.8, 0.9, 0.95, 0.98]
HAZARD_DAYS = [20, 40, 60, 120]
HAZARD_OBS = [440, 880, 1320, 2640]
COOLDOWN_HOURS = 24.0
WARNING_HOURS = 120.0
BETA = 0.5
SELECTION_END = pd.Timestamp("2024-11-01", tz="UTC")
WARM_START = pd.Timestamp("2024-11-01", tz="UTC")
CHALLENGE_START = pd.Timestamp("2025-01-01", tz="UTC")
CHALLENGE_END = pd.Timestamp("2026-01-01", tz="UTC")


def load_daily_weekdays() -> pd.DataFrame:
    db_url = base._secret("NEON_DATABASE_URL")
    sql = """
        select observation_ts, value
        from canonical_latest
        where series_id = %s
          and observation_ts >= timestamptz '2023-01-01 00:00:00+00'
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
    frame["bar_start_ny"] = frame["bar_start_utc"].dt.tz_convert(base.NY_TZ)
    frame["local_date"] = frame["bar_start_ny"].dt.strftime("%Y-%m-%d")
    frame["available_at_utc"] = frame["bar_start_utc"] + pd.Timedelta(hours=1)
    frame = frame.sort_values("bar_start_utc").drop_duplicates("bar_start_utc").reset_index(drop=True)
    return frame


def build_daily_events(daily: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    d = daily.copy().sort_values("bar_start_utc").reset_index(drop=True)
    d["log_return_pct"] = 100.0 * np.log(d["value"] / d["value"].shift(1))
    d["sigma20"] = d["log_return_pct"].shift(1).rolling(20, min_periods=20).std(ddof=1)
    d["z"] = d["log_return_pct"] / d["sigma20"]
    d["is_event"] = d["z"].abs() >= 2.0
    d["previous_daily_available_at_utc"] = d["available_at_utc"].shift(1)
    mask = (
        (d["local_date"] >= start_date)
        & (d["local_date"] <= end_date)
        & d["is_event"]
        & d["previous_daily_available_at_utc"].notna()
    )
    events = d.loc[mask, [
        "local_date", "available_at_utc", "previous_daily_available_at_utc", "z", "log_return_pct"
    ]].copy()
    events = events.rename(columns={"available_at_utc": "event_available_at_utc"})
    return events.reset_index(drop=True)


def select_episodes(timeline: pd.DataFrame, threshold: float) -> pd.DataFrame:
    q = timeline[(timeline["map_reset"]) & (timeline["reset_fraction"] >= threshold)].copy()
    q = q.sort_values("available_at_utc").reset_index(drop=True)
    kept = []
    last_kept = None
    for idx, row in q.iterrows():
        ts = pd.Timestamp(row["available_at_utc"])
        if last_kept is None or (ts - last_kept).total_seconds() / 3600.0 >= COOLDOWN_HOURS:
            kept.append(idx)
            last_kept = ts
    return q.loc[kept].reset_index(drop=True) if kept else q.iloc[0:0].copy()


def match_episodes_to_events(episodes: pd.DataFrame, events: pd.DataFrame) -> dict:
    ep_times = [pd.Timestamp(x) for x in episodes["available_at_utc"].tolist()]
    matched_episode_idx = set()
    captured_event_idx = set()
    leads = []

    for event_idx, event in events.iterrows():
        event_time = pd.Timestamp(event["event_available_at_utc"])
        prev_close = pd.Timestamp(event["previous_daily_available_at_utc"])
        candidates = []
        for i, ts in enumerate(ep_times):
            lead = (event_time - ts).total_seconds() / 3600.0
            if ts <= prev_close and 0.0 < lead <= WARNING_HOURS:
                candidates.append((i, ts, lead))
        if candidates:
            latest = max(candidates, key=lambda x: x[1])
            captured_event_idx.add(event_idx)
            leads.append(float(latest[2]))

    for i, ts in enumerate(ep_times):
        for _, event in events.iterrows():
            event_time = pd.Timestamp(event["event_available_at_utc"])
            prev_close = pd.Timestamp(event["previous_daily_available_at_utc"])
            lead = (event_time - ts).total_seconds() / 3600.0
            if ts <= prev_close and 0.0 < lead <= WARNING_HOURS:
                matched_episode_idx.add(i)
                break

    n_ep = len(episodes)
    n_ev = len(events)
    tp_ep = len(matched_episode_idx)
    cap_ev = len(captured_event_idx)
    precision = tp_ep / n_ep if n_ep else 0.0
    recall = cap_ev / n_ev if n_ev else 0.0
    beta2 = BETA * BETA
    fbeta = ((1.0 + beta2) * precision * recall / (beta2 * precision + recall)) if (precision > 0 and recall > 0) else 0.0
    return {
        "episodes": n_ep,
        "matched_episodes": tp_ep,
        "false_episodes": n_ep - tp_ep,
        "events": n_ev,
        "captured_events": cap_ev,
        "precision": precision,
        "recall": recall,
        "f0_5": fbeta,
        "captured_event_leads_hours": leads,
    }


def selection_key(row: dict) -> tuple:
    return (
        row["f0_5"],
        -row["episodes"],
        row["threshold"],
        row["hazard_days"],
    )


def event_overlay(episodes: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    ep_times = pd.DatetimeIndex(pd.to_datetime(episodes["available_at_utc"], utc=True)).sort_values()
    rows = []
    for event in events.itertuples(index=False):
        event_time = pd.Timestamp(event.event_available_at_utc)
        prev_close = pd.Timestamp(event.previous_daily_available_at_utc)
        formal = ep_times[(ep_times <= prev_close) & (ep_times < event_time)]
        formal = formal[((event_time - formal).total_seconds() / 3600.0) <= WARNING_HOURS] if len(formal) else formal
        latest_formal = formal[-1] if len(formal) else pd.NaT
        formal_lead = (event_time - latest_formal).total_seconds() / 3600.0 if pd.notna(latest_formal) else math.nan
        all_prior = ep_times[ep_times < event_time]
        latest_any = all_prior[-1] if len(all_prior) else pd.NaT
        any_lead = (event_time - latest_any).total_seconds() / 3600.0 if pd.notna(latest_any) else math.nan
        intraday = bool(pd.notna(latest_any) and latest_any > prev_close)
        rows.append({
            "event_date": event.local_date,
            "event_z": float(event.z),
            "formal_captured": bool(len(formal)),
            "formal_latest_episode_at": latest_formal,
            "formal_lead_hours": formal_lead,
            "latest_any_prior_episode_at": latest_any,
            "latest_any_prior_lead_hours": any_lead,
            "latest_any_is_intraday_after_previous_close": intraday,
        })
    return pd.DataFrame(rows)


def main() -> None:
    out_dir = Path(os.environ.get("OUTPUT_DIR", "candidate_b2_output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    formation_prices = base.load_formation_prices()
    challenge_prices = base.fetch_2025_prices()
    daily = load_daily_weekdays()

    d2025 = daily[(daily["local_date"] >= "2025-01-01") & (daily["local_date"] <= "2025-12-31")].copy()
    base.validate_2025_hourly_against_daily(challenge_prices, d2025)

    prices = pd.concat([formation_prices, challenge_prices], ignore_index=True).sort_values("bar_start_utc")
    prices = prices.drop_duplicates("bar_start_utc", keep="first").reset_index(drop=True)
    returns = base.build_returns(prices)
    hour_stats = base.fit_hour_adjustment(returns)
    adjusted = base.apply_hour_adjustment(returns, hour_stats)
    prior = base.fit_prior(adjusted)

    selection_events = build_daily_events(daily, "2024-01-01", "2024-10-31")
    if len(selection_events) < 3:
        raise RuntimeError(f"INSUFFICIENT_2024_SELECTION_EVENTS:{len(selection_events)}")
    print(f"B2_SELECTION_EVENTS_2024_JAN_OCT={len(selection_events)}")
    for row in selection_events.itertuples(index=False):
        print(f"B2_SELECTION_EVENT date={row.local_date} z={row.z:.6f}")

    sel_frame = adjusted[
        (adjusted["bar_start_ny"].dt.year == 2024)
        & (adjusted["bar_start_ny"].dt.month <= 10)
    ].copy()

    grid_rows = []
    for hazard_days, hazard_obs in zip(HAZARD_DAYS, HAZARD_OBS):
        timeline, log_evidence = base.run_bocpd(sel_frame, prior, hazard_obs)
        for threshold in THRESHOLDS:
            episodes = select_episodes(timeline, threshold)
            metrics = match_episodes_to_events(episodes, selection_events)
            row = {
                "hazard_days": hazard_days,
                "hazard_obs": hazard_obs,
                "threshold": threshold,
                "log_evidence": float(log_evidence),
                **metrics,
            }
            grid_rows.append(row)
            print(
                "B2_GRID "
                f"hazard_days={hazard_days} threshold={threshold:.2f} episodes={metrics['episodes']} "
                f"matched={metrics['matched_episodes']} captured={metrics['captured_events']}/{metrics['events']} "
                f"precision={metrics['precision']:.6f} recall={metrics['recall']:.6f} f0_5={metrics['f0_5']:.6f}"
            )

    best = max(grid_rows, key=selection_key)
    print("B2_SELECTED=" + json.dumps(best, sort_keys=True, default=str))

    warm_challenge = adjusted[
        (adjusted["bar_start_ny"] >= pd.Timestamp("2024-11-01", tz=base.NY_TZ))
        & (adjusted["bar_start_ny"] < pd.Timestamp("2026-01-01", tz=base.NY_TZ))
    ].copy()
    timeline_wc, _ = base.run_bocpd(warm_challenge, prior, int(best["hazard_obs"]))
    episodes_wc = select_episodes(timeline_wc, float(best["threshold"]))
    challenge_timeline = timeline_wc[timeline_wc["bar_start_ny"].dt.year == 2025].copy()
    challenge_episodes = episodes_wc[episodes_wc["bar_start_ny"].dt.year == 2025].copy()

    challenge_events = build_daily_events(daily, "2025-01-01", "2025-12-31")
    if len(challenge_events) != 19:
        raise RuntimeError(f"FROZEN_2025_EVENT_COUNT_MISMATCH:{len(challenge_events)}")
    challenge_metrics = match_episodes_to_events(challenge_episodes, challenge_events)
    overlay = event_overlay(challenge_episodes, challenge_events)

    grid = pd.DataFrame(grid_rows).sort_values(
        ["f0_5", "episodes", "threshold", "hazard_days"],
        ascending=[False, True, False, False],
    ).reset_index(drop=True)
    grid.to_csv(out_dir / "candidate_b2_2024_selection_grid.csv", index=False)
    selection_events.to_csv(out_dir / "candidate_b2_2024_selection_events.csv", index=False)
    challenge_timeline.to_csv(out_dir / "candidate_b2_2025_full_timeline.csv", index=False)
    challenge_episodes.to_csv(out_dir / "candidate_b2_2025_episode_onsets.csv", index=False)
    overlay.to_csv(out_dir / "candidate_b2_2025_event_overlay.csv", index=False)
    hour_stats.to_csv(out_dir / "candidate_b2_2023_hour_adjustment.csv", index=False)

    summary = {
        "identity": IDENTITY,
        "selection_period": "2024-01-01/2024-10-31",
        "selection_event_count": int(len(selection_events)),
        "selected": best,
        "warm_start": "2024-11-01/2024-12-31 continuous into 2025",
        "challenge_event_count": int(len(challenge_events)),
        "challenge_eligible_hourly_returns": int(len(challenge_timeline)),
        "challenge_episode_count": int(len(challenge_episodes)),
        "challenge_metrics_frozen_120h_strict": challenge_metrics,
        "challenge_episode_days": int(challenge_episodes["local_date"].nunique()) if len(challenge_episodes) else 0,
        "production_promotion": "NOT_AUTOMATIC",
        "direction_vote_permitted": False,
        "challenge_used_for_selection": False,
    }
    (out_dir / "candidate_b2_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print("B2_CHALLENGE_SUMMARY=" + json.dumps(summary, sort_keys=True, default=str))
    print("B2_2025_EPISODES_BEGIN")
    for row in challenge_episodes.itertuples(index=False):
        print(
            f"B2_EPISODE bar_start_ny={row.bar_start_ny.isoformat()} available_at_utc={row.available_at_utc.isoformat()} "
            f"reset_fraction={row.reset_fraction:.6f} map_run={row.map_run}"
        )
    print("B2_2025_EPISODES_END")
    print("B2_2025_EVENT_OVERLAY_BEGIN")
    for row in overlay.itertuples(index=False):
        lead = "NA" if pd.isna(row.formal_lead_hours) else f"{row.formal_lead_hours:.2f}"
        print(
            f"B2_EVENT date={row.event_date} captured={row.formal_captured} lead_hours={lead} "
            f"intraday_latest_any={row.latest_any_is_intraday_after_previous_close}"
        )
    print("B2_2025_EVENT_OVERLAY_END")
    print("DATABASE_MODEL_OUTPUT_WRITES=NONE")
    print("B2_COMPLETE")


if __name__ == "__main__":
    main()
