from __future__ import annotations
import json, os, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"EXECUTION_TIMING_V2_OUT"; OUT.mkdir(exist_ok=True)
NY="America/New_York"
CPG_TRES_THRESHOLD=0.164484

V5_FILE=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
RIFT_FILE=AX/"GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
VEGA_FILE=AX/"GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
SAGE_FILE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
TRES_FILE=AX/"GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv"
RF_FILE=AX/"GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv"

def truth(v):
    if isinstance(v,bool): return v
    return str(v).strip().lower() in {"true","1","yes"}

def get_td(interval,start,end):
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not key: raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    p={"symbol":"XAU/USD","interval":interval,"timezone":NY,"order":"ASC","outputsize":5000,
       "apikey":key,"start_date":start,"end_date":end}
    last=None
    for k in range(5):
        r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
        try: j=r.json()
        except Exception: j={"message":r.text[:300]}
        if r.status_code==429 or (isinstance(j,dict) and j.get("code")==429):
            time.sleep(65); continue
        vals=j.get("values") if isinstance(j,dict) else None
        if r.ok and vals:
            rows=[]
            for z in vals:
                try:
                    rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"]),"close":float(z["close"])})
                except: pass
            return pd.DataFrame(rows)
        last=(r.status_code,j)
        break
    raise RuntimeError(f"TD_FAIL {interval} {start} {end} {last}")

def fetch_1h_history():
    chunks=[
      ("2025-06-25 00:00:00","2025-09-30 23:59:59"),
      ("2025-10-01 00:00:00","2025-12-31 23:59:59"),
      ("2026-01-01 00:00:00","2026-03-31 23:59:59"),
      ("2026-04-01 00:00:00","2026-06-30 23:59:59"),
      ("2026-07-01 00:00:00","2026-09-26 23:59:59"),
    ]
    xs=[]
    for a,b in chunks:
        xs.append(get_td("1h",a,b)); time.sleep(8)
    x=pd.concat(xs,ignore_index=True).sort_values("dt").drop_duplicates("dt",keep="last").reset_index(drop=True)
    return x

def fetch_15m_current():
    a=get_td("15min","2026-08-01 00:00:00","2026-08-31 23:59:59"); time.sleep(8)
    b=get_td("15min","2026-09-01 00:00:00","2026-09-26 23:59:59")
    return pd.concat([a,b],ignore_index=True).sort_values("dt").drop_duplicates("dt",keep="last").reset_index(drop=True)

def build_panel():
    v5=pd.read_csv(V5_FILE); rift=pd.read_csv(RIFT_FILE); vega=pd.read_csv(VEGA_FILE)
    sage=pd.read_csv(SAGE_FILE); tres=pd.read_csv(TRES_FILE); rf=pd.read_csv(RF_FILE)
    for z in [v5,rift,vega,sage,tres]:
        for c in ["feature_cutoff_date","forecast_issue_date"]:
            if c in z.columns: z[c]=pd.to_datetime(z[c]).dt.strftime("%Y-%m-%d")
    V=v5.set_index("forecast_issue_date")
    R=rift.set_index("forecast_issue_date")
    G=vega.set_index("forecast_issue_date")
    S=sage.set_index("forecast_issue_date")
    T=tres.set_index("forecast_issue_date")
    rf_dates=set(rf.loc[rf["v3_candidate"].map(truth),"date"].astype(str))
    dates=sorted(d for d in V.index.unique() if "2025-07-01"<=d<="2026-09-25" and d in R.index and d in G.index and d in T.index)
    rows=[]
    for d in dates:
        vr=V.loc[d]; rr=R.loc[d]; gr=G.loc[d]; tr=T.loc[d]
        if isinstance(vr,pd.DataFrame): vr=vr.iloc[-1]
        if isinstance(rr,pd.DataFrame): rr=rr.iloc[-1]
        if isinstance(gr,pd.DataFrame): gr=gr.iloc[-1]
        if isinstance(tr,pd.DataFrame): tr=tr.iloc[-1]
        cutoff=str(vr["feature_cutoff_date"])
        v=int(float(vr["p_helios_v5_dce"])>=0.5)
        r=int(float(rr["p_rift"])>=0.5)
        g=int(float(gr["p_vega"])>=0.5)
        sage_exception=False
        sage_present=d in S.index
        if sage_present:
            sr=S.loc[d]
            if isinstance(sr,pd.DataFrame): sr=sr.iloc[-1]
            follows=int(sr["v5_pred"])==int(sr["momentum_up"])
            sage_exception=bool(
              follows and float(sr["ifbc_count60"])>=4 and float(sr["ifbc_score"])>=0.70 and
              truth(sr["llrs_external_opposes"]) and float(sr["llrs_incremental"])>0 and float(sr["llrs_pressure"])>=0.10
            )
        ruleflow_exception=cutoff in rf_dates
        s=1-v if (sage_exception or ruleflow_exception) else v
        frev=float(tr["F_reversal"])
        consensus=(s==v==r==g)
        cpg=bool(consensus and v==1 and frev<CPG_TRES_THRESHOLD)
        # Full UTC-day daily average for feature_cutoff_date completes at next UTC midnight.
        avail=(pd.Timestamp(cutoff,tz="UTC")+pd.Timedelta(days=1)).tz_convert(NY).tz_localize(None)
        rows.append({"issue_date":d,"feature_cutoff_date":cutoff,"available_ny":str(avail),
                     "sage":s,"v5":v,"rift":r,"vega":g,"sage_present":sage_present,
                     "sage_exception":sage_exception,"ruleflow_exception":ruleflow_exception,
                     "F_reversal":frev,"consensus":consensus,"cpg_up":cpg})
    return pd.DataFrame(rows)

