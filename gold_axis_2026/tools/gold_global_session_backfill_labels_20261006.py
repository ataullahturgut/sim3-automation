from __future__ import annotations

import calendar
import hashlib
import json
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "GLOBAL_SESSION_BACKFILL_OUT"
OUT.mkdir(exist_ok=True)

TD = "https://api.twelvedata.com/time_series"
UTC = ZoneInfo("UTC")
NY = ZoneInfo("America/New_York")
LON = ZoneInfo("Europe/London")
SHA = ZoneInfo("Asia/Shanghai")
IST = ZoneInfo("Europe/Istanbul")

FETCH_START = date(2022, 12, 30)
FETCH_END = date(2026, 1, 2)
LABEL_START = date(2023, 1, 1)
LABEL_END = date(2025, 12, 31)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def month_chunks(start: date, end: date):
    cur = date(start.year, start.month, 1)
    out = []
    while cur <= end:
        last = date(cur.year, cur.month, calendar.monthrange(cur.year, cur.month)[1])
        a = max(cur, start)
        b = min(last, end)
        out.append((a, b))
        cur = last + timedelta(days=1)
    return out


def fetch_chunk(a: date, b: date, key: str):
    params = {
        "symbol": "XAU/USD",
        "interval": "15min",
        "timezone": "UTC",
        "order": "ASC",
        "outputsize": 5000,
        "apikey": key,
        "start_date": f"{a.isoformat()} 00:00:00",
        "end_date": f"{b.isoformat()} 23:59:59",
    }
    last_error = None
    for attempt in range(1, 5):
        r = requests.get(TD, params=params, timeout=90)
        try:
            j = r.json()
        except Exception:
            j = {"raw": r.text[:1000]}
        vals = j.get("values") if isinstance(j, dict) else None
        if r.ok and vals:
            rows = []
            for z in vals:
                rows.append(
                    {
                        "dt_utc": pd.Timestamp(z["datetime"], tz="UTC"),
                        "open": float(z["open"]),
                        "high": float(z["high"]),
                        "low": float(z["low"]),
                        "close": float(z["close"]),
                        "volume": None if z.get("volume") in (None, "") else float(z["volume"]),
                    }
                )
            meta = {
                "start": a.isoformat(),
                "end": b.isoformat(),
                "http": r.status_code,
                "rows": len(rows),
                "response_meta": j.get("meta"),
                "attempt": attempt,
            }
            return pd.DataFrame(rows), meta
        last_error = {
            "start": a.isoformat(),
            "end": b.isoformat(),
            "http": r.status_code,
            "response": j,
            "attempt": attempt,
        }
        time.sleep(30 * attempt)
    raise RuntimeError(json.dumps(last_error, default=str))


def aware_local(d: date, hh: int, mm: int, tz: ZoneInfo) -> pd.Timestamp:
    return pd.Timestamp(datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz))


def utc_ts(d: date, hh: int, mm: int) -> pd.Timestamp:
    return aware_local(d, hh, mm, UTC)


def ny_ts(d: date, hh: int, mm: int) -> pd.Timestamp:
    return aware_local(d, hh, mm, NY)


def local_text(ts: pd.Timestamp, tz: ZoneInfo) -> str:
    return ts.tz_convert(tz).isoformat()


def offset_hours(ts: pd.Timestamp, tz: ZoneInfo) -> float:
    x = ts.tz_convert(tz).utcoffset()
    return float(x.total_seconds() / 3600.0)


