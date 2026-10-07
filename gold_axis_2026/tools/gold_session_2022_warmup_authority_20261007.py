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
OUT=AX/"SESSION_2022_WARMUP_AUTHORITY_OUT"; OUT.mkdir(exist_ok=True)

TD="https://api.twelvedata.com/time_series"
UTC=ZoneInfo("UTC"); NY=ZoneInfo("America/New_York"); LON=ZoneInfo("Europe/London"); SHA=ZoneInfo("Asia/Shanghai"); IST=ZoneInfo("Europe/Istanbul")
FETCH_START=date(2021,12,30); FETCH_END=date(2023,1,2)
LABEL_START=date(2022,1,1); LABEL_END=date(2022,12,31)
EXISTING=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"

DATASET="GLBX.MDP3"; GC_SCHEMA="ohlcv-1h"; GC_ROLLS=["n","v"]; GC_START="2021-12-30"; GC_END="2023-01-03"; GC_COST_CAP=0.20

# Official SGE 2022 holiday authority:
# https://en.sge.com.cn/eng_news_Announcement/10000677
SGE_CLOSED=set()
def add_range(a,b):
    for d in pd.date_range(a,b,freq="D"): SGE_CLOSED.add(d.date())
for a,b in [
    ("2022-01-01","2022-01-03"),
    ("2022-01-31","2022-02-06"),
    ("2022-04-03","2022-04-05"),
    ("2022-04-30","2022-05-04"),
    ("2022-06-03","2022-06-05"),
    ("2022-09-10","2022-09-12"),
    ("2022-10-01","2022-10-09"),
]:
    add_range(a,b)

# GOV.UK England and Wales 2022 bank holidays.
UK_BANK_HOLIDAYS=set(pd.to_datetime([
    "2022-01-03","2022-04-15","2022-04-18","2022-05-02",
    "2022-06-02","2022-06-03","2022-08-29","2022-09-19",
    "2022-12-26","2022-12-27",
]).date)

