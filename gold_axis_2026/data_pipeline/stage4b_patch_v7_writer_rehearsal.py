from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
V7 = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_evidence.json"
SCHEMA = ROOT / "stage4b" / "forecast_writer_schema_evidence.json"
OUT = ROOT / "stage4b" / "patch_v7_writer_rehearsal_evidence.json"
MODEL_NAME = "CAUSAL_PATCH_R1"
MODEL_VERSION = "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE"


def main() -> int:
    v7 = json.loads(V7.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if v7.get("decision") != "PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS" or not v7.get("model_impact_pass"):
        raise RuntimeError("V7_PARENT_NOT_PASS")
    if schema.get("decision") != "FORECAST_WRITER_SCHEMA_AUDIT_PASS" or not schema.get("schema_audit_pass"):
        raise RuntimeError("WRITER_SCHEMA_NOT_PASS")

    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")

    # EXPLAIN without ANALYZE validates the actual INSERT statement shape against
    # the production schema while executing no INSERT and consuming no identity value.
    input_sql = """
    insert into forecast_input_snapshots
      (forecast_origin,target_period,model_name,model_version,git_commit,
       series_id,semantic_id,observation_ts,value_used,available_as_of,
       retrieved_at,transform,lineage_id,metadata)
    values
      (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
    returning id
    """
    contract_sql = """
    insert into monthly_forecast_contracts
      (target_month,forecast_origin,model_name,model_version,forecast_value,
       unit,model_role,frozen_at,git_commit,provenance)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
    returning id
    """

    sentinel_ts = datetime(2098, 12, 31, 23, 0, tzinfo=timezone.utc)
    input_params = (
        sentinel_ts, "2099-01", MODEL_NAME, MODEL_VERSION, "SCHEMA_REHEARSAL",
        "SCHEMA_REHEARSAL_SENTINEL", "SCHEMA_REHEARSAL_SENTINEL", sentinel_ts,
        1.0, sentinel_ts, sentinel_ts, "SCHEMA_REHEARSAL", "SCHEMA_REHEARSAL_SENTINEL",
        json.dumps({"evidence_class": "SCHEMA_REHEARSAL_ONLY", "persistent_write": False}),
    )
    contract_params = (
        sentinel_ts.date().replace(day=1), sentinel_ts, MODEL_NAME, MODEL_VERSION, 1.0,
        "USD/oz", "PRIMARY_EXECUTABLE", sentinel_ts, "SCHEMA_REHEARSAL",
        json.dumps({"evidence_class": "SCHEMA_REHEARSAL_ONLY", "persistent_write": False}),
    )

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("select count(*) as n from forecast_input_snapshots")
            before_inputs = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from monthly_forecast_contracts")
            before_contracts = int(cur.fetchone()["n"])
            cur.execute("EXPLAIN (FORMAT JSON) " + input_sql, input_params)
            input_plan = cur.fetchone()
            cur.execute("EXPLAIN (FORMAT JSON) " + contract_sql, contract_params)
            contract_plan = cur.fetchone()
            cur.execute("select count(*) as n from forecast_input_snapshots")
            after_inputs = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from monthly_forecast_contracts")
            after_contracts = int(cur.fetchone()["n"])
        conn.rollback()

    passed = bool(
        input_plan is not None and contract_plan is not None
        and before_inputs == 0 and before_contracts == 0
        and after_inputs == before_inputs and after_contracts == before_contracts
    )
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": MODEL_VERSION,
        "parent_v7_decision": v7.get("decision"),
        "schema_decision": schema.get("decision"),
        "mode": "READ_ONLY_EXPLAIN_INSERT_REHEARSAL",
        "input_insert_plan_valid": input_plan is not None,
        "contract_insert_plan_valid": contract_plan is not None,
        "forecast_input_rows_before": before_inputs,
        "forecast_input_rows_after": after_inputs,
        "forecast_contract_rows_before": before_contracts,
        "forecast_contract_rows_after": after_contracts,
        "persistent_database_writes": "NONE",
        "identity_values_consumed": False,
        "raw_market_values_logged": False,
        "rehearsal_pass": passed,
        "decision": "PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS" if passed else "BLOCKED_PATCH_V7_FORECAST_WRITER_NOT_PROVEN",
        "prospective_claim": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print(f"PATCH_V7_WRITER_REHEARSAL_PASS={str(passed).lower()}")
    print(f"FORECAST_INPUT_ROWS={before_inputs}->{after_inputs}")
    print(f"FORECAST_CONTRACT_ROWS={before_contracts}->{after_contracts}")
    print("PERSISTENT_DATABASE_WRITES=NONE")
    print("IDENTITY_VALUES_CONSUMED=NO")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
