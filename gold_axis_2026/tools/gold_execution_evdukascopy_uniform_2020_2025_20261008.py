"""Independent EV Trading Labs Dukascopy-derived XAUUSD M15 BID/ASK 2020-2025.
All price rows stored privately in Neon, annual public receipts only.
URLs are directly exposed on the provider's /data catalog.
No account required for closed years M15. Attribution: EV Trading Labs.
Source is a NEW homogeneous candidate, NOT a patch into HistData's BID.
"""
from __future__ import annotations
import gzip,hashlib,json,os,time
from pathlib import Path
from datetime import datetime,timezone
import requests
import pandas as pd
import numpy as np
import psycopg

AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_EV_DUKASCOPY_XAU_2020_2025_UNIFORM_CANDIDATE_20261008.json"
URL="https://evtradelabs.com/api/simulator/data/XAUUSD/M15/{year}.json.gz"
SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1"
TABLE="gold_research_evduka_xau15m_bidask_candidate"
H2020="HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_V1"
H2023="HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1"
H2025="HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026"
D_SOURCE="DUKASCOPY_XAUUSD_M1_BIDASK_UTC_PILOT_V1"

def get(y):
    url=URL.format(year=y)
    r=requests.get(url,timeout=(12,45),headers={"Accept":"application/gzip, application/octet-stream","User-Agent":"XAU-Source-QC/2026-10-08"})
    if r.status_code!=200:raise RuntimeError("ANNUAL_VENDOR_DOWNLOAD_HTTP_"+str(r.status_code)+"_"+str(y))
    if len(r.content)<25000 or len(r.content)>30_000_000:raise RuntimeError("ANNUAL_DATA_SIZE_IMPLAUSIBLE")
    try:raw=gzip.decompress(r.content)
    except OSError as e:raise RuntimeError("VENDOR_NOT_GZIP_"+str(y)) from e
    d=json.loads(raw)
    if isinstance(d,dict):
        for k in ("data","bars","candles","items","rows"):
            if isinstance(d.get(k),list):d=d[k];break
    if not isinstance(d,list):raise RuntimeError("VENDOR_SCHEMA_NOT_LIST")
    x=pd.DataFrame(d)
    required={"ts","o","h","l","c","ao","ah","al","ac"}
    if not required.issubset(set(x.columns)):
        raise RuntimeError("VENDOR_MISSING_BIDASK_COLS_"+str(sorted(x.columns)[:18]))
    if len(x)<17000:raise RuntimeError("VENDOR_YEAR_THIN_"+str(y)+"_"+str(len(x)))
    ts=pd.to_numeric(x.ts,errors="coerce")
    if ts.isna().any():raise RuntimeError("BAD_TIMESTAMP")
    if not ts.between(1_500_000_000,2_100_000_000).all():raise RuntimeError("UNIX_SECONDS_UTC_EXPECTED")
    x["bar_start_utc"]=pd.to_datetime(ts.astype("int64"),unit="s",utc=True)
    x=x.rename(columns={"o":"bid_open","h":"bid_high","l":"bid_low","c":"bid_close",
                "ao":"ask_open","ah":"ask_high","al":"ask_low","ac":"ask_close"})
    price=["bid_open","bid_high","bid_low","bid_close","ask_open","ask_high","ask_low","ask_close"]
    for c in price:x[c]=pd.to_numeric(x[c],errors="coerce")
    if x[price].isna().any().any():raise RuntimeError("NULL_BIDASK")
    if (x[price]<=0).any().any():raise RuntimeError("NONPOSITIVE_BIDASK")
    if (x.bid_close>=10000).any() or (x.bid_close<=200).any():raise RuntimeError("INVALID_XAU_LEVEL")
    if x.bar_start_utc.duplicated().any():raise RuntimeError("DUPLICATE_INTERVAL")
    if not ((x.bar_start_utc.dt.year==y)&(x.bar_start_utc.dt.minute%15==0)&(x.bar_start_utc.dt.second==0)).all():
        raise RuntimeError("YEAR_OR_15M_NOT_ALIGNED")
    if (x.bid_high+1e-6<x[["bid_open","bid_close","bid_low"]].max(axis=1)).any():
        raise RuntimeError("BID_OHLC_FAIL")
    if (x.bid_low-1e-6>x[["bid_open","bid_close","bid_high"]].min(axis=1)).any():
        raise RuntimeError("BID_LOW_FAIL")
    if (x.ask_high+1e-6<x[["ask_open","ask_close","ask_low"]].max(axis=1)).any():
        raise RuntimeError("ASK_OHLC_FAIL")
    if (x.ask_low-1e-6>x[["ask_open","ask_close","ask_high"]].min(axis=1)).any():
        raise RuntimeError("ASK_LOW_FAIL")
    crossed=((x.ask_open<x.bid_open)|(x.ask_close<x.bid_close))
    if crossed.any():raise RuntimeError("CROSSED_SOURCE_M15_QUOTES_"+str(int(crossed.sum())))
    closed=((x.bar_start_utc.dt.dayofweek==5)|
           ((x.bar_start_utc.dt.dayofweek==6)&(x.bar_start_utc.dt.hour<21)))
    if closed.any():raise RuntimeError("OFFMARKET_15M_"+str(int(closed.sum())))
    x=x.sort_values("bar_start_utc")
    x=x[["bar_start_utc"]+price].copy()
    receipt={"year":y,"source_url_path":f"/api/simulator/data/XAUUSD/M15/{y}.json.gz",
        "source_sha256_gzip":hashlib.sha256(r.content).hexdigest(),
        "source_derived_15m_rows":len(x),
        "first_utc":x.bar_start_utc.min().isoformat(),"last_utc":x.bar_start_utc.max().isoformat(),
        "matched_bid_ask_cross_count":int(crossed.sum()),
        "hard_closed_market_bars":int(closed.sum()),
        "unique_utc_days":int(x.bar_start_utc.dt.date.nunique()),
        "monthly_counts":{str(int(k)):int(v) for k,v in x.groupby(x.bar_start_utc.dt.month).size().items()},
        "median_vendor_spread_bps":float(np.median((x.ask_close/x.bid_close-1)*10000)),
        "p95_vendor_spread_bps":float(np.quantile((x.ask_close/x.bid_close-1)*10000,.95))}
    return x,receipt

