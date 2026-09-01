from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

from decision_store import persist_decision
from decision_store_reader import read_latest_decision


ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "schema_patch_decision_store_v1.sql"
TABLES = ("decision_runs", "decision_signal_snapshots", "decision_events")


def _exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return cur.fetchone()[0] is not None


def _payload(evidence_class: str, as_of: str, generated_at: str, classification: str, reason_code: str) -> dict:
    return {
        "run": {
            "decision_as_of": as_of,
            "generated_at": generated_at,
            "engine_version": "R4.1-READER-SMOKE",
            "config_version": "R4.1-READER-SMOKE",
            "config_hash": "reader-smoke-config",
            "code_sha": "reader-smoke-sha",
            "trigger_type": "reader_smoke",
            "evidence_class": evidence_class,
            "status": "SUCCESS",
            "input_snapshot_ref": f"reader-smoke-input-{evidence_class}",
            "forecast_contract_ref": f"reader-smoke-forecast-{evidence_class}",
            "metadata": {"synthetic": True, "rollback_only": True},
        },
        "snapshot": {
            "target_month": "2026-09",
            "close_value": 4455.15,
            "close_source_ref": f"reader-smoke-close-{evidence_class}",
            "vw_forecast_frozen": 4093.03884,
            "forecast_contract_ref": f"reader-smoke-forecast-{evidence_class}",
            "monthly_direction_3m": "DOWN",
            "level_emergency": "UP",
            "reversal_emergency": "OFF",
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
        print("DECISION_STORE_READER_SMOKE_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    try:
        with psycopg.connect(url, autocommit=False) as conn:
            with conn.cursor() as cur:
                pre = {name: _exists(cur, name) for name in TABLES}
                conn.rollback()
                cur.execute(PATCH.read_text(encoding="utf-8"))

            # Synthetic rollback-only records prove the reader cannot mix
            # historical replay with prospective/live state.
            persist_decision(
                conn,
                _payload(
                    "HISTORICAL_REPLAY",
                    "2026-08-28T21:00:00+00:00",
                    "2026-09-01T09:00:00+00:00",
                    "ALIGNED_UP",
                    "LEVEL_FAST_SLOW_ALIGNED_UP",
                ),
            )
            persist_decision(
                conn,
                _payload(
                    "PROSPECTIVE_SHADOW",
                    "2026-08-29T21:00:00+00:00",
                    "2026-09-01T09:01:00+00:00",
                    "CONFLICT",
                    "MONTHLY_VS_TACTICAL_CONFLICT",
                ),
            )

            replay = read_latest_decision(conn, "HISTORICAL_REPLAY")
            shadow = read_latest_decision(conn, "PROSPECTIVE_SHADOW")
            live = read_latest_decision(conn, "LIVE_PRODUCTION")

            assert replay is not None and replay["evidence_class"] == "HISTORICAL_REPLAY"
            assert replay["classification"] == "ALIGNED_UP"
            assert shadow is not None and shadow["evidence_class"] == "PROSPECTIVE_SHADOW"
            assert shadow["classification"] == "CONFLICT"
            assert shadow["action_state"] is None
            assert live is None

            try:
                read_latest_decision(conn, "CURRENT")
                raise AssertionError("READER_INVALID_EVIDENCE_CLASS_NOT_REJECTED")
            except ValueError:
                pass

            conn.rollback()
            with conn.cursor() as cur:
                post = {name: _exists(cur, name) for name in TABLES}
                conn.rollback()
            assert post == pre, f"READER_ROLLBACK_SCHEMA_MISMATCH pre={pre} post={post}"

        print(
            "DECISION_STORE_READER_SMOKE_PASS "
            "evidence_isolation=PASS replay_not_live=PASS action_mapping_guard=PASS rollback=PASS"
        )
        return 0
    except Exception as exc:
        print(f"DECISION_STORE_READER_SMOKE_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
