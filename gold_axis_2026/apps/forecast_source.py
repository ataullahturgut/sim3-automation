from __future__ import annotations

import json
from typing import Any

import psycopg
from psycopg.rows import dict_row

from production_display_snapshot import (
    load_production_display_snapshot,
    snapshot_historical_replay_rows,
)


DISPLAY_EVIDENCE = ("LIVE_PRODUCTION", "PROSPECTIVE_SHADOW")
REPLAY_EVIDENCE = ("HISTORICAL_REPLAY",)
CANONICAL_SELECTOR_BLOCK = "NOT_PROVEN_EXPERT_SELECTION_RULE"
TRACK_MONTH_END = "MONTH_END_EXPERT"
TRACK_EARLY_INDICATIVE = "EARLY_INDICATIVE"
TRACK_HISTORICAL_REPLAY = "HISTORICAL_REPLAY"
VALID_TRACKS = (TRACK_MONTH_END, TRACK_EARLY_INDICATIVE, TRACK_HISTORICAL_REPLAY)
EXPERT_ORDER = ("CAUSAL_PATCH", "VW_MIDAS_MSVR", "MOMENTUM_3M", "RANDOM_WALK")


def _json_obj(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _normalize_canonical(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    provenance = _json_obj(out.get("provenance"))
    out["provenance"] = provenance
    out["evidence_class"] = provenance.get("evidence_class")
    out["canonical_authority"] = provenance.get("canonical_authority") is True
    out["selector_status"] = provenance.get("selector_status")
    out["auto_selector"] = str(provenance.get("auto_selector", "OFF")).upper()
    out["auto_ensemble"] = str(provenance.get("auto_ensemble", "OFF")).upper()
    return out


def _canonical_row_is_governed(row: dict[str, Any]) -> bool:
    p = row.get("provenance") or {}
    if row.get("evidence_class") not in DISPLAY_EVIDENCE:
        return False
    if row.get("canonical_authority") is not True:
        return False
    if row.get("auto_selector") != "OFF" or row.get("auto_ensemble") != "OFF":
        return False
    selector = str(p.get("selector_status") or "")
    if not selector or selector == CANONICAL_SELECTOR_BLOCK:
        return False
    if not p.get("selector_rule_version"):
        return False
    return True


def fetch_current_forecast(database_url: str) -> dict[str, Any] | None:
    """Return only a governed canonical forecast, never an arbitrary expert/replay row."""
    if not database_url:
        return None
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id,target_month,forecast_origin,model_name,model_version,
                       forecast_value,unit,model_role,frozen_at,git_commit,provenance
                from monthly_forecast_contracts
                order by target_month desc, frozen_at desc, id desc
                limit 50
                """
            )
            rows = [_normalize_canonical(dict(r)) for r in cur.fetchall()]
    governed = [r for r in rows if _canonical_row_is_governed(r)]
    if not governed:
        return None
    newest_target = max(str(r.get("target_month") or "") for r in governed)
    candidates = [r for r in governed if str(r.get("target_month") or "") == newest_target]
    candidates.sort(key=lambda r: (0 if r.get("evidence_class") == "LIVE_PRODUCTION" else 1, str(r.get("frozen_at") or "")))
    return candidates[0] if candidates else None


def fetch_forecast_history(database_url: str, limit: int = 60) -> list[dict[str, Any]]:
    """Governed canonical forecast history only; replay never enters this scorecard."""
    if not database_url:
        return []
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id,target_month,forecast_origin,model_name,model_version,
                       forecast_value,unit,model_role,frozen_at,git_commit,provenance
                from monthly_forecast_contracts
                order by target_month desc, frozen_at desc, id desc
                limit %s
                """,
                (max(1, min(int(limit), 500)),),
            )
            rows = [_normalize_canonical(dict(r)) for r in cur.fetchall()]
    return [r for r in rows if _canonical_row_is_governed(r)]


def _expert_table_exists(cur) -> bool:
    cur.execute("select to_regclass('public.monthly_expert_forecasts') as reg")
    row = cur.fetchone()
    return bool(row and row["reg"] is not None)


def _normalize_expert(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["provenance"] = _json_obj(out.get("provenance"))
    out["input_snapshot_ids"] = list(out.get("input_snapshot_ids") or [])
    out["canonical_authority"] = False
    return out


def _evidence_for_track(forecast_track: str) -> tuple[str, ...]:
    if forecast_track == TRACK_HISTORICAL_REPLAY:
        return REPLAY_EVIDENCE
    return DISPLAY_EVIDENCE


def _snapshot_replay_rows() -> list[dict[str, Any]]:
    rows = snapshot_historical_replay_rows(load_production_display_snapshot())
    normalized = [_normalize_expert(row) for row in rows]
    order = {x: i for i, x in enumerate(EXPERT_ORDER)}
    normalized.sort(key=lambda r: order.get(str(r.get("expert_id")), 99))
    return normalized


def fetch_latest_expert_forecasts(
    database_url: str,
    forecast_track: str = TRACK_MONTH_END,
) -> list[dict[str, Any]]:
    """Latest separately-issued rows for one explicit track; tracks never merge."""
    if forecast_track not in VALID_TRACKS:
        raise ValueError(f"INVALID_FORECAST_TRACK:{forecast_track}")
    if not database_url:
        return _snapshot_replay_rows() if forecast_track == TRACK_HISTORICAL_REPLAY else []
    evidence = _evidence_for_track(forecast_track)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            if not _expert_table_exists(cur):
                return []
            cur.execute(
                """
                with newest as (
                    select max(target_month) as target_month
                    from monthly_expert_forecasts
                    where forecast_track=%s and evidence_class=any(%s)
                ), ranked as (
                    select e.*,
                           row_number() over (partition by e.expert_id order by e.as_of desc, e.id desc) as rn
                    from monthly_expert_forecasts e, newest n
                    where e.forecast_track=%s
                      and e.evidence_class=any(%s)
                      and e.target_month=n.target_month
                      and e.canonical_authority=false
                      and e.selector_status=%s
                      and e.auto_selector='OFF'
                      and e.auto_ensemble='OFF'
                )
                select id,target_month,forecast_origin,as_of,forecast_track,
                       expert_id,model_name,model_version,expert_role,forecast_value,
                       unit,evidence_class,git_commit,input_snapshot_ids,input_fingerprint,
                       selector_status,auto_selector,auto_ensemble,canonical_authority,
                       provenance,created_at
                from ranked where rn=1
                """,
                (forecast_track, list(evidence), forecast_track, list(evidence), CANONICAL_SELECTOR_BLOCK),
            )
            rows = [_normalize_expert(dict(r)) for r in cur.fetchall()]
    order = {x: i for i, x in enumerate(EXPERT_ORDER)}
    rows.sort(key=lambda r: order.get(str(r.get("expert_id")), 99))
    return rows


def fetch_expert_forecast_history(
    database_url: str,
    forecast_track: str | None = None,
    limit: int = 240,
) -> list[dict[str, Any]]:
    """Read append-only expert history without merging forecast tracks/evidence classes."""
    if forecast_track is not None and forecast_track not in VALID_TRACKS:
        raise ValueError(f"INVALID_FORECAST_TRACK:{forecast_track}")
    if not database_url:
        return _snapshot_replay_rows()[: max(1, min(int(limit), 2000))] if forecast_track == TRACK_HISTORICAL_REPLAY else []
    evidence = _evidence_for_track(forecast_track) if forecast_track is not None else DISPLAY_EVIDENCE
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            if not _expert_table_exists(cur):
                return []
            params: list[Any] = [list(evidence), CANONICAL_SELECTOR_BLOCK]
            where_track = ""
            if forecast_track is not None:
                where_track = " and forecast_track=%s"
                params.append(forecast_track)
            params.append(max(1, min(int(limit), 2000)))
            cur.execute(
                f"""
                select id,target_month,forecast_origin,as_of,forecast_track,
                       expert_id,model_name,model_version,expert_role,forecast_value,
                       unit,evidence_class,git_commit,input_snapshot_ids,input_fingerprint,
                       selector_status,auto_selector,auto_ensemble,canonical_authority,
                       provenance,created_at
                from monthly_expert_forecasts
                where evidence_class=any(%s)
                  and selector_status=%s
                  and auto_selector='OFF'
                  and auto_ensemble='OFF'
                  and canonical_authority=false
                  {where_track}
                order by target_month desc, as_of desc, expert_id, id desc
                limit %s
                """,
                tuple(params),
            )
            rows = [_normalize_expert(dict(r)) for r in cur.fetchall()]
    order = {x: i for i, x in enumerate(EXPERT_ORDER)}
    rows.sort(key=lambda r: (str(r.get("target_month") or ""), order.get(str(r.get("expert_id")), 99), str(r.get("as_of") or "")), reverse=True)
    return rows
