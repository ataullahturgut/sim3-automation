from pathlib import Path
import json, time
from datetime import datetime, timezone
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUTJ=AX/"GOLD_H3_HOURLY_HISTORY_DEPTH_PROBE_2026-10-05.json"
OUTM=AX/"GOLD_H3_HOURLY_HISTORY_DEPTH_PROBE_2026-10-05.md"

SYMS={"GC":"GC=F","SI":"SI=F","ZN":"ZN=F","NQ":"NQ=F","CL":"CL=F"}
RANGES={
 "2023":("2022-10-01","2024-01-15"),
 "2024":("2023-10-01","2025-01-15"),
 "2025":("2024-07-01","2026-01-15"),
}
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def epoch(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())

def fetch(sym,start,end):
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(sym,safe='')}"
        params={"period1":epoch(start),"period2":epoch(end),"interval":"1h","events":"history","includeAdjustedClose":"true"}
        try:
            r=S.get(url,params=params,timeout=60)
            item={"host":host,"http":r.status_code,"url":r.url}
            if r.status_code!=200:
                item["error"]=r.text[:500]; last=item; continue
            j=r.json().get("chart",{})
            if j.get("error") or not j.get("result"):
                item["error"]=j.get("error"); last=item; continue
            z=j["result"][0]; ts=z.get("timestamp",[])
            item["rows"]=len(ts)
            if ts:
                item["first_utc"]=datetime.fromtimestamp(ts[0],timezone.utc).isoformat()
                item["last_utc"]=datetime.fromtimestamp(ts[-1],timezone.utc).isoformat()
            return item
        except Exception as e:
            last={"host":host,"error":f"{type(e).__name__}: {e}"}
    return last or {"error":"unknown"}

out={}
for yr,(start,end) in RANGES.items():
    out[yr]={}
    for name,sym in SYMS.items():
        out[yr][name]=fetch(sym,start,end)
        time.sleep(.15)

OUTJ.write_text(json.dumps(out,indent=2)+"\n")
lines=["# GOLD H3 — Hourly History Depth Probe","",
       "Purpose: test whether the original Yahoo hourly futures source can reproduce the missing historical IFBC/LLRS windows without source substitution.","",
       "| Target window | Channel | HTTP | Rows | First UTC | Last UTC | Error |",
       "|---|---|---:|---:|---|---|---|"]
for yr,items in out.items():
    for name,x in items.items():
        err=x.get("error","")
        if isinstance(err,dict): err=json.dumps(err)
        lines.append(f"| {yr} | {name} | {x.get('http','')} | {x.get('rows','')} | {x.get('first_utc','')} | {x.get('last_utc','')} | {str(err).replace('|','/')} |")
OUTM.write_text("\n".join(lines)+"\n")
print(OUTM.read_text())

# trigger: probe-after-workflow-installed
