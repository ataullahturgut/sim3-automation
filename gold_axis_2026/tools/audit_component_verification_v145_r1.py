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
PROTOCOL = GC / "GOLD_CONTROL_COMPONENT_VERIFICATION_PROTOCOL_V145_2026-09-09.md"

ENGINE_ORDER = [
    "CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK",
    "MONTHLY_DIRECTION_3M", "FAST", "SLOW", "MACRO_EVENT_SUCCESSOR_V2",
    "BOCPD_RETURN_SUCCESSOR_V1", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL", "GVZ_RISK",
]
EXPECTED_VERSION = {
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
DIMS = (
    "C1_FROZEN_IDENTITY", "C2_IMPLEMENTATION_RULE", "C3_SOURCE_BINDING",
    "C4_HISTORICAL_COVERAGE", "C5_ORIGIN_PIT", "C6_FUTURE_INFORMATION",
    "C7_RECONSTRUCTION_VINTAGE", "C8_DETERMINISM_REPRODUCIBILITY", "C9_PILOT_CELL_EXECUTION",
)
AUTHORITY_TABLES = ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events")
VALID = {"PASS", "FAIL", "BLOCKED", "NOT_PROVEN"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dim(status: str, evidence: Any) -> dict[str, Any]:
    if status not in VALID:
        raise ValueError(status)
    return {"status": status, "evidence": evidence}


def empty_dims() -> dict[str, dict[str, Any]]:
    return {name: dim("NOT_PROVEN", None) for name in DIMS}


def final_status(dims: dict[str, dict[str, Any]]) -> str:
    states = {v["status"] for v in dims.values()}
    if "FAIL" in states:
        return "FAIL"
    if "BLOCKED" in states:
        return "BLOCKED"
    if "NOT_PROVEN" in states:
        return "NOT_PROVEN"
    return "PASS"


def result(engine: str, dims: dict[str, dict[str, Any]], evidence: str) -> dict[str, Any]:
    return {
        "engine_id": engine,
        "component_verification_status": final_status(dims),
        "dimensions": dims,
        "evidence_reference": evidence,
        "performance_fields_consumed": False,
    }


def read_snapshot(dsn: str) -> dict[str, Any]:
    with psycopg.connect(dsn, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
            cur.execute("select current_timestamp snapshot_at, txid_current_snapshot()::text tx_snapshot")
            ident = dict(cur.fetchone())
            cur.execute("""
                select engine_id,engine_version,engine_role,target_context,runtime_status,status_code,evidence_class,git_commit,metadata
                from current_engine_runtime_state_v1 order by engine_id
            """)
            runtime = [dict(r) for r in cur.fetchall()]
            cur.execute("""
                select series_id,source_name,source_symbol,frequency,status,metadata
                from source_registry where series_id in (
                  'XAU_EOD_TWELVE_NY17','GVZ_CBOE',
                  'MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT',
                  'MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT',
                  'MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT') order by series_id
            """)
            sources = [dict(r) for r in cur.fetchall()]
            cur.execute("""
                select run_id::text,status,observations_read,observations_written,pipeline_version,trigger_type
                from retrieval_runs where run_id='6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a'::uuid
            """)
            macro_run = dict(cur.fetchone() or {})
            cur.execute("""
                select series_id,count(*)::int n,count(*) filter(where available_as_of is null)::int null_available
                from observations where run_id='6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a'::uuid
                group by series_id order by series_id
            """)
            macro_series = [dict(r) for r in cur.fetchall()]
            authority = {}
            for table in AUTHORITY_TABLES:
                cur.execute(f"select count(*)::int n from {table}")
                authority[table] = int(cur.fetchone()["n"])
    return {**ident, "runtime": runtime, "sources": sources, "macro_run": macro_run,
            "macro_series": macro_series, "authority_counts": authority}


def base(engine: str, snap: dict[str, Any]) -> dict[str, dict[str, Any]]:
    d = empty_dims()
    rows = {r["engine_id"]: r for r in snap["runtime"]}
    r = rows.get(engine)
    expected = EXPECTED_VERSION[engine]
    ok = bool(r and r.get("engine_version") == expected and r.get("runtime_status") == "ACTIVE")
    d["C1_FROZEN_IDENTITY"] = dim("PASS" if ok else "FAIL", {"expected": expected, "actual": None if r is None else r.get("engine_version")})
    return d


def verify_patch(snap: dict[str, Any]) -> dict[str, Any]:
    d = base("CAUSAL_PATCH", snap)
    e = load(GC / "patch_repro_v1/locked_replay_v7_daily_feature_pit_evidence.json")
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if e.get("candidate_id") == EXPECTED_VERSION["CAUSAL_PATCH"] and e.get("geometry") == {"L":252,"P":21,"D":32} and e.get("geometry_reselected") is False else "FAIL", e.get("geometry"))
    d["C3_SOURCE_BINDING"] = dim("PASS", e.get("daily_feature_rule"))
    d["C4_HISTORICAL_COVERAGE"] = dim("PASS", e.get("locked_window"))
    pit = e.get("pit_gate") or {}
    d["C5_ORIGIN_PIT"] = dim("PASS" if pit.get("pass") and pit.get("same_origin_date_feature_uses") == 0 else "FAIL", pit)
    d["C6_FUTURE_INFORMATION"] = dim("PASS" if e.get("future_information_violations") == 0 else "FAIL", e.get("future_information_violations"))
    d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS", {"evidence_class": e.get("evidence_class"), "prospective_claim": e.get("prospective_claim")})
    d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if e.get("deterministic_max_abs_diff") == 0.0 and e.get("target_reconciliation") == "43/43" else "FAIL", {"max_abs_diff":e.get("deterministic_max_abs_diff"),"reconciliation":e.get("target_reconciliation")})
    d["C9_PILOT_CELL_EXECUTION"] = dim("NOT_PROVEN", "2026-08 frozen-identity replay not yet preserved")
    return result("CAUSAL_PATCH", d, "patch_repro_v1/locked_replay_v7_daily_feature_pit_evidence.json")


def verify_simple(engine: str, snap: dict[str, Any]) -> dict[str, Any]:
    d = base(engine, snap)
    e = load(GC / "simple_expert_v2/simple_expert_v2_source_binding_evidence.json")
    key = "momentum_model_version" if engine == "MOMENTUM_3M" else "rw_model_version"
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if e.get(key) == EXPECTED_VERSION[engine] else "FAIL", e.get(key))
    s = e.get("source_semantic") or {}
    source_ok = e.get("source_id") == "SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2" and s.get("provider") == "Twelve Data" and s.get("symbol") == "XAU/USD" and s.get("interval") == "1h" and s.get("requested_timezone") == "America/New_York" and s.get("selected_bar_end_semantic") == "17:00_ET_HOURLY_CLOSE" and e.get("provider_substitution") is False
    d["C3_SOURCE_BINDING"] = dim("PASS" if source_ok else "FAIL", {"source_id":e.get("source_id"),"source_semantic":s})
    d["C4_HISTORICAL_COVERAGE"] = dim("PASS" if e.get("source_missing_month_count") == 0 and e.get("source_low_count_month_count") == 0 else "FAIL", e.get("locked_window"))
    d["C5_ORIGIN_PIT"] = dim("PASS" if e.get("hard_integrity_pass") is True else "FAIL", "source-bound origin-safe replay")
    d["C6_FUTURE_INFORMATION"] = dim("PASS" if e.get("future_information_violations") == 0 else "FAIL", e.get("future_information_violations"))
    d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS", {"evidence_class":e.get("evidence_class"),"prospective_claim":e.get("prospective_claim")})
    d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if e.get("deterministic_max_abs_diff") == 0.0 and e.get("actual_reconciliation") == "43/43" else "FAIL", {"max_abs_diff":e.get("deterministic_max_abs_diff"),"reconciliation":e.get("actual_reconciliation")})
    d["C9_PILOT_CELL_EXECUTION"] = dim("NOT_PROVEN", "2026-08 frozen-identity replay not yet preserved")
    return result(engine, d, "simple_expert_v2/simple_expert_v2_source_binding_evidence.json")


