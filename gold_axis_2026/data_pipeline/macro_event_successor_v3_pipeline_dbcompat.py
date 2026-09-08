from __future__ import annotations

from datetime import datetime

from psycopg.rows import dict_row

import macro_event_successor_v3_pipeline as core


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


def official_cpi_release_schedule(start_year: int, end_year: int) -> list[dict]:
    """Use FRED source-published CPI release dates; BLS CPI release time is 08:30 ET.

    FRED release/dates is the historical date authority and is linked to the BLS CPI
    press release (release_id=10). Each CPI release publishes the prior reference
    month. Exact time uses the governed BLS CPI 08:30 America/New_York release rule.
    """
    key = core.require_env("FRED_API_KEY")
    base = "https://api.stlouisfed.org/fred"
    rel = core.get(
        base + "/series/release",
        params={"series_id": "CPIAUCSL", "api_key": key, "file_type": "json"},
    ).json()
    releases = rel.get("releases") or []
    if len(releases) != 1:
        raise RuntimeError(f"CPI_SERIES_RELEASE_AMBIGUOUS:{len(releases)}")
    release = releases[0]
    if int(release.get("id")) != 10 or str(release.get("name")) != "Consumer Price Index":
        raise RuntimeError(f"CPI_RELEASE_IDENTITY_MISMATCH:{release}")

    payload = core.get(
        base + "/release/dates",
        params={
            "release_id": 10,
            "api_key": key,
            "file_type": "json",
            "realtime_start": f"{start_year}-01-01",
            "realtime_end": datetime.now(core.UTC).date().isoformat(),
            "limit": 10000,
            "sort_order": "asc",
        },
    ).json()
    rows = payload.get("release_dates") or []
    out = []
    seen = set()
    for row in rows:
        d = datetime.strptime(str(row["date"]), "%Y-%m-%d")
        if not (start_year <= d.year <= end_year):
            continue
        ref = previous_month_key(d)
        if ref in seen:
            raise RuntimeError(f"DUPLICATE_CPI_REFERENCE_MONTH:{ref}")
        seen.add(ref)
        release_local = datetime(d.year, d.month, d.day, 8, 30, tzinfo=core.ET)
        out.append(
            {
                "reference_month": ref,
                "release_at": release_local.astimezone(core.UTC),
                "release_date": d.date().isoformat(),
                "authority_url": "FRED_RELEASE_ID_10_SOURCE_PUBLISHED_DATE__BLS_CPI_0830_ET",
            }
        )
    if len(out) < 120:
        raise RuntimeError(f"CPI_RELEASE_COVERAGE_TOO_SHORT:{len(out)}")
    return out


core.fetch_existing = fetch_existing_dbcompat
core.bls_cpi_schedule = official_cpi_release_schedule

if __name__ == "__main__":
    raise SystemExit(core.main())
