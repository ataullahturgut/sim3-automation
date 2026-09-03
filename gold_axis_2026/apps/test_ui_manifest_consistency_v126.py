from pathlib import Path

from engine_observability_contract import ENGINE_REGISTRY
from mobile_ui_contract import EXPERT_DISPLAY
from piyasa_contract import gvz_regime


def test_monthly_expert_display_contract_matches_governed_registry():
    for engine_id in ("CAUSAL_PATCH", "VW_MIDAS_MSVR", "MOMENTUM_3M", "RANDOM_WALK"):
        assert EXPERT_DISPLAY[engine_id]["model_version"] == ENGINE_REGISTRY[engine_id]["version"]
        assert EXPERT_DISPLAY[engine_id]["empty_status"] == ENGINE_REGISTRY[engine_id]["default_status"]


def test_promoted_simple_experts_are_waiting_not_source_blocked():
    assert EXPERT_DISPLAY["MOMENTUM_3M"]["model_version"] == "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
    assert EXPERT_DISPLAY["RANDOM_WALK"]["model_version"] == "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
    assert EXPERT_DISPLAY["MOMENTUM_3M"]["empty_status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert EXPERT_DISPLAY["RANDOM_WALK"]["empty_status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"


def test_gvz_frozen_threshold_mapping_is_available():
    assert gvz_regime(25.9795, full_max=25.9795, half_max=30.5238) == "NORMAL"
    assert gvz_regime(26.14, full_max=25.9795, half_max=30.5238) == "ELEVATED"
    assert gvz_regime(30.6, full_max=25.9795, half_max=30.5238) == "PANIC"


def test_current_ui_source_contains_no_stale_v123_or_r1_simple_expert_contract():
    root = Path(__file__).resolve().parent
    mobile = (root / "gold_control_mobile_v1.py").read_text(encoding="utf-8")
    contract = (root / "mobile_ui_contract.py").read_text(encoding="utf-8")
    entry = (root / "gold_control.py").read_text(encoding="utf-8")
    assert "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND" not in contract
    assert "MOMENTUM_3M_R1" not in contract
    assert "RW_R1" not in contract
    assert "MANIFEST_V1_23" not in mobile
    assert "manifest v1.23" not in entry
    assert "gvz_regime(float(value), full_max=" in mobile
    assert "gc-engine-grid" in mobile
    assert "SENARYOLAR HENÜZ YAYIMLANMADI" in mobile
    assert "ÖZET METRİKLER" in mobile
