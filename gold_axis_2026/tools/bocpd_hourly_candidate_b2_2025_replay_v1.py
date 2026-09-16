from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

import bocpd_hourly_candidate_b_v1_r1 as base
import bocpd_hourly_candidate_b2_calibration_v1 as cal

CONTRACT_PATH = Path("gold_axis_2026/bocpd_hourly_candidate_b2/frozen_contract_v1.json")
DAILY_SERIES_ID = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
LOOKBACK_HOURS = [24, 72, 120, 240]


def load_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract["identity"] != cal.IDENTITY:
        raise RuntimeError("CONTRACT_IDENTITY_MISMATCH")
    if int(contract["alarm_score"]["short_run_k_observations"]) != cal.SHORT_RUN_K:
        raise RuntimeError("CONTRACT_SHORT_RUN_K_MISMATCH")
    if int(contract["hazard"]["selected_expected_run_observations"]) != 440:
        raise RuntimeError("CONTRACT_HAZARD_OBS_MISMATCH")
    if not math.isclose(float(contract["alarm_score"]["selected_threshold"]), 0.8, abs_tol=1e-12):
        raise RuntimeError("CONTRACT_THRESHOLD_MISMATCH")
    if contract["evidence_policy"]["2025_class"] != "HISTORICAL_REPLAY_VISIBLE_REUSED_CHALLENGE":
        raise RuntimeError("CONTRACT_EVIDENCE_CLASS_MISMATCH")
    return contract


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
            cur.execute(sql, (DAILY_SERIES_ID,))
            rows = cur.fetchall()
    frame = pd.DataFrame(rows, columns=["bar_start_utc", "value"])
    frame["bar_start_utc"] = pd.to_datetime(frame["bar_start_utc"], utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="raise").astype(float)
    frame["local_date"] = frame["bar_start_utc"].dt.tz_convert(base.NY_TZ).dt.strftime("%Y-%m-%d")
    return frame.sort_values("bar_start_utc").reset_index(drop=True)


def add_alarm_state(timeline: pd.DataFrame, threshold: float, short_run_k: int) -> pd.DataFrame:
    t = timeline.copy()
    t["score_above_threshold"] = t["short_run_mass_k22"] >= threshold
    t["previous_short_run_mass_k22"] = t["short_run_mass_k22"].shift(1)
    t["previous_map_run_for_alarm"] = t["map_run"].shift(1)
    t["threshold_upcross"] = (
        (t["short_run_mass_k22"] >= threshold)
        & (t["previous_short_run_mass_k22"] < threshold)
    )
    t["mature_preceding_regime"] = t["previous_map_run_for_alarm"] >= short_run_k
    t["alarm_onset"] = t["threshold_upcross"] & t["mature_preceding_regime"]

    segment_start = t["score_above_threshold"] & (~t["score_above_threshold"].shift(1, fill_value=False))
    t["threshold_segment_id"] = segment_start.cumsum().where(t["score_above_threshold"], 0).astype(int)
    onset_segment_ids = set(t.loc[t["alarm_onset"], "threshold_segment_id"].astype(int).tolist())
    t["alarm_episode_active"] = t["threshold_segment_id"].isin(onset_segment_ids) & t["score_above_threshold"]
    t["alarm_episode_id"] = t["threshold_segment_id"].where(t["alarm_episode_active"], 0).astype(int)
    t["alarm_state"] = np.select(
        [t["alarm_onset"], t["alarm_episode_active"]],
        ["ALARM_ONSET", "ALARM_CONTINUATION"],
        default="NO_ALARM",
    )
    return t


