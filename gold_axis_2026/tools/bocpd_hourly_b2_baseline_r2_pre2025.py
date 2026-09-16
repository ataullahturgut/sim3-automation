from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.special import gammaln

SOURCE_SERIES_ID = "XAU_USD_TWELVE_1H_RESEARCH_V1"
DAILY_SERIES_ID = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
NY_TZ = "America/New_York"

IDENTITY_BASE = "BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH"
THRESHOLDS_RESET = [0.70, 0.80, 0.90, 0.95, 0.98]
HAZARD_DAYS = [20, 40, 60, 120]
HAZARD_OBS = [d * 22 for d in HAZARD_DAYS]
COOLDOWN_HOURS = 24.0
WARNING_HOURS = 120.0
BETA = 0.5
FIT_YEAR = 2022
DEV_YEAR = 2023
VALID_YEAR = 2024


@dataclass(frozen=True)
class NIGPrior:
    mu0: float
    kappa0: float
    alpha0: float
    beta0: float


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return value


def load_hourly() -> pd.DataFrame:
    sql = """
        select observation_ts, value
        from canonical_latest
        where series_id = %s
          and observation_ts >= timestamptz '2022-01-01 00:00:00+00'
          and observation_ts < timestamptz '2025-01-01 00:00:00+00'
        order by observation_ts
    """
    with psycopg.connect(_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (SOURCE_SERIES_ID,))
            rows = cur.fetchall()
    frame = pd.DataFrame(rows, columns=["bar_start_utc", "value"])
    frame["bar_start_utc"] = pd.to_datetime(frame["bar_start_utc"], utc=True)
    frame["value"] = pd.to_numeric(frame["value"], errors="raise").astype(float)
    if frame.empty or frame["bar_start_utc"].duplicated().any():
        raise RuntimeError("HOURLY_EMPTY_OR_DUPLICATE")
    if frame["value"].isna().any() or (frame["value"] <= 0).any():
        raise RuntimeError("HOURLY_INVALID_VALUE")
    return apply_session_gate(frame)


