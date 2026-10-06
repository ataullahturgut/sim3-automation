from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"RAW_CIG_TIMING_SCAN_OUT"; OUT.mkdir(exist_ok=True)
PANEL=AX/"GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"
NY="America/New_York"

def fetch_chunk(a,b):
    key=os.environ["TWELVE_DATA_API_KEY"]
    p={"symbol":"XAU/USD","interval":"1h","timezone":NY,"order":"ASC","outputsize":5000,
       "apikey":key,"start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90); j=r.json()
    if not r.ok or not j.get("values"): raise RuntimeError((r.status_code,j))
    rows=[]
    for z in j["values"]:
        try: rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"])})
        except: pass
    return pd.DataFrame(rows)
def fetch():
    chunks=[
      ("2025-06-25 00:00:00","2025-09-30 23:59:59"),
      ("2025-10-01 00:00:00","2025-12-31 23:59:59"),
      ("2026-01-01 00:00:00","2026-03-31 23:59:59"),
      ("2026-04-01 00:00:00","2026-06-30 23:59:59"),
      ("2026-07-01 00:00:00","2026-09-26 23:59:59")]
    xs=[]
    for a,b in chunks:
        xs.append(fetch_chunk(a,b)); time.sleep(8)
    return pd.concat(xs).sort_values("dt").drop_duplicates("dt").reset_index(drop=True)
def first(x,t,tol=90):
    t=pd.Timestamp(t); z=x[(x.dt>=t)&(x.dt<=t+pd.Timedelta(minutes=tol))]
    if z.empty:return np.nan,None
    q=z.iloc[0]; return float(q["open"]),q["dt"]
def at_hour(x,d,h):
    t=pd.Timestamp(f"{d} {h:02d}:00:00"); z=x[x.dt==t]
    if z.empty:return np.nan,None
    q=z.iloc[0]; return float(q["open"]),q["dt"]
def comp(a): return float(np.prod(1+np.asarray(a,float))-1) if len(a) else np.nan
def period(d):
    if d<"2026-01-01":return "2025_H2"
    if d<="2026-07-31":return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def main():
    p=pd.read_csv(PANEL)
    p["consensus"]=p.consensus.astype(str).str.lower().eq("true")
    p["raw_up"]=p.consensus & (p.v5.astype(int)==1)
    x=fetch()
    rows=[]
    for delay in range(0,13):
      for eh in range(0,24):
        rr=[]
        for _,r in p[p.raw_up].iterrows():
            p0,t0=first(x,pd.Timestamp(r.available_ny)+pd.Timedelta(hours=delay))
            p1,t1=at_hour(x,r.issue_date,eh)
            if np.isfinite(p0) and np.isfinite(p1) and t1>t0:
                rr.append((r.issue_date,period(r.issue_date),p1/p0-1))
        if len(rr)<20:continue
        z=pd.DataFrame(rr,columns=["date","period","ret"])
        o={"delay_h":delay,"exit_hour":eh,"n":len(z),"all_compound":comp(z.ret)}
        for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
            g=z[z.period==pp]
            o[pp+"_n"]=len(g); o[pp+"_compound"]=comp(g.ret); o[pp+"_hit"]=float((g.ret>0).mean()) if len(g) else np.nan
        rows.append(o)
    s=pd.DataFrame(rows)
    s.to_csv(OUT/"scan.csv",index=False)
    # choose ONLY on 2025_H2
    dev=s[(s["2025_H2_n"]>=60)&(s["2025_H2_hit"]>=0.60)].sort_values(["2025_H2_compound","2025_H2_hit"],ascending=False)
    best=dev.iloc[0].to_dict() if len(dev) else None
    # nearby top 20
    dev.head(30).to_csv(OUT/"dev_top.csv",index=False)
    summary={"status":"RETROSPECTIVE_RAW_CIG_TIMING_SCAN_NOT_PROSPECTIVE",
             "selection":"2025_H2_ONLY","best_2025H2":best,
             "warning":"Chosen on 2025H2; 2026 columns are transport diagnostics, not selection."}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))
if __name__=="__main__": main()
