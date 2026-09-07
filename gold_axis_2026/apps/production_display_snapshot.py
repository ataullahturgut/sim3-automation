from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SNAPSHOT_CONTRACT = "GOLD_CONTROL_CURRENT_PRODUCTION_DISPLAY_SNAPSHOT_V142"
CURRENT_SURFACE_CONTRACT = "GOLD_CONTROL_CURRENT_SURFACE_V142"
SNAPSHOT_SOURCE_MODE = "PRODUCTION_CURRENT_SNAPSHOT_FALLBACK"
SNAPSHOT_PATH = Path(__file__).with_name("production_display_snapshot.json")
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
INTEGRITY_ZERO_FIELDS = (
    "orphan_input_snapshots",
    "expert_rows_without_input_set",
    "expert_input_fingerprint_mismatches",
)
AUTHORITY_ZERO_FIELDS = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)
FORBIDDEN_KEYS = {
    "action_state",
    "classification",
    "canonical_forecast_value",
    "database_url",
    "connection_string",
    "password",
    "selector_weights",
}


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
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _reject_forbidden_keys(value: Any, path: str = "snapshot") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise RuntimeError(f"CURRENT_SNAPSHOT_FORBIDDEN_KEY:{path}.{key}")
            _reject_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_keys(child, f"{path}[{index}]")


def validate_production_display_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise RuntimeError("CURRENT_SNAPSHOT_NOT_OBJECT")
    if snapshot.get("snapshot_contract") != SNAPSHOT_CONTRACT:
        raise RuntimeError("CURRENT_SNAPSHOT_CONTRACT_MISMATCH")
    if snapshot.get("current_surface_contract") != CURRENT_SURFACE_CONTRACT:
        raise RuntimeError("CURRENT_SNAPSHOT_SURFACE_CONTRACT_MISMATCH")
    if snapshot.get("database_writes") != "NONE":
        raise RuntimeError("CURRENT_SNAPSHOT_WRITE_CLAIM_INVALID")

    expected_hash = str(snapshot.get("payload_sha256") or "").strip().lower()
    actual_hash = payload_sha256(snapshot)
    if not expected_hash or expected_hash != actual_hash:
        raise RuntimeError("CURRENT_SNAPSHOT_FINGERPRINT_MISMATCH")

    runtime = snapshot.get("runtime")
    if not isinstance(runtime, list) or len(runtime) != len(CURRENT_ENGINE_IDS):
        raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_COUNT_MISMATCH")
    engine_ids = [str(row.get("engine_id") or "") for row in runtime if isinstance(row, dict)]
    if set(engine_ids) != set(CURRENT_ENGINE_IDS) or len(engine_ids) != len(set(engine_ids)):
        raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_IDENTITY_MISMATCH")
    if any(str(row.get("runtime_status") or "").upper() != "ACTIVE" for row in runtime):
        raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_NOT_ALL_ACTIVE")
    for row in runtime:
        metadata = row.get("metadata") if isinstance(row, dict) else None
        if not isinstance(metadata, dict) or metadata.get("current_surface_contract") != CURRENT_SURFACE_CONTRACT:
            raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_SURFACE_CONTRACT_MISMATCH")
        if metadata.get("runtime_selection_rule") != "LATEST_COMPLETE_12_ENGINE_TARGET_CONTEXT":
            raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_SELECTION_RULE_MISMATCH")

    target_context = str(snapshot.get("target_context") or "").strip()
    if len(target_context) != 7:
        raise RuntimeError("CURRENT_SNAPSHOT_TARGET_CONTEXT_INVALID")
    if any(str(row.get("target_context") or "") != target_context for row in runtime):
        raise RuntimeError("CURRENT_SNAPSHOT_RUNTIME_TARGET_MISMATCH")

    features = snapshot.get("features")
    if not isinstance(features, list) or len(features) != len(CURRENT_CONTEXT_FEATURES):
        raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_COUNT_MISMATCH")
    feature_names = [str(row.get("feature_name") or "") for row in features if isinstance(row, dict)]
    if set(feature_names) != set(CURRENT_CONTEXT_FEATURES) or len(feature_names) != len(set(feature_names)):
        raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_IDENTITY_MISMATCH")
    for row in features:
        if not isinstance(row, dict):
            raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_INVALID")
        if row.get("quality_status") != "HISTORICAL_REPLAY_CONTEXT":
            raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_EVIDENCE_INVALID")
        metadata = row.get("metadata")
        if not isinstance(metadata, dict) or metadata.get("current_surface_contract") != CURRENT_SURFACE_CONTRACT:
            raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_SURFACE_CONTRACT_MISMATCH")
        if metadata.get("context_selection_rule") != "LATEST_COMPLETE_7_FEATURE_TARGET_CONTEXT":
            raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_SELECTION_RULE_MISMATCH")
        if metadata.get("target_context") != target_context:
            raise RuntimeError("CURRENT_SNAPSHOT_FEATURE_TARGET_MISMATCH")

    source_surface = snapshot.get("source_surface")
    if not isinstance(source_surface, dict):
        raise RuntimeError("CURRENT_SNAPSHOT_SOURCE_SURFACE_MISSING")
    if int(source_surface.get("current_source_count") or 0) <= 0:
        raise RuntimeError("CURRENT_SNAPSHOT_SOURCE_SURFACE_EMPTY")
    if int(source_surface.get("disallowed_current_source_count") or 0) != 0:
        raise RuntimeError("CURRENT_SNAPSHOT_DISALLOWED_SOURCE_PRESENT")

    health = snapshot.get("health")
    if not isinstance(health, dict):
        raise RuntimeError("CURRENT_SNAPSHOT_HEALTH_INVALID")
    for key in INTEGRITY_ZERO_FIELDS:
        if int(health.get(key) or 0) != 0:
            raise RuntimeError(f"CURRENT_SNAPSHOT_INTEGRITY_BLOCKED:{key}")

    authority = snapshot.get("authority_store_counts")
    if not isinstance(authority, dict):
        raise RuntimeError("CURRENT_SNAPSHOT_AUTHORITY_COUNTS_MISSING")
    for key in AUTHORITY_ZERO_FIELDS:
        if int(authority.get(key) or 0) != 0:
            raise RuntimeError(f"CURRENT_SNAPSHOT_UNAUTHORIZED_AUTHORITY_STATE:{key}")

    _reject_forbidden_keys(snapshot)
    return snapshot