def compare_private(con,x,year):
    hist_source=H2020 if year<=2021 else H2023 if year<=2024 else H2025
    with con.cursor() as c:
        c.execute("""SELECT bar_start_utc,close_price
          FROM gold_research_histdata_xau15m_candidate
          WHERE source_id=%s AND bar_start_utc >=%s AND bar_start_utc<%s
          ORDER BY bar_start_utc""",(hist_source,f"{year}-01-01",f"{year+1}-01-01"))
        z=pd.DataFrame(c.fetchall(),columns=["bar_start_utc","hbid_close"])
    if len(z):z.bar_start_utc=pd.to_datetime(z.bar_start_utc,utc=True)
    m=x.merge(z,on="bar_start_utc",how="left")
    common=m.dropna(subset=["hbid_close"])
    d=np.abs(common.bid_close/common.hbid_close-1)*10000
    return {"histdata_same_year_15m_rows":int(len(z)),
        "other_bid_source_overlaps":int(len(common)),
        "separate_source_bars_absent_from_histdata":int(m.hbid_close.isna().sum()),
        "source_bid_median_abs_price_bps":float(d.median()) if len(d) else None,
        "source_bid_p95_abs_price_bps":float(d.quantile(.95)) if len(d) else None}

def pilot_corroboration(con,x,year):
    if year!=2023:return None
    with con.cursor() as c:
        c.execute("""SELECT bar_start_utc,bid_close,ask_close
           FROM gold_research_dukascopy_xau15m_bidask_candidate
           WHERE source_id=%s ORDER BY bar_start_utc""",(D_SOURCE,))
        q=pd.DataFrame(c.fetchall(),columns=["bar_start_utc","primary_bid","primary_ask"])
    if q.empty:return {"status":"PILOT_NOT_FOUND"}
    q.bar_start_utc=pd.to_datetime(q.bar_start_utc,utc=True)
    m=x.merge(q,on="bar_start_utc",how="inner")
    if len(m)<150:raise RuntimeError("FIRST_PARTY_PILOT_OVERLAP_TOO_SMALL")
    bid=np.abs(m.bid_close/m.primary_bid-1)*10000
    ask=np.abs(m.ask_close/m.primary_ask-1)*10000
    return {"matched_first_party_m15_bars":len(m),
       "bid_median_abs_bps":float(bid.median()),
       "bid_p95_abs_bps":float(bid.quantile(.95)),
       "ask_median_abs_bps":float(ask.median()),
       "ask_p95_abs_bps":float(ask.quantile(.95)),
       "bid_direction_sign_consistency":float((np.sign(m.bid_close-m.bid_open)==np.sign(m.primary_bid-m.bid_open)).mean())}

