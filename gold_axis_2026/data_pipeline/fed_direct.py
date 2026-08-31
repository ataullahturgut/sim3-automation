from __future__ import annotations

import io
from typing import Iterable

import pandas as pd
import requests

import collector_r2 as base

H15_PACKAGE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?"
    "filetype=csv&from=&label=include&lastobs={lastobs}&layout=seriescolumn&"
    "rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&to=&type=package"
)
H10_RATES_PACKAGE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?"
    "filetype=csv&from=&label=include&lastobs={lastobs}&layout=seriescolumn&"
    "rel=H10&series=60f32914ab61dfab590e0e470153e3ae&to=&type=package"
)
H10_INDEX_PACKAGE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?"
    "filetype=csv&from=&label=include&lastobs={lastobs}&layout=seriescolumn&"
    "rel=H10&series=122e3bcb627e8e53f1bf72a1a09cfb81&to=&type=package"
)
NYFED_EFFR_URL = "https://markets.newyorkfed.org/api/rates/unsecured/effr/last/{lastobs}.json"

DIRECT_SERIES = {
    "DGS10_FRB_H15": {
        "url_template": H15_PACKAGE_URL,
        "column": "RIFLGFCY10_N.B",
        "source": "Board of Governors of the Federal Reserve System H.15 DDP",
        "symbol": "RIFLGFCY10_N.B",
        "frequency": "daily",
        "unit": "percent",
        "status": "APPROVED_DIRECT_AUTHORITY",
        "release": "H.15",
    },
    "DEXCHUS_FRB_H10": {
        "url_template": H10_RATES_PACKAGE_URL,
        "column": "RXI_N.B.CH",
        "source": "Board of Governors of the Federal Reserve System H.10 DDP",
        "symbol": "RXI_N.B.CH",
        "frequency": "daily_observation_release_lagged",
        "unit": "CNY per USD",
        "status": "APPROVED_DIRECT_AUTHORITY",
        "release": "H.10",
    },
    "DTWEXBGS_FRB_H10": {
        "url_template": H10_INDEX_PACKAGE_URL,
        "column": "JRXWTFB_N.B",
        "source": "Board of Governors of the Federal Reserve System H.10 DDP",
        "symbol": "JRXWTFB_N.B",
        "frequency": "daily_observation_release_lagged",
        "unit": "index",
        "status": "APPROVED_PROXY_ONLY_DIRECT_AUTHORITY",
        "release": "H.10",
    },
}


def _lastobs(mode: str) -> int:
    if mode == "backfill":
        return 5000
    if mode == "daily":
        return 220
    return 40


def _get(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, headers=base.HEADERS, timeout=(8, 25))
    response.raise_for_status()
    return response


def _read_frb_package(content: bytes) -> pd.DataFrame:
    # Federal Reserve DDP package CSV contains five metadata rows followed by
    # the actual Time Period header row.
    df = pd.read_csv(io.BytesIO(content), skiprows=5)
    if "Time Period" not in df.columns:
        raise ValueError(f"FRB_DDP_TIME_PERIOD_MISSING:{list(df.columns)}")
    df["Time Period"] = pd.to_datetime(df["Time Period"], errors="coerce")
    return df.dropna(subset=["Time Period"])


