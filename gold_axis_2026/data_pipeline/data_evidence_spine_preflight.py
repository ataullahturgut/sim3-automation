from __future__ import annotations

import json
import os

import psycopg
from psycopg.rows import dict_row


NEW_OBJECTS = (
    "forecast_input_sets",
    "forecast_input_set_members",
    "engine_execution_runs",
    "engine_execution_derived_outputs",
    "engine_execution_expert_outputs",
    "engine_execution_decision_outputs",
)


def classify_preflight(
    *,
    input_rows: int,
    expert_rows: int,
    derived_rows: int,
    decision_rows: int,
    pit_surface: bool,
    legacy_immutability_guards: int,
    object_state: dict[str, bool],
) -> dict[str, object]:
    no_reconciliation_needed = input_rows == 0 and expert_rows == 0
    legacy_integrity = pit_surface and legacy_immutability_guards == 3 and derived_rows >= 7
    all_new_objects_present = all(bool(object_state.get(name)) for name in NEW_OBJECTS)
    no_new_objects_present = not any(bool(object_state.get(name)) for name in NEW_OBJECTS)

    if all_new_objects_present:
        mode = "ALREADY_MIGRATED"
        # Existing governed rows are expected after migration. Their FK/PIT/runtime-link
        # correctness is proved by the immediately following read-only integrity audit.
        passed = legacy_integrity and decision_rows == 0
        status = "PASS_ALREADY_MIGRATED" if passed else "BLOCKED_POST_MIGRATION_INTEGRITY"
        existing_rows_allowed_in_mode = True
    elif no_new_objects_present:
        mode = "PRE_MIGRATION"
        passed = no_reconciliation_needed and legacy_integrity and decision_rows == 0
        status = "PASS_PRE_MIGRATION" if passed else "BLOCKED_PRE_MIGRATION_RECONCILIATION"
        existing_rows_allowed_in_mode = False
    else:
        mode = "PARTIAL_MIGRATION"
        passed = False
        status = "BLOCKED_PARTIAL_MIGRATION"
        existing_rows_allowed_in_mode = False

    return {
        "status": status,
        "preflight_mode": mode,
        "passed": passed,
        "legacy_integrity": legacy_integrity,
        "all_new_objects_present": all_new_objects_present,
        "no_new_objects_present": no_new_objects_present,
        "existing_row_reconciliation_required": not no_reconciliation_needed,
        "existing_rows_allowed_in_mode": existing_rows_allowed_in_mode,
    }


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("select count(*) as n from forecast_input_snapshots")
            input_rows = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from monthly_expert_forecasts")
            expert_rows = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from derived_feature_snapshots")
            derived_rows = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from decision_signal_snapshots")
            decision_rows = int(cur.fetchone()["n"])
            cur.execute("select to_regprocedure('observations_as_of(timestamp with time zone)') as reg")
            pit_surface = cur.fetchone()["reg"] is not None
            cur.execute(
                """
                select count(distinct trigger_name) as n
                from information_schema.triggers
                where event_object_schema='public'
                  and trigger_name in (
                    'trg_forecast_input_snapshots_immutable',
                    'trg_derived_feature_snapshots_immutable',
                    'trg_monthly_forecast_contracts_immutable'
                  )
                """
            )
            legacy_immutability_guards = int(cur.fetchone()["n"])
            object_state = {}
            for name in NEW_OBJECTS:
                cur.execute("select to_regclass(%s) as reg", (f"public.{name}",))
                object_state[name] = cur.fetchone()["reg"] is not None
        conn.rollback()

    classification = classify_preflight(
        input_rows=input_rows,
        expert_rows=expert_rows,
        derived_rows=derived_rows,
        decision_rows=decision_rows,
        pit_surface=pit_surface,
        legacy_immutability_guards=legacy_immutability_guards,
        object_state=object_state,
    )
    passed = bool(classification["passed"])
    print(json.dumps({
        "status": classification["status"],
        "preflight_mode": classification["preflight_mode"],
        "forecast_input_snapshot_rows": input_rows,
        "monthly_expert_forecast_rows": expert_rows,
        "derived_feature_rows": derived_rows,
        "decision_signal_rows": decision_rows,
        "observations_as_of_available": pit_surface,
        "legacy_immutability_guard_count": legacy_immutability_guards,
        "new_spine_objects_already_present": object_state,
        "all_new_objects_present": classification["all_new_objects_present"],
        "existing_row_reconciliation_required": classification["existing_row_reconciliation_required"],
        "existing_rows_allowed_in_mode": classification["existing_rows_allowed_in_mode"],
        "database_writes": "NONE",
    }, sort_keys=True))
    print(f"DATA_EVIDENCE_SPINE_PRODUCTION_PREFLIGHT_PASS={str(passed).lower()}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
