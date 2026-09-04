from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from bocpd_return_successor_v1 import (
    ARCHIVED_ID,
    CONTRACT_PATH,
    DIRECTION_VOTE_PERMITTED,
    NIGPrior,
    POSITION_MAPPING_PERMITTED,
    SUCCESSOR_ID,
    assert_prefix_invariance,
    build_replay,
    canonical_hash,
    fit_development_prior,
    load_contract,
    load_core_monthly,
    monthly_log_returns,
    run_bocpd,
    student_t_logpdf,
)


def test_contract_identity_and_global_locks():
    contract = load_contract()
    assert SUCCESSOR_ID == "BOCPD_RETURN_SUCCESSOR_V1"
    assert ARCHIVED_ID == "BOCPD"
    assert SUCCESSOR_ID != ARCHIVED_ID
    assert contract["contract_version"] == SUCCESSOR_ID
    assert contract["archived_identity"] == ARCHIVED_ID
    assert contract["archived_status"].startswith("BLOCKED_")
    assert contract["direction_vote_permitted"] is False
    assert contract["position_mapping_permitted"] is False
    assert contract["database_writes_permitted"] is False
    assert DIRECTION_VOTE_PERMITTED is False
    assert POSITION_MAPPING_PERMITTED is False


def test_archived_threshold_is_not_reused():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert contract["state_rule"]["numeric_alarm_threshold"] is None
    assert contract["state_rule"]["archived_threshold_reused"] is False


def test_student_t_predictive_is_finite():
    lp = student_t_logpdf(0.01, 0.0, 1.0, 2.0, 0.001)
    assert np.isfinite(lp)


def test_synthetic_abrupt_negative_shift_can_emit_adverse_break_candidate():
    idx = pd.date_range("2020-01-01", periods=28, freq="MS")
    series = pd.Series([0.0] * 24 + [-0.15] * 4, index=idx, name="log_return")
    prior = NIGPrior(mu0=0.0, kappa0=1.0, alpha0=2.0, beta0=0.0004)
    contract = load_contract()
    out = run_bocpd(series, prior, 36, contract)
    tail = out.loc["2022-01-01":]
    assert (tail["state"] == "ADVERSE_BREAK_CANDIDATE").any()
    assert (tail.loc[tail["state"] == "ADVERSE_BREAK_CANDIDATE", "log_return"] < 0).all()


def test_posterior_normalizes_and_constant_hazard_run0_probability_is_structural():
    idx = pd.date_range("2020-01-01", periods=18, freq="MS")
    series = pd.Series(np.linspace(-0.03, 0.04, len(idx)), index=idx, name="log_return")
    prior = NIGPrior(mu0=0.0, kappa0=1.0, alpha0=2.0, beta0=0.001)
    contract = load_contract()
    out = run_bocpd(series, prior, 36, contract)
    assert np.allclose(out["posterior_sum"], 1.0, rtol=0.0, atol=1e-12)
    assert np.allclose(out["p_run0"], 1.0 / 36.0, rtol=0.0, atol=1e-12)


def test_real_core_frozen_windows_and_development_only_prior():
    contract = load_contract()
    core = load_core_monthly()
    returns = monthly_log_returns(core)
    prior = fit_development_prior(returns, contract)
    assert np.isfinite(prior.mu0)
    assert prior.kappa0 == 1.0
    assert prior.alpha0 == 2.0
    assert prior.beta0 > 0

    # Mutating validation/locked observations must not change the prior because
    # the prior is fitted exclusively on the frozen development window.
    mutated = returns.copy()
    mutated.loc[pd.Timestamp("2021-01-01"):] = mutated.loc[pd.Timestamp("2021-01-01"):] + 99.0
    prior2 = fit_development_prior(mutated, contract)
    assert prior == prior2


def test_prefix_invariance_on_frozen_real_axis():
    contract = load_contract()
    core = load_core_monthly()
    returns = monthly_log_returns(core)
    prior = fit_development_prior(returns, contract)
    w = contract["windows"]
    replay = returns.loc[pd.Timestamp(w["development_start"]): pd.Timestamp(w["locked_end"])]
    assert_prefix_invariance(
        replay,
        prior,
        int(contract["hazard"]["expected_run_length_months"]),
        contract,
        [pd.Timestamp("2023-12-01"), pd.Timestamp("2025-12-01"), pd.Timestamp("2026-07-01")],
    )


def test_full_replay_counts_determinism_and_no_promotion():
    one = build_replay()
    two = build_replay()
    assert one.summary["row_count"] == 199
    assert one.summary["period_counts"] == {"DEV": 132, "LOCK": 31, "VAL": 36}
    assert one.summary["first_replay_month"] == "2010-01-01"
    assert one.summary["last_replay_month"] == "2026-07-01"
    assert one.summary["determinism_sha256"] == two.summary["determinism_sha256"]
    assert one.summary["database_writes"] == "NONE"
    assert one.summary["direction_vote_permitted"] is False
    assert one.summary["position_mapping_permitted"] is False
    assert one.summary["promotion_authorized"] is False
    assert one.summary["prospective_claim"] is False
    assert all(one.summary["hard_gates"].values())


def test_canonical_hash_changes_when_observation_changes():
    contract = load_contract()
    idx = pd.date_range("2020-01-01", periods=12, freq="MS")
    series = pd.Series(np.linspace(-0.02, 0.03, 12), index=idx, name="log_return")
    prior = NIGPrior(mu0=0.0, kappa0=1.0, alpha0=2.0, beta0=0.001)
    a = run_bocpd(series, prior, 36, contract)
    changed = series.copy()
    changed.iloc[-1] += 0.01
    b = run_bocpd(changed, prior, 36, contract)
    assert canonical_hash(a, prior, 36) != canonical_hash(b, prior, 36)
