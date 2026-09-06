from data_evidence_spine_runtime_bootstrap import STATIC_VERSIONS, STATUS_SPECS, VW_SEPTEMBER_REFERENCE


def test_runtime_bootstrap_distribution_matches_v139_target():
    statuses = {engine_id: spec[0] for engine_id, spec in STATUS_SPECS.items()}
    # Four persisted context engines + two validated context successors are ACTIVE.
    # VW/MSVR Successor V1 is also ACTIVE as a non-prospective September
    # historical-replay current-month reference. Five governed identities remain WAITING.
    assert sum(v == "ACTIVE" for v in statuses.values()) == 1
    assert sum(v == "WAITING" for v in statuses.values()) == 5
    assert sum(v == "BLOCKED" for v in statuses.values()) == 0


def test_runtime_bootstrap_exact_waiting_identities():
    waiting = {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "WAITING"}
    assert waiting == {
        "CAUSAL_PATCH",
        "MOMENTUM_3M",
        "RANDOM_WALK",
        "EMERGENCY_LEVEL",
        "EMERGENCY_REVERSAL",
    }


def test_runtime_bootstrap_vw_current_reference_is_active_and_nonprospective():
    assert STATUS_SPECS["VW_MIDAS_MSVR_SUCCESSOR_V1"][0] == "ACTIVE"
    assert STATUS_SPECS["VW_MIDAS_MSVR_SUCCESSOR_V1"][1] == "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE"
    assert STATIC_VERSIONS["VW_MIDAS_MSVR_SUCCESSOR_V1"] == "VW_MIDAS_MSVR_SUCCESSOR_V1"
    assert VW_SEPTEMBER_REFERENCE["reference_kind"] == "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE"
    assert VW_SEPTEMBER_REFERENCE["evidence_class"] == "HISTORICAL_REPLAY"
    assert VW_SEPTEMBER_REFERENCE["target_month"] == "2026-09"
    assert VW_SEPTEMBER_REFERENCE["forecast_value"] == 4565.115907930242
    assert VW_SEPTEMBER_REFERENCE["canonical_authority"] is False
    assert VW_SEPTEMBER_REFERENCE["prospective_claim"] is False
    assert VW_SEPTEMBER_REFERENCE["auto_selector"] == "OFF"
    assert VW_SEPTEMBER_REFERENCE["auto_ensemble"] == "OFF"


def test_runtime_bootstrap_emergency_status_codes_are_current():
    assert STATUS_SPECS["EMERGENCY_LEVEL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert STATUS_SPECS["EMERGENCY_REVERSAL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert STATIC_VERSIONS["EMERGENCY_LEVEL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
    assert STATIC_VERSIONS["EMERGENCY_REVERSAL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
