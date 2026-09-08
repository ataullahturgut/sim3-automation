from __future__ import annotations

import hashlib
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from psycopg.rows import dict_row

import macro_event_successor_v3_pipeline as core

_INV_SESSION = requests.Session()
_INV_DEFAULTS: tuple[str, str] | None = None
_CONSENSUS_CACHE: dict[str, tuple[dict[str, float], str]] = {}


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


def consensus_and_timestamp_for_date(release_date: str) -> tuple[dict[str, float], str, str]:
    tz, tf = investing_defaults_once()
    payload = [
        ("dateFrom", release_date), ("dateTo", release_date), ("timeZone", tz),
        ("timeFilter", tf), ("currentTab", "custom"), ("submitFilters", "1"),
        ("limit_from", "0"),
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
            time.sleep(max(wait, 2.0))
            continue
        if 500 <= r.status_code < 600:
            time.sleep(min(3.0 * (attempt + 1), 20.0))
            continue
        r.raise_for_status()
        body = r.json(); html = str(body.get("data") or "")
        if not html:
            raise RuntimeError("INVESTING_NO_DATA")
        soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
        found: dict[str, float] = {}
        timestamps: set[str] = set()
        countries: set[str] = set()
        for tr in soup.find_all("tr"):
            cell = tr.select_one("td.event")
            if not cell:
                continue
            name = core.normalize_event_name(cell.get_text(" ", strip=True))
            if name not in core.INVESTING_IDS:
                continue
            attr = str(tr.get("event_attr_id") or tr.get("event_attr_ID") or "")
            if attr != core.INVESTING_IDS[name]:
                continue
            flag = tr.select_one("td.flagCur span")
            country = str(flag.get("title") or "") if flag else ""
            if country != "United States":
                continue
            fore = tr.select_one("td.fore")
            val = core.parse_provider_number(fore.get_text(" ", strip=True) if fore else "")
            pdt = str(tr.get("data-event-datetime") or tr.get("event_timestamp") or "")
            if val is not None and pdt:
                found[name] = val
                timestamps.add(pdt)
                countries.add(country)
        if set(found) != set(core.INVESTING_IDS) or len(timestamps) != 1 or countries != {"United States"}:
            raise RuntimeError(f"NO_EXACT_US_MONTHLY_CPI_PAIR:{sorted(found)}:{sorted(timestamps)}:{sorted(countries)}")
        digest = hashlib.sha256(html.encode()).hexdigest()
        return found, digest, next(iter(timestamps))
    raise RuntimeError(f"INVESTING_RATE_LIMIT_RETRY_EXHAUSTED:{release_date}:{last_status}")


def official_cpi_release_schedule(start_year: int, end_year: int) -> list[dict]:
    """Cross-validate official FRED CPI release dates with exact US provider event identities."""
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
    out: list[dict] = []
    seen: set[str] = set()
    diagnostics: list[str] = []
    for row in payload.get("release_dates") or []:
        d = datetime.strptime(str(row["date"]), "%Y-%m-%d")
        if not (start_year <= d.year <= end_year):
            continue
        try:
            consensus, digest, provider_dt = consensus_and_timestamp_for_date(d.date().isoformat())
        except RuntimeError as exc:
            # Special/revision FRED release dates may legitimately lack the exact CPI/Core pair.
            # Rate-limit exhaustion is NOT silently skipped.
            if str(exc).startswith("INVESTING_RATE_LIMIT_RETRY_EXHAUSTED"):
                raise
            diagnostics.append(f"{d.date()}:{exc}")
            time.sleep(1.0)
            continue
        release_local = datetime(d.year, d.month, d.day, 8, 30, tzinfo=core.ET)
        expected_utc = release_local.astimezone(core.UTC).strftime("%Y/%m/%d %H:%M:%S")
        if provider_dt != expected_utc:
            raise RuntimeError(f"CPI_RELEASE_TIMESTAMP_MISMATCH:{d.date()}:{provider_dt}:{expected_utc}")
        ref = previous_month_key(d)
        if ref in seen:
            raise RuntimeError(f"DUPLICATE_CONFIRMED_CPI_REFERENCE_MONTH:{ref}")
        seen.add(ref)
        _CONSENSUS_CACHE[d.date().isoformat()] = (consensus, digest)
        out.append({
            "reference_month": ref,
            "release_at": release_local.astimezone(core.UTC),
            "release_date": d.date().isoformat(),
            "authority_url": "FRED_RELEASE_ID_10_SOURCE_DATE_PLUS_EXACT_US_CPI69_CORE56_0830ET_MATCH",
        })
        time.sleep(1.25)
    if len(out) < 120:
        raise RuntimeError(f"CONFIRMED_CPI_RELEASE_COVERAGE_TOO_SHORT:{len(out)}:diagnostics={diagnostics[:8]}")
    return out


def historical_cpi_consensus_cached(release_date: str) -> tuple[dict[str, float], str]:
    value = _CONSENSUS_CACHE.get(release_date)
    if value is None:
        consensus, digest, _ = consensus_and_timestamp_for_date(release_date)
        value = (consensus, digest)
        _CONSENSUS_CACHE[release_date] = value
    return value


core.fetch_existing = fetch_existing_dbcompat
core.bls_cpi_schedule = official_cpi_release_schedule
core.historical_cpi_consensus = historical_cpi_consensus_cached

if __name__ == "__main__":
    raise SystemExit(core.main())
