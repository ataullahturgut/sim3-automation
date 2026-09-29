from __future__ import annotations

import argparse, hashlib, io, json, time, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

START="2010-01-01"
END="2026-09-29"
EXPECTED_V1_PAYLOAD="c52670ccf7bccc75e7c92e6d8261fe25d2d8c62b986300d45d5f264a26142353"

FRED_DAILY={
    "NASDAQ100":"NASDAQ100",
    "WTI":"DCOILWTICO",
    "BRENT":"DCOILBRENTEU",
}

SOURCE_AUTHORITY={
    "NASDAQ100":{
        "upstream_source":"Nasdaq, Inc.",
        "redistributor":"Federal Reserve Bank of St. Louis FRED",
        "frequency":"DAILY_CLOSE",
        "units":"INDEX",
        "availability_lag_days":1,
    },
    "WTI":{
        "upstream_source":"U.S. Energy Information Administration",
        "redistributor":"Federal Reserve Bank of St. Louis FRED",
        "frequency":"DAILY",
        "units":"USD_PER_BARREL",
        "availability_lag_days":7,
    },
    "BRENT":{
        "upstream_source":"U.S. Energy Information Administration",
        "redistributor":"Federal Reserve Bank of St. Louis FRED",
        "frequency":"DAILY",
        "units":"USD_PER_BARREL",
        "availability_lag_days":7,
    },
}

def sha_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def sha_obj(x)->str:
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def get(url:str, timeout=60)->bytes:
    last=None
    for attempt in range(5):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-research/2.0"})
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"DOWNLOAD_FAILED {url} {type(last).__name__}:{last}")

def fetch_fred_daily(series_id:str):
    url=(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
         f"&cosd={START}&coed={END}")
    raw=get(url,90)
    df=pd.read_csv(io.BytesIO(raw))
    if len(df.columns)<2:
        raise RuntimeError(f"BAD_FRED_COLUMNS {series_id} {list(df.columns)}")
    df=df.iloc[:,:2].copy()
    df.columns=["date","value"]
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df["value"]=pd.to_numeric(df["value"],errors="coerce")
    df=df.dropna(subset=["date","value"]).sort_values("date")
    df=df[(df.date>=pd.Timestamp(START))&(df.date<=pd.Timestamp(END))]
    if df.empty:
        raise RuntimeError(f"NO_FRED_ROWS {series_id}")
    if df.date.duplicated().any():
        raise RuntimeError(f"DUPLICATE_DATES {series_id}")
    out={r.date.strftime("%Y-%m-%d"):float(r.value) for r in df.itertuples(index=False)}
    return out,{
        "series_id":series_id,
        "url":url,
        "sha256":sha_bytes(raw),
        "first":min(out),
        "last":max(out),
        "n":len(out),
    }

def month_avg(daily:dict[str,float]):
    s=pd.Series(daily,dtype=float)
    s.index=pd.to_datetime(s.index)
    return {str(k):float(v) for k,v in s.groupby(s.index.to_period("M")).mean().items()}

def coverage_diag(name,daily, min_total, min_monthly=10):
    idx=pd.to_datetime(list(daily))
    vals=np.array(list(daily.values()),float)
    if len(daily)<min_total:
        raise RuntimeError(f"{name}_TOO_FEW total={len(daily)} min={min_total}")
    if not np.all(np.isfinite(vals)):
        raise RuntimeError(f"{name}_NONFINITE")
    if np.any(vals<=0):
        raise RuntimeError(f"{name}_NONPOSITIVE")
    months=pd.Series(1,index=idx).groupby(idx.to_period("M")).sum()
    required=pd.period_range("2010-01","2024-12",freq="M")
    missing=[str(m) for m in required if m not in months.index]
    if missing:
        raise RuntimeError(f"{name}_MISSING_MONTHS {missing[:12]}")
    thin={str(m):int(months.loc[m]) for m in required if int(months.loc[m])<min_monthly}
    return {
        "n":len(daily),"first":min(daily),"last":max(daily),
        "min_value":float(vals.min()),"max_value":float(vals.max()),
        "required_months":len(required),"thin_months":thin,
        "min_required_monthly_observations":min_monthly,
    }

