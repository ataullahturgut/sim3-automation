from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, precision_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
XFILES=[AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv",AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"]
MACRO=AX/"GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv"
OUTP=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
OUTM=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_METRICS_2026-10-07.csv"
OUTD=AX/"GOLD_EXECUTION_LIT_STAGE3_MECHANISM_DIAGNOSTICS_2026-10-07.csv"
OUTS=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_RESULT_2026-10-07.md"

MIN_TRAIN=80
CONF=0.60
QLEVEL=0.67
MIN_YEAR_ACTIVE=30

POLICIES=[
 "PAIR_ALL",
 "PAIR_CONF60",
 "SNR_Q67",
 "SNR_Q67_PAIR_SAME",
 "SNR_Q67_PAIR_SAME_NOFOMC",
 "PAIR_CONF60_NOFOMC",
]

def load15():
    xs=[]
    for p in XFILES:
        q=pd.read_csv(p,low_memory=False)
        q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
        q["open"]=pd.to_numeric(q.open,errors="coerce");q["close"]=pd.to_numeric(q.close,errors="coerce")
        xs.append(q[["ts","open","close"]])
    q=pd.concat(xs).dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    return q[(q.ts>="2022-01-01")&(q.ts<"2026-01-10")].set_index("ts")

def point(q,d,hm,col):
    h,m=map(int,hm.split(":"));ts=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=h,minutes=m)
    try:return float(q.at[ts,col])
    except KeyError:return np.nan

def lr(a,b):
    return float(np.log(b/a)) if np.isfinite(a) and np.isfinite(b) and a>0 and b>0 else np.nan

def intr(q,d,op,cl):return lr(point(q,d,op,"open"),point(q,d,cl,"close"))

def pre17_state(q,d):
    rs=[];t=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=11)  # 14:00 TRT
    for k in range(12):
        ts=t+pd.Timedelta(minutes=15*k)
        try:r=lr(float(q.at[ts,"open"]),float(q.at[ts,"close"]))
        except KeyError:r=np.nan
        rs.append(r)
    if not np.isfinite(rs).all():return np.nan
    return float(np.sqrt(np.sum(np.square(rs))))

def macro_map():
    m=pd.read_csv(MACRO,low_memory=False)
    m["event_ts_utc"]=pd.to_datetime(m.event_ts_utc,utc=True,errors="coerce")
    m["surprise_ready_at_utc"]=pd.to_datetime(m.surprise_ready_at_utc,utc=True,errors="coerce")
    m["surprise"]=pd.to_numeric(m.surprise,errors="coerce")
    m["pair_complete"]=m.pair_complete.astype(str).str.lower().eq("true")
    m=m.sort_values("event_ts_utc").reset_index(drop=True)
    zs=[]
    for i,r in m.iterrows():
        h=m[(m.event_type==r.event_type)&(m.event_ts_utc<r.event_ts_utc)&m.surprise.notna()]
        if len(h)>=6 and np.isfinite(r.surprise):
            sd=float(h.surprise.std(ddof=1))
            z=(float(r.surprise)-float(h.surprise.mean()))/sd if sd>1e-12 else np.nan
        else:z=np.nan
        zs.append(z)
    m["surprise_z_pit"]=zs
    return m

def event_features(m,d,nextd):
    decision=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=14) # 17:00 TRT
    end=pd.Timestamp(nextd,tz="UTC")+pd.Timedelta(hours=6) if nextd is not None else decision
    local_date=pd.Timestamp(d).date()
    rel=m[(m.surprise_ready_at_utc.notna())&(m.surprise_ready_at_utc<=decision)&
          ((m.event_ts_utc+pd.Timedelta(hours=3)).dt.date==local_date)&m.pair_complete]
    maxz=float(rel.surprise_z_pit.abs().max()) if len(rel) and rel.surprise_z_pit.notna().any() else np.nan
    upf=m[(m.event_type=="FOMC")&(m.event_ts_utc>decision)&(m.event_ts_utc<=end)]
    return int(len(rel)>0),maxz,int(len(upf)>0)

