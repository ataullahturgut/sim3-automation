from __future__ import annotations

from typing import Any


ENGINE_OBSERVABILITY_CONTRACT = "ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V1"

ENGINE_DISPLAY_ORDER = (
    "CAUSAL_PATCH",
    "VW_MIDAS_MSVR",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "MACRO_EVENT",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "BOCPD",
    "GVZ_RISK",
)

ENGINE_REGISTRY: dict[str, dict[str, Any]] = {
    "CAUSAL_PATCH": {
        "label": "Causal Patch",
        "category": "MONTHLY_FORECAST",
        "role": "Forward issuer candidate / monthly expert",
        "version": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",
        "direction_vote": False,
        "expert_id": "CAUSAL_PATCH",
    },
    "VW_MIDAS_MSVR": {
        "label": "VW-MIDAS-MSVR",
        "category": "MONTHLY_FORECAST",
        "role": "Audited analytical shadow/reference",
        "version": "VW_AUDITED_SHADOW_V2",
        "default_status": "BLOCKED_NOT_PROVEN_EXECUTABLE",
        "direction_vote": False,
        "expert_id": "VW_MIDAS_MSVR",
    },
    "MOMENTUM_3M": {
        "label": "3M Momentum · H=1 Expert",
        "category": "MONTHLY_FORECAST",
        "role": "Monthly expert / direction challenger; H=1 price output is distinct from stored monthly direction context",
        "version": "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
        "default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",
        "direction_vote": False,
        "expert_id": "MOMENTUM_3M",
    },
    "RANDOM_WALK": {
        "label": "Random Walk",
        "category": "MONTHLY_FORECAST",
        "role": "Mandatory naive benchmark",
        "version": "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
        "default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",
        "direction_vote": False,
        "expert_id": "RANDOM_WALK",
    },
    "MONTHLY_DIRECTION_3M": {
        "label": "Monthly Direction · 3M",
        "category": "STRATEGIC_DIRECTION",
        "role": "Strategic monthly direction / prior / context",
        "version": "R4_1_3M_SIMPLE_RETURN_V1",
        "default_status": "NOT_ISSUED",
        "direction_vote": True,
        "decision_key": "monthly_direction_3m",
        "feature_name": "MONTHLY_DIRECTION_3M",
    },
    "FAST": {
        "label": "FAST",
        "category": "TACTICAL_DIRECTION",
        "role": "Short-horizon tactical confirmation/conflict state",
        "version": "R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1",
        "default_status": "NOT_ISSUED",
        "direction_vote": True,
        "decision_key": "fast_state",
        "feature_name": "FAST_STATE",
    },
    "SLOW": {
        "label": "SLOW",
        "category": "TACTICAL_DIRECTION",
        "role": "Medium-horizon tactical confirmation/conflict state",
        "version": "R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1",
        "default_status": "NOT_ISSUED",
        "direction_vote": True,
        "decision_key": "slow_state",
        "feature_name": "SLOW_STATE",
    },
    "MACRO_EVENT": {
        "label": "Macro Event",
        "category": "EVENT_RISK",
        "role": "Timestamp-safe event-risk state only",
        "version": "NOT_FULLY_RECOVERED",
        "default_status": "BLOCKED_NOT_FULLY_RECOVERED",
        "direction_vote": False,
        "decision_key": "macro_event_state",
    },
    "EMERGENCY_LEVEL": {
        "label": "Emergency · Level",
        "category": "EMERGENCY",
        "role": "Abnormal level-move alert/context",
        "version": "R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_PASS",
        "default_status": "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE",
        "direction_vote": False,
        "decision_key": "level_emergency",
    },
    "EMERGENCY_REVERSAL": {
        "label": "Emergency · Reversal",
        "category": "EMERGENCY",
        "role": "Reversal alert/context; alert-only under frozen geometry",
        "version": "R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_PASS",
        "default_status": "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE",
        "direction_vote": False,
        "decision_key": "reversal_emergency",
    },
    "BOCPD": {
        "label": "BOCPD",
        "category": "REGIME_BREAK",
        "role": "Regime/break context and alert only",
        "version": "NOT_RECOVERED_EXACT_FORWARD_RULE",
        "default_status": "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED",
        "direction_vote": False,
        "decision_key": "bocpd_context",
    },
    "GVZ_RISK": {
        "label": "GVZ Risk Cap",
        "category": "RISK",
        "role": "Volatility/risk-cap context; never a gold-direction vote",
        "version": "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
        "default_status": "NOT_ISSUED",
        "direction_vote": False,
        "feature_name": "GVZ_REGIME",
    },
}

_MISSING = {"", "NONE", "N/A", "NAN", "NOT_ISSUED", "YAYIMLANMADI", "KULLANILAMIYOR"}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _available(value: Any) -> bool:
    return _text(value).upper() not in _MISSING


def _latest_expert(rows: list[dict[str, Any]] | None, expert_id: str) -> dict[str, Any] | None:
    candidates = [dict(row) for row in (rows or []) if _text(row.get("expert_id")) == expert_id]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: (
            _text(row.get("as_of")),
            _text(row.get("created_at")),
            _text(row.get("target_month")),
        ),
    )


