from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2"
LEGACY_SNAPSHOT_CONTRACT = "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1"
SNAPSHOT_SOURCE_MODE = "PRODUCTION_SNAPSHOT_FALLBACK"
SNAPSHOT_PATH = Path(__file__).with_name("production_display_snapshot.json")
EXPECTED_ENGINE_COUNT = 12
REQUIRED_CONTEXT_FEATURES = (
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
)
INTEGRITY_ZERO_FIELDS = (
    "orphan_input_snapshots",
    "expert_rows_without_input_set",
    "expert_input_fingerprint_mismatches",
)
FORBIDDEN_KEYS = {
    "action_state",
    "classification",
    "canonical_forecast",
    "canonical_forecast_value",
    "database_url",
    "connection_string",
    "password",
    "selector_weights",
}
REPLAY_TRACK = "HISTORICAL_REPLAY"
REPLAY_EVIDENCE = "HISTORICAL_REPLAY"
SELECTOR_LOCK = "NOT_PROVEN_EXPERT_SELECTION_RULE"


def _payload_for_hash(snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = dict(snapshot)
    payload.pop("payload_sha256", None)
    return payload


def payload_sha256(snapshot: dict[str, Any]) -> str:
    canonical = json.dumps(
        _payload_for_hash(snapshot),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _reject_forbidden_keys(value: Any, path: str = "snapshot") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise RuntimeError(f"PRODUCTION_DISPLAY_SNAPSHOT_FORBIDDEN_KEY:{path}.{key}")
            _reject_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_keys(child, f"{path}[{index}]")


def _validate_replay_rows(snapshot: dict[str, Any]) -> None:
    rows = snapshot.get("historical_replay_experts", [])
    if not isinstance(rows, list):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_INVALID")
    if snapshot.get("snapshot_contract") == LEGACY_SNAPSHOT_CONTRACT:
        if rows:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_LEGACY_REPLAY_FORBIDDEN")
        return
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_ROW_INVALID")
        if row.get("forecast_track") != REPLAY_TRACK or row.get("evidence_class") != REPLAY_EVIDENCE:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_TRACK_EVIDENCE_MISMATCH")
        if row.get("canonical_authority") is not False:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_CANONICAL_AUTHORITY_VIOLATION")
        if row.get("selector_status") != SELECTOR_LOCK or row.get("auto_selector") != "OFF" or row.get("auto_ensemble") != "OFF":
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_SELECTOR_LOCK_VIOLATION")
        provenance = dict(row.get("provenance") or {})
        if provenance.get("historical_replay") is not True or provenance.get("prospective_claim") is not False:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_PROSPECTIVE_CLAIM_VIOLATION")
        if provenance.get("canonical_authority") is not False or provenance.get("direction_vote_permitted") is not False:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_AUTHORITY_VIOLATION")
        ids.append(str(row.get("expert_id") or ""))
    if len(ids) != len(set(ids)) or "" in ids:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_IDENTITY_INVALID")
    target = snapshot.get("historical_replay_target_month")
    if rows and not target:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_TARGET_MISSING")
    if rows and any(str(row.get("target_month") or "")[:7] != str(target)[:7] for row in rows):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_REPLAY_TARGET_MISMATCH")


def validate_production_display_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_NOT_OBJECT")
    if snapshot.get("snapshot_contract") not in {SNAPSHOT_CONTRACT, LEGACY_SNAPSHOT_CONTRACT}:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_CONTRACT_MISMATCH")
    if snapshot.get("database_writes") != "NONE":
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_WRITE_CLAIM_INVALID")

    expected_hash = str(snapshot.get("payload_sha256") or "").strip().lower()
    actual_hash = payload_sha256(snapshot)
    if not expected_hash or expected_hash != actual_hash:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_FINGERPRINT_MISMATCH")

    runtime = snapshot.get("runtime")
    if not isinstance(runtime, list) or len(runtime) != EXPECTED_ENGINE_COUNT:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_RUNTIME_COUNT_MISMATCH")
    engine_ids = [str(row.get("engine_id") or "") for row in runtime if isinstance(row, dict)]
    if len(engine_ids) != EXPECTED_ENGINE_COUNT or len(set(engine_ids)) != EXPECTED_ENGINE_COUNT or "" in engine_ids:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_RUNTIME_IDENTITY_INVALID")

    features = snapshot.get("features")
    if not isinstance(features, list) or len(features) != len(REQUIRED_CONTEXT_FEATURES):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_FEATURE_COUNT_MISMATCH")
    feature_names = [str(row.get("feature_name") or "") for row in features if isinstance(row, dict)]
    if set(feature_names) != set(REQUIRED_CONTEXT_FEATURES) or len(feature_names) != len(set(feature_names)):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_FEATURE_IDENTITY_INVALID")

    target_context = str(snapshot.get("target_context") or "").strip()
    if len(target_context) != 7:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_TARGET_CONTEXT_INVALID")
    for row in runtime:
        if str(row.get("target_context") or "") != target_context:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_RUNTIME_TARGET_MISMATCH")
    for row in features:
        metadata = dict(row.get("metadata") or {})
        if str(metadata.get("target_context") or "") != target_context:
            raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_FEATURE_TARGET_MISMATCH")

    health = snapshot.get("health")
    if not isinstance(health, dict):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_HEALTH_INVALID")
    for key in INTEGRITY_ZERO_FIELDS:
        if int(health.get(key) or 0) != 0:
            raise RuntimeError(f"PRODUCTION_DISPLAY_SNAPSHOT_INTEGRITY_BLOCKED:{key}")
    if int(snapshot.get("context_exactly_one_link") or 0) != len(REQUIRED_CONTEXT_FEATURES):
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_CONTEXT_LINK_MISMATCH")

    _validate_replay_rows(snapshot)
    _reject_forbidden_keys(snapshot)
    return snapshot


def load_production_display_snapshot(path: Path | str | None = None) -> dict[str, Any]:
    snapshot_path = Path(path) if path is not None else SNAPSHOT_PATH
    if not snapshot_path.is_file():
        raise RuntimeError(f"PRODUCTION_DISPLAY_SNAPSHOT_NOT_FOUND:{snapshot_path}")
    try:
        raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_JSON_INVALID") from exc
    return validate_production_display_snapshot(raw)


def snapshot_feature_rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    validated = validate_production_display_snapshot(snapshot)
    return [dict(row) for row in validated["features"]]


def snapshot_historical_replay_rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    validated = validate_production_display_snapshot(snapshot)
    return [dict(row) for row in validated.get("historical_replay_experts", [])]


def snapshot_runtime_observability(snapshot: dict[str, Any]) -> dict[str, Any]:
    validated = validate_production_display_snapshot(snapshot)
    health = dict(validated["health"])
    return {
        "contract": "FROZEN_DATA_EVIDENCE_SPINE_V1_READ_ONLY_APP_V1",
        "status": "DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS",
        "source_mode": SNAPSHOT_SOURCE_MODE,
        "snapshot_contract": validated.get("snapshot_contract"),
        "snapshot_source_state_at": validated.get("source_state_at"),
        "snapshot_payload_sha256": validated.get("payload_sha256"),
        "runtime": [dict(row) for row in validated["runtime"]],
        "runtime_engine_count": EXPECTED_ENGINE_COUNT,
        "health": health,
        "integrity_ok": True,
        "runtime_complete": True,
        "context_target": validated.get("target_context"),
        "context_expected": len(REQUIRED_CONTEXT_FEATURES),
        "context_exactly_one_link": int(validated["context_exactly_one_link"]),
        "context_complete": True,
        "database_writes": "NONE",
    }
