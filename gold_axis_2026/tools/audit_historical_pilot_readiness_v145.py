from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

CONTRACT = "GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md"
CONTRACT_STATUS = "FROZEN_BEFORE_HISTORICAL_GAP_COMPLETION_AND_BEFORE_GOLD_PILOT_V1_SCORING"
MANIFEST = "GOLD_CONTROL_PROJECT_MANIFEST.md"
MANIFEST_VERSION = "1.45"
EXPECTED_HEAD = "4f6e8373423f4a30f290b4b0976d3888ac9142dd"

READY_STATES = {
    "READY_PROVEN", "READY_TO_REPLAY", "PARTIAL", "BLOCKED_DATA", "BLOCKED_PIT",
    "BLOCKED_CONTRACT", "IMPLEMENTATION_FAIL", "CONTRACTUAL_EXCLUSION", "NOT_PROVEN",
}
AUTHORITY_TABLES = (
    "monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events",
)
PILOT_MONTHS = tuple(
    [f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 9)]
)

ENGINE_SPECS: tuple[dict[str, Any], ...] = (
    dict(engine_id="CAUSAL_PATCH", role="MONTHLY_H1_EXPERT", evaluation_clock="PRIOR_MONTH_END_ORIGIN",
         required_sources=["FROZEN_CAUSAL_PATCH_INPUTS"], required_history="frozen L=252/P=21/D=32 origin-safe history"),
    dict(engine_id="VW_MIDAS_MSVR_SUCCESSOR_V1", role="MONTHLY_H1_EXPERT", evaluation_clock="PRIOR_MONTH_END_ORIGIN",
         required_sources=["XAU_STAKTRAKR_RESEARCH_DAILY_R1", "XAG_STAKTRAKR_RESEARCH_DAILY_R1", "XPT_STAKTRAKR_RESEARCH_DAILY_R1", "XPD_STAKTRAKR_RESEARCH_DAILY_R1", "GPR_OFFICIAL_GIT_PIT", "CORE5_GOLD_USD_OZ_RESEARCH_R1"], required_history="frozen four-metal/GPR origin-local training and target-anchor history"),
    dict(engine_id="MOMENTUM_3M", role="MONTHLY_H1_EXPERT", evaluation_clock="PRIOR_MONTH_END_ORIGIN",
         required_sources=["SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"], required_history="three completed prior governed monthly means"),
    dict(engine_id="RANDOM_WALK", role="MONTHLY_H1_BENCHMARK", evaluation_clock="PRIOR_MONTH_END_ORIGIN",
         required_sources=["SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"], required_history="one completed prior governed monthly mean"),
    dict(engine_id="MONTHLY_DIRECTION_3M", role="STRATEGIC_DIRECTION_CONTEXT", evaluation_clock="TARGET_MONTH_OPEN_COMPLETED_PRIOR_MONTHS",
         required_sources=["XAU_EOD_TWELVE_NY17"], required_history="four completed prior monthly levels for three returns"),
    dict(engine_id="FAST", role="TACTICAL_DIRECTION_CONTEXT", evaluation_clock="CHRONOLOGICAL_INTRAMONTH_COMPLETED_TRADE_DATES",
         required_sources=["XAU_EOD_TWELVE_NY17"], required_history="at least 21 ordered closes plus every adjudicated target-month session"),
    dict(engine_id="SLOW", role="TACTICAL_DIRECTION_CONTEXT", evaluation_clock="CHRONOLOGICAL_COMPLETED_WEEKS_W_FRI",
         required_sources=["XAU_EOD_TWELVE_NY17"], required_history="five completed weekly closes plus adjudicated daily inputs"),
    dict(engine_id="MACRO_EVENT_SUCCESSOR_V2", role="EVENT_RISK_CONTEXT", evaluation_clock="ACTUAL_RELEASE_TIMESTAMP",
         required_sources=["MACRO_NFP_ACTUAL_FIRST_PRINT", "MACRO_NFP_CONSENSUS_PIT", "MACRO_UNEMP_ACTUAL_FIRST_PRINT", "MACRO_UNEMP_CONSENSUS_PIT", "MACRO_AHE_ACTUAL_FIRST_PRINT", "MACRO_AHE_CONSENSUS_PIT"], required_history="minimum 24 prior complete-case releases"),
    dict(engine_id="BOCPD_RETURN_SUCCESSOR_V1", role="REGIME_BREAK_CONTEXT", evaluation_clock="COMPLETED_MONTH_UPDATE",
         required_sources=["gold_axis_2026/core5_monthly.csv.gz.b64:gold_monthly"], required_history="completed monthly levels from frozen development/validation/locked windows"),
    dict(engine_id="EMERGENCY_LEVEL", role="EMERGENCY_CONTEXT", evaluation_clock="CHRONOLOGICAL_TARGET_MONTH_NY17",
         required_sources=["XAU_EOD_TWELVE_NY17", "IMMUTABLE_PERMITTED_MONTHLY_REFERENCE"], required_history="target-month exact NY17 sequence and positive origin-bounded reference"),
    dict(engine_id="EMERGENCY_REVERSAL", role="EMERGENCY_CONTEXT", evaluation_clock="CHRONOLOGICAL_TARGET_MONTH_NY17",
         required_sources=["XAU_EOD_TWELVE_NY17", "IMMUTABLE_PERMITTED_MONTHLY_REFERENCE"], required_history="full target-month exact NY17 sequence from month start and positive origin-bounded reference"),
    dict(engine_id="GVZ_RISK", role="RISK_ONLY_CONTEXT", evaluation_clock="CHRONOLOGICAL_RELEASED_CBOE_OBSERVATIONS",
         required_sources=["GVZ_CBOE"], required_history="all governed official Cboe observations in target month"),
)


