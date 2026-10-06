from __future__ import annotations
import hashlib,json
from datetime import date,datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np,pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"; OUT=AX/"SESSION_LABELS_V3_FROZEN_OUT"; OUT.mkdir(exist_ok=True)
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OLD_WGC=AX/"GOLD_SESSION_LABELS_WGC2026_NY3_2023_2025.csv"
OLD_SOB=AX/"GOLD_SESSION_LABELS_SOBTI5_ET_2023_2025.csv"
UTC=ZoneInfo("UTC"); NY=ZoneInfo("America/New_York"); LON=ZoneInfo("Europe/London"); SHA=ZoneInfo("Asia/Shanghai"); IST=ZoneInfo("Europe/Istanbul")
START=date(2023,1,1); END=date(2025,12,31)

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def ny(d,h,m):return pd.Timestamp(datetime(d.year,d.month,d.day,h,m,tzinfo=NY))
def loc(t,z):return t.tz_convert(z).isoformat()
def direc(r):
 if r>0:return "UP"
 if r<0:return "DOWN"
 return "FLAT"

def make_row(op,cl,d,part,win,s,e):
 su=s.tz_convert("UTC");eu=e.tz_convert("UTC"); ep=eu-pd.Timedelta(minutes=15)
 ps=op.get(su); pe=cl.get(ep)
 ret=None if ps is None or pe is None else pe/ps-1
 label=None if ret is None else direc(ret)
 if part=="SOBTI_5_ET" and win=="US_LATE_LIT" and d.weekday()==4:
  status="NOT_ELIGIBLE_WEEKLY_CLOSE_FRIDAY";train=False
 elif ps is None and pe is None:
  status="EXCLUDE_BOTH_BOUNDARIES_MISSING";train=False
 elif ps is None:
  status="EXCLUDE_START_BOUNDARY_MISSING";train=False
 elif pe is None:
  status="EXCLUDE_END_BOUNDARY_MISSING";train=False
 elif label=="FLAT":
  status="EXCLUDE_ZERO_RETURN";train=False
 else:
  status="TRAINABLE";train=True
 return {
  "label_date":d.isoformat(),"year":d.year,"weekday":d.weekday(),"partition":part,"window":win,
  "start_utc":su.isoformat(),"end_utc":eu.isoformat(),"end_price_bar_open_utc":ep.isoformat(),
  "start_ny":loc(su,NY),"end_ny":loc(eu,NY),"start_london":loc(su,LON),"end_london":loc(eu,LON),
  "start_shanghai":loc(su,SHA),"end_shanghai":loc(eu,SHA),"start_istanbul":loc(su,IST),"end_istanbul":loc(eu,IST),
  "start_price_semantics":"OPEN_AT_SESSION_START","end_price_semantics":"CLOSE_OF_LAST_15M_BAR_BEFORE_SESSION_END",
  "start_price":ps,"end_price":pe,"return":ret,"direction":label,
  "eligibility_status":status,"trainable":train,
  "source_regime":"TWELVE_PRE_2025_04_22" if d<date(2025,4,22) else "TWELVE_2025_04_22_PLUS"
 }

def coverage(q):
 out={}
 for (yr,w),g in q.groupby(["year","window"]):
  tr=g[g.trainable]
  out[f"{yr}_{w}"]={"eligible_weekdays":int(len(g)),"trainable":int(len(tr)),"excluded":int((~g.trainable).sum()),
   "trainable_rate":float(g.trainable.mean()),"up":int((tr.direction=="UP").sum()),"down":int((tr.direction=="DOWN").sum()),
   "flat_excluded":int((g.eligibility_status=="EXCLUDE_ZERO_RETURN").sum())}
 return out

def compare(old,new,name):
 o=pd.read_csv(old)[["label_date","partition","window","direction","return"]].rename(columns={"direction":"old_direction","return":"old_return"})
 q=new.merge(o,on=["label_date","partition","window"],how="left")
 q["direction_changed"]=q.trainable & q.old_direction.notna() & (q.direction!=q.old_direction)
 q["abs_return_delta"]=(q["return"]-q.old_return).abs()
 cols=["label_date","partition","window","eligibility_status","direction","old_direction","return","old_return","direction_changed","abs_return_delta"]
 q[cols].to_csv(OUT/f"v2_v3_compare_{name}.csv",index=False)
 return {"comparable_trainable":int((q.trainable&q.old_direction.notna()).sum()),
         "direction_changes":int(q.direction_changed.sum()),
         "max_abs_return_delta":None if q.abs_return_delta.dropna().empty else float(q.abs_return_delta.max())}

