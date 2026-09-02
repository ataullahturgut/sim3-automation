from __future__ import annotations

from datetime import date, datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row


DISPLAY_EVIDENCE_ORDER = ("LIVE_PRODUCTION", "PROSPECTIVE_SHADOW")


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _normalize(row: dict[str, Any]) -> dict[str, Any]:
    provenance = row.get("provenance") or {}
    if not isinstance(provenance, dict):
        provenance = {}
    evidence_class = provenance.get("evidence_class")
    return {
        "id": row.get("id"),
        "target_month": _iso(row.get("target_month")),
        "forecast_origin": _iso(row.get("forecast_origin")),
        "model_name": row.get("model_name"),
        "model_version": row.get("model_version"),
        "forecast_value": row.get("forecast_value"),
        "unit": row.get("unit"),
        "model_role": row.get("model_role"),
        "frozen_at": _iso(row.get("frozen_at")),
        "git_commit": row.get("git_commit"),
        "evidence_class": evidence_class,
        "prospective_claim": provenance.get("prospective_claim"),
        "forecast_input_snapshot_ids": provenance.get("forecast_input_snapshot_ids") or [],
        "derived_feature_snapshot_id": provenance.get("derived_feature_snapshot_id"),
        "input_fingerprint": provenance.get("input_fingerprint"),
        "provenance": provenance,
    }


def fetch_current_forecast(database_url: str) -> dict[str, Any] | None:
    """Return the newest display-eligible issued H=1 forecast.

    File-backed research and HISTORICAL_REPLAY records are deliberately excluded.
    LIVE_PRODUCTION has display priority over PROSPECTIVE_SHADOW for the same
    newest target universe.
    """
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")

    query = """
        select id,target_month,forecast_origin,model_name,model_version,
               forecast_value,unit,model_role,frozen_at,git_commit,provenance
        from monthly_forecast_contracts
        where provenance->>'evidence_class'=%s
        order by target_month desc, frozen_at desc, id desc
        limit 1
    """
    candidates: list[dict[str, Any]] = []
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for evidence_class in DISPLAY_EVIDENCE_ORDER:
                cur.execute(query, (evidence_class,))
                row = cur.fetchone()
                if row is not None:
                    normalized = _normalize(dict(row))
                    if normalized.get("evidence_class") != evidence_class:
                        raise RuntimeError("FORECAST_EVIDENCE_CLASS_MISMATCH")
                    candidates.append(normalized)
        conn.rollback()

    if not candidates:
        return None
    newest_target = max(str(x.get("target_month") or "") for x in candidates)
    newest = [x for x in candidates if str(x.get("target_month") or "") == newest_target]
    for evidence_class in DISPLAY_EVIDENCE_ORDER:
        for item in newest:
            if item.get("evidence_class") == evidence_class:
                return item
    return newest[0]


def fetch_forecast_history(database_url: str, limit: int = 60) -> list[dict[str, Any]]:
    """Return only prospectively issued/live forecast contracts for UI history."""
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")
    safe_limit = max(1, min(int(limit), 240))
    query = """
        select id,target_month,forecast_origin,model_name,model_version,
               forecast_value,unit,model_role,frozen_at,git_commit,provenance
        from monthly_forecast_contracts
        where provenance->>'evidence_class' in ('PROSPECTIVE_SHADOW','LIVE_PRODUCTION')
        order by target_month desc, frozen_at desc, id desc
        limit %s
    """
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(query, (safe_limit,))
            rows = [_normalize(dict(row)) for row in cur.fetchall()]
        conn.rollback()
    return rows
