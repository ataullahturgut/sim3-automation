from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

from production_display_snapshot import (
    SNAPSHOT_CONTRACT,
    SNAPSHOT_SOURCE_MODE,
    load_production_display_snapshot,
    snapshot_feature_rows,
)


GOLD_ROOT = Path(__file__).resolve().parents[1]
DATA_PIPELINE_ROOT = GOLD_ROOT / "data_pipeline"
if str(DATA_PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(DATA_PIPELINE_ROOT))

from decision_store_reader import read_latest_decision  # noqa: E402


DISPLAY_EVIDENCE_ORDER = ("LIVE_PRODUCTION", "PROSPECTIVE_SHADOW")
CONTEXT_EVIDENCE_CLASS = "LATE_BOOTSTRAP_SHADOW_CONTEXT"
CONTEXT_FEATURES = (
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
)
EMERGENCY_CONTEXT_STATUS = "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE"
BOCPD_CONTEXT_STATUS = "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED"
MACRO_EVENT_CONTEXT_STATUS = "BLOCKED_NOT_FULLY_RECOVERED"


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _to_transitional_app_shape(row: dict[str, Any]) -> dict[str, Any]:
    """Map stored Decision Store state to UI field names without recomputing signals."""
    decision_as_of = row.get("decision_as_of")
    if isinstance(decision_as_of, datetime):
        display_date = decision_as_of.date().isoformat()
    else:
        display_date = str(decision_as_of)[:10] if decision_as_of is not None else "N/A"

    return {
        "date": display_date,
        "decision_as_of": _iso(decision_as_of),
        "generated_at": _iso(row.get("generated_at")),
        "evidence_class": row.get("evidence_class"),
        "run_id": _iso(row.get("run_id")),
        "snapshot_id": _iso(row.get("snapshot_id")),
        "target_month": _iso(row.get("target_month")),
        "close": row.get("close_value"),
        "close_source_ref": row.get("close_source_ref"),
        "vw_forecast_frozen": row.get("vw_forecast_frozen"),
        "monthly_direction_3m": row.get("monthly_direction_3m"),
        "level_emergency": row.get("level_emergency"),
        "reversal_emergency": row.get("reversal_emergency"),
        "fast_state": row.get("fast_state"),
        "slow_state": row.get("slow_state"),
        "gvz": row.get("gvz_value"),
        "gvz_cap": row.get("gvz_cap"),
        "gvz_panic": row.get("gvz_panic"),
        "gvz_regime": None,
        "macro_event_down": row.get("macro_event_down"),
        "macro_event_state": row.get("macro_event_down"),
        "bocpd_context": row.get("bocpd_context"),
        "classification": row.get("classification"),
        "reason_code": row.get("reason_code"),
        "quality_status": row.get("quality_status"),
        "default_execution_session": _iso(row.get("default_execution_session")),
        "action_state": row.get("action_state"),
        "engine_version": row.get("engine_version"),
        "config_version": row.get("config_version"),
        "code_sha": row.get("code_sha"),
        "context_only": False,
    }


def _row_recency_key(row: dict[str, Any]) -> tuple[str, int]:
    return (_iso(row.get("calculation_ts")) or "", int(row.get("id") or 0))


def _row_target_context(row: dict[str, Any]) -> str:
    metadata = dict(row.get("metadata") or {})
    return str(metadata.get("target_context") or "").strip()


def _latest_value(latest: dict[str, dict[str, Any]], feature_name: str, fallback: str) -> str:
    return str((latest.get(feature_name) or {}).get("value_text") or fallback).strip() or fallback