def sha(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def month_chunks(start:date,end:date):
    cur=date(start.year,start.month,1)
    while cur<=end:
        last=date(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        yield max(start,cur),min(end,last)
        cur=last+timedelta(days=1)

def fetch_chunk(a,b,key):
    params={"symbol":"XAU/USD","interval":"15min","timezone":"UTC","order":"ASC","outputsize":5000,
            "apikey":key,"start_date":f"{a.isoformat()} 00:00:00","end_date":f"{b.isoformat()} 23:59:59"}
    last=None
    for attempt in range(1,5):
        r=requests.get(TD,params=params,timeout=90)
        try:j=r.json()
        except Exception:j={"raw":r.text[:1000]}
        vals=j.get("values") if isinstance(j,dict) else None
        if r.ok and vals:
            rows=[{"dt_utc":pd.Timestamp(z["datetime"],tz="UTC"),"open":float(z["open"]),"high":float(z["high"]),
                   "low":float(z["low"]),"close":float(z["close"]),
                   "volume":None if z.get("volume") in (None,"") else float(z["volume"])} for z in vals]
            return pd.DataFrame(rows),{"start":a.isoformat(),"end":b.isoformat(),"http":r.status_code,
                                      "rows":len(rows),"response_meta":j.get("meta"),"attempt":attempt}
        last={"start":a.isoformat(),"end":b.isoformat(),"http":r.status_code,"response":j,"attempt":attempt}
        time.sleep(20*attempt)
    raise RuntimeError(json.dumps(last,default=str))

def fetch_xau():
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key:raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    parts=[];meta=[]
    for a,b in month_chunks(FETCH_START,FETCH_END):
        q,m=fetch_chunk(a,b,key);parts.append(q);meta.append(m);time.sleep(5)
    x=pd.concat(parts,ignore_index=True).sort_values("dt_utc")
    dup=int(x.duplicated("dt_utc").sum())
    x=x.drop_duplicates("dt_utc",keep="last").reset_index(drop=True)
    if dup:raise RuntimeError(f"RAW_DUPLICATE:{dup}")
    if not ((x.dt_utc.dt.minute%15)==0).all():raise RuntimeError("GRID_FAIL")
    if not (((x.high>=x[["open","close"]].max(axis=1))&(x.low<=x[["open","close"]].min(axis=1))&
            (x[["open","high","low","close"]]>0).all(axis=1))).all():raise RuntimeError("OHLC_FAIL")
    return x,meta

def overlap_audit(x):
    old=pd.read_csv(EXISTING,usecols=["dt_utc","open","high","low","close"])
    old["dt_utc"]=pd.to_datetime(old.dt_utc,utc=True)
    a=pd.Timestamp("2022-12-30",tz="UTC");b=pd.Timestamp("2023-01-03",tz="UTC")
    n=x[(x.dt_utc>=a)&(x.dt_utc<b)][["dt_utc","open","high","low","close"]]
    o=old[(old.dt_utc>=a)&(old.dt_utc<b)]
    m=n.merge(o,on="dt_utc",suffixes=("_new","_old"),how="inner")
    if m.empty:raise RuntimeError("NO_OVERLAP")
    for c in ["open","high","low","close"]:
        m[f"{c}_absdiff"]=(m[f"{c}_new"]-m[f"{c}_old"]).abs()
    exact=np.logical_and.reduce([m[f"{c}_absdiff"].eq(0).to_numpy() for c in ["open","high","low","close"]])
    summ={"matched_rows":int(len(m)),"exact_ohlc_rows":int(exact.sum()),"mismatch_rows":int((~exact).sum()),
          "max_abs_diff":{c:float(m[f"{c}_absdiff"].max()) for c in ["open","high","low","close"]}}
    m.to_csv(OUT/"overlap_audit.csv",index=False)
    if summ["mismatch_rows"]!=0:raise RuntimeError(f"OVERLAP_VALUE_FAIL:{summ}")
    return summ

def ny(d,h,m):return pd.Timestamp(datetime(d.year,d.month,d.day,h,m,tzinfo=NY))
def loc(t,z):return t.tz_convert(z).isoformat()
def direction(r):return "UP" if r>0 else ("DOWN" if r<0 else "FLAT")

def make_row(op,cl,d,part,win,s,e):
    su=s.tz_convert("UTC");eu=e.tz_convert("UTC");ep=eu-pd.Timedelta(minutes=15)
    ps=op.get(su);pe=cl.get(ep)
    ret=None if ps is None or pe is None else pe/ps-1
    dr=None if ret is None else direction(ret)
    if part=="SOBTI_5_ET" and win=="US_LATE_LIT" and d.weekday()==4:
        status="NOT_ELIGIBLE_WEEKLY_CLOSE_FRIDAY";train=False
    elif ps is None and pe is None:status="EXCLUDE_BOTH_BOUNDARIES_MISSING";train=False
    elif ps is None:status="EXCLUDE_START_BOUNDARY_MISSING";train=False
    elif pe is None:status="EXCLUDE_END_BOUNDARY_MISSING";train=False
    elif dr=="FLAT":status="EXCLUDE_ZERO_RETURN";train=False
    else:status="TRAINABLE";train=True
    return {"label_date":d.isoformat(),"year":d.year,"weekday":d.weekday(),"partition":part,"window":win,
            "start_utc":su.isoformat(),"end_utc":eu.isoformat(),"end_price_bar_open_utc":ep.isoformat(),
            "start_ny":loc(su,NY),"end_ny":loc(eu,NY),"start_london":loc(su,LON),"end_london":loc(eu,LON),
            "start_shanghai":loc(su,SHA),"end_shanghai":loc(eu,SHA),"start_istanbul":loc(su,IST),"end_istanbul":loc(eu,IST),
            "start_price_semantics":"OPEN_AT_SESSION_START","end_price_semantics":"CLOSE_OF_LAST_15M_BAR_BEFORE_SESSION_END",
            "start_price":ps,"end_price":pe,"return":ret,"direction":dr,"eligibility_status":status,"trainable":train,
            "source_regime":"TWELVE_PRE_2025_04_22"}

def build_v3(x):
    op=dict(zip(x.dt_utc,x.open.astype(float)));cl=dict(zip(x.dt_utc,x.close.astype(float)))
    W=[];S=[];d=LABEL_START
    while d<=LABEL_END:
        if d.weekday()<5:
            p=d-timedelta(days=1)
            W += [make_row(op,cl,d,"WGC_2026_NY3","ASIA",ny(p,18,0),ny(d,3,0)),
                  make_row(op,cl,d,"WGC_2026_NY3","EUROPE",ny(d,3,0),ny(d,8,0)),
                  make_row(op,cl,d,"WGC_2026_NY3","US",ny(d,8,0),ny(d,17,0))]
            S += [make_row(op,cl,d,"SOBTI_5_ET","ASIA_MORNING_LIT",ny(p,21,0),ny(p,23,30)),
                  make_row(op,cl,d,"SOBTI_5_ET","ASIA_AFTERNOON_LIT",ny(d,1,30),ny(d,3,30)),
                  make_row(op,cl,d,"SOBTI_5_ET","EUROPE_LIT",ny(d,3,30),ny(d,8,0)),
                  make_row(op,cl,d,"SOBTI_5_ET","NY_LONDON_LIT",ny(d,8,0),ny(d,14,30)),
                  make_row(op,cl,d,"SOBTI_5_ET","US_LATE_LIT",ny(d,14,30),ny(d,21,0))]
        d+=timedelta(days=1)
    return pd.DataFrame(W),pd.DataFrame(S)

def fetch_gc():
    import databento as db
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:raise RuntimeError("DATABENTO_API_KEY_MISSING")
    c=db.Historical(key);costs={}
    for r in GC_ROLLS:
        costs[r]=float(c.metadata.get_cost(dataset=DATASET,schema=GC_SCHEMA,symbols=[f"GC.{r}.0"],
                                           stype_in="continuous",start=GC_START,end=GC_END))
    total=sum(costs.values())
    if total>GC_COST_CAP:raise RuntimeError(f"GC_COST_CAP:{total}>{GC_COST_CAP}")
    out={}
    for r in GC_ROLLS:
        q=c.timeseries.get_range(dataset=DATASET,schema=GC_SCHEMA,symbols=[f"GC.{r}.0"],stype_in="continuous",
                                 start=GC_START,end=GC_END).to_df().reset_index()
        if "ts_event" not in q.columns and "index" in q.columns:q=q.rename(columns={"index":"ts_event"})
        out[r]=set(pd.to_datetime(q.ts_event,utc=True))
    return out,costs,total

def gc_has(gc,t):return sum(pd.Timestamp(t) in gc[r] for r in GC_ROLLS)>=1
def gc_flags(gc,row):
    s=pd.Timestamp(row.start_utc);e=pd.Timestamp(row.end_utc)
    if row.partition=="WGC_2026_NY3" and row.window=="US":a=s;b=e-pd.Timedelta(hours=1)
    elif row.partition=="SOBTI_5_ET" and row.window=="NY_LONDON_LIT":a=s;b=e.floor("h")
    elif row.partition=="SOBTI_5_ET" and row.window=="US_LATE_LIT":a=s.floor("h");b=e-pd.Timedelta(hours=1)
    else:return None,None,None
    ha=gc_has(gc,a);hb=gc_has(gc,b);return bool(ha),bool(hb),bool(ha and hb)

def venue_enrich(df,gc):
    out=[]
    for _,r in df.iterrows():
        lond=pd.Timestamp(r.start_london).date();sh=pd.Timestamp(r.start_shanghai).date()
        london_open=(lond.weekday()<5 and lond not in UK_BANK_HOLIDAYS)
        sge_open=(sh.weekday()<5 and sh not in SGE_CLOSED)
        gs,ge,gfull=gc_flags(gc,r)
        price=bool(r.trainable);core=price;reasons=[]
        if r.partition=="WGC_2026_NY3":
            if r.window=="EUROPE" and not london_open:core=False;reasons.append("LONDON_BANK_HOLIDAY")
            elif r.window=="US" and gfull is not True:core=False;reasons.append("GC_US_WINDOW_NOT_FULL")
        else:
            if r.window in ("ASIA_MORNING_LIT","ASIA_AFTERNOON_LIT") and not sge_open:
                core=False;reasons.append("SGE_CLOSED")
            elif r.window=="EUROPE_LIT" and not london_open:
                core=False;reasons.append("LONDON_BANK_HOLIDAY")
            elif r.window=="NY_LONDON_LIT":
                if not london_open:core=False;reasons.append("LONDON_BANK_HOLIDAY")
                if gfull is not True:core=False;reasons.append("GC_NYLON_WINDOW_NOT_FULL")
            elif r.window=="US_LATE_LIT" and gfull is not True:
                core=False;reasons.append("GC_USLATE_WINDOW_NOT_FULL")
        if not price:reasons.insert(0,str(r.eligibility_status))
        z=r.to_dict();z.update({"london_business_day":london_open,"sge_business_day":sge_open,
                                "gc_boundary_start_active":gs,"gc_boundary_end_active":ge,"gc_window_full":gfull,
                                "price_trainable":price,"core_trainable":bool(core),
                                "core_exclusion_reason":"|".join(dict.fromkeys(reasons))})
        out.append(z)
    return pd.DataFrame(out)

def expected_grid(s,e):return pd.date_range(s,e-pd.Timedelta(minutes=15),freq="15min",tz="UTC")
def allowed_maintenance(row):
    if row["partition"]!="SOBTI_5_ET" or row["window"]!="US_LATE_LIT":return set()
    s=pd.Timestamp(row["start_utc"]);nyd=s.tz_convert("America/New_York").date()
    base=pd.Timestamp(f"{nyd.isoformat()} 17:00",tz="America/New_York").tz_convert("UTC")
    return {base+pd.Timedelta(minutes=15*k) for k in range(4)}

def final_clean(df,present):
    rows=[]
    for _,r in df.iterrows():
        z=r.to_dict();s=pd.Timestamp(r.start_utc);e=pd.Timestamp(r.end_utc)
        grid=list(expected_grid(s,e));missing=[t for t in grid if t not in present];allowed=allowed_maintenance(r)
        dis=[t for t in missing if t not in allowed]
        path_clean=(len(dis)==0);final=bool(r.core_trainable) and path_clean
        reasons=[]
        if not bool(r.core_trainable):reasons.append(str(r.core_exclusion_reason) or "V4_CORE_EXCLUDED")
        if dis:reasons.append("DISALLOWED_INTERNAL_15M_GAP")
        z.update({"expected_15m_slots":len(grid),"missing_15m_slots":len(missing),
                  "allowed_maintenance_missing_slots":sum(t in allowed for t in missing),
                  "disallowed_missing_slots":len(dis),"disallowed_missing_utc":"|".join(t.isoformat() for t in dis),
                  "path_clean":bool(path_clean),"final_trainable":bool(final),
                  "final_exclusion_reason":"|".join(dict.fromkeys(reasons))})
        rows.append(z)
    return pd.DataFrame(rows)

def cov(df):
    out={}
    for (part,win),g in df.groupby(["partition","window"],sort=True):
        f=g[g.final_trainable]
        out[f"{part}|{win}"]={"rows":len(g),"v3_trainable":int(g.trainable.astype(bool).sum()),
                              "v4_core":int(g.core_trainable.astype(bool).sum()),"v5_final":int(g.final_trainable.sum()),
                              "up_final":int(((g.direction=="UP")&g.final_trainable).sum()),
                              "down_final":int(((g.direction=="DOWN")&g.final_trainable).sum())}
    return out

def main():
    x,req=fetch_xau()
    overlap=overlap_audit(x)
    w3,s3=build_v3(x)
    gc,costs,total=fetch_gc()
    w4=venue_enrich(w3,gc);s4=venue_enrich(s3,gc)
    present=set(x.dt_utc)
    w5=final_clean(w4,present);s5=final_clean(s4,present)
    allq=pd.concat([w5,s5],ignore_index=True)
    if allq.duplicated(["label_date","partition","window"]).any():raise RuntimeError("DUPLICATE_TARGET")
    bad=allq[allq.final_trainable & (~allq.core_trainable.astype(bool)|~allq.path_clean)]
    if len(bad):raise RuntimeError("INVALID_FINAL_ROWS")

    rawp=OUT/"xauusd_15m_utc_2022_with_overlap.csv"
    wp=OUT/"targets_wgc2026_ny3_final_v5_2022.csv";sp=OUT/"targets_sobti5_et_final_v5_2022.csv"
    x.to_csv(rawp,index=False);w5.to_csv(wp,index=False);s5.to_csv(sp,index=False)

    summary={"status":"SESSION_2022_WARMUP_AUTHORITY_PASS","scope":"2022 warm-up only; no 2025 model outcome used",
             "raw":{"rows":len(x),"first":x.dt_utc.min().isoformat(),"last":x.dt_utc.max().isoformat(),
                    "sha256":sha(rawp),"requests":req},
             "overlap_with_existing_authority":overlap,
             "calendar_authority":{"SGE_2022":"official SGE holiday schedule announced 2021-12-21",
                                   "London_2022":"GOV.UK England/Wales bank holidays"},
             "databento_gc":{"dataset":DATASET,"schema":GC_SCHEMA,"rolls":GC_ROLLS,"costs":costs,"total_usd":total},
             "target_rules":{"v3":"exact start OPEN + exact final 15m CLOSE; no fallback; Friday Sobti late-US excluded",
                             "v4":"same venue/calendar gates as 2023-2025",
                             "v5":"full internal 15m path; only registered 17:00-18:00 NY maintenance exception in Sobti late-US"},
             "coverage":cov(allq),"hashes":{"wgc_final":sha(wp),"sobti_final":sha(sp)},
             "model_use":"TRAINING/WARM-UP ONLY. 2022 is not a reported development score period."}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    (OUT/"result.md").write_text(
        "# GOLD SESSION 2022 WARM-UP AUTHORITY\n\n"
        "**Status:** SESSION_2022_WARMUP_AUTHORITY_PASS\n\n"
        f"- Twelve XAU/USD 15m rows: **{len(x):,}**\n"
        f"- Overlap exact OHLC: **{overlap['exact_ohlc_rows']}/{overlap['matched_rows']}**\n"
        "- V3/V4/V5 target rules replicated for 2022.\n"
        "- Use: training/warm-up only; never reported as development score.\n"
    )
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":main()
