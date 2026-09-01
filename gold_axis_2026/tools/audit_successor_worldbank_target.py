from __future__ import annotations

import io
import math
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
WB_URL = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
TWELVE_URL = "https://api.twelvedata.com/time_series"

# Frozen before successful overlap scoring. These are research-lineage
# materiality gates, not identity claims and not production forecast gates.
BRIDGE_LEVEL_CORR_MIN = 0.995
BRIDGE_MEDIAN_GAP_BPS_MAX = 50.0
BRIDGE_P95_GAP_BPS_MAX = 100.0
BRIDGE_RETURN_CORR_MIN = 0.95
BRIDGE_SIGN_AGREE_MIN = 0.80


def load_world_bank_gold() -> pd.Series:
    r = requests.get(WB_URL, headers={"User-Agent": "Gold-Control-Audit/1.0"}, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Monthly Prices", header=None)
    gold_col = None
    for rr in range(min(12, len(raw))):
        for cc in range(raw.shape[1]):
            v = str(raw.iat[rr, cc]).strip().lower()
            if v == "gold" or v.startswith("gold "):
                gold_col = cc
                break
        if gold_col is not None:
            break
    if gold_col is None:
        raise RuntimeError("WORLD_BANK_GOLD_COLUMN_NOT_FOUND")
    rows = []
    for _, row in raw.iterrows():
        ds = str(row.iloc[0]).strip()
        m = re.match(r"^(\d{4})M(\d{1,2})$", ds, re.I)
        if not m:
            continue
        y, mo = int(m.group(1)), int(m.group(2))
        val = pd.to_numeric(row.iloc[gold_col], errors="coerce")
        if pd.notna(val):
            rows.append((pd.Timestamp(y, mo, 1), float(val)))
    if not rows:
        raise RuntimeError("WORLD_BANK_GOLD_DATA_NOT_PARSED")
    s = pd.Series(dict(rows)).sort_index()
    s.name = "world_bank_gold"
    return s


def request_json(session: requests.Session, params: dict) -> tuple[dict | None, str | None]:
    for attempt in range(8):
        try:
            r = session.get(TWELVE_URL, params=params, timeout=120)
            j = r.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt == 7:
                return None, f"TRANSPORT_{type(exc).__name__}"
            time.sleep(min(15 * (attempt + 1), 65))
            continue
        code = j.get("code") if isinstance(j, dict) else None
        if r.status_code == 429 or code == 429:
            time.sleep(65)
            continue
        if r.status_code != 200 or (isinstance(j, dict) and j.get("status") == "error"):
            return None, f"HTTP_{r.status_code}_API_{code if code is not None else 'NA'}"
        return j, None
    return None, "RATE_LIMIT_EXHAUSTED"


def fetch_twelve_hourly_window(
    session: requests.Session, api_key: str, start_month: pd.Timestamp, end_month: pd.Timestamp
) -> tuple[dict[pd.Timestamp, tuple[float, int]], str | None]:
    start = start_month.strftime("%Y-%m-01 00:00:00")
    end = (end_month + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d 23:59:59")
    params = {
        "symbol": "XAU/USD",
        "interval": "1h",
        "start_date": start,
        "end_date": end,
        "timezone": "America/New_York",
        "outputsize": 5000,
        "apikey": api_key,
        "order": "ASC",
    }
    j, err = request_json(session, params)
    if err or not isinstance(j, dict):
        return {}, err or "INVALID_RESPONSE"
    by_month: dict[pd.Timestamp, list[float]] = {}
    for z in j.get("values", []):
        dt = str(z.get("datetime", ""))
        if not dt.endswith("16:00:00"):
            continue
        try:
            ts = pd.Timestamp(dt)
            m = pd.Timestamp(ts.year, ts.month, 1)
            by_month.setdefault(m, []).append(float(z["close"]))
        except Exception:
            continue
    return {m: (float(np.mean(v)), len(v)) for m, v in by_month.items() if v}, None


def main() -> None:
    wb = load_world_bank_gold()
    print(f"WORLD_BANK_START={wb.index.min().strftime('%Y-%m')}")
    print(f"WORLD_BANK_END={wb.index.max().strftime('%Y-%m')}")
    print(f"WORLD_BANK_MONTHS={len(wb)}")
    print(f"WORLD_BANK_HAS_2016_01={pd.Timestamp('2016-01-01') in wb.index}")
    frozen_range = pd.date_range("2016-01-01", "2026-07-01", freq="MS")
    missing_frozen = [m for m in frozen_range if m not in wb.index or not math.isfinite(float(wb.loc[m]))]
    print(f"WORLD_BANK_FROZEN_WINDOW_EXPECTED_MONTHS={len(frozen_range)}")
    print(f"WORLD_BANK_FROZEN_WINDOW_MISSING_MONTHS={len(missing_frozen)}")

    prod = pd.read_csv(ROOT / "production_closure" / "production_history_43.csv")
    prod["month_ts"] = pd.to_datetime(prod["month"] + "-01")
    merged = prod.merge(wb.rename("wb").rename_axis("month_ts").reset_index(), on="month_ts", how="left")
    actual = pd.to_numeric(merged["actual"], errors="coerce").to_numpy(float)
    wbv = pd.to_numeric(merged["wb"], errors="coerce").to_numpy(float)
    valid = np.isfinite(actual) & np.isfinite(wbv)
    diff = np.abs(actual[valid] - wbv[valid])
    print(f"PRODUCTION_COMMON_MONTHS={int(valid.sum())}")
    print(f"PRODUCTION_WB_EXACT_EQUAL_COUNT={int(np.sum(actual[valid] == wbv[valid]))}/{int(valid.sum())}")
    print(f"PRODUCTION_WB_MAX_ABS_DIFF={float(diff.max()) if len(diff) else math.nan:.12f}")
    print(f"PRODUCTION_WB_MEDIAN_ABS_DIFF={float(np.median(diff)) if len(diff) else math.nan:.12f}")

    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")

    windows = [
        ("2020-08-01", "2020-10-01"),
        ("2021-03-01", "2021-05-01"),
        ("2022-06-01", "2022-08-01"),
        ("2023-06-01", "2023-08-01"),
        ("2024-06-01", "2024-08-01"),
        ("2025-06-01", "2025-08-01"),
        ("2026-05-01", "2026-07-01"),
    ]
    rows = []
    ret_pairs: list[tuple[float, float]] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-Audit/1.0"})

    for a, b in windows:
        sm, em = pd.Timestamp(a), pd.Timestamp(b)
        got, err = fetch_twelve_hourly_window(session, api_key, sm, em)
        window_rows = []
        if err:
            print(f"OVERLAP_WINDOW={sm.strftime('%Y-%m')}..{em.strftime('%Y-%m')} STATUS={err}")
        else:
            for m in pd.date_range(sm, em, freq="MS"):
                if m not in got or m not in wb.index:
                    print(f"OVERLAP_MONTH={m.strftime('%Y-%m')} STATUS=MISSING")
                    continue
                ny17, n = got[m]
                wbval = float(wb.loc[m])
                rec = (m, wbval, ny17, n, abs(ny17 - wbval), abs(ny17 - wbval) / abs(wbval) * 10000)
                rows.append(rec)
                window_rows.append(rec)
                print(f"OVERLAP_MONTH={m.strftime('%Y-%m')} STATUS=PASS N_NY17={n} ABS_GAP_LOGGED=NO")
            window_rows.sort(key=lambda x: x[0])
            for prev, cur in zip(window_rows, window_rows[1:]):
                if cur[0] == prev[0] + pd.offsets.MonthBegin(1):
                    ret_pairs.append((math.log(cur[1] / prev[1]), math.log(cur[2] / prev[2])))
        time.sleep(12)

    if len(rows) < 15:
        raise RuntimeError(f"INSUFFICIENT_OVERLAP_MONTHS:{len(rows)}")
    if len(ret_pairs) < 10:
        raise RuntimeError(f"INSUFFICIENT_CONSECUTIVE_RETURN_PAIRS:{len(ret_pairs)}")

    rows.sort(key=lambda x: x[0])
    levels_wb = np.array([r[1] for r in rows], float)
    levels_ny = np.array([r[2] for r in rows], float)
    abs_gap = np.abs(levels_wb - levels_ny)
    rel_bps = abs_gap / np.abs(levels_wb) * 10000
    level_corr = float(np.corrcoef(levels_wb, levels_ny)[0, 1])
    ret_wb = np.array([x[0] for x in ret_pairs], float)
    ret_ny = np.array([x[1] for x in ret_pairs], float)
    ret_corr = float(np.corrcoef(ret_wb, ret_ny)[0, 1])
    sign_agree = float(np.mean(np.sign(ret_wb) == np.sign(ret_ny)))
    median_bps = float(np.median(rel_bps))
    p95_bps = float(np.quantile(rel_bps, 0.95))

    coverage_pass = len(missing_frozen) == 0
    bridge_pass = bool(
        coverage_pass
        and level_corr >= BRIDGE_LEVEL_CORR_MIN
        and median_bps <= BRIDGE_MEDIAN_GAP_BPS_MAX
        and p95_bps <= BRIDGE_P95_GAP_BPS_MAX
        and ret_corr >= BRIDGE_RETURN_CORR_MIN
        and sign_agree >= BRIDGE_SIGN_AGREE_MIN
    )

    print(f"OVERLAP_VALID_MONTHS={len(rows)}")
    print(f"CONSECUTIVE_RETURN_PAIRS={len(ret_pairs)}")
    print(f"MONTHLY_LEVEL_CORR={level_corr:.12f}")
    print(f"MONTHLY_MEDIAN_ABS_GAP_USD={float(np.median(abs_gap)):.12f}")
    print(f"MONTHLY_P95_ABS_GAP_USD={float(np.quantile(abs_gap, 0.95)):.12f}")
    print(f"MONTHLY_MEDIAN_ABS_GAP_BPS={median_bps:.9f}")
    print(f"MONTHLY_P95_ABS_GAP_BPS={p95_bps:.9f}")
    print(f"MONTHLY_RETURN_CORR={ret_corr:.12f}")
    print(f"MONTHLY_RETURN_SIGN_AGREE={sign_agree:.9f}")
    print(f"BRIDGE_LEVEL_CORR_MIN={BRIDGE_LEVEL_CORR_MIN}")
    print(f"BRIDGE_MEDIAN_GAP_BPS_MAX={BRIDGE_MEDIAN_GAP_BPS_MAX}")
    print(f"BRIDGE_P95_GAP_BPS_MAX={BRIDGE_P95_GAP_BPS_MAX}")
    print(f"BRIDGE_RETURN_CORR_MIN={BRIDGE_RETURN_CORR_MIN}")
    print(f"BRIDGE_SIGN_AGREE_MIN={BRIDGE_SIGN_AGREE_MIN}")
    print(f"WORLD_BANK_RESEARCH_BRIDGE_PASS={bridge_pass}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("MODEL_SCORE_RUN=NONE")
    print("SUCCESSOR_WORLD_BANK_TARGET_AUDIT_COMPLETE")


if __name__ == "__main__":
    main()
