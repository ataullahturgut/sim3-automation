from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


SNAPSHOT_CONTRACT = "FROZEN_AUG31_REPLAY_EXPANSION_V2_DISPLAY_SNAPSHOT_V1"
SNAPSHOT_PATH = Path(__file__).with_name("aug31_replay_expansion_snapshot.json")
REPLAY_CONTRACT = "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md"
TARGET_CONTEXT = "2026-09"
STATE_AS_OF = "2026-08-31T21:00:00+00:00"
EVIDENCE_CLASS = "HISTORICAL_REPLAY"
SOURCE_DB = "NEON_DB_READ_ONLY"
SOURCE_SNAPSHOT = "PRODUCTION_SNAPSHOT_FALLBACK"
ARTIFACT_DIGEST = "sha256:f90a38ba6239931b272a5cff9f631f9bc9bb3c04dbc5ff10ffbf5f4fc4bb9b20"
PATCH_FINGERPRINT = "029d71f693775159c120f9782c1bf3e91888ad04fe06b88b4322bced400c5554"
BOCPD_FINGERPRINT = "9ad26a95f2b064e6ceb89e722bd8f6f889d19df7b7e261af7b9c14ac7f79c658"
FEATURE_NAMES = (
    "AUG31_REPLAY_CAUSAL_PATCH_SEPTEMBER_FORECAST",
    "AUG31_REPLAY_CAUSAL_PATCH_PREDICTED_LOG_RETURN",
    "AUG31_REPLAY_EMERGENCY_LEVEL",
    "AUG31_REPLAY_EMERGENCY_REVERSAL",
    "AUG31_REPLAY_BOCPD_SUCCESSOR_STATE",
    "AUG31_REPLAY_BOCPD_SUCCESSOR_RESET_FRACTION",
)


