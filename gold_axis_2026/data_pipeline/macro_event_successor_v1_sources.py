from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin
from zoneinfo import ZoneInfo

import requests

BLS_ARCHIVE_INDEX = "https://www.bls.gov/bls/news-release/empsit.htm"
TE_BASE = "https://api.tradingeconomics.com"
PIPELINE_VERSION = "MACRO_EVENT_SUCCESSOR_V1_SOURCE_AUDIT_2026-09-05"
NY = ZoneInfo("America/New_York")

SERIES = {
    "nfp": ("MACRO_NFP_ACTUAL_FIRST_PRINT", "thousand_persons_change"),
    "unemp": ("MACRO_UNEMP_ACTUAL_FIRST_PRINT", "percent"),
    "ahe": ("MACRO_AHE_ACTUAL_FIRST_PRINT", "percent_mom"),
}
TE_INDICATORS = {
    "nfp": "non farm payrolls",
    "unemp": "unemployment rate",
    "ahe": "average hourly earnings mom",
}
MONTHS = {
    name.lower(): i
    for i, name in enumerate(
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        1,
    )
}


class LinkAndTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(str(href))

    def handle_data(self, data: str) -> None:
        if data and data.strip():
            self.parts.append(data.strip())

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


@dataclass(frozen=True)
class ParsedRelease:
    reference_month: str
    release_ts: datetime
    nfp_thousands: float
    unemployment_pct: float
    ahe_mom_pct: float
    ahe_transform: str


