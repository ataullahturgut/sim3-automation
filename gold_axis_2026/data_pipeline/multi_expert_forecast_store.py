from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from data_evidence_spine import (
    ForecastInputSetSpec,
    create_forecast_input_set,
    record_engine_execution,
    spine_schema_ready,
    verify_input_set,
)
from multi_expert_forecast import ExpertForecastRecord


def table_exists(cur) -> bool:
    cur.execute("select to_regclass('public.monthly_expert_forecasts') as reg")
    row = cur.fetchone()
    return bool(row and row["reg"] is not None)


def _target_date(target_month: str) -> str:
    return target_month + "-01" if len(target_month) == 7 else target_month


def _verify_snapshot_identity_and_pit(cur, record: ExpertForecastRecord) -> tuple[int, ...]:
    snapshot_ids = tuple(sorted(set(int(x) for x in record.input_snapshot_ids)))
    cur.execute(
        """
        select id,forecast_origin,target_period,model_name,model_version,
               observation_ts,available_as_of,retrieved_at,metadata
        from forecast_input_snapshots where id=any(%s)
        order by id
        """,
        (list(snapshot_ids),),
    )
    rows = [dict(r) for r in cur.fetchall()]
    if len(rows) != len(snapshot_ids):
        raise RuntimeError(
            f"BLOCKED_EXPERT_INPUT_SNAPSHOT_LINEAGE_INCOMPLETE:{len(rows)}/{len(snapshot_ids)}"
        )
    expected_target = record.target_month[:7]
    for row in rows:
        if row["forecast_origin"] != record.forecast_origin:
            raise RuntimeError("BLOCKED_EXPERT_INPUT_SNAPSHOT_FORECAST_ORIGIN_MISMATCH")
        if str(row["target_period"]) != expected_target:
            raise RuntimeError("BLOCKED_EXPERT_INPUT_SNAPSHOT_TARGET_MISMATCH")
        if row["model_name"] != record.model_name or row["model_version"] != record.model_version:
            raise RuntimeError("BLOCKED_EXPERT_INPUT_SNAPSHOT_MODEL_IDENTITY_MISMATCH")
        if row["available_as_of"] > record.as_of or row["retrieved_at"] > record.as_of:
            raise RuntimeError("BLOCKED_EXPERT_INPUT_SNAPSHOT_PIT_VIOLATION")
        if record.forecast_track == "HISTORICAL_REPLAY":
            metadata = dict(row.get("metadata") or {})
            if metadata.get("historical_replay") is not True or metadata.get("prospective_claim") is not False:
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SNAPSHOT_METADATA_INVALID")
            source_period_end_text = str(metadata.get("source_period_end") or "")
            if not source_period_end_text:
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_END_MISSING")
            try:
                source_period_end = datetime.fromisoformat(source_period_end_text.replace("Z", "+00:00"))
            except Exception as exc:
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_END_INVALID") from exc
            if source_period_end.tzinfo is None:
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_END_NAIVE")
            if source_period_end > record.forecast_origin:
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_SOURCE_PERIOD_AFTER_ORIGIN")
            if row["observation_ts"] > record.forecast_origin or row["available_as_of"] > record.forecast_origin:
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_INFORMATION_AFTER_ORIGIN")
            if str(row["target_period"]) == source_period_end.strftime("%Y-%m"):
                raise RuntimeError("BLOCKED_HISTORICAL_REPLAY_TARGET_DATA_AS_INPUT")
    return snapshot_ids


def _create_and_bind_input_set(cur, record: ExpertForecastRecord, snapshot_ids: tuple[int, ...]) -> str:
    input_set_metadata = {
        "contract": "FROZEN_DATA_EVIDENCE_SPINE_V1",
        "source": "multi_expert_forecast_store.insert_expert_forecast",
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "canonical_authority": False,
    }
    if record.forecast_track == "HISTORICAL_REPLAY":
        for key in ("historical_replay", "prospective_claim", "information_cutoff", "replay_executed_at", "official_prospective_status", "source_id"):
            if key in record.provenance:
                input_set_metadata[key] = record.provenance[key]
    input_set_id = create_forecast_input_set(
        cur,
        ForecastInputSetSpec(
            target_month=record.target_month,
            forecast_origin=record.forecast_origin,
            as_of=record.as_of,
            forecast_track=record.forecast_track,
            expert_id=record.expert_id,
            model_name=record.model_name,
            model_version=record.model_version,
            evidence_class=record.evidence_class,
            input_fingerprint=record.input_fingerprint,
            git_commit=record.git_commit,
            metadata=input_set_metadata,
        ),
    )
    for snapshot_id in snapshot_ids:
        cur.execute(
            """
            insert into forecast_input_set_members(input_set_id,snapshot_id)
            values (%s,%s)
            on conflict (snapshot_id) do nothing
            """,
            (input_set_id, snapshot_id),
        )
    verify_input_set(cur, input_set_id, record.input_fingerprint, snapshot_ids)
    return input_set_id