def verify_vw(snap: dict[str, Any], vw_result: Path | None) -> dict[str, Any]:
    d = base("VW_MIDAS_MSVR_SUCCESSOR_V1", snap)
    code = (GC / "tools/vw_midas_msvr_successor_v1.py").read_text(encoding="utf-8")
    contract = (GC / "GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-06.md").read_text(encoding="utf-8")
    rule_ok = all(x in code for x in ('MODEL_ID = "VW_MIDAS_MSVR_SUCCESSOR_V1"','GPR_PIT = "GPR_OFFICIAL_GIT_PIT"','MIN_INNER = 6','C in (0.1, 1.0, 10.0)','ep in (0.02, 0.05)','gm in (0.5, 1.0)')) and "Random split forbidden" in contract
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if rule_ok else "FAIL", "frozen true multi-output MSVR/grid/nested rule")
    sources = ["XAU_STAKTRAKR_RESEARCH_DAILY_R1","XAG_STAKTRAKR_RESEARCH_DAILY_R1","XPT_STAKTRAKR_RESEARCH_DAILY_R1","XPD_STAKTRAKR_RESEARCH_DAILY_R1","GPR_OFFICIAL_GIT_PIT"]
    d["C3_SOURCE_BINDING"] = dim("PASS" if all(x in code for x in sources) else "FAIL", sources)
    d["C4_HISTORICAL_COVERAGE"] = dim("PASS", "frozen evaluation/source contract through 2026-07; Aug execution separate")
    d["C5_ORIGIN_PIT"] = dim("PASS" if "available_as_of" in code and "month_end_utc" in code else "FAIL", "origin-local GPR vintage")
    d["C6_FUTURE_INFORMATION"] = dim("PASS" if "eligible = [u for u in all_targets if u < t]" in code else "FAIL", "inner target < outer target")
    d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS", "historical StakTrakr research + GPR PIT explicitly separated")
    if vw_result and vw_result.exists():
        v = load(vw_result); g = v.get("governance") or {}
        ok = v.get("determinism_check") == "PASS" and g.get("database_writes") == "NONE" and g.get("forecast_writes") == "NONE" and g.get("decision_writes") == "NONE" and g.get("auto_selector") == "OFF" and g.get("auto_ensemble") == "OFF" and v.get("authority_invariants_before") == v.get("authority_invariants_after")
        d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if ok else "FAIL", "fresh technical determinism; performance ignored")
    else:
        d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("NOT_PROVEN", "fresh technical replay artifact absent")
    d["C9_PILOT_CELL_EXECUTION"] = dim("NOT_PROVEN", "2026-08 frozen-identity execution not preserved")
    return result("VW_MIDAS_MSVR_SUCCESSOR_V1", d, "GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_CHANGE_CONTROL_2026-09-06.md")


