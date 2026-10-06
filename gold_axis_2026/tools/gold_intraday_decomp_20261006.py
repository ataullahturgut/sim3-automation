from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"INTRADAY_DECOMP_OUT"; OUT.mkdir(exist_ok=True)
SIG=AX/"GOLD_EXECUTION_CHANNEL_AUDIT_SIGNAL_PANEL_2026-10-06.csv"

def fetch():
    key=os.environ["TWELVE_DATA_API_KEY"]
    p={"symbol":"XAU/USD","interval":"15min","timezone":"America/New_York","order":"ASC",
       "outputsize":5000,"apikey":key,"start_date":"2026-08-03 00:00:00","end_date":"2026-09-25 23:59:59"}
    j=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90).json()
    rows=[]
    for z in j.get("values",[]):
        try: rows.append((pd.Timestamp(z["datetime"]),float(z["open"]),float(z["close"])))
        except: pass
    return pd.DataFrame(rows,columns=["dt","open","close"]).sort_values("dt")

def comp(rs): return float(np.prod(1+np.array(rs))-1)

x=fetch(); x["date"]=x.dt.dt.strftime("%Y-%m-%d"); x["hm"]=x.dt.dt.strftime("%H:%M")
by={(r.date,r.hm):r for r in x.itertuples(index=False)}
days=pd.read_csv(SIG).query("cpg_up==True").date.astype(str).tolist()
all_dates=sorted(x.date.unique())
prev={all_dates[i]:all_dates[i-1] for i in range(1,len(all_dates))}
rows=[]
for d in days:
    pd0=prev[d]
    a=by.get((pd0,"16:00")); b=by.get((d,"08:45")); c=by.get((d,"11:15")); e=by.get((d,"16:00"))
    if None in (a,b,c,e): continue
    r1=b.open/a.open-1; r2=c.open/b.open-1; r3=e.open/c.open-1; rt=e.open/a.open-1
    rows.append({"date":d,"prev_date":pd0,"prev1600_to_0845":r1,"0845_to_1115":r2,"1115_to_1600":r3,"prev1600_to_1600":rt})
df=pd.DataFrame(rows)
summary={k:comp(df[k]) for k in ["prev1600_to_0845","0845_to_1115","1115_to_1600","prev1600_to_1600"]}
summary["n"]=len(df)
(OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
df.to_csv(OUT/"details.csv",index=False)
print(json.dumps(summary,indent=2))
