from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, precision_score, brier_score_loss, log_loss, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
XFILES=[AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv",AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"]
OUTP=AX/"GOLD_EXECUTION_LIT_STAGE2_PREDICTIONS_2026-10-07.csv"
OUTM=AX/"GOLD_EXECUTION_LIT_STAGE2_METRICS_2026-10-07.csv"
OUTS=AX/"GOLD_EXECUTION_LIT_STAGE2_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_LIT_STAGE2_RESULT_2026-10-07.md"
MIN_TRAIN=80

SPECS={
 "BASE_1600_1630":["r1600_1630"],
 "PAIR_1600_1700":["r1600_1630","r1630_1700","pair_inter","pair_same"],
 "LIT_OVN2_STATE":["r1600_1630","r1630_1700","pair_same","rv3h","jump3h","abs3h","r16_x_rv","r16_x_jump"],
}

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
    # 14:00-17:00 Europe/Istanbul = 11:00-14:00 UTC.
    rs=[]
    t=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=11)
    for k in range(12):
        ts=t+pd.Timedelta(minutes=15*k)
        try:r=lr(float(q.at[ts,"open"]),float(q.at[ts,"close"]))
        except KeyError:r=np.nan
        rs.append(r)
    if not np.isfinite(rs).all():return (np.nan,np.nan,np.nan)
    rv=float(np.sqrt(np.sum(np.square(rs))))
    jump=float(np.max(np.abs(rs)))
    abs3=abs(lr(point(q,d,"11:00","open"),point(q,d,"13:45","close")))
    return rv,jump,abs3

def build(q):
    dates=sorted({t.date() for t in q.index if t.hour==6 and t.minute==0})
    rows=[]
    for i,d in enumerate(dates[:-1]):
        nxt=dates[i+1]
        r16=intr(q,d,"13:00","13:15");r1630=intr(q,d,"13:30","13:45")
        rv,jump,abs3=pre17_state(q,d)
        ovn=lr(point(q,d,"14:00","open"),point(q,nxt,"05:45","close"))
        rows.append({
          "date":pd.Timestamp(d),"year":d.year,"next_date":pd.Timestamp(nxt),
          "r1600_1630":r16,"r1630_1700":r1630,
          "pair_inter":r16*r1630 if np.isfinite(r16) and np.isfinite(r1630) else np.nan,
          "pair_same":float(np.sign(r16)==np.sign(r1630)) if np.isfinite(r16) and np.isfinite(r1630) and r16!=0 and r1630!=0 else np.nan,
          "rv3h":rv,"jump3h":jump,"abs3h":abs3,
          "r16_x_rv":r16*rv if np.isfinite(r16) and np.isfinite(rv) else np.nan,
          "r16_x_jump":r16*jump if np.isfinite(r16) and np.isfinite(jump) else np.nan,
          "ret":ovn,"y":float(ovn>0) if np.isfinite(ovn) else np.nan})
    return pd.DataFrame(rows)

def fit_predict(d,name,features):
    q=d.dropna(subset=features+["ret","y"]).sort_values("date").reset_index(drop=True)
    rows=[]
    for _,r in q[q.year.isin([2023,2024])].iterrows():
        h=q[(q.date<r.date)&(q.next_date<=r.date)].copy()
        if len(h)<MIN_TRAIN or h.y.nunique()<2:continue
        X=h[features].to_numpy(float);y=h.y.astype(int).to_numpy();xr=r[features].to_numpy(float).reshape(1,-1)
        lg=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000)).fit(X,y)
        ol=make_pipeline(StandardScaler(),LinearRegression()).fit(X,h.ret.to_numpy(float))
        p=float(lg.predict_proba(xr)[0,1]);rh=float(ol.predict(xr)[0])
        rows.append([name,r.date,"DEV",int(r.year),len(h),float(r.ret),int(r.y),p,int(p>=.5),rh,int(rh>=0),float(h.ret.mean())])
    tr=q[(q.year<=2024)&(q.next_date<=pd.Timestamp("2025-01-01"))].copy();te=q[q.year==2025].copy()
    X=tr[features].to_numpy(float);y=tr.y.astype(int).to_numpy()
    lg=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000)).fit(X,y)
    ol=make_pipeline(StandardScaler(),LinearRegression()).fit(X,tr.ret.to_numpy(float));mh=float(tr.ret.mean())
    for _,r in te.iterrows():
        xr=r[features].to_numpy(float).reshape(1,-1);p=float(lg.predict_proba(xr)[0,1]);rh=float(ol.predict(xr)[0])
        rows.append([name,r.date,"TRANSPORT_2025",2025,len(tr),float(r.ret),int(r.y),p,int(p>=.5),rh,int(rh>=0),mh])
    return pd.DataFrame(rows,columns=["spec","date","period","year","train_n","actual_ret","actual_y","p","pred_logit","ret_hat","pred_ols","mean_hat"])

