"""Probe free four-metal APIs without changing Neon or publishing vendor prices.

Uses documented anonymous endpoints only. Does not assume that a 2010
timestamp means a real daily observation: verifies response grain and 4-metal
shared dates; a 2010 monthly value is NOT enough for VW-MIDAS daily inputs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

METALS = ("XAU", "XAG", "XPT", "XPD")
WINDOWS = {
    "2010": ("2010-06-14", "2010-06-18"),
    "2015": ("2015-06-15", "2015-06-19"),
    "2020": ("2020-06-15", "2020-06-19"),
    "2026": ("2026-10-12", "2026-10-16"),
}

def fetch_json(url: str, timeout: int = 14):
    headers = {"Accept": "application/json", "User-Agent": "GoldMonthlyResearchSourceCoverage/1.0"}
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            data = resp.read(700_000)
            return {"http_status": resp.status, "payload": json.loads(data.decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        # Never include token-bearing URL; these anonymous requests use no key.
        return {"http_status": exc.code, "error": "HTTP_" + str(exc.code)}
    except Exception as exc:
        return {"http_status": None, "error": type(exc).__name__ + ": " + str(exc)[:160]}

def check_live(payload):
    if not isinstance(payload, dict):
        return {"valid": False, "reason": "NOT_OBJECT"}
    price = payload.get("price")
    try:
        valid = math.isfinite(float(price)) and float(price) > 0
    except (TypeError, ValueError):
        valid = False
    return {
        "valid": valid,
        "symbol": payload.get("symbol"),
        "currency": payload.get("currency"),
        "updated_at": payload.get("updatedAt"),
        "unit_not_certified": True,
    }

def check_daily_window(payload, first: str, last: str):
    if not isinstance(payload, dict):
        return {"eligible": False, "reason": "NOT_OBJECT", "unique_daily_dates": []}
    points = payload.get("points")
    grain = str(payload.get("grain") or "UNKNOWN")
    if not isinstance(points, list):
        return {"eligible": False, "reason": "NO_POINTS", "grain": grain,
                "unique_daily_dates": [], "response_keys": sorted(payload)[:14]}
    daily = set()
    invalid = 0
    for row in points:
        if not isinstance(row, dict):
            invalid += 1
            continue
        stamp = str(row.get("t") or "")
        day = stamp[:10]
        try:
            parsed = dt.date.fromisoformat(day)
            val = float(row["price"])
            if not math.isfinite(val) or val <= 0:
                invalid += 1
                continue
        except (TypeError, KeyError, ValueError):
            invalid += 1
            continue
        if first <= day <= last and parsed.weekday() < 5:
            daily.add(day)
    # A single monthly point must not be promoted to a five-day daily series.
    eligible = grain.lower() in ("daily", "1d", "day") and len(daily) >= 2 and invalid == 0
    return {"eligible": eligible, "grain": grain, "points_in_response": len(points),
            "invalid_points": invalid, "unique_daily_dates": sorted(daily),
            "source": payload.get("source"), "unit": payload.get("unit"),
            "reason": "DAILY_WINDOW_PASS" if eligible else "NOT_VERIFIED_AS_DAILY_4METAL"}

def probe():
    live = {}
    for metal in METALS:
        url = "https://api.gold-api.com/price/" + metal
        resp = fetch_json(url)
        live[metal] = {"http_status": resp["http_status"],
                       **(check_live(resp["payload"]) if "payload" in resp
                          else {"valid": False, "error": resp.get("error")})}

    history = {}
    for year, (first, last) in WINDOWS.items():
        month = {}
        for metal in METALS:
            qs = urllib.parse.urlencode({"metal": metal, "start_date": first, "end_date": last})
            url = "https://standardbullion.com/api/v1/market/history?" + qs
            resp = fetch_json(url)
            month[metal] = {"http_status": resp["http_status"],
                            **(check_daily_window(resp["payload"], first, last)
                               if "payload" in resp else {"eligible": False,
                                    "unique_daily_dates": [], "error": resp.get("error")})}
        matching = set.intersection(*(set(month[m]["unique_daily_dates"]) for m in METALS))
        history[year] = {"metals": month,
                         "verified_common_daily_dates": sorted(matching),
                         "all_four_daily_eligible": all(month[m]["eligible"] for m in METALS)
                             and len(matching) >= 2}
    return {
        "report_version": "FREE_FOUR_METAL_PUBLIC_API_COVERAGE_V1",
        "scope": "ANONYMOUS_PUBLIC_ENDPOINT_REAL_HTTP_TEST_NO_NEON_WRITES",
        "gold_api_anonymous_live": live,
        "gold_api_history": {
            "status": "NOT_TESTED_NO_AUTHENTICATED_HISTORY_KEY",
            "reason": "gold-api.com history API requires a free account key; it does not publish independently validated 2010 XPT/XPD daily coverage",
            "published_free_quota": "10 history requests per hour",
        },
        "standard_bullion_daily_probe": history,
        "can_certify_2010_to_2026_one_provider": all(
            item["all_four_daily_eligible"] for item in history.values()
        ),
        "notes": [
            "Standard Bullion documents daily prices starting in 2011; older periods may return monthly history but that does not prove daily 2010 coverage.",
            "Both provider quote basis and benchmark method differ from original LBMA fixing.",
            "No imputation, no price changes, no database or GitHub secret reads.",
        ],
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    report = probe()
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({
        "result": "PUBLIC_API_COVERAGE_PROBE_FINISHED",
        "gold_api_live_4_metals": sum(bool(x.get("valid")) for x in report["gold_api_anonymous_live"].values()),
        "standard_bullion_four_metal_daily_eligible_by_year":
            {y: x["all_four_daily_eligible"] for y, x in report["standard_bullion_daily_probe"].items()},
        "one_source_2010_to_today_verified": report["can_certify_2010_to_2026_one_provider"],
        "gold_api_historical_unverified": True
    }, sort_keys=True))

if __name__ == "__main__":
    main()
