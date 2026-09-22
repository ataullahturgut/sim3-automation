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
from scipy.optimize import minimize
from scipy.stats import rankdata

IDENTITY="DOWNSIDE_QHAR_DR_XAU_V1_RESEARCH"
PARENT="DOWNSIDE_HAR_DR_XAU_V1_RESEARCH"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
EPS=1e-14
FORM_END=date(2023,12,31)
VAL_START=date(2024,1,1); VAL_END=date(2024,12,31)
CH_START=date(2025,1,1); CH_END=date(2025,12,31)

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,dtype=float)
    if len(a)==0:
        raise RuntimeError("EMPTY_QUANTILE")
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
        if not (math.isfinite(c) and c>0 and math.isfinite(x) and x>=0):
            raise RuntimeError(f"BAD_ROW:{d}")
        ds.append(d); close.append(c); dr.append(x); bars.append(int(n))
    if len(ds)<600:
        raise RuntimeError(f"INSUFFICIENT_DAYS:{len(ds)}")
    return ds,np.array(close,dtype=float),np.array(dr,dtype=float),np.array(bars,dtype=int)

def panel_hash(ds,close,dr,through):
    s="\n".join(
        f"{d.isoformat()}|{c:.12f}|{x:.16g}"
        for d,c,x in zip(ds,close,dr) if d<=through
    )
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

def raw_matrix(rows):
    X=np.array([[1.0,r["dr_d"],r["dr_w"],r["dr_m"]] for r in rows],dtype=float)
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    return X,y

def formation_scaler(rows):
    X,y=raw_matrix(rows)
    mu=X[:,1:].mean(axis=0)
    sd=X[:,1:].std(axis=0,ddof=0)
    sd=np.where(sd<=1e-18,1.0,sd)
    Xs=np.column_stack([np.ones(len(X)),(X[:,1:]-mu)/sd])
    return Xs,y,mu,sd

def to_raw_beta(theta,mu,sd):
    theta=np.asarray(theta,dtype=float)
    beta=np.empty_like(theta)
    beta[1:]=theta[1:]/sd
    beta[0]=theta[0]-float(np.sum(theta[1:]*mu/sd))
    return beta

def fit_ols(rows):
    X,y=raw_matrix(rows)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return beta,float(np.linalg.cond(X))

def qlike_objective(theta,Xs,y):
    f=Xs@theta
    if np.any(~np.isfinite(f)) or np.any(f<EPS):
        return 1e100
    return float(np.mean(np.log(f)+y/f))

def qlike_gradient(theta,Xs,y):
    f=Xs@theta
    if np.any(~np.isfinite(f)) or np.any(f<EPS):
        return np.zeros_like(theta)
    w=(1.0/f)-(y/(f*f))
    return (Xs.T@w)/len(y)

def fit_qhar(rows):
    Xs,y,mu,sd=formation_scaler(rows)
    theta0=np.linalg.lstsq(Xs,y,rcond=None)[0]

    f0=Xs@theta0
    if np.min(f0)<EPS:
        # Keep identical linear form; only shift intercept enough to enter QLIKE domain.
        theta0=theta0.copy()
        theta0[0]+=EPS-float(np.min(f0))+1e-12

    cons={
        "type":"ineq",
        "fun":lambda th: Xs@th-EPS,
        "jac":lambda th: Xs,
    }
    res=minimize(
        qlike_objective,
        theta0,
        args=(Xs,y),
        jac=qlike_gradient,
        method="SLSQP",
        constraints=[cons],
        options={"maxiter":5000,"ftol":1e-12,"disp":False},
    )
    if not res.success:
        raise RuntimeError(f"QHAR_OPTIMIZER_FAILED:{res.message}")
    if not np.all(np.isfinite(res.x)):
        raise RuntimeError("QHAR_NONFINITE_THETA")
    fitted=Xs@res.x
    if np.any(fitted<EPS):
        raise RuntimeError("QHAR_FORMATION_NONPOSITIVE_FORECAST")

    beta=to_raw_beta(res.x,mu,sd)
    rawX,_=raw_matrix(rows)
    parity=np.max(np.abs(rawX@beta-fitted))
    if parity>1e-12:
        raise RuntimeError(f"QHAR_REPARAMETERIZATION_PARITY_FAILED:{parity}")

    return {
        "beta_raw":beta,
        "theta_scaled":np.asarray(res.x,dtype=float),
        "mu":mu,
        "sd":sd,
        "objective":float(res.fun),
        "iterations":int(res.nit),
        "message":str(res.message),
        "min_fitted":float(np.min(fitted)),
        "max_parity_error":float(parity),
    }

