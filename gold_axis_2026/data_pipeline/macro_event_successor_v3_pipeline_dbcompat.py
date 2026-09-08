from __future__ import annotations

import hashlib
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from psycopg.rows import dict_row

import macro_event_successor_v3_pipeline as core

_INV_SESSION = requests.Session()
_INV_DEFAULTS: tuple[str, str] | None = None
_CONSENSUS_CACHE: dict[str, tuple[dict[str, float], str]] = {}
_MONTH_SUFFIX_CAPTURE = re.compile(r"\s+\((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\)$")
_MONTH_NUM = {m: i for i, m in enumerate(("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"), 1)}


def fetch_existing_dbcompat(conn, series_ids: list[str]) -> list[dict]:
    """Read only columns that production canonical_latest actually exposes."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select series_id, observation_ts, value, available_as_of,
                   quality_status, lineage_id, metadata
            from canonical_latest
            where series_id = any(%s)
            order by observation_ts, series_id
            """,
            (series_ids,),
        )
        return [dict(x) for x in cur.fetchall()]


def previous_month_key(d: datetime) -> str:
    if d.month == 1:
        return f"{d.year - 1:04d}-12"
    return f"{d.year:04d}-{d.month - 1:02d}"


def investing_defaults_once() -> tuple[str, str]:
    global _INV_DEFAULTS
    if _INV_DEFAULTS is not None:
        return _INV_DEFAULTS
    r = _INV_SESSION.get(core.INVESTING_BASE, headers=core.inv_headers(), timeout=(10, 60))
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tz, tf = "55", "timeRemain"
    sel = soup.find("select", {"id": "timeZone"})
    if sel:
        opt = sel.find("option", selected=True)
        if opt and opt.get("value"):
            tz = str(opt["value"])
    chk = soup.find("input", {"name": "timeFilter", "checked": True})
    if chk and chk.get("value"):
        tf = str(chk["value"])
    _INV_DEFAULTS = (tz, tf)
    return _INV_DEFAULTS


def _post_calendar_range(start_date: str, end_date: str) -> tuple[str, str]:
    """Fetch one US-only calendar range with bounded retry and return HTML + SHA256."""
    tz, tf = investing_defaults_once()
    payload = [
        ("dateFrom", start_date), ("dateTo", end_date), ("timeZone", tz),
        ("timeFilter", tf), ("currentTab", "custom"), ("submitFilters", "1"),
        ("limit_from", "0"), ("country[]", "5"),
    ]
    last_status: int | None = None
    for attempt in range(8):
        r = _INV_SESSION.post(core.INVESTING_FILTERED, data=payload, headers=core.inv_headers(), timeout=(10, 60))
        last_status = r.status_code
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            try:
                wait = float(retry_after) if retry_after else min(5.0 * (attempt + 1), 30.0)
            except ValueError:
                wait = min(5.0 * (attempt + 1), 30.0)
            time.sleep(max(wait, 2.0)); continue
        if 500 <= r.status_code < 600:
            time.sleep(min(3.0 * (attempt + 1), 20.0)); continue
        r.raise_for_status()
        body = r.json(); html = str(body.get("data") or "")
        if not html:
            raise RuntimeError(f"INVESTING_NO_DATA:{start_date}:{end_date}")
        return html, hashlib.sha256(html.encode()).hexdigest()
    raise RuntimeError(f"INVESTING_RANGE_RETRY_EXHAUSTED:{start_date}:{end_date}:{last_status}")


def _parse_us_cpi_pairs(html: str, digest: str) -> dict[str, tuple[dict[str, float], str, str, str]]:
    """Return exact US CPI/Core MoM pairs keyed by release date.

    Each value is (consensus dict, digest, provider datetime, reference month).
    No other country, CPI flavor, event ID, or incomplete pair is accepted.
    """
    soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
    grouped: dict[str, dict] = {}
    us_event_rows = 0
    for tr in soup.find_all("tr"):
        cell = tr.select_one("td.event")
        if not cell:
            continue
        flag = tr.select_one("td.flagCur span")
        country = str(flag.get("title") or "") if flag else ""
        if country != "United States":
            continue
        us_event_rows += 1
        attr = str(tr.get("event_attr_id") or tr.get("event_attr_ID") or "")
        if attr not in {"69", "56"}:
            continue
        raw_name = " ".join(cell.get_text(" ", strip=True).split())
        normalized = core.normalize_event_name(raw_name)
        expected_name = "CPI (MoM)" if attr == "69" else "Core CPI (MoM)"
        if normalized != expected_name:
            continue
        fore = tr.select_one("td.fore")
        value = core.parse_provider_number(fore.get_text(" ", strip=True) if fore else "")
        pdt = str(tr.get("data-event-datetime") or tr.get("event_timestamp") or "")
        if value is None or not pdt:
            continue
        try:
            pdt_obj = datetime.strptime(pdt, "%Y/%m/%d %H:%M:%S").replace(tzinfo=core.UTC)
        except ValueError as exc:
            raise RuntimeError(f"INVESTING_BAD_EVENT_DATETIME:{pdt}") from exc
        month_match = _MONTH_SUFFIX_CAPTURE.search(raw_name)
        if not month_match:
            raise RuntimeError(f"INVESTING_CPI_REFERENCE_MONTH_SUFFIX_MISSING:{raw_name}:{pdt}")
        month_num = _MONTH_NUM[month_match.group(1)]
        ref_year = pdt_obj.year if month_num <= pdt_obj.month else pdt_obj.year - 1
        ref_key = f"{ref_year:04d}-{month_num:02d}"
        date_key = pdt_obj.date().isoformat()
        g = grouped.setdefault(date_key, {"values": {}, "timestamps": set(), "refs": set()})
        g["values"][expected_name] = float(value)
        g["timestamps"].add(pdt)
        g["refs"].add(ref_key)
    # A half-year US-only response should be comfortably below the provider's ~200-row cap.
    # If not, fail closed rather than silently accepting a truncated calendar page.
    if us_event_rows >= 190:
        raise RuntimeError(f"INVESTING_RANGE_POSSIBLY_TRUNCATED:{us_event_rows}")
    out: dict[str, tuple[dict[str, float], str, str, str]] = {}
    for date_key, g in grouped.items():
        if set(g["values"]) != {"CPI (MoM)", "Core CPI (MoM)"}:
            continue
        if len(g["timestamps"]) != 1 or len(g["refs"]) != 1:
            raise RuntimeError(f"INVESTING_CPI_PAIR_AMBIGUOUS:{date_key}:{g}")
        out[date_key] = (dict(g["values"]), digest, next(iter(g["timestamps"])), next(iter(g["refs"])))
    return out


