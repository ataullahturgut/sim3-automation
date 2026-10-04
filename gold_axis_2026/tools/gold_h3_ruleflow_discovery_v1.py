from __future__ import annotations
from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
VAST=AX/"GOLD_H3_VAST_V1_HOURLY_PANEL_2026-10-04.csv"

OUT_CSV=AX/"GOLD_H3_RULEFLOW_DISCOVERY_V1_EVENTS_2026-10-04.csv"
OUT_MD=AX/"GOLD_H3_RULEFLOW_DISCOVERY_V1_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_RULEFLOW_DISCOVERY_V1_SUMMARY_2026-10-04.json"

EVENTS=[
("2025-03-05","ADP","08:15",3.99),("2025-03-07","NFP","08:30",3.99),
("2025-03-11","JOLTS","10:00",3.94),("2025-03-12","CPI","08:30",4.01),
("2025-03-19","FOMC","14:00",3.99),("2025-03-28","PCE","08:30",3.89),
("2025-04-01","JOLTS","10:00",3.87),("2025-04-02","ADP","08:15",3.91),
("2025-04-04","NFP","08:30",3.68),("2025-04-10","CPI","08:30",3.84),
("2025-04-29","JOLTS","10:00",3.65),("2025-04-30","ADP+PCE","08:15",3.60),
("2025-05-02","NFP","08:30",3.83),("2025-05-07","FOMC","14:00",3.78),
("2025-05-13","CPI","08:30",4.02),("2025-05-30","PCE","08:30",3.89),
("2025-06-03","JOLTS","10:00",3.96),("2025-06-04","ADP","08:15",3.87),
("2025-06-06","NFP","08:30",4.04),("2025-06-11","CPI","08:30",3.94),
("2025-06-18","FOMC","14:00",3.94),("2025-06-27","PCE","08:30",3.73),
("2025-07-01","JOLTS","10:00",3.78),("2025-07-02","ADP","08:15",3.78),
("2025-07-03","NFP","08:30",3.88),("2025-07-15","CPI","08:30",3.95),
("2025-07-29","JOLTS","10:00",3.86),("2025-07-30","ADP+FOMC","08:15",3.94),
("2025-07-31","PCE","08:30",3.94),("2025-08-01","NFP","08:30",3.69),
("2025-08-12","CPI","08:30",3.72),("2025-08-29","PCE","08:30",3.59),
("2025-09-03","JOLTS","10:00",3.61),("2025-09-04","ADP","08:15",3.59),
("2025-09-05","NFP","08:30",3.51),("2025-09-11","CPI","08:30",3.52),
("2025-09-17","FOMC","14:00",3.52),("2025-09-26","PCE","08:30",3.63),
("2025-09-30","JOLTS","10:00",3.60),
]

STATE_SIGNS={"trend_strength":-1.0,"session_against_trend":1.0,"trend_close_location":-1.0,"adverse_excursion":1.0}

def load():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])
    h=pd.read_csv(VAST,usecols=["ts","GC_close"])
    h["ts"]=pd.to_datetime(h.ts,utc=True)
    h=h.dropna().sort_values("ts")
    z=v.merge(p,on="feature_cutoff_date",how="inner",suffixes=("","_p"))
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z.sort_values("feature_cutoff_date").reset_index(drop=True),h

def last_px(h,t):
    q=h[h.ts<=t].tail(1)
    return np.nan if q.empty else float(q.GC_close.iloc[0])

def path(h,date,time):
    rel=pd.Timestamp(f"{date} {time}",tz="America/New_York").tz_convert("UTC")
    p0=last_px(h,rel-pd.Timedelta(hours=1))
    p1=last_px(h,rel+pd.Timedelta(hours=2))
    close=last_px(h,(pd.Timestamp(date).tz_localize("America/New_York")+pd.Timedelta(hours=16)).tz_convert("UTC"))
    if not np.isfinite([p0,p1,close]).all():
        return np.nan,np.nan,np.nan,False
    r1=float(np.log(p1/p0)); r2=float(np.log(close/p1)); rt=float(np.log(close/p0))
    decay=bool((r1>0 and r2<0 and rt>0) or (r1<0 and r2>0 and rt<0))
    return r1,r2,rt,decay

def rank(hist,val):
    a=np.asarray(hist,float); a=a[np.isfinite(a)]
    return float((1+np.sum(a<=val))/(len(a)+1)) if len(a) else np.nan