def load_production_display_snapshot(path: Path | str | None = None) -> dict[str, Any]:
    snapshot_path = Path(path) if path is not None else SNAPSHOT_PATH
    if not snapshot_path.is_file():
        raise RuntimeError(f"CURRENT_SNAPSHOT_NOT_FOUND:{snapshot_path}")
    try:
        raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError("CURRENT_SNAPSHOT_JSON_INVALID") from exc
    return validate_production_display_snapshot(raw)


def snapshot_feature_rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    validated = validate_production_display_snapshot(snapshot)
    return [dict(row) for row in validated["features"]]


def snapshot_historical_replay_rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    validate_production_display_snapshot(snapshot)
    return []


def snapshot_runtime_observability(snapshot: dict[str, Any]) -> dict[str, Any]:
    validated = validate_production_display_snapshot(snapshot)
    health = dict(validated["health"])
    source_surface = dict(validated["source_surface"])
    return {
        "contract": "GOLD_CONTROL_CURRENT_RUNTIME_SOURCE_V142",
        "status": "CURRENT_RUNTIME_HEALTH_PASS",
        "source_mode": SNAPSHOT_SOURCE_MODE,
        "snapshot_contract": SNAPSHOT_CONTRACT,
        "snapshot_source_state_at": validated.get("source_state_at"),
        "snapshot_payload_sha256": validated.get("payload_sha256"),
        "runtime": [dict(row) for row in validated["runtime"]],
        "runtime_engine_count": len(CURRENT_ENGINE_IDS),
        "health": health,
        "integrity_ok": True,
        "runtime_complete": True,
        "context_target": validated.get("target_context"),
        "context_feature_count": len(CURRENT_CONTEXT_FEATURES),
        "current_source_count": int(source_surface.get("current_source_count") or 0),
        "disallowed_current_source_count": int(source_surface.get("disallowed_current_source_count") or 0),
        "database_writes": "NONE",
    }
