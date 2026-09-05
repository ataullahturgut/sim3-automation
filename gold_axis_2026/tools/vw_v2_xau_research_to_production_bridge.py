from __future__ import annotations

import hashlib
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "vw_midas_svr_xau_successor_v2" / "bridge" / "xau_research_to_production_bridge_evidence.json"
URL = "https://api.twelvedata.com/time_series"
START = pd.Timestamp("2025-07-01")
END = pd.Timestamp("2026-06-01")
MIN_DAILY = 15
LEVEL_CORR_MIN = 0.995
MEDIAN_GAP_BPS_MAX = 50.0
P95_GAP_BPS_MAX = 100.0
RETURN_CORR_MIN = 0.95
RETURN_SIGN_AGREEMENT_MIN = 0.80


class BridgeError(RuntimeError):
    pass


def request_json(session: requests.Session, params: dict, attempts: int = 12) -> dict:
    for attempt in range(attempts):
        try:
            r = session.get(URL, params=params, timeout=(20, 120))
            payload = r.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt + 1 == attempts:
                raise BridgeError(f"TWELVE_TRANSPORT_{type(exc).__name__}") from exc
            time.sleep(min(5 * (attempt + 1), 30))
            continue
        code = payload.get("code") if isinstance(payload, dict) else None
        if r.status_code == 429 or code == 429:
            if attempt + 1 == attempts:
                raise BridgeError("TWELVE_RATE_LIMIT_EXHAUSTED")
            time.sleep(65)
            continue
        if r.status_code != 200 or not isinstance(payload, dict) or payload.get("status") == "error":
            message = payload.get("message") if isinstance(payload, dict) else None
            raise BridgeError(f"TWELVE_HTTP_{r.status_code}_API_{code or 'NA'}:{message or 'NO_MESSAGE'}")
        return payload
    raise AssertionError("unreachable")


def fetch_research_hourly(api_key: str) -> pd.Series:
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-VW-V2-XAU-Bridge-Hourly/1.0"})
    rows: dict[pd.Timestamp, float] = {}
    cur = START
    while cur <= END:
        last_month = min(cur + pd.offsets.MonthBegin(2), END)
        end_day = last_month + pd.offsets.MonthEnd(0)
        payload = request_json(session, {
            "symbol": "XAU/USD",
            "interval": "1h",
            "start_date": cur.strftime("%Y-%m-%d 00:00:00"),
            "end_date": end_day.strftime("%Y-%m-%d 23:59:59"),
            "timezone": "America/New_York",
            "order": "ASC",
            "outputsize": 5000,
            "apikey": api_key,
        })
        for item in payload.get("values") or []:
            dt = str(item.get("datetime", ""))
            if not dt.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(dt).normalize()
                val = float(item["close"])
            except Exception:
                continue
            month = ts.to_period("M").to_timestamp()
            if START <= month <= END and math.isfinite(val) and val > 0:
                rows[ts] = val
        cur = last_month + pd.offsets.MonthBegin(1)
        time.sleep(1)
    s = pd.Series(rows, dtype=float).sort_index()
    if s.empty or s.index.has_duplicates:
        raise BridgeError("RESEARCH_HOURLY_EMPTY_OR_DUPLICATE")
    return s


def three_day_chunks(month: pd.Timestamp):
    start = month
    month_end = month + pd.offsets.MonthEnd(0)
    while start <= month_end:
        end = min(start + pd.Timedelta(days=2), month_end)
        yield start, end
        start = end + pd.Timedelta(days=1)


def fetch_exact_1min(api_key: str) -> pd.Series:
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-VW-V2-XAU-Bridge-Exact1m/1.0"})
    rows: dict[pd.Timestamp, float] = {}
    for month in pd.date_range(START, END, freq="MS"):
        for a, b in three_day_chunks(month):
            payload = request_json(session, {
                "symbol": "XAU/USD",
                "interval": "1min",
                "start_date": a.strftime("%Y-%m-%d 00:00:00"),
                "end_date": b.strftime("%Y-%m-%d 23:59:59"),
                "timezone": "America/New_York",
                "order": "ASC",
                "outputsize": 5000,
                "apikey": api_key,
            })
            for item in payload.get("values") or []:
                dt = str(item.get("datetime", ""))
                if not dt.endswith("16:59:00"):
                    continue
                try:
                    ts = pd.Timestamp(dt).normalize()
                    val = float(item["close"])
                except Exception:
                    continue
                if ts.to_period("M") == month.to_period("M") and math.isfinite(val) and val > 0:
                    rows[ts] = val
            time.sleep(0.5)
    s = pd.Series(rows, dtype=float).sort_index()
    if s.empty or s.index.has_duplicates:
        raise BridgeError("EXACT_1MIN_EMPTY_OR_DUPLICATE")
    return s


def fingerprint(s: pd.Series) -> str:
    h = hashlib.sha256()
    for ts, val in s.items():
        h.update(f"{pd.Timestamp(ts).isoformat()}|{float(val):.10f}\n".encode())
    return h.hexdigest()


