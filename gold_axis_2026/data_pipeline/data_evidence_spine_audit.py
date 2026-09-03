from __future__ import annotations

import argparse
import json
import os

import psycopg
from psycopg.rows import dict_row

from data_evidence_spine import SCHEMA_REQUIRED_OBJECTS, spine_schema_ready


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
            cur.execute("select engine_id,runtime_status,status_code,engine_version,as_of,target_context,evidence_class from latest_engine_runtime_state order by engine_id")
            runtime = [dict(r) for r in cur.fetchall()]
            cur.execute(
                """
                select count(*) as n from information_schema.triggers
                where event_object_schema='public'
                  and trigger_name in (
                    'trg_monthly_expert_input_set_binding',
                    'trg_monthly_expert_runtime_ledger',
                    'trg_derived_feature_runtime_ledger',
                    'trg_forecast_input_sets_immutable',
                    'trg_forecast_input_set_members_immutable',
                    'trg_engine_execution_runs_immutable'
                  )
                """
            )
            guard_count = int(cur.fetchone()["n"])
        conn.rollback()

    integrity_ok = (
        int(health["orphan_input_snapshots"]) == 0
        and int(health["expert_rows_without_input_set"]) == 0
        and int(health["expert_input_fingerprint_mismatches"]) == 0
        and guard_count == 6
    )
    runtime_ok = len(runtime) == 12 if args.require_runtime_12 else True
    passed = integrity_ok and runtime_ok
    print(json.dumps({
        "status": "PASS" if passed else "BLOCKED",
        "health": health,
        "runtime_engine_count": len(runtime),
        "runtime": runtime,
        "required_guard_count": 6,
        "actual_guard_count": guard_count,
        "integrity_ok": integrity_ok,
        "runtime_ok": runtime_ok,
        "database_writes": "NONE",
    }, default=str, sort_keys=True))
    print(f"DATA_EVIDENCE_SPINE_AUDIT_PASS={str(passed).lower()}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
