from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


URL = "https://api.twelvedata.com/time_series"
ACCEPTED_TIME = "16:59:00"


def classify_error(code: int | str | None, message: str) -> str:
    text = message.lower()
    if str(code) == "404" or "data not found" in text or "no data" in text:
        return "PROVIDER_NO_BAR"
    if str(code) in {"401", "403"} or "api key" in text or "authentication" in text:
        return "AUTHENTICATION_ERROR" if str(code) == "401" else "ENTITLEMENT_BLOCKED"
    if str(code) == "429" or "credit" in text or "rate limit" in text:
        return "ENTITLEMENT_BLOCKED"
    if str(code).startswith("5") or "server" in text:
        return "SERVER_ERROR"
    if str(code) == "400" or "parameter" in text or "invalid" in text:
        return "INVALID_REQUEST"
    return "REQUEST_ERROR"


def classify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("status") == "error" or "values" not in payload:
        status = classify_error(payload.get("code"), str(payload.get("message") or "missing values"))
        return {"acquisition_status": status, "provider_code": payload.get("code"), "provider_message": payload.get("message")}
    selected = [row for row in payload.get("values", []) if str(row.get("datetime", "")).endswith(f" {ACCEPTED_TIME}")]
    if not selected:
        return {"acquisition_status": "PROVIDER_NO_BAR", "provider_code": None, "provider_message": "exact 16:59:00 source bar absent"}
    if len(selected) != 1:
        return {"acquisition_status": "MALFORMED_BAR", "provider_code": None, "provider_message": f"duplicate exact bars: {len(selected)}"}
    row = selected[0]
    try:
        values = {k: float(row[k]) for k in ("open", "high", "low", "close")}
    except (KeyError, TypeError, ValueError):
        return {"acquisition_status": "MALFORMED_BAR", "provider_code": None, "provider_message": "OHLC parse failure"}
    if not all(math.isfinite(v) and v > 0 for v in values.values()):
        return {"acquisition_status": "MALFORMED_BAR", "provider_code": None, "provider_message": "non-positive or non-finite OHLC"}
    if values["high"] < max(values["open"], values["low"], values["close"]) or values["low"] > min(values["open"], values["high"], values["close"]):
        return {"acquisition_status": "MALFORMED_BAR", "provider_code": None, "provider_message": "OHLC range invalid"}
    return {"acquisition_status": "VALID_EXACT_BAR", "provider_code": None, "provider_message": None, "source_bar_datetime": row["datetime"], **values}


def request_date(api_key: str, trade_date: str) -> tuple[dict[str, Any], str, str]:
    params = urllib.parse.urlencode({"symbol": "XAU/USD", "interval": "1min", "timezone": "America/New_York", "start_date": f"{trade_date} 00:00:00", "end_date": f"{trade_date} 23:59:59", "outputsize": 5000, "format": "JSON"})
    request = urllib.request.Request(f"{URL}?{params}", headers={"Authorization": f"apikey {api_key}", "User-Agent": "GoldControl-V145-HistoricalGapProbe/1.0"})
    retrieved_at = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=60) as response: raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try: payload = json.loads(raw)
        except Exception: payload = {"status": "error", "code": exc.code, "message": str(exc)}
    except Exception as exc:
        payload = {"status": "error", "code": None, "message": f"{type(exc).__name__}:{exc}"}; raw = json.dumps(payload).encode()
    else:
        try: payload = json.loads(raw)
        except Exception: payload = {"status": "error", "code": None, "message": "non-JSON provider response"}
    return classify_payload(payload), retrieved_at, hashlib.sha256(raw).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_ny17_gap_inventory_v145.csv"))
    parser.add_argument("--out-json", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_ny17_exact_date_probe_v145.json"))
    parser.add_argument("--out-csv", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_ny17_exact_date_probe_v145.csv"))
    parser.add_argument("--pacing-seconds", type=float, default=8.0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key: raise SystemExit("BLOCKED_DATA:TWELVE_DATA_API_KEY_NOT_SET")
    with Path(args.inventory).open(encoding="utf-8", newline="") as fh:
        candidates = [r for r in csv.DictReader(fh) if r["gap_action"] != "NO_WRITE_ALREADY_CANONICAL"]
    if args.limit is not None: candidates = candidates[:args.limit]
    out: list[dict[str, Any]] = []
    entitlement_blocked = False
    for i, row in enumerate(candidates):
        if entitlement_blocked:
            result = {"acquisition_status": "ENTITLEMENT_BLOCKED", "provider_code": None, "provider_message": "not requested after provider quota/entitlement blocker in same run"}
            retrieved_at = None; payload_sha256 = None
        else:
            result, retrieved_at, payload_sha256 = request_date(api_key, row["trade_date"])
            if result["acquisition_status"] == "ENTITLEMENT_BLOCKED": entitlement_blocked = True
            if i + 1 < len(candidates) and not entitlement_blocked: time.sleep(args.pacing_seconds)
        out.append({"trade_date": row["trade_date"], **result, "retrieved_at": retrieved_at, "payload_sha256": payload_sha256,
                    "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1min", "timezone": "America/New_York",
                    "accepted_source_time": ACCEPTED_TIME, "stored_semantic": "17:00 ET", "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                    "prospective_claim": False, "impacted_readiness_cells": json.loads(row["impacted_readiness_cells"])})
    payload = {"probe_id": "GOLD_CONTROL_HISTORICAL_NY17_EXACT_DATE_PROBE_V145", "production_write": "NONE", "performance_scoring": False,
               "row_count": len(out), "rows": out}
    Path(args.out_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = list(out[0]) if out else ["trade_date", "acquisition_status"]
    with Path(args.out_csv).open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader()
        for row in out:
            flat = dict(row); flat["impacted_readiness_cells"] = json.dumps(flat["impacted_readiness_cells"], separators=(",", ":")); writer.writerow(flat)
    counts: dict[str, int] = {}
    for row in out: counts[row["acquisition_status"]] = counts.get(row["acquisition_status"], 0) + 1
    print(json.dumps({"row_count": len(out), "status_counts": counts, "production_write": "NONE"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
