"""Official free daily history and no-charge vendor access/cost preflight.
No purchased historical data. Existing frozen source files are never overwritten.
"""
from __future__ import annotations
import csv, hashlib, io, json, os, time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
START = pd.Timestamp("2020-01-01")
END = pd.Timestamp("2026-10-07")  # 2026-10-08 daily close may not be ready
HEADERS = {"User-Agent": "Gold-Governed-Free-Backfill/1.0", "Accept": "text/csv,application/json,*/*"}
GVZ_URL = "https://cdn-api.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv"
H15_URL = "https://www.federalreserve.gov/datadownload/Output.aspx?filetype=csv&from=&label=include&lastobs=&layout=seriescolumn&rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&to=&type=package"
DFII10_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10"
FILES = {
    "GVZ": ("GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv", "GOLD_GVZCLS_RAW_2021_2025.csv"),
    "DGS2": ("GOLD_EXECUTION_DGS2_FREE_CANDIDATE_2020_20261007.csv", "GOLD_DGS2_RAW_2022_2025.csv"),
    "DFII10": ("GOLD_EXECUTION_DFII10_FREE_CANDIDATE_2020_20261007.csv", None),
}
SUMMARY = AX / "GOLD_EXECUTION_FREE_SOURCE_STAGE1_2026-10-08.json"

def get_public(url, tries=3):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=(12, 55))
            r.raise_for_status()
            if len(r.content) < 80: raise ValueError("PUBLIC_SOURCE_SHORT_RESPONSE")
            return r
        except (requests.RequestException, ValueError) as e:
            last = e
            if i + 1 < tries: time.sleep(2 * (i + 1))
    raise RuntimeError("PUBLIC_SOURCE_FETCH_FAILED:" + type(last).__name__)

def parse_gvz(raw):
    q = pd.read_csv(io.BytesIO(raw))
    q.columns = [str(c).strip().upper() for c in q.columns]
    date_col = "DATE" if "DATE" in q else q.columns[0]
    val_col = "GVZ" if "GVZ" in q else "CLOSE" if "CLOSE" in q else None
    if val_col is None: raise ValueError("GVZ_CLOSE_COLUMN_MISSING")
    return q[[date_col, val_col]].set_axis(["date", "value"], axis=1)

def parse_h15(raw):
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
    k = next((i for i, r in enumerate(rows) if r and r[0].strip() == "Time Period"), None)
    if k is None: raise ValueError("H15_TIME_PERIOD_MISSING")
    heads = [x.strip() for x in rows[k]]
    if "RIFLGFCY02_N.B" not in heads: raise ValueError("H15_DGS2_ID_MISSING")
    c = heads.index("RIFLGFCY02_N.B")
    return pd.DataFrame(((r[0], r[c]) for r in rows[k+1:] if len(r) > c), columns=["date", "value"])

def parse_dfii10(raw):
    q = pd.read_csv(io.BytesIO(raw))
    q.columns = [str(c).strip().upper() for c in q.columns]
    dc = "DATE" if "DATE" in q else "OBSERVATION_DATE" if "OBSERVATION_DATE" in q else None
    if dc is None or "DFII10" not in q: raise ValueError("DFII10_SOURCE_SCHEMA_MISMATCH")
    return q[[dc, "DFII10"]].set_axis(["date", "value"], axis=1)

def normalize(q):
    q = q.copy()
    q["date"] = pd.to_datetime(q["date"], errors="coerce", utc=True).dt.tz_localize(None)
    q["value"] = pd.to_numeric(q["value"], errors="coerce")
    q = q.dropna(subset=["date", "value"])
    q = q[(q.date >= START) & (q.date <= END)]
    q = q.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    if not q.empty and (q.date.dt.hour != 0).any(): raise ValueError("NON_DAILY_DATE")
    return q

def qc(q, oldpath):
    annual = {str(int(y)): int(len(g)) for y, g in q.groupby(q.date.dt.year)}
    low = {str(y): {"rows": annual.get(str(y), 0), "minimum": 150 if y == 2026 else 180}
           for y in range(2020, 2027)
           if annual.get(str(y), 0) < (150 if y == 2026 else 180)}
    report = {"rows": len(q), "first": str(q.date.min().date()) if len(q) else None,
              "last": str(q.date.max().date()) if len(q) else None,
              "annual": annual, "thin_years": low,
              "overlap_rows": 0, "overlap_conflicts": 0}
    if oldpath and oldpath.exists():
        old = normalize(pd.read_csv(oldpath))
        m = q.merge(old, on="date", how="inner", suffixes=("_new", "_old"))
        diff = (m.value_new - m.value_old).abs()
        report.update(overlap_rows=len(m),
                      overlap_conflicts=int((diff > 1e-8).sum()),
                      overlap_max_abs_delta=float(diff.max()) if len(m) else None,
                      frozen_rows=len(old),
                      overlap_insufficient=len(m) < max(50, int(len(old) * 0.9)))
    report["acceptance"] = ("CANDIDATE_READY" if not low and not report["overlap_conflicts"]
                             and not report.get("overlap_insufficient") else "QUARANTINED_REVIEW_REQUIRED")
    return report