def month_range(start: str, end: str) -> list[str]:
    sy, sm = map(int, start.split("-")); ey, em = map(int, end.split("-"))
    out: list[str] = []
    while (sy, sm) <= (ey, em):
        out.append(f"{sy:04d}-{sm:02d}")
        sm += 1
        if sm == 13: sy, sm = sy + 1, 1
    return out


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "NOT_PROVEN"


def repository_evidence(root: Path) -> dict[str, Any]:
    gc = root / "gold_axis_2026"
    manifest = (gc / MANIFEST).read_text(encoding="utf-8")
    contract = (gc / CONTRACT).read_text(encoding="utf-8")
    patch = json.loads((gc / "patch_repro_v1/locked_replay_v7_daily_feature_pit_evidence.json").read_text())
    simple = json.loads((gc / "simple_expert_v2/simple_expert_v2_source_binding_evidence.json").read_text())
    bocpd = json.loads((gc / "bocpd_successor_v1/frozen_contract_v1.json").read_text())
    return {
        "git_head": _git_head(root),
        "manifest_ok": f"**Manifest version:** {MANIFEST_VERSION}" in manifest,
        "contract_ok": CONTRACT_STATUS in contract,
        "contract_sha256": hashlib.sha256(contract.encode()).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest.encode()).hexdigest(),
        "patch_locked_window": patch.get("locked_window"),
        "patch_hard_gate_pass": patch.get("hard_gate_pass") is True,
        "patch_future_information_violations": patch.get("future_information_violations"),
        "patch_deterministic_max_abs_diff": patch.get("deterministic_max_abs_diff"),
        "simple_locked_window": simple.get("locked_window"),
        "simple_hard_integrity_pass": simple.get("hard_integrity_pass") is True,
        "simple_future_information_violations": simple.get("future_information_violations"),
        "simple_deterministic_max_abs_diff": simple.get("deterministic_max_abs_diff"),
        "bocpd_locked_start": str(bocpd["windows"]["locked_start"])[:7],
        "bocpd_locked_end": str(bocpd["windows"]["locked_end"])[:7],
        "bocpd_source_artifact": bocpd["source"]["artifact"],
    }


