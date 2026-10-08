"""Direct Dukascopy XAUUSD hourly BID/ASK monthly source pilot, frozen Oct 8 2026.

H1 exists in one vendor file per month and may bypass per-day M1 HTTP 503.
This is a diagnostic: monthly H1 source cannot supply M15 shape features;
must not relabel true 15m models as same-source without separately valid M15.
No raw licensed prices committed. 2025 overlap independently crosschecked.
"""
from __future__ import annotations
import datetime as dt,hashlib,io,json,lzma,os,struct,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import pandas as pd,numpy as np,psycopg,requests
AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_2026_DUKASCOPY_DIRECT_H1_MONTHLY_SOURCE_PILOT_20261008.json"
TABLE="gold_research_dukascopy_xau_h1_monthly_source_candidate_v1"
SOURCE="DIRECT_DUKASCOPY_XAUUSD_H1_BIDASK_2025_2026"
END=dt.datetime(2026,10,8,14,0,tzinfo=dt.timezone.utc)
URLS=("https://datafeed.dukascopy.com/datafeed","https://www.dukascopy.com/datafeed")
RECORD=struct.Struct(">IIIIIf")
def pull(year,month,side):
    uri=f"/XAUUSD/{year:04d}/{month-1:02d}/{side}_candles_hour_1.bi5"
    errors=[]
    for host in URLS:
      try:
        res=requests.get(host+uri,timeout=(8,26),headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
        if res.status_code!=200:
            errors.append(f"HTTP_{res.status_code}")
            continue
        for fmt in (lzma.FORMAT_ALONE,lzma.FORMAT_AUTO):
          try: raw=lzma.decompress(res.content,format=fmt);break
          except lzma.LZMAError:raw=None
        if raw is None or len(raw)%RECORD.size:raise RuntimeError("H1_INVALID_BI5_FORMAT")
        records=list(RECORD.iter_unpack(raw))
        if not records:raise RuntimeError("H1_EMPTY_MONTH")
        first=dt.datetime(year,month,1,tzinfo=dt.timezone.utc)
        data=pd.DataFrame(records,columns=["seconds","open","close","low","high","volume"])
        # Dukascopy's monthly H1 offset field convention must be validated
        # against the actual source monthly time grid, never guessed.
        if data.seconds.max()>32*86400 or (data.seconds%3600).any():
            raise RuntimeError("H1_MONTH_OFFSET_NOT_SECONDS_FROM_MONTH_OPEN")
        data["utc"]=pd.to_datetime(first)+pd.to_timedelta(data.seconds,unit="s")
        data=data.sort_values("utc")
        if data.utc.duplicated().any():raise RuntimeError("H1_DUPLICATE")
        if not (data.utc.dt.year.eq(year)&data.utc.dt.month.eq(month)).all():
            raise RuntimeError("H1_TIMESTAMP_OUTSIDE_MONTH")
        if (data[["open","close","low","high"]]<=0).any().any():
            raise RuntimeError("H1_NONPOSITIVE_PRICE")
        if (data.high<data[["open","close","low"]].max(axis=1)).any() or (
            data.low>data[["open","close","high"]].min(axis=1)).any():
            raise RuntimeError("H1_OHLC_GEOMETRY")
        for k in ("open","close","low","high"):data[k]/=1000.
        if not data.close.between(200,15000).all():raise RuntimeError("H1_XAU_PRICE_SCALE")
        return data,{"status":"OK","rows":len(data),
           "raw_gzip_sha256":hashlib.sha256(res.content).hexdigest()}
      except Exception as e:errors.append(type(e).__name__+":"+str(e)[:80])
    return None,{"status":"SOURCE_UNAVAILABLE_OR_QUARANTINED","errors":errors}
def init(conn):
    with conn.cursor() as c:
      c.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
        source_id TEXT NOT NULL, utc TIMESTAMPTZ NOT NULL,
        bid_open DOUBLE PRECISION NOT NULL,bid_close DOUBLE PRECISION NOT NULL,
        ask_open DOUBLE PRECISION NOT NULL,ask_close DOUBLE PRECISION NOT NULL,
        source_vintage TEXT NOT NULL,
        PRIMARY KEY (source_id,utc))""")
    conn.commit()
def main():
    tic=time.time()
    months=[(2025,x) for x in (3,6,9,12)]+[(2026,x) for x in range(1,11)]
    tasks={}
    with ThreadPoolExecutor(max_workers=2) as pool:
      for y,m in months:
        for side in ("BID","ASK"):
          tasks[pool.submit(pull,y,m,side)]=(y,m,side)
      results={}
      for job in as_completed(tasks):
        k=tasks[job];results[k]=job.result()
        print("H1_SOURCE",k,results[k][1],flush=True)
    source=[];accepted=[];frames=[]
    for y,m in months:
      b,bs=results[(y,m,"BID")];a,ass=results[(y,m,"ASK")]
      report={"month":f"{y}-{m:02d}","bid":bs,"ask":ass}
      if b is not None and a is not None:
        join=b[["utc","open","close"]].merge(a[["utc","open","close"]],
               on="utc",suffixes=("_bid","_ask"),validate="one_to_one")
        if (join.close_ask<join.close_bid).any():raise RuntimeError("H1_BID_ASK_CROSSED")
        if y==2026:join=join[join.utc.dt.to_pydatetime()<END]
        report["joined_bars"]=len(join)
        if len(join):
          join["source_id"]=SOURCE;join["source_vintage"]="RETRIEVED_2026_10_08_NOT_PIT"
          frames.append(join)
          report["status"]="BOTH_SIDES_ACCEPTED"
        else:report["status"]="NO_MATURE_BARS"
      else:report["status"]="INCOMPLETE_OR_UNAVAILABLE_MONTH"
      source.append(report)
    total=0
    if frames:
      z=pd.concat(frames,ignore_index=True)
      if z.utc.duplicated().any():raise RuntimeError("2025_26_DUPLICATE_MONTH_H1")
      with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as conn:
        init(conn)
        with conn.cursor() as c:
          c.execute(f"""CREATE TEMP TABLE stage (
            source_id TEXT,utc TIMESTAMPTZ,bid_open DOUBLE PRECISION,
            bid_close DOUBLE PRECISION,ask_open DOUBLE PRECISION,
            ask_close DOUBLE PRECISION,source_vintage TEXT) ON COMMIT DROP""")
          with c.copy("COPY stage (source_id,utc,bid_open,bid_close,ask_open,ask_close,source_vintage) FROM STDIN") as cp:
            for r in z.itertuples(index=False):
              cp.write_row((r.source_id,r.utc.to_pydatetime(),float(r.open_bid),
                 float(r.close_bid),float(r.open_ask),float(r.close_ask),r.source_vintage))
          c.execute(f"""INSERT INTO {TABLE}
             (source_id,utc,bid_open,bid_close,ask_open,ask_close,source_vintage)
             SELECT source_id,utc,bid_open,bid_close,ask_open,ask_close,source_vintage
             FROM stage ON CONFLICT(source_id,utc) DO NOTHING""")
          total=c.rowcount
        conn.commit()
    out={"asof":"2026-10-08","status":"DIRECT_DUKASCOPY_H1_SOURCE_PILOT_COMPLETE",
        "source":"Dukascopy direct XAUUSD hour_1 M1-independent monthly BID ASK",
        "source_h1_table_private":TABLE,"months":source,
        "successful_months":sum(x["status"]=="BOTH_SIDES_ACCEPTED" for x in source),
        "rows_inserted_private":total,
        "h1_not_m15":True,
        "no_M15_shape_models_scored_in_this_step":True,
        "raw_quotes_not_in_git":True,
        "elapsed_sec":int(time.time()-tic)}
    OUT.write_text(json.dumps(out,indent=2,default=str)+"\n")
    print("H1_PILOT_FINAL",json.dumps(out,default=str),flush=True)
if __name__=="__main__":main()
