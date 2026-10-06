from __future__ import annotations
import json, os, time, io, subprocess, calendar
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"; OUT=AX/"CIG_REFERENCE_CLOCK_AUDIT_OUT"; OUT.mkdir(exist_ok=True)
PIN="fcbf50080afdf164dae460e8e855faf3f72bb1b0"
NY="America/New_York"
EXACT=AX/"GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv"

def git_csv(path):
    s=subprocess.run(["git","show",f"{PIN}:{path}"],capture_output=True,text=True,check=True).stdout
    return pd.read_csv(io.StringIO(s))

def monthly_chunks(start,end):
    out=[]; cur=pd.Timestamp(start); end=pd.Timestamp(end)
    while cur<=end:
        last=pd.Timestamp(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        b=min(last,end); out.append((f"{cur.date()} 00:00:00",f"{b.date()} 23:59:59")); cur=b+pd.Timedelta(days=1)
    return out

def fetch(interval,a,b,tz):
    p={"symbol":"XAU/USD","interval":interval,"timezone":tz,"order":"ASC","outputsize":5000,
       "apikey":os.environ["TWELVE_DATA_API_KEY"],"start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
    j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(str({"interval":interval,"a":a,"b":b,"tz":tz,"resp":j}))
    rows=[]
    for z in vals:
        try: rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"]),"close":float(z["close"])})
        except: pass
    return pd.DataFrame(rows)

def diracc(rows,col):
    z=[r for r in rows if r.get(col) is not None]
    if not z:return {}
    y=np.array([1 if r[col]>0 else 0 for r in z],int)
    p=np.array([r["consensus_pred"] for r in z],int)
    return {"n":len(z),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "positive_share":float((np.array([r[col] for r in z])>0).mean()),
            "mean_return":float(np.mean([r[col] for r in z])),
            "median_return":float(np.median([r[col] for r in z]))}

def main():
    exact=pd.read_csv(EXACT)
    exact["issue_date"]=pd.to_datetime(exact.issue_date).dt.strftime("%Y-%m-%d")
    v5=git_csv("gold_axis_2026/GOLD_H3_CLEAN_V5_2026_CALL_BY_CALL_2026-10-03.csv")
    v5["forecast_issue_date"]=pd.to_datetime(v5.forecast_issue_date).dt.strftime("%Y-%m-%d")
    v5["feature_cutoff_date"]=pd.to_datetime(v5.feature_cutoff_date).dt.strftime("%Y-%m-%d")
    cutoff={r.forecast_issue_date:r.feature_cutoff_date for r in v5.itertuples(index=False)}

    # 15m NY data for exact pre/post clock decomposition.
    parts=[]
    for a,b in monthly_chunks("2025-12-15","2026-08-02"):
        parts.append(fetch("15min",a,b,NY)); time.sleep(8)
    q=pd.concat(parts,ignore_index=True).sort_values("dt").drop_duplicates("dt")
    q["ts_ny"]=q.dt.dt.tz_localize(NY,ambiguous="NaT",nonexistent="shift_forward")
    q=q[q.ts_ny.notna()].copy()
    q["ts_utc"]=q.ts_ny.dt.tz_convert("UTC")
    q["ny_date"]=q.ts_ny.dt.strftime("%Y-%m-%d")
    q["ny_hm"]=q.ts_ny.dt.strftime("%H:%M")
    q["utc_date"]=q.ts_utc.dt.strftime("%Y-%m-%d")
    q["utc_hm"]=q.ts_utc.dt.strftime("%H:%M")
    Mny={(r.ny_date,r.ny_hm):float(r.open) for r in q.itertuples(index=False)}
    Mutc={(r.utc_date,r.utc_hm):float(r.open) for r in q.itertuples(index=False)}

    # 1h UTC comparator for daily-reference semantic.
    hparts=[]
    for a,b in [("2025-12-15 00:00:00","2026-04-15 23:59:59"),("2026-04-16 00:00:00","2026-08-02 23:59:59")]:
        hparts.append(fetch("1h",a,b,"UTC")); time.sleep(8)
    h=pd.concat(hparts,ignore_index=True).sort_values("dt").drop_duplicates("dt")
    h["utc_date"]=h.dt.dt.strftime("%Y-%m-%d")
    means=h.groupby("utc_date").close.mean().sort_index()
    mean_dates=list(means.index); mean_ix={d:i for i,d in enumerate(mean_dates)}

    rows=[]
    for r in exact.itertuples(index=False):
        d=r.issue_date; c=cutoff.get(d)
        if not c: continue
        p16=Mny.get((c,"16:00"))
        p08=Mny.get((d,"08:00"))
        p0815=Mny.get((d,"08:15"))
        p20=Mny.get((d,"20:00"))
        p00=Mutc.get((d,"00:00"))
        rec={"issue_date":d,"feature_cutoff_date":c,"consensus_pred":int(r.consensus_pred),
             "actual_daily_label":int(r.actual_daily_label)}
        rec["ret_feature16_to_utc00"]=(p00/p16-1) if p16 and p00 else None
        rec["ret_utc00_to_08"]=(p08/p00-1) if p00 and p08 else None
        rec["ret_utc00_to_0815"]=(p0815/p00-1) if p00 and p0815 else None
        rec["ret_feature16_to_08"]=(p08/p16-1) if p16 and p08 else None
        rec["ret_feature16_to_0815"]=(p0815/p16-1) if p16 and p0815 else None
        rec["ret_0815_to_20"]=(p20/p0815-1) if p0815 and p20 else None
        i=mean_ix.get(d)
        if i is not None and i>0:
            rec["twelve_utc_mean_label"]=int(float(means.iloc[i])>float(means.iloc[i-1]))
            rec["twelve_utc_mean_ret"]=float(means.iloc[i]/means.iloc[i-1]-1)
        else:
            rec["twelve_utc_mean_label"]=None; rec["twelve_utc_mean_ret"]=None
        rows.append(rec)
    z=pd.DataFrame(rows); z.to_csv(OUT/"rows.csv",index=False)

    semantic=z[z.twelve_utc_mean_label.notna()].copy()
    semantic_match=float((semantic.twelve_utc_mean_label.astype(int)==semantic.actual_daily_label.astype(int)).mean())
    signal_vs_twelve=float((semantic.twelve_utc_mean_label.astype(int)==semantic.consensus_pred.astype(int)).mean())

    result={
      "status":"EXACT_125_REFERENCE_CLOCK_AUDIT",
      "n":len(z),
      "old_daily_label_accuracy":float((z.consensus_pred==z.actual_daily_label).mean()),
      "daily_reference_semantic_check":{
        "comparator":"Twelve Data 1h arithmetic mean of hourly closes per UTC calendar day",
        "n":int(len(semantic)),
        "old_label_vs_twelve_utc_mean_direction_agreement":semantic_match,
        "signal_accuracy_vs_twelve_utc_mean_direction":signal_vs_twelve
      },
      "signal_direction_by_clock_window":{
        "feature_cutoff_16NY_to_current_UTC00":diracc(rows,"ret_feature16_to_utc00"),
        "current_UTC00_to_issue_08NY":diracc(rows,"ret_utc00_to_08"),
        "current_UTC00_to_first_post_0815NY":diracc(rows,"ret_utc00_to_0815"),
        "feature_cutoff_16NY_to_issue_08NY":diracc(rows,"ret_feature16_to_08"),
        "feature_cutoff_16NY_to_first_post_0815NY":diracc(rows,"ret_feature16_to_0815"),
        "post_issue_0815_to_20NY":diracc(rows,"ret_0815_to_20")
      },
      "interpretation_guardrails":[
        "UTC00 is 03:00 Europe/Istanbul year-round.",
        "16:00 New York equals 23:00 Istanbul in US DST and 00:00 next day in US standard time.",
        "08:00 New York equals 15:00 Istanbul in US DST and 16:00 in US standard time.",
        "The old daily label is a daily-average/reference semantic, not a point-to-point clock return.",
        "Clock-window returns are diagnostics on the exact same 125 consensus rows."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
