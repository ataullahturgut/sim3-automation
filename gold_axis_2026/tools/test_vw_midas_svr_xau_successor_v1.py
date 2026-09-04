from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("vwv1", HERE / "vw_midas_svr_xau_successor_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(M)


def synthetic_daily(start="2020-02-20", end="2026-08-31"):
    idx = pd.bdate_range(start, end)
    x = np.arange(len(idx), dtype=float)
    vals = 1500.0 * np.exp(0.00025 * x + 0.006 * np.sin(x / 17.0))
    return pd.Series(vals, index=idx, dtype=float)


def synthetic_inputs():
    daily = synthetic_daily()
    monthly = daily.loc[daily.index >= M.SOURCE_START].groupby(daily.loc[daily.index >= M.SOURCE_START].index.to_period("M")).mean()
    monthly.index = monthly.index.to_timestamp()
    monthly = monthly.reindex(pd.date_range(M.SOURCE_START, M.SOURCE_END, freq="MS"))
    origins = pd.date_range("2020-09-01", M.CURRENT_ORIGIN, freq="MS")
    gpr = {o: 0.15 + 0.7 * ((i % 19) / 18.0) for i, o in enumerate(origins)}
    return daily, monthly, gpr


def test_contract_self_audit_and_governance_locks():
    M.contract_self_audit()
    contract = __import__("json").loads(M.CONTRACT_PATH.read_text())
    assert contract["engine_id"] == "VW_MIDAS_SVR_XAU_SUCCESSOR_V1"
    assert contract["archived_engine_id"] == "VW_MIDAS_MSVR"
    assert contract["production_authorized"] is False
    assert contract["prospective_claim"] is False
    assert contract["db_writes_permitted"] is False
    assert contract["direction_vote_permitted"] is False
    assert contract["auto_selector"] is False
    assert contract["auto_ensemble"] is False


def test_variable_weighted_return_is_causal_and_finite():
    daily, _, _ = synthetic_inputs()
    origin = pd.Timestamp("2023-06-01")
    a = M.variable_weighted_daily_return(daily, origin, 0.2)
    b = M.variable_weighted_daily_return(daily.loc[: origin + pd.offsets.MonthEnd(0)], origin, 0.2)
    assert math.isfinite(a)
    assert abs(a - b) < 1e-15


def test_feature_frame_contains_only_frozen_features():
    daily, monthly, gpr = synthetic_inputs()
    frame = M.build_feature_frame(daily, monthly, gpr, include_current_unknown=True)
    assert set(M.FEATURES).issubset(frame.columns)
    assert frame.loc[pd.Timestamp("2024-06-01"), "origin"] == pd.Timestamp("2024-05-01")
    assert frame.loc[pd.Timestamp("2024-06-01"), list(M.FEATURES)].notna().all()


def test_prefix_invariance_on_synthetic_history():
    daily, monthly, gpr = synthetic_inputs()
    assert M.prefix_invariance_check(daily, monthly, gpr, pd.Timestamp("2024-06-01"))


def test_future_target_mutation_cannot_change_earlier_prediction():
    daily, monthly, gpr = synthetic_inputs()
    frame = M.build_feature_frame(daily, monthly, gpr, include_current_unknown=True)
    target = pd.Timestamp("2024-12-01")
    p1 = M.predict_target(frame, target)
    changed = frame.copy()
    future = changed.index > target
    changed.loc[future, "actual"] = changed.loc[future, "actual"].fillna(99999.0) * 3.0
    changed.loc[future, "y"] = changed.loc[future].apply(
        lambda r: math.log(float(r["actual"]) / float(r["origin_price"])) if np.isfinite(r["actual"]) else np.nan,
        axis=1,
    )
    p2 = M.predict_target(changed, target)
    assert abs(p1["forecast"] - p2["forecast"]) < 1e-10
    assert (p1["C"], p1["gamma"], p1["epsilon"]) == (p2["C"], p2["gamma"], p2["epsilon"])


def test_replay_determinism_on_synthetic_history():
    daily, monthly, gpr = synthetic_inputs()
    frame = M.build_feature_frame(daily, monthly, gpr, include_current_unknown=True)
    a = M.replay(frame, pd.Timestamp("2024-01-01"), pd.Timestamp("2024-03-01"))
    b = M.replay(frame, pd.Timestamp("2024-01-01"), pd.Timestamp("2024-03-01"))
    assert M.prediction_fingerprint(a) == M.prediction_fingerprint(b)


def test_validation_gate_is_fixed_and_not_lock_dependent():
    passing = {
        "relative_mae_vs_rw": 0.9,
        "mape": 2.0,
        "rw_mape": 2.2,
        "median_ae": 30.0,
        "rw_median_ae": 35.0,
        "monthly_win_rate_vs_rw": 0.55,
    }
    ok, failed = M.validation_gate(passing, {"2023": 0.9, "2024": 1.1})
    assert ok and failed == []
    bad = dict(passing, relative_mae_vs_rw=1.01)
    ok2, failed2 = M.validation_gate(bad, {"2023": 0.9, "2024": 1.1})
    assert not ok2
    assert "relative_mae_vs_rw_lt_1" in failed2


def test_no_database_client_or_write_path_in_engine_source():
    src = (HERE / "vw_midas_svr_xau_successor_v1.py").read_text().lower()
    forbidden = ["psycopg", "sqlalchemy", "insert into", "update public.", "delete from", "neon_database_url"]
    assert all(x not in src for x in forbidden)
