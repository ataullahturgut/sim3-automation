from __future__ import annotations

"""Macro Event V3 inflation data-channel backfill (research evidence only).

This is a V3 extension of the already-proven Gold Control Macro Event research
channel, not a new provider lane.  It reuses:
- Investing.com Economic Calendar /more-history pagination, throttling and 429
  backoff pattern proven by git 9ff6d50c9bd7469a17ffc66e17b59a4d6f9ee278;
- FRED/ALFRED as-of-release-date reconstruction used by the governed macro data
  spine;
- the existing Neon source_registry/observations/retrieval_runs evidence spine.

It writes only research source observations.  It does not score the model,
change Market Shock, or write forecast/decision authority tables.
"""

import hashlib
import json
import os
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time as dtime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
import requests
from bs4 import BeautifulSoup
from psycopg.rows import dict_row

PIPELINE_VERSION = "MACRO_EVENT_SUCCESSOR_V3_INFLATION_EXISTING_CHANNEL_R2_2026-09-08"
START_REFERENCE = "2016-01"
END_REFERENCE = "2026-08"
NY = ZoneInfo("America/New_York")

INVESTING_ENDPOINT = "https://www.investing.com/economic-calendar/more-history"
INVESTING_REFERER = "https://www.investing.com/economic-calendar/"
REQUEST_INTERVAL_SECONDS = 7.0
MAX_429_RETRIES = 4

FRED_API = "https://api.stlouisfed.org/fred"
FRED_CPI_RELEASE_ID = 10

EVENTS = {
    "cpi": {"event_attr_id": "69", "name": "CPI MoM"},
    "core": {"event_attr_id": "56", "name": "Core CPI MoM"},
}
ACTUAL_IDS = {
    "cpi": "MACRO_CPI_ACTUAL_FIRST_PRINT",
    "core": "MACRO_CORE_CPI_ACTUAL_FIRST_PRINT",
}
CONSENSUS_IDS = {
    "cpi": "MACRO_CPI_CONSENSUS_PIT",
    "core": "MACRO_CORE_CPI_CONSENSUS_PIT",
}
FRED_LEVEL_IDS = {"cpi": "CPIAUCSL", "core": "CPILFESL"}
ALL_SERIES_IDS = tuple(ACTUAL_IDS.values()) + tuple(CONSENSUS_IDS.values())
DECISION_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)
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


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return v


def fred_key() -> str:
    v = os.environ.get("FRED_API_KEY", "").strip()
    if not v:
        raise RuntimeError("FRED_API_KEY_NOT_SET")
    return v


def git_sha() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True,
                              text=True, timeout=5).stdout.strip()
    except Exception:
        return os.environ.get("GITHUB_SHA")


def stable_hash(x: Any) -> str:
    raw = json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def month_range(start_ym: str, end_ym: str) -> list[str]:
    sy, sm = map(int, start_ym.split("-")); ey, em = map(int, end_ym.split("-"))
    y, m = sy, sm; out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13: y, m = y + 1, 1
    return out


def ref_dates(reference_month: str) -> tuple[str, str]:
    y, m = map(int, reference_month.split("-"))
    ref = f"{y:04d}-{m:02d}-01"
    prev = f"{y-1:04d}-12-01" if m == 1 else f"{y:04d}-{m-1:02d}-01"
    return ref, prev


def parse_number(value: str) -> float | None:
    s = value.strip().replace(",", "")
    if not s or s in {"-", "--", "N/A"}: return None
    mult = 1.0
    if s.endswith("K"): s = s[:-1]
    elif s.endswith("M"): s, mult = s[:-1], 1000.0
    if s.endswith("%"): s = s[:-1]
    try: return float(s) * mult
    except ValueError: return None


def parse_release_date_and_reference(value: str) -> tuple[date, str]:
    import re
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})(?:\s*\(([A-Z][a-z]{2})\))?", value)
    if not m: raise ValueError(f"UNPARSEABLE_RELEASE_DATE:{value}")
    rel_mon, rel_day, rel_year, ref_mon = m.groups()
    rel = date(int(rel_year), MONTHS[rel_mon], int(rel_day))
    if not ref_mon:
        d = rel.replace(day=1) - timedelta(days=1)
        return rel, f"{d.year:04d}-{d.month:02d}"
    rm = MONTHS[ref_mon]
    ry = rel.year - 1 if rm > rel.month else rel.year
    return rel, f"{ry:04d}-{rm:02d}"


def parse_history_rows(html: str) -> list[HistoryRow]:
    soup = BeautifulSoup(f"<table>{html}</table>", "html.parser")
    out = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 5: continue
        vals = [" ".join(td.get_text(" ", strip=True).split()) for td in tds]
        try: rel, ref = parse_release_date_and_reference(vals[0])
        except Exception: continue
        out.append(HistoryRow(rel, ref, parse_number(vals[3]), parse_number(vals[2]), parse_number(vals[4])))
    return out


