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

SNAPSHOT_CONTRACT = "FROZEN_AUG31_STATE_REPLAY_DISPLAY_SNAPSHOT_V1"
TARGET_CONTEXT = "2026-09"
STATE_AS_OF = "2026-08-31T21:00:00+00:00"
EVIDENCE_CLASS = "HISTORICAL_REPLAY"
FEATURE_NAMES = (
    "AUG31_REPLAY_MONTHLY_DIRECTION_3M",
    "AUG31_REPLAY_FAST_STATE",
    "AUG31_REPLAY_SLOW_STATE",
    "AUG31_REPLAY_GVZ_VALUE",
    "AUG31_REPLAY_GVZ_CAP",
    "AUG31_REPLAY_GVZ_PANIC",
    "AUG31_REPLAY_GVZ_REGIME",
)
BLOCKERS = {
    "CAUSAL_PATCH": "BLOCKED_REPLAY_INPUT_SET_NOT_REPRODUCIBLE_FOR_2026_08_31",
    "VW_MIDAS_MSVR": "BLOCKED_NOT_PROVEN_EXECUTABLE",
    "MACRO_EVENT": "BLOCKED_NOT_FULLY_RECOVERED",
    "EMERGENCY_LEVEL": "BLOCKED_NO_AUTHORIZED_REPLAY_MONTHLY_REFERENCE",
    "EMERGENCY_REVERSAL": "BLOCKED_NO_AUTHORIZED_REPLAY_MONTHLY_REFERENCE",
    "BOCPD": "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED",
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _hash(snapshot: dict[str, Any]) -> str:
    payload = dict(snapshot)
    payload.pop("payload_sha256", None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def export(database_url: str) -> dict[str, Any]:
    url = str(database_url or "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT feature_name,feature_version,calculation_ts,input_cutoff,value_text,
                       git_commit,quality_status,
                       jsonb_build_object(
                           'target_context',metadata->>'target_context',
                           'state_as_of',metadata->>'state_as_of',
                           'evidence_class',metadata->>'evidence_class',
                           'prospective_h1_claim',COALESCE((metadata->>'prospective_h1_claim')::boolean,false),
                           'current_runtime_authority',COALESCE((metadata->>'current_runtime_authority')::boolean,false),
                           'canonical_authority',COALESCE((metadata->>'canonical_authority')::boolean,false),
                           'contract',metadata->>'contract',
                           'role',metadata->>'role'
                       ) AS metadata
                FROM derived_feature_snapshots
                WHERE feature_name=ANY(%s)
                  AND quality_status=%s
                  AND metadata->>'evidence_class'=%s
                  AND metadata->>'target_context'=%s
                  AND metadata->>'state_as_of'=%s
                ORDER BY feature_name,calculation_ts DESC,id DESC
                """,
                (list(FEATURE_NAMES), EVIDENCE_CLASS, EVIDENCE_CLASS, TARGET_CONTEXT, STATE_AS_OF),
            )
            rows = [_jsonable(dict(r)) for r in cur.fetchall()]
            names = [str(r.get("feature_name") or "") for r in rows]
            if len(rows) != 7 or set(names) != set(FEATURE_NAMES) or len(names) != len(set(names)):
                raise RuntimeError(f"AUG31_STATE_REPLAY_SNAPSHOT_CARDINALITY_INVALID:{names}")
            for row in rows:
                m = dict(row.get("metadata") or {})
                if m.get("evidence_class") != EVIDENCE_CLASS or m.get("target_context") != TARGET_CONTEXT or m.get("state_as_of") != STATE_AS_OF:
                    raise RuntimeError(f"AUG31_STATE_REPLAY_SNAPSHOT_SCOPE_INVALID:{row.get('feature_name')}")
                if m.get("prospective_h1_claim") is not False or m.get("current_runtime_authority") is not False or m.get("canonical_authority") is not False:
                    raise RuntimeError(f"AUG31_STATE_REPLAY_SNAPSHOT_AUTHORITY_INVALID:{row.get('feature_name')}")
            cur.execute(
                """
                SELECT count(*) AS n
                FROM engine_execution_derived_outputs o
                JOIN derived_feature_snapshots d ON d.id=o.derived_feature_snapshot_id
                JOIN engine_execution_runs r ON r.run_id=o.run_id
                WHERE d.feature_name=ANY(%s)
                  AND r.evidence_class=%s
                  AND r.metadata->>'state_as_of'=%s
                """,
                (list(FEATURE_NAMES), EVIDENCE_CLASS, STATE_AS_OF),
            )
            if int(cur.fetchone()["n"]) != 7:
                raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_LINK_COUNT_INVALID")
            cur.execute("SELECT count(*) AS n FROM monthly_forecast_contracts")
            if int(cur.fetchone()["n"]) != 0:
                raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_CANONICAL_FORECAST_PRESENT")
            cur.execute("SELECT count(*) AS n FROM decision_signal_snapshots")
            if int(cur.fetchone()["n"]) != 0:
                raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_DECISION_PRESENT")
        conn.rollback()
    source_state_at = max(str(r.get("calculation_ts") or "") for r in rows)
    snapshot: dict[str, Any] = {
        "snapshot_contract": SNAPSHOT_CONTRACT,
        "source": "NEON_PRODUCTION_READ_ONLY_EXPORT",
        "source_state_at": source_state_at,
        "target_context": TARGET_CONTEXT,
        "state_as_of": STATE_AS_OF,
        "evidence_class": EVIDENCE_CLASS,
        "features": rows,
        "blocked_components": BLOCKERS,
        "database_writes": "NONE",
    }
    snapshot["payload_sha256"] = _hash(snapshot)
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--out", default="gold_axis_2026/apps/aug31_state_replay_snapshot.json")
    args = parser.parse_args()
    snapshot = export(args.database_url)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(
        "AUG31_STATE_REPLAY_DISPLAY_SNAPSHOT_EXPORT_PASS "
        f"features={len(snapshot['features'])}/7 target={snapshot['target_context']} "
        f"state_as_of={snapshot['state_as_of']} sha256={snapshot['payload_sha256']} writes=NONE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
