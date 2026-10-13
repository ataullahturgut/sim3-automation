#!/usr/bin/env python3
import json, os, math
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, average_precision_score, roc_auc_score

OUT = Path("gold_axis_2026")
OUT.mkdir(exist_ok=True)
BAR = 0.03
HORIZON_BARS = 480  # 5 x 96 observed M15 bars ~= 5 trading days
CLASSES = np.array(["NO_HIT","UP_FIRST","DOWN_FIRST"])

def load():
    url=os.environ["NEON_DATABASE_URL"]
    sql = """
      SELECT bar_start_utc, close_price
      FROM gold_research_histdata_xau15m_candidate
      WHERE bar_start_utc >= '2020-01-01'::timestamptz
        AND bar_start_utc <  '2026-10-01'::timestamptz
      ORDER BY bar_start_utc
    """
    with psycopg.connect(url) as con:
        df=pd.read_sql_query(sql, con)
    df["bar_start_utc"]=pd.to_datetime(df["bar_start_utc"], utc=True)
    df["available_ts"]=df["bar_start_utc"]+pd.Timedelta(minutes=15)
    df=df.drop_duplicates("available_ts",keep="last").sort_values("available_ts").reset_index(drop=True)
    return df

def build(df):
    px=df["close_price"].astype(float)
    lr=np.log(px).diff()
    X=pd.DataFrame(index=df.index)
    for n,name in [(1,"r15m"),(4,"r1h"),(12,"r3h"),(24,"r6h"),(48,"r12h"),(96,"r24h"),(192,"r48h")]:
        X[name]=np.log(px/px.shift(n))
    for n,name in [(12,"3h"),(24,"6h"),(48,"12h"),(96,"24h")]:
        rr=lr.rolling(n,min_periods=max(4,n//2))
        X[f"rv_{name}"]=rr.std()
        pos=lr.clip(lower=0).pow(2).rolling(n,min_periods=max(4,n//2)).mean()
        neg=lr.clip(upper=0).pow(2).rolling(n,min_periods=max(4,n//2)).mean()
        X[f"semidiff_{name}"]=(pos-neg)/(pos+neg+1e-12)
        path=lr.abs().rolling(n,min_periods=max(4,n//2)).sum()
        X[f"eff_{name}"]=np.log(px/px.shift(n)).abs()/(path+1e-12)
    roll_hi=px.rolling(96,min_periods=48).max()
    roll_lo=px.rolling(96,min_periods=48).min()
    X["dd_24h"]=px/roll_hi-1
    X["du_24h"]=px/roll_lo-1
    short_abs=lr.abs().rolling(4,min_periods=4).mean()
    long_abs=lr.abs().rolling(96,min_periods=48).median()
    X["range_expand_1h_vs24h"]=short_abs/(long_abs+1e-12)

    sigma=lr.rolling(96,min_periods=48).std().shift(1)
    z=(lr/(sigma+1e-12)).replace([np.inf,-np.inf],np.nan).fillna(0).clip(-8,8).to_numpy()
    sp=np.zeros(len(z)); sn=np.zeros(len(z)); k=.25
    for i,v in enumerate(z):
        if i:
            sp[i]=max(0.0, sp[i-1]+v-k)
            sn[i]=min(0.0, sn[i-1]+v+k)
        sp[i]=min(sp[i],25.0); sn[i]=max(sn[i],-25.0)
    X["cusum_pos"]=sp
    X["cusum_neg"]=-sn
    X["cusum_balance"]=sp+sn

    hourly=(df["available_ts"].dt.minute==0)
    pos=np.flatnonzero(hourly.to_numpy())
    rec=[]
    closes=px.to_numpy()
    times=df["available_ts"].to_numpy()
    for j in pos:
        if j+HORIZON_BARS >= len(df):
            continue
        p0=closes[j]
        fut=closes[j+1:j+1+HORIZON_BARS]
        up=np.flatnonzero(fut >= p0*(1+BAR))
        dn=np.flatnonzero(fut <= p0*(1-BAR))
        if len(up)==0 and len(dn)==0:
            y="NO_HIT"; hit=-1
        elif len(dn)==0 or (len(up) and up[0] < dn[0]):
            y="UP_FIRST"; hit=int(up[0])+1
        else:
            y="DOWN_FIRST"; hit=int(dn[0])+1
        maturity=j+HORIZON_BARS
        rec.append((j,df.loc[j,"available_ts"],p0,y,hit,df.loc[maturity,"available_ts"]))
    meta=pd.DataFrame(rec,columns=["row","decision_ts","price","y","hit_bars","maturity_ts"]).set_index("row")
    out=X.loc[meta.index].join(meta)
    out["year"]=out["decision_ts"].dt.year
    out=out.replace([np.inf,-np.inf],np.nan).dropna()
    return out

def probs_climatology(train, test):
    freq=train["y"].value_counts(normalize=True)
    arr=np.zeros((len(test),3))
    for i,c in enumerate(CLASSES): arr[:,i]=freq.get(c,0.0)
    arr=(arr+1e-6); arr/=arr.sum(1,keepdims=True)
    return arr

def fit_predict(train,test,features,C):
    pipe=Pipeline([
      ("scaler",StandardScaler()),
      ("lr",LogisticRegression(C=C,max_iter=1000,solver="lbfgs"))
    ])
    pipe.fit(train[features],train["y"])
    pp=pipe.predict_proba(test[features])
    cls=pipe.named_steps["lr"].classes_
    arr=np.zeros((len(test),3))
    for i,c in enumerate(CLASSES):
        if c in cls: arr[:,i]=pp[:,list(cls).index(c)]
    arr=np.clip(arr,1e-8,1); arr/=arr.sum(1,keepdims=True)
    return arr

def metrics(y, p):
    yi=np.array([np.where(CLASSES==v)[0][0] for v in y])
    pred=CLASSES[p.argmax(1)]
    one=np.eye(3)[yi]
    d={
      "n":len(y),
      "accuracy":float(accuracy_score(y,pred)),
      "macro_recall":float(np.mean([np.mean(pred[np.array(y)==c]==c) if np.any(np.array(y)==c) else np.nan for c in CLASSES])),
      "brier_multiclass":float(np.mean(np.sum((p-one)**2,axis=1))),
      "logloss":float(log_loss(y,p,labels=CLASSES)),
    }
    for i,c in enumerate(CLASSES):
        yy=(np.array(y)==c).astype(int)
        d[f"base_{c.lower()}"]=float(yy.mean())
        d[f"recall_{c.lower()}"]=float(np.mean(pred[yy==1]==c)) if yy.sum() else np.nan
        d[f"ap_{c.lower()}"]=float(average_precision_score(yy,p[:,i])) if 0<yy.sum()<len(yy) else np.nan
        d[f"auc_{c.lower()}"]=float(roc_auc_score(yy,p[:,i])) if 0<yy.sum()<len(yy) else np.nan
    return d

def mature_before(frame, cutoff):
    return frame[frame["maturity_ts"] < pd.Timestamp(cutoff,tz="UTC")]

df=load()
panel=build(df)
base_features=[c for c in panel.columns if c.startswith(("r","rv_","semidiff_","eff_","dd_","du_","range_"))]
cusum_features=base_features+["cusum_pos","cusum_neg","cusum_balance"]

# Select C only on 2025. Training labels must mature before 2025.
train24=mature_before(panel[panel["decision_ts"]<pd.Timestamp("2025-01-01",tz="UTC")],"2025-01-01")
val25=panel[(panel["decision_ts"]>=pd.Timestamp("2025-01-01",tz="UTC")) & (panel["decision_ts"]<pd.Timestamp("2026-01-01",tz="UTC"))]
val25=mature_before(val25,"2026-01-01")
Cs=[0.01,0.1,1.0,10.0]
selection={}
for name,features in [("PRICE",base_features),("PRICE_CUSUM",cusum_features)]:
    rows=[]
    for C in Cs:
        p=fit_predict(train24,val25,features,C)
        m=metrics(val25["y"].to_numpy(),p)
        rows.append({"C":C,**m})
    best=min(rows,key=lambda z:z["logloss"])
    selection[name]={"best_C":best["C"],"grid":rows}

records=[]
# Walk-forward descriptive 2023-2025 and frozen 2026 using 2025-selected C.
for year in [2023,2024,2025,2026]:
    start=pd.Timestamp(f"{year}-01-01",tz="UTC")
    end=pd.Timestamp(f"{year+1}-01-01",tz="UTC") if year<2026 else pd.Timestamp("2026-10-01",tz="UTC")
    train=panel[panel["decision_ts"]<start]
    train=mature_before(train,start)
    test=panel[(panel["decision_ts"]>=start)&(panel["decision_ts"]<end)]
    # test itself already excludes censored horizon because panel build requires full 480 future bars
    for model in ["CLIMATOLOGY","PRICE","PRICE_CUSUM"]:
        if model=="CLIMATOLOGY":
            p=probs_climatology(train,test)
        elif model=="PRICE":
            p=fit_predict(train,test,base_features,selection["PRICE"]["best_C"])
        else:
            p=fit_predict(train,test,cusum_features,selection["PRICE_CUSUM"]["best_C"])
        records.append({"year":year,"model":model,**metrics(test["y"].to_numpy(),p)})

met=pd.DataFrame(records)
met.to_csv(OUT/"GOLD_R78_FIRSTPASSAGE_3PCT_5TD_METRICS_20261013.csv",index=False)
summary={
  "status":"EXECUTED_RETROSPECTIVE_FIRST_PASSAGE_3PCT_5_TRADING_DAY",
  "source":"gold_research_histdata_xau15m_candidate",
  "decision_frequency":"hourly using last completed M15 close",
  "target":"which M15 close first crosses +3% or -3% within next 480 observed M15 bars, else NO_HIT",
  "barrier_pct":3.0,
  "horizon_observed_m15_bars":480,
  "selection":"C chosen by 2025 logloss only; final 2026 train uses only labels matured before 2026",
  "selected_C":{k:v["best_C"] for k,v in selection.items()},
  "n_panel":int(len(panel)),
  "panel_first":str(panel["decision_ts"].min()),
  "panel_last":str(panel["decision_ts"].max()),
  "metrics":records,
  "guardrails":["bar close available at bar_start+15m","features one-sided only","no 2026 threshold/model selection","2026 retrospective already inspected","hourly rows overlap and are not independent events"]
}
(OUT/"GOLD_R78_FIRSTPASSAGE_3PCT_5TD_SUMMARY_20261013.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

lines=["# GOLD R78 — ±3% / 5-trading-day first-passage first experiment (2026-10-13)","",
"**Status:** executed retrospective research; not a prospective trading claim.","",
"Target: at each hourly decision, using only the last completed M15 close and causal history, which barrier is reached first in the next 480 observed M15 bars: +3%, -3%, or neither.",
"",
"Model selection: regularization C selected only on 2025 log-loss; 2026 is scored with frozen C and training labels matured before 2026.","",
"## Metrics","",
met.to_markdown(index=False,floatfmt=".4f"),"",
"## Selected regularization","",
f"- PRICE C = {selection['PRICE']['best_C']}",
f"- PRICE+CUSUM C = {selection['PRICE_CUSUM']['best_C']}",
"",
"## Interpretation guardrails","",
"- Hourly decisions overlap; they are not  independent event samples.",
"- AUC/AP/Brier/log-loss are signal diagnostics, not bank P&L.",
"- 2026 has already been inspected in the broader project and is retrospective, not pristine.",
"- This experiment tests whether causal price structure contains transferable first-passage information before adding cross-market/macro features.",
]
(OUT/"GOLD_R78_FIRSTPASSAGE_3PCT_5TD_RESULT_20261013.md").write_text("\n".join(lines),encoding="utf-8")
print(met.to_string(index=False))
print(json.dumps(summary["selected_C"]))
