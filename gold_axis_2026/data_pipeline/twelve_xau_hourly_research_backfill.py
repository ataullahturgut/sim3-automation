from __future__ import annotations

import hashlib
import json
import math
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://api.twelvedata.com/time_series"
SERIES_ID = "XAU_USD_TWELVE_1H_RESEARCH_V1"
SOURCE = "Twelve Data"
SYMBOL = "XAU/USD"
INTERVAL = "1h"
REQUEST_TZ = "UTC"
UNIT = "USD_per_troy_ounce"
QUALITY_STATUS = "APPROVED_HISTORICAL_RESEARCH_BACKFILL_NOT_PIT_ISSUED"
PIPELINE_VERSION = "XAU_1H_RESEARCH_BACKFILL_V1_2026-09-16"
START_DATE = pd.Timestamp("2023-01-01 00:00:00", tz="UTC")
END_DATE_EXCLUSIVE = pd.Timestamp("2025-01-01 00:00:00", tz="UTC")
OUTPUTSIZE = 5000


@dataclass(frozen=True)
class Bar:
    ts: pd.Timestamp
    close: float
    payload_hash: str
    chunk_start: str
    chunk_end: str


def _secret(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}_MISSING")
    return value


def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=2.0,
        status_forcelist=(408, 425, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4))
    s.headers.update({"User-Agent": "GoldControl-XAU1H-Research/1.0", "Accept": "application/json"})
    return s


