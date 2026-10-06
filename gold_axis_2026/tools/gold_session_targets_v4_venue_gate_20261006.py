from __future__ import annotations
import hashlib,json,os
from datetime import date
from pathlib import Path
import numpy as np,pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026";OUT=AX/"SESSION_TARGETS_V4_VENUE_GATE_OUT";OUT.mkdir(exist_ok=True)
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FROZEN_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FROZEN_2023_2025.csv"
DATASET="GLBX.MDP3";SCHEMA="ohlcv-1h";ROLLS=["n","v"];START="2022-12-30";END="2026-01-03";COST_CAP=0.40

UK_BANK_HOLIDAYS=set(pd.to_datetime([
 "2023-01-02","2023-04-07","2023-04-10","2023-05-01","2023-05-08","2023-05-29","2023-08-28","2023-12-25","2023-12-26",
 "2024-01-01","2024-03-29","2024-04-01","2024-05-06","2024-05-27","2024-08-26","2024-12-25","2024-12-26",
 "2025-01-01","2025-04-18","2025-04-21","2025-05-05","2025-05-26","2025-08-25","2025-12-25","2025-12-26"
]).date)

SGE_CLOSED=set()
def add_range(a,b):
 for d in pd.date_range(a,b,freq="D"): SGE_CLOSED.add(d.date())
# Official SGE public-holiday schedules; weekends are handled separately by weekday.
for a,b in [
 ("2023-01-02","2023-01-02"),("2023-01-21","2023-01-27"),("2023-04-05","2023-04-05"),("2023-04-29","2023-05-03"),("2023-06-22","2023-06-24"),("2023-09-29","2023-10-06"),
 ("2024-01-01","2024-01-01"),("2024-02-10","2024-02-17"),("2024-04-04","2024-04-06"),("2024-05-01","2024-05-05"),("2024-06-08","2024-06-10"),("2024-09-15","2024-09-17"),("2024-10-01","2024-10-07"),
 ("2025-01-01","2025-01-01"),("2025-01-28","2025-02-04"),("2025-04-04","2025-04-06"),("2025-05-01","2025-05-05"),("2025-05-31","2025-06-02"),("2025-10-01","2025-10-08")
]: add_range(a,b)

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def fetch_gc():
 import databento as db
 key=os.environ.get("DATABENTO_API_KEY","").strip()
 if not key: raise RuntimeError("DATABENTO_API_KEY_MISSING")
 c=db.Historical(key);costs={}
 for r in ROLLS:
  costs[r]=float(c.metadata.get_cost(dataset=DATASET,schema=SCHEMA,symbols=[f"GC.{r}.0"],stype_in="continuous",start=START,end=END))
 total=sum(costs.values())
 if total>COST_CAP: raise RuntimeError(f"COST_CAP:{total}>{COST_CAP}")
 out={}
 for r in ROLLS:
  q=c.timeseries.get_range(dataset=DATASET,schema=SCHEMA,symbols=[f"GC.{r}.0"],stype_in="continuous",start=START,end=END).to_df().reset_index()
  if "ts_event" not in q.columns and "index" in q.columns:q=q.rename(columns={"index":"ts_event"})
  q["ts"]=pd.to_datetime(q.ts_event,utc=True)
  out[r]=set(q.ts)
 return out,costs,total

def gc_has(gc,t):
 return sum(pd.Timestamp(t) in gc[r] for r in ROLLS)>=1

def gc_window_flags(gc,row):
 # Use hourly bar timestamps that establish activity near target start/end.
 s=pd.Timestamp(row.start_utc); e=pd.Timestamp(row.end_utc)
 # For half-hour boundaries, use the containing/adjacent full hour as market-state telemetry.
 sny=s.tz_convert("America/New_York");eny=e.tz_convert("America/New_York")
 if row.partition=="WGC_2026_NY3" and row.window=="US":
  a=s # 08:00 NY
  b=e-pd.Timedelta(hours=1) # 16:00 NY bar ending 17:00
 elif row.partition=="SOBTI_5_ET" and row.window=="NY_LONDON_LIT":
  a=s # 08:00
  b=e.floor("h") # 14:00 bar, activity through 14:30
 elif row.partition=="SOBTI_5_ET" and row.window=="US_LATE_LIT":
  a=s.floor("h") # 14:00 bar contains 14:30 start
  b=e-pd.Timedelta(hours=1) # 20:00 bar ending 21:00
 else:
  return None,None,None
 ha=gc_has(gc,a);hb=gc_has(gc,b)
 return bool(ha),bool(hb),bool(ha and hb)

