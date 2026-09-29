from __future__ import annotations
import argparse, base64, csv, gzip, hashlib, io, json, re, urllib.parse, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd

import gold_monthly_fx_h10_residual_v1 as h10

START="2010-01-01"
END="2026-09-29"
WB_URL="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
VIX_URL="https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
NASDAQ_URL="https://indexes.nasdaqomx.com/reports/history.ashx"
H15_PACKAGE="0b98a66d3ff5e1ea0fbf88adc59b387f"

def sha(b:bytes): return hashlib.sha256(b).hexdigest()

def get(url,timeout=90):
    req=urllib.request.Request(url,headers={
      "User-Agent":"Mozilla/5.0 Gold-Monthly-Research/1.0",
      "Accept":"text/csv,application/json,application/vnd.ms-excel,*/*"
    })
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(), dict(r.headers.items())

def post_json(url,payload,timeout=90):
    raw=json.dumps(payload).encode()
    req=urllib.request.Request(url,data=raw,headers={
      "User-Agent":"Gold-Monthly-Research/1.0",
      "Content-Type":"application/json",
      "Accept":"application/json"
    },method="POST")
    with urllib.request.urlopen(req,timeout=timeout) as r:
        out=r.read()
    return out

def load_core5(path:Path):
    comp=base64.b64decode(path.read_bytes().strip(),validate=True)
    raw=gzip.decompress(comp)
    df=pd.read_csv(io.BytesIO(raw))
    df["date"]=pd.to_datetime(df["date"],errors="raise")
    q=df[(df.date>=pd.Timestamp(START))&(df.date<=pd.Timestamp(END))].copy()
    keep=["date","fedfunds","nasdaq","usdcny"]
    if any(k not in q.columns for k in keep): raise RuntimeError(f"CORE5_COLUMNS_MISSING {list(q.columns)}")
    rows={r.date.strftime("%Y-%m"):{
      "FEDFUNDS_MONTHLY":float(r.fedfunds),
      "NASDAQ_AVG_MONTHLY":float(r.nasdaq),
      "USDCNY_AVG_MONTHLY":float(r.usdcny),
    } for r in q[keep].itertuples(index=False)}
    return rows,{"sha256":sha(raw),"first":min(rows),"last":max(rows),"n":len(rows),
                 "evidence_class":"LOCKED_LOCAL_RESEARCH_SNAPSHOT_NOT_HISTORICAL_PIT"}

def fetch_nasdaq():
    params=urllib.parse.urlencode({
      "IndexSymbol":"NDX","StartDate":START,"EndDate":END,"Type":"csv"
    })
    url=NASDAQ_URL+"?"+params
    raw,h=get(url,120)
    txt=raw.decode("utf-8-sig",errors="replace").strip()
    if "<html" in txt.lower() or "login" in txt.lower():
        raise RuntimeError("NASDAQ_GIW_RETURNED_HTML_OR_LOGIN")
    rows=list(csv.reader(io.StringIO(txt)))
    header=None
    for i,r in enumerate(rows):
        if r and "trade date" in r[0].strip().lower():
            header=i;break
    if header is None: raise RuntimeError(f"NASDAQ_GIW_HEADER_NOT_FOUND {rows[:5]}")
    cols=[x.strip() for x in rows[header]]
    date_i=next((i for i,x in enumerate(cols) if x.lower()=="trade date"),None)
    val_i=next((i for i,x in enumerate(cols) if x.lower()=="index value"),None)
    if date_i is None or val_i is None: raise RuntimeError(f"NASDAQ_GIW_COLUMNS {cols}")
    out={}
    for r in rows[header+1:]:
        if len(r)<=max(date_i,val_i): continue
        d=pd.to_datetime(r[date_i],errors="coerce")
        v=pd.to_numeric(r[val_i],errors="coerce")
        if pd.notna(d) and pd.notna(v) and pd.Timestamp(START)<=d<=pd.Timestamp(END):
            out[d.strftime("%Y-%m-%d")]=float(v)
    if len(out)<3000: raise RuntimeError(f"NASDAQ_GIW_TOO_FEW {len(out)}")
    return out,{"url":url,"sha256":sha(raw),"first":min(out),"last":max(out),"n":len(out),
                "source":"Nasdaq Global Index Watch NDX history"}

