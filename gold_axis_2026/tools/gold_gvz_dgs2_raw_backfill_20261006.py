from __future__ import annotations

import hashlib
import io
import json
import time
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"GVZ_DGS2_RAW_BACKFILL_OUT"; OUT.mkdir(exist_ok=True)

SPECS={
    "GVZCLS":{
        "url":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS&cosd=2021-01-01&coed=2025-12-31",
        "start_required":"2021-01-01","end_required":"2025-12-31",
        "use_rule":"FULL_SESSION_D_MINUS_1_ONLY_UNTIL_INTRADAY_PUBLICATION_PROVEN"
    },
    "DGS2":{
        "url":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2&cosd=2022-12-20&coed=2025-12-31",
        "start_required":"2022-12-20","end_required":"2025-12-31",
        "use_rule":"FULL_SESSION_D_MINUS_1_ONLY; SAME_DAY_AVAILABLE_FOR_LATER_HEAD_ONLY_IF_PUBLICATION_TIME_PROVEN"
    }
}

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def fetch(name,spec):
    last=None
    r=None
    for attempt in range(1,6):
        try:
            r=requests.get(
                spec["url"],
                timeout=(15,45),
                headers={"User-Agent":"gold-raw-backfill/1.0","Accept":"text/csv"},
            )
            r.raise_for_status()
            if len(r.content)<100:
                raise RuntimeError(f"FRED_SHORT_RESPONSE bytes={len(r.content)}")
            break
        except Exception as e:
            last=e
            if attempt==5:
                raise RuntimeError(f"{name}_FRED_FETCH_FAIL after {attempt} attempts: {e}")
            time.sleep(5*attempt)
    q=pd.read_csv(io.BytesIO(r.content))
    q=q.iloc[:,:2].copy()
    q.columns=["date","value"]
    q["date"]=pd.to_datetime(q.date,errors="coerce")
    q["value"]=pd.to_numeric(q.value,errors="coerce")
    raw_rows=int(len(q))
    null_rows=int(q.value.isna().sum())
    q=q.dropna(subset=["date","value"]).sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)
    p=OUT/f"{name.lower()}_raw.csv"
    q.to_csv(p,index=False)
    return q,p,{"http":r.status_code,"bytes":len(r.content),"raw_rows":raw_rows,"null_value_rows":null_rows}

def main():
    summary={"status":"GVZ_DGS2_RAW_BACKFILL_COMPLETE","sources":{}}
    for name,spec in SPECS.items():
        q,p,meta=fetch(name,spec)
        yearly={}
        for yr,g in q.groupby(q.date.dt.year):
            yearly[str(int(yr))]={"rows":int(len(g)),"first":str(g.date.min().date()),"last":str(g.date.max().date())}
        summary["sources"][name]={
            "url":spec["url"],
            "rows_valid":int(len(q)),
            "first":str(q.date.min().date()),
            "last":str(q.date.max().date()),
            "sha256":sha(p),
            "yearly":yearly,
            "transport":meta,
            "governed_session_use":spec["use_rule"],
        }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
