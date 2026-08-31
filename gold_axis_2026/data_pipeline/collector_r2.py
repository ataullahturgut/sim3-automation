from __future__ import annotations

import argparse
import hashlib
import io
import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PIPELINE_VERSION = "GOLD_DATA_R2_2026-08-31"
ROOT = Path(__file__).resolve().parent
CONTRACTS_PATH = ROOT / "source_contracts.json"
HEADERS = {"User-Agent": "Gold-Control-Data-R2/1.0", "Accept": "*/*"}

CBOE = {
    "GVZ_CBOE": "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv",
    "VIX_CBOE": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
}
FRED = {
    "DGS10_FRED": "DGS10",
    "DFF_FRED": "DFF",
    "DEXCHUS_FRED": "DEXCHUS",
    "DTWEXBGS_FRED": "DTWEXBGS",
    "SP500_FRED": "SP500",
    "DJIA_FRED": "DJIA",
    "NASDAQ100_FRED": "NASDAQ100",
}
FRED_UNITS = {
    "DGS10_FRED": "percent",
    "DFF_FRED": "percent",
    "DEXCHUS_FRED": "CNY_per_USD",
    "DTWEXBGS_FRED": "index",
    "SP500_FRED": "index",
    "DJIA_FRED": "index",
    "NASDAQ100_FRED": "index",
}
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
XAUS_SPOT_URL = "https://xaus.com/api/v1/spot"
XAUS_HISTORY_URL = "https://xaus.com/api/v1/history"


@dataclass
class Observation:
    run_id: str
    series_id: str
    observation_ts: str
    value: float
    source: str
    source_symbol: str | None
    provider_as_of: str | None
    available_as_of: str | None
    first_seen_at: str
    retrieved_at: str
    frequency: str
    unit: str | None
    transform: str
    quality_status: str
    lineage_id: str
    payload_hash: str | None
    metadata: dict


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lineage_id(series_id: str, source: str, symbol: str | None) -> str:
    raw = f"{series_id}|{source}|{symbol or ''}".encode()
    return hashlib.sha256(raw).hexdigest()[:20]


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.5,
        status_forcelist=(408, 425, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8))
    s.headers.update(HEADERS)
    return s


def get(s: requests.Session, url: str, **kwargs) -> requests.Response:
    r = s.get(url, timeout=(10, 60), **kwargs)
    r.raise_for_status()
    return r


def make_obs(
    run_id: str,
    series_id: str,
    dt,
    value,
    source: str,
    symbol: str | None,
    frequency: str,
    unit: str | None,
    retrieved_at: datetime,
    *,
    provider_as_of=None,
    available_as_of=None,
    status="OK",
    payload_hash=None,
    metadata=None,
) -> Observation:
    observation_ts = iso_utc(dt)
    retrieved_iso = iso_utc(retrieved_at)
    provider_iso = iso_utc(provider_as_of) if provider_as_of is not None else None
    available_iso = iso_utc(available_as_of) if available_as_of is not None else provider_iso or observation_ts
    return Observation(
        run_id=run_id,
        series_id=series_id,
        observation_ts=observation_ts,
        value=float(value),
        source=source,
        source_symbol=symbol,
        provider_as_of=provider_iso,
        available_as_of=available_iso,
        first_seen_at=retrieved_iso,
        retrieved_at=retrieved_iso,
        frequency=frequency,
        unit=unit,
        transform="LEVEL",
        quality_status=status,
        lineage_id=lineage_id(series_id, source, symbol),
        payload_hash=payload_hash,
        metadata=metadata or {},
    )


