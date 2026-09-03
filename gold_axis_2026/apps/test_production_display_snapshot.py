from __future__ import annotations

import copy

import pytest

from decision_source import fetch_current_decision_state
from production_display_snapshot import (
    SNAPSHOT_SOURCE_MODE,
    load_production_display_snapshot,
    validate_production_display_snapshot,
)
from runtime_source import fetch_runtime_observability


def _feature_map(snapshot):
    return {row["feature_name"]: row["value_text"] for row in snapshot["features"]}


def test_missing_database_url_uses_validated_production_snapshot() -> None:
    snapshot = load_production_display_snapshot()
    expected = _feature_map(snapshot)

    state = fetch_current_decision_state("")
    assert state is not None
    assert state["source_mode"] == SNAPSHOT_SOURCE_MODE
    assert state["context_only"] is True
    assert state["monthly_direction_3m"] == expected["MONTHLY_DIRECTION_3M"]
    assert state["fast_state"] == expected["FAST_STATE"]
    assert state["slow_state"] == expected["SLOW_STATE"]
    assert state["monthly_direction_3m"] not in {"", "YAYIMLANMADI", "NOT_ISSUED"}
    assert state["fast_state"] not in {"", "YAYIMLANMADI", "NOT_ISSUED"}
    assert state["slow_state"] not in {"", "YAYIMLANMADI", "NOT_ISSUED"}
    assert state["gvz"] == float(expected["GVZ_VALUE"])
    assert state["gvz_cap"] == float(expected["GVZ_CAP"])
    assert state["gvz_regime"] == expected["GVZ_REGIME"]
    assert state["classification"] is None
    assert state["action_state"] is None
    assert state["prospective_h1_claim"] is False


def test_missing_database_url_runtime_uses_snapshot_without_promoting_authority() -> None:
    snapshot = load_production_display_snapshot()
    runtime = fetch_runtime_observability("")

    assert runtime["source_mode"] == SNAPSHOT_SOURCE_MODE
    assert runtime["runtime_engine_count"] == 12
    assert runtime["context_exactly_one_link"] == 7
    assert runtime["integrity_ok"] is True
    assert runtime["database_writes"] == "NONE"

    states = {row["engine_id"]: row for row in runtime["runtime"]}
    assert len(states) == 12
    expected_states = {row["engine_id"]: row for row in snapshot["runtime"]}
    assert set(states) == set(expected_states)
    assert sum(1 for row in states.values() if row.get("direction_vote_permitted") is True) == sum(
        1 for row in expected_states.values() if row.get("direction_vote_permitted") is True
    )


def test_snapshot_fingerprint_tamper_fails_closed() -> None:
    snapshot = load_production_display_snapshot()
    tampered = copy.deepcopy(snapshot)
    tampered["features"][0]["value_text"] = "TAMPERED"
    with pytest.raises(RuntimeError, match="FINGERPRINT_MISMATCH"):
        validate_production_display_snapshot(tampered)
