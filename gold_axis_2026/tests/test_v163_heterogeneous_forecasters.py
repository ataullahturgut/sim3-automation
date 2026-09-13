import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v163_research import run_v163_heterogeneous_forecasters as v163

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v163_research/contracts/v163_heterogeneous_forecasters_freeze_v1.json"


def test_contract_is_frozen_and_selector_forbidden():
    c = json.loads(CONTRACT.read_text())
    assert c["status"] == "FROZEN_BEFORE_ANY_V163_SCORING"
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["evaluation"]["meta_selector_scoring_in_v163"] == "FORBIDDEN"
    assert c["governance"]["production_authority"] is False
    assert c["governance"]["production_writes"] == "NONE"


def test_maturity_rule_excludes_unmatured_targets():
    y = pd.Series([0, 1, 0, 1, 0, 1, np.nan], dtype=float)
    idx = v163.matured_indices(y, t=5, h=3, cap=252)
    assert idx == [0, 1, 2]
    assert all(j + 3 <= 5 for j in idx)


def test_expert_pool_is_information_block_heterogeneous():
    sets = {k: set(v[1]) for k, v in v163.EXPERTS.items() if k != "FULL_HGB"}
    assert len(sets) == 4
    for a, sa in sets.items():
        for b, sb in sets.items():
            if a >= b:
                continue
            assert sa != sb
    assert set(v163.ROLE_CONTEXT).issubset(set(v163.FULL))


def test_role_context_is_not_flat_vote():
    assert set(v163.ROLE_CONTEXT) == {
        "fast_state_encoded", "slow_state_encoded", "monthly_direction_3m_encoded"
    }
    assert not any(name in v163.EXPERTS for name in ["FAST", "SLOW", "MONTHLY_DIRECTION_3M"])


def test_target_series_uses_future_close_only_for_label():
    d = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=5, freq="D"),
        "close": [100.0, 101.0, 99.0, 102.0, 103.0],
    })
    y, ret, td = v163.target_series(d, 1)
    assert y.iloc[0] == 1
    assert y.iloc[1] == 0
    assert pd.isna(y.iloc[-1])
    assert td.iloc[0] == pd.Timestamp("2026-01-02")
    assert ret.iloc[0] > 0
