from __future__ import annotations

import json
from pathlib import Path

from gold_axis_2026.tools.build_v149_phase2_engine_state_pit_panel import build_rows, write_artifacts

ROOT = Path(__file__).resolve().parents[1]


def test_exact_origin_and_target_maturity_counts():
    rows = build_rows()
    assert len(rows) == 400
    assert len({r["origin_date"] for r in rows}) == 400
    assert sum(r["target_1d_maturity"] == "MATURED" for r in rows) == 399
    assert sum(r["target_3d_maturity"] == "MATURED" for r in rows) == 397
    for i, row in enumerate(rows):
        if row["target_1d_date"]:
            assert row["target_1d_date"] == rows[i + 1]["origin_date"]
        if row["target_3d_date"]:
            assert row["target_3d_date"] == rows[i + 3]["origin_date"]


def test_asof_and_fail_closed_lanes():
    for row in build_rows():
        assert not row["gvz_source_date"] or row["gvz_source_date"] <= row["origin_date"]
        assert row["gvz_pit_status"].startswith("BLOCKED_PIT")
        assert row["macro_event_v2_pit_status"].startswith("BLOCKED_")
        assert row["bocpd_pit_status"].startswith("BLOCKED_DATA")
        assert row["market_shock_v3_status"] == "NOT_FOUND_CANONICAL"
        assert row["scoring_eligibility"] == "B0_AND_B4_ONLY_NO_NEW_PHASE2_SCORE"
        assert row["prospective_claim"] == "false"


def test_roles_are_not_converted_to_equal_direction_votes():
    contract = json.loads((ROOT / "v149_phase2/contracts/role_preserving_short_horizon_prereg_v1.json").read_text())
    roles = contract["role_constraints"]
    assert "not direction vote" in roles["GVZ_RISK"]
    assert "regime interaction only" in roles["BOCPD_RETURN_SUCCESSOR_V1"]
    assert "not an unconditional vote" in roles["FAST"]
    assert contract["auto_selector"] == contract["auto_ensemble"] == "OFF"


def test_deterministic_serialization(tmp_path):
    a, am = tmp_path / "a.csv", tmp_path / "a.json"
    b, bm = tmp_path / "b.csv", tmp_path / "b.json"
    ma = write_artifacts(a, am); mb = write_artifacts(b, bm)
    assert a.read_bytes() == b.read_bytes()
    assert ma["output_sha256"] == mb["output_sha256"]
    assert ma["source_hashes"] == mb["source_hashes"]


def test_event_study_is_separate_and_market_shock_is_blocked():
    contract = json.loads((ROOT / "v149_phase2/contracts/macro_event_market_shock_event_study_prereg_v1.json").read_text())
    assert contract["status"] == "FROZEN_DESIGN_BLOCKED_MARKET_SHOCK_INVENTORY"
    assert contract["market_shock_artifact_status"] == "NOT_FOUND_CANONICAL"
    assert contract["separate_from_general_daily_model"] is True