def collect_cboe(s: requests.Session, run_id: str, retrieved_at: datetime, tail: int | None) -> list[Observation]:
    out: list[Observation] = []
    for sid, url in CBOE.items():
        r = get(s, url)
        ph = sha256_bytes(r.content)
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = [str(c).strip().upper() for c in df.columns]
        value_col = sid.split("_")[0] if sid.split("_")[0] in df.columns else "CLOSE"
        if "DATE" not in df.columns or value_col not in df.columns:
            raise ValueError(f"CBOE_SCHEMA_{sid}:{list(df.columns)}")
        if tail:
            df = df.tail(tail)
        for _, row in df.iterrows():
            dt = pd.to_datetime(row["DATE"], errors="coerce")
            val = pd.to_numeric(row[value_col], errors="coerce")
            if pd.notna(dt) and pd.notna(val):
                out.append(make_obs(
                    run_id, sid, dt, val, "Cboe", sid.split("_")[0], "daily_close", "index", retrieved_at,
                    provider_as_of=dt, available_as_of=dt, payload_hash=ph,
                    metadata={"endpoint": url, "authority": "Cboe"},
                ))
    return out


def collect_fred_one(s: requests.Session, run_id: str, sid: str, fred_id: str,
                     retrieved_at: datetime, tail: int | None) -> list[Observation]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}"
    r = get(s, url)
    ph = sha256_bytes(r.content)
    df = pd.read_csv(io.StringIO(r.text))
    date_col = next((c for c in df.columns if str(c).strip().lower() in {"date", "observation_date"}), df.columns[0])
    if fred_id not in df.columns:
        raise ValueError(f"FRED_SCHEMA_{sid}:{list(df.columns)}")
    if tail:
        df = df.tail(tail)
    out: list[Observation] = []
    for _, row in df.iterrows():
        dt = pd.to_datetime(row[date_col], errors="coerce")
        val = pd.to_numeric(row[fred_id], errors="coerce")
        if pd.notna(dt) and pd.notna(val):
            out.append(make_obs(
                run_id, sid, dt, val, "FRED", fred_id, "daily", FRED_UNITS[sid], retrieved_at,
                provider_as_of=dt,
                # Conservative point-in-time policy: a value is never considered available before we retrieved it.
                available_as_of=retrieved_at,
                payload_hash=ph,
                metadata={"endpoint": url, "fred_series": fred_id, "availability_policy": "retrieval_time_floor"},
            ))
    return out


def collect_gpr(s: requests.Session, run_id: str, retrieved_at: datetime, tail: int | None):
    r = get(s, GPR_URL)
    ph = sha256_bytes(r.content)
    sheets = pd.read_excel(io.BytesIO(r.content), sheet_name=None, engine="xlrd")
    best = None
    best_sheet = None
    for sheet, df in sheets.items():
        cols = {str(c).strip().upper(): c for c in df.columns}
        if {"GPR", "GPRT", "GPRA"}.issubset(cols):
            date_col = cols.get("MONTH") or cols.get("DATE") or df.columns[0]
            q = df[[date_col, cols["GPR"], cols["GPRT"], cols["GPRA"]]].copy()
            q.columns = ["date", "GPR", "GPRT", "GPRA"]
            q["date"] = pd.to_datetime(q["date"], errors="coerce")
            q = q.dropna(subset=["date"])
            if best is None or len(q) > len(best):
                best, best_sheet = q, sheet
    if best is None:
        raise ValueError("GPR_SCHEMA_NOT_FOUND")
    if tail:
        best = best.tail(tail)
    out: list[Observation] = []
    mapping = {"GPR": "GPR_OFFICIAL", "GPRT": "GPRT_OFFICIAL", "GPRA": "GPRA_OFFICIAL"}
    for _, row in best.iterrows():
        for col, sid in mapping.items():
            val = pd.to_numeric(row[col], errors="coerce")
            if pd.notna(val):
                out.append(make_obs(
                    run_id, sid, row["date"], val, "Caldara-Iacoviello official workbook", col,
                    "monthly_vintage", "index", retrieved_at,
                    provider_as_of=None,
                    available_as_of=retrieved_at,
                    status="AUTHORITATIVE_REVISION_PRONE",
                    payload_hash=ph,
                    metadata={"endpoint": GPR_URL, "sheet": best_sheet, "vintage_hash": ph},
                ))
    vintage = {
        "source_id": "GPR_OFFICIAL_WORKBOOK",
        "retrieved_at": iso_utc(retrieved_at),
        "provider_as_of": None,
        "content_sha256": ph,
        "content_type": r.headers.get("content-type"),
        "byte_count": len(r.content),
        "metadata": {"endpoint": GPR_URL, "sheet": best_sheet},
    }
    return out, vintage


