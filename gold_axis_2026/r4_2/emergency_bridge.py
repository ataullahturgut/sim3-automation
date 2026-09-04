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
    reference_identity_family: str | None
    input_snapshot_id: str | None
    forecast_contract_id: str | None
    input_set_id: str | None
    expert_forecast_id: str | None


def evaluate_emergency(
    state: EmergencyState,
    *,
    date: pd.Timestamp,
    close: float,
    monthly_reference: MonthlyPriceReference,
    require_persisted_reference: bool = False,
) -> EmergencyBridgeResult:
    """Apply frozen R4.1 Emergency geometry to an explicitly named reference.

    Only the numeric reference value enters the frozen EmergencyState geometry.
    Provenance is carried separately. An expert-ledger reference is never
    relabelled as a canonical forecast contract or as ``monthly_vw_forecast``.
    """

    monthly_reference.validate(require_persisted_ids=require_persisted_reference)
    level, alert = state.update(date, close, monthly_reference.value)
    return EmergencyBridgeResult(
        level_emergency=level,
        reversal_alert=alert,
        reference_model_id=monthly_reference.model_id,
        reference_target_month=monthly_reference.target_month,
        reference_evidence_class=monthly_reference.evidence_class,
        reference_identity_family=monthly_reference.persisted_identity_family(),
        input_snapshot_id=monthly_reference.input_snapshot_id,
        forecast_contract_id=monthly_reference.forecast_contract_id,
        input_set_id=monthly_reference.input_set_id,
        expert_forecast_id=monthly_reference.expert_forecast_id,
    )
