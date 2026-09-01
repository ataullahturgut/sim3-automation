from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import requests

import collector_r2 as base
from persist_neon import persist_bundle

SERIES_ID = "XAU_EOD_TWELVE_NY17"
SOURCE = "Twelve Data"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
NY = ZoneInfo("America/New_York")
TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
PIPELINE_VERSION = "GOLD_DATA_R2.8_XAU_NY17_2026-09-01"
QUALITY_STATUS = "APPROVED_CANONICAL_TWELVE_NY17"
CUTOFF = time(17, 0, 0)
TARGET_BAR = time(16, 59, 0)


def _api_key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")
    return value


def _candidate_dates(now_ny: datetime, lookback_days: int = 10) -> list[date]:
    if now_ny.tzinfo is None:
        raise ValueError("now_ny must be timezone-aware")
    start = now_ny.date()
    out: list[date] = []
    for offset in range(lookback_days + 1):
        d = start - timedelta(days=offset)
        cutoff_dt = datetime.combine(d, CUTOFF, tzinfo=NY)
        if cutoff_dt <= now_ny:
            out.append(d)
    return out


def _request_day(session: requests.Session, d: date) -> tuple[dict, bytes]:
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "start_date": f"{d.isoformat()} 16:55:00",
        "end_date": f"{d.isoformat()} 17:01:00",
        "timezone": "America/New_York",
        "outputsize": 20,
        "format": "JSON",
    }
    response = session.get(
        TIME_SERIES_URL,
        params=params,
        headers={
            "Authorization": f"apikey {_api_key()}",
            "User-Agent": "GoldControl-XAU-NY17/1.0",
        },
        timeout=(8, 35),
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") == "error":
        raise RuntimeError(
            f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}"
        )
    return payload, response.content


def _extract_exact_bar(payload: dict, d: date) -> dict | None:
    values = payload.get("values") or []
    matches = []
    for item in values:
        raw_dt = str(item.get("datetime") or "")
        dt = pd.to_datetime(raw_dt, errors="coerce")
        if pd.isna(dt):
            continue
        if dt.date() == d and dt.time().replace(microsecond=0) == TARGET_BAR:
            matches.append(item)
    if not matches:
        return None
    if len(matches) != 1:
        raise RuntimeError(f"TWELVE_NY1659_BAR_NOT_UNIQUE:{d.isoformat()}:{len(matches)}")

    bar = matches[0]
    parsed = {}
    for field in ("open", "high", "low", "close"):
        value = pd.to_numeric(bar.get(field), errors="coerce")
        if pd.isna(value) or not float(value) > 0:
            raise RuntimeError(f"TWELVE_INVALID_{field.upper()}:{d.isoformat()}")
        parsed[field] = float(value)

    if parsed["low"] > parsed["high"]:
        raise RuntimeError(f"TWELVE_INVALID_HIGH_LOW:{d.isoformat()}")
    if not (parsed["low"] <= parsed["open"] <= parsed["high"]):
        raise RuntimeError(f"TWELVE_OPEN_OUTSIDE_RANGE:{d.isoformat()}")
    if not (parsed["low"] <= parsed["close"] <= parsed["high"]):
        raise RuntimeError(f"TWELVE_CLOSE_OUTSIDE_RANGE:{d.isoformat()}")
    return {"item": bar, **parsed}


