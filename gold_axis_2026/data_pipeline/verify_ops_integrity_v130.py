from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

KNOWN_LEGACY_DUPLICATE = {
    "series_id": "XAU_DAILY_XAUS",
    "observation_ts": datetime(2026, 8, 31, tzinfo=timezone.utc),
    "lineage_id": "68c41f97ba9e2e6ba5f5",
    "value": 4491.2,
    "quality_status": "CANDIDATE_NOT_BENCHMARK",
    "n": 2,
}
REQUIRED_LATEST_TRIGGERS = {
    "hourly:xau",
    "daily:xau",
    "daily:cboe",
    "daily:fed",
    "daily:gpr",
    "daily:fred_indices",
    "daily:twelve_market",
    "daily:twelve_xau_ny17",
}


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _is_known_legacy_duplicate(row: dict) -> bool:
    return (
        row["series_id"] == KNOWN_LEGACY_DUPLICATE["series_id"]
        and row["observation_ts"] == KNOWN_LEGACY_DUPLICATE["observation_ts"]
        and row["lineage_id"] == KNOWN_LEGACY_DUPLICATE["lineage_id"]
        and abs(float(row["value"]) - KNOWN_LEGACY_DUPLICATE["value"]) < 1e-9
        and row["quality_status"] == KNOWN_LEGACY_DUPLICATE["quality_status"]
        and int(row["n"]) == KNOWN_LEGACY_DUPLICATE["n"]
    )


