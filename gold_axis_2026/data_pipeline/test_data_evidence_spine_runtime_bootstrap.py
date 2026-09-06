from data_evidence_spine_runtime_bootstrap import STATIC_VERSIONS, STATUS_SPECS


def test_runtime_bootstrap_waiting_distribution_matches_v138_target():
    statuses = {engine_id: spec[0] for engine_id, spec in STATUS_SPECS.items()}
    # Four persisted context engines plus two validated context successors are ACTIVE.
    # The remaining six current governed identities are WAITING; none is BLOCKED.
    assert sum(v == "WAITING" for v in statuses.values()) == 6
    assert sum(v == "BLOCKED" for v in statuses.values()) == 0


def test_runtime_bootstrap_exact_waiting_identities():
    waiting = {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "WAITING"}
    assert waiting == {
        "CAUSAL_PATCH",
        "VW_MIDAS_MSVR_SUCCESSOR_V1",
        "MOMENTUM_3M",
        "RANDOM_WALK",
        "EMERGENCY_LEVEL",
        "EMERGENCY_REVERSAL",
    }


def test_runtime_bootstrap_successor_status_codes_are_current():
    assert STATUS_SPECS["VW_MIDAS_MSVR_SUCCESSOR_V1"][1] == "WAITING_ORIGIN_NOT_REACHED"
    assert STATUS_SPECS["EMERGENCY_LEVEL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert STATUS_SPECS["EMERGENCY_REVERSAL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert STATIC_VERSIONS["VW_MIDAS_MSVR_SUCCESSOR_V1"] == "VW_MIDAS_MSVR_SUCCESSOR_V1"
    assert STATIC_VERSIONS["EMERGENCY_LEVEL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
    assert STATIC_VERSIONS["EMERGENCY_REVERSAL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
