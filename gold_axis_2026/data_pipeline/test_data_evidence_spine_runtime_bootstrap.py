from data_evidence_spine_runtime_bootstrap import STATIC_VERSIONS, STATUS_SPECS


def test_runtime_bootstrap_distribution_matches_governed_operational_state():
    statuses = {engine_id: spec[0] for engine_id, spec in STATUS_SPECS.items()}
    # Four ACTIVE engines are generated from CONTEXT_FEATURES; the remaining eight
    # governed engines below must therefore contribute 5 WAITING and 3 BLOCKED.
    assert sum(v == "WAITING" for v in statuses.values()) == 5
    assert sum(v == "BLOCKED" for v in statuses.values()) == 3


def test_runtime_bootstrap_exact_waiting_and_blocked_identities():
    waiting = {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "WAITING"}
    blocked = {engine_id for engine_id, spec in STATUS_SPECS.items() if spec[0] == "BLOCKED"}
    assert waiting == {
        "CAUSAL_PATCH",
        "MOMENTUM_3M",
        "RANDOM_WALK",
        "EMERGENCY_LEVEL",
        "EMERGENCY_REVERSAL",
    }
    assert blocked == {"VW_MIDAS_MSVR", "MACRO_EVENT", "BOCPD"}


def test_runtime_bootstrap_recovery_status_codes_are_current():
    assert STATUS_SPECS["VW_MIDAS_MSVR"][1] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"
    assert STATUS_SPECS["MACRO_EVENT"][1] == "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED"
    assert STATUS_SPECS["BOCPD"][1] == "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED"
    assert STATUS_SPECS["EMERGENCY_LEVEL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert STATUS_SPECS["EMERGENCY_REVERSAL"][1] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert STATIC_VERSIONS["EMERGENCY_LEVEL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
    assert STATIC_VERSIONS["EMERGENCY_REVERSAL"] == "R4_2_PATCH_EXPERT_REFERENCE_READY_V1"
