from __future__ import annotations

from forecast_source import (
    TRACK_EARLY_INDICATIVE,
    TRACK_HISTORICAL_REPLAY,
    TRACK_MONTH_END,
    fetch_expert_forecast_history,
    fetch_latest_expert_forecasts,
)
from production_display_snapshot import (
    SNAPSHOT_CONTRACT,
    load_production_display_snapshot,
    snapshot_historical_replay_rows,
)


def test_v2_snapshot_contains_only_governed_replay_rows() -> None:
    snapshot = load_production_display_snapshot()
    assert snapshot["snapshot_contract"] == SNAPSHOT_CONTRACT
    rows = snapshot_historical_replay_rows(snapshot)
    assert {row["expert_id"] for row in rows} == {"MOMENTUM_3M", "RANDOM_WALK"}
    assert len(rows) == 2
    for row in rows:
        assert row["forecast_track"] == TRACK_HISTORICAL_REPLAY
        assert row["evidence_class"] == "HISTORICAL_REPLAY"
        assert row["canonical_authority"] is False
        assert row["selector_status"] == "NOT_PROVEN_EXPERT_SELECTION_RULE"
        assert row["auto_selector"] == "OFF"
        assert row["auto_ensemble"] == "OFF"
        p = row["provenance"]
        assert p["historical_replay"] is True
        assert p["prospective_claim"] is False
        assert p["canonical_authority"] is False
        assert p["direction_vote_permitted"] is False


def test_no_db_url_reads_replay_from_snapshot_but_not_other_tracks() -> None:
    replay = fetch_latest_expert_forecasts("", TRACK_HISTORICAL_REPLAY)
    history = fetch_expert_forecast_history("", TRACK_HISTORICAL_REPLAY)
    assert len(replay) == 2
    assert len(history) == 2
    assert {row["expert_id"] for row in replay} == {"MOMENTUM_3M", "RANDOM_WALK"}
    assert all(float(row["forecast_value"]) > 0 for row in replay)
    assert fetch_latest_expert_forecasts("", TRACK_MONTH_END) == []
    assert fetch_latest_expert_forecasts("", TRACK_EARLY_INDICATIVE) == []


def test_replay_snapshot_never_becomes_direction_or_canonical_authority() -> None:
    rows = fetch_latest_expert_forecasts("", TRACK_HISTORICAL_REPLAY)
    for row in rows:
        assert row["canonical_authority"] is False
        assert row["provenance"]["direction_vote_permitted"] is False
        assert row["provenance"]["prospective_claim"] is False
