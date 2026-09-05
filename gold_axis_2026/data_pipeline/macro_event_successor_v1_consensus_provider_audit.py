from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

ENGINE_ID = "MACRO_EVENT_SUCCESSOR_V1"
OUT = Path("macro_event_consensus_provider_audit_v1.json")
TE_BASE = "https://api.tradingeconomics.com"

EVENTS = {
    "nfp": {
        "indicator": "non farm payrolls",
        "expected_category": "Non Farm Payrolls",
        "contract_series_id": "MACRO_NFP_CONSENSUS_PIT",
        "unit_family": "thousand_persons_change",
    },
    "unemployment": {
        "indicator": "unemployment rate",
        "expected_category": "Unemployment Rate",
        "contract_series_id": "MACRO_UNEMP_CONSENSUS_PIT",
        "unit_family": "percent",
    },
    "ahe_mom": {
        "indicator": "average hourly earnings mom",
        "expected_category": "Average Hourly Earnings MoM",
        "contract_series_id": "MACRO_AHE_CONSENSUS_PIT",
        "unit_family": "percent_mom",
    },
}

# Separated dates chosen before provider payload inspection. External values are
# informational cross-checks only; they are not equality gates because survey
# providers and snapshot times can differ.
SAMPLES = [
    {
        "release_date": "2016-12-02",
        "reference_month": "2016-11",
        "external_checks": {"nfp": 175.0},
        "external_check_source": "Reuters pre-release survey (public report)",
    },
    {
        "release_date": "2023-06-02",
        "reference_month": "2023-05",
        "external_checks": {"nfp": 190.0, "unemployment": 3.5, "ahe_mom": 0.3},
        "external_check_source": "Reuters/official-market reporting around release; informational only",
    },
    {
        "release_date": "2024-09-06",
        "reference_month": "2024-08",
        "external_checks": {"nfp": 160.0, "unemployment": 4.2, "ahe_mom": 0.3},
        "external_check_source": "Reuters/market-calendar public reporting; informational only",
    },
    {
        "release_date": "2026-09-04",
        "reference_month": "2026-08",
        "external_checks": {"nfp": 56.0, "unemployment": 4.1},
        "external_check_source": "Reuters release-day pre-release survey; informational only",
    },
]

