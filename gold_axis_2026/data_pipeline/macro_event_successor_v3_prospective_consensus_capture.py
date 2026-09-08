from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

BASE = "https://www.investing.com/economic-calendar/"
FILTERED = BASE + "Service/getCalendarFilteredData"

FAMILY_EVENTS = {
    "EMPLOYMENT": {
        "Nonfarm Payrolls": "MACRO_NFP_CONSENSUS_PIT",
        "Unemployment Rate": "MACRO_UNEMP_CONSENSUS_PIT",
        "Average Hourly Earnings (MoM)": "MACRO_AHE_CONSENSUS_PIT",
    },
    "INFLATION": {
        "CPI (MoM)": "MACRO_CPI_CONSENSUS_PIT",
        "Core CPI (MoM)": "MACRO_CORE_CPI_CONSENSUS_PIT",
    },
}

# Investing appends the reference month to current-calendar event labels, e.g.
# "CPI (MoM) (Mar)". V3 normalizes only this terminal month suffix; it does
# not fuzzy-match, rename event families, or broaden scope.
_REFERENCE_MONTH_SUFFIX = re.compile(
    r"\s+\((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\)$"
)


@dataclass(frozen=True)
class ConsensusSnapshot:
    family: str
    event_name: str
    series_id: str
    event_attr_id: str
    event_row_id: str | None
    provider_event_datetime: str | None
    consensus_value: float
    unit: str
    captured_at: str
    official_release_at: str
    provider: str
    payload_hash_sha256: str
    evidence_class: str = "PROSPECTIVE_PRE_RELEASE_CAPTURE"
    provider_exact_update_timestamp_proven: bool = False
    capture_timestamp_proven: bool = True


def headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE,
        "Origin": "https://www.investing.com",
    }


def parse_number(text: str) -> tuple[float | None, str | None]:
    s = text.strip().replace(",", "")
    if not s or s in {"-", "--", "N/A"}:
        return None, None
    unit = "raw"
    mult = 1.0
    if s.endswith("%"):
        unit = "percent"
        s = s[:-1]
    elif s.endswith("K"):
        unit = "thousand"
        s = s[:-1]
    elif s.endswith("M"):
        unit = "thousand"
        mult = 1000.0
        s = s[:-1]
    try:
        return float(s) * mult, unit
    except ValueError:
        return None, None


def normalize_event_name(name: str) -> str:
    return _REFERENCE_MONTH_SUFFIX.sub("", " ".join(name.split())).strip()


def _defaults(session: requests.Session) -> tuple[str, str]:
    r = session.get(BASE, headers=headers(), timeout=(10, 40))
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tz = "55"
    time_filter = "timeRemain"
    select = soup.find("select", {"id": "timeZone"})
    if select:
        selected = select.find("option", selected=True)
        if selected and selected.get("value"):
            tz = str(selected["value"])
    checked = soup.find("input", {"name": "timeFilter", "checked": True})
    if checked and checked.get("value"):
        time_filter = str(checked["value"])
    return tz, time_filter


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


def _forecast_text(row) -> str:
    cell = row.select_one("td.fore")
    return " ".join(cell.get_text(" ", strip=True).split()) if cell else ""


def fetch_calendar_html(event_date: str) -> tuple[str, str]:
    session = requests.Session()
    tz, time_filter = _defaults(session)
    payload = [
        ("dateFrom", event_date),
        ("dateTo", event_date),
        ("timeZone", tz),
        ("timeFilter", time_filter),
        ("currentTab", "custom"),
        ("submitFilters", "1"),
        ("limit_from", "0"),
    ]
    r = session.post(FILTERED, data=payload, headers=headers(), timeout=(10, 40))
    if r.status_code == 429:
        raise RuntimeError("INVESTING_RATE_LIMIT")
    r.raise_for_status()
    body = r.json()
    html = str(body.get("data") or "")
    if not html:
        raise RuntimeError("INVESTING_CALENDAR_NO_DATA")
    return html, hashlib.sha256(html.encode("utf-8")).hexdigest()


