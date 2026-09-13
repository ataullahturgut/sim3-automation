import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v170_research/contracts/v170a_free_public_data_acquisition_freeze_v1.json"


def test_v170a_contract_is_data_only_and_frozen_before_scoring():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "FROZEN_BEFORE_ANY_V170_FORECAST_SCORING"
    assert c["sources"]["legacy_futures_only"]["dataset_id"] == "6dca-aqww"
    assert c["sources"]["disaggregated_futures_only"]["dataset_id"] == "72hh-3qpy"
    assert c["sources"]["legacy_futures_only"]["contract_market_code"] == "088691"
    assert c["capture_window"] == ["2023-01-01", "2026-06-30"]
    assert "report_date + 6 calendar days" in c["pit_clock_rule_for_later_modeling"]
    forbidden = set(c["forbidden_in_v170a"])
    assert "forecast_scoring" in forbidden
    assert "forecast_model_fit" in forbidden
    assert "feature_selection_using_outcomes" in forbidden
    assert c["governance"]["AUTO_SELECTOR"] == "OFF"
    assert c["governance"]["AUTO_ENSEMBLE"] == "OFF"
    assert c["governance"]["production_authority"] is False
