from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from data_evidence_spine import (
    ENGINE_IDS,
    RUNTIME_EVIDENCE_CLASSES,
    RUNTIME_STATUSES,
    SPINE_CONTRACT,
    ForecastInputSetSpec,
)


ROOT = Path(__file__).resolve().parent
MIGRATION = ROOT / "schema_patch_data_evidence_spine_neon_v1.sql"
STORE = ROOT / "multi_expert_forecast_store.py"


def _spec(**overrides):
    origin = datetime(2026, 9, 30, 21, 0, tzinfo=timezone.utc)
    data = {
        "target_month": "2026-10",
        "forecast_origin": origin,
        "as_of": origin,
        "forecast_track": "MONTH_END_EXPERT",
        "expert_id": "CAUSAL_PATCH",
        "model_name": "CAUSAL_PATCH_R1",
        "model_version": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "evidence_class": "PROSPECTIVE_SHADOW",
        "input_fingerprint": "abc123",
        "git_commit": "deadbeef",
        "metadata": {},
    }
    data.update(overrides)
    return ForecastInputSetSpec(**data)


def test_contract_and_engine_inventory_are_exact():
    assert SPINE_CONTRACT == "FROZEN_DATA_EVIDENCE_SPINE_V1"
    assert ENGINE_IDS == (
        "CAUSAL_PATCH",
        "VW_MIDAS_MSVR",
        "MOMENTUM_3M",
        "RANDOM_WALK",
        "MONTHLY_DIRECTION_3M",
        "FAST",
        "SLOW",
        "MACRO_EVENT",
        "EMERGENCY_LEVEL",
        "EMERGENCY_REVERSAL",
        "BOCPD",
        "GVZ_RISK",
    )
    assert RUNTIME_STATUSES == {"ACTIVE", "ISSUED", "WAITING", "BLOCKED", "NOT_PROVEN"}
    assert "RUNTIME_GOVERNANCE_AUDIT" in RUNTIME_EVIDENCE_CLASSES


def test_month_end_input_set_requires_exact_origin_as_of():
    _spec().validate()
    with pytest.raises(ValueError, match="MONTH_END_INPUT_SET_AS_OF_MUST_EQUAL_ORIGIN"):
        _spec(as_of=_spec().forecast_origin + timedelta(minutes=1)).validate()


def test_input_set_rejects_future_origin_and_unknown_contract_values():
    origin = _spec().forecast_origin
    with pytest.raises(ValueError, match="INPUT_SET_AS_OF_BEFORE_ORIGIN"):
        _spec(as_of=origin - timedelta(seconds=1)).validate()
    with pytest.raises(ValueError, match="INVALID_INPUT_SET_FORECAST_TRACK"):
        _spec(forecast_track="UNKNOWN").validate()
    with pytest.raises(ValueError, match="INVALID_INPUT_SET_EXPERT"):
        _spec(expert_id="UNKNOWN").validate()
    with pytest.raises(ValueError, match="INVALID_INPUT_SET_EVIDENCE_CLASS"):
        _spec(evidence_class="HISTORICAL_REPLAY").validate()
    with pytest.raises(ValueError, match="INPUT_SET_FINGERPRINT_REQUIRED"):
        _spec(input_fingerprint="").validate()


def test_migration_contains_normalized_fk_append_only_and_runtime_surfaces():
    sql = MIGRATION.read_text(encoding="utf-8")
    required = (
        "CREATE TABLE IF NOT EXISTS forecast_input_sets",
        "CREATE TABLE IF NOT EXISTS forecast_input_set_members",
        "monthly_expert_forecasts_input_set_identity_fkey",
        "CREATE TABLE IF NOT EXISTS engine_execution_runs",
        "CREATE TABLE IF NOT EXISTS engine_execution_derived_outputs",
        "CREATE TABLE IF NOT EXISTS engine_execution_expert_outputs",
        "CREATE TABLE IF NOT EXISTS engine_execution_decision_outputs",
        "CREATE OR REPLACE VIEW latest_engine_runtime_state",
        "CREATE OR REPLACE VIEW data_evidence_spine_health_v1",
    )
    for marker in required:
        assert marker in sql
    for trigger in (
        "trg_forecast_input_sets_immutable",
        "trg_forecast_input_set_members_immutable",
        "trg_engine_execution_runs_immutable",
        "trg_engine_execution_derived_outputs_immutable",
        "trg_engine_execution_expert_outputs_immutable",
        "trg_engine_execution_decision_outputs_immutable",
    ):
        assert trigger in sql
    assert "COMMENT ON" not in sql


def test_store_enforces_point_in_time_and_atomic_runtime_link_contract():
    source = STORE.read_text(encoding="utf-8")
    assert 'row["available_as_of"] > record.as_of' in source
    assert 'row["retrieved_at"] > record.as_of' in source
    assert "BLOCKED_EXPERT_INPUT_SNAPSHOT_PIT_VIOLATION" in source
    assert "create_forecast_input_set(" in source
    assert "forecast_input_set_members" in source
    assert "record_engine_execution(" in source
    assert "engine_execution_expert_outputs" in source
    assert '"selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE"' in source
    assert '"auto_selector": "OFF"' in source
    assert '"auto_ensemble": "OFF"' in source
    assert '"canonical_authority": False' in source
