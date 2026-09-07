from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
import requests


GOLDAPI_SPOT_URL = "https://api.gold-api.com/price/XAU"
XAUS_HISTORY_URL = "https://xaus.com/api/v1/history"
CBOE_GVZ_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv"

HEADERS = {
    "User-Agent": "Gold-Control/1.0 (+https://github.com/ataullahturgut/sim3-automation)",
    "Accept": "application/json,text/csv,*/*",
}


def _get(url: str, *, params: dict[str, Any] | None = None, timeout: int = 15) -> requests.Response:
    response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response


def _age_seconds(value: Any) -> float | None:
    if not value:
        return None
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return max(0.0, float((pd.Timestamp.now(tz="UTC") - ts).total_seconds()))


def fetch_xau_spot(max_response_age_seconds: int = 300) -> dict[str, Any]:
    """Indicative XAU/USD display price; never a model-authority input."""
    payload = _get(GOLDAPI_SPOT_URL).json()
    symbol = str(payload.get("symbol") or "").upper()
    currency = str(payload.get("currency") or "").upper()
    if symbol != "XAU" or currency != "USD":
        raise ValueError(f"Gold API instrument mismatch: {symbol}/{currency}")
    price = float(payload.get("price"))
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
        "source": "Gold API",
        "source_series": "XAU_SPOT_GOLDAPI",
        "stale": stale,
        "endpoint": GOLDAPI_SPOT_URL,
        "use_role": "INDICATIVE_DISPLAY_ONLY_NO_MODEL_USE",
    }


def fetch_xau_history() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Daily XAU/USD history for chart/display use only."""
    payload = _get(XAUS_HISTORY_URL, params={"range": "1y"}).json()
    points = payload.get("points") or []
    if not points:
        raise ValueError("XAU history response has no points")

    df = pd.DataFrame(points)
    rename = {"d": "date", "c": "close", "h": "high", "l": "low", "o": "open"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if "date" not in df.columns or "close" not in df.columns:
        raise ValueError(f"Unexpected XAU history columns: {list(df.columns)}")

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
        "use_role": "DISPLAY_HISTORY_ONLY_NO_MODEL_USE",
    }
    return df.reset_index(drop=True), meta


def fetch_gvz_history() -> pd.DataFrame:
    """Official Cboe GVZ daily history for risk/display context."""
    response = _get(CBOE_GVZ_URL)
    df = pd.read_csv(StringIO(response.text))
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
        "value": float(row["close"]),
        "as_of": pd.Timestamp(row["date"]).date().isoformat(),
        "source": "Cboe Gold ETF Volatility Index (GVZ) daily history",
        "endpoint": CBOE_GVZ_URL,
        "use_role": "RISK_DISPLAY_CONTEXT_ONLY",
    }