def construct_monthly(research: pd.Series, exact: pd.Series) -> tuple[pd.Series, pd.Series, list[dict]]:
    r_monthly: dict[pd.Timestamp, float] = {}
    e_monthly: dict[pd.Timestamp, float] = {}
    coverage: list[dict] = []
    for month in pd.date_range(START, END, freq="MS"):
        rp = research[research.index.to_period("M") == month.to_period("M")]
        ep = exact[exact.index.to_period("M") == month.to_period("M")]
        r_dates = {pd.Timestamp(x).date() for x in rp.index}
        e_dates = {pd.Timestamp(x).date() for x in ep.index}
        if len(rp) < MIN_DAILY or len(ep) < MIN_DAILY:
            raise BridgeError(f"BRIDGE_MONTH_DAILY_COUNT_LT_{MIN_DAILY}:{month.strftime('%Y-%m')}:{len(rp)}:{len(ep)}")
        if r_dates != e_dates:
            only_r = len(r_dates - e_dates)
            only_e = len(e_dates - r_dates)
            raise BridgeError(f"BRIDGE_MONTH_DATE_SET_MISMATCH:{month.strftime('%Y-%m')}:{only_r}:{only_e}")
        r_monthly[month] = float(rp.mean())
        e_monthly[month] = float(ep.mean())
        coverage.append({"month": month.strftime("%Y-%m"), "research_days": len(rp), "exact_days": len(ep), "date_sets_equal": True})
    return pd.Series(r_monthly), pd.Series(e_monthly), coverage


def metric_payload(research_monthly: pd.Series, exact_monthly: pd.Series) -> tuple[dict, dict]:
    a = research_monthly.to_numpy(float)
    b = exact_monthly.to_numpy(float)
    if len(a) != 12 or len(b) != 12:
        raise BridgeError(f"BRIDGE_MONTH_COUNT_NOT_12:{len(a)}:{len(b)}")
    abs_bps = np.abs(a - b) / np.abs(b) * 10000.0
    level_corr = float(np.corrcoef(a, b)[0, 1])
    ra = np.diff(np.log(a))
    rb = np.diff(np.log(b))
    return_corr = float(np.corrcoef(ra, rb)[0, 1])
    sign_agree = float(np.mean(np.sign(ra) == np.sign(rb)))
    metrics = {
        "n_months": 12,
        "level_correlation": level_corr,
        "median_absolute_level_gap_bps": float(np.median(abs_bps)),
        "p95_absolute_level_gap_bps": float(np.quantile(abs_bps, 0.95)),
        "monthly_return_correlation": return_corr,
        "monthly_return_sign_agreement": sign_agree,
    }
    checks = {
        "level_correlation_gte_0_995": metrics["level_correlation"] >= LEVEL_CORR_MIN,
        "median_gap_bps_lte_50": metrics["median_absolute_level_gap_bps"] <= MEDIAN_GAP_BPS_MAX,
        "p95_gap_bps_lte_100": metrics["p95_absolute_level_gap_bps"] <= P95_GAP_BPS_MAX,
        "return_correlation_gte_0_95": metrics["monthly_return_correlation"] >= RETURN_CORR_MIN,
        "return_sign_agreement_gte_0_80": metrics["monthly_return_sign_agreement"] >= RETURN_SIGN_AGREEMENT_MIN,
    }
    return metrics, checks


def main() -> int:
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        research = fetch_research_hourly(api_key)
        exact = fetch_exact_1min(api_key)
        research_monthly, exact_monthly, coverage = construct_monthly(research, exact)
        metrics, checks = metric_payload(research_monthly, exact_monthly)
        passed = all(checks.values())
        result = "XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_PASS" if passed else "BLOCKED_XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_MATERIALITY_FAIL"
        evidence = {
            "engine_id": "VW_MIDAS_SVR_XAU_SUCCESSOR_V2",
            "evidence_class": "XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "window": ["2025-07", "2026-06"],
            "coverage": coverage,
            "metrics": metrics,
            "checks": checks,
            "bridge_pass": passed,
            "result": result,
            "research_input_fingerprint_sha256": fingerprint(research),
            "exact_input_fingerprint_sha256": fingerprint(exact),
            "raw_market_values_logged": False,
            "raw_market_values_committed": False,
            "database_write": False,
            "model_score_run": False,
            "prospective_claim": False,
        }
        OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("VW_V2_XAU_BRIDGE_SOURCE_COVERAGE=PASS")
        for row in coverage:
            print(f"BRIDGE_MONTH={row['month']} RESEARCH_DAYS={row['research_days']} EXACT_DAYS={row['exact_days']} DATE_SETS_EQUAL=YES")
        print(f"LEVEL_CORRELATION={metrics['level_correlation']:.12f}")
        print(f"MEDIAN_ABSOLUTE_LEVEL_GAP_BPS={metrics['median_absolute_level_gap_bps']:.9f}")
        print(f"P95_ABSOLUTE_LEVEL_GAP_BPS={metrics['p95_absolute_level_gap_bps']:.9f}")
        print(f"MONTHLY_RETURN_CORRELATION={metrics['monthly_return_correlation']:.12f}")
        print(f"MONTHLY_RETURN_SIGN_AGREEMENT={metrics['monthly_return_sign_agreement']:.9f}")
        print(f"VW_V2_XAU_BRIDGE={'PASS' if passed else 'FAIL'}")
        print(f"RESULT={result}")
        print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
        print("DATABASE_WRITES=NONE")
        print("MODEL_SCORE_RUN=NONE")
        return 0 if passed else 3
    except BridgeError as exc:
        evidence = {
            "engine_id": "VW_MIDAS_SVR_XAU_SUCCESSOR_V2",
            "evidence_class": "XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "window": ["2025-07", "2026-06"],
            "bridge_pass": False,
            "result": "BLOCKED_XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_SOURCE_OR_COVERAGE_NOT_PROVEN",
            "block_reason": str(exc),
            "raw_market_values_logged": False,
            "raw_market_values_committed": False,
            "database_write": False,
            "model_score_run": False,
            "prospective_claim": False,
        }
        OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("VW_V2_XAU_BRIDGE=BLOCKED")
        print(f"BLOCK_REASON={exc}")
        print("RESULT=BLOCKED_XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_SOURCE_OR_COVERAGE_NOT_PROVEN")
        print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
        print("DATABASE_WRITES=NONE")
        print("MODEL_SCORE_RUN=NONE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
