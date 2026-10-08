"""2026 XAU Dukascopy-node PUBLIC third-party mirror, strict adversarial audit.

NOT automatically trusted: publisher's Jan-May M1 files contain synthetic or
forward-filled all-calendar-minute coverage (including definitely closed hours).
Never count those as native observed M1 evidence. Remove definitely-closed market
hours, flat-padded 15m intervals, and independently compare matched BID/ASK
quotes against EV 2025 and directly downloaded primary 2026 Dukascopy M1.

Only if independent source-overlap 2025 and 2026 PRICE gates pass, preserve
nonclosed price bars in separated private Neon research panel. Original tables,
models, labels unchanged; no raw prices publicly committed.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from datetime import datetime,timezone
import hashlib,io,json,os,time
import numpy as np,pandas as pd,requests,psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_2026_DUKASCOPY_NODE_MIRROR_SOURCE_FORENSIC_20261008.json"
SOURCE="THIRD_PARTY_GITHUB_DUKASCOPY_NODE_M1_2026_M15_BIDASK_CANDIDATE_V1"
TABLE="gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidate"
GITHUB_REPO="3650326613-png/dukascopy_xauusd_1m_data"
URL="https://raw.githubusercontent.com/"+GITHUB_REPO+"/main/xauusd/{side}/m1/xauusd_{side}_m1_{year}_{month:02d}.csv"
PERIODS=[(2025,12)]+[(2026,m) for m in range(1,9)]
FIELDS=["source_id","bar_start_utc","bid_open","bid_high","bid_low","bid_close",
        "ask_open","ask_high","ask_low","ask_close",
        "matched_calendar_m1_count","source_vintage"]

def source_csv(y,m,side):
    url=URL.format(year=y,month=m,side=side)
    last=None
    for _ in range(2):
      try:
        r=requests.get(url,timeout=(12,38),headers={"User-Agent":"Gold-Execution-Source-Audit/1.0"})
        if r.status_code!=200:raise RuntimeError(f"CSV_HTTP_{r.status_code}")
        b=r.content
        if len(b)<100000 or len(b)>15000000:raise RuntimeError("CSV_SIZE_INVALID")
        z=pd.read_csv(io.BytesIO(b))
        if not {"timestamp","open","high","low","close"}.issubset(z.columns):
            raise RuntimeError("CSV_SCHEMA_INVALID")
        z=z[["timestamp","open","high","low","close"]].copy()
        z["ts"]=pd.to_datetime(pd.to_numeric(z.timestamp,errors="raise"),
                    unit="ms",utc=True)
        if z.ts.duplicated().any():raise RuntimeError("DUPLICATE_MIRROR_M1")
        if not (z.ts.dt.year.eq(y)&z.ts.dt.month.eq(m)).all():
            raise RuntimeError("MIRROR_CROSSED_MONTH")
        if not (z.ts.dt.second==0).all():raise RuntimeError("MINUTE_ALIGNMENT")
        for k in ("open","high","low","close"):
            z[k]=pd.to_numeric(z[k],errors="raise")
        if not z[["open","high","low","close"]].notna().all().all():
            raise RuntimeError("MIRROR_NAN_PRICES")
        if not z.close.between(200,15000).all():raise RuntimeError("MIRROR_PRICE_SCALE")
        if (z.high+1e-8<z[["open","low","close"]].max(axis=1)).any() or (
            z.low-1e-8>z[["open","high","close"]].min(axis=1)).any():
            raise RuntimeError("MIRROR_BAD_OHLC")
        return z.sort_values("ts"),{"status":"CSV_RECEIVED",
            "raw_sha256":hashlib.sha256(b).hexdigest(),
            "rows":len(z),"size_bytes":len(b)}
      except Exception as e:
        last=type(e).__name__+":"+str(e)[:90]
        time.sleep(.5)
    return None,{"status":"UNAVAILABLE","reason":last}

def m15_pair(bid,ask):
    b=bid[["ts","open","high","low","close"]].rename(columns={
        x:"bid_"+x for x in ("open","high","low","close")})
    a=ask[["ts","open","high","low","close"]].rename(columns={
        x:"ask_"+x for x in ("open","high","low","close")})
    x=b.merge(a,on="ts",validate="one_to_one",how="inner")
    if x.empty:raise RuntimeError("MIRROR_NO_M1_OVERLAP")
    if (x.ask_close+1e-9<x.bid_close).sum()>3:
        raise RuntimeError("MIRROR_CROSSED_QUOTES_ON_OPEN_MARKET")
    # Recognize suspicious padded closed-market minute records. DO NOT silently
    # represent 24/7 calendar coverage as native broker price observations.
    day=x.ts.dt.dayofweek
    closed=(day==5)|((day==6)&(x.ts.dt.hour<21))
    closed_minutes=int(closed.sum())
    x=x.loc[~closed].copy().set_index("ts")
    rules={k:("first" if k.endswith("_open") else "last" if k.endswith("_close")
              else "max" if k.endswith("_high") else "min")
           for k in x.columns}
    g=x.resample("15min",label="left",closed="left").agg(rules)
    g["matched_calendar_m1_count"]=x.bid_close.resample("15min").count()
    g=g[g.matched_calendar_m1_count==15].dropna().reset_index().rename(
        columns={"ts":"bar_start_utc"})
    # Quarantine any 15m flat-fill artifact; a real broker may have a flat
    # short period; exclude conservatively rather than claim true ticks.
    flat=((g.bid_high-g.bid_low).abs()<1e-8)|(
           (g.ask_high-g.ask_low).abs()<1e-8)
    flat_excluded=int(flat.sum())
    g=g.loc[~flat].copy()
    if (g.ask_close<g.bid_close).any() or (g.ask_open<g.bid_open).any():
        raise RuntimeError("MIRROR_M15_CROSSED_QUOTES")
    return g,{"market_closed_minute_rows_quarantined":closed_minutes,
        "minute_aligned_paired_rows":len(x),
        "full_calendar_minute_m15_before_flat_filter":int(len(flat)),
        "zero_range_m15_quarantined":flat_excluded,
        "accepted_nonclosed_m15_after_flat_filter":len(g),
        "label":"THIRD_PARTY_M1_CALENDAR_FILLED_NOT_PROOF_OF_TICK_NATIVE"}

def compare_primary(con,g):
    with con.cursor() as c:
      c.execute("""SELECT bar_start_utc,bid_open,bid_close,ask_open,ask_close
          FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
          WHERE source_id='DUKASCOPY_DIRECT_M1_BIDASK_2026_M15_NATIVE_FULL_V2'
          AND bar_start_utc>='2026-01-01' AND bar_start_utc<'2026-09-01'
          ORDER BY bar_start_utc""")
      rows=c.fetchall()
    if not rows:return {"status":"NO_PRIMARY_2026_TABLE_ROWS","matched_cells":0}
    p=pd.DataFrame(rows,columns=["bar_start_utc","bid_open","bid_close","ask_open","ask_close"])
    p.bar_start_utc=pd.to_datetime(p.bar_start_utc,utc=True)
    shared=g.merge(p,on="bar_start_utc",how="inner",suffixes=("_mirror","_direct"),
                   validate="one_to_one")
    diffs=[]
    for name in ("bid_open","bid_close","ask_open","ask_close"):
       diffs.extend((10000*np.abs(
          shared[name+"_mirror"].to_numpy()-shared[name+"_direct"].to_numpy()
       )/shared[name+"_direct"].to_numpy()).tolist())
    n=len(diffs)
    return {"status":"PRIMARY_OVERLAP_EVALUATED",
      "matched_m15_bars":len(shared),"matched_price_cells":n,
      "matched_utc_days":int(shared.bar_start_utc.dt.date.nunique()),
      "median_abs_bps":float(np.median(diffs)) if n else None,
      "p95_abs_bps":float(np.percentile(diffs,95)) if n else None,
      "max_abs_bps":float(np.max(diffs)) if n else None,
      "price_gate_pass":bool(n>=500 and len(shared)>=125 and
              np.median(diffs)<=.3 and np.percentile(diffs,95)<=3.) if n else False}

def compare_ev2025(con,g):
    with con.cursor() as c:
      c.execute("""SELECT bar_start_utc,bid_open,bid_close,ask_open,ask_close
            FROM gold_research_evduka_xau15m_bidask_candidate
            WHERE source_id='EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1'
            AND bar_start_utc>='2025-12-01' AND bar_start_utc<'2026-01-01'
            ORDER BY bar_start_utc""")
      rows=c.fetchall()
    p=pd.DataFrame(rows,columns=["bar_start_utc","bid_open","bid_close","ask_open","ask_close"])
    p.bar_start_utc=pd.to_datetime(p.bar_start_utc,utc=True)
    s=g.merge(p,on="bar_start_utc",how="inner",suffixes=("_mirror","_ev"),
              validate="one_to_one")
    diffs=[]
    for name in ("bid_open","bid_close","ask_open","ask_close"):
      diffs.extend((10000*np.abs(s[name+"_mirror"]-s[name+"_ev"])/s[name+"_ev"]).tolist())
    n=len(diffs)
    return {"matched_m15_bars":len(s),"matched_price_cells":n,
      "median_abs_bps":float(np.median(diffs)) if n else None,
      "p95_abs_bps":float(np.percentile(diffs,95)) if n else None,
      "price_gate_pass":bool(n>=500 and np.median(diffs)<=.3
                 and np.percentile(diffs,95)<=3.) if n else False}

def persist_private(con,frame):
    if frame.empty:return 0
    with con.cursor() as c:
      c.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE}(
          source_id TEXT NOT NULL,bar_start_utc TIMESTAMPTZ NOT NULL,
          bid_open DOUBLE PRECISION NOT NULL,bid_high DOUBLE PRECISION NOT NULL,
          bid_low DOUBLE PRECISION NOT NULL,bid_close DOUBLE PRECISION NOT NULL,
          ask_open DOUBLE PRECISION NOT NULL,ask_high DOUBLE PRECISION NOT NULL,
          ask_low DOUBLE PRECISION NOT NULL,ask_close DOUBLE PRECISION NOT NULL,
          matched_calendar_m1_count SMALLINT NOT NULL,source_vintage TEXT NOT NULL,
          PRIMARY KEY(source_id,bar_start_utc))""")
      c.execute("""CREATE TEMP TABLE stage (
          source_id TEXT,bar_start_utc TIMESTAMPTZ,
          bid_open DOUBLE PRECISION,bid_high DOUBLE PRECISION,bid_low DOUBLE PRECISION,bid_close DOUBLE PRECISION,
          ask_open DOUBLE PRECISION,ask_high DOUBLE PRECISION,ask_low DOUBLE PRECISION,ask_close DOUBLE PRECISION,
          matched_calendar_m1_count SMALLINT,source_vintage TEXT) ON COMMIT DROP""")
      with c.copy("COPY stage("+",".join(FIELDS)+") FROM STDIN") as w:
        for row in frame.itertuples(index=False):
          w.write_row((SOURCE,row.bar_start_utc.to_pydatetime(),
           *[float(getattr(row,k)) for k in FIELDS[2:10]],
           int(row.matched_calendar_m1_count),
           "GITHUB_THIRD_PARTY_2026_08_23_M1_MIRROR_NOT_PIT_CALENDAR_PADDED"))
      c.execute(f"""INSERT INTO {TABLE}({','.join(FIELDS)})
          SELECT {','.join(FIELDS)} FROM stage
          ON CONFLICT(source_id,bar_start_utc) DO NOTHING""")
      n=c.rowcount
    con.commit()
    return n

