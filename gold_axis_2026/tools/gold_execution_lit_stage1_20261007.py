from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, precision_score, brier_score_loss, log_loss, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
XFILES = [AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv", AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"]
OUTP = AX/"GOLD_EXECUTION_LIT_STAGE1_PREDICTIONS_2026-10-07.csv"
OUTM = AX/"GOLD_EXECUTION_LIT_STAGE1_METRICS_2026-10-07.csv"
OUTS = AX/"GOLD_EXECUTION_LIT_STAGE1_SUMMARY_2026-10-07.json"
OUTR = AX/"GOLD_EXECUTION_LIT_STAGE1_RESULT_2026-10-07.md"
MIN_TRAIN=80

SPECS={
 "LIT_OVN0_1530_1600":("OVN",["r1530_1600"],"LIT_OVN0"),
 "LIT_OVN0_1600_1630":("OVN",["r1600_1630"],"LIT_OVN0"),
 "LIT_OVN0_1630_1700":("OVN",["r1630_1700"],"LIT_OVN0"),
 "LIT_OVN1_PAIR":("OVN",["r1600_1630","r1630_1700","pair_inter","pair_same"],"LIT_OVN1"),
 "LIT_DAY0_EXEC_0900":("DAY",["r0800_0830","r0830_0900","prev_ovn"],"LIT_DAY0"),
 "LIT_DAY1_DELAY_0930":("DAYD",["r0900_0930"],"LIT_DAY1_DELAYED"),
}

def load15():
    xs=[]
    for p in XFILES:
        q=pd.read_csv(p,low_memory=False)
        if not {"dt_utc","open","close"}.issubset(q.columns): raise RuntimeError("schema "+p.name)
        q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
        q["open"]=pd.to_numeric(q.open,errors="coerce"); q["close"]=pd.to_numeric(q.close,errors="coerce")
        xs.append(q[["ts","open","close"]])
    q=pd.concat(xs).dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    return q[(q.ts>="2022-01-01")&(q.ts<"2026-01-10")].set_index("ts")

def val(q,d,hm,col):
    h,m=map(int,hm.split(":")); ts=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=h,minutes=m)
    try:return float(q.at[ts,col])
    except KeyError:return np.nan

def ret(a,b):
    return float(np.log(b/a)) if np.isfinite(a) and np.isfinite(b) and a>0 and b>0 else np.nan

def interval(q,d,op,cl): return ret(val(q,d,op,"open"),val(q,d,cl,"close"))

def build(q):
    dates=sorted({t.date() for t in q.index if t.hour==6 and t.minute==0})
    rows=[]
    for i,d in enumerate(dates):
        prev=dates[i-1] if i else None; nxt=dates[i+1] if i+1<len(dates) else None
        r16=interval(q,d,"13:00","13:15"); r1630=interval(q,d,"13:30","13:45")
        day=interval(q,d,"06:00","13:45")
        dayd=interval(q,d,"06:30","13:45")
        ovn=interval(q,d,"14:00","05:45") if False else np.nan
        if nxt is not None: ovn=ret(val(q,d,"14:00","open"),val(q,nxt,"05:45","close"))
        prevovn=np.nan
        if prev is not None: prevovn=ret(val(q,prev,"14:00","open"),val(q,d,"05:45","close"))
        rows.append({
          "date":pd.Timestamp(d),"year":d.year,"next_date":pd.Timestamp(nxt) if nxt else pd.NaT,
          "r0800_0830":interval(q,d,"05:00","05:15"),
          "r0830_0900":interval(q,d,"05:30","05:45"),
          "r0900_0930":interval(q,d,"06:00","06:15"),
          "r1530_1600":interval(q,d,"12:30","12:45"),
          "r1600_1630":r16,"r1630_1700":r1630,
          "pair_inter":r16*r1630 if np.isfinite(r16) and np.isfinite(r1630) else np.nan,
          "pair_same":float(np.sign(r16)==np.sign(r1630)) if np.isfinite(r16) and np.isfinite(r1630) and r16!=0 and r1630!=0 else np.nan,
          "prev_ovn":prevovn,
          "ret_DAY":day,"y_DAY":float(day>0) if np.isfinite(day) else np.nan,
          "ret_DAYD":dayd,"y_DAYD":float(dayd>0) if np.isfinite(dayd) else np.nan,
          "ret_OVN":ovn,"y_OVN":float(ovn>0) if np.isfinite(ovn) else np.nan
        })
    return pd.DataFrame(rows)

