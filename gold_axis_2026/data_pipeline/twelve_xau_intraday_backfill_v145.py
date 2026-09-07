from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import requests

import collector_r2 as base
from persist_neon import persist_bundle

SERIES_ID = "XAU_INTRADAY_TWELVE_REST_1M"
SOURCE = "Twelve Data REST"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
PIPELINE_VERSION = "GOLD_CONTROL_XAU_INTRADAY_BOOTSTRAP_V145"
QUALITY_STATUS = "APPROVED_LIVE_SHADOW_BOOTSTRAP_1M"
MAX_DAYS = 14


def _api_key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")
    return value


def _utc(value: object) -> datetime:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.to_pydatetime()


def _request_day(session: requests.Session, day: date) -> tuple[dict, bytes]:
    response = session.get(
        TIME_SERIES_URL,
        params={
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "start_date": f"{day.isoformat()} 00:00:00",
            "end_date": f"{day.isoformat()} 23:59:59",
            "timezone": "UTC",
            "outputsize": 2000,
            "format": "JSON",
        },
        headers={
            "Authorization": f"apikey {_api_key()}",
            "User-Agent": "GoldControl-XAU-Intraday-Bootstrap/1.0",
        },
        timeout=(8, 45),
    )
    try:
        payload = response.json()
    except ValueError as exc:
        response.raise_for_status()
        raise RuntimeError("TWELVE_NON_JSON_RESPONSE") from exc
    if payload.get("status") == "error":
        try:
            code = int(payload.get("code"))
        except (TypeError, ValueError):
            code = None
        if code == 404:
            return payload, response.content
        raise RuntimeError(f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}")
    response.raise_for_status()
    meta = payload.get("meta") or {}
    if (meta.get("symbol") or SYMBOL) != SYMBOL:
        raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{meta.get('symbol')}")
    if meta.get("interval") not in (None, INTERVAL):
        raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{meta.get('interval')}")
    return payload, response.content


def _extract(day: date, payload: dict) -> list[tuple[datetime, float]]:
    if payload.get("status") == "error":
        return []
    rows: dict[datetime, float] = {}
    for item in payload.get("values") or []:
        raw_dt = str(item.get("datetime") or "")
        ts = pd.to_datetime(raw_dt, utc=True, errors="coerce")
        if pd.isna(ts) or ts.date() != day:
            continue
        value = pd.to_numeric(item.get("close"), errors="coerce")
        if pd.isna(value) or float(value) <= 0:
            raise RuntimeError(f"TWELVE_INVALID_CLOSE:{day.isoformat()}:{raw_dt}")
        dt = ts.to_pydatetime().replace(second=0, microsecond=0)
        if dt in rows and rows[dt] != float(value):
            raise RuntimeError(f"TWELVE_DUPLICATE_MINUTE_CONFLICT:{dt.isoformat()}")
        rows[dt] = float(value)
    return sorted(rows.items())


def collect(days: list[date]) -> dict:
    if not days or len(days) > MAX_DAYS:
        raise ValueError(f"days must contain 1..{MAX_DAYS} dates")
    retrieved_at = datetime.now(timezone.utc)
    run_id = str(base.uuid.uuid4())
    session = base.session()
    observations = []
    day_summary = []
    for day in sorted(days):
        if day > retrieved_at.date():
            raise RuntimeError(f"BLOCKED_FUTURE_DAY:{day.isoformat()}")
        payload, raw = _request_day(session, day)
        points = _extract(day, payload)
        day_summary.append({"date": day.isoformat(), "rows": len(points)})
        payload_hash = base.sha256_bytes(raw)
        for ts, close in points:
            # For bootstrap history, provider event availability is not known at
            # original minute granularity. We therefore floor available_as_of at
            # this retrieval time and explicitly classify the evidence as catch-up.
            observations.append(
                asdict(
                    base.make_obs(
                        run_id,
                        SERIES_ID,
                        ts,
                        close,
                        SOURCE,
                        SYMBOL,
                        "1min",
                        "USD/troy_oz",
                        retrieved_at,
                        provider_as_of=ts,
                        available_as_of=retrieved_at,
                        status=QUALITY_STATUS,
                        payload_hash=payload_hash,
                        metadata={
                            "contract": PIPELINE_VERSION,
                            "endpoint": TIME_SERIES_URL,
                            "provider_symbol": SYMBOL,
                            "provider_interval": INTERVAL,
                            "requested_timezone": "UTC",
                            "acquisition_mode": "REST_BOOTSTRAP_CATCHUP",
                            "evidence_class": "HISTORICAL_BOOTSTRAP_CATCHUP",
                            "prospective_claim": False,
                            "fallback_policy": "NONE",
                            "interpolation": "FORBIDDEN",
                            "forward_fill": "FORBIDDEN",
                            "rights_policy": "PRIVATE_INTERNAL_NON_DISPLAY_NO_PUBLIC_RAW_REDISTRIBUTION",
                        },
                    )
                )
            )
    return {
        "run_id": run_id,
        "started_at": base.iso_utc(retrieved_at),
        "finished_at": base.iso_utc(datetime.now(timezone.utc)),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "intraday:twelve_xau_1m_bootstrap",
        "observations": observations,
        "vintages": [],
        "quality_events": [],
        "day_summary": day_summary,
    }


def _days_from_args(start: str | None, end: str | None, lookback_days: int) -> list[date]:
    today = datetime.now(timezone.utc).date()
    if start or end:
        if not start or not end:
            raise ValueError("--start-date and --end-date must be provided together")
        a = date.fromisoformat(start)
        b = date.fromisoformat(end)
    else:
        if lookback_days < 1 or lookback_days > MAX_DAYS:
            raise ValueError(f"--lookback-days must be 1..{MAX_DAYS}")
        a = today - timedelta(days=lookback_days - 1)
        b = today
    if b < a:
        raise ValueError("end date precedes start date")
    days = [a + timedelta(days=i) for i in range((b - a).days + 1)]
    if len(days) > MAX_DAYS:
        raise ValueError(f"requested date range exceeds {MAX_DAYS} days")
    return days


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--lookback-days", type=int, default=1)
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    days = _days_from_args(args.start_date, args.end_date, args.lookback_days)
    bundle = collect(days)
    print(json.dumps({
        "contract": PIPELINE_VERSION,
        "run_id": bundle["run_id"],
        "day_summary": bundle["day_summary"],
        "observation_count": len(bundle["observations"]),
        "database_write_requested": bool(args.persist),
        "raw_market_values_logged": False,
    }, indent=2))
    if args.persist:
        result = persist_bundle(bundle)
        print(json.dumps({"persist": result}, indent=2))
        if result.get("status") != "SUCCESS":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
