from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tomllib
from datetime import date
from pathlib import Path
from typing import Any, Mapping

import psycopg

from decision_store import PersistResult, persist_decision
from decision_store_reader import read_latest_decision
from r4_1_decision_adapter import build_decision_payload


ROOT = Path(__file__).resolve().parent
GOLD_ROOT = ROOT.parent
R4_ROOT = GOLD_ROOT / "r4_1"
R4_CONFIG = R4_ROOT / "config" / "frozen_r4_1.json"
R4_PYPROJECT = R4_ROOT / "pyproject.toml"

REQUIRED_STATE_FIELDS = {
    "date",
    "close",
    "target_month",
    "vw_forecast_frozen",
    "monthly_direction_3m",
    "level_emergency",
    "reversal_emergency",
    "fast_state",
    "slow_state",
    "classification",
}
OPTIONAL_STATE_FIELDS = {
    "gvz",
    "gvz_cap",
    "gvz_panic",
    "macro_event_down",
    "bocpd_context",
    "default_execution_session",
}
ALLOWED_STATE_FIELDS = REQUIRED_STATE_FIELDS | OPTIONAL_STATE_FIELDS
FORBIDDEN_ACTION_FIELDS = {
    "action",
    "action_state",
    "position",
    "pos",
    "exposure",
    "target_exposure",
    "trade",
}


class BridgeContractError(ValueError):
    pass


def _parse_state_date(value: Any) -> date:
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise BridgeContractError(f"Invalid emitted state date: {value!r}") from exc


def _parse_target_month(value: Any) -> date:
    text = str(value).strip()
    if len(text) == 7:
        text = f"{text}-01"
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise BridgeContractError(f"Invalid target_month: {value!r}") from exc
    if parsed.day != 1:
        raise BridgeContractError("target_month must resolve to the first calendar day")
    return parsed


