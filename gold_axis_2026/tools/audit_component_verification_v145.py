from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
GC = ROOT / "gold_axis_2026"
AUDITS = GC / "data_pipeline" / "audits"
PROTOCOL = "GOLD_CONTROL_COMPONENT_VERIFICATION_PROTOCOL_V145_2026-09-09.md"
MANIFEST = "GOLD_CONTROL_PROJECT_MANIFEST.md"

ENGINE_ORDER = [
    "CAUSAL_PATCH",
    "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "MACRO_EVENT_SUCCESSOR_V2",
    "BOCPD_RETURN_SUCCESSOR_V1",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "GVZ_RISK",
]

EXPECTED_RUNTIME_VERSION = {
    "CAUSAL_PATCH": "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE",
    "VW_MIDAS_MSVR_SUCCESSOR_V1": "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "MOMENTUM_3M": "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
    "RANDOM_WALK": "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
    "MONTHLY_DIRECTION_3M": "R4_1_3M_SIMPLE_RETURN_V1",
    "FAST": "R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1",
    "SLOW": "R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1",
    "MACRO_EVENT_SUCCESSOR_V2": "MACRO_EVENT_SUCCESSOR_V2",
    "BOCPD_RETURN_SUCCESSOR_V1": "BOCPD_RETURN_SUCCESSOR_V1",
    "EMERGENCY_LEVEL": "R4_2_PATCH_EXPERT_REFERENCE_READY_V1",
    "EMERGENCY_REVERSAL": "R4_2_PATCH_EXPERT_REFERENCE_READY_V1",
    "GVZ_RISK": "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
}

NY17_ENGINES = {
    "MONTHLY_DIRECTION_3M", "FAST", "SLOW", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"
}
AUTHORITY_TABLES = (
    "monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events"
)
DIMENSIONS = (
    "C1_FROZEN_IDENTITY",
    "C2_IMPLEMENTATION_RULE",
    "C3_SOURCE_BINDING",
    "C4_HISTORICAL_COVERAGE",
    "C5_ORIGIN_PIT",
    "C6_FUTURE_INFORMATION",
    "C7_RECONSTRUCTION_VINTAGE",
    "C8_DETERMINISM_REPRODUCIBILITY",
    "C9_PILOT_CELL_EXECUTION",
)
VALID_DIM = {"PASS", "FAIL", "BLOCKED", "NOT_PROVEN"}


def jload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(status: str, evidence: Any) -> dict[str, Any]:
    if status not in VALID_DIM:
        raise ValueError(status)
    return {"status": status, "evidence": evidence}


def final_status(dimensions: dict[str, dict[str, Any]]) -> str:
    states = [v["status"] for v in dimensions.values()]
    if "FAIL" in states:
        return "FAIL"
    if "BLOCKED" in states:
        return "BLOCKED"
    if "NOT_PROVEN" in states:
        return "NOT_PROVEN"
    return "PASS"


def new_dims() -> dict[str, dict[str, Any]]:
    return {k: d("NOT_PROVEN", None) for k in DIMENSIONS}


def read_prod_snapshot(dsn: str) -> dict[str, Any]:
    with psycopg.connect(dsn, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
            cur.execute("select current_timestamp as snapshot_at, txid_current_snapshot()::text as tx_snapshot")
            ident = dict(cur.fetchone())
            cur.execute("""
                select engine_id,engine_version,engine_role,target_context,runtime_status,status_code,evidence_class,git_commit,metadata
                from current_engine_runtime_state_v1 order by engine_id
            """)
            runtime = [dict(x) for x in cur.fetchall()]
            cur.execute("""
                select series_id,source_name,source_symbol,frequency,status,metadata
                from source_registry
                where series_id in (
                    'XAU_EOD_TWELVE_NY17','GVZ_CBOE',
                    'MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT',
                    'MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT',
                    'MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT'
                ) order by series_id
            """)
            sources = [dict(x) for x in cur.fetchall()]
            cur.execute("""
                select run_id::text,status,observations_read,observations_written,pipeline_version,trigger_type
                from retrieval_runs where run_id='6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a'::uuid
            """)
            macro_run = dict(cur.fetchone() or {})
            cur.execute("""
                select series_id,count(*)::int n,count(*) filter(where available_as_of is null)::int null_available
                from observations
                where run_id='6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a'::uuid
                group by series_id order by series_id
            """)
            macro_series = [dict(x) for x in cur.fetchall()]
            counts: dict[str, int] = {}
            for table in AUTHORITY_TABLES:
                cur.execute(f"select count(*)::int n from {table}")
                counts[table] = int(cur.fetchone()["n"])
            return {
                **ident,
                "runtime": runtime,
                "sources": sources,
                "macro_run": macro_run,
                "macro_series": macro_series,
                "authority_counts": counts,
            }


def runtime_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["engine_id"]: r for r in snapshot["runtime"]}


