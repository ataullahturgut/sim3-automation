from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
R2_PATH = HERE / "audit_component_verification_v145_r2.py"
spec = importlib.util.spec_from_file_location("component_verifier_v145_r2_base", R2_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("COMPONENT_VERIFIER_R2_IMPORT_FAILED")
r2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r2)
base = r2.base

ROLE_EVIDENCE = base.AUDITS / "component_role_replays_v145/component_role_replays_v145.json"
EXPECTED_ROLE_EVIDENCE_SHA256 = "910ad77c326c0ce96076db79d0dc9001b3d4aa13bd740eb41259b64c627e8f73"


def role_evidence() -> dict[str, Any]:
    raw = ROLE_EVIDENCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_ROLE_EVIDENCE_SHA256:
        raise RuntimeError("ROLE_REPLAY_EVIDENCE_FINGERPRINT_MISMATCH")
    value = json.loads(raw)
    if value.get("performance_fields_consumed") is not False or value.get("production_writes") != "NONE":
        raise RuntimeError("ROLE_REPLAY_GOVERNANCE_FAIL")
    if value.get("prospective_claim") is not False or value.get("auto_selector") != "OFF" or value.get("auto_ensemble") != "OFF":
        raise RuntimeError("ROLE_REPLAY_AUTHORITY_FAIL")
    return value


def promote_h1(row: dict[str, Any], engine: str, evidence: dict[str, Any]) -> dict[str, Any]:
    item = evidence["h1_2026_08"][engine]
    ok = (item.get("target_month") == "2026-08" and item.get("origin_month") == "2026-07"
          and item.get("determinism") == "PASS" and item.get("future_information_violations") == 0
          and item.get("performance_consumed") is False and item.get("prospective_claim") is False)
    row["dimensions"]["C4_HISTORICAL_COVERAGE"] = base.dim("PASS" if ok else "FAIL", "existing replay plus governed 2026-08 extension")
    row["dimensions"]["C5_ORIGIN_PIT"] = base.dim("PASS" if ok else "FAIL", {"origin_month": item.get("origin_month")})
    row["dimensions"]["C6_FUTURE_INFORMATION"] = base.dim("PASS" if ok else "FAIL", item.get("future_information_violations"))
    row["dimensions"]["C7_RECONSTRUCTION_VINTAGE"] = base.dim("PASS" if ok else "FAIL", {"prospective_claim": item.get("prospective_claim")})
    row["dimensions"]["C8_DETERMINISM_REPRODUCIBILITY"] = base.dim("PASS" if ok else "FAIL", item.get("determinism"))
    row["dimensions"]["C9_PILOT_CELL_EXECUTION"] = base.dim("PASS" if ok else "FAIL", item)
    row["component_verification_status"] = base.final_status(row["dimensions"])
    row["evidence_reference"] = str(ROLE_EVIDENCE.relative_to(base.ROOT))
    return row


def promote_r4(row: dict[str, Any], engine: str, evidence: dict[str, Any]) -> dict[str, Any]:
    item = evidence["ny17_context"][engine]
    ok = item.get("status") == "PASS" and item.get("pilot_cells_executed") == 20 and item.get("determinism") == "PASS" and item.get("future_information_violations") == 0
    row["dimensions"]["C8_DETERMINISM_REPRODUCIBILITY"] = base.dim("PASS" if ok else "FAIL", item.get("output_sha256"))
    row["dimensions"]["C9_PILOT_CELL_EXECUTION"] = base.dim("PASS" if ok else "FAIL", item)
    row["component_verification_status"] = base.final_status(row["dimensions"])
    row["evidence_reference"] = str(ROLE_EVIDENCE.relative_to(base.ROOT))
    return row


