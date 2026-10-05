from __future__ import annotations
import io, json, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"OCT5_CIGD1_AUDIT_OUT"; OUT.mkdir(exist_ok=True)
os.environ.setdefault("STAK_LIVE_REF","54fdf1c8d39b7b6c7b874d0f30f784296e886044")

import gold_h3_iris_v1 as iris
import gold_h3_rift_v1 as rift
import gold_h3_vega_v1 as vega
import gold_h3_clean_v5_prospective_v1 as cv5

ORIGIN=pd.Timestamp("2026-10-02")
ISSUE=pd.Timestamp("2026-10-05")
TARGET=pd.Timestamp("2026-10-07")
IRIS_FETCH_ORIG=iris.fetch_extension

def extend_hourly():
    x,n=IRIS_FETCH_ORIG()
    vals=iris.api_request(pd.Timestamp("2026-09-30 00:00:00"),pd.Timestamp("2026-10-03 23:59:59"))
    rows=[]
    for row in vals:
        dt=row.get("datetime"); close=row.get("close")
        if dt is None or close is None: continue
        try:
            ts=pd.Timestamp(dt).tz_localize(iris.TZ,ambiguous="NaT",nonexistent="shift_forward").tz_convert("UTC")
            val=float(close)
        except Exception:
            continue
        if pd.notna(ts) and np.isfinite(val) and val>0: rows.append((ts,val))
    if rows:
        y=pd.DataFrame(rows,columns=["ts","value"])
        x=pd.concat([x,y],ignore_index=True).sort_values("ts").drop_duplicates("ts",keep="last").reset_index(drop=True)
    return x,n+1

def fetch_gvz():
    url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS&cosd=2021-01-01&coed=2026-10-02"
    r=requests.get(url,timeout=60); r.raise_for_status()
    df=pd.read_csv(io.BytesIO(r.content)).iloc[:,:2].copy()
    df.columns=["date","gvz"]; df["date"]=pd.to_datetime(df.date,errors="coerce"); df["gvz"]=pd.to_numeric(df.gvz,errors="coerce")
    df=df.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)
    return df,{"url":url,"n":int(len(df)),"min":str(df.date.min().date()),"max":str(df.date.max().date())}

def main():
    prior=json.loads((AX/"GOLD_H3_OCT5_DIAGNOSTIC_NOWCAST_2026-10-05.json").read_text())
    hist=pd.read_csv(cv5.HIST_AURORA)
    last=pd.to_datetime(hist.forecast_issue_date).max()
    tail=hist.iloc[-1]
    row={
      "feature_cutoff_date":"2026-10-02","forecast_issue_date":"2026-10-05","target_end_date_h3":"2026-10-07",
      "year":2026,"month":"2026-10","y_up":0,"target_r3":0.0,
      "p_structural":prior["aurora"]["p_structural"],"p_path_global":prior["aurora"]["p_path_global"],
      "p_sentry":prior["aurora"]["p_structural"],"p_dart":prior["aurora"]["p_up"],"p_aurora":prior["aurora"]["p_up"],
      "active_expert":prior["aurora"]["active_expert"],"matured_pair_n":int(tail.matured_pair_n),
      "net_rescue_63":int(tail.net_rescue_63),"matured_disagreements":int(tail.matured_disagreements),
      "q_path":float(tail.q_path),"prob_path_superior":float(tail.prob_path_superior)
    }
    syn=pd.concat([hist,pd.DataFrame([row])],ignore_index=True)
    with tempfile.TemporaryDirectory() as td:
        af=Path(td)/"a.csv"; syn.to_csv(af,index=False)
        iris.fetch_extension=extend_hourly
        rift.AURORA=af
        rp,_,_=rift.load_panel()
        full_r=cv5.extend(cv5.FROZEN_RIFT_PANEL,rp,last)
        rr=rift.run_rift(full_r)
        rr["feature_cutoff_date"]=pd.to_datetime(rr.feature_cutoff_date)
        r0=rr[rr.feature_cutoff_date==ORIGIN].iloc[0]
        fr=full_r.copy()
        fr["feature_cutoff_date"]=pd.to_datetime(fr.feature_cutoff_date)
        qi=fr.index[fr.feature_cutoff_date==ORIGIN]
        if len(qi)!=1: raise RuntimeError(f"RIFT_FEATURE_ROW_FAIL {len(qi)}")
        jj=int(qi[0]); h=fr.iloc[max(0,jj-120):jj]
        def erank(a,val):
            a=pd.to_numeric(a,errors="coerce").dropna().to_numpy(float)
            return float((1+np.sum(a<=val))/(len(a)+1))
        specs=[("trend_strength",-1),("session_against_trend",1),("trend_close_location",-1),("adverse_excursion",1)]
        ranks=[erank(s*pd.to_numeric(h[col],errors="coerce"),s*float(fr.iloc[jj][col])) for col,s in specs]
        susceptibility=float(np.median(ranks))
        rift_features={col:float(fr.iloc[jj][col]) for col,_ in specs}

        vega.AURORA=af; vega.fetch_gvz=fetch_gvz
        vp,_,_,_=vega.load_panel()
        full_v=cv5.extend(cv5.FROZEN_VEGA_PANEL,vp,last)
        vv=vega.run_vega(full_v)
        vv["feature_cutoff_date"]=pd.to_datetime(vv.feature_cutoff_date)
        v0=vv[vv.feature_cutoff_date==ORIGIN].iloc[0]

    out={
      "status":"DIAGNOSTIC_ONLY_INTERMEDIATE_EXPERT_AUDIT",
      "feature_cutoff_date":"2026-10-02","planned_issue_date":"2026-10-05",
      "aurora":{"p_up":float(prior["aurora"]["p_up"]),"direction":prior["aurora"]["direction"]},
      "v5":prior["v5"],
      "rift":{"p_reversal":float(r0.p_reversal),"override":bool(r0.override),"p_up":float(r0.p_rift),"direction":"UP" if float(r0.p_rift)>=.5 else "DOWN","ruleflow_susceptibility":susceptibility,"features":rift_features},
      "vega":{"p_reversal":float(v0.p_reversal),"override":bool(v0.override),"p_up":float(v0.p_vega),"direction":"UP" if float(v0.p_vega)>=.5 else "DOWN"}
    }
    (OUT/"CIGD1_AUDIT.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
