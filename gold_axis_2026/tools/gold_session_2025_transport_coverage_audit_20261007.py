import json
from pathlib import Path
import pandas as pd

AX=Path(__file__).resolve().parents[1]
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
S14=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
SAGE=AX/"GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
OUT=AX/"SESSION_2025_TRANSPORT_COVERAGE_AUDIT_OUT";OUT.mkdir(exist_ok=True)

def main():
 r=pd.read_csv(RAW,usecols=["dt_utc"]);r["dt_utc"]=pd.to_datetime(r.dt_utc,utc=True)
 t=[]
 for p in [WGC,SOB]:
  q=pd.read_csv(p)
  q=q[q.final_trainable.astype(str).str.lower().eq("true")].copy()
  q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
  q=q[q.start_utc.dt.year.eq(2025)]
  t.append(q)
 t=pd.concat(t,ignore_index=True)
 target=[]
 for (part,win),g in t.groupby(["partition","window"],sort=True):
  target.append({"partition":part,"window":win,"n":len(g),"first":g.start_utc.min().isoformat(),"last":g.start_utc.max().isoformat()})
 pred=[]
 for src,p in [("S14",S14),("SAGE",SAGE)]:
  q=pd.read_csv(p);q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
  for (m,part,win),g in q.groupby(["model","partition","window"],sort=True):
   pred.append({"source":src,"model":m,"partition":part,"window":win,"n":len(g),"first":g.start_utc.min().isoformat(),"last":g.start_utc.max().isoformat()})
 out={"status":"AUDIT_COMPLETE","raw":{"rows":len(r),"first":r.dt_utc.min().isoformat(),"last":r.dt_utc.max().isoformat()},
      "target_2025":target,"prediction_2025":pred}
 (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps(out,indent=2))

if __name__=="__main__":main()
