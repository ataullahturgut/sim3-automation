from __future__ import annotations

import argparse
import json
import time as time_mod
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone

import requests

import collector_r2 as base
from persist_neon import persist_bundle
import twelve_xau_ny17 as ny17

PIPELINE_VERSION = "GOLD_DATA_R2.9_XAU_NY17_BACKFILL_2026-09-01_R3"
MAX_ATTEMPTS_PER_DATE = 4
SHORT_RETRY_SLEEP_SECONDS = (2.0, 5.0, 10.0)
# Twelve Data documents that API credits reset every minute and that Basic has
# 8 API credits/minute. Keep this one-time historical backfill below that floor.
INTER_DATE_PACING_SECONDS = 8.0
QUOTA_RESET_SLEEP_SECONDS = 61.0


def _dates(start: date, end: date, anchor_dates: tuple[date, ...] = ()):
    requested = set(anchor_dates)
    d = start
    while d <= end:
        if d.weekday() < 5:
            requested.add(d)
        d += timedelta(days=1)
    for d in sorted(requested):
        if d.weekday() < 5:
            yield d


def _request_with_retry(session: requests.Session, d: date):
    failures = []
    for attempt in range(1, MAX_ATTEMPTS_PER_DATE + 1):
        try:
            return ny17._request_day(session, d), failures
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            name = type(exc).__name__
            failures.append({
                "attempt": attempt,
                "error": name,
                "http_status": status,
            })
            retryable = status is None or status == 429 or status >= 500
            if not retryable or attempt >= MAX_ATTEMPTS_PER_DATE:
                raise
            # urllib3 may surface exhausted 429 retries as requests.RetryError
            # without the original response attached. Treat that as a quota-window
            # reset condition rather than hammering the endpoint again immediately.
            if status == 429 or isinstance(exc, requests.exceptions.RetryError):
                time_mod.sleep(QUOTA_RESET_SLEEP_SECONDS)
            else:
                delay = SHORT_RETRY_SLEEP_SECONDS[min(attempt - 1, len(SHORT_RETRY_SLEEP_SECONDS) - 1)]
                time_mod.sleep(delay)
    raise RuntimeError("UNREACHABLE_RETRY_STATE")


def collect_range(start: date, end: date, anchor_dates: tuple[date, ...] = ()) -> dict:
    if end < start:
        raise ValueError("end before start")
    retrieved_at = datetime.now(timezone.utc)
    session = base.session()
    run_id = str(base.uuid.uuid4())
    observations = []
    missing = []
    provider_errors = []
    retry_summary = []

    for d in _dates(start, end, anchor_dates):
        try:
            (payload, raw), failures = _request_with_retry(session, d)
            if failures:
                retry_summary.append({"date": d.isoformat(), "transient_failures": failures})
            bar = ny17._extract_exact_bar(payload, d)
        except Exception as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            provider_errors.append({
                "date": d.isoformat(),
                "error": type(exc).__name__,
                "http_status": status,
            })
            time_mod.sleep(INTER_DATE_PACING_SECONDS)
            continue
        if bar is None:
            missing.append(d.isoformat())
            time_mod.sleep(INTER_DATE_PACING_SECONDS)
            continue

        meta = payload.get("meta") or {}
        if (meta.get("symbol") or ny17.SYMBOL) != ny17.SYMBOL:
            raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{d.isoformat()}")
        if meta.get("interval") not in (None, ny17.INTERVAL):
            raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{d.isoformat()}")

        cutoff_ny = datetime.combine(d, ny17.CUTOFF, tzinfo=ny17.NY)
        cutoff_utc = cutoff_ny.astimezone(timezone.utc)
        if cutoff_utc > retrieved_at:
            time_mod.sleep(INTER_DATE_PACING_SECONDS)
            continue

        observations.append(asdict(base.make_obs(
            run_id,
            ny17.SERIES_ID,
            cutoff_utc,
            bar["close"],
            ny17.SOURCE,
            ny17.SYMBOL,
            "trade_date_daily",
            "USD/troy_oz",
            retrieved_at,
            provider_as_of=cutoff_utc,
            available_as_of=retrieved_at,
            status=ny17.QUALITY_STATUS,
            payload_hash=base.sha256_bytes(raw),
            metadata={
                "endpoint": ny17.TIME_SERIES_URL,
                "vendor_symbol": ny17.SYMBOL,
                "provider_interval": ny17.INTERVAL,
                "requested_timezone": "America/New_York",
                "trade_date": d.isoformat(),
                "session_definition_authority": "CME Group / EBS Market",
                "trade_date_boundary": "17:00 ET",
                "source_bar_open_time": f"{d.isoformat()} 16:59:00 America/New_York",
                "price_field": "close",
                "price_semantic": "end_of_16_59_minute_bar_internal_17ET_decision_reference",
                "availability_policy": "BACKFILL_RETRIEVAL_TIME_FLOOR_NOT_HISTORICALLY_KNOWABLE",
                "evidence_class": "HISTORICAL_BACKFILL_CURRENTLY_RETRIEVED",
                "rights_policy": "PRIVATE_INTERNAL_NON_DISPLAY_NO_PUBLIC_RAW_REDISTRIBUTION",
                "fallback_policy": "NONE",
            },
        )))
        time_mod.sleep(INTER_DATE_PACING_SECONDS)

    # Atomic safety rule: no partial DB write if any provider/request failure remains
    # after retries. Missing market/holiday bars are separate and may be legitimate.
    if provider_errors:
        summary = ",".join(
            f"{x['date']}:{x['error']}:{x['http_status']}" for x in provider_errors
        )
        raise RuntimeError(f"BACKFILL_PROVIDER_ERRORS:{len(provider_errors)}:{summary}")

    # Require enough coverage for both Fast SMA20 and Slow weekly SMA4+persistence.
    in_range_observations = [
        o for o in observations
        if start <= datetime.fromisoformat(o["observation_ts"]).astimezone(ny17.NY).date() <= end
    ]
    if len(in_range_observations) < 35:
        raise RuntimeError(f"BACKFILL_INSUFFICIENT_VALID_TRADE_DATES:{len(in_range_observations)}")
    covered = [o["observation_ts"] for o in in_range_observations]
    first = min(covered)
    last = max(covered)
    if (last - first).days < 50:
        raise RuntimeError("BACKFILL_INSUFFICIENT_CALENDAR_SPAN")

    present_dates = {
        datetime.fromisoformat(o["observation_ts"]).astimezone(ny17.NY).date()
        for o in observations
    }
    missing_anchors = [d.isoformat() for d in anchor_dates if d not in present_dates]
    if missing_anchors:
        raise RuntimeError("BACKFILL_REQUIRED_ANCHORS_MISSING:" + ",".join(missing_anchors))

    return {
        "run_id": run_id,
        "started_at": base.iso_utc(retrieved_at),
        "finished_at": base.iso_utc(datetime.now(timezone.utc)),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "backfill:twelve_xau_ny17",
        "observations": observations,
        "vintages": [],
        "quality_events": [],
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "anchor_dates": [d.isoformat() for d in anchor_dates],
        "valid_trade_dates": len(in_range_observations),
        "total_observations": len(observations),
        "missing_weekdays": missing,
        "retried_dates": len(retry_summary),
    }


