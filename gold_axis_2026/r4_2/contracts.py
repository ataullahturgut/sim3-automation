from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from gold_r4.contracts import Direction, FastState, GVZRisk, ReversalAlert, SlowState


ALLOWED_EVIDENCE_CLASSES = {"HISTORICAL_REPLAY", "PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}


@dataclass(frozen=True)
class MonthlyPriceReference:
    """Generic H=1 monthly price reference with explicit provenance.

    The historical R4.1 field name ``monthly_vw_forecast`` is intentionally not
    reused here. A Patch forecast may become a MonthlyPriceReference only when
    its own model identity and forecast/input contracts are carried explicitly.
    """

    value: float
    model_id: str
    target_month: str
    forecast_origin: str
    evidence_class: str
    input_snapshot_id: Optional[str] = None
    forecast_contract_id: Optional[str] = None

    def validate(self, *, require_persisted_ids: bool = False) -> None:
        if not (self.value > 0):
            raise ValueError("monthly reference value must be positive")
        if not self.model_id.strip():
            raise ValueError("model_id is required")
        if len(self.target_month) != 7 or self.target_month[4] != "-":
            raise ValueError("target_month must be YYYY-MM")
        if not self.forecast_origin.strip():
            raise ValueError("forecast_origin is required")
        if self.evidence_class not in ALLOWED_EVIDENCE_CLASSES:
            raise ValueError(f"unsupported evidence_class: {self.evidence_class}")
        if require_persisted_ids and (not self.input_snapshot_id or not self.forecast_contract_id):
            raise ValueError("persisted input_snapshot_id and forecast_contract_id are required")


@dataclass(frozen=True)
class EngineSnapshotV2:
    """Forward engine snapshot with generic monthly-reference provenance."""

    date: str
    close: float
    monthly_reference: MonthlyPriceReference
    monthly_direction: Direction
    level_emergency: Direction
    reversal_alert: ReversalAlert
    fast_state: FastState
    slow_state: SlowState
    gvz: Optional[GVZRisk]
    macro_event_down: Optional[bool]
    bocpd_context: Optional[str]
    classification: str

    def validate(self, *, require_persisted_reference: bool = False) -> None:
        if not (self.close > 0):
            raise ValueError("close must be positive")
        self.monthly_reference.validate(require_persisted_ids=require_persisted_reference)