def _bulk_us_cpi_history(start_year: int, end_year: int) -> dict[str, tuple[dict[str, float], str, str, str]]:
    """Load exact CPI/Core pairs in two US-only calendar calls per year."""
    out: dict[str, tuple[dict[str, float], str, str, str]] = {}
    today = datetime.now(core.UTC).date()
    for year in range(start_year, end_year + 1):
        ranges = [(f"{year}-01-01", f"{year}-06-30"), (f"{year}-07-01", f"{year}-12-31")]
        for start_date, end_date in ranges:
            if datetime.strptime(start_date, "%Y-%m-%d").date() > today:
                continue
            if datetime.strptime(end_date, "%Y-%m-%d").date() > today:
                end_date = today.isoformat()
            html, digest = _post_calendar_range(start_date, end_date)
            pairs = _parse_us_cpi_pairs(html, digest)
            overlap = set(out).intersection(pairs)
            if overlap:
                raise RuntimeError(f"INVESTING_CPI_DUPLICATE_DATES_ACROSS_RANGES:{sorted(overlap)}")
            out.update(pairs)
            time.sleep(1.0)
    return out


def official_cpi_release_schedule(start_year: int, end_year: int) -> list[dict]:
    """Cross-validate FRED CPI release dates against bulk exact US CPI/Core provider rows."""
    key = core.require_env("FRED_API_KEY")
    base = "https://api.stlouisfed.org/fred"
    rel = core.get(base + "/series/release", params={"series_id": "CPIAUCSL", "api_key": key, "file_type": "json"}).json()
    releases = rel.get("releases") or []
    if len(releases) != 1 or int(releases[0].get("id", -1)) != 10 or str(releases[0].get("name")) != "Consumer Price Index":
        raise RuntimeError(f"CPI_RELEASE_IDENTITY_MISMATCH:{releases}")
    payload = core.get(
        base + "/release/dates",
        params={
            "release_id": 10, "api_key": key, "file_type": "json",
            "realtime_start": f"{start_year}-01-01",
            "realtime_end": datetime.now(core.UTC).date().isoformat(),
            "limit": 10000, "sort_order": "asc",
        },
    ).json()
    official_dates = {str(x["date"]) for x in (payload.get("release_dates") or [])}
    provider_pairs = _bulk_us_cpi_history(start_year, end_year)
    out: list[dict] = []
    seen_refs: set[str] = set()
    for date_key in sorted(set(provider_pairs).intersection(official_dates)):
        consensus, digest, provider_dt, ref_key = provider_pairs[date_key]
        d = datetime.strptime(date_key, "%Y-%m-%d")
        release_local = datetime(d.year, d.month, d.day, 8, 30, tzinfo=core.ET)
        expected_utc = release_local.astimezone(core.UTC).strftime("%Y/%m/%d %H:%M:%S")
        if provider_dt != expected_utc:
            raise RuntimeError(f"CPI_RELEASE_TIMESTAMP_MISMATCH:{date_key}:{provider_dt}:{expected_utc}")
        expected_ref = previous_month_key(d)
        if ref_key != expected_ref:
            raise RuntimeError(f"CPI_REFERENCE_MONTH_MISMATCH:{date_key}:{ref_key}:{expected_ref}")
        if ref_key in seen_refs:
            raise RuntimeError(f"DUPLICATE_CONFIRMED_CPI_REFERENCE_MONTH:{ref_key}")
        seen_refs.add(ref_key)
        _CONSENSUS_CACHE[date_key] = (consensus, digest)
        out.append({
            "reference_month": ref_key,
            "release_at": release_local.astimezone(core.UTC),
            "release_date": date_key,
            "authority_url": "FRED_RELEASE_ID_10_PLUS_EXACT_US_CPI69_CORE56_0830ET_BULK_MATCH",
        })
    # Jan 2016 through Aug 2026 is 128 ordinary monthly releases; allow a small
    # bounded margin for unusual source omissions, but never accept sparse history.
    if len(out) < 120:
        raise RuntimeError(
            f"CONFIRMED_CPI_RELEASE_COVERAGE_TOO_SHORT:{len(out)}:provider_pairs={len(provider_pairs)}:official_dates={len(official_dates)}"
        )
    return out


def historical_cpi_consensus_cached(release_date: str) -> tuple[dict[str, float], str]:
    value = _CONSENSUS_CACHE.get(release_date)
    if value is None:
        raise RuntimeError(f"CPI_CONSENSUS_CACHE_MISS_AFTER_BULK_VALIDATION:{release_date}")
    return value


core.fetch_existing = fetch_existing_dbcompat
core.bls_cpi_schedule = official_cpi_release_schedule
core.historical_cpi_consensus = historical_cpi_consensus_cached

if __name__ == "__main__":
    raise SystemExit(core.main())
