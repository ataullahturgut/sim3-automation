from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "gold_axis_2026/tools/audit_component_verification_v145_r3.py"
SPEC = importlib.util.spec_from_file_location("component_r3", MODULE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def test_role_evidence_fingerprint_and_governance():
    value = m.role_evidence()
    assert value["performance_fields_consumed"] is False
    assert value["production_writes"] == "NONE"
    assert value["auto_selector"] == "OFF"
    assert value["auto_ensemble"] == "OFF"


def test_all_non_bocpd_replay_gates_exist():
    value = m.role_evidence()
    assert set(value["h1_2026_08"]) == {"CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK"}
    assert set(value["ny17_context"]) == {"MONTHLY_DIRECTION_3M", "FAST", "SLOW", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"}
    assert value["gvz"]["pilot_cells_executed"] == 20
    assert value["macro_event"]["contractual_exclusion"] == "2025-10"


def test_bocpd_blocker_is_fail_closed_and_no_output_was_computed():
    item = m.role_evidence()["bocpd_2026_08"]
    assert item["status"] == "BLOCKED_DATA"
    assert item["blocker_code"] == "CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND"
    assert item["output_computed"] is False

