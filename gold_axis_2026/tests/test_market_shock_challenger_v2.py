from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026" / "tools" / "market_shock_challenger_v2.py"
spec = importlib.util.spec_from_file_location("market_shock_challenger_v2", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def _frame_from_returns(returns: np.ndarray, start="2025-01-02 00:00:00") -> pd.DataFrame:
    ts = pd.date_range(start, periods=len(returns) + 1, freq="5min", tz="UTC")
    logp = np.r_[math.log(2000.0), math.log(2000.0) + np.cumsum(returns)]
    return pd.DataFrame({"ts": ts, "close": np.exp(logp)})


def test_lm_constants_match_primary_formula() -> None:
    n = 288
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    expected_cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    expected_sn = 1.0 / (c * root)
    cn, sn = m.lm_constants(n)
    assert math.isclose(cn, expected_cn, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(sn, expected_sn, rel_tol=0.0, abs_tol=1e-12)
    assert sn > 0


def test_lm_999_critical_uses_corrected_scale() -> None:
    alpha = 0.001
    n = 288
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    sn = 1.0 / (c * root)
    beta = -math.log(-math.log(1.0 - alpha))
    expected = cn + sn * beta
    assert math.isclose(m.lm_critical(alpha, n), expected, rel_tol=0.0, abs_tol=1e-12)


def test_current_return_does_not_enter_its_own_local_scale() -> None:
    base_returns = np.resize(np.array([0.0002, -0.0003, 0.0001, -0.00015, 0.00025]), 450)
    base = m.build_returns(_frame_from_returns(base_returns))
    row = 360
    before = float(base.loc[row, "local_sigma"])
    assert math.isfinite(before) and before > 0

    shocked_returns = base_returns.copy()
    # DataFrame row `row` contains returns[row-1].
    shocked_returns[row - 1] = 0.05
    shocked = m.build_returns(_frame_from_returns(shocked_returns))
    after = float(shocked.loc[row, "local_sigma"])
    assert math.isclose(after, before, rel_tol=0.0, abs_tol=1e-15)
    assert abs(float(shocked.loc[row, "ret"])) > 0.04


def test_gap_return_and_cross_gap_30m_move_are_blocked() -> None:
    ts = list(pd.date_range("2025-01-02 00:00:00", periods=12, freq="5min", tz="UTC"))
    ts[6:] = [x + pd.Timedelta(minutes=20) for x in ts[6:]]
    close = np.exp(math.log(2000.0) + np.arange(12) * 0.0001)
    out = m.build_returns(pd.DataFrame({"ts": ts, "close": close}))
    assert pd.isna(out.loc[6, "ret"])
    for idx in range(6, 12):
        assert pd.isna(out.loc[idx, "move30"])


def test_evt_fit_returns_critical_above_pot_threshold() -> None:
    x = pd.Series(np.geomspace(0.1, 25.0, 20000))
    fit = m.fit_evt(x)
    assert fit.n_train == 20000
    assert 400 <= fit.n_exceed <= 600
    assert fit.critical_score > fit.threshold_u > 0
    assert math.isfinite(fit.shape)
    assert math.isfinite(fit.scale) and fit.scale > 0


def test_synthetic_jump_size_increases_standardized_impact() -> None:
    sigma = 0.001
    period = 1.0
    base_r = 0.0002
    scores = []
    for size in m.SYNTHETIC_SIZES:
        jump = math.log1p(size)
        scores.append(abs(base_r + jump) / (sigma * period))
    assert all(scores[i + 1] > scores[i] for i in range(len(scores) - 1))


def test_frozen_v2_parameters_and_no_monthly_anchor() -> None:
    assert m.SYMBOL == "XAU/USD"
    assert m.INTERVAL == "5min"
    assert m.K_LM == 270
    assert math.isclose(m.LM_MAIN_ALPHA, 0.001)
    assert math.isclose(m.POT_Q, 0.975)
    assert math.isclose(m.TAIL_P, 0.001)
    assert math.isclose(m.BNS_ALPHA, 0.001)
    assert m.SYNTHETIC_N == 300
    assert m.SYNTHETIC_SIZES == [0.0025, 0.0050, 0.0075, 0.0100, 0.0150, 0.0200]