def build_raw(key: str):
    parts = []
    requests_meta = []
    for a, b in month_chunks(FETCH_START, FETCH_END):
        q, m = fetch_chunk(a, b, key)
        parts.append(q)
        requests_meta.append(m)
        time.sleep(8)
    x = pd.concat(parts, ignore_index=True)
    duplicate_count = int(x.duplicated("dt_utc").sum())
    x = x.sort_values("dt_utc").drop_duplicates("dt_utc", keep="last").reset_index(drop=True)

    x["dt_ny"] = x["dt_utc"].dt.tz_convert("America/New_York")
    x["dt_london"] = x["dt_utc"].dt.tz_convert("Europe/London")
    x["dt_shanghai"] = x["dt_utc"].dt.tz_convert("Asia/Shanghai")
    x["dt_istanbul"] = x["dt_utc"].dt.tz_convert("Europe/Istanbul")

    minute_mod_ok = bool(((x["dt_utc"].dt.minute % 15) == 0).all())
    ohlc_ok = bool(
        (
            (x["high"] >= x[["open", "close"]].max(axis=1))
            & (x["low"] <= x[["open", "close"]].min(axis=1))
            & (x[["open", "high", "low", "close"]] > 0).all(axis=1)
        ).all()
    )

    integrity = {
        "raw_rows": int(len(x)),
        "duplicate_dt_utc_before_dedup": duplicate_count,
        "first_utc": str(x["dt_utc"].min()),
        "last_utc": str(x["dt_utc"].max()),
        "all_timestamps_on_15min_grid": minute_mod_ok,
        "ohlc_internal_consistency": ohlc_ok,
        "request_chunks": requests_meta,
    }
    return x, integrity


def price_map(x: pd.DataFrame):
    return {
        pd.Timestamp(r.dt_utc): {
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "close": float(r.close),
        }
        for r in x.itertuples(index=False)
    }


def direction(ret):
    if ret is None or pd.isna(ret):
        return None
    if ret > 0:
        return "UP"
    if ret < 0:
        return "DOWN"
    return "FLAT"


def label_row(pm, label_date: date, partition: str, window: str, start: pd.Timestamp, end: pd.Timestamp):
    s = start.tz_convert("UTC")
    e = end.tz_convert("UTC")
    ps = pm.get(s)
    pe = pm.get(e)
    missing = []
    if ps is None:
        missing.append("START")
    if pe is None:
        missing.append("END")
    if missing:
        ret = None
        p0 = p1 = None
    else:
        p0 = ps["open"]
        p1 = pe["open"]
        ret = p1 / p0 - 1.0

    return {
        "label_date": label_date.isoformat(),
        "year": label_date.year,
        "partition": partition,
        "window": window,
        "start_utc": s.isoformat(),
        "end_utc": e.isoformat(),
        "start_ny": local_text(s, NY),
        "end_ny": local_text(e, NY),
        "start_london": local_text(s, LON),
        "end_london": local_text(e, LON),
        "start_shanghai": local_text(s, SHA),
        "end_shanghai": local_text(e, SHA),
        "start_istanbul": local_text(s, IST),
        "end_istanbul": local_text(e, IST),
        "ny_utc_offset_start_h": offset_hours(s, NY),
        "london_utc_offset_start_h": offset_hours(s, LON),
        "shanghai_utc_offset_start_h": offset_hours(s, SHA),
        "istanbul_utc_offset_start_h": offset_hours(s, IST),
        "start_open": p0,
        "end_open": p1,
        "return": ret,
        "direction": direction(ret),
        "coverage": "PASS" if not missing else "MISSING_BOUNDARY",
        "missing_boundary": "|".join(missing) if missing else "",
    }


def build_labels(x: pd.DataFrame):
    pm = price_map(x)
    wgc = []
    sobti = []
    d = LABEL_START
    while d <= LABEL_END:
        prev = d - timedelta(days=1)

        # Partition A: modern WGC-3, fixed UTC.
        wgc.append(label_row(pm, d, "MODERN_WGC_3", "ASIA", utc_ts(prev, 22, 0), utc_ts(d, 7, 0)))
        wgc.append(label_row(pm, d, "MODERN_WGC_3", "EUROPE", utc_ts(d, 7, 0), utc_ts(d, 12, 0)))
        wgc.append(label_row(pm, d, "MODERN_WGC_3", "US", utc_ts(d, 12, 0), utc_ts(d, 21, 0)))

        # Partition B: Sobti 5-zone ET replication. One 24h cycle is indexed by date d.
        sobti.append(label_row(pm, d, "SOBTI_5_ET", "ASIA_MORNING_LIT", ny_ts(prev, 21, 0), ny_ts(prev, 23, 30)))
        sobti.append(label_row(pm, d, "SOBTI_5_ET", "ASIA_AFTERNOON_LIT", ny_ts(d, 1, 30), ny_ts(d, 3, 30)))
        sobti.append(label_row(pm, d, "SOBTI_5_ET", "EUROPE_LIT", ny_ts(d, 3, 30), ny_ts(d, 8, 0)))
        sobti.append(label_row(pm, d, "SOBTI_5_ET", "NY_LONDON_LIT", ny_ts(d, 8, 0), ny_ts(d, 14, 30)))
        sobti.append(label_row(pm, d, "SOBTI_5_ET", "US_LATE_LIT", ny_ts(d, 14, 30), ny_ts(d, 21, 0)))

        d += timedelta(days=1)

    return pd.DataFrame(wgc), pd.DataFrame(sobti)


