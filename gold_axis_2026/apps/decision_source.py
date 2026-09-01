from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import psycopg


GOLD_ROOT = Path(__file__).resolve().parents[1]
DATA_PIPELINE_ROOT = GOLD_ROOT / "data_pipeline"
if str(DATA_PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(DATA_PIPELINE_ROOT))

from decision_store_reader import read_latest_decision  # noqa: E402


DISPLAY_EVIDENCE_ORDER = ("LIVE_PRODUCTION", "PROSPECTIVE_SHADOW")


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _to_transitional_app_shape(row: dict[str, Any]) -> dict[str, Any]:
    """Map stored state to the existing UI field names without recomputing signals."""
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
    }


def fetch_current_decision_state(database_url: str) -> dict[str, Any] | None:
    """Read the latest display-eligible stored decision state.

    Historical replay is deliberately excluded. LIVE_PRODUCTION has priority;
    PROSPECTIVE_SHADOW is returned only when no live-production row exists and
    remains explicitly labelled by evidence_class.
    """
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")

    with psycopg.connect(url, autocommit=True) as conn:
        for evidence_class in DISPLAY_EVIDENCE_ORDER:
            row = read_latest_decision(conn, evidence_class)
            if row is None:
                continue
            if row.get("action_state") is not None:
                raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")
            result = _to_transitional_app_shape(row)
            if result.get("evidence_class") != evidence_class:
                raise RuntimeError("DECISION_EVIDENCE_CLASS_MISMATCH")
            return result
    return None
