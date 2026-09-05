from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

FRED_API = "https://api.stlouisfed.org/fred/series/observations"
OUT = Path("macro_event_alfred_construction_audit_v1.json")
SERIES = {
    "nfp_level": "PAYEMS",
    "unemployment_rate": "UNRATE",
    "ahe_level": "CES0500000003",
}

# Frozen authority checks transcribed from official BLS Employment Situation first releases.
# These are audit references only, not model-training inputs.
CHECKS = [
    {
        "release_date": "2016-06-03",
        "reference_month": "2016-05-01",
        "previous_month": "2016-04-01",
        "expected_nfp_change_thousands": 38.0,
        "expected_unemployment_pct": 4.7,
        "expected_ahe_level": 25.59,
        "expected_previous_ahe_level": 25.54,
    },
    {
        "release_date": "2016-07-08",
        "reference_month": "2016-06-01",
        "previous_month": "2016-05-01",
        "expected_nfp_change_thousands": 287.0,
        "expected_unemployment_pct": 4.9,
        "expected_ahe_level": 25.61,
        "expected_previous_ahe_level": 25.59,
    },
    {
        "release_date": "2026-09-04",
        "reference_month": "2026-08-01",
        "previous_month": "2026-07-01",
        "expected_nfp_change_thousands": 162.0,
        "expected_unemployment_pct": 4.1,
        "expected_ahe_level": 37.75,
        "expected_previous_ahe_level": 37.65,
    },
]


def get_json(session: requests.Session, params: dict) -> dict:
    r = session.get(
        FRED_API,
        params=params,
        headers={"User-Agent": "Gold-Control-Macro-ALFRED-Construction-Audit/1.0"},
        timeout=(10, 40),
    )
    if r.status_code != 200:
        try:
            err = r.json()
        except Exception:
            err = {}
        raise RuntimeError(f"FRED_HTTP_{r.status_code}:{err.get('error_code')}:{err.get('error_message')}")
    return r.json()


def asof_values(session: requests.Session, api_key: str, series_id: str, asof: str, start: str, end: str) -> dict[str, float]:
    j = get_json(session, {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "output_type": 1,
        "realtime_start": asof,
        "realtime_end": asof,
        "observation_start": start,
        "observation_end": end,
        "sort_order": "asc",
        "limit": 100,
    })
    out = {}
    for row in j.get("observations", []):
        value = str(row.get("value", "."))
        if value in {".", "", "nan", "None"}:
            continue
        out[str(row["date"])] = float(value)
    return out


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def main() -> int:
    key = os.environ.get("FRED_API_KEY", "").strip()
    if not key:
        payload = {
            "status": "BLOCKED_FRED_API_KEY_NOT_CONFIGURED",
            "approved_construction": False,
            "model_score_run": False,
            "production_db_write": False,
        }
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    session = requests.Session()
    results = []
    for check in CHECKS:
        asof = check["release_date"]
        ref = check["reference_month"]
        prev = check["previous_month"]
        start = prev
        end = ref
        payems = asof_values(session, key, SERIES["nfp_level"], asof, start, end)
        unrate = asof_values(session, key, SERIES["unemployment_rate"], asof, ref, ref)
        ahe = asof_values(session, key, SERIES["ahe_level"], asof, start, end)

        required = {
            "payems_ref": ref in payems,
            "payems_prev": prev in payems,
            "unrate_ref": ref in unrate,
            "ahe_ref": ref in ahe,
            "ahe_prev": prev in ahe,
        }
        if not all(required.values()):
            results.append({
                "release_date": asof,
                "reference_month": ref[:7],
                "status": "FAIL_REQUIRED_ASOF_VALUE_MISSING",
                "required_presence": required,
                "raw_values_logged": False,
            })
            continue

        nfp = payems[ref] - payems[prev]
        u = unrate[ref]
        ahe_ref = ahe[ref]
        ahe_prev = ahe[prev]
        ahe_mom_rounded = round((ahe_ref / ahe_prev - 1.0) * 100.0, 1)
        expected_ahe_mom_rounded = round(
            (check["expected_ahe_level"] / check["expected_previous_ahe_level"] - 1.0) * 100.0,
            1,
        )
        checks = {
            "nfp_headline_change": close(nfp, check["expected_nfp_change_thousands"]),
            "unemployment_rate": close(u, check["expected_unemployment_pct"]),
            "ahe_current_level": close(ahe_ref, check["expected_ahe_level"]),
            "ahe_previous_revised_level_asof_release": close(ahe_prev, check["expected_previous_ahe_level"]),
            "ahe_mom_1dp": close(ahe_mom_rounded, expected_ahe_mom_rounded),
        }
        results.append({
            "release_date": asof,
            "reference_month": ref[:7],
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "derived_ahe_mom_1dp": ahe_mom_rounded,
            "expected_ahe_mom_1dp": expected_ahe_mom_rounded,
            "nfp_difference_error_thousands": nfp - check["expected_nfp_change_thousands"],
            "unemployment_error_pct_point": u - check["expected_unemployment_pct"],
            "ahe_level_error_dollars": ahe_ref - check["expected_ahe_level"],
            "raw_source_levels_logged": False,
        })

    passed = len(results) == len(CHECKS) and all(x.get("status") == "PASS" for x in results)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
        "method": "ALFRED_ASOF_RELEASE_DATE_LEVELS",
        "release_id_context": 50,
        "series": SERIES,
        "authority_reference_count": len(CHECKS),
        "results": results,
        "status": "PASS_CONSTRUCTION_EQUIVALENCE_SAMPLE" if passed else "FAIL_CONSTRUCTION_EQUIVALENCE_SAMPLE",
        "approved_construction": passed,
        "approval_scope": "historical_actual_reconstruction_method_only; consensus and macro-score remain unapproved",
        "model_score_run": False,
        "production_db_write": False,
        "forecast_or_decision_write": False,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
