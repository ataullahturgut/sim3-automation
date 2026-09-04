from data_evidence_spine_preflight import NEW_OBJECTS, classify_preflight


def _objects(value: bool):
    return {name: value for name in NEW_OBJECTS}


def test_pre_migration_empty_legacy_state_passes():
    r = classify_preflight(
        input_rows=0,
        expert_rows=0,
        derived_rows=7,
        decision_rows=0,
        pit_surface=True,
        legacy_immutability_guards=3,
        object_state=_objects(False),
    )
    assert r["preflight_mode"] == "PRE_MIGRATION"
    assert r["status"] == "PASS_PRE_MIGRATION"
    assert r["passed"] is True


def test_pre_migration_existing_expert_rows_fail_closed():
    r = classify_preflight(
        input_rows=5,
        expert_rows=2,
        derived_rows=14,
        decision_rows=0,
        pit_surface=True,
        legacy_immutability_guards=3,
        object_state=_objects(False),
    )
    assert r["preflight_mode"] == "PRE_MIGRATION"
    assert r["status"] == "BLOCKED_PRE_MIGRATION_RECONCILIATION"
    assert r["passed"] is False


def test_already_migrated_governed_rows_are_deferred_to_integrity_audit():
    r = classify_preflight(
        input_rows=5,
        expert_rows=2,
        derived_rows=14,
        decision_rows=0,
        pit_surface=True,
        legacy_immutability_guards=3,
        object_state=_objects(True),
    )
    assert r["preflight_mode"] == "ALREADY_MIGRATED"
    assert r["status"] == "PASS_ALREADY_MIGRATED"
    assert r["passed"] is True
    assert r["existing_row_reconciliation_required"] is True
    assert r["existing_rows_allowed_in_mode"] is True


def test_already_migrated_decision_authority_rows_fail_closed():
    r = classify_preflight(
        input_rows=5,
        expert_rows=2,
        derived_rows=14,
        decision_rows=1,
        pit_surface=True,
        legacy_immutability_guards=3,
        object_state=_objects(True),
    )
    assert r["status"] == "BLOCKED_POST_MIGRATION_INTEGRITY"
    assert r["passed"] is False


def test_partial_migration_always_fails_closed():
    state = _objects(False)
    state[NEW_OBJECTS[0]] = True
    r = classify_preflight(
        input_rows=0,
        expert_rows=0,
        derived_rows=7,
        decision_rows=0,
        pit_surface=True,
        legacy_immutability_guards=3,
        object_state=state,
    )
    assert r["preflight_mode"] == "PARTIAL_MIGRATION"
    assert r["status"] == "BLOCKED_PARTIAL_MIGRATION"
    assert r["passed"] is False
