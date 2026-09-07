from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row


SNAPSHOT_CONTRACT = "GOLD_CONTROL_CURRENT_PRODUCTION_DISPLAY_SNAPSHOT_V141"
CURRENT_ENGINE_IDS = (
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
CURRENT_CONTEXT_FEATURES = (
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
)
AUTHORITY_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _payload_hash(snapshot: dict[str, Any]) -> str:
    payload = dict(snapshot)
    payload.pop("payload_sha256", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def export_snapshot(database_url: str) -> dict[str, Any]:
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                "select to_regclass('public.current_engine_runtime_state_v1') as runtime_view, "
                "to_regclass('public.current_context_feature_state_v1') as context_view"
            )
            row = cur.fetchone()
            if not row or row["runtime_view"] is None or row["context_view"] is None:
                raise RuntimeError("CURRENT_SURFACE_VIEW_NOT_AVAILABLE")

            cur.execute(
                """
                select run_id,engine_id,engine_version,engine_role,as_of,target_context,
                       evidence_class,runtime_status,status_code,direction_vote_permitted,
                       git_commit,input_fingerprint,metadata,created_at
                from current_engine_runtime_state_v1
                order by engine_id
                """
            )
            runtime = [_jsonable(dict(row)) for row in cur.fetchall()]
            ids = {str(row.get("engine_id") or "") for row in runtime}
            if len(runtime) != 12 or ids != set(CURRENT_ENGINE_IDS):
                raise RuntimeError(f"CURRENT_SNAPSHOT_RUNTIME_INVALID:{len(runtime)}:{sorted(ids)}")
            if any(str(row.get("runtime_status") or "").upper() != "ACTIVE" for row in runtime):
                raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_NOT_ALL_ACTIVE")

            targets = {str(row.get("target_context") or "") for row in runtime}
            if len(targets) != 1:
                raise RuntimeError(f"CURRENT_SNAPSHOT_RUNTIME_TARGETS_INVALID:{sorted(targets)}")
            target_context = next(iter(targets))

            cur.execute(
                """
                select id,feature_name,feature_version,calculation_ts,input_cutoff,
                       value_num,value_text,git_commit,quality_status,metadata
                from current_context_feature_state_v1
                where feature_name=any(%s)
                  and metadata->>'target_context'=%s
                order by feature_name
                """,
                (list(CURRENT_CONTEXT_FEATURES), target_context),
            )
            features = [_jsonable(dict(row)) for row in cur.fetchall()]
            names = {str(row.get("feature_name") or "") for row in features}
            if len(features) != len(CURRENT_CONTEXT_FEATURES) or names != set(CURRENT_CONTEXT_FEATURES):
                raise RuntimeError(f"CURRENT_SNAPSHOT_FEATURES_INVALID:{sorted(names)}")
            for feature in features:
                if feature.get("quality_status") != "HISTORICAL_REPLAY_CONTEXT":
                    raise RuntimeError("CURRENT_SNAPSHOT_CONTEXT_EVIDENCE_INVALID")
                metadata = feature.get("metadata") or {}
                if metadata.get("current_surface_contract") != "GOLD_CONTROL_CURRENT_SURFACE_V141":
                    raise RuntimeError("CURRENT_SNAPSHOT_CONTEXT_CONTRACT_INVALID")

            cur.execute("select * from data_evidence_spine_health_v1")
            health_row = cur.fetchone()
            if not health_row:
                raise RuntimeError("CURRENT_SNAPSHOT_HEALTH_MISSING")
            health = _jsonable(dict(health_row))
            for key in (
                "orphan_input_snapshots",
                "expert_rows_without_input_set",
                "expert_input_fingerprint_mismatches",
            ):
                if int(health.get(key) or 0) != 0:
                    raise RuntimeError(f"CURRENT_SNAPSHOT_INTEGRITY_BLOCKED:{key}")

            authority_store_counts: dict[str, int] = {}
            for table in AUTHORITY_TABLES:
                cur.execute(f"select count(*) as n from {table}")
                authority_store_counts[table] = int(cur.fetchone()["n"])
            if any(authority_store_counts.values()):
                raise RuntimeError(f"CURRENT_SNAPSHOT_AUTHORITY_STORE_NONZERO:{authority_store_counts}")
        conn.rollback()

    timestamps = [str(row.get("as_of") or "") for row in runtime]
    timestamps.extend(str(row.get("calculation_ts") or "") for row in features)
    source_state_at = max(value for value in timestamps if value)

    snapshot: dict[str, Any] = {
        "snapshot_contract": SNAPSHOT_CONTRACT,
        "source": "NEON_PRODUCTION_CURRENT_SURFACES_READ_ONLY_EXPORT",
        "source_state_at": source_state_at,
        "target_context": target_context,
        "runtime": runtime,
        "features": features,
        "health": health,
        "authority_store_counts": authority_store_counts,
        "database_writes": "NONE",
    }
    snapshot["payload_sha256"] = _payload_hash(snapshot)
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--out", default="gold_axis_2026/apps/production_display_snapshot.json")
    args = parser.parse_args()
    snapshot = export_snapshot(args.database_url)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(
        "CURRENT_PRODUCTION_DISPLAY_SNAPSHOT_EXPORT_PASS "
        f"runtime={len(snapshot['runtime'])}/12 features={len(snapshot['features'])}/7 "
        f"target={snapshot['target_context']} sha256={snapshot['payload_sha256']} writes=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
