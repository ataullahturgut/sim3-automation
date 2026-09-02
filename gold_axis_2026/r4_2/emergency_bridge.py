from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from gold_r4.contracts import Direction, ReversalAlert
from gold_r4.emergency import EmergencyState

from .contracts import MonthlyPriceReference


@dataclass(frozen=True)
class EmergencyBridgeResult:
    level_emergency: Direction
    reversal_alert: ReversalAlert
    reference_model_id: str
    reference_target_month: str
    reference_evidence_class: str
    input_snapshot_id: str | None
    forecast_contract_id: str | None


def evaluate_emergency(
    state: EmergencyState,
    *,
    date: pd.Timestamp,
    close: float,
    monthly_reference: MonthlyPriceReference,
    require_persisted_reference: bool = False,
) -> EmergencyBridgeResult:
    """Apply the frozen R4.1 Emergency geometry to an explicitly named reference.

    This function intentionally passes only the numeric reference value into the
    frozen EmergencyState calculation. The model identity is carried separately
    and is never relabelled as ``monthly_vw_forecast``.
    """

    monthly_reference.validate(require_persisted_ids=require_persisted_reference)
    level, alert = state.update(date, close, monthly_reference.value)
    return EmergencyBridgeResult(
        level_emergency=level,
        reversal_alert=alert,
        reference_model_id=monthly_reference.model_id,
        reference_target_month=monthly_reference.target_month,
        reference_evidence_class=monthly_reference.evidence_class,
        input_snapshot_id=monthly_reference.input_snapshot_id,
        forecast_contract_id=monthly_reference.forecast_contract_id,
    )
