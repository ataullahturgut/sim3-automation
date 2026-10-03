from __future__ import annotations
import csv, io, json, requests
from pathlib import Path

BASE="https://marketdata.theocc.com/volume-query"
OUT=Path("gold_h3_occ_gld_volume_probe_out")
OUT.mkdir(exist_ok=True)
DATES=["20230103","20241004","20250102","20261002"]

def one(date, side, symbol_type, with_contract):
    p={
        "reportDate":date,
        "format":"csv",
        "volumeQueryType":"O",
        "symbolType":symbol_type,
        "symbol":"GLD",
        "reportType":"D",
        "accountType":"ALL",
        "productKind":"OSTK",
        "porc":side,
    }
    if with_contract:
        p["contractDt"]=date
    r=requests.get(
        BASE,params=p,timeout=60,allow_redirects=True,
        headers={"User-Agent":"Mozilla/5.0 research","Accept":"text/csv,text/plain,*/*"}
    )
    try:
        txt=r.content.decode("utf-8-sig")
    except Exception:
        txt=r.content.decode("latin-1","replace")
    rows=[]
    try:
        for i,row in enumerate(csv.reader(io.StringIO(txt))):
            rows.append(row)
            if i>=20:
                break
    except Exception:
        pass
    return {
        "date":date,"side":side,"symbol_type":symbol_type,"with_contract":with_contract,
        "status":r.status_code,"url":r.url,"bytes":len(r.content),
        "content_type":r.headers.get("content-type"),
        "content_disposition":r.headers.get("content-disposition"),
        "history":[{"status":h.status_code,"location":h.headers.get("location")} for h in r.history],
        "rows":rows,"head":txt[:8000],
    }

res=[]
for d in DATES:
    for side in ["C","P"]:
        for st in ["U","O"]:
            res.append(one(d,side,st,False))
        res.append(one(d,side,"U",True))

(OUT/"probe.json").write_text(json.dumps(res,indent=2))
lines=["# OCC GLD CALL/PUT VOLUME BATCH PROBE",""]
for x in res:
    lines += [
        "## "+x["date"]+" "+x["side"]+" symbolType="+x["symbol_type"]+" contract="+str(x["with_contract"]),
        "- HTTP: "+str(x["status"]),
        "- content-type: "+str(x["content_type"]),
        "- disposition: "+str(x["content_disposition"]),
        "- bytes: "+str(x["bytes"]),
        "- URL: "+x["url"],
        "",
        "### Rows",
    ]
    for row in x["rows"][:20]:
        lines.append("- "+" | ".join(str(v) for v in row))
    lines += ["","### Head",x["head"][:5000],""]
(OUT/"RESULT.md").write_text("\n".join(lines))
print((OUT/"RESULT.md").read_text())
