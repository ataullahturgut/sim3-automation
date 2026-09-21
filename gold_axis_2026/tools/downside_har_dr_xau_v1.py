from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from scipy.stats import rankdata

IDENTITY="DOWNSIDE_HAR_DR_XAU_V1_RESEARCH"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
FORM_END=date(2023,12,31)
VAL_START=date(2024,1,1); VAL_END=date(2024,12,31)
CH_START=date(2025,1,1); CH_END=date(2025,12,31)

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,dtype=float)
    k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_days(end_date):
    sql=f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where observation_ts < (%s::date + interval '1 day' + interval '6 hours')
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    intr as (
      select d,observation_ts,close,
             case when prev_close is not null and prev_close>0 then ln(close/prev_close) end as r
      from b
    )
    select d,count(*)::int as n_bars,
           (array_agg(close order by observation_ts desc))[1]::double precision as close,
           coalesce(sum(case when r<=0 then r*r else 0 end),0)::double precision as dr
    from intr
    group by d
    having count(*) >= {MIN_BARS}
    order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql,(end_date.isoformat(),))
            raw=cur.fetchall()
    ds=[]; close=[]; dr=[]; bars=[]
    for d,n,c,x in raw:
        c=float(c); x=float(x)
        if not (math.isfinite(c) and c>0 and math.isfinite(x) and x>=0): raise RuntimeError(f"BAD_ROW:{d}")
        ds.append(d); close.append(c); dr.append(x); bars.append(int(n))
    if len(ds)<600: raise RuntimeError(f"INSUFFICIENT_DAYS:{len(ds)}")
    return ds,np.array(close),np.array(dr),np.array(bars)

def panel_hash(ds,close,dr,through):
    s="\n".join(f"{d.isoformat()}|{c:.12f}|{x:.16g}" for d,c,x in zip(ds,close,dr) if d<=through)
    return hashlib.sha256(s.encode()).hexdigest()

def build_rows(ds,close,dr):
    rows=[]
    daily_ret=np.full(len(ds),np.nan)
    daily_ret[1:]=np.log(close[1:]/close[:-1])
    for i in range(21,len(ds)-1):
        target=i+1
        rows.append({
            "origin_date":ds[i].isoformat(),
            "target_date":ds[target].isoformat(),
            "dr_d":float(dr[i]),
            "dr_w":float(np.mean(dr[i-4:i+1])),
            "dr_m":float(np.mean(dr[i-21:i+1])),
            "target_dr":float(dr[target]),
            "target_close_return":float(daily_ret[target]),
        })
    return rows

def matrix(rows):
    X=np.array([[1.0,r["dr_d"],r["dr_w"],r["dr_m"]] for r in rows],dtype=float)
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    return X,y

def fit(rows):
    X,y=matrix(rows)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    yhat=X@b
    return b,yhat,float(np.linalg.cond(X))