REQUIRED_FIELDS = (
    "CalendarId",
    "Date",
    "Country",
    "Category",
    "Event",
    "Reference",
    "ReferenceDate",
    "Source",
    "SourceURL",
    "Actual",
    "Previous",
    "Forecast",
    "TEForecast",
    "DateSpan",
    "Importance",
    "LastUpdate",
    "Revised",
    "Unit",
    "Ticker",
    "Symbol",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_number(v: object) -> float | None:
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(",", "")
    mult = 1.0
    if s.upper().endswith("K"):
        mult = 1.0
        s = s[:-1]
    elif s.upper().endswith("M"):
        mult = 1000.0
        s = s[:-1]
    s = s.replace("%", "").strip()
    m = re.fullmatch(r"[-+]?\d+(?:\.\d+)?", s)
    if not m:
        return None
    return float(s) * mult


def normalize_date(v: object) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    if len(s) >= 10:
        return s[:10]
    return None


def payload_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def te_request(session: requests.Session, api_key: str, indicator: str, release_date: str) -> tuple[int, object]:
    url = (
        f"{TE_BASE}/calendar/country/united%20states/indicator/"
        f"{quote(indicator, safe='')}/{release_date}/{release_date}"
    )
    r = session.get(
        url,
        params={"c": api_key, "f": "json"},
        headers={"User-Agent": "Gold-Control-Macro-Consensus-Audit/1.0"},
        timeout=(10, 45),
    )
    try:
        payload = r.json()
    except Exception:
        payload = {"non_json_response": True, "body_sha256": hashlib.sha256(r.content).hexdigest()}
    return r.status_code, payload


def select_event(payload: object, expected_category: str, release_date: str) -> tuple[dict | None, int]:
    if not isinstance(payload, list):
        return None, 0
    candidates = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        country = str(row.get("Country", "")).strip().lower()
        category = str(row.get("Category", "")).strip().lower()
        event = str(row.get("Event", "")).strip().lower()
        d = normalize_date(row.get("Date"))
        if country == "united states" and d == release_date and (
            category == expected_category.lower() or event == expected_category.lower()
        ):
            candidates.append(row)
    return (candidates[0] if len(candidates) == 1 else None), len(candidates)


def audit_row(row: dict, spec: dict, sample: dict, external_value: float | None) -> dict:
    field_presence = {f: f in row for f in REQUIRED_FIELDS}
    forecast = parse_number(row.get("Forecast"))
    te_forecast = parse_number(row.get("TEForecast"))
    actual = parse_number(row.get("Actual"))
    event_date = normalize_date(row.get("Date"))
    ref_date = normalize_date(row.get("ReferenceDate"))
    exact_time = str(row.get("DateSpan", "")).strip() == "0"
    category_ok = str(row.get("Category", "")).strip().lower() == spec["expected_category"].lower()
    country_ok = str(row.get("Country", "")).strip().lower() == "united states"
    release_date_ok = event_date == sample["release_date"]
    forecast_ok = forecast is not None
    required_metadata_ok = all(field_presence.values())
    structural_pass = all((exact_time, category_ok, country_ok, release_date_ok, forecast_ok, required_metadata_ok))

    # Do not emit the licensed raw payload or raw consensus value to public CI logs.
    out = {
        "contract_series_id": spec["contract_series_id"],
        "calendar_id": str(row.get("CalendarId", "")),
        "ticker": str(row.get("Ticker", "")),
        "symbol": str(row.get("Symbol", "")),
        "event_date": event_date,
        "reference_date": ref_date,
        "reference": str(row.get("Reference", "")),
        "date_span_exact": exact_time,
        "field_presence": field_presence,
        "forecast_present_and_numeric": forecast_ok,
        "teforecast_present_and_numeric": te_forecast is not None,
        "actual_present_and_numeric": actual is not None,
        "forecast_and_teforecast_separately_identifiable": "Forecast" in row and "TEForecast" in row,
        "raw_payload_sha256": payload_hash(row),
        "licensed_raw_values_logged": False,
        "structural_status": "PASS" if structural_pass else "FAIL",
        "availability_semantics": "PRE_RELEASE_CONSENSUS_FIELD_PRESERVED_BY_PROVIDER_AT_EVENT_RELEASE",
        "last_update_used_as_consensus_timestamp": False,
        "teforecast_eligible_for_consensus": False,
    }
    if external_value is not None and forecast is not None:
        out["public_external_spot_check"] = {
            "reference_value": external_value,
            "difference_abs": abs(forecast - external_value),
            "informational_only": True,
            "provider_equality_gate": False,
        }
    return out


def main() -> int:
    key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    base = {
        "generated_at": now_iso(),
        "engine_id": ENGINE_ID,
        "evidence_class": "CONSENSUS_PROVIDER_SOURCE_AUDIT",
        "provider": "Trading Economics Economic Calendar Point-in-Time",
        "provider_role": "CANDIDATE_PRIMARY_EXECUTABLE_CONSENSUS_PROVIDER",
        "provider_documentation": "https://docs.tradingeconomics.com/economic_calendar/point-in-time/",
        "provider_schema_documentation": "https://docs.tradingeconomics.com/economic_calendar/schema/",
        "forecast_field_semantic": "survey consensus from representative group of economists",
        "teforecast_field_semantic": "Trading Economics proprietary/model forecast; forbidden as consensus input",
        "production_db_write": False,
        "model_score_run": False,
        "forecast_or_decision_write": False,
        "direction_vote": False,
        "approved_for_model_use": False,
        "raw_licensed_provider_payload_committed": False,
        "samples": [],
    }

    if not key:
        base.update({
            "status": "BLOCKED_TE_PIT_CREDENTIAL_NOT_CONFIGURED",
            "credential_present": False,
            "next_action": "Configure TRADING_ECONOMICS_API_KEY, rerun frozen provider audit, then review event mapping/coverage before any ingestion or score.",
        })
        OUT.write_text(json.dumps(base, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(base, indent=2, sort_keys=True))
        return 0

    base["credential_present"] = True
    session = requests.Session()
    overall_ok = True
    for sample in SAMPLES:
        sample_out = {
            "release_date": sample["release_date"],
            "reference_month": sample["reference_month"],
            "external_check_source": sample["external_check_source"],
            "events": {},
        }
        for name, spec in EVENTS.items():
            status_code, payload = te_request(session, key, spec["indicator"], sample["release_date"])
            selected, candidate_count = select_event(payload, spec["expected_category"], sample["release_date"])
            rec = {
                "http_status": status_code,
                "candidate_count": candidate_count,
                "response_sha256": payload_hash(payload),
                "raw_payload_logged": False,
            }
            if status_code != 200 or selected is None:
                rec["status"] = "FAIL_PROVIDER_EVENT_RESOLUTION"
                overall_ok = False
            else:
                row_audit = audit_row(selected, spec, sample, sample["external_checks"].get(name))
                rec.update(row_audit)
                rec["status"] = "PASS" if row_audit["structural_status"] == "PASS" else "FAIL_STRUCTURAL_GATE"
                if rec["status"] != "PASS":
                    overall_ok = False
            sample_out["events"][name] = rec
        base["samples"].append(sample_out)

    base["status"] = "PASS_TE_PIT_PROVIDER_STRUCTURE" if overall_ok else "FAIL_TE_PIT_PROVIDER_STRUCTURE"
    base["approved_for_model_use"] = False
    base["next_action"] = (
        "Freeze exact provider event mappings and run full historical coverage audit before governed Neon consensus ingestion."
        if overall_ok
        else "Do not ingest or score; resolve provider mapping/coverage failure under change control."
    )
    OUT.write_text(json.dumps(base, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(base, indent=2, sort_keys=True))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
