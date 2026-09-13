from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v164_research import run_v164_adaptive_error_memory as v164

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v164_research/contracts/v164_adaptive_error_memory_freeze_v1.json"


def test_contract_is_frozen_and_governance_locked():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "FROZEN_BEFORE_ANY_V164_SCORING"
    assert c["training"]["maturity_rule"] == "j+h<=t"
    assert c["training"]["random_split"] is False
    assert c["evaluation"]["selector_scoring_in_v164"] == "FORBIDDEN"
    assert c["evaluation"]["abstention_tuning_in_v164"] == "FORBIDDEN"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"


def test_residual_correction_moves_in_error_direction():
    pos, neff_pos = v164._residual_correction(
        np.asarray([0.2, 0.1, 0.3]), np.ones(3), rho=0.5, shrink_kappa=1.0
    )
    neg, neff_neg = v164._residual_correction(
        np.asarray([-0.2, -0.1, -0.3]), np.ones(3), rho=0.5, shrink_kappa=1.0
    )
    assert pos > 0
    assert neg < 0
    assert neff_pos == neff_neg == 3.0


def test_effective_n_penalizes_concentrated_weights():
    equal = v164._effective_n(np.ones(10))
    concentrated = v164._effective_n(np.asarray([1.0] + [0.0] * 9))
    assert equal == 10.0
    assert concentrated == 1.0


def test_state_local_weights_use_only_supplied_prior_rows():
    d = pd.DataFrame({
        "gold_mom5": [0.0, 0.1, 0.2, 0.15],
        "gold_mom20": [0.0, 0.2, 0.4, 0.3],
        "gold_rv20": [1.0, 1.1, 1.2, 1.15],
        "fast_state_encoded": [-1.0, 0.0, 1.0, 1.0],
        "slow_state_encoded": [-1.0, 0.0, 1.0, 1.0],
        "monthly_direction_3m_encoded": [-1.0, -1.0, 1.0, 1.0],
        "broad_usd_logdiff5": [0.0, 0.01, 0.02, 0.015],
        "real10_delta5": [0.0, 0.1, 0.2, 0.15],
    })
    features = [
        "gold_mom5", "gold_mom20", "gold_rv20",
        "fast_state_encoded", "slow_state_encoded", "monthly_direction_3m_encoded",
        "broad_usd_logdiff5", "real10_delta5",
    ]
    w, neff, bandwidth = v164._state_local_weights(
        d, [0, 1, 2], 3, np.asarray([3.0, 2.0, 1.0]), 60.0, features
    )
    assert len(w) == 3
    assert np.all(np.isfinite(w))
    assert np.all(w >= 0)
    assert 1.0 <= neff <= 3.0
    assert bandwidth > 0


def test_source_keeps_selector_and_abstention_out_of_v164():
    source = (ROOT / "v164_research/run_v164_adaptive_error_memory.py").read_text(encoding="utf-8")
    assert '"selector_scoring_performed": False' in source
    assert '"abstention_tuning_performed": False' in source
    assert '+ h <= t' in source
