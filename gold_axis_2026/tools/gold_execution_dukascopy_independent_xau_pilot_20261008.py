"""Dukascopy Bank XAUUSD independent BID/ASK M1 2023/2026 feasibility pilot.
Separate price source, private Neon only. Never silently fill HistData BID
with another provider or declare bank execution without matching instrument.
This pilot does not access paid APIs.
"""
from __future__ import annotations
import datetime as dt
import hashlib, json, lzma, os, struct, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
import psycopg
import requests

AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_DUKASCOPY_XAU_BIDASK_PILOT_2026-10-08.json"
SOURCE="DUKASCOPY_XAUUSD_M1_BIDASK_UTC_PILOT_V1"
TABLE="gold_research_dukascopy_xau15m_bidask_candidate"
HIST="HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1"
DATES=["2023-04-03","2023-04-11","2023-04-18","2023-04-25",
       "2026-10-01","2026-10-05","2026-10-06","2026-10-07"]
HOSTS=("https://datafeed.dukascopy.com/datafeed",
       "https://www.dukascopy.com/datafeed")
RECORD=struct.Struct(">IIIIIf")

def pull(date,side):
    d=dt.date.fromisoformat(date)
    path=f"/XAUUSD/{d.year:04d}/{d.month-1:02d}/{d.day:02d}/{side}_candles_min_1.bi5"
    errs=[]
    for root in HOSTS:
        try:
            r=requests.get(root+path,timeout=(15,40),headers={"User-Agent":"XAUUSD-Source-Integrity-Research/1.0","Accept":"*/*"})
            if r.status_code==404:
                errs.append("NOT_FOUND")
                continue
            if r.status_code!=200: 
                errs.append(f"HTTP_{r.status_code}")
                continue
            if not r.content: return pd.DataFrame(), {"result":"EMPTY_SOURCE_DAY"}
            decoded=None
            for fmt in (lzma.FORMAT_ALONE,lzma.FORMAT_AUTO):
                try:decoded=lzma.decompress(r.content,format=fmt);break
                except lzma.LZMAError:continue
            if decoded is None:raise ValueError("BI5_NOT_LZMA")
            if len(decoded)%RECORD.size:raise ValueError("BI5_RECORD_LENGTH_INVALID")
            raw=np.frombuffer(decoded,dtype=np.dtype([
                 ("second",">u4"),("open",">u4"),("close",">u4"),
                 ("low",">u4"),("high",">u4"),("volume",">f4")]))
            if len(raw)==0:return pd.DataFrame(),{"result":"EMPTY_SOURCE_DAY"}
            if raw["second"].max()>=86400:raise ValueError("INVALID_SECONDS_FROM_DAY")
            values=pd.DataFrame({
                "bar_start_utc":pd.Timestamp(date,tz="UTC")+pd.to_timedelta(raw["second"].astype("int64"),unit="s"),
                "open":raw["open"].astype("float64")/1000,
                "high":raw["high"].astype("float64")/1000,
                "low":raw["low"].astype("float64")/1000,
                "close":raw["close"].astype("float64")/1000,
            })
            if values.bar_start_utc.duplicated().any():raise ValueError("DUPLICATE_M1_START")
            if (values[["open","high","low","close"]]<=0).any().any():raise ValueError("NONPOSITIVE_PRICE")
            if (values.high+1e-9<values[["open","low","close"]].max(axis=1)).any():
                raise ValueError("INVALID_HIGH")
            if (values.low-1e-9>values[["open","high","close"]].min(axis=1)).any():
                raise ValueError("INVALID_LOW")
            if not (values.close.between(200,15000).all()):raise ValueError("XAU_PRICE_SCALE_SUSPECT")
            if ((values.bar_start_utc.dt.second%60)!=0).any():raise ValueError("M1_NOT_MINUTE_ALIGNED")
            return values.sort_values("bar_start_utc"),{
                "result":"SOURCE_DAY_RECEIVED","origin_host":root.replace("https://",""),
                "m1_rows":len(values),"payload_byte_size":len(r.content),
                "sha256_bi5":hashlib.sha256(r.content).hexdigest()}
        except Exception as e:
            errs.append(type(e).__name__+":"+str(e)[:35])
    return None,{"result":"SOURCE_UNAVAILABLE_OR_INVALID","causes":errs[:3]}

