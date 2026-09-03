from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

import aug31_eod_state_historical_replay as core


def _authority_counts(cur) -> dict[str, int]:
    cur.execute("SELECT count(*) AS n FROM monthly_forecast_contracts")
    monthly_contracts = int(cur.fetchone()["n"])
    cur.execute("SELECT count(*) AS n FROM decision_signal_snapshots")
    decision_snapshots = int(cur.fetchone()["n"])
    cur.execute("SELECT count(*) AS n FROM decision_runs")
    decision_runs = int(cur.fetchone()["n"])
    cur.execute("SELECT count(*) AS n FROM decision_events")
    decision_events = int(cur.fetchone()["n"])
    return {
        "monthly_forecast_contracts": monthly_contracts,
        "decision_signal_snapshots": decision_snapshots,
        "decision_runs": decision_runs,
        "decision_events": decision_events,
    }


def _validate_operational_state(cur) -> None:
    cur.execute("SELECT count(*) AS n FROM latest_engine_runtime_state")
    if int(cur.fetchone()["n"]) != 12:
        raise RuntimeError("AUG31_STATE_REPLAY_OPERATIONAL_RUNTIME_COUNT_CHANGED")
    cur.execute(
        """
        SELECT runtime_status, count(*) AS n
        FROM latest_engine_runtime_state
        GROUP BY runtime_status
        """
    )
    counts = {str(r["runtime_status"]): int(r["n"]) for r in cur.fetchall()}
    if counts != {"ACTIVE": 4, "WAITING": 3, "BLOCKED": 5}:
        raise RuntimeError(f"AUG31_STATE_REPLAY_RUNTIME_DISTRIBUTION_CHANGED:{counts}")
    cur.execute("SELECT count(*) AS n FROM latest_engine_runtime_state WHERE direction_vote_permitted")
    if int(cur.fetchone()["n"]) != 3:
        raise RuntimeError("AUG31_STATE_REPLAY_DIRECTION_VOTE_COUNT_CHANGED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    if not core.CONTRACT.is_file() or core.CONTRACT_MARKER not in core.CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("AUG31_STATE_REPLAY_CONTRACT_NOT_FROZEN")
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    calc_ts = datetime.now(timezone.utc)
    sha = core.git_commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(distinct trigger_name) AS n
                FROM information_schema.triggers
                WHERE event_object_schema='public'
                  AND event_object_table='derived_feature_snapshots'
                  AND trigger_name='trg_derived_feature_snapshots_immutable'
                """
            )
            if int(cur.fetchone()["n"]) != 1:
                raise RuntimeError("AUG31_STATE_REPLAY_IMMUTABILITY_GUARD_MISSING")

            _validate_operational_state(cur)
            authority_before = _authority_counts(cur)
            if any(authority_before.values()):
                raise RuntimeError(f"AUG31_STATE_REPLAY_AUTHORITY_PRECONDITION_FAILED:{authority_before}")

            xau = core._load_xau(cur)
            gvz_row = core._load_gvz(cur)
            state = core.calculate_state(xau, gvz_row)
            expected = core._expected_features(state, core._xau_lineage(xau), core._gvz_lineage(gvz_row))
            existing = core._existing(cur)
            core._verify_existing_exact(existing, expected)

            summary = core.build_summary(state, "DRY_RUN_PASS")
            summary["authority_counts"] = authority_before
            summary["xau_retrieved_post_origin"] = bool(next(iter(expected.values()))["lineage"].get("retrieved_post_origin"))
            summary["gvz_retrieved_post_origin"] = bool(expected["AUG31_REPLAY_GVZ_VALUE"]["lineage"].get("retrieved_post_origin"))

            if not args.persist:
                conn.rollback()
                print(json.dumps(summary, indent=2, sort_keys=True))
                print("AUG31_EOD_STATE_HISTORICAL_REPLAY_V2_DRY_RUN_PASS")
                return 0

            if existing:
                conn.rollback()
                summary["status"] = "IDEMPOTENT_ALREADY_PRESENT"
                print(json.dumps(summary, indent=2, sort_keys=True))
                print("AUG31_EOD_STATE_HISTORICAL_REPLAY_V2_ALREADY_PRESENT_PASS")
                return 0

            inserted = core._insert_replay(cur, expected, sha, calc_ts)
            if len(inserted) != 7:
                raise RuntimeError(f"AUG31_STATE_REPLAY_INSERT_COUNT:{len(inserted)}")
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            existing = core._existing(cur)
            core._verify_existing_exact(existing, expected)
            if len(existing) != 7:
                raise RuntimeError(f"AUG31_STATE_REPLAY_POST_WRITE_FEATURE_COUNT:{len(existing)}")
            cur.execute(
                """
                SELECT count(*) AS n
                FROM engine_execution_runs
                WHERE evidence_class='HISTORICAL_REPLAY'
                  AND metadata->>'contract'=%s
                  AND metadata->>'state_as_of'=%s
                """,
                (core.CONTRACT.name, core.STATE_AS_OF.isoformat()),
            )
            replay_runs = int(cur.fetchone()["n"])
            if replay_runs != 4:
                raise RuntimeError(f"AUG31_STATE_REPLAY_RUN_COUNT:{replay_runs}")
            cur.execute(
                """
                SELECT count(*) AS n
                FROM engine_execution_derived_outputs o
                JOIN engine_execution_runs r ON r.run_id=o.run_id
                WHERE r.evidence_class='HISTORICAL_REPLAY'
                  AND r.metadata->>'contract'=%s
                  AND r.metadata->>'state_as_of'=%s
                """,
                (core.CONTRACT.name, core.STATE_AS_OF.isoformat()),
            )
            links = int(cur.fetchone()["n"])
            if links != 7:
                raise RuntimeError(f"AUG31_STATE_REPLAY_LINK_COUNT:{links}")
            _validate_operational_state(cur)
            authority_after = _authority_counts(cur)
            if authority_after != authority_before:
                raise RuntimeError(f"AUG31_STATE_REPLAY_AUTHORITY_COUNTS_CHANGED:{authority_before}:{authority_after}")
        conn.rollback()

    summary = core.build_summary(state, "INSERTED_VERIFIED")
    summary.update(
        {
            "inserted_feature_count": 7,
            "engine_execution_run_count": 4,
            "derived_output_link_count": 7,
            "authority_counts": authority_after,
        }
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("AUG31_EOD_STATE_HISTORICAL_REPLAY_V2_PERSIST_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
