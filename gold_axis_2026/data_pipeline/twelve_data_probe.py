from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

BASE_URL = "https://api.twelvedata.com"

# Probe exact/common vendor spellings only. This script never writes market data.
CANDIDATES = [
    "NEM",
    "B",
    "GLL",
    "DZZ",
    "HL-PB",
    "HL-P-B",
    "HL.PR.B",
    "HL-PRB",
]


def key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY missing")
    return value


def request_json(session: requests.Session, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    headers = {"Authorization": f"apikey {key()}", "User-Agent": "GoldControl/2.6"}
    response = session.get(f"{BASE_URL}/{endpoint}", params=params, headers=headers, timeout=(8, 25))
    try:
        payload = response.json()
    except Exception:
        payload = {"status": "error", "message": f"NON_JSON_HTTP_{response.status_code}"}
    payload["_http_status"] = response.status_code
    return payload


def sanitize_meta(meta: dict[str, Any] | None) -> dict[str, Any]:
    meta = meta or {}
    # No raw market prices are emitted to public CI logs.
    keep = ["symbol", "name", "exchange", "mic_code", "currency", "type", "country", "exchange_timezone"]
    return {k: meta.get(k) for k in keep if meta.get(k) is not None}


def main() -> int:
    session = requests.Session()
    results = []
    for symbol in CANDIDATES:
        payload = request_json(session, "time_series", {
            "symbol": symbol,
            "interval": "1day",
            "outputsize": 1,
            "format": "JSON",
        })
        status = payload.get("status")
        values = payload.get("values") or []
        ok = payload.get("_http_status") == 200 and status != "error" and bool(values)
        results.append({
            "candidate": symbol,
            "ok": ok,
            "http_status": payload.get("_http_status"),
            "meta": sanitize_meta(payload.get("meta")),
            "error_code": payload.get("code") if not ok else None,
            "error_message": payload.get("message") if not ok else None,
        })

    # Discovery searches are metadata-only and help resolve Hecla preferred notation.
    searches = []
    for query in ["Hecla Mining", "HL preferred", "Newmont", "Barrick", "UltraShort Gold", "Gold Double Short"]:
        payload = request_json(session, "symbol_search", {"symbol": query, "outputsize": 20})
        data = payload.get("data") or []
        searches.append({
            "query": query,
            "http_status": payload.get("_http_status"),
            "status": payload.get("status"),
            "matches": [sanitize_meta(x) for x in data[:10]],
            "error_code": payload.get("code") if payload.get("status") == "error" else None,
            "error_message": payload.get("message") if payload.get("status") == "error" else None,
        })

    out = {"status": "PASS_PROBE", "candidates": results, "searches": searches}
    print(json.dumps(out, indent=2, ensure_ascii=False))

    # A valid secret must at minimum reach the API and resolve NEM.
    nem = next((x for x in results if x["candidate"] == "NEM"), None)
    if not nem or not nem["ok"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