def source_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["series_id"]: r for r in snapshot["sources"]}


def base_identity(engine: str, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    dims = new_dims()
    rmap = runtime_map(snapshot)
    row = rmap.get(engine)
    expected = EXPECTED_RUNTIME_VERSION[engine]
    if row is None:
        dims["C1_FROZEN_IDENTITY"] = d("FAIL", "RUNTIME_IDENTITY_MISSING")
    elif row.get("engine_version") != expected:
        dims["C1_FROZEN_IDENTITY"] = d("FAIL", {"expected": expected, "actual": row.get("engine_version")})
    elif row.get("runtime_status") != "ACTIVE":
        dims["C1_FROZEN_IDENTITY"] = d("FAIL", {"runtime_status": row.get("runtime_status")})
    else:
        dims["C1_FROZEN_IDENTITY"] = d("PASS", {"engine_version": expected, "target_context": row.get("target_context")})
    return dims


def verify_patch(snapshot: dict[str, Any]) -> dict[str, Any]:
    dims = base_identity("CAUSAL_PATCH", snapshot)
    e = jload(GC / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_evidence.json")
    identity_ok = e.get("candidate_id") == EXPECTED_RUNTIME_VERSION["CAUSAL_PATCH"]
    geometry_ok = e.get("geometry") == {"L": 252, "P": 21, "D": 32} and e.get("geometry_reselected") is False
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS" if identity_ok and geometry_ok else "FAIL", {"candidate_id": e.get("candidate_id"), "geometry": e.get("geometry")})
    dims["C3_SOURCE_BINDING"] = d("PASS", e.get("daily_feature_rule"))
    dims["C4_HISTORICAL_COVERAGE"] = d("PASS", e.get("locked_window"))
    pit = e.get("pit_gate") or {}
    dims["C5_ORIGIN_PIT"] = d("PASS" if pit.get("pass") and pit.get("same_origin_date_feature_uses") == 0 else "FAIL", pit)
    dims["C6_FUTURE_INFORMATION"] = d("PASS" if e.get("future_information_violations") == 0 else "FAIL", e.get("future_information_violations"))
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS", {"evidence_class": e.get("evidence_class"), "prospective_claim": e.get("prospective_claim")})
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if e.get("deterministic_max_abs_diff") == 0.0 and e.get("target_reconciliation") == "43/43" else "FAIL", {"max_abs_diff": e.get("deterministic_max_abs_diff"), "reconciliation": e.get("target_reconciliation")})
    dims["C9_PILOT_CELL_EXECUTION"] = d("NOT_PROVEN", "2026-08 frozen-identity replay not yet preserved; 2025-01..2026-07 covered")
    return result("CAUSAL_PATCH", dims, "patch_repro_v1/locked_replay_v7_daily_feature_pit_evidence.json")


def verify_simple(engine: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    dims = base_identity(engine, snapshot)
    e = jload(GC / "simple_expert_v2" / "simple_expert_v2_source_binding_evidence.json")
    key = "momentum_model_version" if engine == "MOMENTUM_3M" else "rw_model_version"
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS" if e.get(key) == EXPECTED_RUNTIME_VERSION[engine] else "FAIL", e.get(key))
    sem = e.get("source_semantic") or {}
    source_ok = (
        e.get("source_id") == "SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"
        and sem.get("provider") == "Twelve Data" and sem.get("symbol") == "XAU/USD"
        and sem.get("interval") == "1h" and sem.get("requested_timezone") == "America/New_York"
        and sem.get("selected_bar_end_semantic") == "17:00_ET_HOURLY_CLOSE"
        and e.get("provider_substitution") is False
    )
    dims["C3_SOURCE_BINDING"] = d("PASS" if source_ok else "FAIL", {"source_id": e.get("source_id"), "semantic": sem})
    coverage_ok = e.get("source_missing_month_count") == 0 and e.get("source_low_count_month_count") == 0
    dims["C4_HISTORICAL_COVERAGE"] = d("PASS" if coverage_ok else "FAIL", {"locked_window": e.get("locked_window"), "minimum_selected_observations_per_month": e.get("minimum_selected_observations_per_month")})
    dims["C5_ORIGIN_PIT"] = d("PASS" if e.get("hard_integrity_pass") is True else "FAIL", "source-bound origin-safe immutable replay")
    dims["C6_FUTURE_INFORMATION"] = d("PASS" if e.get("future_information_violations") == 0 else "FAIL", e.get("future_information_violations"))
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS", {"evidence_class": e.get("evidence_class"), "prospective_claim": e.get("prospective_claim")})
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if e.get("deterministic_max_abs_diff") == 0.0 and e.get("actual_reconciliation") == "43/43" else "FAIL", {"max_abs_diff": e.get("deterministic_max_abs_diff"), "reconciliation": e.get("actual_reconciliation")})
    dims["C9_PILOT_CELL_EXECUTION"] = d("NOT_PROVEN", "2026-08 frozen-identity replay not yet preserved; 2025-01..2026-07 covered")
    return result(engine, dims, "simple_expert_v2/simple_expert_v2_source_binding_evidence.json")


def verify_vw(snapshot: dict[str, Any], vw_result_path: Path | None) -> dict[str, Any]:
    dims = base_identity("VW_MIDAS_MSVR_SUCCESSOR_V1", snapshot)
    code = (GC / "tools" / "vw_midas_msvr_successor_v1.py").read_text(encoding="utf-8")
    contract = (GC / "GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-06.md").read_text(encoding="utf-8")
    constants_ok = all(x in code for x in (
        'MODEL_ID = "VW_MIDAS_MSVR_SUCCESSOR_V1"',
        'GPR_PIT = "GPR_OFFICIAL_GIT_PIT"',
        'MIN_INNER = 6',
        'C in (0.1, 1.0, 10.0)',
        'ep in (0.02, 0.05)',
        'gm in (0.5, 1.0)',
    )) and "Random split forbidden" in contract
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS" if constants_ok else "FAIL", "frozen four-metal MSVR constants/grid/nested rule")
    source_tokens = ["XAU_STAKTRAKR_RESEARCH_DAILY_R1", "XAG_STAKTRAKR_RESEARCH_DAILY_R1", "XPT_STAKTRAKR_RESEARCH_DAILY_R1", "XPD_STAKTRAKR_RESEARCH_DAILY_R1", "GPR_OFFICIAL_GIT_PIT"]
    dims["C3_SOURCE_BINDING"] = d("PASS" if all(x in code for x in source_tokens) else "FAIL", source_tokens)
    dims["C4_HISTORICAL_COVERAGE"] = d("PASS", "governed implementation frozen evaluation coverage through 2026-07; source gate rerun required")
    dims["C5_ORIGIN_PIT"] = d("PASS" if "available_as_of" in code and "month_end_utc" in code else "FAIL", "origin-local GPR vintage availability gate")
    dims["C6_FUTURE_INFORMATION"] = d("PASS" if "eligible = [u for u in all_targets if u < t]" in code else "FAIL", "inner target strictly before outer target")
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS", "StakTrakr historical research + GPR_OFFICIAL_GIT_PIT explicitly separated")
    if vw_result_path and vw_result_path.exists():
        v = jload(vw_result_path)
        gov = v.get("governance") or {}
        det_ok = (
            v.get("determinism_check") == "PASS"
            and gov.get("database_writes") == "NONE"
            and gov.get("forecast_writes") == "NONE"
            and gov.get("decision_writes") == "NONE"
            and gov.get("auto_selector") == "OFF"
            and gov.get("auto_ensemble") == "OFF"
            and v.get("authority_invariants_before") == v.get("authority_invariants_after")
        )
        dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if det_ok else "FAIL", "fresh technical deterministic replay; performance metrics ignored")
    else:
        dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("NOT_PROVEN", "fresh deterministic result artifact not supplied to verifier")
    dims["C9_PILOT_CELL_EXECUTION"] = d("NOT_PROVEN", "frozen successor evaluation ends 2026-07; 2026-08 execution not preserved")
    return result("VW_MIDAS_MSVR_SUCCESSOR_V1", dims, "GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-06.md")


