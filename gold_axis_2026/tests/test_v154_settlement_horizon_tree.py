from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v154_thesis import run_v154_settlement_horizon_tree as v

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v154_thesis/contracts/v154_settlement_horizon_tree_freeze_v1.json"


def _contract():
    return json.loads(CONTRACT.read_text())


def test_contract_frozen_and_research_only():
    c = _contract()
    assert c["status"] == "FROZEN_BEFORE_V154_2025_2026_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"
    assert c["source"]["endpoint_time"] == "13:29:00"
    assert c["source"]["no_fallback"] is True


def test_target_geometry_uses_future_h_endpoint_only_as_label():
    d = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=30, freq="D"), "close": np.arange(100.0, 130.0)})
    z = v.add_target(d, 5)
    assert z.loc[0, "target_close"] == 105.0
    assert z.loc[0, "target_date"] == pd.Timestamp("2024-01-06")
    assert np.isnan(z.loc[29, "y"])


def test_validation_training_labels_end_before_2025():
    dates = pd.date_range("2023-01-01", periods=900, freq="D")
    close = 1900 * np.exp(np.cumsum(np.resize(np.array([0.002, -0.001, 0.003, -0.002]), len(dates))))
    d = pd.DataFrame({"date": dates, "observation_ts": pd.to_datetime(dates, utc=True), "close": close})
    d, features = v.add_features(d)
    z = v.add_target(d, 20)
    score, info = v._fit_and_predict(z, features, "LOGIT", _contract()["models"]["LOGIT"], "2024-12-31", "2025-01-01", "2025-12-31")
    assert info["train_last_target_date"] <= "2024-12-31"
    assert score["date"].min() >= pd.Timestamp("2025-01-01")
    assert score["target_date"].max() <= pd.Timestamp("2025-12-31")


def test_roles_are_origin_observable():
    dates = pd.bdate_range("2023-01-02", periods=120)
    close = np.linspace(1800, 2000, len(dates))
    d = pd.DataFrame({"date": dates, "observation_ts": pd.to_datetime(dates, utc=True), "close": close})
    out, features = v.add_features(d)
    assert "fast_role" in features
    assert "slow_role" in features
    assert "monthly_direction_3m" in features
    # Once mature, a monotone series should have positive role context.
    mature = out.dropna(subset=["fast_role", "slow_role", "monthly_direction_3m"])
    assert not mature.empty
    assert mature.iloc[-1]["fast_role"] == 1.0
    assert mature.iloc[-1]["slow_role"] == 1.0
    assert mature.iloc[-1]["monthly_direction_3m"] == 1.0


def test_research_interest_gate_requires_both_periods():
    c = _contract()
    good = {"balanced_accuracy": 0.66, "accuracy": 0.66, "balanced_accuracy_gain_vs_training_majority": 0.16}
    bad = {"balanced_accuracy": 0.55, "accuracy": 0.62, "balanced_accuracy_gain_vs_training_majority": 0.05}
    assert v.gate_pass(good, good, c)["pass"] is True
    assert v.gate_pass(good, bad, c)["pass"] is False