def collect_xaus_spot(s: requests.Session, run_id: str, retrieved_at: datetime) -> list[Observation]:
    r = get(s, XAUS_SPOT_URL, params={"compact": 1, "fresh": int(time.time())})
    ph = sha256_bytes(r.content)
    p = r.json()
    state = p.get("data_state") or {}
    price = p.get("spot_usd_oz") or (p.get("xau") or {}).get("price")
    if price is None:
        raise ValueError("XAUS_PRICE_MISSING")
    as_of = p.get("price_as_of") or p.get("updated_at") or state.get("as_of") or retrieved_at
    provider = p.get("price_source") or state.get("source") or "XAUS public API"
    provider_stale = str(state.get("status", "")).lower() == "stale" or bool(p.get("stale", False))
    return [make_obs(
        run_id, "XAU_SPOT_XAUS", as_of, price, provider, "XAU", "live", "USD/oz", retrieved_at,
        provider_as_of=as_of, available_as_of=retrieved_at,
        status="STALE" if provider_stale else "APPROVED_INDICATIVE_NOT_SETTLEMENT",
        payload_hash=ph,
        metadata={"endpoint": XAUS_SPOT_URL, "provider_status": state.get("status")},
    )]


def _history_rows(payload):
    if isinstance(payload, list):
        return payload
    for key in ("data", "history", "prices", "rows"):
        if isinstance(payload.get(key), list):
            return payload[key]
    return []


def collect_xaus_history(s: requests.Session, run_id: str, retrieved_at: datetime,
                         tail: int | None) -> list[Observation]:
    r = get(s, XAUS_HISTORY_URL, params={"range": "1y"})
    ph = sha256_bytes(r.content)
    rows = _history_rows(r.json())
    parsed = []
    for z in rows:
        dt = z.get("d") or z.get("date") or z.get("timestamp") or z.get("time")
        close = z.get("c") if z.get("c") is not None else z.get("close")
        if dt is None or close is None:
            continue
        t = pd.to_datetime(dt, errors="coerce", utc=True)
        v = pd.to_numeric(close, errors="coerce")
        if pd.notna(t) and pd.notna(v):
            parsed.append((t, float(v), z))
    parsed.sort(key=lambda x: x[0])
    if tail:
        parsed = parsed[-tail:]
    out = []
    for dt, val, z in parsed:
        out.append(make_obs(
            run_id, "XAU_DAILY_XAUS", dt, val, "XAUS history", "XAUUSD", "daily", "USD/oz", retrieved_at,
            provider_as_of=dt, available_as_of=retrieved_at,
            status="CANDIDATE_NOT_BENCHMARK", payload_hash=ph,
            metadata={"endpoint": XAUS_HISTORY_URL, "raw_keys": sorted(z.keys())},
        ))
    return out


