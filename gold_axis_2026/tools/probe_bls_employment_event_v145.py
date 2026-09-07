from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any

import requests

CONTRACT = "GOLD_CONTROL_BLS_EMPLOYMENT_EVENT_PREFLIGHT_V145"
API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
SERIES = {
    "NFP_LEVEL": "CES0000000001",
    "UNEMP_RATE": "LNS14000000",
    "AHE_LEVEL": "CES0500000003",
}


def _fetch(series_id: str) -> dict[str, Any]:
    response = requests.get(f"{API}{series_id}", timeout=(8, 30), headers={"User-Agent": "GoldControl-BLS-Event/1.0"})
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS_API_STATUS:{payload.get('status')}:{payload.get('message')}")
    series = (payload.get("Results") or {}).get("series") or []
    if len(series) != 1 or series[0].get("seriesID") != series_id:
        raise RuntimeError(f"BLS_SERIES_MISMATCH:{series_id}")
    data = series[0].get("data") or []
    monthly = [row for row in data if str(row.get("period") or "").startswith("M") and row.get("period") != "M13"]
    if len(monthly) < 2:
        raise RuntimeError(f"BLS_INSUFFICIENT_MONTHLY_DATA:{series_id}")
    return {"series_id": series_id, "latest": monthly[0], "previous": monthly[1]}


def probe() -> dict[str, Any]:
    fetched = {name: _fetch(series_id) for name, series_id in SERIES.items()}
    nfp_latest = float(fetched["NFP_LEVEL"]["latest"]["value"])
    nfp_prev = float(fetched["NFP_LEVEL"]["previous"]["value"])
    unemp = float(fetched["UNEMP_RATE"]["latest"]["value"])
    ahe_latest = float(fetched["AHE_LEVEL"]["latest"]["value"])
    ahe_prev = float(fetched["AHE_LEVEL"]["previous"]["value"])
    nfp_change = nfp_latest - nfp_prev
    ahe_mom = round((ahe_latest / ahe_prev - 1.0) * 100.0, 1)
    latest_periods = {name: f"{item['latest']['year']}-{item['latest']['period']}" for name, item in fetched.items()}
    same_period = len(set(latest_periods.values())) == 1
    return {
        "contract": CONTRACT,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "PROVEN_ACTUAL_SOURCE_ACCESS" if same_period else "BLOCKED_PERIOD_MISMATCH",
        "source": "U.S. Bureau of Labor Statistics Public Data API v2",
        "series": SERIES,
        "latest_periods": latest_periods,
        "derived_actuals": {
            "nfp_change_thousand": nfp_change,
            "unemployment_rate_percent": unemp,
            "ahe_mom_percent_rounded_1dp": ahe_mom,
        },
        "release_time_authority": "BLS Employment Situation schedule, 08:30 America/New_York",
        "actual_first_print_operational_note": "At future release time, poll only after official availability and persist first-seen values before later revisions.",
        "consensus_status": "BLOCKED_NO_APPROVED_PROSPECTIVE_PRE_RELEASE_CONSENSUS_PROVIDER",
        "macro_event_live_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="bls_employment_event_preflight_v145.json")
    args = parser.parse_args()
    result = probe()
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, default=str)
        handle.write("\n")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0 if result["status"] == "PROVEN_ACTUAL_SOURCE_ACCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
