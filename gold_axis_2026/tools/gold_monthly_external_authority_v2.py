from __future__ import annotations

import argparse, hashlib, io, json, time, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

START="2010-01-01"
END="2026-09-29"
EXPECTED_V1_PAYLOAD="c52670ccf7bccc75e7c92e6d8261fe25d2d8c62b986300d45d5f264a26142353"
WB_URL="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"

SOURCE_AUTHORITY={
    "NASDAQ100":{
        "upstream_source":"Nasdaq, Inc.",
        "redistributor":None,
        "frequency":"DAILY_CLOSE",
        "units":"INDEX",
        "availability_lag_days":1,
    },
    "WTI":{
        "upstream_source":"U.S. Energy Information Administration",
        "redistributor":None,
        "frequency":"DAILY",
        "units":"USD_PER_BARREL",
        "availability_lag_days":7,
        "transform_class":"SIGNED_LEVEL_DIFFERENCE__NEGATIVE_PRICES_EXIST",
    },
    "BRENT":{
        "upstream_source":"U.S. Energy Information Administration",
        "redistributor":None,
        "frequency":"DAILY",
        "units":"USD_PER_BARREL",
        "availability_lag_days":7,
    },
}

def sha_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def sha_obj(x)->str:
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def get(url:str, timeout=60)->bytes:
    last=None
    for attempt in range(5):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-research/2.0"})
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"DOWNLOAD_FAILED {url} {type(last).__name__}:{last}")

def get_with_headers(url:str, headers:dict[str,str], timeout=60)->bytes:
    last=None
    for attempt in range(5):
        try:
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"DOWNLOAD_FAILED {url} {type(last).__name__}:{last}")

def clean_market_number(v):
    s=str(v or "").replace("$","").replace(",","").strip()
    if s in {"","--","N/A","None"}: return None
    try:
        x=float(s)
    except Exception:
        return None
    return x if np.isfinite(x) else None

def fetch_nasdaq100_official():
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Accept":"application/json,text/plain,*/*",
        "Accept-Language":"en-US,en;q=0.9",
        "Referer":"https://www.nasdaq.com/",
        "Origin":"https://www.nasdaq.com",
    }
    out={}; chunks=[]
    for year in range(2010,2027):
        a=f"{year}-01-01"
        b=END if year==2026 else f"{year}-12-31"
        url=(f"https://api.nasdaq.com/api/quote/NDX/historical?assetclass=index"
             f"&fromdate={a}&todate={b}&limit=5000")
        raw=get_with_headers(url,headers,60)
        d=json.loads(raw)
        rows=((d.get("data") or {}).get("tradesTable") or {}).get("rows") or []
        if not isinstance(rows,list) or not rows:
            raise RuntimeError(f"NASDAQ100_NO_ROWS {year}")
        before=len(out)
        for r in rows:
            ds=str(r.get("date") or "").strip()
            dt=pd.to_datetime(ds,format="%m/%d/%Y",errors="coerce")
            v=clean_market_number(r.get("close"))
            if pd.notna(dt) and v is not None and pd.Timestamp(START)<=dt<=pd.Timestamp(END):
                out[dt.strftime("%Y-%m-%d")]=float(v)
        chunks.append({"year":year,"url":url,"sha256":sha_bytes(raw),"rows_received":len(rows),"rows_added":len(out)-before})
    if not out or min(out)>"2010-01-15":
        raise RuntimeError(f"NASDAQ100_HISTORY_TOO_SHORT first={min(out) if out else None}")
    return dict(sorted(out.items())),{
        "source":"Nasdaq, Inc. public historical quote API",
        "series":"NDX",
        "endpoint":"https://api.nasdaq.com/api/quote/NDX/historical",
        "first":min(out),"last":max(out),"n":len(out),"chunks":chunks,
    }

def fetch_eia_daily_xls(name:str,url:str):
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Accept":"application/vnd.ms-excel,application/octet-stream,*/*",
        "Referer":"https://www.eia.gov/",
    }
    raw=get_with_headers(url,headers,120)
    book=pd.ExcelFile(io.BytesIO(raw),engine="xlrd")
    sheet=book.sheet_names[1] if len(book.sheet_names)>1 else book.sheet_names[0]
    x=pd.read_excel(io.BytesIO(raw),sheet_name=sheet,header=None,engine="xlrd")
    header_row=None
    for i in range(min(12,len(x))):
        row=[str(v).strip().lower() for v in x.iloc[i].tolist()]
        if any(v=="date" for v in row):
            header_row=i; break
    if header_row is None:
        raise RuntimeError(f"{name}_EIA_HEADER_NOT_FOUND sheets={book.sheet_names}")
    df=pd.read_excel(io.BytesIO(raw),sheet_name=sheet,header=header_row,engine="xlrd")
    date_col=df.columns[0]
    value_cols=[z for z in df.columns[1:] if "unnamed" not in str(z).lower()]
    if not value_cols:
        value_cols=list(df.columns[1:])
    if not value_cols:
        raise RuntimeError(f"{name}_EIA_VALUE_COLUMN_NOT_FOUND")
    value_col=value_cols[0]
    dt=pd.to_datetime(df[date_col],errors="coerce")
    val=pd.to_numeric(df[value_col],errors="coerce")
    z=pd.DataFrame({"date":dt,"value":val}).dropna()
    z=z[(z.date>=pd.Timestamp(START))&(z.date<=pd.Timestamp(END))]
    out={r.date.strftime("%Y-%m-%d"):float(r.value) for r in z.itertuples(index=False)}
    if not out or min(out)>"2010-01-15":
        raise RuntimeError(f"{name}_EIA_HISTORY_TOO_SHORT first={min(out) if out else None}")
    return dict(sorted(out.items())),{
        "source":"U.S. Energy Information Administration",
        "url":url,"sha256":sha_bytes(raw),"sheet":sheet,
        "date_column":str(date_col),"value_column":str(value_col),
        "first":min(out),"last":max(out),"n":len(out),
    }