def insert_expert_forecast(cur, record: ExpertForecastRecord, *, verify_snapshots: bool = True) -> dict:
    """Insert one expert row into the caller's transaction.

    Data Evidence Spine V1 is mandatory. Input snapshots, normalized input set,
    expert output and runtime-engine output link become visible atomically.
    The caller owns commit/rollback.
    """
    record.validate()
    if not table_exists(cur):
        raise RuntimeError("BLOCKED_MULTI_EXPERT_LEDGER_SCHEMA_NOT_APPLIED")
    if not spine_schema_ready(cur):
        raise RuntimeError("BLOCKED_DATA_EVIDENCE_SPINE_SCHEMA_NOT_APPLIED")

    cur.execute(
        """
        select id,input_set_id from monthly_expert_forecasts
        where target_month=%s and forecast_track=%s and as_of=%s
          and expert_id=%s and model_version=%s
        """,
        (
            _target_date(record.target_month),
            record.forecast_track,
            record.as_of,
            record.expert_id,
            record.model_version,
        ),
    )
    existing = cur.fetchone()
    if existing:
        if existing.get("input_set_id") is None:
            raise RuntimeError("BLOCKED_EXISTING_EXPERT_WITHOUT_INPUT_SET")
        return {"duplicate": True, "id": int(existing["id"]), "input_set_id": str(existing["input_set_id"])}

    snapshot_ids = (
        _verify_snapshot_identity_and_pit(cur, record)
        if verify_snapshots
        else tuple(sorted(set(int(x) for x in record.input_snapshot_ids)))
    )
    input_set_id = _create_and_bind_input_set(cur, record, snapshot_ids)

    provenance = dict(record.provenance)
    provenance.update(
        {
            "canonical_authority": False,
            "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
            "data_evidence_spine_contract": "FROZEN_DATA_EVIDENCE_SPINE_V1",
            "input_set_id": input_set_id,
        }
    )
    cur.execute(
        """
        insert into monthly_expert_forecasts
          (target_month,forecast_origin,as_of,forecast_track,expert_id,
           model_name,model_version,expert_role,forecast_value,unit,
           evidence_class,git_commit,input_snapshot_ids,input_fingerprint,
           selector_status,auto_selector,auto_ensemble,canonical_authority,provenance,input_set_id)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                'NOT_PROVEN_EXPERT_SELECTION_RULE','OFF','OFF',false,%s::jsonb,%s)
        returning id
        """,
        (
            _target_date(record.target_month),
            record.forecast_origin,
            record.as_of,
            record.forecast_track,
            record.expert_id,
            record.model_name,
            record.model_version,
            record.expert_role,
            float(record.forecast_value),
            record.unit,
            record.evidence_class,
            record.git_commit,
            list(snapshot_ids),
            record.input_fingerprint,
            json.dumps(provenance, sort_keys=True),
            input_set_id,
        ),
    )
    expert_row_id = int(cur.fetchone()["id"])
    runtime_role = "MONTHLY_H1_BENCHMARK" if record.expert_role == "BENCHMARK" else "MONTHLY_H1_EXPERT"
    runtime_run_id = record_engine_execution(
        cur,
        engine_id=record.expert_id,
        engine_version=record.model_version,
        engine_role=runtime_role,
        as_of=record.as_of,
        target_context=record.target_month[:7],
        evidence_class=record.evidence_class,
        runtime_status="ISSUED",
        status_code=f"{record.forecast_track}_ISSUED",
        direction_vote_permitted=False,
        git_commit=record.git_commit,
        input_fingerprint=record.input_fingerprint,
        metadata={
            "forecast_track": record.forecast_track,
            "input_set_id": input_set_id,
            "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
            "canonical_authority": False,
            "historical_replay": record.forecast_track == "HISTORICAL_REPLAY",
            "prospective_claim": False if record.forecast_track == "HISTORICAL_REPLAY" else record.provenance.get("prospective_claim"),
            "information_cutoff": record.provenance.get("information_cutoff"),
            "replay_executed_at": record.provenance.get("replay_executed_at"),
        },
        monthly_expert_forecast_ids=(expert_row_id,),
    )
    return {
        "duplicate": False,
        "id": expert_row_id,
        "input_set_id": input_set_id,
        "engine_execution_run_id": runtime_run_id,
    }


def _post_commit_verify(database_url: str, row_id: int) -> None:
    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                select e.id,e.selector_status,e.auto_selector,e.auto_ensemble,e.canonical_authority,
                       e.input_set_id,s.input_fingerprint,
                       (select count(*) from forecast_input_set_members m where m.input_set_id=e.input_set_id) as member_count,
                       (select count(*) from engine_execution_expert_outputs o where o.monthly_expert_forecast_id=e.id) as runtime_link_count
                from monthly_expert_forecasts e
                join forecast_input_sets s on s.input_set_id=e.input_set_id
                where e.id=%s
                """,
                (row_id,),
            )
            stored = cur.fetchone()
        conn.rollback()
    if not stored:
        raise RuntimeError("EXPERT_FORECAST_POST_COMMIT_VERIFY_MISSING")
    if stored["selector_status"] != "NOT_PROVEN_EXPERT_SELECTION_RULE":
        raise RuntimeError("EXPERT_FORECAST_SELECTOR_GUARD_FAILED")
    if stored["auto_selector"] != "OFF" or stored["auto_ensemble"] != "OFF":
        raise RuntimeError("EXPERT_FORECAST_AUTO_SELECTION_GUARD_FAILED")
    if stored["canonical_authority"] is not False:
        raise RuntimeError("EXPERT_FORECAST_CANONICAL_AUTHORITY_GUARD_FAILED")
    if stored["input_set_id"] is None or int(stored["member_count"]) <= 0:
        raise RuntimeError("EXPERT_FORECAST_INPUT_SET_GUARD_FAILED")
    if int(stored["runtime_link_count"]) != 1:
        raise RuntimeError("EXPERT_FORECAST_RUNTIME_LEDGER_GUARD_FAILED")


def persist_expert_forecast(database_url: str, record: ExpertForecastRecord) -> dict:
    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        try:
            with conn.cursor() as cur:
                result = insert_expert_forecast(cur, record, verify_snapshots=True)
            if result["duplicate"]:
                conn.rollback()
                return result
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    _post_commit_verify(database_url, int(result["id"]))
    return {**result, "record": asdict(record)}
