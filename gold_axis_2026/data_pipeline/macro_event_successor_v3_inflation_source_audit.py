from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

FRED_API = "https://api.stlouisfed.org/fred/series/observations"
INVESTING_BASE = "https://www.investing.com/economic-calendar/"
INVESTING_FILTERED = INVESTING_BASE + "Service/getCalendarFilteredData"
OUT = Path("macro_event_successor_v3_inflation_source_audit.json")

# Frozen V3 choice: seasonally-adjusted month-over-month headline and core CPI.
ALFRED_SERIES = {
    "cpi_level": "CPIAUCSL",
    "core_cpi_level": "CPILFESL",
}

# Authority checks are taken from official BLS releases and are validation references only.
CHECKS = (
    {
        "release_date": "2026-05-12",
        "reference_month": "2026-04-01",
        "previous_month": "2026-03-01",
        "expected_cpi_mom_pct_1dp": 0.6,
        "expected_core_cpi_mom_pct_1dp": 0.4,
    },
    {
        "release_date": "2026-06-10",
        "reference_month": "2026-05-01",
        "previous_month": "2026-04-01",
        "expected_cpi_mom_pct_1dp": 0.5,
        "expected_core_cpi_mom_pct_1dp": 0.2,
    },
    {
        "release_date": "2026-08-12",
        "reference_month": "2026-07-01",
        "previous_month": "2026-06-01",
        "expected_cpi_mom_pct_1dp": 0.1,
        "expected_core_cpi_mom_pct_1dp": 0.2,
    },
)

TARGET_EVENT_NAMES = {
    "CPI (MoM)": "MACRO_CPI_CONSENSUS_PIT",
    "Core CPI (MoM)": "MACRO_CORE_CPI_CONSENSUS_PIT",
}
DISCOVERY_DATE = "2026-04-10"
_REFERENCE_MONTH_SUFFIX = re.compile(
    r"\s+\((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\)$"
)


@dataclass(frozen=True)
class CalendarEventMetadata:
    event_name: str
    event_attr_id: str
    event_row_id: str | None
    provider_datetime: str | None
    currency: str | None
    forecast_present: bool


def fred_key() -> str:
    value = os.environ.get("FRED_API_KEY", "").strip()
    if not value:
        raise RuntimeError("FRED_API_KEY_NOT_SET")
    return value


def _fred_json(session: requests.Session, params: dict[str, Any]) -> dict[str, Any]:
    r = session.get(
        FRED_API,
        params=params,
        headers={"User-Agent": "Gold-Control-Macro-V3-Inflation-Audit/1.0"},
        timeout=(10, 40),
    )
    if r.status_code != 200:
        raise RuntimeError(f"FRED_HTTP_{r.status_code}")
    return r.json()


def asof_values(session: requests.Session, series_id: str, asof: str, start: str, end: str) -> dict[str, float]:
    payload = _fred_json(session, {
        "series_id": series_id,
        "api_key": fred_key(),
        "file_type": "json",
        "output_type": 1,
        "realtime_start": asof,
        "realtime_end": asof,
        "observation_start": start,
        "observation_end": end,
        "sort_order": "asc",
        "limit": 100,
    })
    out: dict[str, float] = {}
    for row in payload.get("observations", []):
        value = str(row.get("value", "."))
        if value in {".", "", "nan", "None"}:
            continue
        out[str(row["date"])] = float(value)
    return out


def pct_mom_1dp(current: float, previous: float) -> float:
    if current <= 0 or previous <= 0:
        raise ValueError("CPI_LEVEL_MUST_BE_POSITIVE")
    return round((current / previous - 1.0) * 100.0, 1)


def normalize_event_name(name: str) -> str:
    return _REFERENCE_MONTH_SUFFIX.sub("", " ".join(name.split())).strip()


def audit_alfred_actuals() -> dict[str, Any]:
    s = requests.Session()
    rows = []
    for check in CHECKS:
        ref = check["reference_month"]
        prev = check["previous_month"]
        asof = check["release_date"]
        headline = asof_values(s, ALFRED_SERIES["cpi_level"], asof, prev, ref)
        core = asof_values(s, ALFRED_SERIES["core_cpi_level"], asof, prev, ref)
        presence = {
            "headline_ref": ref in headline,
            "headline_prev": prev in headline,
            "core_ref": ref in core,
            "core_prev": prev in core,
        }
        if not all(presence.values()):
            rows.append({
                "release_date": asof,
                "reference_month": ref[:7],
                "status": "FAIL_REQUIRED_ASOF_VALUE_MISSING",
                "presence": presence,
            })
            continue
        got_headline = pct_mom_1dp(headline[ref], headline[prev])
        got_core = pct_mom_1dp(core[ref], core[prev])
        checks = {
            "headline_cpi_mom_1dp": abs(got_headline - check["expected_cpi_mom_pct_1dp"]) <= 1e-12,
            "core_cpi_mom_1dp": abs(got_core - check["expected_core_cpi_mom_pct_1dp"]) <= 1e-12,
        }
        rows.append({
            "release_date": asof,
            "reference_month": ref[:7],
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "derived_headline_cpi_mom_1dp": got_headline,
            "expected_headline_cpi_mom_1dp": check["expected_cpi_mom_pct_1dp"],
            "derived_core_cpi_mom_1dp": got_core,
            "expected_core_cpi_mom_pct_1dp": check["expected_core_cpi_mom_pct_1dp"],
            "raw_levels_logged": False,
        })
    passed = len(rows) == len(CHECKS) and all(r["status"] == "PASS" for r in rows)
    return {
        "status": "PASS_ALFRED_BLS_FIRST_PRINT_CONSTRUCTION" if passed else "FAIL_ALFRED_BLS_FIRST_PRINT_CONSTRUCTION",
        "method": "ALFRED_ASOF_OFFICIAL_BLS_RELEASE_DATE_LEVELS_TO_MOM_1DP",
        "series": ALFRED_SERIES,
        "authority_check_count": len(CHECKS),
        "results": rows,
    }


