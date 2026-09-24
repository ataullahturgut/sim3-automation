from __future__ import annotations

import argparse, calendar, json, math, os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

IDENTITY = "GOLD_CONTROL_DAILY_MIXED_FREQUENCY_MIDAS_V1_RESEARCH"
METALS = ("Gold","Silver","Platinum","Palladium")
DAILY_SERIES = {
    "Gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "Silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "Platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "Palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
GPR_PIT = "GPR_OFFICIAL_GIT_PIT"
START = "2020-01-01"
END = "2026-09-01"
PRED_START = pd.Timestamp("2022-01-01")
MIN_TRAIN = 250
FAST_LAGS = 60
SLOW_LAGS = 12
TAIL_Q = 0.67

def month_key(x):
    return x[:7] if isinstance(x,str) else f"{x.year:04d}-{x.month:02d}"

def month_shift(m,delta):
    y,mo=map(int,m.split("-")); z=y*12+mo-1+delta
    return f"{z//12:04d}-{z%12+1:02d}"

def month_end_utc(m):
    y,mo=map(int,m.split("-")); d=calendar.monthrange(y,mo)[1]
    return datetime(y,mo,d,23,59,59,tzinfo=timezone.utc)

def authority_invariants(cur):
    out={}
    for name in ("monthly_forecast_contracts","decision_signal_snapshots","decision_runs","decision_events"):
        cur.execute(f"SELECT count(*) FROM {name}"); out[name]=int(cur.fetchone()[0])
    return out

def load_daily_xau(cur):
    sql=r"""
    WITH raw AS (
      SELECT observation_ts,
             close::double precision AS close,
             ((observation_ts AT TIME ZONE 'America/New_York') + interval '7 hours')::date AS trade_date,
             (observation_ts AT TIME ZONE 'America/New_York')::time AS ny_time,
             date_bin(interval '5 minutes', observation_ts, timestamptz '2000-01-01 00:00:00+00') AS bucket5
      FROM xau_intraday_research_cache_1m
      WHERE observation_ts >= %s::timestamptz
        AND observation_ts < %s::timestamptz
        AND close > 0
    ), five AS (
      SELECT DISTINCT ON (trade_date,bucket5) trade_date,bucket5,observation_ts,close
      FROM raw ORDER BY trade_date,bucket5,observation_ts DESC
    ), fr AS (
      SELECT trade_date,bucket5,close,
             ln(close/lag(close) OVER (PARTITION BY trade_date ORDER BY bucket5)) AS r5
      FROM five
    ), rv AS (
      SELECT trade_date,count(r5) AS n5,
             sum(r5*r5) AS rv,
             sum(r5*r5) FILTER (WHERE r5<0) AS rs_minus,
             sum(r5*r5) FILTER (WHERE r5>0) AS rs_plus
      FROM fr GROUP BY trade_date
    ), ep AS (
      SELECT trade_date,
             max(close) FILTER (WHERE ny_time='03:29:00') AS c0329,
             max(close) FILTER (WHERE ny_time='07:59:00') AS c0759,
             max(close) FILTER (WHERE ny_time='16:59:00') AS c1659
      FROM raw GROUP BY trade_date
    )
    SELECT r.trade_date,r.n5,r.rv,r.rs_minus,r.rs_plus,e.c0329,e.c0759,e.c1659
    FROM rv r LEFT JOIN ep e USING(trade_date)
    ORDER BY r.trade_date
    """
    cur.execute(sql,(START,END))
    rows=cur.fetchall()
    d=pd.DataFrame(rows,columns=["trade_date","n5","rv","rs_minus","rs_plus","c0329","c0759","c1659"])
    d["trade_date"]=pd.to_datetime(d["trade_date"])
    for c in ["n5","rv","rs_minus","rs_plus","c0329","c0759","c1659"]:
        d[c]=pd.to_numeric(d[c],errors="coerce")
    d=d[d["c1659"].gt(0)].copy().sort_values("trade_date").reset_index(drop=True)
    d["ret"]=np.log(d["c1659"]/d["c1659"].shift(1))
    d["abs_ret"]=d["ret"].abs()
    d["neg_ret"]=np.minimum(d["ret"],0.0)
    d["downside_share"]=d["rs_minus"]/d["rv"].replace(0,np.nan)
    d["europe_ret"]=np.where(d["c0329"].gt(0)&d["c0759"].gt(0),np.log(d["c0759"]/d["c0329"]),np.nan)
    d["target_date"]=d["trade_date"].shift(-1)
    d["r_next"]=np.log(d["c1659"].shift(-1)/d["c1659"])
    d=d[d["target_date"].notna() & np.isfinite(d["r_next"])].copy().reset_index(drop=True)
    return d

def load_monthly(cur):
    raw={}
    checks={}
    for metal,sid in DAILY_SERIES.items():
        cur.execute("SELECT observation_ts,value FROM observations WHERE series_id=%s ORDER BY observation_ts",(sid,))
        z=defaultdict(list)
        for ts,v in cur.fetchall():
            z[month_key(ts)].append(float(v))
        mm={m:float(np.mean(v)) for m,v in z.items() if len(v)>=5}
        rr={}
        for m in sorted(mm):
            p=month_shift(m,-1)
            if p in mm and mm[p]>0 and mm[m]>0: rr[m]=float(math.log(mm[m]/mm[p]))
        raw[metal]=rr
        checks[metal]={"months":len(mm),"returns":len(rr),"first":min(rr) if rr else None,"last":max(rr) if rr else None}

    cur.execute("SELECT observation_ts,value,available_as_of,metadata->>'origin_month' FROM observations WHERE series_id=%s ORDER BY metadata->>'origin_month',observation_ts",(GPR_PIT,))
    vint=defaultdict(dict); avail={}
    for ts,v,a,om in cur.fetchall():
        if not om: continue
        vint[om][month_key(ts)]=float(v)
        avail[om]=min(avail.get(om,a),a)
    checks["gpr_vintages"]={"n":len(vint),"first":min(vint) if vint else None,"last":max(vint) if vint else None}
    return raw,dict(vint),avail,checks

def almon_basis(seq):
    x=np.asarray(seq,float)
    if len(x)<2 or not np.all(np.isfinite(x)): return [np.nan,np.nan,np.nan]
    # x[0] is most recent lag. Fixed polynomial MIDAS basis; coefficients are learned by downstream model.
    u=np.linspace(0.0,1.0,len(x))
    b0=np.ones(len(x))
    b1=1.0-2.0*u
    b2=6.0*u*u-6.0*u+1.0
    return [float(np.mean(x*b0)),float(np.mean(x*b1)),float(np.mean(x*b2))]

def seq_from_series(values,i,L):
    # include information observable at origin i; most recent first
    if i-L+1<0: return None
    z=values[i-L+1:i+1][::-1]
    return z if np.all(np.isfinite(z)) else None

def gpr_sequence(vintages,availability,origin_date,L):
    m=month_key(origin_date); vo=month_shift(m,-1)
    hist=vintages.get(vo)
    if hist is None: return None
    a=availability.get(vo)
    if a is None or a>month_end_utc(vo): return None
    end=month_shift(m,-2)  # strict completed/PIT lag
    vals=[]
    cur=end
    for _ in range(L):
        if cur not in hist: return None
        vals.append(float(hist[cur])); cur=month_shift(cur,-1)
    return vals

def slow_sequence(monthly_ret,metal,origin_date,L):
    cur=month_shift(month_key(origin_date),-1)
    vals=[]
    for _ in range(L):
        if cur not in monthly_ret[metal]: return None
        vals.append(float(monthly_ret[metal][cur])); cur=month_shift(cur,-1)
    return vals

def build_panel(d,monthly,vint,avail):
    fast_cols=["ret","abs_ret","neg_ret","rv","downside_share","europe_ret"]
    rows=[]
    arrays={c:d[c].to_numpy(float) for c in fast_cols}
    for i,r in d.iterrows():
        od=pd.Timestamp(r["trade_date"])
        z={"origin_date":od,"target_date":pd.Timestamp(r["target_date"]),"r_next":float(r["r_next"])}
        ok=True
        for c in fast_cols:
            s=seq_from_series(arrays[c],i,FAST_LAGS)
            if s is None: ok=False; break
            for j,v in enumerate(almon_basis(s)): z[f"F_{c}_A{j}"]=v
        if not ok: continue
        slow_ok=True
        for metal in METALS:
            s=slow_sequence(monthly,metal,od,SLOW_LAGS)
            if s is None: slow_ok=False; break
            for j,v in enumerate(almon_basis(s)): z[f"M_{metal}_A{j}"]=v
        gs=gpr_sequence(vint,avail,od,SLOW_LAGS)
        if gs is None: slow_ok=False
        else:
            for j,v in enumerate(almon_basis(gs)): z[f"M_GPR_A{j}"]=v
        z["slow_available"]=bool(slow_ok)
        rows.append(z)
    p=pd.DataFrame(rows).sort_values("origin_date").reset_index(drop=True)
    # origin-safe material threshold from already matured one-day returns only
    p["tail_cutoff"]=p["r_next"].abs().shift(1).expanding(min_periods=120).quantile(TAIL_Q)
    p["y_up"]=(p["r_next"]>0).astype(int)
    p["y_tail_up"]=(p["r_next"]>p["tail_cutoff"]).astype(int)
    p["y_tail_down"]=(p["r_next"]<-p["tail_cutoff"]).astype(int)
    return p

def pipe_logit():
    return Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler()),("m",LogisticRegression(C=1.0,solver="lbfgs",max_iter=4000,random_state=0))])

