from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from psycopg.rows import dict_row


SPINE_CONTRACT = "FROZEN_DATA_EVIDENCE_SPINE_V1"
SCHEMA_REQUIRED_OBJECTS = (
    "forecast_input_sets",
    "forecast_input_set_members",
    "engine_execution_runs",
    "engine_execution_derived_outputs",
    "engine_execution_expert_outputs",
    "engine_execution_decision_outputs",
)
ENGINE_IDS = (
    "CAUSAL_PATCH",
    "VW_MIDAS_MSVR",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "MACRO_EVENT",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "BOCPD",
    "GVZ_RISK",
)
RUNTIME_STATUSES = frozenset({"ACTIVE", "ISSUED", "WAITING", "BLOCKED", "NOT_PROVEN"})
RUNTIME_EVIDENCE_CLASSES = frozenset(
    {
        "RUNTIME_GOVERNANCE_AUDIT",
        "HISTORICAL_REPLAY",
        "LATE_BOOTSTRAP_SHADOW_CONTEXT",
        "PROSPECTIVE_SHADOW",
        "LIVE_PRODUCTION",
    }
)


@dataclass(frozen=True)
class ForecastInputSetSpec:
    target_month: str
    forecast_origin: datetime
    as_of: datetime
    forecast_track: str
    expert_id: str
    model_name: str
    model_version: str
    evidence_class: str
    input_fingerprint: str
    git_commit: str | None
    metadata: dict[str, Any]

    def validate(self) -> None:
        if self.forecast_origin.tzinfo is None or self.as_of.tzinfo is None:
            raise ValueError("INPUT_SET_TIMEZONE_AWARE_TIMESTAMPS_REQUIRED")
        if self.as_of < self.forecast_origin:
            raise ValueError("INPUT_SET_AS_OF_BEFORE_ORIGIN")
        if self.forecast_track == "MONTH_END_EXPERT" and self.as_of != self.forecast_origin:
            raise ValueError("MONTH_END_INPUT_SET_AS_OF_MUST_EQUAL_ORIGIN")
        if self.forecast_track not in {"MONTH_END_EXPERT", "EARLY_INDICATIVE"}:
            raise ValueError("INVALID_INPUT_SET_FORECAST_TRACK")
        if self.expert_id not in {"CAUSAL_PATCH", "VW_MIDAS_MSVR", "MOMENTUM_3M", "RANDOM_WALK"}:
            raise ValueError("INVALID_INPUT_SET_EXPERT")
        if self.evidence_class not in {"PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}:
            raise ValueError("INVALID_INPUT_SET_EVIDENCE_CLASS")
        if not self.input_fingerprint:
            raise ValueError("INPUT_SET_FINGERPRINT_REQUIRED")


def spine_schema_ready(cur) -> bool:
    for name in SCHEMA_REQUIRED_OBJECTS:
        cur.execute("select to_regclass(%s) as reg", (f"public.{name}",))
        row = cur.fetchone()
        if not row or row["reg"] is None:
            return False
    return True


def create_forecast_input_set(cur, spec: ForecastInputSetSpec) -> str:
    spec.validate()
    if not spine_schema_ready(cur):
        raise RuntimeError("BLOCKED_DATA_EVIDENCE_SPINE_SCHEMA_NOT_APPLIED")
    target = spec.target_month + "-01" if len(spec.target_month) == 7 else spec.target_month
    cur.execute(
        """
        select input_set_id,input_fingerprint
        from forecast_input_sets
        where target_month=%s and forecast_track=%s and as_of=%s
          and expert_id=%s and model_version=%s
        """,
        (target, spec.forecast_track, spec.as_of, spec.expert_id, spec.model_version),
    )
    existing = cur.fetchone()
    if existing:
        if existing["input_fingerprint"] != spec.input_fingerprint:
            raise RuntimeError("BLOCKED_CONFLICTING_EXISTING_INPUT_SET")
        return str(existing["input_set_id"])

    input_set_id = str(uuid.uuid4())
    cur.execute(
        """
        insert into forecast_input_sets
          (input_set_id,target_month,forecast_origin,as_of,forecast_track,expert_id,
           model_name,model_version,evidence_class,input_fingerprint,git_commit,metadata)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        """,
        (
            input_set_id,
            target,
            spec.forecast_origin,
            spec.as_of,
            spec.forecast_track,
            spec.expert_id,
            spec.model_name,
            spec.model_version,
            spec.evidence_class,
            spec.input_fingerprint,
            spec.git_commit,
            json.dumps(spec.metadata, sort_keys=True),
        ),
    )
    return input_set_id


def input_set_snapshot_ids(cur, input_set_id: str) -> tuple[int, ...]:
    cur.execute(
        """
        select snapshot_id from forecast_input_set_members
        where input_set_id=%s order by snapshot_id
        """,
        (input_set_id,),
    )
    return tuple(int(r["snapshot_id"]) for r in cur.fetchall())


def verify_input_set(cur, input_set_id: str, expected_fingerprint: str, expected_snapshot_ids: Iterable[int]) -> None:
    cur.execute(
        "select input_fingerprint from forecast_input_sets where input_set_id=%s",
        (input_set_id,),
    )
    row = cur.fetchone()
    if not row:
        raise RuntimeError("INPUT_SET_POST_WRITE_MISSING")
    if row["input_fingerprint"] != expected_fingerprint:
        raise RuntimeError("INPUT_SET_POST_WRITE_FINGERPRINT_MISMATCH")
    actual = input_set_snapshot_ids(cur, input_set_id)
    expected = tuple(sorted(set(int(x) for x in expected_snapshot_ids)))
    if actual != expected:
        raise RuntimeError(f"INPUT_SET_POST_WRITE_MEMBERSHIP_MISMATCH:{actual}:{expected}")


def record_engine_execution(
    cur,
    *,
    engine_id: str,
    engine_version: str,
    engine_role: str,
    as_of: datetime,
    target_context: str | None,
    evidence_class: str,
    runtime_status: str,
    status_code: str,
    direction_vote_permitted: bool,
    git_commit: str | None,
    input_fingerprint: str | None = None,
    metadata: dict[str, Any] | None = None,
    derived_feature_snapshot_ids: Iterable[int] = (),
    monthly_expert_forecast_ids: Iterable[int] = (),
    decision_snapshot_ids: Iterable[str] = (),
) -> str:
    if engine_id not in ENGINE_IDS:
        raise ValueError(f"UNKNOWN_ENGINE_ID:{engine_id}")
    if runtime_status not in RUNTIME_STATUSES:
        raise ValueError(f"INVALID_RUNTIME_STATUS:{runtime_status}")
    if evidence_class not in RUNTIME_EVIDENCE_CLASSES:
        raise ValueError(f"INVALID_RUNTIME_EVIDENCE_CLASS:{evidence_class}")
    if as_of.tzinfo is None:
        raise ValueError("RUNTIME_AS_OF_MUST_BE_TIMEZONE_AWARE")
    if not status_code:
        raise ValueError("RUNTIME_STATUS_CODE_REQUIRED")
    if not spine_schema_ready(cur):
        raise RuntimeError("BLOCKED_DATA_EVIDENCE_SPINE_SCHEMA_NOT_APPLIED")

    cur.execute(
        """
        select run_id from engine_execution_runs
        where engine_id=%s and engine_version=%s and as_of=%s
          and coalesce(target_context,'')=coalesce(%s,'')
          and evidence_class=%s and status_code=%s
        """,
        (engine_id, engine_version, as_of, target_context, evidence_class, status_code),
    )
    existing = cur.fetchone()
    if existing:
        return str(existing["run_id"])

    run_id = str(uuid.uuid4())
    cur.execute(
        """
        insert into engine_execution_runs
          (run_id,engine_id,engine_version,engine_role,as_of,target_context,evidence_class,
           runtime_status,status_code,direction_vote_permitted,git_commit,input_fingerprint,metadata)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        """,
        (
            run_id,
            engine_id,
            engine_version,
            engine_role,
            as_of,
            target_context,
            evidence_class,
            runtime_status,
            status_code,
            direction_vote_permitted,
            git_commit,
            input_fingerprint,
            json.dumps(metadata or {}, sort_keys=True),
        ),
    )

    for snapshot_id in sorted(set(int(x) for x in derived_feature_snapshot_ids)):
        cur.execute(
            "insert into engine_execution_derived_outputs(run_id,derived_feature_snapshot_id) values (%s,%s)",
            (run_id, snapshot_id),
        )
    for forecast_id in sorted(set(int(x) for x in monthly_expert_forecast_ids)):
        cur.execute(
            "insert into engine_execution_expert_outputs(run_id,monthly_expert_forecast_id) values (%s,%s)",
            (run_id, forecast_id),
        )
    for decision_id in sorted(set(str(x) for x in decision_snapshot_ids)):
        cur.execute(
            "insert into engine_execution_decision_outputs(run_id,decision_snapshot_id) values (%s,%s)",
            (run_id, decision_id),
        )
    return run_id
