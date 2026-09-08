from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.investing.com/economic-calendar/"
FILTERED = BASE + "Service/getCalendarFilteredData"
PROBE_DATE = "2026-04-10"
OUT = Path("macro_event_successor_v3_investing_cpi_identity_probe.json")


def headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE,
        "Origin": "https://www.investing.com",
    }


def defaults(session: requests.Session) -> tuple[str, str]:
    r = session.get(BASE, headers=headers(), timeout=(10, 40))
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tz = "55"
    tf = "timeRemain"
    sel = soup.select_one("select#timeZone option[selected]")
    if sel and sel.get("value"):
        tz = str(sel["value"])
    chk = soup.select_one('input[name="timeFilter"][checked]')
    if chk and chk.get("value"):
        tf = str(chk["value"])
    return tz, tf


def main() -> int:
    s = requests.Session()
    tz, tf = defaults(s)
    payload = [
        ("dateFrom", PROBE_DATE),
        ("dateTo", PROBE_DATE),
        ("timeZone", tz),
        ("timeFilter", tf),
        ("currentTab", "custom"),
        ("submitFilters", "1"),
        ("limit_from", "0"),
    ]
    r = s.post(FILTERED, data=payload, headers=headers(), timeout=(10, 40))
    if r.status_code == 429:
        result = {"status": "BLOCKED_PROVIDER_RATE_LIMIT", "probe_date": PROBE_DATE, "candidates": []}
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    r.raise_for_status()
    body = r.json()
    html = str(body.get("data") or "")
    if not html:
        raise RuntimeError("NO_CALENDAR_DATA")
    soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
    candidates = []
    row_count = 0
    for row in soup.select("tr"):
        row_count += 1
        event_cell = row.select_one("td.event")
        if not event_cell:
            continue
        name = " ".join(event_cell.get_text(" ", strip=True).split())
        if "CPI" not in name.upper():
            continue
        cur_cell = row.select_one("td.flagCur")
        currency_text = " ".join(cur_cell.get_text(" ", strip=True).split()) if cur_cell else ""
        if "USD" not in currency_text:
            continue
        attr = row.get("event_attr_id") or row.get("event_attr_ID")
        candidates.append({
            "event_name": name,
            "event_attr_id": str(attr) if attr else None,
            "event_row_id": str(row.get("id")) if row.get("id") else None,
            "provider_datetime": str(row.get("data-event-datetime") or row.get("event_timestamp") or "") or None,
            "forecast_cell_present": row.select_one("td.fore") is not None,
        })
    names = {c["event_name"] for c in candidates}
    exact = {"CPI (MoM)", "Core CPI (MoM)"}
    result = {
        "engine_id": "MACRO_EVENT_SUCCESSOR_V3",
        "family": "INFLATION",
        "status": "PASS_EXACT_CPI_EVENT_IDENTITIES_FOUND" if exact.issubset(names) else "BLOCKED_EXACT_CPI_EVENT_IDENTITIES_NOT_FOUND",
        "probe_date": PROBE_DATE,
        "response_hash_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "calendar_row_count": row_count,
        "candidates": candidates,
        "raw_provider_values_logged": False,
        "production_db_write": False,
        "historical_pit_claim": False,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
