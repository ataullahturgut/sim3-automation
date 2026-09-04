from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "stage4b" / "aug31_replay_expansion_v2_evidence.json"
CHANGE_CONTROL = ROOT / "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md"
ENGINEERING = ROOT / "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_ENGINEERING_EVIDENCE_2026-09-04.md"
TARGET_CONTEXT = "2026-09"
EVIDENCE_CLASS = "HISTORICAL_REPLAY"
FEATURE_VERSION = "AUG31_REPLAY_EXPANSION_V2"
CONTRACT_MARKER = "FROZEN_BEFORE_AUG31_EXPANSION_RESULT"
EXPECTED_ARTIFACT_DIGEST = "sha256:f90a38ba6239931b272a5cff9f631f9bc9bb3c04dbc5ff10ffbf5f4fc4bb9b20"
EXPECTED_DRY_RUN_SHA = "f255fbcc7f8e3513242fe9f99cfc380d234dc94e"

FEATURE_ENGINE: dict[str, tuple[str, str, str]] = {
    "AUG31_REPLAY_CAUSAL_PATCH_SEPTEMBER_FORECAST": (
        "CAUSAL_PATCH",
        "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "MONTHLY_H1_EXPERT_REPLAY_REFERENCE",
    ),
    "AUG31_REPLAY_CAUSAL_PATCH_PREDICTED_LOG_RETURN": (
        "CAUSAL_PATCH",
        "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
        "MONTHLY_H1_EXPERT_REPLAY_REFERENCE",
    ),
    "AUG31_REPLAY_EMERGENCY_LEVEL": (
        "EMERGENCY_LEVEL",
        "R4_1_EMERGENCY_LEVEL_REPLAY_V1",
        "EMERGENCY_CONTEXT_REPLAY",
    ),
    "AUG31_REPLAY_EMERGENCY_REVERSAL": (
        "EMERGENCY_REVERSAL",
        "R4_1_EMERGENCY_REVERSAL_REPLAY_V1",
        "EMERGENCY_CONTEXT_REPLAY",
    ),
    "AUG31_REPLAY_BOCPD_SUCCESSOR_STATE": (
        "BOCPD",
        "BOCPD_RETURN_SUCCESSOR_V1",
        "REGIME_BREAK_SUCCESSOR_REPLAY_CONTEXT",
    ),
    "AUG31_REPLAY_BOCPD_SUCCESSOR_RESET_FRACTION": (
        "BOCPD",
        "BOCPD_RETURN_SUCCESSOR_V1",
        "REGIME_BREAK_SUCCESSOR_REPLAY_CONTEXT",
    ),
}


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _load() -> dict[str, Any]:
    if CONTRACT_MARKER not in CHANGE_CONTROL.read_text(encoding="utf-8"):
        raise RuntimeError("AUG31_REPLAY_V2_CHANGE_CONTROL_NOT_FROZEN")
    if "PASS_READ_ONLY_REPLAY_CONSTRUCTION" not in ENGINEERING.read_text(encoding="utf-8"):
        raise RuntimeError("AUG31_REPLAY_V2_ENGINEERING_EVIDENCE_NOT_FROZEN")
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if data.get("artifact_digest") != EXPECTED_ARTIFACT_DIGEST:
        raise RuntimeError("AUG31_REPLAY_V2_ARTIFACT_DIGEST_MISMATCH")
    if data.get("dry_run_git_commit") != EXPECTED_DRY_RUN_SHA or data.get("dry_run_pass") is not True:
        raise RuntimeError("AUG31_REPLAY_V2_DRY_RUN_AUTHORITY_MISMATCH")
    if data.get("target_context") != TARGET_CONTEXT:
        raise RuntimeError("AUG31_REPLAY_V2_TARGET_MISMATCH")
    if data.get("prospective_claim") is not False or data.get("canonical_authority") is not False:
        raise RuntimeError("AUG31_REPLAY_V2_AUTHORITY_FLAGS_INVALID")
    if data["patch"]["daily_max_date"] >= "2026-08-31":
        raise RuntimeError("AUG31_REPLAY_V2_PATCH_PIT_INVALID")
    if data["emergency"]["level"] != "NEUTRAL" or data["emergency"]["reversal"] != "OFF":
        raise RuntimeError("AUG31_REPLAY_V2_EMERGENCY_MONTH_OPEN_INVALID")
    if data["archived_bocpd"]["unchanged"] is not True:
        raise RuntimeError("AUG31_REPLAY_V2_ARCHIVED_BOCPD_GUARD_INVALID")
    return data


