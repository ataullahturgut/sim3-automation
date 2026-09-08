from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gold_axis_2026.tools import emergency_intraday_replay_validation_v146 as emergency
from gold_axis_2026.tools import xau_intraday_cache_model_replay_v1 as full

# Conservative partial-cache scope: only months whose 1m cache row counts
# match the frozen direct-API baseline exactly. June and July 2026 are excluded.
PARTIAL_START_MONTH = "2023-01"
PARTIAL_END_MONTH = "2026-05"
EXPECTED_ELIGIBLE_1M_ROWS = 1_305_943
EXPECTED_EMERGENCY_PARTIAL = {
    "months_requested_with_anchor": 41,
    "months_retrieved": 41,
    "observed_minutes": 1_305_943,
    "level_episodes": 908,
    "reversal_alert_episodes": 714,
    "reversal_alert_rows": 204_479,
    "cross_through_transitions": 7,
    "cross_through_without_expected_alert": 0,
    "zero_observation_months": [],
}
EXCLUDED_1M_RANGES = [
    {
        "reason": "INCOMPLETE_MONTH_18200_BASELINE_MINUTES_NOT_CACHED",
        "missing_from": "2026-06-01T00:00:00+00:00",
        "missing_through": "2026-06-13T15:19:00+00:00",
        "replay_exclusion": "ENTIRE_2026-06_MONTH",
    },
    {
        "reason": "MONTH_NOT_CACHED_44640_BASELINE_MINUTES",
        "missing_from": "2026-07-01T00:00:00+00:00",
        "missing_through": "2026-07-31T23:59:00+00:00",
        "replay_exclusion": "ENTIRE_2026-07_MONTH",
    },
]


def _run_emergency_partial(json_path: Path, csv_path: Path) -> int:
    orig_session = emergency._session
    orig_earliest = emergency._earliest_timestamp
    orig_fetch = emergency._fetch_month
    argv = sys.argv[:]
    try:
        emergency._session = lambda: None
        emergency._earliest_timestamp = full._cache_earliest
        emergency._fetch_month = full._cache_fetch_month
        sys.argv = [
            "emergency_intraday_replay_validation_v146.py",
            "--start-month", PARTIAL_START_MONTH,
            "--end-month", PARTIAL_END_MONTH,
            "--output-json", str(json_path),
            "--output-csv", str(csv_path),
        ]
        rc = emergency.main()
    finally:
        sys.argv = argv
        emergency._session = orig_session
        emergency._earliest_timestamp = orig_earliest
        emergency._fetch_month = orig_fetch

    report = json.loads(json_path.read_text())
    report["input_source"] = "NEON_RESEARCH_CACHE"
    report["cache_tables"] = ["xau_intraday_research_cache_1m"]
    report["provider_requests_this_replay"] = 0
    report["partial_cache_scope"] = True
    report["excluded_1m_ranges"] = EXCLUDED_1M_RANGES
    report["production_promotion"] = "BLOCKED_RESEARCH_ONLY"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    return rc


def _equivalence_partial(m: dict, e: dict) -> dict:
    checks: list[dict] = []

    def ck(name, actual, expected, tol=0.0):
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            ok = abs(actual - expected) <= tol
        else:
            ok = actual == expected
        checks.append({
            "check": name,
            "status": "PASS" if ok else "FAIL",
            "actual": actual,
            "expected": expected,
        })

    # 5m Market Shock cache is complete, so retain the frozen full-scope checks.
    ck("MARKET_ROWS", m["history"]["rows"], full.EXPECTED_MARKET["rows"])
    ck("MARKET_FIRST_TS", m["history"]["first_ts"], full.EXPECTED_MARKET["first_ts"])
    ck("MARKET_LAST_TS", m["history"]["last_ts"], full.EXPECTED_MARKET["last_ts"])
    seg = {int(x["year"]): x["consensus"] for x in m["segments"]}
    for year, exp in full.EXPECTED_MARKET["segments"].items():
        ck(f"MARKET_{year}_SIGNAL_BARS", seg[year]["signal_bars"], exp["signal_bars"])
        ck(f"MARKET_{year}_EPISODES", seg[year]["episodes"], exp["episodes"])
    ck(
        "MARKET_MIN_2PCT_POWER",
        m["gates"]["MIN_2PCT_SYNTHETIC_CONSENSUS_POWER"],
        full.EXPECTED_MARKET["min_2pct_power"],
        1e-12,
    )
    ck(
        "MARKET_MAX_RATE",
        m["gates"]["MAX_HISTORICAL_CONSENSUS_BAR_RATE"],
        full.EXPECTED_MARKET["max_rate"],
        1e-15,
    )

    # 1m Emergency is compared only on the complete 2023-01..2026-05 overlap.
    for key, expected in EXPECTED_EMERGENCY_PARTIAL.items():
        ck(f"EMERGENCY_PARTIAL_{key.upper()}", e["aggregate"][key], expected)

    return {
        "contract": "GOLD_CONTROL_XAU_INTRADAY_PARTIAL_CACHE_REPLAY_EQUIVALENCE_V1",
        "baseline_api_run_id": full.EXPECTED_RUN_ID,
        "baseline_head_sha": "61f7b21f54083258be16d4e2acc182979dff1ce2",
        "methodology_changed": False,
        "data_source_execution_changed": "TWELVE_DIRECT_TO_NEON_RESEARCH_CACHE",
        "comparison_scope": {
            "market_5m": "FULL_2020-04-06_THROUGH_2026-08-31",
            "emergency_1m": f"{PARTIAL_START_MONTH}_THROUGH_{PARTIAL_END_MONTH}",
            "eligible_1m_rows": EXPECTED_ELIGIBLE_1M_ROWS,
            "excluded_1m_ranges": EXCLUDED_1M_RANGES,
        },
        "provider_requests_this_replay": 0,
        "checks": checks,
        "status": "PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL",
        "equivalence_class": "PARTIAL_CACHE_EQUIVALENCE_ONLY",
        "prospective_claim": False,
        "production_promotion": "BLOCKED_RESEARCH_ONLY",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--market-json", default="market_shock_partial_cache_replay_v1.json")
    p.add_argument("--emergency-json", default="emergency_partial_cache_replay_v146.json")
    p.add_argument("--emergency-csv", default="emergency_partial_cache_replay_v146_months.csv")
    p.add_argument("--equivalence-json", default="xau_intraday_partial_cache_replay_equivalence_v1.json")
    args = p.parse_args()

    mpath = Path(args.market_json)
    epath = Path(args.emergency_json)
    cpath = Path(args.emergency_csv)
    qpath = Path(args.equivalence_json)

    rc1 = full._run_market(mpath)
    rc2 = _run_emergency_partial(epath, cpath)
    m = json.loads(mpath.read_text())
    e = json.loads(epath.read_text())
    eq = _equivalence_partial(m, e)
    qpath.write_text(json.dumps(eq, indent=2, sort_keys=True))
    print(json.dumps(eq, indent=2, sort_keys=True))
    return 0 if rc1 == 0 and rc2 == 0 and eq["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