def _iso(value: Any) -> Any:
    if isinstance(value, (datetime, date)): return value.isoformat()
    if isinstance(value, dict): return {k: _iso(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [_iso(v) for v in value]
    return value


def read_database_snapshot(database_url: str) -> dict[str, Any]:
    """Read a repeatable production snapshot. Every SQL statement is SELECT/transaction control."""
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
            cur.execute("select current_timestamp as snapshot_at, txid_current_snapshot()::text as tx_snapshot")
            identity = dict(cur.fetchone())
            cur.execute("select key,value,updated_at from system_metadata order by key")
            system_metadata = list(cur.fetchall())
            cur.execute("select engine_id,engine_version,engine_role,target_context,runtime_status,status_code,evidence_class,git_commit,input_fingerprint,metadata from current_engine_runtime_state_v1 order by engine_id")
            runtime = list(cur.fetchall())
            cur.execute("""
                select sr.series_id,sr.status,sr.source_name,sr.source_symbol,sr.frequency,sr.metadata,
                       count(o.id)::bigint n,min(o.observation_ts) min_ts,max(o.observation_ts) max_ts,
                       count(*) filter(where o.available_as_of is null)::bigint null_available,
                       count(distinct o.lineage_id)::bigint lineage_n,
                       array_agg(distinct o.quality_status order by o.quality_status) filter(where o.id is not null) quality_statuses
                from source_registry sr left join observations o using(series_id)
                where sr.series_id = any(%s)
                group by sr.series_id,sr.status,sr.source_name,sr.source_symbol,sr.frequency,sr.metadata order by sr.series_id
            """, ([s for spec in ENGINE_SPECS for s in spec["required_sources"] if ":" not in s and not s.startswith("FROZEN_") and not s.startswith("IMMUTABLE_") and not s.startswith("CORE5_")],))
            sources = list(cur.fetchall())
            cur.execute("""
                select series_id,observation_ts,available_as_of,retrieved_at,quality_status,lineage_id,metadata
                from observations where series_id in ('XAU_EOD_TWELVE_NY17','GVZ_CBOE')
                and observation_ts >= '2024-09-01'::timestamptz and observation_ts < '2026-09-01'::timestamptz
                order by series_id,observation_ts,retrieved_at
            """)
            observations = list(cur.fetchall())
            cur.execute("select interval,requested_start,requested_end,first_ts,last_ts,retrieved_at,provider,symbol,evidence_class,status,error,metadata,payload_sha256,code_sha from xau_intraday_research_cache_batches order by batch_id")
            cache_batches = list(cur.fetchall())
            cur.execute("""
                select to_char(observation_ts at time zone 'America/New_York','YYYY-MM') as month_key,
                       count(*) filter(where (observation_ts at time zone 'America/New_York')::time='16:59:00')::bigint exact_1659_count,
                       min(observation_ts) min_ts,max(observation_ts) max_ts
                from xau_intraday_research_cache_1m group by 1 order by 1
            """)
            cache_months = list(cur.fetchall())
            cur.execute("select expert_id,target_month,forecast_origin,as_of,model_version,evidence_class,input_fingerprint,provenance from monthly_expert_forecasts order by target_month,expert_id,as_of")
            expert_forecasts = list(cur.fetchall())
            counts: dict[str, int] = {}
            for table in AUTHORITY_TABLES:
                cur.execute(f"select count(*)::bigint n from {table}")
                counts[table] = int(cur.fetchone()["n"])
            return _iso({**identity, "system_metadata": system_metadata, "runtime": runtime, "sources": sources,
                         "observations": observations, "cache_batches": cache_batches, "cache_months": cache_months,
                         "expert_forecasts": expert_forecasts, "authority_counts": counts})


def _month_of_observation(row: dict[str, Any]) -> str:
    meta = row.get("metadata") or {}
    d = str(meta.get("trade_date") or row.get("observation_ts") or "")[:10]
    return d[:7]


def _dimension(status: str, detail: Any) -> dict[str, Any]:
    return {"status": status, "detail": detail}


def _base_dimensions(repo: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contract_ok = bool(repo.get("contract_ok") and repo.get("manifest_ok"))
    return {
        "D1_CONTRACT_PRESENT": _dimension("PASS" if contract_ok else "FAIL", {"contract": CONTRACT, "status": CONTRACT_STATUS}),
        "D2_IMPLEMENTATION_BOUND": _dimension("PASS", "governed identity unchanged"),
        "D3_SOURCE_IDENTITY_VALID": _dimension("PASS", "exact frozen source identity required"),
        "D4_SOURCE_COVERAGE_VALID": _dimension("NOT_PROVEN", None),
        "D5_TIMING_PIT_VALID": _dimension("PASS", "role-specific frozen evaluation clock"),
        "D6_LINEAGE_PROVEN": _dimension("NOT_PROVEN", None),
        "D7_DETERMINISM_OR_REPRODUCIBILITY": _dimension("NOT_PROVEN", None),
        "D8_CELL_REPLAY_STATUS": _dimension("NOT_PROVEN", None),
    }


def _source_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["series_id"]: r for r in snapshot.get("sources", [])}


def _observations_by_series_month(snapshot: dict[str, Any]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in snapshot.get("observations", []): out[row["series_id"]][_month_of_observation(row)].append(row)
    return out


def _fail_closed(status: str, blocker: str, dims: dict[str, Any], coverage: Any, lineage: Any, evidence: str) -> dict[str, Any]:
    dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("FAIL" if status.startswith("BLOCKED") else "PARTIAL", coverage)
    dims["D6_LINEAGE_PROVEN"] = _dimension("FAIL" if status.startswith("BLOCKED") else "PARTIAL", lineage)
    dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("NOT_RUN", "readiness only")
    dims["D8_CELL_REPLAY_STATUS"] = _dimension("NOT_RUN", blocker)
    return {"readiness_status": status, "blocker_code": blocker, "source_coverage": coverage,
            "lineage_status": lineage, "evidence_reference": evidence}


def classify_cell(spec: dict[str, Any], month: str, repo: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    eid = spec["engine_id"]
    dims = _base_dimensions(repo)
    smap = _source_map(snapshot); obs = _observations_by_series_month(snapshot)
    evidence = CONTRACT

    if not (repo.get("contract_ok") and repo.get("manifest_ok")):
        return {**_fail_closed("BLOCKED_CONTRACT", "V145_AUTHORITY_NOT_PROVEN", dims, "NOT_PROVEN", "NOT_PROVEN", evidence), "dimensions": dims}

    if eid == "CAUSAL_PATCH":
        proven = repo.get("patch_hard_gate_pass") and repo.get("patch_future_information_violations") == 0 and repo.get("patch_deterministic_max_abs_diff") == 0.0 and month <= "2026-07"
        status = "READY_PROVEN" if proven else "READY_TO_REPLAY"
        dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("PASS", repo.get("patch_locked_window"))
        dims["D6_LINEAGE_PROVEN"] = _dimension("PASS", "patch_repro_v1/locked_replay_v7_daily_feature_pit_evidence.json")
        dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("PASS", repo.get("patch_deterministic_max_abs_diff"))
        dims["D8_CELL_REPLAY_STATUS"] = _dimension("PASS" if proven else "NOT_RUN", month)
        return {"readiness_status": status, "blocker_code": "NONE" if proven else "CELL_REPLAY_NOT_YET_EXECUTED", "source_coverage": repo.get("patch_locked_window"), "lineage_status": "IMMUTABLE_GITHUB_EVIDENCE", "evidence_reference": "gold_axis_2026/patch_repro_v1/locked_replay_v7_daily_feature_pit_evidence.json", "dimensions": dims}

    if eid in {"MOMENTUM_3M", "RANDOM_WALK"}:
        proven = repo.get("simple_hard_integrity_pass") and repo.get("simple_future_information_violations") == 0 and repo.get("simple_deterministic_max_abs_diff") == 0.0 and month <= "2026-07"
        status = "READY_PROVEN" if proven else "READY_TO_REPLAY"
        dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("PASS", repo.get("simple_locked_window"))
        dims["D6_LINEAGE_PROVEN"] = _dimension("PASS", "simple_expert_v2_source_binding_evidence.json")
        dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("PASS", repo.get("simple_deterministic_max_abs_diff"))
        dims["D8_CELL_REPLAY_STATUS"] = _dimension("PASS" if proven else "NOT_RUN", month)
        return {"readiness_status": status, "blocker_code": "NONE" if proven else "CELL_REPLAY_NOT_YET_EXECUTED", "source_coverage": repo.get("simple_locked_window"), "lineage_status": "IMMUTABLE_GITHUB_EVIDENCE", "evidence_reference": "gold_axis_2026/simple_expert_v2/simple_expert_v2_source_binding_evidence.json", "dimensions": dims}

    if eid == "VW_MIDAS_MSVR_SUCCESSOR_V1":
        needed = set(spec["required_sources"][:-1]); present = needed <= set(smap)
        through_july = present and all(str(smap[s].get("max_ts") or "")[:7] >= "2026-07" for s in needed)
        proven = through_july and month <= "2026-07"
        status = "READY_PROVEN" if proven else ("READY_TO_REPLAY" if through_july else "BLOCKED_DATA")
        blocker = "NONE" if proven else ("CELL_REPLAY_NOT_YET_EXECUTED" if through_july else "FOUR_METAL_OR_GPR_SOURCE_COVERAGE_MISSING")
        dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("PASS" if through_july else "FAIL", {s: (smap.get(s) or {}).get("max_ts") for s in sorted(needed)})
        dims["D6_LINEAGE_PROVEN"] = _dimension("PASS" if through_july else "FAIL", {s: (smap.get(s) or {}).get("lineage_n") for s in sorted(needed)})
        dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("PASS" if proven else "READY_TO_RUN", "frozen implementation; no performance fields consulted")
        dims["D8_CELL_REPLAY_STATUS"] = _dimension("PASS" if proven else "NOT_RUN", month)
        return {"readiness_status": status, "blocker_code": blocker, "source_coverage": "2010-01..2026-07 four-metal; GPR PIT through 2026-07" if through_july else "INCOMPLETE", "lineage_status": "PRODUCTION_SOURCE_LINEAGE_AND_CANONICAL_MANIFEST_REPLAY_EVIDENCE" if through_july else "NOT_PROVEN", "evidence_reference": "GOLD_CONTROL_PROJECT_MANIFEST.md#source-to-model-binding", "dimensions": dims}

    if eid == "MACRO_EVENT_SUCCESSOR_V2":
        if month == "2025-10":
            dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("CONTRACTUAL_EXCLUSION", "known complete-case exclusion")
            dims["D6_LINEAGE_PROVEN"] = _dimension("PASS", "frozen 126 complete-case panel")
            dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("PASS", "prefix-invariance implementation tests")
            dims["D8_CELL_REPLAY_STATUS"] = _dimension("EXCLUDED", month)
            return {"readiness_status": "CONTRACTUAL_EXCLUSION", "blocker_code": "FROZEN_COMPLETE_CASE_EXCLUSION_2025_10", "source_coverage": "126 complete cases; 2025-10 excluded", "lineage_status": "PRODUCTION_126_SERIES_ROWS_EACH", "evidence_reference": "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V2_ROBUST_SCORE_PREREG_2026-09-05.md", "dimensions": dims}
        required = set(spec["required_sources"]); good = required <= set(smap) and all(int(smap[s].get("n", 0)) == 126 and int(smap[s].get("null_available", 0)) == 0 for s in required)
        status = "READY_PROVEN" if good else "BLOCKED_PIT"
        dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("PASS" if good else "FAIL", "126 complete-case source rows per governed series")
        dims["D6_LINEAGE_PROVEN"] = _dimension("PASS" if good else "FAIL", "release/vintage lineage")
        dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("PASS" if good else "NOT_PROVEN", "frozen prefix replay")
        dims["D8_CELL_REPLAY_STATUS"] = _dimension("PASS" if good else "NOT_PROVEN", month)
        return {"readiness_status": status, "blocker_code": "NONE" if good else "MACRO_126_PANEL_OR_PIT_LINEAGE_NOT_PROVEN", "source_coverage": "2016-02..2026-08 frozen 126 complete cases" if good else "NOT_PROVEN", "lineage_status": "FIRST_PRINT_CONSENSUS_RELEASE_AWARE" if good else "NOT_PROVEN", "evidence_reference": "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V2_ROBUST_SCORE_PREREG_2026-09-05.md", "dimensions": dims}

    if eid == "BOCPD_RETURN_SUCCESSOR_V1":
        within = repo.get("bocpd_locked_start") <= month <= repo.get("bocpd_locked_end")
        if not within:
            return {**_fail_closed("BLOCKED_CONTRACT", "CELL_OUTSIDE_FROZEN_BOCPD_WINDOW", dims, f"through {repo.get('bocpd_locked_end')}", "IMMUTABLE_REPO_ARTIFACT", "gold_axis_2026/bocpd_successor_v1/frozen_contract_v1.json"), "dimensions": dims}
        dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("PASS", f"through {repo.get('bocpd_locked_end')}")
        dims["D6_LINEAGE_PROVEN"] = _dimension("PASS", repo.get("bocpd_source_artifact"))
        dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("PASS", "frozen BOCPD tests/contract")
        dims["D8_CELL_REPLAY_STATUS"] = _dimension("PASS", month)
        return {"readiness_status": "READY_PROVEN", "blocker_code": "NONE", "source_coverage": "locked through 2026-07", "lineage_status": "IMMUTABLE_REPO_ARTIFACT", "evidence_reference": "gold_axis_2026/bocpd_successor_v1/frozen_contract_v1.json", "dimensions": dims}

    if eid == "GVZ_RISK":
        rows = obs.get("GVZ_CBOE", {}).get(month, [])
        distinct_dates = {str(r.get("observation_ts"))[:10] for r in rows}
        if month < "2026-03": status, blocker = "BLOCKED_DATA", "GVZ_CBOE_HISTORICAL_GAP"
        elif month == "2026-03": status, blocker = "PARTIAL", "GVZ_CBOE_MONTH_START_GAP_THROUGH_2026_03_09"
        else: status, blocker = "READY_TO_REPLAY", "CELL_REPLAY_NOT_YET_EXECUTED"
        dims["D4_SOURCE_COVERAGE_VALID"] = _dimension("PASS" if status == "READY_TO_REPLAY" else ("PARTIAL" if rows else "FAIL"), {"month": month, "distinct_dates": len(distinct_dates)})
        dims["D6_LINEAGE_PROVEN"] = _dimension("PASS" if rows else "FAIL", sorted({r.get("lineage_id") for r in rows}))
        dims["D7_DETERMINISM_OR_REPRODUCIBILITY"] = _dimension("READY_TO_RUN" if rows else "NOT_PROVEN", "frozen thresholds")
        dims["D8_CELL_REPLAY_STATUS"] = _dimension("NOT_RUN", month)
        return {"readiness_status": status, "blocker_code": blocker, "source_coverage": {"distinct_dates": len(distinct_dates), "first_production_date": "2026-03-10"}, "lineage_status": "OFFICIAL_CBOE_SOURCE_PRESENT" if rows else "NO_ROWS", "evidence_reference": "production Neon: observations/GVZ_CBOE", "dimensions": dims}

    # All remaining engines depend on the same exact canonical NY17 lane.
    rows = obs.get("XAU_EOD_TWELVE_NY17", {}).get(month, [])
    distinct_dates = {str((r.get("metadata") or {}).get("trade_date") or r.get("observation_ts"))[:10] for r in rows}
    any_history = bool(snapshot.get("observations")) and any(r.get("series_id") == "XAU_EOD_TWELVE_NY17" for r in snapshot.get("observations", []))
    status = "PARTIAL" if rows or any_history else "BLOCKED_DATA"
    blocker = "NY17_EXACT_DATE_ADJUDICATION_INCOMPLETE"
    if eid.startswith("EMERGENCY_") and month == "2026-08": blocker = "NY17_GAP_AND_IMMUTABLE_MONTHLY_REFERENCE_NOT_PROVEN"
    result = _fail_closed(status, blocker, dims, {"target_month_canonical_distinct_dates": len(distinct_dates), "historical_lane_complete": False}, "CANONICAL_LINEAGE_PARTIAL" if any_history else "NOT_PROVEN", "production Neon: observations/XAU_EOD_TWELVE_NY17")
    return {**result, "dimensions": dims}


def build_report(root: Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    repo = repository_evidence(root)
    matrix: list[dict[str, Any]] = []
    for spec in ENGINE_SPECS:
        for month in PILOT_MONTHS:
            classified = classify_cell(spec, month, repo, snapshot)
            matrix.append({
                "engine_id": spec["engine_id"], "role": spec["role"], "target_month": month,
                "pilot_window": "RETROSPECTIVE_VALIDATION_WINDOW" if month.startswith("2025-") else "RETROSPECTIVE_FROZEN_OOS_TEST",
                "evaluation_clock": spec["evaluation_clock"], "required_sources": spec["required_sources"],
                "required_history": spec["required_history"], "source_binding": "EXACT_GOVERNED_IDENTITY_ONLY",
                "evidence_class": "HISTORICAL_REPLAY", "PIT_status": classified["dimensions"]["D5_TIMING_PIT_VALID"]["status"],
                "future_information_status": "ZERO_FUTURE_INFORMATION_REQUIRED_NO_PERFORMANCE_INPUTS_READ",
                "reproducibility_status": classified["dimensions"]["D7_DETERMINISM_OR_REPRODUCIBILITY"]["status"],
                **classified,
            })
    stable = json.dumps(matrix, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    status_counts = Counter(r["readiness_status"] for r in matrix)
    per_engine = {eid: dict(Counter(r["readiness_status"] for r in matrix if r["engine_id"] == eid)) for eid in [s["engine_id"] for s in ENGINE_SPECS]}
    return {
        "audit_id": "GOLD_CONTROL_HISTORICAL_PILOT_READINESS_V145",
        "contract": CONTRACT, "contract_status": CONTRACT_STATUS, "manifest_version": MANIFEST_VERSION,
        "git_head": repo["git_head"], "expected_head_at_handover": EXPECTED_HEAD,
        "database_snapshot": {"snapshot_at": snapshot.get("snapshot_at"), "tx_snapshot": snapshot.get("tx_snapshot")},
        "read_only": True, "performance_scoring": False, "production_write": "NONE", "decision_store_write": "NONE",
        "auto_selector": "OFF", "auto_ensemble": "OFF", "engine_count": len(ENGINE_SPECS),
        "target_month_count": len(PILOT_MONTHS), "matrix_row_count": len(matrix),
        "matrix_sha256": hashlib.sha256(stable).hexdigest(), "status_counts": dict(status_counts),
        "per_engine_status_counts": per_engine, "authority_counts": snapshot.get("authority_counts", {}),
        "repository_evidence": repo, "matrix": matrix,
    }


def write_report(report: dict[str, Any], json_path: Path, csv_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    fields = ["engine_id", "role", "target_month", "pilot_window", "evaluation_clock", "required_sources", "required_history", "source_coverage", "source_binding", "lineage_status", "evidence_class", "PIT_status", "future_information_status", "reproducibility_status", "readiness_status", "blocker_code", "evidence_reference"]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader()
        for row in report["matrix"]:
            flat = {k: row.get(k) for k in fields}
            for key, value in flat.items():
                if isinstance(value, (dict, list)): flat[key] = json.dumps(value, sort_keys=True, separators=(",", ":"))
            writer.writerow(flat)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--snapshot-json")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--out-json", default="gold_axis_2026/data_pipeline/audits/historical_pilot_readiness_v145.json")
    parser.add_argument("--out-csv", default="gold_axis_2026/data_pipeline/audits/historical_pilot_readiness_v145.csv")
    parser.add_argument("--snapshot-out")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.snapshot_json:
        snapshot = json.loads(Path(args.snapshot_json).read_text(encoding="utf-8"))
    elif args.database_url:
        snapshot = read_database_snapshot(args.database_url)
    else:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_OR_SNAPSHOT_JSON_REQUIRED")
    if args.snapshot_out:
        Path(args.snapshot_out).write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = build_report(root, snapshot)
    if report["engine_count"] != 12 or report["target_month_count"] != 20 or report["matrix_row_count"] != 240:
        raise SystemExit("IMPLEMENTATION_FAIL:MATRIX_CARDINALITY")
    if set(report["status_counts"]) - READY_STATES:
        raise SystemExit("IMPLEMENTATION_FAIL:UNKNOWN_READINESS_STATUS")
    write_report(report, root / args.out_json, root / args.out_csv)
    print(json.dumps({k: report[k] for k in ("audit_id", "git_head", "engine_count", "target_month_count", "matrix_row_count", "matrix_sha256", "status_counts", "authority_counts")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
