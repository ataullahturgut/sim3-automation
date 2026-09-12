from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as core

ROOT = Path(__file__).resolve().parents[1]


def contract() -> dict:
    return json.loads((ROOT / "v159_thesis/contracts/v159_driver_corrected_meta_trust_freeze_v1.json").read_text())


def test_contract_is_frozen_research_only_and_veto_only():
    c = contract()
    assert c["status"] == "FROZEN_BEFORE_V159_RETROSPECTIVE_SCORING"
    assert c["evidence_class"] == "RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC"
    assert c["target"]["primary_horizon_sessions"] == 20
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
    assert c["routing"]["reversal_policy"].startswith("V1.59 may veto/abstain only")
    assert c["source"]["legacy_fx_correction"]["legacy_series_id"] == "DEXCHUS_ALFRED_PIT_ME"


def test_corrected_parent_removes_legacy_generic_fx_and_adds_gold_drivers():
    c = contract()
    f = core.corrected_parent_features(["ret_lag1", "fx_level", "fx_logdiff", "dgs10_level"], c)
    assert "fx_level" not in f
    assert "fx_logdiff" not in f
    assert "broad_usd_level" in f
    assert "real10_level" in f
    assert "dgs10_level" in f


def test_strict_previous_date_join_forbids_same_day_driver_use():
    left = pd.DataFrame({"date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]), "x": [1, 2, 3]})
    right = pd.DataFrame({"source_date": pd.to_datetime(["2025-01-02", "2025-01-03"]), "value": [100.0, 101.0]})
    out = core._merge_strict_previous_date(left, right, "driver")
    assert pd.isna(out.loc[0, "driver_source_date"])
    assert out.loc[1, "driver_source_date"] == pd.Timestamp("2025-01-02")
    assert out.loc[2, "driver_source_date"] == pd.Timestamp("2025-01-03")
    valid = out["driver_source_date"].notna()
    assert (out.loc[valid, "driver_source_date"] < out.loc[valid, "date"]).all()


def test_meta_training_consumes_only_mature_parent_correctness_labels():
    c = contract()
    spec = c["meta_candidates"]["META_DRIVER_LOGIT"]
    n = 220
    d = pd.DataFrame({
        "origin_index": np.arange(n, dtype=int),
        "parent_signal": np.where(np.arange(n) % 3 == 0, -1, 1),
        "parent_correct": np.where(np.arange(n) % 2 == 0, 1.0, 0.0),
    })
    row_pos = 180
    idx = core.mature_meta_training_indices(d, row_pos, 20, spec)
    assert idx
    current = int(d.loc[row_pos, "origin_index"])
    assert all(int(d.loc[j, "origin_index"]) + 20 <= current for j in idx)
    assert len(idx) <= int(spec["rolling_window"])


def test_support_gate_requires_two_direction_skill_and_2026_preservation():
    c = contract()
    final = {
        "VALIDATION_2025": {"selective_balanced_accuracy": 0.61, "mcc": 0.2, "up_signals": 30, "down_signals": 10, "coverage": 0.35},
        "TEST_2026_AVAILABLE": {"selective_balanced_accuracy": 0.67, "mcc": 0.3, "up_signals": 20, "down_signals": 20, "coverage": 0.40},
    }
    legacy = {
        "VALIDATION_2025": {"selective_balanced_accuracy": 0.50},
        "TEST_2026_AVAILABLE": {"selective_balanced_accuracy": 0.69},
    }
    trust = {
        "VALIDATION_2025": {"n": 40, "brier": 0.20, "prior_frequency_brier": 0.24, "log_loss": 0.60, "prior_frequency_log_loss": 0.68},
        "TEST_2026_AVAILABLE": {"n": 40, "brier": 0.21, "prior_frequency_brier": 0.23, "log_loss": 0.61, "prior_frequency_log_loss": 0.66},
    }
    gate = core.support_gate(final, legacy, trust, c)
    assert gate["pass"] is True
    bad = {k: dict(v) for k, v in final.items()}
    bad["VALIDATION_2025"]["down_signals"] = 0
    gate2 = core.support_gate(bad, legacy, trust, c)
    assert gate2["pass"] is False
    assert gate2["checks"]["validation_both_directions"] is False


def test_no_signal_is_not_neutral_and_threshold_is_frozen():
    c = contract()
    assert c["routing"]["NO_SIGNAL_IS_NOT_NEUTRAL"] is True
    assert c["routing"]["trust_probability_min"] == 0.60
    assert c["rtq_model"]["direction_rule"] == "q25>0 => UP; q75<0 => DOWN; otherwise NO_SIGNAL"