def fetch_fred_daily(series_id:str):
    chunks=[("2010-01-01","2014-12-31"),("2015-01-01","2019-12-31"),
            ("2020-01-01","2023-12-31"),("2024-01-01",END)]
    frames=[]; metas=[]
    for a,b in chunks:
        url=(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
             f"&cosd={a}&coed={b}")
        raw=get(url,60)
        df=pd.read_csv(io.BytesIO(raw))
        if len(df.columns)<2:
            raise RuntimeError(f"BAD_FRED_COLUMNS {series_id} {list(df.columns)}")
        df=df.iloc[:,:2].copy()
        df.columns=["date","value"]
        df["date"]=pd.to_datetime(df["date"],errors="coerce")
        df["value"]=pd.to_numeric(df["value"],errors="coerce")
        df=df.dropna(subset=["date","value"])
        frames.append(df)
        metas.append({"start":a,"end":b,"url":url,"sha256":sha_bytes(raw),"rows":int(len(df))})
    df=pd.concat(frames,ignore_index=True).drop_duplicates("date",keep="last").sort_values("date")
    df=df[(df.date>=pd.Timestamp(START))&(df.date<=pd.Timestamp(END))]
    if df.empty:
        raise RuntimeError(f"NO_FRED_ROWS {series_id}")
    if df.date.duplicated().any():
        raise RuntimeError(f"DUPLICATE_DATES {series_id}")
    out={r.date.strftime("%Y-%m-%d"):float(r.value) for r in df.itertuples(index=False)}
    return out,{
        "series_id":series_id,
        "chunks":metas,
        "first":min(out),
        "last":max(out),
        "n":len(out),
    }


def post_json(url:str, payload:dict, timeout=60)->bytes:
    raw=json.dumps(payload).encode()
    last=None
    for attempt in range(5):
        try:
            req=urllib.request.Request(url,data=raw,headers={
                "User-Agent":"gold-monthly-research/2.0",
                "Content-Type":"application/json",
                "Accept":"application/json",
            },method="POST")
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"POST_FAILED {url} {type(last).__name__}:{last}")

