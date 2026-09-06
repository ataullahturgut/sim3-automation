from data_evidence_spine_runtime_bootstrap import CURRENT_MONTH_REFERENCES, STATIC_VERSIONS, STATUS_SPECS


def test_runtime_bootstrap_distribution_matches_v141_current_surface():
    statuses = {engine_id: spec[0] for engine_id, spec in STATUS_SPECS.items()}
    assert len(statuses) == 12
    assert sum(v == "ACTIVE" for v in statuses.values()) == 12
    assert sum(v == "WAITING" for v in statuses.values()) == 0
    assert sum(v == "BLOCKED" for v in statuses.values()) == 0


def test_runtime_bootstrap_has_no_waiting_identity():
    waiting = {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "WAITING"}
    assert waiting == set()


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
