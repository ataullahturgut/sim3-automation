from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import psycopg
from psycopg.errors import CheckViolation, RaiseException, UniqueViolation


ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "schema_patch_decision_store_v1.sql"
TABLES = ("decision_runs", "decision_signal_snapshots", "decision_events")
VIEWS = ("latest_decision_snapshot_by_evidence",)
AMBIGUOUS_VIEW = "latest_decision_snapshot"


def _exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return cur.fetchone()[0] is not None


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("DECISION_STORE_SMOKE_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    patch_sql = PATCH.read_text(encoding="utf-8")

    try:
        with psycopg.connect(url, autocommit=False) as conn:
            with conn.cursor() as cur:
                objects = TABLES + VIEWS + (AMBIGUOUS_VIEW,)
                pre = {name: _exists(cur, name) for name in objects}
                conn.rollback()

                # PostgreSQL DDL is transactional. Execute the production patch and
                # test constraints, then roll the whole transaction back so this
                # smoke test cannot persist schema or synthetic decision rows.
                cur.execute(patch_sql)
                for name in TABLES + VIEWS:
                    assert _exists(cur, name), f"OBJECT_NOT_CREATED:{name}"
                assert not _exists(cur, AMBIGUOUS_VIEW), "AMBIGUOUS_CROSS_EVIDENCE_LATEST_VIEW_EXISTS"

                run_id = uuid.uuid4()
                snapshot_id = uuid.uuid4()
                event_id = uuid.uuid4()
                run_fp = f"smoke-run-{run_id}"
                snap_fp = f"smoke-snapshot-{snapshot_id}"
                event_fp = f"smoke-event-{event_id}"

                cur.execute(
                    """
                    INSERT INTO decision_runs (
                        run_id, decision_as_of, generated_at, engine_version,
                        config_version, config_hash, code_sha, trigger_type,
                        evidence_class, status, input_snapshot_ref,
                        forecast_contract_ref, fingerprint
                    ) VALUES (
                        %s, '2026-08-31 21:00:00+00', '2026-09-01 08:00:00+00',
                        'R4.1-SMOKE', 'R4.1-SMOKE', 'smoke-config', 'smoke-sha',
                        'schema_smoke', 'HISTORICAL_REPLAY', 'SUCCESS',
                        'smoke-input', 'smoke-forecast', %s
                    )
                    """,
                    (run_id, run_fp),
                )
                cur.execute(
                    """
                    INSERT INTO decision_signal_snapshots (
                        snapshot_id, run_id, decision_as_of, target_month,
                        close_value, close_source_ref, vw_forecast_frozen,
                        forecast_contract_ref, monthly_direction_3m,
                        level_emergency, reversal_emergency, fast_state,
                        slow_state, gvz_value, gvz_cap, gvz_panic,
                        macro_event_down, bocpd_context, classification,
                        default_execution_session, quality_status, fingerprint
                    ) VALUES (
                        %s, %s, '2026-08-31 21:00:00+00', '2026-08-01',
                        1.0, 'smoke-close', 1.0, 'smoke-forecast',
                        'UP', 'UP', 'OFF', 'ROBUST_UP', 'ROBUST_UP',
                        NULL, NULL, NULL, NULL, NULL, 'ALIGNED_UP',
                        '2026-09-01', 'SMOKE_ONLY', %s
                    )
                    """,
                    (snapshot_id, run_id, snap_fp),
                )

                cur.execute(
                    "SELECT evidence_class, classification FROM latest_decision_snapshot_by_evidence"
                )
                latest_rows = cur.fetchall()
                assert latest_rows == [("HISTORICAL_REPLAY", "ALIGNED_UP")], latest_rows

                cur.execute("SAVEPOINT invalid_action")
                try:
                    cur.execute(
                        """
                        INSERT INTO decision_events (
                            event_id, run_id, snapshot_id, event_ts,
                            previous_classification, classification,
                            classification_changed, reason_code, action_state,
                            execution_session, fingerprint
                        ) VALUES (
                            %s, %s, %s, '2026-08-31 21:00:00+00', NULL,
                            'ALIGNED_UP', true, 'LEVEL_FAST_SLOW_ALIGNED_UP',
                            'BUY', '2026-09-01', %s
                        )
                        """,
                        (event_id, run_id, snapshot_id, event_fp + "-invalid"),
                    )
                    raise AssertionError("ACTION_STATE_CONSTRAINT_NOT_ENFORCED")
                except CheckViolation:
                    cur.execute("ROLLBACK TO SAVEPOINT invalid_action")
                cur.execute("RELEASE SAVEPOINT invalid_action")

                cur.execute(
                    """
                    INSERT INTO decision_events (
                        event_id, run_id, snapshot_id, event_ts,
                        previous_classification, classification,
                        classification_changed, reason_code, action_state,
                        execution_session, fingerprint
                    ) VALUES (
                        %s, %s, %s, '2026-08-31 21:00:00+00', NULL,
                        'ALIGNED_UP', true, 'LEVEL_FAST_SLOW_ALIGNED_UP',
                        NULL, '2026-09-01', %s
                    )
                    """,
                    (event_id, run_id, snapshot_id, event_fp),
                )

                cur.execute("SAVEPOINT append_only")
                try:
                    cur.execute(
                        "UPDATE decision_signal_snapshots SET classification='CONFLICT' WHERE snapshot_id=%s",
                        (snapshot_id,),
                    )
                    raise AssertionError("APPEND_ONLY_TRIGGER_NOT_ENFORCED")
                except RaiseException:
                    cur.execute("ROLLBACK TO SAVEPOINT append_only")
                cur.execute("RELEASE SAVEPOINT append_only")

                cur.execute("SAVEPOINT duplicate_fp")
                try:
                    cur.execute(
                        """
                        INSERT INTO decision_runs (
                            run_id, decision_as_of, generated_at, engine_version,
                            config_version, trigger_type, evidence_class, status,
                            fingerprint
                        ) VALUES (
                            %s, '2026-08-31 21:00:00+00', '2026-09-01 08:01:00+00',
                            'R4.1-SMOKE', 'R4.1-SMOKE', 'schema_smoke',
                            'HISTORICAL_REPLAY', 'SUCCESS', %s
                        )
                        """,
                        (uuid.uuid4(), run_fp),
                    )
                    raise AssertionError("FINGERPRINT_UNIQUENESS_NOT_ENFORCED")
                except UniqueViolation:
                    cur.execute("ROLLBACK TO SAVEPOINT duplicate_fp")
                cur.execute("RELEASE SAVEPOINT duplicate_fp")

                conn.rollback()

                post = {name: _exists(cur, name) for name in objects}
                conn.rollback()
                assert post == pre, f"ROLLBACK_SCHEMA_MISMATCH pre={pre} post={post}"

        print(
            "DECISION_STORE_SCHEMA_SMOKE_PASS "
            "transactional_ddl=PASS evidence_scoped_latest_view=PASS "
            "action_mapping_guard=PASS append_only=PASS "
            "idempotency_fingerprint=PASS rollback=PASS"
        )
        return 0
    except Exception as exc:
        print(f"DECISION_STORE_SCHEMA_SMOKE_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
