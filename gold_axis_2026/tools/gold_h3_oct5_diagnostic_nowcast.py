from __future__ import annotations
import json, os, tempfile
from pathlib import Path
import requests
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"OCT5_DIAGNOSTIC_NOWCAST_OUT"
OUT.mkdir(exist_ok=True)

# Required before importing the frozen prospective harness.
os.environ.setdefault("STAK_LIVE_REF","54fdf1c8d39b7b6c7b874d0f30f784296e886044")

import gold_h3_aurora_prospective_v1 as base
import gold_h3_clean_aurora_prospective_v1 as clean
import gold_h3_clean_v5_prospective_v1 as cv5
import gold_h3_iris_v1 as iris
import gold_h3_vega_v1 as vega

START=pd.Timestamp("2026-09-30")
END=pd.Timestamp("2026-10-02")
ORIGIN=pd.Timestamp("2026-10-02")
SYMS={"gold":"GC=F","silver":"SI=F","platinum":"PL=F","palladium":"PA=F"}

def yahoo_chart(symbol):
    import time
    p1=int(pd.Timestamp("2026-09-28",tz="UTC").timestamp())
    p2=int(pd.Timestamp("2026-10-04",tz="UTC").timestamp())
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{requests.utils.quote(symbol,safe='')}?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true"
    r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=60)
    r.raise_for_status()
    j=r.json()
    res=j.get("chart",{}).get("result")
    if not res: raise RuntimeError(f"YAHOO_{symbol}_FAIL {j}")
    x=res[0]; ts=x.get("timestamp") or []; q=(x.get("indicators",{}).get("quote") or [{}])[0]
    close=q.get("close") or []
    out={}
    for t,c in zip(ts,close):
        if c is None: continue
        d=pd.Timestamp(t,unit="s",tz="UTC").tz_convert("America/New_York").tz_localize(None).normalize()
        if np.isfinite(float(c)): out[d]=float(c)
    return out

def build_alt_prices():
    # Extend the frozen spot curve by futures *returns*, preserving the exact
    # frozen 2026-09-29 spot level for every metal.
    frozen=pd.read_csv(AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv")
    frozen["date"]=pd.to_datetime(frozen.date)
    anchor=frozen[frozen.date==pd.Timestamp("2026-09-29")]
    if len(anchor)!=1: raise RuntimeError("FROZEN_20260929_ANCHOR_MISSING")
    anchor=anchor.iloc[0]
    fut={k:yahoo_chart(v) for k,v in SYMS.items()}
    need=[pd.Timestamp("2026-09-29"),pd.Timestamp("2026-09-30"),pd.Timestamp("2026-10-01"),pd.Timestamp("2026-10-02")]
    for k,m in fut.items():
        miss=[str(d.date()) for d in need if d not in m]
        if miss: raise RuntimeError(f"FUTURES_{k}_MISSING {miss}")
    rows=[]
    levels={k:float(anchor[k]) for k in SYMS}
    prev=pd.Timestamp("2026-09-29")
    for d in need[1:]:
        for k in SYMS:
            ret=fut[k][d]/fut[k][prev]-1.0
            levels[k]*=(1.0+ret)
        rows.append({"date":d,**levels,
                     "first_seen_stak_ref":"FUTURES_RETURN_SPLICED_DIAGNOSTIC_ONLY",
                     "first_seen_at_utc":pd.Timestamp.now(tz="UTC").isoformat()})
        prev=d
    diag={"frozen_spot_anchor":{k:float(anchor[k]) for k in SYMS},
          "futures_close":{k:{str(d.date()):fut[k][d] for d in need} for k in SYMS}}
    (OUT/"ALT_SOURCE_DIAGNOSTIC.json").write_text(json.dumps(diag,indent=2)+"\n")
    return pd.DataFrame(rows).sort_values("date")

def extend_hourly_successor():
    orig=iris.fetch_extension
    x,n=orig()
    vals=iris.api_request(pd.Timestamp("2026-09-30 00:00:00"),pd.Timestamp("2026-10-03 23:59:59"))
    rows=[]
    for row in vals:
        dt=row.get("datetime"); close=row.get("close")
        if dt is None or close is None: continue
        try:
            ts=pd.Timestamp(dt).tz_localize(iris.TZ,ambiguous="NaT",nonexistent="shift_forward").tz_convert("UTC")
            v=float(close)
        except Exception:
            continue
        if pd.notna(ts) and np.isfinite(v) and v>0: rows.append((ts,v))
    if rows:
        y=pd.DataFrame(rows,columns=["ts","value"])
        x=pd.concat([x,y],ignore_index=True).sort_values("ts").drop_duplicates("ts",keep="last").reset_index(drop=True)
    return x,n+1

def diag_fetch_gvz():
    import io
    url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS&cosd=2021-01-01&coed=2026-10-02"
    r=requests.get(url,timeout=60); r.raise_for_status()
    df=pd.read_csv(io.BytesIO(r.content)).iloc[:,:2].copy()
    df.columns=["date","gvz"]
    df["date"]=pd.to_datetime(df.date,errors="coerce")
    df["gvz"]=pd.to_numeric(df.gvz,errors="coerce")
    df=df.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)
    return df,{"url":url,"n":int(len(df)),"min":str(df.date.min().date()),"max":str(df.date.max().date())}