def pipe_ridge():
    return Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler()),("m",Ridge(alpha=1.0))])

def predict_walk(panel,features,label):
    out=[]
    for i,row in panel.iterrows():
        if row["origin_date"]<PRED_START: continue
        hist=panel.iloc[:i].copy()
        # target of the immediately preceding row is known at this origin; all earlier are matured
        hist=hist[np.isfinite(hist["r_next"])].copy()
        if label.startswith("tail"):
            hist=hist[np.isfinite(hist["tail_cutoff"])].copy()
        if len(hist)<MIN_TRAIN: continue
        X=hist[features]; x=panel.loc[[i],features]
        y=hist["y_up"].to_numpy(int)
        if len(np.unique(y))<2: continue
        logit=pipe_logit(); logit.fit(X,y); p_up=float(logit.predict_proba(x)[0,1])
        ridge=pipe_ridge(); ridge.fit(X,hist["r_next"].to_numpy(float)); rhat=float(ridge.predict(x)[0])

        # independent material UP/DOWN heads; labels are non-complements because neutral days exist
        hu=hist["y_tail_up"].to_numpy(int); hd=hist["y_tail_down"].to_numpy(int)
        if len(np.unique(hu))<2 or len(np.unique(hd))<2: continue
        lu=pipe_logit(); ld=pipe_logit(); lu.fit(X,hu); ld.fit(X,hd)
        ptu=float(lu.predict_proba(x)[0,1]); ptd=float(ld.predict_proba(x)[0,1])
        out.append({
            "origin_date":row["origin_date"].strftime("%Y-%m-%d"),
            "target_date":row["target_date"].strftime("%Y-%m-%d"),
            "r_next":float(row["r_next"]),"actual_up":int(row["y_up"]),
            "tail_cutoff":None if not np.isfinite(row["tail_cutoff"]) else float(row["tail_cutoff"]),
            "actual_tail_up":int(row["y_tail_up"]),"actual_tail_down":int(row["y_tail_down"]),
            "p_up_logit":p_up,"rhat_ridge":rhat,"p_tail_up":ptu,"p_tail_down":ptd,
            "tail_margin":ptu-ptd,"train_n":int(len(hist))
        })
    return pd.DataFrame(out)

