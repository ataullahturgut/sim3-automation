from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from probe_historical_ny17_gaps_v145 import FINAL_STATUSES, request_date  # noqa: E402

RETRYABLE = {"ENTITLEMENT_BLOCKED", "SERVER_ERROR", "REQUEST_ERROR"}
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


def rate_limit_scope(result: dict) -> str | None:
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


def update_row(df: pd.DataFrame, idx: int, result: dict, retrieved_at: str | None, payload_sha256: str | None) -> None:
    for key, value in result.items():
        if key not in df.columns:
            df[key] = ""
        df.at[idx, key] = "" if value is None else str(value)
    for key, value in {
        "retrieved_at": retrieved_at,
        "payload_sha256": payload_sha256,
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1min",
        "timezone": "America/New_York",
        "accepted_source_time": "16:59:00",
        "stored_semantic": "17:00 ET",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "prospective_claim": "False",
    }.items():
        if key not in df.columns:
            df[key] = ""
        df.at[idx, key] = "" if value is None else str(value)


def build_summary(
    d: pd.DataFrame,
    initial: Counter,
    attempted: int,
    rate_limit_sleeps: int,
    quota_abort: bool,
    quota_scope: str | None,
    last_attempted_trade_date: str | None,
) -> dict:
    final = Counter(d["acquisition_status"])
    unresolved = int(sum(n for status, n in final.items() if status not in FINAL_STATUSES))
    return {
        "audit_id": "GC_BREAK_WP1_EXACT_NY17_RESUME_V2",
        "source_semantic": "Twelve Data XAU/USD 1min exact 16:59:00 America/New_York; no fallback/interpolation",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "initial_status_counts": dict(initial),
        "final_status_counts": dict(final),
        "rows": int(len(d)),
        "attempted_requests": attempted,
        "rate_limit_backoff_count": rate_limit_sleeps,
        "unresolved_count": unresolved,
        "quota_abort": quota_abort,
        "quota_scope": quota_scope,
        "last_attempted_trade_date": last_attempted_trade_date,
        "production_database_write": "NONE",
        "performance_scoring": False,
        "prospective_claim": False,
    }