def fetch_cpi_prehistory():
    endpoint="https://api.bls.gov/publicAPI/v2/timeseries/data/"
    out={}; chunks=[]
    for start,end in ((2008,2017),(2018,2026)):
        payload={"seriesid":["CUUR0000SA0","CUUR0000SA0L1E"],
                 "startyear":str(start),"endyear":str(end)}
        raw=post_json(endpoint,payload,90)
        d=json.loads(raw)
        if str(d.get("status"))!="REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS_FAIL {start}-{end} {d.get('message')}")
        chunks.append({"start":start,"end":end,"sha256":sha_bytes(raw)})
        for s in d["Results"]["series"]:
            sid=s["seriesID"]
            key="CPI_ALL_NSA" if sid=="CUUR0000SA0" else "CPI_CORE_NSA"
            for r in s["data"]:
                per=str(r["period"])
                if not per.startswith("M") or per=="M13": continue
                m=f"{int(r['year']):04d}-{int(per[1:]):02d}"
                v=pd.to_numeric(r.get("value"),errors="coerce")
                if pd.notna(v):
                    out.setdefault(m,{})[key]=float(v)
    if min(out)>"2008-01" or max(out)<"2026-08":
        raise RuntimeError(f"CPI_PREHISTORY_COVERAGE {min(out)} {max(out)}")
    required=pd.period_range("2009-01","2024-12",freq="M")
    missing=[str(m) for m in required if str(m) not in out or
             not {"CPI_ALL_NSA","CPI_CORE_NSA"}<=set(out[str(m)])]
    if missing:
        raise RuntimeError(f"CPI_PREHISTORY_MISSING {missing[:12]}")
    return out,{
        "endpoint":endpoint,
        "source":"U.S. Bureau of Labor Statistics",
        "series":["CUUR0000SA0","CUUR0000SA0L1E"],
        "first":min(out),"last":max(out),"n":len(out),
        "chunks":chunks,
        "purpose":"preserve canonical 2010-03 training start for YoY CPI features",
    }

def fetch_world_bank_prehistory():
    raw=get(WB_URL,180)
    x=pd.read_excel(io.BytesIO(raw),sheet_name="Monthly Prices",header=None,engine="openpyxl")
    header_row=None
    for rr in range(min(12,len(x))):
        vals=[str(v).strip().lower() for v in x.iloc[rr].tolist()]
        if any("crude oil" in v for v in vals) and any(v=="gold" or v.startswith("gold ") for v in vals):
            header_row=rr; break
    if header_row is None: raise RuntimeError("WB_HEADER_NOT_FOUND")
    headers=[str(v).strip() for v in x.iloc[header_row].tolist()]
    targets={}
    for i,name in enumerate(headers):
        lo=name.lower()
        if "crude oil" in lo and "brent" in lo: targets["BRENT"]=i
        elif "crude oil" in lo and ("wti" in lo or "west texas" in lo): targets["WTI"]=i
        elif lo=="copper" or lo.startswith("copper "): targets["COPPER"]=i
        elif "crude oil" in lo and "average" in lo: targets["CRUDE_AVG"]=i
    if not {"BRENT","WTI","COPPER"}<=set(targets):
        raise RuntimeError(f"WB_REQUIRED_COLUMNS_MISSING {targets}")
    out={}
    for _,row in x.iterrows():
        import re
        m=re.match(r"^(\d{4})M(\d{1,2})$",str(row.iloc[0]).strip(),re.I)
        if not m: continue
        mk=f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
        if mk<"2008-01" or mk>"2026-08": continue
        z={}
        for k,i in targets.items():
            v=pd.to_numeric(row.iloc[i],errors="coerce")
            if pd.notna(v): z[k]=float(v)
        if z: out[mk]=z
    if min(out)>"2008-01" or "2009-12" not in out or max(out)<"2026-08":
        raise RuntimeError(f"WB_PREHISTORY_COVERAGE {min(out)} {max(out)}")
    return out,{
        "url":WB_URL,"sha256":sha_bytes(raw),"columns":targets,
        "first":min(out),"last":max(out),"n":len(out),
        "source":"World Bank Pink Sheet",
        "purpose":"preserve canonical 2010-03 history for monthly Copper and commodity controls",
    }

