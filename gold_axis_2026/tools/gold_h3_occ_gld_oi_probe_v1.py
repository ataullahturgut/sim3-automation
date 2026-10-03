from __future__ import annotations
import csv, io, json, requests
from pathlib import Path

BASE="https://marketdata.theocc.com/daily-open-interest"
DATES=["01/03/2023","10/04/2024","01/02/2025","10/02/2026"]
OUT=Path("gold_h3_occ_gld_oi_probe_out")
OUT.mkdir(exist_ok=True)

def inspect(date):
    r=requests.get(
        BASE,
        params={"reportDate":date,"action":"download","format":"csv"},
        timeout=120,
        headers={"User-Agent":"Mozilla/5.0 research","Accept":"text/csv,text/plain,*/*"}
    )
    try:
        txt=r.content.decode("utf-8-sig")
    except Exception:
        txt=r.content.decode("latin-1","replace")
    hits=[]
    header=[]
    err=None
    try:
        rd=csv.reader(io.StringIO(txt))
        for i,row in enumerate(rd):
            if i==0:
                header=row
            joined="|".join(str(v) for v in row).upper()
            if "GLD" in joined:
                hits.append(row)
                if len(hits)>=200:
                    break
    except Exception as e:
        err=repr(e)
    return {
        "date":date,"status":r.status_code,"url":r.url,
        "bytes":len(r.content),"content_type":r.headers.get("content-type"),
        "content_disposition":r.headers.get("content-disposition"),
        "header":header,"gld_hits":hits,"csv_error":err,
        "head":txt[:6000],
    }

res=[inspect(d) for d in DATES]
(OUT/"probe.json").write_text(json.dumps(res,indent=2))
lines=["# OCC GLD DAILY OPEN INTEREST PROBE",""]
for x in res:
    lines += [
        "## "+x["date"],
        "- HTTP: "+str(x["status"]),
        "- bytes: "+str(x["bytes"]),
        "- content-type: "+str(x["content_type"]),
        "- disposition: "+str(x["content_disposition"]),
        "- header: "+json.dumps(x["header"]),
        "- GLD hits: "+str(len(x["gld_hits"])),
        "",
        "### GLD rows",
    ]
    for row in x["gld_hits"][:100]:
        lines.append("- "+" | ".join(str(v) for v in row))
    lines += ["","### Head",x["head"],""]
(OUT/"RESULT.md").write_text("\n".join(lines))
print((OUT/"RESULT.md").read_text())
