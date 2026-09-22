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

IDENTITY="DOWNSIDE_SQRT_QHAR_DR_XAU_V1_RESEARCH"
PARENT="DOWNSIDE_HAR_DR_XAU_V1_RESEARCH"
FAILED_PRECURSOR="DOWNSIDE_QHAR_DR_XAU_V1_RESEARCH"
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

    ds=[]; close=[]; dr=[]
    for d,n,c,x in raw:
        c=float(c); x=float(x)
        if not (math.isfinite(c) and c>0 and math.isfinite(x) and x>=0):
            raise RuntimeError(f"BAD_ROW:{d}")
        ds.append(d); close.append(c); dr.append(x)
    if len(ds)<600:
        raise RuntimeError(f"INSUFFICIENT_DAYS:{len(ds)}")
    return ds,np.array(close,dtype=float),np.array(dr,dtype=float)

def panel_hash(ds,close,dr,through):
    s="\n".join(
        f"{d.isoformat()}|{c:.12f}|{x:.16g}"
        for d,c,x in zip(ds,close,dr) if d<=through
    )
    return hashlib.sha256(s.encode()).hexdigest()

def build_rows(ds,close,dr):
    sd=np.sqrt(dr)
    daily_ret=np.full(len(ds),np.nan)
    daily_ret[1:]=np.log(close[1:]/close[:-1])

    rows=[]
    for i in range(21,len(ds)-1):
        target=i+1
        rows.append({
            "origin_date":ds[i].isoformat(),
            "target_date":ds[target].isoformat(),

            "dr_d":float(dr[i]),
            "dr_w":float(np.mean(dr[i-4:i+1])),
            "dr_m":float(np.mean(dr[i-21:i+1])),

            "sd_d":float(sd[i]),
            "sd_w":float(np.mean(sd[i-4:i+1])),
            "sd_m":float(np.mean(sd[i-21:i+1])),

            "target_dr":float(dr[target]),
            "target_sd":float(sd[target]),
            "target_close_return":float(daily_ret[target]),
        })
    return rows

def raw_matrix(rows):
    X=np.array([[1.0,r["dr_d"],r["dr_w"],r["dr_m"]] for r in rows],dtype=float)
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    return X,y

