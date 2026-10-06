from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_ATTRIBUTION_OUT"; OUT.mkdir(exist_ok=True)
PANEL=AX/"GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"
NY="America/New_York"

def fetch_chunk(a,b):
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

def pxmap(x):
    return {(r.dt.strftime("%Y-%m-%d"),int(r.dt.hour)):float(r.open) for r in x.itertuples(index=False)}

def prev_trading_date(d, all_dates):
    i=all_dates.index(d)
    return all_dates[i-1] if i>0 else None

def comp(vals):
    a=np.asarray(vals,float)
    return float(np.prod(1+a)-1) if len(a) else np.nan

def period(d):
    if d<"2026-01-01": return "2025_H2"
    if d<="2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def main():
    p=pd.read_csv(PANEL)
    p["consensus"]=p.consensus.astype(str).str.lower().eq("true")
    p["state"]=np.where(~p.consensus,"UNCERTAIN",np.where(p.v5.astype(int)==1,"UP","DOWN"))
    p=p[(p.issue_date>="2025-07-01")&(p.issue_date<="2026-09-25")].copy()
    x=fetch(); M=pxmap(x)
    dates=sorted(set(x.dt.dt.strftime("%Y-%m-%d")))
    rows=[]
    # Fixed NY-clock decomposition around the 08:00 issue deadline.
    # These are economic-time buckets, not exchange-defined sessions.
    segments=[
      ("OVERNIGHT_TO_EUROPE",20,2),
      ("EUROPE_MORNING_PRE_ISSUE",2,8),
      ("US_MORNING_POST_ISSUE",8,12),
      ("US_AFTERNOON",12,17),
      ("LATE_US",17,20),
    ]
    for _,r in p.iterrows():
        d=r.issue_date
        if d not in dates: continue
        pd0=prev_trading_date(d,dates)
        if pd0 is None: continue
        out={"issue_date":d,"period":period(d),"state":r.state}
        ok=True
        # segment 1 crosses prior trading day 20 -> current 02
        a=M.get((pd0,20)); b=M.get((d,2))
        if a is None or b is None: ok=False
        else: out["OVERNIGHT_TO_EUROPE"]=b/a-1
        for name,h0,h1 in segments[1:]:
            a=M.get((d,h0)); b=M.get((d,h1))
            if a is None or b is None: ok=False; break
            out[name]=b/a-1
        # full prior 20 -> current 20 and pre/post issue
        a=M.get((pd0,20)); b=M.get((d,8)); c=M.get((d,20))
        if a is None or b is None or c is None: ok=False
        else:
            out["PRE_ISSUE_TOTAL"]=b/a-1
            out["POST_ISSUE_TOTAL"]=c/b-1
            out["FULL_20_TO_20"]=c/a-1
        if ok: rows.append(out)
    z=pd.DataFrame(rows); z.to_csv(OUT/"session_rows.csv",index=False)

    summary={}
    segcols=[s[0] for s in segments]+["PRE_ISSUE_TOTAL","POST_ISSUE_TOTAL","FULL_20_TO_20"]
    for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
        for state in ["UP","DOWN"]:
            g=z[(z.period==pp)&(z.state==state)]
            key=f"{pp}_{state}"
            summary[key]={"n":int(len(g))}
            for c in segcols:
                vals=g[c].dropna().to_numpy(float)
                summary[key][c]={
                    "compound":comp(vals),
                    "mean":float(np.mean(vals)) if len(vals) else None,
                    "median":float(np.median(vals)) if len(vals) else None,
                    "positive_share":float(np.mean(vals>0)) if len(vals) else None
                }
    # How much of total log-return is accumulated before vs after issue on UP days.
    for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
        g=z[(z.period==pp)&(z.state=="UP")]
        if len(g):
            pre=np.log1p(g.PRE_ISSUE_TOTAL).sum()
            post=np.log1p(g.POST_ISSUE_TOTAL).sum()
            full=np.log1p(g.FULL_20_TO_20).sum()
            summary[f"{pp}_UP_log_attribution"]={
                "pre_issue_log_return_sum":float(pre),
                "post_issue_log_return_sum":float(post),
                "full_log_return_sum":float(full),
                "pre_share_of_full":float(pre/full) if full!=0 else None,
                "post_share_of_full":float(post/full) if full!=0 else None
            }

    out={
      "status":"RETROSPECTIVE_SESSION_ATTRIBUTION_NOT_PROSPECTIVE",
      "issue_deadline_ny":"08:00",
      "session_definition":"fixed New York clock buckets; approximate economic sessions",
      "summary":summary,
      "interpretation_guardrail":"Pre-08:00 NY return is not executable using a signal first available at 08:00 NY; it is attribution only."
    }
    (OUT/"summary.json").write_text(json.dumps(out,indent=2,default=str)+"\n")
    print(json.dumps(out,indent=2,default=str))
if __name__=="__main__": main()