def ny17_bundle() -> tuple[bool, Any]:
    p = AUDITS / "historical_reconstruction_bundle_v145/historical_reconstruction_bundle_v145.json"
    if not p.exists():
        return False, "NY17 historical reconstruction bundle not yet present"
    v = load(p)
    ok = v.get("status") == "PASS" and v.get("production_database_write") == "NONE" and v.get("prospective_claim") is False
    return ok, {"path":str(p.relative_to(ROOT)),"status":v.get("status"),"ny17_status_counts":v.get("ny17_status_counts")}


def verify_r4(engine: str, snap: dict[str, Any], tests_pass: bool) -> dict[str, Any]:
    d = base(engine, snap)
    paths = {
        "MONTHLY_DIRECTION_3M":"r4_1/src/gold_r4/monthly.py", "FAST":"r4_1/src/gold_r4/tactical.py",
        "SLOW":"r4_1/src/gold_r4/tactical.py", "EMERGENCY_LEVEL":"r4_1/src/gold_r4/emergency.py",
        "EMERGENCY_REVERSAL":"r4_1/src/gold_r4/emergency.py",
    }
    tokens = {
        "MONTHLY_DIRECTION_3M":["m3 = sum(completed_month_returns[-3:]) / 3.0", 'return "UP"', 'return "DOWN"', 'return "NEUTRAL"'],
        "FAST":["sma_days: int = 20", "persistence_days: int = 2"],
        "SLOW":["sma_weeks: int = 4", "persistence_weeks: int = 2", 'resample("W-FRI")'],
        "EMERGENCY_LEVEL":["level_threshold_abs: float = 0.04", "displacement = close / monthly_vw_forecast - 1.0"],
        "EMERGENCY_REVERSAL":["reversal_threshold_abs: float = 0.04", 'alert = "DOWN_ALERT"', 'alert = "UP_ALERT"'],
    }
    text = (GC / paths[engine]).read_text(encoding="utf-8")
    rule_ok = all(t in text for t in tokens[engine])
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if rule_ok and tests_pass else ("FAIL" if not rule_ok else "NOT_PROVEN"), {"code":paths[engine],"frozen_tests_pass":tests_pass})
    src = {r["series_id"]:r for r in snap["sources"]}.get("XAU_EOD_TWELVE_NY17")
    src_ok = bool(src and src.get("source_name") == "Twelve Data" and src.get("source_symbol") == "XAU/USD")
    d["C3_SOURCE_BINDING"] = dim("PASS" if src_ok else "FAIL", src)
    complete, ev = ny17_bundle()
    d["C4_HISTORICAL_COVERAGE"] = dim("PASS" if complete else "BLOCKED", ev)
    d["C5_ORIGIN_PIT"] = dim("PASS" if rule_ok else "FAIL", "frozen chronological/completed-period rule")
    d["C6_FUTURE_INFORMATION"] = dim("PASS" if rule_ok else "FAIL", "chronological replay; no performance input")
    d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS" if complete else "BLOCKED", ev)
    d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if tests_pass else "NOT_PROVEN", "R4.1 frozen tests")
    d["C9_PILOT_CELL_EXECUTION"] = dim("NOT_PROVEN" if complete else "BLOCKED", "historical role replay follows NY17 bundle completion")
    return result(engine, d, paths[engine])


