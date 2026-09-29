from __future__ import annotations
import argparse, csv, hashlib, io, json, math, time, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import gold_monthly_fx_h10_residual_v1 as h10

START="2010-01-01"
END="2026-09-29"
FRED_SERIES={
 "NASDAQ100":"Nasdaq, Inc. / FRED daily close",
 "SP500":"S&P Dow Jones Indices LLC / FRED daily close",
 "DGS10":"Federal Reserve Board H.15 / FRED",
 "DFII10":"Federal Reserve Board H.15 / FRED",
 "DFF":"Federal Reserve Board / FRED",
 "T10YIE":"Federal Reserve Bank of St. Louis / FRED",
 "VIXCLS":"Cboe / FRED",
}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def get(url,timeout=90,retries=5):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-market-drivers/1.0"})
            with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()
        except Exception as e:
            last=e;time.sleep(2*(i+1))
    raise RuntimeError(f"DOWNLOAD_FAILED {url} {type(last).__name__}:{last}")

def fred(series):
    url=f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={START}&coed={END}"
    raw=get(url)
    df=pd.read_csv(io.BytesIO(raw))
    date_col=df.columns[0];val_col=df.columns[-1]
    df["date"]=pd.to_datetime(df[date_col],errors="coerce")
    df["value"]=pd.to_numeric(df[val_col],errors="coerce")
    df=df.dropna(subset=["date","value"]).sort_values("date").drop_duplicates("date",keep="last")
    if df.empty:raise RuntimeError(f"FRED_EMPTY {series}")
    return {r.date.strftime("%Y-%m-%d"):float(r.value) for r in df[["date","value"]].itertuples(index=False)},{"url":url,"sha256":sha(raw),"first":df.date.iloc[0].strftime("%Y-%m-%d"),"last":df.date.iloc[-1].strftime("%Y-%m-%d"),"n":len(df)}

def monthly_last_return(series):
    s=pd.Series(series,dtype=float)
    s.index=pd.to_datetime(s.index)
    m=s.groupby(s.index.to_period("M")).last().sort_index()
    r=np.log(m/m.shift(1))
    return {str(k):float(v) for k,v in r.dropna().items()}

def load_risk_snapshot(path):
    d=json.loads(Path(path).read_text())
    return {r["origin_month"]:r for r in d["rows"]}

def build_h10():
    h10.START="01/01/2010";h10.END="09/29/2026"
    rr,hr=h10.fetch_package(h10.RATE_PACKAGE);ri,hi=h10.fetch_package(h10.INDEX_PACKAGE)
    rates=h10.parse_ddp(rr);idx=h10.parse_ddp(ri)
    cols={
      "EURUSD_QUOTE":h10.find_col(rates,"RXI$US_N.B.EU"),
      "GBPUSD_QUOTE":h10.find_col(rates,"RXI$US_N.B.UK"),
      "JPY_PER_USD":h10.find_col(rates,"RXI_N.B.JA"),
      "CHF_PER_USD":h10.find_col(rates,"RXI_N.B.SZ"),
      "CNY_PER_USD":h10.find_col(rates,"RXI_N.B.CH"),
      "BROAD_USD_INDEX":h10.find_col(idx,"JRXWTFB_N.B"),
    }
    rows={}
    for dt in sorted(set(rates.date).union(set(idx.date))):
        day=pd.Timestamp(dt).strftime("%Y-%m-%d");z={}
        for name,col in cols.items():
            src=idx if name=="BROAD_USD_INDEX" else rates
            q=src.loc[src.date==dt,col]
            if len(q):
                v=pd.to_numeric(q.iloc[-1],errors="coerce")
                if pd.notna(v):z[name]=float(v)
        if z:rows[day]=z
    return rows,{"rates_sha256":hr,"index_sha256":hi,"columns":cols,"start":"2010-01-01","end":"2026-09-29","source":"Federal Reserve Board H.10 DDP"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--risk-snapshot",required=True)
    ap.add_argument("--output",default="gold_monthly_long_history_market_drivers_v1.json")
    a=ap.parse_args()
    series={};source={}
    for sid in FRED_SERIES:
        series[sid],source[sid]=fred(sid)
    h10_rows,h10_source=build_h10()

    # Reconcile the known NASDAQ compact anomaly against independently retained
    # market-history reconstruction.
    risk=load_risk_snapshot(a.risk_snapshot)
    nas_ret=monthly_last_return(series["NASDAQ100"])
    anomaly={}
    for m in ("2023-10","2023-11","2023-12"):
        old=float(risk[m]["nasdaq100_logret"])
        new=float(nas_ret[m])
        anomaly[m]={"risk_snapshot":old,"rebuilt_from_daily_fred":new,"abs_diff":abs(old-new)}
        if abs(old-new)>1e-8:raise RuntimeError(f"NASDAQ_PARITY_FAIL {m} {old} {new}")
        if abs(new)<1e-6:raise RuntimeError(f"NASDAQ_ANOMALY_NOT_CORRECTED {m}")

    # Ensure enough history for native-model training.
    for sid,z in source.items():
        if z["first"]>"2010-01-05":raise RuntimeError(f"LONG_HISTORY_START_FAIL {sid} {z}")
        if sid in ("NASDAQ100","SP500","DGS10","DFF") and z["last"]<"2026-09-20":
            raise RuntimeError(f"CURRENT_COVERAGE_FAIL {sid} {z}")

    out={
      "schema":"GOLD_MONTHLY_LONG_HISTORY_MARKET_DRIVERS_V1_2026-09-29",
      "authority":{
        "neon_reads":0,
        "role":"RAW_DAILY_FEATURE_RESEARCH_STORE",
        "selection_use":"DERIVE_TRANSFORMS_AND_LAGS_INSIDE_CHRONOLOGICAL_EXPERIMENTS_ONLY",
        "historical_claim":"CURRENT_HISTORICAL_MARKET_OBSERVATION_RECONSTRUCTION_NOT_ORIGINAL_RETRIEVAL_VINTAGE",
        "macro_release_warning":"Do not treat revised macro releases as first-print vintages. CPI surprise remains separate/not supplied here.",
      },
      "fred_series":series,
      "fred_source":source,
      "h10_daily":h10_rows,
      "h10_source":h10_source,
      "nasdaq_reconciliation":{
        "old_external_pit_nasdaq_field_status":"SUPERSEDED_FOR_NASDAQ_ONLY",
        "replacement":"NASDAQ100 daily FRED/Nasdaq market close history",
        "known_zero_anomaly_months":["2023-10","2023-11","2023-12"],
        "parity_vs_existing_market_history":anomaly,
      },
      "candidate_feature_families":{
        "NASDAQ100":["level_control","1m_log_return","3m_momentum","6m_momentum","realized_volatility","drawdown","daily_midas"],
        "rates":["DGS10_level_change","DFII10_real_yield_level_change","DFF_level_change","real_nominal_spread","daily_midas"],
        "inflation_expectations":["T10YIE_level_change","daily_midas"],
        "equity_risk":["SP500_return","NASDAQ100_return","VIXCLS_level_change","realized_volatility","drawdown"],
        "fx":["broad_usd_return","cny_usdstrength_return","major_fx_returns","breadth","dispersion","daily_midas"],
      },
    }
    raw=json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    out["payload_sha256"]=sha(raw)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("LONG_HISTORY_MARKET_DRIVER_GATE=PASS")
    print(json.dumps({
      "series":source,
      "h10_days":len(h10_rows),
      "nasdaq_reconciliation":anomaly,
      "payload_sha256":out["payload_sha256"],
    },sort_keys=True))
if __name__=="__main__":main()
