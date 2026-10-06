from __future__ import annotations
import io, json, os, time, subprocess
from pathlib import Path
import numpy as np, pandas as pd, requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"; OUT=AX/"CIG_CLOCK_SEARCH_OUT"; OUT.mkdir(exist_ok=True)
PIN="fcbf50080afdf164dae460e8e855faf3f72bb1b0"
NY="America/New_York"
HOLIDAYS={"2026-01-19","2026-02-16","2026-04-03","2026-05-25","2026-06-19","2026-07-03"}

def git_csv(path):
    s=subprocess.run(["git","show",f"{PIN}:{path}"],capture_output=True,text=True,check=True).stdout
    return pd.read_csv(io.StringIO(s))

def fetch(a,b):
    p={"symbol":"XAU/USD","interval":"1h","timezone":NY,"order":"ASC","outputsize":5000,
       "apikey":os.environ["TWELVE_DATA_API_KEY"],"start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90); j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(str(j))
    rows=[]
    for z in vals:
        try: rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"]),"close":float(z["close"])})
        except: pass
    return pd.DataFrame(rows)

def main():
    v5=git_csv("gold_axis_2026/GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv")
    rift=git_csv("gold_axis_2026/GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv")
    vega=git_csv("gold_axis_2026/GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv")
    ev=git_csv("gold_axis_2026/GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv")
    for d in [v5,rift,vega]:
        d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date); d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
    V={r.forecast_issue_date.strftime("%Y-%m-%d"):int(float(r.p_helios_v5_dce)>=.5) for r in v5.itertuples(index=False)}
    R={r.forecast_issue_date.strftime("%Y-%m-%d"):int(float(r.p_rift)>=.5) for r in rift.itertuples(index=False)}
    G={r.forecast_issue_date.strftime("%Y-%m-%d"):int(float(r.p_vega)>=.5) for r in vega.itertuples(index=False)}
    C2I={r.feature_cutoff_date.strftime("%Y-%m-%d"):r.forecast_issue_date.strftime("%Y-%m-%d") for r in v5.itertuples(index=False)}
    S=dict(V)
    for e in ev.itertuples(index=False):
        issue=C2I.get(pd.Timestamp(e.feature_cutoff_date).strftime("%Y-%m-%d"))
        if issue:S[issue]=int(e.combined_pred)

    issue_dates=sorted([d for d in V if "2026-01-02"<=d<="2026-07-31" and pd.Timestamp(d).weekday()<5 and d not in HOLIDAYS])
    assert len(issue_dates)==145, len(issue_dates)

    x=pd.concat([fetch("2025-12-15 00:00:00","2026-04-15 23:59:59"),fetch("2026-04-16 00:00:00","2026-08-02 23:59:59")],ignore_index=True)
    x=x.sort_values("dt").drop_duplicates("dt"); x["date"]=x.dt.dt.strftime("%Y-%m-%d");x["hour"]=x.dt.dt.hour
    scans=[]
    expected={"sage":103,"v5":102,"rift":102,"vega":102,"cons_n":125,"cons_correct":93,"dis_n":20,"dis_correct":10}
    for h in range(24):
        a=x[x.hour==h].sort_values("dt").reset_index(drop=True)
        amap={r.date:i for i,r in enumerate(a.itertuples(index=False))}
        rows=[]
        for d in issue_dates:
            i=amap.get(d)
            if i is None or i==0: continue
            cur=float(a.iloc[i].close); prev=float(a.iloc[i-1].close)
            actual=int(cur>prev)
            ss,vv,rr,gg=S[d],V[d],R[d],G[d]
            con=(ss==vv==rr==gg)
            rows.append((d,actual,ss,vv,rr,gg,con))
        if len(rows)!=145: continue
        sage=sum(r[2]==r[1] for r in rows); vv=sum(r[3]==r[1] for r in rows); rr=sum(r[4]==r[1] for r in rows); gg=sum(r[5]==r[1] for r in rows)
        cons=[r for r in rows if r[6]]; dis=[r for r in rows if not r[6]]
        cc=sum(r[3]==r[1] for r in cons); dc=sum(r[3]==r[1] for r in dis)
        vals={"sage":sage,"v5":vv,"rift":rr,"vega":gg,"cons_n":len(cons),"cons_correct":cc,"dis_n":len(dis),"dis_correct":dc}
        dist=sum(abs(vals[k]-expected[k]) for k in expected)
        scans.append({"hour_ny":h,**vals,"distance":dist})
    scans=sorted(scans,key=lambda z:z["distance"])
    pd.DataFrame(scans).to_csv(OUT/"hour_scan.csv",index=False)
    result={"status":"HOURLY_ANCHOR_CLOCK_SEARCH","pinned":PIN,"universe_n":145,"excluded_us_holidays":sorted(HOLIDAYS),
            "expected":expected,"top10":scans[:10],"exact_matches":[z for z in scans if z["distance"]==0]}
    (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
