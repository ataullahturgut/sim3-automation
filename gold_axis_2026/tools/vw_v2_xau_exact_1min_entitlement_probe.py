from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "vw_midas_svr_xau_successor_v2" / "bridge_probe" / "exact_1min_entitlement_probe.json"
URL = "https://api.twelvedata.com/time_series"
DATES = ("2024-12-16", "2025-06-16", "2026-08-28")


def probe_date(session: requests.Session, api_key: str, day: str) -> dict:
    params = {
        "symbol": "XAU/USD",
        "interval": "1min",
        "start_date": f"{day} 16:50:00",
        "end_date": f"{day} 17:00:00",
        "timezone": "America/New_York",
        "order": "ASC",
        "outputsize": 100,
        "apikey": api_key,
    }
    r = session.get(URL, params=params, timeout=(20, 90))
    try:
        payload = r.json()
    except Exception:
        payload = {}
    code = payload.get("code") if isinstance(payload, dict) else None
    if r.status_code != 200 or not isinstance(payload, dict) or payload.get("status") == "error":
        return {"date": day, "pass": False, "reason": f"HTTP_{r.status_code}_API_{code or 'NA'}", "exact_bar_count": 0}
    exact = []
    for row in payload.get("values") or []:
        if str(row.get("datetime", "")).endswith("16:59:00"):
            exact.append(row)
    if len(exact) != 1:
        return {"date": day, "pass": False, "reason": f"EXACT_16_59_BAR_COUNT_{len(exact)}", "exact_bar_count": len(exact)}
    row = exact[0]
    try:
        vals = [float(row[k]) for k in ("open", "high", "low", "close")]
    except Exception:
        return {"date": day, "pass": False, "reason": "OHLC_PARSE_FAIL", "exact_bar_count": 1}
    if not all(math.isfinite(v) and v > 0 for v in vals):
        return {"date": day, "pass": False, "reason": "OHLC_NONPOSITIVE_OR_NONFINITE", "exact_bar_count": 1}
    meta = payload.get("meta") or {}
    return {
        "date": day,
        "pass": True,
        "reason": None,
        "exact_bar_count": 1,
        "meta_symbol": meta.get("symbol"),
        "meta_interval": meta.get("interval"),
        "meta_timezone": meta.get("exchange_timezone") or meta.get("timezone"),
    }


def main() -> int:
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-VW-V2-Exact-1m-Probe/1.0"})
    rows = [probe_date(session, api_key, d) for d in DATES]
    passed = all(r["pass"] for r in rows)
    evidence = {
        "engine_id": "VW_MIDAS_SVR_XAU_SUCCESSOR_V2",
        "evidence_class": "SOURCE_ENTITLEMENT_PROBE_ONLY",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "dates": rows,
        "probe_pass": passed,
        "result": "HISTORICAL_EXACT_1MIN_BRIDGE_SOURCE_ENTITLEMENT_PROVEN_FOR_PROBE_DATES" if passed else "BLOCKED_HISTORICAL_EXACT_1MIN_BRIDGE_SOURCE_NOT_PROVEN",
        "model_score_run": False,
        "bridge_metric_run": False,
        "database_write": False,
        "raw_market_values_logged": False,
        "raw_market_values_committed": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"VW_V2_EXACT_1MIN_PROBE={'PASS' if passed else 'BLOCKED'}")
    for row in rows:
        print(f"PROBE_DATE={row['date']} STATUS={'PASS' if row['pass'] else row['reason']} EXACT_BAR_COUNT={row['exact_bar_count']}")
    print(f"RESULT={evidence['result']}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("MODEL_SCORE_RUN=NONE")
    print("BRIDGE_METRIC_RUN=NONE")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