def write_checkpoint(
    d: pd.DataFrame,
    output_dir: Path,
    initial: Counter,
    attempted: int,
    rate_limit_sleeps: int,
    quota_abort: bool,
    quota_scope: str | None,
    last_attempted_trade_date: str | None,
) -> dict:
    out_csv = output_dir / "gc_break_wp1_exact_ny17_consolidated_v2.csv"
    d.to_csv(out_csv, index=False)
    summary = build_summary(
        d=d,
        initial=initial,
        attempted=attempted,
        rate_limit_sleeps=rate_limit_sleeps,
        quota_abort=quota_abort,
        quota_scope=quota_scope,
        last_attempted_trade_date=last_attempted_trade_date,
    )
    (output_dir / "gc_break_wp1_exact_ny17_resume_v2_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-csv", action="append", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pacing-seconds", type=float, default=8.5)
    parser.add_argument("--backoff-seconds", type=float, default=70.0)
    parser.add_argument("--max-rate-limit-retries", type=int, default=8)
    parser.add_argument("--max-unknown-rate-limit-retries", type=int, default=1)
    parser.add_argument("--checkpoint-every", type=int, default=25)
    args = parser.parse_args()

    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("BLOCKED_DATA:TWELVE_DATA_API_KEY_NOT_SET")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    d = load_inputs(args.probe_csv)
    initial = Counter(d["acquisition_status"])
    attempted = 0
    rate_limit_sleeps = 0
    processed_since_checkpoint = 0
    quota_abort = False
    quota_scope: str | None = None
    last_attempted_trade_date: str | None = None

    for idx in d.index:
        status = str(d.at[idx, "acquisition_status"])
        if status in FINAL_STATUSES:
            continue
        if status not in RETRYABLE and status not in {"AUTHENTICATION_ERROR", "ENTITLEMENT_BLOCKED"}:
            continue

        trade_date = str(d.at[idx, "trade_date"])
        retries = 0
        unknown_retries = 0

        while True:
            result, retrieved_at, payload_sha256 = request_date(api_key, trade_date)
            attempted += 1
            last_attempted_trade_date = trade_date
            scope = rate_limit_scope(result)

            if scope == "MINUTE":
                if retries < args.max_rate_limit_retries:
                    retries += 1
                    rate_limit_sleeps += 1
                    print(
                        json.dumps(
                            {
                                "trade_date": trade_date,
                                "status": "MINUTE_RATE_LIMIT_BACKOFF",
                                "retry": retries,
                                "sleep_seconds": args.backoff_seconds,
                            }
                        ),
                        flush=True,
                    )
                    time.sleep(args.backoff_seconds)
                    continue
                update_row(d, idx, result, retrieved_at, payload_sha256)
                quota_abort = True
                quota_scope = "MINUTE_RETRY_EXHAUSTED"
                break

            if scope == "UNKNOWN_RATE_LIMIT":
                if unknown_retries < args.max_unknown_rate_limit_retries:
                    unknown_retries += 1
                    rate_limit_sleeps += 1
                    print(
                        json.dumps(
                            {
                                "trade_date": trade_date,
                                "status": "UNKNOWN_RATE_LIMIT_BACKOFF",
                                "retry": unknown_retries,
                                "sleep_seconds": args.backoff_seconds,
                            }
                        ),
                        flush=True,
                    )
                    time.sleep(args.backoff_seconds)
                    continue
                update_row(d, idx, result, retrieved_at, payload_sha256)
                quota_abort = True
                quota_scope = "UNKNOWN_RATE_LIMIT_PERSISTENT"
                break

            if scope in {"LONG_QUOTA", "ENTITLEMENT"}:
                update_row(d, idx, result, retrieved_at, payload_sha256)
                quota_abort = True
                quota_scope = scope
                break

            if result.get("acquisition_status") == "AUTHENTICATION_ERROR":
                update_row(d, idx, result, retrieved_at, payload_sha256)
                quota_abort = True
                quota_scope = "AUTHENTICATION_ERROR"
                break

            update_row(d, idx, result, retrieved_at, payload_sha256)
            break

        processed_since_checkpoint += 1
        print(
            json.dumps(
                {
                    "trade_date": trade_date,
                    "status": str(d.at[idx, "acquisition_status"]),
                    "retry": retries,
                    "quota_abort": quota_abort,
                    "quota_scope": quota_scope,
                }
            ),
            flush=True,
        )

        if processed_since_checkpoint >= args.checkpoint_every or quota_abort:
            summary = write_checkpoint(
                d=d,
                output_dir=args.output_dir,
                initial=initial,
                attempted=attempted,
                rate_limit_sleeps=rate_limit_sleeps,
                quota_abort=quota_abort,
                quota_scope=quota_scope,
                last_attempted_trade_date=last_attempted_trade_date,
            )
            print(json.dumps({"checkpoint": True, **summary}, sort_keys=True), flush=True)
            processed_since_checkpoint = 0

        if quota_abort:
            break
        time.sleep(args.pacing_seconds)

    summary = write_checkpoint(
        d=d,
        output_dir=args.output_dir,
        initial=initial,
        attempted=attempted,
        rate_limit_sleeps=rate_limit_sleeps,
        quota_abort=quota_abort,
        quota_scope=quota_scope,
        last_attempted_trade_date=last_attempted_trade_date,
    )
    print(json.dumps(summary, sort_keys=True), flush=True)

    if summary["unresolved_count"]:
        suffix = f":QUOTA_SCOPE:{quota_scope}" if quota_scope else ""
        raise SystemExit(f"BLOCKED_DATA:UNRESOLVED_EXACT_NY17_ROWS:{summary['unresolved_count']}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