def _parse_float_text(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_bool_text(value: str) -> bool | None:
    text = str(value or "").strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def _shape_shadow_direction_context(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Shape governed component shadow context without promoting it to a decision.

    The newest target_context is selected first so monthly, tactical, and risk
    components are never silently mixed across different periods. Any available
    component may be displayed as context; this object can never become a final
    Decision Store classification or action.
    """
    eligible = [
        dict(row)
        for row in rows
        if str(row.get("feature_name") or "") in CONTEXT_FEATURES
    ]
    if not eligible:
        return None

    newest_row = max(eligible, key=_row_recency_key)
    target_context = _row_target_context(newest_row)
    if target_context:
        same_target = [row for row in eligible if _row_target_context(row) == target_context]
        if same_target:
            eligible = same_target

    latest: dict[str, dict[str, Any]] = {}
    for row in sorted(eligible, key=_row_recency_key, reverse=True):
        feature_name = str(row.get("feature_name") or "")
        if feature_name not in latest:
            latest[feature_name] = row

    if not latest:
        return None

    anchor_row = max(latest.values(), key=_row_recency_key)
    if not target_context:
        target_context = _row_target_context(anchor_row)
    target_month = f"{target_context}-01" if len(target_context) == 7 else None
    generated_candidates = [r.get("calculation_ts") for r in latest.values() if r.get("calculation_ts")]
    generated_at = max(generated_candidates) if generated_candidates else anchor_row.get("calculation_ts")

    monthly_value = _latest_value(latest, "MONTHLY_DIRECTION_3M", "YAYIMLANMADI")
    fast_value = _latest_value(latest, "FAST_STATE", "YAYIMLANMADI")
    slow_value = _latest_value(latest, "SLOW_STATE", "YAYIMLANMADI")
    gvz_value_text = _latest_value(latest, "GVZ_VALUE", "YAYIMLANMADI")
    gvz_cap_text = _latest_value(latest, "GVZ_CAP", "YAYIMLANMADI")
    gvz_panic_text = _latest_value(latest, "GVZ_PANIC", "YAYIMLANMADI")
    gvz_regime = _latest_value(latest, "GVZ_REGIME", "YAYIMLANMADI")

    return {
        "date": str(anchor_row.get("input_cutoff"))[:10] if anchor_row.get("input_cutoff") else "N/A",
        "decision_as_of": _iso(anchor_row.get("input_cutoff")),
        "generated_at": _iso(generated_at),
        "evidence_class": CONTEXT_EVIDENCE_CLASS,
        "context_only": True,
        "context_components": tuple(sorted(latest)),
        "context_feature_ids": {name: row.get("id") for name, row in latest.items()},
        "context_feature_versions": {name: row.get("feature_version") for name, row in latest.items()},
        "context_feature_updated_at": {name: _iso(row.get("calculation_ts")) for name, row in latest.items()},
        "context_feature_input_cutoff": {name: _iso(row.get("input_cutoff")) for name, row in latest.items()},
        "context_feature_evidence": {
            name: (dict(row.get("metadata") or {}).get("evidence_class") or row.get("quality_status"))
            for name, row in latest.items()
        },
        "target_month": target_month,
        "monthly_direction_3m": monthly_value,
        "fast_state": fast_value,
        "slow_state": slow_value,
        "level_emergency": EMERGENCY_CONTEXT_STATUS,
        "reversal_emergency": EMERGENCY_CONTEXT_STATUS,
        "macro_event_state": MACRO_EVENT_CONTEXT_STATUS,
        "bocpd_context": BOCPD_CONTEXT_STATUS,
        "gvz": _parse_float_text(gvz_value_text),
        "gvz_cap": _parse_float_text(gvz_cap_text),
        "gvz_panic": _parse_bool_text(gvz_panic_text),
        "gvz_regime": gvz_regime,
        "classification": None,
        "action_state": None,
        "quality_status": CONTEXT_EVIDENCE_CLASS,
        "prospective_h1_claim": False,
    }


def _read_shadow_direction_context(conn) -> dict[str, Any] | None:
    """Read immutable Stage-4A component context without promoting it to a decision."""
    query = """
        SELECT id, feature_name, calculation_ts, input_cutoff, value_text,
               feature_version, quality_status, metadata
        FROM derived_feature_snapshots
        WHERE feature_name IN (
            'MONTHLY_DIRECTION_3M','FAST_STATE','SLOW_STATE',
            'GVZ_VALUE','GVZ_CAP','GVZ_PANIC','GVZ_REGIME'
        )
          AND (
              quality_status = %s
              OR metadata->>'evidence_class' = %s
          )
        ORDER BY calculation_ts DESC, id DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, (CONTEXT_EVIDENCE_CLASS, CONTEXT_EVIDENCE_CLASS))
        rows = [dict(r) for r in cur.fetchall()]
    return _shape_shadow_direction_context(rows)


def _read_snapshot_shadow_direction_context() -> dict[str, Any] | None:
    snapshot = load_production_display_snapshot()
    context = _shape_shadow_direction_context(snapshot_feature_rows(snapshot))
    if context is None:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_CONTEXT_EMPTY")
    context["source_mode"] = SNAPSHOT_SOURCE_MODE
    context["snapshot_contract"] = SNAPSHOT_CONTRACT
    context["snapshot_source_state_at"] = snapshot.get("source_state_at")
    context["snapshot_payload_sha256"] = snapshot.get("payload_sha256")
    return context


def _read_db_current_decision_state(url: str) -> dict[str, Any] | None:
    with psycopg.connect(url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
        for evidence_class in DISPLAY_EVIDENCE_ORDER:
            row = read_latest_decision(conn, evidence_class)
            if row is None:
                continue
            if row.get("action_state") is not None:
                raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")
            result = _to_transitional_app_shape(row)
            if result.get("evidence_class") != evidence_class:
                raise RuntimeError("DECISION_EVIDENCE_CLASS_MISMATCH")
            result["source_mode"] = "NEON_DB_READ_ONLY"
            conn.rollback()
            return result
        context = _read_shadow_direction_context(conn)
        if context is not None:
            context["source_mode"] = "NEON_DB_READ_ONLY"
        conn.rollback()
        return context


def fetch_current_decision_state(database_url: str) -> dict[str, Any] | None:
    """Read current governed display state with a validated deployment fallback.

    Neon remains primary. A missing URL or operational connectivity failure may
    use the frozen production display snapshot. Governance/schema violations are
    never converted into fallback data.
    """
    url = str(database_url or "").strip()
    if not url:
        return _read_snapshot_shadow_direction_context()
    try:
        return _read_db_current_decision_state(url)
    except psycopg.OperationalError:
        return _read_snapshot_shadow_direction_context()


def fetch_decision_history(database_url: str, limit: int = 80) -> list[dict[str, Any]]:
    """Return only prospectively stored/live decision events for UI history.

    HISTORICAL_REPLAY and LATE_BOOTSTRAP_SHADOW_CONTEXT are intentionally
    excluded from this production-facing history. action_state remains
    forbidden by the Decision Store V1 contract.
    """
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")
    safe_limit = max(1, min(int(limit), 240))
    query = """
        SELECT
            e.event_id,
            e.event_ts,
            e.previous_classification,
            e.classification,
            e.classification_changed,
            e.reason_code,
            e.action_state,
            s.snapshot_id,
            s.decision_as_of,
            s.target_month,
            s.close_value,
            s.monthly_direction_3m,
            s.level_emergency,
            s.reversal_emergency,
            s.fast_state,
            s.slow_state,
            s.gvz_value,
            s.gvz_cap,
            s.gvz_panic,
            s.macro_event_down,
            s.bocpd_context,
            s.quality_status,
            r.run_id,
            r.generated_at,
            r.engine_version,
            r.config_version,
            r.code_sha,
            r.evidence_class
        FROM decision_events e
        JOIN decision_signal_snapshots s ON s.snapshot_id = e.snapshot_id
        JOIN decision_runs r ON r.run_id = e.run_id
        WHERE r.status = 'SUCCESS'
          AND r.evidence_class IN ('PROSPECTIVE_SHADOW','LIVE_PRODUCTION')
        ORDER BY e.event_ts DESC, e.created_at DESC
        LIMIT %s
    """
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(query, (safe_limit,))
            rows = [dict(x) for x in cur.fetchall()]
        conn.rollback()

    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("action_state") is not None:
            raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")
        evidence = row.get("evidence_class")
        if evidence not in DISPLAY_EVIDENCE_ORDER:
            raise RuntimeError(f"DECISION_HISTORY_EVIDENCE_NOT_DISPLAY_ELIGIBLE:{evidence}")
        out.append({
            "event_id": _iso(row.get("event_id")),
            "event_ts": _iso(row.get("event_ts")),
            "previous_classification": row.get("previous_classification"),
            "classification": row.get("classification"),
            "classification_changed": row.get("classification_changed"),
            "reason_code": row.get("reason_code"),
            "snapshot_id": _iso(row.get("snapshot_id")),
            "decision_as_of": _iso(row.get("decision_as_of")),
            "target_month": _iso(row.get("target_month")),
            "close": row.get("close_value"),
            "monthly_direction_3m": row.get("monthly_direction_3m"),
            "level_emergency": row.get("level_emergency"),
            "reversal_emergency": row.get("reversal_emergency"),
            "fast_state": row.get("fast_state"),
            "slow_state": row.get("slow_state"),
            "gvz": row.get("gvz_value"),
            "gvz_cap": row.get("gvz_cap"),
            "gvz_panic": row.get("gvz_panic"),
            "macro_event_down": row.get("macro_event_down"),
            "bocpd_context": row.get("bocpd_context"),
            "quality_status": row.get("quality_status"),
            "run_id": _iso(row.get("run_id")),
            "generated_at": _iso(row.get("generated_at")),
            "engine_version": row.get("engine_version"),
            "config_version": row.get("config_version"),
            "code_sha": row.get("code_sha"),
            "evidence_class": evidence,
            "action_state": None,
        })
    return out
