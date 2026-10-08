"""Read-only same-provider XAU/USD Dukascopy M1 bid/ask binary sample pilot.
No licensed prices nor credentials committed. Check overlap with pre-audited 2025
EVTradingLabs Dukascopy-derived BID M15, then 2026 same-provider feasibility.
No 2026 model/target is issued by this pilot.
"""
from __future__ import annotations
import os,sys,io,json,struct,lzma,time,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from datetime import date,timedelta,datetime,timezone
import numpy as np,pandas as pd
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as old
OUT=AX/"GOLD_EXECUTION_DUKASCOPY_2026_SAME_PROVIDER_PILOT_20261008.json"
DAYS_2025=[date(2025,12,9),date(2025,12,10),date(2025,12,11),date(2025,12,12),
           date(2025,12,15),date(2025,12,16),date(2025,12,17),date(2025,12,18)]
DAYS_2026=[date(2026,1,6),date(2026,4,8),date(2026,7,9),date(2026,10,7)]
URL="https://datafeed.dukascopy.com/datafeed/XAUUSD/{year}/{month0:02d}/{day:02d}/{side}_candles_min_1.bi5"

def getday(d,side):
    path=URL.format(year=d.year,month0=d.month-1,day=d.day,side=side)
    error=None
    for k in range(2):
        try:
            req=urllib.request.Request(path,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=9) as response:
                raw=response.read(2000000)
            if len(raw)==0:return pd.DataFrame(columns=["ts","open","close"]),"EMPTY"
            unpacked=lzma.decompress(raw)
            if len(unpacked)%24:raise RuntimeError("BINARY_NOT_24BYTE_ROWS")
            z=[]
            for offset,op,cl,lo,hi,volume in struct.iter_unpack(">IIIIIf",unpacked):
                if offset>86400 or offset%60 or min(op,cl,lo,hi)==0:
                    raise RuntimeError("MINUTE_BAR_ENCODING_INVALID")
                dt=pd.Timestamp(d,tz="UTC")+pd.Timedelta(seconds=int(offset))
                z.append((dt,op/1000.,cl/1000.))
            f=pd.DataFrame(z,columns=["ts","open","close"])
            if f.empty:return f,"EMPTY_DECOMPRESSED"
            if f.ts.duplicated().any():raise RuntimeError("DUPLICATE_MINUTE")
            if not f.open.between(200,15000).all():raise RuntimeError("GOLD_PRICE_SCALE_WRONG")
            return f,"OK"
        except urllib.error.HTTPError as e:
            if e.code==404:return pd.DataFrame(columns=["ts","open","close"]),"MISSING_404"
            error=f"HTTP_{e.code}"
        except Exception as e:
            error=type(e).__name__
        time.sleep(.5*(k+1))
    return pd.DataFrame(columns=["ts","open","close"]),"FAILED_"+str(error)

def m15(f):
    if f.empty:return pd.DataFrame(columns=["open","close","native_minutes"])
    g=f.sort_values("ts").copy().set_index("ts")
    bins=g.groupby(pd.Grouper(freq="15min",label="left",closed="left"))
    o=bins.open.first()
    c=bins.close.last()
    n=bins.open.count()
    q=pd.DataFrame({"open":o,"close":c,"native_minutes":n})
    return q[q.native_minutes>=14].copy()

def main():
    started=time.time()
    q,_=old.source_load()
    results=[];overlap=[]
    all_dates=DAYS_2025+DAYS_2026
    downloaded={}
    with ThreadPoolExecutor(max_workers=8) as pool:
        tasks={pool.submit(getday,d,side):(d,side) for d in all_dates for side in ("BID","ASK")}
        for job in as_completed(tasks):
            downloaded[tasks[job]]=job.result()
    for d in all_dates:
        bid,st_bid=downloaded[(d,"BID")]
        ask,st_ask=downloaded[(d,"ASK")]
        qb=m15(bid);qa=m15(ask)
        if len(qb) and len(qa):
            joined=qb[["close"]].join(qa[["close"]],lsuffix="_bid",rsuffix="_ask",how="inner")
            crossed=int((joined.close_ask<joined.close_bid).sum())
        else:crossed=None
        results.append({"date":str(d),"year":d.year,"bid_status":st_bid,"ask_status":st_ask,
                        "bid_m1":len(bid),"ask_m1":len(ask),
                        "bid_m15_14of15":len(qb),"ask_m15_14of15":len(qa),
                        "crossed_bidask_15m_count":crossed})
        if d.year==2025 and not qb.empty:
            source=q.loc[(q.index.date==d)]
            match=source[["open","close"]].join(qb[["open","close"]],how="inner",
                        lsuffix="_ref",rsuffix="_new")
            if len(match):
                for pricecol in ("open","close"):
                    absbps=10000*np.abs(match[pricecol+"_new"]-match[pricecol+"_ref"])/match[pricecol+"_ref"]
                    overlap.extend([float(x) for x in absbps.to_numpy()])
    resultsdf=pd.DataFrame(results)
    n=len(overlap)
    stats={"n_price_cells":n,
           "median_abs_diff_bps":float(np.median(overlap)) if n else None,
           "p95_abs_diff_bps":float(np.percentile(overlap,95)) if n else None,
           "max_abs_diff_bps":float(np.max(overlap)) if n else None}
    # Sanity gate; if vendor's raw candles disagree, 2026 is NOT a validated
    # extension of the historical trained-price labels.
    status=("PILOT_SAME_PROVIDER_ACCEPTABLE_FOR_FULL_SOURCE_QC"
      if n>=800 and stats["median_abs_diff_bps"]<=.3
      and stats["p95_abs_diff_bps"]<=3.0
      and (resultsdf[resultsdf.year==2026].bid_m15_14of15>=75).all()
      else "PILOT_NEEDS_SOURCE_RECONCILIATION_NO_2026_MODEL")
    out={"status":status,"asof":"2026-10-08","source_name":"Dukascopy public XAUUSD minute BID/ASK",
       "downloaded_price_levels_published":False,
       "pilot_years":[2025,2026],"source_past_frozen":old.SOURCE,
       "overlap_2025":stats,"days":results,
       "price_divisor":1000,"raw_lzma_record_bytes":24,
       "current_2026_year_partial":True,"same_source_target_model_retest_executed":False,
       "elapsed_sec":int(time.time()-started)}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print("PILOT_RESULT",json.dumps(out),flush=True)
if __name__=="__main__":main()
