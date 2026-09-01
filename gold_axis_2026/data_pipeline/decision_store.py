from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Mapping


EVIDENCE_CLASSES = {"HISTORICAL_REPLAY", "PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}
CLASSIFICATIONS = {
    "MACRO_DOWN_RISK",
    "REVERSAL_RISK_DOWN",
    "REVERSAL_RISK_UP",
    "ALIGNED_UP",
    "ALIGNED_DOWN",
    "CONFLICT",
    "UNRESOLVED_MIXED",
}
REASON_CODES = {
    "MACRO_EVENT_DOWN_TRUE",
    "REVERSAL_DOWN_ALERT_ACTIVE",
    "REVERSAL_UP_ALERT_ACTIVE",
    "LEVEL_FAST_SLOW_ALIGNED_UP",
    "LEVEL_FAST_SLOW_ALIGNED_DOWN",
    "MONTHLY_VS_TACTICAL_CONFLICT",
    "NO_DECISIVE_ALIGNMENT",
}
DIRECTIONS = {"UP", "DOWN", "NEUTRAL"}
FAST_STATES = {"ROBUST_UP", "ROBUST_DOWN", "MIXED", "INSUFFICIENT_DATA"}
SLOW_STATES = {"ROBUST_UP", "ROBUST_DOWN", "NOT_YET_ROBUST", "INSUFFICIENT_DATA"}
REVERSAL_STATES = {"UP_ALERT", "DOWN_ALERT", "OFF"}

_NAMESPACE = uuid.UUID("7702b357-1774-4ee8-b8c2-35dfd829ab69")


def _canonical_scalar(value: Any) -> Any:
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            raise ValueError("datetime values must be timezone-aware")
        return dt.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): _canonical_scalar(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_scalar(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported fingerprint value: {type(value).__name__}")


def fingerprint(namespace: str, payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        {"namespace": namespace, "payload": _canonical_scalar(payload)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def deterministic_uuid(kind: str, fp: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, f"{kind}:{fp}")


def _required(payload: Mapping[str, Any], key: str) -> Any:
    if key not in payload or payload[key] is None or payload[key] == "":
        raise ValueError(f"Missing required decision field: {key}")
    return payload[key]


def _parse_dt(value: Any, name: str) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"{name} must be timezone-aware")
    return dt.astimezone(timezone.utc)


def _parse_month(value: Any) -> date:
    if isinstance(value, datetime):
        d = value.date()
    elif isinstance(value, date):
        d = value
    else:
        text = str(value)
        d = date.fromisoformat(text + "-01" if len(text) == 7 else text)
    if d.day != 1:
        raise ValueError("target_month must be the first calendar day of the target month")
    return d


def _parse_optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _enum(value: Any, allowed: set[str], name: str) -> str:
    text = str(value)
    if text not in allowed:
        raise ValueError(f"Invalid {name}: {text!r}")
    return text


def _validate_prospective_provenance(run: Mapping[str, Any]) -> None:
    evidence = str(_required(run, "evidence_class"))
    if evidence not in {"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}:
        return
    for key in ("code_sha", "input_snapshot_ref", "forecast_contract_ref"):
        _required(run, key)


def normalize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    run = dict(_required(payload, "run"))
    snapshot = dict(payload.get("snapshot") or {})
    event = dict(payload.get("event") or {})

    run["decision_as_of"] = _parse_dt(_required(run, "decision_as_of"), "decision_as_of")
    run["generated_at"] = _parse_dt(_required(run, "generated_at"), "generated_at")
    run["evidence_class"] = _enum(_required(run, "evidence_class"), EVIDENCE_CLASSES, "evidence_class")
    run["engine_version"] = str(_required(run, "engine_version"))
    run["config_version"] = str(_required(run, "config_version"))
    run["trigger_type"] = str(_required(run, "trigger_type"))
    run["status"] = str(_required(run, "status"))
    run["metadata"] = dict(run.get("metadata") or {})
    _validate_prospective_provenance(run)

    if run["status"] != "SUCCESS":
        if snapshot or event:
            raise ValueError("Non-SUCCESS runs may not persist an authoritative snapshot/event")
        return {"run": run, "snapshot": None, "event": None}

    snapshot["decision_as_of"] = _parse_dt(
        snapshot.get("decision_as_of", run["decision_as_of"]), "snapshot.decision_as_of"
    )
    if snapshot["decision_as_of"] != run["decision_as_of"]:
        raise ValueError("snapshot decision_as_of must equal run decision_as_of")
    snapshot["target_month"] = _parse_month(_required(snapshot, "target_month"))
    snapshot["close_value"] = float(_required(snapshot, "close_value"))
    snapshot["close_source_ref"] = str(_required(snapshot, "close_source_ref"))
    snapshot["vw_forecast_frozen"] = float(_required(snapshot, "vw_forecast_frozen"))
    snapshot["monthly_direction_3m"] = _enum(
        _required(snapshot, "monthly_direction_3m"), DIRECTIONS, "monthly_direction_3m"
    )
    snapshot["level_emergency"] = _enum(
        _required(snapshot, "level_emergency"), DIRECTIONS, "level_emergency"
    )
    snapshot["reversal_emergency"] = _enum(
        _required(snapshot, "reversal_emergency"), REVERSAL_STATES, "reversal_emergency"
    )
    snapshot["fast_state"] = _enum(_required(snapshot, "fast_state"), FAST_STATES, "fast_state")
    snapshot["slow_state"] = _enum(_required(snapshot, "slow_state"), SLOW_STATES, "slow_state")
    snapshot["classification"] = _enum(
        _required(snapshot, "classification"), CLASSIFICATIONS, "classification"
    )
    snapshot["gvz_value"] = None if snapshot.get("gvz_value") is None else float(snapshot["gvz_value"])
    snapshot["gvz_cap"] = None if snapshot.get("gvz_cap") is None else float(snapshot["gvz_cap"])
    if snapshot["gvz_cap"] is not None and not (0.0 <= snapshot["gvz_cap"] <= 1.0):
        raise ValueError("gvz_cap must be between 0 and 1")
    snapshot["gvz_panic"] = None if snapshot.get("gvz_panic") is None else bool(snapshot["gvz_panic"])
    snapshot["macro_event_down"] = (
        None if snapshot.get("macro_event_down") is None else bool(snapshot["macro_event_down"])
    )
    snapshot["bocpd_context"] = None if snapshot.get("bocpd_context") in (None, "") else str(snapshot["bocpd_context"])
    snapshot["default_execution_session"] = _parse_optional_date(snapshot.get("default_execution_session"))
    snapshot["quality_status"] = str(_required(snapshot, "quality_status"))
    snapshot["metadata"] = dict(snapshot.get("metadata") or {})

    event["event_ts"] = _parse_dt(event.get("event_ts", run["decision_as_of"]), "event.event_ts")
    event["classification"] = _enum(
        event.get("classification", snapshot["classification"]), CLASSIFICATIONS, "event.classification"
    )
    if event["classification"] != snapshot["classification"]:
        raise ValueError("event classification must equal snapshot classification")
    event["reason_code"] = _enum(_required(event, "reason_code"), REASON_CODES, "reason_code")
    if event.get("action_state") not in (None, ""):
        raise ValueError("action_state is NOT_PROVEN_POSITION_MAPPING and must be null")
    event["action_state"] = None
    event["execution_session"] = _parse_optional_date(
        event.get("execution_session", snapshot["default_execution_session"])
    )
    event["metadata"] = dict(event.get("metadata") or {})

    return {"run": run, "snapshot": snapshot, "event": event}


@dataclass(frozen=True)
class PersistResult:
    run_id: uuid.UUID
    snapshot_id: uuid.UUID | None
    event_id: uuid.UUID | None
    inserted_run: bool
    inserted_snapshot: bool
    inserted_event: bool
    classification_changed: bool | None


def _previous_classification(cur, event_ts: datetime, evidence_class: str) -> str | None:
    cur.execute(
        """
        SELECT e.classification
        FROM decision_events e
        JOIN decision_runs r ON r.run_id = e.run_id
        WHERE e.event_ts < %s
          AND r.evidence_class = %s
          AND r.status = 'SUCCESS'
        ORDER BY e.event_ts DESC, e.created_at DESC, e.event_id DESC
        LIMIT 1
        """,
        (event_ts, evidence_class),
    )
    row = cur.fetchone()
    return None if row is None else row[0]


def persist_decision(conn, payload: Mapping[str, Any]) -> PersistResult:
    """Persist one immutable decision run/snapshot/event.

    This function does not recompute R4.1 signal logic or infer a trading action.
    The caller must supply the already-issued descriptive classification and its
    deterministic reason code. Identical payloads are idempotent by fingerprint.
    """
    normalized = normalize_payload(payload)
    run = normalized["run"]
    snapshot = normalized["snapshot"]
    event = normalized["event"]

    run_fp_payload = {
        key: run.get(key)
        for key in (
            "decision_as_of", "generated_at", "engine_version", "config_version",
            "config_hash", "code_sha", "trigger_type", "evidence_class", "status",
            "input_snapshot_ref", "forecast_contract_ref",
        )
    }
    run_fp = fingerprint("decision_run_v1", run_fp_payload)
    run_id = deterministic_uuid("run", run_fp)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO decision_runs (
                run_id, decision_as_of, generated_at, engine_version, config_version,
                config_hash, code_sha, trigger_type, evidence_class, status,
                input_snapshot_ref, forecast_contract_ref, fingerprint, notes, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (fingerprint) DO NOTHING
            RETURNING run_id
            """,
            (
                run_id, run["decision_as_of"], run["generated_at"], run["engine_version"],
                run["config_version"], run.get("config_hash"), run.get("code_sha"),
                run["trigger_type"], run["evidence_class"], run["status"],
                run.get("input_snapshot_ref"), run.get("forecast_contract_ref"), run_fp,
                run.get("notes"), json.dumps(run["metadata"], ensure_ascii=False),
            ),
        )
        inserted_run = cur.fetchone() is not None

        cur.execute("SELECT run_id FROM decision_runs WHERE fingerprint=%s", (run_fp,))
        stored_run_id = cur.fetchone()[0]
        if stored_run_id != run_id:
            raise RuntimeError("Decision run fingerprint resolved to an unexpected ID")

        if snapshot is None:
            return PersistResult(run_id, None, None, inserted_run, False, False, None)

        snapshot_fp_payload = {
            "run_id": run_id,
            **{
                key: snapshot.get(key)
                for key in (
                    "decision_as_of", "target_month", "close_value", "close_source_ref",
                    "vw_forecast_frozen", "forecast_contract_ref", "monthly_direction_3m",
                    "level_emergency", "reversal_emergency", "fast_state", "slow_state",
                    "gvz_value", "gvz_cap", "gvz_panic", "macro_event_down", "bocpd_context",
                    "classification", "default_execution_session", "quality_status",
                )
            },
        }
        snapshot_fp = fingerprint("decision_snapshot_v1", snapshot_fp_payload)
        snapshot_id = deterministic_uuid("snapshot", snapshot_fp)

        cur.execute(
            """
            INSERT INTO decision_signal_snapshots (
                snapshot_id, run_id, decision_as_of, target_month, close_value,
                close_source_ref, vw_forecast_frozen, forecast_contract_ref,
                monthly_direction_3m, level_emergency, reversal_emergency, fast_state,
                slow_state, gvz_value, gvz_cap, gvz_panic, macro_event_down,
                bocpd_context, classification, default_execution_session,
                quality_status, fingerprint, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (fingerprint) DO NOTHING
            RETURNING snapshot_id
            """,
            (
                snapshot_id, run_id, snapshot["decision_as_of"], snapshot["target_month"],
                snapshot["close_value"], snapshot["close_source_ref"],
                snapshot["vw_forecast_frozen"], snapshot.get("forecast_contract_ref"),
                snapshot["monthly_direction_3m"], snapshot["level_emergency"],
                snapshot["reversal_emergency"], snapshot["fast_state"], snapshot["slow_state"],
                snapshot["gvz_value"], snapshot["gvz_cap"], snapshot["gvz_panic"],
                snapshot["macro_event_down"], snapshot["bocpd_context"], snapshot["classification"],
                snapshot["default_execution_session"], snapshot["quality_status"], snapshot_fp,
                json.dumps(snapshot["metadata"], ensure_ascii=False),
            ),
        )
        inserted_snapshot = cur.fetchone() is not None
        cur.execute("SELECT snapshot_id FROM decision_signal_snapshots WHERE fingerprint=%s", (snapshot_fp,))
        stored_snapshot_id = cur.fetchone()[0]
        if stored_snapshot_id != snapshot_id:
            raise RuntimeError("Decision snapshot fingerprint resolved to an unexpected ID")

        previous = _previous_classification(cur, event["event_ts"], run["evidence_class"])
        changed = previous != event["classification"]
        event_fp_payload = {
            "run_id": run_id,
            "snapshot_id": snapshot_id,
            "event_ts": event["event_ts"],
            "previous_classification": previous,
            "classification": event["classification"],
            "classification_changed": changed,
            "reason_code": event["reason_code"],
            "action_state": None,
            "execution_session": event["execution_session"],
        }
        event_fp = fingerprint("decision_event_v1", event_fp_payload)
        event_id = deterministic_uuid("event", event_fp)

        cur.execute(
            """
            INSERT INTO decision_events (
                event_id, run_id, snapshot_id, event_ts, previous_classification,
                classification, classification_changed, reason_code, action_state,
                execution_session, fingerprint, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, %s)
            ON CONFLICT (fingerprint) DO NOTHING
            RETURNING event_id
            """,
            (
                event_id, run_id, snapshot_id, event["event_ts"], previous,
                event["classification"], changed, event["reason_code"],
                event["execution_session"], event_fp,
                json.dumps(event["metadata"], ensure_ascii=False),
            ),
        )
        inserted_event = cur.fetchone() is not None
        cur.execute("SELECT event_id FROM decision_events WHERE fingerprint=%s", (event_fp,))
        stored_event_id = cur.fetchone()[0]
        if stored_event_id != event_id:
            raise RuntimeError("Decision event fingerprint resolved to an unexpected ID")

    return PersistResult(
        run_id=run_id,
        snapshot_id=snapshot_id,
        event_id=event_id,
        inserted_run=inserted_run,
        inserted_snapshot=inserted_snapshot,
        inserted_event=inserted_event,
        classification_changed=changed,
    )
