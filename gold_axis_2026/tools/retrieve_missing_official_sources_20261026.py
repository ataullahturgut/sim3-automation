"""Only official issuer/archive acquisition. No Neon writes, no trading or model fit.

All downloads are independently validated and recorded with URL and SHA256.
BlackRock iShares 'Data Download Excel' sometimes comes as SpreadsheetML XML;
'not PK XLSX' does NOT imply a failure. NAV history != silver fund holdings.
Historical observations != first-publication as-of times.
"""
import csv,datetime as dt,hashlib,io,json,os,re,sys,time,zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from xml.etree import ElementTree as ET
import requests

ROOT=Path(os.environ.get("OUTDIR","/tmp/gold_official_retrieval_20261026"))
ROOT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36","Accept":"application/vnd.ms-excel,application/xml,text/xml,text/csv,application/pdf,*/*"})
inventory={}
def hash_bytes(data):return hashlib.sha256(data).hexdigest()
def get(url,limit=100_000_000,timeout=(20,50)):
    r=S.get(url,timeout=timeout,allow_redirects=True,stream=True,
       headers={"Referer":"https://www.ishares.com/" if "blackrock.com" in url else "https://www.cmegroup.com/" if "cmegroup.com" in url else "https://www.federalreserve.gov/"})
    status=r.status_code
    kind=r.headers.get("Content-Type","")
    if status!=200:
        hint=r.raw.read(250,decode_content=True)
        return None,{"http_status":status,"mime":kind,"final_url":r.url,"hint":hint.decode("utf8","replace")[:130]}
    data=b""
    for chunk in r.iter_content(1024*1024):
        if chunk:
            data+=chunk
            if len(data)>limit:raise ValueError("max download size exceeded")
    return data,{"http_status":status,"mime":kind,"final_url":r.url,"bytes":len(data)}
def save(name,body,meta):
    (ROOT/name).write_bytes(body)
    return {"file":name,"bytes":len(body),"sha256":hash_bytes(body),**meta}
def record(key,fn):
    try:
        inventory[key]=fn()
    except Exception as e:inventory[key]={"status":"FAILED","reason":f"{type(e).__name__}: {str(e)[:370]}"}
    print(key,json.dumps(inventory[key],ensure_ascii=False)[:900],flush=True)
def rows_to_csv(rows,path):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    if not rows:return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def parse_spreadsheetml(content):
    # Issuer SpreadsheetML 2003 XML contains bare & in HRef attributes; escape
    # only unescaped ampersands (no numeric data substitutions). Preserve raw SHA.
    normalized,nfix=re.subn(rb"&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9A-Fa-f]+;)",b"&amp;",content)
    root=ET.fromstring(normalized)
    if root.tag.split("}")[-1].lower()!="workbook":raise ValueError("not spreadsheetml Workbook XML")
    sheets={}
    for ws in root.iter():
        if ws.tag.split("}")[-1]!="Worksheet":continue
        name=next((v for k,v in ws.attrib.items() if k.endswith("}Name") or k=="Name"),"unknown")
        table=next((c for c in ws if c.tag.split("}")[-1]=="Table"),None)
        if table is None:continue
        rows=[]
        for row in table:
            if row.tag.split("}")[-1]!="Row":continue
            line=[];idx=0
            for cell in row:
                if cell.tag.split("}")[-1]!="Cell":continue
                target=next((int(v)-1 for k,v in cell.attrib.items() if k.endswith("}Index")),None)
                if target is not None:
                    if target<0 or target>1000:raise ValueError("bad sparse column index")
                    while len(line)<target:line.append("")
                data=next((v for v in cell if v.tag.split("}")[-1]=="Data"),None)
                line.append((data.text or "") if data is not None else "")
            if any(str(z).strip() for z in line):rows.append(line)
        sheets[name]=rows
    if not sheets:raise ValueError("no spreadsheetml worksheets")
    return sheets
def blackrock_slv():
    url=("https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?"
         "appType=PRODUCT_PAGE&appSubType=ISHARES&targetSite=us-ishares&locale=en_US"
         "&portfolioId=239855&component=fundDownload&userType=individual")
    body,meta=get(url,limit=36_000_000)
    if body is None:return {"status":"HTTP_BLOCKED",**meta}
    header=body[:100].lstrip()
    rawtype=("XLSX_ZIP" if body.startswith(b"PK\x03\x04") else
          "LEGACY_XLS_OLE" if body.startswith(b"\xd0\xcf\x11\xe0") else
          "SPREADSHEETML_XML" if (header.startswith(b"<?xml") or header.startswith(b"<Workbook") or b"<Workbook" in header) else "INVALID")
    if rawtype=="INVALID":return {"status":"INVALID_PAYLOAD","prefix":repr(body[:140]),**meta}
    path="slv_official_download_"+("xml" if rawtype=="SPREADSHEETML_XML" else "xlsx" if rawtype=="XLSX_ZIP" else "xls")
    details=save(path,body,meta)
    if rawtype=="SPREADSHEETML_XML":
        sh=parse_spreadsheetml(body)
        details["sheets"]={name:{"rows":len(rows),"first_three":rows[:3],"last_two":rows[-2:]} for name,rows in sh.items()}
        for name,rows in sh.items():
            # The cells are given as-is; standardized date/value analysis is a separate stage.
            normalized=[]
            for row in rows:
                normalized.append({"col_"+str(i+1):v for i,v in enumerate(row)})
            if normalized:
                safe=re.sub("[^A-Za-z0-9_]","_",name)[:32]
                rows_to_csv(normalized,"slv_"+safe+"_raw_cells.csv")
    else:details["note"]="Valid binary workbook, needs separate non-lossy parser"
    return {"status":"ISSUER_WORKBOOK_ARCHIVED_NEEDS_PIT_VALIDATION","format":rawtype,
        "model_ready":False,"important":"SLV history may be NAV only, do NOT call it silver ounce flow",**details}
def frb_h15():
    url=("https://www.federalreserve.gov/datadownload/Output.aspx?"
        "rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=&to=&filetype=csv"
        "&label=include&layout=seriescolumn&type=package")
    body,meta=get(url,limit=12_000_000,timeout=(20,55))
    if body is None:return {"status":"HTTP_BLOCKED",**meta}
    text=body.decode("utf-8-sig","replace")
    if "<html" in text[:500].lower() or len(body)<40_000:raise ValueError("not a full H15 CSV")
    header="\n".join(text.splitlines()[:30])
    if ("Rate" not in header and "Treasury" not in header and "RIFLGFC" not in header):raise ValueError("not recognized Fed H15 package")
    d=save("fed_h15_treasury_cmt_full_history.csv",body,meta)
    return {"status":"FED_H15_ISSUER_ARCHIVE_RECEIVED","model_ready":False,
            "has_2026":("2026-" in text),"header_preview":text.splitlines()[:12],**d}
def fred_snapshot(series):
    u="https://fred.stlouisfed.org/graph/fredgraph.csv?"+urlencode({"id":series})
    data,meta=get(u,limit=5_000_000,timeout=(10,16))
    if data is None:return {"status":"HTTP_BLOCKED",**meta}
    if len(data)<1000 or series.encode() not in data[:500]:raise ValueError("bad FRED CSV")
    return {"status":"FRED_CURRENT_SNAPSHOT_PIT_UNVERIFIED",**save("fred_"+series+".csv",data,meta)}
def cme_historic(symbol):
    base=f"https://www.cmegroup.com/clearing/risk-management/files/{symbol}-2020-to-present.pdf"
    # no circumvention. Only publicly advertised PDF with normal publisher headers.
    body,meta=get(base,limit=110_000_000,timeout=(20,45))
    if body is None:return {"status":"PUBLISHER_ACCESS_BLOCKED",**meta,"official_url":base}
    if not body.startswith(b"%PDF"):raise ValueError("CME response is not a PDF")
    return {"status":"CME_ORIGINAL_PDF_DOWNLOADED_UNPARSED","model_ready":False,
            **save("cme_"+symbol+"_historical_performance_bond_2020-present.pdf",body,meta)}
record("slv_ishares_official",blackrock_slv)
record("fed_h15_treasury",frb_h15)
for series in ["DFII10","DGS2","DTWEXBGS"]:
    record("fred_"+series,lambda series=series:fred_snapshot(series))
for sym in ["GC","SI"]:
    record("cme_"+sym,lambda sym=sym:cme_historic(sym))
report={"status":"OFFICIAL_ISSUER_FILE_COLLECTION_ONLY","date":dt.datetime.now(dt.timezone.utc).isoformat(),
        "scientific_criteria":"Source hash and schema required; original publish time unverified until separately established",
        "neon_written":False,"model_fit":False,"model_ready":False,"inventory":inventory}
(ROOT/"collection_audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("DONE",json.dumps({k:v.get("status") for k,v in inventory.items()}),flush=True)