def collect(mode: str) -> dict:
    retrieved_at = utcnow()
    run_id = str(uuid.uuid4())
    s = session()
    observations: list[Observation] = []
    vintages: list[dict] = []
    quality_events: list[dict] = []

    tail_daily = None if mode == "backfill" else (120 if mode == "daily" else 40)
    tail_gpr = None if mode == "backfill" else (36 if mode == "daily" else 24)

    collectors: list[tuple[str, Callable[[], list[Observation]]]] = []
    if mode == "hourly":
        collectors = [("XAUS_SPOT", lambda: collect_xaus_spot(s, run_id, retrieved_at))]
    else:
        collectors = [
            ("XAUS_SPOT", lambda: collect_xaus_spot(s, run_id, retrieved_at)),
            ("XAUS_HISTORY", lambda: collect_xaus_history(s, run_id, retrieved_at, tail_daily)),
            ("CBOE", lambda: collect_cboe(s, run_id, retrieved_at, tail_daily)),
        ]
        for sid, fred_id in FRED.items():
            collectors.append((f"FRED:{sid}", lambda sid=sid, fid=fred_id: collect_fred_one(
                s, run_id, sid, fid, retrieved_at, tail_daily
            )))

    for name, fn in collectors:
        try:
            observations.extend(fn())
        except Exception as exc:
            quality_events.append({
                "run_id": run_id,
                "series_id": name.split(":", 1)[1] if name.startswith("FRED:") else None,
                "event_ts": iso_utc(utcnow()),
                "severity": "ERROR",
                "code": "COLLECTOR_FAILURE",
                "message": f"{type(exc).__name__}: {exc}",
                "metadata": {"collector": name},
            })

    if mode != "hourly":
        try:
            gpr_obs, vintage = collect_gpr(s, run_id, retrieved_at, tail_gpr)
            observations.extend(gpr_obs)
            vintages.append(vintage)
        except Exception as exc:
            quality_events.append({
                "run_id": run_id,
                "series_id": "GPR_OFFICIAL",
                "event_ts": iso_utc(utcnow()),
                "severity": "ERROR",
                "code": "COLLECTOR_FAILURE",
                "message": f"{type(exc).__name__}: {exc}",
                "metadata": {"collector": "GPR"},
            })

    # Duplicate and non-finite checks happen before persistence.
    df = pd.DataFrame([asdict(o) for o in observations])
    if not df.empty:
        dup = df.duplicated(["series_id", "observation_ts", "lineage_id"], keep=False)
        if dup.any():
            quality_events.append({
                "run_id": run_id, "series_id": None, "event_ts": iso_utc(utcnow()),
                "severity": "WARN", "code": "DUPLICATE_IN_BUNDLE",
                "message": f"{int(dup.sum())} duplicate candidate rows",
                "metadata": {},
            })

    return {
        "run_id": run_id,
        "started_at": iso_utc(retrieved_at),
        "finished_at": iso_utc(utcnow()),
        "pipeline_version": PIPELINE_VERSION,
        "mode": mode,
        "observations": [asdict(o) for o in observations],
        "vintages": vintages,
        "quality_events": quality_events,
    }


def write_bundle(bundle: dict, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(bundle["observations"]).to_csv(outdir / "observations.csv", index=False)
    (outdir / "vintages.json").write_text(json.dumps(bundle["vintages"], indent=2), encoding="utf-8")
    (outdir / "quality_events.json").write_text(json.dumps(bundle["quality_events"], indent=2), encoding="utf-8")
    manifest = {k: v for k, v in bundle.items() if k not in {"observations", "vintages", "quality_events"}}
    manifest["n_observations"] = len(bundle["observations"])
    manifest["n_errors"] = sum(x.get("severity") == "ERROR" for x in bundle["quality_events"])
    manifest["series"] = sorted({x["series_id"] for x in bundle["observations"]})
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "hourly", "daily", "backfill"], default="smoke")
    parser.add_argument("--outdir", default=str(ROOT / "_out_r2"))
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    bundle = collect(args.mode)
    write_bundle(bundle, Path(args.outdir))
    print(json.dumps({
        "run_id": bundle["run_id"],
        "mode": args.mode,
        "n_observations": len(bundle["observations"]),
        "series": sorted({x["series_id"] for x in bundle["observations"]}),
        "quality_events": bundle["quality_events"],
    }, indent=2))

    if args.persist:
        from persist_neon import persist_bundle
        result = persist_bundle(bundle)
        print(json.dumps(result, indent=2))

    # Smoke CI should fail on source errors. Scheduled persistence records partial runs,
    # but exits nonzero so GitHub Actions surfaces the outage.
    return 1 if any(x.get("severity") == "ERROR" for x in bundle["quality_events"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
