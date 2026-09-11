#!/usr/bin/env python3
"""Build the deterministic V1.49 Phase-2 engine-state PIT inventory panel.

This is an inventory artifact, not a forecasting or production-authority run.
Fail-closed statuses intentionally prevent unproven lanes from entering scoring.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from bisect import bisect_right
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
NY17 = ROOT / "data_pipeline/audits/component_role_replays_v145/ny17_context_role_replay_v145.csv"
GVZ = ROOT / "data_pipeline/audits/component_role_replays_v145/gvz_role_replay_v145.csv"
OUT = ROOT / "data_pipeline/audits/v149_phase2/engine_state_pit_panel_v1.csv"
META = ROOT / "data_pipeline/audits/v149_phase2/engine_state_pit_panel_v1.metadata.json"
EVIDENCE_CLASS = "RETROSPECTIVE_HISTORICAL_RECONSTRUCTION_NOT_PROSPECTIVE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_rows() -> list[dict[str, object]]:
    ny = sorted(read_rows(NY17), key=lambda r: r["date"])
    gvz = sorted(read_rows(GVZ), key=lambda r: r["observation_date"])
    if len({r["date"] for r in ny}) != len(ny):
        raise ValueError("DUPLICATE_NY17_ORIGIN")
    if len({r["observation_date"] for r in gvz}) != len(gvz):
        raise ValueError("DUPLICATE_GVZ_DATE")
    gvz_dates = [r["observation_date"] for r in gvz]
    rows: list[dict[str, object]] = []
    for i, r in enumerate(ny):
        gi = bisect_right(gvz_dates, r["date"]) - 1
        g = gvz[gi] if gi >= 0 else None
        origin = datetime.combine(datetime.fromisoformat(r["date"]).date(), time(17), ZoneInfo("America/New_York"))
        rows.append({
            "origin_index": i,
            "origin_date": r["date"],
            "origin_ts_ny": origin.isoformat(),
            "origin_clock_status": "READY_PROVEN_GOVERNED_NY17_SEMANTIC",
            "target_1d_date": ny[i + 1]["date"] if i + 1 < len(ny) else "",
            "target_1d_maturity": "MATURED" if i + 1 < len(ny) else "NOT_MATURED",
            "target_3d_date": ny[i + 3]["date"] if i + 3 < len(ny) else "",
            "target_3d_maturity": "MATURED" if i + 3 < len(ny) else "NOT_MATURED",
            "close": r["close"],
            "monthly_direction_3m": r["monthly_direction_3m"],
            "fast_state": r["fast_state"],
            "slow_state": r["slow_state"],
            "emergency_level": r["emergency_level"],
            "emergency_reversal": r["emergency_reversal"],
            "ny17_state_pit_status": "READY_TO_REPLAY_RETROSPECTIVE",
            "gvz_source_date": g["observation_date"] if g else "",
            "gvz_value": g["value"] if g else "",
            "gvz_cap": g["cap"] if g else "",
            "gvz_panic": g["panic"] if g else "",
            "gvz_pit_status": "BLOCKED_PIT_EXACT_RELEASE_CLOCK_NOT_PROVEN",
            "macro_event_v2_pit_status": "BLOCKED_PANEL_DAILY_ASOF_JOIN_NOT_CANONICAL",
            "bocpd_pit_status": "BLOCKED_DATA_DAILY_ORIGIN_STATE_NOT_FOUND",
            "market_shock_v3_status": "NOT_FOUND_CANONICAL",
            "scoring_eligibility": "B0_AND_B4_ONLY_NO_NEW_PHASE2_SCORE",
            "evidence_class": EVIDENCE_CLASS,
            "prospective_claim": "false",
        })
    return rows


def write_artifacts(out: Path = OUT, meta: Path = META) -> dict[str, object]:
    rows = build_rows()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    metadata = {
        "artifact_id": "GOLD_CONTROL_V149_PHASE2_ENGINE_STATE_PIT_PANEL_V1",
        "status": "PARTIAL_FAIL_CLOSED",
        "purpose": "SOURCE_CLOCK_AND_TARGET_MATURITY_INVENTORY_NOT_MODEL_SCORING",
        "evidence_class": EVIDENCE_CLASS,
        "production_authority": False,
        "production_writes": "NONE",
        "rows": len(rows),
        "matured_targets": {
            "NEXT_NY17_1D": sum(r["target_1d_maturity"] == "MATURED" for r in rows),
            "NEXT_NY17_3D": sum(r["target_3d_maturity"] == "MATURED" for r in rows),
        },
        "source_hashes": {"ny17": sha256(NY17), "gvz": sha256(GVZ)},
        "output_sha256": sha256(out),
        "ready_lanes": ["B0_GOLD_OWN_HISTORY", "B4_DIRECTION_STATES"],
        "blocked_lanes": {
            "GVZ_RISK": "BLOCKED_PIT_EXACT_RELEASE_CLOCK_NOT_PROVEN",
            "MACRO_EVENT_SUCCESSOR_V2": "BLOCKED_PANEL_DAILY_ASOF_JOIN_NOT_CANONICAL",
            "BOCPD_RETURN_SUCCESSOR_V1": "BLOCKED_DATA_DAILY_ORIGIN_STATE_NOT_FOUND",
            "MARKET_SHOCK_V3": "NOT_FOUND_CANONICAL",
        },
        "decision": "DO_NOT_SCORE_PHASE2_UNTIL_AN_INCREMENTAL_LANE_IS_PIT_PROVEN",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
    }
    meta.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--metadata", type=Path, default=META)
    args = parser.parse_args()
    print(json.dumps(write_artifacts(args.output, args.metadata), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
