from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

import bocpd_hourly_candidate_b_v1_r1 as base

IDENTITY = "BOCPD_HOURLY_POSTERIOR_MASS_CANDIDATE_B2_V1_RESEARCH"
SHORT_RUN_K = 22
THRESHOLD_GRID = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.975, 0.99]
EXPECTED_RUN_DAYS = [20, 40, 60, 120]
EXPECTED_RUN_OBS = [d * 22 for d in EXPECTED_RUN_DAYS]


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


def run_bocpd_with_short_mass(frame: pd.DataFrame, prior: base.NIGPrior, expected_run_obs: int) -> tuple[pd.DataFrame, float]:
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

        current_map = int(np.argmax(new_posterior))
        upper = min(SHORT_RUN_K, len(new_posterior) - 1)
        short_run_mass = float(new_posterior[: upper + 1].sum())
        map_reset = current_map < (previous_map + 1)

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

        rows.append(
            {
                "bar_start_utc": row.bar_start_utc,
                "bar_start_ny": row.bar_start_ny,
                "available_at_utc": row.available_at_utc,
                "local_date": row.local_date,
                "bar_start_hour": int(row.bar_start_hour),
                "adjusted_return": x,
                "previous_map_run": previous_map,
                "map_run": current_map,
                "map_reset": bool(map_reset),
                "short_run_mass_k22": short_run_mass,
            }
        )
        run_posterior, mu, kappa, alpha, beta = new_posterior, next_mu, next_kappa, next_alpha, next_beta

    return pd.DataFrame(rows), float(log_evidence)


def alarm_onsets(timeline: pd.DataFrame, q: float) -> pd.DataFrame:
    t = timeline.copy()
    t["prev_short_run_mass"] = t["short_run_mass_k22"].shift(1)
    t["prev_map_run_for_alarm"] = t["map_run"].shift(1)
    t["alarm_onset"] = (
        (t["short_run_mass_k22"] >= q)
        & (t["prev_short_run_mass"] < q)
        & (t["prev_map_run_for_alarm"] >= SHORT_RUN_K)
    )
    return t[t["alarm_onset"]].copy()


