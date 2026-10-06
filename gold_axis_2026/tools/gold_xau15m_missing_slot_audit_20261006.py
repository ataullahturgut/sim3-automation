from pathlib import Path
import json
import pandas as pd
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"XAU15M_MISSING_SLOT_AUDIT_OUT"; OUT.mkdir(exist_ok=True)

def main():
    x=pd.read_csv(RAW)
    x["dt_utc"]=pd.to_datetime(x.dt_utc,utc=True)
    x=x[(x.dt_utc>=pd.Timestamp("2023-01-01",tz="UTC"))&(x.dt_utc<pd.Timestamp("2026-01-01",tz="UTC"))].copy()
    x["date"]=x.dt_utc.dt.strftime("%Y-%m-%d")
    x["year"]=x.dt_utc.dt.year
    x["hm"]=x.dt_utc.dt.strftime("%H:%M")
    grid=[f"{h:02d}:{m:02d}" for h in range(24) for m in (0,15,30,45)]
    rows=[]
    summary={}
    for yr in [2023,2024,2025]:
        gy=x[x.year==yr]
        patt=Counter()
        examples={}
        for d,g in gy.groupby("date"):
            present=set(g.hm)
            miss=tuple(v for v in grid if v not in present)
            patt[miss]+=1
            examples.setdefault(miss,d)
        top=[]
        for miss,n in patt.most_common(15):
            top.append({"n_dates":n,"example_date":examples[miss],"missing_count":len(miss),"missing_hm":list(miss)})
        summary[str(yr)]={"top_missing_slot_patterns":top}
        for miss,n in patt.items():
            rows.append({"year":yr,"n_dates":n,"example_date":examples[miss],"missing_count":len(miss),"missing_hm":"|".join(miss)})
    pd.DataFrame(rows).sort_values(["year","n_dates"],ascending=[True,False]).to_csv(OUT/"patterns.csv",index=False)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
