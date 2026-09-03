from __future__ import annotations

import argparse
import json
import os

import psycopg
from psycopg.rows import dict_row

from data_evidence_spine import SCHEMA_REQUIRED_OBJECTS, spine_schema_ready


IMMUTABILITY_TRIGGERS = (
    "trg_forecast_input_sets_immutable",
    "trg_forecast_input_set_members_immutable",
    "trg_engine_execution_runs_immutable",
    "trg_engine_execution_derived_outputs_immutable",
    "trg_engine_execution_expert_outputs_immutable",
    "trg_engine_execution_decision_outputs_immutable",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-runtime-12", action="store_true")
    args = parser.parse_args()
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            if not spine_schema_ready(cur):
                missing = []
                for name in SCHEMA_REQUIRED_OBJECTS:
                    cur.execute("select to_regclass(%s) as reg", (f"public.{name}",))
                    row = cur.fetchone()
                    if not row or row["reg"] is None:
                        missing.append(name)
                conn.rollback()
                print(json.dumps({"status": "BLOCKED_SCHEMA_NOT_APPLIED", "missing": missing}, sort_keys=True))
                return 3

            cur.execute("select * from data_evidence_spine_health_v1")
            health = dict(cur.fetchone())
            cur.execute(
                "select engine_id,runtime_status,status_code,engine_version,as_of,target_context,evidence_class "
                "from latest_engine_runtime_state order by engine_id"
            )
            runtime = [dict(r) for r in cur.fetchall()]
            cur.execute(
                """
                select count(*) as n from information_schema.triggers
                where event_object_schema='public' and trigger_name=any(%s)
                """,
                (list(IMMUTABILITY_TRIGGERS),),
            )
            guard_count = int(cur.fetchone()["n"])
            cur.execute(
                """
                select count(*) as n
                from forecast_input_set_members m
                join forecast_input_sets s on s.input_set_id=m.input_set_id
                join forecast_input_snapshots f on f.id=m.snapshot_id
                where f.forecast_origin is distinct from s.forecast_origin
                   or f.target_period is distinct from to_char(s.target_month,'YYYY-MM')
                   or f.model_name is distinct from s.model_name
                   or f.model_version is distinct from s.model_version
                   or f.available_as_of > s.as_of
                   or f.retrieved_at > s.as_of
                """
            )
            member_identity_or_pit_mismatches = int(cur.fetchone()["n"])
            cur.execute(
                """
                select count(*) as n
                from monthly_expert_forecasts e
                where (
                    select array_agg(snapshot_id order by snapshot_id)
                    from forecast_input_set_members m
                    where m.input_set_id=e.input_set_id
                ) is distinct from (
                    select array_agg(x order by x)
                    from (select distinct unnest(e.input_snapshot_ids) as x) q
                )
                """
            )
            expert_membership_array_mismatches = int(cur.fetchone()["n"])
            cur.execute(
                """
                select count(*) as n
                from monthly_expert_forecasts e
                where (select count(*) from engine_execution_expert_outputs o
                       where o.monthly_expert_forecast_id=e.id) <> 1
                """
            )
            expert_runtime_link_mismatches = int(cur.fetchone()["n"])
        conn.rollback()

    extended_integrity = {
        "member_identity_or_pit_mismatches": member_identity_or_pit_mismatches,
        "expert_membership_array_mismatches": expert_membership_array_mismatches,
        "expert_runtime_link_mismatches": expert_runtime_link_mismatches,
    }
    integrity_ok = (
        int(health["orphan_input_snapshots"]) == 0
        and int(health["expert_rows_without_input_set"]) == 0
        and int(health["expert_input_fingerprint_mismatches"]) == 0
        and all(v == 0 for v in extended_integrity.values())
        and guard_count == len(IMMUTABILITY_TRIGGERS)
    )
    runtime_ok = len(runtime) == 12 if args.require_runtime_12 else True
    passed = integrity_ok and runtime_ok
    print(json.dumps({
        "status": "PASS" if passed else "BLOCKED",
        "health": health,
        "extended_integrity": extended_integrity,
        "runtime_engine_count": len(runtime),
        "runtime": runtime,
        "required_guard_count": len(IMMUTABILITY_TRIGGERS),
        "actual_guard_count": guard_count,
        "integrity_ok": integrity_ok,
        "runtime_ok": runtime_ok,
        "database_writes": "NONE",
    }, default=str, sort_keys=True))
    print(f"DATA_EVIDENCE_SPINE_AUDIT_PASS={str(passed).lower()}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