def safe_div(a,b): return None if b==0 else float(a/b)

def direction_metrics(df,score,pred):
    y=df["actual_up"].to_numpy(int); yh=np.asarray(pred,int); sc=np.asarray(score,float)
    tp=int(((yh==1)&(y==1)).sum()); fp=int(((yh==1)&(y==0)).sum())
    tn=int(((yh==0)&(y==0)).sum()); fn=int(((yh==0)&(y==1)).sum())
    upr=safe_div(tp,tp+fn); dnr=safe_div(tn,tn+fp)
    auc=float(roc_auc_score(y,sc)) if len(np.unique(y))==2 else None
    return {
      "n":int(len(df)),"actual_up":int((y==1).sum()),"actual_down":int((y==0).sum()),
      "tp":tp,"fp":fp,"tn":tn,"fn":fn,
      "up_precision":safe_div(tp,tp+fp),"up_recall":upr,"false_up_fpr":safe_div(fp,fp+tn),
      "down_precision":safe_div(tn,tn+fn),"down_recall":dnr,
      "balanced_accuracy":None if upr is None or dnr is None else float((upr+dnr)/2),
      "accuracy":safe_div(tp+tn,len(df)),"auc":auc,
      "youden_j":None if upr is None else float(upr-safe_div(fp,fp+tn))
    }