def coverage_summary(df: pd.DataFrame):
    out = {}
    for (yr, win), g in df.groupby(["year", "window"], sort=True):
        k = f"{yr}_{win}"
        good = g[g["coverage"] == "PASS"]
        out[k] = {
            "calendar_rows": int(len(g)),
            "pass": int(len(good)),
            "missing": int((g["coverage"] != "PASS").sum()),
            "up": int((good["direction"] == "UP").sum()),
            "down": int((good["direction"] == "DOWN").sum()),
            "flat": int((good["direction"] == "FLAT").sum()),
        }
    return out


def build_dst_audit():
    rows = []
    zones = {
        "America/New_York": NY,
        "Europe/London": LON,
        "Asia/Shanghai": SHA,
        "Europe/Istanbul": IST,
    }

    # Detect offset changes at local noon for 2023-2025, then include +/- 3 days around each change.
    event_dates = set()
    for zname, z in zones.items():
        prev_off = None
        d = LABEL_START
        while d <= LABEL_END:
            ts = aware_local(d, 12, 0, z)
            off = ts.utcoffset()
            if prev_off is not None and off != prev_off:
                for delta in range(-3, 4):
                    dd = d + timedelta(days=delta)
                    if LABEL_START <= dd <= LABEL_END:
                        event_dates.add(dd)
            prev_off = off
            d += timedelta(days=1)

    # Add normal winter/summer controls for every year.
    for yr in [2023, 2024, 2025]:
        event_dates.add(date(yr, 1, 15))
        event_dates.add(date(yr, 7, 15))

    for d in sorted(event_dates):
        # Use key Sobti boundaries to expose NY-driven UTC movement.
        for name, ts in [
            ("NY_03_30", ny_ts(d, 3, 30)),
            ("NY_08_00", ny_ts(d, 8, 0)),
            ("NY_14_30", ny_ts(d, 14, 30)),
            ("NY_21_00", ny_ts(d, 21, 0)),
            ("WGC_07_UTC", utc_ts(d, 7, 0)),
            ("WGC_12_UTC", utc_ts(d, 12, 0)),
            ("WGC_21_UTC", utc_ts(d, 21, 0)),
        ]:
            u = ts.tz_convert("UTC")
            rows.append(
                {
                    "date": d.isoformat(),
                    "marker": name,
                    "utc": u.isoformat(),
                    "new_york": local_text(u, NY),
                    "london": local_text(u, LON),
                    "shanghai": local_text(u, SHA),
                    "istanbul": local_text(u, IST),
                    "ny_offset_h": offset_hours(u, NY),
                    "london_offset_h": offset_hours(u, LON),
                    "shanghai_offset_h": offset_hours(u, SHA),
                    "istanbul_offset_h": offset_hours(u, IST),
                }
            )
    return pd.DataFrame(rows)


def build_sge_telemetry_dates():
    # Date-local marker table only; actual SGE holiday calendar is not silently inferred.
    rows = []
    d = LABEL_START
    while d <= LABEL_END:
        s = aware_local(d, 9, 0, SHA).tz_convert("UTC")
        e = aware_local(d, 15, 30, SHA).tz_convert("UTC")
        n0 = aware_local(d - timedelta(days=1), 20, 0, SHA).tz_convert("UTC")
        n1 = aware_local(d, 2, 30, SHA).tz_convert("UTC")
        rows.append(
            {
                "date": d.isoformat(),
                "sge_day_start_utc": s.isoformat(),
                "sge_day_end_utc": e.isoformat(),
                "sge_night_start_utc": n0.isoformat(),
                "sge_night_end_utc": n1.isoformat(),
                "holiday_status": "UNRESOLVED_REQUIRES_OFFICIAL_CALENDAR",
            }
        )
        d += timedelta(days=1)
    return pd.DataFrame(rows)