def fetch_h15():
    base="https://www.federalreserve.gov/datadownload/Output.aspx"
    q=urllib.parse.urlencode({"filetype":"csv","from":"01/01/2010","label":"include",
      "layout":"seriescolumn","rel":"H15","series":H15_PACKAGE,"to":"09/29/2026","type":"package"})
    raw,h=get(base+"?"+q,120)
    df=h10.parse_ddp(raw)
    ncol=h10.find_col(df,"RIFLGFCY10_N.B")
    rcol=h10.find_col(df,"RIFLGFCY10_XII_N.B")
    out={}
    for r in df[["date",ncol,rcol]].itertuples(index=False):
        z={}
        if pd.notna(r[1]): z["DGS10"]=float(r[1])
        if pd.notna(r[2]): z["DFII10"]=float(r[2])
        if z:
            if "DGS10" in z and "DFII10" in z: z["BREAKEVEN10_PROXY"]=z["DGS10"]-z["DFII10"]
            out[pd.Timestamp(r[0]).strftime("%Y-%m-%d")]=z
    if len(out)<3000: raise RuntimeError(f"H15_TOO_FEW {len(out)}")
    return out,{"url":base+"?"+q,"sha256":sha(raw),"nominal_col":ncol,"real_col":rcol,
                "first":min(out),"last":max(out),"n":len(out),"source":"Federal Reserve Board H.15 DDP"}

def fetch_fx():
    h10.START="01/01/2010"; h10.END="09/29/2026"
    rr,hr=h10.fetch_package(h10.RATE_PACKAGE); ri,hi=h10.fetch_package(h10.INDEX_PACKAGE)
    rates=h10.parse_ddp(rr); idx=h10.parse_ddp(ri)
    cols={
      "EURUSD_QUOTE":h10.find_col(rates,"RXI$US_N.B.EU"),
      "GBPUSD_QUOTE":h10.find_col(rates,"RXI$US_N.B.UK"),
      "JPY_PER_USD":h10.find_col(rates,"RXI_N.B.JA"),
      "CHF_PER_USD":h10.find_col(rates,"RXI_N.B.SZ"),
      "CNY_PER_USD":h10.find_col(rates,"RXI_N.B.CH"),
      "BROAD_USD_INDEX":h10.find_col(idx,"JRXWTFB_N.B"),
    }
    out={}
    for dt in sorted(set(rates.date).union(set(idx.date))):
        z={}
        for name,col in cols.items():
            src=idx if name=="BROAD_USD_INDEX" else rates
            q=src.loc[src.date==dt,col]
            if len(q):
                v=pd.to_numeric(q.iloc[-1],errors="coerce")
                if pd.notna(v): z[name]=float(v)
        if z: out[pd.Timestamp(dt).strftime("%Y-%m-%d")]=z
    if len(out)<3000: raise RuntimeError(f"H10_TOO_FEW {len(out)}")
    return out,{"rates_sha256":hr,"index_sha256":hi,"columns":cols,
                "first":min(out),"last":max(out),"n":len(out),"source":"Federal Reserve Board H.10 DDP"}

