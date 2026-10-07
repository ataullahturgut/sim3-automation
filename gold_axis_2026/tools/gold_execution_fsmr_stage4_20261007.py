from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, precision_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
XFILES=[AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv",AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"]
OUTP=AX/"GOLD_EXECUTION_FSMR_STAGE4_PREDICTIONS_2026-10-07.csv"
OUTM=AX/"GOLD_EXECUTION_FSMR_STAGE4_METRICS_2026-10-07.csv"
OUTS=AX/"GOLD_EXECUTION_FSMR_STAGE4_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_FSMR_STAGE4_RESULT_2026-10-07.md"

QLEVEL=.67
SHRINK=10.0
DELTAS=[0.0,0.02,0.04,0.06]
MIN_STATE_HIST=12
MIN_SELECT_N=50

def load15():
    xs=[]
    for p in XFILES:
        q=pd.read_csv(p,low_memory=False);q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
        q["open"]=pd.to_numeric(q.open,errors="coerce");q["close"]=pd.to_numeric(q.close,errors="coerce")
        xs.append(q[["ts","open","close"]])
    q=pd.concat(xs).dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    return q[(q.ts>="2022-01-01")&(q.ts<"2026-01-10")].set_index("ts")

def point(q,d,hm,col):
    h,m=map(int,hm.split(":"));ts=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=h,minutes=m)
    try:return float(q.at[ts,col])
    except KeyError:return np.nan

def lr(a,b):return float(np.log(b/a)) if np.isfinite(a) and np.isfinite(b) and a>0 and b>0 else np.nan
def intr(q,d,op,cl):return lr(point(q,d,op,"open"),point(q,d,cl,"close"))

def rv3h(q,d):
    rs=[];t=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=11)
    for k in range(12):
        ts=t+pd.Timedelta(minutes=15*k)
        try:r=lr(float(q.at[ts,"open"]),float(q.at[ts,"close"]))
        except KeyError:r=np.nan
        rs.append(r)
    return float(np.sqrt(np.sum(np.square(rs)))) if np.isfinite(rs).all() else np.nan

def build(q):
    dates=sorted({t.date() for t in q.index if t.hour==6 and t.minute==0})
    rows=[]
    for i,d in enumerate(dates[:-1]):
        nxt=dates[i+1];r1=intr(q,d,"13:00","13:15");r2=intr(q,d,"13:30","13:45");rv=rv3h(q,d)
        yret=lr(point(q,d,"14:00","open"),point(q,nxt,"05:45","close"))
        rows.append({"date":pd.Timestamp(d),"year":d.year,"next_date":pd.Timestamp(nxt),
                     "r1":r1,"r2":r2,"rv":rv,"abs_norm":abs(r1)/rv if np.isfinite(r1) and np.isfinite(rv) and rv>1e-12 else np.nan,
                     "s1":1 if r1>0 else 0 if r1<0 else np.nan,"s2":1 if r2>0 else 0 if r2<0 else np.nan,
                     "ret":yret,"y":float(yret>0) if np.isfinite(yret) else np.nan})
    d=pd.DataFrame(rows)
    # label-free rolling high-SNR state
    highs=[]
    for _,r in d.iterrows():
        prior=d[(d.date<r.date)&d.abs_norm.notna()].abs_norm
        q67=float(prior.quantile(QLEVEL)) if len(prior)>=80 else np.nan
        highs.append(float(r.abs_norm>=q67) if np.isfinite(r.abs_norm) and np.isfinite(q67) else np.nan)
    d["snr_high"]=highs
    d["state4"]=d.apply(lambda r:f"{int(r.s1)}{int(r.s2)}" if np.isfinite(r.s1) and np.isfinite(r.s2) else None,axis=1)
    d["state8"]=d.apply(lambda r:f"{int(r.s1)}{int(r.s2)}_{int(r.snr_high)}" if np.isfinite(r.s1) and np.isfinite(r.s2) and np.isfinite(r.snr_high) else None,axis=1)
    return d

def score_states(d):
    out=[]
    for _,r in d[d.year.isin([2023,2024,2025])].iterrows():
        h=d[(d.date<r.date)&(d.next_date<=r.date)&d.y.notna()].copy()
        if len(h)<80:continue
        pg=float(h.y.mean())
        for model,state_col in [("FSMR4","state4"),("FSMR8","state8")]:
            state=r[state_col]
            if state is None:continue
            hs=h[h[state_col]==state]
            if len(hs)<MIN_STATE_HIST:continue
            up=float(hs.y.sum());n=float(len(hs))
            p=(up+SHRINK*pg)/(n+SHRINK)
            score=p-pg
            pred=int(score>=0)
            out.append({"date":r.date,"year":int(r.year),"model":model,"state":state,"state_n":int(n),
                        "p_state":p,"p_global":pg,"score":score,"confidence":abs(score),"pred":pred,"y":int(r.y)})
    return pd.DataFrame(out)

