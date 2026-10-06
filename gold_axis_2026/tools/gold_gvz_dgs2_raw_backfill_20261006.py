from __future__ import annotations

import csv
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

GVZ_URL="https://cdn-api.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv"
H15_URL="https://www.federalreserve.gov/datadownload/Output.aspx?filetype=csv&from=&label=include&lastobs=&layout=seriescolumn&rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&to=&type=package"
H15_DGS2_COL="RIFLGFCY02_N.B"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def get(url,name):
    last=None
    for attempt in range(1,6):
        try:
            r=requests.get(url,timeout=(15,60),headers={"User-Agent":"gold-raw-backfill/1.1","Accept":"text/csv,*/*"})
            r.raise_for_status()
            if len(r.content)<100: raise RuntimeError(f"{name}_SHORT_RESPONSE bytes={len(r.content)}")
            return r
        except Exception as e:
            last=e
            if attempt==5: raise RuntimeError(f"{name}_FETCH_FAIL:{e}")
            time.sleep(4*attempt)
    raise last

def fetch_gvz():
    r=get(GVZ_URL,"GVZ")
    q=pd.read_csv(io.BytesIO(r.content))
    q.columns=[str(c).strip().upper() for c in q.columns]
    date_col="DATE" if "DATE" in q.columns else q.columns[0]
    close_col="GVZ" if "GVZ" in q.columns else ("CLOSE" if "CLOSE" in q.columns else None)
    if close_col is None: raise RuntimeError(f"GVZ_VALUE_NOT_FOUND cols={q.columns.tolist()}")
    q=q[[date_col,close_col]].copy()
    q.columns=["date","value"]
    q["date"]=pd.to_datetime(q.date,errors="coerce")
    q["value"]=pd.to_numeric(q.value,errors="coerce")
    q=q.dropna().sort_values("date").drop_duplicates("date",keep="last")
    q=q[(q.date>=pd.Timestamp("2021-01-01"))&(q.date<=pd.Timestamp("2025-12-31"))].reset_index(drop=True)
    p=OUT/"gvzcls_raw.csv";q.to_csv(p,index=False)
    return q,p,{"source":"CBOE_OFFICIAL_GVZ_HISTORICAL","url":GVZ_URL,"bytes":len(r.content)}

def parse_h15(content):
    rows=list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
    header_i=None
    for i,row in enumerate(rows):
        if row and row[0].strip()=="Time Period":
            header_i=i;break
    if header_i is None: raise RuntimeError("H15_TIME_PERIOD_HEADER_NOT_FOUND")
    header=[x.strip() for x in rows[header_i]]
    if H15_DGS2_COL not in header:
        raise RuntimeError(f"H15_DGS2_COL_NOT_FOUND header={header}")
    idx=header.index(H15_DGS2_COL)
    out=[]
    for row in rows[header_i+1:]:
        if len(row)<=idx: continue
        ds=row[0].strip(); val=row[idx].strip()
        if not ds or val in ("","ND","NA","N/A"): continue
        try:
            out.append((pd.Timestamp(ds),float(val)))
        except Exception:
            continue
    return pd.DataFrame(out,columns=["date","value"])

def fetch_dgs2():
    r=get(H15_URL,"H15_DGS2")
    q=parse_h15(r.content)
    q=q[(q.date>=pd.Timestamp("2022-12-20"))&(q.date<=pd.Timestamp("2025-12-31"))].sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)
    if q.empty: raise RuntimeError("DGS2_EMPTY_AFTER_PARSE")
    p=OUT/"dgs2_raw.csv";q.to_csv(p,index=False)
    return q,p,{"source":"FEDERAL_RESERVE_H15_DDP","series":"H15/H15/RIFLGFCY02_N.B","url":H15_URL,"bytes":len(r.content)}

def annual(q):
    return {str(int(y)):{"rows":int(len(g)),"first":str(g.date.min().date()),"last":str(g.date.max().date())}
            for y,g in q.groupby(q.date.dt.year)}

def main():
    gvz,pg,mg=fetch_gvz()
    dgs,pd2,md=fetch_dgs2()
    # Hard coverage gates: the source may skip non-business days, but every requested year must be present.
    for name,q,yrs in [("GVZ",gvz,[2021,2022,2023,2024,2025]),("DGS2",dgs,[2022,2023,2024,2025])]:
        got=set(q.date.dt.year.unique())
        miss=set(yrs)-got
        if miss:raise RuntimeError(f"{name}_MISSING_YEARS:{sorted(miss)}")
    summary={
      "status":"GVZ_DGS2_RAW_BACKFILL_COMPLETE",
      "sources":{
        "GVZ":{
          "rows_valid":int(len(gvz)),"first":str(gvz.date.min().date()),"last":str(gvz.date.max().date()),
          "sha256":sha(pg),"yearly":annual(gvz),"transport":mg,
          "governed_session_use":"FULL_SESSION_D_MINUS_1_ONLY_UNTIL_INTRADAY_PUBLICATION_PROVEN"
        },
        "DGS2":{
          "rows_valid":int(len(dgs)),"first":str(dgs.date.min().date()),"last":str(dgs.date.max().date()),
          "sha256":sha(pd2),"yearly":annual(dgs),"transport":md,
          "governed_session_use":"FULL_SESSION_D_MINUS_1_ONLY; SAME_DAY_AVAILABLE_FOR_LATER_HEAD_ONLY_IF_PUBLICATION_TIME_PROVEN"
        }
      },
      "reason_for_source_change":"FRED graph CSV timed out repeatedly in GitHub Actions; switched to primary official sources: Cboe GVZ history and Federal Reserve H15 DDP.",
      "guardrail":"Raw date/value coverage does not prove same-day source-ready time. Primary full-session models use D-1 completed values until an intraday publication timestamp is separately proven."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