def predict(d,name,target,features,family):
    rcol="ret_"+target; ycol="y_"+target
    q=d.dropna(subset=features+[rcol,ycol]).sort_values("date").reset_index(drop=True)
    out=[]
    for _,row in q[q.year.isin([2023,2024])].iterrows():
        hist=q[q.date<row.date].copy()
        if target=="OVN": hist=hist[hist.next_date<=row.date]
        if len(hist)<MIN_TRAIN or hist[ycol].nunique()<2: continue
        X=hist[features].to_numpy(float); y=hist[ycol].astype(int).to_numpy(); xr=row[features].to_numpy(float).reshape(1,-1)
        lg=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000)).fit(X,y)
        ol=LinearRegression().fit(X,hist[rcol].to_numpy(float))
        pp=float(lg.predict_proba(xr)[0,1]); rh=float(ol.predict(xr)[0])
        out.append([name,family,target,row.date,"DEV",int(row.year),len(hist),row[rcol],int(row[ycol]),pp,int(pp>=.5),rh,int(rh>=0),float(hist[rcol].mean())])
    tr=q[q.year<=2024].copy()
    if target=="OVN": tr=tr[tr.next_date<=pd.Timestamp("2025-01-01")]
    te=q[q.year==2025].copy()
    if len(tr)>=MIN_TRAIN and tr[ycol].nunique()>=2:
        X=tr[features].to_numpy(float); y=tr[ycol].astype(int).to_numpy()
        lg=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,max_iter=2000)).fit(X,y)
        ol=LinearRegression().fit(X,tr[rcol].to_numpy(float)); mh=float(tr[rcol].mean())
        for _,row in te.iterrows():
            xr=row[features].to_numpy(float).reshape(1,-1); pp=float(lg.predict_proba(xr)[0,1]); rh=float(ol.predict(xr)[0])
            out.append([name,family,target,row.date,"TRANSPORT_2025",2025,len(tr),row[rcol],int(row[ycol]),pp,int(pp>=.5),rh,int(rh>=0),mh])
    return pd.DataFrame(out,columns=["spec","family","target","date","period","year","train_n","actual_ret","actual_y","p_logit","pred_logit","ret_hat","pred_ols","mean_hat"])

def cls(g,pred,prob=None):
    y=g.actual_y.astype(int).to_numpy(); p=g[pred].astype(int).to_numpy()
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    x={"n":len(g),"accuracy":accuracy_score(y,p),"balanced_accuracy":balanced_accuracy_score(y,p),
       "up_recall":recall_score(y,p,pos_label=1,zero_division=0),"down_recall":recall_score(y,p,pos_label=0,zero_division=0),
       "up_precision":precision_score(y,p,pos_label=1,zero_division=0),"down_precision":precision_score(y,p,pos_label=0,zero_division=0),
       "tn":tn,"fp":fp,"fn":fn,"tp":tp}
    if prob:
        pr=np.clip(g[prob].to_numpy(float),1e-6,1-1e-6); x["brier"]=brier_score_loss(y,pr); x["log_loss"]=log_loss(y,pr,labels=[0,1])
    else:x["brier"]=np.nan;x["log_loss"]=np.nan
    mse=np.mean((g.actual_ret-g.ret_hat)**2); base=np.mean((g.actual_ret-g.mean_hat)**2)
    x["r2_os_ols"]=1-mse/base if base>0 else np.nan
    return x

def metrics(p):
    rows=[]
    for (s,period),g in p.groupby(["spec","period"]):
        for model,pred,prob in [("OLS_SIGN","pred_ols",None),("LOGIT","pred_logit","p_logit")]:
            sets=[("ALL",g)]+[(str(y),g[g.year==y]) for y in sorted(g.year.unique())]
            for split,gg in sets:
                if len(gg): rows.append({"spec":s,"period":period,"model":model,"split":split,**cls(gg,pred,prob)})
    return pd.DataFrame(rows)

def hac(d):
    out=[]
    for s,(target,features,_) in SPECS.items():
        g=d[d.year.isin([2023,2024])].dropna(subset=features+["ret_"+target])
        X=sm.add_constant(g[features],has_constant="add")
        f=sm.OLS(g["ret_"+target],X).fit(cov_type="HAC",cov_kwds={"maxlags":5})
        for z in features: out.append({"spec":s,"feature":z,"n":len(g),"beta":f.params[z],"hac_t":f.tvalues[z],"hac_p":f.pvalues[z],"r2":f.rsquared})
    return out