def _quarter_chunks() -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    starts = pd.date_range(START_DATE, END_DATE_EXCLUSIVE, freq="QS", inclusive="left")
    out: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for start in starts:
        end = min(start + pd.offsets.QuarterBegin(startingMonth=((start.month - 1) // 3) * 3 + 1), END_DATE_EXCLUSIVE)
        # QuarterBegin from a quarter boundary advances to the next quarter.
        if end <= start:
            end = start + pd.DateOffset(months=3)
        end = min(pd.Timestamp(end), END_DATE_EXCLUSIVE)
        out.append((pd.Timestamp(start), pd.Timestamp(end)))
    return out


def _fmt(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S")


def _parse_payload(response: requests.Response, start: pd.Timestamp, end: pd.Timestamp) -> list[Bar]:
    payload = response.json()
    if isinstance(payload, dict) and payload.get("status") == "error":
        raise RuntimeError(f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}")
    values = payload.get("values") if isinstance(payload, dict) else None
    if not values:
        raise RuntimeError(f"TWELVE_NO_VALUES:{start.date()}:{end.date()}")
    if len(values) >= OUTPUTSIZE:
        raise RuntimeError(f"TWELVE_POSSIBLE_TRUNCATION:{start.date()}:{end.date()}:{len(values)}")

    meta = payload.get("meta") or {}
    meta_symbol = str(meta.get("symbol") or "")
    if meta_symbol and meta_symbol.upper().replace(" ", "") not in {"XAU/USD", "XAUUSD"}:
        raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{meta_symbol}")

    ph = hashlib.sha256(response.content).hexdigest()
    bars: list[Bar] = []
    for row in values:
        raw_dt = row.get("datetime")
        raw_close = row.get("close")
        dt = pd.to_datetime(raw_dt, errors="coerce")
        close = pd.to_numeric(raw_close, errors="coerce")
        if pd.isna(dt) or pd.isna(close):
            continue
        if dt.tzinfo is None:
            dt = dt.tz_localize("UTC")
        else:
            dt = dt.tz_convert("UTC")
        close_f = float(close)
        if not math.isfinite(close_f) or close_f <= 0.0:
            continue
        if not (start <= dt < end):
            continue
        bars.append(
            Bar(
                ts=pd.Timestamp(dt),
                close=close_f,
                payload_hash=ph,
                chunk_start=_fmt(start),
                chunk_end=_fmt(end),
            )
        )
    if not bars:
        raise RuntimeError(f"TWELVE_EMPTY_AFTER_VALIDATION:{start.date()}:{end.date()}")
    return bars


def fetch_all() -> list[Bar]:
    key = _secret("TWELVE_DATA_API_KEY")
    session = _session()
    all_bars: list[Bar] = []
    for idx, (start, end) in enumerate(_quarter_chunks(), start=1):
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "start_date": _fmt(start),
            "end_date": _fmt(end - pd.Timedelta(seconds=1)),
            "timezone": REQUEST_TZ,
            "order": "ASC",
            "outputsize": OUTPUTSIZE,
            "format": "JSON",
            "apikey": key,
        }
        response = session.get(API_URL, params=params, timeout=(10, 60))
        response.raise_for_status()
        chunk = _parse_payload(response, start, end)
        all_bars.extend(chunk)
        print(f"FETCH_CHUNK={idx} rows={len(chunk)} start={start.date()} end_exclusive={end.date()}")
        time.sleep(2)

    by_ts: dict[pd.Timestamp, Bar] = {}
    conflicts: list[str] = []
    for bar in all_bars:
        old = by_ts.get(bar.ts)
        if old is None:
            by_ts[bar.ts] = bar
        elif abs(old.close - bar.close) > 1e-12:
            conflicts.append(bar.ts.isoformat())
    if conflicts:
        raise RuntimeError(f"DUPLICATE_TIMESTAMP_CONFLICTS:{conflicts[:10]}")

    bars = [by_ts[k] for k in sorted(by_ts)]
    if not bars:
        raise RuntimeError("NO_VALID_BARS")
    years = {b.ts.year for b in bars}
    if years != {2023, 2024}:
        raise RuntimeError(f"YEAR_COVERAGE_MISMATCH:{sorted(years)}")
    print(
        "FETCH_COMPLETE "
        f"rows={len(bars)} first={bars[0].ts.isoformat()} last={bars[-1].ts.isoformat()} "
        "raw_market_values_logged=NO"
    )
    return bars


def _lineage_id() -> str:
    raw = f"{SERIES_ID}|{SOURCE}|{SYMBOL}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def persist(bars: list[Bar]) -> None:
    db_url = _secret("NEON_DATABASE_URL")
    retrieved_at = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    lineage = _lineage_id()

    with psycopg.connect(db_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into source_registry
                (series_id, semantic_id, source_name, source_symbol, source_tier, frequency,
                 unit, model_role, status, license_note, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                on conflict (series_id) do update set
                  semantic_id=excluded.semantic_id,
                  source_name=excluded.source_name,
                  source_symbol=excluded.source_symbol,
                  source_tier=excluded.source_tier,
                  frequency=excluded.frequency,
                  unit=excluded.unit,
                  model_role=excluded.model_role,
                  status=excluded.status,
                  license_note=excluded.license_note,
                  metadata=excluded.metadata,
                  updated_at=now()
                """,
                (
                    SERIES_ID,
                    "XAU_USD_SPOT_HOURLY_RESEARCH",
                    SOURCE,
                    SYMBOL,
                    "RESEARCH_TIER_A",
                    "1h",
                    UNIT,
                    "BOCPD intraday research input only",
                    "APPROVED_HISTORICAL_RESEARCH_ONLY_NOT_RUNTIME",
                    "Private internal research; raw vendor values must not be publicly redistributed.",
                    json.dumps(
                        {
                            "interval": INTERVAL,
                            "request_timezone": REQUEST_TZ,
                            "provider_endpoint": API_URL,
                            "evidence_class": "HISTORICAL_RESEARCH_BACKFILL",
                            "availability_policy": "first_retrieval_floor",
                            "historical_publication_timestamp_reconstruction": "NOT_PROVEN",
                            "not_equivalent_to": "XAU_EOD_TWELVE_NY17",
                            "model_use": "RESEARCH_ONLY",
                            "years_requested": [2023, 2024],
                        }
                    ),
                ),
            )

            cur.execute(
                """
                insert into retrieval_runs
                (run_id, started_at, finished_at, git_sha, pipeline_version, trigger_type,
                 status, observations_read, observations_written, notes, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s::jsonb)
                """,
                (
                    run_id,
                    retrieved_at,
                    retrieved_at,
                    os.environ.get("GITHUB_SHA"),
                    PIPELINE_VERSION,
                    "manual_authorized_historical_backfill",
                    "RUNNING",
                    len(bars),
                    "Authorized research-only XAU/USD hourly backfill for 2023-2024",
                    json.dumps(
                        {
                            "series_id": SERIES_ID,
                            "availability_policy": "first_retrieval_floor",
                            "historical_publication_timestamp_reconstruction": "NOT_PROVEN",
                            "raw_market_values_logged": False,
                        }
                    ),
                ),
            )

            cur.execute(
                """
                select observation_ts, value, quality_status
                from canonical_latest
                where series_id=%s
                """,
                (SERIES_ID,),
            )
            existing = {row[0]: (float(row[1]), str(row[2])) for row in cur.fetchall()}

            to_insert = []
            conflicts = []
            retrieved_iso = retrieved_at.isoformat()
            for bar in bars:
                ts = bar.ts.to_pydatetime()
                prev = existing.get(ts)
                if prev is not None:
                    same_value = abs(prev[0] - bar.close) <= 1e-12
                    same_status = prev[1] == QUALITY_STATUS
                    if same_value and same_status:
                        continue
                    conflicts.append(bar.ts.isoformat())
                    continue
                to_insert.append(
                    (
                        run_id,
                        SERIES_ID,
                        ts,
                        bar.close,
                        SOURCE,
                        SYMBOL,
                        None,
                        retrieved_at,
                        retrieved_at,
                        retrieved_at,
                        "1h",
                        UNIT,
                        "LEVEL",
                        QUALITY_STATUS,
                        lineage,
                        bar.payload_hash,
                        json.dumps(
                            {
                                "interval": INTERVAL,
                                "request_timezone": REQUEST_TZ,
                                "chunk_start": bar.chunk_start,
                                "chunk_end": bar.chunk_end,
                                "availability_policy": "first_retrieval_floor",
                                "historical_publication_timestamp_reconstruction": "NOT_PROVEN",
                                "evidence_class": "HISTORICAL_RESEARCH_BACKFILL",
                                "rights_policy": "PRIVATE_INTERNAL_NON_DISPLAY_NO_PUBLIC_RAW_REDISTRIBUTION",
                            }
                        ),
                    )
                )

            if conflicts:
                raise RuntimeError(f"EXISTING_VALUE_CONFLICT:{conflicts[:10]}")

            if to_insert:
                cur.executemany(
                    """
                    insert into observations
                    (run_id, series_id, observation_ts, value, source, source_symbol,
                     provider_as_of, available_as_of, first_seen_at, retrieved_at,
                     frequency, unit, transform, quality_status, lineage_id, payload_hash, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    to_insert,
                )

            cur.execute(
                """
                update retrieval_runs
                set finished_at=now(), status='SUCCESS', observations_written=%s,
                    metadata = metadata || %s::jsonb
                where run_id=%s
                """,
                (
                    len(to_insert),
                    json.dumps({"deduped_existing_rows": len(bars) - len(to_insert)}),
                    run_id,
                ),
            )
        conn.commit()

    print(
        "PERSIST_COMPLETE "
        f"run_id={run_id} read={len(bars)} written={len(to_insert)} "
        f"deduped={len(bars)-len(to_insert)} lineage={lineage}"
    )


def main() -> None:
    bars = fetch_all()
    persist(bars)
    print("XAU_1H_RESEARCH_BACKFILL_COMPLETE")


if __name__ == "__main__":
    main()
