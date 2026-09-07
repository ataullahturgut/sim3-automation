from __future__ import annotations

import copy

import pytest

from production_display_snapshot import (
    AUTHORITY_ZERO_FIELDS,
    CURRENT_CONTEXT_FEATURES,
    CURRENT_ENGINE_IDS,
    SNAPSHOT_CONTRACT,
    payload_sha256,
    validate_production_display_snapshot,
)


def _snapshot() -> dict:
    runtime = [
        {
            "engine_id": engine_id,
            "engine_version": f"current::{engine_id}",
            "engine_role": "CURRENT_ROLE",
            "as_of": "2026-09-06T19:35:41Z",
            "target_context": "2026-09",
            "evidence_class": "RUNTIME_GOVERNANCE_AUDIT",
            "runtime_status": "ACTIVE",
            "status_code": "ACTIVE_CURRENT_CONTEXT_AVAILABLE",
            "direction_vote_permitted": engine_id in {"MONTHLY_DIRECTION_3M", "FAST", "SLOW"},
            "git_commit": "test-sha",
            "metadata": {},
        }
        for engine_id in CURRENT_ENGINE_IDS
    ]
    features = [
        {
            "feature_name": feature_name,
            "feature_version": "CURRENT_TEST",
            "calculation_ts": "2026-09-03T10:14:35Z",
            "input_cutoff": "2026-09-03T01:26:55Z",
            "value_num": None,
            "value_text": "TEST",
            "quality_status": "TEST_CONTEXT",
            "metadata": {"target_context": "2026-09"},
        }
        for feature_name in CURRENT_CONTEXT_FEATURES
    ]
    snapshot = {
        "snapshot_contract": SNAPSHOT_CONTRACT,
        "source": "TEST",
        "source_state_at": "2026-09-06T19:35:41Z",
        "target_context": "2026-09",
        "runtime": runtime,
        "features": features,
        "health": {
            "orphan_input_snapshots": 0,
            "expert_rows_without_input_set": 0,
            "expert_input_fingerprint_mismatches": 0,
        },
        "authority_store_counts": {key: 0 for key in AUTHORITY_ZERO_FIELDS},
        "database_writes": "NONE",
    }
    snapshot["payload_sha256"] = payload_sha256(snapshot)
    return snapshot


def test_current_snapshot_contract_accepts_exact_current_surface() -> None:
    snapshot = validate_production_display_snapshot(_snapshot())
    assert snapshot["snapshot_contract"] == SNAPSHOT_CONTRACT
    assert len(snapshot["runtime"]) == 12
    assert {row["engine_id"] for row in snapshot["runtime"]} == set(CURRENT_ENGINE_IDS)


def test_snapshot_fingerprint_tamper_fails_closed() -> None:
    snapshot = _snapshot()
    tampered = copy.deepcopy(snapshot)
    tampered["features"][0]["value_text"] = "TAMPERED"
    with pytest.raises(RuntimeError, match="FINGERPRINT_MISMATCH"):
        validate_production_display_snapshot(tampered)


def test_snapshot_rejects_non_active_current_runtime() -> None:
    snapshot = _snapshot()
    snapshot["runtime"][0]["runtime_status"] = "WAITING"
    snapshot["payload_sha256"] = payload_sha256(snapshot)
    with pytest.raises(RuntimeError, match="RUNTIME_NOT_ALL_ACTIVE"):
        validate_production_display_snapshot(snapshot)


def test_snapshot_rejects_authority_store_writes() -> None:
    snapshot = _snapshot()
    snapshot["authority_store_counts"]["decision_runs"] = 1
    snapshot["payload_sha256"] = payload_sha256(snapshot)
    with pytest.raises(RuntimeError, match="UNAUTHORIZED_AUTHORITY_STATE"):
        validate_production_display_snapshot(snapshot)
