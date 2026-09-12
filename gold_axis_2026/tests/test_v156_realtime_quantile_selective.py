from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v156_thesis import run_v156_realtime_quantile_selective as v

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v156_thesis/contracts/v156_realtime_quantile_selective_freeze_v1.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text())


def test_contract_frozen_research_only_and_rule_frozen():
    c = _contract()
    assert c["status"] == "FROZEN_BEFORE_V156_2025_2026_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"
    assert c["direction_rules"]["IQR_EXCLUDES_ZERO"].startswith("q25>0")
    assert c["source"]["no_fallback"] is True


def test_forward_target_geometry():
    d = pd.DataFrame({"date": pd.bdate_range("2024-01-02", periods=30), "close": np.arange(100.0, 130.0)})
    z = v.add_target(d, 5)
    assert z.loc[0, "target_close"] == 105.0
    assert z.loc[0, "target_date"] == d.loc[5, "date"]
    assert np.isnan(z.loc[29, "y"])


def test_selective_rule_semantics():
    f = pd.DataFrame(
        {
            "y": [1, 0, 1, 0],
            "q25": [0.01, -0.03, -0.01, -0.02],
            "q50": [0.02, -0.02, 0.00, 0.00],
            "q75": [0.03, -0.01, 0.02, 0.03],
            "target_return": [0.02, -0.02, 0.01, -0.01],
        }
    )
    m = v.selective_metrics(f)
    # First row => UP, second => DOWN, last two => NO_SIGNAL.
    assert m["n"] == 2
    assert m["coverage"] == 0.5
    assert m["selective_accuracy"] == 1.0
    assert m["up_signals"] == 1
    assert m["down_signals"] == 1


def _synthetic(n: int = 390, h: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(20260912)
    dates = pd.bdate_range("2023-01-02", periods=n)
    x = rng.normal(size=n)
    future = 0.006 * np.tanh(x) + rng.normal(scale=0.01, size=n)
    future[-h:] = np.nan
    return pd.DataFrame(
        {
            "date": dates,
            "target_date": pd.Series(dates).shift(-h),
            "target_return": future,
            "y": np.where(np.isfinite(future), (future > 0).astype(int), np.nan),
            "origin_index": np.arange(n),
            "x": x,
        }
    )


def test_quantile_fit_uses_only_mature_targets():
    h = 20
    z = _synthetic(h=h)
    cfg = copy.deepcopy(_contract()["models"]["RTQ_R126"])
    cfg["minimum_mature_targets"] = 60
    cfg["max_iter"] = 15
    chosen = 320
    start = z.loc[chosen, "date"].date().isoformat()
    a = v.sequential_quantiles(z, ["x"], "TEST", cfg, h, start)
    qa = a.loc[a["origin_index"] == chosen, ["q25", "q50", "q75"]].to_numpy(float)[0]

    z2 = z.copy()
    future_mask = z2["origin_index"] > (chosen - h)
    z2.loc[future_mask & z2["target_return"].notna(), "target_return"] *= -10.0
    z2.loc[future_mask & z2["y"].notna(), "y"] = 1.0 - z2.loc[future_mask & z2["y"].notna(), "y"]
    b = v.sequential_quantiles(z2, ["x"], "TEST", cfg, h, start)
    qb = b.loc[b["origin_index"] == chosen, ["q25", "q50", "q75"]].to_numpy(float)[0]
    assert np.allclose(qa, qb, atol=1e-12)
    assert qa[0] <= qa[1] <= qa[2]


def test_research_gate_requires_both_periods():
    c = _contract()
    good = {"selective_accuracy": 0.75, "coverage": 0.25}
    low = {"selective_accuracy": 0.60, "coverage": 0.25}
    assert v._selective_gate(good, good, "STRATEGIC_H20_SELECTIVE", c)["pass"] is True
    assert v._selective_gate(good, low, "STRATEGIC_H20_SELECTIVE", c)["pass"] is False