def _payload_hash(snapshot: dict[str, Any]) -> str:
    payload = dict(snapshot)
    payload.pop("payload_sha256", None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _iso(value: Any) -> str:
    """Normalize DB datetime objects and ISO strings to the frozen UTC text form."""
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        text = str(value.isoformat())
    else:
        text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if "T" not in text and " " in text:
        text = text.replace(" ", "T", 1)
    return text


def _validate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(rows) != len(FEATURE_NAMES):
        raise RuntimeError(f"AUG31_REPLAY_EXPANSION_ROW_COUNT:{len(rows)}")
    names = [str(row.get("feature_name") or "") for row in rows]
    if set(names) != set(FEATURE_NAMES) or len(names) != len(set(names)):
        raise RuntimeError(f"AUG31_REPLAY_EXPANSION_IDENTITIES_INVALID:{names}")

    for row in rows:
        name = str(row.get("feature_name") or "")
        meta = dict(row.get("metadata") or {})
        lineage = dict(row.get("input_lineage") or {})
        if row.get("quality_status") != EVIDENCE_CLASS:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_QUALITY_INVALID:{name}")
        if _iso(row.get("input_cutoff")) != STATE_AS_OF:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_INPUT_CUTOFF_INVALID:{name}")
        if meta.get("contract") != REPLAY_CONTRACT:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_CONTRACT_INVALID:{name}")
        if meta.get("target_context") != TARGET_CONTEXT or _iso(meta.get("state_as_of")) != STATE_AS_OF:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_SCOPE_INVALID:{name}")
        if meta.get("historical_replay") is not True or meta.get("prospective_claim") is not False:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_EVIDENCE_INVALID:{name}")
        if meta.get("current_runtime_authority") is not False or meta.get("canonical_authority") is not False:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_AUTHORITY_VIOLATION:{name}")
        if meta.get("direction_vote_permitted") is not False:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_DIRECTION_VOTE_VIOLATION:{name}")
        if meta.get("auto_selector") != "OFF" or meta.get("auto_ensemble") != "OFF":
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_SELECTOR_VIOLATION:{name}")
        if meta.get("artifact_digest") != ARTIFACT_DIGEST:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_ARTIFACT_DIGEST_INVALID:{name}")
        expected_fp = BOCPD_FINGERPRINT if "BOCPD" in name else PATCH_FINGERPRINT
        if lineage.get("input_fingerprint") != expected_fp:
            raise RuntimeError(f"AUG31_REPLAY_EXPANSION_FINGERPRINT_INVALID:{name}")

    return rows


def _shape(
    rows: list[dict[str, Any]],
    *,
    source_mode: str,
    snapshot_sha256: str | None = None,
    source_state_at: str | None = None,
) -> dict[str, Any]:
    validated = _validate_rows(rows)
    by_name = {str(row["feature_name"]): row for row in validated}

    patch = by_name["AUG31_REPLAY_CAUSAL_PATCH_SEPTEMBER_FORECAST"]
    patch_ret = by_name["AUG31_REPLAY_CAUSAL_PATCH_PREDICTED_LOG_RETURN"]
    level = by_name["AUG31_REPLAY_EMERGENCY_LEVEL"]
    reversal = by_name["AUG31_REPLAY_EMERGENCY_REVERSAL"]
    bocpd = by_name["AUG31_REPLAY_BOCPD_SUCCESSOR_STATE"]
    bocpd_reset = by_name["AUG31_REPLAY_BOCPD_SUCCESSOR_RESET_FRACTION"]

    patch_value = float(patch["value_num"])
    predicted_log_return = float(patch_ret["value_num"])
    emergency_level = str(level.get("value_text") or "")
    emergency_reversal = str(reversal.get("value_text") or "")
    bocpd_state = str(bocpd.get("value_text") or "")
    bocpd_reset_fraction = float(bocpd_reset["value_num"])

    if patch_value <= 0:
        raise RuntimeError("AUG31_REPLAY_EXPANSION_PATCH_VALUE_INVALID")
    if emergency_level != "NEUTRAL" or emergency_reversal != "OFF":
        raise RuntimeError("AUG31_REPLAY_EXPANSION_EMERGENCY_STATE_INVALID")
    if bocpd_state != "NO_ADVERSE_BREAK_CANDIDATE":
        raise RuntimeError("AUG31_REPLAY_EXPANSION_BOCPD_STATE_INVALID")
    if abs(bocpd_reset_fraction) > 1e-15:
        raise RuntimeError("AUG31_REPLAY_EXPANSION_BOCPD_RESET_INVALID")

    level_meta = dict(level.get("metadata") or {})
    bocpd_meta = dict(bocpd.get("metadata") or {})
    reset_meta = dict(bocpd_reset.get("metadata") or {})
    patch_meta = dict(patch.get("metadata") or {})
    patch_lineage = dict(patch.get("input_lineage") or {})
    bocpd_lineage = dict(bocpd.get("input_lineage") or {})

    return {
        "contract": REPLAY_CONTRACT,
        "snapshot_contract": SNAPSHOT_CONTRACT if source_mode == SOURCE_SNAPSHOT else None,
        "source_mode": source_mode,
        "source_state_at": source_state_at,
        "snapshot_payload_sha256": snapshot_sha256,
        "target_context": TARGET_CONTEXT,
        "state_as_of": STATE_AS_OF,
        "evidence_class": EVIDENCE_CLASS,
        "historical_replay": True,
        "prospective_claim": False,
        "prospective_h1_claim": False,
        "current_runtime_authority": False,
        "canonical_authority": False,
        "direction_vote_permitted": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "artifact_digest": ARTIFACT_DIGEST,
        "causal_patch_forecast": patch_value,
        "causal_patch_predicted_log_return": predicted_log_return,
        "causal_patch_version": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "causal_patch_forecast_origin": patch_meta.get("forecast_origin") or STATE_AS_OF,
        "causal_patch_daily_max_date": patch_lineage.get("daily_max_date"),
        "emergency_level": emergency_level,
        "emergency_reversal": emergency_reversal,
        "emergency_reason": level_meta.get("reason"),
        "emergency_monthly_reference": level_meta.get("monthly_reference"),
        "bocpd_successor_state": bocpd_state,
        "bocpd_successor_reset_fraction": bocpd_reset_fraction,
        "bocpd_successor_id": bocpd_meta.get("successor_id"),
        "bocpd_context_identity": bocpd_meta.get("context_identity"),
        "bocpd_archived_engine_status": bocpd_meta.get("archived_engine_status"),
        "bocpd_map_reset": reset_meta.get("map_reset"),
        "bocpd_map_run": reset_meta.get("map_run"),
        "bocpd_previous_map_run": reset_meta.get("previous_map_run"),
        "bocpd_expected_run_length": reset_meta.get("expected_run_length"),
        "bocpd_log_return": reset_meta.get("log_return"),
        "bocpd_source_series": bocpd_lineage.get("source_series"),
        "retrieved_post_origin": True,
        "database_writes": "NONE",
    }


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or snapshot.get("snapshot_contract") != SNAPSHOT_CONTRACT:
        raise RuntimeError("AUG31_REPLAY_EXPANSION_SNAPSHOT_CONTRACT_INVALID")
    if snapshot.get("database_writes") != "NONE":
        raise RuntimeError("AUG31_REPLAY_EXPANSION_SNAPSHOT_WRITE_CLAIM_INVALID")
    if snapshot.get("target_context") != TARGET_CONTEXT or _iso(snapshot.get("state_as_of")) != STATE_AS_OF:
        raise RuntimeError("AUG31_REPLAY_EXPANSION_SNAPSHOT_SCOPE_INVALID")
    if snapshot.get("artifact_digest") != ARTIFACT_DIGEST:
        raise RuntimeError("AUG31_REPLAY_EXPANSION_SNAPSHOT_ARTIFACT_INVALID")
    expected = str(snapshot.get("payload_sha256") or "").strip().lower()
    if not expected or expected != _payload_hash(snapshot):
        raise RuntimeError("AUG31_REPLAY_EXPANSION_SNAPSHOT_FINGERPRINT_INVALID")
    _validate_rows([dict(row) for row in snapshot.get("features") or []])
    return snapshot


def load_snapshot(path: Path | str | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else SNAPSHOT_PATH
    if not target.is_file():
        raise RuntimeError(f"AUG31_REPLAY_EXPANSION_SNAPSHOT_NOT_FOUND:{target}")
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError("AUG31_REPLAY_EXPANSION_SNAPSHOT_JSON_INVALID") from exc
    return validate_snapshot(data)


def _db_rows(url: str) -> list[dict[str, Any]]:
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT feature_name,feature_version,calculation_ts,input_cutoff,value_num,value_text,
                       git_commit,quality_status,metadata,input_lineage
                FROM derived_feature_snapshots
                WHERE feature_name=ANY(%s)
                  AND quality_status=%s
                  AND metadata->>'contract'=%s
                  AND metadata->>'target_context'=%s
                  AND metadata->>'state_as_of'=%s
                ORDER BY feature_name,calculation_ts DESC,id DESC
                """,
                (list(FEATURE_NAMES), EVIDENCE_CLASS, REPLAY_CONTRACT, TARGET_CONTEXT, STATE_AS_OF),
            )
            rows = [dict(row) for row in cur.fetchall()]
        conn.rollback()
    return _validate_rows(rows)


def fetch_aug31_replay_expansion(database_url: str) -> dict[str, Any]:
    url = str(database_url or "").strip()
    if url:
        try:
            rows = _db_rows(url)
            source_state_at = max(_iso(row.get("calculation_ts")) for row in rows)
            return _shape(rows, source_mode=SOURCE_DB, source_state_at=source_state_at)
        except psycopg.OperationalError:
            pass

    snapshot = load_snapshot()
    return _shape(
        [dict(row) for row in snapshot["features"]],
        source_mode=SOURCE_SNAPSHOT,
        snapshot_sha256=str(snapshot.get("payload_sha256") or ""),
        source_state_at=str(snapshot.get("source_state_at") or ""),
    )
