from data_evidence_spine_runtime_bootstrap import (
    ACTIVE_SUCCESSORS,
    CONTEXT_FEATURES,
    CURRENT_MONTH_REFERENCES,
    STATIC_VERSIONS,
    STATUS_SPECS,
)


def test_runtime_bootstrap_partition_is_exactly_twelve_current_identities():
    status_ids = set(STATUS_SPECS)
    context_ids = set(CONTEXT_FEATURES)
    successor_ids = set(ACTIVE_SUCCESSORS)
    assert status_ids.isdisjoint(context_ids)
    assert status_ids.isdisjoint(successor_ids)
    assert context_ids.isdisjoint(successor_ids)
    assert len(status_ids | context_ids | successor_ids) == 12
    assert {spec[0] for spec in STATUS_SPECS.values()} == {"ACTIVE"}


def test_runtime_bootstrap_has_no_waiting_or_blocked_status_spec():
    assert not {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "WAITING"}
    assert not {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "BLOCKED"}


def test_runtime_bootstrap_vw_current_reference_is_active_and_nonprospective():
    assert STATUS_SPECS["VW_MIDAS_MSVR_SUCCESSOR_V1"][0] == "ACTIVE"
    assert STATUS_SPECS["VW_MIDAS_MSVR_SUCCESSOR_V1"][1] == "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE"
    assert STATIC_VERSIONS["VW_MIDAS_MSVR_SUCCESSOR_V1"] == "VW_MIDAS_MSVR_SUCCESSOR_V1"
    ref = CURRENT_MONTH_REFERENCES["VW_MIDAS_MSVR_SUCCESSOR_V1"]
    assert ref["reference_kind"] == "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE"
    assert ref["evidence_class"] == "HISTORICAL_REPLAY"
    assert ref["target_month"] == "2026-09"
    assert ref["forecast_value"] == 4565.115907930242
    assert ref["canonical_authority"] is False
    assert ref["prospective_claim"] is False
    assert ref["auto_selector"] == "OFF"
    assert ref["auto_ensemble"] == "OFF"


def test_runtime_bootstrap_current_september_references_are_nonprospective():
    assert set(CURRENT_MONTH_REFERENCES) == {
        "CAUSAL_PATCH",
        "VW_MIDAS_MSVR_SUCCESSOR_V1",
        "MOMENTUM_3M",
        "RANDOM_WALK",
        "EMERGENCY_LEVEL",
        "EMERGENCY_REVERSAL",
    }
    for engine_id, ref in CURRENT_MONTH_REFERENCES.items():
        assert STATUS_SPECS[engine_id][0] == "ACTIVE"
        assert ref["evidence_class"] == "HISTORICAL_REPLAY"
        assert ref["target_month"] == "2026-09"
        assert ref["forecast_origin"] == "2026-08-31T21:00:00Z"
        assert ref["prospective_claim"] is False
        assert ref["canonical_authority"] is False
        assert ref["auto_selector"] == "OFF"
        assert ref["auto_ensemble"] == "OFF"


def test_runtime_bootstrap_emergency_status_codes_are_current():
    assert STATUS_SPECS["EMERGENCY_LEVEL"][1] == "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE"
    assert STATUS_SPECS["EMERGENCY_REVERSAL"][1] == "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE"
    assert STATIC_VERSIONS["EMERGENCY_LEVEL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
    assert STATIC_VERSIONS["EMERGENCY_REVERSAL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
