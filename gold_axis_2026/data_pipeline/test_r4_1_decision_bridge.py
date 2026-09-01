from __future__ import annotations

import os
import sys
from copy import deepcopy

import psycopg

from r4_1_decision_bridge import (
    BridgeContractError,
    build_bridge_payload,
    frozen_engine_identity,
    persist_bridge_payload,
    validate_emitted_state,
)


def _state() -> dict:
    return {
        "date": "2099-01-05",
        "close": 100.0,
        "target_month": "2099-01",
        "vw_forecast_frozen": 100.0,
        "monthly_direction_3m": "DOWN",
        "level_emergency": "NEUTRAL",
        "reversal_emergency": "OFF",
        "fast_state": "ROBUST_UP",
        "slow_state": "NOT_YET_ROBUST",
        "gvz": 25.0,
        "gvz_cap": 1.0,
        "gvz_panic": False,
        "macro_event_down": None,
        "bocpd_context": "SMOKE_ONLY",
        "classification": "CONFLICT",
        "default_execution_session": "2099-01-06",
    }


def _count(cur, table: str) -> int:
    cur.execute(f"SELECT count(*) FROM {table}")
    return int(cur.fetchone()[0])


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("R4_1_DECISION_BRIDGE_SMOKE_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    try:
        state = _state()
        validated = validate_emitted_state(state)
        assert validated["classification"] == "CONFLICT"

        dangerous = deepcopy(state)
        dangerous["action"] = "AL"
        try:
            validate_emitted_state(dangerous)
            raise AssertionError("forbidden action field was accepted")
        except BridgeContractError as exc:
            assert "NOT_PROVEN_POSITION_MAPPING" in str(exc)

        drifted = deepcopy(state)
        drifted["new_unreviewed_signal"] = 1
        try:
            validate_emitted_state(drifted)
            raise AssertionError("unreviewed emitted-state field was accepted")
        except BridgeContractError as exc:
            assert "UNREVIEWED_EMITTED_STATE_FIELDS" in str(exc)

        engine_version, config_version, config_hash = frozen_engine_identity()
        assert engine_version == "gold-r4-direction-engine@0.1.0"
        assert config_version == "R4.1-challenger"
        assert len(config_hash) == 64

        payload = build_bridge_payload(
            state,
            decision_as_of="2099-01-05T21:00:00+00:00",
            generated_at="2099-01-05T21:01:00+00:00",
            evidence_class="HISTORICAL_REPLAY",
            trigger_type="stage3_bridge_rollback_smoke",
            close_source_ref="SMOKE_ONLY_CLOSE_SOURCE",
            quality_status="SMOKE_ONLY",
            code_sha=os.environ.get("GITHUB_SHA", "ROLLBACK_SMOKE_SHA"),
            input_snapshot_ref="SMOKE_ONLY_INPUT_SNAPSHOT",
            forecast_contract_ref="SMOKE_ONLY_FORECAST_CONTRACT",
            run_notes="rollback-only synthetic bridge verification",
        )
        assert payload["event"]["action_state"] is None
        assert payload["run"]["engine_version"] == engine_version
        assert payload["run"]["config_version"] == config_version
        assert payload["run"]["config_hash"] == config_hash

        tables = ("decision_runs", "decision_signal_snapshots", "decision_events")
        with psycopg.connect(url, autocommit=False) as conn:
            with conn.cursor() as cur:
                pre = {table: _count(cur, table) for table in tables}
                conn.rollback()

            first = persist_bridge_payload(conn, payload)
            assert first.inserted_run and first.inserted_snapshot and first.inserted_event
            second = persist_bridge_payload(conn, payload)
            assert second.run_id == first.run_id
            assert second.snapshot_id == first.snapshot_id
            assert second.event_id == first.event_id
            assert not second.inserted_run
            assert not second.inserted_snapshot
            assert not second.inserted_event

            conn.rollback()
            with conn.cursor() as cur:
                post = {table: _count(cur, table) for table in tables}
                conn.rollback()
            assert post == pre, f"BRIDGE_ROLLBACK_ROW_COUNT_MISMATCH pre={pre} post={post}"

        print(
            "R4_1_DECISION_BRIDGE_SMOKE_PASS "
            "state_contract=PASS forbidden_action_guard=PASS drift_guard=PASS "
            "frozen_identity=PASS store_reader_roundtrip=PASS idempotency=PASS rollback=PASS"
        )
        return 0
    except Exception as exc:
        print(f"R4_1_DECISION_BRIDGE_SMOKE_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