def derive(bid,ask):
    if bid.empty or ask.empty:return pd.DataFrame(),{"status":"EMPTY_SOURCE"}
    b=bid.rename(columns={x:"bid_"+x for x in ("open","high","low","close")})
    a=ask.rename(columns={x:"ask_"+x for x in ("open","high","low","close")})
    m=b.merge(a,on="bar_start_utc",how="inner",validate="one_to_one")
    bad=int((m.ask_close<m.bid_close).sum())
    if bad>3:raise ValueError("CROSSED_QUOTES_COUNT_"+str(bad))
    m=m[(m.ask_close>=m.bid_close)].copy()
    m=m.set_index("bar_start_utc")
    cols=[x for x in m.columns if x!="bar_start_utc"]
    rules={x:("first" if x.endswith("open") else "last" if x.endswith("close") else "max" if x.endswith("high") else "min") for x in cols}
    g=m.resample("15min",label="left",closed="left").agg(rules)
    g["m1_matched"]=m.bid_close.resample("15min",label="left",closed="left").count()
    g=g[g.m1_matched>0].reset_index()
    assert len(g)>0
    return g,{"status":"MATCHED_BID_ASK",
                "same_minute_rows":len(m),"crossed_quote_minutes_removed":bad,
                "m15_bars":len(g),"complete_15m_bars":int((g.m1_matched==15).sum()),
                "partial_m15_bars":int((g.m1_matched<15).sum()),
                "m15_sha256":hashlib.sha256(g.to_csv(index=False).encode()).hexdigest(),
                "median_spread_bps":float(np.median((m.ask_close-m.bid_close)/m.bid_close*10000))}

def compare(g,date):
    if not date.startswith("2023"):return None
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("""SELECT bar_start_utc,close_price
                FROM gold_research_histdata_xau15m_candidate
                WHERE source_id=%s AND bar_start_utc>=%s AND bar_start_utc < (%s::date+interval '1 day')
                ORDER BY bar_start_utc""",(HIST,date,date))
            old=pd.DataFrame(c.fetchall(),columns=["bar_start_utc","hist_bid_close"])
    if not old.empty:old.bar_start_utc=pd.to_datetime(old.bar_start_utc,utc=True)
    shared=g.merge(old,on="bar_start_utc",how="left")
    existing=shared.dropna(subset=["hist_bid_close"])
    discrepancy=np.abs(existing.bid_close/existing.hist_bid_close-1)*10000
    return {"histdata_m15_bars":len(old),
            "independent_bid_m15_bars":len(g),
            "new_intervals_not_in_histdata":int(shared.hist_bid_close.isna().sum()),
            "matched_close_bars":len(existing),
            "median_cross_vendor_bid_diff_bps":float(discrepancy.median()) if len(existing) else None,
            "p95_cross_vendor_bid_diff_bps":float(discrepancy.quantile(.95)) if len(existing) else None}