def get(session: requests.Session, url: str, **kwargs) -> requests.Response:
    headers = dict(kwargs.pop("headers", {}) or {})
    headers.setdefault("User-Agent", "Gold-Control-Macro-Event-Source-Audit/1.0")
    r = session.get(url, headers=headers, timeout=(10, 45), **kwargs)
    r.raise_for_status()
    return r


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def reference_month_from_text(text: str) -> str:
    patterns = [
        r"THE EMPLOYMENT SITUATION\s*--\s*([A-Z]+)\s+(20\d{2})",
        r"Employment Situation\s*[-–—]{1,2}\s*([A-Za-z]+)\s+(20\d{2})",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m and m.group(1).lower() in MONTHS:
            return f"{int(m.group(2)):04d}-{MONTHS[m.group(1).lower()]:02d}"
    raise ValueError("BLS_REFERENCE_MONTH_NOT_FOUND")


def release_ts_from_url(url: str) -> datetime:
    m = re.search(r"empsit_(\d{2})(\d{2})(\d{4})\.htm", url, re.I)
    if not m:
        raise ValueError("BLS_RELEASE_DATE_NOT_IN_URL")
    month, day, year = map(int, m.groups())
    return datetime(year, month, day, 8, 30, tzinfo=NY)


def parse_nfp(text: str) -> float:
    pos = text.lower().find("nonfarm payroll employment")
    if pos < 0:
        raise ValueError("BLS_NFP_ANCHOR_NOT_FOUND")
    window = text[pos:pos + 900]
    m = re.search(r"changed\s+(?:very\s+)?little\s*\(\s*([+-])\s*([\d,]+)\s*\)", window, re.I)
    if not m:
        m = re.search(r"(?:was\s+)?(?:little|essentially)\s+changed\s*\(\s*([+-])\s*([\d,]+)\s*\)", window, re.I)
    if m:
        v = float(m.group(2).replace(",", "")) / 1000.0
        return v if m.group(1) == "+" else -v
    m = re.search(r"(?:increased|rose|grew|advanced|gained)\s+by\s+([\d,]+)", window, re.I)
    if m:
        return float(m.group(1).replace(",", "")) / 1000.0
    m = re.search(r"(?:decreased|declined|fell|dropped)\s+by\s+([\d,]+)", window, re.I)
    if m:
        return -float(m.group(1).replace(",", "")) / 1000.0
    raise ValueError("BLS_NFP_VALUE_NOT_FOUND")


def parse_unemployment(text: str) -> float:
    pos = text.lower().find("unemployment rate")
    if pos < 0:
        raise ValueError("BLS_UNEMP_ANCHOR_NOT_FOUND")
    window = text[pos:pos + 650]
    for pat in [
        r"unemployment rate.{0,180}?(?:to|at|was)\s+([0-9]+(?:\.[0-9]+)?)\s+percent",
        r"unemployment rate\s*\(\s*([0-9]+(?:\.[0-9]+)?)\s+percent\s*\)",
    ]:
        m = re.search(pat, window, re.I)
        if m:
            v = float(m.group(1))
            if 0 <= v <= 30:
                return v
    raise ValueError("BLS_UNEMP_VALUE_NOT_FOUND")


def parse_ahe(text: str) -> tuple[float, str]:
    low = text.lower()
    pos = -1
    for anchor in [
        "average hourly earnings for all employees on private nonfarm payrolls",
        "average hourly earnings for all employees on private nonfarm",
        "average hourly earnings",
    ]:
        pos = low.find(anchor)
        if pos >= 0:
            break
    if pos < 0:
        raise ValueError("BLS_AHE_ANCHOR_NOT_FOUND")
    window = text[pos:pos + 900]

    up = r"rose|increased|advanced|grew|edged\s+up|was\s+up"
    down = r"declined|decreased|fell|edged\s+down|was\s+down"

    # Modern wording: "rose by 10 cents, or 0.3 percent" or "$0.10, or 0.3 percent".
    for verbs, sign in [(up, 1.0), (down, -1.0)]:
        m = re.search(
            rf"(?:{verbs})\s+(?:by\s+)?\$?[0-9]+(?:\.[0-9]+)?\s*(?:cents?)?\s*,\s*or\s+([0-9]+(?:\.[0-9]+)?)\s+percent",
            window,
            re.I,
        )
        if m:
            return sign * float(m.group(1)), "PUBLISHED_MOM_PERCENT"
        m = re.search(
            rf"(?:{verbs})\s+(?:by\s+)?([0-9]+(?:\.[0-9]+)?)\s+percent",
            window,
            re.I,
        )
        if m:
            return sign * float(m.group(1)), "PUBLISHED_MOM_PERCENT"

    # Older wording: cents change plus current level; derive transparently from the same first release.
    cents = re.search(rf"(?:{up})\s*(?:by\s*)?\(?\+?([0-9]+)\s+cents?\)?", window, re.I)
    sign = 1.0
    if not cents:
        cents = re.search(rf"(?:{down})\s*(?:by\s*)?\(?-?([0-9]+)\s+cents?\)?", window, re.I)
        sign = -1.0
    level = re.search(r"to\s+\$([0-9]+(?:\.[0-9]+)?)", window, re.I)
    if cents and level:
        delta = sign * float(cents.group(1)) / 100.0
        current = float(level.group(1))
        previous = current - delta
        if previous <= 0:
            raise ValueError("BLS_AHE_DERIVED_PREVIOUS_NONPOSITIVE")
        return (current / previous - 1.0) * 100.0, "DERIVED_FROM_FIRST_RELEASE_CENTS_AND_LEVEL"
    raise ValueError("BLS_AHE_VALUE_NOT_FOUND")


def parse_release(url: str, html: str) -> ParsedRelease:
    p = LinkAndTextParser()
    p.feed(html)
    text = p.text
    ahe, transform = parse_ahe(text)
    return ParsedRelease(
        reference_month_from_text(text),
        release_ts_from_url(url),
        parse_nfp(text),
        parse_unemployment(text),
        ahe,
        transform,
    )


def discover_archive_urls(session: requests.Session) -> list[str]:
    r = get(session, BLS_ARCHIVE_INDEX)
    p = LinkAndTextParser()
    p.feed(r.text)
    urls = []
    for href in p.links:
        u = urljoin(BLS_ARCHIVE_INDEX, href)
        if re.search(r"/news\.release/archives/empsit_\d{8}\.htm$", u, re.I):
            urls.append(u)
    return sorted(set(urls))


def make_observation(run_id: str, series_id: str, release_ts: datetime, value: float, unit: str,
                     retrieved_at: datetime, payload_hash: str, reference_month: str, url: str,
                     transform: str) -> dict:
    release_iso, retrieved_iso = iso(release_ts), iso(retrieved_at)
    return {
        "run_id": run_id,
        "series_id": series_id,
        "observation_ts": release_iso,
        "value": float(value),
        "source": "U.S. Bureau of Labor Statistics Employment Situation archive",
        "source_symbol": "EMPSIT_FIRST_PRINT",
        "provider_as_of": release_iso,
        "available_as_of": release_iso,
        "first_seen_at": retrieved_iso,
        "retrieved_at": retrieved_iso,
        "frequency": "event_monthly",
        "unit": unit,
        "transform": transform,
        "quality_status": "CANDIDATE_AUTHORITY_FIRST_PRINT_AUDIT",
        "lineage_id": f"BLS_EMPSIT_{reference_month.replace('-', '')}:{series_id}",
        "payload_hash": payload_hash,
        "metadata": {
            "event_family": "BLS_EMPLOYMENT_SITUATION",
            "reference_month": reference_month,
            "official_release_url": url,
            "release_timezone": "America/New_York",
            "release_clock_time": "08:30",
            "first_print": True,
            "historical_reconstruction_not_original_retrieval": True,
            "current_vintage_substitution": False,
        },
    }


def _expected_months(start_ref: str, end_ref: str) -> list[str]:
    y, m = map(int, start_ref.split("-"))
    ey, em = map(int, end_ref.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def build_bls_bundle(start_ref: str, end_ref: str) -> tuple[dict, dict]:
    retrieved_at = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    session = requests.Session()
    urls = discover_archive_urls(session)
    start_year, end_year = int(start_ref[:4]), int(end_ref[:4])

    observations, vintages, failures, releases = [], [], [], []
    for url in urls:
        try:
            url_year = release_ts_from_url(url).year
            if url_year < start_year or url_year > end_year + 1:
                continue
            r = get(session, url)
            parsed = parse_release(url, r.text)
            if not (start_ref <= parsed.reference_month <= end_ref):
                continue
            ph = sha256_bytes(r.content)
            vals = {"nfp": parsed.nfp_thousands, "unemp": parsed.unemployment_pct, "ahe": parsed.ahe_mom_pct}
            trans = {"nfp": "first_print_release_value", "unemp": "first_print_release_value", "ahe": parsed.ahe_transform}
            for key, value in vals.items():
                sid, unit = SERIES[key]
                observations.append(make_observation(run_id, sid, parsed.release_ts, value, unit, retrieved_at,
                                                     ph, parsed.reference_month, url, trans[key]))
            vintages.append({
                "source_id": f"BLS_EMPSIT_ARCHIVE_{parsed.reference_month.replace('-', '')}",
                "retrieved_at": iso(retrieved_at),
                "provider_as_of": iso(parsed.release_ts),
                "content_sha256": ph,
                "content_type": r.headers.get("Content-Type", "text/html"),
                "byte_count": len(r.content),
                "metadata": {
                    "reference_month": parsed.reference_month,
                    "official_release_url": url,
                    "historical_reconstruction_not_original_retrieval": True,
                },
            })
            releases.append({
                "reference_month": parsed.reference_month,
                "release_ts": iso(parsed.release_ts),
                "nfp_thousands": parsed.nfp_thousands,
                "unemployment_pct": parsed.unemployment_pct,
                "ahe_mom_pct": parsed.ahe_mom_pct,
                "ahe_transform": parsed.ahe_transform,
                "url": url,
            })
        except Exception as exc:
            failures.append({"url": url, "error": f"{type(exc).__name__}:{exc}"})

    releases.sort(key=lambda x: x["reference_month"])
    present = {x["reference_month"] for x in releases}
    missing = [x for x in _expected_months(start_ref, end_ref) if x not in present]
    structural_missing = [x for x in missing if x == "2025-10"]
    unexpected_missing = [x for x in missing if x not in structural_missing]
    quality_events = [{
        "run_id": run_id,
        "series_id": None,
        "event_ts": iso(retrieved_at),
        "severity": "ERROR",
        "code": "BLS_UNEXPECTED_REFERENCE_MONTH_MISSING",
        "message": x,
        "metadata": {},
    } for x in unexpected_missing]

    bundle = {
        "run_id": run_id,
        "started_at": iso(retrieved_at),
        "finished_at": iso(datetime.now(timezone.utc)),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "historical_replay_reconstruction:bls_employment_situation",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "observations": observations,
        "vintages": vintages,
        "quality_events": quality_events,
        "metadata": {
            "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
            "start_reference_month": start_ref,
            "end_reference_month": end_ref,
            "historical_reconstruction_not_original_retrieval": True,
            "current_vintage_substitution_allowed": False,
            "forecast_or_decision_write": False,
        },
    }
    summary = {
        "status": "PASS" if not unexpected_missing and not failures else "FAIL",
        "start_reference_month": start_ref,
        "end_reference_month": end_ref,
        "release_count": len(releases),
        "observation_count": len(observations),
        "first_reference_month": releases[0]["reference_month"] if releases else None,
        "last_reference_month": releases[-1]["reference_month"] if releases else None,
        "missing_reference_months": missing,
        "structural_missing_reference_months": structural_missing,
        "unexpected_missing_reference_months": unexpected_missing,
        "parse_failure_count": len(failures),
        "parse_failures": failures,
        "ahe_published_percent_count": sum(x["ahe_transform"] == "PUBLISHED_MOM_PERCENT" for x in releases),
        "ahe_derived_count": sum(x["ahe_transform"] == "DERIVED_FROM_FIRST_RELEASE_CENTS_AND_LEVEL" for x in releases),
        "decision_store_writes": 0,
        "model_score_run": False,
    }
    return bundle, summary


def audit_te_pit(api_key: str, start_date: str, end_date: str) -> dict:
    session = requests.Session()
    out = {
        "provider": "Trading Economics Economic Calendar Point-in-Time",
        "status": "PASS_PROBE_ONLY",
        "approved_for_model_use": False,
        "indicators": {},
    }
    for key, indicator in TE_INDICATORS.items():
        url = f"{TE_BASE}/calendar/country/united%20states/indicator/{quote(indicator, safe='')}/{start_date}/{end_date}"
        payload = get(session, url, params={"c": api_key, "f": "json"}).json()
        if not isinstance(payload, list):
            raise ValueError(f"TE_PIT_SCHEMA_{key}")
        rows = []
        for item in payload:
            if isinstance(item, dict):
                rows.append({
                    "CalendarId": item.get("CalendarId"),
                    "Date": item.get("Date"),
                    "Reference": item.get("Reference"),
                    "ReferenceDate": item.get("ReferenceDate"),
                    "Forecast_present": bool(str(item.get("Forecast") or "").strip()),
                    "LastUpdate": item.get("LastUpdate"),
                    "Revised_present": bool(str(item.get("Revised") or "").strip()),
                    "Ticker": item.get("Ticker"),
                    "Symbol": item.get("Symbol"),
                })
        out["indicators"][key] = {
            "indicator": indicator,
            "row_count": len(rows),
            "forecast_present_count": sum(x["Forecast_present"] for x in rows),
            "rows": rows,
        }
    return out


def write_md(path: Path, summary: dict, consensus: dict) -> None:
    path.write_text("\n".join([
        "# Macro Event Successor V1 — Source/PIT Readiness Audit", "",
        f"- BLS status: `{summary['status']}`",
        f"- BLS releases: `{summary['release_count']}`",
        f"- BLS observations: `{summary['observation_count']}`",
        f"- First/last reference: `{summary['first_reference_month']}` / `{summary['last_reference_month']}`",
        f"- Structural missing: `{summary['structural_missing_reference_months']}`",
        f"- Unexpected missing: `{summary['unexpected_missing_reference_months']}`",
        f"- Parse failures: `{summary['parse_failure_count']}`",
        f"- AHE published-percent rows: `{summary['ahe_published_percent_count']}`",
        f"- AHE transparently derived rows: `{summary['ahe_derived_count']}`",
        f"- Consensus PIT status: `{consensus['status']}`",
        "- Model score run: `NO`",
        "- Production DB write: `NO`",
        "- Forecast/Decision Store write: `NO`", "",
        "Consensus remains unapproved until a separate event-by-event pre-release chronology audit passes.",
    ]) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start-reference", default="2016-01")
    p.add_argument("--end-reference", default="2026-08")
    p.add_argument("--bundle-out", type=Path, default=Path("macro_event_bls_bundle_v1.json"))
    p.add_argument("--summary-out", type=Path, default=Path("macro_event_source_audit_v1.json"))
    p.add_argument("--md-out", type=Path, default=Path("macro_event_source_audit_v1.md"))
    p.add_argument("--te-start-date", default="2024-01-01")
    p.add_argument("--te-end-date", default="2026-09-05")
    args = p.parse_args()

    bundle, summary = build_bls_bundle(args.start_reference, args.end_reference)
    te_key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    if te_key:
        try:
            consensus = audit_te_pit(te_key, args.te_start_date, args.te_end_date)
        except Exception as exc:
            consensus = {
                "provider": "Trading Economics Economic Calendar Point-in-Time",
                "status": f"ERROR_{type(exc).__name__}",
                "approved_for_model_use": False,
                "error": str(exc),
            }
    else:
        consensus = {
            "provider": "Trading Economics Economic Calendar Point-in-Time",
            "status": "BLOCKED_PIT_CONSENSUS_PROVIDER_CREDENTIAL_NOT_CONFIGURED",
            "approved_for_model_use": False,
        }

    full = {"bls": summary, "consensus": consensus}
    args.bundle_out.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    args.summary_out.write_text(json.dumps(full, indent=2, sort_keys=True), encoding="utf-8")
    write_md(args.md_out, summary, consensus)
    print(json.dumps(full, indent=2, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