def build(q,m):
    dates=sorted({t.date() for t in q.index if t.hour==6 and t.minute==0})
    rows=[]
    for i,d in enumerate(dates[:-1]):
        nxt=dates[i+1]
        r16=intr(q,d,"13:00","13:15");r1630=intr(q,d,"13:30","13:45")
        rv=pre17_state(q,d)
        ovn=lr(point(q,d,"14:00","open"),point(q,nxt,"05:45","close"))
        macro_any,maxz,upf=event_features(m,d,nxt)
        rows.append({
          "date":pd.Timestamp(d),"year":d.year,"next_date":pd.Timestamp(nxt),
          "r16":r16,"r1630":r1630,"pair_same":float(np.sign(r16)==np.sign(r1630)) if np.isfinite(r16) and np.isfinite(r1630) and r16!=0 and r1630!=0 else np.nan,
          "rv3h":rv,"abs_norm":abs(r16)/rv if np.isfinite(r16) and np.isfinite(rv) and rv>1e-12 else np.nan,
          "macro_released":macro_any,"macro_max_abs_z":maxz,"big_surprise":int(np.isfinite(maxz) and maxz>=1.0),
          "upcoming_fomc":upf,"ret":ovn,"y":float(ovn>0) if np.isfinite(ovn) else np.nan})
    return pd.DataFrame(rows)

def pair_predictions(d):
    q=d.dropna(subset=["r16","r1630","pair_same","y"]).sort_values("date").reset_index(drop=True)
    rows=[]
    feats=["r16","r1630","pair_same"]
    for _,r in q[q.year.isin([2023,2024])].iterrows():
        h=q[(q.date<r.date)&(q.next_date<=r.date)].copy()
        if len(h)<MIN_TRAIN or h.y.nunique()<2:continue
        model=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000)).fit(h[feats],h.y.astype(int))
        p=float(model.predict_proba(r[feats].to_numpy(float).reshape(1,-1))[0,1])
        # rolling, label-free SNR threshold
        prior=d[(d.date<r.date)&d.abs_norm.notna()].abs_norm
        q67=float(prior.quantile(QLEVEL)) if len(prior)>=MIN_TRAIN else np.nan
        rows.append({**r.to_dict(),"period":"DEV","p_pair":p,"pred_pair":int(p>=.5),"confidence":max(p,1-p),"q67":q67})
    tr=q[(q.year<=2024)&(q.next_date<=pd.Timestamp("2025-01-01"))].copy();te=q[q.year==2025].copy()
    model=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000)).fit(tr[feats],tr.y.astype(int))
    # policy threshold is label-free dynamic q67 using only prior feature history, including 2025 feature observations as they arrive.
    for _,r in te.iterrows():
        p=float(model.predict_proba(r[feats].to_numpy(float).reshape(1,-1))[0,1])
        prior=d[(d.date<r.date)&d.abs_norm.notna()].abs_norm
        q67=float(prior.quantile(QLEVEL)) if len(prior)>=MIN_TRAIN else np.nan
        rows.append({**r.to_dict(),"period":"TRANSPORT_2025","p_pair":p,"pred_pair":int(p>=.5),"confidence":max(p,1-p),"q67":q67})
    return pd.DataFrame(rows)

def apply_policy(r,name):
    high=np.isfinite(r.q67) and np.isfinite(r.abs_norm) and r.abs_norm>=r.q67
    pair=bool(r.pair_same==1)
    nof=not bool(r.upcoming_fomc)
    if name=="PAIR_ALL":return True,int(r.pred_pair)
    if name=="PAIR_CONF60":return bool(r.confidence>=CONF),int(r.pred_pair)
    if name=="SNR_Q67":return high,int(r.r16>0)
    if name=="SNR_Q67_PAIR_SAME":return high and pair,int(r.r16>0)
    if name=="SNR_Q67_PAIR_SAME_NOFOMC":return high and pair and nof,int(r.r16>0)
    if name=="PAIR_CONF60_NOFOMC":return bool(r.confidence>=CONF and nof),int(r.pred_pair)
    raise KeyError(name)

