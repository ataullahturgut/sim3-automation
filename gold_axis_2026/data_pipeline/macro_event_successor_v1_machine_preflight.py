from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data"
BLS_ARCHIVE_INDEX = "https://www.bls.gov/bls/news-release/empsit.htm"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
TE_PIT_DOC = "https://docs.tradingeconomics.com/economic_calendar/point-in-time/"
OUT = Path("macro_event_machine_source_preflight_v1.json")

BLS_SERIES = {
    "nfp_level": "CES0000000001",
    "unemployment_rate": "LNS14000000",
    "ahe_level": "CES0500000003",
}
FRED_SERIES = {
    "nfp_level": "PAYEMS",
    "unemployment_rate": "UNRATE",
    "ahe_level": "CES0500000003",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_get(session: requests.Session, url: str, **kwargs) -> requests.Response:
    headers = dict(kwargs.pop("headers", {}) or {})
    headers.setdefault("User-Agent", "Gold-Control-Macro-Source-Preflight/1.0")
    return session.get(url, headers=headers, timeout=(10, 40), **kwargs)


def probe_bls_api(session: requests.Session) -> dict:
    rows = {}
    for name, sid in BLS_SERIES.items():
        url = f"{BLS_API}/{sid}"
        try:
            r = safe_get(session, url, params={"latest": "true"})
            status = r.status_code
            j = r.json() if status == 200 else None
            series = (((j or {}).get("Results") or {}).get("series") or []) if isinstance((j or {}).get("Results"), dict) else []
            data = (series[0].get("data") or []) if series else []
            rows[name] = {
                "series_id": sid,
                "http_status": status,
                "request_status": (j or {}).get("status") if isinstance(j, dict) else None,
                "valid_latest_row_present": bool(data and str(data[0].get("value", "")).strip()),
                "raw_value_logged": False,
            }
        except Exception as exc:
            rows[name] = {"series_id": sid, "status": f"ERROR_{type(exc).__name__}", "raw_value_logged": False}
    ok = all(x.get("http_status") == 200 and x.get("valid_latest_row_present") for x in rows.values())
    return {
        "status": "PASS_MACHINE_ACCESS" if ok else "BLOCKED_BLS_PUBLIC_API_MACHINE_ACCESS",
        "provider": "U.S. Bureau of Labor Statistics Public Data API v2",
        "series": rows,
        "historical_first_print_approved": False,
        "note": "The live BLS API is an official machine-readable cross-check/current ingestion lane. It is not silently treated as a historical first-print archive because historical series values can be revised.",
    }


def probe_bls_archive(session: requests.Session) -> dict:
    try:
        r = safe_get(session, BLS_ARCHIVE_INDEX)
        return {
            "status": "PASS_MACHINE_ACCESS" if r.status_code == 200 else f"BLOCKED_HTTP_{r.status_code}",
            "http_status": r.status_code,
            "provider": "BLS Employment Situation archive index",
            "content_hash": hashlib.sha256(r.content).hexdigest() if r.status_code == 200 else None,
            "raw_release_values_logged": False,
        }
    except Exception as exc:
        return {"status": f"ERROR_{type(exc).__name__}", "provider": "BLS Employment Situation archive index", "raw_release_values_logged": False}


def probe_fred_initial_release(session: requests.Session) -> dict:
    key = os.environ.get("FRED_API_KEY", "").strip()
    if not key:
        return {
            "status": "BLOCKED_FRED_API_KEY_NOT_CONFIGURED",
            "provider": "Federal Reserve Bank of St. Louis FRED/ALFRED API",
            "output_type": 4,
            "initial_release_semantics": "Observations, Initial Release Only",
            "approved_for_historical_macro_input": False,
        }
    rows = {}
    for name, sid in FRED_SERIES.items():
        try:
            r = safe_get(session, FRED_API, params={
                "series_id": sid,
                "api_key": key,
                "file_type": "json",
                "output_type": 4,
                "observation_start": "2024-01-01",
                "observation_end": "2026-08-31",
                "limit": 100,
                "sort_order": "desc",
            })
            j = r.json() if r.status_code == 200 else None
            obs = (j or {}).get("observations", []) if isinstance(j, dict) else []
            valid = [x for x in obs if str(x.get("value", ".")) not in {".", "", "nan", "None"}]
            rows[name] = {
                "series_id": sid,
                "http_status": r.status_code,
                "valid_initial_release_rows": len(valid),
                "raw_value_logged": False,
            }
        except Exception as exc:
            rows[name] = {"series_id": sid, "status": f"ERROR_{type(exc).__name__}", "raw_value_logged": False}
    ok = all(x.get("http_status") == 200 and x.get("valid_initial_release_rows", 0) > 0 for x in rows.values())
    return {
        "status": "PASS_INITIAL_RELEASE_API_PROBE" if ok else "BLOCKED_INITIAL_RELEASE_API_PROBE",
        "provider": "Federal Reserve Bank of St. Louis FRED/ALFRED API",
        "output_type": 4,
        "series": rows,
        "approved_for_historical_macro_input": False,
        "note": "Passing this probe proves machine-readable initial-release availability for the named level/rate series only. Exact headline-NFP-change and AHE transformation equivalence still require a separately frozen construction audit.",
    }


def consensus_status() -> dict:
    te = bool(os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip())
    bloomberg = bool(os.environ.get("BLOOMBERG_MACRO_CONSENSUS_AVAILABLE", "").strip())
    if bloomberg:
        status = "BLOOMBERG_ACCESS_DECLARED_REQUIRES_PIT_AUDIT"
    elif te:
        status = "TRADING_ECONOMICS_KEY_PRESENT_REQUIRES_PIT_AUDIT"
    else:
        status = "BLOCKED_PIT_CONSENSUS_CREDENTIAL_NOT_CONFIGURED"
    return {
        "status": status,
        "approved_for_model_use": False,
        "preferred_provider": "Bloomberg historical pre-release median consensus",
        "research_fallback": "Trading Economics Economic Calendar Point-in-Time",
        "trading_economics_key_present": te,
        "pit_documentation": TE_PIT_DOC,
    }


def main() -> int:
    session = requests.Session()
    payload = {
        "generated_at": now_iso(),
        "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
        "evidence_class": "SOURCE_READINESS_PREFLIGHT",
        "bls_archive": probe_bls_archive(session),
        "bls_public_api": probe_bls_api(session),
        "fred_alfred_initial_release": probe_fred_initial_release(session),
        "consensus": consensus_status(),
        "production_db_write": False,
        "model_score_run": False,
        "forecast_or_decision_write": False,
        "direction_vote": False,
    }
    payload["status"] = (
        "PASS_PREFLIGHT_WITH_EXTERNAL_BLOCKERS"
        if payload["bls_public_api"]["status"] == "PASS_MACHINE_ACCESS"
        else "BLOCKED_MACHINE_SOURCE_ACCESS"
    )
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_PREFLIGHT_WITH_EXTERNAL_BLOCKERS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