def _calendar_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": INVESTING_BASE,
        "Origin": "https://www.investing.com",
    }


def _base_defaults(session: requests.Session) -> tuple[str, str]:
    r = session.get(INVESTING_BASE, headers=_calendar_headers(), timeout=(10, 40))
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    timezone_value = "55"
    time_filter = "timeRemain"
    tz = soup.find("select", {"id": "timeZone"})
    if tz:
        selected = tz.find("option", selected=True)
        if selected and selected.get("value"):
            timezone_value = str(selected["value"])
    checked = soup.find("input", {"name": "timeFilter", "checked": True)
    if checked and checked.get("value"):
        time_filter = str(checked["value"])
    return timezone_value, time_filter


def _event_name(row) -> str:
    cell = row.select_one("td.event")
    if not cell:
        return ""
    return normalize_event_name(cell.get_text(" ", strip=True))


def _currency(row) -> str | None:
    cell = row.select_one("td.flagCur")
    if not cell:
        return None
    text = " ".join(cell.get_text(" ", strip=True).split())
    m = re.search(r"\b([A-Z]{3})\b", text)
    return m.group(1) if m else None


def _forecast_present(row) -> bool:
    cell = row.select_one("td.fore")
    if cell is None:
        return False
    text = " ".join(cell.get_text(" ", strip=True).split())
    return text not in {"", "-", "--", "N/A"}


def discover_investing_cpi_metadata() -> dict[str, Any]:
    session = requests.Session()
    tz, time_filter = _base_defaults(session)
    payload = [
        ("dateFrom", DISCOVERY_DATE),
        ("dateTo", DISCOVERY_DATE),
        ("timeZone", tz),
        ("timeFilter", time_filter),
        ("currentTab", "custom"),
        ("submitFilters", "1"),
        ("limit_from", "0"),
    ]
    r = session.post(INVESTING_FILTERED, data=payload, headers=_calendar_headers(), timeout=(10, 40))
    if r.status_code == 429:
        return {"status": "BLOCKED_PROVIDER_RATE_LIMIT", "events": []}
    r.raise_for_status()
    try:
        body = r.json()
    except Exception as exc:
        raise RuntimeError("INVESTING_FILTERED_RESPONSE_NOT_JSON") from exc
    html = str(body.get("data") or "")
    if not html:
        raise RuntimeError("INVESTING_FILTERED_RESPONSE_NO_DATA")
    page_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
    soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
    found: dict[str, CalendarEventMetadata] = {}
    for row in soup.find_all("tr"):
        name = _event_name(row)
        if name not in TARGET_EVENT_NAMES:
            continue
        cur = _currency(row)
        if cur != "USD":
            continue
        attr_id = row.get("event_attr_id") or row.get("event_attr_ID")
        if not attr_id:
            continue
        found[name] = CalendarEventMetadata(
            event_name=name,
            event_attr_id=str(attr_id),
            event_row_id=str(row.get("id")) if row.get("id") else None,
            provider_datetime=str(row.get("data-event-datetime") or row.get("event_timestamp") or "") or None,
            currency=cur,
            forecast_present=_forecast_present(row),
        )
    missing = [name for name in TARGET_EVENT_NAMES if name not in found]
    return {
        "status": "PASS_EVENT_IDENTITIES_DISCOVERED" if not missing else "BLOCKED_EVENT_IDENTITIES_NOT_FOUND",
        "provider": "Investing.com Economic Calendar",
        "provider_scope": "DOCTORAL_RESEARCH_INTERNAL_USER_ACCEPTED_LICENSE_RISK",
        "discovery_date": DISCOVERY_DATE,
        "page_hash_sha256": page_hash,
        "raw_provider_values_logged": False,
        "events": [vars(found[k]) for k in sorted(found)],
        "missing_event_names": missing,
        "historical_exact_pre_release_timestamp_proven": False,
        "prospective_capture_required": True,
    }


def main() -> int:
    actual = audit_alfred_actuals()
    try:
        consensus = discover_investing_cpi_metadata()
    except Exception as exc:
        consensus = {
            "status": "BLOCKED_INVESTING_DISCOVERY",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "events": [],
            "historical_exact_pre_release_timestamp_proven": False,
            "prospective_capture_required": True,
        }
    output = {
        "engine_id": "MACRO_EVENT_SUCCESSOR_V3",
        "family": "INFLATION",
        "definition": "CPI_MOM_SA_PLUS_CORE_CPI_MOM_SA",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "actual_first_print": actual,
        "consensus_source_discovery": consensus,
        "source_readiness": (
            "PARTIAL_ACTUAL_METHOD_PASS_CONSENSUS_PROSPECTIVE_CAPTURE_REQUIRED"
            if actual["status"].startswith("PASS") and consensus.get("status") == "PASS_EVENT_IDENTITIES_DISCOVERED"
            else "BLOCKED_SOURCE_AUDIT"
        ),
        "historical_locked_validation_authorized": False,
        "production_db_write": False,
        "market_shock_threshold_changed": False,
        "scope_expanded_beyond_cpi_core_cpi": False,
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
