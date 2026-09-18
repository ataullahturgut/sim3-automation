from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

API_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
INTERVAL = "1h"
TZ_NAME = "America/New_York"
NY = ZoneInfo(TZ_NAME)
START_MONTH = (2022, 2)
END_MONTH = (2025, 12)
OUTPUTSIZE = 1000
PACING_SECONDS = 8.5
MAX_ATTEMPTS = 4
OUT_DIR = Path("bcars_ohlc_research_artifact_v1")


def month_iter(start, end):
    y, m = start
    ey, em = end
    while (y, m) <= (ey, em):
        yield y, m
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1


def next_month(y, m):
    return (y + 1, 1) if m == 12 else (y, m + 1)


def request_month(session: requests.Session, api_key: str, y: int, m: int):
    ny, nm = next_month(y, m)
    start = f"{y:04d}-{m:02d}-01 00:00:00"
    end = f"{ny:04d}-{nm:02d}-01 00:00:00"
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "start_date": start,
        "end_date": end,
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
                    "User-Agent": "GoldControl-BCARS-OHLC-Research/1.0",
                },
                timeout=(10, 90),
            )
            raw = response.content
            try:
                payload = response.json()
            except Exception as exc:
                raise RuntimeError(f"NON_JSON:{response.status_code}") from exc

            if isinstance(payload, dict) and payload.get("status") == "error":
                code = str(payload.get("code") or "")
                msg = str(payload.get("message") or "")
                if attempt < MAX_ATTEMPTS and (
                    code in {"429", "4290"} or "credit" in msg.lower() or "rate" in msg.lower()
                ):
                    time.sleep(61)
                    continue
                raise RuntimeError(f"TWELVE_ERROR:{code}:{msg[:160]}")

            response.raise_for_status()
            values = payload.get("values") if isinstance(payload, dict) else None
            if not isinstance(values, list) or not values:
                raise RuntimeError("NO_VALUES")
            if len(values) >= OUTPUTSIZE:
                raise RuntimeError(f"POSSIBLE_TRUNCATION:{len(values)}")

            meta = payload.get("meta") or {}
            if str(meta.get("symbol") or SYMBOL).upper().replace(" ", "") not in {"XAU/USD", "XAUUSD"}:
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


def monday(d):
    return d.fromordinal(d.toordinal() - d.weekday())


def main():
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise SystemExit("TWELVE_DATA_API_KEY_MISSING")

    session = requests.Session()
    all_bars = {}
    month_audit = []

    months = list(month_iter(START_MONTH, END_MONTH))
    for idx, (y, m) in enumerate(months):
        values, payload_hash, byte_count = request_month(session, key, y, m)
        accepted = 0
        for row in values:
            dt, vals = parse_bar(row)
            k = dt.isoformat()
            old = all_bars.get(k)
            if old is not None and old != vals:
                raise RuntimeError(f"DUPLICATE_TIMESTAMP_CONFLICT:{k}")
            all_bars[k] = vals
            accepted += 1

        month_audit.append({
            "month": f"{y:04d}-{m:02d}",
            "provider_rows": len(values),
            "accepted_rows": accepted,
            "payload_sha256": payload_hash,
            "byte_count": byte_count,
        })
        print(json.dumps({
            "month": f"{y:04d}-{m:02d}",
            "accepted_rows": accepted,
            "payload_sha256": payload_hash,
            "raw_market_values_logged": False,
        }, sort_keys=True))
        if idx + 1 < len(months):
            time.sleep(PACING_SECONDS)

    parsed = []
    for k, vals in all_bars.items():
        parsed.append((datetime.fromisoformat(k), vals))
    parsed.sort(key=lambda x: x[0])
    if not parsed:
        raise RuntimeError("NO_PARSED_BARS")

    # Eligible weekly close anchors are exact 16:00 provider bars on weekdays.
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
        prev_week, prev_dt, prev_close = anchors[i - 1]
        week, close_dt, close = anchors[i]
        interval_bars = [
            vals
            for dt, vals in parsed
            if prev_dt < dt <= close_dt
        ]
        if not interval_bars:
            raise RuntimeError(f"NO_INTERVAL_BARS:{week}")
        high = max(v["high"] for v in interval_bars)
        adjusted_high = max(high, prev_close)

        p_prev = math.log(prev_close)
        p_t = math.log(close)
        h_t = math.log(adjusted_high)
        u = h_t - p_prev
        d = h_t - p_t
        R = u + d
        if not math.isfinite(R) or R <= 0:
            raise RuntimeError(f"INVALID_R:{week}:{R}")
        ur = u / R
        lhs = p_t - p_prev
        rhs = R * (2 * ur - 1)
        identity_error = abs(lhs - rhs)
        if identity_error > 1e-10:
            raise RuntimeError(f"DECOMPOSITION_IDENTITY_FAIL:{week}:{identity_error}")

        rows.append({
            "week_start": week.isoformat(),
            "previous_close_timestamp": prev_dt.isoformat(),
            "close_timestamp": close_dt.isoformat(),
            "previous_close": f"{prev_close:.10f}",
            "weekly_high": f"{high:.10f}",
            "adjusted_high": f"{adjusted_high:.10f}",
            "weekly_close": f"{close:.10f}",
            "interval_hourly_bar_count": len(interval_bars),
            "up_ratio": f"{ur:.15f}",
            "return_log": f"{lhs:.15f}",
            "identity_abs_error": f"{identity_error:.18e}",
        })

    if not rows:
        raise RuntimeError("NO_WEEKLY_ROWS")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "xau_weekly_high_close_up_ratio_2022_2025.csv"
    fields = list(rows[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)

    ur_values = [float(r["up_ratio"]) for r in rows]
    boundary = sum(u <= 0.0 or u >= 1.0 for u in ur_values)

    summary = {
        "artifact_id": "GOLD_CONTROL_BCARS_TRUE_HOURLY_OHLC_RESEARCH_V1",
        "provider": "Twelve Data",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "timezone": TZ_NAME,
        "retrieval_months": len(months),
        "first_month": f"{months[0][0]:04d}-{months[0][1]:02d}",
        "last_month": f"{months[-1][0]:04d}-{months[-1][1]:02d}",
        "unique_hourly_bars": len(parsed),
        "weekly_close_anchors": len(anchors),
        "weekly_up_ratio_rows": len(rows),
        "first_week": rows[0]["week_start"],
        "last_week": rows[-1]["week_start"],
        "up_ratio_min": min(ur_values),
        "up_ratio_max": max(ur_values),
        "boundary_up_ratio_count": boundary,
        "max_identity_abs_error": max(float(r["identity_abs_error"]) for r in rows),
        "production_database_write": "NONE",
        "raw_hourly_payload_persisted": False,
        "weekly_derived_vendor_values_artifact": True,
        "month_payload_audit": month_audit,
    }
    (OUT_DIR / "bcars_ohlc_backfill_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        "status": "PASS",
        "weekly_up_ratio_rows": len(rows),
        "first_week": rows[0]["week_start"],
        "last_week": rows[-1]["week_start"],
        "boundary_up_ratio_count": boundary,
        "max_identity_abs_error": summary["max_identity_abs_error"],
        "production_database_write": "NONE",
        "raw_market_values_logged": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
