from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from probe_historical_ny17_gaps_v145 import (  # noqa: E402
    ACCEPTED_TIME,
    FINAL_STATUSES,
    URL,
    classify_error,
)

MINUTE_LIMIT_MARKERS = (
    "current minute",
    "per minute",
    "minute limit",
    "minute quota",
    "next minute",
)
LONG_QUOTA_MARKERS = (
    "per day",
    "daily limit",
    "daily quota",
    "daily credit",
    "day limit",
    "for today",
    "today's",
    "monthly limit",
    "monthly quota",
    "plan limit",
    "subscription limit",
)


def load_inputs(paths: list[Path]) -> pd.DataFrame:
    frames = []
    for path in paths:
        d = pd.read_csv(path, dtype=str, keep_default_na=False)
        if "trade_date" not in d or "acquisition_status" not in d:
            raise RuntimeError(f"SCHEMA_MISMATCH:{path}")
        d["source_input"] = str(path)
        frames.append(d)
    out = pd.concat(frames, ignore_index=True)
    if out["trade_date"].duplicated().any():
        dup = out.loc[out["trade_date"].duplicated(False), "trade_date"].tolist()
        raise RuntimeError(f"DUPLICATE_TRADE_DATE:{dup[:20]}")
    return out.sort_values("trade_date").reset_index(drop=True)


def rate_limit_scope(result: dict[str, Any]) -> str | None:
    if result.get("acquisition_status") != "ENTITLEMENT_BLOCKED":
        return None
    text = str(result.get("provider_message") or "").lower()
    code = str(result.get("provider_code") or "")
    if any(marker in text for marker in MINUTE_LIMIT_MARKERS):
        return "MINUTE"
    if any(marker in text for marker in LONG_QUOTA_MARKERS):
        return "LONG_QUOTA"
    if code == "429" or "credit" in text or "rate limit" in text or "quota" in text:
        return "UNKNOWN_RATE_LIMIT"
    return "ENTITLEMENT"


def validate_exact_row(row: dict[str, Any]) -> dict[str, Any]:
    try:
        values = {k: float(row[k]) for k in ("open", "high", "low", "close")}
    except (KeyError, TypeError, ValueError):
        return {
            "acquisition_status": "MALFORMED_BAR",
            "provider_code": None,
            "provider_message": "OHLC parse failure",
        }
    if not all(math.isfinite(v) and v > 0 for v in values.values()):
        return {
            "acquisition_status": "MALFORMED_BAR",
            "provider_code": None,
            "provider_message": "non-positive or non-finite OHLC",
        }
    if values["high"] < max(values["open"], values["low"], values["close"]):
        return {
            "acquisition_status": "MALFORMED_BAR",
            "provider_code": None,
            "provider_message": "OHLC range invalid",
        }
    if values["low"] > min(values["open"], values["high"], values["close"]):
        return {
            "acquisition_status": "MALFORMED_BAR",
            "provider_code": None,
            "provider_message": "OHLC range invalid",
        }
    return {
        "acquisition_status": "VALID_EXACT_BAR",
        "provider_code": None,
        "provider_message": None,
        "source_bar_datetime": row["datetime"],
        **values,
    }


def request_window(
    api_key: str,
    start_date: str,
    end_date: str,
    target_dates: list[str],
) -> tuple[dict[str, dict[str, Any]], str, str]:
    params = urllib.parse.urlencode(
        {
            "symbol": "XAU/USD",
            "interval": "1min",
            "timezone": "America/New_York",
            "start_date": f"{start_date} 00:00:00",
            "end_date": f"{end_date} 23:59:59",
            "outputsize": 5000,
            "format": "JSON",
        }
    )
    request = urllib.request.Request(
        f"{URL}?{params}",
        headers={
            "Authorization": f"apikey {api_key}",
            "User-Agent": "GoldControl-GCBreak-WP1-BatchResume/3.0",
        },
    )
    retrieved_at = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"status": "error", "code": exc.code, "message": str(exc)}
    except Exception as exc:
        payload = {
            "status": "error",
            "code": None,
            "message": f"{type(exc).__name__}:{exc}",
        }
        raw = json.dumps(payload).encode()
    else:
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {
                "status": "error",
                "code": None,
                "message": "non-JSON provider response",
            }

    payload_sha256 = hashlib.sha256(raw).hexdigest()
    if payload.get("status") == "error" or "values" not in payload:
        status = classify_error(payload.get("code"), str(payload.get("message") or "missing values"))
        common = {
            "acquisition_status": status,
            "provider_code": payload.get("code"),
            "provider_message": payload.get("message"),
        }
        return {trade_date: dict(common) for trade_date in target_dates}, retrieved_at, payload_sha256

    exact_by_date: dict[str, list[dict[str, Any]]] = {trade_date: [] for trade_date in target_dates}
    for row in payload.get("values", []):
        stamp = str(row.get("datetime", ""))
        if not stamp.endswith(f" {ACCEPTED_TIME}"):
            continue
        trade_date = stamp[:10]
        if trade_date in exact_by_date:
            exact_by_date[trade_date].append(row)

    results: dict[str, dict[str, Any]] = {}
    for trade_date in target_dates:
        selected = exact_by_date[trade_date]
        if not selected:
            results[trade_date] = {
                "acquisition_status": "PROVIDER_NO_BAR",
                "provider_code": None,
                "provider_message": "exact 16:59:00 source bar absent in bounded provider payload",
            }
        elif len(selected) != 1:
            results[trade_date] = {
                "acquisition_status": "MALFORMED_BAR",
                "provider_code": None,
                "provider_message": f"duplicate exact bars: {len(selected)}",
            }
        else:
            results[trade_date] = validate_exact_row(selected[0])
    return results, retrieved_at, payload_sha256


