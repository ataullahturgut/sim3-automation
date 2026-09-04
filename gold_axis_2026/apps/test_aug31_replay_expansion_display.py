from __future__ import annotations

from aug31_replay_expansion_display import attach_aug31_replay_expansion
from aug31_replay_expansion_source import SOURCE_SNAPSHOT, _shape, load_snapshot


def test_snapshot_contract_and_shape() -> None:
    snapshot = load_snapshot()
    shaped = _shape(
        [dict(row) for row in snapshot["features"]],
        source_mode=SOURCE_SNAPSHOT,
        snapshot_sha256=snapshot["payload_sha256"],
        source_state_at=snapshot["source_state_at"],
    )
    assert shaped["causal_patch_forecast"] == 4452.046728838838
    assert shaped["causal_patch_daily_max_date"] == "2026-08-30"
    assert shaped["emergency_level"] == "NEUTRAL"
    assert shaped["emergency_reversal"] == "OFF"
    assert shaped["bocpd_successor_state"] == "NO_ADVERSE_BREAK_CANDIDATE"
    assert shaped["bocpd_archived_engine_status"] == "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED"
    assert shaped["prospective_claim"] is False
    assert shaped["canonical_authority"] is False
    assert shaped["direction_vote_permitted"] is False
    assert shaped["auto_selector"] == "OFF"
    assert shaped["auto_ensemble"] == "OFF"


def test_display_attachment_preserves_operational_status() -> None:
    snapshot = load_snapshot()
    replay = _shape(
        [dict(row) for row in snapshot["features"]],
        source_mode=SOURCE_SNAPSHOT,
        snapshot_sha256=snapshot["payload_sha256"],
        source_state_at=snapshot["source_state_at"],
    )
    rows = [
        {"engine_id": "CAUSAL_PATCH", "status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "runtime_status": "WAITING", "direction_vote": False},
        {"engine_id": "EMERGENCY_LEVEL", "status": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "runtime_status": "WAITING", "direction_vote": False},
        {"engine_id": "EMERGENCY_REVERSAL", "status": "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "runtime_status": "WAITING", "direction_vote": False},
        {"engine_id": "BOCPD", "status": "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED", "runtime_status": "BLOCKED", "direction_vote": False},
    ]
    out = attach_aug31_replay_expansion(rows, replay)
    by_id = {row["engine_id"]: row for row in out}
    assert by_id["CAUSAL_PATCH"]["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert by_id["CAUSAL_PATCH"]["replay_reference"]["output"] == 4452.046728838838
    assert by_id["EMERGENCY_LEVEL"]["status"] == "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE"
    assert by_id["EMERGENCY_LEVEL"]["replay_reference"]["output"] == "NEUTRAL"
    assert by_id["EMERGENCY_REVERSAL"]["replay_reference"]["output"] == "OFF"
    assert by_id["BOCPD"]["status"].startswith("BLOCKED_")
    assert by_id["BOCPD"]["replay_reference"]["version"] == "BOCPD_RETURN_SUCCESSOR_V1"
    assert by_id["BOCPD"]["replay_reference"]["output"] == "NO_ADVERSE_BREAK_CANDIDATE"
    assert all(row.get("direction_vote") is False for row in out)
