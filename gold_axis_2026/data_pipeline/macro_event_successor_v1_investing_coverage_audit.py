from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

ENDPOINT = "https://www.investing.com/economic-calendar/more-history"
REFERER_BASE = "https://www.investing.com/economic-calendar/"

EVENTS = {
    "nfp": {
        "event_attr_id": "227",
        "name": "Nonfarm Payrolls",
        "unit": "thousand_persons_change",
    },
    "unemployment": {
        "event_attr_id": "300",
        "name": "Unemployment Rate",
        "unit": "percent",
    },
    "ahe_mom": {
        "event_attr_id": "8",
        "name": "Average Hourly Earnings MoM",
        "unit": "percent_mom",
    },
}

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


@dataclass(frozen=True)
class HistoryRow:
    release_date: date
    reference_month: str
    forecast: float | None
    actual: float | None
    previous: float | None


def _text(cell: Any) -> str:
    return " ".join(cell.get_text(" ", strip=True).split())


def parse_number(value: str) -> float | None:
    s = value.strip().replace(",", "")
    if not s or s in {"-", "--", "N/A"}:
        return None
    mult = 1.0
    if s.endswith("K"):
        mult = 1.0
        s = s[:-1]
    elif s.endswith("M"):
        mult = 1000.0
        s = s[:-1]
    if s.endswith("%"):
        s = s[:-1]
    try:
        return float(s) * mult
    except ValueError:
        return None


def parse_release_date_and_reference(value: str) -> tuple[date, str]:
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})(?:\s*\(([A-Z][a-z]{2})\))?", value)
    if not m:
        raise ValueError(f"UNPARSEABLE_RELEASE_DATE:{value}")
    rel_month, rel_day, rel_year, ref_mon = m.groups()
    rel = date(int(rel_year), MONTHS[rel_month], int(rel_day))
    if not ref_mon:
        ref_d = (rel.replace(day=1) - timedelta(days=1))
        return rel, f"{ref_d.year:04d}-{ref_d.month:02d}"
    ref_month_num = MONTHS[ref_mon]
    ref_year = rel.year - 1 if ref_month_num > rel.month else rel.year
    return rel, f"{ref_year:04d}-{ref_month_num:02d}"


def parse_history_rows(html: str) -> list[HistoryRow]:
    soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
    out: list[HistoryRow] = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue
        vals = [_text(td) for td in tds]
        try:
            rel, ref = parse_release_date_and_reference(vals[0])
        except Exception:
            continue
        out.append(
            HistoryRow(
                release_date=rel,
                reference_month=ref,
                actual=parse_number(vals[2]),
                forecast=parse_number(vals[3]),
                previous=parse_number(vals[4]),
            )
        )
    return out


def month_range(start_ym: str, end_ym: str) -> list[str]:
    sy, sm = map(int, start_ym.split("-"))
    ey, em = map(int, end_ym.split("-"))
    cur_y, cur_m = sy, sm
    out = []
    while (cur_y, cur_m) <= (ey, em):
        out.append(f"{cur_y:04d}-{cur_m:02d}")
        cur_m += 1
        if cur_m == 13:
            cur_m = 1
            cur_y += 1
    return out


def fetch_page(session: requests.Session, event_attr_id: str, anchor: date) -> dict[str, Any]:
    payload = {
        "eventID": "1",
        "event_attr_ID": event_attr_id,
        "event_timestamp": anchor.isoformat(),
        "is_speech": "0",
    }
    r = session.post(ENDPOINT, data=payload, timeout=25)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP_{r.status_code}")
    try:
        data = r.json()
    except Exception as exc:
        raise RuntimeError("NON_JSON_RESPONSE") from exc
    if not isinstance(data, dict) or "historyRows" not in data:
        raise RuntimeError("UNEXPECTED_RESPONSE_SCHEMA")
    return data


