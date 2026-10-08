"""Uniform 2020-2025 Dukascopy-derived BID+ASK source, strict DAY/OVN labels.
Public output is aggregated counts and digest; licensed quote values private Neon.
This independent 15m feed is M1-derived by EV Trading Labs; native M1 minute
counts are not independently proved and cannot be claimed as checked.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
import numpy as np
import pandas as pd
import psycopg
AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_EV_DUKASCOPY_2020_2025_SESSION_TARGET_QC_20261008.json"
SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1"
TABLE="gold_research_evduka_xau15m_bidask_candidate"
TARGET="gold_research_evduka_xau_session_target_candidate_v1"
FIELDS=["issue_date","year","next_expected_date","day_gate","overnight_gate",
 "day_bid_logret","day_ask_logret","overnight_bid_logret","overnight_ask_logret",
 "day_y","overnight_y","day_bidask_sign_disagreement","ovn_bidask_sign_disagreement",
 "spread_09_bps","spread_17_bps","low_margin_day_10bps","low_margin_ovn_10bps",
 "source_id","quote_semantics","source_vintage","research_evidence_class"]

def get(con):
    with con.cursor() as c:
        c.execute(f"""SELECT bar_start_utc,bid_open,bid_high,bid_low,bid_close,
                      ask_open,ask_high,ask_low,ask_close
               FROM {TABLE} WHERE source_id=%s
               AND bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-01-01'
               ORDER BY bar_start_utc""",(SOURCE,))
        rows=c.fetchall()
    q=pd.DataFrame(rows,columns=["ts","bo","bh","bl","bc","ao","ah","al","ac"])
    q.ts=pd.to_datetime(q.ts,utc=True)
    if q.ts.duplicated().any():raise RuntimeError("DUPLICATE_SOURCE_TIMESTAMPS")
    counts=q.groupby(q.ts.dt.year).size().to_dict()
    if any(counts.get(y,0)<22500 for y in range(2020,2026)):raise RuntimeError("UNIFORM_6_YEAR_SOURCE_INCOMPLETE")
    return q.set_index("ts")

def labels(g):
    idx=g.index
    dates=sorted({x.date() for x in idx if x.hour==6 and x.minute==0 and x.dayofweek<5})
    def getpx(d,hm,key):
        if d is None:return None
        hh,mm=map(int,hm.split(":"))
        ts=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=hh,minutes=mm)
        return float(g.at[ts,key]) if ts in idx else None
    def ret(a,b):
        if a is None or b is None or not a>0 or not b>0:return None
        return float(np.log(b/a))
    rows=[]
    for i,d in enumerate(dates):
        next_expected=(pd.Timestamp(d)+pd.Timedelta(days=3 if pd.Timestamp(d).dayofweek==4 else 1)).date()
        next_d=dates[i+1] if i+1<len(dates) else None
        exact_next=(next_d==next_expected)
        start=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=6)
        full_day=all((start+pd.Timedelta(minutes=15*k)) in idx for k in range(32))
        day_bid=ret(getpx(d,"06:00","bo"),getpx(d,"13:45","bc")) if full_day else None
        day_ask=ret(getpx(d,"06:00","ao"),getpx(d,"13:45","ac")) if full_day else None
        od=getpx(d,"14:00","bo")
        oa=getpx(d,"14:00","ao")
        nb=getpx(next_d,"05:45","bc") if exact_next else None
        na=getpx(next_d,"05:45","ac") if exact_next else None
        if exact_next and pd.Timestamp(d).dayofweek<4:
            t0=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=14)
            t1=pd.Timestamp(next_d,tz="UTC")+pd.Timedelta(hours=6)
            n=int(((idx>=t0)&(idx<t1)).sum())
            dense=n>=55
        else:
            dense=exact_next
        ovn_bid=ret(od,nb) if dense else None
        ovn_ask=ret(oa,na) if dense else None
        def direction(r):return (int(r>0) if r is not None else None)
        if day_bid is None or day_ask is None: day_bid=None;day_ask=None
        if ovn_bid is None or ovn_ask is None: ovn_bid=None;ovn_ask=None
        row={
          "issue_date":d,"year":d.year,"next_expected_date":next_expected,
          "day_gate":"COMPLETE_SINGLE_SOURCE" if day_bid is not None else "QUARANTINE_MISSING_OR_THIN_DAY_PATH",
          "overnight_gate":"COMPLETE_SINGLE_SOURCE" if ovn_bid is not None else "QUARANTINE_MISSING_ANCHOR_PATH_OR_HOLIDAY",
          "day_bid_logret":day_bid,"day_ask_logret":day_ask,
          "overnight_bid_logret":ovn_bid,"overnight_ask_logret":ovn_ask,
          "day_y":direction(day_bid),"overnight_y":direction(ovn_bid),
          "day_bidask_sign_disagreement":(direction(day_bid)!=direction(day_ask)) if day_bid is not None else None,
          "ovn_bidask_sign_disagreement":(direction(ovn_bid)!=direction(ovn_ask)) if ovn_bid is not None else None,
          "spread_09_bps":((getpx(d,"06:00","ao")/getpx(d,"06:00","bo")-1)*10000
                            if getpx(d,"06:00","bo") is not None else None),
          "spread_17_bps":((oa/od-1)*10000 if od is not None else None),
          "low_margin_day_10bps":(abs(day_bid)<=.001) if day_bid is not None else None,
          "low_margin_ovn_10bps":(abs(ovn_bid)<=.001) if ovn_bid is not None else None,
          "source_id":SOURCE,"quote_semantics":"DUKASCOPY_DERIVED_BID_AND_ASK_BARS_NOT_BANK_QUOTES",
          "source_vintage":"EV_TRADING_LABS_PUBLIC_HISTORICAL_RETRIEVED_2026_10_08",
          "research_evidence_class":"M15_NATIVE_SOURCE_COMPLETENESS_15M_ONLY_NOT_NATIVE_M1_VALIDATED"}
        rows.append(row)
    return pd.DataFrame(rows)

def persist(con,z):
    with con.cursor() as c:
        c.execute(f"""CREATE TABLE IF NOT EXISTS {TARGET} (
          issue_date DATE PRIMARY KEY,year INTEGER NOT NULL,next_expected_date DATE,
          day_gate TEXT NOT NULL,overnight_gate TEXT NOT NULL,
          day_bid_logret FLOAT8,day_ask_logret FLOAT8,
          overnight_bid_logret FLOAT8,overnight_ask_logret FLOAT8,
          day_y SMALLINT,overnight_y SMALLINT,
          day_bidask_sign_disagreement BOOLEAN,ovn_bidask_sign_disagreement BOOLEAN,
          spread_09_bps FLOAT8,spread_17_bps FLOAT8,
          low_margin_day_10bps BOOLEAN,low_margin_ovn_10bps BOOLEAN,
          source_id TEXT NOT NULL,quote_semantics TEXT NOT NULL,
          source_vintage TEXT NOT NULL,research_evidence_class TEXT NOT NULL,
          generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
        ddl=[]
        for field in FIELDS:
            if field in ("year","day_y","overnight_y"):
                typ="smallint" if field!="year" else "integer"
            elif field in ("day_bidask_sign_disagreement","ovn_bidask_sign_disagreement",
                           "low_margin_day_10bps","low_margin_ovn_10bps"):typ="boolean"
            elif field in ("day_bid_logret","day_ask_logret","overnight_bid_logret","overnight_ask_logret",
                           "spread_09_bps","spread_17_bps"):typ="float8"
            elif field in ("issue_date","next_expected_date"):typ="date"
            else:typ="text"
            ddl.append(f"{field} {typ}")
        c.execute("CREATE TEMP TABLE stage_session("+",".join(ddl)+") ON COMMIT DROP")
        with c.copy("COPY stage_session ("+",".join(FIELDS)+") FROM STDIN") as cp:
            for row in z.itertuples(index=False,name=None):
                vals=[]
                for k,v in zip(FIELDS,row):
                    if pd.isna(v):v=None
                    elif k in ("year","day_y","overnight_y"):v=int(v)
                    elif k in ("day_bidask_sign_disagreement","ovn_bidask_sign_disagreement",
                           "low_margin_day_10bps","low_margin_ovn_10bps"):v=bool(v)
                    elif k in ("day_bid_logret","day_ask_logret","overnight_bid_logret","overnight_ask_logret",
                           "spread_09_bps","spread_17_bps"):v=float(v)
                    vals.append(v)
                cp.write_row(tuple(vals))
        c.execute(f"""INSERT INTO {TARGET} ({','.join(FIELDS)})
           SELECT {','.join(FIELDS)} FROM stage_session
           ON CONFLICT(issue_date) DO NOTHING""")
        n=c.rowcount
        c.execute(f"""SELECT COUNT(*),COUNT(*) FILTER(WHERE day_y IS NOT NULL),
              COUNT(*) FILTER(WHERE overnight_y IS NOT NULL)
              FROM {TARGET} WHERE source_id=%s""",(SOURCE,))
        totals=c.fetchone()
    con.commit()
    return {"new_origin_rows":int(n),"private_total":int(totals[0]),
       "valid_day":int(totals[1]),"valid_overnight":int(totals[2])}

def main():
    r={"status":"BLOCKED","asof":"2026-10-08",
      "independent_uniform_source":SOURCE,
      "quote_identity":"DUKASCOPY_DERIVED_BID_ASK_ON_SAME_UTC_GRID",
      "target_clock":"Europe/Istanbul fixed UTC+03, 09-17 DAY and 17-next09 OVN",
      "original_archive_overwritten":False,"composite_blended_into_bid":False,
      "native_1min_completeness_proven":False,
      "PIT_historical_vendor_vintage":False,
      "bank_tradable_quote":False,
      "model_retrained":False}
    try:
        with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=25) as con:
            q=get(con)
            z=labels(q)
            years={}
            for yr in range(2020,2026):
                x=z[z.year==yr]
                day=x.day_y.notna();ovn=x.overnight_y.notna()
                bar=q[q.index.year==yr]
                years[str(yr)]={"source_m15_rows":len(bar),"issue_dates":len(x),
                   "day_mature":int(day.sum()),"day_quarantine":int((~day).sum()),
                   "overnight_mature":int(ovn.sum()),"overnight_quarantine":int((~ovn).sum()),
                   "day_bidask_sign_disagreement":int((x.day_bidask_sign_disagreement==True).sum()),
                   "overnight_bidask_sign_disagreement":int((x.ovn_bidask_sign_disagreement==True).sum()),
                   "day_small_bid_move_10bps":int((x.low_margin_day_10bps==True).sum()),
                   "overnight_small_bid_move_10bps":int((x.low_margin_ovn_10bps==True).sum())}
            r["years"]=years
            r["sha256_private_origin_target_vintage"]=hashlib.sha256(
                z[["issue_date","day_gate","overnight_gate","day_bid_logret","overnight_bid_logret"]].
                  to_csv(index=False).encode()).hexdigest()
            r["private_storage"]=persist(con,z)
        r["status"]="UNIFORM_2020_2025_BIDASK_SOURCE_QUALITY_GATED_PRIVATE_RESEARCH_TARGET_CREATED"
    except Exception as e:
        r["status"]="QC_OR_PRIVATE_WRITE_FAILED"
        r["error_type"]=type(e).__name__
        r["error_summary"]=str(e)[:250]
    r["completed_at_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(r,indent=2)+"\n")
    print("FULL_SESSION_SOURCE_GATE_RECEIPT_BEGIN\n",json.dumps(r,indent=2),"\nFULL_SESSION_SOURCE_GATE_RECEIPT_END",flush=True)
    return 0 if r["status"].startswith("UNIFORM_") else 1
if __name__=="__main__":raise SystemExit(main())