def month_avg(daily:dict[str,float]):
    s=pd.Series(daily,dtype=float)
    s.index=pd.to_datetime(s.index)
    return {str(k):float(v) for k,v in s.groupby(s.index.to_period("M")).mean().items()}

def coverage_diag(name,daily, min_total, min_monthly=10, require_positive=True):
    idx=pd.to_datetime(list(daily))
    vals=np.array(list(daily.values()),float)
    if len(daily)<min_total:
        raise RuntimeError(f"{name}_TOO_FEW total={len(daily)} min={min_total}")
    if not np.all(np.isfinite(vals)):
        raise RuntimeError(f"{name}_NONFINITE")
    nonpositive={k:float(v) for k,v in daily.items() if float(v)<=0}
    if require_positive and nonpositive:
        raise RuntimeError(f"{name}_NONPOSITIVE {list(nonpositive.items())[:8]}")
    months=pd.Series(1,index=idx).groupby(idx.to_period("M")).sum()
    required=pd.period_range("2010-01","2024-12",freq="M")
    missing=[str(m) for m in required if m not in months.index]
    if missing:
        raise RuntimeError(f"{name}_MISSING_MONTHS {missing[:12]}")
    thin={str(m):int(months.loc[m]) for m in required if int(months.loc[m])<min_monthly}
    return {
        "n":len(daily),"first":min(daily),"last":max(daily),
        "min_value":float(vals.min()),"max_value":float(vals.max()),
        "nonpositive_count":len(nonpositive),
        "nonpositive_examples":list(nonpositive.items())[:12],
        "required_months":len(required),"thin_months":thin,
        "min_required_monthly_observations":min_monthly,
    }

