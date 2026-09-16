from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

IDENTITY = "BOCPD_DAILY_RETURN_SUCCESSOR_V2_RESEARCH"
SOURCE_SERIES_ID = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
HAZARD_CANDIDATES = (20, 40, 60, 120)


@dataclass(frozen=True)
class NIGPrior:
    mu0: float
    kappa0: float
    alpha0: float
    beta0: float


def student_t_logpdf(x: float, mu: float, kappa: float, alpha: float, beta: float) -> float:
    nu = 2.0 * alpha
    scale2 = beta * (kappa + 1.0) / (alpha * kappa)
    if not (nu > 0.0 and scale2 > 0.0 and math.isfinite(scale2)):
        raise RuntimeError("invalid Student-t predictive parameters")
    z2 = (x - mu) ** 2 / scale2
    return (
        math.lgamma((nu + 1.0) / 2.0)
        - math.lgamma(nu / 2.0)
        - 0.5 * (math.log(nu * math.pi) + math.log(scale2))
        - ((nu + 1.0) / 2.0) * math.log1p(z2 / nu)
    )


def load_prices(path: Path) -> pd.Series:
    frame = pd.read_csv(path)
    required = {"date", "value"}
    if not required.issubset(frame.columns):
        raise RuntimeError("input must contain date,value columns")
    frame["date"] = pd.to_datetime(frame["date"], utc=True).dt.tz_convert(None).dt.normalize()
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"]).sort_values("date")
    frame = frame[frame["date"].dt.dayofweek < 5]
    if frame["date"].duplicated().any():
        raise RuntimeError("duplicate governed date")
    if (frame["value"] <= 0).any() or not np.isfinite(frame["value"].to_numpy(dtype=float)).all():
        raise RuntimeError("invalid price")
    return frame.set_index("date")["value"].astype(float)


def daily_log_returns(price: pd.Series) -> pd.Series:
    ret = np.log(price / price.shift(1)).dropna()
    ret.name = "log_return"
    return ret


def fit_prior(returns: pd.Series) -> NIGPrior:
    dev = returns.loc["2023-01-01":"2023-12-31"]
    if len(dev) < 150:
        raise RuntimeError("insufficient 2023 prior-fit support")
    variance = float(dev.var(ddof=1))
    if not math.isfinite(variance) or variance <= 0:
        raise RuntimeError("invalid 2023 variance")
    return NIGPrior(float(dev.mean()), 1.0, 2.0, variance)


def run_bocpd(returns: pd.Series, prior: NIGPrior, expected_run_days: int) -> tuple[pd.DataFrame, float]:
    hazard = 1.0 / float(expected_run_days)
    run_posterior = np.array([1.0], dtype=float)
    mu = np.array([prior.mu0], dtype=float)
    kappa = np.array([prior.kappa0], dtype=float)
    alpha = np.array([prior.alpha0], dtype=float)
    beta = np.array([prior.beta0], dtype=float)
    log_evidence = 0.0
    rows: list[dict] = []

    for date, raw_x in returns.items():
        x = float(raw_x)
        previous_map = int(np.argmax(run_posterior))
        log_predictive = np.array(
            [student_t_logpdf(x, float(m), float(k), float(a), float(b)) for m, k, a, b in zip(mu, kappa, alpha, beta)],
            dtype=float,
        )
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
            "date": pd.Timestamp(date),
            "log_return": x,
            "previous_map_run": previous_map,
            "expected_uninterrupted_run": expected_uninterrupted_run,
            "map_run": current_map,
            "map_reset": bool(map_reset),
            "reset_fraction": float(reset_fraction),
            "p_run0": float(new_posterior[0]),
            "state": "REGIME_CHANGE_CANDIDATE" if map_reset else "NO_CHANGE_CANDIDATE",
        })
        run_posterior, mu, kappa, alpha, beta = new_posterior, next_mu, next_kappa, next_alpha, next_beta

    return pd.DataFrame(rows).set_index("date"), log_evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True, type=Path, help="Neon export of governed source series with date,value columns")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    price = load_prices(args.input_csv)
    returns = daily_log_returns(price)
    prior = fit_prior(returns)
    formation = returns.loc["2024-01-01":"2024-12-31"]

    evidence: dict[int, float] = {}
    for expected_run in HAZARD_CANDIDATES:
        _, score = run_bocpd(formation, prior, expected_run)
        evidence[expected_run] = float(score)
    selected = max(evidence, key=evidence.get)

    replay = returns.loc["2024-01-01":"2025-12-31"]
    rows, _ = run_bocpd(replay, prior, selected)
    challenge = rows.loc["2025-01-01":"2025-12-31"].copy()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    challenge.to_csv(args.output_dir / "bocpd_daily_v2_2025_full_timeline.csv", index=True)
    challenge.loc[challenge["map_reset"]].to_csv(args.output_dir / "bocpd_daily_v2_2025_reset_dates.csv", index=True)
    summary = {
        "identity": IDENTITY,
        "source_series_id": SOURCE_SERIES_ID,
        "prior_fit": "2023",
        "formation_validation": "2024",
        "challenge": "2025",
        "hazard_candidates": list(HAZARD_CANDIDATES),
        "formation_log_evidence": {str(k): v for k, v in evidence.items()},
        "selected_expected_run_days": int(selected),
        "challenge_rows": int(len(challenge)),
        "challenge_map_reset_days": int(challenge["map_reset"].sum()),
        "direction_vote_permitted": False,
        "evidence_class": "HISTORICAL_REPLAY_RETROSPECTIVE_DIAGNOSTIC",
    }
    (args.output_dir / "bocpd_daily_v2_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
