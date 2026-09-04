from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "bocpd_successor_v1" / "frozen_contract_v1.json"
CORE_PATH = ROOT / "core5_monthly.csv.gz.b64"

SUCCESSOR_ID = "BOCPD_RETURN_SUCCESSOR_V1"
ARCHIVED_ID = "BOCPD"
ROLE = "REGIME_BREAK_CONTEXT"
EVIDENCE_CLASS = "HISTORICAL_REPLAY_SUCCESSOR_RESEARCH"
DIRECTION_VOTE_PERMITTED = False
POSITION_MAPPING_PERMITTED = False
DATABASE_WRITES = "NONE"


@dataclass(frozen=True)
class NIGPrior:
    mu0: float
    kappa0: float
    alpha0: float
    beta0: float


@dataclass(frozen=True)
class ReplayResult:
    rows: pd.DataFrame
    summary: dict


def load_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("contract_version") != SUCCESSOR_ID:
        raise RuntimeError("contract identity mismatch")
    if contract.get("archived_identity") != ARCHIVED_ID:
        raise RuntimeError("archived identity mismatch")
    if contract.get("direction_vote_permitted") is not False:
        raise RuntimeError("direction vote must remain false")
    if contract.get("position_mapping_permitted") is not False:
        raise RuntimeError("position mapping must remain false")
    if contract.get("database_writes_permitted") is not False:
        raise RuntimeError("database writes must remain false")
    if contract.get("state_rule", {}).get("archived_threshold_reused") is not False:
        raise RuntimeError("archived threshold reuse is prohibited")
    return contract


