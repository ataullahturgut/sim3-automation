from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import requests
from requests.adapters import HTTPAdapter
from scipy.special import gammaln
from urllib3.util.retry import Retry

IDENTITY = "BOCPD_HOURLY_SEASONAL_RETURN_CANDIDATE_B_V1_RESEARCH"
SOURCE_SERIES_ID = "XAU_USD_TWELVE_1H_RESEARCH_V1"
DAILY_SERIES_ID = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
API_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
REQUEST_TZ = "UTC"
NY_TZ = "America/New_York"
OUTPUTSIZE = 5000
EXPECTED_HOURS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23]
EXPECTED_RUN_DAYS = [20, 40, 60, 120]
EXPECTED_RUN_OBS = [d * 22 for d in EXPECTED_RUN_DAYS]
EVENT_DATES = [
    "2025-02-10", "2025-02-14", "2025-02-18", "2025-03-13", "2025-04-04",
    "2025-04-09", "2025-04-10", "2025-07-21", "2025-08-01", "2025-09-02",
    "2025-09-22", "2025-09-29", "2025-10-06", "2025-10-13", "2025-10-16",
    "2025-10-17", "2025-10-21", "2025-12-22", "2025-12-29",
]
LOOKBACK_HOURS = [24, 72, 120, 240]


@dataclass(frozen=True)
class NIGPrior:
    mu0: float
    kappa0: float
    alpha0: float
    beta0: float


def _secret(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}_MISSING")
    return value


def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=2.0,
        status_forcelist=(408, 425, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4))
    s.headers.update({"User-Agent": "GoldControl-BOCPD-Hourly-B/1.0", "Accept": "application/json"})
    return s


def _fmt_utc(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S")


def load_formation_prices() -> pd.DataFrame:
    db_url = _secret("NEON_DATABASE_URL")
    sql = """
        select observation_ts, value
        from canonical_latest
        where series_id = %s
          and observation_ts >= timestamptz '2023-01-01 00:00:00+00'
          and observation_ts < timestamptz '2025-01-01 00:00:00+00'
        order by observation_ts
    """
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (SOURCE_SERIES_ID,))
            rows = cur.fetchall()
    if len(rows) != 11751:
        raise RuntimeError(f"FORMATION_ROW_COUNT_MISMATCH:{len(rows)}")
    frame = pd.DataFrame(rows, columns=["bar_start_utc", "value"])
    frame["bar_start_utc"] = pd.to_datetime(frame["bar_start_utc"], utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="raise").astype(float)
    if frame["bar_start_utc"].duplicated().any():
        raise RuntimeError("FORMATION_DUPLICATE_TIMESTAMP")
    if (frame["value"] <= 0).any() or not np.isfinite(frame["value"].to_numpy()).all():
        raise RuntimeError("FORMATION_INVALID_VALUE")
    return frame