def collect_latest_completed(now_utc: datetime | None = None) -> dict:
    retrieved_at = now_utc or datetime.now(timezone.utc)
    if retrieved_at.tzinfo is None:
        retrieved_at = retrieved_at.replace(tzinfo=timezone.utc)
    else:
        retrieved_at = retrieved_at.astimezone(timezone.utc)
    now_ny = retrieved_at.astimezone(NY)

    session = base.session()
    selected = None
    attempts = []
    for d in _candidate_dates(now_ny):
        # Skip obvious weekend dates without making unnecessary vendor calls.
        if d.weekday() >= 5:
            continue
        try:
            payload, raw = _request_day(session, d)
            bar = _extract_exact_bar(payload, d)
            attempts.append({"date": d.isoformat(), "result": "BAR_FOUND" if bar else "NO_EXACT_BAR"})
            if bar is not None:
                selected = (d, payload, raw, bar)
                break
        except requests.HTTPError as exc:
            attempts.append({"date": d.isoformat(), "result": f"HTTP_{exc.response.status_code if exc.response else 'ERROR'}"})
            continue
        except RuntimeError as exc:
            # Provider/API errors and invalid exact bars are not silently bypassed once a bar exists.
            if str(exc).startswith("TWELVE_API_ERROR"):
                raise
            attempts.append({"date": d.isoformat(), "result": str(exc).split(":", 1)[0]})
            if "NOT_UNIQUE" in str(exc) or "INVALID_" in str(exc) or "OUTSIDE_RANGE" in str(exc):
                raise
            continue

    if selected is None:
        raise RuntimeError("BLOCKED_NO_VALID_TWELVE_NY1659_BAR")

    trade_date, payload, raw, bar = selected
    meta = payload.get("meta") or {}
    provider_symbol = meta.get("symbol") or SYMBOL
    if provider_symbol != SYMBOL:
        raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{provider_symbol}")
    provider_interval = meta.get("interval")
    if provider_interval not in (None, INTERVAL):
        raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{provider_interval}")

    cutoff_ny = datetime.combine(trade_date, CUTOFF, tzinfo=NY)
    cutoff_utc = cutoff_ny.astimezone(timezone.utc)
    if cutoff_utc > retrieved_at:
        raise RuntimeError("BLOCKED_SESSION_NOT_COMPLETED")

    run_id = str(base.uuid.uuid4())
    payload_hash = base.sha256_bytes(raw)
    observation = base.make_obs(
        run_id,
        SERIES_ID,
        cutoff_utc,
        bar["close"],
        SOURCE,
        SYMBOL,
        "trade_date_daily",
        "USD/troy_oz",
        retrieved_at,
        provider_as_of=cutoff_utc,
        available_as_of=retrieved_at,
        status=QUALITY_STATUS,
        payload_hash=payload_hash,
        metadata={
            "endpoint": TIME_SERIES_URL,
            "vendor_symbol": SYMBOL,
            "provider_interval": INTERVAL,
            "requested_timezone": "America/New_York",
            "trade_date": trade_date.isoformat(),
            "session_definition_authority": "CME Group / EBS Market",
            "trade_date_boundary": "17:00 ET",
            "source_bar_open_time": f"{trade_date.isoformat()} 16:59:00 America/New_York",
            "price_field": "close",
            "price_semantic": "end_of_16_59_minute_bar_internal_17ET_decision_reference",
            "availability_policy": "retrieval_time_floor",
            "rights_policy": "PRIVATE_INTERNAL_NON_DISPLAY_NO_PUBLIC_RAW_REDISTRIBUTION",
            "fallback_policy": "NONE",
            "candidate_attempts": attempts,
        },
    )

    return {
        "run_id": run_id,
        "started_at": base.iso_utc(retrieved_at),
        "finished_at": base.iso_utc(datetime.now(timezone.utc)),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "daily:twelve_xau_ny17",
        "observations": [asdict(observation)],
        "vintages": [],
        "quality_events": [],
        "selected_trade_date": trade_date.isoformat(),
        "selected_cutoff_utc": cutoff_utc.isoformat(),
    }


def _self_test() -> None:
    # DST-safe cutoff mapping checks.
    winter = datetime(2026, 1, 5, 17, 0, tzinfo=NY).astimezone(timezone.utc)
    summer = datetime(2026, 8, 31, 17, 0, tzinfo=NY).astimezone(timezone.utc)
    assert winter.hour == 22
    assert summer.hour == 21

    payload = {
        "values": [
            {"datetime": "2026-08-31 16:59:00", "open": "1", "high": "2", "low": "0.5", "close": "1.5"}
        ]
    }
    bar = _extract_exact_bar(payload, date(2026, 8, 31))
    assert bar is not None and bar["close"] == 1.5
    assert _extract_exact_bar({"values": []}, date(2026, 8, 31)) is None
    print("TWELVE_XAU_NY17_SELF_TEST_PASS")


def _verify_neon(run_id: str, expected_ts: str) -> dict:
    import psycopg
    from persist_neon import _db_url

    with psycopg.connect(_db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select source, source_symbol, quality_status, observation_ts
                from canonical_latest
                where series_id=%s
                order by observation_ts desc
                limit 1
                """,
                (SERIES_ID,),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("NEON_VERIFY_NO_CANONICAL_XAU_NY17_ROW")
            source, symbol, quality, obs_ts = row
            if source != SOURCE or symbol != SYMBOL or quality != QUALITY_STATUS:
                raise RuntimeError("NEON_VERIFY_LINEAGE_OR_QUALITY_MISMATCH")
            if obs_ts.isoformat() != expected_ts:
                raise RuntimeError(f"NEON_VERIFY_TIMESTAMP_MISMATCH:{obs_ts.isoformat()}:{expected_ts}")

            cur.execute("select status from retrieval_runs where run_id=%s", (run_id,))
            rr = cur.fetchone()
            if rr is None or rr[0] != "SUCCESS":
                raise RuntimeError("NEON_VERIFY_RETRIEVAL_RUN_NOT_SUCCESS")

    return {
        "series_id": SERIES_ID,
        "latest_observation_ts": expected_ts,
        "source": SOURCE,
        "quality_status": QUALITY_STATUS,
        "retrieval_run_status": "SUCCESS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        if not args.persist:
            return 0

    bundle = collect_latest_completed()
    print(json.dumps({
        "series_id": SERIES_ID,
        "run_id": bundle["run_id"],
        "selected_trade_date": bundle["selected_trade_date"],
        "selected_cutoff_utc": bundle["selected_cutoff_utc"],
        "raw_market_values_logged": False,
        "database_write_requested": bool(args.persist),
    }, indent=2))

    if args.persist:
        result = persist_bundle(bundle)
        verified = _verify_neon(bundle["run_id"], bundle["selected_cutoff_utc"])
        print(json.dumps({"persist": result, "verify": verified}, indent=2))
        if result.get("status") != "SUCCESS":
            return 1
        print("TWELVE_XAU_NY17_PIPELINE_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
