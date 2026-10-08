"""2026 primary Dukascopy XAU/USD M1 BID/ASK to private M15 candidate, one month.

Downloaded native BID+ASK bars are kept ONLY in private Neon and private workflow
artifacts. Immutable 2025 quote-source overlap receipt is established separately.
No 2026 label/model selection, no silent price interpolation or vendor switch.
"""
from __future__ import annotations
import argparse,datetime as dt,json,lzma,hashlib,os,struct,time,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np,pandas as pd,psycopg,requests
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_dukascopy_independent_xau_pilot_20261008 as d
TABLE="gold_research_dukascopy_2026_direct_m1_m15_bidask_v2"
SOURCE="DUKASCOPY_DIRECT_M1_BIDASK_2026_M15_NATIVE_FULL_V2"
CONTRACT="2026-10-08"
FIELDS=["source_id","bar_start_utc","bid_open","bid_high","bid_low","bid_close",
        "ask_open","ask_high","ask_low","ask_close","m1_matched","source_vintage"]
def get_db():
    return psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=15)
def init():
    with get_db() as conn:
      with conn.cursor() as cur:
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE} (
          source_id TEXT NOT NULL,bar_start_utc TIMESTAMPTZ NOT NULL,
          bid_open FLOAT8 NOT NULL,bid_high FLOAT8 NOT NULL,bid_low FLOAT8 NOT NULL,bid_close FLOAT8 NOT NULL,
          ask_open FLOAT8 NOT NULL,ask_high FLOAT8 NOT NULL,ask_low FLOAT8 NOT NULL,ask_close FLOAT8 NOT NULL,
          m1_matched SMALLINT NOT NULL,source_vintage TEXT NOT NULL,
          PRIMARY KEY(source_id,bar_start_utc))""")
      conn.commit()
def existing(days):
    with get_db() as conn:
      with conn.cursor() as cur:
        cur.execute(f"""SELECT (bar_start_utc AT TIME ZONE 'UTC')::date,COUNT(*)
           FROM {TABLE} WHERE source_id=%s AND bar_start_utc>= %s AND bar_start_utc<%s
           GROUP BY 1""",(SOURCE,days[0].isoformat(),(days[-1]+dt.timedelta(days=1)).isoformat()))
        return {str(x[0]):int(x[1]) for x in cur.fetchall()}
def get_one(date):
    out={}
    for side in ("BID","ASK"):
        df,info=d.pull(date.isoformat(),side)
        out[side]=(df,info)
    b,bs=out["BID"];a,ass=out["ASK"]
    if b is None or a is None:
        return date,None,{"status":"SOURCE_UNAVAILABLE","bid":bs.get("result"),"ask":ass.get("result"),
                           "bid_reason":bs.get("causes",[])[:1],"ask_reason":ass.get("causes",[])[:1]}
    if len(b)==0 or len(a)==0:
        return date,None,{"status":"EMPTY_OR_HOLIDAY","bid_rows":len(b),"ask_rows":len(a)}
    try:
        bars,report=d.derive(b,a)
        if bars.empty:return date,None,{"status":"EMPTY_AFTER_JOIN"}
        if bars.bar_start_utc.duplicated().any():raise RuntimeError("DUPLICATE_PRIMARY_TS")
        if ((bars.bar_start_utc.dt.dayofweek==5) |
              ((bars.bar_start_utc.dt.dayofweek==6)&(bars.bar_start_utc.dt.hour<21))).any():
            raise RuntimeError("DEFINITELY_CLOSED_MARKET_BARS")
        if (bars[["bid_open","bid_close","ask_open","ask_close"]]<=0).any().any():
            raise RuntimeError("NONPOSITIVE_QUOTES")
        if (bars.ask_close+1e-9<bars.bid_close).any():raise RuntimeError("CROSSED_QUOTES")
        full=bars[bars.m1_matched==15].copy()
        if not len(full):return date,None,{"status":"NO_COMPLETE_M15","candidate_m15":len(bars)}
        return date,full,{"status":"ACCEPTED_PRIMARY_NATIVE_15_OF_15",
                         "native_m1_bid_rows":len(b),"native_m1_ask_rows":len(a),
                         "m15_matched":len(bars),"m15_native_full":len(full),
                         "m15_partial_excluded":int(len(bars)-len(full))}
    except Exception as e:
        return date,None,{"status":"QUARANTINED","error":type(e).__name__,"msg":str(e)[:60]}
def store(frames):
    if not frames:return 0
    z=pd.concat(frames,ignore_index=True)
    if z.bar_start_utc.duplicated().any():raise RuntimeError("SOURCE_DUPLICATES")
    # All price-value rows are in the private Neon DB only.
    with get_db() as conn:
      with conn.cursor() as cur:
        cur.execute(f"""CREATE TEMP TABLE stage2026(
            source_id TEXT,bar_start_utc TIMESTAMPTZ,
            bid_open FLOAT8,bid_high FLOAT8,bid_low FLOAT8,bid_close FLOAT8,
            ask_open FLOAT8,ask_high FLOAT8,ask_low FLOAT8,ask_close FLOAT8,
            m1_matched SMALLINT,source_vintage TEXT
        ) ON COMMIT DROP""")
        with cur.copy("COPY stage2026 ("+",".join(FIELDS)+") FROM STDIN") as w:
          for row in z.itertuples(index=False):
            w.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
                         float(row.bid_open),float(row.bid_high),float(row.bid_low),float(row.bid_close),
                         float(row.ask_open),float(row.ask_high),float(row.ask_low),float(row.ask_close),
                         int(row.m1_matched),"2026-10-08_RETRIEVED_HISTORICAL_NOT_PIT"))
        cur.execute(f"""INSERT INTO {TABLE} ({','.join(FIELDS)})
          SELECT {','.join(FIELDS)} FROM stage2026
          ON CONFLICT(source_id,bar_start_utc) DO NOTHING""")
        n=cur.rowcount
      conn.commit()
    return int(n)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--month",required=True,type=int,choices=range(1,11))
    args=parser.parse_args()
    start=dt.date(2026,args.month,1)
    end=min(dt.date(2026,10,8),dt.date(2026,args.month+1,1)-dt.timedelta(days=1)) if args.month<10 else dt.date(2026,10,8)
    days=[]
    dd=start
    while dd<=end:
        if dd.weekday()<5:days.append(dd)
        dd+=dt.timedelta(days=1)
    init()
    have=existing(days)
    # Keep previously collected correct days; never repeat successful complete days.
    todo=[z for z in days if have.get(z.isoformat(),0)<70]
    log={};frames=[]
    tic=time.monotonic()
    # Small concurrency respects public vendor rate limits and avoids 503 storms.
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs={pool.submit(get_one,day):day for day in todo}
        for future in as_completed(jobs):
            day,data,info=future.result()
            log[day.isoformat()]=info
            if data is not None:frames.append(data)
    stored=store(frames)
    with get_db() as conn:
      with conn.cursor() as cur:
        cur.execute(f"""SELECT COUNT(*),COUNT(DISTINCT (bar_start_utc AT TIME ZONE 'UTC')::date)
          FROM {TABLE} WHERE source_id=%s AND bar_start_utc>=%s AND bar_start_utc<%s""",
          (SOURCE,start.isoformat(),(end+dt.timedelta(days=1)).isoformat()))
        count,nt=cur.fetchone()
    statuses={}
    for info in log.values():
        key=info["status"];statuses[key]=statuses.get(key,0)+1
    out={"status":"PRIMARY_2026_MONTH_SOURCE_CANDIDATE_ACQUIRED",
         "month":f"2026-{args.month:02d}","source_id":SOURCE,
         "asof":CONTRACT,"requested_weekdays":len(days),
         "previous_cached_accepted_days":len([d for d in days if have.get(d.isoformat(),0)>=70]),
         "download_attempt_days":len(todo),"accepted_download_days":len(frames),
         "new_private_m15":stored,"private_month_m15_rows":int(count),
         "private_month_distinct_utc_dates":int(nt),
         "download_status_counts":statuses,"private_licensed_quotes_in_git":False,
         "source_evidence":"native M1 direct Dukascopy BIN > BID+ASK M15",
         "model_training_or_scoring_done":False,"elapsed_seconds":int(time.monotonic()-tic)}
    path=AX/f"GOLD_EXECUTION_2026_DUKASCOPY_PRIMARY_MONTH_{args.month:02d}_QC_20261008.json"
    path.write_text(json.dumps(out,indent=2)+"\n")
    print("MONTH_2026_SOURCE_RESULT",json.dumps(out),flush=True)
    print("FAILED_DAY_COUNTS_BY_REASON",statuses,flush=True)
if __name__=="__main__":main()
