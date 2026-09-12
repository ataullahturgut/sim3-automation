import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v161_thesis import run_v161_short_horizon_price_discovery as v161


def test_contract_is_frozen_and_research_only():
    c = v161.load_contract()
    assert c["status"] == "FROZEN_BEFORE_V161_RETROSPECTIVE_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["evaluation"]["2025_and_2026_are_researcher_visible"] is True
    assert c["evaluation"]["no_post_score_threshold_or_feature_search"] is True


def test_price_discovery_join_is_strict_previous_date():
    panel = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-03", "2025-01-06"]),
        "close": [2600.0, 2610.0],
    })
    market = pd.DataFrame({
        "source_date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]),
        "close": [2650.0, 2660.0, 2670.0],
        "gc_ret1": [0.0, 0.01, 0.02],
    })
    out = v161.strict_previous_merge(panel, market, "gc")
    assert out.loc[0, "gc_source_date"] == pd.Timestamp("2025-01-02")
    assert out.loc[1, "gc_source_date"] == pd.Timestamp("2025-01-03")
    assert (out["gc_source_date"] < out["date"]).all()


def test_target_maturity_geometry():
    d = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=10, freq="D"),
        "close": np.arange(100.0, 110.0),
    })
    z = v161.add_target(d, 3)
    assert z.loc[0, "target_date"] == pd.Timestamp("2025-01-04")
    assert z.loc[0, "future_direction"] == 1
    assert pd.isna(z.loc[8, "target_return"])


def test_feature_sets_do_not_contain_legacy_generic_fx():
    c = v161.load_contract()
    fs = v161.feature_sets(c)
    all_cols = set().union(*[set(x) for x in fs.values()])
    assert "fx_level" not in all_cols
    assert "fx_logdiff" not in all_cols
    assert "broad_usd_level" in all_cols
    assert "real10_level" in all_cols


def test_h5_is_primary_and_h3_secondary():
    c = v161.load_contract()
    assert c["horizons"]["PRIMARY_H5"] == 5
    assert c["horizons"]["SECONDARY_H3"] == 3
    assert any(x.get("role") == "PRIMARY_CHALLENGER" and x["candidate"] == "H5_PD_RM_QB" for x in c["candidate_universe"]["PRIMARY_H5"])