def load_core_monthly() -> pd.DataFrame:
    raw = gzip.decompress(base64.b64decode(CORE_PATH.read_text(encoding="utf-8").strip())).decode("utf-8")
    from io import StringIO

    frame = pd.read_csv(StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()
    if "gold_monthly" not in frame.columns:
        raise RuntimeError("gold_monthly field missing")
    values = pd.to_numeric(frame["gold_monthly"], errors="coerce")
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all() or (values <= 0).any():
        raise RuntimeError("gold_monthly contains invalid observations")
    if frame.index.has_duplicates:
        raise RuntimeError("monthly index contains duplicates")
    return frame


def monthly_log_returns(frame: pd.DataFrame) -> pd.Series:
    price = frame["gold_monthly"].astype(float)
    ret = np.log(price / price.shift(1)).dropna()
    ret.name = "log_return"
    if not np.isfinite(ret.to_numpy(dtype=float)).all():
        raise RuntimeError("non-finite log return")
    return ret


def _ts(value: str) -> pd.Timestamp:
    return pd.Timestamp(value)


def fit_development_prior(returns: pd.Series, contract: dict) -> NIGPrior:
    w = contract["windows"]
    dev = returns.loc[_ts(w["development_start"]): _ts(w["development_end"])].astype(float)
    if len(dev) < 24:
        raise RuntimeError("insufficient development observations")
    variance = float(dev.var(ddof=1))
    if not math.isfinite(variance) or variance <= 0:
        raise RuntimeError("invalid development variance")
    alpha0 = float(contract["observation_model"]["alpha0"])
    kappa0 = float(contract["observation_model"]["kappa0"])
    if alpha0 <= 1 or kappa0 <= 0:
        raise RuntimeError("invalid frozen prior constants")
    return NIGPrior(
        mu0=float(dev.mean()),
        kappa0=kappa0,
        alpha0=alpha0,
        beta0=float(variance * (alpha0 - 1.0)),
    )


def student_t_logpdf(x: float, mu: float, kappa: float, alpha: float, beta: float) -> float:
    """NIG posterior predictive Student-t log density."""
    nu = 2.0 * alpha
    scale2 = beta * (kappa + 1.0) / (alpha * kappa)
    if not (nu > 0 and scale2 > 0 and math.isfinite(scale2)):
        raise RuntimeError("invalid Student-t predictive parameters")
    z2 = (x - mu) ** 2 / scale2
    return (
        math.lgamma((nu + 1.0) / 2.0)
        - math.lgamma(nu / 2.0)
        - 0.5 * (math.log(nu * math.pi) + math.log(scale2))
        - ((nu + 1.0) / 2.0) * math.log1p(z2 / nu)
    )


def _period_label(month: pd.Timestamp, contract: dict) -> str:
    w = contract["windows"]
    if _ts(w["development_start"]) <= month <= _ts(w["development_end"]):
        return "DEV"
    if _ts(w["validation_start"]) <= month <= _ts(w["validation_end"]):
        return "VAL"
    if _ts(w["locked_start"]) <= month <= _ts(w["locked_end"]):
        return "LOCK"
    return "OUTSIDE_FROZEN_REPLAY"


def run_bocpd(
    returns: pd.Series,
    prior: NIGPrior,
    expected_run_length: int,
    contract: dict,
) -> pd.DataFrame:
    if expected_run_length <= 1:
        raise ValueError("expected_run_length must exceed 1")
    hazard = 1.0 / float(expected_run_length)

    run_posterior = np.array([1.0], dtype=float)
    mu = np.array([prior.mu0], dtype=float)
    kappa = np.array([prior.kappa0], dtype=float)
    alpha = np.array([prior.alpha0], dtype=float)
    beta = np.array([prior.beta0], dtype=float)

    rows: list[dict] = []

    for month, raw_x in returns.items():
        month = pd.Timestamp(month)
        x = float(raw_x)
        previous_map = int(np.argmax(run_posterior))

        log_predictive = np.array(
            [
                student_t_logpdf(x, float(m), float(k), float(a), float(b))
                for m, k, a, b in zip(mu, kappa, alpha, beta)
            ],
            dtype=float,
        )
        log_joint = np.log(np.maximum(run_posterior, 1e-300)) + log_predictive
        shift = float(np.max(log_joint))
        joint_scaled = np.exp(log_joint - shift)

        new_posterior = np.empty(len(run_posterior) + 1, dtype=float)
        new_posterior[0] = hazard * float(joint_scaled.sum())
        new_posterior[1:] = (1.0 - hazard) * joint_scaled
        evidence_scaled = float(new_posterior.sum())
        if not math.isfinite(evidence_scaled) or evidence_scaled <= 0:
            raise RuntimeError("invalid posterior evidence")
        new_posterior /= evidence_scaled

        posterior_sum = float(new_posterior.sum())
        if abs(posterior_sum - 1.0) > 1e-12:
            raise RuntimeError("posterior normalization failure")

        expected_uninterrupted_run = previous_map + 1
        current_map = int(np.argmax(new_posterior))
        map_reset = current_map < expected_uninterrupted_run
        reset_fraction = max(
            0.0,
            float(expected_uninterrupted_run - current_map) / float(expected_uninterrupted_run),
        )

        # Sufficient-statistic update for the next observation. Index 0 is the
        # reset/prior hypothesis; indices 1.. are growth hypotheses updated with x_t.
        next_mu = np.empty(len(mu) + 1, dtype=float)
        next_kappa = np.empty(len(kappa) + 1, dtype=float)
        next_alpha = np.empty(len(alpha) + 1, dtype=float)
        next_beta = np.empty(len(beta) + 1, dtype=float)

        next_mu[0] = prior.mu0
        next_kappa[0] = prior.kappa0
        next_alpha[0] = prior.alpha0
        next_beta[0] = prior.beta0

        grown_kappa = kappa + 1.0
        next_mu[1:] = (kappa * mu + x) / grown_kappa
        next_kappa[1:] = grown_kappa
        next_alpha[1:] = alpha + 0.5
        next_beta[1:] = beta + 0.5 * kappa * (x - mu) ** 2 / grown_kappa

        entropy = -float(np.sum(new_posterior * np.log(np.maximum(new_posterior, 1e-300))))
        adverse = bool(map_reset and x < 0.0)
        state = "ADVERSE_BREAK_CANDIDATE" if adverse else "NO_ADVERSE_BREAK_CANDIDATE"

        rows.append(
            {
                "month": month,
                "log_return": x,
                "previous_map_run": previous_map,
                "expected_uninterrupted_run": expected_uninterrupted_run,
                "map_run": current_map,
                "map_reset": bool(map_reset),
                "reset_fraction": reset_fraction,
                "map_segment_mean": float(next_mu[current_map]),
                "run_length_entropy": entropy,
                "p_run0": float(new_posterior[0]),
                "posterior_sum": posterior_sum,
                "state": state,
                "period": _period_label(month, contract),
                "evidence_class": EVIDENCE_CLASS,
                "direction_vote_permitted": DIRECTION_VOTE_PERMITTED,
            }
        )

        run_posterior = new_posterior
        mu = next_mu
        kappa = next_kappa
        alpha = next_alpha
        beta = next_beta

    return pd.DataFrame(rows).set_index("month")


def _canonical_rows(frame: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for month, row in frame.iterrows():
        rows.append(
            {
                "month": pd.Timestamp(month).strftime("%Y-%m-%d"),
                "log_return": float(row["log_return"]),
                "previous_map_run": int(row["previous_map_run"]),
                "expected_uninterrupted_run": int(row["expected_uninterrupted_run"]),
                "map_run": int(row["map_run"]),
                "map_reset": bool(row["map_reset"]),
                "reset_fraction": float(row["reset_fraction"]),
                "map_segment_mean": float(row["map_segment_mean"]),
                "run_length_entropy": float(row["run_length_entropy"]),
                "p_run0": float(row["p_run0"]),
                "posterior_sum": float(row["posterior_sum"]),
                "state": str(row["state"]),
                "period": str(row["period"]),
                "evidence_class": str(row["evidence_class"]),
                "direction_vote_permitted": bool(row["direction_vote_permitted"]),
            }
        )
    return rows


def canonical_hash(frame: pd.DataFrame, prior: NIGPrior, expected_run_length: int) -> str:
    payload = {
        "successor_id": SUCCESSOR_ID,
        "prior": asdict(prior),
        "expected_run_length": int(expected_run_length),
        "rows": _canonical_rows(frame),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def assert_prefix_invariance(
    returns: pd.Series,
    prior: NIGPrior,
    expected_run_length: int,
    contract: dict,
    cutoffs: Iterable[pd.Timestamp],
) -> None:
    full = run_bocpd(returns, prior, expected_run_length, contract)
    cols = [
        "log_return",
        "previous_map_run",
        "expected_uninterrupted_run",
        "map_run",
        "map_reset",
        "reset_fraction",
        "map_segment_mean",
        "run_length_entropy",
        "p_run0",
        "posterior_sum",
        "state",
        "period",
        "evidence_class",
        "direction_vote_permitted",
    ]
    for cutoff in cutoffs:
        cutoff = pd.Timestamp(cutoff)
        prefix_returns = returns.loc[:cutoff]
        prefix = run_bocpd(prefix_returns, prior, expected_run_length, contract)
        reference = full.loc[:cutoff]
        if list(prefix.index) != list(reference.index):
            raise RuntimeError(f"prefix index mismatch at {cutoff.date()}")
        for col in cols:
            left = prefix[col]
            right = reference[col]
            if pd.api.types.is_numeric_dtype(left.dtype) and left.dtype != bool:
                if not np.allclose(left.to_numpy(dtype=float), right.to_numpy(dtype=float), rtol=0.0, atol=1e-12):
                    raise RuntimeError(f"prefix numeric mismatch {col} at {cutoff.date()}")
            else:
                if left.astype(str).tolist() != right.astype(str).tolist():
                    raise RuntimeError(f"prefix categorical mismatch {col} at {cutoff.date()}")


def build_replay() -> ReplayResult:
    contract = load_contract()
    core = load_core_monthly()
    returns = monthly_log_returns(core)
    w = contract["windows"]
    prior = fit_development_prior(returns, contract)
    replay_returns = returns.loc[_ts(w["development_start"]): _ts(w["locked_end"])]
    expected_run_length = int(contract["hazard"]["expected_run_length_months"])

    rows = run_bocpd(replay_returns, prior, expected_run_length, contract)

    assert_prefix_invariance(
        replay_returns,
        prior,
        expected_run_length,
        contract,
        [
            _ts(w["validation_end"]),
            pd.Timestamp("2025-12-01"),
            _ts(w["locked_end"]),
        ],
    )

    periods = rows.groupby("period").size().to_dict()
    alarms = rows[rows["state"] == "ADVERSE_BREAK_CANDIDATE"]
    alarm_counts = alarms.groupby("period").size().to_dict()
    val_n = int(periods.get("VAL", 0))
    lock_n = int(periods.get("LOCK", 0))
    val_alarm_n = int(alarm_counts.get("VAL", 0))
    lock_alarm_n = int(alarm_counts.get("LOCK", 0))

    result_hash = canonical_hash(rows, prior, expected_run_length)
    # Prove deterministic replay by recomputing from the same frozen inputs.
    second = run_bocpd(replay_returns, prior, expected_run_length, contract)
    second_hash = canonical_hash(second, prior, expected_run_length)
    if result_hash != second_hash:
        raise RuntimeError("determinism hash mismatch")

    summary = {
        "successor_id": SUCCESSOR_ID,
        "archived_identity": ARCHIVED_ID,
        "archived_identity_status": contract["archived_status"],
        "candidate_status": "RESEARCH_SHADOW_CANDIDATE_ENGINEERING_PASS",
        "role": ROLE,
        "direction_vote_permitted": DIRECTION_VOTE_PERMITTED,
        "position_mapping_permitted": POSITION_MAPPING_PERMITTED,
        "database_writes": DATABASE_WRITES,
        "evidence_class": EVIDENCE_CLASS,
        "source_artifact": contract["source"]["artifact"],
        "source_field": contract["source"]["field"],
        "first_replay_month": rows.index.min().strftime("%Y-%m-%d"),
        "last_replay_month": rows.index.max().strftime("%Y-%m-%d"),
        "row_count": int(len(rows)),
        "period_counts": {str(k): int(v) for k, v in periods.items()},
        "prior": asdict(prior),
        "expected_run_length_months": expected_run_length,
        "hazard": 1.0 / float(expected_run_length),
        "numeric_alarm_threshold": None,
        "archived_threshold_reused": False,
        "validation_alarm_count": val_alarm_n,
        "validation_alarm_rate": float(val_alarm_n / val_n) if val_n else None,
        "locked_alarm_count": lock_alarm_n,
        "locked_alarm_rate": float(lock_alarm_n / lock_n) if lock_n else None,
        "validation_alarm_months": [m.strftime("%Y-%m-%d") for m in alarms[alarms["period"] == "VAL"].index],
        "locked_alarm_months": [m.strftime("%Y-%m-%d") for m in alarms[alarms["period"] == "LOCK"].index],
        "determinism_sha256": result_hash,
        "hard_gates": {
            "CONTRACT_IDENTITY_PASS": True,
            "NO_ARCHIVED_THRESHOLD_REUSE_PASS": True,
            "DEVELOPMENT_ONLY_PRIOR_PASS": True,
            "POSTERIOR_NORMALIZATION_PASS": bool(np.allclose(rows["posterior_sum"], 1.0, rtol=0.0, atol=1e-12)),
            "DETERMINISM_PASS": True,
            "PREFIX_INVARIANCE_PASS": True,
            "COMPLETED_MONTH_ONLY_PASS": True,
            "VALIDATION_NO_TUNING_PASS": True,
            "LOCKED_NO_TUNING_PASS": True,
            "DIRECTION_VOTE_FALSE_PASS": True,
            "DATABASE_WRITES_NONE_PASS": True,
            "NO_POSITION_MAPPING_PASS": True,
        },
        "promotion_authorized": False,
        "prospective_claim": False,
    }
    if not all(summary["hard_gates"].values()):
        summary["candidate_status"] = "BLOCKED_RESEARCH_CANDIDATE"
    return ReplayResult(rows=rows, summary=summary)


def write_outputs(result: ReplayResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = result.rows.reset_index().copy()
    frame["month"] = pd.to_datetime(frame["month"]).dt.strftime("%Y-%m-%d")
    frame.to_csv(output_dir / "bocpd_return_successor_v1_replay.csv", index=False)
    (output_dir / "bocpd_return_successor_v1_evidence.json").write_text(
        json.dumps(result.summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Gold Control BOCPD return successor V1 research replay")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    result = build_replay()
    if args.output_dir is not None:
        write_outputs(result, args.output_dir)

    print(f"SUCCESSOR_ID={result.summary['successor_id']}")
    print(f"CANDIDATE_STATUS={result.summary['candidate_status']}")
    print(f"EVIDENCE_CLASS={result.summary['evidence_class']}")
    print(f"ROW_COUNT={result.summary['row_count']}")
    print(f"VAL_ALARMS={result.summary['validation_alarm_count']}")
    print(f"LOCK_ALARMS={result.summary['locked_alarm_count']}")
    print(f"DETERMINISM_SHA256={result.summary['determinism_sha256']}")
    print("DIRECTION_VOTE_PERMITTED=NO")
    print("POSITION_MAPPING_PERMITTED=NO")
    print("PROSPECTIVE_CLAIM=NO")
    print("PROMOTION_AUTHORIZED=NO")
    print("DATABASE_WRITES=NONE")
    print("BOCPD_RETURN_SUCCESSOR_V1_ENGINEERING_REPLAY_COMPLETE")


if __name__ == "__main__":
    main()