def event_overlay(alarms: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    d = daily.sort_values("bar_start_utc").reset_index(drop=True).copy()
    d["available_at_utc"] = d["bar_start_utc"] + pd.Timedelta(hours=1)
    by_date = {row.local_date: i for i, row in d.iterrows()}
    alarm_times = pd.DatetimeIndex(pd.to_datetime(alarms["available_at_utc"], utc=True)).sort_values()

    rows = []
    event_side_counts = {h: 0 for h in LOOKBACK_HOURS}
    strict_count = 0
    intraday_count = 0
    same_close_count = 0
    no_240_count = 0

    for event_date in base.EVENT_DATES:
        if event_date not in by_date:
            raise RuntimeError(f"EVENT_DATE_MISSING:{event_date}")
        idx = by_date[event_date]
        if idx == 0:
            raise RuntimeError(f"NO_PREVIOUS_DAILY_CLOSE:{event_date}")

        event_available = pd.Timestamp(d.loc[idx, "available_at_utc"])
        prev_daily_available = pd.Timestamp(d.loc[idx - 1, "available_at_utc"])
        prior = alarm_times[alarm_times < event_available]
        same = alarm_times[alarm_times == event_available]
        latest = prior[-1] if len(prior) else pd.NaT
        lead_hours = float((event_available - latest).total_seconds() / 3600.0) if pd.notna(latest) else math.nan

        within = {}
        for h in LOOKBACK_HOURS:
            hit = bool(pd.notna(latest) and lead_hours <= h)
            within[h] = hit
            event_side_counts[h] += int(hit)

        if pd.isna(latest) or lead_hours > 240:
            latest_prior_category = "NO_ALARM_WITHIN_240H"
            no_240_count += 1
        elif latest < prev_daily_available:
            latest_prior_category = "STRICT_PRE_EVENT_WINDOW"
            strict_count += 1
        else:
            latest_prior_category = "INTRADAY_PRE_EVENT_CLOSE"
            intraday_count += 1

        same_event_close_alarm = bool(len(same))
        same_close_count += int(same_event_close_alarm)
        if latest_prior_category == "NO_ALARM_WITHIN_240H" and same_event_close_alarm:
            primary_category = "SAME_OR_POST_EVENT_CONFIRM"
        else:
            primary_category = latest_prior_category

        rows.append(
            {
                "event_date": event_date,
                "event_available_at_utc": event_available,
                "previous_daily_available_at_utc": prev_daily_available,
                "latest_prior_alarm_available_at_utc": latest,
                "latest_prior_alarm_lead_hours": lead_hours,
                "latest_prior_category": latest_prior_category,
                "same_event_close_alarm": same_event_close_alarm,
                "primary_category": primary_category,
                **{f"prior_alarm_within_{h}h": within[h] for h in LOOKBACK_HOURS},
            }
        )

    overlay = pd.DataFrame(rows)
    event_times = pd.DatetimeIndex(pd.to_datetime(overlay["event_available_at_utc"], utc=True)).sort_values()
    signal_side_counts = {h: 0 for h in LOOKBACK_HOURS}
    for alarm_time in alarm_times:
        future = event_times[event_times > alarm_time]
        if not len(future):
            continue
        lead = float((future[0] - alarm_time).total_seconds() / 3600.0)
        for h in LOOKBACK_HOURS:
            signal_side_counts[h] += int(lead <= h)

    summary = {
        "event_count": len(base.EVENT_DATES),
        "event_with_prior_alarm_within_hours": {str(h): event_side_counts[h] for h in LOOKBACK_HOURS},
        "latest_prior_category_counts": {
            "STRICT_PRE_EVENT_WINDOW": strict_count,
            "INTRADAY_PRE_EVENT_CLOSE": intraday_count,
            "NO_ALARM_WITHIN_240H": no_240_count,
        },
        "same_event_close_alarm_count": same_close_count,
        "signal_to_next_event_within_hours": {str(h): signal_side_counts[h] for h in LOOKBACK_HOURS},
    }
    return overlay, summary


def main() -> None:
    contract = load_contract()
    out_dir = Path(os.environ.get("OUTPUT_DIR", "candidate_b2_2025_output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    selected_obs = int(contract["hazard"]["selected_expected_run_observations"])
    threshold = float(contract["alarm_score"]["selected_threshold"])
    short_run_k = int(contract["alarm_score"]["short_run_k_observations"])

    formation_prices = base.load_formation_prices()
    challenge_prices = base.fetch_2025_prices()
    daily = load_daily_reference_governed_weekdays()
    crosscheck = base.validate_2025_hourly_against_daily(challenge_prices, daily)

    prices = pd.concat([formation_prices, challenge_prices], ignore_index=True).sort_values("bar_start_utc")
    dup = prices.groupby("bar_start_utc")["value"].nunique()
    if (dup > 1).any():
        raise RuntimeError("COMBINED_DUPLICATE_CONFLICT")
    prices = prices.drop_duplicates("bar_start_utc", keep="first").reset_index(drop=True)

    returns = base.build_returns(prices)
    hour_stats = base.fit_hour_adjustment(returns)
    adjusted = base.apply_hour_adjustment(returns, hour_stats)
    prior = base.fit_prior(adjusted)

    expected_prior = contract["bocpd"]
    if not math.isclose(prior.mu0, float(expected_prior["mu0"]), abs_tol=1e-12):
        raise RuntimeError(f"FROZEN_PRIOR_MU_MISMATCH:{prior.mu0}")
    if not math.isclose(prior.beta0, float(expected_prior["beta0"]), rel_tol=0, abs_tol=1e-12):
        raise RuntimeError(f"FROZEN_PRIOR_BETA_MISMATCH:{prior.beta0}")

    replay = adjusted[adjusted["bar_start_ny"].dt.year.isin([2024, 2025])].copy().reset_index(drop=True)
    timeline, replay_log_evidence = cal.run_bocpd_with_short_mass(replay, prior, selected_obs)
    timeline = add_alarm_state(timeline, threshold, short_run_k)

    y2024 = timeline[timeline["bar_start_ny"].dt.year == 2024].copy()
    frozen_2024_onsets = y2024[y2024["alarm_onset"]].copy()
    if len(frozen_2024_onsets) != 12:
        raise RuntimeError(f"CALIBRATION_REPRODUCTION_FAIL_ONSETS:{len(frozen_2024_onsets)}")

    challenge = timeline[timeline["bar_start_ny"].dt.year == 2025].copy()
    alarms = challenge[challenge["alarm_onset"]].copy()
    active_rows = challenge[challenge["alarm_episode_active"]].copy()

    overlay, overlay_summary = event_overlay(alarms, daily)

    monthly_alarms = alarms["bar_start_ny"].dt.strftime("%Y-%m").value_counts().sort_index().to_dict()
    alarm_dates = int(alarms["local_date"].nunique()) if len(alarms) else 0
    threshold_segments = int(challenge.loc[challenge["score_above_threshold"], "threshold_segment_id"].nunique()) if challenge["score_above_threshold"].any() else 0
    active_episode_ids = int(challenge.loc[challenge["alarm_episode_active"], "alarm_episode_id"].nunique()) if challenge["alarm_episode_active"].any() else 0

    challenge.to_csv(out_dir / "candidate_b2_2025_full_engine_timeline.csv", index=False)
    alarms.to_csv(out_dir / "candidate_b2_2025_all_alarm_onsets.csv", index=False)
    active_rows.to_csv(out_dir / "candidate_b2_2025_alarm_episode_rows.csv", index=False)
    overlay.to_csv(out_dir / "candidate_b2_2025_event_overlay.csv", index=False)
    hour_stats.to_csv(out_dir / "candidate_b2_2023_hour_adjustment.csv", index=False)

    summary = {
        "identity": contract["identity"],
        "contract_path": str(CONTRACT_PATH),
        "evidence_class": contract["evidence_policy"]["2025_class"],
        "2025_is_pristine_holdout": False,
        "calibration_parameters_changed_after_freeze": False,
        "selected_expected_run_observations": selected_obs,
        "selected_hazard": float(contract["hazard"]["selected_hazard"]),
        "short_run_k": short_run_k,
        "selected_threshold": threshold,
        "daily_source_crosscheck": crosscheck,
        "eligible_exact_1h_returns": {
            "2023": int((adjusted["bar_start_ny"].dt.year == 2023).sum()),
            "2024": int((adjusted["bar_start_ny"].dt.year == 2024).sum()),
            "2025": int((adjusted["bar_start_ny"].dt.year == 2025).sum()),
        },
        "calibration_reproduction_2024_alarm_onsets": int(len(frozen_2024_onsets)),
        "challenge_eligible_returns": int(len(challenge)),
        "challenge_threshold_segments": threshold_segments,
        "challenge_valid_alarm_episodes": active_episode_ids,
        "challenge_alarm_onsets": int(len(alarms)),
        "challenge_unique_alarm_dates": alarm_dates,
        "challenge_alarm_onset_rate_percent": float(100.0 * len(alarms) / len(challenge)) if len(challenge) else math.nan,
        "challenge_alarms_by_month": monthly_alarms,
        "challenge_alarm_episode_active_rows": int(len(active_rows)),
        "overlay": overlay_summary,
        "replay_log_evidence_2024_2025": replay_log_evidence,
        "warning_validity_horizon_frozen": False,
        "formal_precision_recall_false_alarm_claim": "NOT_PERMITTED",
        "direction_vote_permitted": False,
        "database_model_output_writes": "NONE",
        "runtime_promotion": "NOT_PROVEN",
    }
    (out_dir / "candidate_b2_2025_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )

    print("B2_2025_SUMMARY=" + json.dumps(summary, sort_keys=True, default=str))
    print("B2_2025_ALL_ALARMS_BEGIN")
    for row in alarms.itertuples(index=False):
        print(
            f"ALARM bar_start_ny={row.bar_start_ny.isoformat()} "
            f"available_at_utc={row.available_at_utc.isoformat()} "
            f"short_run_mass={row.short_run_mass_k22:.9f} prev_map={int(row.previous_map_run_for_alarm)}"
        )
    print("B2_2025_ALL_ALARMS_END")
    print("B2_2025_EVENT_OVERLAY_BEGIN")
    for row in overlay.itertuples(index=False):
        lead = "NA" if pd.isna(row.latest_prior_alarm_lead_hours) else f"{row.latest_prior_alarm_lead_hours:.2f}"
        print(
            f"EVENT date={row.event_date} latest_prior_category={row.latest_prior_category} "
            f"lead_hours={lead} same_event_close_alarm={row.same_event_close_alarm} "
            f"within24={row.prior_alarm_within_24h} within72={row.prior_alarm_within_72h} "
            f"within120={row.prior_alarm_within_120h} within240={row.prior_alarm_within_240h}"
        )
    print("B2_2025_EVENT_OVERLAY_END")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_MODEL_OUTPUT_WRITES=NONE")
    print("B2_2025_VISIBLE_REUSED_CHALLENGE_COMPLETE")


if __name__ == "__main__":
    main()