def fetch_daily(name, url, parse):
    resp = get_public(url)
    q = normalize(parse(resp.content))
    if q.empty: raise ValueError("EMPTY_DAILY_HISTORY")
    out_name, old_name = FILES[name]
    dest = AX / out_name
    q.to_csv(dest, index=False, date_format="%Y-%m-%d", float_format="%.10g")
    report = qc(q, AX / old_name if old_name else None)
    report.update(status="DOWNLOADED_FREE_CANDIDATE", source_url=url,
                  filename=out_name,
                  raw_sha256=hashlib.sha256(resp.content).hexdigest(),
                  csv_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                  origin_use="D_MINUS_1_UNTIL_PUBLICATION_CLOCK_PROVEN")
    return report

def probe_twelve():
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key: return {"status": "SECRET_NOT_AVAILABLE", "charged_download": False}
    probes = []
    for day in ("2020-06-01", "2021-06-01", "2026-10-06"):
        d = pd.Timestamp(day)
        params = {"symbol": "XAU/USD", "interval": "15min", "timezone": "UTC",
                  "start_date": d.strftime("%Y-%m-%d 00:00:00"),
                  "end_date": (d + pd.Timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"),
                  "outputsize": 200, "order": "ASC", "apikey": key}
        try:
            r = requests.get("https://api.twelvedata.com/time_series", params=params, timeout=(12, 35))
            p = r.json()
            if not isinstance(p, dict): raise ValueError("TWELVE_NON_OBJECT")
            vals = p.get("values") or []
            times = sorted(str(v.get("datetime", "")) for v in vals if isinstance(v, dict) and v.get("datetime"))
            probes.append({"date": day, "http_status": r.status_code,
                           "api_code": str(p.get("code", ""))[:30],
                           "rows": len(times), "first_utc": times[0] if times else None,
                           "last_utc": times[-1] if times else None,
                           "status": "SAMPLE_AVAILABLE" if times else "NOT_PROVEN"})
            if r.status_code == 429 or str(p.get("code")) in ("429", "402", "403"): break
        except Exception as e:
            probes.append({"date": day, "status": "PROBE_FAILED", "error_type": type(e).__name__})
            break
        time.sleep(9)
    return {"status": "READ_ONLY_SAMPLE_PROBE", "interval": "15min",
            "symbol": "XAU/USD", "probes": probes,
            "bulk_2020_2021_access": "NOT_PROVEN_BY_SAMPLE_ALONE",
            "vendor_raw_prices_saved": False, "charged_download": False}

def probe_databento():
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key: return {"status": "SECRET_NOT_AVAILABLE", "charged_download": False}
    import databento as db
    cl = db.Historical(key)
    cases = {
        "GC_1m_2020_week": ("ohlcv-1m", "2020-06-01", "2020-06-08"),
        "GC_1m_2024_week": ("ohlcv-1m", "2024-06-03", "2024-06-10"),
        "GC_1m_2026_week": ("ohlcv-1m", "2026-09-01", "2026-09-08"),
        "GC_1h_gap_2020_2021": ("ohlcv-1h", "2020-01-01", "2022-01-01"),
        "GC_1h_gap_2025_2026": ("ohlcv-1h", "2025-01-01", "2026-10-08"),
    }
    estimates = {}
    for name, (schema, start, end) in cases.items():
        try:
            cost = cl.metadata.get_cost(dataset="GLBX.MDP3", symbols=["GC.n.0"],
                                        stype_in="continuous", schema=schema,
                                        start=start, end=end)
            estimates[name] = {"status": "QUOTE_ONLY", "estimated_usd": float(cost)}
        except Exception as e:
            estimates[name] = {"status": "QUOTE_UNAVAILABLE", "error_type": type(e).__name__}
    return {"status": "QUOTES_ONLY_NO_DOWNLOAD", "estimates": estimates, "charged_download": False}

def main():
    AX.mkdir(parents=True, exist_ok=True)
    result = {"authority": "GOLD_EXECUTION_2020_2026_DATA_ACQUISITION_AUTHORITY_2026-10-08.md",
              "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "asof": "2026-10-08", "last_matured_daily_date_limit": "2026-10-07",
              "priced_historical_download_executed": False, "model_retrained": False,
              "daily_sources": {}}
    for name, url, parser in (("GVZ", GVZ_URL, parse_gvz), ("DGS2", H15_URL, parse_h15),
                              ("DFII10", DFII10_URL, parse_dfii10)):
        try:
            result["daily_sources"][name] = fetch_daily(name, url, parser)
        except Exception as e:
            result["daily_sources"][name] = {"status": "SOURCE_FETCH_OR_SCHEMA_FAILED",
                                              "error_type": type(e).__name__}
    for name, fn in (("xau15m_twelve_probe", probe_twelve),
                      ("gc_databento_cost_probe", probe_databento)):
        try: result[name] = fn()
        except Exception as e:
            result[name] = {"status": "PROBE_FAILED", "error_type": type(e).__name__}
    result["status"] = ("ALL_DAILY_CANDIDATES_READY" if
                        all(result["daily_sources"][x].get("acceptance") == "CANDIDATE_READY"
                            for x in FILES) else "PARTIAL_OR_QUARANTINED")
    SUMMARY.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "daily": {k: {"status": v.get("status"), "rows": v.get("rows"),
                                     "acceptance": v.get("acceptance"), "thin_years": v.get("thin_years"),
                                     "overlap_conflicts": v.get("overlap_conflicts")}
                                for k, v in result["daily_sources"].items()},
                      "xau15m": result["xau15m_twelve_probe"],
                      "gc_cost": result["gc_databento_cost_probe"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
