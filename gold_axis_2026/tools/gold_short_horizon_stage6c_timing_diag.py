import os,io,json,zipfile,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
READINESS=11166972412
STAGE6C=11178394090
OUT=Path(os.environ.get("OUT_DIR","stage6c_timing_diag_out"))
OUT.mkdir(parents=True,exist_ok=True)

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    n=[x for x in z.namelist() if x.endswith(suffix)]
    if len(n)!=1: raise RuntimeError((suffix,n))
    return pd.read_csv(io.BytesIO(z.read(n[0])))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    zr=get_zip(READINESS)
    panel=read_csv(zr,"short_horizon_readiness_panel.csv")
    panel["date"]=pd.to_datetime(panel["date"])
    zc=get_zip(STAGE6C)
    g=read_csv(zc,"stage6c_gldm_yahoo_daily.csv")
    m=read_csv(zc,"stage6c_mgc_yahoo_daily.csv")
    for x in [g,m]:
        x["date"]=pd.to_datetime(x["date"])
        x["r1"]=np.log(x["adj_close"]).diff()
    base=panel[["date","gold_r1"]].copy()
    rows=[]
    for name,x in [("GLDM",g),("MGC",m)]:
        q=base.merge(x[["date","r1"]],on="date",how="inner").dropna()
        q=q[(q.date>=pd.Timestamp("2022-01-01"))&(q.date<=pd.Timestamp("2024-12-31"))].copy()
        for lag in range(-3,4):
            c=float(q["gold_r1"].corr(q["r1"].shift(lag)))
            rows.append({"instrument":name,"lag_rows":lag,"pearson_r1":c,"n":int(q[["gold_r1","r1"]].dropna().shape[0])})
    out=pd.DataFrame(rows)
    out.to_csv(OUT/"stage6c_daily_return_lag_diagnostic.csv",index=False)
    best=out.loc[out.groupby("instrument")["pearson_r1"].idxmax()].copy()
    best.to_csv(OUT/"stage6c_daily_return_best_lag.csv",index=False)
    lines=["# Stage 6C Post-Run Timing Diagnostic","",
           "This is a post-run diagnostic only. It may not promote an instrument or change Stage-6C gates.","",
           "| Instrument | Best row lag | Daily-return Pearson |",
           "|---|---:|---:|"]
    for _,r in best.iterrows():
        lines.append(f"| {r.instrument} | {int(r.lag_rows)} | {r.pearson_r1:.4f} |")
    lines += ["","Lag convention: positive lag compares BIST daily return with an earlier instrument-return row after merge/shift; this is only a timing clue, not an authorized alignment rule."]
    (OUT/"TIMING_DIAGNOSTIC.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary={"best":best.to_dict(orient="records"),"hashes":{p.name:sha(p) for p in files}}
    (OUT/"timing_diag_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("TIMING_DIAG="+json.dumps(summary,separators=(",",":")))
    print((OUT/"TIMING_DIAGNOSTIC.md").read_text())

if __name__=="__main__":
    main()
