from __future__ import annotations

import argparse
import copy
import json
import uuid

import collector_r2 as base
from persist_neon import persist_bundle
from source_job import collect_source


def clone_for_dedupe(bundle: dict) -> dict:
    clone = copy.deepcopy(bundle)
    new_run_id = str(uuid.uuid4())
    now = base.iso_utc(base.utcnow())
    clone["run_id"] = new_run_id
    clone["started_at"] = now
    clone["finished_at"] = now
    clone["mode"] = f"{bundle.get('mode')}:dedupe_replay"
    for obs in clone.get("observations", []):
        obs["run_id"] = new_run_id
    for q in clone.get("quality_events", []):
        q["run_id"] = new_run_id
    return clone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily", "backfill"], default="daily")
    args = parser.parse_args()

    bundle = collect_source("twelve_market", args.mode)
    errors = [q for q in bundle.get("quality_events", []) if q.get("severity") == "ERROR"]
    if errors:
        print(json.dumps({
            "status": "COLLECTION_FAIL",
            "n_observations": len(bundle.get("observations", [])),
            "quality_events": errors,
        }, indent=2))
        return 1

    first = persist_bundle(bundle)
    replay = clone_for_dedupe(bundle)
    second = persist_bundle(replay)

    report = {
        "status": "PASS" if second.get("observations_written") == 0 else "FAIL",
        "n_observations": len(bundle.get("observations", [])),
        "series": sorted({x["series_id"] for x in bundle.get("observations", [])}),
        "first_persist": first,
        "dedupe_replay": second,
        "api_collection_count": 1,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