def fetch_page(session: requests.Session, event_attr_id: str, anchor: date) -> dict[str, Any]:
    payload = {"eventID": "1", "event_attr_ID": event_attr_id,
               "event_timestamp": anchor.isoformat(), "is_speech": "0"}
    for attempt in range(MAX_429_RETRIES + 1):
        r = session.post(INVESTING_ENDPOINT, data=payload, timeout=25)
        if r.status_code == 429 and attempt < MAX_429_RETRIES:
            try: wait = max(float(r.headers.get("Retry-After", "")), 15.0)
            except Exception: wait = 20.0 * (attempt + 1)
            time.sleep(wait); continue
        if r.status_code != 200: raise RuntimeError(f"INVESTING_HTTP_{r.status_code}")
        data = r.json()
        if not isinstance(data, dict) or "historyRows" not in data:
            raise RuntimeError("INVESTING_UNEXPECTED_RESPONSE_SCHEMA")
        return data
    raise RuntimeError("INVESTING_HTTP_429_RETRY_EXHAUSTED")


def fetch_event_history(event_attr_id: str) -> tuple[dict[str, HistoryRow], dict[str, Any]]:
    expected = set(month_range(START_REFERENCE, END_REFERENCE))
    sy, sm = map(int, START_REFERENCE.split("-"))
    lower = date(sy, sm, 1) - timedelta(days=45)
    anchor = datetime.now(timezone.utc).date()
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest", "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": INVESTING_REFERER, "Accept-Language": "en-US,en;q=0.9",
    })
    by_ref: dict[str, HistoryRow] = {}; hashes = []; calls = 0
    while calls < 40:
        calls += 1
        data = fetch_page(s, event_attr_id, anchor)
        html = str(data.get("historyRows") or "")
        hashes.append(hashlib.sha256(html.encode()).hexdigest())
        rows = parse_history_rows(html)
        if not rows: raise RuntimeError("INVESTING_EMPTY_OR_UNPARSEABLE_HISTORY")
        for row in rows:
            if row.reference_month in expected and row.reference_month not in by_ref:
                by_ref[row.reference_month] = row
        oldest = min(r.release_date for r in rows)
        if expected.issubset(by_ref): break
        if oldest <= lower: break
        new_anchor = oldest - timedelta(days=1)
        if new_anchor >= anchor: raise RuntimeError("INVESTING_NON_DECREASING_HISTORY_CURSOR")
        anchor = new_anchor
        time.sleep(REQUEST_INTERVAL_SECONDS)
    return by_ref, {
        "request_count": calls,
        "page_hash_chain": hashlib.sha256("".join(hashes).encode()).hexdigest() if hashes else None,
        "request_interval_seconds": REQUEST_INTERVAL_SECONDS,
        "max_429_retries": MAX_429_RETRIES,
    }


def fred_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    p = {**params, "api_key": fred_key(), "file_type": "json"}
    last = None
    for attempt in range(5):
        try:
            r = requests.get(FRED_API + path, params=p,
                             headers={"User-Agent": "Gold-Control-Macro-Existing-Channel-R2/1.0"}, timeout=(10, 40))
            if r.status_code == 429: raise RuntimeError("FRED_HTTP_429")
            r.raise_for_status(); return r.json()
        except Exception as exc:
            last = exc
            if attempt < 4: time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"FRED_RETRY_EXHAUSTED:{path}:{last}")


def official_cpi_release_dates() -> set[date]:
    j = fred_get("/release/dates", {"release_id": FRED_CPI_RELEASE_ID,
        "realtime_start": "2016-01-01", "realtime_end": "2026-09-08",
        "limit": 10000, "sort_order": "asc"})
    return {date.fromisoformat(x["date"]) for x in j.get("release_dates", [])}


def asof_values(series_id: str, asof: date, start: str, end: str) -> dict[str, float]:
    j = fred_get("/series/observations", {"series_id": series_id, "output_type": 1,
        "realtime_start": asof.isoformat(), "realtime_end": asof.isoformat(),
        "observation_start": start, "observation_end": end,
        "sort_order": "asc", "limit": 100})
    out = {}
    for row in j.get("observations", []):
        v = str(row.get("value", "."))
        if v not in {".", "", "nan", "None"}: out[str(row["date"])] = float(v)
    return out


def release_ts_utc(d: date) -> datetime:
    return datetime.combine(d, dtime(8, 30), tzinfo=NY).astimezone(timezone.utc)


def decision_counts(conn) -> dict[str, int]:
    out = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for table in DECISION_TABLES:
            cur.execute(f"select count(*)::bigint n from {table}"); out[table] = int(cur.fetchone()["n"])
    return out


