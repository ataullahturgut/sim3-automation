from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

from data_evidence_spine import record_engine_execution, spine_schema_ready
from multi_expert_forecast import EXPERT_REGISTRY


AUDIT_EVIDENCE = "RUNTIME_GOVERNANCE_AUDIT"

# v1.41 current governed inventory. VW/MSVR Successor V1 is ACTIVE as a
# research-shadow current-month reference reconstructed strictly from the
# completed 2026-08-31 information boundary. This does not relabel the result
# as a forecast issued on 2026-08-31 and grants no selector/ensemble/action
# authority. The separate 2026-09-30 -> 2026-10 prospective gate remains a
# later validation milestone, not a blocker for the September reference.
STATUS_SPECS = {
    "CAUSAL_PATCH": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_EXPERT", False),
    "VW_MIDAS_MSVR_SUCCESSOR_V1": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_EXPERT", False),
    "MOMENTUM_3M": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_EXPERT", False),
    "RANDOM_WALK": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE", "MONTHLY_H1_BENCHMARK", False),
    "EMERGENCY_LEVEL": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE", "EMERGENCY_CONTEXT", False),
    "EMERGENCY_REVERSAL": ("ACTIVE", "ACTIVE_HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE", "EMERGENCY_CONTEXT", False),
}

STATIC_VERSIONS = {
    "VW_MIDAS_MSVR_SUCCESSOR_V1": "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "EMERGENCY_LEVEL": "R4_2_PATCH_EXPERT_REFERENCE_READY_V1",
    "EMERGENCY_REVERSAL": "R4_2_PATCH_EXPERT_REFERENCE_READY_V1",
}

ACTIVE_SUCCESSORS = (
    "BOCPD_RETURN_SUCCESSOR_V1",
    "MACRO_EVENT_SUCCESSOR_V2",
)

CONTEXT_FEATURES = {
    "MONTHLY_DIRECTION_3M": ("MONTHLY_DIRECTION_3M", "STRATEGIC_DIRECTION_CONTEXT", True),
    "FAST": ("FAST_STATE", "TACTICAL_DIRECTION_CONTEXT", True),
    "SLOW": ("SLOW_STATE", "TACTICAL_DIRECTION_CONTEXT", True),
    "GVZ_RISK": ("GVZ_REGIME", "RISK_ONLY_CONTEXT", False),
}
GVZ_FEATURES = ("GVZ_VALUE", "GVZ_CAP", "GVZ_PANIC", "GVZ_REGIME")

CURRENT_MONTH_REFERENCES = {
    "CAUSAL_PATCH": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-04T13:42:09.025554Z",
        "forecast_value": 4452.046728838838,
        "unit": "USD/oz",
        "input_fingerprint": "1d7669396dfda83062c4adfe9957b96eb76bd5a568a22c703fa841cff4791eb6",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    },
    "VW_MIDAS_MSVR_SUCCESSOR_V1": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "source_origin_boundary": "2026-08-31",
        "replay_executed_at": "2026-09-06T19:18:23Z",
        "forecast_value": 4565.115907930242,
        "unit": "USD/oz",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "selected_config": [1.0, 0.05, 0.5],
        "august_common_days": 26,
        "random_walk_same_origin": 4404.829230769231,
        "reconstruction_workflow_run_id": 34054462706,
        "reconstruction_head_sha": "24bede3ef96ba655ebb2108dc69ccf7dfc7e2f33",
        "reconstruction_artifact_id": 9995535377,
    },
    "MOMENTUM_3M": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-03T19:21:35Z",
        "forecast_value": 4345.814584037808,
        "unit": "USD/oz",
        "input_fingerprint": "79a4665141f2209fc077c1f67ecf3fbb7145df0df41bcbb621bfa77382774c43",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
    },
    "RANDOM_WALK": {
        "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-03T19:21:35Z",
        "forecast_value": 4397.305673870967,
        "unit": "USD/oz",
        "input_fingerprint": "1ab3d6a747d191d44476cec1d772766eb2e801c566213223c8d95a88aaf6fca7",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
    },
    "EMERGENCY_LEVEL": {
        "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-04T13:42:09.025554Z",
        "state_value": "NEUTRAL",
        "monthly_reference": 4452.046728838838,
        "reason": "MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    },
    "EMERGENCY_REVERSAL": {
        "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE",
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "information_cutoff": "2026-08-31T21:00:00Z",
        "replay_executed_at": "2026-09-04T13:42:09.025554Z",
        "state_value": "OFF",
        "monthly_reference": 4452.046728838838,
        "reason": "MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION",
        "canonical_authority": False,
        "prospective_claim": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    },
}


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _latest_target_context(cur) -> str:
    cur.execute(
        """
        select metadata->>'target_context' as target_context
        from derived_feature_snapshots
        where feature_name in ('MONTHLY_DIRECTION_3M','FAST_STATE','SLOW_STATE','GVZ_REGIME')
          and coalesce(metadata->>'target_context','') <> ''
        order by calculation_ts desc,id desc limit 1
        """
    )
    row = cur.fetchone()
    if not row or not row["target_context"]:
        raise RuntimeError("BLOCKED_RUNTIME_BOOTSTRAP_NO_TARGET_CONTEXT")
    return str(row["target_context"])


