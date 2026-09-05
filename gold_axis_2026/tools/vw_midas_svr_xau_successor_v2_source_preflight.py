from __future__ import annotations

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

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "vw_midas_svr_xau_successor_v2" / "source_preflight"
TWELVE_URL = "https://api.twelvedata.com/time_series"
SOURCE_START = pd.Timestamp("2022-03-01")
SOURCE_END = pd.Timestamp("2026-08-01")
MIN_DAILY = 15
GPR_SERIES = "GPR_OFFICIAL_GIT_PIT"
EXPECTED_GPR_ORIGINS = 54
EXPECTED_FIRST_GPR_ORIGIN = "2022-03"
EXPECTED_LAST_GPR_ORIGIN = "2026-08"


class PreflightError(RuntimeError):
    pass


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[pd.Timestamp]:
    return list(pd.date_range(start, end, freq="MS"))


def three_month_windows(start: pd.Timestamp, end: pd.Timestamp):
    cur = start
    while cur <= end:
        wend = min(cur + pd.offsets.MonthBegin(2), end)
        yield cur, wend
        cur = wend + pd.offsets.MonthBegin(1)


def request_json(session: requests.Session, params: dict, attempts: int = 5) -> dict:
    for attempt in range(attempts):
        try:
            response = session.get(TWELVE_URL, params=params, timeout=(20, 120))
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt + 1 == attempts:
                raise PreflightError(f"TWELVE_TRANSPORT_{type(exc).__name__}") from exc
            time.sleep(min(5 * (attempt + 1), 20))
            continue
        code = payload.get("code") if isinstance(payload, dict) else None
        if response.status_code == 429 or code == 429:
            if attempt + 1 == attempts:
                raise PreflightError("TWELVE_RATE_LIMIT_EXHAUSTED")
            time.sleep(65)
            continue
        if response.status_code != 200 or not isinstance(payload, dict) or payload.get("status") == "error":
            message = payload.get("message") if isinstance(payload, dict) else None
            category = "PLAN_OR_HISTORY_ACCESS" if code in (400, 403) else "API_ERROR"
            raise PreflightError(f"TWELVE_{category}_HTTP_{response.status_code}_API_{code or 'NA'}:{message or 'NO_MESSAGE'}")
        return payload
    raise AssertionError("unreachable")


def fetch_xau_hourly_reference(api_key: str) -> pd.Series:
    if not api_key:
        raise PreflightError("TWELVE_DATA_API_KEY_MISSING")
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-VW-Successor-V2-Source-Preflight/1.0"})
    rows: dict[pd.Timestamp, float] = {}
    for start, end in three_month_windows(SOURCE_START, SOURCE_END):
        end_day = end + pd.offsets.MonthEnd(0)
        payload = request_json(
            session,
            {
                "symbol": "XAU/USD",
                "interval": "1h",
                "start_date": start.strftime("%Y-%m-%d 00:00:00"),
                "end_date": end_day.strftime("%Y-%m-%d 23:59:59"),
                "timezone": "America/New_York",
                "order": "ASC",
                "outputsize": 5000,
                "apikey": api_key,
            },
        )
        for item in payload.get("values") or []:
            dt = str(item.get("datetime", ""))
            if not dt.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(dt)
                val = float(item["close"])
            except Exception:
                continue
            month = ts.to_period("M").to_timestamp()
            if val > 0 and SOURCE_START <= month <= SOURCE_END:
                rows[ts.normalize()] = val
        time.sleep(0.5)
    if not rows:
        raise PreflightError("BLOCKED_TWELVE_HOURLY_NO_NY17_REFERENCES")
    s = pd.Series(rows, dtype=float).sort_index()
    if s.index.has_duplicates:
        raise PreflightError("BLOCKED_TWELVE_DUPLICATE_DAILY_REFERENCE")
    return s


def audit_xau(daily: pd.Series) -> dict:
    expected = month_range(SOURCE_START, SOURCE_END)
    counts = daily.groupby(daily.index.to_period("M")).size()
    month_counts: dict[str, int] = {}
    for month in expected:
        n = int(counts.get(month.to_period("M"), 0))
        month_counts[month.strftime("%Y-%m")] = n
        if n < MIN_DAILY:
            raise PreflightError(f"BLOCKED_TWELVE_V2_MONTH_COVERAGE:{month.strftime('%Y-%m')}:{n}")
    h = hashlib.sha256()
    for ts, val in daily.items():
        h.update(f"{pd.Timestamp(ts).isoformat()}|{float(val):.10f}\n".encode())
    return {
        "series": "XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1",
        "symbol": "XAU/USD",
        "interval": "1h",
        "timezone": "America/New_York",
        "selector": "16:00:00 bar open, treated as hour ending at internal 17:00 ET reference",
        "months_expected": len(expected),
        "months_passed": len(month_counts),
        "first_month": min(month_counts),
        "last_month": max(month_counts),
        "minimum_daily_references": min(month_counts.values()),
        "maximum_daily_references": max(month_counts.values()),
        "daily_reference_rows": int(len(daily)),
        "input_fingerprint_sha256": h.hexdigest(),
        "raw_vendor_values_logged": False,
        "raw_vendor_values_committed": False,
    }