def eval_rows(s,model,delta,year):
    g=s[(s.model==model)&(s.year==year)&(s.confidence>=delta)].copy()
    total=len(s[(s.model==model)&(s.year==year)])
    if not len(g):return {"n":0,"coverage":0.0,"accuracy":np.nan,"ba":np.nan,"up_recall":np.nan,"down_recall":np.nan,"pred_up_rate":np.nan}
    y=g.y.to_numpy(int);p=g.pred.to_numpy(int)
    return {"n":len(g),"coverage":len(g)/total if total else 0,"accuracy":accuracy_score(y,p),"ba":balanced_accuracy_score(y,p),
            "up_recall":recall_score(y,p,pos_label=1,zero_division=0),"down_recall":recall_score(y,p,pos_label=0,zero_division=0),
            "pred_up_rate":float(p.mean())}

def select_2023(s):
    cand=[]
    for model in ["FSMR4","FSMR8"]:
        for d in DELTAS:
            z=eval_rows(s,model,d,2023)
            eligible=z["n"]>=MIN_SELECT_N and .10<=z["pred_up_rate"]<=.90
            score=z["ba"] if eligible else -1
            cand.append((float(score),float(z["coverage"]),-float(d),model,float(d),bool(eligible),z))
    cand=sorted(cand,reverse=True)
    best=cand[0]
    return best[3],best[4],cand

def metric_table(s):
    rows=[]
    for model in ["FSMR4","FSMR8"]:
        for d in DELTAS:
            for y in [2023,2024,2025]:
                z=eval_rows(s,model,d,y);rows.append({"model":model,"delta":d,"year":y,**z})
    return pd.DataFrame(rows)

def same_state_rules(d):
    # descriptive transition table using 2023-24 only, no 2025 selection
    g=d[d.year.isin([2023,2024])].dropna(subset=["state4","y"])
    rows=[]
    for st,h in g.groupby("state4"):
        rows.append({"state":st,"n":len(h),"up_rate":h.y.mean(),"overnight_mean_return":h.ret.mean()})
    return rows

def pct(x):return "NA" if x is None or not np.isfinite(float(x)) else f"{100*float(x):.2f}%"

def main():
    d=build(load15());s=score_states(d);m=metric_table(s)
    model,delta,ranking=select_2023(s)
    z23=eval_rows(s,model,delta,2023);z24=eval_rows(s,model,delta,2024);z25=eval_rows(s,model,delta,2025)
    confirmed=bool(z24["n"]>=MIN_SELECT_N and z24["ba"]>0.50 and .10<=z24["pred_up_rate"]<=.90)
    summary={"status":"COMPLETE","selection_period":"2023 only","confirmation_period":"2024","retrospective_transport":"2025",
             "selected_model":model,"selected_delta":delta,"selection_ranking":ranking,
             "shrinkage_strength":SHRINK,"min_state_history":MIN_STATE_HIST,"snr_quantile":QLEVEL,
             "confirmation_pass":confirmed,"metrics":{"2023":z23,"2024":z24,"2025":z25},
             "state4_development_table":same_state_rules(d),
             "governance":"No 2024/2025 outcome used to choose model/delta. 2024 confirms or rejects the 2023 choice; 2025 is retrospective transport only."}
    s.to_csv(OUTP,index=False);m.to_csv(OUTM,index=False);OUTS.write_text(json.dumps(summary,indent=2)+"\n")
    lines=["# GOLD EXECUTION FSMR STAGE-4 RESULT — 2026-10-07","",
           "**Status:** COMPLETE / 2023-SELECTED FINITE-STATE MOMENTUM-REVERSAL MODEL","",
           "Model identity and abstention delta are selected on 2023 only. 2024 is confirmation; 2025 is retrospective transport.","",
           f"Selected: **{model}**, delta **{delta:.2f}**.","",
           "| Period | N | Coverage | Accuracy | BA | UP recall | DOWN recall |",
           "|---|---:|---:|---:|---:|---:|---:|",
           f"| 2023 selection | {z23['n']} | {pct(z23['coverage'])} | {pct(z23['accuracy'])} | {pct(z23['ba'])} | {pct(z23['up_recall'])} | {pct(z23['down_recall'])} |",
           f"| 2024 confirmation | {z24['n']} | {pct(z24['coverage'])} | {pct(z24['accuracy'])} | {pct(z24['ba'])} | {pct(z24['up_recall'])} | {pct(z24['down_recall'])} |",
           f"| 2025 transport | {z25['n']} | {pct(z25['coverage'])} | {pct(z25['accuracy'])} | {pct(z25['ba'])} | {pct(z25['up_recall'])} | {pct(z25['down_recall'])} |","",
           f"2024 confirmation pass: **{confirmed}**.","",
           "FSMR4 uses four sign states (++,+-,-+,--). FSMR8 adds a label-free high/low normalized-impulse state. Posterior state probabilities are shrunk toward the historical global UP prevalence to reduce sparse-state overfit."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