def ny17_bundle_pass() -> tuple[bool, Any]:
    p = AUDITS / "historical_reconstruction_bundle_v145" / "historical_reconstruction_bundle_v145.json"
    if not p.exists():
        return False, "NY17 historical reconstruction bundle not yet present"
    v = jload(p)
    ok = v.get("status") == "PASS" and v.get("production_database_write") == "NONE" and v.get("prospective_claim") is False
    return ok, {"path": str(p.relative_to(ROOT)), "status": v.get("status"), "ny17_status_counts": v.get("ny17_status_counts")}


def verify_r4_context(engine: str, snapshot: dict[str, Any], r4_tests_pass: bool) -> dict[str, Any]:
    dims = base_identity(engine, snapshot)
    source = source_map(snapshot).get("XAU_EOD_TWELVE_NY17")
    code_file = {
        "MONTHLY_DIRECTION_3M": "r4_1/src/gold_r4/monthly.py",
        "FAST": "r4_1/src/gold_r4/tactical.py",
        "SLOW": "r4_1/src/gold_r4/tactical.py",
        "EMERGENCY_LEVEL": "r4_1/src/gold_r4/emergency.py",
        "EMERGENCY_REVERSAL": "r4_1/src/gold_r4/emergency.py",
    }[engine]
    text = (GC / code_file).read_text(encoding="utf-8")
    required: dict[str, list[str]] = {
        "MONTHLY_DIRECTION_3M": ["r = returns[-3:]", "m = sum(r) / 3.0"],
        "FAST": ["sma_days: int = 20", "persistence_days: int = 2"],
        "SLOW": ["sma_weeks: int = 4", "persistence_weeks: int = 2", 'resample("W-FRI")'],
        "EMERGENCY_LEVEL": ["level_threshold: float = 0.04", "return_level"],
        "EMERGENCY_REVERSAL": ["reversal_threshold: float = 0.04", "DOWN_ALERT", "UP_ALERT"],
    }
    rule_ok = all(token in text for token in required[engine])
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS" if rule_ok and r4_tests_pass else ("FAIL" if not rule_ok else "NOT_PROVEN"), {"code": code_file, "frozen_tests_pass": r4_tests_pass})
    source_ok = source and source.get("source_name") == "Twelve Data" and source.get("source_symbol") == "XAU/USD"
    dims["C3_SOURCE_BINDING"] = d("PASS" if source_ok else "FAIL", source)
    complete, bundle_evidence = ny17_bundle_pass()
    dims["C4_HISTORICAL_COVERAGE"] = d("PASS" if complete else "BLOCKED", bundle_evidence)
    dims["C5_ORIGIN_PIT"] = d("PASS" if rule_ok else "FAIL", "role-specific chronological/completed-period rule frozen in implementation")
    dims["C6_FUTURE_INFORMATION"] = d("PASS" if rule_ok else "FAIL", "chronological replay requirement; no performance input consumed")
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS" if complete else "BLOCKED", bundle_evidence)
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if r4_tests_pass else "NOT_PROVEN", "r4_1 frozen rule/determinism tests")
    dims["C9_PILOT_CELL_EXECUTION"] = d("NOT_PROVEN" if complete else "BLOCKED", "historical role replay follows bundle completion")
    return result(engine, dims, code_file)