def main() -> None:
    out_dir = Path(os.environ.get("OUTPUT_DIR", "candidate_b2_calibration_output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    formation_prices = base.load_formation_prices()
    returns = base.build_returns(formation_prices)
    hour_stats = base.fit_hour_adjustment(returns)
    adjusted = base.apply_hour_adjustment(returns, hour_stats)
    prior = base.fit_prior(adjusted)

    counts = {
        "2023": int((adjusted["bar_start_ny"].dt.year == 2023).sum()),
        "2024": int((adjusted["bar_start_ny"].dt.year == 2024).sum()),
    }
    if counts != {"2023": 5579, "2024": 5650}:
        raise RuntimeError(f"PRE2025_ELIGIBLE_COUNT_MISMATCH:{counts}")

    y2024 = adjusted[adjusted["bar_start_ny"].dt.year == 2024].copy().reset_index(drop=True)

    evidence = {}
    reset_counts = {}
    timelines = {}
    for days, obs in zip(EXPECTED_RUN_DAYS, EXPECTED_RUN_OBS):
        timeline, score = run_bocpd_with_short_mass(y2024, prior, obs)
        evidence[obs] = float(score)
        reset_counts[obs] = int(timeline["map_reset"].sum())
        timelines[obs] = timeline
        print(f"HAZARD_CANDIDATE expected_days={days} expected_obs={obs} log_evidence={score:.9f} map_resets={reset_counts[obs]}")

    selected_obs = max(evidence, key=evidence.get)
    selected_days = EXPECTED_RUN_DAYS[EXPECTED_RUN_OBS.index(selected_obs)]
    selected_timeline = timelines[selected_obs]
    target_spacing = float(selected_obs)
    print(f"HAZARD_SELECTED expected_days={selected_days} expected_obs={selected_obs} hazard={1.0/selected_obs:.12f}")

    calibration_rows = []
    selected_q = None
    selected_onsets = None
    for q in THRESHOLD_GRID:
        onsets = alarm_onsets(selected_timeline, q)
        n = int(len(onsets))
        spacing = float("inf") if n == 0 else float(len(selected_timeline) / n)
        calibration_rows.append(
            {
                "threshold": q,
                "alarm_onsets_2024": n,
                "unique_alarm_dates_2024": int(onsets["local_date"].nunique()) if n else 0,
                "arl_proxy_observations": spacing,
                "target_spacing_observations": target_spacing,
                "passes_spacing_rule": bool(spacing >= target_spacing),
            }
        )
        print(
            f"THRESHOLD q={q:.3f} alarm_onsets={n} "
            f"unique_dates={int(onsets['local_date'].nunique()) if n else 0} "
            f"arl_proxy={'INF' if math.isinf(spacing) else f'{spacing:.3f}'} "
            f"target={target_spacing:.0f} pass={spacing >= target_spacing}"
        )
        if selected_q is None and spacing >= target_spacing:
            selected_q = q
            selected_onsets = onsets

    if selected_q is None:
        raise RuntimeError("THRESHOLD_CALIBRATION_FAIL_NO_GRID_VALUE_MEETS_SPACING")

    selected_zero_onsets = bool(len(selected_onsets) == 0)
    print(
        f"THRESHOLD_SELECTED q={selected_q:.3f} alarm_onsets={len(selected_onsets)} "
        f"zero_onsets={selected_zero_onsets} target_spacing={target_spacing:.0f}"
    )

    selected_timeline.to_csv(out_dir / "candidate_b2_2024_full_timeline.csv", index=False)
    pd.DataFrame(calibration_rows).to_csv(out_dir / "candidate_b2_threshold_calibration.csv", index=False)
    selected_onsets.to_csv(out_dir / "candidate_b2_2024_selected_alarm_onsets.csv", index=False)
    hour_stats.to_csv(out_dir / "candidate_b2_2023_hour_adjustment.csv", index=False)

    summary = {
        "identity": IDENTITY,
        "phase": "PRE2025_CALIBRATION_ONLY",
        "challenge_2025_accessed": False,
        "eligible_returns": counts,
        "short_run_k": SHORT_RUN_K,
        "hazard_candidate_expected_days": EXPECTED_RUN_DAYS,
        "hazard_candidate_expected_obs": EXPECTED_RUN_OBS,
        "hazard_log_evidence_2024": {str(k): v for k, v in evidence.items()},
        "hazard_map_resets_2024": {str(k): v for k, v in reset_counts.items()},
        "selected_expected_run_days": selected_days,
        "selected_expected_run_obs": selected_obs,
        "selected_hazard": 1.0 / selected_obs,
        "threshold_grid": THRESHOLD_GRID,
        "threshold_selection_rule": "SMALLEST_Q_WITH_ARL_PROXY_GTE_SELECTED_EXPECTED_RUN_OBS",
        "selected_threshold": selected_q,
        "selected_alarm_onsets_2024": int(len(selected_onsets)),
        "selected_unique_alarm_dates_2024": int(selected_onsets["local_date"].nunique()) if len(selected_onsets) else 0,
        "selected_zero_onsets": selected_zero_onsets,
        "selected_arl_proxy": float("inf") if len(selected_onsets) == 0 else float(len(selected_timeline) / len(selected_onsets)),
        "arl_proxy_is_formal_null_arl0": False,
        "prior": {"mu0": prior.mu0, "kappa0": prior.kappa0, "alpha0": prior.alpha0, "beta0": prior.beta0},
        "production_promotion": "NOT_PROVEN",
    }
    (out_dir / "candidate_b2_pre2025_calibration_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )
    print("B2_PRE2025_CALIBRATION_SUMMARY=" + json.dumps(summary, sort_keys=True, default=str))
    print("B2_PRE2025_CALIBRATION_COMPLETE")


if __name__ == "__main__":
    main()
