from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from psycopg.errors import RaiseException

from decision_store import normalize_payload, persist_decision


ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "schema_patch_decision_store_v1.sql"
TABLES = ("decision_runs", "decision_signal_snapshots", "decision_events")


def _exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return cur.fetchone()[0] is not None


def _payload(*, decision_as_of: str, generated_at: str, classification: str, reason_code: str) -> dict:
    return {
        "run": {
            "decision_as_of": decision_as_of,
            "generated_at": generated_at,
            "engine_version": "R4.1-WRITER-SMOKE",
            "config_version": "R4.1-WRITER-SMOKE",
            "config_hash": "writer-smoke-config",
            "code_sha": "writer-smoke-sha",
            "trigger_type": "writer_smoke",
            "evidence_class": "HISTORICAL_REPLAY",
            "status": "SUCCESS",
            "input_snapshot_ref": "writer-smoke-input",
            "forecast_contract_ref": "writer-smoke-forecast",
            "metadata": {"synthetic": True, "rollback_only": True},
        },
        "snapshot": {
            "target_month": "2026-08",
            "close_value": 4455.15,
            "close_source_ref": "writer-smoke-close",
            "vw_forecast_frozen": 4093.03884,
            "forecast_contract_ref": "writer-smoke-forecast",
            "monthly_direction_3m": "DOWN",
            "level_emergency": "UP",
            "reversal_emergency": "DOWN_ALERT" if classification == "REVERSAL_RISK_DOWN" else "OFF",
            "fast_state": "ROBUST_UP",
            "slow_state": "ROBUST_UP",
            "gvz_value": 25.17,
            "gvz_cap": 1.0,
            "gvz_panic": False,
            "macro_event_down": None,
            "bocpd_context": "SMOKE_ONLY",
            "classification": classification,
            "default_execution_session": "2026-09-01",
            "quality_status": "SMOKE_ONLY",
            "metadata": {"synthetic": True},
        },
        "event": {
            "reason_code": reason_code,
            "action_state": None,
            "execution_session": "2026-09-01",
            "metadata": {"synthetic": True},
        },
    }


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("DECISION_STORE_WRITER_SMOKE_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    patch_sql = PATCH.read_text(encoding="utf-8")

    try:
        with psycopg.connect(url, autocommit=False) as conn:
            with conn.cursor() as cur:
                pre = {name: _exists(cur, name) for name in TABLES}
                conn.rollback()

                # Build the exact candidate production schema inside one transaction.
                # Every synthetic write below is rolled back before the test exits.
                cur.execute(patch_sql)

            first = _payload(
                decision_as_of="2026-08-28T21:00:00+00:00",
                generated_at="2026-09-01T08:55:00+00:00",
                classification="ALIGNED_UP",
                reason_code="LEVEL_FAST_SLOW_ALIGNED_UP",
            )
            r1 = persist_decision(conn, first)
            assert r1.inserted_run and r1.inserted_snapshot and r1.inserted_event
            assert r1.classification_changed is True

            # Exact same issued payload must be idempotent.
            r1_repeat = persist_decision(conn, first)
            assert r1_repeat.run_id == r1.run_id
            assert r1_repeat.snapshot_id == r1.snapshot_id
            assert r1_repeat.event_id == r1.event_id
            assert not r1_repeat.inserted_run
            assert not r1_repeat.inserted_snapshot
            assert not r1_repeat.inserted_event

            # A later state in the same evidence class must retain prior classification lineage.
            second = _payload(
                decision_as_of="2026-08-29T21:00:00+00:00",
                generated_at="2026-09-01T08:56:00+00:00",
                classification="CONFLICT",
                reason_code="MONTHLY_VS_TACTICAL_CONFLICT",
            )
            r2 = persist_decision(conn, second)
            assert r2.inserted_run and r2.inserted_snapshot and r2.inserted_event
            assert r2.classification_changed is True

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT previous_classification, classification, action_state "
                    "FROM decision_events WHERE event_id=%s",
                    (r2.event_id,),
                )
                prev, current, action = cur.fetchone()
                assert prev == "ALIGNED_UP"
                assert current == "CONFLICT"
                assert action is None

                # The database itself must reject mutation of an issued snapshot.
                cur.execute("SAVEPOINT writer_append_only")
                try:
                    cur.execute(
                        "UPDATE decision_signal_snapshots SET classification='ALIGNED_DOWN' WHERE snapshot_id=%s",
                        (r2.snapshot_id,),
                    )
                    raise AssertionError("WRITER_APPEND_ONLY_TRIGGER_NOT_ENFORCED")
                except RaiseException:
                    cur.execute("ROLLBACK TO SAVEPOINT writer_append_only")
                cur.execute("RELEASE SAVEPOINT writer_append_only")

            # Python boundary must also refuse an invented position/action mapping.
            invalid_action = _payload(
                decision_as_of="2026-08-30T21:00:00+00:00",
                generated_at="2026-09-01T08:57:00+00:00",
                classification="ALIGNED_UP",
                reason_code="LEVEL_FAST_SLOW_ALIGNED_UP",
            )
            invalid_action["event"]["action_state"] = "BUY"
            try:
                normalize_payload(invalid_action)
                raise AssertionError("WRITER_ACTION_MAPPING_GUARD_NOT_ENFORCED")
            except ValueError as exc:
                assert "NOT_PROVEN_POSITION_MAPPING" in str(exc)

            # Prospective evidence cannot be persisted without its mandatory provenance.
            invalid_prospective = _payload(
                decision_as_of="2026-08-31T21:00:00+00:00",
                generated_at="2026-09-01T08:58:00+00:00",
                classification="ALIGNED_UP",
                reason_code="LEVEL_FAST_SLOW_ALIGNED_UP",
            )
            invalid_prospective["run"]["evidence_class"] = "LIVE_PRODUCTION"
            invalid_prospective["run"]["code_sha"] = None
            try:
                normalize_payload(invalid_prospective)
                raise AssertionError("WRITER_PROSPECTIVE_PROVENANCE_GUARD_NOT_ENFORCED")
            except ValueError as exc:
                assert "code_sha" in str(exc)

            conn.rollback()

            with conn.cursor() as cur:
                post = {name: _exists(cur, name) for name in TABLES}
                conn.rollback()
            assert post == pre, f"WRITER_ROLLBACK_SCHEMA_MISMATCH pre={pre} post={post}"

        print(
            "DECISION_STORE_WRITER_SMOKE_PASS "
            "persistence=PASS idempotency=PASS previous_state_lineage=PASS "
            "action_mapping_guard=PASS prospective_provenance_guard=PASS "
            "append_only=PASS rollback=PASS"
        )
        return 0
    except Exception as exc:
        print(f"DECISION_STORE_WRITER_SMOKE_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
