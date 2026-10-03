from __future__ import annotations
import io, json, hashlib
from pathlib import Path
import requests, openpyxl

ROOT=Path(__file__).resolve().parents[2]
OUT_JSON=ROOT/"gold_axis_2026"/"GOLD_H3_FLOW_CME_PUBLIC_PROBE_2026-10-03.json"
OUT_MD=ROOT/"gold_axis_2026"/"GOLD_H3_FLOW_CME_PUBLIC_PROBE_2026-10-03.md"

DATES=["20220103","20240102","20250930","20260930"]
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; FLOW-H3 research probe/1.1)","Accept":"*/*"})

def probe_xlsx(d):
    url=f"https://www.cmegroup.com/ftp/pub/pub/daily_volume/daily_volume_{d}.xlsx"
    r=S.get(url,timeout=60)
    out={"date":d,"url":url,"status":r.status_code,"bytes":len(r.content)}
    if r.status_code!=200:
        out["text_head"]=r.text[:400]
        return out
    out["sha256"]=hashlib.sha256(r.content).hexdigest()
    try:
        wb=openpyxl.load_workbook(io.BytesIO(r.content),read_only=True,data_only=True)
        out["sheets"]=wb.sheetnames
        matches=[]; oi_hits=[]
        for ws in wb.worksheets:
            for ri,row in enumerate(ws.iter_rows(values_only=True),start=1):
                vals=["" if v is None else str(v) for v in row]
                joined=" | ".join(vals); low=joined.lower()
                if "open interest" in low or "open_int" in low:
                    oi_hits.append({"sheet":ws.title,"row":ri,"text":joined[:1000]})
                if ("gold" in low or "comex" in low) and len(joined.strip())>0:
                    matches.append({"sheet":ws.title,"row":ri,"text":joined[:1200]})
        out["open_interest_hits"]=oi_hits[:20]
        out["gold_matches"]=matches[:30]
    except Exception as e:
        out["parse_error"]=repr(e)
    return out

def probe_json(d,flag):
    url=f"https://www.cmegroup.com/CmeWS/mvc/Volume/Details/F/437/{d}/{flag}"
    params={"tradeDate":d,"pageSize":"50"}
    r=S.get(url,params=params,timeout=60,headers={"Accept":"application/json","User-Agent":S.headers["User-Agent"]})
    out={"date":d,"url":r.url,"status":r.status_code,"bytes":len(r.content),"flag":flag}
    if r.status_code==200:
        try:
            j=r.json()
            out["top_keys"]=list(j.keys()) if isinstance(j,dict) else None
            if isinstance(j,dict):
                out["totals"]=j.get("totals")
                md=j.get("monthData")
                out["monthData_n"]=len(md) if isinstance(md,list) else None
                out["monthData_head"]=md[:3] if isinstance(md,list) else md
                out["tradeDate"]=j.get("tradeDate"); out["updateTime"]=j.get("updateTime")
        except Exception as e:
            out["json_error"]=repr(e); out["text_head"]=r.text[:1000]
    else:
        out["text_head"]=r.text[:1000]
    return out

def probe_continuous(provider,base,dataset,start,end):
    url=f"{base}/{dataset}.csv"
    params={"start_date":start,"end_date":end,"order":"asc"}
    r=S.get(url,params=params,timeout=60,headers={"Accept":"text/csv,*/*","User-Agent":S.headers["User-Agent"]})
    out={"provider":provider,"dataset":dataset,"url":r.url,"status":r.status_code,"bytes":len(r.content)}
    txt=r.text
    out["text_head"]=txt[:2000]
    if r.status_code==200:
        lines=[x for x in txt.splitlines() if x.strip()]
        out["line_n"]=len(lines)
        out["header"]=lines[0] if lines else ""
        out["rows_head"]=lines[1:6]
        low=out["header"].lower()
        out["has_volume"]="volume" in low
        out["has_open_interest"]="open interest" in low
    return out

def main():
    xlsx=[probe_xlsx(d) for d in DATES]
    js=[]
    for d in DATES:
        js.append(probe_json(d,"F")); js.append(probe_json(d,"P"))
    alt=[]
    for dataset in ["CHRIS/CME_GC1","CHRIS/CME_GC2","CHRIS/CME_GC3"]:
        alt.append(probe_continuous("NASDAQ_DATA_LINK","https://data.nasdaq.com/api/v3/datasets",dataset,"2023-01-03","2023-01-10"))
        alt.append(probe_continuous("QUANDL_LEGACY","https://www.quandl.com/api/v3/datasets",dataset,"2023-01-03","2023-01-10"))
    payload={"schema":"FLOW_H3_CME_PUBLIC_PROBE_V1_1","xlsx":xlsx,"json_endpoint":js,"continuous_alternatives":alt}
    OUT_JSON.write_text(json.dumps(payload,indent=2,default=str)+"\n")

    lines=["# FLOW-H3 CME / CONTINUOUS SOURCE PROBE — 2026-10-03","",
           "Purpose: test official CME public paths first, then separately test continuous-futures sources that expose both Volume and Open Interest.","",
           "## CME public daily_volume XLSX","",
           "| Date | HTTP | Bytes | OI text hits | Gold rows |","|---|---:|---:|---:|---:|"]
    for x in xlsx:
        lines.append(f"| {x['date']} | {x['status']} | {x['bytes']} | {len(x.get('open_interest_hits',[]))} | {len(x.get('gold_matches',[]))} |")
    lines+=["","## CME Gold product JSON endpoint","",
            "| Date | Flag | HTTP | Bytes | monthData_n | totals present |","|---|---|---:|---:|---:|---|"]
    for j in js:
        lines.append(f"| {j['date']} | {j['flag']} | {j['status']} | {j['bytes']} | {j.get('monthData_n')} | {j.get('totals') is not None} |")
    lines+=["","## Continuous-futures alternative access probe","",
            "| Provider | Dataset | HTTP | Rows | Volume col | OI col |","|---|---|---:|---:|---|---|"]
    for a in alt:
        lines.append(f"| {a['provider']} | {a['dataset']} | {a['status']} | {a.get('line_n')} | {a.get('has_volume')} | {a.get('has_open_interest')} |")
    lines+=["","### Alternative response heads",""]
    for a in alt:
        lines.append(f"#### {a['provider']} {a['dataset']}")
        lines.append(f"- HTTP {a['status']}, bytes {a['bytes']}")
        lines.append(f"- head: {a.get('text_head','')[:800].replace(chr(10),' | ')}")
        lines.append("")
    lines+=["## Governance interpretation","",
            "- Direct CME automated public access returning 403 is not bypassed.",
            "- Nasdaq Data Link / Quandl continuous contracts are not silently treated as the official CME aggregate-product VOI source.",
            "- If an alternative is accessible and includes Volume plus Open Interest, it can only proceed under a separately named FLOW successor after source-semantics and roll/contract mapping are frozen.",
            "- No outcome-based model fitting or threshold selection is performed in this probe."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
