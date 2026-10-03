from __future__ import annotations
import csv, io, json, re, requests
from pathlib import Path

DATES = ["20230103","20240102","20261002"]
BASE = "https://www.cmegroup.com/ftp/fprf/csv/cmeg.cme.fut.prf.{date}.csv"
OUT = Path("gold_h3_flow_oi_salvage_out"); OUT.mkdir(exist_ok=True)

def fetch(date):
    url = BASE.format(date=date)
    r = requests.get(url, timeout=60, headers={"User-Agent":"Mozilla/5.0 (compatible; research; +https://github.com/ataullahturgut/sim3-automation)"})
    item = {"date":date,"url":url,"status":r.status_code,"bytes":len(r.content),"content_type":r.headers.get("content-type")}
    if r.status_code != 200:
        item["head"] = r.text[:1000]
        return item
    txt = r.text
    item["head"] = txt[:1000]
    rd = csv.reader(io.StringIO(txt))
    rows = list(rd)
    item["row_count"] = len(rows)
    item["header"] = rows[0] if rows else []
    header_l = [str(x).lower() for x in item["header"]]
    item["oi_cols"] = [c for c in item["header"] if "open" in c.lower() or "interest" in c.lower()]
    item["vol_cols"] = [c for c in item["header"] if "volume" in c.lower()]
    hits=[]
    for row in rows[1:]:
        joined="|".join(str(x) for x in row)
        low=joined.lower()
        if re.search(r"(^|\W)gc(\W|$)", low) or "gold" in low:
            hits.append(row)
            if len(hits)>=50: break
    item["gold_hits"]=hits
    return item

res=[fetch(d) for d in DATES]
(OUT/"probe.json").write_text(json.dumps(res,indent=2))
lines=["# CME FPRF GC OPEN-INTEREST SALVAGE PROBE",""]
for x in res:
    lines += [f"## {x['date']}",f"- HTTP: {x['status']}",f"- bytes: {x['bytes']}",f"- content-type: {x.get('content_type')}"]
    if x["status"]==200:
        lines += [f"- rows: {x.get('row_count')}",f"- header: {x.get('header')}",f"- OI-like columns: {x.get('oi_cols')}",f"- volume-like columns: {x.get('vol_cols')}","", "### Gold/GC sample rows"]
        for row in x.get("gold_hits",[])[:20]:
            lines.append("- " + " | ".join(str(v) for v in row))
    else:
        lines += ["- head: " + x.get("head","").replace("\n"," ")[:500]]
    lines.append("")
(OUT/"RESULT.md").write_text("\n".join(lines))
print((OUT/"RESULT.md").read_text())
