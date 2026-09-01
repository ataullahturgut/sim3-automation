from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime

import requests

API = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
TZ = "America/New_York"

DATES = [
    "2015-01-15",
    "2018-06-15",
    "2020-03-16",
    "2021-06-15",
    "2023-06-15",
    "2025-06-16",
    "2026-08-31",
]

OVERLAP_DATES = ["2026-06-15", "2026-07-15", "2026-08-17"]


@dataclass
class Probe:
    date: str
    interval: str
    expected_ts: str
    http_status: int | None
    api_status: str
    expected_bar_present: bool
    returned_values: int
    error_code: str | None = None


def request_values(date: str, interval: str) -> tuple[int, dict]:
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")

    if interval == "1min":
        start = f"{date} 16:50:00"
        end = f"{date} 17:05:00"
    elif interval == "1h":
        start = f"{date} 15:00:00"
        end = f"{date} 18:00:00"
    else:
        raise ValueError(interval)

    params = {
        "symbol": SYMBOL,
        "interval": interval,
        "start_date": start,
        "end_date": end,
        "timezone": TZ,
        "order": "ASC",
        "outputsize": 5000,
        "apikey": key,
    }

    for attempt in range(3):
        r = requests.get(API, params=params, timeout=30)
        if r.status_code == 429:
            if attempt == 2:
                return r.status_code, {"status": "error", "code": 429}
            time.sleep(65)
            continue
        try:
            payload = r.json()
        except Exception:
            payload = {"status": "error", "code": f"NON_JSON_HTTP_{r.status_code}"}
        return r.status_code, payload
    raise AssertionError("unreachable")


def probe(date: str, interval: str) -> tuple[Probe, float | None]:
    expected = f"{date} 16:59:00" if interval == "1min" else f"{date} 16:00:00"
    status, payload = request_values(date, interval)
    values = payload.get("values") or [] if isinstance(payload, dict) else []
    found = None
    for row in values:
        if str(row.get("datetime")) == expected:
            found = row
            break
    close = None
    if found is not None:
        try:
            close = float(found["close"])
            if close <= 0:
                close = None
        except Exception:
            close = None
    api_status = str(payload.get("status") or ("ok" if values else "unknown")) if isinstance(payload, dict) else "invalid"
    code = None if not isinstance(payload, dict) else payload.get("code")
    return (
        Probe(
            date=date,
            interval=interval,
            expected_ts=expected,
            http_status=status,
            api_status=api_status,
            expected_bar_present=close is not None,
            returned_values=len(values),
            error_code=None if code is None else str(code),
        ),
        close,
    )


def main() -> None:
    results: list[Probe] = []
    closes: dict[tuple[str, str], float] = {}

    for date in DATES:
        for interval in ("1min", "1h"):
            p, close = probe(date, interval)
            results.append(p)
            if close is not None:
                closes[(date, interval)] = close
            print(
                f"DEPTH date={date} interval={interval} http={p.http_status} "
                f"api_status={p.api_status} expected_bar={p.expected_bar_present} "
                f"n_values={p.returned_values} error_code={p.error_code or 'NONE'}"
            )
            time.sleep(5)

    depth_1m = [r.date for r in results if r.interval == "1min" and r.expected_bar_present]
    depth_1h = [r.date for r in results if r.interval == "1h" and r.expected_bar_present]
    print("ONE_MIN_AVAILABLE_DATES=" + ",".join(depth_1m))
    print("ONE_HOUR_AVAILABLE_DATES=" + ",".join(depth_1h))
    print("ONE_MIN_EARLIEST_PROVEN=" + (min(depth_1m) if depth_1m else "NOT_PROVEN"))
    print("ONE_HOUR_EARLIEST_PROVEN=" + (min(depth_1h) if depth_1h else "NOT_PROVEN"))

    # Compatibility diagnostic on recent dates. We print only derived differences,
    # never either vendor market value.
    for date in OVERLAP_DATES:
        p1, c1 = probe(date, "1min")
        time.sleep(5)
        ph, ch = probe(date, "1h")
        time.sleep(5)
        if c1 is None or ch is None:
            print(
                f"OVERLAP date={date} comparable=False one_min={c1 is not None} one_hour={ch is not None}"
            )
            continue
        abs_diff = abs(c1 - ch)
        rel_bps = abs_diff / abs(c1) * 10000.0
        print(f"OVERLAP date={date} comparable=True abs_diff_usd={abs_diff:.12f} rel_diff_bps={rel_bps:.9f}")

    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("MODEL_SCORE_RUN=NONE")
    print("SUCCESSOR_TWELVE_HISTORY_DEPTH_AUDIT_COMPLETE")


if __name__ == "__main__":
    main()