def fetch_vix():
    raw,h=get(VIX_URL,90)
    df=pd.read_csv(io.BytesIO(raw))
    df.columns=[str(x).strip().upper() for x in df.columns]
    dc=next((x for x in df.columns if x in ("DATE","TRADE_DATE")),None)
    vc=next((x for x in df.columns if x in ("CLOSE","VIX","CLOSEPRICE","CLOSE_PRICE")),None)
    if not dc or not vc: raise RuntimeError(f"VIX_COLUMNS {list(df.columns)}")
    df["date"]=pd.to_datetime(df[dc],errors="coerce");df["value"]=pd.to_numeric(df[vc],errors="coerce")
    df=df.dropna(subset=["date","value"])
    df=df[(df.date>=pd.Timestamp(START))&(df.date<=pd.Timestamp(END))]
    out={r.date.strftime("%Y-%m-%d"):float(r.value) for r in df[["date","value"]].itertuples(index=False)}
    if len(out)<3000: raise RuntimeError(f"VIX_TOO_FEW {len(out)}")
    return out,{"url":VIX_URL,"sha256":sha(raw),"first":min(out),"last":max(out),"n":len(out),"source":"Cboe VIX history"}

def bls_block(start,end):
    payload={"seriesid":["CUUR0000SA0","CUUR0000SA0L1E"],"startyear":str(start),"endyear":str(end)}
    raw=post_json("https://api.bls.gov/publicAPI/v2/timeseries/data/",payload,90)
    d=json.loads(raw)
    if str(d.get("status"))!="REQUEST_SUCCEEDED": raise RuntimeError(f"BLS_FAIL {d.get('message')}")
    return d,sha(raw)

def fetch_cpi():
    out={}; hashes=[]
    for a,b in ((2010,2019),(2020,2026)):
        d,h=bls_block(a,b);hashes.append({"start":a,"end":b,"sha256":h})
        for s in d["Results"]["series"]:
            sid=s["seriesID"]; key="CPI_ALL_NSA" if sid=="CUUR0000SA0" else "CPI_CORE_NSA"
            for r in s["data"]:
                p=str(r["period"])
                if not p.startswith("M") or p=="M13": continue
                m=f"{int(r['year']):04d}-{int(p[1:]):02d}"
                out.setdefault(m,{})[key]=float(r["value"])
    if min(out)>"2010-01" or max(out)<"2026-08": raise RuntimeError(f"BLS_CPI_COVERAGE {min(out)} {max(out)}")
    return out,{"endpoint":"BLS Public Data API v2","chunks":hashes,"first":min(out),"last":max(out),"n":len(out),
                "source":"U.S. Bureau of Labor Statistics","revision_note":"NSA CPI index candidates; not survey-consensus surprise"}

