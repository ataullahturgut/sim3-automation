from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r4_1" / "src"))
sys.path.insert(0, str(ROOT))

from gold_r4.contracts import Direction, ReversalAlert  # noqa: E402
from gold_r4.emergency import EmergencyState  # noqa: E402
from r4_2.contracts import MonthlyPriceReference  # noqa: E402
from r4_2.emergency_bridge import evaluate_emergency  # noqa: E402

PATCH_ID = "CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE"
VW_ID = "VW_AUDITED_SHADOW_V2"


def ref(model_id: str, value: float = 1000.0) -> MonthlyPriceReference:
    return MonthlyPriceReference(
        value=value,
        model_id=model_id,
        target_month="2026-10",
        forecast_origin="2026-09-30T21:00:00Z",
        evidence_class="HISTORICAL_REPLAY",
    )


def test_level_geometry_is_model_identity_invariant() -> None:
    ratios = [0.90, 0.96, 0.9601, 1.0, 1.0399, 1.04, 1.10]
    for ratio in ratios:
        legacy = EmergencyState(level_threshold_abs=0.04, reversal_threshold_abs=0.04)
        generic = EmergencyState(level_threshold_abs=0.04, reversal_threshold_abs=0.04)
        date = pd.Timestamp("2026-10-05")
        close = 1000.0 * ratio
        legacy_level, legacy_alert = legacy.update(date, close, 1000.0)
        bridged = evaluate_emergency(
            generic,
            date=date,
            close=close,
            monthly_reference=ref(PATCH_ID),
        )
        assert bridged.level_emergency == legacy_level
        assert bridged.reversal_alert == legacy_alert
        assert bridged.reference_model_id == PATCH_ID


def test_reference_identity_does_not_change_geometry() -> None:
    a = EmergencyState()
    b = EmergencyState()
    date = pd.Timestamp("2026-10-05")
    close = 1040.0
    patch = evaluate_emergency(a, date=date, close=close, monthly_reference=ref(PATCH_ID))
    vw = evaluate_emergency(b, date=date, close=close, monthly_reference=ref(VW_ID))
    assert patch.level_emergency == vw.level_emergency == Direction.UP
    assert patch.reversal_alert == vw.reversal_alert == ReversalAlert.OFF
    assert patch.reference_model_id != vw.reference_model_id


def test_reversal_geometry_is_preserved() -> None:
    legacy = EmergencyState(level_threshold_abs=0.04, reversal_threshold_abs=0.04)
    generic = EmergencyState(level_threshold_abs=0.04, reversal_threshold_abs=0.04)
    r = ref(PATCH_ID)
    seq = [
        ("2026-10-03", 1045.0),
        ("2026-10-04", 1080.0),
        ("2026-10-05", 1036.0),
    ]
    for d, close in seq:
        ll, la = legacy.update(pd.Timestamp(d), close, 1000.0)
        br = evaluate_emergency(generic, date=pd.Timestamp(d), close=close, monthly_reference=r)
        assert br.level_emergency == ll
        assert br.reversal_alert == la
    assert br.reversal_alert == ReversalAlert.DOWN_ALERT


def test_persisted_reference_gate_fails_closed() -> None:
    state = EmergencyState()
    try:
        evaluate_emergency(
            state,
            date=pd.Timestamp("2026-10-05"),
            close=1000.0,
            monthly_reference=ref(PATCH_ID),
            require_persisted_reference=True,
        )
    except ValueError as exc:
        assert "input_snapshot_id" in str(exc)
    else:
        raise AssertionError("missing persistence ids must fail closed")


def test_persisted_reference_gate_passes_with_ids() -> None:
    r = MonthlyPriceReference(
        value=1000.0,
        model_id=PATCH_ID,
        target_month="2026-10",
        forecast_origin="2026-09-30T21:00:00Z",
        evidence_class="PROSPECTIVE_SHADOW",
        input_snapshot_id="snapshot-1",
        forecast_contract_id="forecast-1",
    )
    out = evaluate_emergency(
        EmergencyState(),
        date=pd.Timestamp("2026-10-05"),
        close=1000.0,
        monthly_reference=r,
        require_persisted_reference=True,
    )
    assert out.input_snapshot_id == "snapshot-1"
    assert out.forecast_contract_id == "forecast-1"
