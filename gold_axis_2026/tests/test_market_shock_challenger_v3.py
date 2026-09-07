from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026" / "tools" / "market_shock_challenger_v3.py"
spec = importlib.util.spec_from_file_location("market_shock_challenger_v3", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def _frame_from_returns(returns: np.ndarray, start="2025-01-02 00:00:00") -> pd.DataFrame:
    ts = pd.date_range(start, periods=len(returns) + 1, freq="5min", tz="UTC")
    logp = np.r_[math.log(2000.0), math.log(2000.0) + np.cumsum(returns)]
    return pd.DataFrame({"ts": ts, "close": np.exp(logp)})


def _frame_with_daily_gaps(n=3500) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    returns = rng.normal(0.0, 0.0004, n - 1)
    base = _frame_from_returns(returns)
    ts = base["ts"].copy()
    shifts = np.zeros(n, dtype=int)
    for k in range(288, n, 288):
        shifts[k:] += 60
    base["ts"] = ts + pd.to_timedelta(shifts, unit="m")
    return base


def test_lm_constants_match_primary_formula() -> None:
    n = 288
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    expected_cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    expected_sn = 1.0 / (c * root)
    cn, sn = m.lm_constants(n)
    assert math.isclose(cn, expected_cn, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(sn, expected_sn, rel_tol=0.0, abs_tol=1e-12)


def test_current_return_does_not_enter_own_medrv_scale() -> None:
    base_returns = np.resize(np.array([0.0002, -0.0003, 0.0001, -0.00015, 0.00025]), 600)
    base = m.build_returns(_frame_from_returns(base_returns))
    row = 420
    before = float(base.loc[row, "local_sigma"])
    shocked_returns = base_returns.copy()
    shocked_returns[row - 1] = 0.05
    shocked = m.build_returns(_frame_from_returns(shocked_returns))
    after = float(shocked.loc[row, "local_sigma"])
    assert math.isfinite(before) and before > 0
    assert math.isclose(after, before, rel_tol=0.0, abs_tol=1e-15)
    assert abs(float(shocked.loc[row, "ret"])) > 0.04


def test_future_return_cannot_change_past_scale() -> None:
    rng = np.random.default_rng(7)
    returns = rng.normal(0, 0.0004, 650)
    a = m.build_returns(_frame_from_returns(returns))
    altered = returns.copy()
    altered[560] = 0.08
    b = m.build_returns(_frame_from_returns(altered))
    for row in (300, 450, 560):
        av = float(a.loc[row, "local_sigma"])
        bv = float(b.loc[row, "local_sigma"])
        assert math.isclose(av, bv, rel_tol=0.0, abs_tol=1e-15)


def test_isolated_prior_jump_is_robustly_truncated_by_median_triplets() -> None:
    returns = np.resize(np.array([0.0002, -0.00025, 0.00015]), 700).astype(float)
    base = m.build_returns(_frame_from_returns(returns))
    shocked = returns.copy()
    shocked[350] = 0.05
    out = m.build_returns(_frame_from_returns(shocked))
    ratio = float(out.loc[500, "local_sigma"] / base.loc[500, "local_sigma"])
    assert 0.95 <= ratio <= 1.05


def test_gap_return_and_first_30_minutes_are_quarantined() -> None:
    ts = list(pd.date_range("2025-01-02 00:00:00", periods=30, freq="5min", tz="UTC"))
    ts[15:] = [x + pd.Timedelta(minutes=30) for x in ts[15:]]
    close = np.exp(math.log(2000.0) + np.arange(30) * 0.0001)
    out = m.build_returns(pd.DataFrame({"ts": ts, "close": close}))
    assert bool(out.loc[15, "gap_reopen_context"])
    assert pd.isna(out.loc[15, "ret"])
    assert out.loc[15:20, "gap_reopen_warmup"].all()
    assert not bool(out.loc[21, "gap_reopen_warmup"])


def test_no_30m_window_crosses_gap() -> None:
    ts = list(pd.date_range("2025-01-02 00:00:00", periods=30, freq="5min", tz="UTC"))
    ts[15:] = [x + pd.Timedelta(minutes=30) for x in ts[15:]]
    close = np.exp(math.log(2000.0) + np.arange(30) * 0.0001)
    out = m.build_returns(pd.DataFrame({"ts": ts, "close": close}))
    assert out.loc[15:20, "move30"].isna().all()
    assert pd.notna(out.loc[21, "move30"])


def test_v3_valid_term_scale_recovers_coverage_under_repeated_daily_gaps() -> None:
    out = m.build_returns(_frame_with_daily_gaps())
    base = out["base_scoreable"]
    new_covered = base & out["local_sigma"].notna()
    new_coverage = float(new_covered.sum() / base.sum())

    pair = out["ret"].abs() * out["ret"].shift(1).abs()
    v2_sigma = np.sqrt(pair.rolling(268, min_periods=268).mean().shift(1))
    v2_coverage = float((base & v2_sigma.notna()).sum() / base.sum())

    assert new_coverage >= 0.90
    assert new_coverage > v2_coverage + 0.50


def test_periodicity_fallback_is_explicit_not_silent_one() -> None:
    returns = np.resize(np.array([0.0002, -0.0003, 0.0001]), 500)
    frame = m.build_returns(_frame_from_returns(returns))
    target = frame.iloc[[400]].copy()
    tod = int(target.iloc[0]["slot_day"])
    model = m.PeriodicityModel(exact={}, tod={tod: 1.25}, normalization_rms=1.0)
    scored = m.add_scores(target, model)
    assert scored.iloc[0]["period_source"] == "TOD_FALLBACK"
    assert math.isclose(float(scored.iloc[0]["period_factor"]), 1.25)


def test_warmup_cannot_emit_intraday_score() -> None:
    out = m.build_returns(_frame_with_daily_gaps(1200))
    model = m.PeriodicityModel(
        exact={int(x): 1.0 for x in out["week_slot"].unique()},
        tod={int(x): 1.0 for x in out["slot_day"].unique()},
        normalization_rms=1.0,
    )
    scored = m.add_scores(out, model)
    assert scored.loc[scored["gap_reopen_warmup"], "score5"].isna().all()
    assert scored.loc[scored["gap_reopen_warmup"], "score30"].isna().all()


def test_medrv_constant_matches_authority_formula() -> None:
    expected = math.pi / (6.0 - 4.0 * math.sqrt(3.0) + math.pi)
    assert math.isclose(m.MEDRV_CONST, expected, rel_tol=0.0, abs_tol=1e-15)


def test_frozen_v3_parameters() -> None:
    assert m.SYMBOL == "XAU/USD"
    assert m.INTERVAL == "5min"
    assert m.GAP_MAX_SECONDS == 600
    assert m.REOPEN_WARMUP_BARS == 6
    assert m.MEDRV_MAX_TERMS == 270
    assert m.MEDRV_MIN_TERMS == 96
    assert m.MEDRV_MAX_AGE_HOURS == 72
    assert m.PERIOD_EXACT_MIN == 20
    assert m.PERIOD_TOD_MIN == 50
    assert math.isclose(m.LM_MAIN_ALPHA, 0.001)
    assert math.isclose(m.POT_Q, 0.975)
    assert math.isclose(m.TAIL_P, 0.001)
    assert math.isclose(m.COVERAGE_GATE, 0.90)
    assert m.SYNTHETIC_N == 300
    assert m.SYNTHETIC_SIZES == [0.0025, 0.0050, 0.0075, 0.0100, 0.0150, 0.0200]
