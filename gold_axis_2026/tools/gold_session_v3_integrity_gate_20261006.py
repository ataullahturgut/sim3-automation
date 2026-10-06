from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
FILES=[
 AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FROZEN_2023_2025.csv",
 AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FROZEN_2023_2025.csv",
]
OUT=AX/"SESSION_V3_INTEGRITY_GATE_OUT"; OUT.mkdir(exist_ok=True)
NY=ZoneInfo("America/New_York")

CLOCKS={
 ("WGC_2026_NY3","ASIA"):(18,0,3,0,True),
 ("WGC_2026_NY3","EUROPE"):(3,0,8,0,False),
 ("WGC_2026_NY3","US"):(8,0,17,0,False),
 ("SOBTI_5_ET","ASIA_MORNING_LIT"):(21,0,23,30,True),
 ("SOBTI_5_ET","ASIA_AFTERNOON_LIT"):(1,30,3,30,False),
 ("SOBTI_5_ET","EUROPE_LIT"):(3,30,8,0,False),
 ("SOBTI_5_ET","NY_LONDON_LIT"):(8,0,14,30,False),
 ("SOBTI_5_ET","US_LATE_LIT"):(14,30,21,0,False),
}

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def at(d,h,m):
 return pd.Timestamp(datetime(d.year,d.month,d.day,h,m,tzinfo=NY))

def sign(r):
 return "UP" if r>0 else ("DOWN" if r<0 else "FLAT")

def main():
 raw=pd.read_csv(RAW); raw["dt_utc"]=pd.to_datetime(raw.dt_utc,utc=True)
 raw=raw.sort_values("dt_utc")
 duplicate_raw=int(raw.duplicated("dt_utc").sum())
 raw=raw.drop_duplicates("dt_utc",keep="last")
 op=dict(zip(raw.dt_utc,raw.open.astype(float)))
 cl=dict(zip(raw.dt_utc,raw.close.astype(float)))
 rows=[]; errs=[]; missing_ts=set()
 for f in FILES:
  q=pd.read_csv(f)
  for idx,r in q.iterrows():
   d=pd.Timestamp(r.label_date).date()
   sh,sm,eh,em,prev=CLOCKS[(r.partition,r.window)]
   sd=d-timedelta(days=1) if prev else d
   ed=sd if (r.partition=="SOBTI_5_ET" and r.window=="ASIA_MORNING_LIT") else d
   s=at(sd,sh,sm).tz_convert("UTC")
   e=at(ed,eh,em).tz_convert("UTC")
   ep=e-pd.Timedelta(minutes=15)
   ps=op.get(s); pe=cl.get(ep)
   ret=None if ps is None or pe is None else pe/ps-1
   dire=None if ret is None else sign(ret)
   expected_status=(
    "NOT_ELIGIBLE_WEEKLY_CLOSE_FRIDAY"
    if r.partition=="SOBTI_5_ET" and r.window=="US_LATE_LIT" and d.weekday()==4
    else "EXCLUDE_BOTH_BOUNDARIES_MISSING" if ps is None and pe is None
    else "EXCLUDE_START_BOUNDARY_MISSING" if ps is None
    else "EXCLUDE_END_BOUNDARY_MISSING" if pe is None
    else "EXCLUDE_ZERO_RETURN" if dire=="FLAT"
    else "TRAINABLE"
   )
   expected_train=expected_status=="TRAINABLE"
   er=[]
   if d.weekday()>=5: er.append("NON_WEEKDAY_LABEL")
   if pd.Timestamp(r.start_utc)!=s: er.append("START_CLOCK")
   if pd.Timestamp(r.end_utc)!=e: er.append("END_CLOCK")
   if pd.Timestamp(r.end_price_bar_open_utc)!=ep: er.append("END_BAR_CLOCK")
   if bool(r.trainable)!=expected_train: er.append("TRAINABLE_FLAG")
   if r.eligibility_status!=expected_status: er.append("ELIGIBILITY_STATUS")
   if ps is None:
    missing_ts.add(s.isoformat())
    if not pd.isna(r.start_price):er.append("START_SHOULD_NULL")
   elif not np.isclose(float(r.start_price),ps,rtol=0,atol=1e-10):er.append("START_PRICE")
   if pe is None:
    missing_ts.add(ep.isoformat())
    if not pd.isna(r.end_price):er.append("END_SHOULD_NULL")
   elif not np.isclose(float(r.end_price),pe,rtol=0,atol=1e-10):er.append("END_PRICE")
   if ret is None:
    if not pd.isna(r["return"]):er.append("RETURN_SHOULD_NULL")
   else:
    if not np.isclose(float(r["return"]),ret,rtol=0,atol=1e-12):er.append("RETURN")
    if r.direction!=dire:er.append("DIRECTION")
   # internal bar telemetry; not used to alter label
   inside=raw[(raw.dt_utc>=s)&(raw.dt_utc<e)]
   expected_slots=int(round((e-s).total_seconds()/900))
   internal_n=int(len(inside)); coverage=internal_n/expected_slots if expected_slots else 1.0
   rows.append({"file":f.name,"label_date":r.label_date,"partition":r.partition,"window":r.window,
                "trainable":bool(r.trainable),"eligibility_status":r.eligibility_status,
                "internal_bars":internal_n,"expected_slots":expected_slots,"internal_coverage":coverage,
                "integrity_errors":"|".join(er)})
   if er:errs.append({"file":f.name,"row":int(idx),"date":r.label_date,"partition":r.partition,"window":r.window,"errors":er})
 a=pd.DataFrame(rows);a.to_csv(OUT/"row_audit.csv",index=False)
 tr=a[a.trainable]
 low=tr[tr.internal_coverage<0.75].copy();low.to_csv(OUT/"trainable_low_internal_coverage.csv",index=False)
 summ={
  "status":"V3_FROZEN_PREMODEL_INTEGRITY_GATE",
  "raw_sha256":sha(RAW),
  "file_sha256":{f.name:sha(f) for f in FILES},
  "raw_duplicate_timestamps":duplicate_raw,
  "rows":int(len(a)),
  "integrity_error_rows":int(len(errs)),
  "integrity_errors_sample":errs[:50],
  "duplicate_keys":int(pd.concat([pd.read_csv(f) for f in FILES]).duplicated(["label_date","partition","window"]).sum()),
  "trainable_rows":int(tr.shape[0]),
  "nontrainable_rows":int((~a.trainable).sum()),
  "trainable_internal_coverage_below_75pct":int(len(low)),
  "min_internal_coverage_trainable":None if tr.empty else float(tr.internal_coverage.min()),
  "missing_boundary_timestamps_unique":len(missing_ts),
  "missing_boundary_timestamps_sample":sorted(missing_ts)[:100],
  "pass":bool(len(errs)==0 and duplicate_raw==0),
  "note":"Internal path coverage is telemetry only; V3 direction label depends only on exact start OPEN and exact final bar CLOSE."
 }
 (OUT/"summary.json").write_text(json.dumps(summ,indent=2)+"\n")
 print(json.dumps(summ,indent=2))
if __name__=="__main__":main()
