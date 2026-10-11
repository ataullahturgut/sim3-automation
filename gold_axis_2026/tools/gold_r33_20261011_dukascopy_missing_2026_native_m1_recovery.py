"""R33: recover missing 2026 09:00TR direct Dukascopy BID+ASK native M1 days.
Source acquisition ONLY. No source substitution, model scoring, backfilled PIT, or bank price claims.
Idempotent private Neon INSERT-only. Downloads no already-complete 06:00UTC origins.
"""
from __future__ import annotations
import os,sys,time,json,datetime as dt,traceback
from pathlib import Path
import pandas as pd
import psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_dukascopy_independent_xau_pilot_20261008 as dk
TABLE="gold_research_dukascopy_2026_direct_m1_m15_bidask_v2"
H1="gold_research_dukascopy_xau_h1_monthly_source_candidate_v1"
SOURCE="DUKASCOPY_DIRECT_M1_BIDASK_2026_M15_NATIVE_FULL_V2"
VINTAGE="2026-10-11_RETRIEVED_HISTORICAL_NOT_PIT"
END=dt.date(2026,10,9)
OUT=AX/"GOLD_R33_20261011_2026_PRIMARY_M1_MISSING_DAY_RECOVERY_QC.json"
def db():
    return psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20)
def todo():
    with db() as c:
        days={r[0] for r in c.execute(
           f"SELECT (bar_start_utc AT TIME ZONE 'UTC')::date FROM {TABLE} "
           "WHERE source_id=%s AND EXTRACT(HOUR FROM bar_start_utc AT TIME ZONE 'UTC')=6 "
           "AND EXTRACT(MINUTE FROM bar_start_utc AT TIME ZONE 'UTC')=0",
           (SOURCE,)).fetchall()}
    start=dt.date(2026,1,1); ds=[]
    while start<=END:
        if start.weekday()<5 and start not in days:ds.append(start)
        start+=dt.timedelta(days=1)
    return ds
