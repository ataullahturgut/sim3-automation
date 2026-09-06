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

# v1.38 current governed inventory. The VW/MSVR slot is the separately validated
# Successor V1 research-shadow identity and is WAITING for its first genuine
# prospective origin. No superseded VW runtime identity is part of this plan.
STATUS_SPECS = {
    "CAUSAL_PATCH": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_EXPERT", False),
    "VW_MIDAS_MSVR_SUCCESSOR_V1": ("WAITING", "WAITING_ORIGIN_NOT_REACHED", "MONTHLY_H1_EXPERT", False),
    "MOMENTUM_3M": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_EXPERT", False),
    "RANDOM_WALK": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_BENCHMARK", False),
    "EMERGENCY_LEVEL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "EMERGENCY_CONTEXT", False),
    "EMERGENCY_REVERSAL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "EMERGENCY_CONTEXT", False),
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
            "audit_scope": "CANONICAL_MANIFEST_RUNTIME_STATUS_V138",
            "no_output_fabricated": True,
            "no_forecast_issued": True,
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
        }
        if engine_id == "VW_MIDAS_MSVR_SUCCESSOR_V1":
            metadata.update(
                {
                    "model_status": "RESEARCH_SHADOW_CANDIDATE_HISTORICAL_REPLAY_PASS_PROSPECTIVE_VALIDATION_REQUIRED",
                    "first_prospective_origin": "2026-09-30T21:00:00Z",
                    "first_prospective_target": "2026-10",
                    "prospective_claim": False,
                    "canonical_forecast_authority": False,
                }
            )
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
    if counts != {"active": 6, "waiting": 6, "blocked": 0}:
        raise RuntimeError(f"RUNTIME_BOOTSTRAP_V138_COUNTS_INVALID:{counts}")
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
    if total != 12 or counts.get("ACTIVE") != 6 or counts.get("WAITING") != 6 or counts.get("BLOCKED", 0) != 0:
        raise RuntimeError(f"RUNTIME_BOOTSTRAP_POST_COMMIT_COUNTS_INVALID:{total}:{counts}")
    print(json.dumps({"status": "INSERTED_VERIFIED", "total": total, "counts": counts, "run_ids": run_ids}, sort_keys=True))
    print("DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_V138_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
