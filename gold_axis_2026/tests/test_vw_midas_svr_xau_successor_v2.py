from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "vw_midas_svr_xau_successor_v2.py"
spec = importlib.util.spec_from_file_location("vw_v2", MODULE_PATH)
assert spec and spec.loader
vw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vw)


def test_structural_self_audit():
    vw.structural_self_audit()


def test_corrected_validation_window_is_12_origins():
    origins = pd.date_range(vw.VALIDATION_ORIGIN_START, vw.VALIDATION_ORIGIN_END, freq="MS")
    assert len(origins) == 12
    assert origins[0] == pd.Timestamp("2024-10-01")
    assert origins[-1] == pd.Timestamp("2025-09-01")
    assert origins[0] + pd.offsets.MonthBegin(1) == pd.Timestamp("2024-11-01")
    assert origins[-1] + pd.offsets.MonthBegin(1) == pd.Timestamp("2025-10-01")


def test_validation_gate_is_strict_and_rw_relative():
    passing = {
        "relative_mae_vs_rw": 0.99,
        "mape": 4.0,
        "rw_mape": 4.1,
        "median_ae": 40.0,
        "rw_median_ae": 41.0,
        "monthly_win_rate_vs_rw": 0.5,
    }
    ok, failed = vw.validation_gate(passing, {"2024-10..2024-12": 1.5, "2025-01..2025-09": 1.4})
    assert ok is True
    assert failed == []

    failing = dict(passing)
    failing["relative_mae_vs_rw"] = 1.0
    ok, failed = vw.validation_gate(failing, {"2024-10..2024-12": 1.0, "2025-01..2025-09": 1.0})
    assert ok is False
    assert "relative_mae_vs_rw_lt_1" in failed


def test_no_current_sep_reconstruction_constant_contract():
    assert vw.CURRENT_ORIGIN == pd.Timestamp("2026-08-01")
    assert vw.CURRENT_TARGET == pd.Timestamp("2026-09-01")
