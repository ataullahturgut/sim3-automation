from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping


_REASON_BY_CLASSIFICATION = {
    "MACRO_DOWN_RISK": "MACRO_EVENT_DOWN_TRUE",
    "REVERSAL_RISK_DOWN": "REVERSAL_DOWN_ALERT_ACTIVE",
    "REVERSAL_RISK_UP": "REVERSAL_UP_ALERT_ACTIVE",
    "ALIGNED_UP": "LEVEL_FAST_SLOW_ALIGNED_UP",
    "ALIGNED_DOWN": "LEVEL_FAST_SLOW_ALIGNED_DOWN",
    "CONFLICT": "MONTHLY_VS_TACTICAL_CONFLICT",
    "UNRESOLVED_MIXED": "NO_DECISIVE_ALIGNMENT",
}


def reason_code_for_classification(classification: str) -> str:
    """Map the frozen R4.1 descriptive branch to its audit reason code.

    This is trace vocabulary only. It does not infer a position/action.
    """
    try:
        return _REASON_BY_CLASSIFICATION[str(classification)]
    except KeyError as exc:
        raise ValueError(f"Unsupported R4.1 classification: {classification!r}") from exc


def _required(row: Mapping[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required R4.1 emitted field: {key}")
    return value


def build_decision_payload(
    emitted_state: Mapping[str, Any],
    *,
    decision_as_of: datetime | str,
    generated_at: datetime | str,
    engine_version: str,
    config_version: str,
    config_hash: str | None,
    code_sha: str | None,
    trigger_type: str,
    evidence_class: str,
    input_snapshot_ref: str | None,
    forecast_contract_ref: str | None,
    close_source_ref: str,
    quality_status: str,
    run_status: str = "SUCCESS",
    run_notes: str | None = None,
    run_metadata: Mapping[str, Any] | None = None,
    snapshot_metadata: Mapping[str, Any] | None = None,
    event_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the Decision Store V1 payload from an already-emitted R4.1 state.

    The adapter is intentionally non-discretionary:
    - it does not recompute Fast/Slow/Emergency/GVZ/classification;
    - it does not create a BUY/SELL/HOLD/REDUCE action;
    - it preserves the engine-emitted descriptive state and binds provenance.
    """
    if run_status != "SUCCESS":
        return {
            "run": {
                "decision_as_of": decision_as_of,
                "generated_at": generated_at,
                "engine_version": engine_version,
                "config_version": config_version,
                "config_hash": config_hash,
                "code_sha": code_sha,
                "trigger_type": trigger_type,
                "evidence_class": evidence_class,
                "status": run_status,
                "input_snapshot_ref": input_snapshot_ref,
                "forecast_contract_ref": forecast_contract_ref,
                "notes": run_notes,
                "metadata": dict(run_metadata or {}),
            }
        }

    classification = str(_required(emitted_state, "classification"))
    reason_code = reason_code_for_classification(classification)

    target_month = str(_required(emitted_state, "target_month"))
    if len(target_month) == 7:
        target_month = f"{target_month}-01"

    return {
        "run": {
            "decision_as_of": decision_as_of,
            "generated_at": generated_at,
            "engine_version": engine_version,
            "config_version": config_version,
            "config_hash": config_hash,
            "code_sha": code_sha,
            "trigger_type": trigger_type,
            "evidence_class": evidence_class,
            "status": "SUCCESS",
            "input_snapshot_ref": input_snapshot_ref,
            "forecast_contract_ref": forecast_contract_ref,
            "notes": run_notes,
            "metadata": dict(run_metadata or {}),
        },
        "snapshot": {
            "decision_as_of": decision_as_of,
            "target_month": target_month,
            "close_value": float(_required(emitted_state, "close")),
            "close_source_ref": close_source_ref,
            "vw_forecast_frozen": float(_required(emitted_state, "vw_forecast_frozen")),
            "forecast_contract_ref": forecast_contract_ref,
            "monthly_direction_3m": str(_required(emitted_state, "monthly_direction_3m")),
            "level_emergency": str(_required(emitted_state, "level_emergency")),
            "reversal_emergency": str(_required(emitted_state, "reversal_emergency")),
            "fast_state": str(_required(emitted_state, "fast_state")),
            "slow_state": str(_required(emitted_state, "slow_state")),
            "gvz_value": emitted_state.get("gvz"),
            "gvz_cap": emitted_state.get("gvz_cap"),
            "gvz_panic": emitted_state.get("gvz_panic"),
            "macro_event_down": emitted_state.get("macro_event_down"),
            "bocpd_context": emitted_state.get("bocpd_context"),
            "classification": classification,
            "default_execution_session": emitted_state.get("default_execution_session"),
            "quality_status": quality_status,
            "metadata": dict(snapshot_metadata or {}),
        },
        "event": {
            "event_ts": decision_as_of,
            "classification": classification,
            "reason_code": reason_code,
            "action_state": None,
            "execution_session": emitted_state.get("default_execution_session"),
            "metadata": dict(event_metadata or {}),
        },
    }