def save_private(g):
    if g.empty:return 0
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
               source_id TEXT NOT NULL,bar_start_utc TIMESTAMPTZ NOT NULL,
               bid_open FLOAT8 NOT NULL,bid_high FLOAT8 NOT NULL,
               bid_low FLOAT8 NOT NULL,bid_close FLOAT8 NOT NULL,
               ask_open FLOAT8 NOT NULL,ask_high FLOAT8 NOT NULL,
               ask_low FLOAT8 NOT NULL,ask_close FLOAT8 NOT NULL,
               m1_matched SMALLINT NOT NULL,
               source_vintage TEXT NOT NULL,
               PRIMARY KEY(source_id,bar_start_utc))""")
            c.execute(f"""CREATE TEMP TABLE stage (
               source_id TEXT,bar_start_utc TIMESTAMPTZ,
               bid_open FLOAT8,bid_high FLOAT8,bid_low FLOAT8,bid_close FLOAT8,
               ask_open FLOAT8,ask_high FLOAT8,ask_low FLOAT8,ask_close FLOAT8,
               m1_matched SMALLINT,source_vintage TEXT
            ) ON COMMIT DROP""")
            cols=["source_id","bar_start_utc","bid_open","bid_high","bid_low","bid_close",
                  "ask_open","ask_high","ask_low","ask_close","m1_matched","source_vintage"]
            with c.copy("COPY stage ("+",".join(cols)+") FROM STDIN") as cp:
                for row in g.itertuples(index=False):
                    cp.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
                        *[float(getattr(row,x)) for x in cols[2:10]],int(row.m1_matched),
                        "HISTORICAL_RETRIEVED_2026_10_08_NOT_PIT"))
            c.execute(f"""INSERT INTO {TABLE} ({','.join(cols)})
                 SELECT {','.join(cols)} FROM stage
                 ON CONFLICT (source_id,bar_start_utc) DO NOTHING""")
            n=c.rowcount
        con.commit()
    return int(n)

def main():
    report={"status":"NOT_STARTED","asof":"2026-10-08",
       "purpose":"Independent BID/ASK XAU/USD quote source feasibility; 2023 HistData gaps and October 2026",
       "source":"Dukascopy Bank M1 candle BID/ASK UTC direct archive, 0-based calendar month",
       "historical_price_scale":"XAUUSD native integer points /1000",
       "raw_vendor_quotes_not_public":True,"paid_api_charge_usd":0,
       "source_candidate_only":True,"same_source_stitching_into_histdata":False,
       "days":[]}
    chunks=[]
    for date in DATES:
        day={"date":date}
        with ThreadPoolExecutor(max_workers=2) as pool:
            f={side:pool.submit(pull,date,side) for side in ("BID","ASK")}
            bid,binfo=f["BID"].result()
            ask,ainfo=f["ASK"].result()
        day["bid"]=binfo;day["ask"]=ainfo
        try:
            if bid is None or ask is None:raise RuntimeError("MISSING_OR_INVALID_SOURCE_CANDLE")
            g,m=derive(bid,ask)
            day["aggregate"]=m
            if len(g)>0:
                if ((g.bar_start_utc.dt.dayofweek==5)|
                  ((g.bar_start_utc.dt.dayofweek==6)&(g.bar_start_utc.dt.hour<21))).any():
                    raise RuntimeError("OFFMARKET_BARS_REJECTED")
                day["reference_compare"]=compare(g,date)
                chunks.append(g)
            day["result"]="DATA_QC_COMPLETE"
        except Exception as ex:
            day["result"]="BLOCKED";day["error_type"]=type(ex).__name__
            day["reason"]=str(ex)[:75]
        report["days"].append(day)
        print("PILOT",json.dumps(day,default=str)[:1250],flush=True)
    if chunks:
        combined=pd.concat(chunks,ignore_index=True)
        if combined.bar_start_utc.duplicated().any():raise RuntimeError("PILOT_DUPLICATE_M15_UTC")
        report["private_new_m15_rows"]=save_private(combined)
        report["successful_days"]=len(chunks)
        report["status"]="INDEPENDENT_PILOT_SAVED_PRIVATE"
    else:report["status"]="NO_SOURCE_DATA_RETRIEVED"
    report["generated_at_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.write_text(json.dumps(report,indent=2,default=str)+"\n")
    print("FINAL_STATUS",report["status"],report.get("successful_days"),flush=True)
    return 0 if chunks else 1

if __name__=="__main__":raise SystemExit(main())
