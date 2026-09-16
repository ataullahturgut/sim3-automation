from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

import bocpd_hourly_b2_successor_pre2025 as base

IDENTITY = "BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH"
EXPECTED_DAYS = [20, 40]
EXPECTED_OBS = [d * 22 for d in EXPECTED_DAYS]
GAMMA_RUN = [0.0, 0.75]
GAMMA_VOL = [0.5, 1.0, 1.5]
VOL_HALFLIFE = [22, 66]
MAX_HAZARD = 0.25


def _logit(p: float) -> float:
    p = min(max(float(p), 1e-12), 1.0 - 1e-12)
    return math.log(p / (1.0 - p))


def _sigmoid(x: np.ndarray) -> np.ndarray:
    out = np.empty_like(x, dtype=float)
    pos = x >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x[pos]))
    ex = np.exp(x[~pos])
    out[~pos] = ex / (1.0 + ex)
    return out


def adaptive_hazard_vector(
    n: int,
    expected_obs: int,
    gamma_run: float,
    gamma_vol: float,
    lagged_vol: float,
) -> np.ndarray:
    """Causal hazard using run length and lagged EWMA volatility only."""
    base_h = 1.0 / float(expected_obs)
    r = np.arange(n, dtype=float)
    duration_feature = np.log1p(r / float(expected_obs))
    vol_feature = math.log(max(float(lagged_vol), 1e-6))
    linear = _logit(base_h) + gamma_run * duration_feature + gamma_vol * vol_feature
    return np.clip(_sigmoid(linear), 1e-8, MAX_HAZARD)


def run_adaptive_bocpd(
    frame: pd.DataFrame,
    prior: base.NIGPrior,
    expected_obs: int,
    gamma_run: float,
    gamma_vol: float,
    vol_halflife: int,
) -> pd.DataFrame:
    run_posterior = np.array([1.0], dtype=float)
    mu = np.array([prior.mu0], dtype=float)
    kappa = np.array([prior.kappa0], dtype=float)
    alpha = np.array([prior.alpha0], dtype=float)
    beta = np.array([prior.beta0], dtype=float)

    decay = math.exp(math.log(0.5) / float(vol_halflife))
    ewma_var = 1.0
    rows: list[dict] = []

    for row in frame.itertuples(index=False):
        x = float(row.adjusted_return)
        lagged_vol = math.sqrt(max(ewma_var, 1e-12))
        previous_map = int(np.argmax(run_posterior))

        log_predictive = base.student_t_logpdf_vec(x, mu, kappa, alpha, beta)
        log_joint = np.log(np.maximum(run_posterior, 1e-300)) + log_predictive
        shift = float(np.max(log_joint))
        joint_scaled = np.exp(log_joint - shift)

        h = adaptive_hazard_vector(
            len(run_posterior), expected_obs, gamma_run, gamma_vol, lagged_vol
        )
        cp_mass = float(np.sum(joint_scaled * h))
        growth_mass = joint_scaled * (1.0 - h)
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

        gmu, gk, ga, gb = base.update_nig(mu, kappa, alpha, beta, x)
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

        rows.append(
            {
                "bar_start_utc": row.bar_start_utc,
                "bar_start_ny": row.bar_start_ny,
                "available_at_utc": row.available_at_utc,
                "local_date": row.local_date,
                "adjusted_return": x,
                "lagged_ewma_vol": float(lagged_vol),
                "hazard_at_map": float(h[min(previous_map, len(h) - 1)]),
                "previous_map_run": previous_map,
                "map_run": current_map,
                "map_reset": bool(map_reset),
                "reset_fraction": float(reset_fraction),
                "p_run0": float(new_posterior[0]),
            }
        )

        ewma_var = decay * ewma_var + (1.0 - decay) * (x * x)
        run_posterior, mu, kappa, alpha, beta = (
            new_posterior,
            next_mu,
            next_kappa,
            next_alpha,
            next_beta,
        )

    return pd.DataFrame(rows)


