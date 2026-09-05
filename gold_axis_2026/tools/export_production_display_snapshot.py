from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2"
REQUIRED_FEATURES = (
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
)
CURRENT_ENGINE_IDS = (
    "CAUSAL_PATCH",
    "VW_MIDAS_MSVR",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "MACRO_EVENT_SUCCESSOR_V2",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "BOCPD_RETURN_SUCCESSOR_V1",
    "GVZ_RISK",
)
EXPECTED_ENGINE_COUNT = len(CURRENT_ENGINE_IDS)
REPLAY_TRACK = "HISTORICAL_REPLAY"
REPLAY_EVIDENCE = "HISTORICAL_REPLAY"
SELECTOR_LOCK = "NOT_PROVEN_EXPERT_SELECTION_RULE"


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _payload_hash(snapshot: dict[str, Any]) -> str:
    payload = dict(snapshot)
    payload.pop("payload_sha256", None)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def export_snapshot(database_url: str) -> dict[str, Any]:
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT engine_id,engine_version,engine_role,as_of,target_context,
                       evidence_class,runtime_status,status_code,direction_vote_permitted,
                       git_commit
                FROM latest_engine_runtime_state
                WHERE engine_id = ANY(%s)
                ORDER BY engine_id
                """,
                (list(CURRENT_ENGINE_IDS),),
            )
            runtime = [_jsonable(dict(row)) for row in cur.fetchall()]
            runtime_ids = {str(r["engine_id"]) for r in runtime}
            if (
                len(runtime) != EXPECTED_ENGINE_COUNT
                or len(runtime_ids) != EXPECTED_ENGINE_COUNT
                or runtime_ids != set(CURRENT_ENGINE_IDS)
            ):
                raise RuntimeError(f"SNAPSHOT_RUNTIME_CARDINALITY_INVALID:{len(runtime)}:{sorted(runtime_ids)}")

            targets = {str(row.get("target_context") or "") for row in runtime}
            if len(targets) != 1:
                raise RuntimeError(f"SNAPSHOT_RUNTIME_TARGETS_INVALID:{sorted(targets)}")
            target_context = next(iter(targets))

            cur.execute(
                """
                SELECT id,feature_name,feature_version,calculation_ts,input_cutoff,value_text,
                       git_commit,quality_status,
                       jsonb_build_object(
                           'target_context', metadata->>'target_context',
                           'evidence_class', metadata->>'evidence_class',
                           'prospective_h1_claim', COALESCE((metadata->>'prospective_h1_claim')::boolean,false)
                       ) AS metadata
                FROM derived_feature_snapshots
                WHERE feature_name=ANY(%s)
                  AND metadata->>'target_context'=%s
                ORDER BY id
                """,
                (list(REQUIRED_FEATURES), target_context),
            )
            features = [_jsonable(dict(row)) for row in cur.fetchall()]
            names = [row["feature_name"] for row in features]
            if len(features) != len(REQUIRED_FEATURES) or set(names) != set(REQUIRED_FEATURES) or len(names) != len(set(names)):
                raise RuntimeError(f"SNAPSHOT_FEATURE_CARDINALITY_INVALID:{names}")

            cur.execute("SELECT * FROM data_evidence_spine_health_v1")
            health_row = cur.fetchone()
            if not health_row:
                raise RuntimeError("SNAPSHOT_HEALTH_VIEW_EMPTY")
            health = _jsonable(dict(health_row))
            for key in (
                "orphan_input_snapshots",
                "expert_rows_without_input_set",
                "expert_input_fingerprint_mismatches",
            ):
                if int(health.get(key) or 0) != 0:
                    raise RuntimeError(f"SNAPSHOT_INTEGRITY_BLOCKED:{key}:{health.get(key)}")

            cur.execute(
                """
                WITH expected AS (
                    SELECT id
                    FROM derived_feature_snapshots
                    WHERE feature_name=ANY(%s)
                      AND metadata->>'target_context'=%s
                )
                SELECT count(*) AS n
                FROM expected e
                WHERE (SELECT count(*) FROM engine_execution_derived_outputs o
                       WHERE o.derived_feature_snapshot_id=e.id)=1
                """,
                (list(REQUIRED_FEATURES), target_context),
            )
            context_links = int(cur.fetchone()["n"])
            if context_links != len(REQUIRED_FEATURES):
                raise RuntimeError(f"SNAPSHOT_CONTEXT_LINK_INVALID:{context_links}")

            cur.execute(
                """
                WITH newest AS (
                    SELECT max(target_month) AS target_month
                    FROM monthly_expert_forecasts
                    WHERE forecast_track=%s AND evidence_class=%s
                ), ranked AS (
                    SELECT e.*,
                           row_number() OVER (PARTITION BY e.expert_id ORDER BY e.as_of DESC,e.id DESC) AS rn
                    FROM monthly_expert_forecasts e,newest n
                    WHERE e.forecast_track=%s
                      AND e.evidence_class=%s
                      AND e.target_month=n.target_month
                      AND e.canonical_authority=false
                      AND e.selector_status=%s
                      AND e.auto_selector='OFF'
                      AND e.auto_ensemble='OFF'
                )
                SELECT id,target_month,forecast_origin,as_of,forecast_track,
                       expert_id,model_name,model_version,expert_role,forecast_value,
                       unit,evidence_class,git_commit,input_snapshot_ids,input_fingerprint,
                       selector_status,auto_selector,auto_ensemble,canonical_authority,
                       provenance,created_at
                FROM ranked
                WHERE rn=1
                ORDER BY expert_id
                """,
                (REPLAY_TRACK, REPLAY_EVIDENCE, REPLAY_TRACK, REPLAY_EVIDENCE, SELECTOR_LOCK),
            )
            replay_rows = [_jsonable(dict(row)) for row in cur.fetchall()]
            replay_targets = {str(row.get("target_month") or "")[:7] for row in replay_rows}
            if len(replay_targets) > 1:
                raise RuntimeError(f"SNAPSHOT_REPLAY_TARGETS_INVALID:{sorted(replay_targets)}")
            for row in replay_rows:
                p = dict(row.get("provenance") or {})
                if p.get("historical_replay") is not True or p.get("prospective_claim") is not False:
                    raise RuntimeError(f"SNAPSHOT_REPLAY_PROSPECTIVE_GUARD_INVALID:{row.get('expert_id')}")
                if p.get("canonical_authority") is not False or p.get("direction_vote_permitted") is not False:
                    raise RuntimeError(f"SNAPSHOT_REPLAY_AUTHORITY_GUARD_INVALID:{row.get('expert_id')}")
        conn.rollback()

    timestamps = [str(row.get("as_of") or "") for row in runtime]
    timestamps.extend(str(row.get("calculation_ts") or "") for row in features)
    timestamps.extend(str(row.get("created_at") or "") for row in replay_rows)
    source_state_at = max(t for t in timestamps if t)

    snapshot: dict[str, Any] = {
        "snapshot_contract": SNAPSHOT_CONTRACT,
        "source": "NEON_PRODUCTION_READ_ONLY_EXPORT",
        "source_state_at": source_state_at,
        "target_context": target_context,
        "runtime": runtime,
        "features": features,
        "historical_replay_target_month": next(iter(replay_targets), None),
        "historical_replay_experts": replay_rows,
        "health": health,
        "context_exactly_one_link": context_links,
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
    text = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    output.write_text(text, encoding="utf-8")
    print(
        "PRODUCTION_DISPLAY_SNAPSHOT_EXPORT_PASS "
        f"runtime={len(snapshot['runtime'])}/{EXPECTED_ENGINE_COUNT} features={len(snapshot['features'])}/7 "
        f"replay={len(snapshot['historical_replay_experts'])} "
        f"links={snapshot['context_exactly_one_link']}/7 target={snapshot['target_context']} "
        f"sha256={snapshot['payload_sha256']} writes=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
