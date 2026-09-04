from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r4_1" / "src"))
sys.path.insert(0, str(ROOT))

from gold_r4.contracts import Direction  # noqa: E402
from gold_r4.emergency import EmergencyState  # noqa: E402
from r4_2.emergency_bridge import evaluate_emergency  # noqa: E402
from r4_2.monthly_expert_reference import patch_expert_monthly_reference  # noqa: E402


def patch_row(**overrides):
    row = {
        "id": 123,
        "target_month": "2026-10-01",
        "forecast_origin": "2026-09-30T21:30:00+00:00",
        "forecast_track": "MONTH_END_EXPERT",
        "expert_id": "CAUSAL_PATCH",
        "model_name": "Causal Patch R1",
        "model_version": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "forecast_value": 4500.0,
        "evidence_class": "PROSPECTIVE_SHADOW",
        "input_set_id": "c267da01-78b4-482d-9ff2-c5ceee1405a5",
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "canonical_authority": False,
    }
    row.update(overrides)
    return row


def test_patch_expert_reference_preserves_multi_expert_identity() -> None:
    ref = patch_expert_monthly_reference(patch_row())
    assert ref.persisted_identity_family() == "MONTHLY_EXPERT_FORECAST"
    assert ref.expert_forecast_id == "123"
    assert ref.input_set_id == "c267da01-78b4-482d-9ff2-c5ceee1405a5"
    assert ref.forecast_contract_id is None
    assert ref.input_snapshot_id is None
    assert ref.target_month == "2026-10"
    assert ref.evidence_class == "PROSPECTIVE_SHADOW"


def test_patch_expert_reference_runs_frozen_emergency_geometry() -> None:
    ref = patch_expert_monthly_reference(patch_row())
    out = evaluate_emergency(
        EmergencyState(level_threshold_abs=0.04, reversal_threshold_abs=0.04),
        date=pd.Timestamp("2026-10-05"),
        close=4680.0,
        monthly_reference=ref,
        require_persisted_reference=True,
    )
    assert out.level_emergency == Direction.UP
    assert out.reference_identity_family == "MONTHLY_EXPERT_FORECAST"
    assert out.expert_forecast_id == "123"
    assert out.input_set_id == ref.input_set_id
    assert out.forecast_contract_id is None


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"expert_id": "RANDOM_WALK"}, "unsupported emergency expert reference"),
        ({"forecast_track": "HISTORICAL_REPLAY"}, "requires MONTH_END_EXPERT"),
        ({"evidence_class": "HISTORICAL_REPLAY"}, "requires prospective evidence"),
        ({"canonical_authority": True}, "canonical_authority=false"),
        ({"auto_selector": "ON"}, "AUTO_SELECTOR=OFF"),
        ({"auto_ensemble": "ON"}, "AUTO_ENSEMBLE=OFF"),
        ({"selector_status": "PROVEN"}, "NOT_PROVEN_EXPERT_SELECTION_RULE"),
        ({"input_set_id": None}, "persisted id and input_set_id"),
        ({"id": None}, "persisted id and input_set_id"),
    ],
)
def test_patch_expert_reference_fails_closed(overrides, expected) -> None:
    with pytest.raises(ValueError, match=expected):
        patch_expert_monthly_reference(patch_row(**overrides))