def predict(rows,beta):
    X,_=raw_matrix(rows)
    p=X@np.asarray(beta,dtype=float)
    if np.any(~np.isfinite(p)):
        raise RuntimeError("NONFINITE_FORECAST")
    if np.any(p<EPS):
        bad=np.where(p<EPS)[0][:10].tolist()
        raise RuntimeError(f"NONPOSITIVE_OOS_FORECAST:{bad}")
    return p

def roc_auc(y,s):
    y=np.asarray(y,dtype=int); s=np.asarray(s,dtype=float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if n1==0 or n0==0:
        return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qlike(y,f):
    yy=np.maximum(np.asarray(y,dtype=float),EPS)
    ff=np.asarray(f,dtype=float)
    if np.any(ff<EPS):
        raise RuntimeError("QLIKE_NONPOSITIVE_FORECAST")
    ratio=yy/ff
    return float(np.mean(ratio-np.log(ratio)-1))

def calibration(y,p):
    Z=np.column_stack([np.ones(len(p)),p])
    b=np.linalg.lstsq(Z,y,rcond=None)[0]
    return float(b[0]),float(b[1])

def evaluate(rows,pred,mean_dr,hi_thr,extreme_ret_thr):
    _,y=raw_matrix(rows)
    persistence=np.array([r["dr_d"] for r in rows],dtype=float)
    meanpred=np.full(len(rows),mean_dr,dtype=float)

    mse=float(np.mean((pred-y)**2))
    mean_mse=float(np.mean((meanpred-y)**2))
    per_mse=float(np.mean((persistence-y)**2))
    mae=float(np.mean(np.abs(pred-y)))
    corr=float(np.corrcoef(pred,y)[0,1]) if np.std(pred)>0 and np.std(y)>0 else None

    high=(y>=hi_thr).astype(int)
    alert=pred>=hi_thr
    tp=int(np.sum(alert & (high==1))); fp=int(np.sum(alert & (high==0)))
    fn=int(np.sum((~alert)&(high==1))); tn=int(np.sum((~alert)&(high==0)))
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else 0.0

    ret=np.array([r["target_close_return"] for r in rows],dtype=float)
    down=ret<0
    extreme=ret<=extreme_ret_thr
    ci,cs=calibration(y,pred)

    return {
        "n":len(rows),
        "mse":mse,
        "historical_mean_mse":mean_mse,
        "persistence_mse":per_mse,
        "oos_r2_vs_historical_mean":float(1-mse/mean_mse) if mean_mse>0 else None,
        "mae":mae,
        "qlike":qlike(y,pred),
        "historical_mean_qlike":qlike(y,meanpred),
        "persistence_qlike":qlike(y,persistence),
        "correlation":corr,
        "forecast_mean":float(np.mean(pred)),
        "realized_mean":float(np.mean(y)),
        "mean_ratio_realized_to_forecast":float(np.mean(y)/np.mean(pred)),
        "calibration_intercept":ci,
        "calibration_slope":cs,
        "pred_min":float(np.min(pred)),
        "pred_median":float(np.median(pred)),
        "pred_max":float(np.max(pred)),
        "high_risk_threshold":hi_thr,
        "high_risk_event_rate":float(np.mean(high)),
        "high_risk_roc_auc":roc_auc(high,pred),
        "alert_coverage":float(np.mean(alert)),
        "alert_precision":precision,
        "alert_recall":recall,
        "alert_f1":f1,
        "tp":tp,"fp":fp,"fn":fn,"tn":tn,
        "unconditional_down_day_rate":float(np.mean(down)),
        "down_day_rate_given_alert":float(np.mean(down[alert])) if np.sum(alert) else None,
        "unconditional_extreme_negative_return_rate":float(np.mean(extreme)),
        "extreme_negative_return_rate_given_alert":float(np.mean(extreme[alert])) if np.sum(alert) else None,
    }

def compare(qm,om):
    rel=(om["qlike"]-qm["qlike"])/om["qlike"]
    return {
        "qlike_delta_qhar_minus_ols":qm["qlike"]-om["qlike"],
        "qlike_relative_improvement_vs_ols":rel,
        "mse_delta_qhar_minus_ols":qm["mse"]-om["mse"],
        "auc_delta_qhar_minus_ols":(
            qm["high_risk_roc_auc"]-om["high_risk_roc_auc"]
            if qm["high_risk_roc_auc"] is not None and om["high_risk_roc_auc"] is not None else None
        ),
        "calibration_slope_delta_qhar_minus_ols":qm["calibration_slope"]-om["calibration_slope"],
    }

def gate24(qm,om):
    rel=(om["qlike"]-qm["qlike"])/om["qlike"]
    return bool(
        qm["qlike"] < om["qlike"]
        and qm["qlike"] < qm["persistence_qlike"]
        and rel >= 0.02
        and qm["high_risk_roc_auc"] is not None
        and qm["high_risk_roc_auc"] >= 0.55
        and qm["alert_precision"] is not None
        and qm["alert_precision"] > qm["high_risk_event_rate"]
        and qm["pred_min"] >= EPS
    )

def gate25(qm,om,passed24):
    return bool(
        passed24
        and qm["qlike"] <= om["qlike"]
        and qm["qlike"] < qm["persistence_qlike"]
        and qm["high_risk_roc_auc"] is not None
        and qm["high_risk_roc_auc"] >= 0.50
        and qm["alert_precision"] is not None
        and qm["alert_precision"] > qm["high_risk_event_rate"]
        and qm["pred_min"] >= EPS
    )

def select(rows,start,end):
    return [r for r in rows if start<=date.fromisoformat(r["target_date"])<=end]

def write_csv(path,rows,qpred,opred):
    if not rows:
        return
    fields=list(rows[0].keys())+["qhar_dr_forecast","ols_har_dr_forecast"]
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r,qp,op in zip(rows,qpred,opred):
            rr=dict(r)
            rr["qhar_dr_forecast"]=float(qp)
            rr["ols_har_dr_forecast"]=float(op)
            w.writerow(rr)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=("pre2025","2025"),required=True)
    ap.add_argument("--outdir",required=True)
    ap.add_argument("--config")
    ap.add_argument("--pre-result")
    a=ap.parse_args()

    out=Path(a.outdir)
    out.mkdir(parents=True,exist_ok=True)
    end=VAL_END if a.stage=="pre2025" else CH_END
    ds,close,dr,bars=load_days(end)
    rows=build_rows(ds,close,dr)

    if a.stage=="pre2025":
        train=[r for r in rows if date.fromisoformat(r["target_date"])<=FORM_END]
        val=select(rows,VAL_START,VAL_END)

        ols_beta,cond=fit_ols(train)
        qfit=fit_qhar(train)

        ytrain=np.array([r["target_dr"] for r in train],dtype=float)
        mean_dr=float(np.mean(ytrain))
        hi_thr=nearest_rank(ytrain,0.80)
        ret_train=np.array([r["target_close_return"] for r in train],dtype=float)
        ext_thr=nearest_rank(ret_train,0.05)

        q24=predict(val,qfit["beta_raw"])
        o24=predict(val,ols_beta)
        qm24=evaluate(val,q24,mean_dr,hi_thr,ext_thr)
        om24=evaluate(val,o24,mean_dr,hi_thr,ext_thr)
        cmp24=compare(qm24,om24)
        passed=gate24(qm24,om24)

        cfg={
            "identity":IDENTITY,
            "parent":PARENT,
            "source_table":TABLE,
            "timezone":TZ,
            "formation_n":len(train),
            "formation_mean_dr":mean_dr,
            "high_risk_threshold_q80":hi_thr,
            "extreme_negative_return_threshold_q05":ext_thr,
            "ols_beta":[float(x) for x in ols_beta],
            "ols_condition_number":cond,
            "qhar_beta":[float(x) for x in qfit["beta_raw"]],
            "qhar_theta_scaled":[float(x) for x in qfit["theta_scaled"]],
            "qhar_scaler_mu":[float(x) for x in qfit["mu"]],
            "qhar_scaler_sd":[float(x) for x in qfit["sd"]],
            "qhar_formation_objective":qfit["objective"],
            "qhar_iterations":qfit["iterations"],
            "qhar_optimizer_message":qfit["message"],
            "qhar_min_formation_forecast":qfit["min_fitted"],
            "qhar_reparameterization_max_error":qfit["max_parity_error"],
            "qlike_domain_epsilon":EPS,
            "panel_sha256_through_2024":panel_hash(ds,close,dr,VAL_END),
            "frozen_before_2025":True,
        }
        res={
            "identity":IDENTITY,
            "status":"PRE2025_FROZEN",
            "2024_validation":{
                "QHAR_DR":qm24,
                "OLS_HAR_DR":om24,
                "comparison":cmp24,
            },
            "pre2025_gate_passed":passed,
            "decision":"PRE2025_QLIKE_ESTIMATION_SUPPORTED" if passed else "PRE2025_QLIKE_ESTIMATION_NOT_SUPPORTED",
        }

        (out/"GOLD_CONTROL_DOWNSIDE_QHAR_DR_XAU_V1_FROZEN_CONFIG_2026-09-22.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
        (out/"GOLD_CONTROL_DOWNSIDE_QHAR_DR_XAU_V1_PRE2025_RESULT_2026-09-22.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
        write_csv(out/"GOLD_CONTROL_DOWNSIDE_QHAR_DR_XAU_V1_2024_FORECASTS_2026-09-22.csv",val,q24,o24)
        print("QHARDR_PRE2025_SUCCESS")
        return

    if not a.config or not a.pre_result:
        raise RuntimeError("CONFIG_PRE_RESULT_REQUIRED")

    cfg=json.loads(Path(a.config).read_text(encoding="utf-8"))
    pre=json.loads(Path(a.pre_result).read_text(encoding="utf-8"))
    if cfg["identity"]!=IDENTITY or pre["identity"]!=IDENTITY:
        raise RuntimeError("IDENTITY_MISMATCH")
    if panel_hash(ds,close,dr,VAL_END)!=cfg["panel_sha256_through_2024"]:
        raise RuntimeError("PANEL_PREFIX_CHANGED")

    rows25=select(rows,CH_START,CH_END)
    qbeta=np.array(cfg["qhar_beta"],dtype=float)
    obeta=np.array(cfg["ols_beta"],dtype=float)

    q25=predict(rows25,qbeta)
    o25=predict(rows25,obeta)
    qm25=evaluate(
        rows25,q25,
        float(cfg["formation_mean_dr"]),
        float(cfg["high_risk_threshold_q80"]),
        float(cfg["extreme_negative_return_threshold_q05"]),
    )
    om25=evaluate(
        rows25,o25,
        float(cfg["formation_mean_dr"]),
        float(cfg["high_risk_threshold_q80"]),
        float(cfg["extreme_negative_return_threshold_q05"]),
    )
    cmp25=compare(qm25,om25)
    trans=gate25(qm25,om25,bool(pre["pre2025_gate_passed"]))

    res={
        "identity":IDENTITY,
        "status":"LOCKED_2025_REPLAY_COMPLETE",
        "2025_challenge":{
            "QHAR_DR":qm25,
            "OLS_HAR_DR":om25,
            "comparison":cmp25,
        },
        "pre2025_gate_passed":pre["pre2025_gate_passed"],
        "2025_transport_passed":trans,
        "decision":"2025_QLIKE_TRANSPORT_SUPPORTED" if trans else "2025_QLIKE_TRANSPORT_NOT_SUPPORTED",
    }

    (out/"GOLD_CONTROL_DOWNSIDE_QHAR_DR_XAU_V1_2025_RESULT_2026-09-22.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
    write_csv(out/"GOLD_CONTROL_DOWNSIDE_QHAR_DR_XAU_V1_2025_FORECASTS_2026-09-22.csv",rows25,q25,o25)

    v=pre["2024_validation"]
    lines=[
        "# GOLD CONTROL — QLIKE-ESTIMATED HAR-DR V1 RESULT",
        "",
        f"**Identity:** `{IDENTITY}`  ",
        "**Manifest update:** deferred pending user review.  ",
        "",
        "## Main comparison",
        "",
        "| Period | Model | QLIKE | MSE | OOS R2 | High-risk AUC | Precision | Recall | Calibration slope |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label,block in [("2024",v),("2025",res["2025_challenge"])]:
        for name in ("QHAR_DR","OLS_HAR_DR"):
            m=block[name]
            lines.append(
                f"| {label} | {name} | {m['qlike']:.6f} | {m['mse']:.6g} | "
                f"{m['oos_r2_vs_historical_mean']:.4f} | {m['high_risk_roc_auc']:.4f} | "
                f"{(m['alert_precision'] if m['alert_precision'] is not None else float('nan')):.4f} | "
                f"{(m['alert_recall'] if m['alert_recall'] is not None else float('nan')):.4f} | "
                f"{m['calibration_slope']:.4f} |"
            )
    lines += [
        "",
        "## Frozen decisions",
        "",
        f"- 2024 QLIKE-estimation gate: **{'PASS' if pre['pre2025_gate_passed'] else 'FAIL'}**.",
        f"- 2025 transport gate: **{'PASS' if trans else 'FAIL'}**.",
        "- No adaptive calibration state or post-2025 rescue was used.",
        "- No manifest change was made by this workflow.",
    ]
    (out/"GOLD_CONTROL_DOWNSIDE_QHAR_DR_XAU_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("QHARDR_2025_SUCCESS")

if __name__=="__main__":
    main()
