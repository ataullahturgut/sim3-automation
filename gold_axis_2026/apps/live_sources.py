from __future__ import annotations

from io import StringIO
from time import time
from typing import Any

import pandas as pd
import requests

XAUS_SPOT_URL = "https://xaus.com/api/v1/spot"
XAUS_HISTORY_URL = "https://xaus.com/api/v1/history"
CBOE_GVZ_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv"

HEADERS = {
    "User-Agent": "Gold-Control/1.0 (+https://github.com/ataullahturgut/sim3-automation)",
    "Accept": "application/json,text/csv,*/*",
}


def _get(url: str, *, params: dict[str, Any] | None = None, timeout: int = 15) -> requests.Response:
    r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r


def fetch_xau_spot() -> dict[str, Any]:
    """Indicative XAU/USD spot with explicit freshness metadata.

    This is a display/monitoring feed. It must not be silently treated as the
    frozen R4.1 EOD execution close.
    """
    r = _get(XAUS_SPOT_URL, params={"compact": 1, "fresh": int(time())})
    payload = r.json()
    state = payload.get("data_state") or {}
    price = payload.get("spot_usd_oz")
    if price is None:
        xau = payload.get("xau") or {}
        price = xau.get("price")
    if price is None:
        raise ValueError("XAUS response has no XAU/USD price")

    status = str(state.get("status") or ("stale" if payload.get("stale") else "unknown"))
    as_of = state.get("as_of") or payload.get("price_as_of") or payload.get("updated_at")
    age_seconds = state.get("age_seconds")
    source = state.get("source") or payload.get("price_source") or "XAUS"

    return {
        "price": float(price),
        "status": status,
        "as_of": as_of,
        "age_seconds": None if age_seconds is None else float(age_seconds),
        "source": str(source),
        "stale": bool(payload.get("stale", status.lower() == "stale")),
        "endpoint": XAUS_SPOT_URL,
    }


def fetch_xau_history() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Daily XAU/USD history from XAUS history endpoint."""
    payload = _get(XAUS_HISTORY_URL).json()
    points = payload.get("points") or []
    if not points:
        raise ValueError("XAUS history response has no points")

    df = pd.DataFrame(points)
    rename = {"d": "date", "c": "close", "h": "high", "l": "low", "o": "open"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError(f"Unexpected XAUS history columns: {list(df.columns)}")
    df["date"] = pd.to_datetime(df["date"], errors="raise", utc=True).dt.tz_convert(None)
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date", "close"]).sort_values("date").drop_duplicates("date", keep="last")

    state = payload.get("data_state") or {}
    meta = {
        "status": state.get("status", "unknown"),
        "as_of": state.get("as_of") or payload.get("updated_at"),
        "source": state.get("source") or "XAUS history",
        "endpoint": XAUS_HISTORY_URL,
    }
    return df.reset_index(drop=True), meta


def fetch_gvz_history() -> pd.DataFrame:
    """Official Cboe GVZ daily history (updated by Cboe)."""
    r = _get(CBOE_GVZ_URL)
    df = pd.read_csv(StringIO(r.text))
    original = list(df.columns)
    df.columns = [str(c).strip().lower() for c in df.columns]

    date_col = next((c for c in ["date", "trade_date"] if c in df.columns), None)
    close_col = next((c for c in ["close", "closeprice", "close_price"] if c in df.columns), None)
    if date_col is None or close_col is None:
        raise ValueError(f"Unexpected Cboe GVZ columns: {original}")

    out = pd.DataFrame({
        "date": pd.to_datetime(df[date_col], errors="coerce"),
        "close": pd.to_numeric(df[close_col], errors="coerce"),
    })
    for col in ["open", "high", "low"]:
        if col in df.columns:
            out[col] = pd.to_numeric(df[col], errors="coerce")
    return out.dropna(subset=["date", "close"]).sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)


def fetch_gvz_latest() -> dict[str, Any]:
    df = fetch_gvz_history()
    if df.empty:
        raise ValueError("Cboe GVZ history is empty")
    row = df.iloc[-1]
    return {
        "close": float(row["close"]),
        "as_of": pd.Timestamp(row["date"]).date().isoformat(),
        "source": "Cboe Gold ETF Volatility Index (GVZ) daily history",
        "endpoint": CBOE_GVZ_URL,
    }
