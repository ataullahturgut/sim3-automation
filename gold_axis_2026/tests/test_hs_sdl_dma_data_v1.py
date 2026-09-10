from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hs_sdl_dma_v1.data import build_targets, load_role_replay, one_hot_direction_features


def sample():
    return pd.DataFrame({
        "date": pd.to_datetime(["2026-01-02","2026-01-05","2026-01-09","2026-01-10"]),
        "close": [100.0,101.0,99.0,102.0],
        "fast_state": ["MIXED","ROBUST_UP","ROBUST_DOWN","ROBUST_UP"],
        "slow_state": ["NOT_YET_ROBUST","ROBUST_UP","ROBUST_DOWN","ROBUST_UP"],
        "monthly_direction_3m": ["NEUTRAL","UP","DOWN","UP"],
        "emergency_level": ["NEUTRAL"]*4,
        "emergency_reversal": ["OFF"]*4,
    })


def test_target_is_next_eligible_not_calendar_day():
    t = build_targets(sample(), 1)
    assert t.loc[0,"target_date"] == pd.Timestamp("2026-01-05")
    assert t.loc[1,"target_date"] == pd.Timestamp("2026-01-09")


def test_three_day_target_matures_only_at_third_subsequent_row():
    t = build_targets(sample(), 3)
    assert len(t) == 1
    assert t.loc[0,"target_date"] == pd.Timestamp("2026-01-10")


def test_one_hot_is_not_ordinal_vote_encoding():
    x = one_hot_direction_features(sample())
    assert "fast_state__ROBUST_UP" in x
    assert "fast_state__ROBUST_DOWN" in x
    assert set(x.to_numpy().ravel()) <= {0.0,1.0}


def test_unknown_state_fails_closed(tmp_path):
    p=tmp_path/"bad.csv"; d=sample(); d.loc[0,"fast_state"]="UP_GUESSED"; d.to_csv(p,index=False)
    with pytest.raises(RuntimeError,match="UNFROZEN_STATE_LEVEL"):
        load_role_replay(p)


def test_missing_state_fails_closed():
    d=sample(); d.loc[0,"slow_state"]=None
    with pytest.raises(RuntimeError,match="BLOCKED_INVENTORY"):
        one_hot_direction_features(d)
