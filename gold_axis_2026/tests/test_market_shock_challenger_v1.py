from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026" / "tools" / "market_shock_challenger_v1.py"
spec = importlib.util.spec_from_file_location("market_shock_challenger_v1", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def _frame_from_returns(returns: np.ndarray, start="2025-01-02 00:00:00") -> pd.DataFrame:
    ts = pd.date_range(start, periods=len(returns) + 1, freq="5min", tz="UTC")
    logp = np.r_[math.log(2000.0), math.log(2000.0) + np.cumsum(returns)]
    return pd.DataFrame({"ts": ts, "close": np.exp(logp)})


def test_lm_critical_matches_frozen_formula() -> None:
    alpha = 0.05
    n = 288
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    sn = 1.0 / (2.0 * c * root)
    beta = -math.log(-math.log(1.0 - alpha))
    expected = cn + sn * beta
    assert math.isclose(m.lm_critical(alpha, n), expected, rel_tol=0.0, abs_tol=1e-12)
    assert 4.2 < expected < 4.3


def test_current_extreme_return_does_not_change_its_own_local_scale() -> None:
    base_returns = np.resize(np.array([0.0002, -0.0003, 0.0001, -0.00015, 0.00025]), 420)
    base = m.build_returns(_frame_from_returns(base_returns))
    i = 350
    before = float(base.loc[i, "local_sigma"])
    assert math.isfinite(before) and before > 0

    shocked_returns = base_returns.copy()
    shocked_returns[i - 1] = 0.05
    shocked = m.build_returns(_frame_from_returns(shocked_returns))
    after = float(shocked.loc[i, "local_sigma"])
    assert math.isclose(after, before, rel_tol=0.0, abs_tol=1e-15)
    assert abs(float(shocked.loc[i, "ret"])) > 0.04


def test_gap_return_and_cross_gap_30m_move_are_not_scored() -> None:
    ts = list(pd.date_range("2025-01-02 00:00:00", periods=10, freq="5min", tz="UTC"))
    ts[5:] = [x + pd.Timedelta(minutes=20) for x in ts[5:]]
    close = np.exp(math.log(2000.0) + np.arange(10) * 0.0001)
    out = m.build_returns(pd.DataFrame({"ts": ts, "close": close}))
    assert pd.isna(out.loc[5, "ret"])
    # Six-return 30-minute windows spanning the discontinuity must be blocked.
    for idx in range(5, 10):
        assert pd.isna(out.loc[idx, "move30"])


def test_evt_fit_returns_tail_critical_above_pot_threshold() -> None:
    # Deterministic heavy-tailed positive scores; no RNG dependence in this unit test.
    x = pd.Series(np.geomspace(0.1, 25.0, 20000))
    fit = m.fit_evt(x)
    assert fit.n_train == 20000
    assert 400 <= fit.n_exceed <= 600
    assert fit.critical_score > fit.threshold_u > 0
    assert math.isfinite(fit.shape)
    assert math.isfinite(fit.scale) and fit.scale > 0


def test_synthetic_jump_is_monotone_in_standardized_score() -> None:
    sigma = 0.001
    period = 1.0
    base_r = 0.0002
    scores = []
    for size in m.SYNTHETIC_SIZES:
        jump = math.log1p(size)
        scores.append(abs(base_r + jump) / (sigma * period))
    assert all(scores[i + 1] > scores[i] for i in range(len(scores) - 1))


def test_frozen_primary_frequency_and_thresholds() -> None:
    assert m.INTERVAL == "5min"
    assert m.K_LM == 270
    assert math.isclose(m.POT_Q, 0.975)
    assert math.isclose(m.TAIL_P, 0.001)
    assert m.SYNTHETIC_SIZES == [0.0025, 0.0050, 0.0075, 0.0100, 0.0150, 0.0200]