def validate_emitted_state(state: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(state, Mapping):
        raise BridgeContractError("R4.1 emitted state must be a JSON object / mapping")

    keys = {str(k) for k in state.keys()}
    forbidden = sorted(keys & FORBIDDEN_ACTION_FIELDS)
    if forbidden:
        raise BridgeContractError(
            "NOT_PROVEN_POSITION_MAPPING: emitted state contains forbidden action/exposure fields: "
            + ", ".join(forbidden)
        )

    missing = sorted(REQUIRED_STATE_FIELDS - keys)
    if missing:
        raise BridgeContractError("Missing required emitted-state fields: " + ", ".join(missing))

    unknown = sorted(keys - ALLOWED_STATE_FIELDS)
    if unknown:
        raise BridgeContractError(
            "UNREVIEWED_EMITTED_STATE_FIELDS: contract update required before persistence: "
            + ", ".join(unknown)
        )

    normalized = dict(state)
    _parse_state_date(normalized["date"])
    _parse_target_month(normalized["target_month"])
    return normalized


def frozen_engine_identity() -> tuple[str, str, str]:
    config_bytes = R4_CONFIG.read_bytes()
    config = json.loads(config_bytes.decode("utf-8"))
    config_version = str(config["version"])
    config_hash = hashlib.sha256(config_bytes).hexdigest()

    project = tomllib.loads(R4_PYPROJECT.read_text(encoding="utf-8"))["project"]
    engine_version = f"{project['name']}@{project['version']}"
    return engine_version, config_version, config_hash


def build_bridge_payload(
    emitted_state: Mapping[str, Any],
    *,
    decision_as_of: str,
    generated_at: str,
    evidence_class: str,
    trigger_type: str,
    close_source_ref: str,
    quality_status: str,
    code_sha: str | None,
    input_snapshot_ref: str | None,
    forecast_contract_ref: str | None,
    run_notes: str | None = None,
) -> dict[str, Any]:
    state = validate_emitted_state(emitted_state)
    engine_version, config_version, config_hash = frozen_engine_identity()

    return build_decision_payload(
        state,
        decision_as_of=decision_as_of,
        generated_at=generated_at,
        engine_version=engine_version,
        config_version=config_version,
        config_hash=config_hash,
        code_sha=code_sha,
        trigger_type=trigger_type,
        evidence_class=evidence_class,
        input_snapshot_ref=input_snapshot_ref,
        forecast_contract_ref=forecast_contract_ref,
        close_source_ref=close_source_ref,
        quality_status=quality_status,
        run_notes=run_notes,
        run_metadata={
            "bridge_contract": "GOLD_CONTROL_R4_1_EMITTED_STATE_CONTRACT",
            "emitted_state_date": str(state["date"]),
            "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
        },
        snapshot_metadata={"emitter_contract": "R4_1_DESCRIPTIVE_STATE_ONLY"},
        event_metadata={"action_mapping": "NOT_PROVEN_POSITION_MAPPING"},
    )


def persist_bridge_payload(conn, payload: Mapping[str, Any]) -> PersistResult:
    result = persist_decision(conn, payload)
    evidence_class = str(payload["run"]["evidence_class"])
    stored = read_latest_decision(conn, evidence_class)
    if stored is None:
        raise RuntimeError("DECISION_STORE_READER_RETURNED_NONE_AFTER_PERSIST")
    if stored.get("run_id") != result.run_id:
        raise RuntimeError(
            "PERSISTED_STATE_NOT_LATEST_FOR_EVIDENCE_CLASS: refuse ambiguous bridge verification"
        )
    if stored.get("action_state") is not None:
        raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")
    expected_classification = payload.get("snapshot", {}).get("classification")
    if stored.get("classification") != expected_classification:
        raise RuntimeError("BRIDGE_CLASSIFICATION_ROUNDTRIP_MISMATCH")
    return result


def _load_state(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise BridgeContractError("State JSON must contain one object")
    return obj


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _require_write_gate(evidence_class: str) -> None:
    if os.environ.get("GOLD_CONTROL_DECISION_WRITES_ENABLED") != "1":
        raise RuntimeError("PRODUCTION_DECISION_WRITES_DISABLED")
    if evidence_class == "LIVE_PRODUCTION" and os.environ.get("GOLD_CONTROL_LIVE_PRODUCTION_ENABLED") != "1":
        raise RuntimeError("LIVE_PRODUCTION_DISABLED_PENDING_PRODUCTION_GRADUATION")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Persist an already-emitted R4.1 descriptive state without recomputing signals"
    )
    parser.add_argument("--state-json", required=True, type=Path)
    parser.add_argument("--decision-as-of", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--evidence-class", required=True, choices=["HISTORICAL_REPLAY", "PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"])
    parser.add_argument("--trigger-type", required=True)
    parser.add_argument("--close-source-ref", required=True)
    parser.add_argument("--quality-status", required=True)
    parser.add_argument("--code-sha", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("--input-snapshot-ref")
    parser.add_argument("--forecast-contract-ref")
    parser.add_argument("--run-notes")
    parser.add_argument("--mode", choices=["dry-run", "rollback-smoke", "commit"], default="dry-run")
    args = parser.parse_args()

    try:
        state = _load_state(args.state_json)
        payload = build_bridge_payload(
            state,
            decision_as_of=args.decision_as_of,
            generated_at=args.generated_at,
            evidence_class=args.evidence_class,
            trigger_type=args.trigger_type,
            close_source_ref=args.close_source_ref,
            quality_status=args.quality_status,
            code_sha=args.code_sha,
            input_snapshot_ref=args.input_snapshot_ref,
            forecast_contract_ref=args.forecast_contract_ref,
            run_notes=args.run_notes,
        )

        if args.mode == "dry-run":
            print(
                "R4_1_DECISION_BRIDGE_DRY_RUN_PASS "
                f"evidence_class={args.evidence_class} classification={payload['snapshot']['classification']} "
                "persistent_write=NO action_mapping=NOT_PROVEN_POSITION_MAPPING"
            )
            return 0

        if args.mode == "commit":
            _require_write_gate(args.evidence_class)

        with psycopg.connect(_db_url(), autocommit=False) as conn:
            result = persist_bridge_payload(conn, payload)
            if args.mode == "rollback-smoke":
                conn.rollback()
                print(
                    "R4_1_DECISION_BRIDGE_ROLLBACK_PASS "
                    f"evidence_class={args.evidence_class} run_id={result.run_id} "
                    "persistent_write=NO action_mapping=NOT_PROVEN_POSITION_MAPPING"
                )
                return 0

            conn.commit()
            print(
                "R4_1_DECISION_BRIDGE_COMMIT_PASS "
                f"evidence_class={args.evidence_class} run_id={result.run_id} "
                "persistent_write=YES action_mapping=NOT_PROVEN_POSITION_MAPPING"
            )
            return 0
    except Exception as exc:
        print(f"R4_1_DECISION_BRIDGE_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