def first_at_or_after(x,target,tol_minutes=90):
    target=pd.Timestamp(target)
    z=x[(x.dt>=target)&(x.dt<=target+pd.Timedelta(minutes=tol_minutes))]
    if z.empty: return np.nan,None
    q=z.iloc[0]; return float(q["open"]),q["dt"]

def exact_hour(x,d,h):
    target=pd.Timestamp(f"{d} {h:02d}:00:00")
    z=x[x.dt==target]
    if z.empty: return np.nan,None
    q=z.iloc[0]; return float(q["open"]),q["dt"]

def comp(rs):
    a=np.array([float(v) for v in rs if np.isfinite(v)])
    return float(np.prod(1+a)-1) if len(a) else np.nan

def period(d):
    if d<"2026-01-01": return "2025_H2"
    if d<="2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def eval_with_1h(panel,x):
    # Natural decision-to-decision at earliest complete data availability.
    d2d=[]
    for i,row in panel.iloc[:-1].iterrows():
        if not bool(row.cpg_up): continue
        nxt=panel.iloc[i+1]
        p0,t0=first_at_or_after(x,pd.Timestamp(row.available_ny),90)
        p1,t1=first_at_or_after(x,pd.Timestamp(nxt.available_ny),90)
        if np.isfinite(p0) and np.isfinite(p1):
            d2d.append({"issue_date":row.issue_date,"period":period(row.issue_date),"entry_ts":str(t0),"exit_ts":str(t1),"ret":p1/p0-1})
    d2d=pd.DataFrame(d2d)

    # Fixed issue-day exit scan; entry delay is hours after earliest data-ready time.
    scan=[]
    for delay_h in [0,1,2,3,4,6,8,12]:
      for exit_h in range(8,21):
        recs=[]
        for _,row in panel[panel.cpg_up].iterrows():
            target=pd.Timestamp(row.available_ny)+pd.Timedelta(hours=delay_h)
            p0,t0=first_at_or_after(x,target,90)
            p1,t1=exact_hour(x,row.issue_date,exit_h)
            if np.isfinite(p0) and np.isfinite(p1) and t1>t0:
                recs.append((row.issue_date,period(row.issue_date),p1/p0-1))
        if not recs: continue
        z=pd.DataFrame(recs,columns=["date","period","ret"])
        vals={"entry_delay_h":delay_h,"exit_hour_ny":exit_h,"n":len(z),"all_compound":comp(z.ret)}
        for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
            zz=z[z.period==pp]
            vals[pp+"_n"]=len(zz); vals[pp+"_compound"]=comp(zz.ret)
            vals[pp+"_hit"]=float((zz.ret>0).mean()) if len(zz) else np.nan
        scan.append(vals)
    scan=pd.DataFrame(scan)
    # Selection using ONLY 2025 H2: maximize compound, require >=60% hit and >=15 trades.
    dev=scan[(scan["2025_H2_n"]>=15)&(scan["2025_H2_hit"]>=0.60)].sort_values(
      ["2025_H2_compound","2025_H2_hit"],ascending=False)
    dev_best=dev.iloc[0].to_dict() if len(dev) else None
    # Robust selection: positive in all 3 periods, then maximize worst-period compound.
    rob=scan[(scan["2025_H2_compound"]>0)&(scan["2026_JAN_JUL_compound"]>0)&(scan["2026_AUG_SEP_compound"]>0)].copy()
    if len(rob):
        rob["worst_period"]=rob[["2025_H2_compound","2026_JAN_JUL_compound","2026_AUG_SEP_compound"]].min(axis=1)
        rob=rob.sort_values(["worst_period","all_compound"],ascending=False)
        robust_best=rob.iloc[0].to_dict()
    else: robust_best=None
    return d2d,scan,dev_best,robust_best

