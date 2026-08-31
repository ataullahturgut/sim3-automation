from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import requests

import collector_r2 as base
from fed_direct import collect_fed_direct
from fred_indices_api import collect_fred_indices
from persist_neon import persist_bundle

ROOT = Path(__file__).resolve().parent
PIPELINE_VERSION = "GOLD_DATA_R2.6_2026-08-31"


def bounded_get(session: requests.Session, url: str, **kwargs):
    kwargs.pop("timeout", None)
    r = session.get(url, timeout=(8, 25), **kwargs)
    r.raise_for_status()
    return r


def qevent(run_id: str, series_id, code: str, message: str, metadata=None):
    return {
        "run_id": run_id,
        "series_id": series_id,
        "event_ts": base.iso_utc(base.utcnow()),
        "severity": "ERROR",
        "code": code,
        "message": message,
        "metadata": metadata or {},
    }


def collect_xau_history_points(session: requests.Session, run_id: str, retrieved_at, tail: int | None):
    r = bounded_get(session, base.XAUS_HISTORY_URL, params={"range": "1y"})
    payload = r.json()
    points = payload.get("points") or []
    if not points:
        raise ValueError("XAUS_HISTORY_NO_POINTS")

    df = pd.DataFrame(points)
    rename = {"d": "date", "c": "close", "h": "high", "l": "low", "o": "open"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError(f"XAUS_HISTORY_SCHEMA:{list(df.columns)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["date", "close"]).sort_values("date").drop_duplicates("date", keep="last")
    if tail:
        df = df.tail(tail)
    if df.empty:
        raise ValueError("XAUS_HISTORY_EMPTY_AFTER_PARSE")

    state = payload.get("data_state") or {}
    source = payload.get("price_source") or state.get("source") or "XAUS history"
    ph = base.sha256_bytes(r.content)
    out = []
    for _, row in df.iterrows():
        dt = row["date"]
        out.append(base.make_obs(
            run_id, "XAU_DAILY_XAUS", dt, row["close"], source, "XAUUSD", "daily", "USD/oz", retrieved_at,
            provider_as_of=dt,
            available_as_of=retrieved_at,
            status="CANDIDATE_NOT_BENCHMARK",
            payload_hash=ph,
            metadata={
                "endpoint": base.XAUS_HISTORY_URL,
                "provider_status": state.get("status"),
                "history_contract": "points[d,c]",
                "availability_policy": "first_retrieval_floor",
                "historical_publication_timestamp_reconstruction": "NOT_PROVEN",
            },
        ))
    return out


def collect_source(source: str, mode: str) -> dict:
    retrieved_at = base.utcnow()
    run_id = str(base.uuid.uuid4())
    observations = []
    vintages = []
    quality_events = []

    base.get = bounded_get
    session = requests.Session()
    session.headers.update(base.HEADERS)

    try:
        if source == "xau":
            observations.extend(base.collect_xaus_spot(session, run_id, retrieved_at))
            if mode != "hourly":
                tail = None if mode == "backfill" else 120
                observations.extend(collect_xau_history_points(session, run_id, retrieved_at, tail))

        elif source == "cboe":
            tail = None if mode == "backfill" else 120
            observations.extend(base.collect_cboe(session, run_id, retrieved_at, tail))
            found = {o.series_id for o in observations}
            required = {"GVZ_CBOE", "VIX_CBOE"}
            if not required.issubset(found):
                raise ValueError(f"CBOE_REQUIRED_SERIES_MISSING:{sorted(required-found)}")

        elif source == "fed":
            observations.extend(collect_fed_direct(run_id, retrieved_at, mode))

        elif source == "fred_indices":
            observations.extend(collect_fred_indices(run_id, retrieved_at, mode))

        elif source == "gpr":
            tail = None if mode == "backfill" else 36
            gpr_obs, vintage = base.collect_gpr(session, run_id, retrieved_at, tail)
            observations.extend(gpr_obs)
            vintages.append(vintage)
            found = {o.series_id for o in observations}
            required = {"GPR_OFFICIAL", "GPRT_OFFICIAL", "GPRA_OFFICIAL"}
            if not required.issubset(found):
                raise ValueError(f"GPR_REQUIRED_SERIES_MISSING:{sorted(required-found)}")

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
    p.add_argument("--source", choices=["xau", "cboe", "fed", "fred_indices", "gpr"], required=True)
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
