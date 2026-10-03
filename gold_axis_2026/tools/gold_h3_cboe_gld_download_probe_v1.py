from __future__ import annotations
import csv, io, json, requests
from pathlib import Path

BASE = "https://www.cboe.com/us/options/market_statistics/historical_data/download/class/"
OUT = Path("gold_h3_cboe_gld_download_probe_out")
OUT.mkdir(exist_ok=True)

COMMON = {
    "symbolType":"underlying",
    "symbol":"GLD",
    "startDate":"2023-01-03",
    "endDate":"2023-01-10",
}

CASES = [
    ("volume_all", {
        **COMMON,
        "reportType":"volume",
        "volumeType":"sum",
        "volumeAggType":"daily",
        "exchanges":["CBOE","BATS","C2","EDGX"],
    }),
    ("volume_cboe", {
        **COMMON,
        "reportType":"volume",
        "volumeType":"sum",
        "volumeAggType":"daily",
        "exchanges":["CBOE"],
    }),
    ("oi_underlying", {
        **COMMON,
        "reportType":"oi",
        "volumeType":"sum",
        "volumeAggType":"daily",
    }),
]

HEADERS = {
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept":"text/csv,application/csv,text/plain,application/octet-stream,*/*",
    "Referer":"https://www.cboe.com/us/options/market_statistics/historical_data/",
}

def inspect(name, params):
    s=requests.Session()
    q=[]
    for k,v in params.items():
        if isinstance(v,list):
            for x in v:
                q.append((k,x))
        else:
            q.append((k,v))
    r=s.get(BASE,params=q,headers=HEADERS,timeout=90,allow_redirects=True)
    item={
        "name":name,
        "requested_url":r.request.url,
        "status":r.status_code,
        "final_url":r.url,
        "history":[{"status":h.status_code,"url":h.url,"location":h.headers.get("location")} for h in r.history],
        "content_type":r.headers.get("content-type"),
        "content_disposition":r.headers.get("content-disposition"),
        "bytes":len(r.content),
    }
    raw=r.content
    try:
        txt=raw.decode("utf-8-sig")
    except Exception:
        txt=raw.decode("latin-1","replace")
    item["text_head"]=txt[:12000]
    rows=[]
    try:
        rd=csv.reader(io.StringIO(txt))
        for i,row in enumerate(rd):
            rows.append(row)
            if i>=25:
                break
    except Exception as e:
        item["csv_error"]=repr(e)
    item["rows"]=rows
    return item

res=[inspect(name,p) for name,p in CASES]
(OUT/"probe.json").write_text(json.dumps(res,indent=2))

lines=["# CBOE GLD HISTORICAL OPTIONS DOWNLOAD PAYLOAD PROBE",""]
for x in res:
    lines += [
        "## "+x["name"],
        "- HTTP: "+str(x["status"]),
        "- final URL: "+x["final_url"],
        "- content-type: "+str(x["content_type"]),
        "- content-disposition: "+str(x["content_disposition"]),
        "- bytes: "+str(x["bytes"]),
        "- redirects: "+json.dumps(x["history"]),
        "",
        "### Parsed first rows",
        "",
    ]
    for row in x.get("rows",[])[:25]:
        lines.append("- " + " | ".join(str(v) for v in row))
    lines += ["","### Text head","",x.get("text_head","")[:12000],""]

(OUT/"RESULT.md").write_text("\n".join(lines))
print((OUT/"RESULT.md").read_text())