def update_row(
    df: pd.DataFrame,
    idx: int,
    result: dict[str, Any],
    retrieved_at: str | None,
    payload_sha256: str | None,
    window_start: str,
    window_end: str,
) -> None:
    for key, value in result.items():
        if key not in df.columns:
            df[key] = ""
        df.at[idx, key] = "" if value is None else str(value)
    metadata = {
        "retrieved_at": retrieved_at,
        "payload_sha256": payload_sha256,
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1min",
        "timezone": "America/New_York",
        "accepted_source_time": ACCEPTED_TIME,
        "stored_semantic": "17:00 ET",
        "retrieval_window_start": window_start,
        "retrieval_window_end": window_end,
        "retrieval_mode": "BOUNDED_3_CALENDAR_DAY_BATCH_MAX",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "prospective_claim": "False",
    }
    for key, value in metadata.items():
        if key not in df.columns:
            df[key] = ""
        df.at[idx, key] = "" if value is None else str(value)


def unresolved_rows(df: pd.DataFrame) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for idx in df.index:
        status = str(df.at[idx, "acquisition_status"])
        if status not in FINAL_STATUSES:
            out.append((int(idx), str(df.at[idx, "trade_date"])))
    return out


def make_windows(rows: list[tuple[int, str]], window_days: int) -> list[list[tuple[int, str]]]:
    windows: list[list[tuple[int, str]]] = []
    pos = 0
    while pos < len(rows):
        start = date.fromisoformat(rows[pos][1])
        end = start + timedelta(days=window_days - 1)
        batch: list[tuple[int, str]] = []
        while pos < len(rows) and date.fromisoformat(rows[pos][1]) <= end:
            batch.append(rows[pos])
            pos += 1
        windows.append(batch)
    return windows


