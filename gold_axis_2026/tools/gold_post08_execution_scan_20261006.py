from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"POST08_EXECUTION_SCAN_OUT"; OUT.mkdir(exist_ok=True)
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
def pxmap(x):
    return {(r.dt.strftime("%Y-%m-%d"),r.dt.hour):float(r.open) for r in x.itertuples(index=False)}
def comp(a): return float(np.prod(1+np.asarray(a,float))-1) if len(a) else np.nan
def period(d):
    if d<"2026-01-01": return "2025_H2"
    if d<="2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def main():
    p=pd.read_csv(PANEL)
    p["consensus"]=p.consensus.astype(str).str.lower().eq("true")
    p["state"]=np.where(~p.consensus,"UNCERTAIN",np.where(p.v5.astype(int)==1,"UP","DOWN"))
    p=p[(p.issue_date>="2025-07-01")&(p.issue_date<="2026-09-25")].reset_index(drop=True)
    x=fetch(); M=pxmap(x)
    rows=[]
    # Issue deadline is 08:00 NY. To avoid using the 08:00 bar open as if tradable
    # before computation completes, earliest 1h execution is 09:00 NY.
    for ent in range(9,20):
      for ex in range(ent+1,21):
        rec=[]
        for _,r in p[p.state=="UP"].iterrows():
            a=M.get((r.issue_date,ent)); b=M.get((r.issue_date,ex))
            if a is None or b is None: continue
            rec.append((r.issue_date,period(r.issue_date),b/a-1))
        if not rec: continue
        z=pd.DataFrame(rec,columns=["date","period","ret"])
        o={"entry_hour_ny":ent,"exit_hour_ny":ex,"n":len(z),"all_compound":comp(z.ret)}
        for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
            g=z[z.period==pp]
            o[pp+"_n"]=len(g); o[pp+"_compound"]=comp(g.ret)
            o[pp+"_hit"]=float((g.ret>0).mean()) if len(g) else np.nan
            o[pp+"_mean"]=float(g.ret.mean()) if len(g) else np.nan
        rows.append(o)
    s=pd.DataFrame(rows)
    s.to_csv(OUT/"same_day_scan_1h.csv",index=False)
    dev=s[s["2025_H2_n"]>=60].sort_values(["2025_H2_compound","2025_H2_hit"],ascending=False)
    dev.head(30).to_csv(OUT/"same_day_dev_top.csv",index=False)

    # DOWN days: choose a sell/exit hour after the 08:00 signal.
    # Compare that sale to 20:00 NY. Positive avoided return means the earlier sale
    # avoided a subsequent decline into 20:00.
    down_rows=[]
    for sell_h in range(9,20):
        rec=[]
        for _,r in p[p.state=="DOWN"].iterrows():
            a=M.get((r.issue_date,sell_h)); b=M.get((r.issue_date,20))
            if a is None or b is None: continue
            rec.append((r.issue_date,period(r.issue_date),a/b-1))
        if not rec: continue
        z=pd.DataFrame(rec,columns=["date","period","avoided"])
        o={"sell_hour_ny":sell_h,"n":len(z),"all_compound_avoided":comp(z.avoided)}
        for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
            g=z[z.period==pp]
            o[pp+"_n"]=len(g); o[pp+"_compound_avoided"]=comp(g.avoided)
            o[pp+"_hit"]=float((g.avoided>0).mean()) if len(g) else np.nan
            o[pp+"_mean_avoided"]=float(g.avoided.mean()) if len(g) else np.nan
        down_rows.append(o)
    ds=pd.DataFrame(down_rows)
    ds.to_csv(OUT/"down_exit_scan_1h.csv",index=False)
    ddev=ds[ds["2025_H2_n"]>=30].sort_values(["2025_H2_compound_avoided","2025_H2_hit"],ascending=False)
    ddev.head(20).to_csv(OUT/"down_exit_dev_top.csv",index=False)

    # Decision-to-next-issue: enter after issue on an UP day, hold to next issue;
    # use 09:00 on both ends as causal hourly approximation.
    nxt=[]
    for i in range(len(p)-1):
        r=p.iloc[i]; n=p.iloc[i+1]
        if r.state!="UP": continue
        a=M.get((r.issue_date,9)); b=M.get((n.issue_date,9))
        if a is None or b is None: continue
        nxt.append({"date":r.issue_date,"period":period(r.issue_date),"ret":b/a-1})
    nd=pd.DataFrame(nxt); nd.to_csv(OUT/"next_issue_0900.csv",index=False)
    ndsum={}
    for pp,g in nd.groupby("period"):
        ndsum[pp]={"n":len(g),"compound":comp(g.ret),"hit":float((g.ret>0).mean())}

    best=dev.iloc[0].to_dict() if len(dev) else None
    # robust among windows positive in all periods, maximizing minimum period return
    rb=s[(s["2025_H2_compound"]>0)&(s["2026_JAN_JUL_compound"]>0)&(s["2026_AUG_SEP_compound"]>0)].copy()
    if len(rb):
        rb["worst"]=rb[["2025_H2_compound","2026_JAN_JUL_compound","2026_AUG_SEP_compound"]].min(axis=1)
        rb=rb.sort_values(["worst","2025_H2_compound"],ascending=False)
        robust=rb.iloc[0].to_dict()
    else: robust=None
    summary={
      "status":"RETROSPECTIVE_POST08_EXECUTION_SCAN_NOT_PROSPECTIVE",
      "issue_deadline_ny":"08:00",
      "earliest_hourly_execution_ny":"09:00",
      "rule":"Only raw CIG-D1 4/4 UP days are eligible; no CPG/TRES filtering.",
      "best_selected_on_2025H2_only":best,
      "best_down_exit_selected_on_2025H2_only":ddev.iloc[0].to_dict() if len(ddev) else None,
      "robust_positive_all_periods":robust,
      "next_issue_0900":ndsum,
      "warning":"Same-day timing is selected on 2025H2 only. 2026 is transport evidence. Hourly bars are proxies; 15-minute refinement must use first bar strictly after 08:00."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))
if __name__=="__main__": main()