def eval_current_15m(panel,x):
    zpan=panel[(panel.issue_date>="2026-08-04")&(panel.issue_date<="2026-09-25")].reset_index(drop=True)
    # Scan realistic delays after earliest availability through issue-day 20:00 in 15m grid.
    rows=[]
    for delay_min in [0,15,30,45,60,90,120]:
      for h in range(8,21):
        for m in [0,15,30,45]:
          hh=f"{h:02d}:{m:02d}"
          rs=[]
          for _,row in zpan[zpan.cpg_up].iterrows():
            target=pd.Timestamp(row.available_ny)+pd.Timedelta(minutes=delay_min)
            p0,t0=first_at_or_after(x,target,20)
            target1=pd.Timestamp(f"{row.issue_date} {hh}:00")
            p1,t1=first_at_or_after(x,target1,20)
            if np.isfinite(p0) and np.isfinite(p1) and t1>t0: rs.append(p1/p0-1)
          if len(rs)>=8:
            rows.append({"delay_min":delay_min,"exit_ny":hh,"n":len(rs),"compound":comp(rs),"hit":float(np.mean(np.array(rs)>0)),
                         "mean":float(np.mean(rs)),"min_trade":float(np.min(rs)),"max_trade":float(np.max(rs))})
    scan=pd.DataFrame(rows).sort_values(["compound","hit"],ascending=False)
    # Natural decision-to-decision at earliest causal availability.
    d2d=[]
    for i,row in zpan.iloc[:-1].iterrows():
        if not bool(row.cpg_up): continue
        nxt=zpan.iloc[i+1]
        p0,t0=first_at_or_after(x,pd.Timestamp(row.available_ny),20)
        p1,t1=first_at_or_after(x,pd.Timestamp(nxt.available_ny),20)
        if np.isfinite(p0) and np.isfinite(p1):
            d2d.append({"issue_date":row.issue_date,"entry_ts":str(t0),"exit_ts":str(t1),"ret":p1/p0-1})
    return pd.DataFrame(d2d),scan

def main():
    panel=build_panel()
    x1=fetch_1h_history()
    d2d1,scan1,dev_best,robust_best=eval_with_1h(panel,x1)
    x15=fetch_15m_current()
    d2d15,scan15=eval_current_15m(panel,x15)

    panel.to_csv(OUT/"signal_panel_corrected.csv",index=False)
    d2d1.to_csv(OUT/"d2d_earliest_1h.csv",index=False)
    scan1.to_csv(OUT/"fixed_exit_scan_1h.csv",index=False)
    d2d15.to_csv(OUT/"d2d_earliest_15m_augsep.csv",index=False)
    scan15.to_csv(OUT/"fixed_exit_scan_15m_augsep.csv",index=False)

    period_counts=panel.groupby(panel.issue_date.map(period)).cpg_up.sum().astype(int).to_dict()
    d2d_period={}
    if len(d2d1):
      for pp,g in d2d1.groupby("period"):
        d2d_period[pp]={"n":len(g),"compound":comp(g.ret),"hit":float((g.ret>0).mean())}
    cur_sig=panel[(panel.issue_date>="2026-08-04")&(panel.issue_date<="2026-09-25")&panel.cpg_up].issue_date.tolist()
    summary={
      "status":"RETROSPECTIVE_EXECUTION_TIMING_AUDIT_V2_NOT_PROSPECTIVE_EVIDENCE",
      "critical_corrections":[
        "CPG F_reversal is joined from complete TRES Stage1 predictions for every issue date; missing SAGE no longer bypasses CPG.",
        "Earliest complete signal availability is based on full UTC-day daily-average semantics: next UTC midnight after feature_cutoff_date, converted to New York time.",
        "Feature-cutoff date, not previous 24h spot-calendar date, anchors pre-issue execution."
      ],
      "cpg_threshold":CPG_TRES_THRESHOLD,
      "period_signal_counts":period_counts,
      "augsep_corrected_signal_dates":cur_sig,
      "earliest_availability_d2d_1h_by_period":d2d_period,
      "dev_selected_on_2025H2_only":dev_best,
      "robust_positive_all_periods":robust_best,
      "augsep_15m_natural_d2d":{"n":len(d2d15),"compound":comp(d2d15.ret) if len(d2d15) else None,"hit":float((d2d15.ret>0).mean()) if len(d2d15) else None},
      "augsep_15m_raw_best_fixed_exit":scan15.iloc[0].to_dict() if len(scan15) else None,
      "warning":"Timing scans are retrospective. The 2025H2-selected window is the cleaner transport test; the Aug-Sep raw best is discovery-only."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
