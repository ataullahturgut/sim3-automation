from __future__ import annotations

import argparse
import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

import pandas as pd
import requests

import collector_r2 as base

PIPELINE_VERSION = "GOLD_DATA_R2.1_2026-08-31"
ROOT = Path(__file__).resolve().parent


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _fred_url_params(ids: list[str], mode: str, retrieved_at):
    params = {"id": ",".join(ids)}
    if mode != "backfill":
        start = (pd.Timestamp(retrieved_at).tz_convert("UTC") - pd.Timedelta(days=220)).date()
        params["cosd"] = start.isoformat()
    return "https://fred.stlouisfed.org/graph/fredgraph.csv", params


def _parse_fred_frame(run_id: str, retrieved_at, content: bytes, mode: str):
    df = pd.read_csv(io.BytesIO(content))
    date_col = next((c for c in df.columns if str(c).strip().lower() in {"date", "observation_date"}), df.columns[0])
    ph = _sha(content)
    out = []
    for sid, fred_id in base.FRED.items():
        if fred_id not in df.columns:
            continue
        for _, row in df.iterrows():
            dt = pd.to_datetime(row[date_col], errors="coerce")
            val = pd.to_numeric(row[fred_id], errors="coerce")
            if pd.notna(dt) and pd.notna(val):
                out.append(base.make_obs(
                    run_id, sid, dt, val, "FRED", fred_id, "daily", base.FRED_UNITS[sid], retrieved_at,
                    provider_as_of=dt,
                    available_as_of=retrieved_at,
                    payload_hash=ph,
                    metadata={
                        "fred_series": fred_id,
                        "availability_policy": "retrieval_time_floor",
                        "collector": "bounded_batch" if len(base.FRED) > 1 else "bounded_single",
                    },
                ))
    return out


def _fred_batch(run_id: str, retrieved_at, mode: str):
    ids = list(base.FRED.values())
    url, params = _fred_url_params(ids, mode, retrieved_at)
    r = requests.get(url, params=params, headers=base.HEADERS, timeout=(8, 25))
    r.raise_for_status()
    obs = _parse_fred_frame(run_id, retrieved_at, r.content, mode)
    found = {o.series_id for o in obs}
    missing = sorted(set(base.FRED) - found)
    if missing:
        raise ValueError(f"FRED_BATCH_MISSING:{missing}")
    return obs


def _fred_one(run_id: str, retrieved_at, mode: str, sid: str, fred_id: str):
    url, params = _fred_url_params([fred_id], mode, retrieved_at)
    r = requests.get(url, params=params, headers=base.HEADERS, timeout=(8, 20))
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    date_col = next((c for c in df.columns if str(c).strip().lower() in {"date", "observation_date"}), df.columns[0])
    if fred_id not in df.columns:
        raise ValueError(f"FRED_SCHEMA_{sid}:{list(df.columns)}")
    ph = _sha(r.content)
    out = []
    for _, row in df.iterrows():
        dt = pd.to_datetime(row[date_col], errors="coerce")
        val = pd.to_numeric(row[fred_id], errors="coerce")
        if pd.notna(dt) and pd.notna(val):
            out.append(base.make_obs(
                run_id, sid, dt, val, "FRED", fred_id, "daily", base.FRED_UNITS[sid], retrieved_at,
                provider_as_of=dt, available_as_of=retrieved_at, payload_hash=ph,
                metadata={"fred_series": fred_id, "availability_policy": "retrieval_time_floor", "collector": "bounded_fallback"},
            ))
    if not out:
        raise ValueError(f"FRED_EMPTY:{sid}")
    return out


def collect_fred_bounded(run_id: str, retrieved_at, mode: str):
    errors = []
    try:
        return _fred_batch(run_id, retrieved_at, mode), errors
    except Exception as exc:
        errors.append({"collector": "FRED_BATCH", "error": f"{type(exc).__name__}: {exc}"})

    out = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(_fred_one, run_id, retrieved_at, mode, sid, fid): sid
            for sid, fid in base.FRED.items()
        }
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                out.extend(fut.result())
            except Exception as exc:
                errors.append({"collector": f"FRED:{sid}", "error": f"{type(exc).__name__}: {exc}"})
    return out, errors


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


def collect(mode: str) -> dict:
    retrieved_at = base.utcnow()
    run_id = str(base.uuid.uuid4())
    s = base.session()
    observations = []
    vintages = []
    quality_events = []

    tail_daily = None if mode == "backfill" else (120 if mode == "daily" else 40)
    tail_gpr = None if mode == "backfill" else (36 if mode == "daily" else 24)

    if mode == "hourly":
        try:
            observations.extend(base.collect_xaus_spot(s, run_id, retrieved_at))
        except Exception as exc:
            quality_events.append(qevent(run_id, "XAU_SPOT_XAUS", "COLLECTOR_FAILURE", f"{type(exc).__name__}: {exc}"))
    else:
        for name, sid, fn in [
            ("XAUS_SPOT", "XAU_SPOT_XAUS", lambda: base.collect_xaus_spot(s, run_id, retrieved_at)),
            ("XAUS_HISTORY", "XAU_DAILY_XAUS", lambda: base.collect_xaus_history(s, run_id, retrieved_at, tail_daily)),
            ("CBOE", None, lambda: base.collect_cboe(s, run_id, retrieved_at, tail_daily)),
        ]:
            try:
                observations.extend(fn())
            except Exception as exc:
                quality_events.append(qevent(run_id, sid, "COLLECTOR_FAILURE", f"{type(exc).__name__}: {exc}", {"collector": name}))

        fred_obs, fred_errors = collect_fred_bounded(run_id, retrieved_at, mode)
        observations.extend(fred_obs)
        for e in fred_errors:
            # Batch failure is diagnostic only if all individual series recovered.
            if e["collector"] == "FRED_BATCH" and {o.series_id for o in fred_obs} >= set(base.FRED):
                continue
            series_id = e["collector"].split(":", 1)[1] if e["collector"].startswith("FRED:") else None
            quality_events.append(qevent(run_id, series_id, "COLLECTOR_FAILURE", e["error"], {"collector": e["collector"]}))

        try:
            gpr_obs, vintage = base.collect_gpr(s, run_id, retrieved_at, tail_gpr)
            observations.extend(gpr_obs)
            vintages.append(vintage)
        except Exception as exc:
            quality_events.append(qevent(run_id, "GPR_OFFICIAL", "COLLECTOR_FAILURE", f"{type(exc).__name__}: {exc}", {"collector": "GPR"}))

    return {
        "run_id": run_id,
        "started_at": base.iso_utc(retrieved_at),
        "finished_at": base.iso_utc(base.utcnow()),
        "pipeline_version": PIPELINE_VERSION,
        "mode": mode,
        "observations": [asdict(o) for o in observations],
        "vintages": vintages,
        "quality_events": quality_events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "hourly", "daily", "backfill"], default="smoke")
    parser.add_argument("--outdir", default=str(ROOT / "_out_r2_bounded"))
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    bundle = collect(args.mode)
    base.write_bundle(bundle, Path(args.outdir))
    print(json.dumps({
        "run_id": bundle["run_id"],
        "pipeline_version": bundle["pipeline_version"],
        "mode": args.mode,
        "n_observations": len(bundle["observations"]),
        "series": sorted({x["series_id"] for x in bundle["observations"]}),
        "quality_events": bundle["quality_events"],
    }, indent=2))

    if args.persist:
        from persist_neon import persist_bundle
        result = persist_bundle(bundle)
        print(json.dumps(result, indent=2))

    return 1 if any(x.get("severity") == "ERROR" for x in bundle["quality_events"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
