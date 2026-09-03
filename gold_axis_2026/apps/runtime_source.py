from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from production_display_snapshot import (
    load_production_display_snapshot,
    snapshot_runtime_observability,
)


RUNTIME_SOURCE_CONTRACT = "FROZEN_DATA_EVIDENCE_SPINE_V1_READ_ONLY_APP_V1"
EXPECTED_ENGINE_COUNT = 12
CONTEXT_FEATURES = (
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


def fetch_runtime_observability(database_url: str) -> dict[str, Any]:
    """Read runtime/health without recomputation; Neon primary, snapshot fallback."""
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
            cur.execute("select to_regclass('public.latest_engine_runtime_state') as runtime_view, to_regclass('public.data_evidence_spine_health_v1') as health_view")
            schema = _to_dict(cur.fetchone())
            if schema.get("runtime_view") is None or schema.get("health_view") is None:
                conn.rollback()
                return {
                    "contract": RUNTIME_SOURCE_CONTRACT,
                    "status": "BLOCKED_DATA_EVIDENCE_SPINE_SCHEMA_NOT_AVAILABLE",
                    "runtime": [],
                    "runtime_engine_count": 0,
                    "health": {},
                    "integrity_ok": False,
                    "context_target": None,
                    "context_expected": len(CONTEXT_FEATURES),
                    "context_exactly_one_link": 0,
                    "database_writes": "NONE",
                }

            cur.execute(
                """
                select run_id,engine_id,engine_version,engine_role,as_of,target_context,
                       evidence_class,runtime_status,status_code,direction_vote_permitted,
                       git_commit,input_fingerprint,metadata,created_at
                from latest_engine_runtime_state
                order by engine_id
                """
            )
            runtime = [dict(row) for row in cur.fetchall()]

            cur.execute("select * from data_evidence_spine_health_v1")
            health = _to_dict(cur.fetchone())

            cur.execute(
                """
                select metadata->>'target_context' as target_context
                from derived_feature_snapshots
                where feature_name in ('MONTHLY_DIRECTION_3M','FAST_STATE','SLOW_STATE','GVZ_REGIME')
                  and coalesce(metadata->>'target_context','') <> ''
                order by calculation_ts desc,id desc limit 1
                """
            )
            target_row = cur.fetchone()
            context_target = str(target_row["target_context"]) if target_row and target_row["target_context"] else None

            context_exactly_one_link = 0
            if context_target:
                cur.execute(
                    """
                    with expected as (
                        select id
                        from derived_feature_snapshots
                        where feature_name=any(%s)
                          and metadata->>'target_context'=%s
                    )
                    select count(*) as n
                    from expected e
                    where (select count(*) from engine_execution_derived_outputs o
                           where o.derived_feature_snapshot_id=e.id) = 1
                    """,
                    (list(CONTEXT_FEATURES), context_target),
                )
                context_exactly_one_link = int(cur.fetchone()["n"])
        conn.rollback()

    integrity_ok = bool(
        int(health.get("orphan_input_snapshots") or 0) == 0
        and int(health.get("expert_rows_without_input_set") or 0) == 0
        and int(health.get("expert_input_fingerprint_mismatches") or 0) == 0
    )
    runtime_complete = len(runtime) == EXPECTED_ENGINE_COUNT
    context_complete = context_exactly_one_link == len(CONTEXT_FEATURES)
    status = "DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS" if (integrity_ok and runtime_complete and context_complete) else "BLOCKED_DATA_EVIDENCE_SPINE_RUNTIME_HEALTH"

    return {
        "contract": RUNTIME_SOURCE_CONTRACT,
        "status": status,
        "runtime": runtime,
        "runtime_engine_count": len(runtime),
        "health": health,
        "integrity_ok": integrity_ok,
        "runtime_complete": runtime_complete,
        "context_target": context_target,
        "context_expected": len(CONTEXT_FEATURES),
        "context_exactly_one_link": context_exactly_one_link,
        "context_complete": context_complete,
        "database_writes": "NONE",
        "source_mode": "NEON_DB_READ_ONLY",
        "snapshot_contract": None,
        "snapshot_source_state_at": None,
        "snapshot_payload_sha256": None,
    }