def capture(family: str, event_date: str, official_release_at: datetime, captured_at: datetime | None = None) -> dict[str, Any]:
    family = family.upper()
    if family not in FAMILY_EVENTS:
        raise ValueError(f"UNSUPPORTED_FAMILY:{family}")
    if official_release_at.tzinfo is None:
        raise ValueError("OFFICIAL_RELEASE_AT_MUST_BE_TIMEZONE_AWARE")
    captured = captured_at or datetime.now(timezone.utc)
    if captured.tzinfo is None:
        raise ValueError("CAPTURED_AT_MUST_BE_TIMEZONE_AWARE")
    release_utc = official_release_at.astimezone(timezone.utc)
    captured_utc = captured.astimezone(timezone.utc)
    if not captured_utc < release_utc:
        raise RuntimeError("NOT_PRE_RELEASE_CAPTURE")

    html, response_hash = fetch_calendar_html(event_date)
    soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
    required = FAMILY_EVENTS[family]
    snapshots: dict[str, ConsensusSnapshot] = {}
    duplicates: list[str] = []

    for row in soup.find_all("tr"):
        name = _event_name(row)
        if name not in required or _currency(row) != "USD":
            continue
        if name in snapshots:
            duplicates.append(name)
            continue
        attr = row.get("event_attr_id") or row.get("event_attr_ID")
        if not attr:
            continue
        value, unit = parse_number(_forecast_text(row))
        if value is None or unit is None:
            continue
        normalized = {
            "family": family,
            "event_name": name,
            "series_id": required[name],
            "event_attr_id": str(attr),
            "consensus_value": value,
            "unit": unit,
            "captured_at": captured_utc.isoformat(),
            "official_release_at": release_utc.isoformat(),
            "provider_response_hash": response_hash,
        }
        snapshots[name] = ConsensusSnapshot(
            family=family,
            event_name=name,
            series_id=required[name],
            event_attr_id=str(attr),
            event_row_id=str(row.get("id")) if row.get("id") else None,
            provider_event_datetime=str(row.get("data-event-datetime") or row.get("event_timestamp") or "") or None,
            consensus_value=value,
            unit=unit,
            captured_at=captured_utc.isoformat(),
            official_release_at=release_utc.isoformat(),
            provider="INVESTING_COM_ECONOMIC_CALENDAR_RESEARCH_ONLY",
            payload_hash_sha256=hashlib.sha256(
                json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
        )

    missing = [name for name in required if name not in snapshots]
    status = "PASS_PROSPECTIVE_PRE_RELEASE_CAPTURE" if not missing and not duplicates else "BLOCKED_INCOMPLETE_PROSPECTIVE_CAPTURE"
    return {
        "engine_id": "MACRO_EVENT_SUCCESSOR_V3",
        "family": family,
        "status": status,
        "event_date": event_date,
        "captured_at": captured_utc.isoformat(),
        "official_release_at": release_utc.isoformat(),
        "capture_before_release": captured_utc < release_utc,
        "provider_response_hash_sha256": response_hash,
        "required_event_names": list(required),
        "missing_event_names": missing,
        "duplicate_event_names": duplicates,
        "snapshots": [asdict(snapshots[name]) for name in sorted(snapshots)],
        "historical_backdating": False,
        "production_db_write": False,
        "market_shock_threshold_changed": False,
        "raw_market_shock_episode_changed": False,
    }


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=sorted(FAMILY_EVENTS))
    ap.add_argument("--event-date", required=True)
    ap.add_argument("--official-release-at", required=True)
    ap.add_argument("--out", default="macro_event_successor_v3_prospective_consensus_capture.json")
    args = ap.parse_args()
    result = capture(args.family, args.event_date, parse_iso(args.official_release_at))
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
