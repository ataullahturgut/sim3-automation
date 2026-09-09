from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

NY17_ENGINES = {
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def apply_overlay(rows: list[dict[str, str]], bundle: dict) -> tuple[list[dict[str, str]], dict[str, int]]:
    if bundle.get("bundle_id") != "GOLD_CONTROL_HISTORICAL_RECONSTRUCTION_BUNDLE_V145":
        raise ValueError("BUNDLE_ID_MISMATCH")
    if bundle.get("status") != "PASS" or bundle.get("production_database_write") != "NONE":
        raise ValueError("BUNDLE_NOT_ACCEPTABLE")
    if bundle.get("prospective_claim") is not False:
        raise ValueError("BUNDLE_PROSPECTIVE_CLAIM_INVALID")

    out: list[dict[str, str]] = []
    for raw in rows:
        row = dict(raw)
        eid = row["engine_id"]
        month = row["target_month"]
        old = row["readiness_status"]
        changed = False

        if eid in NY17_ENGINES:
            if old != "PARTIAL":
                raise ValueError(f"UNEXPECTED_NY17_BASELINE_STATE:{eid}:{month}:{old}")
            row["source_coverage"] = "V145_IMMUTABLE_NY17_HISTORICAL_RECONSTRUCTION_ARTIFACT_COMPLETE"
            row["lineage_status"] = "IMMUTABLE_GITHUB_ARTIFACT_LANE_WITH_TRUTHFUL_PROVIDER_RETRIEVAL"
            row["evidence_class"] = "HISTORICAL_REPLAY"
            row["readiness_status"] = "READY_TO_REPLAY"
            row["blocker_code"] = "NONE_DATA_GAP_RESOLVED_REPLAY_PENDING"
            row["evidence_reference"] = "gold_axis_2026/data_pipeline/audits/historical_reconstruction_bundle_v145/historical_reconstruction_bundle_v145.json"
            changed = True

        elif eid == "GVZ_RISK" and month <= "2026-03":
            if old not in {"BLOCKED_DATA", "PARTIAL"}:
                raise ValueError(f"UNEXPECTED_GVZ_BASELINE_STATE:{month}:{old}")
            row["source_coverage"] = "V145_OFFICIAL_CBOE_IMMUTABLE_HISTORICAL_RECONSTRUCTION_ARTIFACT_COMPLETE"
            row["lineage_status"] = "OFFICIAL_CBOE_PAYLOAD_HASH_AND_IMMUTABLE_ROW_ARTIFACT"
            row["evidence_class"] = "HISTORICAL_REPLAY"
            row["readiness_status"] = "READY_TO_REPLAY"
            row["blocker_code"] = "NONE_DATA_GAP_RESOLVED_REPLAY_PENDING"
            row["evidence_reference"] = "gold_axis_2026/data_pipeline/audits/historical_gvz_reconstruction_lane_v145_evidence.json"
            changed = True

        if changed:
            row["reproducibility_status"] = "READY_FOR_FROZEN_ROLE_REPLAY"
        out.append(row)

    if len(out) != 240:
        raise ValueError(f"MATRIX_CARDINALITY_MISMATCH:{len(out)}")
    counts = dict(sorted(Counter(r["readiness_status"] for r in out).items()))
    return out, counts


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    audits = root / "gold_axis_2026/data_pipeline/audits"
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default=str(audits / "historical_pilot_readiness_v145.csv"))
    parser.add_argument("--bundle", default=str(audits / "historical_reconstruction_bundle_v145/historical_reconstruction_bundle_v145.json"))
    parser.add_argument("--out-csv", default=str(audits / "historical_pilot_readiness_v145_post_gap.csv"))
    parser.add_argument("--out-json", default=str(audits / "historical_pilot_readiness_v145_post_gap.json"))
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    bundle_path = Path(args.bundle)
    rows = load_csv(baseline_path)
    fields = list(rows[0]) if rows else []
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    updated, counts = apply_overlay(rows, bundle)
    write_csv(Path(args.out_csv), updated, fields)
    summary = {
        "audit_id": "GOLD_CONTROL_HISTORICAL_PILOT_READINESS_V145_POST_GAP",
        "status": "PASS_DATA_GAPS_RESOLVED_REPLAY_PENDING",
        "baseline_sha256": sha256_file(baseline_path),
        "bundle_sha256": sha256_file(bundle_path),
        "matrix_rows": len(updated),
        "status_counts": counts,
        "production_database_write": "NONE",
        "performance_scoring": False,
        "prospective_claim": False,
        "note": "READY_TO_REPLAY is not READY_PROVEN; frozen role-specific replay remains required.",
    }
    Path(args.out_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