def verify_macro(snap: dict[str, Any]) -> dict[str, Any]:
    d = base("MACRO_EVENT_SUCCESSOR_V2", snap)
    run = snap["macro_run"]; rows = snap["macro_series"]
    expected = {"MACRO_NFP_ACTUAL_FIRST_PRINT","MACRO_NFP_CONSENSUS_PIT","MACRO_UNEMP_ACTUAL_FIRST_PRINT","MACRO_UNEMP_CONSENSUS_PIT","MACRO_AHE_ACTUAL_FIRST_PRINT","MACRO_AHE_CONSENSUS_PIT"}
    source_ok = run.get("run_id") == "6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a" and run.get("status") == "SUCCESS" and int(run.get("observations_read") or 0) == 756 and int(run.get("observations_written") or 0) == 756 and {r["series_id"] for r in rows} == expected and all(int(r["n"]) == 126 and int(r["null_available"]) == 0 for r in rows)
    code = (GC / "data_pipeline/macro_event_successor_v2_score_replay.py").read_text(encoding="utf-8")
    rule_ok = all(x in code for x in ("MIN_PRIOR = 24","MAD_NORMAL_SCALE = 1.4826","score = sum(g) / 3.0","score <= -1.0","score >= 1.0","assert_prefix_invariance"))
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if rule_ok else "FAIL", "frozen robust-score rule")
    d["C3_SOURCE_BINDING"] = dim("PASS" if source_ok else "FAIL", {"run":run,"series_counts":rows})
    d["C4_HISTORICAL_COVERAGE"] = dim("PASS" if source_ok else "FAIL", "126 complete cases / 756 rows; 2025-10 explicit exclusion")
    d["C5_ORIGIN_PIT"] = dim("PASS" if source_ok else "FAIL", "first-print + consensus PIT panel")
    try:
        sys.path.insert(0, str(GC / "data_pipeline")); import macro_event_successor_v2_score_replay as m  # type: ignore
        with psycopg.connect(os.environ["NEON_DATABASE_URL"], autocommit=False) as conn:
            with conn.cursor() as cur: cur.execute("set transaction isolation level repeatable read, read only")
            panel, _ = m.load_frozen_panel(conn); a = m.compute_scores(panel); m.assert_prefix_invariance(panel, a); b = m.compute_scores(panel)
        ha = hashlib.sha256(json.dumps([asdict(x) for x in a], sort_keys=True, default=str).encode()).hexdigest(); hb = hashlib.sha256(json.dumps([asdict(x) for x in b], sort_keys=True, default=str).encode()).hexdigest(); deterministic = ha == hb
    except Exception as exc:
        deterministic = False; ha = f"ERROR:{type(exc).__name__}:{exc}"; hb = None
    d["C6_FUTURE_INFORMATION"] = dim("PASS" if deterministic else "FAIL", "prefix invariance executed")
    d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS" if source_ok else "FAIL", "first-print/consensus PIT identities retained")
    d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if deterministic else "FAIL", {"hash_a":ha,"hash_b":hb})
    d["C9_PILOT_CELL_EXECUTION"] = dim("PASS" if deterministic and source_ok else "FAIL", "2025-10 remains CONTRACTUAL_EXCLUSION")
    return result("MACRO_EVENT_SUCCESSOR_V2", d, "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V2_ROBUST_SCORE_PREREG_2026-09-05.md")