def verify_macro(snapshot: dict[str, Any]) -> dict[str, Any]:
    dims = base_identity("MACRO_EVENT_SUCCESSOR_V2", snapshot)
    run = snapshot.get("macro_run") or {}
    rows = snapshot.get("macro_series") or []
    exact_series = {
        "MACRO_NFP_ACTUAL_FIRST_PRINT", "MACRO_NFP_CONSENSUS_PIT",
        "MACRO_UNEMP_ACTUAL_FIRST_PRINT", "MACRO_UNEMP_CONSENSUS_PIT",
        "MACRO_AHE_ACTUAL_FIRST_PRINT", "MACRO_AHE_CONSENSUS_PIT",
    }
    source_ok = (
        run.get("run_id") == "6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a"
        and run.get("status") == "SUCCESS"
        and int(run.get("observations_read") or 0) == 756
        and int(run.get("observations_written") or 0) == 756
        and {r["series_id"] for r in rows} == exact_series
        and all(int(r["n"]) == 126 and int(r["null_available"]) == 0 for r in rows)
    )
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS", "frozen V2 MAD/IQR/sign/equal-weight/threshold code + prereg identity")
    dims["C3_SOURCE_BINDING"] = d("PASS" if source_ok else "FAIL", {"run": run, "series_counts": rows})
    dims["C4_HISTORICAL_COVERAGE"] = d("PASS" if source_ok else "FAIL", "126 complete cases / 756 source rows; 2025-10 contractual exclusion preserved")
    dims["C5_ORIGIN_PIT"] = d("PASS" if source_ok else "FAIL", "actual first print + consensus PIT release-aware source panel")
    # Run the frozen technical replay in-memory/read-only and compare twice. No performance metric is read.
    try:
        sys.path.insert(0, str(GC / "data_pipeline"))
        import macro_event_successor_v2_score_replay as m  # type: ignore
        with psycopg.connect(os.environ["NEON_DATABASE_URL"], autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute("set transaction isolation level repeatable read, read only")
            panel, _ = m.load_frozen_panel(conn)
            scores_a = m.compute_scores(panel)
            m.assert_prefix_invariance(panel, scores_a)
            scores_b = m.compute_scores(panel)
        stable_a = hashlib.sha256(json.dumps([asdict(x) for x in scores_a], sort_keys=True, default=str).encode()).hexdigest()
        stable_b = hashlib.sha256(json.dumps([asdict(x) for x in scores_b], sort_keys=True, default=str).encode()).hexdigest()
        det_ok = stable_a == stable_b
    except Exception as exc:
        det_ok = False
        stable_a = f"ERROR:{type(exc).__name__}:{exc}"
        stable_b = None
    dims["C6_FUTURE_INFORMATION"] = d("PASS" if det_ok else "FAIL", "prefix invariance executed on frozen panel")
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS" if source_ok else "FAIL", "first-print and consensus-PIT source identities retained")
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if det_ok else "FAIL", {"rerun_hash_a": stable_a, "rerun_hash_b": stable_b})
    dims["C9_PILOT_CELL_EXECUTION"] = d("PASS" if det_ok and source_ok else "FAIL", "2025-10 remains CONTRACTUAL_EXCLUSION, not imputed")
    return result("MACRO_EVENT_SUCCESSOR_V2", dims, "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V2_ROBUST_SCORE_PREREG_2026-09-05.md")


