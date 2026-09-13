import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v162_research.run_v162_context_aware_meta_forecast import (
    EXPERTS,
    STATE_COLS,
    _entropy_confidence,
    _matured_indices,
    _softmax_losses,
    local_weights,
    prepare_state,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v162_research/contracts/v162_context_aware_meta_forecast_freeze_v1.json"


def test_contract_is_frozen_and_nonproduction():
    c = json.loads(CONTRACT.read_text())
    assert c["status"] == "FROZEN_BEFORE_ANY_V162_SCORING"
    assert c["evidence_class"] == "RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS"
    assert c["auto_selector"] == "OFF"
    assert c["auto_ensemble"] == "OFF"
    assert c["production_authority"] is False
    assert "POST_SCORE_V162_TUNING" in c["forbidden"]


def test_maturity_rule_excludes_unmatured_forecasts():
    paths = {e: {j: 0.55 for j in range(20)} for e in EXPERTS}
    y = pd.Series([0, 1] * 10, dtype=float)
    idx = _matured_indices(paths, y, t=10, h=3)
    assert idx == list(range(8))  # j+3<=10 and j<10 -> j<=7
    assert all(j + 3 <= 10 for j in idx)


def test_softmax_prefers_lower_loss_and_entropy_confidence_is_bounded():
    w = _softmax_losses(np.array([0.10, 0.20, 0.30]), eta=12.0)
    assert np.isclose(w.sum(), 1.0)
    assert w[0] > w[1] > w[2]
    c = _entropy_confidence(w)
    assert 0.0 <= c <= 1.0


def test_prepare_state_preserves_roles_as_encoded_context():
    d = pd.DataFrame({
        "monthly_direction_3m": ["UP", "DOWN"],
        "fast_state": ["ROBUST_UP", "MIXED"],
        "slow_state": ["ROBUST_DOWN", "NOT_YET_ROBUST"],
        "emergency_level": ["NEUTRAL", "UP"],
        "emergency_reversal": ["OFF", "ON"],
    })
    z = prepare_state(d)
    assert list(z.monthly_direction_3m_encoded) == [1.0, -1.0]
    assert list(z.fast_state_encoded) == [1.0, 0.0]
    assert list(z.slow_state_encoded) == [-1.0, 0.0]
    assert list(z.emergency_level_encoded) == [0.0, 1.0]
    assert list(z.emergency_reversal_encoded) == [0.0, 1.0]
    assert list(z.legacy_state_available) == [1.0, 1.0]


def test_local_weights_use_only_supplied_prior_indices_and_sum_to_one():
    n = 90
    d = pd.DataFrame(index=range(n))
    for c in STATE_COLS:
        d[c] = np.linspace(-1, 1, n)
    paths = {
        EXPERTS[0]: {j: 0.8 if j % 2 else 0.2 for j in range(n)},
        EXPERTS[1]: {j: 0.6 for j in range(n)},
        EXPERTS[2]: {j: 0.4 for j in range(n)},
    }
    y = pd.Series([j % 2 for j in range(n)], dtype=float)
    idx = list(range(60))
    w, score, eff_n, bw = local_weights(d, paths, y, idx, t=70)
    assert np.isclose(w.sum(), 1.0)
    assert len(score) == len(EXPERTS)
    assert eff_n > 0
    assert bw > 0
