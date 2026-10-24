"""Official-only archive capture for exogenous gold-risk research (manual run).

NO ANN training, no Neon writes and no cron. Strictly label raw-byte download
different from model-ready point-in-time feature validation. Annual CFTC files
are grouped by *position/report date*, not publication date. 2025 shutdown
requires an overriding official revision calendar.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, io, json, os, re, time, zipfile
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

CFTC_BASE="https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
FRED_BASE="https://fred.stlouisfed.org/graph/fredgraph.csv?id={symbol}"
CME={"GC":"https://www.cmegroup.com/clearing/risk-management/files/GC-2020-to-present.pdf",
     "SI":"https://www.cmegroup.com/clearing/risk-management/files/SI-2020-to-present.pdf"}
GLD="https://www.spdrgoldshares.com/usa/gld/"
SLV="https://www.ishares.com/us/products/239855/ishares-silver-trust-fund"
# The final 2025 government-shutdown release dates from CFTC press 9147-25,
# NOT the original scheduled Friday dates. Includes Dec 2025 report published
# in Jan 2026 (should be treated independently when captured).
CFTC_DELAY_2025={
 "2025-09-30":"2025-11-19","2025-10-07":"2025-11-21",
 "2025-10-14":"2025-11-25","2025-10-21":"2025-12-02",
 "2025-10-28":"2025-12-05","2025-11-04":"2025-12-09",
 "2025-11-10":"2025-12-10","2025-11-18":"2025-12-12",
 "2025-11-25":"2025-12-15","2025-12-02":"2025-12-17",
 "2025-12-09":"2025-12-19","2025-12-16":"2025-12-23",
 "2025-12-23":"2025-12-29"}
CFTC_REVISED_URL="https://www.cftc.gov/PressRoom/PressReleases/9147-25"
def sha(b):return hashlib.sha256(b).hexdigest()
def download(sess,url,max_bytes=25_000_000):
    r=sess.get(url,timeout=(20,90),allow_redirects=True)
    r.raise_for_status()
    body=r.content
    if len(body)>max_bytes:raise RuntimeError(f"response exceeds {max_bytes} bytes")
    if len(body)<200:raise RuntimeError(f"undersized data {len(body)}")
    return body,r.url
def safe_save(root,name,payload,url,kind,notes=""):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(payload)
    return {"status":"RAW_ARCHIVED_UNPARSED" if kind in ("xlsx","pdf") else "RAW_ARCHIVED",
       "source":url,"file":str(p.relative_to(root)),"type":kind,
       "sha256":sha(payload),"bytes":len(payload),"notes":notes}
def field(d,*terms):
    norm={re.sub("[^a-z0-9]","",k.lower()):k for k in d}
    for term in terms:
        key=re.sub("[^a-z0-9]","",term.lower())
        if key in norm:return d[norm[key]]
    return None
def cftc_asof(d):
    if d in CFTC_DELAY_2025:
        # On day of release COT is published 15:30 New York; conservative
        # following calendar day date is definitely later.
        return (dt.date.fromisoformat(CFTC_DELAY_2025[d])+dt.timedelta(days=1)).isoformat(),"OFFICIAL_CFTC_2025_SHUTDOWN_RESCHEDULE"
    # All ordinary weeks TUESDAY report, usually FRI release. Provisional
    # 7-day lag does not certify exceptions/holidays, so is research-only.
    day=dt.date.fromisoformat(d)
    return (day+dt.timedelta(days=7)).isoformat(),"CONSERVATIVE_7_DAY_RELEASE_PROXY_NOT_PROVEN"
def parse_cftc(zbytes,year,root):
    z=zipfile.ZipFile(io.BytesIO(zbytes))
    files=[n for n in z.namelist() if n.lower().endswith((".txt",".csv"))]
    if not files:raise ValueError(f"archive {year} lacks COT text")
    payload=z.read(max(files,key=lambda n:z.getinfo(n).file_size))
    raw=payload.decode("utf-8-sig",errors="replace")
    # One untrusted source version per year; unknown schema must fail closed.
    reader=csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:raise ValueError("CFTC_EMPTY_HEADER")
    out={}; all_name=[]
    for row in reader:
        name=str(field(row,"Market_and_Exchange_Names","Contract_Market_Name") or "")
        if "GOLD" in name.upper() and ("COMMODITY EXCHANGE" in name.upper() or "COMEX" in name.upper()):
            metal="GC"
        elif "SILVER" in name.upper() and ("COMMODITY EXCHANGE" in name.upper() or "COMEX" in name.upper()):
            metal="SI"
        else:continue
        day=str(field(row,"Report_Date_as_YYYY-MM-DD","Report_Date_as_YYYY_MM_DD","As_of_Date_In_Form_YYMMDD") or "").strip()
        if re.fullmatch(r"\d{8}",day): day=f"{day[:4]}-{day[4:6]}-{day[6:]}"
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",day):
            raise ValueError("CFTC_UNKNOWN_REPORT_DATE_FORMAT "+day)
        if day[:4]!=str(year):continue
        long=field(row,"M_Money_Positions_Long_All","M_Money_Positions_Long")
        short=field(row,"M_Money_Positions_Short_All","M_Money_Positions_Short")
        oi=field(row,"Open_Interest_All","Open_Interest")
        if long is None or short is None or oi is None:
            raise ValueError("CFTC_MONEY_COLUMNS_MISSING "+str(reader.fieldnames))
        key=(day,metal)
        if key in out:raise ValueError("CFTC_DUPLICATED_REPORT_CONTRACT_"+str(key))
        publication,tag=cftc_asof(day)
        def n(x):return float(str(x).replace(",","").strip())
        l,s,o=n(long),n(short),n(oi)
        if min(l,s,o)<0 or o<=0:raise ValueError("CFTC_NEGATIVE_OR_ZERO_OI")
        out[key]={"position_date":day,"market":metal,
            "available_on_or_after_ny_date":publication,"release_protocol":tag,
            "managed_money_long":l,"managed_money_short":s,
            "managed_money_net":l-s,"open_interest":o,"mm_net_over_oi":(l-s)/o,
            "source_year":year}
    records=sorted(out.values(),key=lambda r:(r["position_date"],r["market"]))
    if len(records)<75 or len({r["market"] for r in records})<2:
        raise ValueError(f"CFTC_NOT_COMPLETE_GOLD_SILVER_{year}:{len(records)}")
    (root/f"cot_gold_silver_{year}_research.csv").write_text(
        "" if not records else to_csv(records),encoding="utf-8")
    return {"status":"HISTORIC_CFTC_GC_SI_PARSED_RESEARCH",
            "gold_records":sum(x["market"]=="GC" for x in records),
            "silver_records":sum(x["market"]=="SI" for x in records),
            "first_position_date":min(x["position_date"] for x in records),
            "last_position_date":max(x["position_date"] for x in records),
            "release_calendar":"2025-shutdown official; other dates conservative 7-day proxy",
            "file":f"cot_gold_silver_{year}_research.csv"}
def to_csv(records):
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(records[0]))
    writer.writeheader();writer.writerows(records)
    return out.getvalue()
def capture_spdr(sess,root):
    raw,_=download(sess,GLD,max_bytes=3_000_000)
    html=BeautifulSoup(raw,"html.parser")
    hits=[]
    for a in html.find_all("a",href=True):
        t=a.get_text(" ",strip=True).lower()
        href=urljoin(GLD,a["href"])
        if "api.spdrgoldshares.com" in href and ("xlsx" in href.lower() or "historical" in href.lower() or "archive" in href.lower() or "download" in t):
            hits.append(href)
    hits=list(dict.fromkeys(hits))
    if len(hits)!=1:raise RuntimeError("GLD_AMBIGUOUS_HISTORIC_XLSX_LINKS "+repr(hits[:8]))
    b,url=download(sess,hits[0],max_bytes=25_000_000)
    if not b.startswith(b"PK"):raise ValueError("GLD_DOWNLOAD_NOT_XLSX")
    return safe_save(root,"gld_official_historical_archive.xlsx",b,url,"xlsx",
         notes="Downloaded publisher archive; date coverage and point-in-time posting to be separately audited")
def capture_slv(sess,root):
    raw,_=download(sess,SLV,max_bytes=3_000_000)
    soup=BeautifulSoup(raw,"html.parser")
    links=[]
    for a in soup.find_all("a",href=True):
        t=a.get_text(" ",strip=True).lower()
        if "data download" in t and ("excel" in t or "download" in t):
            links.append(urljoin(SLV,a["href"]))
    links=list(dict.fromkeys(links))
    if len(links)!=1:raise RuntimeError("SLV_DOWNLOAD_EXCEL_LINK_NOT_UNIQUE "+repr(links[:8]))
    b,url=download(sess,links[0],max_bytes=25_000_000)
    if not b.startswith(b"PK") and not b.startswith(b"\xd0\xcf\x11\xe0"):
        raise ValueError("SLV_DOWNLOAD_NOT_VALID_XLSX_XLS")
    ext=".xlsx" if b.startswith(b"PK") else ".xls"
    return safe_save(root,"slv_official_data_download"+ext,b,url,"xlsx",
       notes="Downloaded as published: historical daily ounces/tonnes/share coverage NOT independently verified")
def capture_fred(sess,root,symbol):
    url=FRED_BASE.format(symbol=symbol)
    b,url=download(sess,url,max_bytes=3_000_000)
    rows=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    if not rows or symbol not in rows[0]:raise ValueError("FRED_BAD_CSV_"+symbol)
    vals=[r for r in rows if str(r.get(symbol) or "").strip() not in (".","")]
    relevant=[r for r in vals if "2023-01-01"<=str(r.get("observation_date") or r.get("DATE") or "")<="2025-12-31"]
    if len(relevant)<500:raise ValueError(f"FRED_THREE_YEAR_COVERAGE_{symbol}_{len(relevant)}")
    entry=safe_save(root,f"fred_{symbol}.csv",b,url,"csv")
    entry.update({"status":"HISTORICAL_CSV_DOWNLOADED","usable_2023_2025":len(relevant),
       "vintage":"CURRENT HISTORICAL SNAPSHOT, original release vintage UNVERIFIED"})
    return entry
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--outdir",default="/tmp/gold_exogenous_data")
    parser.add_argument("--no-cme",action="store_true")
    a=parser.parse_args()
    root=Path(a.outdir).absolute();root.mkdir(parents=True,exist_ok=True)
    sess=requests.Session()
    sess.headers.update({"User-Agent":"Mozilla/5.0 (Gold research evidence audit / original publisher sources)"})
    inventory={}
    for year in [2023,2024,2025,2026]:
        key=f"cftc_disagg_futures_{year}";url=CFTC_BASE.format(year=year)
        try:
            b,actual=download(sess,url,max_bytes=18_000_000)
            raw=safe_save(root,f"cftc_{year}_official_disaggregated.zip",b,actual,"zip")
            raw.update(parse_cftc(b,year,root))
            inventory[key]=raw
        except Exception as e:inventory[key]={"status":"BLOCKED","url":url,"reason":str(e)[:400]}
    for sym in ["DFII10","DGS2","DGS10","DTWEXBGS"]:
        try:inventory[f"fred_{sym}"]=capture_fred(sess,root,sym)
        except Exception as e:inventory[f"fred_{sym}"]={"status":"BLOCKED","reason":str(e)[:400]}
    for key,fn in [("gld",capture_spdr),("slv",capture_slv)]:
        try: inventory[key]=fn(sess,root)
        except Exception as e:inventory[key]={"status":"BLOCKED_OR_UNVALIDATED","reason":str(e)[:400]}
    if not a.no_cme:
        for symbol,url in CME.items():
            try:
                b,actual=download(sess,url,max_bytes=35_000_000)
                if not b.startswith(b"%PDF"):raise ValueError("CME_HISTORY_NOT_PDF")
                inventory[f"cme_margin_{symbol}"]=safe_save(root,f"cme_{symbol}_historic_margins.pdf",b,actual,"pdf",
                      notes="Raw PDF only: margins keyed by maturity/roll; historical value is not published notice date and is NOT model ready")
            except Exception as e:inventory[f"cme_margin_{symbol}"]={"status":"BLOCKED","reason":str(e)[:400]}
    report={
      "status":"DOWNLOAD_AUDIT_ONLY_NO_NEON_WRITE_NO_TRAINING",
      "scope":"CFTC/GLD/SLV/CME/FRED, 2023-2025 build and optional 2026 stress",
      "data_scope":"raw vendor originals, research-only; not certified origin/vintage until field validation",
      "cftc_2025_shutdown_revision":CFTC_REVISED_URL,
      "run_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "inventory":inventory,
      "model_ready":False,"neon_database_modified":False}
    (root/"source_inventory.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"items":{k:v["status"] for k,v in inventory.items()}},
             indent=2,ensure_ascii=False),flush=True)
    # Do not treat partial source failures as training readiness. Audit artifact
    # always produced, downstream model explicitly blocked on model_ready=false.
    if not any(x.get("status")=="HISTORIC_CFTC_GC_SI_PARSED_RESEARCH" for x in inventory.values()):
        print("WARNING: NO_COMPLETE_CFTC_SOURCE, RESEARCH MODEL MUST NOT FIT",flush=True)
if __name__=="__main__":
    main()