def fetch_event_history(event_attr_id: str, start_ref: str, end_ref: str) -> tuple[list[HistoryRow], dict[str, Any]]:
    expected = set(month_range(start_ref, end_ref))
    start_year, start_month = map(int, start_ref.split("-"))
    lower_bound = date(start_year, start_month, 1) - timedelta(days=45)
    anchor = datetime.now(timezone.utc).date()

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": REFERER_BASE,
        "Accept-Language": "en-US,en;q=0.9",
    })

    by_ref: dict[str, HistoryRow] = {}
    page_hashes: list[str] = []
    calls = 0
    status = "PASS_ENDPOINT_ACCESS"
    blocker = None

    while calls < 40:
        calls += 1
        try:
            payload = fetch_page(s, event_attr_id, anchor)
        except Exception as exc:
            status = "BLOCKED_PROVIDER_ENDPOINT"
            blocker = str(exc)
            break

        history_html = str(payload.get("historyRows") or "")
        page_hashes.append(hashlib.sha256(history_html.encode("utf-8")).hexdigest())
        rows = parse_history_rows(history_html)
        if not rows:
            status = "BLOCKED_EMPTY_OR_UNPARSEABLE_HISTORY"
            blocker = "NO_PARSED_ROWS"
            break

        for row in rows:
            if row.reference_month in expected and row.reference_month not in by_ref:
                by_ref[row.reference_month] = row

        oldest = min(r.release_date for r in rows)
        if expected.issubset(by_ref.keys()):
            break
        if oldest <= lower_bound:
            break
        new_anchor = oldest - timedelta(days=1)
        if new_anchor >= anchor:
            status = "BLOCKED_NON_DECREASING_HISTORY_CURSOR"
            blocker = f"anchor={anchor};oldest={oldest}"
            break
        anchor = new_anchor
        time.sleep(0.35)

    rows = [by_ref[k] for k in sorted(by_ref)]
    meta = {
        "endpoint_status": status,
        "blocker": blocker,
        "request_count": calls,
        "page_hash_count": len(page_hashes),
        "page_hash_chain": hashlib.sha256("".join(page_hashes).encode("utf-8")).hexdigest() if page_hashes else None,
    }
    return rows, meta


def summarize_event(rows: list[HistoryRow], expected_months: list[str], meta: dict[str, Any]) -> dict[str, Any]:
    row_map = {r.reference_month: r for r in rows}
    present = [m for m in expected_months if m in row_map]
    forecast_present = [m for m in expected_months if m in row_map and row_map[m].forecast is not None]
    missing_rows = [m for m in expected_months if m not in row_map]
    missing_forecasts = [m for m in expected_months if m in row_map and row_map[m].forecast is None]
    coverage = len(forecast_present) / len(expected_months) if expected_months else 0.0
    return {
        **meta,
        "expected_reference_months": len(expected_months),
        "rows_present": len(present),
        "forecasts_present": len(forecast_present),
        "forecast_coverage_ratio": round(coverage, 6),
        "first_reference_month": min(present) if present else None,
        "last_reference_month": max(present) if present else None,
        "missing_row_count": len(missing_rows),
        "missing_forecast_count": len(missing_forecasts),
        "missing_rows": missing_rows,
        "missing_forecasts": missing_forecasts,
        "raw_values_logged": False,
        "normalized_values_committed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-reference", default="2016-01")
    ap.add_argument("--end-reference", default="2026-08")
    ap.add_argument("--out", default="macro_event_investing_coverage_audit_v1.json")
    args = ap.parse_args()

    expected = month_range(args.start_reference, args.end_reference)
    results: dict[str, Any] = {}
    for key, spec in EVENTS.items():
        rows, meta = fetch_event_history(spec["event_attr_id"], args.start_reference, args.end_reference)
        results[key] = {
            "event": spec["name"],
            "event_attr_id": spec["event_attr_id"],
            "unit": spec["unit"],
            **summarize_event(rows, expected, meta),
        }

    endpoint_pass = all(v["endpoint_status"] == "PASS_ENDPOINT_ACCESS" for v in results.values())
    min_coverage = min((v["forecast_coverage_ratio"] for v in results.values()), default=0.0)
    if not endpoint_pass:
        status = "BLOCKED_INVESTING_HISTORY_ENDPOINT"
        approved = False
    elif min_coverage >= 0.98:
        status = "PASS_COVERAGE_RESEARCH_DATASET_ELIGIBLE"
        approved = True
    else:
        status = "FAIL_INSUFFICIENT_HISTORICAL_CONSENSUS_COVERAGE"
        approved = False

    out = {
        "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
        "provider": "Investing.com Economic Calendar",
        "provider_scope": "DOCTORAL_RESEARCH_INTERNAL_USER_ACCEPTED_LICENSE_RISK",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION_SOURCE_AUDIT",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reference_window": {"start": args.start_reference, "end": args.end_reference, "expected_months": len(expected)},
        "status": status,
        "eligible_for_research_ingestion": approved,
        "approval_threshold_forecast_coverage_ratio": 0.98,
        "results": results,
        "production_db_write": False,
        "model_score_run": False,
        "forecast_or_decision_write": False,
        "direction_vote": False,
        "raw_provider_payload_committed": False,
        "note": "Coverage audit only. Investing.com actual values are not model authority; BLS/ALFRED remains the first-print actual lane. Exact historical pre-release update timestamps are not inferred from this endpoint."
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
