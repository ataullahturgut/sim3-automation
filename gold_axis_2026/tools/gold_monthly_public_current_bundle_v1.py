from __future__ import annotations
import argparse, hashlib, io, json, math, re, urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base

STAK_REPO="lbruton/StakTrakr"
STAK_API_REPO="lbruton/StakTrakrApi"
WB_URL="https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
METALS=base.METALS

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"gold-monthly-public-refresh/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def sha(b): return hashlib.sha256(b).hexdigest()

def parse_stak_annual(raw:bytes):
    rows=json.loads(raw)
    out=defaultdict(dict)
    for r in rows:
        m=str(r.get("metal") or "")
        if m not in METALS: continue
        ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
        if pd.isna(ts): continue
        try:v=float(r.get("spot"))
        except Exception:continue
        if not np.isfinite(v) or v<=0:continue
        out[m][ts.date().isoformat()]=v
    return out

def parse_hourly_12(raw:bytes,day:str):
    rows=json.loads(raw); out={}
    for r in rows:
        if r.get("metal") not in METALS: continue
        if str(r.get("timestamp") or "") != day+" 12:00:00": continue
        out[r["metal"]]=float(r["spot"])
    if set(out)!=set(METALS):
        raise RuntimeError(f"STAK_HOURLY_12_INCOMPLETE {day} {sorted(out)}")
    return out

def fetch_stak_extension(stak_ref,api_ref,start_day,end_day):
    years=sorted(set(range(pd.Timestamp(start_day).year,pd.Timestamp(end_day).year+1)))
    by=defaultdict(dict); annual_hashes={}
    for y in years:
        url=f"https://raw.githubusercontent.com/{STAK_REPO}/{stak_ref}/data/spot-history-{y}.json"
        raw=get_bytes(url); annual_hashes[str(y)]=sha(raw)
        q=parse_stak_annual(raw)
        for m in METALS: by[m].update(q[m])
    annual_last=max(set.intersection(*(set(by[m]) for m in METALS)))
    parity={}
    api_hashes={}
    # compare the last annual day with live API 12:00 if available
    try:
        url=f"https://raw.githubusercontent.com/{STAK_API_REPO}/{api_ref}/data/hourly/{annual_last[:4]}/{annual_last[5:7]}/{annual_last[8:10]}/12.json"
        raw=get_bytes(url); api_hashes[annual_last]=sha(raw)
        h=parse_hourly_12(raw,annual_last)
        parity={m:float(h[m]-by[m][annual_last]) for m in METALS}
    except Exception as e:
        parity={"status":f"NOT_AVAILABLE:{type(e).__name__}"}
    for d in pd.date_range(max(pd.Timestamp(start_day),pd.Timestamp(annual_last)+pd.Timedelta(days=1)),pd.Timestamp(end_day),freq="D"):
        day=d.date().isoformat()
        url=f"https://raw.githubusercontent.com/{STAK_API_REPO}/{api_ref}/data/hourly/{day[:4]}/{day[5:7]}/{day[8:10]}/12.json"
        try:
            raw=get_bytes(url)
        except Exception:
            # today's 12:00 may not exist yet; fail closed only for past dates
            if d.date() < datetime.now(timezone.utc).date():
                raise
            continue
        api_hashes[day]=sha(raw); h=parse_hourly_12(raw,day)
        for m in METALS: by[m][day]=h[m]
    common=sorted(set.intersection(*(set(by[m]) for m in METALS)))
    common=[d for d in common if start_day<=d<=end_day]
    rows=[{"date":d,**{m:float(by[m][d]) for m in METALS}} for d in common]
    return rows,{"annual_hashes":annual_hashes,"api_hourly_hashes":api_hashes,"annual_last":annual_last,"parity_hourly_minus_annual":parity}

def workbook_series(raw:bytes,series:str):
    sheets=pd.read_excel(io.BytesIO(raw),sheet_name=None,engine="xlrd")
    cand=[]
    for df in sheets.values():
        cols={str(c).strip().upper():c for c in df.columns}
        if series.upper() not in cols:continue
        date_col=cols.get("MONTH") or cols.get("DATE") or df.columns[0]
        q=df[[date_col,cols[series.upper()]]].copy();q.columns=["date","value"]
        q["date"]=pd.to_datetime(q["date"],errors="coerce");q["value"]=pd.to_numeric(q["value"],errors="coerce")
        q=q.dropna().sort_values("date").drop_duplicates("date",keep="last")
        if len(q):cand.append(q)
    if not cand:raise RuntimeError(f"GPR_SERIES_NOT_FOUND {series}")
    return max(cand,key=len)

def load_gpr_vintage_file(path:Path,origin:str,source_ref:str):
    raw=path.read_bytes()
    q=workbook_series(raw,"GPR")
    hist={pd.Timestamp(r.date).strftime("%Y-%m"):float(r.value) for r in q.itertuples()}
    if base.month_shift(origin,-1) not in hist:
        raise RuntimeError(f"GPR_REQUIRED_LAG_MISSING {origin}")
    if origin=="2026-08":
        evidence="PREVIOUS_AUDIT_CONTINUOUS_PIT_PROVEN_THROUGH_2026_08"
    elif origin=="2026-09":
        evidence="DIRECT_EXACT_VINTAGE_PRESENT_ON_2026_09_29_BEFORE_MONTH_END_ORIGIN"
    else:
        evidence="CURRENT_EXACT_VINTAGE_RETRIEVAL"
    return hist,{"origin":origin,"source_ref":source_ref,"evidence_class":evidence,"payload_sha256":sha(raw)}

