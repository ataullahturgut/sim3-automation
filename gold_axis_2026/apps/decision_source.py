from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


GOLD_ROOT = Path(__file__).resolve().parents[1]
DATA_PIPELINE_ROOT = GOLD_ROOT / "data_pipeline"
if str(DATA_PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(DATA_PIPELINE_ROOT))

from decision_store_reader import read_latest_decision  # noqa: E402


DISPLAY_EVIDENCE_ORDER = ("LIVE_PRODUCTION", "PROSPECTIVE_SHADOW")
CONTEXT_EVIDENCE_CLASS = "LATE_BOOTSTRAP_SHADOW_CONTEXT"
CONTEXT_FEATURES = ("MONTHLY_DIRECTION_3M", "FAST_STATE", "SLOW_STATE")


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
        "macro_event_down": row.get("macro_event_down"),
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


def _read_shadow_direction_context(conn) -> dict[str, Any] | None:
    """Read immutable Stage-4A directional context without promoting it to a decision."""
    query = """
        SELECT id, feature_name, calculation_ts, input_cutoff, value_text,
               feature_version, quality_status, metadata
        FROM derived_feature_snapshots
        WHERE feature_name IN ('MONTHLY_DIRECTION_3M','FAST_STATE','SLOW_STATE')
          AND (
              quality_status = %s
              OR metadata->>'evidence_class' = %s
          )
        ORDER BY feature_name, calculation_ts DESC, id DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, (CONTEXT_EVIDENCE_CLASS, CONTEXT_EVIDENCE_CLASS))
        rows = [dict(r) for r in cur.fetchall()]

    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        feature_name = str(row.get("feature_name") or "")
        if feature_name in CONTEXT_FEATURES and feature_name not in latest:
            latest[feature_name] = row

    monthly_row = latest.get("MONTHLY_DIRECTION_3M")
    if not monthly_row:
        return None
    monthly_value = str(monthly_row.get("value_text") or "").strip()
    if not monthly_value:
        return None

    metadata = dict(monthly_row.get("metadata") or {})
    target_context = str(metadata.get("target_context") or "").strip()
    target_month = f"{target_context}-01" if len(target_context) == 7 else None
    generated_candidates = [r.get("calculation_ts") for r in latest.values() if r.get("calculation_ts")]
    generated_at = max(generated_candidates) if generated_candidates else monthly_row.get("calculation_ts")
    fast_value = str((latest.get("FAST_STATE") or {}).get("value_text") or "YAYIMLANMADI")
    slow_value = str((latest.get("SLOW_STATE") or {}).get("value_text") or "YAYIMLANMADI")

    return {
        "date": str(monthly_row.get("input_cutoff"))[:10] if monthly_row.get("input_cutoff") else "N/A",
        "decision_as_of": _iso(monthly_row.get("input_cutoff")),
        "generated_at": _iso(generated_at),
        "evidence_class": CONTEXT_EVIDENCE_CLASS,
        "context_only": True,
        "context_feature_ids": {name: row.get("id") for name, row in latest.items()},
        "target_month": target_month,
        "monthly_direction_3m": monthly_value,
        "fast_state": fast_value,
        "slow_state": slow_value,
        "level_emergency": "YAYIMLANMADI",
        "reversal_emergency": "YAYIMLANMADI",
        "macro_event_state": "BLOCKED_NOT_FULLY_RECOVERED",
        "bocpd_context": "YAYIMLANMADI",
        "classification": None,
        "action_state": None,
        "quality_status": CONTEXT_EVIDENCE_CLASS,
        "prospective_h1_claim": False,
    }


def fetch_current_decision_state(database_url: str) -> dict[str, Any] | None:
    """Read current display state without inventing a final decision.

    Priority is the governed Decision Store: LIVE_PRODUCTION, then
    PROSPECTIVE_SHADOW. When neither exists, the function may return the
    already-persisted Stage-4A directional context with ``context_only=True``.
    That fallback is not a final decision, does not close Stage 6, and contains
    no action mapping.
    """
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")

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
            conn.rollback()
            return result
        context = _read_shadow_direction_context(conn)
        conn.rollback()
        return context


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
