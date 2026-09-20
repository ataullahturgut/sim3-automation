from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

API_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
INTERVAL = "1h"
TZ_NAME = "America/New_York"
NY = ZoneInfo(TZ_NAME)

START_LOCAL = datetime(2022, 2, 21, 0, 0, 0, tzinfo=NY)
END_EXCLUSIVE_LOCAL = datetime(2026, 1, 1, 0, 0, 0, tzinfo=NY)
CHUNK_DAYS = 35
OUTPUTSIZE = 1000
PACING_SECONDS = 8.5
MAX_ATTEMPTS = 4
OUT_DIR = Path("realp_hourly_research_artifact_v1")


def chunk_iter():
    start = START_LOCAL
    while start < END_EXCLUSIVE_LOCAL:
        end = min(start + timedelta(days=CHUNK_DAYS), END_EXCLUSIVE_LOCAL)
        yield start, end
        start = end


def request_chunk(session: requests.Session, api_key: str, start_dt: datetime, end_dt: datetime):
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "start_date": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": (end_dt - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": TZ_NAME,
        "order": "ASC",
        "outputsize": OUTPUTSIZE,
        "format": "JSON",
    }
    last = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.get(
                API_URL,
                params=params,
                headers={
                    "Authorization": f"apikey {api_key}",
                    "User-Agent": "GoldControl-RealP-Research/1.0",
                },
                timeout=(10, 90),
            )
            raw = response.content
            payload = response.json()
            if isinstance(payload, dict) and payload.get("status") == "error":
                code = str(payload.get("code") or "")
                msg = str(payload.get("message") or "")
                if attempt < MAX_ATTEMPTS and (
                    code in {"429", "4290"} or "credit" in msg.lower() or "rate" in msg.lower()
                ):
                    time.sleep(61)
                    continue
                raise RuntimeError(f"TWELVE_ERROR:{code}:{msg[:180]}")
            response.raise_for_status()
            values = payload.get("values") if isinstance(payload, dict) else None
            if not isinstance(values, list) or not values:
                raise RuntimeError("NO_VALUES")
            if len(values) >= OUTPUTSIZE:
                raise RuntimeError(f"POSSIBLE_TRUNCATION:{len(values)}")
            meta = payload.get("meta") or {}
            sym = str(meta.get("symbol") or SYMBOL).upper().replace(" ", "")
            if sym not in {"XAU/USD", "XAUUSD"}:
                raise RuntimeError(f"SYMBOL_MISMATCH:{meta.get('symbol')}")
            if meta.get("interval") not in (None, "", INTERVAL):
                raise RuntimeError(f"INTERVAL_MISMATCH:{meta.get('interval')}")
            return values, hashlib.sha256(raw).hexdigest(), len(raw)
        except Exception as exc:
            last = exc
            if attempt >= MAX_ATTEMPTS:
                raise
            time.sleep(5 * attempt)
    raise RuntimeError(str(last))