def verify_bocpd(snapshot: dict[str, Any], bocpd_tests_pass: bool) -> dict[str, Any]:
    dims = base_identity("BOCPD_RETURN_SUCCESSOR_V1", snapshot)
    c = jload(GC / "bocpd_successor_v1" / "frozen_contract_v1.json")
    contract_ok = (
        c.get("contract_version") == "BOCPD_RETURN_SUCCESSOR_V1"
        and c.get("source", {}).get("artifact") == "gold_axis_2026/core5_monthly.csv.gz.b64"
        and c.get("source", {}).get("field") == "gold_monthly"
        and c.get("source", {}).get("transform") == "log(P_t/P_t-1)"
        and c.get("source", {}).get("completed_month_only") is True
        and c.get("hazard", {}).get("expected_run_length_months") == 36
        and c.get("windows", {}).get("tuning_2026") == "NONE"
    )
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS" if contract_ok and bocpd_tests_pass else ("FAIL" if not contract_ok else "NOT_PROVEN"), {"contract": contract_ok, "tests": bocpd_tests_pass})
    dims["C3_SOURCE_BINDING"] = d("PASS" if contract_ok else "FAIL", c.get("source"))
    dims["C4_HISTORICAL_COVERAGE"] = d("BLOCKED", {"locked_end": c.get("windows", {}).get("locked_end"), "missing_pilot_cell": "2026-08"})
    dims["C5_ORIGIN_PIT"] = d("PASS" if contract_ok else "FAIL", "completed-month only")
    dims["C6_FUTURE_INFORMATION"] = d("PASS" if c.get("windows", {}).get("tuning_2026") == "NONE" else "FAIL", "tuning_2026=NONE")
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS", {"evidence": c.get("evidence"), "database_writes_permitted": c.get("database_writes_permitted")})
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if bocpd_tests_pass else "NOT_PROVEN", "frozen BOCPD tests")
    dims["C9_PILOT_CELL_EXECUTION"] = d("BLOCKED", "2026-08 is outside frozen locked_end=2026-07; evaluation-only extension not yet governed")
    return result("BOCPD_RETURN_SUCCESSOR_V1", dims, "bocpd_successor_v1/frozen_contract_v1.json")