def main() -> int:
    report: dict = {"audit": "GOLD_CONTROL_V130_OPS_INTEGRITY", "database_writes": "NONE"}
    with psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")

            cur.execute("""
                WITH checks AS (
                    SELECT 'observations_missing_run' k, COUNT(*)::bigint n
                    FROM observations o LEFT JOIN retrieval_runs r ON r.run_id=o.run_id
                    WHERE o.run_id IS NOT NULL AND r.run_id IS NULL
                    UNION ALL SELECT 'observations_missing_series',COUNT(*)
                    FROM observations o LEFT JOIN source_registry s ON s.series_id=o.series_id WHERE s.series_id IS NULL
                    UNION ALL SELECT 'quality_missing_run',COUNT(*)
                    FROM quality_events q LEFT JOIN retrieval_runs r ON r.run_id=q.run_id WHERE q.run_id IS NOT NULL AND r.run_id IS NULL
                    UNION ALL SELECT 'quality_missing_series',COUNT(*)
                    FROM quality_events q LEFT JOIN source_registry s ON s.series_id=q.series_id WHERE q.series_id IS NOT NULL AND s.series_id IS NULL
                    UNION ALL SELECT 'input_member_missing_set',COUNT(*)
                    FROM forecast_input_set_members m LEFT JOIN forecast_input_sets s ON s.input_set_id=m.input_set_id WHERE s.input_set_id IS NULL
                    UNION ALL SELECT 'input_member_missing_snapshot',COUNT(*)
                    FROM forecast_input_set_members m LEFT JOIN forecast_input_snapshots f ON f.id=m.snapshot_id WHERE f.id IS NULL
                    UNION ALL SELECT 'expert_missing_input_set',COUNT(*)
                    FROM monthly_expert_forecasts e LEFT JOIN forecast_input_sets s ON s.input_set_id=e.input_set_id WHERE s.input_set_id IS NULL
                    UNION ALL SELECT 'expert_array_missing_snapshot',COUNT(*)
                    FROM monthly_expert_forecasts e CROSS JOIN LATERAL unnest(e.input_snapshot_ids) u(snapshot_id)
                    LEFT JOIN forecast_input_snapshots f ON f.id=u.snapshot_id WHERE f.id IS NULL
                    UNION ALL SELECT 'derived_output_missing_run',COUNT(*)
                    FROM engine_execution_derived_outputs x LEFT JOIN engine_execution_runs r ON r.run_id=x.run_id WHERE r.run_id IS NULL
                    UNION ALL SELECT 'derived_output_missing_feature',COUNT(*)
                    FROM engine_execution_derived_outputs x LEFT JOIN derived_feature_snapshots d ON d.id=x.derived_feature_snapshot_id WHERE d.id IS NULL
                    UNION ALL SELECT 'expert_output_missing_run',COUNT(*)
                    FROM engine_execution_expert_outputs x LEFT JOIN engine_execution_runs r ON r.run_id=x.run_id WHERE r.run_id IS NULL
                    UNION ALL SELECT 'expert_output_missing_forecast',COUNT(*)
                    FROM engine_execution_expert_outputs x LEFT JOIN monthly_expert_forecasts e ON e.id=x.monthly_expert_forecast_id WHERE e.id IS NULL
                    UNION ALL SELECT 'decision_output_missing_run',COUNT(*)
                    FROM engine_execution_decision_outputs x LEFT JOIN engine_execution_runs r ON r.run_id=x.run_id WHERE r.run_id IS NULL
                    UNION ALL SELECT 'unlinked_derived_features',COUNT(*)
                    FROM derived_feature_snapshots d LEFT JOIN engine_execution_derived_outputs x ON x.derived_feature_snapshot_id=d.id WHERE x.derived_feature_snapshot_id IS NULL
                    UNION ALL SELECT 'multiply_linked_derived_features',COUNT(*)
                    FROM (SELECT derived_feature_snapshot_id FROM engine_execution_derived_outputs GROUP BY 1 HAVING COUNT(*)<>1) z
                    UNION ALL SELECT 'unlinked_expert_forecasts',COUNT(*)
                    FROM monthly_expert_forecasts e LEFT JOIN engine_execution_expert_outputs x ON x.monthly_expert_forecast_id=e.id WHERE x.monthly_expert_forecast_id IS NULL
                    UNION ALL SELECT 'multiply_linked_expert_forecasts',COUNT(*)
                    FROM (SELECT monthly_expert_forecast_id FROM engine_execution_expert_outputs GROUP BY 1 HAVING COUNT(*)<>1) z
                    UNION ALL SELECT 'unlinked_input_snapshots',COUNT(*)
                    FROM forecast_input_snapshots f LEFT JOIN forecast_input_set_members m ON m.snapshot_id=f.id WHERE m.snapshot_id IS NULL
                    UNION ALL SELECT 'multiply_linked_input_snapshots',COUNT(*)
                    FROM (SELECT snapshot_id FROM forecast_input_set_members GROUP BY 1 HAVING COUNT(*)<>1) z
                    UNION ALL SELECT 'expert_set_fingerprint_mismatch',COUNT(*)
                    FROM monthly_expert_forecasts e JOIN forecast_input_sets s ON s.input_set_id=e.input_set_id
                    WHERE e.input_fingerprint<>s.input_fingerprint
                    UNION ALL SELECT 'expert_set_identity_mismatch',COUNT(*)
                    FROM monthly_expert_forecasts e JOIN forecast_input_sets s ON s.input_set_id=e.input_set_id
                    WHERE e.expert_id<>s.expert_id OR e.model_name<>s.model_name OR e.model_version<>s.model_version
                       OR e.forecast_origin<>s.forecast_origin OR e.target_month<>s.target_month
                       OR e.forecast_track<>s.forecast_track OR e.evidence_class<>s.evidence_class
                )
                SELECT k,n FROM checks ORDER BY k
            """)
            checks = {r["k"]: int(r["n"]) for r in cur.fetchall()}
            bad = {k: v for k, v in checks.items() if v != 0}
            if bad:
                raise AssertionError(f"V130_RELATIONSHIP_INTEGRITY_FAILURE:{bad}")

            cur.execute("""
                SELECT series_id,observation_ts,lineage_id,value,quality_status,COUNT(*)::bigint AS n
                FROM observations
                GROUP BY series_id,observation_ts,lineage_id,value,quality_status
                HAVING COUNT(*)>1
                ORDER BY series_id,observation_ts,lineage_id
            """)
            duplicate_rows = [dict(r) for r in cur.fetchall()]
            unexpected_duplicates = [r for r in duplicate_rows if not _is_known_legacy_duplicate(r)]
            if unexpected_duplicates:
                raise AssertionError(f"V130_UNEXPECTED_EXACT_DUPLICATE:{unexpected_duplicates}")
            duplicate = {
                "duplicate_groups": len(duplicate_rows),
                "duplicate_extra_rows": sum(int(r["n"]) - 1 for r in duplicate_rows),
                "affected_series": len({r["series_id"] for r in duplicate_rows}),
                "legacy_exception_only": bool(duplicate_rows),
            }

            cur.execute("""
                SELECT 'decision_events' object,COUNT(*)::bigint n FROM decision_events
                UNION ALL SELECT 'decision_runs',COUNT(*) FROM decision_runs
                UNION ALL SELECT 'decision_signal_snapshots',COUNT(*) FROM decision_signal_snapshots
                UNION ALL SELECT 'monthly_forecast_contracts',COUNT(*) FROM monthly_forecast_contracts
                ORDER BY object
            """)
            authority_counts = {r["object"]: int(r["n"]) for r in cur.fetchall()}
            if any(authority_counts.values()):
                raise AssertionError(f"V130_UNAUTHORIZED_DECISION_OR_CANONICAL_STATE:{authority_counts}")

            cur.execute("""
                SELECT trigger_type,status,finished_at,observations_read,observations_written,
                       pipeline_version,git_sha,metadata
                FROM (
                    SELECT *,ROW_NUMBER() OVER (PARTITION BY trigger_type ORDER BY finished_at DESC NULLS LAST,started_at DESC) rn
                    FROM retrieval_runs
                    WHERE trigger_type IN (
                        'hourly:xau','daily:xau','daily:cboe','daily:fed','daily:gpr',
                        'daily:fred_indices','daily:twelve_market','daily:twelve_xau_ny17'
                    )
                ) x WHERE rn=1 ORDER BY trigger_type
            """)
            latest_runs = [dict(r) for r in cur.fetchall()]
            latest_by_trigger = {r["trigger_type"]: r for r in latest_runs}
            missing_triggers = sorted(REQUIRED_LATEST_TRIGGERS - set(latest_by_trigger))
            non_success = {
                k: v["status"] for k, v in latest_by_trigger.items()
                if v["status"] != "SUCCESS"
            }
            if missing_triggers or non_success:
                raise AssertionError(
                    f"V130_LATEST_INGESTION_HEALTH_FAILURE:missing={missing_triggers}:non_success={non_success}"
                )

            provenance_mismatches = []
            for row in latest_runs:
                metadata = row.get("metadata") or {}
                code_sha = metadata.get("code_git_sha") if isinstance(metadata, dict) else None
                if code_sha and row.get("git_sha") != code_sha:
                    provenance_mismatches.append({
                        "trigger_type": row["trigger_type"],
                        "git_sha": row.get("git_sha"),
                        "code_git_sha": code_sha,
                    })
            if provenance_mismatches:
                raise AssertionError(f"V130_CODE_SHA_PROVENANCE_MISMATCH:{provenance_mismatches}")

            cur.execute("""
                SELECT series_id,MAX(observation_ts) latest_observation_ts,MAX(retrieved_at) latest_retrieved_at,COUNT(*)::bigint rows
                FROM canonical_latest
                WHERE series_id IN ('XAU_EOD_TWELVE_NY17','XAU_SPOT_XAUS','GVZ_CBOE','DGS10_FRB_H15','EFFR_NYFED')
                GROUP BY series_id ORDER BY series_id
            """)
            freshness = [dict(r) for r in cur.fetchall()]

        conn.rollback()

    report["status"] = "PASS"
    report["relationship_checks"] = checks
    report["exact_duplicates"] = duplicate
    report["authority_counts"] = authority_counts
    report["latest_ingestion_runs"] = latest_runs
    report["provenance_mismatches"] = provenance_mismatches
    report["freshness_observations"] = freshness
    print(json.dumps(report, indent=2, default=str))
    print("GOLD_CONTROL_V130_OPS_INTEGRITY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
