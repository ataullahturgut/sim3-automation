from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

PIPELINE_VERSION = "GOLD_DATA_R1_2026-08-31"
ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "data_pipeline" / "source_contracts.json"

CBOE = {
    "GVZ": "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv",
    "VIX": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
}
FRED = {
    "DGS10": "DGS10",
    "FEDFUNDS_DAILY": "DFF",
    "USDCNY": "DEXCHUS",
    "NDX": "NASDAQ100",
    "SP500": "SP500",
    "DJI": "DJIA",
}
YF = {
    "DXY": "DX-Y.NYB",
    "US10YT_MODEL_PROXY": "^TNX",
    "NEM": "NEM",
    "HL": "HL-PB",
    "BARRICK_TSX_PROXY": "ABX.TO",
    "DZZ": "DZZ",
    "GLL": "GLL",
}
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
STAKTRAKR_2026 = "https://raw.githubusercontent.com/lbruton/StakTrakr/main/data/spot-history-2026.json"
XAUS_SPOT = "https://xaus.com/api/v1/spot"

HEADERS = {"User-Agent": "Gold-Control-Data-R1/1.0", "Accept": "*/*"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def lineage(series_id: str, source: str, symbol: str | None = None) -> str:
    raw = f"{series_id}|{source}|{symbol or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class Obs:
    run_id: str
    series_id: str
    observation_ts: str
    value: float
    source: str
    source_symbol: str | None
    provider_as_of: str | None
    retrieved_at: str
    frequency: str
    unit: str | None
    transform: str
    quality_status: str
    lineage_id: str
    payload_hash: str | None
    metadata: dict


def get(url: str, **kwargs) -> requests.Response:
    r = requests.get(url, headers=HEADERS, timeout=45, **kwargs)
    r.raise_for_status()
    return r


def load_contracts() -> dict:
    return json.loads(CONTRACTS.read_text(encoding="utf-8"))


def make_obs(run_id: str, series_id: str, dt, value, source: str, symbol: str | None,
             frequency: str, unit: str | None, retrieved_at: datetime, *, provider_as_of=None,
             status="OK", payload_hash=None, metadata=None) -> Obs:
    ts = pd.Timestamp(dt)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    pa = None
    if provider_as_of is not None:
        q = pd.Timestamp(provider_as_of)
        if q.tzinfo is None:
            q = q.tz_localize("UTC")
        else:
            q = q.tz_convert("UTC")
        pa = q.isoformat()
    return Obs(
        run_id=run_id, series_id=series_id, observation_ts=ts.isoformat(), value=float(value),
        source=source, source_symbol=symbol, provider_as_of=pa,
        retrieved_at=pd.Timestamp(retrieved_at).isoformat(), frequency=frequency, unit=unit,
        transform="LEVEL", quality_status=status, lineage_id=lineage(series_id, source, symbol),
        payload_hash=payload_hash, metadata=metadata or {},
    )


def collect_cboe(run_id: str, retrieved_at: datetime) -> list[Obs]:
    out: list[Obs] = []
    for sid, url in CBOE.items():
        r = get(url)
        ph = sha256_bytes(r.content)
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = [str(c).strip().upper() for c in df.columns]
        date_col = "DATE"
        value_col = sid if sid in df.columns else "CLOSE"
        if date_col not in df.columns or value_col not in df.columns:
            raise ValueError(f"CBOE_SCHEMA_{sid}:{list(df.columns)}")
        for _, row in df.tail(4000).iterrows():
            dt = pd.to_datetime(row[date_col], errors="coerce")
            val = pd.to_numeric(row[value_col], errors="coerce")
            if pd.notna(dt) and pd.notna(val):
                out.append(make_obs(run_id, sid, dt, val, "Cboe", sid, "daily", "index",
                                    retrieved_at, provider_as_of=dt, payload_hash=ph,
                                    metadata={"endpoint": url}))
    return out


def fred_csv(series: str) -> tuple[pd.DataFrame, str]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    r = get(url)
    df = pd.read_csv(io.StringIO(r.text))
    return df, sha256_bytes(r.content)


def collect_fred(run_id: str, retrieved_at: datetime) -> list[Obs]:
    units = {
        "DGS10":"percent", "FEDFUNDS_DAILY":"percent", "USDCNY":"CNY_per_USD",
        "NDX":"index", "SP500":"index", "DJI":"index",
    }
    out: list[Obs] = []
    for sid, fred_id in FRED.items():
        df, ph = fred_csv(fred_id)
        if "DATE" not in df.columns or fred_id not in df.columns:
            raise ValueError(f"FRED_SCHEMA_{sid}:{list(df.columns)}")
        for _, row in df.tail(5000).iterrows():
            dt = pd.to_datetime(row["DATE"], errors="coerce")
            val = pd.to_numeric(row[fred_id], errors="coerce")
            if pd.notna(dt) and pd.notna(val):
                out.append(make_obs(run_id, sid, dt, val, "FRED", fred_id, "daily", units[sid],
                                    retrieved_at, provider_as_of=dt, payload_hash=ph,
                                    metadata={"fred_series": fred_id}))
    return out


def collect_yahoo(run_id: str, retrieved_at: datetime) -> list[Obs]:
    try:
        import yfinance as yf
    except ImportError as e:
        raise RuntimeError("yfinance is required for operational proxy series") from e
    out: list[Obs] = []
    for sid, ticker in YF.items():
        df = yf.download(ticker, start="2010-01-01", auto_adjust=True, progress=False, threads=False)
        if df is None or df.empty:
            raise ValueError(f"YF_EMPTY:{sid}:{ticker}")
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        for dt, val in close.dropna().items():
            out.append(make_obs(run_id, sid, dt, val, "Yahoo Finance operational feed", ticker,
                                "daily", "index_or_market_price", retrieved_at,
                                provider_as_of=dt, status="OPERATIONAL_THIRD_PARTY",
                                metadata={"ticker": ticker, "auto_adjust": True}))
    return out


def collect_gpr(run_id: str, retrieved_at: datetime) -> tuple[list[Obs], dict]:
    r = get(GPR_URL)
    ph = sha256_bytes(r.content)
    sheets = pd.read_excel(io.BytesIO(r.content), sheet_name=None, engine="xlrd")
    best = None
    for sh, d in sheets.items():
        cols = {str(c).strip().upper(): c for c in d.columns}
        if {"GPR","GPRT","GPRA"}.issubset(cols):
            dc = cols.get("MONTH") or cols.get("DATE") or d.columns[0]
            q = d[[dc, cols["GPR"], cols["GPRT"], cols["GPRA"]]].copy()
            q.columns = ["date","GPR","GPRT","GPRA"]
            q["date"] = pd.to_datetime(q["date"], errors="coerce")
            q = q.dropna(subset=["date"])
            if best is None or len(q) > len(best):
                best = q
    if best is None:
        raise ValueError("GPR_SCHEMA_NOT_FOUND")
    out: list[Obs] = []
    for _, row in best.iterrows():
        for sid in ["GPR","GPRT","GPRA"]:
            val = pd.to_numeric(row[sid], errors="coerce")
            if pd.notna(val):
                out.append(make_obs(run_id, sid, row["date"], val,
                                    "Caldara-Iacoviello official GPR workbook", sid,
                                    "monthly", "index", retrieved_at,
                                    payload_hash=ph, status="AUTHORITATIVE_REVISION_PRONE",
                                    metadata={"endpoint": GPR_URL}))
    vintage = {"source_id":"GPR_OFFICIAL_WORKBOOK", "retrieved_at":pd.Timestamp(retrieved_at).isoformat(),
               "content_sha256":ph, "content_type":r.headers.get("content-type"),
               "byte_count":len(r.content), "metadata":{"url":GPR_URL}}
    return out, vintage


def collect_staktrakr_2026(run_id: str, retrieved_at: datetime) -> list[Obs]:
    r = get(STAKTRAKR_2026)
    ph = sha256_bytes(r.content)
    rows = r.json()
    map_sid = {"Gold":"GOLD_DAILY_ARCHIVE", "Silver":"SILVER_DAILY_ARCHIVE",
               "Platinum":"PLATINUM_DAILY_ARCHIVE", "Palladium":"PALLADIUM_DAILY_ARCHIVE"}
    out: list[Obs] = []
    for z in rows:
        metal = z.get("metal")
        if metal not in map_sid:
            continue
        dt = pd.to_datetime(z.get("timestamp"), errors="coerce")
        val = pd.to_numeric(z.get("spot"), errors="coerce")
        if pd.isna(dt) or pd.isna(val):
            continue
        out.append(make_obs(run_id, map_sid[metal], dt, val,
                            "lbruton/StakTrakr third-party archive", metal,
                            "daily", "USD/oz", retrieved_at, provider_as_of=dt,
                            payload_hash=ph, status="OPERATIONAL_ARCHIVE_NOT_PRIMARY_AUTHORITY",
                            metadata={"reported_provider": z.get("provider"), "reported_source": z.get("source")}))
    return out


def collect_xau_spot(run_id: str, retrieved_at: datetime) -> list[Obs]:
    r = get(XAUS_SPOT, params={"compact": 1, "fresh": int(retrieved_at.timestamp())})
    ph = sha256_bytes(r.content)
    p = r.json()
    state = p.get("data_state") or {}
    price = p.get("spot_usd_oz") or (p.get("xau") or {}).get("price")
    if price is None:
        raise ValueError("XAUS_PRICE_MISSING")
    as_of = state.get("as_of") or p.get("price_as_of") or p.get("updated_at") or retrieved_at
    source = p.get("price_source") or state.get("source") or "gold-api.com"
    stale = bool(p.get("stale", False)) or str(state.get("status", "")).lower() == "stale"
    return [make_obs(run_id, "XAU_SPOT", as_of, price, source, "XAU", "live_snapshot", "USD/oz",
                     retrieved_at, provider_as_of=as_of, payload_hash=ph,
                     status="STALE" if stale else "OPERATIONAL",
                     metadata={"endpoint":XAUS_SPOT, "raw_status":state.get("status")})]


def basic_quality(obs: Iterable[Obs]) -> list[dict]:
    df = pd.DataFrame([asdict(x) for x in obs])
    events: list[dict] = []
    if df.empty:
        return [{"severity":"ERROR", "code":"EMPTY_COLLECTION", "message":"Collector produced no observations"}]
    for sid, g in df.groupby("series_id"):
        vals = pd.to_numeric(g["value"], errors="coerce")
        if vals.isna().any():
            events.append({"series_id":sid,"severity":"ERROR","code":"NON_NUMERIC","message":"Non-numeric values found"})
        if sid in {"XAU_SPOT","GOLD_DAILY_ARCHIVE","SILVER_DAILY_ARCHIVE","PLATINUM_DAILY_ARCHIVE","PALLADIUM_DAILY_ARCHIVE"} and (vals <= 0).any():
            events.append({"series_id":sid,"severity":"ERROR","code":"NON_POSITIVE_PRICE","message":"Non-positive precious-metal value"})
        dates = pd.to_datetime(g["observation_ts"], utc=True, errors="coerce")
        if dates.isna().any():
            events.append({"series_id":sid,"severity":"ERROR","code":"BAD_TIMESTAMP","message":"Invalid observation timestamp"})
    return events


def write_local_bundle(run_id: str, retrieved_at: datetime, obs: list[Obs], vintages: list[dict], events: list[dict]) -> Path:
    outdir = ROOT / "data_pipeline" / "_out"
    outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([asdict(x) for x in obs]).to_csv(outdir / "observations.csv", index=False)
    (outdir / "vintages.json").write_text(json.dumps(vintages, indent=2), encoding="utf-8")
    (outdir / "quality_events.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
    manifest = {"run_id":run_id, "retrieved_at":pd.Timestamp(retrieved_at).isoformat(),
                "pipeline_version":PIPELINE_VERSION, "n_observations":len(obs),
                "n_quality_events":len(events), "series":sorted({x.series_id for x in obs})}
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return outdir


def main() -> int:
    _ = load_contracts()
    run_id = str(uuid.uuid4())
    retrieved_at = now_utc()
    observations: list[Obs] = []
    vintages: list[dict] = []
    collectors = [collect_xau_spot, collect_cboe, collect_fred, collect_yahoo, collect_staktrakr_2026]
    failures = []
    for fn in collectors:
        try:
            observations.extend(fn(run_id, retrieved_at))
        except Exception as e:
            failures.append({"collector":fn.__name__, "error":f"{type(e).__name__}: {e}"})
    try:
        gpr_obs, vintage = collect_gpr(run_id, retrieved_at)
        observations.extend(gpr_obs)
        vintages.append(vintage)
    except Exception as e:
        failures.append({"collector":"collect_gpr", "error":f"{type(e).__name__}: {e}"})

    events = basic_quality(observations)
    for f in failures:
        events.append({"severity":"ERROR", "code":"COLLECTOR_FAILURE", "message":f["error"], "metadata":{"collector":f["collector"]}})
    outdir = write_local_bundle(run_id, retrieved_at, observations, vintages, events)
    print(json.dumps({"outdir":str(outdir), "observations":len(observations), "failures":failures, "quality_events":events}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