def _component_meta(decision: dict[str, Any] | None, feature_name: str | None, field: str) -> Any:
    if not decision or not feature_name:
        return None
    mapping = decision.get(field)
    if isinstance(mapping, dict):
        return mapping.get(feature_name)
    return None


def _component_row(engine_id: str, base: dict[str, Any], decision: dict[str, Any] | None) -> dict[str, Any]:
    key = base.get("decision_key")
    feature_name = base.get("feature_name")
    value = decision.get(key) if decision and key else None

    if engine_id == "GVZ_RISK":
        gvz_value = decision.get("gvz") if decision else None
        gvz_regime = decision.get("gvz_regime") if decision else None
        gvz_cap = decision.get("gvz_cap") if decision else None
        gvz_panic = decision.get("gvz_panic") if decision else None
        parts = []
        if gvz_value is not None:
            parts.append(f"GVZ={gvz_value}")
        if _available(gvz_regime):
            parts.append(f"REGIME={gvz_regime}")
        if gvz_cap is not None:
            parts.append(f"CAP={gvz_cap}")
        if gvz_panic is not None:
            parts.append(f"PANIC={str(bool(gvz_panic)).lower()}")
        value = " · ".join(parts) if parts else None

    status = base["default_status"]
    if _available(value):
        value_text = _text(value)
        status = value_text if value_text.startswith(("BLOCKED_", "NOT_PROVEN_", "WAITING_")) else "STORED_CONTEXT_AVAILABLE"

    version = _component_meta(decision, feature_name, "context_feature_versions") or base["version"]
    updated_at = _component_meta(decision, feature_name, "context_feature_updated_at")
    input_cutoff = _component_meta(decision, feature_name, "context_feature_input_cutoff")
    evidence = _component_meta(decision, feature_name, "context_feature_evidence")
    if evidence is None and decision:
        evidence = decision.get("evidence_class")

    return {
        "engine_id": engine_id,
        "label": base["label"],
        "category": base["category"],
        "role": base["role"],
        "version": version,
        "output": value,
        "status": status,
        "evidence_class": evidence,
        "target_month": None if not decision else decision.get("target_month"),
        "as_of": updated_at or input_cutoff or (None if not decision else decision.get("generated_at") or decision.get("decision_as_of")),
        "input_cutoff": input_cutoff,
        "direction_vote": bool(base["direction_vote"]),
        "canonical_authority": False,
        "forecast_track": None,
    }


def _expert_row(
    engine_id: str,
    base: dict[str, Any],
    month_end_rows: list[dict[str, Any]] | None,
    early_rows: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    expert_id = str(base["expert_id"])
    month = _latest_expert(month_end_rows, expert_id)
    early = _latest_expert(early_rows, expert_id)
    row = month or early
    if row:
        track = _text(row.get("forecast_track")) or ("MONTH_END_EXPERT" if month else "EARLY_INDICATIVE")
        status = "ISSUED_MONTH_END_EXPERT" if month else "ISSUED_EARLY_INDICATIVE_ONLY"
        output = row.get("forecast_value")
        evidence = row.get("evidence_class")
        version = row.get("model_version") or base["version"]
        target_month = row.get("target_month")
        as_of = row.get("as_of") or row.get("created_at")
    else:
        track = None
        status = base["default_status"]
        output = None
        evidence = None
        version = base["version"]
        target_month = None
        as_of = None

    return {
        "engine_id": engine_id,
        "label": base["label"],
        "category": base["category"],
        "role": base["role"],
        "version": version,
        "output": output,
        "status": status,
        "evidence_class": evidence,
        "target_month": target_month,
        "as_of": as_of,
        "input_cutoff": None,
        "direction_vote": bool(base["direction_vote"]),
        "canonical_authority": False,
        "forecast_track": track,
    }


def build_engine_inventory(
    decision: dict[str, Any] | None,
    month_end_experts: list[dict[str, Any]] | None,
    early_experts: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Return every governed motor even when it has no issued value.

    This is a presentation/read-model inventory. It must never create a selector,
    ensemble, final action, or substitute a missing forward output.
    """
    out: list[dict[str, Any]] = []
    for engine_id in ENGINE_DISPLAY_ORDER:
        base = ENGINE_REGISTRY[engine_id]
        if base.get("expert_id"):
            row = _expert_row(engine_id, base, month_end_experts, early_experts)
        else:
            row = _component_row(engine_id, base, decision)
        out.append(row)
    return out


def engine_inventory_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"total": len(rows), "active": 0, "issued": 0, "blocked": 0, "waiting": 0, "other": 0}
    for row in rows:
        status = _text(row.get("status")).upper()
        if status.startswith("ISSUED_"):
            counts["issued"] += 1
        elif status == "STORED_CONTEXT_AVAILABLE":
            counts["active"] += 1
        elif status.startswith(("BLOCKED_", "NOT_PROVEN_")):
            counts["blocked"] += 1
        elif status.startswith(("WAITING_", "NOT_ISSUED")):
            counts["waiting"] += 1
        else:
            counts["other"] += 1
    return counts