def main():
 x=pd.read_csv(RAW);x["dt_utc"]=pd.to_datetime(x.dt_utc,utc=True);x=x.sort_values("dt_utc").drop_duplicates("dt_utc")
 op=dict(zip(x.dt_utc,x.open.astype(float)));cl=dict(zip(x.dt_utc,x.close.astype(float)))
 W=[];S=[];d=START
 while d<=END:
  if d.weekday()<5:
   p=d-timedelta(days=1)
   W += [
    make_row(op,cl,d,"WGC_2026_NY3","ASIA",ny(p,18,0),ny(d,3,0)),
    make_row(op,cl,d,"WGC_2026_NY3","EUROPE",ny(d,3,0),ny(d,8,0)),
    make_row(op,cl,d,"WGC_2026_NY3","US",ny(d,8,0),ny(d,17,0))]
   S += [
    make_row(op,cl,d,"SOBTI_5_ET","ASIA_MORNING_LIT",ny(p,21,0),ny(p,23,30)),
    make_row(op,cl,d,"SOBTI_5_ET","ASIA_AFTERNOON_LIT",ny(d,1,30),ny(d,3,30)),
    make_row(op,cl,d,"SOBTI_5_ET","EUROPE_LIT",ny(d,3,30),ny(d,8,0)),
    make_row(op,cl,d,"SOBTI_5_ET","NY_LONDON_LIT",ny(d,8,0),ny(d,14,30)),
    make_row(op,cl,d,"SOBTI_5_ET","US_LATE_LIT",ny(d,14,30),ny(d,21,0))]
  d+=timedelta(days=1)
 w=pd.DataFrame(W);s=pd.DataFrame(S)
 pw=OUT/"labels_wgc2026_ny3_frozen.csv";ps=OUT/"labels_sobti5_et_frozen.csv"
 w.to_csv(pw,index=False);s.to_csv(ps,index=False)
 cw=compare(OLD_WGC,w,"wgc");cs=compare(OLD_SOB,s,"sobti")
 allq=pd.concat([w,s],ignore_index=True)
 # hard invariants
 dup=int(allq.duplicated(["label_date","partition","window"]).sum())
 bad_clock=0
 for r in allq.itertuples(index=False):
  a=pd.Timestamp(r.start_utc);b=pd.Timestamp(r.end_utc)
  if a>=b or a.minute%15 or b.minute%15:bad_clock+=1
 summary={"status":"FROZEN_PREMODEL_TARGET_PANEL_V3","raw_file":RAW.name,"raw_sha256":sha(RAW),
  "rules":{"start":"exact OPEN at target start; no fallback","end":"exact CLOSE of bar opened T-15; no fallback",
           "friday_sobti_us_late":"NOT_ELIGIBLE irrespective vendor 24x7 quotes","zero_return":"excluded from binary UP/DOWN training"},
  "rows_total":int(len(allq)),"duplicates":dup,"bad_clock_rows":bad_clock,
  "coverage":{"WGC_2026_NY3":coverage(w),"SOBTI_5_ET":coverage(s)},
  "v2_to_v3":{"WGC":cw,"SOBTI":cs},
  "hashes":{"wgc":sha(pw),"sobti":sha(ps)},
  "model_gate":"Only trainable==True rows may be used. eligibility_status must be joined and asserted by model code.",
  "source_regime_flag":"Audit-only metadata; must not be used as predictive feature."
 }
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 (OUT/"result.md").write_text("# GOLD SESSION TARGET PANEL V3 — FROZEN PREMODEL\n\n"
   f"- Raw SHA256: `{summary['raw_sha256']}`\n"
   "- Start: exact session-start 15m bar OPEN.\n"
   "- End: CLOSE of the final 15m bar ending exactly at session end.\n"
   "- No price fallback/imputation.\n"
   "- Sobti Friday US_LATE: NOT_ELIGIBLE.\n"
   "- FLAT: excluded from binary direction training.\n"
   "- Model code must assert trainable==True.\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