def policy_rows(p):
    out=[]
    for _,r in p.iterrows():
        for pol in POLICIES:
            active,pred=apply_policy(r,pol)
            out.append({"policy":pol,"date":r.date,"year":int(r.year),"period":r.period,"active":active,"pred":pred,
                        "y":int(r.y),"p_pair":r.p_pair,"confidence":r.confidence,"abs_norm":r.abs_norm,"q67":r.q67,
                        "pair_same":r.pair_same,"macro_released":r.macro_released,"big_surprise":r.big_surprise,
                        "upcoming_fomc":r.upcoming_fomc})
    return pd.DataFrame(out)

def stat(g,denom):
    a=g[g.active].copy()
    if len(a)==0:return {"n":0,"coverage":0.0,"accuracy":np.nan,"ba":np.nan,"up_recall":np.nan,"down_recall":np.nan,"pred_up_rate":np.nan}
    y=a.y.astype(int).to_numpy();p=a.pred.astype(int).to_numpy()
    return {"n":len(a),"coverage":len(a)/denom,"accuracy":accuracy_score(y,p),"ba":balanced_accuracy_score(y,p),
            "up_recall":recall_score(y,p,pos_label=1,zero_division=0),"down_recall":recall_score(y,p,pos_label=0,zero_division=0),
            "pred_up_rate":float(np.mean(p))}

def metrics(pr):
    rows=[]
    for (pol,period),g in pr.groupby(["policy","period"]):
        for split,gg in [("ALL",g)]+[(str(y),g[g.year==y]) for y in sorted(g.year.unique())]:
            if len(gg):
                s=stat(gg,len(gg));rows.append({"policy":pol,"period":period,"split":split,**s})
    return pd.DataFrame(rows)

def choose(m):
    x=[]
    for pol in POLICIES:
        a=m[(m.policy==pol)&(m.period=="DEV")&(m.split=="ALL")]
        a3=m[(m.policy==pol)&(m.period=="DEV")&(m.split=="2023")]
        a4=m[(m.policy==pol)&(m.period=="DEV")&(m.split=="2024")]
        if a.empty or a3.empty or a4.empty:continue
        a=a.iloc[0];a3=a3.iloc[0];a4=a4.iloc[0]
        eligible=(a3.n>=MIN_YEAR_ACTIVE and a4.n>=MIN_YEAR_ACTIVE and
                  .10<=a3.pred_up_rate<=.90 and .10<=a4.pred_up_rate<=.90)
        score=min(a3.ba,a4.ba) if eligible else -1
        x.append((score,a.ba,a.coverage,pol,eligible))
    x=sorted(x,reverse=True)
    return x[0][3],x

def diagnostics(pr,chosen):
    q=pr[(pr.policy==chosen)&pr.active].copy()
    rows=[]
    for period,g in q.groupby("period"):
        states=[
          ("ALL",pd.Series(True,index=g.index)),
          ("MACRO_RELEASED",g.macro_released.eq(1)),
          ("NO_MACRO_RELEASE",g.macro_released.eq(0)),
          ("BIG_SURPRISE",g.big_surprise.eq(1)),
          ("PAIR_SAME",g.pair_same.eq(1)),
          ("PAIR_FLIP",g.pair_same.eq(0)),
          ("UPCOMING_FOMC",g.upcoming_fomc.eq(1)),
          ("NO_UPCOMING_FOMC",g.upcoming_fomc.eq(0)),
        ]
        for name,mask in states:
            gg=g[mask]
            if not len(gg):continue
            y=gg.y.astype(int).to_numpy();p=gg.pred.astype(int).to_numpy()
            rows.append({"policy":chosen,"period":period,"state":name,"n":len(gg),"accuracy":accuracy_score(y,p),"ba":balanced_accuracy_score(y,p)})
    return pd.DataFrame(rows)

