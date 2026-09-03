from __future__ import annotations

from datetime import datetime, timezone

import pytest

from data_evidence_spine import ForecastInputSetSpec
from multi_expert_forecast import (
    ExpertForecastRecord,
    RW_EXPERT,
    RW_V2_VERSION,
    TRACK_HISTORICAL_REPLAY,
)
from multi_expert_forecast_store import _verify_snapshot_identity_and_pit

ORIGIN = datetime(2026, 8, 31, 21, 0, tzinfo=timezone.utc)
AS_OF = datetime(2026, 9, 3, 19, 10, tzinfo=timezone.utc)


def provenance(**overrides):
    value = {
        "historical_replay": True,
        "prospective_claim": False,
        "information_cutoff": ORIGIN.isoformat(),
        "replay_executed_at": AS_OF.isoformat(),
        "canonical_authority": False,
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    }
    value.update(overrides)
    return value


def record(**overrides):
    value = dict(
        target_month="2026-09",
        forecast_origin=ORIGIN,
        as_of=AS_OF,
        forecast_track=TRACK_HISTORICAL_REPLAY,
        expert_id=RW_EXPERT,
        model_name="RANDOM_WALK",
        model_version=RW_V2_VERSION,
        expert_role="BENCHMARK",
        forecast_value=1.0,
        unit="USD/oz",
        evidence_class="HISTORICAL_REPLAY",
        git_commit="test",
        input_snapshot_ids=(1,),
        input_fingerprint="fp",
        provenance=provenance(),
    )
    value.update(overrides)
    return ExpertForecastRecord(**value)


def test_valid_historical_replay_record() -> None:
    record().validate()


def test_replay_requires_replay_evidence() -> None:
    with pytest.raises(ValueError, match="REQUIRES_REPLAY_EVIDENCE"):
        record(evidence_class="PROSPECTIVE_SHADOW").validate()


def test_replay_cannot_backdate_as_of() -> None:
    bad = record(as_of=ORIGIN, provenance={**provenance(), "replay_executed_at": ORIGIN.isoformat()})
    with pytest.raises(ValueError, match="AS_OF_MUST_BE_AFTER_ORIGIN"):
        bad.validate()


def test_replay_cannot_claim_prospective() -> None:
    with pytest.raises(ValueError, match="PROSPECTIVE_CLAIM_MUST_BE_FALSE"):
        record(provenance=provenance(prospective_claim=True)).validate()


def test_valid_historical_replay_input_set() -> None:
    ForecastInputSetSpec(
        target_month="2026-09",
        forecast_origin=ORIGIN,
        as_of=AS_OF,
        forecast_track="HISTORICAL_REPLAY",
        expert_id="RANDOM_WALK",
        model_name="RANDOM_WALK",
        model_version=RW_V2_VERSION,
        evidence_class="HISTORICAL_REPLAY",
        input_fingerprint="fp",
        git_commit="test",
        metadata=provenance(),
    ).validate()


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, *_args, **_kwargs):
        return None

    def fetchall(self):
        return self.rows


def snapshot_row(*, period_end: str, observation_ts: datetime | None = None, available_as_of: datetime | None = None):
    return {
        "id": 1,
        "forecast_origin": ORIGIN,
        "target_period": "2026-09",
        "model_name": "RANDOM_WALK",
        "model_version": RW_V2_VERSION,
        "observation_ts": observation_ts or ORIGIN,
        "available_as_of": available_as_of or ORIGIN,
        "retrieved_at": AS_OF,
        "metadata": {
            "historical_replay": True,
            "prospective_claim": False,
            "source_period_end": period_end,
        },
    }


def test_replay_snapshot_rejects_source_period_after_origin() -> None:
    cur = FakeCursor([snapshot_row(period_end="2026-09-01T21:00:00+00:00")])
    with pytest.raises(RuntimeError, match="SOURCE_PERIOD_AFTER_ORIGIN"):
        _verify_snapshot_identity_and_pit(cur, record())


def test_replay_snapshot_rejects_observation_after_origin() -> None:
    cur = FakeCursor([
        snapshot_row(
            period_end="2026-08-31T21:00:00+00:00",
            observation_ts=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
        )
    ])
    with pytest.raises(RuntimeError, match="INFORMATION_AFTER_ORIGIN"):
        _verify_snapshot_identity_and_pit(cur, record())


def test_replay_snapshot_accepts_archival_retrieval_after_origin() -> None:
    cur = FakeCursor([snapshot_row(period_end="2026-08-31T21:00:00+00:00")])
    assert _verify_snapshot_identity_and_pit(cur, record()) == (1,)
