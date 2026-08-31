from __future__ import annotations

import os
from typing import Iterable

import pandas as pd
import requests

import collector_r2 as base

TIME_SERIES_URL = "https://api.twelvedata.com/time_series"

SERIES = {
    "NEM_TWELVEDATA": {
        "symbol": "NEM",
        "exchange": "NYSE",
        "mic_code": "XNYS",
        "type": "Common Stock",
        "currency": "USD",
        "unit": "USD",
    },
    "BARRICK_B_TWELVEDATA": {
        "symbol": "B",
        "exchange": "NYSE",
        "mic_code": "XNYS",
        "type": "Common Stock",
        "currency": "USD",
        "unit": "USD",
    },
    "GLL_TWELVEDATA": {
        "symbol": "GLL",
        "exchange": "NYSE",
        "mic_code": "ARCX",
        "type": "ETF",
        "currency": "USD",
        "unit": "USD",
    },
    "DZZ_TWELVEDATA": {
        "symbol": "DZZ",
        "exchange": "NYSE",
        "mic_code": "ARCX",
        "type": "ETF",
        "currency": "USD",
        "unit": "USD",
    },
    "HL_PB_TWELVEDATA": {
        "symbol": "HL.PR.B",
        "exchange": "NYSE",
        "mic_code": "XNYS",
        "type": "Preferred Stock",
        "currency": "USD",
        "unit": "USD",
    },
}

QUALITY_STATUS = "APPROVED_VENDOR_IDENTITY_VALIDATED_INTERNAL_NON_DISPLAY"


def api_key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")
    return value


def outputsize(mode: str) -> int:
    return 5000 if mode == "backfill" else 260


def _validate_meta(series_id: str, meta: dict, spec: dict) -> None:
    checks = {
        "symbol": spec["symbol"],
        "exchange": spec["exchange"],
        "mic_code": spec["mic_code"],
        "currency": spec["currency"],
        "type": spec["type"],
    }
    mismatches = {}
    for key, expected in checks.items():
        actual = meta.get(key)
        if actual != expected:
            mismatches[key] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"TWELVE_META_MISMATCH:{series_id}:{mismatches}")


def _collect_one(
    session: requests.Session,
    run_id: str,
    retrieved_at,
    mode: str,
    series_id: str,
    spec: dict,
):
    response = session.get(
        TIME_SERIES_URL,
        params={
            "symbol": spec["symbol"],
            "interval": "1day",
            "outputsize": outputsize(mode),
            "format": "JSON",
        },
        headers={"Authorization": f"apikey {api_key()}", "User-Agent": "GoldControl/2.7"},
        timeout=(8, 30),
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") == "error":
        raise RuntimeError(
            f"TWELVE_API_ERROR:{series_id}:{payload.get('code')}:{payload.get('message')}"
        )

    meta = payload.get("meta") or {}
    _validate_meta(series_id, meta, spec)
    values = payload.get("values") or []
    if not values:
        raise RuntimeError(f"TWELVE_NO_VALUES:{series_id}")

    rows = []
    for item in values:
        dt = pd.to_datetime(item.get("datetime"), errors="coerce")
        close = pd.to_numeric(item.get("close"), errors="coerce")
        if pd.isna(dt) or pd.isna(close):
            continue
        rows.append((dt, float(close)))
    if not rows:
        raise RuntimeError(f"TWELVE_EMPTY_AFTER_PARSE:{series_id}")
    rows.sort(key=lambda x: x[0])

    payload_hash = base.sha256_bytes(response.content)
    observations = []
    for dt, close in rows:
        observations.append(base.make_obs(
            run_id,
            series_id,
            dt,
            close,
            "Twelve Data",
            spec["symbol"],
            "daily_close",
            spec["unit"],
            retrieved_at,
            provider_as_of=None,
            # The bar date is not a proven historical publication timestamp.
            # Backfilled rows become historically usable only from first retrieval.
            available_as_of=retrieved_at,
            status=QUALITY_STATUS,
            payload_hash=payload_hash,
            metadata={
                "endpoint": TIME_SERIES_URL,
                "vendor_symbol": spec["symbol"],
                "exchange": meta.get("exchange"),
                "mic_code": meta.get("mic_code"),
                "currency": meta.get("currency"),
                "instrument_type": meta.get("type"),
                "exchange_timezone": meta.get("exchange_timezone"),
                "availability_policy": "first_retrieval_floor",
                "historical_release_timestamp_reconstruction": "NOT_PROVEN",
                "rights_policy": "PRIVATE_INTERNAL_NON_DISPLAY_NO_PUBLIC_RAW_REDISTRIBUTION",
                "provider_identity_validation": "PASS_2026-08-31",
            },
        ))
    return observations


def collect_twelve_market(
    run_id: str,
    retrieved_at,
    mode: str,
    series_ids: Iterable[str] | None = None,
):
    requested = list(series_ids or SERIES.keys())
    unknown = sorted(set(requested) - set(SERIES))
    if unknown:
        raise ValueError(f"UNKNOWN_TWELVE_SERIES:{unknown}")

    session = base.session()
    observations = []
    failures = []
    for series_id in requested:
        try:
            observations.extend(_collect_one(
                session, run_id, retrieved_at, mode, series_id, SERIES[series_id]
            ))
        except Exception as exc:
            failures.append((series_id, f"{type(exc).__name__}: {exc}"))

    found = {o.series_id for o in observations}
    missing = sorted(set(requested) - found)
    if failures or missing:
        raise RuntimeError(f"TWELVE_COLLECTION_INCOMPLETE:missing={missing}:failures={failures}")
    return observations