def fetch_wb():
    raw,h=get(WB_URL,180)
    x=pd.read_excel(io.BytesIO(raw),sheet_name="Monthly Prices",header=None,engine="openpyxl")
    header_row=None
    for rr in range(min(12,len(x))):
        vals=[str(v).strip().lower() for v in x.iloc[rr].tolist()]
        if any("crude oil" in v for v in vals) and any(v=="gold" or v.startswith("gold ") for v in vals):
            header_row=rr;break
    if header_row is None: raise RuntimeError("WB_HEADER_NOT_FOUND")
    headers=[str(v).strip() for v in x.iloc[header_row].tolist()]
    targets={}
    for i,name in enumerate(headers):
        lo=name.lower()
        if "crude oil" in lo and "brent" in lo: targets["BRENT"]=i
        elif "crude oil" in lo and ("wti" in lo or "west texas" in lo): targets["WTI"]=i
        elif lo=="copper" or lo.startswith("copper "): targets["COPPER"]=i
        elif "crude oil" in lo and "average" in lo: targets["CRUDE_AVG"]=i
    if not {"BRENT","WTI"}<=set(targets): raise RuntimeError(f"WB_OIL_COLUMNS_MISSING {targets} headers={headers}")
    out={}
    for _,row in x.iterrows():
        m=re.match(r"^(\d{4})M(\d{1,2})$",str(row.iloc[0]).strip(),re.I)
        if not m: continue
        mk=f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
        if mk<"2010-01": continue
        z={}
        for k,i in targets.items():
            v=pd.to_numeric(row.iloc[i],errors="coerce")
            if pd.notna(v): z[k]=float(v)
        if z: out[mk]=z
    if min(out)>"2010-01" or max(out)<"2026-08": raise RuntimeError(f"WB_COMMODITY_COVERAGE {min(out)} {max(out)}")
    return out,{"url":WB_URL,"sha256":sha(raw),"columns":targets,"first":min(out),"last":max(out),"n":len(out),
                "source":"World Bank Pink Sheet monthly prices"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--core5",required=True)
    ap.add_argument("--output",default="gold_monthly_direct_external_store_v1.json")
    a=ap.parse_args()
    core,coremeta=load_core5(Path(a.core5))
    ndx,ndxmeta=fetch_nasdaq()
    h15,h15meta=fetch_h15()
    fx,fxmeta=fetch_fx()
    vix,vixmeta=fetch_vix()
    cpi,cpimeta=fetch_cpi()
    wb,wbmeta=fetch_wb()

    # parity: official NDX daily month averages vs locked CORE5 NASDAQ monthly averages.
    s=pd.Series(ndx,dtype=float);s.index=pd.to_datetime(s.index)
    ndx_avg={str(k):float(v) for k,v in s.groupby(s.index.to_period("M")).mean().items()}
    overlap=sorted(set(ndx_avg)&set(core))
    diffs=[abs(ndx_avg[m]-core[m]["NASDAQ_AVG_MONTHLY"]) for m in overlap if m<="2026-07"]
    parity={"n":len(diffs),"median_abs_diff":float(np.median(diffs)),"p95_abs_diff":float(np.quantile(diffs,.95)),
            "max_abs_diff":float(np.max(diffs))}
    out={
      "schema":"GOLD_MONTHLY_DIRECT_EXTERNAL_STORE_V1_2026-09-29",
      "authority":{"neon_reads":0,"role":"RAW_AND_LOW_TRANSFORM_FEATURE_RESEARCH_STORE",
        "selection_rule":"All transformations/lags selected only inside chronological DEV experiments",
        "cpi_consensus_surprise_status":"NOT_PROVEN_LONG_HISTORY; do not synthesize consensus"},
      "core5_monthly":core,"core5_meta":coremeta,
      "nasdaq100_daily":ndx,"nasdaq_meta":ndxmeta,"nasdaq_core5_parity":parity,
      "h15_daily":h15,"h15_meta":h15meta,
      "h10_daily":fx,"h10_meta":fxmeta,
      "vix_daily":vix,"vix_meta":vixmeta,
      "cpi_monthly":cpi,"cpi_meta":cpimeta,
      "commodity_monthly":wb,"commodity_meta":wbmeta,
      "readiness":{
        "metals":"READY_SEPARATE_CANONICAL_SNAPSHOT",
        "gpr":"READY_THROUGH_2026_09_VINTAGE",
        "target_gold":"READY_THROUGH_2026_08_WORLD_BANK_FINAL",
        "nasdaq100":"READY_DIRECT_GIW",
        "rates_nominal_real":"READY_FED_H15",
        "fedfunds":"READY_CORE5_MONTHLY",
        "fx":"READY_FED_H10",
        "vix":"READY_CBOE",
        "inflation_realized":"READY_BLS_NSA",
        "cpi_survey_surprise":"NOT_PROVEN_LONG_HISTORY",
        "commodity_oil":"READY_WORLD_BANK_MONTHLY",
      }
    }
    raw=json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    out["payload_sha256"]=sha(raw)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("DIRECT_EXTERNAL_STORE_GATE=PASS")
    print(json.dumps({
      "readiness":out["readiness"],"nasdaq":ndxmeta,"h15":h15meta,"h10":fxmeta,
      "vix":vixmeta,"cpi":cpimeta,"commodity":wbmeta,"nasdaq_core5_parity":parity,
      "payload_sha256":out["payload_sha256"]
    },sort_keys=True))

if __name__=="__main__":main()
