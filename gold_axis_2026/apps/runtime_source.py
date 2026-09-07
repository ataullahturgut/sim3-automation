from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from engine_observability_contract import ENGINE_DISPLAY_ORDER
from production_display_snapshot import load_production_display_snapshot, snapshot_runtime_observability


RUNTIME_SOURCE_CONTRACT = "GOLD_CONTROL_CURRENT_RUNTIME_SOURCE_V141"
CURRENT_RUNTIME_VIEW = "current_engine_runtime_state_v1"
CURRENT_CONTEXT_VIEW = "current_context_feature_state_v1"
EXPECTED_ENGINE_COUNT = len(ENGINE_DISPLAY_ORDER)
CURRENT_CONTEXT_FEATURES = (
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
)


def _to_dict(row: Any) -> dict[str, Any]:
    return dict(row) if row is not None else {}


def _latest_target_context(runtime: list[dict[str, Any]]) -> str | None:
    values = [str(row.get("target_context") or "").strip() for row in runtime]
    values = [value for value in values if value]
    if not values:
        return None
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return max(sorted(counts), key=lambda value: counts[value])


def _latest_features(cur: psycopg.Cursor[Any], target_context: str) -> dict[str, dict[str, Any]]:
    cur.execute(
        """
        select id,feature_name,feature_version,calculation_ts,input_cutoff,
               value_num,value_text,quality_status,git_commit,metadata
        from current_context_feature_state_v1
        where feature_name=any(%s)
          and metadata->>'target_context'=%s
        order by feature_name
        """,
        (list(CURRENT_CONTEXT_FEATURES), target_context),
    )
    return {str(row["feature_name"]): dict(row) for row in cur.fetchall()}


def _feature_value(row: dict[str, Any] | None) -> Any:
    if not row:
        return None
    return row.get("value_num") if row.get("value_num") is not None else row.get("value_text")


def _enrich_runtime(runtime: list[dict[str, Any]], features: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    feature_map = {
        "MONTHLY_DIRECTION_3M": "MONTHLY_DIRECTION_3M",
        "FAST": "FAST_STATE",
        "SLOW": "SLOW_STATE",
    }
    enriched: list[dict[str, Any]] = []
    for raw in runtime:
        row = dict(raw)
        engine_id = str(row.get("engine_id") or "")
        feature_name = feature_map.get(engine_id)
        if feature_name:
            feature = features.get(feature_name)
            if feature:
                row["display_output"] = _feature_value(feature)
                row["display_evidence_class"] = feature.get("quality_status")
                row["display_as_of"] = feature.get("calculation_ts")
                row["display_input_cutoff"] = feature.get("input_cutoff")
                row["display_feature_version"] = feature.get("feature_version")
        elif engine_id == "GVZ_RISK":
            gvz_value = _feature_value(features.get("GVZ_VALUE"))
            gvz_regime = _feature_value(features.get("GVZ_REGIME"))
            gvz_cap = _feature_value(features.get("GVZ_CAP"))
            gvz_panic = _feature_value(features.get("GVZ_PANIC"))
            parts: list[str] = []
            if gvz_value is not None:
                parts.append(f"GVZ={gvz_value}")
            if gvz_regime is not None:
                parts.append(f"REGIME={gvz_regime}")
            if gvz_cap is not None:
                parts.append(f"CAP={gvz_cap}")
            if gvz_panic is not None:
                parts.append(f"PANIC={gvz_panic}")
            if parts:
                anchor = features.get("GVZ_REGIME") or features.get("GVZ_VALUE")
                row["display_output"] = " · ".join(parts)
                row["display_evidence_class"] = None if not anchor else anchor.get("quality_status")
                row["display_as_of"] = None if not anchor else anchor.get("calculation_ts")
                row["display_input_cutoff"] = None if not anchor else anchor.get("input_cutoff")
                row["display_feature_version"] = None if not anchor else anchor.get("feature_version")
        enriched.append(row)
    return enriched


def fetch_runtime_observability(database_url: str) -> dict[str, Any]:
    """Read only the sanitized current runtime/context surfaces."""
    url = str(database_url or "").strip()
    if not url:
        return snapshot_runtime_observability(load_production_display_snapshot())

    try:
        conn_ctx = psycopg.connect(url, autocommit=False, row_factory=dict_row)
    except psycopg.OperationalError:
        return snapshot_runtime_observability(load_production_display_snapshot())

    with conn_ctx as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                "select to_regclass('public.current_engine_runtime_state_v1') as runtime_view, "
                "to_regclass('public.current_context_feature_state_v1') as context_view, "
                "to_regclass('public.data_evidence_spine_health_v1') as health_view"
            )
            schema = _to_dict(cur.fetchone())
            if any(schema.get(key) is None for key in ("runtime_view", "context_view", "health_view")):
                conn.rollback()
                return snapshot_runtime_observability(load_production_display_snapshot())

            cur.execute(
                """
                select run_id,engine_id,engine_version,engine_role,as_of,target_context,
                       evidence_class,runtime_status,status_code,direction_vote_permitted,
                       git_commit,input_fingerprint,metadata,created_at
                from current_engine_runtime_state_v1
                order by engine_id
                """
            )
            runtime = [dict(row) for row in cur.fetchall()]
            target_context = _latest_target_context(runtime)
            features = _latest_features(cur, target_context) if target_context else {}
            runtime = _enrich_runtime(runtime, features)

            cur.execute("select * from data_evidence_spine_health_v1")
            health = _to_dict(cur.fetchone())
        conn.rollback()

    current_ids = {str(row.get("engine_id") or "") for row in runtime}
    runtime_complete = (
        len(runtime) == EXPECTED_ENGINE_COUNT
        and current_ids == set(ENGINE_DISPLAY_ORDER)
        and all(str(row.get("runtime_status") or "").upper() == "ACTIVE" for row in runtime)
        and len(features) == len(CURRENT_CONTEXT_FEATURES)
    )
    integrity_ok = bool(
        int(health.get("orphan_input_snapshots") or 0) == 0
        and int(health.get("expert_rows_without_input_set") or 0) == 0
        and int(health.get("expert_input_fingerprint_mismatches") or 0) == 0
    )

    return {
        "contract": RUNTIME_SOURCE_CONTRACT,
        "status": "CURRENT_RUNTIME_HEALTH_PASS" if (runtime_complete and integrity_ok) else "CURRENT_RUNTIME_HEALTH_BLOCKED",
        "runtime": runtime,
        "runtime_engine_count": len(runtime),
        "health": health,
        "integrity_ok": integrity_ok,
        "runtime_complete": runtime_complete,
        "context_target": target_context,
        "context_feature_count": len(features),
        "database_writes": "NONE",
        "source_mode": "NEON_CURRENT_SURFACES_READ_ONLY",
        "snapshot_contract": None,
        "snapshot_source_state_at": None,
        "snapshot_payload_sha256": None,
    }