def _verify_neon(anchor_dates: tuple[date, ...] = (), min_rows: int = 35) -> dict:
    import psycopg
    from psycopg.rows import dict_row
    from persist_neon import _db_url
    with psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
                select count(*) as n, min(observation_ts) as first_ts, max(observation_ts) as last_ts,
                       count(distinct date_trunc('week', observation_ts at time zone 'America/New_York')) as weeks,
                       count(*) filter (where quality_status=%s) as approved_n,
                       count(distinct lineage_id) as lineage_count,
                       (array_agg(source order by observation_ts desc, retrieved_at desc))[1] as latest_source
                from usable_observations
                where series_id=%s
            """, (ny17.QUALITY_STATUS, ny17.SERIES_ID))
            row = dict(cur.fetchone())
            if row["n"] < min_rows or row["approved_n"] < min_rows:
                raise RuntimeError(f"NEON_NY17_HISTORY_INSUFFICIENT:{row['n']}:{row['approved_n']}")
            if row["weeks"] < 8:
                raise RuntimeError(f"NEON_NY17_WEEK_COVERAGE_INSUFFICIENT:{row['weeks']}")
            if row["latest_source"] != ny17.SOURCE:
                raise RuntimeError("NEON_NY17_SOURCE_MISMATCH")
            anchor_present = 0
            for d in anchor_dates:
                cur.execute("""
                    select count(*) as n
                    from usable_observations
                    where series_id=%s
                      and quality_status=%s
                      and (observation_ts at time zone 'America/New_York')::date=%s
                """, (ny17.SERIES_ID, ny17.QUALITY_STATUS, d))
                if int(cur.fetchone()["n"]) < 1:
                    raise RuntimeError(f"NEON_NY17_REQUIRED_ANCHOR_MISSING:{d.isoformat()}")
                anchor_present += 1
            row["required_anchor_count"] = len(anchor_dates)
            row["required_anchor_present"] = anchor_present
        conn.rollback()
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2026-07-01")
    p.add_argument("--end", default="2026-08-31")
    p.add_argument("--anchor", action="append", default=[])
    p.add_argument("--persist", action="store_true")
    args = p.parse_args()
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    anchors = tuple(date.fromisoformat(x) for x in args.anchor)
    bundle = collect_range(start, end, anchors)
    print(json.dumps({
        "range_start": bundle["range_start"],
        "range_end": bundle["range_end"],
        "anchor_dates": bundle["anchor_dates"],
        "valid_trade_dates": bundle["valid_trade_dates"],
        "total_observations": bundle["total_observations"],
        "missing_weekday_count": len(bundle["missing_weekdays"]),
        "retried_date_count": bundle["retried_dates"],
        "raw_market_values_logged": False,
        "database_write_requested": bool(args.persist),
    }, indent=2))
    if not args.persist:
        return 0
    result = persist_bundle(bundle)
    verify = _verify_neon(anchors)
    print(json.dumps({"persist": result, "verify": verify}, indent=2, default=str))
    if result.get("status") != "SUCCESS":
        return 1
    print("TWELVE_XAU_NY17_HISTORY_BACKFILL_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
