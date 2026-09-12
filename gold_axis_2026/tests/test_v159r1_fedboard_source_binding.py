from __future__ import annotations

import json
from pathlib import Path

from gold_axis_2026.v159_thesis import run_v159r1_entry as r1

ROOT = Path(__file__).resolve().parents[1]


def test_overlay_is_frozen_before_any_scoring():
    o = json.loads((ROOT / "v159_thesis/contracts/v159r1_fedboard_source_binding_freeze_v1.json").read_text())
    assert o["status"] == "FROZEN_BEFORE_V159R1_RETROSPECTIVE_SCORING"
    assert o["parent_scoring_status"] == "NO_PERFORMANCE_SCORE_PRODUCED"
    assert o["inheritance_lock"]["trust_probability_min"] == 0.60
    assert o["inheritance_lock"]["primary_horizon_sessions"] == 20
    assert o["inheritance_lock"]["AUTO_SELECTOR"] == "OFF"
    assert o["inheritance_lock"]["AUTO_ENSEMBLE"] == "OFF"
    assert o["inheritance_lock"]["production_authority"] is False


def test_source_binding_uses_original_federal_reserve_releases():
    c = r1.merged_contract()
    s = c["source_binding_revision"]["source_binding"]["series"]
    assert s["DTWEXBGS"]["unique_id"] == "H10/H10/JRXWTFB_N.B"
    assert s["DTWEXBGS"]["package_column"] == "JRXWTFB_N.B"
    assert s["DFII10"]["unique_id"] == "H15/H15/RIFLGFCY10_XII_N.B"
    assert s["DFII10"]["package_column"] == "RIFLGFCY10_XII_N.B"


def test_source_overlay_does_not_change_models_thresholds_or_evaluation():
    parent = json.loads((ROOT / "v159_thesis/contracts/v159_driver_corrected_meta_trust_freeze_v1.json").read_text())
    merged = r1.merged_contract()
    for key in ["windows", "target", "parent_experts", "rtq_model", "corrected_driver_features", "meta_target", "meta_features", "meta_candidates", "routing", "evaluation", "governance"]:
        assert merged[key] == parent[key]
    assert merged["contract_id"] != parent["contract_id"]