def run():
    alt=build_alt_prices()
    alt.to_csv(OUT/"ALT_DAILY_PRICES.csv",index=False)

    # Configure the CLEAN frozen model, but permit 2026-10-02 solely for this
    # diagnostic nowcast. This is explicitly NOT prospective evidence.
    clean.OUT=OUT
    clean.configure()
    base.OUT=OUT
    base.PROSPECTIVE_MIN_FEATURE=ORIGIN

    price_path=OUT/"DIAG_PRICE_LEDGER.csv"
    forecast_path=OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_LEDGER.csv"
    miss_path=OUT/"DIAG_AURORA_MISSES.csv"
    integ_path=OUT/"DIAG_INTEGRITY.csv"
    alt.to_csv(price_path,index=False)

    base.PRICE_LEDGER_FILE=price_path
    base.FORECAST_LEDGER_FILE=forecast_path
    base.MISS_LEDGER_FILE=miss_path
    base.INTEGRITY_LEDGER_FILE=integ_path

    base.main()
    a=pd.read_csv(forecast_path)
    a["feature_cutoff_date"]=pd.to_datetime(a.feature_cutoff_date,errors="coerce")
    ar=a[a.feature_cutoff_date==ORIGIN]
    if len(ar)!=1:
        raise RuntimeError(f"AURORA_ORIGIN_ROW_FAIL n={len(ar)}")
    ar=ar.iloc[0]

    # Run the frozen CLEAN V5-DCE chain on the same diagnostic AURORA row.
    # Extend only the research data cutoffs that were hard-coded at Sep-30.
    iris.fetch_extension=extend_hourly_successor
    vega.fetch_gvz=diag_fetch_gvz
    cv5.OUT=OUT
    cv5.AURORA_LEDGER=forecast_path
    cv5.V5_LEDGER=OUT/"DIAG_V5_LEDGER.csv"
    cv5.V5_MISSES=OUT/"DIAG_V5_MISSES.csv"
    cv5.FIRST_FEATURE=ORIGIN
    cv5.main()
    v=pd.read_csv(OUT/"DIAG_V5_LEDGER.csv")
    v["feature_cutoff_date"]=pd.to_datetime(v.feature_cutoff_date,errors="coerce")
    vr=v[v.feature_cutoff_date==ORIGIN]
    if len(vr)!=1:
        raise RuntimeError(f"V5_ORIGIN_ROW_FAIL n={len(vr)}")
    vr=vr.iloc[0]

    out={
      "status":"DIAGNOSTIC_ONLY_NOT_PROSPECTIVE_EVIDENCE",
      "feature_cutoff_date":"2026-10-02",
      "planned_issue_date":"2026-10-05",
      "alt_source":"TwelveData daily spot for 2026-09-30..2026-10-02",
      "alt_prices":alt.assign(date=alt.date.dt.strftime("%Y-%m-%d")).to_dict("records"),
      "aurora":{
        "p_up":float(ar.p_aurora),
        "direction":str(ar.direction),
        "active_expert":str(ar.active_expert),
        "p_structural":float(ar.p_structural),
        "p_path_global":float(ar.p_path_global),
        "h_ret_12":float(ar.h_ret_12),
        "h_ret_24":float(ar.h_ret_24),
        "h_ret_48":float(ar.h_ret_48),
      },
      "v5":{
        "p_up":float(vr.p_clean_v5),
        "direction":str(vr.v5_direction),
        "aurora_direction":str(vr.aurora_direction),
        "changed_from_aurora":bool(vr.changed_from_aurora),
        "candidate_reversal":bool(vr.candidate_reversal),
        "opal_override":bool(vr.opal_override),
        "p_opal_reversal":float(vr.p_opal_reversal),
        "gt_flip_share":float(vr.gt_flip_share),
        "v4_route":bool(vr.v4_route),
        "rge_active":bool(vr.rge_active),
        "dce_exception":bool(vr.dce_exception),
      }
    }
    (OUT/"OCT5_DIAGNOSTIC_NOWCAST.json").write_text(json.dumps(out,indent=2,default=str)+"\n")
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__":
    run()