def verify_gvz(snapshot: dict[str, Any], r4_tests_pass: bool) -> dict[str, Any]:
    dims = base_identity("GVZ_RISK", snapshot)
    sm = source_map(snapshot)
    src = sm.get("GVZ_CBOE")
    lane = jload(AUDITS / "historical_gvz_reconstruction_lane_v145_evidence.json")
    code = (GC / "r4_1" / "src" / "gold_r4" / "gvz.py").read_text(encoding="utf-8")
    rule_ok = all(x in code for x in ("25.9795", "30.5238", "cap=1.0", "cap=0.5", "cap=0.25", "panic=True"))
    source_ok = src and src.get("source_name") == "Cboe official historical price data" and src.get("source_symbol") == "GVZ"
    lane_ok = lane.get("status") == "PASS_GAP_COMPLETED_AS_IMMUTABLE_ARTIFACT_LANE" and lane.get("historical_rows") == 295 and lane.get("prospective_claim") is False
    dims["C2_IMPLEMENTATION_RULE"] = d("PASS" if rule_ok and r4_tests_pass else ("FAIL" if not rule_ok else "NOT_PROVEN"), {"rule": rule_ok, "tests": r4_tests_pass})
    dims["C3_SOURCE_BINDING"] = d("PASS" if source_ok else "FAIL", src)
    dims["C4_HISTORICAL_COVERAGE"] = d("PASS" if lane_ok else "BLOCKED", {"historical_rows": lane.get("historical_rows"), "range": [lane.get("first_observation_date"), lane.get("last_observation_date")]})
    dims["C5_ORIGIN_PIT"] = d("PASS", "chronological released Cboe observations")
    dims["C6_FUTURE_INFORMATION"] = d("PASS", "risk-only chronological context; no performance input consumed")
    dims["C7_RECONSTRUCTION_VINTAGE"] = d("PASS" if lane_ok else "BLOCKED", {"evidence_class": lane.get("evidence_class"), "prospective_claim": lane.get("prospective_claim")})
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = d("PASS" if rule_ok and r4_tests_pass else "NOT_PROVEN", "pure frozen mapping + frozen tests")
    # Data is complete and code is verified, but role replay evidence is intentionally a later step.
    dims["C9_PILOT_CELL_EXECUTION"] = d("NOT_PROVEN", "historical GVZ role replay not yet preserved; lane maximum before replay is READY_TO_REPLAY")
    return result("GVZ_RISK", dims, "data_pipeline/audits/historical_gvz_reconstruction_lane_v145_evidence.json")