def audit_gpr_neon(database_url: str) -> dict:
    if not database_url:
        raise PreflightError("NEON_DATABASE_URL_MISSING")
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select metadata->>'origin_month' as origin_month,
                       count(*)::bigint as rows,
                       count(distinct lineage_id)::bigint as lineages,
                       count(distinct payload_hash)::bigint as payloads,
                       min(available_as_of) as available_as_of,
                       bool_and((metadata->>'historical_reconstruction_not_original_retrieval')::boolean) as reconstruction_truth,
                       bool_and(retrieved_at=first_seen_at) as retrieval_truth
                from observations
                where series_id=%s
                  and quality_status='APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH'
                group by metadata->>'origin_month'
                order by origin_month
                """,
                (GPR_SERIES,),
            )
            rows = [dict(r) for r in cur.fetchall()]
            cur.execute(
                "select count(*)::bigint as n from source_vintages where source_id like 'GPR_OFFICIAL_GIT_PIT_VINTAGE_%%'"
            )
            vintage_count = int(cur.fetchone()["n"])
    origins = [str(r["origin_month"]) for r in rows]
    if len(origins) != EXPECTED_GPR_ORIGINS:
        raise PreflightError(f"GPR_V2_ORIGIN_COUNT:{len(origins)}/{EXPECTED_GPR_ORIGINS}")
    if not origins or origins[0] != EXPECTED_FIRST_GPR_ORIGIN or origins[-1] != EXPECTED_LAST_GPR_ORIGIN:
        raise PreflightError(f"GPR_V2_ORIGIN_RANGE:{origins[0] if origins else 'NONE'}:{origins[-1] if origins else 'NONE'}")
    expected = [m.strftime("%Y-%m") for m in month_range(pd.Timestamp("2022-03-01"), pd.Timestamp("2026-08-01"))]
    if origins != expected:
        raise PreflightError("GPR_V2_ORIGIN_CONTINUITY_FAIL")
    if vintage_count != EXPECTED_GPR_ORIGINS:
        raise PreflightError(f"GPR_V2_VINTAGE_COUNT:{vintage_count}/{EXPECTED_GPR_ORIGINS}")
    for row in rows:
        if int(row["lineages"]) != 1 or int(row["payloads"]) != 1:
            raise PreflightError(f"GPR_V2_LINEAGE_OR_PAYLOAD_MULTIPLICITY:{row['origin_month']}")
        if row["reconstruction_truth"] is not True or row["retrieval_truth"] is not True:
            raise PreflightError(f"GPR_V2_TRUTH_METADATA_FAIL:{row['origin_month']}")
    return {
        "series": GPR_SERIES,
        "origin_count": len(origins),
        "first_origin": origins[0],
        "last_origin": origins[-1],
        "source_vintages": vintage_count,
        "continuous": True,
        "vintage_specific_lineage": True,
        "current_final_vintage_substitution": False,
        "database_write": False,
    }


def eligibility_arithmetic() -> dict:
    feature_complete_origins = list(pd.date_range("2022-09-01", "2026-08-01", freq="MS"))
    first_feature_origin = feature_complete_origins[0]
    # Target at origin p is p+1. At origin 2024-09 there are 24 completed feature-target rows,
    # but no inner origin itself has 24 prior rows. One additional completed target is required.
    first_outer_train_24_origin = pd.Timestamp("2024-09-01")
    first_tunable_outer_origin = pd.Timestamp("2024-10-01")
    validation_origins = list(pd.date_range("2024-10-01", "2025-09-01", freq="MS"))
    diagnostic_origins = list(pd.date_range("2025-10-01", "2026-07-01", freq="MS"))
    if len(validation_origins) != 12:
        raise AssertionError("VALIDATION_ORIGIN_COUNT_NOT_12")
    return {
        "first_feature_complete_origin": first_feature_origin.strftime("%Y-%m"),
        "first_outer_origin_with_24_training_rows": first_outer_train_24_origin.strftime("%Y-%m"),
        "first_fully_tunable_outer_origin": first_tunable_outer_origin.strftime("%Y-%m"),
        "validation_origins": [validation_origins[0].strftime("%Y-%m"), validation_origins[-1].strftime("%Y-%m")],
        "validation_origin_count": len(validation_origins),
        "validation_targets": [
            (validation_origins[0] + pd.offsets.MonthBegin(1)).strftime("%Y-%m"),
            (validation_origins[-1] + pd.offsets.MonthBegin(1)).strftime("%Y-%m"),
        ],
        "locked_diagnostic_origins": [diagnostic_origins[0].strftime("%Y-%m"), diagnostic_origins[-1].strftime("%Y-%m")],
        "model_score_observed_by_this_preflight": False,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    daily = fetch_xau_hourly_reference(api_key)
    xau = audit_xau(daily)
    gpr = audit_gpr_neon(database_url)
    eligibility = eligibility_arithmetic()
    evidence = {
        "engine_id": "VW_MIDAS_SVR_XAU_SUCCESSOR_V2",
        "evidence_class": "PRE_SCORE_SOURCE_AND_ELIGIBILITY_PREFLIGHT",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "xau_source_gate": xau,
        "gpr_source_gate": gpr,
        "eligibility_arithmetic": eligibility,
        "source_gate_pass": True,
        "model_scoring_executed": False,
        "prospective_claim": False,
        "database_write": False,
        "forecast_write": False,
        "decision_write": False,
        "raw_vendor_values_logged": False,
    }
    out = OUT_DIR / "source_preflight_evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print("VW_V2_SOURCE_PREFLIGHT=PASS")
    print(f"XAU_MONTHS={xau['months_passed']}/{xau['months_expected']}")
    print(f"XAU_MIN_DAILY_REFERENCES={xau['minimum_daily_references']}")
    print(f"GPR_ORIGINS={gpr['origin_count']}/{EXPECTED_GPR_ORIGINS}")
    print("FIRST_FULLY_TUNABLE_OUTER_ORIGIN=2024-10")
    print("VALIDATION_ORIGINS=2024-10..2025-09")
    print("MODEL_SCORING_EXECUTED=NO")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