def build(z,h):
    rows=[]
    for i,(date,event,time,y2) in enumerate(EVENTS):
        d=pd.Timestamp(date)
        q=z[z.feature_cutoff_date==d]
        if q.empty: continue
        r=q.iloc[-1]
        idx=z.index[z.feature_cutoff_date==d][0]
        hist=z.iloc[max(0,idx-120):idx]
        ranks=[]
        for c,s in STATE_SIGNS.items():
            ranks.append(rank((s*hist[c].astype(float)).to_numpy(),s*float(r[c])))
        susceptibility=float(np.median(ranks)) if np.isfinite(ranks).all() else np.nan

        prev=z[z.feature_cutoff_date<d].tail(1)
        prev_mom=int(prev.momentum_up.iloc[0]) if len(prev) else int(r.momentum_up)

        step=np.nan if i==0 else 100*(y2-EVENTS[i-1][3])
        last3=[]
        for j in range(max(1,i-2),i+1):
            last3.append(100*(EVENTS[j][3]-EVENTS[j-1][3]))
        if len(last3)==3:
            gross=float(sum(abs(x) for x in last3)); net=float(sum(last3))
            churn=float(gross-abs(net)); conflict=float(churn/gross) if gross>0 else 0.0
            dominance=float(abs(step)/gross) if gross>0 and np.isfinite(step) else np.nan
        else:
            gross=net=churn=conflict=dominance=np.nan

        r1,r2,rt,decay=path(h,date,time)
        event_mom=int(r.momentum_up)
        y=int(r.y_up); pred=int(r.v5_pred)
        sm=1 if prev_mom==1 else -1
        shock_opposes=bool(np.isfinite(step) and step*sm>0)
        implied_gold_dir=(-1 if step>0 else (1 if step<0 else 0)) if np.isfinite(step) else 0
        first_dir=1 if r1>0 else (-1 if r1<0 else 0)
        first_aligns_rates=bool(implied_gold_dir!=0 and first_dir==implied_gold_dir)
        rows.append({
          "date":date,"event":event,"two_y":y2,"step_bp":step,
          "gross3":gross,"churn3":churn,"conflict_ratio":conflict,"current_dominance":dominance,
          "susceptibility":susceptibility,
          "pre_momentum_up":prev_mom,"event_momentum_up":event_mom,
          "event_momentum_flip":int(prev_mom!=event_mom),
          "shock_opposes_pre_momentum":int(shock_opposes),
          "first_ret":r1,"post_first_ret":r2,"event_total_ret":rt,
          "reaction_decay":int(decay),"first_aligns_rates":int(first_aligns_rates),
          "target_reversal":int(y!=event_mom),
          "v5_follows_momentum":int(pred==event_mom),
          "v5_missed_reversal":int(pred==event_mom and y!=event_mom),
          "h3_return":float(r.target_r3),
        })
    return pd.DataFrame(rows)

def rule_metrics(q,mask):
    m=pd.Series(mask,index=q.index).fillna(False).astype(bool)
    n=int(m.sum())
    rev=int((m&q.target_reversal.astype(bool)).sum())
    acts=m&q.v5_follows_momentum.astype(bool)
    rescue=int((acts&q.v5_missed_reversal.astype(bool)).sum())
    broken=int((acts&~q.v5_missed_reversal.astype(bool)).sum())
    return dict(flag_n=n,rev=rev,rev_rate=rev/max(n,1),actions=int(acts.sum()),rescue=rescue,broken=broken,net=rescue-broken,precision=rescue/max(int(acts.sum()),1))

def main():
    z,h=load(); q=build(z,h)
    q=q[q.date>="2025-03-12"].reset_index(drop=True)
    q.to_csv(OUT_CSV,index=False)

    feats=["susceptibility","conflict_ratio","current_dominance","event_momentum_flip",
           "shock_opposes_pre_momentum","reaction_decay","first_aligns_rates"]
    x=q.dropna(subset=feats).copy()
    tree=DecisionTreeClassifier(max_depth=3,min_samples_leaf=3,class_weight="balanced",random_state=20261004)
    tree.fit(x[feats],x.target_reversal)
    txt=export_text(tree,feature_names=feats,decimals=3)

    flows={
      "F1_FRAGMENTED_UNRESOLVED": (q.conflict_ratio>=0.50)&(q.current_dominance<0.50),
      "F2_F1_PLUS_FLIP": (q.conflict_ratio>=0.50)&(q.current_dominance<0.50)&(q.event_momentum_flip==1),
      "F3_F1_PLUS_SUS": (q.conflict_ratio>=0.50)&(q.current_dominance<0.50)&(q.susceptibility>=0.50),
      "F4_F1_PLUS_RATE_ALIGN": (q.conflict_ratio>=0.50)&(q.current_dominance<0.50)&(q.first_aligns_rates==1),
      "F5_FRAGMENTED_RESOLVED": (q.conflict_ratio>=0.50)&(q.current_dominance>=0.50),
      "F6_COHERENT": q.conflict_ratio<0.50,
    }
    periods={"H1ish":(q.date<="2025-06-30"),"H2ish":(q.date>="2025-07-01")}
    metrics=[]
    for f,m in flows.items():
      for p,pm in periods.items():
        metrics.append({"flow":f,"period":p,**rule_metrics(q,m&pm)})
      metrics.append({"flow":f,"period":"ALL",**rule_metrics(q,m)})
    mdf=pd.DataFrame(metrics)

    summary={"tree":txt,"metrics":metrics,"n":len(q),"reversals":int(q.target_reversal.sum())}
    OUT_JSON.write_text(json.dumps(summary,indent=2)+"\n")

    lines=["# GOLD H3 — RULE-FLOW DISCOVERY V1","",
      "**Scope:** major U.S. macro/Fed event origins, 2025-03-12..2025-09-30.",
      "**Status:** exploratory structure discovery; not promotion evidence.","",
      "## Shallow tree","", "~~~~", txt, "~~~~","",
      "## Predefined rule flows","",
      "| Flow | Period | Flag N | Reversal | Reversal rate | V5 actions | Rescue | Broken | Net | Precision |",
      "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in mdf.itertuples():
      lines.append(f"| {r.flow} | {r.period} | {r.flag_n} | {r.rev} | {100*r.rev_rate:.1f}% | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.1f}% |")
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
