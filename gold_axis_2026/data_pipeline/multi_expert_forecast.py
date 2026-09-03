from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


MANIFEST_VERSION = "1.28"
SELECTOR_STATUS = "NOT_PROVEN_EXPERT_SELECTION_RULE"
AUTO_SELECTOR = "OFF"
AUTO_ENSEMBLE = "OFF"

TRACK_MONTH_END = "MONTH_END_EXPERT"
TRACK_EARLY_INDICATIVE = "EARLY_INDICATIVE"
TRACK_HISTORICAL_REPLAY = "HISTORICAL_REPLAY"
FORECAST_TRACKS = frozenset({TRACK_MONTH_END, TRACK_EARLY_INDICATIVE, TRACK_HISTORICAL_REPLAY})
DISPLAY_EVIDENCE_CLASSES = frozenset({"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION", "HISTORICAL_REPLAY"})

PATCH_EXPERT = "CAUSAL_PATCH"
VW_EXPERT = "VW_MIDAS_MSVR"
MOMENTUM_EXPERT = "MOMENTUM_3M"
RW_EXPERT = "RANDOM_WALK"
EXPERT_ORDER = (PATCH_EXPERT, VW_EXPERT, MOMENTUM_EXPERT, RW_EXPERT)

SIMPLE_EXPERT_SOURCE_ID = "SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"
RW_V2_VERSION = "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
MOMENTUM_V2_VERSION = "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
SIMPLE_EXPERT_SOURCE_EVIDENCE = "SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS"


@dataclass(frozen=True)
class ExpertDefinition:
    expert_id: str
    label: str
    model_name: str
    model_version: str
    expert_role: str
    execution_status: str
    status_reason: str


EXPERT_REGISTRY: dict[str, ExpertDefinition] = {
    PATCH_EXPERT: ExpertDefinition(
        expert_id=PATCH_EXPERT,
        label="Causal Patch",
        model_name="CAUSAL_PATCH_R1",
        model_version="CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        expert_role="EXPERT",
        execution_status="EXECUTABLE_FORWARD_ISSUER_CANDIDATE",
        status_reason="Patch V7 completed-session PIT contract is the current executable forward issuer candidate.",
    ),
    VW_EXPERT: ExpertDefinition(
        expert_id=VW_EXPERT,
        label="VW-MIDAS-MSVR",
        model_name="VW_MIDAS_MSVR",
        model_version="VW_AUDITED_SHADOW_V2",
        expert_role="EXPERT",
        execution_status="BLOCKED_NOT_PROVEN_EXECUTABLE",
        status_reason="Exact archived executable runner is not proven; historical analytical evidence is not a forward issuer.",
    ),
    MOMENTUM_EXPERT: ExpertDefinition(
        expert_id=MOMENTUM_EXPERT,
        label="3M Momentum",
        model_name="MOMENTUM_3M",
        model_version=MOMENTUM_V2_VERSION,
        expert_role="EXPERT",
        execution_status="EXECUTABLE_FORWARD_EXPERT",
        status_reason="Source-bound V2 passed the frozen 43-origin source/materiality/non-inferiority audit; issuance waits for an eligible prospective month-end origin.",
    ),
    RW_EXPERT: ExpertDefinition(
        expert_id=RW_EXPERT,
        label="Random Walk",
        model_name="RANDOM_WALK",
        model_version=RW_V2_VERSION,
        expert_role="BENCHMARK",
        execution_status="EXECUTABLE_FORWARD_EXPERT",
        status_reason="Source-bound V2 passed the frozen 43-origin source/materiality/non-inferiority audit; issuance waits for an eligible prospective month-end origin.",
    ),
}


