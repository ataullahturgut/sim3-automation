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


def is_rate_limit(result: dict) -> bool:
    text = str(result.get("provider_message") or "").lower()
    return result.get("acquisition_status") == "ENTITLEMENT_BLOCKED" and (
        str(result.get("provider_code")) == "429" or "credit" in text or "rate limit" in text or "current minute" in text
    )


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-csv", action="append", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pacing-seconds", type=float, default=8.5)
    parser.add_argument("--backoff-seconds", type=float, default=70.0)
    parser.add_argument("--max-rate-limit-retries", type=int, default=8)
    args = parser.parse_args()

    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("BLOCKED_DATA:TWELVE_DATA_API_KEY_NOT_SET")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    d = load_inputs(args.probe_csv)
    initial = Counter(d["acquisition_status"])
    attempted = 0
    rate_limit_sleeps = 0

    for idx in d.index:
        status = str(d.at[idx, "acquisition_status"])
        if status in FINAL_STATUSES:
            continue
        if status not in RETRYABLE and status not in {"AUTHENTICATION_ERROR", "ENTITLEMENT_BLOCKED"}:
            continue
        trade_date = str(d.at[idx, "trade_date"])
        retries = 0
        while True:
            result, retrieved_at, payload_sha256 = request_date(api_key, trade_date)
            attempted += 1
            if is_rate_limit(result) and retries < args.max_rate_limit_retries:
                retries += 1
                rate_limit_sleeps += 1
                print(json.dumps({"trade_date": trade_date, "status": "RATE_LIMIT_BACKOFF", "retry": retries, "sleep_seconds": args.backoff_seconds}), flush=True)
                time.sleep(args.backoff_seconds)
                continue
            update_row(d, idx, result, retrieved_at, payload_sha256)
            print(json.dumps({"trade_date": trade_date, "status": result.get("acquisition_status"), "retry": retries}), flush=True)
            break
        time.sleep(args.pacing_seconds)

    final = Counter(d["acquisition_status"])
    unresolved = int(sum(n for status, n in final.items() if status not in FINAL_STATUSES))
    out_csv = args.output_dir / "gc_break_wp1_exact_ny17_consolidated_v2.csv"
    d.to_csv(out_csv, index=False)
    summary = {
        "audit_id": "GC_BREAK_WP1_EXACT_NY17_RESUME_V2",
        "source_semantic": "Twelve Data XAU/USD 1min exact 16:59:00 America/New_York; no fallback/interpolation",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "initial_status_counts": dict(initial),
        "final_status_counts": dict(final),
        "rows": int(len(d)),
        "attempted_requests": attempted,
        "rate_limit_backoff_count": rate_limit_sleeps,
        "unresolved_count": unresolved,
        "production_database_write": "NONE",
        "performance_scoring": False,
        "prospective_claim": False,
    }
    (args.output_dir / "gc_break_wp1_exact_ny17_resume_v2_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)
    if unresolved:
        raise SystemExit(f"BLOCKED_DATA:UNRESOLVED_EXACT_NY17_ROWS:{unresolved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