def fetch_2025_prices() -> pd.DataFrame:
    key = _secret("TWELVE_DATA_API_KEY")
    s = _session()
    starts = pd.date_range(pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"), freq="QS", inclusive="left")
    rows: list[tuple[pd.Timestamp, float]] = []
    for idx, start in enumerate(starts, start=1):
        end = min(start + pd.DateOffset(months=3), pd.Timestamp("2026-01-01", tz="UTC"))
        params = {
            "symbol": SYMBOL,
            "interval": "1h",
            "start_date": _fmt_utc(pd.Timestamp(start)),
            "end_date": _fmt_utc(pd.Timestamp(end) - pd.Timedelta(seconds=1)),
            "timezone": REQUEST_TZ,
            "order": "ASC",
            "outputsize": OUTPUTSIZE,
            "format": "JSON",
            "apikey": key,
        }
        response = s.get(API_URL, params=params, timeout=(10, 60))
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and payload.get("status") == "error":
            raise RuntimeError(f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}")
        values = payload.get("values") if isinstance(payload, dict) else None
        if not values:
            raise RuntimeError(f"TWELVE_NO_VALUES:{start.date()}:{end.date()}")
        if len(values) >= OUTPUTSIZE:
            raise RuntimeError(f"TWELVE_POSSIBLE_TRUNCATION:{start.date()}:{end.date()}:{len(values)}")
        valid = 0
        for row in values:
            ts = pd.to_datetime(row.get("datetime"), errors="coerce", utc=True)
            value = pd.to_numeric(row.get("close"), errors="coerce")
            if pd.isna(ts) or pd.isna(value):
                continue
            value_f = float(value)
            if not math.isfinite(value_f) or value_f <= 0:
                continue
            if pd.Timestamp(start) <= ts < pd.Timestamp(end):
                rows.append((pd.Timestamp(ts), value_f))
                valid += 1
        print(f"CHALLENGE_FETCH_CHUNK={idx} rows={valid} start={start.date()} end_exclusive={end.date()}")
        time.sleep(2)

    frame = pd.DataFrame(rows, columns=["bar_start_utc", "value"]).sort_values("bar_start_utc")
    if frame.empty:
        raise RuntimeError("CHALLENGE_EMPTY")
    dup = frame.groupby("bar_start_utc")["value"].nunique()
    if (dup > 1).any():
        raise RuntimeError("CHALLENGE_DUPLICATE_CONFLICT")
    frame = frame.drop_duplicates("bar_start_utc", keep="first").reset_index(drop=True)
    if not (5700 <= len(frame) <= 6100):
        raise RuntimeError(f"CHALLENGE_IMPLAUSIBLE_ROW_COUNT:{len(frame)}")
    print(f"CHALLENGE_FETCH_COMPLETE rows={len(frame)} raw_market_values_logged=NO")
    return frame


def load_daily_reference() -> pd.DataFrame:
    db_url = _secret("NEON_DATABASE_URL")
    sql = """
        select observation_ts, value
        from canonical_latest
        where series_id = %s
          and observation_ts >= timestamptz '2024-12-15 00:00:00+00'
          and observation_ts < timestamptz '2026-01-01 00:00:00+00'
        order by observation_ts
    """
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (DAILY_SERIES_ID,))
            rows = cur.fetchall()
    frame = pd.DataFrame(rows, columns=["bar_start_utc", "value"])
    frame["bar_start_utc"] = pd.to_datetime(frame["bar_start_utc"], utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="raise").astype(float)
    frame["local_date"] = frame["bar_start_utc"].dt.tz_convert(NY_TZ).dt.strftime("%Y-%m-%d")
    return frame.sort_values("bar_start_utc").reset_index(drop=True)


def validate_2025_hourly_against_daily(hourly: pd.DataFrame, daily: pd.DataFrame) -> dict:
    d2025 = daily[daily["local_date"].str.startswith("2025-")].copy()
    hmap = dict(zip(hourly["bar_start_utc"], hourly["value"]))
    missing = 0
    mismatch = 0
    max_abs = 0.0
    for row in d2025.itertuples(index=False):
        got = hmap.get(row.bar_start_utc)
        if got is None:
            missing += 1
            continue
        diff = abs(float(got) - float(row.value))
        max_abs = max(max_abs, diff)
        if diff > 1e-9:
            mismatch += 1
    if len(d2025) != 255 or missing or mismatch:
        raise RuntimeError(f"DAILY_CROSSCHECK_FAIL:daily={len(d2025)} missing={missing} mismatch={mismatch} max_abs={max_abs}")
    print(f"DAILY_CROSSCHECK_PASS daily_rows={len(d2025)} exact_timestamp_overlap={len(d2025)-missing} exact_value_match={len(d2025)-missing-mismatch} max_abs_diff={max_abs:.12g}")
    return {"daily_rows": len(d2025), "exact_timestamp_overlap": len(d2025)-missing, "exact_value_match": len(d2025)-missing-mismatch, "max_abs_diff": max_abs}


