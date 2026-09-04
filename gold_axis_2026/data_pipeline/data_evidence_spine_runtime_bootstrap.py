from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from data_evidence_spine import record_engine_execution, spine_schema_ready
from multi_expert_forecast import EXPERT_REGISTRY


ROOT = Path(__file__).resolve().parents[1]
TARGET_CONTEXT = "2026-09"
AUDIT_EVIDENCE = "RUNTIME_GOVERNANCE_AUDIT"

STATUS_SPECS = {
    "CAUSAL_PATCH": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_EXPERT", False),
    "VW_MIDAS_MSVR": ("BLOCKED", "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN", "MONTHLY_H1_EXPERT", False),
    "MOMENTUM_3M": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_EXPERT", False),
    "RANDOM_WALK": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", "MONTHLY_H1_BENCHMARK", False),
    "MACRO_EVENT": ("BLOCKED", "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED", "EVENT_CONTEXT", False),
    "EMERGENCY_LEVEL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "EMERGENCY_CONTEXT", False),
    "EMERGENCY_REVERSAL": ("WAITING", "WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE", "EMERGENCY_CONTEXT", False),
    "BOCPD": ("BLOCKED", "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED", "REGIME_CONTEXT", False),
}

STATIC_VERSIONS = {
    "MACRO_EVENT": "MACRO_EVENT_PARTIAL_RULE_RECOVERED_SOURCE_CONTRACT_BLOCKED",
    "EMERGENCY_LEVEL": "R4_2_PATCH_EXPERT_REFERENCE_READY_V1",
    "EMERGENCY_REVERSAL": "R4_2_PATCH_EXPERT_REFERENCE_READY_V1",
    "BOCPD": "BOCPD_RETURN_R1_PARTIAL_RECOVERY_L36_THRESHOLD_LOCKED",
}

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

    for engine_id, (runtime_status, status_code, role, direction_vote) in STATUS_SPECS.items():
        if engine_id in EXPERT_REGISTRY:
            version = EXPERT_REGISTRY[engine_id].model_version
        else:
            version = STATIC_VERSIONS[engine_id]
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
                "metadata": {
                    "audit_scope": "CANONICAL_MANIFEST_RUNTIME_STATUS",
                    "no_output_fabricated": True,
                    "no_forecast_issued": True,
                },
            }
        )

    if len(rows) != 12 or len({r["engine_id"] for r in rows}) != 12:
        raise RuntimeError("RUNTIME_BOOTSTRAP_ENGINE_INVENTORY_NOT_12")
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
                if counts != {"active": 4, "waiting": 5, "blocked": 3}:
                    raise RuntimeError(f"RUNTIME_BOOTSTRAP_DRY_RUN_COUNTS_INVALID:{counts}")
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
            cur.execute("select runtime_status,count(*) as n from latest_engine_runtime_state group by runtime_status order by runtime_status")
            counts = {r["runtime_status"]: int(r["n"]) for r in cur.fetchall()}
            cur.execute("select count(*) as n from latest_engine_runtime_state")
            total = int(cur.fetchone()["n"])
        conn.rollback()
    if total != 12 or counts.get("ACTIVE") != 4 or counts.get("WAITING") != 5 or counts.get("BLOCKED") != 3:
        raise RuntimeError(f"RUNTIME_BOOTSTRAP_POST_COMMIT_COUNTS_INVALID:{total}:{counts}")
    print(json.dumps({"status": "INSERTED_VERIFIED", "total": total, "counts": counts, "run_ids": run_ids}, sort_keys=True))
    print("DATA_EVIDENCE_SPINE_RUNTIME_BOOTSTRAP_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
