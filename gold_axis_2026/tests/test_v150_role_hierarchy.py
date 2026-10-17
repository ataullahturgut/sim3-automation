import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v150_thesis.run_v150_development import (
    CONTRACT,
    add_gold_features,
    role_fast,
    select_threshold,
    targets,
)


def _toy(n=90):
    dates = pd.bdate_range("2023-01-02", periods=n)
    close = 1800.0 * np.exp(np.cumsum(np.sin(np.arange(n) / 7.0) * 0.002 + 0.0003))
    return pd.DataFrame({"date": dates, "observation_ts": pd.to_datetime(dates).tz_localize("America/New_York") + pd.Timedelta(hours=17), "close": close})


def test_contract_freezes_outer_and_production_closed():
    c = json.loads(Path(CONTRACT).read_text())
    assert c["status"] == "FROZEN_BEFORE_V150_DEVELOPMENT_RUN"
    assert c["outer_lock"]["forbidden_for_design_or_scoring"][0] == "2025-01-01"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"


def test_target_maturity_is_forward_only():
    d = _toy(20)
    y1, r1 = targets(d, 1)
    y3, r3 = targets(d, 3)
    assert y1.iloc[-1:].isna().all()
    assert y3.iloc[-3:].isna().all()
    assert np.isclose(r1.iloc[0], np.log(d.close.iloc[1] / d.close.iloc[0]))
    assert np.isclose(r3.iloc[0], np.log(d.close.iloc[3] / d.close.iloc[0]))


def test_gold_features_do_not_use_future_values():
    d = _toy(90)
    a = add_gold_features(d.copy())
    b = add_gold_features(d.iloc[:-1].copy())
    cols = [c for c in a.columns if c.startswith("gold_")]
    pd.testing.assert_frame_equal(a.iloc[:-1][cols].reset_index(drop=True), b[cols].reset_index(drop=True))


def test_fast_role_prefix_invariant():
    d = _toy(90)
    full = role_fast(d)
    prefix = role_fast(d.iloc[:-1].copy())
    pd.testing.assert_series_equal(full.iloc[:-1].reset_index(drop=True), prefix.reset_index(drop=True), check_names=False)


def test_selective_threshold_obeys_coverage_and_n():
    n = 50
    f = pd.DataFrame({
        "p": np.r_[np.repeat(0.8, 20), np.repeat(0.2, 20), np.repeat(0.51, 10)],
        "y": np.r_[np.ones(20), np.zeros(20), np.array([0, 1] * 5)],
    })
    out = select_threshold(f, [0.0, 0.05, 0.1, 0.15, 0.2])
    assert out["selection_status"] == "SELECTED_ON_PRELOCK"
    assert out["selection_n"] >= 20
    assert out["selection_coverage"] >= 0.35


def test_no_2025_2026_literal_read_in_development_range_contract():
    c = json.loads(Path(CONTRACT).read_text())
    assert c["general_direction"]["development_data"] == ["2023-01-01", "2024-12-31"]
    assert c["event_direction"]["development_data"] == ["2023-01-01", "2024-12-31"]