def get(m,s,period="DEV",model="OLS_SIGN",split="ALL"):
    z=m[(m.spec==s)&(m.period==period)&(m.model==model)&(m.split==split)]
    return None if z.empty else z.iloc[0]

def pct(v): return "NA" if v is None or not np.isfinite(float(v)) else f"{100*float(v):.2f}%"

def main():
    d=build(load15())
    preds=[predict(d,s,*cfg) for s,cfg in SPECS.items()]
    p=pd.concat(preds,ignore_index=True); m=metrics(p); h=hac(d)
    ov=m[(m.period=="DEV")&(m.model=="OLS_SIGN")&(m.split=="ALL")&m.spec.str.startswith("LIT_OVN0_")].sort_values(["balanced_accuracy","r2_os_ols"],ascending=False)
    lead=str(ov.iloc[0].spec)
    def stable(s):
        a=get(m,s); y3=get(m,s,split="2023"); y4=get(m,s,split="2024")
        return bool(a is not None and y3 is not None and y4 is not None and a.balanced_accuracy>0.5 and a.r2_os_ols>0 and y3.balanced_accuracy>0.5 and y4.balanced_accuracy>0.5)
    summary={"status":"COMPLETE","dev_years":[2023,2024],"transport_year":2025,"warmup_year":2022,"min_train":MIN_TRAIN,
             "ovn0_dev_leader":lead,"ovn0_stable_gate":stable(lead),"ovn1_stable_gate":stable("LIT_OVN1_PAIR"),
             "gate":"DEV pooled OLS-sign BA>50%, chronological OLS R2_OS>0, and 2023/2024 BA both >50%; 2025 not consulted.",
             "hac":h,"no_2025_selection":True}
    p.to_csv(OUTP,index=False);m.to_csv(OUTM,index=False);OUTS.write_text(json.dumps(summary,indent=2)+"\n")
    lines=["# GOLD EXECUTION LITERATURE STAGE-1 RESULT — 2026-10-07","","**Status:** COMPLETE / LOW-CAPACITY MECHANISM TEST","",
           "No 2025 result was used to choose an interval, sign, threshold or model family.","",
           "## OVERNIGHT 17:00 -> next 09:00","","| Spec | DEV BA | DEV R2_OS | 2023 BA | 2024 BA | 2025 BA | 2025 Acc |","|---|---:|---:|---:|---:|---:|---:|"]
    for s in ["LIT_OVN0_1530_1600","LIT_OVN0_1600_1630","LIT_OVN0_1630_1700","LIT_OVN1_PAIR"]:
        a=get(m,s);a3=get(m,s,split="2023");a4=get(m,s,split="2024");t=get(m,s,"TRANSPORT_2025")
        lines.append(f"| {s} | {pct(a.balanced_accuracy)} | {pct(a.r2_os_ols)} | {pct(a3.balanced_accuracy)} | {pct(a4.balanced_accuracy)} | {pct(t.balanced_accuracy)} | {pct(t.accuracy)} |")
    lines += ["",f"Development-only OVN0 leader: **{lead}**.",f"OVN0 stability gate: **{summary['ovn0_stable_gate']}**.",f"OVN1 pair stability gate: **{summary['ovn1_stable_gate']}**.","",
              "## DAY","","| Spec | Target | DEV BA | DEV R2_OS | 2023 BA | 2024 BA | 2025 BA | 2025 Acc |","|---|---|---:|---:|---:|---:|---:|---:|"]
    for s in ["LIT_DAY0_EXEC_0900","LIT_DAY1_DELAY_0930"]:
        a=get(m,s);a3=get(m,s,split="2023");a4=get(m,s,split="2024");t=get(m,s,"TRANSPORT_2025")
        lines.append(f"| {s} | {SPECS[s][0]} | {pct(a.balanced_accuracy)} | {pct(a.r2_os_ols)} | {pct(a3.balanced_accuracy)} | {pct(a4.balanced_accuracy)} | {pct(t.balanced_accuracy)} | {pct(t.accuracy)} |")
    lines += ["","LIT_DAY1_DELAY_0930 is a 09:30 decision challenger only; it is not a 09:00 backtest.",
              "LIT-OVN-2 state conditioning is allowed only if Stage-1 development evidence is coherent; no extra half-hour mining is allowed."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