def _context_outputs(cur, target_context: str) -> dict[str, dict]:
    feature_names = [v[0] for v in CONTEXT_FEATURES.values()] + list(GVZ_FEATURES)
    cur.execute(
        """
        select id,feature_name,feature_version,calculation_ts,value_text,quality_status,metadata,input_lineage
        from derived_feature_snapshots
        where feature_name=any(%s)
          and metadata->>'target_context'=%s
        order by calculation_ts desc,id desc
        """,
        (feature_names, target_context),
    )
    latest: dict[str, dict] = {}
    for raw in cur.fetchall():
        row = dict(raw)
        latest.setdefault(str(row["feature_name"]), row)
    required = {"MONTHLY_DIRECTION_3M", "FAST_STATE", "SLOW_STATE", *GVZ_FEATURES}
    missing = sorted(required - set(latest))
    if missing:
        raise RuntimeError(f"BLOCKED_RUNTIME_BOOTSTRAP_CONTEXT_MISSING:{missing}")
    return latest


def _latest_active_successor_rows(cur, now: datetime, target_context: str) -> list[dict]:
    rows: list[dict] = []
    for engine_id in ACTIVE_SUCCESSORS:
        cur.execute(
            """
            select engine_id,engine_version,engine_role,evidence_class,runtime_status,
                   status_code,direction_vote_permitted,input_fingerprint,metadata
            from engine_execution_runs
            where engine_id=%s and evidence_class<>'HISTORICAL_REPLAY'
            order by as_of desc,created_at desc,run_id desc
            limit 1
            """,
            (engine_id,),
        )
        raw = cur.fetchone()
        if not raw:
            raise RuntimeError(f"BLOCKED_RUNTIME_BOOTSTRAP_ACTIVE_SUCCESSOR_MISSING:{engine_id}")
        source = dict(raw)
        if source["runtime_status"] != "ACTIVE" or source["direction_vote_permitted"] is not False:
            raise RuntimeError(f"BLOCKED_RUNTIME_BOOTSTRAP_ACTIVE_SUCCESSOR_STATE_INVALID:{engine_id}")
        metadata = dict(source.get("metadata") or {})
        metadata["bootstrap_copied_from_latest_governed_successor"] = True
        metadata["no_recalculation"] = True
        rows.append(
            {
                "engine_id": engine_id,
                "engine_version": source["engine_version"],
                "engine_role": source["engine_role"],
                "as_of": now,
                "target_context": target_context,
                "evidence_class": AUDIT_EVIDENCE,
                "runtime_status": "ACTIVE",
                "status_code": source["status_code"],
                "direction_vote_permitted": False,
                "input_fingerprint": source.get("input_fingerprint"),
                "derived_feature_snapshot_ids": [],
                "metadata": metadata,
            }
        )
    return rows


