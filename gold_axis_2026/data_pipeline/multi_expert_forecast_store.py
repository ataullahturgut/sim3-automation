from __future__ import annotations

import json
from dataclasses import asdict

import psycopg
from psycopg.rows import dict_row

from multi_expert_forecast import ExpertForecastRecord


def table_exists(cur) -> bool:
    cur.execute("select to_regclass('public.monthly_expert_forecasts') as reg")
    row = cur.fetchone()
    return bool(row and row["reg"] is not None)


def insert_expert_forecast(cur, record: ExpertForecastRecord, *, verify_snapshots: bool = True) -> dict:
    """Insert one expert row into the caller's transaction.

    The caller owns commit/rollback. This allows input snapshots, derived
    features and the expert output to become visible atomically.
    """
    record.validate()
    if not table_exists(cur):
        raise RuntimeError("BLOCKED_MULTI_EXPERT_LEDGER_SCHEMA_NOT_APPLIED")

    if verify_snapshots:
        cur.execute(
            "select count(*) as n from forecast_input_snapshots where id=any(%s)",
            (list(record.input_snapshot_ids),),
        )
        found = int(cur.fetchone()["n"])
        if found != len(set(record.input_snapshot_ids)):
            raise RuntimeError(
                f"BLOCKED_EXPERT_INPUT_SNAPSHOT_LINEAGE_INCOMPLETE:{found}/{len(set(record.input_snapshot_ids))}"
            )

    cur.execute(
        """
        select id from monthly_expert_forecasts
        where target_month=%s and forecast_track=%s and as_of=%s
          and expert_id=%s and model_version=%s
        """,
        (
            record.target_month + "-01" if len(record.target_month) == 7 else record.target_month,
            record.forecast_track,
            record.as_of,
            record.expert_id,
            record.model_version,
        ),
    )
    existing = cur.fetchone()
    if existing:
        return {"duplicate": True, "id": int(existing["id"])}

    provenance = dict(record.provenance)
    provenance.update(
        {
            "canonical_authority": False,
            "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
        }
    )
    cur.execute(
        """
        insert into monthly_expert_forecasts
          (target_month,forecast_origin,as_of,forecast_track,expert_id,
           model_name,model_version,expert_role,forecast_value,unit,
           evidence_class,git_commit,input_snapshot_ids,input_fingerprint,
           selector_status,auto_selector,auto_ensemble,canonical_authority,provenance)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                'NOT_PROVEN_EXPERT_SELECTION_RULE','OFF','OFF',false,%s::jsonb)
        returning id
        """,
        (
            record.target_month + "-01" if len(record.target_month) == 7 else record.target_month,
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
            list(record.input_snapshot_ids),
            record.input_fingerprint,
            json.dumps(provenance, sort_keys=True),
        ),
    )
    return {"duplicate": False, "id": int(cur.fetchone()["id"])}


def _post_commit_verify(database_url: str, row_id: int) -> None:
    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id,selector_status,auto_selector,auto_ensemble,canonical_authority
                from monthly_expert_forecasts where id=%s
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
