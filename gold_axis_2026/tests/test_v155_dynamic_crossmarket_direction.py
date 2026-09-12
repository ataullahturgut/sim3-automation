from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v155_thesis import run_v155_dynamic_crossmarket_direction as v

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v155_thesis/contracts/v155_dynamic_crossmarket_direction_freeze_v1.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text())


def test_contract_frozen_and_research_only():
    c = _contract()
    assert c["status"] == "FROZEN_BEFORE_V155_2025_2026_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"
    assert c["source"]["external_daily_rule"].startswith("strict previous-source-date")
    assert c["source"]["no_fallback"] is True
    assert c["source"]["no_interpolation"] is True


def test_target_geometry_is_forward_only():
    d = pd.DataFrame(
        {
            "date": pd.bdate_range("2024-01-02", periods=40),
            "close": np.arange(100.0, 140.0),
        }
    )
    z = v.add_target(d, 20)
    assert z.loc[0, "target_close"] == 120.0
    assert z.loc[0, "target_date"] == d.loc[20, "date"]
    assert z.loc[0, "origin_index"] == 0
    assert np.isnan(z.loc[39, "y"])


def _synthetic_seq_frame(n: int = 430, h: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(20260912)
    dates = pd.bdate_range("2023-01-02", periods=n)
    x = rng.normal(size=n)
    latent = 0.8 * x + rng.normal(scale=0.9, size=n)
    y = (latent > 0).astype(float)
    target_date = pd.Series(dates).shift(-h)
    target_return = np.where(y > 0, 0.01, -0.01).astype(float)
    y[-h:] = np.nan
    target_return[-h:] = np.nan
    return pd.DataFrame(
        {
            "date": dates,
            "target_date": target_date,
            "target_return": target_return,
            "y": y,
            "origin_index": np.arange(n),
            "x": x,
        }
    )


def test_sequential_candidate_cannot_use_unmatured_future_labels():
    h = 20
    z = _synthetic_seq_frame(h=h)
    c = copy.deepcopy(_contract())
    c["sequential_training"]["minimum_mature_labels"] = 60
    chosen_t = 320
    c["sequential_training"]["prediction_start"] = z.loc[chosen_t, "date"].date().isoformat()
    cfg = {"feature_set": "BASE", "model": "LOGIT", "fit_mode": "ROLLING", "window": 126}

    a = v.sequential_candidate(z, ["x"], "TEST", cfg, c["model_parameters"], h, c)
    p_a = float(a.loc[a["origin_index"] == chosen_t, "p"].iloc[0])

    z2 = z.copy()
    # At origin chosen_t, only labels j+h <= chosen_t are mature.  Flip every
    # later label, including the current target, and verify the probability is invariant.
    future_mask = z2["origin_index"] > (chosen_t - h)
    z2.loc[future_mask & z2["y"].notna(), "y"] = 1.0 - z2.loc[future_mask & z2["y"].notna(), "y"]
    b = v.sequential_candidate(z2, ["x"], "TEST", cfg, c["model_parameters"], h, c)
    p_b = float(b.loc[b["origin_index"] == chosen_t, "p"].iloc[0])
    assert np.isclose(p_a, p_b, atol=1e-12)


def _candidate_frame(name: str, p_good: float, invert_after: int | None = None) -> pd.DataFrame:
    rows = []
    for t in range(100, 231):
        y = int(t % 2 == 0)
        p = p_good if y == 1 else 1.0 - p_good
        if invert_after is not None and t > invert_after:
            p = 1.0 - p
        rows.append(
            {
                "origin_index": t,
                "origin_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=t),
                "target_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=t + 1),
                "target_return": 0.01 if y else -0.01,
                "y": y,
                "candidate": name,
                "p": p,
                "p_histfreq": 0.5,
                "train_n": 126,
            }
        )
    return pd.DataFrame(rows)


def test_dma_weights_are_prior_only():
    c = copy.deepcopy(_contract())
    c["dynamic_layer"]["DMA_LOGLOSS63"]["minimum_mature_per_member"] = 20
    a = _candidate_frame("A", 0.80)
    b = _candidate_frame("B", 0.60)
    dma1, _ = v.dynamic_layer({"A": a, "B": b}, 1, c)
    t = 200
    p1 = float(dma1.loc[dma1["origin_index"] == t, "p"].iloc[0])

    # Corrupt only predictions after t; the DMA value at t must not move.
    a2 = a.copy()
    b2 = b.copy()
    a2.loc[a2["origin_index"] > t, "p"] = 0.01
    b2.loc[b2["origin_index"] > t, "p"] = 0.99
    dma2, _ = v.dynamic_layer({"A": a2, "B": b2}, 1, c)
    p2 = float(dma2.loc[dma2["origin_index"] == t, "p"].iloc[0])
    assert np.isclose(p1, p2, atol=1e-12)


def test_selective_gate_requires_accuracy_and_coverage_in_both_periods():
    c = _contract()
    good = {"selective_accuracy": 0.70, "coverage": 0.30}
    low_cov = {"selective_accuracy": 0.90, "coverage": 0.10}
    low_acc = {"selective_accuracy": 0.60, "coverage": 0.40}
    assert v.selective_gate(good, good, c)["pass"] is True
    assert v.selective_gate(good, low_cov, c)["pass"] is False
    assert v.selective_gate(good, low_acc, c)["pass"] is False