def evaluate(adjusted, prior, dev_events, valid_events):
    dev = adjusted[adjusted["year"] == base.DEV_YEAR].copy()
    grid: list[dict] = []
    best = None
    best_key = None

    for days, obs in zip(EXPECTED_DAYS, EXPECTED_OBS):
        for gamma_run in GAMMA_RUN:
            for gamma_vol in GAMMA_VOL:
                for half_life in VOL_HALFLIFE:
                    tl = run_adaptive_bocpd(
                        dev, prior, obs, gamma_run, gamma_vol, half_life
                    )
                    for thr in base.THRESHOLDS_RESET:
                        ep = base.episode_from_reset(tl, thr)
                        m = base.score_episodes(ep, dev_events)
                        row = {
                            "hazard_days": days,
                            "hazard_obs": obs,
                            "gamma_run": gamma_run,
                            "gamma_vol": gamma_vol,
                            "vol_halflife": half_life,
                            "threshold": thr,
                            **m,
                        }
                        grid.append(row)
                        key = base.score_key(
                            m,
                            (
                                -abs(gamma_run),
                                -abs(gamma_vol),
                                -half_life,
                                -days,
                            ),
                        )
                        if best_key is None or key > best_key:
                            best_key = key
                            best = row

    assert best is not None

    val_frame = base.validation_frame(adjusted)
    val_tl = run_adaptive_bocpd(
        val_frame,
        prior,
        int(best["hazard_obs"]),
        float(best["gamma_run"]),
        float(best["gamma_vol"]),
        int(best["vol_halflife"]),
    )
    val_tl = val_tl[pd.to_datetime(val_tl["bar_start_ny"]).dt.year == base.VALID_YEAR].copy()
    ep = base.episode_from_reset(val_tl, float(best["threshold"]))
    val_score = base.score_episodes(ep, valid_events)
    return best, val_score, pd.DataFrame(grid), ep, val_tl


def main() -> None:
    outdir = Path(os.environ.get("OUTPUT_DIR", "b2_adaptive_hazard_output"))
    outdir.mkdir(parents=True, exist_ok=True)

    hourly = base.load_hourly()
    returns = base.build_returns(hourly)
    hour_stats = base.fit_hour_adjustment(returns)
    adjusted = base.apply_hour_adjustment(returns, hour_stats)
    prior = base.fit_prior(adjusted)
    daily = base.load_daily()
    dev_events = base.build_events(daily, base.DEV_YEAR)
    valid_events = base.build_events(daily, base.VALID_YEAR)

    baseline_best, baseline_val, _, _, _ = base.evaluate_baseline(
        adjusted, prior, dev_events, valid_events
    )
    best, val_score, grid, episodes, timeline = evaluate(
        adjusted, prior, dev_events, valid_events
    )

    winner = (
        IDENTITY
        if (
            val_score["f0_5"],
            val_score["precision"],
            val_score["recall"],
            -val_score["episodes"],
        )
        > (
            baseline_val["f0_5"],
            baseline_val["precision"],
            baseline_val["recall"],
            -baseline_val["episodes"],
        )
        else base.IDENTITY_BASE
    )

    summary = {
        "evidence_class": "PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE",
        "identity": IDENTITY,
        "fit_year": base.FIT_YEAR,
        "development_year": base.DEV_YEAR,
        "validation_year": base.VALID_YEAR,
        "2025_used": False,
        "hazard_design": "causal logistic hazard from run length and lagged EWMA volatility",
        "development_selected": best,
        "validation_2024": val_score,
        "baseline_dev_selected": baseline_best,
        "baseline_validation_2024": baseline_val,
        "validation_comparison_winner": winner,
        "promotion": "NONE_AUTOMATIC",
        "database_model_output_writes": "NONE",
    }

    grid.to_csv(outdir / "adaptive_hazard_dev_grid_2023.csv", index=False)
    episodes.to_csv(outdir / "adaptive_hazard_validation_episodes_2024.csv", index=False)
    timeline.to_csv(outdir / "adaptive_hazard_validation_timeline_2024.csv", index=False)
    (outdir / "adaptive_hazard_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    print("ADAPTIVE_HAZARD_SUMMARY=" + json.dumps(summary, sort_keys=True, default=str))
    print("NO_2025_DATA_ACCESSED_BY_MODEL_SCRIPT=TRUE")
    print("DATABASE_MODEL_OUTPUT_WRITES=NONE")


if __name__ == "__main__":
    main()