def tail_metrics(df,col,score):
    y=df[col].to_numpy(int); sc=np.asarray(score,float)
    if len(np.unique(y))<2: return {"n":int(len(df)),"auc":None}
    pred=(sc>=0.5).astype(int)
    tp=int(((pred==1)&(y==1)).sum()); fp=int(((pred==1)&(y==0)).sum())
    tn=int(((pred==0)&(y==0)).sum()); fn=int(((pred==0)&(y==1)).sum())
    return {"n":int(len(df)),"positive_n":int(y.sum()),"auc":float(roc_auc_score(y,sc)),
            "brier":float(brier_score_loss(y,sc)),"calls":int(pred.sum()),
            "precision":safe_div(tp,tp+fp),"recall":safe_div(tp,tp+fn),"fpr":safe_div(fp,fp+tn)}

def period_metrics(pred):
    out={}
    periods={"2022":"2022","2023":"2023","2024":"2024","2025":"2025","2026":"2026",
             "PRE2025_2022_2024":None}
    for name,year in periods.items():
        if year is None:
            g=pred[pred["origin_date"].str[:4].isin(["2022","2023","2024"])].copy()
        else: g=pred[pred["origin_date"].str[:4]==year].copy()
        if g.empty: continue
        out[name]={
          "logistic_direction":direction_metrics(g,g["p_up_logit"],(g["p_up_logit"]>=0.5).astype(int)),
          "ridge_direction":direction_metrics(g,g["rhat_ridge"],(g["rhat_ridge"]>0).astype(int)),
          "two_head_tail_margin_direction":direction_metrics(g,g["tail_margin"],(g["tail_margin"]>=0).astype(int)),
          "material_up_head":tail_metrics(g,"actual_tail_up",g["p_tail_up"]),
          "material_down_head":tail_metrics(g,"actual_tail_down",g["p_tail_down"]),
        }
    return out

def run(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only=on")
        before=authority_invariants(cur)
        d=load_daily_xau(cur)
        monthly,vint,avail,source_checks=load_monthly(cur)
    panel=build_panel(d,monthly,vint,avail)
    fast=[c for c in panel.columns if c.startswith("F_")]
    slow=[c for c in panel.columns if c.startswith("M_")]
    # mixed rows require complete slow information; fast-only retains all fast-ready rows.
    pfast=panel.copy()
    pmix=panel[panel["slow_available"]].copy().reset_index(drop=True)

    pred_fast=predict_walk(pfast,fast,"tail")
    pred_mix=predict_walk(pmix,fast+slow,"tail")

    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only=on")
        after=authority_invariants(cur)

    result={
      "identity":IDENTITY,
      "status":"RESEARCH_ONLY_NOT_RUNTIME",
      "method":{
        "target":"next exact NY17 log return / sign",
        "fast_midas_basis":"60 completed/current-origin daily lags compressed by fixed degree-2 Almon basis",
        "slow_midas_basis":"12 completed monthly lags compressed by fixed degree-2 Almon basis",
        "slow_inputs":"Gold/Silver/Platinum/Palladium monthly returns + PIT GPR vintage lagged strictly",
        "models":["L2 logistic direction","ridge continuous return","independent material-UP and material-DOWN logistic heads"],
        "tail_definition":"origin-safe rolling 67th percentile of absolute one-day return; material heads are non-complementary",
        "hyperparameter_search":"NONE",
        "random_split":False,
        "2025_tuning":False,
        "2026_tuning":False,
      },
      "source_checks":source_checks,
      "panel":{"daily_raw_n":int(len(d)),"feature_panel_n":int(len(panel)),"fast_features":len(fast),"slow_features":len(slow),
               "mixed_ready_n":int(len(pmix)),"first":panel["origin_date"].min().strftime("%Y-%m-%d"),"last":panel["origin_date"].max().strftime("%Y-%m-%d")},
      "FAST_ONLY":{"metrics":period_metrics(pred_fast),"prediction_rows":pred_fast.to_dict("records")},
      "MIXED_FREQ_MIDAS":{"metrics":period_metrics(pred_mix),"prediction_rows":pred_mix.to_dict("records")},
      "authority_invariants_before":before,"authority_invariants_after":after,"authority_invariants_unchanged":before==after,
      "governance":{"database_writes":"NONE","runtime_promotion":"NONE","canonical_branch_modified":False}
    }
    return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIXED_FREQUENCY_MIDAS_V1_RESULT_2026-09-24.json")
    a=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    result=run(dsn)
    Path(a.out).write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
    slim={k:v for k,v in result.items() if k not in ("FAST_ONLY","MIXED_FREQ_MIDAS")}
    slim["FAST_ONLY_METRICS"]=result["FAST_ONLY"]["metrics"]
    slim["MIXED_FREQ_MIDAS_METRICS"]=result["MIXED_FREQ_MIDAS"]["metrics"]
    print(json.dumps(slim,indent=2,default=str))

if __name__=="__main__": main()
