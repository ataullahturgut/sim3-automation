from __future__ import annotations
import io, json, requests
import pandas as pd
from pathlib import Path

BASE="https://marketdata.theocc.com/volume-query"
OUT=Path("gold_h3_options_flow_diag_out"); OUT.mkdir(exist_ok=True)
DATES=["20241004","20241007","20250102"]
SIDES=["BOTH","C","P"]

def one(d,side):
    p={
        "reportDate":d,"format":"csv","volumeQueryType":"O","symbolType":"O",
        "symbol":"GLD","reportType":"D","accountType":"ALL","productKind":"OSTK","porc":side
    }
    r=requests.get(BASE,params=p,timeout=60,headers={"User-Agent":"Mozilla/5.0 research","Accept":"text/csv,text/plain,application/octet-stream,*/*"})
    txt=r.content.decode("utf-8-sig",errors="replace")
    item={"date":d,"side":side,"status":r.status_code,"bytes":len(r.content),"url":r.url,
          "content_type":r.headers.get("content-type"),"head":txt[:2000]}
    try:
        df=pd.read_csv(io.StringIO(txt))
        item["columns"]=list(map(str,df.columns))
        item["rows"]=len(df)
        item["porc_values"]=sorted(set(df["porc"].astype(str))) if "porc" in df else []
        item["symbol_values"]=sorted(set(df["symbol"].astype(str)))[:20] if "symbol" in df else []
    except Exception as e:
        item["parse_error"]=repr(e)
    return item

res=[one(d,s) for d in DATES for s in SIDES]
(OUT/"diag.json").write_text(json.dumps(res,indent=2))
lines=["# OPTIONS-FLOW OCC MINIMAL DIAGNOSTIC",""]
for x in res:
    lines += [
        f"## {x['date']} {x['side']}",
        f"- HTTP: {x['status']}",
        f"- bytes: {x['bytes']}",
        f"- columns: {x.get('columns')}",
        f"- rows: {x.get('rows')}",
        f"- porc: {x.get('porc_values')}",
        f"- symbols: {x.get('symbol_values')}",
        f"- parse_error: {x.get('parse_error')}",
        "- head:",
        x["head"],
        ""
    ]
(OUT/"RESULT.md").write_text("\n".join(lines))
print((OUT/"RESULT.md").read_text())