def acquire(day):
    record={"utc_date":day.isoformat(),"attempts":[]}
    for attempt in (1,2):
        try:
            b,bi=dk.pull(day.isoformat(),"BID")
            a,ai=dk.pull(day.isoformat(),"ASK")
            detail={"attempt":attempt,"bid_result":bi.get("result"),"ask_result":ai.get("result"),
               "bid_sha256":bi.get("sha256_bi5"),"ask_sha256":ai.get("sha256_bi5"),
               "bid_causes":bi.get("causes",[])[:2],"ask_causes":ai.get("causes",[])[:2]}
            record["attempts"].append(detail)
            if b is None or a is None or b.empty or a.empty:
                record["status"]="SOURCE_UNAVAILABLE_OR_CLOSED";continue
            m,der=dk.derive(b,a)
            m=m[m.m1_matched.eq(15)].copy()
            if m.empty or m.bar_start_utc.duplicated().any():raise ValueError("NATIVE_M1_M15_INCOMPLETE")
            if len(m)<72:raise ValueError("INSUFFICIENT_NATIVE_M15_BARS_"+str(len(m)))
            if ((m.bar_start_utc.dt.dayofweek==5) |
                ((m.bar_start_utc.dt.dayofweek==6)&(m.bar_start_utc.dt.hour<21))).any():
                raise ValueError("IMPOSSIBLE_WEEKEND_BARS")
            if (m.ask_close < m.bid_close).any() or (m.bid_close<=0).any():raise ValueError("INVALID_QUOTES")
            issue=dt.datetime.combine(day,dt.time(6),tzinfo=dt.timezone.utc)
            needed=pd.date_range(issue-dt.timedelta(hours=4,minutes=15),periods=16,freq="15min",tz="UTC")
            found=set(m.bar_start_utc)
            if pd.Timestamp(issue) not in found or any(x not in found for x in needed):
                raise ValueError("MISSING_06_OR_PREISSUE_16")
            # A vendor can publish 15 calendar-padded M1 candles despite a CLOSED market.
            # E.g. 2026-01-01 has 92/96 completely flat M15 bars, only trading after 23Z.
            pre=m[m.bar_start_utc.isin(needed)]
            active=((pre.bid_high>pre.bid_low)|(pre.ask_high>pre.ask_low))
            if len(pre)!=16 or int(active.sum())<4:
                raise ValueError("INACTIVE_OR_PADDED_09TR_PREISSUE_SESSION")
            record["active_preissue_m15"]=int(active.sum())
            record["native_bars"]=len(m)
            record["bid_sha256"]=bi.get("sha256_bi5")
            record["ask_sha256"]=ai.get("sha256_bi5")
            with db() as conn:
                ref=conn.execute(f"SELECT utc,bid_open,bid_close,ask_open,ask_close FROM {H1} WHERE utc >= %s AND utc < %s",
                       (day.isoformat(),(day+dt.timedelta(days=1)).isoformat())).fetchall()
                hmap={r[0]:r[1:] for r in ref}
                bytime={row.bar_start_utc.to_pydatetime():row for row in m.itertuples(index=False)}
                # Different direct monthly H1 endpoint of the *same* upstream publisher.
                checks=0; mismatches=[]
                for hour,hvals in hmap.items():
                    r0=bytime.get(hour);r3=bytime.get(hour+dt.timedelta(minutes=45))
                    if r0 is None or r3 is None:continue
                    got=(float(r0.bid_open),float(r3.bid_close),float(r0.ask_open),float(r3.ask_close))
                    checks+=1
                    if got!=tuple(float(v) for v in hvals):mismatches.append(hour.isoformat())
                record["direct_monthly_H1_hours_checked"]=checks
                record["direct_monthly_H1_mismatches"]=len(mismatches)
                if checks<20 or mismatches:
                    raise ValueError("DIRECT_H1_PARITY_FAIL_OR_INSUFFICIENT")
                old=conn.execute(f"SELECT bar_start_utc,bid_open,bid_high,bid_low,bid_close,ask_open,ask_high,ask_low,ask_close FROM {TABLE} WHERE source_id=%s AND bar_start_utc >= %s AND bar_start_utc < %s",
                   (SOURCE,day.isoformat(),(day+dt.timedelta(days=1)).isoformat())).fetchall()
                new={row.bar_start_utc.to_pydatetime():tuple(float(getattr(row,k)) for k in
                     ("bid_open","bid_high","bid_low","bid_close","ask_open","ask_high","ask_low","ask_close"))
                     for row in m.itertuples(index=False)}
                if any(t not in new or tuple(vals)!=new[t] for t,*vals in old):
                    raise ValueError("DIRECT_PRIMARY_OVERLAP_PRICE_CONFLICT")
                fields=["source_id","bar_start_utc","bid_open","bid_high","bid_low","bid_close","ask_open","ask_high","ask_low","ask_close","m1_matched","source_vintage"]
                rows=[(SOURCE,t,*vals,15,VINTAGE) for t,vals in new.items()]
                with conn.cursor() as cur:
                    cur.executemany(f"INSERT INTO {TABLE} ({','.join(fields)}) VALUES ({','.join(['%s']*len(fields))}) ON CONFLICT (source_id,bar_start_utc) DO NOTHING",rows)
                    inserted=cur.rowcount
                conn.commit()
            record["inserted_new_native_M15"]=int(inserted)
            record["status"]="INSERTED_DIRECT_NATIVE_M1_H1_EXACT"
            return record
        except Exception as ex:
            record["attempts"].append({"attempt":attempt,"validation_error":type(ex).__name__+":"+str(ex)[:125]})
            if attempt==2:
                record["status"]="QUARANTINED"
                return record
        if attempt==1:time.sleep(1)
    return record
def main():
    if not os.environ.get("NEON_DATABASE_URL"):raise RuntimeError("NEON_DATABASE_URL not configured")
    days=todo();results=[];start=time.monotonic()
    print("R33_SOURCE_RETRY_DAYS",len(days),flush=True)
    # Serial days keep vendor rate/HTTP pressure low; stop safely on job timeout.
    for day in days:
        result=acquire(day);results.append(result)
        print("R33_DAY",json.dumps({"date":day.isoformat(),"status":result["status"],
               "new":result.get("inserted_new_native_M15",0),"H1_checked":result.get("direct_monthly_H1_hours_checked",0)}),flush=True)
        OUT.write_text(json.dumps({"source":SOURCE,"source_vintage":VINTAGE,
           "retrieval_asof_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
           "end_utc_date":END.isoformat(),"initial_missing_09_origin_weekdays":len(days),
           "processed":len(results),"new_native_m15":sum(x.get("inserted_new_native_M15",0) for x in results),
           "accepted_days":sum(x["status"]=="INSERTED_DIRECT_NATIVE_M1_H1_EXACT" for x in results),
           "results":results,"seconds_elapsed":int(time.monotonic()-start),
           "PIT_certified":False,"models_scored":False,"quotes_in_git":False},indent=2)+"\n")
    print("R33_DONE",len(results),sum(x.get("inserted_new_native_M15",0) for x in results),flush=True)
if __name__=="__main__": main()