def build_returns(prices: pd.DataFrame) -> pd.DataFrame:
    frame = prices.sort_values("bar_start_utc").drop_duplicates("bar_start_utc").reset_index(drop=True).copy()
    frame["prev_ts"] = frame["bar_start_utc"].shift(1)
    frame["prev_value"] = frame["value"].shift(1)
    frame["elapsed_hours"] = (frame["bar_start_utc"] - frame["prev_ts"]).dt.total_seconds() / 3600.0
    frame["raw_log_return"] = np.log(frame["value"] / frame["prev_value"])
    frame = frame[np.isclose(frame["elapsed_hours"], 1.0, atol=1e-12)].copy()
    frame["bar_start_ny"] = frame["bar_start_utc"].dt.tz_convert(NY_TZ)
    frame["bar_start_hour"] = frame["bar_start_ny"].dt.hour.astype(int)
    frame["local_date"] = frame["bar_start_ny"].dt.strftime("%Y-%m-%d")
    frame["available_at_utc"] = frame["bar_start_utc"] + pd.Timedelta(hours=1)
    actual_hours = sorted(frame[frame["bar_start_ny"].dt.year.isin([2023, 2024])]["bar_start_hour"].unique().tolist())
    if actual_hours != EXPECTED_HOURS:
        raise RuntimeError(f"ELIGIBLE_HOUR_SET_MISMATCH:{actual_hours}")
    return frame[["bar_start_utc", "bar_start_ny", "available_at_utc", "local_date", "bar_start_hour", "raw_log_return"]].reset_index(drop=True)


def fit_hour_adjustment(returns: pd.DataFrame) -> pd.DataFrame:
    dev = returns[returns["bar_start_ny"].dt.year == 2023].copy()
    stats = dev.groupby("bar_start_hour")["raw_log_return"].agg(["count", "mean", "std"]).reset_index()
    if sorted(stats["bar_start_hour"].tolist()) != EXPECTED_HOURS:
        raise RuntimeError("HOUR_STATS_MISSING_BUCKET")
    if int(stats["count"].min()) < 150:
        raise RuntimeError(f"INSUFFICIENT_2023_HOUR_SUPPORT:{int(stats['count'].min())}")
    if (stats["std"] <= 0).any() or not np.isfinite(stats["std"].to_numpy()).all():
        raise RuntimeError("INVALID_HOUR_SCALE")
    return stats


