from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row
from psycopg import sql

SYMBOL = "XAU/USD"
PROVIDER = "Twelve Data"
TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
MAX_OUTPUT = 5000
MIN_REQUEST_INTERVAL_SECONDS = float(os.environ.get("TWELVE_MIN_REQUEST_INTERVAL_SECONDS", "10.0"))
TABLES = {"5min": "xau_intraday_research_cache_5m", "1min": "xau_intraday_research_cache_1m"}
EVIDENCE_CLASS = "HISTORICAL_RESEARCH_RETRIEVAL"
PURPOSE = "ACADEMIC_RESEARCH_PRIVATE_CACHE"
_LAST_REQUEST = 0.0


def _db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return v


def _api_key() -> str:
    v = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not v:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")
    return v


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": f"apikey {_api_key()}", "User-Agent": "GoldControl-XAU-Research-Cache-V1/1.0"})
    return s


def _pace() -> None:
    global _LAST_REQUEST
    elapsed = time.monotonic() - _LAST_REQUEST
    if _LAST_REQUEST and elapsed < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)


def _request_json(session: requests.Session, params: dict) -> dict:
    global _LAST_REQUEST
    waits = [0, 10, 20]
    last = None
    for wait in waits:
        if wait:
            time.sleep(wait)
        _pace()
        try:
            r = session.get(TIME_SERIES_URL, params=params, timeout=(8, 90))
            _LAST_REQUEST = time.monotonic()
            payload = r.json()
            if payload.get("status") == "error":
                code = str(payload.get("code"))
                msg = str(payload.get("message"))
                if code == "429":
                    raise RuntimeError(f"BLOCKED_PROVIDER_QUOTA:{msg}")
                if code in {"500", "502", "503", "504"}:
                    last = RuntimeError(f"TWELVE_RETRYABLE:{code}:{msg}")
                    continue
                raise RuntimeError(f"TWELVE_API_ERROR:{code}:{msg}")
            r.raise_for_status()
            return payload
        except RuntimeError as exc:
            if str(exc).startswith("BLOCKED_PROVIDER_QUOTA:"):
                raise
            last = exc
        except (requests.RequestException, ValueError) as exc:
            last = exc
    raise RuntimeError(f"TWELVE_REQUEST_FAILED:{last}")


