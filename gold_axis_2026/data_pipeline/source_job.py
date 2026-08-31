from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import requests

import collector_r2 as base
from collector_r2_bounded import collect_fred_bounded, qevent
from persist_neon import persist_bundle

ROOT = Path(__file__).resolve().parent
PIPELINE_VERSION = "GOLD_DATA_R2.2_2026-08-31"


def bounded_get(session: requests.Session, url: str, **kwargs):
    # Source isolation: one HTTP endpoint cannot hold the entire data plane open.
    kwargs.pop("timeout", None)
    r = session.get(url, timeout=(8, 25), **kwargs)
    r.raise_for_status()
    return r


def collect_source(source: str, mode: str) -> dict:
    retrieved_at = base.utcnow()
    run_id = str(base.uuid.uuid4())
    observations = []
    vintages = []
    quality_events = []

    # Replace the legacy long-retry helper only inside this isolated process.
    base.get = bounded_get
    session = requests.Session()
    session.headers.update(base.HEADERS)

    try:
        if source == "xau":
            observations.extend(base.collect_xaus_spot(session, run_id, retrieved_at))
            if mode != "hourly":
                tail = None if mode == "backfill" else 120
                observations.extend(base.collect_xaus_history(session, run_id, retrieved_at, tail))

        elif source == "cboe":
            tail = None if mode == "backfill" else 120
            observations.extend(base.collect_cboe(session, run_id, retrieved_at, tail))

        elif source == "fred":
            fred_obs, fred_errors = collect_fred_bounded(run_id, retrieved_at, mode)
            observations.extend(fred_obs)
            recovered = {o.series_id for o in fred_obs}
            for e in fred_errors:
                if e["collector"] == "FRED_BATCH" and recovered >= set(base.FRED):
                    continue
                series_id = e["collector"].split(":", 1)[1] if e["collector"].startswith("FRED:") else None
                quality_events.append(qevent(
                    run_id, series_id, "COLLECTOR_FAILURE", e["error"], {"collector": e["collector"]}
                ))

        elif source == "gpr":
            tail = None if mode == "backfill" else 36
            gpr_obs, vintage = base.collect_gpr(session, run_id, retrieved_at, tail)
            observations.extend(gpr_obs)
            vintages.append(vintage)

        else:
            raise ValueError(f"UNKNOWN_SOURCE:{source}")

    except Exception as exc:
        quality_events.append(qevent(
            run_id, None, "COLLECTOR_FAILURE", f"{type(exc).__name__}: {exc}", {"source_job": source}
        ))

    return {
        "run_id": run_id,
        "started_at": base.iso_utc(retrieved_at),
        "finished_at": base.iso_utc(base.utcnow()),
        "pipeline_version": PIPELINE_VERSION,
        "mode": f"{mode}:{source}",
        "observations": [asdict(o) for o in observations],
        "vintages": vintages,
        "quality_events": quality_events,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=["xau", "cboe", "fred", "gpr"], required=True)
    p.add_argument("--mode", choices=["hourly", "daily", "backfill"], default="daily")
    p.add_argument("--persist", action="store_true")
    args = p.parse_args()

    bundle = collect_source(args.source, args.mode)
    print(json.dumps({
        "source": args.source,
        "mode": args.mode,
        "run_id": bundle["run_id"],
        "n_observations": len(bundle["observations"]),
        "series": sorted({x["series_id"] for x in bundle["observations"]}),
        "quality_events": bundle["quality_events"],
    }, indent=2))

    if args.persist:
        result = persist_bundle(bundle)
        print(json.dumps(result, indent=2))

    return 1 if any(x.get("severity") == "ERROR" for x in bundle["quality_events"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