def apply_hour_adjustment(returns: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
    out = returns.merge(stats[["bar_start_hour", "mean", "std"]], on="bar_start_hour", how="left", validate="many_to_one")
    if out[["mean", "std"]].isna().any().any():
        raise RuntimeError("UNSEEN_HOUR_IN_ADJUSTMENT")
    out["adjusted_return"] = (out["raw_log_return"] - out["mean"]) / out["std"]
    if not np.isfinite(out["adjusted_return"].to_numpy()).all():
        raise RuntimeError("NONFINITE_ADJUSTED_RETURN")
    return out


def fit_prior(adjusted: pd.DataFrame) -> NIGPrior:
    dev = adjusted[adjusted["bar_start_ny"].dt.year == 2023]["adjusted_return"]
    variance = float(dev.var(ddof=1))
    if len(dev) < 4000 or not math.isfinite(variance) or variance <= 0:
        raise RuntimeError("INVALID_2023_PRIOR_FIT")
    return NIGPrior(float(dev.mean()), 1.0, 2.0, variance)


def student_t_logpdf_vec(x: float, mu: np.ndarray, kappa: np.ndarray, alpha: np.ndarray, beta: np.ndarray) -> np.ndarray:
    nu = 2.0 * alpha
    scale2 = beta * (kappa + 1.0) / (alpha * kappa)
    if np.any(scale2 <= 0) or not np.isfinite(scale2).all():
        raise RuntimeError("INVALID_STUDENT_T_SCALE")
    z2 = (x - mu) ** 2 / scale2
    return (
        gammaln((nu + 1.0) / 2.0)
        - gammaln(nu / 2.0)
        - 0.5 * (np.log(nu * np.pi) + np.log(scale2))
        - ((nu + 1.0) / 2.0) * np.log1p(z2 / nu)
    )


def run_bocpd(frame: pd.DataFrame, prior: NIGPrior, expected_run_obs: int) -> tuple[pd.DataFrame, float]:
    hazard = 1.0 / float(expected_run_obs)
    run_posterior = np.array([1.0], dtype=float)
    mu = np.array([prior.mu0], dtype=float)
    kappa = np.array([prior.kappa0], dtype=float)
    alpha = np.array([prior.alpha0], dtype=float)
    beta = np.array([prior.beta0], dtype=float)
    log_evidence = 0.0
    rows: list[dict] = []

    for row in frame.itertuples(index=False):
        x = float(row.adjusted_return)
        previous_map = int(np.argmax(run_posterior))
        log_predictive = student_t_logpdf_vec(x, mu, kappa, alpha, beta)
        log_joint = np.log(np.maximum(run_posterior, 1e-300)) + log_predictive
        shift = float(np.max(log_joint))
        joint_scaled = np.exp(log_joint - shift)
        evidence_scaled = float(joint_scaled.sum())
        log_evidence += shift + math.log(evidence_scaled)

        new_posterior = np.empty(len(run_posterior) + 1, dtype=float)
        new_posterior[0] = hazard * evidence_scaled
        new_posterior[1:] = (1.0 - hazard) * joint_scaled
        new_posterior /= float(new_posterior.sum())

        expected_uninterrupted_run = previous_map + 1
        current_map = int(np.argmax(new_posterior))
        map_reset = current_map < expected_uninterrupted_run
        reset_fraction = max(0.0, (expected_uninterrupted_run - current_map) / float(expected_uninterrupted_run))

        next_mu = np.empty(len(mu) + 1, dtype=float)
        next_kappa = np.empty(len(kappa) + 1, dtype=float)
        next_alpha = np.empty(len(alpha) + 1, dtype=float)
        next_beta = np.empty(len(beta) + 1, dtype=float)
        next_mu[0], next_kappa[0], next_alpha[0], next_beta[0] = prior.mu0, prior.kappa0, prior.alpha0, prior.beta0
        grown_kappa = kappa + 1.0
        next_mu[1:] = (kappa * mu + x) / grown_kappa
        next_kappa[1:] = grown_kappa
        next_alpha[1:] = alpha + 0.5
        next_beta[1:] = beta + 0.5 * kappa * (x - mu) ** 2 / grown_kappa

        rows.append({
            "bar_start_utc": row.bar_start_utc,
            "bar_start_ny": row.bar_start_ny,
            "available_at_utc": row.available_at_utc,
            "local_date": row.local_date,
            "bar_start_hour": int(row.bar_start_hour),
            "adjusted_return": x,
            "previous_map_run": previous_map,
            "expected_uninterrupted_run": expected_uninterrupted_run,
            "map_run": current_map,
            "map_reset": bool(map_reset),
            "reset_fraction": float(reset_fraction),
            "p_run0": float(new_posterior[0]),
            "state": "REGIME_CHANGE_CANDIDATE" if map_reset else "NO_CHANGE_CANDIDATE",
        })
        run_posterior, mu, kappa, alpha, beta = new_posterior, next_mu, next_kappa, next_alpha, next_beta

    return pd.DataFrame(rows), float(log_evidence)


def event_overlay(resets: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    d = daily.sort_values("bar_start_utc").reset_index(drop=True).copy()
    d["available_at_utc"] = d["bar_start_utc"] + pd.Timedelta(hours=1)
    by_date = {row.local_date: i for i, row in d.iterrows()}
    reset_times = pd.DatetimeIndex(pd.to_datetime(resets["available_at_utc"], utc=True)).sort_values()

    rows = []
    coverage = {h: 0 for h in LOOKBACK_HOURS}
    for event_date in EVENT_DATES:
        if event_date not in by_date:
            raise RuntimeError(f"EVENT_DATE_MISSING_FROM_DAILY_SOURCE:{event_date}")
        idx = by_date[event_date]
        if idx == 0:
            raise RuntimeError(f"NO_PREVIOUS_DAILY_CLOSE:{event_date}")
        event_available = pd.Timestamp(d.loc[idx, "available_at_utc"])
        prev_available = pd.Timestamp(d.loc[idx - 1, "available_at_utc"])
        prior = reset_times[reset_times < event_available]
        same = reset_times[reset_times == event_available]
        latest = prior[-1] if len(prior) else pd.NaT
        lead_hours = float((event_available - latest).total_seconds() / 3600.0) if pd.notna(latest) else math.nan
        within = {}
        for h in LOOKBACK_HOURS:
            hit = bool(len(prior) and lead_hours <= h)
            within[str(h)] = hit
            coverage[h] += int(hit)
        if pd.isna(latest) or lead_hours > 240:
            category = "NO_RESET_WITHIN_240H"
        elif latest < prev_available:
            category = "STRICT_PRE_EVENT_WINDOW"
        else:
            category = "INTRADAY_PRE_EVENT_CLOSE"
        rows.append({
            "event_date": event_date,
            "event_available_at_utc": event_available,
            "previous_daily_available_at_utc": prev_available,
            "latest_prior_reset_available_at_utc": latest,
            "latest_prior_reset_lead_hours": lead_hours,
            "latest_prior_category": category,
            "same_event_bar_reset": bool(len(same)),
            **{f"prior_reset_within_{h}h": within[str(h)] for h in LOOKBACK_HOURS},
        })

    overlay = pd.DataFrame(rows)
    signal_to_event = {h: 0 for h in LOOKBACK_HOURS}
    event_times = pd.DatetimeIndex(pd.to_datetime(overlay["event_available_at_utc"], utc=True)).sort_values()
    for reset_time in reset_times:
        future = event_times[event_times > reset_time]
        if not len(future):
            continue
        lead = float((future[0] - reset_time).total_seconds() / 3600.0)
        for h in LOOKBACK_HOURS:
            signal_to_event[h] += int(lead <= h)

    summary = {
        "event_count": len(EVENT_DATES),
        "event_with_prior_reset_within_hours": {str(h): coverage[h] for h in LOOKBACK_HOURS},
        "latest_prior_category_within_240h": overlay["latest_prior_category"].value_counts().to_dict(),
        "same_event_bar_reset_count": int(overlay["same_event_bar_reset"].sum()),
        "signal_to_next_event_within_hours": {str(h): signal_to_event[h] for h in LOOKBACK_HOURS},
    }
    return overlay, summary


def main() -> None:
    out_dir = Path(os.environ.get("OUTPUT_DIR", "candidate_b_output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    formation_prices = load_formation_prices()
    challenge_prices = fetch_2025_prices()
    daily = load_daily_reference()
    crosscheck = validate_2025_hourly_against_daily(challenge_prices, daily)

    prices = pd.concat([formation_prices, challenge_prices], ignore_index=True).sort_values("bar_start_utc")
    if prices["bar_start_utc"].duplicated().any():
        dup = prices.groupby("bar_start_utc")["value"].nunique()
        if (dup > 1).any():
            raise RuntimeError("COMBINED_DUPLICATE_CONFLICT")
        prices = prices.drop_duplicates("bar_start_utc", keep="first")

    returns = build_returns(prices)
    hour_stats = fit_hour_adjustment(returns)
    adjusted = apply_hour_adjustment(returns, hour_stats)
    prior = fit_prior(adjusted)

    formation_2024 = adjusted[adjusted["bar_start_ny"].dt.year == 2024].copy()
    evidence = {}
    formation_resets = {}
    for days, obs in zip(EXPECTED_RUN_DAYS, EXPECTED_RUN_OBS):
        timeline, score = run_bocpd(formation_2024, prior, obs)
        evidence[obs] = score
        formation_resets[obs] = int(timeline["map_reset"].sum())
        print(f"FORMATION_HAZARD expected_days={days} expected_obs={obs} log_evidence={score:.6f} map_resets={formation_resets[obs]}")
    selected_obs = max(evidence, key=evidence.get)
    selected_days = EXPECTED_RUN_DAYS[EXPECTED_RUN_OBS.index(selected_obs)]
    print(f"FORMATION_SELECTED expected_days={selected_days} expected_obs={selected_obs} hazard={1.0/selected_obs:.12f}")

    replay = adjusted[adjusted["bar_start_ny"].dt.year.isin([2024, 2025])].copy()
    timeline, replay_log_evidence = run_bocpd(replay, prior, selected_obs)
    challenge = timeline[pd.to_datetime(timeline["bar_start_ny"]).dt.year == 2025].copy()
    resets = challenge[challenge["map_reset"]].copy()
    reset_days = int(resets["local_date"].nunique())
    monthly = pd.to_datetime(resets["bar_start_ny"]).dt.strftime("%Y-%m").value_counts().sort_index().to_dict()

    overlay, overlay_summary = event_overlay(resets, daily)

    challenge.to_csv(out_dir / "candidate_b_2025_full_timeline.csv", index=False)
    resets.to_csv(out_dir / "candidate_b_2025_all_reset_hours.csv", index=False)
    overlay.to_csv(out_dir / "candidate_b_2025_event_overlay.csv", index=False)
    hour_stats.to_csv(out_dir / "candidate_b_2023_hour_adjustment.csv", index=False)

    summary = {
        "identity": IDENTITY,
        "formation_source_rows_2023_2024": int(len(formation_prices)),
        "challenge_source_rows_2025": int(len(challenge_prices)),
        "daily_source_crosscheck": crosscheck,
        "eligible_exact_1h_returns": {
            "2023": int((adjusted["bar_start_ny"].dt.year == 2023).sum()),
            "2024": int((adjusted["bar_start_ny"].dt.year == 2024).sum()),
            "2025": int((adjusted["bar_start_ny"].dt.year == 2025).sum()),
        },
        "hour_adjustment_min_2023_support": int(hour_stats["count"].min()),
        "hour_adjustment_max_2023_support": int(hour_stats["count"].max()),
        "prior": {"mu0": prior.mu0, "kappa0": prior.kappa0, "alpha0": prior.alpha0, "beta0": prior.beta0},
        "hazard_candidates_expected_days": EXPECTED_RUN_DAYS,
        "hazard_candidates_expected_obs": EXPECTED_RUN_OBS,
        "formation_log_evidence": {str(k): v for k, v in evidence.items()},
        "formation_map_resets": {str(k): v for k, v in formation_resets.items()},
        "selected_expected_run_days": selected_days,
        "selected_expected_run_observations": selected_obs,
        "selected_hazard": 1.0 / selected_obs,
        "challenge_eligible_returns": int(len(challenge)),
        "challenge_reset_hours": int(len(resets)),
        "challenge_unique_reset_days": reset_days,
        "challenge_reset_rate_percent": float(100.0 * len(resets) / len(challenge)),
        "challenge_resets_by_month": monthly,
        "overlay": overlay_summary,
        "replay_log_evidence": replay_log_evidence,
        "direction_vote_permitted": False,
        "warning_horizon_frozen": False,
        "evidence_class": "HISTORICAL_REPLAY_RETROSPECTIVE_DIAGNOSTIC",
        "production_promotion": "NOT_PROVEN",
    }
    (out_dir / "candidate_b_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print("CANDIDATE_B_SUMMARY=" + json.dumps(summary, sort_keys=True, default=str))
    print("CANDIDATE_B_EVENT_OVERLAY_BEGIN")
    for row in overlay.itertuples(index=False):
        lead = "NA" if pd.isna(row.latest_prior_reset_lead_hours) else f"{row.latest_prior_reset_lead_hours:.2f}"
        print(
            f"EVENT date={row.event_date} category={row.latest_prior_category} "
            f"lead_hours={lead} same_event_bar_reset={row.same_event_bar_reset} "
            f"within24={row.prior_reset_within_24h} within72={row.prior_reset_within_72h} "
            f"within120={row.prior_reset_within_120h} within240={row.prior_reset_within_240h}"
        )
    print("CANDIDATE_B_EVENT_OVERLAY_END")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_MODEL_OUTPUT_WRITES=NONE")
    print("CANDIDATE_B_COMPLETE")


if __name__ == "__main__":
    main()
