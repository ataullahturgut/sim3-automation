from __future__ import annotations
import json, os, time, calendar
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"EXECUTION_15M_TIMING_OUT"; OUT.mkdir(exist_ok=True)
PANEL=AX/"GOLD_EXECUTION_TIMING_AUDIT_V2_SIGNAL_PANEL_2026-10-06.csv"
NY="America/New_York"

def chunks():
    out=[]; cur=pd.Timestamp("2025-06-30"); end=pd.Timestamp("2026-09-27")
    while cur<=end:
        last=pd.Timestamp(cur.year,cur.month,calendar.monthrange(cur.year,cur.month)[1])
        b=min(last,end)
        out.append((str(cur.date())+" 00:00:00",str(b.date())+" 23:59:59"))
        cur=b+pd.Timedelta(days=1)
    return out

def fetch(a,b):
    p={"symbol":"XAU/USD","interval":"15min","timezone":"America/New_York","order":"ASC",
       "outputsize":5000,"apikey":os.environ["TWELVE_DATA_API_KEY"],
       "start_date":a,"end_date":b}
    r=requests.get("https://api.twelvedata.com/time_series",params=p,timeout=90)
    j=r.json(); vals=j.get("values") or []
    if not vals: raise RuntimeError(str({"a":a,"b":b,"status":r.status_code,"response":j}))
    rows=[]
    for z in vals:
        try:
            rows.append({"dt":pd.Timestamp(z["datetime"]),"open":float(z["open"])})
        except: pass
    return pd.DataFrame(rows), {"start":a,"end":b,"rows":len(rows)}

def compound(v):
    a=np.asarray(v,float)
    return float(np.prod(1+a)-1) if len(a) else np.nan

def maxdd(v):
    w=1.0; pk=1.0; dd=0.0
    for r in v:
        w*=1+float(r); pk=max(pk,w); dd=min(dd,w/pk-1)
    return float(dd)

def period(d):
    if d<"2026-01-01": return "2025_H2"
    if d<="2026-07-31": return "2026_JAN_JUL"
    return "2026_AUG_SEP"

def hmgrid(a="08:00",b="20:00"):
    return pd.date_range("2000-01-01 "+a,"2000-01-01 "+b,freq="15min").strftime("%H:%M").tolist()

def metrics(rs):
    rs=np.asarray(rs,float)
    return {
      "n":int(len(rs)),"compound":compound(rs),"mean":float(rs.mean()) if len(rs) else None,
      "median":float(np.median(rs)) if len(rs) else None,
      "hit":float((rs>0).mean()) if len(rs) else None,
      "max_drawdown":maxdd(rs) if len(rs) else None,
      "worst":float(rs.min()) if len(rs) else None,
      "best":float(rs.max()) if len(rs) else None
    }