@dataclass(frozen=True)
class ExpertForecastRecord:
    target_month: str
    forecast_origin: datetime
    as_of: datetime
    forecast_track: str
    expert_id: str
    model_name: str
    model_version: str
    expert_role: str
    forecast_value: float
    unit: str
    evidence_class: str
    git_commit: str | None
    input_snapshot_ids: tuple[int, ...]
    input_fingerprint: str
    provenance: dict[str, Any]

    def validate(self) -> None:
        if self.forecast_track not in FORECAST_TRACKS:
            raise ValueError(f"INVALID_FORECAST_TRACK:{self.forecast_track}")
        if self.expert_id not in EXPERT_REGISTRY:
            raise ValueError(f"UNKNOWN_EXPERT:{self.expert_id}")
        definition = EXPERT_REGISTRY[self.expert_id]
        if self.model_name != definition.model_name or self.model_version != definition.model_version:
            raise ValueError(f"EXPERT_IDENTITY_MISMATCH:{self.expert_id}")
        if self.expert_role != definition.expert_role:
            raise ValueError(f"EXPERT_ROLE_MISMATCH:{self.expert_id}")
        if self.evidence_class not in DISPLAY_EVIDENCE_CLASSES:
            raise ValueError(f"INVALID_EVIDENCE_CLASS:{self.evidence_class}")
        if self.forecast_track == TRACK_HISTORICAL_REPLAY:
            if self.evidence_class != "HISTORICAL_REPLAY":
                raise ValueError("HISTORICAL_REPLAY_TRACK_REQUIRES_REPLAY_EVIDENCE")
        elif self.evidence_class == "HISTORICAL_REPLAY":
            raise ValueError("HISTORICAL_REPLAY_EVIDENCE_REQUIRES_REPLAY_TRACK")
        if not self.target_month or len(self.target_month) < 7:
            raise ValueError("TARGET_MONTH_REQUIRED")
        if self.forecast_origin.tzinfo is None or self.as_of.tzinfo is None:
            raise ValueError("TIMEZONE_AWARE_TIMESTAMPS_REQUIRED")
        if self.as_of < self.forecast_origin:
            raise ValueError("AS_OF_BEFORE_FORECAST_ORIGIN")
        if self.forecast_track == TRACK_HISTORICAL_REPLAY:
            if self.as_of <= self.forecast_origin:
                raise ValueError("HISTORICAL_REPLAY_AS_OF_MUST_BE_AFTER_ORIGIN")
            if self.provenance.get("historical_replay") is not True:
                raise ValueError("HISTORICAL_REPLAY_PROVENANCE_REQUIRED")
            if self.provenance.get("prospective_claim") is not False:
                raise ValueError("HISTORICAL_REPLAY_PROSPECTIVE_CLAIM_MUST_BE_FALSE")
            if str(self.provenance.get("information_cutoff")) != self.forecast_origin.isoformat():
                raise ValueError("HISTORICAL_REPLAY_INFORMATION_CUTOFF_MISMATCH")
            if str(self.provenance.get("replay_executed_at")) != self.as_of.isoformat():
                raise ValueError("HISTORICAL_REPLAY_EXECUTION_TIME_MISMATCH")
        if not isinstance(self.forecast_value, (int, float)) or not (self.forecast_value > 0):
            raise ValueError("POSITIVE_FORECAST_VALUE_REQUIRED")
        if not self.input_snapshot_ids:
            raise ValueError("IMMUTABLE_INPUT_SNAPSHOT_IDS_REQUIRED")
        if not self.input_fingerprint:
            raise ValueError("INPUT_FINGERPRINT_REQUIRED")
        if self.provenance.get("canonical_authority") is True:
            raise ValueError("INDIVIDUAL_EXPERT_CANNOT_SELF_PROMOTE_TO_CANONICAL_AUTHORITY")
        if str(self.provenance.get("selector_status", SELECTOR_STATUS)) != SELECTOR_STATUS:
            raise ValueError("SELECTOR_STATUS_MUST_REMAIN_NOT_PROVEN")
        if str(self.provenance.get("auto_selector", AUTO_SELECTOR)).upper() != AUTO_SELECTOR:
            raise ValueError("AUTO_SELECTOR_MUST_REMAIN_OFF")
        if str(self.provenance.get("auto_ensemble", AUTO_ENSEMBLE)).upper() != AUTO_ENSEMBLE:
            raise ValueError("AUTO_ENSEMBLE_MUST_REMAIN_OFF")


def selector_contract() -> dict[str, str]:
    return {
        "selector_status": SELECTOR_STATUS,
        "auto_selector": AUTO_SELECTOR,
        "auto_ensemble": AUTO_ENSEMBLE,
    }


def registry_rows() -> list[dict[str, str]]:
    return [vars(EXPERT_REGISTRY[x]).copy() for x in EXPERT_ORDER]


def executable_experts() -> tuple[str, ...]:
    return tuple(
        x for x in EXPERT_ORDER
        if EXPERT_REGISTRY[x].execution_status.startswith("EXECUTABLE_FORWARD_")
    )


def rw_r1(monthly_levels: Iterable[float]) -> float:
    values = [float(x) for x in monthly_levels]
    if len(values) < 1 or values[-1] <= 0:
        raise ValueError("RW_R1_REQUIRES_POSITIVE_COMPLETED_MONTH_LEVEL")
    return values[-1]


def momentum_3m_r1(monthly_levels: Iterable[float]) -> float:
    values = [float(x) for x in monthly_levels]
    if len(values) < 4 or any(x <= 0 for x in values[-4:]):
        raise ValueError("MOMENTUM_3M_R1_REQUIRES_FOUR_POSITIVE_COMPLETED_MONTH_LEVELS")
    recent = values[-4:]
    returns = [recent[i] / recent[i - 1] - 1.0 for i in range(1, 4)]
    return recent[-1] * (1.0 + sum(returns) / 3.0)


def rw_r2_source_bound(monthly_levels: Iterable[float]) -> float:
    """Forward V2 RW formula; source semantics are enforced by the issuer contract."""
    return rw_r1(monthly_levels)


def momentum_3m_r2_source_bound(monthly_levels: Iterable[float]) -> float:
    """Forward V2 3M Momentum formula; source semantics are enforced by the issuer contract."""
    return momentum_3m_r1(monthly_levels)


def expert_status(expert_id: str) -> dict[str, str]:
    if expert_id not in EXPERT_REGISTRY:
        raise KeyError(expert_id)
    row = vars(EXPERT_REGISTRY[expert_id]).copy()
    row.update(selector_contract())
    return row