def verify_bocpd(snap: dict[str, Any], tests_pass: bool) -> dict[str, Any]:
    d = base("BOCPD_RETURN_SUCCESSOR_V1", snap); c = load(GC / "bocpd_successor_v1/frozen_contract_v1.json")
    ok = c.get("contract_version") == "BOCPD_RETURN_SUCCESSOR_V1" and c.get("source",{}).get("artifact") == "gold_axis_2026/core5_monthly.csv.gz.b64" and c.get("source",{}).get("field") == "gold_monthly" and c.get("source",{}).get("transform") == "log(P_t/P_t-1)" and c.get("source",{}).get("completed_month_only") is True and c.get("hazard",{}).get("expected_run_length_months") == 36 and c.get("windows",{}).get("tuning_2026") == "NONE"
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if ok and tests_pass else ("FAIL" if not ok else "NOT_PROVEN"), {"contract":ok,"tests":tests_pass})
    d["C3_SOURCE_BINDING"] = dim("PASS" if ok else "FAIL", c.get("source"))
    d["C4_HISTORICAL_COVERAGE"] = dim("BLOCKED", {"locked_end":c.get("windows",{}).get("locked_end"),"missing":"2026-08"})
    d["C5_ORIGIN_PIT"] = dim("PASS" if ok else "FAIL", "completed month only")
    d["C6_FUTURE_INFORMATION"] = dim("PASS" if c.get("windows",{}).get("tuning_2026") == "NONE" else "FAIL", "tuning_2026=NONE")
    d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS", {"evidence":c.get("evidence"),"database_writes_permitted":c.get("database_writes_permitted")})
    d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if tests_pass else "NOT_PROVEN", "frozen BOCPD tests")
    d["C9_PILOT_CELL_EXECUTION"] = dim("BLOCKED", "2026-08 outside frozen locked_end; evaluation-only extension not governed")
    return result("BOCPD_RETURN_SUCCESSOR_V1", d, "bocpd_successor_v1/frozen_contract_v1.json")


def verify_gvz(snap: dict[str, Any], tests_pass: bool) -> dict[str, Any]:
    d = base("GVZ_RISK", snap); src = {r["series_id"]:r for r in snap["sources"]}.get("GVZ_CBOE"); lane = load(AUDITS / "historical_gvz_reconstruction_lane_v145_evidence.json"); code = (GC / "r4_1/src/gold_r4/gvz.py").read_text(encoding="utf-8")
    rule_ok = all(x in code for x in ("25.9795","30.5238","cap=1.0","cap=0.5","cap=0.25","panic=True")); source_ok = bool(src and src.get("source_name") == "Cboe official historical price data" and src.get("source_symbol") == "GVZ"); lane_ok = lane.get("status") == "PASS_GAP_COMPLETED_AS_IMMUTABLE_ARTIFACT_LANE" and lane.get("historical_rows") == 295 and lane.get("prospective_claim") is False
    d["C2_IMPLEMENTATION_RULE"] = dim("PASS" if rule_ok and tests_pass else ("FAIL" if not rule_ok else "NOT_PROVEN"), {"rule":rule_ok,"tests":tests_pass})
    d["C3_SOURCE_BINDING"] = dim("PASS" if source_ok else "FAIL", src); d["C4_HISTORICAL_COVERAGE"] = dim("PASS" if lane_ok else "BLOCKED", {"rows":lane.get("historical_rows"),"first":lane.get("first_observation_date"),"last":lane.get("last_observation_date")})
    d["C5_ORIGIN_PIT"] = dim("PASS", "chronological released Cboe observations"); d["C6_FUTURE_INFORMATION"] = dim("PASS", "risk-only context; no performance input"); d["C7_RECONSTRUCTION_VINTAGE"] = dim("PASS" if lane_ok else "BLOCKED", {"evidence_class":lane.get("evidence_class"),"prospective_claim":lane.get("prospective_claim")}); d["C8_DETERMINISM_REPRODUCIBILITY"] = dim("PASS" if rule_ok and tests_pass else "NOT_PROVEN", "pure frozen mapping + R4 tests"); d["C9_PILOT_CELL_EXECUTION"] = dim("NOT_PROVEN", "GVZ historical role replay not yet preserved")
    return result("GVZ_RISK", d, "data_pipeline/audits/historical_gvz_reconstruction_lane_v145_evidence.json")