def main():
    tick=time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
      fut={pool.submit(source_csv,y,m,side):(y,m,side)
             for y,m in PERIODS for side in ("bid","ask")}
      allresult={}
      for f in as_completed(fut):
        key=fut[f];allresult[key]=f.result()
        print("FETCH_MIRROR",key,allresult[key][1],flush=True)
    parts_2026=[];pilot25=None;monthly=[]
    for y,m in PERIODS:
      b,bs=allresult[(y,m,"bid")];a,ass=allresult[(y,m,"ask")]
      rec={"month":f"{y}-{m:02d}","bid":bs,"ask":ass}
      if b is None or a is None:
        rec["status"]="UNAVAILABLE";monthly.append(rec);continue
      try:
        k,info=m15_pair(b,a)
        rec.update(info);rec["status"]="QC_FILTERED_NONCLOSED"
        if y==2025:pilot25=k
        elif len(k):parts_2026.append(k)
      except Exception as e:
        rec["status"]="QUARANTINED";rec["error"]=str(e)[:150]
      monthly.append(rec)
    report={"asof":"2026-10-08","source":SOURCE,"third_party_repository":GITHUB_REPO,
       "status":"SOURCE_RESEARCH_BLOCKED_PENDING_GATES","month_receipts":monthly,
       "calendar_filled_weekends_and_flat_m15_not_native":True,
       "raw_price_files_committed_to_git":False,
       "source_identity":"Dukascopy-node republished public M1, distinct from direct Dukascopy native M1",
       "2026_latest_possible":"2026-08-20; Sep and Oct NOT present in source"}
    if not parts_2026 or pilot25 is None:
        report["reason"]="REQUIRED_MONTHLY_FILES_UNAVAILABLE_OR_INVALID"
    else:
      q2026=pd.concat(parts_2026,ignore_index=True).sort_values("bar_start_utc")
      if q2026.bar_start_utc.duplicated().any():raise RuntimeError("MIRROR_2026_DUPLICATE_INTERVALS")
      with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as conn:
        ev=compare_ev2025(conn,pilot25)
        direct=compare_primary(conn,q2026)
        report["2025_original_ev_quote_gate"]=ev
        report["2026_direct_primary_overlap_gate"]=direct
        report["2026_m15_nonclosed_nonflat_candidates"]=len(q2026)
        if ev.get("price_gate_pass") and direct.get("price_gate_pass"):
          insert=persist_private(conn,q2026)
          report["new_private_m15_saved"]=int(insert)
          report["status"]="THIRD_PARTY_DUKASCOPY_MIRROR_SAMPLED_PRICE_GATES_PASS_RESEARCH_CANDIDATE"
          report["same_upstream_provider_not_same_publisher"]=True
          report["2026_full_year_claim"]=False
        else:report["reason"]="MIRROR_VS_PRIMARY_AND_EV_PRICE_GATE_NOT_PASSED"
    report["runtime_seconds"]=int(time.monotonic()-tick)
    OUT.write_text(json.dumps(report,indent=2,default=str)+"\n")
    print("MIRROR_SOURCE_AUDIT_RESULT",json.dumps(report,default=str),flush=True)
if __name__=="__main__":main()