def main():
    sig=pd.read_csv(PANEL)
    sig["consensus"]=sig.consensus.astype(str).str.lower().eq("true")
    sig=sig[(sig.issue_date>="2025-07-01")&(sig.issue_date<="2026-09-25")].copy()
    sig["state"]=np.where(~sig.consensus,"UNCERTAIN",np.where(sig.v5.astype(int)==1,"UP","DOWN"))

    parts=[]
    for a,b in chunks():
        q,_=fetch(a,b); parts.append(q); time.sleep(8)
    x=pd.concat(parts,ignore_index=True).sort_values("dt").drop_duplicates("dt")
    x["date"]=x.dt.dt.strftime("%Y-%m-%d"); x["hm"]=x.dt.dt.strftime("%H:%M")
    by={(r.date,r.hm):float(r.open) for r in x.itertuples(index=False)}

    grid=hmgrid()
    # 1) Forward 1h and 2h clock maps for start/acceleration/giveback diagnostics.
    frows=[]
    for st in ["UP","DOWN"]:
      dlist=sig[(sig.consensus)&(sig.state==st)].issue_date.astype(str).tolist()
      for i,hm in enumerate(grid):
        for horizon in [60,120]:
          j=i+horizon//15
          if j>=len(grid): continue
          hm2=grid[j]
          rec=[]
          for d in dlist:
            a=by.get((d,hm)); b=by.get((d,hm2))
            if a is not None and b is not None: rec.append((d,b/a-1))
          for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
            v=[r for d,r in rec if period(d)==pp]
            if not v: continue
            m=metrics(v)
            frows.append({"state":st,"period":pp,"start_ny":hm,"end_ny":hm2,
                          "horizon_min":horizon,**m})
    fw=pd.DataFrame(frows)
    fw.to_csv(OUT/"forward_clock_map.csv",index=False)

    # 2) UP entry/exit windows, selected ONLY on 2025 H2 with jitter robustness.
    updays=sig[(sig.consensus)&(sig.state=="UP")].issue_date.astype(str).tolist()
    wrows=[]
    for i,en in enumerate(grid[:-1]):
      for j in range(i+4,len(grid)): # >=60m hold
        ex=grid[j]
        rec=[]
        for d in updays:
          a=by.get((d,en)); b=by.get((d,ex))
          if a is not None and b is not None: rec.append((d,b/a-1))
        row={"entry_ny":en,"exit_ny":ex,"hold_min":(j-i)*15}
        for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
          v=[r for d,r in rec if period(d)==pp]; m=metrics(v)
          for k,val in m.items(): row[pp+"_"+k]=val
        wrows.append(row)
    ws=pd.DataFrame(wrows)

    # jitter robustness on dev: +/-30m entry and exit around each candidate
    idx={hm:i for i,hm in enumerate(grid)}
    robust=[]
    lookup={(r.entry_ny,r.exit_ny):r for r in ws.itertuples(index=False)}
    for r in ws.itertuples(index=False):
        i=idx[r.entry_ny]; j=idx[r.exit_ny]
        vals=[]
        for di in [-2,-1,0,1,2]:
          for dj in [-2,-1,0,1,2]:
            ii=i+di; jj=j+dj
            if ii<0 or jj>=len(grid) or jj-ii<4: continue
            rr=lookup.get((grid[ii],grid[jj]))
            if rr is not None and rr._asdict()["2025_H2_n"]>=65:
                vals.append(rr._asdict()["2025_H2_compound"])
        robust.append({
          "entry_ny":r.entry_ny,"exit_ny":r.exit_ny,
          "dev_jitter_n":len(vals),
          "dev_jitter_median_compound":float(np.median(vals)) if vals else np.nan,
          "dev_jitter_min_compound":float(np.min(vals)) if vals else np.nan,
          "dev_jitter_positive_share":float(np.mean(np.asarray(vals)>0)) if vals else np.nan
        })
    rb=pd.DataFrame(robust)
    ws=ws.merge(rb,on=["entry_ny","exit_ny"],how="left")
    ws.to_csv(OUT/"up_window_scan.csv",index=False)

    elig=ws[(ws["2025_H2_n"]>=65)&
            (ws["2025_H2_hit"]>=0.55)&
            (ws["dev_jitter_n"]>=9)&
            (ws["dev_jitter_positive_share"]>=0.80)].copy()
    elig=elig.sort_values(["dev_jitter_min_compound","dev_jitter_median_compound","2025_H2_compound"],
                          ascending=False)
    elig.head(100).to_csv(OUT/"up_window_dev_robust_top.csv",index=False)
    upbest=elig.iloc[0].to_dict() if len(elig) else None

    # 3) DOWN exit timing. If already long, selling at t instead of holding to 20:00:
    # avoided_return = P(t)/P(20:00)-1. Select only on 2025 H2 and jitter +/-30m.
    dndays=sig[(sig.consensus)&(sig.state=="DOWN")].issue_date.astype(str).tolist()
    drows=[]
    for hm in grid[:-1]:
      rec=[]
      for d in dndays:
        a=by.get((d,hm)); b=by.get((d,"20:00"))
        if a is not None and b is not None: rec.append((d,a/b-1))
      row={"sell_ny":hm}
      for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
        v=[r for d,r in rec if period(d)==pp]; m=metrics(v)
        for k,val in m.items(): row[pp+"_"+k]=val
      drows.append(row)
    ds=pd.DataFrame(drows)
    # jitter across +/-30m
    vals_by={r.sell_ny:r for r in ds.itertuples(index=False)}
    jr=[]
    for r in ds.itertuples(index=False):
      i=idx[r.sell_ny]; vals=[]
      for di in [-2,-1,0,1,2]:
        ii=i+di
        if ii<0 or ii>=len(grid)-1: continue
        rr=vals_by.get(grid[ii])
        if rr is not None and rr._asdict()["2025_H2_n"]>=35:
          vals.append(rr._asdict()["2025_H2_compound"])
      jr.append({"sell_ny":r.sell_ny,"dev_jitter_n":len(vals),
                 "dev_jitter_median_compound":float(np.median(vals)) if vals else np.nan,
                 "dev_jitter_min_compound":float(np.min(vals)) if vals else np.nan,
                 "dev_jitter_positive_share":float(np.mean(np.asarray(vals)>0)) if vals else np.nan})
    ds=ds.merge(pd.DataFrame(jr),on="sell_ny",how="left")
    ds.to_csv(OUT/"down_exit_scan.csv",index=False)
    delig=ds[(ds["2025_H2_n"]>=35)&(ds["dev_jitter_n"]>=3)&(ds["dev_jitter_positive_share"]>=0.80)].copy()
    delig=delig.sort_values(["dev_jitter_min_compound","dev_jitter_median_compound","2025_H2_compound"],ascending=False)
    delig.head(50).to_csv(OUT/"down_exit_dev_robust_top.csv",index=False)
    downbest=delig.iloc[0].to_dict() if len(delig) else None

    # 4) Summarize strongest 1h acceleration/giveback windows selected on 2025 only, then transport.
    accel={}
    for st in ["UP","DOWN"]:
      g=fw[(fw.state==st)&(fw.period=="2025_H2")&(fw.horizon_min==60)].copy()
      if len(g):
        top=g.sort_values("mean",ascending=False).iloc[0]
        bottom=g.sort_values("mean",ascending=True).iloc[0]
        def transport(row):
          out={"start_ny":row.start_ny,"end_ny":row.end_ny,"dev_mean":float(row["mean"])}
          for pp in ["2025_H2","2026_JAN_JUL","2026_AUG_SEP"]:
            q=fw[(fw.state==st)&(fw.period==pp)&(fw.horizon_min==60)&
                 (fw.start_ny==row.start_ny)&(fw.end_ny==row.end_ny)]
            if len(q): out[pp]={"mean":float(q.iloc[0]["mean"]),"compound":float(q.iloc[0]["compound"]),
                                "hit":float(q.iloc[0]["hit"]),"n":int(q.iloc[0]["n"])}
          return out
        accel[st]={"strongest_positive_1h_dev":transport(top),
                   "strongest_negative_1h_dev":transport(bottom)}

    # Istanbul clock range for selected fixed NY times by period.
    def tr_clock_for_dates(hm, dates):
      vals=[]
      for d in dates:
        ts=pd.Timestamp(d+" "+hm,tz=NY).tz_convert("Europe/Istanbul")
        vals.append(ts.strftime("%H:%M"))
      return sorted(set(vals))
    if upbest:
      d2025=sig[(sig.issue_date>="2025-07-01")&(sig.issue_date<="2025-12-31")].issue_date.astype(str).tolist()
      upbest["entry_istanbul_clocks_2025H2"]=tr_clock_for_dates(upbest["entry_ny"],d2025)
      upbest["exit_istanbul_clocks_2025H2"]=tr_clock_for_dates(upbest["exit_ny"],d2025)
    if downbest:
      d2025=sig[(sig.issue_date>="2025-07-01")&(sig.issue_date<="2025-12-31")].issue_date.astype(str).tolist()
      downbest["sell_istanbul_clocks_2025H2"]=tr_clock_for_dates(downbest["sell_ny"],d2025)

    out={
      "status":"RETROSPECTIVE_15M_EXECUTION_TIMING_DEV2025_TRANSPORT2026_NOT_PROSPECTIVE",
      "signal_time_ny":"08:00",
      "method":"2025 H2 selects; 2026 Jan-Jul and Aug-Sep are unchanged transport. 15m windows require >=60m and jitter robustness +/-30m.",
      "up_selected_dev2025":upbest,
      "down_exit_selected_dev2025":downbest,
      "one_hour_acceleration_giveback":accel,
      "guardrails":[
        "No pre-08:00 NY price is used for executable CIG-D1 timing.",
        "Selection is retrospective and architecture was itself developed with historical knowledge; 2026 is transport diagnostic, not pristine prospective OOS.",
        "Gross XAU/USD only; no spread, commission, slippage, swap, taxes, or venue basis."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(out,indent=2,default=str)+"\n")
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__":
    main()
