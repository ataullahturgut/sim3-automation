from __future__ import annotations

import copy

import pytest

from aug31_state_replay_source import (
    BLOCKERS,
    SOURCE_SNAPSHOT,
    fetch_aug31_state_replay,
    load_snapshot,
    validate_snapshot,
)


def test_snapshot_fallback_exposes_aug31_replay_without_authority() -> None:
    state = fetch_aug31_state_replay("")
    assert state["source_mode"] == SOURCE_SNAPSHOT
    assert state["evidence_class"] == "HISTORICAL_REPLAY"
    assert state["state_as_of"] == "2026-08-31T21:00:00+00:00"
    assert state["monthly_direction_3m"] == "DOWN"
    assert state["fast_state"] == "ROBUST_UP"
    assert state["slow_state"] == "ROBUST_UP"
    assert state["gvz_value"] == pytest.approx(24.40)
    assert state["gvz_cap"] == pytest.approx(1.0)
    assert state["gvz_panic"] is False
    assert state["gvz_regime"] == "NORMAL"
    assert state["blocked_components"] == BLOCKERS
    assert state["prospective_h1_claim"] is False
    assert state["current_runtime_authority"] is False
    assert state["canonical_authority"] is False
    assert state["direction_vote_permitted"] is False
    assert state["database_writes"] == "NONE"


def test_snapshot_tamper_fails_closed() -> None:
    snapshot = load_snapshot()
    tampered = copy.deepcopy(snapshot)
    tampered["features"][0]["value_text"] = "TAMPERED"
    with pytest.raises(RuntimeError, match="FINGERPRINT_INVALID"):
        validate_snapshot(tampered)


def test_snapshot_blocker_tamper_fails_closed() -> None:
    snapshot = load_snapshot()
    tampered = copy.deepcopy(snapshot)
    tampered["blocked_components"]["BOCPD"] = "FAKE_PASS"
    with pytest.raises(RuntimeError, match="FINGERPRINT_INVALID|BLOCKERS_INVALID"):
        validate_snapshot(tampered)
