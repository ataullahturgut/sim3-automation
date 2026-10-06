from __future__ import annotations

import calendar, hashlib, json, os, time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
EXISTING=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_2022_WARMUP_V5_BACKFILL_OUT";OUT.mkdir(exist_ok=True)

TD="https://api.twelvedata.com/time_series"
UTC=ZoneInfo("UTC");NY=ZoneInfo("America/New_York")
LON=ZoneInfo("Europe/London");SHA=ZoneInfo("Asia/Shanghai")
FETCH_START=date(2021,12,30);FETCH_END=date(2023,1,3)
LABEL_START=date(2022,1,1);LABEL_END=date(2022,12,31)
DATASET="GLBX.MDP3";SCHEMA="ohlcv-1h";ROLLS=["n","v"];GC_COST_CAP=0.20

UK_BANK=set(pd.to_datetime([
 "2022-01-03","2022-04-15","2022-04-18","2022-05-02","2022-06-02",
 "2022-06-03","2022-08-29","2022-09-19","2022-12-26","2022-12-27"
]).date)

SGE_CLOSED=set()
def add_range(a,b):
    for d in pd.date_range(a,b,freq="D"):SGE_CLOSED.add(d.date())
for a,b in [
 ("2022-01-01","2022-01-03"),
 ("2022-01-31","2022-02-06"),
 ("2022-04-03","2022-04-05"),
 ("2022-04-30","2022-05-04"),
 ("2022-06-03","2022-06-05"),
 ("2022-09-10","2022-09-12"),
 ("2022-10-01","2022-10-09"),
]:add_range(a,b)

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def month_chunks(a,b):
    cur=date(a.year,a.month,1);out=[]
    while cur<=b:
        last=date(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        out.append((max(cur,a),min(last,b)));cur=last+timedelta(days=1)
    return out

def fetch_td(a,b,key):
    params={"symbol":"XAU/USD","interval":"15min","timezone":"UTC","order":"ASC",
            "outputsize":5000,"apikey":key,
            "start_date":f"{a.isoformat()} 00:00:00","end_date":f"{b.isoformat()} 23:59:59"}
    last=None
    for attempt in range(1,5):
        r=requests.get(TD,params=params,timeout=90)
        try:j=r.json()
        except Exception:j={"raw":r.text[:500]}
        vals=j.get("values") if isinstance(j,dict) else None
        if r.ok and vals:
            q=pd.DataFrame([{
              "dt_utc":pd.Timestamp(z["datetime"],tz="UTC"),
              "open":float(z["open"]),"high":float(z["high"]),
              "low":float(z["low"]),"close":float(z["close"]),
              "volume":np.nan if z.get("volume") in (None,"") else float(z["volume"])
            } for z in vals])
            return q,{"start":str(a),"end":str(b),"rows":len(q),"http":r.status_code,"meta":j.get("meta")}
        last={"attempt":attempt,"status":r.status_code,"body":j}
        time.sleep(20*attempt)
    raise RuntimeError(f"TWELVE_FETCH_FAIL {a} {b} {last}")

def fetch_raw():
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key:raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    parts=[];meta=[]
    for a,b in month_chunks(FETCH_START,FETCH_END):
        q,m=fetch_td(a,b,key);parts.append(q);meta.append(m);time.sleep(2)
    x=pd.concat(parts,ignore_index=True).sort_values("dt_utc")
    dup=int(x.duplicated("dt_utc").sum())
    x=x.drop_duplicates("dt_utc",keep="last").reset_index(drop=True)
    if not ((x.dt_utc.dt.minute%15)==0).all():raise RuntimeError("NON_15M_TIMESTAMP")
    good=(x.high>=x[["open","close"]].max(axis=1))&(x.low<=x[["open","close"]].min(axis=1))&(x[["open","high","low","close"]]>0).all(axis=1)
    if not good.all():raise RuntimeError(f"OHLC_FAIL {int((~good).sum())}")
    return x,meta,dup

def overlap_audit(x):
    e=pd.read_csv(EXISTING)
    e["dt_utc"]=pd.to_datetime(e.dt_utc,utc=True)
    for c in ["open","high","low","close"]:e[c]=pd.to_numeric(e[c],errors="raise")
    start=pd.Timestamp("2022-12-30",tz="UTC");end=pd.Timestamp("2023-01-04",tz="UTC")
    a=x[(x.dt_utc>=start)&(x.dt_utc<end)][["dt_utc","open","high","low","close"]]
    b=e[(e.dt_utc>=start)&(e.dt_utc<end)][["dt_utc","open","high","low","close"]]
    m=a.merge(b,on="dt_utc",how="inner",suffixes=("_new","_old"))
    if len(m)<50:raise RuntimeError(f"OVERLAP_TOO_SMALL {len(m)}")
    out={"matched_rows":int(len(m)),"new_only":int(len(a)-len(m)),"old_only":int(len(b)-len(m))}
    for c in ["open","high","low","close"]:
        d=(m[f"{c}_new"]-m[f"{c}_old"]).abs()
        out[f"{c}_mismatch_n"]=int((d>1e-9).sum());out[f"{c}_max_abs_diff"]=float(d.max())
    if any(out[f"{c}_mismatch_n"] for c in ["open","high","low","close"]):
        raise RuntimeError(f"TWELVE_OVERLAP_VALUE_FAIL {out}")
    return out

def fetch_gc():
    import databento as db
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:raise RuntimeError("DATABENTO_API_KEY_MISSING")
    c=db.Historical(key);costs={}
    for r in ROLLS:
        costs[r]=float(c.metadata.get_cost(dataset=DATASET,schema=SCHEMA,symbols=[f"GC.{r}.0"],
                         stype_in="continuous",start="2021-12-30",end="2023-01-04"))
    total=sum(costs.values())
    if total>GC_COST_CAP:raise RuntimeError(f"GC_COST_CAP {total}>{GC_COST_CAP}")
    out={}
    for r in ROLLS:
        q=c.timeseries.get_range(dataset=DATASET,schema=SCHEMA,symbols=[f"GC.{r}.0"],
          stype_in="continuous",start="2021-12-30",end="2023-01-04").to_df().reset_index()
        if "ts_event" not in q.columns and "index" in q.columns:q=q.rename(columns={"index":"ts_event"})
        out[r]=set(pd.to_datetime(q.ts_event,utc=True))
    return out,costs,total

def ny_ts(d,hh,mm):
    return pd.Timestamp(datetime(d.year,d.month,d.day,hh,mm,tzinfo=NY))

def gc_has(gc,t):
    return any(pd.Timestamp(t) in gc[r] for r in ROLLS)

def gc_flags(gc,part,win,s,e):
    if part=="WGC_2026_NY3" and win=="US":
        a=s;b=e-pd.Timedelta(hours=1)
    elif part=="SOBTI_5_ET" and win=="NY_LONDON_LIT":
        a=s;b=e.floor("h")
    elif part=="SOBTI_5_ET" and win=="US_LATE_LIT":
        a=s.floor("h");b=e-pd.Timedelta(hours=1)
    else:return None,None,None
    ha=gc_has(gc,a);hb=gc_has(gc,b);return bool(ha),bool(hb),bool(ha and hb)

def pmaps(x):
    op=dict(zip(x.dt_utc,x.open.astype(float)))
    cl=dict(zip(x.dt_utc,x.close.astype(float)))
    present=set(x.dt_utc)
    return op,cl,present

def expected_grid(s,e):
    return pd.date_range(s,e-pd.Timedelta(minutes=15),freq="15min",tz="UTC")

def allowed_maintenance(part,win,s):
    if not (part=="SOBTI_5_ET" and win=="US_LATE_LIT"):return set()
    nd=s.tz_convert("America/New_York").date()
    base=pd.Timestamp(f"{nd} 17:00",tz="America/New_York").tz_convert("UTC")
    return {base+pd.Timedelta(minutes=15*k) for k in range(4)}

def row(op,cl,present,gc,label_date,part,win,s,e):
    s=s.tz_convert("UTC");e=e.tz_convert("UTC");last=e-pd.Timedelta(minutes=15)
    ps=op.get(s);pe=cl.get(last)
    boundary_ok=(ps is not None and pe is not None)
    ret=(pe/ps-1.0) if boundary_ok else np.nan
    direction="UP" if boundary_ok and ret>0 else ("DOWN" if boundary_ok and ret<0 else ("FLAT" if boundary_ok else None))

    missing=[t for t in expected_grid(s,e) if t not in present]
    allowed=allowed_maintenance(part,win,s)
    disallowed=[t for t in missing if t not in allowed]
    path_clean=(len(disallowed)==0)

    london_date=s.tz_convert("Europe/London").date()
    sh_date=s.tz_convert("Asia/Shanghai").date()
    london_open=london_date.weekday()<5 and london_date not in UK_BANK
    sge_open=sh_date.weekday()<5 and sh_date not in SGE_CLOSED
    gs,ge,gfull=gc_flags(gc,part,win,s,e)

    price_trainable=boundary_ok and direction in ("UP","DOWN")
    reasons=[]
    if not boundary_ok:reasons.append("MISSING_BOUNDARY")
    if direction=="FLAT":reasons.append("FLAT")
    if part=="SOBTI_5_ET" and win=="US_LATE_LIT" and s.tz_convert("America/New_York").weekday()==4:
        price_trainable=False;reasons.append("FRIDAY_US_LATE")

    core=price_trainable
    if part=="WGC_2026_NY3":
        if win=="EUROPE" and not london_open:core=False;reasons.append("LONDON_BANK_HOLIDAY")
        elif win=="US" and gfull is not True:core=False;reasons.append("GC_US_WINDOW_NOT_FULL")
    else:
        if win in ("ASIA_MORNING_LIT","ASIA_AFTERNOON_LIT") and not sge_open:
            core=False;reasons.append("SGE_CLOSED")
        elif win=="EUROPE_LIT" and not london_open:
            core=False;reasons.append("LONDON_BANK_HOLIDAY")
        elif win=="NY_LONDON_LIT":
            if not london_open:core=False;reasons.append("LONDON_BANK_HOLIDAY")
            if gfull is not True:core=False;reasons.append("GC_NYLON_WINDOW_NOT_FULL")
        elif win=="US_LATE_LIT" and gfull is not True:
            core=False;reasons.append("GC_USLATE_WINDOW_NOT_FULL")
    final=bool(core and path_clean)
    if not path_clean:reasons.append("DISALLOWED_INTERNAL_15M_GAP")

    return {
      "label_date":label_date.isoformat(),"year":2022,"partition":part,"window":win,
      "start_utc":s.isoformat(),"end_utc":e.isoformat(),
      "start_price":ps,"end_price":pe,"return":ret,"direction":direction,
      "london_business_day":london_open,"sge_business_day":sge_open,
      "gc_boundary_start_active":gs,"gc_boundary_end_active":ge,"gc_window_full":gfull,
      "price_trainable":bool(price_trainable),"core_trainable":bool(core),
      "path_clean":bool(path_clean),"final_trainable":final,
      "missing_15m_slots":len(missing),"allowed_maintenance_missing_slots":sum(t in allowed for t in missing),
      "disallowed_missing_slots":len(disallowed),
      "final_exclusion_reason":"|".join(dict.fromkeys(reasons))
    }

def build_targets(x,gc):
    op,cl,present=pmaps(x);rows=[]
    d=LABEL_START
    while d<=LABEL_END:
        if d.weekday()<5:
            prev=d-timedelta(days=1)
            defs=[
              ("WGC_2026_NY3","ASIA",ny_ts(prev,18,0),ny_ts(d,3,0)),
              ("WGC_2026_NY3","EUROPE",ny_ts(d,3,0),ny_ts(d,8,0)),
              ("WGC_2026_NY3","US",ny_ts(d,8,0),ny_ts(d,17,0)),
              ("SOBTI_5_ET","ASIA_MORNING_LIT",ny_ts(prev,21,0),ny_ts(prev,23,30)),
              ("SOBTI_5_ET","ASIA_AFTERNOON_LIT",ny_ts(d,1,30),ny_ts(d,3,30)),
              ("SOBTI_5_ET","EUROPE_LIT",ny_ts(d,3,30),ny_ts(d,8,0)),
              ("SOBTI_5_ET","NY_LONDON_LIT",ny_ts(d,8,0),ny_ts(d,14,30)),
              ("SOBTI_5_ET","US_LATE_LIT",ny_ts(d,14,30),ny_ts(d,21,0)),
            ]
            for part,win,s,e in defs:rows.append(row(op,cl,present,gc,d,part,win,s,e))
        d+=timedelta(days=1)
    return pd.DataFrame(rows)

def main():
    x,req,dup=fetch_raw()
    overlap=overlap_audit(x)
    gc,costs,gccost=fetch_gc()
    targets=build_targets(x,gc)

    # Hard target integrity.
    final=targets[targets.final_trainable].copy()
    if final.empty:raise RuntimeError("NO_2022_FINAL_TARGETS")
    if final.direction.isna().any() or (~final.direction.isin(["UP","DOWN"])).any():raise RuntimeError("BAD_FINAL_DIRECTION")
    if final.duplicated(["label_date","partition","window"]).any():raise RuntimeError("DUP_FINAL_TARGET")

    rawp=OUT/"xauusd_15m_utc_2022_with_buffer.csv"
    tarp=OUT/"session_targets_v5_equivalent_warmup_2022.csv"
    x.to_csv(rawp,index=False);targets.to_csv(tarp,index=False)

    cov=[]
    for (part,win),g in targets.groupby(["partition","window"],sort=True):
        f=g[g.final_trainable]
        cov.append({"partition":part,"window":win,"rows":len(g),"final_trainable":len(f),
                    "up":int((f.direction=="UP").sum()),"down":int((f.direction=="DOWN").sum()),
                    "first":None if f.empty else f.start_utc.min(),"last":None if f.empty else f.start_utc.max()})

    summary={
      "status":"2022_V5_EQUIVALENT_WARMUP_GATE_PASS",
      "role":"WARMUP_ONLY_NOT_EVALUATION",
      "twelve":{"fetch_start":str(FETCH_START),"fetch_end":str(FETCH_END),"rows":len(x),"duplicate_before_dedup":dup,
                "request_chunks":req,"overlap_with_governed_archive":overlap},
      "databento_gc":{"dataset":DATASET,"schema":SCHEMA,"rolls":ROLLS,"costs":costs,"total_cost_usd":gccost},
      "calendar_authority":{
        "SGE":"Shanghai Gold Exchange Announcement of Trading Schedule during Public Holidays for Year 2022, 2021-12-21",
        "UK":"GOV.UK past bank holidays in England and Wales 2022"
      },
      "rules":{
        "clock":"America/New_York date-aware for both WGC_2026_NY3 and SOBTI_5_ET",
        "target":"exact start 15m OPEN -> exact final 15m CLOSE",
        "venue":"same V4 policy as 2023-2025",
        "internal_path":"all 15m slots required except four 17:00-18:00 NY maintenance slots in Sobti US_LATE",
        "friday_sobti_us_late":"not eligible",
        "imputation":"none"
      },
      "coverage":cov,
      "hashes":{"raw_2022":sha(rawp),"targets_2022":sha(tarp),"existing_2023_2025_raw":sha(EXISTING)},
      "guardrail":"2022 rows may be used only to mature/train Stage-1 session models; no 2022 result is used as a transport/test metric and 2025/2026 remain unopened."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    lines=["# 2022 SESSION WARM-UP — V5-EQUIVALENT DATA GATE","",
      "**Status:** PASS","",
      f"- Twelve overlap matched rows: **{overlap['matched_rows']}**, OHLC mismatches: **0**.",
      f"- 2022 final-trainable session rows: **{len(final)}**.",
      "- Role: **warm-up/training only**, never evaluation.",
      "- 2025/2026 remain unopened."]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":main()