def _authority_counts(cur) -> dict[str, int]:
    out = {}
    for table in ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events"):
        cur.execute(f"select count(*)::int as n from {table}")
        out[table] = int(cur.fetchone()["n"])
    return out


def _runtime_state(cur) -> dict[str, Any]:
    cur.execute("select runtime_status,count(*)::int as n from latest_engine_runtime_state group by runtime_status")
    counts = {str(row["runtime_status"]): int(row["n"]) for row in cur.fetchall()}
    cur.execute("select count(*)::int as n from latest_engine_runtime_state where direction_vote_permitted")
    votes = int(cur.fetchone()["n"])
    return {"counts": counts, "direction_votes": votes}


def _expected_features(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    common = {
        "contract": CHANGE_CONTROL.name,
        "engineering_evidence": ENGINEERING.name,
        "machine_evidence": EVIDENCE.name,
        "artifact_digest": data["artifact_digest"],
        "historical_replay": True,
        "prospective_claim": False,
        "current_runtime_authority": False,
        "canonical_authority": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
        "target_context": TARGET_CONTEXT,
        "state_as_of": data["information_cutoff"],
        "replay_executed_at": data["replay_executed_at"],
        "retrieved_post_origin": True,
        "direction_vote_permitted": False,
        "decision_store_write": "NONE",
        "canonical_forecast_write": "NONE",
    }
    patch_lineage = {
        "input_fingerprint": data["patch"]["input_fingerprint"],
        "dry_run_git_commit": data["dry_run_git_commit"],
        "dry_run_workflow_run": data["dry_run_workflow_run"],
        "artifact_digest": data["artifact_digest"],
        "daily_max_date": data["patch"]["daily_max_date"],
        "source_meta": data["patch"]["source_meta"],
        "retrieved_post_origin": True,
    }
    emergency_lineage = {
        **patch_lineage,
        "monthly_reference": data["emergency"]["monthly_reference"],
        "reference_identity": data["emergency"]["reference_identity"],
        "reference_evidence": data["emergency"]["reference_evidence"],
    }
    bocpd_lineage = {
        "input_fingerprint": _canonical_hash({
            "context_identity": data["bocpd_successor"]["context_identity"],
            "source_series": data["bocpd_successor"]["source_series"],
            "august_daily_level": data["patch"]["august_daily_level"],
            "prior": data["bocpd_successor"]["prior"],
            "expected_run_length": data["bocpd_successor"]["expected_run_length"],
        }),
        "artifact_digest": data["artifact_digest"],
        "context_identity": data["bocpd_successor"]["context_identity"],
        "successor_id": data["bocpd_successor"]["successor_id"],
        "source_series": data["bocpd_successor"]["source_series"],
        "source_bridge_used": data["bocpd_successor"]["source_bridge_used"],
        "retrieved_post_origin": data["bocpd_successor"]["retrieved_post_origin"],
    }
    return {
        "AUG31_REPLAY_CAUSAL_PATCH_SEPTEMBER_FORECAST": {
            "value_num": float(data["patch"]["forecast"]),
            "value_text": None,
            "lineage": patch_lineage,
            "metadata": {**common, "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE", "unit": "USD/oz", "forecast_origin": data["information_cutoff"], "model_version": data["emergency"]["reference_identity"]},
        },
        "AUG31_REPLAY_CAUSAL_PATCH_PREDICTED_LOG_RETURN": {
            "value_num": float(data["patch"]["predicted_return"]),
            "value_text": None,
            "lineage": patch_lineage,
            "metadata": {**common, "role": "PATCH_REPLAY_DIAGNOSTIC", "unit": "log_return"},
        },
        "AUG31_REPLAY_EMERGENCY_LEVEL": {
            "value_num": None,
            "value_text": str(data["emergency"]["level"]),
            "lineage": emergency_lineage,
            "metadata": {**common, "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE", "reason": data["emergency"]["reason"], "monthly_reference": data["emergency"]["monthly_reference"]},
        },
        "AUG31_REPLAY_EMERGENCY_REVERSAL": {
            "value_num": None,
            "value_text": str(data["emergency"]["reversal"]),
            "lineage": emergency_lineage,
            "metadata": {**common, "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE", "reason": data["emergency"]["reason"], "monthly_reference": data["emergency"]["monthly_reference"]},
        },
        "AUG31_REPLAY_BOCPD_SUCCESSOR_STATE": {
            "value_num": None,
            "value_text": str(data["bocpd_successor"]["state"]),
            "lineage": bocpd_lineage,
            "metadata": {
                **common,
                "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",
                "successor_id": data["bocpd_successor"]["successor_id"],
                "context_identity": data["bocpd_successor"]["context_identity"],
                "archived_engine_status": data["archived_bocpd"]["status"],
                "validation_claim": False,
                "production_claim": False,
                "source_series": data["bocpd_successor"]["source_series"],
            },
        },
        "AUG31_REPLAY_BOCPD_SUCCESSOR_RESET_FRACTION": {
            "value_num": float(data["bocpd_successor"]["reset_fraction"]),
            "value_text": None,
            "lineage": bocpd_lineage,
            "metadata": {
                **common,
                "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT",
                "successor_id": data["bocpd_successor"]["successor_id"],
                "map_reset": data["bocpd_successor"]["map_reset"],
                "map_run": data["bocpd_successor"]["map_run"],
                "previous_map_run": data["bocpd_successor"]["previous_map_run"],
                "expected_uninterrupted_run": data["bocpd_successor"]["expected_uninterrupted_run"],
                "expected_run_length": data["bocpd_successor"]["expected_run_length"],
                "log_return": data["bocpd_successor"]["log_return"],
                "validation_claim": False,
                "production_claim": False,
            },
        },
    }


def _existing(cur) -> dict[str, dict[str, Any]]:
    names = list(FEATURE_ENGINE)
    cur.execute(
        """
        select id,feature_name,feature_version,value_num,value_text,input_lineage,metadata
        from derived_feature_snapshots
        where feature_name=any(%s)
          and metadata->>'contract'=%s
          and metadata->>'target_context'=%s
          and metadata->>'state_as_of'=%s
        order by feature_name,calculation_ts desc,id desc
        """,
        (names, CHANGE_CONTROL.name, TARGET_CONTEXT, "2026-08-31T21:00:00+00:00"),
    )
    out: dict[str, dict[str, Any]] = {}
    for row in cur.fetchall():
        name = str(row["feature_name"])
        if name in out:
            raise RuntimeError(f"AUG31_REPLAY_V2_DUPLICATE_FEATURE:{name}")
        out[name] = dict(row)
    return out


def _verify_existing(existing: dict[str, dict[str, Any]], expected: dict[str, dict[str, Any]]) -> None:
    if not existing:
        return
    if set(existing) != set(expected):
        raise RuntimeError(f"AUG31_REPLAY_V2_PARTIAL_EXISTING:{sorted(existing)}")
    for name, spec in expected.items():
        row = existing[name]
        if row.get("value_text") != spec.get("value_text"):
            raise RuntimeError(f"AUG31_REPLAY_V2_EXISTING_TEXT_CONFLICT:{name}")
        a, b = row.get("value_num"), spec.get("value_num")
        if a is None and b is None:
            pass
        elif a is None or b is None or abs(float(a) - float(b)) > 1e-12:
            raise RuntimeError(f"AUG31_REPLAY_V2_EXISTING_NUM_CONFLICT:{name}")
        if (row.get("input_lineage") or {}).get("input_fingerprint") != spec["lineage"]["input_fingerprint"]:
            raise RuntimeError(f"AUG31_REPLAY_V2_EXISTING_LINEAGE_CONFLICT:{name}")


def _insert(cur, data: dict[str, Any], expected: dict[str, dict[str, Any]], git_sha: str) -> dict[str, Any]:
    calc_ts = datetime.fromisoformat(data["replay_executed_at"])
    input_cutoff = datetime.fromisoformat(data["information_cutoff"])
    feature_ids: dict[str, int] = {}
    per_engine: dict[str, list[int]] = {}

    for name, spec in expected.items():
        engine_id, version, _ = FEATURE_ENGINE[name]
        cur.execute(
            """
            insert into derived_feature_snapshots
              (feature_name,feature_version,calculation_ts,input_cutoff,value_num,value_text,
               git_commit,input_lineage,quality_status,metadata)
            values (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
            returning id
            """,
            (
                name,
                FEATURE_VERSION,
                calc_ts,
                input_cutoff,
                spec.get("value_num"),
                spec.get("value_text"),
                git_sha,
                json.dumps(spec["lineage"], sort_keys=True),
                EVIDENCE_CLASS,
                json.dumps(spec["metadata"], sort_keys=True),
            ),
        )
        fid = int(cur.fetchone()["id"])
        feature_ids[name] = fid
        per_engine.setdefault(engine_id, []).append(fid)

    run_ids: dict[str, str] = {}
    for engine_id, ids in per_engine.items():
        names = [name for name, (eid, _, _) in FEATURE_ENGINE.items() if eid == engine_id]
        _, version, role = FEATURE_ENGINE[names[0]]
        fingerprints = sorted(expected[name]["lineage"]["input_fingerprint"] for name in names)
        run_fingerprint = _canonical_hash({"engine_id": engine_id, "version": version, "feature_fingerprints": fingerprints, "state_as_of": data["information_cutoff"]})
        run_id = str(uuid.uuid4())
        if engine_id == "CAUSAL_PATCH":
            status = "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE"
            extra = {"forecast_value": data["patch"]["forecast"], "unit": "USD/oz", "forecast_origin": data["information_cutoff"], "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE"}
        elif engine_id in {"EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"}:
            status = "HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE"
            extra = {"emergency_level": data["emergency"]["level"], "emergency_reversal": data["emergency"]["reversal"], "reason": data["emergency"]["reason"], "monthly_reference": data["emergency"]["monthly_reference"], "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE"}
        else:
            status = "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT_AVAILABLE"
            extra = {"successor_id": data["bocpd_successor"]["successor_id"], "successor_state": data["bocpd_successor"]["state"], "context_identity": data["bocpd_successor"]["context_identity"], "archived_engine_status": data["archived_bocpd"]["status"], "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT", "validation_claim": False, "production_claim": False}
        metadata = {
            "contract": CHANGE_CONTROL.name,
            "engineering_evidence": ENGINEERING.name,
            "machine_evidence": EVIDENCE.name,
            "artifact_digest": data["artifact_digest"],
            "historical_replay": True,
            "information_cutoff": data["information_cutoff"],
            "replay_executed_at": data["replay_executed_at"],
            "prospective_claim": False,
            "prospective_h1_claim": False,
            "current_runtime_authority": False,
            "canonical_authority": False,
            "direction_vote_permitted": False,
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
            "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
            "decision_store_write": "NONE",
            "canonical_forecast_write": "NONE",
            **extra,
        }
        cur.execute(
            """
            insert into engine_execution_runs
              (run_id,engine_id,engine_version,engine_role,as_of,target_context,evidence_class,
               runtime_status,status_code,direction_vote_permitted,git_commit,input_fingerprint,metadata)
            values (%s,%s,%s,%s,%s,%s,%s,'ISSUED',%s,false,%s,%s,%s::jsonb)
            """,
            (run_id, engine_id, version, role, calc_ts, TARGET_CONTEXT, EVIDENCE_CLASS, status, git_sha, run_fingerprint, json.dumps(metadata, sort_keys=True)),
        )
        for fid in ids:
            cur.execute("insert into engine_execution_derived_outputs(run_id,derived_feature_snapshot_id) values (%s,%s)", (run_id, fid))
        run_ids[engine_id] = run_id
    return {"feature_ids": feature_ids, "run_ids": run_ids}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    data = _load()
    expected = _expected_features(data)
    url = str(os.environ.get("NEON_DATABASE_URL", "")).strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    git_sha = _git_sha()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*)::int as n from information_schema.triggers where event_object_schema='public' and event_object_table='derived_feature_snapshots' and trigger_name='trg_derived_feature_snapshots_immutable'")
            if int(cur.fetchone()["n"]) != 1:
                raise RuntimeError("AUG31_REPLAY_V2_IMMUTABILITY_GUARD_MISSING")
            runtime_before = _runtime_state(cur)
            authority_before = _authority_counts(cur)
            if runtime_before != {"counts": {"ACTIVE": 4, "BLOCKED": 3, "WAITING": 5}, "direction_votes": 3}:
                raise RuntimeError(f"AUG31_REPLAY_V2_RUNTIME_PRECONDITION_CHANGED:{runtime_before}")
            if any(authority_before.values()):
                raise RuntimeError(f"AUG31_REPLAY_V2_AUTHORITY_PRECONDITION_CHANGED:{authority_before}")
            existing = _existing(cur)
            _verify_existing(existing, expected)
            if not args.persist:
                conn.rollback()
                print("AUG31_REPLAY_EXPANSION_V2_PERSIST_PREFLIGHT_PASS writes=NONE")
                return 0
            if existing:
                conn.rollback()
                print("AUG31_REPLAY_EXPANSION_V2_ALREADY_PRESENT_PASS writes=NONE")
                return 0
            inserted = _insert(cur, data, expected, git_sha)
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            stored = _existing(cur)
            _verify_existing(stored, expected)
            if len(stored) != len(expected):
                raise RuntimeError("AUG31_REPLAY_V2_POST_WRITE_FEATURE_COUNT_INVALID")
            cur.execute(
                """
                select engine_id,count(*)::int as n
                from engine_execution_runs
                where evidence_class='HISTORICAL_REPLAY'
                  and metadata->>'contract'=%s
                  and metadata->>'information_cutoff'=%s
                group by engine_id order by engine_id
                """,
                (CHANGE_CONTROL.name, data["information_cutoff"]),
            )
            runs = {str(r["engine_id"]): int(r["n"]) for r in cur.fetchall()}
            if runs != {"BOCPD": 1, "CAUSAL_PATCH": 1, "EMERGENCY_LEVEL": 1, "EMERGENCY_REVERSAL": 1}:
                raise RuntimeError(f"AUG31_REPLAY_V2_POST_WRITE_RUNS_INVALID:{runs}")
            runtime_after = _runtime_state(cur)
            authority_after = _authority_counts(cur)
            if runtime_after != runtime_before:
                raise RuntimeError(f"AUG31_REPLAY_V2_OPERATIONAL_RUNTIME_CHANGED:{runtime_before}:{runtime_after}")
            if authority_after != authority_before:
                raise RuntimeError(f"AUG31_REPLAY_V2_AUTHORITY_COUNTS_CHANGED:{authority_before}:{authority_after}")
        conn.rollback()

    print(json.dumps({"status": "AUG31_REPLAY_EXPANSION_V2_PERSIST_PASS", "inserted": inserted, "operational_runtime": runtime_after, "authority_counts": authority_after}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
