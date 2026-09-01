from __future__ import annotations

import io
import json
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


def load_world_bank_gold() -> pd.Series:
    r = requests.get(WB_URL, headers={"User-Agent": "Gold-Control-Audit/1.0"}, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Monthly Prices", header=None)

    # World Bank Pink Sheet workbook layout: commodity names and units are in
    # metadata rows; data rows use YYYYMMM / YYYYMmm style date codes.
    gold_col = None
    date_col = 0
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
        ds = str(row.iloc[date_col]).strip()
        m = re.match(r"^(\d{4})M(\d{1,2})$", ds, re.I)
        if not m:
            continue
        y, mo = int(m.group(1)), int(m.group(2))
        val = pd.to_numeric(row.iloc[gold_col], errors="coerce")
        if pd.isna(val):
            continue
        rows.append((pd.Timestamp(y, mo, 1), float(val)))
    if not rows:
        raise RuntimeError("WORLD_BANK_GOLD_DATA_NOT_PARSED")
    s = pd.Series(dict(rows)).sort_index()
    s.name = "world_bank_gold"
    return s


def fetch_twelve_hourly_month(api_key: str, month: pd.Timestamp) -> tuple[float | None, int, str | None]:
    # Reconstruct a research monthly NY17 reference from Twelve 1h history.
    # 16:00 America/New_York bar closes at 17:00 ET; overlap audit already
    # proved equality with exact 16:59 1min close on sampled recent dates.
    start = month.strftime("%Y-%m-01 00:00:00")
    end = (month + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d 23:59:59")
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
    for attempt in range(6):
        r = requests.get(TWELVE_URL, params=params, timeout=90)
        try:
            j = r.json()
        except Exception:
            j = {}
        if r.status_code == 429 or (isinstance(j, dict) and j.get("code") == 429):
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code != 200 or (isinstance(j, dict) and j.get("status") == "error"):
            return None, 0, f"HTTP_{r.status_code}_API_{j.get('code') if isinstance(j, dict) else 'NA'}"
        vals = j.get("values", []) if isinstance(j, dict) else []
        closes = []
        for z in vals:
            dt = str(z.get("datetime", ""))
            if dt.endswith("16:00:00"):
                try:
                    closes.append(float(z["close"]))
                except Exception:
                    pass
        if closes:
            return float(np.mean(closes)), len(closes), None
        return None, 0, "NO_1600_BAR"
    return None, 0, "RATE_LIMIT_EXHAUSTED"


def main() -> None:
    wb = load_world_bank_gold()
    print(f"WORLD_BANK_START={wb.index.min().strftime('%Y-%m')}")
    print(f"WORLD_BANK_END={wb.index.max().strftime('%Y-%m')}")
    print(f"WORLD_BANK_MONTHS={len(wb)}")
    print(f"WORLD_BANK_HAS_2016_01={pd.Timestamp('2016-01-01') in wb.index}")

    prod_path = ROOT / "production_closure" / "production_history_43.csv"
    prod = pd.read_csv(prod_path)
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

    # Pre-frozen overlap sample: full calendar months spread across 2020-2026.
    sample_months = pd.to_datetime([
        "2020-04-01", "2020-09-01", "2021-03-01", "2021-11-01",
        "2022-06-01", "2022-12-01", "2023-06-01", "2023-12-01",
        "2024-06-01", "2024-12-01", "2025-06-01", "2025-12-01",
        "2026-01-01", "2026-03-01", "2026-05-01", "2026-07-01",
    ])
    rows = []
    for m in sample_months:
        ny17, n, err = fetch_twelve_hourly_month(api_key, m)
        if err:
            print(f"OVERLAP_MONTH={m.strftime('%Y-%m')} STATUS={err} N_NY17=0")
        else:
            wbval = float(wb.loc[m]) if m in wb.index else math.nan
            abs_gap = abs(ny17 - wbval) if math.isfinite(wbval) else math.nan
            rel_bps = abs_gap / abs(wbval) * 10000 if math.isfinite(wbval) and wbval != 0 else math.nan
            rows.append((m, wbval, ny17, n, abs_gap, rel_bps))
            print(f"OVERLAP_MONTH={m.strftime('%Y-%m')} STATUS=PASS N_NY17={n} ABS_GAP_LOGGED=NO")
        time.sleep(4)

    if len(rows) < 10:
        raise RuntimeError(f"INSUFFICIENT_OVERLAP_MONTHS:{len(rows)}")
    a = np.array([r[1] for r in rows], float)
    b = np.array([r[2] for r in rows], float)
    abs_gap = np.abs(a-b)
    rel_bps = abs_gap/np.abs(a)*10000
    corr = float(np.corrcoef(a,b)[0,1])
    ret_a = np.diff(np.log(a)); ret_b = np.diff(np.log(b))
    ret_corr = float(np.corrcoef(ret_a, ret_b)[0,1]) if len(ret_a) >= 2 else math.nan
    sign_agree = float(np.mean(np.sign(ret_a) == np.sign(ret_b))) if len(ret_a) else math.nan
    print(f"OVERLAP_VALID_MONTHS={len(rows)}")
    print(f"MONTHLY_LEVEL_CORR={corr:.12f}")
    print(f"MONTHLY_MEDIAN_ABS_GAP_USD={float(np.median(abs_gap)):.12f}")
    print(f"MONTHLY_P95_ABS_GAP_USD={float(np.quantile(abs_gap,0.95)):.12f}")
    print(f"MONTHLY_MEDIAN_ABS_GAP_BPS={float(np.median(rel_bps)):.9f}")
    print(f"MONTHLY_P95_ABS_GAP_BPS={float(np.quantile(rel_bps,0.95)):.9f}")
    print(f"MONTHLY_RETURN_CORR={ret_corr:.12f}")
    print(f"MONTHLY_RETURN_SIGN_AGREE={sign_agree:.9f}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    print("MODEL_SCORE_RUN=NONE")
    print("SUCCESSOR_WORLD_BANK_TARGET_AUDIT_COMPLETE")


if __name__ == "__main__":
    main()