def verify_bocpd_final(snap: dict[str, Any], tests_pass: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    row = base.verify_bocpd(snap, tests_pass)
    item = evidence["bocpd_2026_08"]
    governed = (item.get("status") == "BLOCKED_DATA" and item.get("blocker_code") == "CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND"
                and item.get("output_computed") is False and item.get("model_or_threshold_change") == "NONE")
    row["dimensions"]["C4_HISTORICAL_COVERAGE"] = base.dim("BLOCKED" if governed else "FAIL", item)
    row["dimensions"]["C9_PILOT_CELL_EXECUTION"] = base.dim("BLOCKED" if governed else "FAIL", {
        "extension_contract": "gold_axis_2026/bocpd_successor_v1/evaluation_extension_2026_08_v145.json",
        "blocker": item,
    })
    row["component_verification_status"] = base.final_status(row["dimensions"])
    row["evidence_reference"] = "gold_axis_2026/GOLD_CONTROL_BOCPD_2026_08_EVALUATION_EXTENSION_V145_2026-09-09.md"
    return row


def verify_gvz_final(snap: dict[str, Any], tests_pass: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    row = base.verify_gvz(snap, tests_pass)
    item = evidence["gvz"]
    ok = item.get("status") == "PASS" and item.get("pilot_cells_executed") == 20 and item.get("determinism") == "PASS" and item.get("future_information_violations") == 0
    row["dimensions"]["C8_DETERMINISM_REPRODUCIBILITY"] = base.dim("PASS" if ok else "FAIL", item.get("output_sha256"))
    row["dimensions"]["C9_PILOT_CELL_EXECUTION"] = base.dim("PASS" if ok else "FAIL", item)
    row["component_verification_status"] = base.final_status(row["dimensions"])
    row["evidence_reference"] = str(ROLE_EVIDENCE.relative_to(base.ROOT))
    return row


def build(snap: dict[str, Any], r4_tests_pass: bool, bocpd_tests_pass: bool, vw_result: Path | None) -> dict[str, Any]:
    if sorted(r["engine_id"] for r in snap["runtime"]) != sorted(base.ENGINE_ORDER):
        raise RuntimeError("RUNTIME_ENGINE_INVENTORY_DRIFT")
    evidence = role_evidence()
    rows = [
        promote_h1(base.verify_patch(snap), "CAUSAL_PATCH", evidence),
        promote_h1(base.verify_vw(snap, vw_result), "VW_MIDAS_MSVR_SUCCESSOR_V1", evidence),
        promote_h1(base.verify_simple("MOMENTUM_3M", snap), "MOMENTUM_3M", evidence),
        promote_h1(base.verify_simple("RANDOM_WALK", snap), "RANDOM_WALK", evidence),
        promote_r4(r2.verify_r4("MONTHLY_DIRECTION_3M", snap, r4_tests_pass), "MONTHLY_DIRECTION_3M", evidence),
        promote_r4(r2.verify_r4("FAST", snap, r4_tests_pass), "FAST", evidence),
        promote_r4(r2.verify_r4("SLOW", snap, r4_tests_pass), "SLOW", evidence),
        base.verify_macro(snap),
        verify_bocpd_final(snap, bocpd_tests_pass, evidence),
        promote_r4(r2.verify_r4("EMERGENCY_LEVEL", snap, r4_tests_pass), "EMERGENCY_LEVEL", evidence),
        promote_r4(r2.verify_r4("EMERGENCY_REVERSAL", snap, r4_tests_pass), "EMERGENCY_REVERSAL", evidence),
        verify_gvz_final(snap, r4_tests_pass, evidence),
    ]
    order = {row["engine_id"]: row for row in rows}
    rows = [order[engine] for engine in base.ENGINE_ORDER]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["component_verification_status"]] = counts.get(row["component_verification_status"], 0) + 1
    return {
        "audit_id": "GOLD_CONTROL_COMPONENT_VERIFICATION_V145_R3_FINAL",
        "mode": "FINAL_POST_GAP_COMPONENT_VERIFICATION",
        "protocol": str(base.PROTOCOL.relative_to(base.ROOT)),
        "production_database_access": "READ_ONLY", "production_writes": "NONE",
        "performance_fields_consumed": False, "model_or_threshold_change": "NONE",
        "engine_count": 12, "status_counts": counts, "authority_counts": snap["authority_counts"],
        "auto_selector": "OFF", "auto_ensemble": "OFF", "snapshot_at": str(snap["snapshot_at"]),
        "tx_snapshot": snap["tx_snapshot"], "rows": rows,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["engine_id", "component_verification_status", *base.DIMS, "evidence_reference"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader()
        for item in rows:
            row = {"engine_id": item["engine_id"], "component_verification_status": item["component_verification_status"], "evidence_reference": item["evidence_reference"]}
            for name in base.DIMS:
                row[name] = item["dimensions"][name]["status"]
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", required=True); parser.add_argument("--output-csv", required=True)
    parser.add_argument("--vw-result", required=True); parser.add_argument("--r4-tests-pass", action="store_true")
    parser.add_argument("--bocpd-tests-pass", action="store_true")
    args = parser.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not dsn:
        raise SystemExit("BLOCKED:NEON_DATABASE_URL_NOT_SET")
    snap = base.read_snapshot(dsn)
    out = build(snap, args.r4_tests_pass, args.bocpd_tests_pass, Path(args.vw_result))
    Path(args.output_json).write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    write_csv(Path(args.output_csv), out["rows"])
    print(json.dumps({k: out[k] for k in ("audit_id", "status_counts", "authority_counts", "production_writes", "performance_fields_consumed")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
