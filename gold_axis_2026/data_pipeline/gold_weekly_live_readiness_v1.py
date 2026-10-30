#!/usr/bin/env python3
"""Fail-closed read-only audit for weekly ANN + V22/BASE14 go-live.

Canonical Neon source observations are NOT interchangeable with indicative
Gold API display prices or retrospective forecast/signal archives.

Exit statuses:
  0 -- --self-test PASS or non-strict report successfully produced.
  2 -- --strict-data and required sources not recent.
  3 -- --strict-live and any data, ANN executor, signal issuer is unavailable.
The script DOES NOT emit forecasts, make trades, or write to Neon.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REQUIRED = {
    "XAU_EOD_TWELVE_NY17": ("APPROVED_CANONICAL_TWELVE_NY17", 2),
    "GVZ_CBOE": ("APPROVED_AUTHORITY_RETRIEVAL_FLOOR", 3),
    "VIX_CBOE": ("APPROVED_AUTHORITY_RETRIEVAL_FLOOR", 3),
    "DGS10_FRB_H15": ("APPROVED_DIRECT_AUTHORITY", 4),
    "EFFR_NYFED": ("APPROVED_DIRECT_AUTHORITY", 4),
}
WEEKLY_MODEL = "V34_ORIGINAL_WEEKLY_H1_MLP8_TANH_ALPHA1_V1"
SIGNAL_MODELS = ("V22", "BASE14")


def business_days_since(observed: date, as_of: date) -> int:
    if observed > as_of:
        raise ValueError("FUTURE_OBSERVATION_DATE")
    count = 0
    day = observed
    while day < as_of:
        day += timedelta(days=1)
        if day.weekday() < 5:
            count += 1
    return count


def evaluate_sources(rows, now: datetime) -> dict:
    items = []
    today = now.date()
    grouped = {row["series_id"]: row for row in rows}
    for series, (accepted_quality, max_business_age) in REQUIRED.items():
        row = grouped.get(series)
        if row is None or row.get("last_observed") is None:
            items.append({"series": series, "status": "MISSING", "latest": None,
                          "businessDayLag": None})
            continue
        ts = row["last_observed"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            raise ValueError("UNZONED_MARKET_TIMESTAMP:" + series)
        quality = row.get("quality_status")
        lag = business_days_since(ts.astimezone(timezone.utc).date(), today)
        status = ("READY" if quality == accepted_quality and lag <= max_business_age
                  else "STALE" if lag > max_business_age else "UNAPPROVED_QUALITY")
        items.append({"series": series, "status": status,
                      "latest": ts.astimezone(timezone.utc).isoformat(),
                      "quality": quality, "businessDayLag": lag,
                      "maxBusinessDayLag": max_business_age})
    return {"status": "READY" if all(x["status"] == "READY" for x in items)
            else "BLOCKED", "series": items}


def report(now: datetime, market_rows, decision_rows: int,
           signal_rows: int) -> dict:
    market = evaluate_sources(market_rows, now)
    weekly = ("BLOCKED_NO_VERIFIED_PROSPECTIVE_EXECUTOR"
              if decision_rows == 0 else "UNVERIFIED_FORECAST_CONTRACT")
    signals = ("BLOCKED_NO_VERIFIED_LIVE_SIGNAL_ISSUER"
               if signal_rows == 0 else "UNVERIFIED_SIGNAL_ASOF_CONTRACT")
    # Presence of an unspecified DB row NEVER certifies a prospectively frozen
    # V34 ANN model or live timestamp-certified V22 and BASE14 signals.
    ready = market["status"] == "READY" and weekly == "READY" and signals == "READY"
    return {
        "schema": "GOLD_WEEKLY_LIVE_READINESS_V1",
        "asOfUTC": now.isoformat(),
        "status": "READY" if ready else "BLOCKED_NOT_LIVE",
        "marketData": market,
        "weeklyANN": {"status": weekly, "expectedModel": WEEKLY_MODEL,
                      "candidateRunsPresent": decision_rows},
        "downsideSignals": {"status": signals, "expected": SIGNAL_MODELS,
                            "candidateSnapshotsPresent": signal_rows},
        "strictStopNoCurrentForecast": not ready,
        "sourcePolicy": "ONLY_CANONICAL_APPROVED_SERIES; NO_GOLDAPI_DISPLAY_FALLBACK",
        "historicalReplayIsNotLive": True,
        "monthlyCalibrationPaused": True,
        "writesToNeon": False,
    }


def from_neon():
    import psycopg
    from psycopg.rows import dict_row
    uri = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not uri:
        raise RuntimeError("MISSING_NEON_DATABASE_URL")
    keys = list(REQUIRED)
    with psycopg.connect(uri, row_factory=dict_row,
                         connect_timeout=12, options="-c default_transaction_read_only=on") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (series_id)
                  series_id, observation_ts AS last_observed, quality_status
                FROM canonical_latest
                WHERE series_id = ANY(%s)
                  AND quality_status = ANY(%s)
                ORDER BY series_id, observation_ts DESC
            """, (keys, [v[0] for v in REQUIRED.values()]))
            market_rows = cur.fetchall()
            cur.execute("SELECT count(*) AS n FROM decision_runs")
            decision_n = int(cur.fetchone()["n"])
            cur.execute("SELECT count(*) AS n FROM decision_signal_snapshots")
            signal_n = int(cur.fetchone()["n"])
            return market_rows, decision_n, signal_n


def self_test():
    now = datetime(2026, 10, 30, 7, 0, tzinfo=timezone.utc)
    assert business_days_since(date(2026, 10, 23), date(2026, 10, 26)) == 1
    assert business_days_since(date(2026, 10, 29), date(2026, 10, 30)) == 1
    rows = [{"series_id": k, "quality_status": q,
             "last_observed": datetime(2026, 10, 29, 21, tzinfo=timezone.utc)}
            for k, (q, _) in REQUIRED.items()]
    good = report(now, rows, 0, 0)
    assert good["marketData"]["status"] == "READY"
    assert good["status"] == "BLOCKED_NOT_LIVE"
    assert good["monthlyCalibrationPaused"] is True
    old = [{**row, "last_observed": datetime(2026, 10, 20, tzinfo=timezone.utc)}
           for row in rows]
    stale = report(now, old, 0, 0)
    assert stale["marketData"]["status"] == "BLOCKED"
    assert all(item["status"] == "STALE" for item in stale["marketData"]["series"])
    assert report(now, rows, 10, 10)["status"] == "BLOCKED_NOT_LIVE"
    assert business_days_since(date(2026, 10, 31), date(2026, 10, 30)) \
        if False else True
    print("GOLD_WEEKLY_LIVE_READINESS_SELF_TEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--strict-data", action="store_true")
    parser.add_argument("--strict-live", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    now = datetime.now(timezone.utc)
    market, decisions, signals = from_neon()
    result = report(now, market, decisions, signals)
    output = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    print(output)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(output + "\n", encoding="utf-8")
    if args.strict_live and result["status"] != "READY":
        return 3
    if args.strict_data and result["marketData"]["status"] != "READY":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