def build_plan(cur, now: datetime) -> list[dict]:
    target_context = _latest_target_context(cur)
    latest = _context_outputs(cur, target_context)
    rows: list[dict] = []

    for engine_id, (feature_name, role, direction_vote) in CONTEXT_FEATURES.items():
        if engine_id == "GVZ_RISK":
            linked = [int(latest[name]["id"]) for name in GVZ_FEATURES]
            anchor = latest["GVZ_REGIME"]
        else:
            linked = [int(latest[feature_name]["id"])]
            anchor = latest[feature_name]
        rows.append(
            {
                "engine_id": engine_id,
                "engine_version": str(anchor["feature_version"]),
                "engine_role": role,
                "as_of": now,
                "target_context": target_context,
                "evidence_class": AUDIT_EVIDENCE,
                "runtime_status": "ACTIVE",
                "status_code": "VERIFIED_PERSISTED_CONTEXT_AVAILABLE",
                "direction_vote_permitted": direction_vote,
                "input_fingerprint": str((anchor.get("metadata") or {}).get("input_fingerprint") or (anchor.get("input_lineage") or {}).get("input_fingerprint") or "") or None,
                "derived_feature_snapshot_ids": linked,
                "metadata": {
                    "audit_scope": "CURRENT_PERSISTED_CONTEXT_ONLY",
                    "linked_output_evidence_class": anchor.get("quality_status"),
                    "linked_output_calculation_ts": anchor.get("calculation_ts").isoformat(),
                    "no_recalculation": True,
                    "no_prospective_relabel": True,
                },
            }
        )

    rows.extend(_latest_active_successor_rows(cur, now, target_context))

    for engine_id, (runtime_status, status_code, role, direction_vote) in STATUS_SPECS.items():
        if engine_id in EXPERT_REGISTRY:
            version = EXPERT_REGISTRY[engine_id].model_version
        else:
            version = STATIC_VERSIONS[engine_id]
        metadata = {
            "audit_scope": "CANONICAL_MANIFEST_RUNTIME_STATUS_V141",
            "no_output_fabricated": True,
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
        }
        if engine_id in CURRENT_MONTH_REFERENCES:
            metadata.update(
                {
                    "model_status": "ACTIVE_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE",
                    "current_month_reference": dict(CURRENT_MONTH_REFERENCES[engine_id]),
                    "no_prospective_issuance": True,
                    "prospective_claim": False,
                    "canonical_forecast_authority": False,
                }
            )
            if engine_id == "VW_MIDAS_MSVR_SUCCESSOR_V1":
                metadata.update(
                    {
                        "later_prospective_validation_origin": "2026-09-30T21:00:00Z",
                        "later_prospective_validation_target": "2026-10",
                    }
                )
        else:
            metadata["no_forecast_issued"] = True
        rows.append(
            {
                "engine_id": engine_id,
                "engine_version": version,
                "engine_role": role,
                "as_of": now,
                "target_context": target_context,
                "evidence_class": AUDIT_EVIDENCE,
                "runtime_status": runtime_status,
                "status_code": status_code,
                "direction_vote_permitted": direction_vote,
                "input_fingerprint": None,
                "derived_feature_snapshot_ids": [],
                "metadata": metadata,
            }
        )

    if len(rows) != 12 or len({r["engine_id"] for r in rows}) != 12:
        raise RuntimeError("RUNTIME_BOOTSTRAP_ENGINE_INVENTORY_NOT_12")
    counts = {
        "active": sum(x["runtime_status"] == "ACTIVE" for x in rows),
        "waiting": sum(x["runtime_status"] == "WAITING" for x in rows),
        "blocked": sum(x["runtime_status"] == "BLOCKED" for x in rows),
    }
    if counts != {"active": 12, "waiting": 0, "blocked": 0}:
        raise RuntimeError(f"RUNTIME_BOOTSTRAP_V140_COUNTS_INVALID:{counts}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    now = datetime.now(timezone.utc)
    sha = git_sha()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            if not spine_schema_ready(cur):
                raise RuntimeError("BLOCKED_DATA_EVIDENCE_SPINE_SCHEMA_NOT_APPLIED")
            plan = build_plan(cur, now)
            if not args.persist:
                conn.rollback()
                counts = {
                    "active": sum(x["runtime_status"] == "ACTIVE" for x in plan),
                    "waiting": sum(x["runtime_status"] == "WAITING" for x in plan),
                    "blocked": sum(x["runtime_status"] == "BLOCKED" for x in plan),
                }
                print(json.dumps({
                    "status": "DRY_RUN_PASS",
                    "engine_count": len(plan),
                    **counts,
                    "database_writes": "NONE",
                    "target_context": plan[0]["target_context"],
                }, sort_keys=True))
                return 0

            run_ids = []
            for spec in plan:
                run_ids.append(
                    record_engine_execution(
                        cur,
                        engine_id=spec["engine_id"],
                        engine_version=spec["engine_version"],
                        engine_role=spec["engine_role"],
                        as_of=spec["as_of"],
                        target_context=spec["target_context"],
                        evidence_class=spec["evidence_class"],
                        runtime_status=spec["runtime_status"],
                        status_code=spec["status_code"],
                        direction_vote_permitted=spec["direction_vote_permitted"],
                        git_commit=sha,
                        input_fingerprint=spec["input_fingerprint"],
                        metadata=spec["metadata"],
                        derived_feature_snapshot_ids=spec["derived_feature_snapshot_ids"],
                    )
                )
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                "select runtime_status,count(*) as n from latest_engine_runtime_state "
                "where engine_id=any(%s) group by runtime_status order by runtime_status",
                ([r["engine_id"] for r in plan],),
            )
            counts = {r["runtime_status"]: int(r["n"]) for r in cur.fetchall()}
            cur.execute("select count(*) as n from latest_engine_runtime_state where engine_id=any(%s)", ([r["engine_id"] for r in plan],))
            total = int(cur.fetchone()["n"])
        conn.rollback()
    if total != 12 or counts.get("ACTIVE") != 12 or counts.get("WAITING", 0) != 0 or counts.get("BLOCKED", 0) != 0:
        raise RuntimeError(f"RUNTIME_BOOTSTRAP_POST_COMMIT_COUNTS_INVALID:{total}:{counts}")
    print(json.dumps({"status": "INSERTED_VERIFIED", "total": total, "counts": counts, "run_ids": run_ids}, sort_keys=True))
    print("DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_V141_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