def apply_session_gate(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.sort_values("bar_start_utc").drop_duplicates("bar_start_utc").copy()
    local = out["bar_start_utc"].dt.tz_convert(NY_TZ)
    dow = local.dt.dayofweek
    hour = local.dt.hour
    allowed = (
        ((dow == 6) & (hour >= 18))
        | ((dow >= 0) & (dow <= 3) & ((hour <= 16) | (hour >= 18)))
        | ((dow == 4) & (hour <= 16))
    )
    out = out.loc[allowed].copy().reset_index(drop=True)
    out["bar_start_ny"] = out["bar_start_utc"].dt.tz_convert(NY_TZ)
    out["year"] = out["bar_start_ny"].dt.year.astype(int)
    return out


def build_returns(prices: pd.DataFrame) -> pd.DataFrame:
    f = prices.sort_values("bar_start_utc").copy()
    f["prev_ts"] = f["bar_start_utc"].shift(1)
    f["prev_value"] = f["value"].shift(1)
    f["elapsed_hours"] = (f["bar_start_utc"] - f["prev_ts"]).dt.total_seconds() / 3600.0
    f = f[np.isclose(f["elapsed_hours"], 1.0, atol=1e-12)].copy()
    f["raw_log_return"] = np.log(f["value"] / f["prev_value"])
    f["bar_start_ny"] = f["bar_start_utc"].dt.tz_convert(NY_TZ)
    f["bar_start_hour"] = f["bar_start_ny"].dt.hour.astype(int)
    f["local_date"] = f["bar_start_ny"].dt.strftime("%Y-%m-%d")
    f["available_at_utc"] = f["bar_start_utc"] + pd.Timedelta(hours=1)
    f["year"] = f["bar_start_ny"].dt.year.astype(int)
    return f.reset_index(drop=True)


def fit_hour_adjustment(returns: pd.DataFrame) -> pd.DataFrame:
    fit = returns[returns["year"] == FIT_YEAR].copy()
    stats = fit.groupby("bar_start_hour")["raw_log_return"].agg(["count", "mean", "std"]).reset_index()
    if len(stats) < 20 or int(stats["count"].min()) < 100:
        raise RuntimeError("INSUFFICIENT_2022_HOUR_SUPPORT")
    if (stats["std"] <= 0).any():
        raise RuntimeError("INVALID_2022_HOUR_SCALE")
    return stats


def apply_hour_adjustment(returns: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
    out = returns.merge(
        stats[["bar_start_hour", "mean", "std"]],
        on="bar_start_hour",
        how="left",
        validate="many_to_one",
    )
    if out[["mean", "std"]].isna().any().any():
        raise RuntimeError("UNSEEN_HOUR_BUCKET")
    out["adjusted_return"] = (out["raw_log_return"] - out["mean"]) / out["std"]
    return out


def fit_prior(adjusted: pd.DataFrame) -> NIGPrior:
    x = adjusted[adjusted["year"] == FIT_YEAR]["adjusted_return"].astype(float)
    v = float(x.var(ddof=1))
    if len(x) < 4000 or not math.isfinite(v) or v <= 0:
        raise RuntimeError("INVALID_2022_PRIOR")
    return NIGPrior(float(x.mean()), 1.0, 2.0, v)


def load_daily() -> pd.DataFrame:
    sql = """
        select observation_ts, value
        from canonical_latest
        where series_id = %s
          and observation_ts >= timestamptz '2022-02-01 00:00:00+00'
          and observation_ts < timestamptz '2025-01-01 00:00:00+00'
          and extract(isodow from observation_ts at time zone 'America/New_York') between 1 and 5
        order by observation_ts
    """
    with psycopg.connect(_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (DAILY_SERIES_ID,))
            rows = cur.fetchall()
    d = pd.DataFrame(rows, columns=["bar_start_utc", "value"])
    d["bar_start_utc"] = pd.to_datetime(d["bar_start_utc"], utc=True)
    d["value"] = pd.to_numeric(d["value"], errors="raise").astype(float)
    d["bar_start_ny"] = d["bar_start_utc"].dt.tz_convert(NY_TZ)
    d["local_date"] = d["bar_start_ny"].dt.strftime("%Y-%m-%d")
    d["year"] = d["bar_start_ny"].dt.year.astype(int)
    d["available_at_utc"] = d["bar_start_utc"] + pd.Timedelta(hours=1)
    return d.sort_values("bar_start_utc").reset_index(drop=True)


def build_events(daily: pd.DataFrame, year: int) -> pd.DataFrame:
    d = daily.copy().sort_values("bar_start_utc").reset_index(drop=True)
    d["log_return_pct"] = 100.0 * np.log(d["value"] / d["value"].shift(1))
    d["sigma20"] = d["log_return_pct"].shift(1).rolling(20, min_periods=20).std(ddof=1)
    d["z"] = d["log_return_pct"] / d["sigma20"]
    d["is_event"] = d["z"].abs() >= 2.0
    d["previous_daily_available_at_utc"] = d["available_at_utc"].shift(1)
    e = d[(d["year"] == year) & d["is_event"] & d["previous_daily_available_at_utc"].notna()].copy()
    e = e.rename(columns={"available_at_utc": "event_available_at_utc"})
    return e[[
        "local_date",
        "event_available_at_utc",
        "previous_daily_available_at_utc",
        "z",
        "log_return_pct",
    ]].reset_index(drop=True)


def student_t_logpdf_vec(
    x: float,
    mu: np.ndarray,
    kappa: np.ndarray,
    alpha: np.ndarray,
    beta: np.ndarray,
) -> np.ndarray:
    nu = 2.0 * alpha
    scale2 = beta * (kappa + 1.0) / (alpha * kappa)
    z2 = (x - mu) ** 2 / scale2
    return (
        gammaln((nu + 1.0) / 2.0)
        - gammaln(nu / 2.0)
        - 0.5 * (np.log(nu * np.pi) + np.log(scale2))
        - ((nu + 1.0) / 2.0) * np.log1p(z2 / nu)
    )


def update_nig(mu, kappa, alpha, beta, x):
    grown_kappa = kappa + 1.0
    next_mu = (kappa * mu + x) / grown_kappa
    next_kappa = grown_kappa
    next_alpha = alpha + 0.5
    next_beta = beta + 0.5 * kappa * (x - mu) ** 2 / grown_kappa
    return next_mu, next_kappa, next_alpha, next_beta


def run_bocpd(frame: pd.DataFrame, prior: NIGPrior, expected_obs: int) -> pd.DataFrame:
    run_posterior = np.array([1.0], dtype=float)
    mu = np.array([prior.mu0], dtype=float)
    kappa = np.array([prior.kappa0], dtype=float)
    alpha = np.array([prior.alpha0], dtype=float)
    beta = np.array([prior.beta0], dtype=float)
    rows: list[dict] = []
    hazard = 1.0 / float(expected_obs)

    for row in frame.itertuples(index=False):
        x = float(row.adjusted_return)
        previous_map = int(np.argmax(run_posterior))
        log_predictive = student_t_logpdf_vec(x, mu, kappa, alpha, beta)
        log_joint = np.log(np.maximum(run_posterior, 1e-300)) + log_predictive
        shift = float(np.max(log_joint))
        joint_scaled = np.exp(log_joint - shift)
        cp_mass = float(np.sum(joint_scaled * hazard))
        growth_mass = joint_scaled * (1.0 - hazard)
        new_posterior = np.empty(len(run_posterior) + 1, dtype=float)
        new_posterior[0] = cp_mass
        new_posterior[1:] = growth_mass
        new_posterior /= float(new_posterior.sum())

        expected_uninterrupted_run = previous_map + 1
        current_map = int(np.argmax(new_posterior))
        map_reset = current_map < expected_uninterrupted_run
        reset_fraction = max(
            0.0,
            (expected_uninterrupted_run - current_map)
            / float(max(1, expected_uninterrupted_run)),
        )

        gmu, gk, ga, gb = update_nig(mu, kappa, alpha, beta, x)
        next_mu = np.empty(len(mu) + 1, dtype=float)
        next_kappa = np.empty(len(kappa) + 1, dtype=float)
        next_alpha = np.empty(len(alpha) + 1, dtype=float)
        next_beta = np.empty(len(beta) + 1, dtype=float)
        next_mu[0], next_kappa[0], next_alpha[0], next_beta[0] = (
            prior.mu0,
            prior.kappa0,
            prior.alpha0,
            prior.beta0,
        )
        next_mu[1:], next_kappa[1:], next_alpha[1:], next_beta[1:] = (
            gmu,
            gk,
            ga,
            gb,
        )

        rows.append({
            "bar_start_utc": row.bar_start_utc,
            "bar_start_ny": row.bar_start_ny,
            "available_at_utc": row.available_at_utc,
            "local_date": row.local_date,
            "adjusted_return": x,
            "previous_map_run": previous_map,
            "map_run": current_map,
            "map_reset": bool(map_reset),
            "reset_fraction": float(reset_fraction),
            "p_run0": float(new_posterior[0]),
        })
        run_posterior, mu, kappa, alpha, beta = (
            new_posterior,
            next_mu,
            next_kappa,
            next_alpha,
            next_beta,
        )

    return pd.DataFrame(rows)


def cooldown(q: pd.DataFrame) -> pd.DataFrame:
    q = q.sort_values("available_at_utc").reset_index(drop=True)
    keep: list[int] = []
    last = None
    for i, row in q.iterrows():
        ts = pd.Timestamp(row["available_at_utc"])
        if last is None or (ts - last).total_seconds() / 3600.0 >= COOLDOWN_HOURS:
            keep.append(i)
            last = ts
    return q.loc[keep].reset_index(drop=True) if keep else q.iloc[0:0].copy()


def episode_from_reset(timeline: pd.DataFrame, threshold: float) -> pd.DataFrame:
    q = timeline[
        timeline["map_reset"] & (timeline["reset_fraction"] >= threshold)
    ].copy()
    return cooldown(q)


def score_episodes(episodes: pd.DataFrame, events: pd.DataFrame) -> dict:
    ep_times = [pd.Timestamp(v) for v in episodes["available_at_utc"].tolist()]
    matched: set[int] = set()
    captured: set[int] = set()
    leads: list[float] = []

    for ei, e in events.iterrows():
        et = pd.Timestamp(e["event_available_at_utc"])
        prev = pd.Timestamp(e["previous_daily_available_at_utc"])
        candidates = []
        for i, ts in enumerate(ep_times):
            lead = (et - ts).total_seconds() / 3600.0
            if ts <= prev and 0.0 < lead <= WARNING_HOURS:
                candidates.append((i, ts, lead))
        if candidates:
            latest = max(candidates, key=lambda x: x[1])
            captured.add(int(ei))
            leads.append(float(latest[2]))

    for i, ts in enumerate(ep_times):
        for _, e in events.iterrows():
            et = pd.Timestamp(e["event_available_at_utc"])
            prev = pd.Timestamp(e["previous_daily_available_at_utc"])
            lead = (et - ts).total_seconds() / 3600.0
            if ts <= prev and 0.0 < lead <= WARNING_HOURS:
                matched.add(i)
                break

    n_ep, n_ev = len(episodes), len(events)
    precision = len(matched) / n_ep if n_ep else 0.0
    recall = len(captured) / n_ev if n_ev else 0.0
    b2 = BETA * BETA
    f = (
        (1.0 + b2) * precision * recall / (b2 * precision + recall)
        if precision and recall
        else 0.0
    )
    return {
        "episodes": int(n_ep),
        "matched_episodes": int(len(matched)),
        "false_episodes": int(n_ep - len(matched)),
        "events": int(n_ev),
        "captured_events": int(len(captured)),
        "precision": float(precision),
        "recall": float(recall),
        "f0_5": float(f),
        "lead_hours": leads,
    }


def score_key(m: dict, complexity: tuple = ()) -> tuple:
    return (m["f0_5"], -m["episodes"], m["precision"], *complexity)


def validation_frame(adjusted: pd.DataFrame) -> pd.DataFrame:
    return adjusted[
        (adjusted["bar_start_ny"] >= pd.Timestamp("2023-11-01", tz=NY_TZ))
        & (adjusted["bar_start_ny"] < pd.Timestamp("2025-01-01", tz=NY_TZ))
    ].copy()


def evaluate_baseline(adjusted, prior, dev_events, valid_events):
    dev = adjusted[adjusted["year"] == DEV_YEAR].copy()
    grid: list[dict] = []
    for days, obs in zip(HAZARD_DAYS, HAZARD_OBS):
        timeline = run_bocpd(dev, prior, obs)
        for threshold in THRESHOLDS_RESET:
            metrics = score_episodes(
                episode_from_reset(timeline, threshold), dev_events
            )
            grid.append({
                "hazard_days": days,
                "hazard_obs": obs,
                "threshold": threshold,
                **metrics,
            })
    best = max(
        grid,
        key=lambda row: score_key(
            row, (row["threshold"], row["hazard_days"])
        ),
    )
    timeline = run_bocpd(
        validation_frame(adjusted), prior, int(best["hazard_obs"])
    )
    valid_timeline = timeline[
        pd.to_datetime(timeline["bar_start_ny"]).dt.year == VALID_YEAR
    ].copy()
    episodes = episode_from_reset(valid_timeline, float(best["threshold"]))
    return (
        best,
        score_episodes(episodes, valid_events),
        pd.DataFrame(grid),
        episodes,
        valid_timeline,
    )


def main() -> None:
    outdir = Path(os.environ.get("OUTPUT_DIR", "b2_baseline_r2_output"))
    outdir.mkdir(parents=True, exist_ok=True)

    hourly = load_hourly()
    returns = build_returns(hourly)
    hour_stats = fit_hour_adjustment(returns)
    adjusted = apply_hour_adjustment(returns, hour_stats)
    prior = fit_prior(adjusted)
    daily = load_daily()
    dev_events = build_events(daily, DEV_YEAR)
    valid_events = build_events(daily, VALID_YEAR)
    best, validation, grid, episodes, timeline = evaluate_baseline(
        adjusted, prior, dev_events, valid_events
    )

    summary = {
        "identity": IDENTITY_BASE,
        "evidence_class": "PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE",
        "fit_year": FIT_YEAR,
        "development_year": DEV_YEAR,
        "validation_year": VALID_YEAR,
        "2025_used": False,
        "development_selected": best,
        "validation_2024": validation,
        "promotion": "FROZEN_COMPARISON_BASELINE_ONLY",
        "database_model_output_writes": "NONE",
    }
    grid.to_csv(outdir / "baseline_r2_dev_grid_2023.csv", index=False)
    episodes.to_csv(outdir / "baseline_r2_validation_episodes_2024.csv", index=False)
    timeline.to_csv(outdir / "baseline_r2_validation_timeline_2024.csv", index=False)
    (outdir / "baseline_r2_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    print("BASELINE_R2_SUMMARY=" + json.dumps(summary, default=str, sort_keys=True))
    print("NO_2025_DATA_ACCESSED_BY_MODEL_SCRIPT=TRUE")
    print("DATABASE_MODEL_OUTPUT_WRITES=NONE")


if __name__ == "__main__":
    main()
