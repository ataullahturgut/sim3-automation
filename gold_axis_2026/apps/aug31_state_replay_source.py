from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

SNAPSHOT_CONTRACT = "FROZEN_AUG31_STATE_REPLAY_DISPLAY_SNAPSHOT_V1"
SNAPSHOT_PATH = Path(__file__).with_name("aug31_state_replay_snapshot.json")
TARGET_CONTEXT = "2026-09"
STATE_AS_OF = "2026-08-31T21:00:00+00:00"
EVIDENCE_CLASS = "HISTORICAL_REPLAY"
SOURCE_DB = "NEON_DB_READ_ONLY"
SOURCE_SNAPSHOT = "PRODUCTION_SNAPSHOT_FALLBACK"
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


def _payload_hash(snapshot: dict[str, Any]) -> str:
    payload = dict(snapshot)
    payload.pop("payload_sha256", None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(rows) != len(FEATURE_NAMES):
        raise RuntimeError(f"AUG31_STATE_REPLAY_ROW_COUNT:{len(rows)}")
    names = [str(r.get("feature_name") or "") for r in rows]
    if set(names) != set(FEATURE_NAMES) or len(names) != len(set(names)):
        raise RuntimeError(f"AUG31_STATE_REPLAY_IDENTITIES_INVALID:{names}")
    for row in rows:
        metadata = dict(row.get("metadata") or {})
        if row.get("quality_status") != EVIDENCE_CLASS:
            raise RuntimeError(f"AUG31_STATE_REPLAY_QUALITY_INVALID:{row.get('feature_name')}")
        if metadata.get("evidence_class") != EVIDENCE_CLASS:
            raise RuntimeError(f"AUG31_STATE_REPLAY_EVIDENCE_INVALID:{row.get('feature_name')}")
        if metadata.get("target_context") != TARGET_CONTEXT:
            raise RuntimeError(f"AUG31_STATE_REPLAY_TARGET_INVALID:{row.get('feature_name')}")
        if metadata.get("state_as_of") != STATE_AS_OF:
            raise RuntimeError(f"AUG31_STATE_REPLAY_BOUNDARY_INVALID:{row.get('feature_name')}:{metadata.get('state_as_of')}")
        if metadata.get("prospective_h1_claim") is not False:
            raise RuntimeError(f"AUG31_STATE_REPLAY_PROSPECTIVE_VIOLATION:{row.get('feature_name')}")
        if metadata.get("current_runtime_authority") is not False:
            raise RuntimeError(f"AUG31_STATE_REPLAY_RUNTIME_AUTHORITY_VIOLATION:{row.get('feature_name')}")
        if metadata.get("canonical_authority") is not False:
            raise RuntimeError(f"AUG31_STATE_REPLAY_CANONICAL_AUTHORITY_VIOLATION:{row.get('feature_name')}")
    return rows


def _shape(rows: list[dict[str, Any]], *, source_mode: str, snapshot_sha256: str | None = None, source_state_at: str | None = None) -> dict[str, Any]:
    validated = _validate_rows(rows)
    values = {str(r["feature_name"]): r.get("value_text") for r in validated}
    try:
        gvz_value = float(values["AUG31_REPLAY_GVZ_VALUE"])
        gvz_cap = float(values["AUG31_REPLAY_GVZ_CAP"])
    except Exception as exc:
        raise RuntimeError("AUG31_STATE_REPLAY_GVZ_NUMERIC_INVALID") from exc
    panic_raw = str(values["AUG31_REPLAY_GVZ_PANIC"]).strip().lower()
    if panic_raw not in {"true", "false"}:
        raise RuntimeError("AUG31_STATE_REPLAY_GVZ_PANIC_INVALID")
    result = {
        "contract": "FROZEN_AUG31_EOD_STATE_REPLAY_V1",
        "snapshot_contract": SNAPSHOT_CONTRACT if source_mode == SOURCE_SNAPSHOT else None,
        "source_mode": source_mode,
        "source_state_at": source_state_at,
        "snapshot_payload_sha256": snapshot_sha256,
        "target_context": TARGET_CONTEXT,
        "state_as_of": STATE_AS_OF,
        "evidence_class": EVIDENCE_CLASS,
        "prospective_h1_claim": False,
        "current_runtime_authority": False,
        "canonical_authority": False,
        "direction_vote_permitted": False,
        "monthly_direction_3m": str(values["AUG31_REPLAY_MONTHLY_DIRECTION_3M"]),
        "fast_state": str(values["AUG31_REPLAY_FAST_STATE"]),
        "slow_state": str(values["AUG31_REPLAY_SLOW_STATE"]),
        "gvz_value": gvz_value,
        "gvz_cap": gvz_cap,
        "gvz_panic": panic_raw == "true",
        "gvz_regime": str(values["AUG31_REPLAY_GVZ_REGIME"]),
        "blocked_components": dict(BLOCKERS),
        "database_writes": "NONE",
    }
    if result["monthly_direction_3m"] not in {"UP", "DOWN", "NEUTRAL"}:
        raise RuntimeError("AUG31_STATE_REPLAY_MONTHLY_INVALID")
    if result["fast_state"] not in {"ROBUST_UP", "ROBUST_DOWN", "MIXED", "INSUFFICIENT_DATA"}:
        raise RuntimeError("AUG31_STATE_REPLAY_FAST_INVALID")
    if result["slow_state"] not in {"ROBUST_UP", "ROBUST_DOWN", "NOT_YET_ROBUST", "INSUFFICIENT_DATA"}:
        raise RuntimeError("AUG31_STATE_REPLAY_SLOW_INVALID")
    if result["gvz_regime"] not in {"NORMAL", "ELEVATED", "PANIC"}:
        raise RuntimeError("AUG31_STATE_REPLAY_GVZ_REGIME_INVALID")
    return result


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or snapshot.get("snapshot_contract") != SNAPSHOT_CONTRACT:
        raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_CONTRACT_INVALID")
    if snapshot.get("database_writes") != "NONE":
        raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_WRITE_CLAIM_INVALID")
    expected = str(snapshot.get("payload_sha256") or "").strip().lower()
    if not expected or expected != _payload_hash(snapshot):
        raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_FINGERPRINT_INVALID")
    if snapshot.get("target_context") != TARGET_CONTEXT or snapshot.get("state_as_of") != STATE_AS_OF:
        raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_SCOPE_INVALID")
    if snapshot.get("blocked_components") != BLOCKERS:
        raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_BLOCKERS_INVALID")
    _validate_rows(list(snapshot.get("features") or []))
    return snapshot


def load_snapshot(path: Path | str | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else SNAPSHOT_PATH
    if not target.is_file():
        raise RuntimeError(f"AUG31_STATE_REPLAY_SNAPSHOT_NOT_FOUND:{target}")
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError("AUG31_STATE_REPLAY_SNAPSHOT_JSON_INVALID") from exc
    return validate_snapshot(data)


def _db_rows(url: str) -> list[dict[str, Any]]:
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT feature_name,feature_version,calculation_ts,input_cutoff,value_text,
                       git_commit,quality_status,metadata
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
            rows = [dict(r) for r in cur.fetchall()]
        conn.rollback()
    return _validate_rows(rows)


def fetch_aug31_state_replay(database_url: str) -> dict[str, Any]:
    url = str(database_url or "").strip()
    if url:
        try:
            rows = _db_rows(url)
            source_state_at = max(str(r.get("calculation_ts") or "") for r in rows)
            return _shape(rows, source_mode=SOURCE_DB, source_state_at=source_state_at)
        except psycopg.OperationalError:
            pass
    snapshot = load_snapshot()
    return _shape(
        [dict(r) for r in snapshot["features"]],
        source_mode=SOURCE_SNAPSHOT,
        snapshot_sha256=str(snapshot.get("payload_sha256") or ""),
        source_state_at=str(snapshot.get("source_state_at") or ""),
    )
