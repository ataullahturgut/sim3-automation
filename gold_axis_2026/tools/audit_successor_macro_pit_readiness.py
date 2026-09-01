from __future__ import annotations

import io
import os
from pathlib import Path

import pandas as pd
import requests

FRED_SERIES = ["DGS10", "DFF", "DEXCHUS", "DTWEXBGS", "NASDAQ100", "SP500", "DJIA"]
CBOE = {
    "VIX": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
    "GVZ": "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv",
}
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
FRED_GRAPH = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"


def get(url: str, **kwargs) -> requests.Response:
    r = requests.get(url, timeout=(15, 90), headers={"User-Agent": "Gold-Control-Input-Audit/1.0"}, **kwargs)
    r.raise_for_status()
    return r


def audit_fred_current() -> None:
    for sid in FRED_SERIES:
        try:
            r = get(FRED_GRAPH, params={"id": sid})
            df = pd.read_csv(io.StringIO(r.text))
            date_col = df.columns[0]
            value_col = sid if sid in df.columns else df.columns[-1]
            dt = pd.to_datetime(df[date_col], errors="coerce")
            vv = pd.to_numeric(df[value_col], errors="coerce")
            ok = dt.notna() & vv.notna()
            d = dt[ok]
            if d.empty:
                print(f"FRED_CURRENT series={sid} status=NO_VALID_ROWS")
                continue
            has_2016 = bool(((d >= pd.Timestamp('2016-01-01')) & (d <= pd.Timestamp('2016-12-31'))).any())
            print(
                f"FRED_CURRENT series={sid} status=PASS start={d.min().date()} end={d.max().date()} "
                f"n={len(d)} has_2016={has_2016} raw_values_logged=NO"
            )
        except Exception as exc:
            print(f"FRED_CURRENT series={sid} status=ERROR_{type(exc).__name__}")


def audit_fred_past_asof() -> None:
    key = os.environ.get("FRED_API_KEY", "").strip()
    if not key:
        print("FRED_ALFRED_API_ACCESS=BLOCKED_SECRET_NOT_CONFIGURED")
        return
    print("FRED_ALFRED_API_ACCESS=SECRET_PRESENT")
    # Pre-score as-of probes. No values are logged; only whether non-missing observations
    # existed in the API's real-time view as of each historical month-end.
    probes = ["2016-01-31", "2016-06-30", "2016-12-31", "2020-01-31"]
    for sid in FRED_SERIES:
        for asof in probes:
            try:
                params = {
                    "series_id": sid,
                    "api_key": key,
                    "file_type": "json",
                    "realtime_start": asof,
                    "realtime_end": asof,
                    "observation_end": asof,
                    "sort_order": "desc",
                    "limit": 10,
                }
                j = get(FRED_API, params=params).json()
                obs = j.get("observations", []) if isinstance(j, dict) else []
                valid = [z for z in obs if str(z.get("value", ".")) not in {".", "", "nan", "None"}]
                print(f"FRED_ASOF series={sid} asof={asof} status={'PASS' if valid else 'NO_VALUE'} n_valid={len(valid)} raw_values_logged=NO")
            except Exception as exc:
                print(f"FRED_ASOF series={sid} asof={asof} status=ERROR_{type(exc).__name__}")


def audit_cboe() -> None:
    for sid, url in CBOE.items():
        try:
            r = get(url)
            df = pd.read_csv(io.StringIO(r.text))
            cols = {str(c).strip().upper(): c for c in df.columns}
            dc = cols.get("DATE") or df.columns[0]
            dt = pd.to_datetime(df[dc], errors="coerce").dropna()
            has_2016 = bool(((dt >= pd.Timestamp('2016-01-01')) & (dt <= pd.Timestamp('2016-12-31'))).any())
            print(f"CBOE_HISTORY series={sid} status=PASS start={dt.min().date()} end={dt.max().date()} n={len(dt)} has_2016={has_2016} raw_values_logged=NO")
        except Exception as exc:
            print(f"CBOE_HISTORY series={sid} status=ERROR_{type(exc).__name__}")


def audit_gpr() -> None:
    try:
        r = get(GPR_URL)
        book = pd.read_excel(io.BytesIO(r.content), sheet_name=None, engine="xlrd")
        best = None
        for _, df in book.items():
            cols = {str(c).strip().upper(): c for c in df.columns}
            if {"GPR", "GPRT", "GPRA"}.issubset(cols):
                dc = cols.get("MONTH") or cols.get("DATE") or df.columns[0]
                dt = pd.to_datetime(df[dc], errors="coerce").dropna()
                if best is None or len(dt) > len(best):
                    best = dt
        if best is None or len(best) == 0:
            print("GPR_CURRENT_HISTORY status=NO_VALID_ROWS")
            return
        has_2016 = bool(((best >= pd.Timestamp('2016-01-01')) & (best <= pd.Timestamp('2016-12-31'))).any())
        print(f"GPR_CURRENT_HISTORY status=PASS start={best.min().date()} end={best.max().date()} n={len(best)} has_2016={has_2016} raw_values_logged=NO")
        print("GPR_HISTORICAL_VINTAGE_STATUS=NOT_PROVEN_BY_CURRENT_WORKBOOK")
    except Exception as exc:
        print(f"GPR_CURRENT_HISTORY status=ERROR_{type(exc).__name__}")


def main() -> None:
    audit_fred_current()
    audit_fred_past_asof()
    audit_cboe()
    audit_gpr()
    print("DATABASE_WRITES=NONE")
    print("MODEL_SCORE_RUN=NONE")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    print("SUCCESSOR_MACRO_PIT_READINESS_AUDIT_COMPLETE")


if __name__ == "__main__":
    main()
