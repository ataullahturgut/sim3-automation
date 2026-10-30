#!/usr/bin/env python3
"""Audit free StakTrakr four-metal daily history vs GitHub snapshot (read-only).

StakTrakr public API daily observations are UTC-day spot averages / reference
quotes, not NY17 trading-session closing prices. Never mix them into the
canonical XAU_EOD_TWELVE_NY17 series or prospectively certify old vintages.
"""
from __future__ import annotations
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

METALS = ("Gold", "Silver", "Platinum", "Palladium")
ENDPOINTS = (
    ("staktrakr_public_api", "https://api.staktrakr.com/data/spot-history-2026.json"),
    ("staktrakr_github_main", "https://raw.githubusercontent.com/lbruton/StakTrakr/main/data/spot-history-2026.json"),
)


def download(url):
    request = Request(url, headers={"User-Agent": "Gold-Control-StakTrakr-Source-Probe/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=25) as resp:
        raw = resp.read(3_000_000)
        if not raw:
            raise ValueError("EMPTY_SOURCE_PAYLOAD")
        if len(raw) >= 3_000_000:
            raise ValueError("OVERSIZED_SOURCE_PAYLOAD")
        return raw


def summarize(raw, label, now):
    records = json.loads(raw)
    if not isinstance(records, list):
        raise ValueError("SOURCE_NOT_JSON_ARRAY")
    by = defaultdict(dict)
    duplicate = []
    discarded_future = 0
    for r in records:
        if not isinstance(r, dict) or r.get("metal") not in METALS:
            continue
        metal = r["metal"]
        raw_date = str(r.get("timestamp", ""))[:10]
        day = datetime.strptime(raw_date, "%Y-%m-%d").date()
        price = float(r["spot"])
        if not math.isfinite(price) or price <= 0:
            raise ValueError("NONPOSITIVE_OR_NONFINITE_METAL_PRICE")
        if day > now.date():
            discarded_future += 1
            continue
        if metal in by[day]:
            duplicate.append((day.isoformat(), metal))
        by[day][metal] = {
            "value": price, "source": r.get("source"),
            "provider": r.get("provider"), "timestamp": r.get("timestamp"),
        }
    if duplicate:
        raise ValueError("DUPLICATE_DAY_METAL:" + str(duplicate[:3]))
    per_metal = {}
    for metal in METALS:
        dates = sorted(d for d in by if metal in by[d])
        per_metal[metal] = {
            "rows": len(dates),
            "lastDay": dates[-1].isoformat() if dates else None,
            "lastValue": by[dates[-1]][metal]["value"] if dates else None,
            "lastSource": by[dates[-1]][metal]["source"] if dates else None,
            "lastProvider": by[dates[-1]][metal]["provider"] if dates else None,
        }
    complete = sorted(d for d, metals in by.items() if all(m in metals for m in METALS))
    weekday = [d for d in complete if d.weekday() < 5]
    recent = [d for d in weekday if (now.date() - d).days <= 20]
    return {
        "provider": label,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "series": per_metal,
        "fourMetalAlignedTotal": len(complete),
        "fourMetalAlignedWeekdays": len(weekday),
        "latestAlignedDay": complete[-1].isoformat() if complete else None,
        "latestAlignedWeekday": weekday[-1].isoformat() if weekday else None,
        "recentAlignedWeekdays": [d.isoformat() for d in recent],
        "futureRowsDiscarded": discarded_future,
        "scope": "UTC_DAILY_REFERENCE_NOT_NY17",
        "historicalOriginFirstprintCertified": False,
    }


def main():
    now = datetime.now(timezone.utc)
    report = {
        "schema": "GOLD_STAKTRAKR_4METAL_PUBLIC_FEED_PROBE_V1",
        "asOfUTC": now.isoformat(),
        "source": "lbruton/StakTrakr",
        "sourceIdentity": "PUBLIC_UTC_DAY_SPOT_REFERENCE_NOT_NY17",
        "databaseWrites": False,
        "modelPromoted": False,
        "results": [],
    }
    for label, url in ENDPOINTS:
        try:
            result = summarize(download(url), label, now)
            result["status"] = "SOURCE_FETCH_OK"
        except Exception as e:
            result = {"provider": label, "status": "SOURCE_FETCH_FAILED",
                      "error": type(e).__name__ + ": " + str(e)[:250]}
        report["results"].append(result)
    api = report["results"][0]
    git = report["results"][1]
    report["apiAccessible"] = api["status"] == "SOURCE_FETCH_OK"
    report["githubAccessible"] = git["status"] == "SOURCE_FETCH_OK"
    report["preferredSource"] = "staktrakr_public_api" if report["apiAccessible"] else "none"
    report["freshnessComparedToGithub"] = (
        "API_NEWER" if api["latestAlignedWeekday"] > git["latestAlignedWeekday"] else
        "API_SAME_DATE" if api["latestAlignedWeekday"] == git["latestAlignedWeekday"] else
        "API_OLDER"
    ) if report["apiAccessible"] and report["githubAccessible"] else "UNVERIFIED"
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    Path("staktrakr_public_feed_probe_v1_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if report["apiAccessible"] or report["githubAccessible"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
