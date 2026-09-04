from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from gold_r4.contracts import Direction, FastState, GVZRisk, ReversalAlert, SlowState


ALLOWED_EVIDENCE_CLASSES = {"HISTORICAL_REPLAY", "PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}


@dataclass(frozen=True)
class MonthlyPriceReference:
    """Generic H=1 monthly price reference with explicit provenance.

    The historical R4.1 field name ``monthly_vw_forecast`` is intentionally not
    reused here. A forecast may become a MonthlyPriceReference only when its
    model identity and the persistence identity of the ledger that actually
    stores it are carried explicitly.

    Two persisted identity families are supported:

    1. legacy/canonical forecast contract:
       ``input_snapshot_id + forecast_contract_id``;
    2. v1.22+ multi-expert ledger:
       ``input_set_id + expert_forecast_id``.

    Supporting the second family does not create selector, ensemble, winner, or
    canonical authority. It only lets Emergency consume an explicitly named
    persisted expert forecast without falsifying it as a canonical contract.
    """

    value: float
    model_id: str
    target_month: str
    forecast_origin: str
    evidence_class: str
    input_snapshot_id: Optional[str] = None
    forecast_contract_id: Optional[str] = None
    input_set_id: Optional[str] = None
    expert_forecast_id: Optional[str] = None

    def persisted_identity_family(self) -> Optional[str]:
        canonical_complete = bool(self.input_snapshot_id and self.forecast_contract_id)
        expert_complete = bool(self.input_set_id and self.expert_forecast_id)
        canonical_partial = bool(self.input_snapshot_id) ^ bool(self.forecast_contract_id)
        expert_partial = bool(self.input_set_id) ^ bool(self.expert_forecast_id)
        if canonical_partial or expert_partial:
            return None
        if canonical_complete and expert_complete:
            return None
        if canonical_complete:
            return "FORECAST_CONTRACT"
        if expert_complete:
            return "MONTHLY_EXPERT_FORECAST"
        return None

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

        canonical_any = bool(self.input_snapshot_id or self.forecast_contract_id)
        expert_any = bool(self.input_set_id or self.expert_forecast_id)
        family = self.persisted_identity_family()
        if canonical_any or expert_any:
            if family is None:
                raise ValueError(
                    "persisted reference identity must be exactly one complete family: "
                    "input_snapshot_id+forecast_contract_id or input_set_id+expert_forecast_id"
                )
        if require_persisted_ids and family is None:
            raise ValueError(
                "persisted reference identity is required: "
                "input_snapshot_id+forecast_contract_id or input_set_id+expert_forecast_id"
            )


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
