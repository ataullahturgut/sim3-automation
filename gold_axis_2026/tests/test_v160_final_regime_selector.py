from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v160_thesis import run_v160_final_regime_selector as v160


def _contract():
    return v160.load_contract()


def test_contract_is_final_frozen_and_h1_is_not_reopened():
    c = _contract()
    assert c["status"] == "FROZEN_BEFORE_V160_RETROSPECTIVE_SCORING"
    assert c["stopping_rule"] == "FINAL_NORMAL_DAY_RETROSPECTIVE_ARCHITECTURE_EXPERIMENT_V151_V160_SEQUENCE"
    assert c["target"]["primary_horizon_sessions"] == 20
    assert c["target"]["no_h1_reopening"] is True
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False


def test_regime_thresholds_are_prior_only_and_early_rows_are_unknown():
    c = _contract()
    n = 75
    d = pd.DataFrame({
        "origin_index": np.arange(n),
        "vol20": np.linspace(1.0, 2.0, n),
        "bocpd_reset_fraction": np.linspace(0.0, 0.2, n),
        "fast_role": np.ones(n),
        "slow_role": np.ones(n),
        "monthly_direction_3m": np.ones(n),
        "emergency_alert_onset": np.zeros(n, dtype=int),
        "emergency_reversal": np.zeros(n, dtype=int),
    })
    z = v160.add_causal_regime(d, c)
    assert (z.loc[:59, "regime_key"] == "UNKNOWN").all()
    assert z.loc[60, "regime_key"] != "UNKNOWN"
    expected = float(d.loc[:59, "vol20"].median())
    assert abs(float(z.loc[60, "causal_vol_median_ref"]) - expected) < 1e-12


def _expert_frame(signals):
    n = len(signals)
    actual = np.array([1 if i % 2 == 0 else -1 for i in range(n)])
    return pd.DataFrame({
        "origin_index": np.arange(n),
        "origin_date": pd.date_range("2024-01-01", periods=n, freq="D"),
        "target_date": pd.date_range("2024-01-21", periods=n, freq="D"),
        "future_direction": actual,
        "target_return": actual * 0.01,
        "parent_signal": np.asarray(signals, dtype=int),
        "regime_key": ["VOL_LOW|STRUCT_CALM|ROLE_CONSENSUS"] * n,
    })


def test_one_class_expert_cannot_become_eligible_from_raw_accuracy():
    c = _contract()
    f = _expert_frame([1] * 70)
    snap = v160.reliability_snapshot(f, 69, c)
    assert snap["eligible"] is False
    assert snap["reason"] == "DEGENERATE_PREDICTED_CLASS_SUPPORT"


def test_unmatured_future_labels_cannot_change_reliability_snapshot():
    c = _contract()
    signals = [1 if i % 4 in (0, 1) else -1 for i in range(70)]
    f1 = _expert_frame(signals)
    f2 = f1.copy()
    # At origin 69 with H20, rows 50..68 are not mature and must be ignored.
    f2.loc[50:68, "future_direction"] *= -1
    a = v160.reliability_snapshot(f1, 69, c)
    b = v160.reliability_snapshot(f2, 69, c)
    assert a == b


def test_selector_has_no_reversal_flip_or_new_direction_model_contract():
    c = _contract()
    assert c["selector"]["no_direction_model"] is True
    assert c["selector"]["no_probability_meta_model"] is True
    assert c["selector"]["no_reversal_flip"] is True
    assert c["selector"]["NO_SIGNAL_IS_NOT_NEUTRAL"] is True


def test_role_consensus_requires_two_nonzero_agreeing_roles():
    assert v160.role_consensus(pd.Series({"fast_role": 1, "slow_role": 1, "monthly_direction_3m": -1})) == "CONSENSUS"
    assert v160.role_consensus(pd.Series({"fast_role": 1, "slow_role": -1, "monthly_direction_3m": 0})) == "MIXED"
