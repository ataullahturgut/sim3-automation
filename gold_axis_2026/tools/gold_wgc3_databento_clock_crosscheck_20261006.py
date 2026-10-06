from __future__ import annotations
import json, os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
LAB=AX/"GOLD_SESSION_LABELS_WGC2026_NY3_2023_2025.csv"
OUT=AX/"WGC3_DATABENTO_CLOCK_CROSSCHECK_OUT"; OUT.mkdir(exist_ok=True)

DATASET="GLBX.MDP3"; SCHEMA="ohlcv-1h"
START="2022-12-30"; END="2026-01-03"
ROLLS=["c","n","v"]; MAX_COST=1.60
NY=ZoneInfo("America/New_York")

def fetch():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key: raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)
    costs={}
    for roll in ROLLS:
        sym=f"GC.{roll}.0"
        costs[roll]=float(client.metadata.get_cost(dataset=DATASET,schema=SCHEMA,symbols=[sym],stype_in="continuous",start=START,end=END))
    total=sum(costs.values())
    if total>MAX_COST: raise RuntimeError(f"COST_CAP:{total}>{MAX_COST}")
    out={}
    for roll in ROLLS:
        sym=f"GC.{roll}.0"
        q=client.timeseries.get_range(dataset=DATASET,schema=SCHEMA,symbols=[sym],stype_in="continuous",start=START,end=END).to_df().reset_index()
        if "ts_event" not in q.columns and "index" in q.columns:q=q.rename(columns={"index":"ts_event"})
        q["ts"]=pd.to_datetime(q.ts_event,utc=True)
        for c in ["open","close"]: q[c]=pd.to_numeric(q[c],errors="coerce")
        q=q[np.isfinite(q.open)&np.isfinite(q.close)&(q.open>0)&(q.close>0)].sort_values("ts").drop_duplicates("ts")
        out[roll]=q[["ts","open","close","instrument_id"]].copy()
    return out,costs,float(total)

def maps(q):
    return dict(zip(q.ts,q.open.astype(float))),dict(zip(q.ts,q.close.astype(float)))

def price_at(mopen,mclose,t,which):
    u=t.tz_convert("UTC")
    if which=="START":
        if u in mopen:return mopen[u],"OPEN_AT_T"
        return None,"MISSING"
    # end boundary: first prefer open at T; otherwise close of previous 1h bar ending at T.
    if u in mopen:return mopen[u],"OPEN_AT_T"
    p=u-pd.Timedelta(hours=1)
    if p in mclose:return mclose[p],"PREV_1H_CLOSE_AT_T"
    return None,"MISSING"

def sign(r):
    if r is None:return None
    return 1 if r>0 else (-1 if r<0 else 0)

def majority(vals):
    v=[x for x in vals if x is not None and x!=0]
    if len(v)<2:return None
    if v.count(1)>=2:return 1
    if v.count(-1)>=2:return -1
    return None

def main():
    labs=pd.read_csv(LAB)
    labs=labs[labs.coverage=="PASS"].copy()
    labs["start_utc"]=pd.to_datetime(labs.start_utc,utc=True)
    labs["end_utc"]=pd.to_datetime(labs.end_utc,utc=True)
    labs=labs.rename(columns={"return":"spot_return"})
    groups,costs,total=fetch()
    mm={r:maps(q) for r,q in groups.items()}

    rows=[]
    for z in labs.itertuples(index=False):
        dirs=[]; row={"label_date":z.label_date,"year":int(z.year),"window":z.window,"spot_direction":z.direction,"spot_return":float(z.spot_return)}
        for roll in ROLLS:
            mo,mc=mm[roll]
            ps,ms=price_at(mo,mc,z.start_utc,"START")
            pe,me=price_at(mo,mc,z.end_utc,"END")
            ret=None if ps is None or pe is None else pe/ps-1
            d=sign(ret);dirs.append(d)
            row[f"gc_{roll}_start_method"]=ms;row[f"gc_{roll}_end_method"]=me
            row[f"gc_{roll}_ret"]=ret;row[f"gc_{roll}_dir"]=d
        md=majority(dirs)
        sd=1 if z.direction=="UP" else (-1 if z.direction=="DOWN" else 0)
        row["gc_majority_dir"]=md
        row["direction_agree"]=None if md is None or sd==0 else bool(md==sd)
        row["roll_unanimous"]=bool(len([d for d in dirs if d is not None])==3 and len(set(dirs))==1)
        rows.append(row)
    z=pd.DataFrame(rows)
    z.to_csv(OUT/"rows.csv",index=False)

    summary={}
    for (yr,w),g in z.groupby(["year","window"]):
        q=g[g.direction_agree.notna()]
        summary[f"{yr}_{w}"]={
          "spot_rows":int(len(g)),
          "gc_comparable":int(len(q)),
          "agreement":None if q.empty else float(q.direction_agree.mean()),
          "gc_roll_unanimous_share":float(g.roll_unanimous.mean())
        }
    # pre/post Twelve source regime diagnostic
    z["date"]=pd.to_datetime(z.label_date)
    for tag,mask in [
        ("PRE_2025_04_22",z.date<pd.Timestamp("2025-04-22")),
        ("POST_2025_04_22",z.date>=pd.Timestamp("2025-04-22"))
    ]:
        q=z[mask & z.direction_agree.notna()]
        summary[tag]={
          "n":int(len(q)),
          "agreement":None if q.empty else float(q.direction_agree.mean())
        }

    out={
      "status":"INDEPENDENT_WGC3_CLOCK_DIRECTION_CROSSCHECK",
      "dataset":DATASET,"schema":SCHEMA,"symbols":[f"GC.{r}.0" for r in ROLLS],
      "estimated_cost_usd":total,"costs":costs,"cost_cap_usd":MAX_COST,
      "purpose":"Clock/date/source-regime validation only; GC futures does not replace XAU spot labels.",
      "summary":summary
    }
    (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