def load_worldbank():
    raw=get_bytes(WB_URL,180)
    x=pd.read_excel(io.BytesIO(raw),sheet_name="Monthly Prices",header=None,engine="openpyxl")
    gold_col=None
    for rr in range(min(12,len(x))):
        for cc in range(x.shape[1]):
            v=str(x.iat[rr,cc]).strip().lower()
            if v=="gold" or v.startswith("gold "): gold_col=cc;break
        if gold_col is not None:break
    if gold_col is None:raise RuntimeError("WORLD_BANK_GOLD_COLUMN_NOT_FOUND")
    vals={}
    for _,row in x.iterrows():
        m=re.match(r"^(\d{4})M(\d{1,2})$",str(row.iloc[0]).strip(),re.I)
        if not m:continue
        v=pd.to_numeric(row.iloc[gold_col],errors="coerce")
        if pd.notna(v): vals[f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"]=float(v)
    return vals,{"url":WB_URL,"payload_sha256":sha(raw),"first":min(vals),"last":max(vals),"rows":len(vals)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dev-snapshot",required=True)
    ap.add_argument("--gpr-202608",required=True)
    ap.add_argument("--gpr-202609",required=True)
    ap.add_argument("--gpr-ref",required=True)
    ap.add_argument("--stak-ref",required=True)
    ap.add_argument("--stak-api-ref",required=True)
    ap.add_argument("--cutoff",default="2026-09-29")
    ap.add_argument("--output",default="gold_monthly_public_current_bundle_v1.json")
    a=ap.parse_args()

    b,meta=snap.load_snapshot(a.dev_snapshot)
    start="2025-01-01"
    rows,stak=fetch_stak_extension(a.stak_ref,a.stak_api_ref,start,a.cutoff)
    wb,wbmeta=load_worldbank()
    gpr={}
    gmeta={}
    gpr["2026-08"],gmeta["2026-08"]=load_gpr_vintage_file(Path(a.gpr_202608),"2026-08",a.gpr_ref)
    gpr["2026-09"],gmeta["2026-09"]=load_gpr_vintage_file(Path(a.gpr_202609),"2026-09",a.gpr_ref)

    # Quality gates
    if wbmeta["last"] < "2026-08": raise RuntimeError(f"WORLD_BANK_AUGUST_NOT_AVAILABLE {wbmeta}")
    if "2026-08" not in wb: raise RuntimeError("WORLD_BANK_AUGUST_GOLD_MISSING")
    common_dates=[r["date"] for r in rows]
    if max(common_dates) < "2026-09-28": raise RuntimeError(f"PUBLIC_METAL_COVERAGE_TOO_SHORT {max(common_dates)}")
    if min(common_dates) > "2025-01-02": raise RuntimeError(f"PUBLIC_METAL_HISTORY_START_LATE {min(common_dates)}")

    # Compare public 2025/2026 line with old August reconstruction where possible only by provenance metadata;
    # do not mutate dev snapshot.
    out={
      "schema":"GOLD_MONTHLY_PUBLIC_CURRENT_BUNDLE_V1_2026-09-29",
      "authority":{
        "neon_reads":0,
        "dev_snapshot_schema":meta["schema_version"],
        "dev_snapshot_payload_sha256":meta["payload_sha256"],
        "role":"PUBLIC_EXTENSION_FOR_FORWARD_RESEARCH_ONLY",
        "forecast_targets":["2026-09","2026-10"],
        "october_role":"PROVISIONAL_UNTIL_SEPTEMBER_MONTH_END_COMPLETE",
      },
      "cutoff_requested":a.cutoff,
      "daily_extension_rows":rows,
      "daily_extension_first":min(common_dates),
      "daily_extension_last":max(common_dates),
      "staktrakr":{"repo_ref":a.stak_ref,"api_repo_ref":a.stak_api_ref,**stak},
      "world_bank":{"gold_monthly":{k:v for k,v in wb.items() if k>="2025-01"},**wbmeta},
      "gpr_vintages":gpr,
      "gpr_meta":gmeta,
    }
    raw=json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    out["payload_sha256"]=sha(raw)
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("PUBLIC_CURRENT_BUNDLE_GATE=PASS")
    print(json.dumps({
      "daily_first":out["daily_extension_first"],"daily_last":out["daily_extension_last"],
      "daily_n":len(rows),"wb_last":wbmeta["last"],"wb_aug_gold":wb["2026-08"],
      "gpr_origins":sorted(gpr),"payload_sha256":out["payload_sha256"],
      "stak_parity":stak["parity_hourly_minus_annual"]
    },sort_keys=True))

if __name__=="__main__":
    main()