def parse_bar(row):
    raw_dt = str(row.get("datetime") or "")
    dt = datetime.fromisoformat(raw_dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=NY)
    else:
        dt = dt.astimezone(NY)

    vals = {}
    for f in ("open", "high", "low", "close"):
        v = float(row[f])
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"INVALID_{f.upper()}:{raw_dt}")
        vals[f] = v
    if vals["low"] > vals["high"]:
        raise ValueError(f"INVALID_HIGH_LOW:{raw_dt}")
    if not (vals["low"] <= vals["open"] <= vals["high"]):
        raise ValueError(f"OPEN_OUTSIDE_RANGE:{raw_dt}")
    if not (vals["low"] <= vals["close"] <= vals["high"]):
        raise ValueError(f"CLOSE_OUTSIDE_RANGE:{raw_dt}")
    return dt, vals


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def main():
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("TWELVE_DATA_API_KEY_MISSING")

    session = requests.Session()
    all_bars = {}
    chunk_audit = []
    chunks = list(chunk_iter())

    for idx, (start, end) in enumerate(chunks):
        values, payload_hash, byte_count = request_chunk(session, api_key, start, end)
        accepted = 0
        for row in values:
            dt, vals = parse_bar(row)
            key = dt.isoformat()
            old = all_bars.get(key)
            if old is not None and old != vals:
                raise RuntimeError(f"DUPLICATE_TIMESTAMP_CONFLICT:{key}")
            all_bars[key] = vals
            accepted += 1

        chunk_audit.append(
            {
                "chunk_start": start.isoformat(),
                "chunk_end_exclusive": end.isoformat(),
                "provider_rows": len(values),
                "accepted_rows": accepted,
                "payload_sha256": payload_hash,
                "byte_count": byte_count,
            }
        )
        print(
            json.dumps(
                {
                    "chunk": idx + 1,
                    "chunks_total": len(chunks),
                    "accepted_rows": accepted,
                    "payload_sha256": payload_hash,
                    "raw_market_values_logged": False,
                },
                sort_keys=True,
            )
        )
        if idx + 1 < len(chunks):
            time.sleep(PACING_SECONDS)

    parsed = [(datetime.fromisoformat(k), v) for k, v in all_bars.items()]
    parsed.sort(key=lambda x: x[0])
    if not parsed:
        raise RuntimeError("NO_PARSED_BARS")

    # Exact governed weekly close-anchor rule inherited from B-CARS:
    # last observed 16:00 New-York weekday bar in each Monday-start week.
    close_candidates = defaultdict(list)
    for dt, vals in parsed:
        if dt.weekday() < 5 and dt.strftime("%H:%M:%S") == "16:00:00":
            close_candidates[monday(dt.date())].append((dt, vals["close"]))

    anchors = []
    for week, cand in sorted(close_candidates.items()):
        dt, close = max(cand, key=lambda x: x[0])
        anchors.append((week, dt, close))

    rows = []
    for i in range(1, len(anchors)):
        _, prev_dt, prev_close = anchors[i - 1]
        week, close_dt, close = anchors[i]

        interval = [
            (dt, vals["close"])
            for dt, vals in parsed
            if prev_dt < dt <= close_dt
        ]
        if not interval:
            raise RuntimeError(f"NO_INTERVAL_CLOSE_PATH:{week}")

        log_prices = [math.log(prev_close)] + [math.log(c) for _, c in interval]
        increments = [log_prices[j] - log_prices[j - 1] for j in range(1, len(log_prices))]
        cpr = sum(x for x in increments if x > 0.0)
        cnr = sum(x for x in increments if x < 0.0)
        car = cpr - cnr
        if not math.isfinite(car) or car <= 0.0:
            raise RuntimeError(f"INVALID_CAR:{week}:{car}")
        realp = cpr / car
        ret = math.log(close / prev_close)

        identity = car * (2.0 * realp - 1.0)
        identity_error = abs(ret - identity)
        telescoping_error = abs(ret - sum(increments))
        if identity_error > 1e-10 or telescoping_error > 1e-10:
            raise RuntimeError(
                f"REALP_IDENTITY_FAIL:{week}:{identity_error}:{telescoping_error}"
            )
        if (ret > 0.0) != (realp > 0.5):
            if abs(ret) > 1e-14:
                raise RuntimeError(f"DIRECTION_IDENTITY_FAIL:{week}:{ret}:{realp}")

        rows.append(
            {
                "week_start": week.isoformat(),
                "previous_close_timestamp": prev_dt.isoformat(),
                "close_timestamp": close_dt.isoformat(),
                "previous_close": f"{prev_close:.10f}",
                "weekly_close": f"{close:.10f}",
                "intraperiod_hourly_close_count": len(interval),
                "cpr": f"{cpr:.15f}",
                "cnr": f"{cnr:.15f}",
                "car": f"{car:.15f}",
                "realp": f"{realp:.15f}",
                "return_log": f"{ret:.15f}",
                "identity_abs_error": f"{identity_error:.18e}",
                "telescoping_abs_error": f"{telescoping_error:.18e}",
            }
        )

    if not rows:
        raise RuntimeError("NO_REALP_WEEKLY_ROWS")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "xau_weekly_realp_2022_2025.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)

    rp = [float(r["realp"]) for r in rows]
    summary = {
        "artifact_id": "GOLD_CONTROL_REALP_TRUE_HOURLY_CLOSE_RESEARCH_V1",
        "provider": "Twelve Data",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "timezone": TZ_NAME,
        "unique_validated_hourly_bars": len(parsed),
        "weekly_close_anchors": len(anchors),
        "weekly_realp_rows": len(rows),
        "first_week": rows[0]["week_start"],
        "last_week": rows[-1]["week_start"],
        "realp_min": min(rp),
        "realp_max": max(rp),
        "realp_boundary_count": sum(x <= 0.0 or x >= 1.0 for x in rp),
        "max_identity_abs_error": max(float(r["identity_abs_error"]) for r in rows),
        "max_telescoping_abs_error": max(float(r["telescoping_abs_error"]) for r in rows),
        "raw_hourly_payload_persisted": False,
        "weekly_derived_vendor_values_artifact": True,
        "production_database_write": "NONE",
        "chunk_payload_audit": chunk_audit,
    }
    (OUT_DIR / "realp_hourly_backfill_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "unique_validated_hourly_bars": len(parsed),
                "weekly_realp_rows": len(rows),
                "first_week": rows[0]["week_start"],
                "last_week": rows[-1]["week_start"],
                "realp_boundary_count": summary["realp_boundary_count"],
                "max_identity_abs_error": summary["max_identity_abs_error"],
                "production_database_write": "NONE",
                "raw_market_values_logged": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
