from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v165diag_research import run_v165diag_failure_attribution as diag

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v165diag_research/contracts/v165diag_failure_attribution_freeze_v1.json"


def test_contract_is_frozen_and_no_intervention_is_allowed():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "FROZEN_BEFORE_ANY_V165DIAG_SCORING"
    e = c["evaluation_lock"]
    assert e["model_refitting_in_v165diag"] == "FORBIDDEN"
    assert e["recalibration_in_v165diag"] == "FORBIDDEN"
    assert e["drift_detector_scoring_in_v165diag"] == "FORBIDDEN"
    assert e["triggered_adaptation_in_v165diag"] == "FORBIDDEN"
    assert e["selector_scoring_in_v165diag"] == "FORBIDDEN"
    assert e["abstention_tuning_in_v165diag"] == "FORBIDDEN"
    assert e["post_score_threshold_or_feature_search"] == "FORBIDDEN"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False


def test_block_bootstrap_is_deterministic_for_fixed_seed():
    x = np.linspace(-0.2, 0.2, 50)
    a = diag.moving_block_mean_ci(x, block_length=5, replicates=200, seed=123)
    b = diag.moving_block_mean_ci(x, block_length=5, replicates=200, seed=123)
    assert a == b
    assert a[0] <= np.mean(x) <= a[1]


def test_calibration_decomposition_is_finite():
    y = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    p = np.array([0.1, 0.2, 0.8, 0.7, 0.3, 0.6, 0.4, 0.9])
    out = diag.brier_decomposition(y, p, bins=10)
    assert out["bins_used"] > 0
    assert out["ece"] >= 0
    assert out["murphy_reliability"] >= 0
    assert out["murphy_resolution"] >= 0
    assert out["murphy_uncertainty"] > 0


def test_state_volatility_thresholds_are_anchored_only_to_2024():
    dates = pd.date_range("2024-01-01", periods=12, freq="MS").append(
        pd.date_range("2025-01-01", periods=12, freq="MS")
    ).append(pd.date_range("2026-01-01", periods=6, freq="MS"))
    n = len(dates)
    base = pd.DataFrame({
        "date": dates,
        "gold_rv20": list(np.linspace(1.0, 12.0, 12)) + [1000.0] * 18,
        "gold_mom20": np.ones(n),
        "broad_usd_logdiff5": np.ones(n),
        "real10_delta5": np.ones(n),
        "fast_state_encoded": np.zeros(n),
        "slow_state_encoded": np.zeros(n),
        "monthly_direction_3m_encoded": np.zeros(n),
    })
    _, thresholds = diag.build_state_labels(base)
    assert thresholds["gold_rv20_q67_2024"] < 12.0
    assert thresholds["gold_rv20_q67_2024"] < 1000.0


def test_source_contains_no_forecaster_refit_or_detector_path():
    source = (ROOT / "v165diag_research/run_v165diag_failure_attribution.py").read_text(encoding="utf-8")
    assert "model_refitting_performed\": False" in source
    assert "drift_detector_scoring_performed\": False" in source
    assert "triggered_adaptation_performed\": False" in source
    assert "selector_scoring_performed\": False" in source
    assert "RETROSPECTIVE_UNATTAINABLE_UPPER_BOUND_NOT_A_SELECTOR" in source