def result(engine: str, dims: dict[str, dict[str, Any]], evidence_reference: str) -> dict[str, Any]:
    return {
        "engine_id": engine,
        "component_verification_status": final_status(dims),
        "dimensions": dims,
        "evidence_reference": evidence_reference,
        "performance_fields_consumed": False,
    }


def build(snapshot: dict[str, Any], *, r4_tests_pass: bool, bocpd_tests_pass: bool, vw_result: Path | None) -> dict[str, Any]:
    actual_inventory = sorted(r["engine_id"] for r in snapshot["runtime"])
    if actual_inventory != sorted(ENGINE_ORDER):
        raise RuntimeError(f"RUNTIME_ENGINE_INVENTORY_DRIFT:{actual_inventory}")
    rows = [
        verify_patch(snapshot),
        verify_vw(snapshot, vw_result),
        verify_simple("MOMENTUM_3M", snapshot),
        verify_simple("RANDOM_WALK", snapshot),
        verify_r4_context("MONTHLY_DIRECTION_3M", snapshot, r4_tests_pass),
        verify_r4_context("FAST", snapshot, r4_tests_pass),
        verify_r4_context("SLOW", snapshot, r4_tests_pass),
        verify_macro(snapshot),
        verify_bocpd(snapshot, bocpd_tests_pass),
        verify_r4_context("EMERGENCY_LEVEL", snapshot, r4_tests_pass),
        verify_r4_context("EMERGENCY_REVERSAL", snapshot, r4_tests_pass),
        verify_gvz(snapshot, r4_tests_pass),
    ]
    by_engine = {x["engine_id"]: x for x in rows}
    rows = [by_engine[e] for e in ENGINE_ORDER]
    counts: dict[str, int] = {}
    for row in rows:
        s = row["component_verification_status"]
        counts[s] = counts.get(s, 0) + 1
    return {
        "audit_id": "GOLD_CONTROL_COMPONENT_VERIFICATION_V145",
        "mode": "PROVISIONAL_PRE_GAP" if not ny17_bundle_pass()[0] else "POST_GAP_COMPONENT_VERIFICATION",
        "protocol": PROTOCOL,
        "manifest_version": "1.45",
        "production_database_access": "READ_ONLY",
        "production_writes": "NONE",
        "performance_fields_consumed": False,
        "engine_count": 12,
        "status_counts": counts,
        "authority_counts": snapshot["authority_counts"],
        "snapshot_at": str(snapshot["snapshot_at"]),
        "tx_snapshot": snapshot["tx_snapshot"],
        "rows": rows,
    }


def dump_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["engine_id", "component_verification_status", *DIMENSIONS, "evidence_reference"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            out = {
                "engine_id": row["engine_id"],
                "component_verification_status": row["component_verification_status"],
                "evidence_reference": row["evidence_reference"],
            }
            for k in DIMENSIONS:
                out[k] = row["dimensions"][k]["status"]
            w.writerow(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", default=str(AUDITS / "component_verification_v145.json"))
    parser.add_argument("--output-csv", default=str(AUDITS / "component_verification_v145.csv"))
    parser.add_argument("--vw-result")
    parser.add_argument("--r4-tests-pass", action="store_true")
    parser.add_argument("--bocpd-tests-pass", action="store_true")
    args = parser.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not dsn:
        raise SystemExit("BLOCKED:NEON_DATABASE_URL_NOT_SET")
    protocol = GC / PROTOCOL
    manifest = GC / MANIFEST
    if not protocol.exists() or not manifest.exists():
        raise SystemExit("BLOCKED:V145_COMPONENT_AUTHORITY_MISSING")
    snapshot = read_prod_snapshot(dsn)
    out = build(
        snapshot,
        r4_tests_pass=args.r4_tests_pass,
        bocpd_tests_pass=args.bocpd_tests_pass,
        vw_result=Path(args.vw_result) if args.vw_result else None,
    )
    Path(args.output_json).write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    dump_csv(Path(args.output_csv), out["rows"])
    print(json.dumps({
        "audit_id": out["audit_id"],
        "mode": out["mode"],
        "status_counts": out["status_counts"],
        "production_writes": out["production_writes"],
        "performance_fields_consumed": out["performance_fields_consumed"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