def roc_auc(y,s):
    y=np.asarray(y,dtype=int); s=np.asarray(s,dtype=float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if n1==0 or n0==0:return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qlike(y,f):
    eps=1e-14
    yy=np.maximum(np.asarray(y,dtype=float),eps)
    ff=np.maximum(np.asarray(f,dtype=float),eps)
    ratio=yy/ff
    return float(np.mean(ratio-np.log(ratio)-1))

def evaluate(rows,beta,mean_dr,hi_thr,extreme_ret_thr):
    X,y=matrix(rows)
    pred=X@beta
    persistence=np.array([r["dr_d"] for r in rows],dtype=float)
    meanpred=np.full(len(rows),mean_dr,dtype=float)
    mse=float(np.mean((pred-y)**2)); mean_mse=float(np.mean((meanpred-y)**2)); per_mse=float(np.mean((persistence-y)**2))
    mae=float(np.mean(np.abs(pred-y)))
    corr=float(np.corrcoef(pred,y)[0,1]) if np.std(pred)>0 and np.std(y)>0 else None
    high=(y>=hi_thr).astype(int)
    alert=pred>=hi_thr
    tp=int(np.sum(alert & (high==1))); fp=int(np.sum(alert & (high==0)))
    fn=int(np.sum((~alert)&(high==1))); tn=int(np.sum((~alert)&(high==0)))
    precision=tp/(tp+fp) if tp+fp else None; recall=tp/(tp+fn) if tp+fn else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else 0.0
    ret=np.array([r["target_close_return"] for r in rows],dtype=float)
    down=ret<0
    extreme=ret<=extreme_ret_thr
    return {
        "n":len(rows),
        "mse":mse,"historical_mean_mse":mean_mse,"persistence_mse":per_mse,
        "oos_r2_vs_historical_mean":float(1-mse/mean_mse) if mean_mse>0 else None,
        "mae":mae,"qlike":qlike(y,pred),"persistence_qlike":qlike(y,persistence),
        "correlation":corr,
        "pred_min":float(np.min(pred)),"pred_median":float(np.median(pred)),"pred_max":float(np.max(pred)),
        "high_risk_threshold":hi_thr,"high_risk_event_rate":float(np.mean(high)),
        "high_risk_roc_auc":roc_auc(high,pred),
        "alert_coverage":float(np.mean(alert)),
        "alert_precision":precision,"alert_recall":recall,"alert_f1":f1,
        "tp":tp,"fp":fp,"fn":fn,"tn":tn,
        "unconditional_down_day_rate":float(np.mean(down)),
        "down_day_rate_given_alert":float(np.mean(down[alert])) if np.sum(alert) else None,
        "unconditional_extreme_negative_return_rate":float(np.mean(extreme)),
        "extreme_negative_return_rate_given_alert":float(np.mean(extreme[alert])) if np.sum(alert) else None,
    },pred

def gate24(m):
    return bool(m["oos_r2_vs_historical_mean"] is not None and m["oos_r2_vs_historical_mean"]>0
                and m["mse"]<m["persistence_mse"]
                and m["high_risk_roc_auc"] is not None and m["high_risk_roc_auc"]>=0.55
                and m["alert_precision"] is not None and m["alert_precision"]>m["high_risk_event_rate"])

def gate25(m,passed24):
    return bool(passed24 and m["oos_r2_vs_historical_mean"] is not None and m["oos_r2_vs_historical_mean"]>0
                and m["mse"]<m["persistence_mse"]
                and m["high_risk_roc_auc"] is not None and m["high_risk_roc_auc"]>=0.50
                and m["alert_precision"] is not None and m["alert_precision"]>m["high_risk_event_rate"])

def select(rows,start,end):
    return [r for r in rows if start<=date.fromisoformat(r["target_date"])<=end]

def write_csv(path,rows,pred):
    if not rows:return
    fields=list(rows[0].keys())+["har_dr_forecast"]
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r,p in zip(rows,pred):
            rr=dict(r);rr["har_dr_forecast"]=float(p);w.writerow(rr)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=("pre2025","2025"),required=True)
    ap.add_argument("--outdir",required=True);ap.add_argument("--config");ap.add_argument("--pre-result")
    a=ap.parse_args();out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    end=VAL_END if a.stage=="pre2025" else CH_END
    ds,close,dr,bars=load_days(end)
    rows=build_rows(ds,close,dr)

    if a.stage=="pre2025":
        train=[r for r in rows if date.fromisoformat(r["target_date"])<=FORM_END]
        val=select(rows,VAL_START,VAL_END)
        beta,train_pred,cond=fit(train)
        ytrain=np.array([r["target_dr"] for r in train],dtype=float)
        mean_dr=float(np.mean(ytrain))
        hi_thr=nearest_rank(ytrain,0.80)
        ret_train=np.array([r["target_close_return"] for r in train],dtype=float)
        ext_thr=nearest_rank(ret_train,0.05)
        m24,p24=evaluate(val,beta,mean_dr,hi_thr,ext_thr)
        passed=gate24(m24)
        cfg={
            "identity":IDENTITY,"source_table":TABLE,"timezone":TZ,
            "beta":[float(x) for x in beta],"condition_number":cond,
            "formation_n":len(train),"formation_mean_dr":mean_dr,
            "high_risk_threshold_q80":hi_thr,"extreme_negative_return_threshold_q05":ext_thr,
            "panel_sha256_through_2024":panel_hash(ds,close,dr,VAL_END),
            "frozen_before_2025":True,
        }
        res={"identity":IDENTITY,"status":"PRE2025_FROZEN","2024_validation":m24,
             "pre2025_gate_passed":passed,
             "decision":"PRE2025_DOWNSIDE_RISK_FORECAST_SUPPORTED" if passed else "PRE2025_DOWNSIDE_RISK_FORECAST_NOT_SUPPORTED"}
        (out/"GOLD_CONTROL_DOWNSIDE_HAR_DR_XAU_V1_FROZEN_CONFIG_2026-09-21.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
        (out/"GOLD_CONTROL_DOWNSIDE_HAR_DR_XAU_V1_PRE2025_RESULT_2026-09-21.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
        write_csv(out/"GOLD_CONTROL_DOWNSIDE_HAR_DR_XAU_V1_2024_FORECASTS_2026-09-21.csv",val,p24)
        print("HARDR_PRE2025_SUCCESS")
    else:
        if not a.config or not a.pre_result:raise RuntimeError("CONFIG_PRE_RESULT_REQUIRED")
        cfg=json.loads(Path(a.config).read_text());pre=json.loads(Path(a.pre_result).read_text())
        if cfg["identity"]!=IDENTITY or pre["identity"]!=IDENTITY:raise RuntimeError("IDENTITY_MISMATCH")
        if panel_hash(ds,close,dr,VAL_END)!=cfg["panel_sha256_through_2024"]:raise RuntimeError("PANEL_PREFIX_CHANGED")
        rows25=select(rows,CH_START,CH_END)
        beta=np.array(cfg["beta"],dtype=float)
        m25,p25=evaluate(rows25,beta,float(cfg["formation_mean_dr"]),float(cfg["high_risk_threshold_q80"]),float(cfg["extreme_negative_return_threshold_q05"]))
        trans=gate25(m25,bool(pre["pre2025_gate_passed"]))
        res={"identity":IDENTITY,"status":"LOCKED_2025_REPLAY_COMPLETE","2025_challenge":m25,
             "pre2025_gate_passed":pre["pre2025_gate_passed"],"2025_transport_passed":trans,
             "decision":"2025_DOWNSIDE_RISK_TRANSPORT_SUPPORTED" if trans else "2025_DOWNSIDE_RISK_TRANSPORT_NOT_SUPPORTED"}
        (out/"GOLD_CONTROL_DOWNSIDE_HAR_DR_XAU_V1_2025_RESULT_2026-09-21.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
        write_csv(out/"GOLD_CONTROL_DOWNSIDE_HAR_DR_XAU_V1_2025_FORECASTS_2026-09-21.csv",rows25,p25)
        print("HARDR_2025_SUCCESS")

if __name__=="__main__":
    main()