def write_checkpoint(
    df: pd.DataFrame,
    output_dir: Path,
    initial: Counter,
    attempted_windows: int,
    rate_limit_sleeps: int,
    quota_abort: bool,
    quota_scope: str | None,
    last_window: str | None,
) -> dict[str, Any]:
    final = Counter(df["acquisition_status"])
    unresolved = int(sum(n for status, n in final.items() if status not in FINAL_STATUSES))
    csv_path = output_dir / "gc_break_wp1_exact_ny17_consolidated_batch_v3.csv"
    df.to_csv(csv_path, index=False)
    summary = {
        "audit_id": "GC_BREAK_WP1_EXACT_NY17_BATCH_RESUME_V3",
        "source_semantic": "Twelve Data XAU/USD 1min exact 16:59:00 America/New_York; bounded <=3-calendar-day transport batches; no fallback/interpolation",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "initial_status_counts": dict(initial),
        "final_status_counts": dict(final),
        "rows": int(len(df)),
        "attempted_windows": attempted_windows,
        "rate_limit_backoff_count": rate_limit_sleeps,
        "unresolved_count": unresolved,
        "quota_abort": quota_abort,
        "quota_scope": quota_scope,
        "last_window": last_window,
        "production_database_write": "NONE",
        "performance_scoring": False,
        "prospective_claim": False,
    }
    (output_dir / "gc_break_wp1_exact_ny17_batch_resume_v3_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-csv", action="append", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--window-days", type=int, default=3, choices=(1, 2, 3))
    parser.add_argument("--pacing-seconds", type=float, default=8.5)
    parser.add_argument("--backoff-seconds", type=float, default=70.0)
    parser.add_argument("--max-minute-rate-limit-retries", type=int, default=8)
    parser.add_argument("--max-unknown-rate-limit-retries", type=int, default=1)
    parser.add_argument("--max-transient-retries", type=int, default=2)
    parser.add_argument("--checkpoint-every-windows", type=int, default=10)
    args = parser.parse_args()

    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("BLOCKED_DATA:TWELVE_DATA_API_KEY_NOT_SET")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = load_inputs(args.probe_csv)
    initial = Counter(df["acquisition_status"])
    windows = make_windows(unresolved_rows(df), args.window_days)
    attempted_windows = 0
    rate_limit_sleeps = 0
    quota_abort = False
    quota_scope: str | None = None
    last_window: str | None = None

    for window_number, batch in enumerate(windows, start=1):
        target_dates = [trade_date for _, trade_date in batch]
        start_date = target_dates[0]
        end_date = (date.fromisoformat(start_date) + timedelta(days=args.window_days - 1)).isoformat()
        last_window = f"{start_date}..{end_date}"
        minute_retries = 0
        unknown_retries = 0
        transient_retries = 0

        while True:
            results, retrieved_at, payload_sha256 = request_window(
                api_key=api_key,
                start_date=start_date,
                end_date=end_date,
                target_dates=target_dates,
            )
            attempted_windows += 1
            sample = results[target_dates[0]]
            scope = rate_limit_scope(sample)

            if scope == "MINUTE" and minute_retries < args.max_minute_rate_limit_retries:
                minute_retries += 1
                rate_limit_sleeps += 1
                print(json.dumps({"window": last_window, "status": "MINUTE_RATE_LIMIT_BACKOFF", "retry": minute_retries}), flush=True)
                time.sleep(args.backoff_seconds)
                continue
            if scope == "UNKNOWN_RATE_LIMIT" and unknown_retries < args.max_unknown_rate_limit_retries:
                unknown_retries += 1
                rate_limit_sleeps += 1
                print(json.dumps({"window": last_window, "status": "UNKNOWN_RATE_LIMIT_BACKOFF", "retry": unknown_retries}), flush=True)
                time.sleep(args.backoff_seconds)
                continue
            if sample.get("acquisition_status") in {"SERVER_ERROR", "REQUEST_ERROR"} and transient_retries < args.max_transient_retries:
                transient_retries += 1
                time.sleep(min(30.0, 5.0 * transient_retries))
                continue

            for idx, trade_date in batch:
                update_row(
                    df=df,
                    idx=idx,
                    result=results[trade_date],
                    retrieved_at=retrieved_at,
                    payload_sha256=payload_sha256,
                    window_start=start_date,
                    window_end=end_date,
                )

            if scope in {"LONG_QUOTA", "ENTITLEMENT"}:
                quota_abort = True
                quota_scope = scope
            elif scope == "MINUTE":
                quota_abort = True
                quota_scope = "MINUTE_RETRY_EXHAUSTED"
            elif scope == "UNKNOWN_RATE_LIMIT":
                quota_abort = True
                quota_scope = "UNKNOWN_RATE_LIMIT_PERSISTENT"
            elif sample.get("acquisition_status") == "AUTHENTICATION_ERROR":
                quota_abort = True
                quota_scope = "AUTHENTICATION_ERROR"
            break

        print(
            json.dumps(
                {
                    "window": last_window,
                    "target_dates": target_dates,
                    "status_counts": dict(Counter(df.loc[[idx for idx, _ in batch], "acquisition_status"])),
                    "quota_abort": quota_abort,
                    "quota_scope": quota_scope,
                },
                sort_keys=True,
            ),
            flush=True,
        )

        if window_number % args.checkpoint_every_windows == 0 or quota_abort:
            summary = write_checkpoint(
                df=df,
                output_dir=args.output_dir,
                initial=initial,
                attempted_windows=attempted_windows,
                rate_limit_sleeps=rate_limit_sleeps,
                quota_abort=quota_abort,
                quota_scope=quota_scope,
                last_window=last_window,
            )
            print(json.dumps({"checkpoint": True, **summary}, sort_keys=True), flush=True)

        if quota_abort:
            break
        time.sleep(args.pacing_seconds)

    summary = write_checkpoint(
        df=df,
        output_dir=args.output_dir,
        initial=initial,
        attempted_windows=attempted_windows,
        rate_limit_sleeps=rate_limit_sleeps,
        quota_abort=quota_abort,
        quota_scope=quota_scope,
        last_window=last_window,
    )
    print(json.dumps(summary, sort_keys=True), flush=True)
    if summary["unresolved_count"]:
        suffix = f":QUOTA_SCOPE:{quota_scope}" if quota_scope else ""
        raise SystemExit(f"BLOCKED_DATA:UNRESOLVED_EXACT_NY17_ROWS:{summary['unresolved_count']}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