def parity(a:dict[str,float], b:dict[str,float], end="2026-07"):
    common=sorted(k for k in set(a)&set(b) if k<=end)
    pairs=[(a[k],b[k]) for k in common if np.isfinite(a[k]) and np.isfinite(b[k]) and b[k]!=0]
    if not pairs:
        return {"n":0,"status":"NO_OVERLAP"}
    aa=np.array([x for x,_ in pairs],float)
    bb=np.array([y for _,y in pairs],float)
    diff=np.abs(aa-bb)
    rel=diff/np.abs(bb)
    return {
        "n":len(pairs),
        "median_abs_diff":float(np.median(diff)),
        "p95_abs_diff":float(np.quantile(diff,.95)),
        "max_abs_diff":float(diff.max()),
        "median_abs_rel_diff":float(np.median(rel)),
        "p95_abs_rel_diff":float(np.quantile(rel,.95)),
        "corr":float(np.corrcoef(aa,bb)[0,1]) if len(aa)>2 else None,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v1-store",required=True)
    ap.add_argument("--output",default="gold_monthly_external_authority_v2.json")
    a=ap.parse_args()

    v1=json.loads(Path(a.v1_store).read_text())
    if v1.get("payload_sha256")!=EXPECTED_V1_PAYLOAD:
        raise RuntimeError(f"V1_PAYLOAD_MISMATCH {v1.get('payload_sha256')}")

    daily={}; meta={}
    for name,sid in FRED_DAILY.items():
        daily[name],meta[name]=fetch_fred_daily(sid)

    diag={
        "NASDAQ100":coverage_diag("NASDAQ100",daily["NASDAQ100"],min_total=3500,min_monthly=10),
        "WTI":coverage_diag("WTI",daily["WTI"],min_total=3500,min_monthly=10),
        "BRENT":coverage_diag("BRENT",daily["BRENT"],min_total=3500,min_monthly=10),
    }

    ndx_m=month_avg(daily["NASDAQ100"])
    core_ndx={m:float(z["NASDAQ_AVG_MONTHLY"]) for m,z in v1["core5_monthly"].items() if z.get("NASDAQ_AVG_MONTHLY") is not None}
    wb=v1["commodity_monthly"]
    wb_wti={m:float(z["WTI"]) for m,z in wb.items() if z.get("WTI") is not None}
    wb_brent={m:float(z["BRENT"]) for m,z in wb.items() if z.get("BRENT") is not None}

    diagnostics={
        "coverage":diag,
        "nasdaq_daily_monthly_avg_vs_core5":parity(ndx_m,core_ndx),
        "wti_daily_monthly_avg_vs_world_bank":parity(month_avg(daily["WTI"]),wb_wti),
        "brent_daily_monthly_avg_vs_world_bank":parity(month_avg(daily["BRENT"]),wb_brent),
    }

    out={
        "schema":"GOLD_MONTHLY_EXTERNAL_AUTHORITY_V2_2026-09-29",
        "authority":{
            "role":"RAW_FREQUENCY_AUTHORITY_BEFORE_F4_RESTART",
            "neon_reads":0,
            "model_results_in_this_stage":False,
            "no_synthetic_daily_data":True,
            "historical_market_series_class":"HISTORICAL_RECONSTRUCTION_NOT_VINTAGE",
            "v1_store_payload_sha256":EXPECTED_V1_PAYLOAD,
            "selection_use":"NONE",
            "2025_selection_use":"NONE",
            "2026_selection_use":"NONE",
        },
        "source_authority":SOURCE_AUTHORITY,
        "source_meta":meta,
        "nasdaq100_daily":daily["NASDAQ100"],
        "wti_daily":daily["WTI"],
        "brent_daily":daily["BRENT"],
        "h15_daily":v1["h15_daily"],
        "h15_meta":v1["h15_meta"],
        "h10_daily":v1["h10_daily"],
        "h10_meta":v1["h10_meta"],
        "vix_daily":v1["vix_daily"],
        "vix_meta":v1["vix_meta"],
        "cpi_monthly":v1["cpi_monthly"],
        "cpi_meta":v1["cpi_meta"],
        "commodity_monthly":v1["commodity_monthly"],
        "commodity_meta":v1["commodity_meta"],
        "core5_monthly":v1["core5_monthly"],
        "core5_meta":v1["core5_meta"],
        "readiness":{
            "rates_daily":"READY_FED_H15",
            "fx_daily":"READY_FED_H10",
            "vix_daily":"READY_CBOE",
            "nasdaq100_daily":"READY_FRED_UPSTREAM_NASDAQ",
            "wti_daily":"READY_FRED_UPSTREAM_EIA",
            "brent_daily":"READY_FRED_UPSTREAM_EIA",
            "cpi":"READY_MONTHLY_NATIVE_FREQUENCY",
            "copper":"READY_MONTHLY_WORLD_BANK__DAILY_NOT_PROVEN",
            "cpi_daily":"NOT_APPLICABLE_NATIVE_MONTHLY_STATISTIC",
        },
        "diagnostics":diagnostics,
    }
    out["payload_sha256"]=sha_obj(out)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("EXTERNAL_AUTHORITY_V2_GATE=PASS")
    print(json.dumps({
        "payload_sha256":out["payload_sha256"],
        "readiness":out["readiness"],
        "source_meta":meta,
        "diagnostics":diagnostics,
    },sort_keys=True))

if __name__=="__main__":
    main()
