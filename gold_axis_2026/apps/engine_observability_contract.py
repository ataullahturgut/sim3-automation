from __future__ import annotations

from typing import Any


ENGINE_OBSERVABILITY_CONTRACT = "GOLD_CONTROL_CURRENT_ENGINE_OBSERVABILITY_V142"

ENGINE_DISPLAY_ORDER = (
    "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "CAUSAL_PATCH",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "MACRO_EVENT_SUCCESSOR_V2",
    "BOCPD_RETURN_SUCCESSOR_V1",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "GVZ_RISK",
)

ENGINE_REGISTRY: dict[str, dict[str, Any]] = {
    "VW_MIDAS_MSVR_SUCCESSOR_V1": {
        "label": "VW/MSVR Successor V1",
        "category": "MONTHLY_FORECAST",
        "role": "Monthly H=1 price expert",
        "direction_vote": False,
    },
    "CAUSAL_PATCH": {
        "label": "Causal Patch",
        "category": "MONTHLY_FORECAST",
        "role": "Monthly H=1 price expert",
        "direction_vote": False,
    },
    "MOMENTUM_3M": {
        "label": "3M Momentum · H=1 Expert",
        "category": "MONTHLY_FORECAST",
        "role": "Monthly H=1 price expert",
        "direction_vote": False,
    },
    "RANDOM_WALK": {
        "label": "Random Walk",
        "category": "MONTHLY_FORECAST",
        "role": "Mandatory same-origin benchmark",
        "direction_vote": False,
    },
    "MONTHLY_DIRECTION_3M": {
        "label": "Monthly Direction · 3M",
        "category": "STRATEGIC_DIRECTION",
        "role": "Strategic monthly direction / prior",
        "direction_vote": True,
    },
    "FAST": {
        "label": "FAST",
        "category": "TACTICAL_DIRECTION",
        "role": "Short-horizon tactical confirmation/conflict",
        "direction_vote": True,
    },
    "SLOW": {
        "label": "SLOW",
        "category": "TACTICAL_DIRECTION",
        "role": "Slower tactical confirmation/conflict",
        "direction_vote": True,
    },
    "MACRO_EVENT_SUCCESSOR_V2": {
        "label": "Macro Event · Successor V2",
        "category": "EVENT_RISK",
        "role": "Timestamp-safe labor-event risk/context",
        "direction_vote": False,
    },
    "BOCPD_RETURN_SUCCESSOR_V1": {
        "label": "BOCPD · Successor V1",
        "category": "REGIME_BREAK",
        "role": "Regime/break context only",
        "direction_vote": False,
    },
    "EMERGENCY_LEVEL": {
        "label": "Emergency · Level",
        "category": "EMERGENCY",
        "role": "Intramonth abnormal-level alert/context",
        "direction_vote": False,
    },
    "EMERGENCY_REVERSAL": {
        "label": "Emergency · Reversal",
        "category": "EMERGENCY",
        "role": "Intramonth peak/trough reversal alert/context",
        "direction_vote": False,
    },
    "GVZ_RISK": {
        "label": "GVZ Risk",
        "category": "RISK",
        "role": "Volatility/risk context only",
        "direction_vote": False,
    },
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _available(value: Any) -> bool:
    return value is not None and _text(value).upper() not in {"", "NONE", "N/A", "NAN"}


def _latest_expert(rows: list[dict[str, Any]] | None, expert_id: str) -> dict[str, Any] | None:
    candidates = [dict(row) for row in (rows or []) if _text(row.get("expert_id")) == expert_id]
    if not candidates:
        return None
    return max(candidates, key=lambda row: (_text(row.get("as_of")), _text(row.get("created_at"))))


def _decision_value(engine_id: str, decision: dict[str, Any] | None) -> Any:
    if not decision:
        return None
    key_map = {
        "MONTHLY_DIRECTION_3M": "monthly_direction_3m",
        "FAST": "fast_state",
        "SLOW": "slow_state",
        "MACRO_EVENT_SUCCESSOR_V2": "macro_event_successor_context",
        "BOCPD_RETURN_SUCCESSOR_V1": "bocpd_successor_context",
        "EMERGENCY_LEVEL": "level_emergency",
        "EMERGENCY_REVERSAL": "reversal_emergency",
    }
    if engine_id == "GVZ_RISK":
        parts: list[str] = []
        if decision.get("gvz") is not None:
            parts.append(f"GVZ={decision['gvz']}")
        if _available(decision.get("gvz_regime")):
            parts.append(f"REGIME={decision['gvz_regime']}")
        if decision.get("gvz_cap") is not None:
            parts.append(f"CAP={decision['gvz_cap']}")
        if decision.get("gvz_panic") is not None:
            parts.append(f"PANIC={str(bool(decision['gvz_panic'])).lower()}")
        return " · ".join(parts) if parts else None
    key = key_map.get(engine_id)
    return decision.get(key) if key else None


def _runtime_reference(runtime: dict[str, Any]) -> tuple[Any, str | None, Any, Any]:
    if _available(runtime.get("display_output")):
        return (
            runtime.get("display_output"),
            _text(runtime.get("display_evidence_class")) or None,
            runtime.get("display_as_of"),
            runtime.get("display_input_cutoff"),
        )

    metadata = runtime.get("metadata") if isinstance(runtime.get("metadata"), dict) else {}
    reference = metadata.get("current_month_reference") if isinstance(metadata.get("current_month_reference"), dict) else None
    if reference:
        value = reference.get("forecast_value") if reference.get("forecast_value") is not None else reference.get("state_value")
        if _available(value):
            return (
                value,
                _text(reference.get("evidence_class")) or None,
                reference.get("replay_executed_at") or reference.get("as_of") or runtime.get("as_of"),
                reference.get("information_cutoff") or reference.get("forecast_origin"),
            )

    state = metadata.get("current_state")
    if _available(state):
        return (
            state,
            _text(metadata.get("current_state_evidence_class")) or _text(runtime.get("evidence_class")) or None,
            metadata.get("current_state_as_of") or runtime.get("as_of"),
            metadata.get("information_cutoff"),
        )

    return None, None, runtime.get("as_of"), None


def build_engine_inventory(
    decision: dict[str, Any] | None,
    month_end_experts: list[dict[str, Any]] | None,
    early_experts: list[dict[str, Any]] | None,
    runtime_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build the current 12-motor display from current runtime authority.

    Runtime state is authoritative. Expert/decision rows may supply a display value
    when a runtime row has no embedded value, but they never change runtime status,
    selector/ensemble locks or direction-vote authority.
    """
    runtime_by_engine = {
        _text(row.get("engine_id")): dict(row)
        for row in (runtime_rows or [])
        if _text(row.get("engine_id")) in ENGINE_REGISTRY
    }
    monthly_expert_ids = {
        "VW_MIDAS_MSVR_SUCCESSOR_V1",
        "CAUSAL_PATCH",
        "MOMENTUM_3M",
        "RANDOM_WALK",
    }

    out: list[dict[str, Any]] = []
    for engine_id in ENGINE_DISPLAY_ORDER:
        base = ENGINE_REGISTRY[engine_id]
        runtime = runtime_by_engine.get(engine_id)

        output = None
        evidence = None
        as_of = None
        input_cutoff = None
        if runtime:
            output, evidence, as_of, input_cutoff = _runtime_reference(runtime)

        if not _available(output) and engine_id in monthly_expert_ids:
            candidate = _latest_expert(month_end_experts, engine_id) or _latest_expert(early_experts, engine_id)
            if candidate:
                output = candidate.get("forecast_value")
                evidence = _text(candidate.get("evidence_class")) or evidence
                as_of = candidate.get("as_of") or candidate.get("created_at") or as_of

        if not _available(output):
            decision_value = _decision_value(engine_id, decision)
            if _available(decision_value):
                output = decision_value
                if decision:
                    evidence = _text(decision.get("evidence_class")) or evidence
                    as_of = decision.get("generated_at") or decision.get("decision_as_of") or as_of

        if runtime:
            runtime_status = _text(runtime.get("runtime_status")).upper() or "MISSING_RUNTIME_STATUS"
            status_code = _text(runtime.get("status_code")) or "MISSING_RUNTIME_STATUS_CODE"
            direction_vote = bool(base["direction_vote"] and runtime.get("direction_vote_permitted") is True)
        else:
            runtime_status = "MISSING"
            status_code = "MISSING_CURRENT_RUNTIME_RECORD"
            direction_vote = False

        out.append(
            {
                "engine_id": engine_id,
                "label": base["label"],
                "category": base["category"],
                "role": base["role"],
                "output": output,
                "status": status_code,
                "runtime_status": runtime_status,
                "runtime_status_code": status_code,
                "evidence_class": evidence,
                "target_month": None if not runtime else runtime.get("target_context"),
                "as_of": as_of or (None if not runtime else runtime.get("as_of")),
                "input_cutoff": input_cutoff,
                "version": None if not runtime else runtime.get("engine_version"),
                "git_commit": None if not runtime else runtime.get("git_commit"),
                "direction_vote": direction_vote,
                "canonical_authority": False,
            }
        )
    return out


def engine_inventory_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"total": len(rows), "active": 0, "waiting": 0, "blocked": 0, "missing": 0, "other": 0}
    for row in rows:
        runtime_status = _text(row.get("runtime_status")).upper()
        if runtime_status == "ACTIVE":
            counts["active"] += 1
        elif runtime_status == "WAITING":
            counts["waiting"] += 1
        elif runtime_status in {"BLOCKED", "NOT_PROVEN"}:
            counts["blocked"] += 1
        elif runtime_status in {"", "MISSING"}:
            counts["missing"] += 1
        else:
            counts["other"] += 1
    return counts