def private_save(con,x):
    with con.cursor() as c:
        c.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
          source_id TEXT NOT NULL,bar_start_utc TIMESTAMPTZ NOT NULL,
          bid_open FLOAT8 NOT NULL,bid_high FLOAT8 NOT NULL,
          bid_low FLOAT8 NOT NULL,bid_close FLOAT8 NOT NULL,
          ask_open FLOAT8 NOT NULL,ask_high FLOAT8 NOT NULL,
          ask_low FLOAT8 NOT NULL,ask_close FLOAT8 NOT NULL,
          source_type TEXT NOT NULL,
          PRIMARY KEY(source_id,bar_start_utc))""")
        c.execute("""CREATE TEMP TABLE IF NOT EXISTS qa_source_stage(
          source_id text,bar_start_utc timestamptz,
          bid_open float8,bid_high float8,bid_low float8,bid_close float8,
          ask_open float8,ask_high float8,ask_low float8,ask_close float8,
          source_type text) ON COMMIT DROP""")
        cols=["source_id","bar_start_utc"]+list(x.columns[1:])+["source_type"]
        with c.copy("COPY qa_source_stage ("+",".join(cols)+") FROM STDIN") as cp:
            for row in x.itertuples(index=False):
                cp.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
                   *[float(getattr(row,k)) for k in x.columns[1:]],
                    "EV Trading Labs derived from Dukascopy tick source BID ASK M15 historical non-PIT"))
        c.execute(f"""INSERT INTO {TABLE}({','.join(cols)})
           SELECT {','.join(cols)} FROM qa_source_stage
           ON CONFLICT (source_id,bar_start_utc) DO NOTHING""")
        inserted=c.rowcount
        c.execute("TRUNCATE qa_source_stage")
    con.commit()
    return int(inserted)

def main():
    report={"status":"NOT_ACQUIRED","asof":"2026-10-08",
       "source":SOURCE,"year_span":"2020-2025 (closed years only)",
       "canonical_promotion":False,"source_acknowledgement":"EV Trading Labs, Dukascopy-derived",
       "official_corroboration":"compare same exact 2023 timestamp with Dukascopy primary datafeed private pilot",
       "source_is_bidask":True,"not_bank_executable":True,
       "paid_download_usd":0,"private_prices_only":True,
       "no_2026_current_year_free_account_attempt":True,"years":{}}
    try:
        with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=25) as con:
            for year in range(2020,2026):
                x,r=get(year)
                r["histdata_comparison"]=compare_private(con,x,year)
                if year==2023:
                    r["independent_primary_pilot"]=pilot_corroboration(con,x,year)
                    test=r["independent_primary_pilot"]
                    if test["bid_p95_abs_bps"]>10 or test["ask_p95_abs_bps"]>10:
                        raise RuntimeError("MIRROR_VS_DUKASCOPY_PRIMARY_QUOTE_MISMATCH_NOT_APPROVED")
                r["new_rows_saved_private"]=private_save(con,x)
                report["years"][str(year)]=r
                print("FULL_YEAR_INDEPENDENT",year,len(x),
                    "missing_histdata",r["histdata_comparison"]["separate_source_bars_absent_from_histdata"],flush=True)
            report["status"]="SINGLE_ALTERNATIVE_SOURCE_2020_2025_SAVED_PRIVATE_AS_RESEARCH_CANDIDATE"
    except Exception as e:
        report["status"]="SOURCE_RETRIEVAL_OR_QC_BLOCKED"
        report["error_type"]=type(e).__name__
        report["error_summary"]=str(e)[:190]
    report["completed_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",report["status"],report.get("error_summary",""),flush=True)
    return 0 if report["status"].startswith("SINGLE_") else 1

if __name__=="__main__":
    code=main()
    if code==0:
        # Forensic is an independent read-only audit of persisted prices and target labels.
        from gold_execution_2020_2025_price_label_forensic_20261008 import main as forensic
        code=forensic()
    raise SystemExit(code)

# Research receipt policy: no vendor raw quotes committed to the public repository.
