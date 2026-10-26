#!/usr/bin/env python3
"""V12 research-source acquisition 2010-2019. Fetch issuer bytes, quarantine PIT.
No Neon writes, no training, no signal or trading. Runs on GitHub Actions.
Downloaded datasets are modern revised archives, NOT historical first prints.
"""
from __future__ import annotations
from pathlib import Path
from datetime import date,datetime,timezone
import csv,hashlib,io,json,os,zipfile,time,requests

OUT=Path(os.getenv("GOLD_V12_OUT","/tmp/gold_risk_legacy_macro_2010_2019_v12"))
OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (compatible; academic-research-source-validation/1.0)",
"Accept":"application/zip,text/csv,text/plain,*/*"})
results={}
def sha(b):return hashlib.sha256(b).hexdigest()
def download(name,url,maxlen=50000000):
    last=None
    for trial in range(3):
        try:
            r=S.get(url,timeout=(20,90),allow_redirects=True)
            if r.status_code != 200:raise RuntimeError(f"HTTP {r.status_code}; mime {r.headers.get('Content-Type')}")
            b=r.content
            if len(b)>maxlen or len(b)<1000:raise ValueError(f"invalid byte length {len(b)}")
            if b[:100].lstrip().lower().startswith((b"<html",b"<!doctype")):raise ValueError("html instead of data")
            p=OUT/name;p.write_bytes(b)
            return {"status":"DOWNLOADED_RAW_NOT_PIT","name":name,"url":url,
                "sha256":sha(b),"bytes":len(b),"mime":r.headers.get('Content-Type','')}
        except Exception as e:
            last=str(e)
            time.sleep(trial)
    return {"status":"DOWNLOAD_FAILED","name":name,"url":url,"error":last}

for year in range(2010,2020):
    name=f"cftc_disaggregated_futures_only_{year}.zip"
    url=f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
    result=download(name,url)
    if result["status"].startswith("DOWNLOADED"):
        b=(OUT/name).read_bytes()
        try:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                filenames=z.namelist()
                if not filenames:raise ValueError("empty archive")
                text_files=[n for n in filenames if n.lower().endswith((".txt",".csv"))]
                if not text_files:raise ValueError("no TXT/CSV inside archive")
                pair_counts={"088691":0,"084691":0}
                sample_columns=[]
                for fn in text_files:
                    if z.getinfo(fn).file_size>150000000:raise ValueError("uncompressed file too large")
                    raw=z.read(fn)
                    for encoding in ("utf-8-sig","cp1252","latin-1"):
                        try: txt=raw.decode(encoding);break
                        except UnicodeDecodeError:continue
                    rdr=csv.DictReader(io.StringIO(txt))
                    names=rdr.fieldnames or []
                    if not sample_columns:sample_columns=names[:]
                    for row in rdr:
                        code=str(row.get("CFTC_Contract_Market_Code",
                              row.get("CFTC_Contract_Market_Code ",""))).strip().zfill(6)
                        if code in pair_counts:pair_counts[code]+=1
                if not all(pair_counts.values()):
                    raise ValueError(f"GC/SI contracts absent in archive {pair_counts}")
                result.update({"status":"RAW_GC_SI_PRESENT_NOT_RELEASE_CERTIFIED",
                    "files":filenames,"gc_si_records":pair_counts,
                    "raw_columns":sample_columns[:50],"research_only":True})
        except Exception as e:
            result.update({"status":"QUARANTINE_INVALID_CFTC_ARCHIVE","error":str(e)})
    results[f"CFTC_{year}"]=result
    print("CFTC",year,result["status"],flush=True)

series={
"GVZ_CBOE":"https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv",
"H15_REAL_DFII10":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10",
"H15_NOMINAL_DGS10":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
"H15_NOMINAL_DGS2":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2",
"H10_LEGACY_BROAD_DTWEXB":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXB",
"H10_CURRENT_BROAD_DTWEXBGS":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS",
}
for key,url in series.items():
    name=f"{key}.csv";result=download(name,url,maxlen=12000000)
    if result["status"].startswith("DOWNLOADED"):
        try:
            txt=(OUT/name).read_bytes().decode("utf-8-sig")
            rows=list(csv.reader(io.StringIO(txt)))
            header=rows[0]
            # GVZ original uses DATE,GVZ; FRED uses DATE, SERIES.
            if key=="GVZ_CBOE":
                if not {"DATE","GVZ"}.issubset(set(header)):raise ValueError("GVZ schema missing")
                date_col=header.index("DATE")
                def parse(s):return datetime.strptime(s,"%m/%d/%Y").date()
            else:
                if "DATE" not in header or key.rsplit("_",1)[-1] not in header:
                    raise ValueError("FRED schema missing "+str(header))
                date_col=header.index("DATE")
                def parse(s):return date.fromisoformat(s)
            target=[r for r in rows[1:] if len(r)>date_col and r[date_col] and 2010<=parse(r[date_col]).year<=2019]
            if not target:raise ValueError("no historical 2010-2019 rows")
            result.update({"status":"REVISED_HISTORICAL_SERIES_NOT_PIT","rows_2010_2019":len(target),
                           "first_day":str(parse(target[0][date_col])),"last_day":str(parse(target[-1][date_col])),
                           "columns":header,"asof_verified":False})
        except Exception as e:
            result.update({"status":"QUARANTINE_INVALID_SERIES","error":str(e)})
    results[key]=result
    print(key,result["status"],flush=True)

audit={"run_utc":datetime.now(timezone.utc).isoformat(),
       "objective":"Retrieve issuer data for 2010–2019 case-control macro study; NO model refit",
       "pit_certified":False,"may_train_live_model":False,"neon_write":False,
       "critical":"2011/2013 legacy USD DTWEXB is NOT same historical published series as new DTWEXBGS first released 2019. Never join them as if identical. CFTC Tuesday observation != Friday publication; each report's actual publication time must be confirmed.",
       "sources":results}
(OUT/"audit_v12.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding="utf8")
print("DONE",json.dumps({k:v["status"] for k,v in results.items()}),flush=True)