def get(m,pol,period,split="ALL"):
    z=m[(m.policy==pol)&(m.period==period)&(m.split==split)]
    return None if z.empty else z.iloc[0]

def pct(x):return "NA" if x is None or not np.isfinite(float(x)) else f"{100*float(x):.2f}%"

def main():
    d=build(load15(),macro_map())
    p=pair_predictions(d)
    pr=policy_rows(p);m=metrics(pr)
    chosen,ranking=choose(m)
    diag=diagnostics(pr,chosen)
    dev=get(m,chosen,"DEV");d3=get(m,chosen,"DEV","2023");d4=get(m,chosen,"DEV","2024");t=get(m,chosen,"TRANSPORT_2025")
    # same-covered pair baseline and majority baseline to guard against abstention illusion
    cov=pr[(pr.policy==chosen)&pr.active][["date","period","year","y"]].drop_duplicates()
    base=p.merge(cov,on=["date","period","year","y"],how="inner")
    base_acc=float((base.pred_pair.astype(int)==base.y.astype(int)).mean()) if len(base) else np.nan
    majority_acc=float(max(base.y.mean(),1-base.y.mean())) if len(base) else np.nan
    summary={"status":"COMPLETE","chosen_policy_development_only":chosen,"policy_ranking":ranking,
             "selection_rule":"maximize minimum of 2023/2024 BA; require >=30 active rows/year and predicted-UP rate 10%-90% each year; tie-break pooled BA then coverage",
             "confidence_threshold":CONF,"snr_quantile":QLEVEL,"no_2025_selection":True,
             "dev":{"n":int(dev.n),"coverage":float(dev.coverage),"accuracy":float(dev.accuracy),"ba":float(dev.ba),
                    "2023_ba":float(d3.ba),"2024_ba":float(d4.ba)},
             "transport_2025":{"n":int(t.n),"coverage":float(t.coverage),"accuracy":float(t.accuracy),"ba":float(t.ba),
                               "up_recall":float(t.up_recall),"down_recall":float(t.down_recall)},
             "same_covered_pair_baseline_accuracy_all_periods":base_acc,
             "same_covered_majority_accuracy_all_periods":majority_acc,
             "interpretation":"selective specialist only; not a full-coverage overnight model"}
    pr.to_csv(OUTP,index=False);m.to_csv(OUTM,index=False);diag.to_csv(OUTD,index=False);OUTS.write_text(json.dumps(summary,indent=2)+"\n")
    lines=["# GOLD EXECUTION LITERATURE STAGE-3 SELECTIVE RESULT — 2026-10-07","",
           "**Status:** COMPLETE / DEVELOPMENT-SELECTED SELECTIVE SPECIALIST","",
           "The candidate menu and selection rule were fixed before 2025 transport was read. Selection uses 2023-2024 only.","",
           "| Policy | DEV N | DEV coverage | DEV BA | 2023 BA | 2024 BA | 2025 N | 2025 coverage | 2025 Acc | 2025 BA |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for pol in POLICIES:
        a=get(m,pol,"DEV");a3=get(m,pol,"DEV","2023");a4=get(m,pol,"DEV","2024");tt=get(m,pol,"TRANSPORT_2025")
        lines.append(f"| {pol} | {int(a.n)} | {pct(a.coverage)} | {pct(a.ba)} | {pct(a3.ba)} | {pct(a4.ba)} | {int(tt.n)} | {pct(tt.coverage)} | {pct(tt.accuracy)} | {pct(tt.ba)} |")
    lines += ["",f"Development-only selected policy: **{chosen}**.",
              f"2025 frozen transport: **{int(t.n)} actions**, coverage **{pct(t.coverage)}**, accuracy **{pct(t.accuracy)}**, BA **{pct(t.ba)}**, UP recall **{pct(t.up_recall)}**, DOWN recall **{pct(t.down_recall)}**.",
              "",
              "This is a selective specialist, not a claim of full-coverage overnight accuracy.",
              "Risk-coverage diagnostics and macro/FOMC subgroup diagnostics are saved separately; no 2025 threshold was tuned."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