def parity(a:dict[str,float], b:dict[str,float], end="2026-07"):
    common=sorted(k for k in set(a)&set(b) if k<=end)
    pairs=[(a[k],b[k]) for k in common if np.isfinite(a[k]) and np.isfinite(b[k]) and b[k]!=0]
    if not pairs:
        return {"n":0,"status":"NO_OVERLAP"}
    aa=np.array([x for x,_ in pairs],float)
    bb=np.array([y for _,y in pairs],float)
    diff=np.abs(aa-bb)
    rel=diff/np.abs(bb)
    return {
        "n":len(pairs),
        "median_abs_diff":float(np.median(diff)),
        "p95_abs_diff":float(np.quantile(diff,.95)),
        "max_abs_diff":float(diff.max()),
        "median_abs_rel_diff":float(np.median(rel)),
        "p95_abs_rel_diff":float(np.quantile(rel,.95)),
        "corr":float(np.corrcoef(aa,bb)[0,1]) if len(aa)>2 else None,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v1-store",required=True)
    ap.add_argument("--output",default="gold_monthly_external_authority_v2.json")
    a=ap.parse_args()

    v1=json.loads(Path(a.v1_store).read_text())
    if v1.get("payload_sha256")!=EXPECTED_V1_PAYLOAD:
        raise RuntimeError(f"V1_PAYLOAD_MISMATCH {v1.get('payload_sha256')}")

    daily={}; meta={}
    daily["NASDAQ100"],meta["NASDAQ100"]=fetch_nasdaq100_official()
    daily["WTI"],meta["WTI"]=fetch_eia_daily_xls(
        "WTI","https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls")
    daily["BRENT"],meta["BRENT"]=fetch_eia_daily_xls(
        "BRENT","https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls")

    diag={
        "NASDAQ100":coverage_diag("NASDAQ100",daily["NASDAQ100"],min_total=3500,min_monthly=10),
        "WTI":coverage_diag("WTI",daily["WTI"],min_total=3500,min_monthly=10,require_positive=False),
        "BRENT":coverage_diag("BRENT",daily["BRENT"],min_total=3500,min_monthly=10),
    }

    ndx_m=month_avg(daily["NASDAQ100"])
    core_ndx={m:float(z["NASDAQ_AVG_MONTHLY"]) for m,z in v1["core5_monthly"].items() if z.get("NASDAQ_AVG_MONTHLY") is not None}
    wb=v1["commodity_monthly"]
    wb_wti={m:float(z["WTI"]) for m,z in wb.items() if z.get("WTI") is not None}
    wb_brent={m:float(z["BRENT"]) for m,z in wb.items() if z.get("BRENT") is not None}

    cpi_long,cpi_long_meta=fetch_cpi_prehistory()
    wb_long,wb_long_meta=fetch_world_bank_prehistory()

    diagnostics={
        "coverage":diag,
        "nasdaq_daily_monthly_avg_vs_core5":parity(ndx_m,core_ndx),
        "wti_daily_monthly_avg_vs_world_bank":parity(month_avg(daily["WTI"]),wb_wti),
        "brent_daily_monthly_avg_vs_world_bank":parity(month_avg(daily["BRENT"]),wb_brent),
    }

    out={
        "schema":"GOLD_MONTHLY_EXTERNAL_AUTHORITY_V2_2026-09-29",
        "authority":{
            "role":"RAW_FREQUENCY_AUTHORITY_BEFORE_F4_RESTART",
            "neon_reads":0,
            "model_results_in_this_stage":False,
            "no_synthetic_daily_data":True,
            "historical_market_series_class":"HISTORICAL_RECONSTRUCTION_NOT_VINTAGE",
            "v1_store_payload_sha256":EXPECTED_V1_PAYLOAD,
            "selection_use":"NONE",
            "2025_selection_use":"NONE",
            "2026_selection_use":"NONE",
        },
        "source_authority":SOURCE_AUTHORITY,
        "source_meta":meta,
        "nasdaq100_daily":daily["NASDAQ100"],
        "wti_daily":daily["WTI"],
        "brent_daily":daily["BRENT"],
        "h15_daily":v1["h15_daily"],
        "h15_meta":v1["h15_meta"],
        "h10_daily":v1["h10_daily"],
        "h10_meta":v1["h10_meta"],
        "vix_daily":v1["vix_daily"],
        "vix_meta":v1["vix_meta"],
        "cpi_monthly":cpi_long,
        "cpi_meta":cpi_long_meta,
        "commodity_monthly":wb_long,
        "commodity_meta":wb_long_meta,
        "core5_monthly":v1["core5_monthly"],
        "core5_meta":v1["core5_meta"],
        "readiness":{
            "rates_daily":"READY_FED_H15",
            "fx_daily":"READY_FED_H10",
            "vix_daily":"READY_CBOE",
            "nasdaq100_daily":"READY_NASDAQ_OFFICIAL",
            "wti_daily":"READY_EIA_OFFICIAL",
            "brent_daily":"READY_EIA_OFFICIAL",
            "cpi":"READY_MONTHLY_NATIVE_FREQUENCY_WITH_2008_PREHISTORY",
            "copper":"READY_MONTHLY_WORLD_BANK_WITH_2008_PREHISTORY__DAILY_NOT_PROVEN",
            "cpi_daily":"NOT_APPLICABLE_NATIVE_MONTHLY_STATISTIC",
        },
        "diagnostics":diagnostics,
    }
    out["payload_sha256"]=sha_obj(out)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("EXTERNAL_AUTHORITY_V2_GATE=PASS")
    print(json.dumps({
        "payload_sha256":out["payload_sha256"],
        "readiness":out["readiness"],
        "source_meta":meta,
        "diagnostics":diagnostics,
    },sort_keys=True))

if __name__=="__main__":
    main()