def enrich(df,gc):
 out=[]
 for _, r in df.iterrows():
  d=pd.Timestamp(r.label_date).date()
  lond=pd.Timestamp(r.start_london).date()
  sh=pd.Timestamp(r.start_shanghai).date()
  london_open=(lond.weekday()<5 and lond not in UK_BANK_HOLIDAYS)
  sge_open=(sh.weekday()<5 and sh not in SGE_CLOSED)
  gs,ge,gfull=gc_window_flags(gc,r)
  price_trainable=bool(r.trainable)
  core=price_trainable
  reasons=[]
  # Venue-specific gates for primary clean research panel.
  if r.partition=="WGC_2026_NY3":
   if r.window=="EUROPE" and not london_open:
    core=False;reasons.append("LONDON_BANK_HOLIDAY")
   elif r.window=="US" and gfull is not True:
    core=False;reasons.append("GC_US_WINDOW_NOT_FULL")
   # WGC Asia is a broad regional window; SGE state is flagged but not a hard gate.
  else:
   if r.window in ("ASIA_MORNING_LIT","ASIA_AFTERNOON_LIT") and not sge_open:
    core=False;reasons.append("SGE_CLOSED")
   elif r.window=="EUROPE_LIT" and not london_open:
    core=False;reasons.append("LONDON_BANK_HOLIDAY")
   elif r.window=="NY_LONDON_LIT":
    if not london_open:
     core=False;reasons.append("LONDON_BANK_HOLIDAY")
    if gfull is not True:
     core=False;reasons.append("GC_NYLON_WINDOW_NOT_FULL")
   elif r.window=="US_LATE_LIT" and gfull is not True:
    core=False;reasons.append("GC_USLATE_WINDOW_NOT_FULL")
  if not price_trainable: reasons.insert(0,str(r.eligibility_status))
  z=r.to_dict()
  z.update({"london_business_day":london_open,"sge_business_day":sge_open,
            "gc_boundary_start_active":gs,"gc_boundary_end_active":ge,"gc_window_full":gfull,
            "price_trainable":price_trainable,"core_trainable":bool(core),
            "core_exclusion_reason":"|".join(dict.fromkeys(reasons))})
  out.append(z)
 return pd.DataFrame(out)

def summ(q):
 out={}
 for (yr,w),g in q.groupby(["year","window"]):
  out[f"{yr}_{w}"]={"rows":int(len(g)),"price_trainable":int(g.price_trainable.sum()),
                    "core_trainable":int(g.core_trainable.sum()),
                    "venue_gate_excluded_from_price_valid":int((g.price_trainable & ~g.core_trainable).sum()),
                    "up_core":int(((g.direction=="UP")&g.core_trainable).sum()),
                    "down_core":int(((g.direction=="DOWN")&g.core_trainable).sum())}
 return out

def main():
 gc,costs,total=fetch_gc()
 w=enrich(pd.read_csv(WGC),gc);s=enrich(pd.read_csv(SOB),gc)
 pw=OUT/"wgc2026_ny3_core.csv";ps=OUT/"sobti5_et_core.csv"
 w.to_csv(pw,index=False);s.to_csv(ps,index=False)
 excl=pd.concat([w[~w.core_trainable],s[~s.core_trainable]],ignore_index=True)
 excl.to_csv(OUT/"excluded_rows.csv",index=False)
 summary={"status":"FROZEN_PREMODEL_VENUE_GATE_V4","databento":{"dataset":DATASET,"schema":SCHEMA,"rolls":ROLLS,"costs":costs,"total_cost_usd":total},
  "calendar_authority":{"SGE":"official annual public-holiday schedules 2023-2025","London":"UK England/Wales bank holidays; LBMA precious metal prices are not published weekends/UK bank holidays",
                        "GC":"actual Databento GLBX.MDP3 hourly bar presence near target boundaries"},
  "policy":{"WGC_ASIA":"SGE state flag only; broad Asia target not hard-gated by one venue",
            "WGC_EUROPE":"London business day required","WGC_US":"GC activity near 08:00 and 17:00 NY boundaries required",
            "SOBTI_ASIA":"SGE business day required","SOBTI_EUROPE":"London business day required",
            "SOBTI_NYLON":"London business day + GC boundary activity required","SOBTI_US_LATE":"GC boundary activity required; Friday already NOT_ELIGIBLE"},
  "coverage":{"WGC_2026_NY3":summ(w),"SOBTI_5_ET":summ(s)},
  "rows_excluded_core_total":int(len(excl)),"hashes":{"wgc_core":sha(pw),"sobti_core":sha(ps)},
  "model_gate":"Primary modelling must assert core_trainable==True. price_trainable-only rows may be used only in declared sensitivity analysis."
 }
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