def calc(g,pred,prob=None):
    y=g.actual_y.astype(int).to_numpy();p=g[pred].astype(int).to_numpy()
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    mse=float(np.mean((g.actual_ret-g.ret_hat)**2));base=float(np.mean((g.actual_ret-g.mean_hat)**2))
    d={"n":len(g),"accuracy":accuracy_score(y,p),"balanced_accuracy":balanced_accuracy_score(y,p),
       "up_recall":recall_score(y,p,pos_label=1,zero_division=0),"down_recall":recall_score(y,p,pos_label=0,zero_division=0),
       "up_precision":precision_score(y,p,pos_label=1,zero_division=0),"down_precision":precision_score(y,p,pos_label=0,zero_division=0),
       "tn":tn,"fp":fp,"fn":fn,"tp":tp,"r2_os":1-mse/base if base>0 else np.nan}
    if prob:
        pr=np.clip(g[prob].to_numpy(float),1e-6,1-1e-6);d["brier"]=brier_score_loss(y,pr);d["log_loss"]=log_loss(y,pr,labels=[0,1])
    else:d["brier"]=np.nan;d["log_loss"]=np.nan
    return d

def metrics(p):
    rows=[]
    for (s,period),g in p.groupby(["spec","period"]):
        for model,pred,prob in [("LOGIT","pred_logit","p"),("OLS_SIGN","pred_ols",None)]:
            for split,gg in [("ALL",g)]+[(str(y),g[g.year==y]) for y in sorted(g.year.unique())]:
                if len(gg):rows.append({"spec":s,"period":period,"model":model,"split":split,**calc(gg,pred,prob)})
    return pd.DataFrame(rows)

def get(m,s,period="DEV",model="LOGIT",split="ALL"):
    z=m[(m.spec==s)&(m.period==period)&(m.model==model)&(m.split==split)]
    return None if z.empty else z.iloc[0]

def pct(x):return "NA" if x is None or not np.isfinite(float(x)) else f"{100*float(x):.2f}%"

def main():
    d=build(load15())
    p=pd.concat([fit_predict(d,s,f) for s,f in SPECS.items()],ignore_index=True)
    m=metrics(p)
    base=get(m,"BASE_1600_1630");pair=get(m,"PAIR_1600_1700");state=get(m,"LIT_OVN2_STATE")
    b3=get(m,"BASE_1600_1630",split="2023");b4=get(m,"BASE_1600_1630",split="2024")
    s3=get(m,"LIT_OVN2_STATE",split="2023");s4=get(m,"LIT_OVN2_STATE",split="2024")
    dev_gain=float(state.balanced_accuracy-base.balanced_accuracy)
    dev_r2_gain=float(state.r2_os-base.r2_os)
    retain=bool(dev_gain>0 and dev_r2_gain>0 and s3.balanced_accuracy>=b3.balanced_accuracy and s4.balanced_accuracy>=b4.balanced_accuracy)
    summary={"status":"COMPLETE","spec":"fixed before 2025 transport","features":SPECS["LIT_OVN2_STATE"],
             "development_ba_gain_vs_base":dev_gain,"development_r2_gain_vs_base":dev_r2_gain,
             "development_nonworse_each_year":bool(s3.balanced_accuracy>=b3.balanced_accuracy and s4.balanced_accuracy>=b4.balanced_accuracy),
             "retain_on_development_rule":retain,"no_2025_selection":True,
             "rule":"Retain only if DEV BA and R2_OS both improve BASE_1600_1630 and BA is non-worse in both 2023 and 2024."}
    p.to_csv(OUTP,index=False);m.to_csv(OUTM,index=False);OUTS.write_text(json.dumps(summary,indent=2)+"\n")
    lines=["# GOLD EXECUTION LITERATURE STAGE-2 RESULT — 2026-10-07","","**Status:** COMPLETE / FIXED STATE-CONDITIONED CHALLENGER","",
           "State features are continuous and origin-known; no 2025 threshold/state selection was performed.","",
           "| Spec | DEV Logit BA | 2023 BA | 2024 BA | DEV R2_OS | 2025 BA | 2025 Acc | 2025 DOWN recall |",
           "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for s in SPECS:
        a=get(m,s);a3=get(m,s,split="2023");a4=get(m,s,split="2024");t=get(m,s,"TRANSPORT_2025")
        lines.append(f"| {s} | {pct(a.balanced_accuracy)} | {pct(a3.balanced_accuracy)} | {pct(a4.balanced_accuracy)} | {pct(a.r2_os)} | {pct(t.balanced_accuracy)} | {pct(t.accuracy)} | {pct(t.down_recall)} |")
    lines += ["",f"Development BA gain vs single 16:00-16:30 base: **{100*dev_gain:+.2f} pp**.",
              f"Development R2_OS gain vs base: **{100*dev_r2_gain:+.2f} pp**.",
              f"Development retention rule: **{retain}**.",
              "2025 is transport evidence only and does not change this decision."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