def require_registered(conn) -> None:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("select series_id from source_registry where series_id=any(%s)", (list(ALL_SERIES_IDS),))
        present = {r["series_id"] for r in cur.fetchall()}
    missing = sorted(set(ALL_SERIES_IDS) - present)
    if missing: raise RuntimeError(f"GOVERNED_SOURCE_REGISTRY_MISSING:{missing}")


def main() -> int:
    cpi_rows, cpi_meta = fetch_event_history(EVENTS["cpi"]["event_attr_id"])
    time.sleep(REQUEST_INTERVAL_SECONDS)
    core_rows, core_meta = fetch_event_history(EVENTS["core"]["event_attr_id"])
    official_dates = official_cpi_release_dates()
    expected = month_range(START_REFERENCE, END_REFERENCE)

    complete: dict[str, dict[str, HistoryRow]] = {}
    excluded: dict[str, str] = {}
    for month in expected:
        a, b = cpi_rows.get(month), core_rows.get(month)
        if a is None or b is None:
            excluded[month] = "PROVIDER_ROW_MISSING"; continue
        if a.forecast is None or b.forecast is None:
            excluded[month] = "FORECAST_MISSING"; continue
        if a.release_date != b.release_date:
            excluded[month] = "CPI_CORE_RELEASE_DATE_MISMATCH"; continue
        if a.release_date not in official_dates:
            excluded[month] = "NOT_IN_FRED_SOURCE_RELEASE_DATES"; continue
        complete[month] = {"cpi": a, "core": b}

    if len(complete) <= 24:
        raise RuntimeError(f"INFLATION_COMPLETE_CASES_BELOW_MODEL_MIN_PRIOR:{len(complete)}")

    run_id = str(uuid.uuid4()); retrieved = datetime.now(timezone.utc); observations = []
    actual_failures = []
    for i, (month, pair) in enumerate(sorted(complete.items()), 1):
        rel = pair["cpi"].release_date; ts = release_ts_utc(rel); ref, prev = ref_dates(month)
        actuals = {}
        try:
            for key in ("cpi", "core"):
                vals = asof_values(FRED_LEVEL_IDS[key], rel, prev, ref)
                if ref not in vals or prev not in vals: raise RuntimeError(f"ALFRED_REQUIRED_ASOF_VALUE_MISSING:{key}")
                actuals[key] = float(round((vals[ref] / vals[prev] - 1.0) * 100.0, 1))
        except Exception as exc:
            actual_failures.append(f"{month}:{type(exc).__name__}:{exc}"); continue

        for key, sid in ACTUAL_IDS.items():
            normalized = {"provider": "ALFRED_BLS_RELEASE_DATE_RECONSTRUCTION", "series_id": sid,
                          "reference_month": month, "release_date": rel.isoformat(), "value": actuals[key]}
            observations.append({"run_id": run_id, "series_id": sid, "observation_ts": ts,
                "value": actuals[key], "source": "BLS + ALFRED", "source_symbol": FRED_LEVEL_IDS[key],
                "provider_as_of": ts, "available_as_of": ts, "first_seen_at": retrieved, "retrieved_at": retrieved,
                "frequency": "event_monthly", "unit": "percent_mom", "transform": "RELEASE_VALUE",
                "quality_status": "APPROVED_HISTORICAL_FIRST_PRINT_RECONSTRUCTION_RESEARCH",
                "lineage_id": f"V3R2_ALFRED_{key.upper()}_{month.replace('-', '')}",
                "payload_hash": stable_hash(normalized), "metadata": json.dumps({
                    "engine": "MACRO_EVENT_SUCCESSOR_V3", "reference_month": month,
                    "release_date": rel.isoformat(), "official_release_time_rule": "08:30 America/New_York",
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                    "construction_method": "ALFRED_ASOF_RELEASE_DATE_LEVELS",
                    "historical_reconstruction_not_original_retrieval": True,
                    "current_vintage_substitution": False, "model_score_run": False,
                    "production_authority": False}, sort_keys=True)})

        for key, sid in CONSENSUS_IDS.items():
            forecast = float(pair[key].forecast)
            normalized = {"provider": "Investing.com Economic Calendar",
                          "event_attr_id": EVENTS[key]["event_attr_id"], "field": "Forecast",
                          "series_id": sid, "reference_month": month, "release_date": rel.isoformat(), "value": forecast}
            observations.append({"run_id": run_id, "series_id": sid, "observation_ts": ts,
                "value": forecast, "source": "Investing.com Economic Calendar",
                "source_symbol": f"event_attr_id={EVENTS[key]['event_attr_id']}",
                "provider_as_of": ts, "available_as_of": ts, "first_seen_at": retrieved, "retrieved_at": retrieved,
                "frequency": "event_monthly", "unit": "percent_mom", "transform": "RELEASE_CONSENSUS",
                "quality_status": "HISTORICAL_RECONSTRUCTION_NOT_PIT_PROVEN_PROSPECTIVE_CAPTURE_ENABLED",
                "lineage_id": f"V3R2_INVESTING_{key.upper()}_{month.replace('-', '')}",
                "payload_hash": stable_hash(normalized), "metadata": json.dumps({
                    "engine": "MACRO_EVENT_SUCCESSOR_V3", "reference_month": month,
                    "release_date": rel.isoformat(), "official_release_time_rule": "08:30 America/New_York",
                    "provider_field": "Forecast", "investing_event_attr_id": EVENTS[key]["event_attr_id"],
                    "provider_exact_pre_release_update_timestamp_proven": False,
                    "availability_policy": "NO_EARLIER_THAN_OFFICIAL_BLS_RELEASE_TIMESTAMP",
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                    "historical_reconstruction_not_original_retrieval": True,
                    "no_redistribution": True, "model_score_run": False,
                    "production_authority": False}, sort_keys=True)})
        if i % 10 == 0: time.sleep(0.4)

    good_months = len(observations) // 4
    if actual_failures: raise RuntimeError(f"ALFRED_ACTUAL_RECONSTRUCTION_FAILURES:{len(actual_failures)}:{actual_failures[:5]}")
    if good_months != len(complete): raise RuntimeError(f"INFLATION_OBSERVATION_COUNT_DRIFT:{good_months}/{len(complete)}")

    with psycopg.connect(db_url(), autocommit=False) as conn:
        require_registered(conn); before = decision_counts(conn)
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("select series_id,observation_ts,lineage_id,value,quality_status from observations where series_id=any(%s)",
                        (list(ALL_SERIES_IDS),))
            prior = {(r["series_id"], r["observation_ts"], r["lineage_id"]): r for r in cur.fetchall()}
        to_insert = []
        for o in observations:
            p = prior.get((o["series_id"], o["observation_ts"], o["lineage_id"]))
            if p is None: to_insert.append(o); continue
            if float(p["value"]) != float(o["value"]) or str(p["quality_status"]) != str(o["quality_status"]):
                raise RuntimeError(f"FROZEN_INFLATION_CHANNEL_CHANGED:{o['series_id']}:{o['metadata']}")
        finished = datetime.now(timezone.utc)
        meta = {"engine_id": "MACRO_EVENT_SUCCESSOR_V3", "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                "source_channel_reuse": True, "source_channel_provenance_git_sha": "9ff6d50c9bd7469a17ffc66e17b59a4d6f9ee278",
                "complete_case_months": len(complete), "expected_months": len(expected), "excluded": excluded,
                "investing_page_hash_chains": {"cpi": cpi_meta["page_hash_chain"], "core": core_meta["page_hash_chain"]},
                "fred_release_id": FRED_CPI_RELEASE_ID, "raw_investing_payload_stored": False,
                "model_score_run": False, "forecast_or_decision_write": False, "production_authority": False}
        with conn.cursor() as cur:
            cur.execute("""insert into retrieval_runs
                (run_id,started_at,finished_at,pipeline_version,git_sha,trigger_type,status,observations_read,observations_written,notes,metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                (run_id,retrieved,finished,PIPELINE_VERSION,git_sha(),"macro_event_v3_existing_channel_inflation_backfill",
                 "SUCCESS",len(observations),len(to_insert),"Existing Gold Control Investing + ALFRED/BLS channel reuse; no model score",
                 json.dumps(meta,sort_keys=True)))
            if to_insert:
                cur.executemany("""insert into observations
                    (run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,
                     first_seen_at,retrieved_at,frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata)
                    values (%(run_id)s,%(series_id)s,%(observation_ts)s,%(value)s,%(source)s,%(source_symbol)s,
                     %(provider_as_of)s,%(available_as_of)s,%(first_seen_at)s,%(retrieved_at)s,%(frequency)s,%(unit)s,
                     %(transform)s,%(quality_status)s,%(lineage_id)s,%(payload_hash)s,%(metadata)s::jsonb)""",to_insert)
        after = decision_counts(conn)
        if after != before: raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED:{before}->{after}")
        conn.commit()

    result = {"status": "PASS_EXISTING_CHANNEL_INFLATION_BACKFILL", "run_id": run_id,
              "complete_case_months": len(complete), "expected_months": len(expected),
              "excluded": excluded, "observations_written": len(to_insert),
              "source_channel_reuse": True, "model_score_run": False,
              "market_shock_changed": False, "production_authority": False}
    with open("macro_event_v3_inflation_channel_backfill_r2_result.json","w",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,default=str)
    print(json.dumps(result,indent=2,sort_keys=True,default=str)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
