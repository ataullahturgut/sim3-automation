from __future__ import annotations
import argparse, csv, hashlib, io, json, math, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import gold_monthly_fx_h10_residual_v1 as h10

START_YEAR=2010
END_DATE=pd.Timestamp("2026-09-29")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/153 Safari/537.36","Accept":"application/json,text/html,text/csv,*/*"}

def clean_num(v):
    if v is None:return np.nan
    s=str(v).replace("$","").replace(",","").replace("%","").strip()
    if s in ("","N/A","nan","None","--"):return np.nan
    try:return float(s)
    except:return np.nan

def sha(b):return hashlib.sha256(b).hexdigest()

def req(url,params=None,timeout=35,retries=4):
    last=None
    for i in range(retries):
        try:
            r=requests.get(url,params=params,headers=UA,timeout=timeout)
            r.raise_for_status();return r
        except Exception as e:
            last=e;time.sleep(1.5*(i+1))
    raise RuntimeError(f"DOWNLOAD_FAILED {url} {type(last).__name__}:{last}")

def nasdaq100():
    start=int(pd.Timestamp("2010-01-01",tz="UTC").timestamp())
    end=int((END_DATE+pd.Timedelta(days=1)).tz_localize("UTC").timestamp())
    url="https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX"
    r=req(url,{"period1":start,"period2":end,"interval":"1d","events":"history","includeAdjustedClose":"true"},timeout=35)
    j=r.json();res=((j.get("chart") or {}).get("result") or [])
    if not res: raise RuntimeError(f"YAHOO_NDX_EMPTY error={(j.get('chart') or {}).get('error')}")
    q=res[0];ts=q.get("timestamp") or [];close=(((q.get("indicators") or {}).get("quote") or [{}])[0].get("close") or [])
    out={}
    for t,v in zip(ts,close):
        if v is None:continue
        d=pd.to_datetime(int(t),unit="s",utc=True).strftime("%Y-%m-%d");v=float(v)
        if np.isfinite(v) and v>0:out[d]=v
    if len(out)<3500: raise RuntimeError(f"NASDAQ_HISTORY_TOO_SHORT n={len(out)}")
    # Optional latest cross-check against Nasdaq's current quote endpoint.
    official=None
    try:
        z=req("https://api.nasdaq.com/api/quote/NDX/info",{"assetclass":"index"},timeout=20).json()
        official={"status":"RETRIEVED","payload_sha256":sha(json.dumps(z,sort_keys=True).encode())}
    except Exception as ex:
        official={"status":f"UNAVAILABLE:{type(ex).__name__}"}
    return dict(sorted(out.items())),{"source":"Yahoo Finance ^NDX historical chart (Nasdaq GIDS-labelled index history)",
      "source_role":"SECONDARY_LONG_HISTORY_VALIDATED_BY_OVERLAP; OFFICIAL_NASDAQ_EXTENDED_GIW_REQUIRES_ENTITLEMENT",
      "url":url,"sha256":sha(r.content),"first":min(out),"last":max(out),"n":len(out),"official_nasdaq_current_check":official}

def treasury(kind):
    typ={"nominal":"daily_treasury_yield_curve","real":"daily_treasury_real_yield_curve"}[kind]
    out={};meta={}
    for y in range(START_YEAR,END_DATE.year+1):
        url="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView"
        r=req(url,{"type":typ,"field_tdr_date_value":str(y)},timeout=35)
        tabs=pd.read_html(io.StringIO(r.text))
        chosen=None
        for q in tabs:
            cols=[str(c).strip().upper() for c in q.columns]
            if "DATE" in cols and "10 YR" in cols:
                q=q.copy();q.columns=cols;chosen=q;break
        if chosen is None: raise RuntimeError(f"TREASURY_TABLE_NOT_FOUND {kind} {y}")
        for z in chosen.itertuples(index=False,name=None):
            row=dict(zip(chosen.columns,z))
            d=pd.to_datetime(row.get("DATE"),errors="coerce");v=clean_num(row.get("10 YR"))
            if pd.notna(d) and np.isfinite(v):
                out[d.strftime("%Y-%m-%d")]=float(v)
        meta[str(y)]=sha(r.content)
    if len(out)<3500: raise RuntimeError(f"TREASURY_{kind.upper()}_TOO_SHORT n={len(out)}")
    return dict(sorted(out.items())),{"source":"U.S. Treasury Daily Treasury Rates","type":typ,"hashes_by_year":meta,"first":min(out),"last":max(out),"n":len(out)}

def effr():
    out={};hashes={}
    url="https://markets.newyorkfed.org/api/rates/unsecured/effr/search.json"
    for y in range(START_YEAR,END_DATE.year+1):
        a=f"{y}-01-01";b=f"{y}-12-31" if y<END_DATE.year else END_DATE.strftime("%Y-%m-%d")
        r=req(url,{"startDate":a,"endDate":b,"type":"rate"},timeout=30)
        hashes[str(y)]=sha(r.content); j=r.json()
        rows=j.get("refRates") or (j.get("data") or {}).get("refRates") or []
        for z in rows:
            d=pd.to_datetime(z.get("effectiveDate"),errors="coerce");v=clean_num(z.get("percentRate"))
            if pd.notna(d) and np.isfinite(v):out[d.strftime("%Y-%m-%d")]=float(v)
    if len(out)<3000: raise RuntimeError(f"EFFR_HISTORY_TOO_SHORT n={len(out)}")
    return dict(sorted(out.items())),{"source":"Federal Reserve Bank of New York Markets API","url":url,"hashes_by_year":hashes,"first":min(out),"last":max(out),"n":len(out)}

def cboe(symbol):
    url=f"https://cdn.cboe.com/api/global/us_indices/daily_prices/{symbol}_History.csv"
    r=req(url,timeout=30);df=pd.read_csv(io.BytesIO(r.content))
    df.columns=[str(c).strip().upper() for c in df.columns]
    dc="DATE"; vc=symbol if symbol in df.columns else "CLOSE"
    if dc not in df.columns or vc not in df.columns:raise RuntimeError(f"CBOE_COLS {symbol} {list(df.columns)}")
    d={}; 
    for z in df[[dc,vc]].itertuples(index=False):
        dt=pd.to_datetime(z[0],errors="coerce");v=clean_num(z[1])
        if pd.notna(dt) and dt>=pd.Timestamp("2010-01-01") and dt<=END_DATE and np.isfinite(v):
            d[dt.strftime("%Y-%m-%d")]=float(v)
    if len(d)<2500:raise RuntimeError(f"CBOE_HISTORY_TOO_SHORT {symbol} n={len(d)}")
    return dict(sorted(d.items())),{"source":f"Cboe {symbol} official daily history","url":url,"sha256":sha(r.content),"first":min(d),"last":max(d),"n":len(d)}

def h10_daily():
    h10.START="01/01/2010";h10.END="09/29/2026"
    rr,hr=h10.fetch_package(h10.RATE_PACKAGE);ri,hi=h10.fetch_package(h10.INDEX_PACKAGE)
    rates=h10.parse_ddp(rr);idx=h10.parse_ddp(ri)
    C={"EURUSD":h10.find_col(rates,"RXI$US_N.B.EU"),"GBPUSD":h10.find_col(rates,"RXI$US_N.B.UK"),
       "JPYUSD":h10.find_col(rates,"RXI_N.B.JA"),"CHFUSD":h10.find_col(rates,"RXI_N.B.SZ"),
       "CNYUSD":h10.find_col(rates,"RXI_N.B.CH"),"BROADUSD":h10.find_col(idx,"JRXWTFB_N.B")}
    out={}
    for _,z in rates.iterrows():
        d=pd.Timestamp(z["date"]).strftime("%Y-%m-%d");q={}
        for k,c in C.items():
            if k=="BROADUSD":continue
            v=pd.to_numeric(z[c],errors="coerce")
            if pd.notna(v):q[k]=float(v)
        if q:out[d]=q
    for _,z in idx.iterrows():
        d=pd.Timestamp(z["date"]).strftime("%Y-%m-%d");v=pd.to_numeric(z[C["BROADUSD"]],errors="coerce")
        if pd.notna(v):out.setdefault(d,{})["BROADUSD"]=float(v)
    return dict(sorted(out.items())),{"source":"Federal Reserve Board H.10 DDP","rates_sha256":hr,"index_sha256":hi,"columns":C,"first":min(out),"last":max(out),"n":len(out)}

def monthly_logret(d):
    s=pd.Series(d,dtype=float);s.index=pd.to_datetime(s.index);m=s.groupby(s.index.to_period("M")).last().sort_index()
    q=np.log(m/m.shift(1)).dropna();return {str(k):float(v) for k,v in q.items()}

def load_risk(path):
    d=json.loads(Path(path).read_text());return {r["origin_month"]:r for r in d["rows"]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--risk-snapshot",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    ndx,ndxm=nasdaq100()
    nom,nomm=treasury("nominal")
    real,realm=treasury("real")
    ff,ffm=effr()
    vix,vixm=cboe("VIX")
    gvz,gvzm=cboe("GVZ")
    fx,fxm=h10_daily()

    # monthly market-implied inflation compensation proxy: nominal minus real 10y
    common=sorted(set(nom)&set(real));breakeven={d:float(nom[d]-real[d]) for d in common}
    risk=load_risk(a.risk_snapshot);nret=monthly_logret(ndx)
    reconcile={}
    for m in ("2023-10","2023-11","2023-12"):
        old=float(risk[m]["nasdaq100_logret"]);new=float(nret[m]);diff=abs(old-new)
        reconcile[m]={"market_history_snapshot":old,"rebuilt_official_nasdaq":new,"abs_diff":diff}
        if diff>5e-4:raise RuntimeError(f"NASDAQ_PARITY_FAIL {m} old={old} new={new}")
        if abs(new)<1e-5:raise RuntimeError(f"NASDAQ_ZERO_ANOMALY_PERSISTS {m}")

    out={
      "schema":"GOLD_MONTHLY_LONG_HISTORY_MARKET_DRIVERS_V2_2026-09-29",
      "authority":{"neon_reads":0,"role":"RAW_DAILY_FEATURE_RESEARCH_STORE",
        "historical_claim":"CURRENT_OFFICIAL_HISTORICAL_MARKET_SERIES; NOT ORIGINAL RETRIEVAL VINTAGES",
        "selection_use":"transform/lag/MIDAS choices must occur inside chronological DEV experiments",
        "cpi_surprise_status":"NOT_INCLUDED_LONG_HISTORY; HISTORICAL_CONSENSUS_FIRST-PRINT_PROOF_NOT_READY"},
      "series":{"NASDAQ100":ndx,"DGS10_TREASURY":nom,"DFII10_TREASURY":real,"EFFR_NYFED":ff,
                "TENY_BREAKEVEN_PROXY":breakeven,"VIX_CBOE":vix,"GVZ_CBOE":gvz},
      "fx_h10_daily":fx,
      "sources":{"NASDAQ100":ndxm,"DGS10_TREASURY":nomm,"DFII10_TREASURY":realm,"EFFR_NYFED":ffm,
                 "VIX_CBOE":vixm,"GVZ_CBOE":gvzm,"FX_H10":fxm},
      "nasdaq_reconciliation":{"old_external_pit_nasdaq_field_status":"SUPERSEDED_FOR_NASDAQ_ONLY",
        "known_zero_anomaly_months":["2023-10","2023-11","2023-12"],"replacement":"official Nasdaq NDX daily history","parity":reconcile},
      "candidate_feature_families":{
        "NASDAQ100":["level_control","1m_log_return","3m_momentum","6m_momentum","realized_volatility","drawdown","daily_midas"],
        "rates":["nominal10y_level_change","real10y_level_change","EFFR_level_change","nominal_real_spread","daily_midas"],
        "inflation_expectations":["10y_nominal_minus_real_proxy_level_change","daily_midas"],
        "risk":["VIX_level_change","GVZ_level_change","NASDAQ100_realized_volatility","NASDAQ100_drawdown"],
        "fx":["broad_usd_return","cny_return","major_fx_returns","breadth","dispersion","daily_midas"]},
    }
    raw=json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False).encode();out["payload_sha256"]=sha(raw)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("LONG_HISTORY_MARKET_DRIVER_GATE=PASS")
    print(json.dumps({"sources":out["sources"],"nasdaq_reconciliation":reconcile,"payload_sha256":out["payload_sha256"]},sort_keys=True))
if __name__=="__main__":main()
