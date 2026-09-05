from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from engine_observability_contract import ENGINE_DISPLAY_ORDER
from production_display_snapshot import (
    load_production_display_snapshot,
    snapshot_runtime_observability,
)


RUNTIME_SOURCE_CONTRACT = "FROZEN_DATA_EVIDENCE_SPINE_V1_READ_ONLY_APP_V2_CURRENT_MONTH_REFERENCE"
EXPECTED_ENGINE_COUNT = len(ENGINE_DISPLAY_ORDER)
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


def _runtime_target_context(runtime: list[dict[str, Any]]) -> str | None:
    targets = [str(row.get("target_context") or "").strip() for row in runtime]
    targets = [value for value in targets if value]
    if not targets:
        return None
    # The view is one latest row per engine. Prefer the most common current
    # target and break ties deterministically by the lexical month key.
    counts: dict[str, int] = {}
    for value in targets:
        counts[value] = counts.get(value, 0) + 1
    return max(sorted(counts), key=lambda value: counts[value])


def _attach_current_month_replay_references(
    cur: psycopg.Cursor[Any],
    runtime: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, str | None]:
    """Attach governed replay evidence without changing operational runtime state.

    Historical replay is presentation/reference evidence only. We intentionally
    preserve runtime_status/status_code from latest_engine_runtime_state and add
    a nested current_month_reference object to metadata for the observability
    layer. No selector, ensemble, canonical authority, or decision output is
    synthesized here.
    """
    target_context = _runtime_target_context(runtime)
    if not target_context:
        return runtime, 0, None

    cur.execute(
        """
        select distinct on (expert_id)
               expert_id, model_version, forecast_value, unit, target_month,
               forecast_origin, as_of, evidence_class, forecast_track,
               canonical_authority, auto_selector, auto_ensemble, selector_status
        from monthly_expert_forecasts
        where forecast_track='HISTORICAL_REPLAY'
          and to_char(target_month, 'YYYY-MM')=%s
        order by expert_id, as_of desc, id desc
        """,
        (target_context,),
    )
    refs = {str(row["expert_id"]): dict(row) for row in cur.fetchall()}

    attached = 0
    enriched: list[dict[str, Any]] = []
    for source_row in runtime:
        row = dict(source_row)
        ref = refs.get(str(row.get("engine_id") or ""))
        if ref:
            # Fail closed: only replay rows with no canonical/auto authority can
            # be exposed as current-month reference evidence.
            if (
                str(ref.get("evidence_class") or "") == "HISTORICAL_REPLAY"
                and ref.get("canonical_authority") is False
                and str(ref.get("auto_selector") or "") == "OFF"
                and str(ref.get("auto_ensemble") or "") == "OFF"
            ):
                metadata = dict(row.get("metadata") or {})
                metadata["current_month_reference"] = {
                    "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
                    "expert_id": ref.get("expert_id"),
                    "model_version": ref.get("model_version"),
                    "forecast_value": ref.get("forecast_value"),
                    "unit": ref.get("unit"),
                    "target_month": ref.get("target_month"),
                    "forecast_origin": ref.get("forecast_origin"),
                    "as_of": ref.get("as_of"),
                    "evidence_class": ref.get("evidence_class"),
                    "forecast_track": ref.get("forecast_track"),
                    "canonical_authority": False,
                    "auto_selector": "OFF",
                    "auto_ensemble": "OFF",
                    "selector_status": ref.get("selector_status"),
                    "operational_runtime_status": row.get("runtime_status"),
                    "operational_status_code": row.get("status_code"),
                }
                row["metadata"] = metadata
                attached += 1
        enriched.append(row)
    return enriched, attached, target_context


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
                    "current_month_reference_target": None,
                    "current_month_reference_count": 0,
                    "database_writes": "NONE",
                }

            cur.execute(
                """
                select run_id,engine_id,engine_version,engine_role,as_of,target_context,
                       evidence_class,runtime_status,status_code,direction_vote_permitted,
                       git_commit,input_fingerprint,metadata,created_at
                from latest_engine_runtime_state
                where engine_id=any(%s)
                order by engine_id
                """,
                (list(ENGINE_DISPLAY_ORDER),),
            )
            runtime = [dict(row) for row in cur.fetchall()]
            runtime, current_month_reference_count, current_month_reference_target = (
                _attach_current_month_replay_references(cur, runtime)
            )

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
        "current_month_reference_target": current_month_reference_target,
        "current_month_reference_count": current_month_reference_count,
        "database_writes": "NONE",
        "source_mode": "NEON_DB_READ_ONLY",
        "snapshot_contract": None,
        "snapshot_source_state_at": None,
        "snapshot_payload_sha256": None,
    }
