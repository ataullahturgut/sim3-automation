from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v153_thesis import run_v153_intraday_regime_specialists as v

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v153_thesis/contracts/v153_intraday_regime_specialists_freeze_v1.json"


def test_contract_is_frozen_and_fail_closed():
    c = json.loads(CONTRACT.read_text())
    assert c["status"] == "FROZEN_BEFORE_V153_2025_2026_SUCCESSOR_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"
    assert c["governance"]["missing_data"] == "NO_SIGNAL_NOT_NEUTRAL"


def test_ttsm_s2_rule_geometry():
    c = json.loads(CONTRACT.read_text())
    dates = pd.date_range("2023-01-01", periods=280, freq="D")
    d = pd.DataFrame({
        "trade_date": dates,
        "n5": 200,
        "rs_plus": np.linspace(1, 3, 280),
        "rs_minus": np.linspace(1, 3, 280),
        "rv": np.linspace(2, 6, 280),
        "c0329": 1900.0,
        "c0759": 1901.0,
        "c1659": np.linspace(1900, 2100, 280),
    })
    d = v.add_semivariance_state(d, c)
    x = v.exact_origin_frame(d, c)
    # Before a full 250-day semivariance reference exists, the literature specialist must abstain.
    assert (x.loc[:240, "sig_ttsm_s2"] == 0).all()


def test_downshock_thresholds_use_prior_returns_only():
    c = json.loads(CONTRACT.read_text())
    dates = pd.date_range("2023-01-01", periods=300, freq="D")
    close = 1900 * np.exp(np.cumsum(np.resize(np.array([0.005,-0.004,0.007,-0.006]),300)))
    d = pd.DataFrame({
        "trade_date": dates,
        "n5": 200,
        "rs_plus": 1.0,
        "rs_minus": 1.0,
        "rv": 2.0,
        "c0329": close * 0.999,
        "c0759": close,
        "c1659": close,
    })
    d = v.add_semivariance_state(d, c)
    x = v.exact_origin_frame(d, c)
    # Mutating the current return cannot affect its own already-lagged threshold input by construction.
    i = 150
    prior = x.loc[i, ["down_q50","down_q75"]].copy()
    assert pd.notna(prior["down_q50"]) and pd.notna(prior["down_q75"])


def test_metric_ignores_no_signal():
    d = pd.DataFrame({
        "sig": [1,0,-1,0],
        "target_sign": [1,-1,-1,1],
        "ret_next": [0.01,-0.01,-0.02,0.03],
    })
    m = v.metric(d, "sig")
    assert m["n"] == 2
    assert m["hits"] == 2
    assert m["selective_accuracy"] == 1.0


def test_no_future_window_dates_in_contract():
    c = json.loads(CONTRACT.read_text())
    assert c["windows"]["formation_end"] == "2024-12-31"
    assert c["windows"]["validation_start"] == "2025-01-01"
    assert c["windows"]["test_start"] == "2026-01-01"