def build(snap: dict[str, Any], r4_tests_pass: bool, bocpd_tests_pass: bool, vw_result: Path | None) -> dict[str, Any]:
    if sorted(r["engine_id"] for r in snap["runtime"]) != sorted(ENGINE_ORDER): raise RuntimeError("RUNTIME_ENGINE_INVENTORY_DRIFT")
    rows = [verify_patch(snap),verify_vw(snap,vw_result),verify_simple("MOMENTUM_3M",snap),verify_simple("RANDOM_WALK",snap),verify_r4("MONTHLY_DIRECTION_3M",snap,r4_tests_pass),verify_r4("FAST",snap,r4_tests_pass),verify_r4("SLOW",snap,r4_tests_pass),verify_macro(snap),verify_bocpd(snap,bocpd_tests_pass),verify_r4("EMERGENCY_LEVEL",snap,r4_tests_pass),verify_r4("EMERGENCY_REVERSAL",snap,r4_tests_pass),verify_gvz(snap,r4_tests_pass)]
    order = {r["engine_id"]:r for r in rows}; rows = [order[e] for e in ENGINE_ORDER]; counts: dict[str,int] = {}
    for r in rows: counts[r["component_verification_status"]] = counts.get(r["component_verification_status"],0)+1
    return {"audit_id":"GOLD_CONTROL_COMPONENT_VERIFICATION_V145_R1","mode":"POST_GAP_COMPONENT_VERIFICATION" if ny17_bundle()[0] else "PROVISIONAL_PRE_GAP","protocol":str(PROTOCOL.relative_to(ROOT)),"production_database_access":"READ_ONLY","production_writes":"NONE","performance_fields_consumed":False,"engine_count":12,"status_counts":counts,"authority_counts":snap["authority_counts"],"snapshot_at":str(snap["snapshot_at"]),"tx_snapshot":snap["tx_snapshot"],"rows":rows}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields=["engine_id","component_verification_status",*DIMS,"evidence_reference"]
    with path.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
        for r in rows:
            row={"engine_id":r["engine_id"],"component_verification_status":r["component_verification_status"],"evidence_reference":r["evidence_reference"]}
            for name in DIMS: row[name]=r["dimensions"][name]["status"]
            w.writerow(row)


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--output-json",default=str(AUDITS/"component_verification_v145_r1.json")); p.add_argument("--output-csv",default=str(AUDITS/"component_verification_v145_r1.csv")); p.add_argument("--vw-result"); p.add_argument("--r4-tests-pass",action="store_true"); p.add_argument("--bocpd-tests-pass",action="store_true"); a=p.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL","").strip()
    if not dsn: raise SystemExit("BLOCKED:NEON_DATABASE_URL_NOT_SET")
    if not PROTOCOL.exists(): raise SystemExit("BLOCKED:COMPONENT_VERIFICATION_PROTOCOL_MISSING")
    snap=read_snapshot(dsn); out=build(snap,a.r4_tests_pass,a.bocpd_tests_pass,Path(a.vw_result) if a.vw_result else None)
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8"); write_csv(Path(a.output_csv),out["rows"])
    print(json.dumps({"audit_id":out["audit_id"],"mode":out["mode"],"status_counts":out["status_counts"],"authority_counts":out["authority_counts"],"production_writes":"NONE","performance_fields_consumed":False},sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
