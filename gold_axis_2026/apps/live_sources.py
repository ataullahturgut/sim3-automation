from __future__ import annotations

from io import StringIO
from time import time
from typing import Any

import pandas as pd
import requests

GOLDAPI_SPOT_URL = "https://api.gold-api.com/price/XAU"
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


def _age_seconds(value: Any) -> float | None:
    if not value:
        return None
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    now = pd.Timestamp.now(tz="UTC")
    return max(0.0, float((now - ts).total_seconds()))


def fetch_xau_spot(max_response_age_seconds: int = 300) -> dict[str, Any]:
    """Gold API indicative XAU/USD display price.

    This provider is frozen for Piyasa display/monitoring only. Its upstream
    fallback lineage is provider-managed/opaque, so this function must never be
    used as the R4.1 EOD close, forecast input, VW reference, or decision input.
    """
    r = _get(GOLDAPI_SPOT_URL)
    payload = r.json()
    symbol = str(payload.get("symbol") or "").upper()
    currency = str(payload.get("currency") or "").upper()
    if symbol != "XAU":
        raise ValueError(f"Gold API symbol mismatch: {symbol!r}")
    if currency != "USD":
        raise ValueError(f"Gold API currency mismatch: {currency!r}")
    price = payload.get("price")
    if price is None:
        raise ValueError("Gold API response has no price")
    price = float(price)
    if not pd.notna(price) or price <= 0:
        raise ValueError("Gold API price is not positive finite")
    updated_at = payload.get("updatedAt")
    age = _age_seconds(updated_at)
    stale = age is None or age > max_response_age_seconds
    return {
        "price": price,
        "status": "stale" if stale else "fresh",
        "as_of": updated_at,
        "updated_at": updated_at,
        "provider_age_seconds": age,
        "response_age_seconds": age,
        "price_age_seconds": age,
        "source": "Gold API",
        "source_series": "XAU_SPOT_GOLDAPI",
        "stale": stale,
        "provider_stale": stale,
        "cache_stale": stale,
        "endpoint": GOLDAPI_SPOT_URL,
        "use_role": "INDICATIVE_DISPLAY_ONLY_NO_MODEL_USE",
        "upstream_lineage": "OPAQUE_PROVIDER_MANAGED_FALLBACK",
    }


def fetch_xau_spot_xaus(max_response_age_seconds: int = 300) -> dict[str, Any]:
    """Legacy XAUS indicative XAU/USD spot with explicit freshness metadata.

    The endpoint's own data_state is preserved, but we also independently check
    the response generation timestamp, per XAUS's documented stale-proof rule.
    This is display/monitoring data and is not silently promoted to the frozen
    R4.1 EOD execution close.
    """
    r = _get(XAUS_SPOT_URL, params={"compact": 1, "fresh": int(time())})
    payload = r.json()
    state = payload.get("data_state") or {}

    price = payload.get("spot_usd_oz")
    if price is None:
        price = (payload.get("xau") or {}).get("price")
    if price is None:
        raise ValueError("XAUS response has no XAU/USD price")

    status = str(state.get("status") or ("stale" if payload.get("stale") else "unknown"))
    price_as_of = state.get("as_of") or payload.get("price_as_of")
    updated_at = payload.get("updated_at")
    provider_age = state.get("age_seconds")
    response_age = _age_seconds(updated_at)
    price_age = _age_seconds(price_as_of)

    provider_stale = bool(payload.get("stale", status.lower() == "stale"))
    cache_stale = response_age is not None and response_age > max_response_age_seconds
    stale = provider_stale or cache_stale

    source = payload.get("price_source") or state.get("source") or payload.get("source") or "XAUS"

    return {
        "price": float(price),
        "status": "stale" if stale else status,
        "as_of": price_as_of or updated_at,
        "updated_at": updated_at,
        "provider_age_seconds": None if provider_age is None else float(provider_age),
        "response_age_seconds": response_age,
        "price_age_seconds": price_age,
        "source": str(source),
        "stale": stale,
        "provider_stale": provider_stale,
        "cache_stale": cache_stale,
        "endpoint": XAUS_SPOT_URL,
    }


def fetch_xau_history() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Daily XAU/USD history from XAUS history endpoint."""
    payload = _get(XAUS_HISTORY_URL, params={"range": "1y"}).json()
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
        "source": payload.get("price_source") or state.get("source") or "XAUS history",
        "endpoint": XAUS_HISTORY_URL,
    }
    return df.reset_index(drop=True), meta


def fetch_gvz_history() -> pd.DataFrame:
    """Official Cboe GVZ daily history (updated daily by Cboe)."""
    r = _get(CBOE_GVZ_URL)
    df = pd.read_csv(StringIO(r.text))
    original = list(df.columns)
    df.columns = [str(c).strip().lower() for c in df.columns]

    date_col = next((c for c in ["date", "trade_date"] if c in df.columns), None)
    value_col = next((c for c in ["gvz", "close", "closeprice", "close_price"] if c in df.columns), None)
    if date_col is None or value_col is None:
        raise ValueError(f"Unexpected Cboe GVZ columns: {original}")

    out = pd.DataFrame({
        "date": pd.to_datetime(df[date_col], errors="coerce"),
        "close": pd.to_numeric(df[value_col], errors="coerce"),
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
