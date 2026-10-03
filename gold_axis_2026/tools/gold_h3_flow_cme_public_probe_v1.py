from __future__ import annotations
import io, json, hashlib
from pathlib import Path
import requests, openpyxl

ROOT=Path(__file__).resolve().parents[2]
OUT_JSON=ROOT/"gold_axis_2026"/"GOLD_H3_FLOW_CME_PUBLIC_PROBE_2026-10-03.json"
OUT_MD=ROOT/"gold_axis_2026"/"GOLD_H3_FLOW_CME_PUBLIC_PROBE_2026-10-03.md"

DATES=["20220103","20240102","20250930","20260930"]
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; FLOW-H3 research probe/1.0)","Accept":"*/*"})

def probe_xlsx(d):
    url=f"https://www.cmegroup.com/ftp/pub/pub/daily_volume/daily_volume_{d}.xlsx"
    r=S.get(url,timeout=60)
    out={"date":d,"url":url,"status":r.status_code,"bytes":len(r.content)}
    if r.status_code!=200:
        out["text_head"]=r.text[:200]
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
                out["tradeDate"]=j.get("tradeDate")
                out["updateTime"]=j.get("updateTime")
        except Exception as e:
            out["json_error"]=repr(e); out["text_head"]=r.text[:1000]
    else:
        out["text_head"]=r.text[:1000]
    return out

def main():
    xlsx=[probe_xlsx(d) for d in DATES]
    js=[]
    for d in DATES:
        js.append(probe_json(d,"F"))
        js.append(probe_json(d,"P"))
    payload={"schema":"FLOW_H3_CME_PUBLIC_PROBE_V1","xlsx":xlsx,"json_endpoint":js}
    OUT_JSON.write_text(json.dumps(payload,indent=2,default=str)+"\n")

    lines=["# FLOW-H3 CME PUBLIC SOURCE PROBE — 2026-10-03","",
           "Purpose: test whether CME public archives can supply official historical GC daily Volume/Open Interest without DataMine entitlement.","",
           "## Public daily_volume XLSX archive","",
           "| Date | HTTP | Bytes | OI text hits | Gold rows |","|---|---:|---:|---:|---:|"]
    for x in xlsx:
        lines.append(f"| {x['date']} | {x['status']} | {x['bytes']} | {len(x.get('open_interest_hits',[]))} | {len(x.get('gold_matches',[]))} |")
    lines+=["","### Workbook evidence",""]
    for x in xlsx:
        lines.append(f"#### {x['date']}")
        lines.append(f"- sheets: {x.get('sheets')}")
        lines.append(f"- contains explicit Open Interest text: {bool(x.get('open_interest_hits'))}")
        for m in x.get("gold_matches",[])[:8]:
            lines.append(f"- {m['sheet']} row {m['row']}: {m['text'][:400]}")
        lines.append("")
    lines+=["## CME product JSON endpoint (Gold product id 437)","",
            "| Date | Flag | HTTP | Bytes | monthData_n | totals present |","|---|---|---:|---:|---:|---|"]
    for j in js:
        lines.append(f"| {j['date']} | {j['flag']} | {j['status']} | {j['bytes']} | {j.get('monthData_n')} | {j.get('totals') is not None} |")
    lines+=["","## Interpretation","",
            "- A public path is acceptable for FLOW only if it contains required GC daily Volume and Open Interest with stable historical coverage and an auditable final/preliminary clock.",
            "- If the XLSX archive is volume-only, it may support a volume-only diagnostic but cannot satisfy frozen FLOW-H3 V1 as preregistered.",
            "- If the JSON endpoint is short-retention only, it cannot backfill 2023-2026 and remains prospective/supporting only.",
            "- No model fitting or threshold selection is performed by this probe."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