def sd_matrix(rows):
    X=np.array([[1.0,r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],dtype=float)
    y=np.array([r["target_sd"] for r in rows],dtype=float)
    return X,y

def fit_ols(X,y):
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

def to_raw_beta(theta,mu,sd):
    theta=np.asarray(theta,dtype=float)
    beta=np.empty_like(theta)
    beta[1:]=theta[1:]/sd
    beta[0]=theta[0]-float(np.sum(theta[1:]*mu/sd))
    return beta

def fit_qhar_sd(rows):
    X,y=sd_matrix(rows)
    mu=X[:,1:].mean(axis=0)
    scale=X[:,1:].std(axis=0,ddof=0)
    scale=np.where(scale<=1e-18,1.0,scale)
    Xs=np.column_stack([np.ones(len(X)),(X[:,1:]-mu)/scale])

    theta0=np.linalg.lstsq(Xs,y,rcond=None)[0]
    f0=Xs@theta0
    shifted=False
    if np.min(f0)<EPS:
        theta0=theta0.copy()
        theta0[0]+=EPS-float(np.min(f0))+1e-12
        shifted=True

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
        raise RuntimeError(f"QHAR_SD_OPTIMIZER_FAILED:{res.message}")
    if not np.all(np.isfinite(res.x)):
        raise RuntimeError("QHAR_SD_NONFINITE_THETA")

    fitted=Xs@res.x
    if np.any(fitted<EPS):
        raise RuntimeError("QHAR_SD_FORMATION_NONPOSITIVE")

    beta=to_raw_beta(res.x,mu,scale)
    parity=np.max(np.abs(X@beta-fitted))
    if parity>1e-12:
        raise RuntimeError(f"QHAR_SD_REPARAMETERIZATION_FAILED:{parity}")

    return {
        "beta":beta,
        "theta":np.asarray(res.x,dtype=float),
        "mu":mu,
        "scale":scale,
        "objective":float(res.fun),
        "iterations":int(res.nit),
        "message":str(res.message),
        "min_fitted":float(np.min(fitted)),
        "initial_intercept_shifted_for_domain":shifted,
        "parity_error":float(parity),
    }

def predict(X,beta,positive_required=False,label="MODEL"):
    p=X@np.asarray(beta,dtype=float)
    if np.any(~np.isfinite(p)):
        raise RuntimeError(f"{label}_NONFINITE_FORECAST")
    if positive_required and np.any(p<EPS):
        bad=np.where(p<EPS)[0][:10].tolist()
        raise RuntimeError(f"{label}_NONPOSITIVE_FORECAST:{bad}")
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

def dr_metrics(rows,pred_dr,mean_dr,hi_thr,extreme_ret_thr):
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    persistence=np.array([r["dr_d"] for r in rows],dtype=float)
    meanpred=np.full(len(rows),mean_dr,dtype=float)

    mse=float(np.mean((pred_dr-y)**2))
    mean_mse=float(np.mean((meanpred-y)**2))
    per_mse=float(np.mean((persistence-y)**2))
    mae=float(np.mean(np.abs(pred_dr-y)))
    corr=float(np.corrcoef(pred_dr,y)[0,1]) if np.std(pred_dr)>0 and np.std(y)>0 else None

    high=(y>=hi_thr).astype(int)
    alert=pred_dr>=hi_thr
    tp=int(np.sum(alert & (high==1))); fp=int(np.sum(alert & (high==0)))
    fn=int(np.sum((~alert)&(high==1))); tn=int(np.sum((~alert)&(high==0)))
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else 0.0

    ret=np.array([r["target_close_return"] for r in rows],dtype=float)
    down=ret<0
    extreme=ret<=extreme_ret_thr
    ci,cs=calibration(y,pred_dr)

    return {
        "n":len(rows),
        "mse":mse,
        "historical_mean_mse":mean_mse,
        "persistence_mse":per_mse,
        "oos_r2_vs_historical_mean":float(1-mse/mean_mse) if mean_mse>0 else None,
        "mae":mae,
        "dr_qlike":qlike(y,pred_dr),
        "historical_mean_dr_qlike":qlike(y,meanpred),
        "persistence_dr_qlike":qlike(y,persistence),
        "correlation":corr,
        "forecast_mean":float(np.mean(pred_dr)),
        "realized_mean":float(np.mean(y)),
        "mean_ratio_realized_to_forecast":float(np.mean(y)/np.mean(pred_dr)),
        "calibration_intercept":ci,
        "calibration_slope":cs,
        "pred_min":float(np.min(pred_dr)),
        "pred_median":float(np.median(pred_dr)),
        "pred_max":float(np.max(pred_dr)),
        "high_risk_threshold":hi_thr,
        "high_risk_event_rate":float(np.mean(high)),
        "high_risk_roc_auc":roc_auc(high,pred_dr),
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

def sd_metrics(rows,pred_sd):
    y=np.array([r["target_sd"] for r in rows],dtype=float)
    return {
        "sd_mse":float(np.mean((pred_sd-y)**2)),
        "sd_mae":float(np.mean(np.abs(pred_sd-y))),
        "sd_qlike":qlike(y,pred_sd),
        "pred_sd_min":float(np.min(pred_sd)),
        "pred_sd_median":float(np.median(pred_sd)),
        "pred_sd_max":float(np.max(pred_sd)),
    }

def select(rows,start,end):
    return [r for r in rows if start<=date.fromisoformat(r["target_date"])<=end]

def compare(q_sd,q_dr,ols_sd,ols_dr,raw_dr):
    rel=(ols_sd["sd_qlike"]-q_sd["sd_qlike"])/ols_sd["sd_qlike"]
    return {
        "sd_qlike_delta_qhar_minus_sqrt_ols":q_sd["sd_qlike"]-ols_sd["sd_qlike"],
        "sd_qlike_relative_improvement_vs_sqrt_ols":rel,
        "dr_qlike_delta_qhar_minus_raw_ols":q_dr["dr_qlike"]-raw_dr["dr_qlike"],
        "dr_qlike_delta_qhar_minus_sqrt_ols":q_dr["dr_qlike"]-ols_dr["dr_qlike"],
        "auc_delta_qhar_minus_raw_ols":(
            q_dr["high_risk_roc_auc"]-raw_dr["high_risk_roc_auc"]
            if q_dr["high_risk_roc_auc"] is not None and raw_dr["high_risk_roc_auc"] is not None else None
        ),
    }

def gate24(q_sd,q_dr,ols_sd,raw_dr):
    rel=(ols_sd["sd_qlike"]-q_sd["sd_qlike"])/ols_sd["sd_qlike"]
    return bool(
        q_sd["sd_qlike"] < ols_sd["sd_qlike"]
        and rel >= 0.02
        and q_dr["dr_qlike"] <= raw_dr["dr_qlike"]
        and q_dr["high_risk_roc_auc"] is not None
        and q_dr["high_risk_roc_auc"] >= 0.55
        and q_dr["alert_precision"] is not None
        and q_dr["alert_precision"] > q_dr["high_risk_event_rate"]
        and q_sd["pred_sd_min"] >= EPS
    )

def gate25(q_sd,q_dr,ols_sd,raw_dr,passed24):
    return bool(
        passed24
        and q_sd["sd_qlike"] <= ols_sd["sd_qlike"]
        and q_dr["dr_qlike"] <= raw_dr["dr_qlike"]
        and q_dr["high_risk_roc_auc"] is not None
        and q_dr["high_risk_roc_auc"] >= 0.50
        and q_dr["alert_precision"] is not None
        and q_dr["alert_precision"] > q_dr["high_risk_event_rate"]
        and q_sd["pred_sd_min"] >= EPS
    )

def write_csv(path,rows,qsd,osd,raw):
    if not rows:
        return
    fields=list(rows[0].keys())+[
        "sqrt_qhar_sd_forecast","sqrt_qhar_dr_forecast",
        "sqrt_ols_sd_forecast","sqrt_ols_dr_forecast",
        "raw_ols_har_dr_forecast"
    ]
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r,a,b,c in zip(rows,qsd,osd,raw):
            rr=dict(r)
            rr["sqrt_qhar_sd_forecast"]=float(a)
            rr["sqrt_qhar_dr_forecast"]=float(a*a)
            rr["sqrt_ols_sd_forecast"]=float(b)
            rr["sqrt_ols_dr_forecast"]=float(b*b)
            rr["raw_ols_har_dr_forecast"]=float(c)
            w.writerow(rr)

def evaluate_period(rows,qbeta,sobeta,rawbeta,mean_dr,hi_thr,ext_thr):
    Xsd,_=sd_matrix(rows)
    Xraw,_=raw_matrix(rows)

    qsd=predict(Xsd,qbeta,True,"SQRT_QHAR")
    osd=predict(Xsd,sobeta,True,"SQRT_OLS")
    raw=predict(Xraw,rawbeta,True,"RAW_OLS")

    qdr=qsd*qsd
    odr=osd*osd

    q_sd=sd_metrics(rows,qsd)
    o_sd=sd_metrics(rows,osd)
    q_dr=dr_metrics(rows,qdr,mean_dr,hi_thr,ext_thr)
    o_dr=dr_metrics(rows,odr,mean_dr,hi_thr,ext_thr)
    r_dr=dr_metrics(rows,raw,mean_dr,hi_thr,ext_thr)

    return {
        "SQRT_QHAR_DR":{"sd":q_sd,"dr":q_dr},
        "SQRT_OLS_HAR_DR":{"sd":o_sd,"dr":o_dr},
        "RAW_OLS_HAR_DR":{"dr":r_dr},
        "comparison":compare(q_sd,q_dr,o_sd,o_dr,r_dr),
    },qsd,osd,raw

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
    ds,close,dr=load_days(end)
    rows=build_rows(ds,close,dr)

    if a.stage=="pre2025":
        train=[r for r in rows if date.fromisoformat(r["target_date"])<=FORM_END]
        val=select(rows,VAL_START,VAL_END)

        Xsd,ysd=sd_matrix(train)
        Xraw,yraw=raw_matrix(train)

        sqrt_ols_beta,sqrt_cond=fit_ols(Xsd,ysd)
        raw_ols_beta,raw_cond=fit_ols(Xraw,yraw)
        qfit=fit_qhar_sd(train)

        mean_dr=float(np.mean(yraw))
        hi_thr=nearest_rank(yraw,0.80)
        ret_train=np.array([r["target_close_return"] for r in train],dtype=float)
        ext_thr=nearest_rank(ret_train,0.05)

        block,qsd,osd,raw=evaluate_period(
            val,qfit["beta"],sqrt_ols_beta,raw_ols_beta,
            mean_dr,hi_thr,ext_thr
        )
        passed=gate24(
            block["SQRT_QHAR_DR"]["sd"],
            block["SQRT_QHAR_DR"]["dr"],
            block["SQRT_OLS_HAR_DR"]["sd"],
            block["RAW_OLS_HAR_DR"]["dr"],
        )

        cfg={
            "identity":IDENTITY,
            "parent":PARENT,
            "failed_precursor":FAILED_PRECURSOR,
            "source_table":TABLE,
            "timezone":TZ,
            "formation_n":len(train),
            "formation_mean_dr":mean_dr,
            "high_risk_threshold_q80":hi_thr,
            "extreme_negative_return_threshold_q05":ext_thr,
            "sqrt_ols_beta":[float(x) for x in sqrt_ols_beta],
            "sqrt_ols_condition_number":sqrt_cond,
            "raw_ols_beta":[float(x) for x in raw_ols_beta],
            "raw_ols_condition_number":raw_cond,
            "sqrt_qhar_beta":[float(x) for x in qfit["beta"]],
            "sqrt_qhar_theta_scaled":[float(x) for x in qfit["theta"]],
            "sqrt_qhar_scaler_mu":[float(x) for x in qfit["mu"]],
            "sqrt_qhar_scaler_scale":[float(x) for x in qfit["scale"]],
            "sqrt_qhar_formation_objective":qfit["objective"],
            "sqrt_qhar_iterations":qfit["iterations"],
            "sqrt_qhar_optimizer_message":qfit["message"],
            "sqrt_qhar_min_formation_forecast":qfit["min_fitted"],
            "sqrt_qhar_initial_intercept_shifted_for_domain":qfit["initial_intercept_shifted_for_domain"],
            "sqrt_qhar_reparameterization_max_error":qfit["parity_error"],
            "qlike_domain_epsilon":EPS,
            "panel_sha256_through_2024":panel_hash(ds,close,dr,VAL_END),
            "frozen_before_2025":True,
        }

        res={
            "identity":IDENTITY,
            "status":"PRE2025_FROZEN",
            "2024_validation":block,
            "pre2025_gate_passed":passed,
            "decision":"PRE2025_SOURCE_CONSISTENT_QLIKE_SUPPORTED" if passed else "PRE2025_SOURCE_CONSISTENT_QLIKE_NOT_SUPPORTED",
        }

        (out/"GOLD_CONTROL_DOWNSIDE_SQRT_QHAR_DR_XAU_V1_FROZEN_CONFIG_2026-09-22.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
        (out/"GOLD_CONTROL_DOWNSIDE_SQRT_QHAR_DR_XAU_V1_PRE2025_RESULT_2026-09-22.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
        write_csv(out/"GOLD_CONTROL_DOWNSIDE_SQRT_QHAR_DR_XAU_V1_2024_FORECASTS_2026-09-22.csv",val,qsd,osd,raw)
        print("SQRT_QHARDR_PRE2025_SUCCESS")
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
    block,qsd,osd,raw=evaluate_period(
        rows25,
        np.array(cfg["sqrt_qhar_beta"],dtype=float),
        np.array(cfg["sqrt_ols_beta"],dtype=float),
        np.array(cfg["raw_ols_beta"],dtype=float),
        float(cfg["formation_mean_dr"]),
        float(cfg["high_risk_threshold_q80"]),
        float(cfg["extreme_negative_return_threshold_q05"]),
    )

    trans=gate25(
        block["SQRT_QHAR_DR"]["sd"],
        block["SQRT_QHAR_DR"]["dr"],
        block["SQRT_OLS_HAR_DR"]["sd"],
        block["RAW_OLS_HAR_DR"]["dr"],
        bool(pre["pre2025_gate_passed"]),
    )

    res={
        "identity":IDENTITY,
        "status":"LOCKED_2025_REPLAY_COMPLETE",
        "2025_challenge":block,
        "pre2025_gate_passed":pre["pre2025_gate_passed"],
        "2025_transport_passed":trans,
        "decision":"2025_SOURCE_CONSISTENT_QLIKE_TRANSPORT_SUPPORTED" if trans else "2025_SOURCE_CONSISTENT_QLIKE_TRANSPORT_NOT_SUPPORTED",
    }

    (out/"GOLD_CONTROL_DOWNSIDE_SQRT_QHAR_DR_XAU_V1_2025_RESULT_2026-09-22.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
    write_csv(out/"GOLD_CONTROL_DOWNSIDE_SQRT_QHAR_DR_XAU_V1_2025_FORECASTS_2026-09-22.csv",rows25,qsd,osd,raw)

    v=pre["2024_validation"]
    lines=[
        "# GOLD CONTROL — SOURCE-CONSISTENT SQRT-QLIKE HAR-DR V1 RESULT",
        "",
        f"**Identity:** `{IDENTITY}`  ",
        "**Manifest update:** deferred pending user review.  ",
        "",
        "## Main comparison",
        "",
        "| Period | Model | SD QLIKE | DR QLIKE | DR OOS R2 | High-risk AUC | Precision | Recall | DR calibration slope |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label,blk in [("2024",v),("2025",block)]:
        for name in ("SQRT_QHAR_DR","SQRT_OLS_HAR_DR"):
            sdmet=blk[name]["sd"]; drmet=blk[name]["dr"]
            lines.append(
                f"| {label} | {name} | {sdmet['sd_qlike']:.6f} | {drmet['dr_qlike']:.6f} | "
                f"{drmet['oos_r2_vs_historical_mean']:.4f} | {drmet['high_risk_roc_auc']:.4f} | "
                f"{(drmet['alert_precision'] if drmet['alert_precision'] is not None else float('nan')):.4f} | "
                f"{(drmet['alert_recall'] if drmet['alert_recall'] is not None else float('nan')):.4f} | "
                f"{drmet['calibration_slope']:.4f} |"
            )
        drmet=blk["RAW_OLS_HAR_DR"]["dr"]
        lines.append(
            f"| {label} | RAW_OLS_HAR_DR | NA | {drmet['dr_qlike']:.6f} | "
            f"{drmet['oos_r2_vs_historical_mean']:.4f} | {drmet['high_risk_roc_auc']:.4f} | "
            f"{(drmet['alert_precision'] if drmet['alert_precision'] is not None else float('nan')):.4f} | "
            f"{(drmet['alert_recall'] if drmet['alert_recall'] is not None else float('nan')):.4f} | "
            f"{drmet['calibration_slope']:.4f} |"
        )

    lines += [
        "",
        "## Frozen decisions",
        "",
        f"- 2024 source-consistent QLIKE gate: **{'PASS' if pre['pre2025_gate_passed'] else 'FAIL'}**.",
        f"- 2025 transport gate: **{'PASS' if trans else 'FAIL'}**.",
        "- No adaptive calibration state or post-result rescue was used.",
        "- No manifest change was made.",
    ]
    (out/"GOLD_CONTROL_DOWNSIDE_SQRT_QHAR_DR_XAU_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("SQRT_QHARDR_2025_SUCCESS")

if __name__=="__main__":
    main()