def main():
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY is missing")

    x, integrity = build_raw(key)
    wgc, sobti = build_labels(x)
    dst = build_dst_audit()
    sge = build_sge_telemetry_dates()

    raw_path = OUT / "xauusd_15m_utc_2023_2025_with_buffer.csv"
    wgc_path = OUT / "labels_wgc3_2023_2025.csv"
    sobti_path = OUT / "labels_sobti5_2023_2025.csv"
    dst_path = OUT / "dst_audit_2023_2025.csv"
    sge_path = OUT / "sge_clock_markers_2023_2025.csv"

    x_out = x.copy()
    for c in ["dt_utc", "dt_ny", "dt_london", "dt_shanghai", "dt_istanbul"]:
        x_out[c] = x_out[c].astype(str)
    x_out.to_csv(raw_path, index=False)
    wgc.to_csv(wgc_path, index=False)
    sobti.to_csv(sobti_path, index=False)
    dst.to_csv(dst_path, index=False)
    sge.to_csv(sge_path, index=False)

    hashes = {
        raw_path.name: sha256_file(raw_path),
        wgc_path.name: sha256_file(wgc_path),
        sobti_path.name: sha256_file(sobti_path),
        dst_path.name: sha256_file(dst_path),
        sge_path.name: sha256_file(sge_path),
    }

    summary = {
        "status": "SESSION_CLOCK_BACKFILL_AND_LABEL_GATE",
        "clock_contract": "CORRECTED_DUAL_EXTERNAL_PARTITION",
        "fetch_window_utc": [FETCH_START.isoformat(), FETCH_END.isoformat()],
        "label_window": [LABEL_START.isoformat(), LABEL_END.isoformat()],
        "raw_integrity": integrity,
        "coverage": {
            "MODERN_WGC_3": coverage_summary(wgc),
            "SOBTI_5_ET": coverage_summary(sobti),
        },
        "hashes_sha256": hashes,
        "rules": {
            "raw_timezone": "UTC",
            "bar_timestamp_semantics": "BAR_OPEN",
            "boundary_matching": "EXACT_ONLY_NO_FILL",
            "wgc3": {
                "ASIA": "22:00 previous UTC date -> 07:00 label UTC date",
                "EUROPE": "07:00 -> 12:00 UTC",
                "US": "12:00 -> 21:00 UTC",
            },
            "sobti5": {
                "ASIA_MORNING_LIT": "21:00 -> 23:30 America/New_York on prior calendar date",
                "ASIA_AFTERNOON_LIT": "01:30 -> 03:30 America/New_York",
                "EUROPE_LIT": "03:30 -> 08:00 America/New_York",
                "NY_LONDON_LIT": "08:00 -> 14:30 America/New_York",
                "US_LATE_LIT": "14:30 -> 21:00 America/New_York",
            },
            "modern_sge_day": "09:00-15:30 Asia/Shanghai; venue-state telemetry, not target partition",
        },
        "guardrail": "No 2026 direction result was used to choose or move any clock boundary.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    md = []
    md.append("# GOLD SESSION CLOCK BACKFILL / LABEL GATE — 2026-10-06")
    md.append("")
    md.append(f"- Raw rows: **{integrity['raw_rows']:,}**")
    md.append(f"- Raw UTC range: **{integrity['first_utc']} → {integrity['last_utc']}**")
    md.append(f"- 15-minute grid: **{'PASS' if integrity['all_timestamps_on_15min_grid'] else 'FAIL'}**")
    md.append(f"- OHLC consistency: **{'PASS' if integrity['ohlc_internal_consistency'] else 'FAIL'}**")
    md.append("- Boundary matching: **exact bar-open only; no fill**")
    md.append("- Partitions: **MODERN_WGC_3 + SOBTI_5_ET**")
    md.append("- Modern SGE 09:00–15:30 Shanghai is telemetry/venue state, not a silently substituted target.")
    md.append("")
    md.append("## Hashes")
    for k, v in hashes.items():
        md.append(f"- `{k}`: `{v}`")
    (OUT / "result.md").write_text("\n".join(md) + "\n")

    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
