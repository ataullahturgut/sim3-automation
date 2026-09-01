from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg
from pandas.testing import assert_frame_equal

from decision_store import persist_decision
from decision_store_reader import read_latest_decision
from r4_1_decision_adapter import build_decision_payload, reason_code_for_classification


DATA_PIPELINE_ROOT = Path(__file__).resolve().parent
GOLD_ROOT = DATA_PIPELINE_ROOT.parent
R4_ROOT = GOLD_ROOT / "r4_1"
R4_SRC = R4_ROOT / "src"
R4_REPLAY = R4_ROOT / "scripts" / "replay_daily.py"
R4_CONFIG = R4_ROOT / "config" / "frozen_r4_1.json"
PATCH = DATA_PIPELINE_ROOT / "schema_patch_decision_store_v1.sql"
TABLES = ("decision_runs", "decision_signal_snapshots", "decision_events")


def _load_replay():
    sys.path.insert(0, str(R4_SRC))
    spec = importlib.util.spec_from_file_location("gold_r4_replay_daily_adapter_smoke", R4_REPLAY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load R4.1 replay: {R4_REPLAY}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_replay


run_replay = _load_replay()


def _exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s)", (f"public.{name}",))
    return cur.fetchone()[0] is not None


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.bdate_range("2026-08-03", "2026-08-28")
    closes = [100.0 + i * 0.6 for i in range(len(dates))]
    daily = pd.DataFrame(
        {
            "date": dates,
            "close": closes,
            "gvz": 25.17,
            "macro_event_down": False,
            "bocpd_context": "NONE",
        }
    )
    monthly = pd.DataFrame(
        [
            {
                "target_month": "2026-08",
                "vw_forecast": 100.0,
                "return_t1": -0.03,
                "return_t2": -0.02,
                "return_t3": 0.01,
            }
        ]
    )
    return daily, monthly


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("R4_1_DECISION_ADAPTER_SMOKE_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    try:
        config_bytes = R4_CONFIG.read_bytes()
        config = json.loads(config_bytes.decode("utf-8"))
        config_hash = hashlib.sha256(config_bytes).hexdigest()

        daily, monthly = _inputs()
        replay_a = run_replay(daily, monthly)
        replay_b = run_replay(daily, monthly)
        assert_frame_equal(replay_a, replay_b, check_exact=True)
        emitted = replay_a.iloc[-1].to_dict()

        classification = str(emitted["classification"])
        reason = reason_code_for_classification(classification)
        assert reason

        decision_as_of = "2026-08-28T21:00:00+00:00"
        payload = build_decision_payload(
            emitted,
            decision_as_of=decision_as_of,
            generated_at="2026-09-01T09:30:00+00:00",
            engine_version="gold-r4-direction-engine@0.1.0",
            config_version=str(config["version"]),
            config_hash=config_hash,
            code_sha=os.environ.get("GITHUB_SHA", "ROLLBACK_SMOKE_SHA"),
            trigger_type="r4_1_adapter_smoke",
            evidence_class="HISTORICAL_REPLAY",
            input_snapshot_ref="ROLLBACK_SMOKE_INPUT_SNAPSHOT",
            forecast_contract_ref="ROLLBACK_SMOKE_MONTHLY_CONTRACT",
            close_source_ref="ROLLBACK_SMOKE_CLOSE_SOURCE",
            quality_status="SMOKE_ONLY",
            run_metadata={"rollback_only": True},
        )

        assert payload["snapshot"]["classification"] == classification
        assert payload["event"]["reason_code"] == reason
        assert payload["event"]["action_state"] is None
        assert payload["run"]["config_version"] == config["version"]
        assert payload["run"]["config_hash"] == config_hash

        with psycopg.connect(url, autocommit=False) as conn:
            with conn.cursor() as cur:
                pre = {name: _exists(cur, name) for name in TABLES}
                conn.rollback()
                cur.execute(PATCH.read_text(encoding="utf-8"))

            first = persist_decision(conn, payload)
            assert first.inserted_run and first.inserted_snapshot and first.inserted_event

            repeated = persist_decision(conn, payload)
            assert repeated.run_id == first.run_id
            assert repeated.snapshot_id == first.snapshot_id
            assert repeated.event_id == first.event_id
            assert not repeated.inserted_run
            assert not repeated.inserted_snapshot
            assert not repeated.inserted_event

            stored = read_latest_decision(conn, "HISTORICAL_REPLAY")
            assert stored is not None
            assert stored["classification"] == emitted["classification"]
            assert stored["event_classification"] == emitted["classification"]
            assert stored["monthly_direction_3m"] == emitted["monthly_direction_3m"]
            assert stored["level_emergency"] == emitted["level_emergency"]
            assert stored["reversal_emergency"] == emitted["reversal_emergency"]
            assert stored["fast_state"] == emitted["fast_state"]
            assert stored["slow_state"] == emitted["slow_state"]
            assert float(stored["vw_forecast_frozen"]) == float(emitted["vw_forecast_frozen"])
            assert stored["reason_code"] == reason
            assert stored["action_state"] is None
            assert stored["engine_version"] == "gold-r4-direction-engine@0.1.0"
            assert stored["config_version"] == config["version"]
            assert stored["config_hash"] == config_hash

            # No synthetic state/schema may survive this protected smoke test.
            conn.rollback()
            with conn.cursor() as cur:
                post = {name: _exists(cur, name) for name in TABLES}
                conn.rollback()
            assert post == pre, f"R4_ADAPTER_ROLLBACK_SCHEMA_MISMATCH pre={pre} post={post}"

        print(
            "R4_1_DECISION_ADAPTER_SMOKE_PASS "
            "engine_repeatability=PASS state_to_payload=PASS provenance_binding=PASS "
            "store_roundtrip=PASS idempotency=PASS action_mapping_guard=PASS rollback=PASS"
        )
        return 0
    except Exception as exc:
        print(f"R4_1_DECISION_ADAPTER_SMOKE_FAILED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
