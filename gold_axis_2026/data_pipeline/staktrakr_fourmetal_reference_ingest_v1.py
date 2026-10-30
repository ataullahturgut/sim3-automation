#!/usr/bin/env python3
"""Non-destructive StakTrakr API -> Neon separate four-metal UTC reference ledger.

- Fetches public endpoint, not moving raw GitHub main.
- Day is UTC reference/day average; never NY17 and never substitutes canonical.
- No invented firstprint/backfill PIT: every row permanently labelled non-PIT.
- Append-only source row hashes; revisions do not overwrite earlier source data.
- Current UTC day excluded to avoid an unfinished session.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://api.staktrakr.com/data/spot-history-2026.json"
CODES = {"Gold": "AU", "Silver": "AG", "Platinum": "PT", "Palladium": "PD"}
DEST = "gold_weekly_live.staktrakr_daily_utc_reference_v1"
SOURCE_CLASS = "PUBLIC_API_FETCH_NOT_ORIGIN_PIT"


def validated_rows(raw: bytes, now: datetime):
    obj = json.loads(raw.decode("utf-8"), parse_float=Decimal)
    if not isinstance(obj, list):
        raise ValueError("STAK_PUBLIC_SOURCE_NOT_JSON_LIST")
    by_day = defaultdict(dict)
    for v in obj:
        if not isinstance(v, dict) or v.get("metal") not in CODES:
            continue
        key = CODES[v["metal"]]
        raw_ts = str(v.get("timestamp", ""))
        day = datetime.strptime(raw_ts[:10], "%Y-%m-%d").date()
        if day.year != 2026:
            raise ValueError("STAK_PRICE_DATE_OUTSIDE_2026")
        if day >= now.date():
            continue  # unfinished current UTC day or improperly future-dated
        try:
            value = Decimal(str(v["spot"]))
        except (InvalidOperation, KeyError):
            raise ValueError("STAK_BAD_SPOT_NUMBER")
        if not value.is_finite() or value <= 0:
            raise ValueError("STAK_NONPOSITIVE_SPOT")
        if key in by_day[day]:
            raise ValueError("STAK_DUPLICATE_METAL_DAY_" + str(day))
        by_day[day][key] = (day, key, value, raw_ts,
                             str(v.get("source") or ""),
                             str(v.get("provider") or ""))
    aligned_days = sorted(d for d, values in by_day.items()
                          if set(values) == set(CODES.values()))
    if len(aligned_days) < 200:
        raise ValueError("STAK_2026_FOUR_METAL_ALIGNED_COVERAGE_LOW")
    weekdays = [d for d in aligned_days if d.weekday() < 5]
    if (now.date() - weekdays[-1]).days > 5:
        raise ValueError("STAK_FOUR_METAL_PRICE_FEED_STALE")
    source_sha = hashlib.sha256(raw).hexdigest()
    records = []
    for day in aligned_days:
        for metal in sorted(CODES.values()):
            d, m, price, stamp, event, provider = by_day[day][metal]
            canonical = json.dumps(
                [d.isoformat(), m, format(price, "f"), stamp, event, provider],
                ensure_ascii=False, separators=(",", ":"))
            row_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            records.append((m, d, price, stamp, event, provider,
                            row_sha, source_sha, URL))
    evidence = {
        "schema": "GOLD_STAKTRAKR_PUBLIC_UTC_REFERENCE_INGEST_V1",
        "sourceUrl": URL, "sourceSha256": source_sha,
        "lastCompletedDate": weekdays[-1].isoformat(),
        "alignedDays": len(aligned_days),
        "alignedWeekdays": len(weekdays),
        "rowsValidated": len(records),
        "sourceClass": SOURCE_CLASS,
        "priceReference": "STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17",
        "originalV34FirstprintProven": False,
    }
    return records, evidence


def fetch():
    req = Request(URL, headers={"User-Agent": "Gold-Control-Reference-Collector/1.0",
                                "Accept": "application/json"})
    with urlopen(req, timeout=25) as r:
        blob = r.read(3_000_001)
        if len(blob) < 1000 or len(blob) > 3_000_000:
            raise ValueError("STAK_PAYLOAD_SIZE_INVALID")
        return blob


def apply_append(records):
    import psycopg
    uri = os.getenv("NEON_DATABASE_URL", "").strip()
    if not uri:
        raise ValueError("NEON_DATABASE_URL_REQUIRED")
    # Connection applies only to the separate research-quality ledger.
    sql = """
        INSERT INTO gold_weekly_live.staktrakr_daily_utc_reference_v1
          (metal, price_date, spot_usd_oz, source_row_timestamp,
           source_event, upstream_provider, source_row_sha256,
           raw_snapshot_sha256, source_url)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (metal,price_date,source_row_sha256) DO NOTHING
        RETURNING id
    """
    written = 0
    with psycopg.connect(uri, connect_timeout=15) as db:
        with db.cursor() as cur:
            for row in records:
                cur.execute(sql, row)
                if cur.fetchone() is not None:
                    written += 1
        db.commit()
    return written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dry-run", "apply"], required=True)
    parser.add_argument("--allow-research-only", action="store_true")
    parser.add_argument("--out", default="staktrakr_reference_ingest_report.json")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    rows, report = validated_rows(fetch(), now)
    report["retrievedAtUTC"] = now.isoformat()
    report["mode"] = args.mode
    report["written"] = 0
    report["canonicalNY17Overwritten"] = False
    report["liveANNForecastCreated"] = False
    if args.mode == "apply":
        if not args.allow_research_only:
            raise RuntimeError("RESEARCH_ONLY_APPEND_EXPLICIT_FLAG_REQUIRED")
        report["written"] = apply_append(rows)
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
