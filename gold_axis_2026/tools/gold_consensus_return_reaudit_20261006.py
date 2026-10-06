from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"CONSENSUS_RETURN_REAUDIT_OUT"; OUT.mkdir(exist_ok=True)
PANEL=AX/"GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"
NY="America/New_York"

def td1h(a,b):
    key=os.environ["TWELVE_DATA_API_KEY"]
    p={"symbol":"XAU/USD","interval":"1h","timezone":NY,"order":"ASC","outputsize":5000,
       "apikey":key,"start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
    j=r.json()
    if not r.ok or not j.get("values"): raise RuntimeError((r.status_code,j))
    rows=[]
    for z in j["values"]:
        try: rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"])})
        except: pass
    return pd.DataFrame(rows)

def fetch():
    xs=[]
    chunks=[
      ("2025-06-25 00:00:00","2025-09-30 23:59:59"),
      ("2025-10-01 00:00:00","2025-12-31 23:59:59"),
      ("2026-01-01 00:00:00","2026-03-31 23:59:59"),
      ("2026-04-01 00:00:00","2026-06-30 23:59:59"),
      ("2026-07-01 00:00:00","2026-09-26 23:59:59"),
    ]
    for a,b in chunks:
        xs.append(td1h(a,b)); time.sleep(8)
    return pd.concat(xs).sort_values("dt").drop_duplicates("dt").reset_index(drop=True)

def first(x,t,tol=90):
    t=pd.Timestamp(t)
    z=x[(x.dt>=t)&(x.dt<=t+pd.Timedelta(minutes=tol))]
    if z.empty:return np.nan,None
    q=z.iloc[0];return float(q["open"]),q["dt"]

def comp(a):
    a=np.asarray(a,float)
    return float(np.prod(1+a)-1) if len(a) else np.nan

def period(d):
    if d<"2026-01-01": return "2025_H2"
    if d<="2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def main():
    p=pd.read_csv(PANEL)
    for c in ["consensus","cpg_up"]:
        p[c]=p[c].astype(str).str.lower().eq("true")
    p["raw_consensus_up"]=p["consensus"] & (p["v5"].astype(int)==1)
    x=fetch()

    rows=[]
    for i in range(len(p)-1):
        r=p.iloc[i]; n=p.iloc[i+1]
        p0,t0=first(x,r.available_ny); p1,t1=first(x,n.available_ny)
        if not(np.isfinite(p0) and np.isfinite(p1)): continue
        ret=p1/p0-1
        rows.append({
          "issue_date":r.issue_date,"period":period(r.issue_date),
          "raw_consensus_up":bool(r.raw_consensus_up),"cpg_up":bool(r.cpg_up),
          "entry_ts":str(t0),"exit_ts":str(t1),"ret":ret
        })
    z=pd.DataFrame(rows); z.to_csv(OUT/"all_d2d.csv",index=False)

    summary={}
    for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
        g=z[z.period==pp]
        for rule in ["raw_consensus_up","cpg_up"]:
            q=g[g[rule]]
            summary[f"{pp}_{rule}"]={
              "n":int(len(q)),"compound":comp(q.ret),"simple_sum":float(q.ret.sum()),
              "hit":float((q.ret>0).mean()) if len(q) else None,
              "mean":float(q.ret.mean()) if len(q) else None,
              "median":float(q.ret.median()) if len(q) else None,
            }
    # Also continuous-position equivalence: every interval flagged UP compounds identically.
    # Compare what CPG removed from raw consensus.
    for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
        g=z[(z.period==pp)&z.raw_consensus_up]
        kept=g[g.cpg_up]; removed=g[~g.cpg_up]
        summary[f"{pp}_cpg_removed_from_raw"]={
          "n":int(len(removed)),"compound":comp(removed.ret),"simple_sum":float(removed.ret.sum()),
          "hit":float((removed.ret>0).mean()) if len(removed) else None
        }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
