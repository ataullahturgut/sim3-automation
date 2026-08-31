from __future__ import annotations

import os
from typing import Iterable

import pandas as pd
import requests

import collector_r2 as base

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"

INDEX_SERIES = {
    "SP500_FRED": {
        "fred_id": "SP500",
        "semantic": "SP500",
        "source": "FRED; underlying S&P Dow Jones Indices",
        "unit": "index",
        "status": "APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION",
    },
    "DJIA_FRED": {
        "fred_id": "DJIA",
        "semantic": "DJI",
        "source": "FRED; underlying S&P Dow Jones Indices",
        "unit": "index",
        "status": "APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION",
    },
    "NASDAQ100_FRED": {
        "fred_id": "NASDAQ100",
        "semantic": "NDX",
        "source": "FRED; underlying Nasdaq Inc.",
        "unit": "index",
        "status": "APPROVED_PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION",
    },
}


def api_key() -> str:
    value = os.environ.get("FRED_API_KEY", "").strip()
    if not value:
        raise RuntimeError("FRED_API_KEY is not set")
    return value


def _limit(mode: str) -> int:
    if mode == "backfill":
        return 100000
    if mode == "daily":
        return 260
    return 60


def _fetch_one(
    session: requests.Session,
    run_id: str,
    retrieved_at,
    mode: str,
    series_id: str,
    spec: dict,
):
    params = {
        "series_id": spec["fred_id"],
        "api_key": api_key(),
        "file_type": "json",
        "sort_order": "desc",
        "limit": _limit(mode),
    }
    response = session.get(
        FRED_OBSERVATIONS_URL,
        params=params,
        headers=base.HEADERS,
        timeout=(8, 25),
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("observations") or []
    if not rows:
        raise ValueError(f"FRED_API_NO_OBSERVATIONS:{series_id}")

    payload_hash = base.sha256_bytes(response.content)
    parsed = []
    for row in rows:
        dt = pd.to_datetime(row.get("date"), errors="coerce")
        value = pd.to_numeric(row.get("value"), errors="coerce")
        if pd.isna(dt) or pd.isna(value):
            continue
        parsed.append((dt, float(value), row))

    parsed.sort(key=lambda x: x[0])
    if not parsed:
        raise ValueError(f"FRED_API_EMPTY_AFTER_PARSE:{series_id}")

    out = []
    for dt, value, row in parsed:
        out.append(base.make_obs(
            run_id,
            series_id,
            dt,
            value,
            spec["source"],
            spec["fred_id"],
            "daily_close",
            spec["unit"],
            retrieved_at,
            provider_as_of=None,
            # Current FRED API observations are not retroactively treated as
            # historically knowable. Our prospective data plane starts the clock
            # when it actually retrieves the observation.
            available_as_of=retrieved_at,
            status=spec["status"],
            payload_hash=payload_hash,
            metadata={
                "endpoint": FRED_OBSERVATIONS_URL,
                "fred_series_id": spec["fred_id"],
                "fred_realtime_start": row.get("realtime_start"),
                "fred_realtime_end": row.get("realtime_end"),
                "availability_policy": "first_retrieval_floor",
                "historical_vintage_reconstruction": "NOT_PROVEN",
                "rights_policy": "PRIVATE_MODEL_USE_NO_PUBLIC_RAW_REDISTRIBUTION",
            },
        ))
    return out


def collect_fred_indices(run_id: str, retrieved_at, mode: str, series_ids: Iterable[str] | None = None):
    session = requests.Session()
    session.headers.update(base.HEADERS)
    requested = list(series_ids or INDEX_SERIES.keys())
    unknown = sorted(set(requested) - set(INDEX_SERIES))
    if unknown:
        raise ValueError(f"UNKNOWN_FRED_INDEX_SERIES:{unknown}")

    observations = []
    failures = []
    for series_id in requested:
        try:
            observations.extend(_fetch_one(
                session, run_id, retrieved_at, mode, series_id, INDEX_SERIES[series_id]
            ))
        except Exception as exc:
            failures.append((series_id, f"{type(exc).__name__}: {exc}"))

    found = {o.series_id for o in observations}
    missing = sorted(set(requested) - found)
    if failures or missing:
        raise RuntimeError(f"FRED_INDEX_COLLECTION_INCOMPLETE:missing={missing}:failures={failures}")
    return observations