def _month_bounds(month: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(f"{month}-01", tz="UTC")
    end = (start + pd.offsets.MonthBegin(1)) - pd.Timedelta(seconds=1)
    return start, end


def _parse_page(payload: dict, interval: str, lower: pd.Timestamp, upper: pd.Timestamp) -> list[tuple[pd.Timestamp, float]]:
    meta = payload.get("meta") or {}
    if meta.get("symbol") not in (None, SYMBOL):
        raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{meta.get('symbol')}")
    if meta.get("interval") not in (None, interval):
        raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{meta.get('interval')}")
    step = "5min" if interval == "5min" else "min"
    rows: dict[pd.Timestamp, float] = {}
    for item in payload.get("values") or []:
        ts = pd.to_datetime(item.get("datetime"), utc=True, errors="coerce")
        close = pd.to_numeric(item.get("close"), errors="coerce")
        if pd.isna(ts) or pd.isna(close):
            continue
        ts = pd.Timestamp(ts).floor(step)
        if ts < lower or ts > upper:
            continue
        close = float(close)
        if close <= 0:
            raise RuntimeError(f"TWELVE_INVALID_CLOSE:{ts.isoformat()}")
        if ts in rows and abs(rows[ts] - close) > 1e-12:
            raise RuntimeError(f"TWELVE_PAGE_DUPLICATE_CONFLICT:{ts.isoformat()}")
        rows[ts] = close
    return sorted(rows.items())


def _hash_points(points: list[tuple[pd.Timestamp, float]]) -> str:
    h = hashlib.sha256()
    for ts, close in points:
        h.update(f"{ts.isoformat()}|{close:.12f}\n".encode())
    return h.hexdigest()


def _insert_points(conn: psycopg.Connection, interval: str, points: list[tuple[pd.Timestamp, float]]) -> int:
    if not points:
        return 0
    table = TABLES[interval]
    times = [x[0].to_pydatetime() for x in points]
    vals = [x[1] for x in points]
    with conn.cursor() as cur:
        q_conf = sql.SQL("""
            select c.observation_ts, c.close as existing_close, u.close as incoming_close
            from {table} c
            join unnest(%s::timestamptz[], %s::double precision[]) as u(observation_ts, close)
              on u.observation_ts=c.observation_ts
            where abs(c.close-u.close) > 1e-10
            limit 1
        """).format(table=sql.Identifier(table))
        cur.execute(q_conf, (times, vals))
        conflict = cur.fetchone()
        if conflict:
            raise RuntimeError(f"CACHE_VALUE_CONFLICT:{interval}:{conflict}")
        q_ins = sql.SQL("""
            insert into {table}(observation_ts, close)
            select * from unnest(%s::timestamptz[], %s::double precision[])
            on conflict (observation_ts) do nothing
        """).format(table=sql.Identifier(table))
        cur.execute(q_ins, (times, vals))
        inserted = cur.rowcount
    conn.commit()
    return inserted


def _batch_start(conn, interval: str, start: pd.Timestamp, end: pd.Timestamp) -> int:
    with conn.cursor() as cur:
        cur.execute("""
          insert into xau_intraday_research_cache_batches
            (series_id, interval, requested_start, requested_end, code_sha, status, metadata)
          values (%s,%s,%s,%s,%s,'IN_PROGRESS',%s::jsonb)
          returning batch_id
        """, (f"XAU_RESEARCH_TWELVE_{interval.upper()}_CACHE_V1", interval, start.to_pydatetime(), end.to_pydatetime(), os.environ.get("GOLD_CODE_SHA","NOT_PROVIDED"), json.dumps({"min_request_interval_seconds": MIN_REQUEST_INTERVAL_SECONDS, "page_outputsize": MAX_OUTPUT})))
        batch_id = int(cur.fetchone()[0])
    conn.commit()
    return batch_id


def _batch_update(conn, batch_id: int, *, status: str, row_count: int, inserted_count: int, first_ts=None, last_ts=None, payload_sha256=None, error=None, metadata=None) -> None:
    with conn.cursor() as cur:
        cur.execute("""
          update xau_intraday_research_cache_batches
          set status=%s,row_count=%s,inserted_count=%s,first_ts=%s,last_ts=%s,payload_sha256=%s,error=%s,
              metadata=metadata || %s::jsonb
          where batch_id=%s
        """, (status,row_count,inserted_count,first_ts,last_ts,payload_sha256,error,json.dumps(metadata or {}),batch_id))
    conn.commit()


def _is_complete(conn, interval: str, start: pd.Timestamp, end: pd.Timestamp) -> bool:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
          select 1 from xau_intraday_research_cache_batches
          where interval=%s and requested_start=%s and requested_end=%s and status='COMPLETE'
          order by batch_id desc limit 1
        """, (interval, start.to_pydatetime(), end.to_pydatetime()))
        return cur.fetchone() is not None


def _resume_cursor(conn, interval: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.Timestamp:
    table = TABLES[interval]
    with conn.cursor() as cur:
        q = sql.SQL("select min(observation_ts) from {table} where observation_ts between %s and %s").format(table=sql.Identifier(table))
        cur.execute(q, (start.to_pydatetime(), end.to_pydatetime()))
        row = cur.fetchone()
    if row and row[0] is not None:
        step = pd.Timedelta(minutes=5 if interval == "5min" else 1)
        return min(end, pd.Timestamp(row[0]) - step)
    return end


def _fetch_range_to_cache(session, conn, interval: str, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    if _is_complete(conn, interval, start, end):
        return {"interval": interval, "start": start.isoformat(), "end": end.isoformat(), "status": "ALREADY_COMPLETE"}
    batch_id = _batch_start(conn, interval, start, end)
    cursor_end = _resume_cursor(conn, interval, start, end)
    pages = 0
    rows_seen = 0
    inserted_total = 0
    all_hash = hashlib.sha256()
    first_ts = None
    last_ts = None
    try:
        while cursor_end >= start:
            payload = _request_json(session, {
                "symbol": SYMBOL,
                "interval": interval,
                "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": cursor_end.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": "UTC",
                "outputsize": MAX_OUTPUT,
                "order": "DESC",
                "format": "JSON",
            })
            values = payload.get("values") or []
            if not values:
                break
            points = _parse_page(payload, interval, start, cursor_end)
            if not points:
                raise RuntimeError(f"TWELVE_PAGE_NO_VALID_ROWS:{interval}:{cursor_end.isoformat()}")
            pages += 1
            rows_seen += len(points)
            inserted_total += _insert_points(conn, interval, points)
            ph = _hash_points(points)
            all_hash.update(ph.encode())
            oldest, newest = points[0][0], points[-1][0]
            first_ts = oldest if first_ts is None else min(first_ts, oldest)
            last_ts = newest if last_ts is None else max(last_ts, newest)
            step = pd.Timedelta(minutes=5 if interval == "5min" else 1)
            next_cursor = oldest - step
            _batch_update(conn, batch_id, status="IN_PROGRESS", row_count=rows_seen, inserted_count=inserted_total,
                          first_ts=first_ts.to_pydatetime(), last_ts=last_ts.to_pydatetime(),
                          metadata={"pages": pages, "next_cursor_end": next_cursor.isoformat()})
            print(json.dumps({"interval": interval, "page": pages, "rows": len(points), "inserted": inserted_total, "oldest": oldest.isoformat(), "newest": newest.isoformat()}, sort_keys=True), flush=True)
            if oldest <= start or len(values) < MAX_OUTPUT:
                break
            if next_cursor >= cursor_end:
                raise RuntimeError(f"PAGINATION_NON_PROGRESS:{interval}:{cursor_end.isoformat()}")
            cursor_end = next_cursor
        _batch_update(conn, batch_id, status="COMPLETE", row_count=rows_seen, inserted_count=inserted_total,
                      first_ts=first_ts.to_pydatetime() if first_ts is not None else None,
                      last_ts=last_ts.to_pydatetime() if last_ts is not None else None,
                      payload_sha256=all_hash.hexdigest(), metadata={"pages": pages})
        return {"interval": interval, "start": start.isoformat(), "end": end.isoformat(), "status": "COMPLETE", "pages": pages, "rows_seen": rows_seen, "inserted": inserted_total}
    except Exception as exc:
        status = "BLOCKED_PROVIDER_QUOTA_PARTIAL" if "BLOCKED_PROVIDER_QUOTA" in str(exc) else "FAILED_PARTIAL"
        _batch_update(conn, batch_id, status=status, row_count=rows_seen, inserted_count=inserted_total,
                      first_ts=first_ts.to_pydatetime() if first_ts is not None else None,
                      last_ts=last_ts.to_pydatetime() if last_ts is not None else None,
                      payload_sha256=all_hash.hexdigest() if pages else None, error=f"{type(exc).__name__}:{exc}",
                      metadata={"pages": pages, "next_cursor_end": cursor_end.isoformat()})
        return {"interval": interval, "start": start.isoformat(), "end": end.isoformat(), "status": status, "pages": pages, "rows_seen": rows_seen, "inserted": inserted_total, "error": f"{type(exc).__name__}:{exc}"}


def _audit(conn) -> dict:
    out = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for interval, table in TABLES.items():
            q = sql.SQL("select count(*) as rows,min(observation_ts) as first_ts,max(observation_ts) as last_ts from {table}").format(table=sql.Identifier(table))
            cur.execute(q)
            r = dict(cur.fetchone())
            cur.execute("select pg_total_relation_size(%s::regclass) as bytes", (f"public.{table}",))
            r["total_relation_bytes"] = int(cur.fetchone()[0])
            out[interval] = {k:(v.isoformat() if hasattr(v,'isoformat') else v) for k,v in r.items()}
    out["expected_from_success_run_34173429840"] = {"5min_rows": 482734, "1min_rows": 1393783, "1min_months": 43}
    out["cache_complete_for_replay"] = (out["5min"]["rows"] == 482734 and out["1min"]["rows"] == 1393783)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="xau_intraday_research_cache_ingest_v1.json")
    p.add_argument("--five-start", default="2020-04-06 00:00:00")
    p.add_argument("--five-end", default="2026-08-31 23:59:59")
    p.add_argument("--one-start-month", default="2023-01")
    p.add_argument("--one-end-month", default="2026-07")
    args = p.parse_args()
    report = {"contract":"GOLD_CONTROL_XAU_INTRADAY_RESEARCH_CACHE_INGEST_V1","generated_at":datetime.now(timezone.utc).isoformat(),"database_write":"RESEARCH_CACHE_ONLY","canonical_authority":False,"prospective_claim":False,"provider":PROVIDER,"symbol":SYMBOL,"results":[]}
    session = _session()
    with psycopg.connect(_db_url(), autocommit=False) as conn:
        five_start = pd.Timestamp(args.five_start, tz="UTC")
        five_end = pd.Timestamp(args.five_end, tz="UTC")
        report["results"].append(_fetch_range_to_cache(session, conn, "5min", five_start, five_end))
        months = pd.period_range(args.one_start_month, args.one_end_month, freq="M")
        for period in months:
            start, end = _month_bounds(str(period))
            result = _fetch_range_to_cache(session, conn, "1min", start, end)
            report["results"].append(result)
            if result["status"] == "BLOCKED_PROVIDER_QUOTA_PARTIAL":
                break
        report["audit"] = _audit(conn)
    statuses = [r["status"] for r in report["results"]]
    report["status"] = "COMPLETE" if report["audit"]["cache_complete_for_replay"] else ("PARTIAL_PROVIDER_QUOTA" if any("QUOTA" in s for s in statuses) else "PARTIAL")
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