def _collect_frb_series(
    session: requests.Session,
    run_id: str,
    retrieved_at,
    mode: str,
    series_ids: Iterable[str],
):
    out = []
    lastobs = _lastobs(mode)

    # Group series that come from the same official DDP package so the Board is
    # not hit repeatedly for the same payload.
    groups: dict[str, list[tuple[str, dict]]] = {}
    for sid in series_ids:
        spec = DIRECT_SERIES[sid]
        url = spec["url_template"].format(lastobs=lastobs)
        groups.setdefault(url, []).append((sid, spec))

    for url, group in groups.items():
        response = _get(session, url)
        payload_hash = base.sha256_bytes(response.content)
        df = _read_frb_package(response.content)

        for sid, spec in group:
            column = spec["column"]
            if column not in df.columns:
                raise ValueError(f"FRB_DDP_SERIES_MISSING:{sid}:{column}:{list(df.columns)}")

            values = pd.to_numeric(df[column], errors="coerce")
            good = df.loc[values.notna(), ["Time Period"]].copy()
            good["value"] = values[values.notna()].astype(float).values
            if good.empty:
                raise ValueError(f"FRB_DDP_EMPTY:{sid}")

            for _, row in good.iterrows():
                dt = row["Time Period"]
                out.append(base.make_obs(
                    run_id,
                    sid,
                    dt,
                    row["value"],
                    spec["source"],
                    spec["symbol"],
                    spec["frequency"],
                    spec["unit"],
                    retrieved_at,
                    provider_as_of=dt,
                    # We are not reconstructing historical release timestamps here.
                    # For leakage safety, a value is usable no earlier than the first
                    # time our own data plane retrieved it.
                    available_as_of=retrieved_at,
                    status=spec["status"],
                    payload_hash=payload_hash,
                    metadata={
                        "endpoint": url,
                        "authority": "Federal Reserve Board",
                        "release": spec["release"],
                        "frb_unique_identifier": column,
                        "availability_policy": "first_retrieval_floor",
                        "historical_release_timestamp_reconstruction": "NOT_PROVEN",
                    },
                ))
    return out


def _collect_effr(session: requests.Session, run_id: str, retrieved_at, mode: str):
    lastobs = 1000 if mode == "backfill" else (220 if mode == "daily" else 40)
    url = NYFED_EFFR_URL.format(lastobs=lastobs)
    response = _get(session, url)
    payload_hash = base.sha256_bytes(response.content)
    payload = response.json()
    rows = payload.get("refRates") or []
    if not rows:
        raise ValueError("NYFED_EFFR_NO_ROWS")

    out = []
    for row in rows:
        dt = pd.to_datetime(row.get("effectiveDate"), errors="coerce")
        val = pd.to_numeric(row.get("percentRate"), errors="coerce")
        if pd.isna(dt) or pd.isna(val):
            continue
        revision = str(row.get("revisionIndicator") or "").strip()
        out.append(base.make_obs(
            run_id,
            "EFFR_NYFED",
            dt,
            val,
            "Federal Reserve Bank of New York Markets Data API",
            "EFFR",
            "business_day_rate",
            "percent",
            retrieved_at,
            provider_as_of=dt,
            available_as_of=retrieved_at,
            status="APPROVED_DIRECT_AUTHORITY_REVISED" if revision else "APPROVED_DIRECT_AUTHORITY",
            payload_hash=payload_hash,
            metadata={
                "endpoint": url,
                "authority": "Federal Reserve Bank of New York",
                "revision_indicator": revision,
                "target_rate_from": row.get("targetRateFrom"),
                "target_rate_to": row.get("targetRateTo"),
                "volume_in_billions": row.get("volumeInBillions"),
                "availability_policy": "first_retrieval_floor",
                "publication_timestamp_reconstruction": "NOT_PROVEN",
            },
        ))
    if not out:
        raise ValueError("NYFED_EFFR_EMPTY_AFTER_PARSE")
    return out


def collect_fed_direct(run_id: str, retrieved_at, mode: str):
    session = requests.Session()
    session.headers.update(base.HEADERS)

    observations = _collect_frb_series(
        session,
        run_id,
        retrieved_at,
        mode,
        ["DGS10_FRB_H15", "DEXCHUS_FRB_H10", "DTWEXBGS_FRB_H10"],
    )
    observations.extend(_collect_effr(session, run_id, retrieved_at, mode))

    required = {"DGS10_FRB_H15", "DEXCHUS_FRB_H10", "DTWEXBGS_FRB_H10", "EFFR_NYFED"}
    found = {o.series_id for o in observations}
    missing = sorted(required - found)
    if missing:
        raise ValueError(f"FED_DIRECT_REQUIRED_SERIES_MISSING:{missing}")
    return observations
