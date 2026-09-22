from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from scipy.stats import binomtest, rankdata, norm

IDENTITY="DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
YEARS=(2022,2023,2024,2025,2026)
PRE_YEARS=(2022,2023,2024)
EPS=1e-14

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

def load_days():
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
      where extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
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
            cur.execute(sql)
            raw=cur.fetchall()

    ds=[]; close=[]; dr=[]
    for d,n,c,x in raw:
        c=float(c); x=float(x)
        if not (math.isfinite(c) and c>0 and math.isfinite(x) and x>=0):
            raise RuntimeError(f"BAD_ROW:{d}")
        ds.append(d); close.append(c); dr.append(x)
    if len(ds)<800:
        raise RuntimeError(f"INSUFFICIENT_DAYS:{len(ds)}")
    return ds,np.array(close,dtype=float),np.array(dr,dtype=float)

def panel_hash(ds,close,dr):
    s="\n".join(f"{d.isoformat()}|{c:.12f}|{x:.16g}" for d,c,x in zip(ds,close,dr))
    return hashlib.sha256(s.encode()).hexdigest()

def build_rows(ds,close,dr):
    sd=np.sqrt(dr)
    daily_ret=np.full(len(ds),np.nan)
    daily_ret[1:]=np.log(close[1:]/close[:-1])
    rows=[]
    for i in range(21,len(ds)-1):
        t=i+1
        rows.append({
            "origin_date":ds[i].isoformat(),
            "target_date":ds[t].isoformat(),
            "dr_d":float(dr[i]),
            "dr_w":float(np.mean(dr[i-4:i+1])),
            "dr_m":float(np.mean(dr[i-21:i+1])),
            "sd_d":float(sd[i]),
            "sd_w":float(np.mean(sd[i-4:i+1])),
            "sd_m":float(np.mean(sd[i-21:i+1])),
            "target_dr":float(dr[t]),
            "target_sd":float(sd[t]),
            "target_close_return":float(daily_ret[t]),
        })
    return rows

def raw_matrix(rows):
    X=np.array([[1.0,r["dr_d"],r["dr_w"],r["dr_m"]] for r in rows],dtype=float)
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    return X,y

def sqrt_matrix(rows):
    X=np.array([[1.0,r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],dtype=float)
    y=np.array([r["target_sd"] for r in rows],dtype=float)
    return X,y

def fit_ols(X,y):
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return beta,float(np.linalg.cond(X))

def roc_auc(y,s):
    y=np.asarray(y,dtype=int); s=np.asarray(s,dtype=float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if n1==0 or n0==0:
        return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qloss(y,f):
    yy=max(float(y),EPS); ff=max(float(f),EPS)
    z=yy/ff
    return z-math.log(z)-1.0

def calibration(y,p):
    Z=np.column_stack([np.ones(len(p)),p])
    b=np.linalg.lstsq(Z,y,rcond=None)[0]
    return float(b[0]),float(b[1])

def metrics(rows,pred,mean_dr,hi_thr,ext_thr,sd_pred=None):
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    persistence=np.array([r["dr_d"] for r in rows],dtype=float)
    meanpred=np.full(len(rows),mean_dr,dtype=float)

    mse=float(np.mean((pred-y)**2))
    mean_mse=float(np.mean((meanpred-y)**2))
    per_mse=float(np.mean((persistence-y)**2))
    mae=float(np.mean(np.abs(pred-y)))
    qlike=float(np.mean([qloss(a,b) for a,b in zip(y,pred)]))
    pqlike=float(np.mean([qloss(a,b) for a,b in zip(y,persistence)]))
    mqlike=float(np.mean([qloss(a,b) for a,b in zip(y,meanpred)]))
    corr=float(np.corrcoef(pred,y)[0,1]) if np.std(pred)>0 and np.std(y)>0 else None
    ci,cs=calibration(y,pred)

    high=(y>=hi_thr).astype(int)
    alert=pred>=hi_thr
    tp=int(np.sum(alert & (high==1))); fp=int(np.sum(alert & (high==0)))
    fn=int(np.sum((~alert)&(high==1))); tn=int(np.sum((~alert)&(high==0)))
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else 0.0

    ret=np.array([r["target_close_return"] for r in rows],dtype=float)
    down=ret<0
    extreme=ret<=ext_thr

    out={
        "n":len(rows),
        "mse":mse,
        "historical_mean_mse":mean_mse,
        "persistence_mse":per_mse,
        "oos_r2_vs_historical_mean":float(1-mse/mean_mse) if mean_mse>0 else None,
        "mae":mae,
        "dr_qlike":qlike,
        "historical_mean_dr_qlike":mqlike,
        "persistence_dr_qlike":pqlike,
        "correlation":corr,
        "forecast_mean":float(np.mean(pred)),
        "realized_mean":float(np.mean(y)),
        "mean_ratio_realized_to_forecast":float(np.mean(y)/np.mean(pred)),
        "calibration_intercept":ci,
        "calibration_slope":cs,
        "calibration_slope_abs_error":abs(cs-1.0),
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
    if sd_pred is not None:
        out["sd_pred_min"]=float(np.min(sd_pred))
        out["sd_nonpositive_count"]=int(np.sum(sd_pred<=0))
    return out

def nw_mean_t(diff,lag):
    x=np.asarray(diff,dtype=float)
    n=len(x); mu=float(np.mean(x))
    d=x-mu
    gamma0=float(np.dot(d,d)/n)
    lrv=gamma0
    L=min(lag,n-1)
    for k in range(1,L+1):
        g=float(np.dot(d[k:],d[:-k])/n)
        lrv += 2.0*(1.0-k/(L+1.0))*g
    se=math.sqrt(max(lrv,0.0)/n)
    t=mu/se if se>0 else None
    p=2*(1-norm.cdf(abs(t))) if t is not None else None
    return {"mean":mu,"se":se,"t":t,"normal_approx_p_two_sided":p,"lag":lag}

def yearly_fit_eval(rows,year):
    cutoff=date(year-1,12,31)
    train=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
    test=[r for r in rows if date.fromisoformat(r["target_date"]).year==year]
    if len(train)<250:
        raise RuntimeError(f"FORMATION_TOO_SHORT:{year}:{len(train)}")
    if len(test)==0:
        raise RuntimeError(f"NO_TEST_ROWS:{year}")

    Xr,yr=raw_matrix(train)
    Xs,ys=sqrt_matrix(train)
    rb,rcond=fit_ols(Xr,yr)
    sb,scond=fit_ols(Xs,ys)

    Xrt,_=raw_matrix(test)
    Xst,_=sqrt_matrix(test)
    raw_pred=Xrt@rb
    sd_pred=Xst@sb
    if np.any(~np.isfinite(raw_pred)) or np.any(raw_pred<=0):
        raise RuntimeError(f"RAW_NONPOSITIVE_OOS:{year}")
    nonpos=int(np.sum(sd_pred<=0))
    if nonpos>0:
        raise RuntimeError(f"SQRT_NONPOSITIVE_SD_OOS:{year}:{nonpos}")
    sqrt_pred=sd_pred*sd_pred

    mean_dr=float(np.mean(yr))
    hi_thr=nearest_rank(yr,0.80)
    train_rets=np.array([r["target_close_return"] for r in train],dtype=float)
    ext_thr=nearest_rank(train_rets,0.05)

    rawm=metrics(test,raw_pred,mean_dr,hi_thr,ext_thr)
    sqrtm=metrics(test,sqrt_pred,mean_dr,hi_thr,ext_thr,sd_pred=sd_pred)

    augmented=[]
    for r,rp,sp,sdp in zip(test,raw_pred,sqrt_pred,sd_pred):
        rr=dict(r)
        rr.update({
            "evaluation_year":year,
            "formation_n":len(train),
            "formation_mean_dr":mean_dr,
            "high_risk_threshold":hi_thr,
            "extreme_return_threshold":ext_thr,
            "raw_har_dr_forecast":float(rp),
            "sqrt_har_sd_forecast":float(sdp),
            "sqrt_har_dr_forecast":float(sp),
            "actual_high_risk":int(r["target_dr"]>=hi_thr),
            "raw_high_risk_alert":int(rp>=hi_thr),
            "sqrt_high_risk_alert":int(sp>=hi_thr),
            "raw_normalized_risk_score":float(rp/hi_thr),
            "sqrt_normalized_risk_score":float(sp/hi_thr),
        })
        augmented.append(rr)

    return {
        "year":year,
        "formation_n":len(train),
        "test_n":len(test),
        "formation_cutoff":cutoff.isoformat(),
        "raw_beta":[float(x) for x in rb],
        "sqrt_beta":[float(x) for x in sb],
        "raw_condition_number":rcond,
        "sqrt_condition_number":scond,
        "RAW_HAR_DR":rawm,
        "SQRT_HAR_DR":sqrtm,
        "comparison":{
            "mse_delta_sqrt_minus_raw":sqrtm["mse"]-rawm["mse"],
            "mse_relative_change_vs_raw":(sqrtm["mse"]-rawm["mse"])/rawm["mse"],
            "qlike_delta_sqrt_minus_raw":sqrtm["dr_qlike"]-rawm["dr_qlike"],
            "calibration_abs_error_delta_sqrt_minus_raw":sqrtm["calibration_slope_abs_error"]-rawm["calibration_slope_abs_error"],
            "auc_delta_sqrt_minus_raw":sqrtm["high_risk_roc_auc"]-rawm["high_risk_roc_auc"],
        }
    },augmented

def pooled_pre(rows):
    y=np.array([r["target_dr"] for r in rows],dtype=float)
    raw=np.array([r["raw_har_dr_forecast"] for r in rows],dtype=float)
    sqrt=np.array([r["sqrt_har_dr_forecast"] for r in rows],dtype=float)
    hi=np.array([r["high_risk_threshold"] for r in rows],dtype=float)
    actual_hi=np.array([r["actual_high_risk"] for r in rows],dtype=int)
    raw_alert=np.array([r["raw_high_risk_alert"] for r in rows],dtype=int)
    sqrt_alert=np.array([r["sqrt_high_risk_alert"] for r in rows],dtype=int)

    mse_raw=float(np.mean((raw-y)**2))
    mse_sqrt=float(np.mean((sqrt-y)**2))
    qraw=np.array([qloss(a,b) for a,b in zip(y,raw)])
    qsqrt=np.array([qloss(a,b) for a,b in zip(y,sqrt)])

    raw_score=np.array([r["raw_normalized_risk_score"] for r in rows],dtype=float)
    sqrt_score=np.array([r["sqrt_normalized_risk_score"] for r in rows],dtype=float)

    raw_correct=(raw_alert==actual_hi)
    sqrt_correct=(sqrt_alert==actual_hi)
    sqrt_only=int(np.sum(sqrt_correct & (~raw_correct)))
    raw_only=int(np.sum(raw_correct & (~sqrt_correct)))
    discord=sqrt_only+raw_only
    pbin=float(binomtest(min(sqrt_only,raw_only),discord,0.5,alternative="two-sided").pvalue) if discord else 1.0

    mse_diff=(raw-y)**2-(sqrt-y)**2
    qdiff=qraw-qsqrt

    return {
        "n":len(rows),
        "raw_mse":mse_raw,
        "sqrt_mse":mse_sqrt,
        "sqrt_minus_raw_mse":mse_sqrt-mse_raw,
        "raw_qlike":float(np.mean(qraw)),
        "sqrt_qlike":float(np.mean(qsqrt)),
        "sqrt_minus_raw_qlike":float(np.mean(qsqrt)-np.mean(qraw)),
        "raw_high_risk_auc_normalized":roc_auc(actual_hi,raw_score),
        "sqrt_high_risk_auc_normalized":roc_auc(actual_hi,sqrt_score),
        "paired_mse_loss_raw_minus_sqrt":{
            "nw5":nw_mean_t(mse_diff,5),
            "nw10":nw_mean_t(mse_diff,10),
        },
        "paired_qlike_loss_raw_minus_sqrt":{
            "nw5":nw_mean_t(qdiff,5),
            "nw10":nw_mean_t(qdiff,10),
        },
        "high_risk_correctness":{
            "both_correct":int(np.sum(raw_correct & sqrt_correct)),
            "sqrt_only_correct":sqrt_only,
            "raw_only_correct":raw_only,
            "neither_correct":int(np.sum((~raw_correct)&(~sqrt_correct))),
            "discordant_exact_two_sided_p":pbin,
        },
    }

def pre_gate(years,pooled):
    mse_wins=sum(1 for y in PRE_YEARS if years[str(y)]["SQRT_HAR_DR"]["mse"] < years[str(y)]["RAW_HAR_DR"]["mse"])
    cal_wins=sum(1 for y in PRE_YEARS if years[str(y)]["SQRT_HAR_DR"]["calibration_slope_abs_error"] < years[str(y)]["RAW_HAR_DR"]["calibration_slope_abs_error"])
    auc_ok=all(years[str(y)]["SQRT_HAR_DR"]["high_risk_roc_auc"] >= years[str(y)]["RAW_HAR_DR"]["high_risk_roc_auc"]-0.02 for y in PRE_YEARS)
    positive=all(years[str(y)]["SQRT_HAR_DR"].get("sd_nonpositive_count",0)==0 for y in PRE_YEARS)
    pooled_auc_ok=pooled["sqrt_high_risk_auc_normalized"] >= pooled["raw_high_risk_auc_normalized"]-0.01
    passed=bool(
        mse_wins>=2
        and pooled["sqrt_mse"]<pooled["raw_mse"]
        and cal_wins>=2
        and auc_ok
        and pooled_auc_ok
        and positive
    )
    return {
        "passed":passed,
        "mse_wins_2022_2024":mse_wins,
        "calibration_wins_2022_2024":cal_wins,
        "auc_no_worse_than_minus_002_all_years":auc_ok,
        "pooled_auc_within_minus_001":pooled_auc_ok,
        "all_sqrt_sd_forecasts_positive":positive,
        "decision":"PRE2025_SEMIDEVIATION_REPRESENTATION_SUPPORTED" if passed else "PRE2025_SEMIDEVIATION_REPRESENTATION_NOT_SUPPORTED",
    }

def stress_label(block,prepassed):
    if not prepassed:
        return "NOT_ASSESSED_PRIMARY_GATE_FAILED"
    r=block["RAW_HAR_DR"]; s=block["SQRT_HAR_DR"]
    ok=bool(
        s["mse"]<=r["mse"]
        and s["calibration_slope_abs_error"]<r["calibration_slope_abs_error"]
        and s["high_risk_roc_auc"]>=r["high_risk_roc_auc"]-0.02
        and s.get("sd_nonpositive_count",0)==0
    )
    return "REPRESENTATION_STRESS_SUPPORT" if ok else "REPRESENTATION_STRESS_NOT_SUPPORTED"

def write_csv(path,rows):
    if not rows:
        return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

def main():
    out=Path("multiorigin_out")
    out.mkdir(parents=True,exist_ok=True)

    ds,close,dr=load_days()
    rows=build_rows(ds,close,dr)

    years={}
    all_aug=[]
    for y in YEARS:
        block,aug=yearly_fit_eval(rows,y)
        years[str(y)]=block
        all_aug.extend(aug)
        print(json.dumps({
            "year":y,
            "formation_n":block["formation_n"],
            "test_n":block["test_n"],
            "raw_mse":block["RAW_HAR_DR"]["mse"],
            "sqrt_mse":block["SQRT_HAR_DR"]["mse"],
            "raw_auc":block["RAW_HAR_DR"]["high_risk_roc_auc"],
            "sqrt_auc":block["SQRT_HAR_DR"]["high_risk_roc_auc"],
        },sort_keys=True))

    pre_rows=[r for r in all_aug if int(r["evaluation_year"]) in PRE_YEARS]
    pooled=pooled_pre(pre_rows)
    gate=pre_gate(years,pooled)

    stress={
        "2025":stress_label(years["2025"],gate["passed"]),
        "2026YTD":stress_label(years["2026"],gate["passed"]),
        "2026_last_target_date":max(r["target_date"] for r in all_aug if int(r["evaluation_year"])==2026),
    }

    result={
        "identity":IDENTITY,
        "source_table":TABLE,
        "timezone":TZ,
        "panel_first_day":ds[0].isoformat(),
        "panel_last_day":ds[-1].isoformat(),
        "panel_sha256":panel_hash(ds,close,dr),
        "production_database_write":"NONE",
        "years":years,
        "pooled_2022_2024":pooled,
        "pre2025_gate":gate,
        "stress_periods":stress,
        "evidence_note":"2025 generated the hypothesis and is not pristine confirmatory evidence; 2026YTD is retrospective stress evidence.",
    }

    (out/"GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    write_csv(out/"GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv",all_aug)

    lines=[
        "# GOLD CONTROL — RAW vs SQRT HAR-DR MULTI-ORIGIN V1 RESULT","",
        f"**Identity:** `{IDENTITY}`  ",
        "**Manifest update:** deferred pending user review.  ","",
        "## Annual expanding-origin results","",
        "| Year | n | Raw MSE | Sqrt MSE | Raw R2 | Sqrt R2 | Raw cal slope | Sqrt cal slope | Raw AUC | Sqrt AUC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for y in YEARS:
        b=years[str(y)]; r=b["RAW_HAR_DR"]; s=b["SQRT_HAR_DR"]
        lines.append(
            f"| {y} | {b['test_n']} | {r['mse']:.6g} | {s['mse']:.6g} | "
            f"{r['oos_r2_vs_historical_mean']:.4f} | {s['oos_r2_vs_historical_mean']:.4f} | "
            f"{r['calibration_slope']:.4f} | {s['calibration_slope']:.4f} | "
            f"{r['high_risk_roc_auc']:.4f} | {s['high_risk_roc_auc']:.4f} |"
        )
    lines += [
        "",
        "## Frozen decisions","",
        f"- Primary 2022-2024 representation gate: **{'PASS' if gate['passed'] else 'FAIL'}**.",
        f"- 2025 stress: **{stress['2025']}**.",
        f"- 2026 YTD stress: **{stress['2026YTD']}**.",
        "- 2025 and 2026 are not described as pristine blind confirmation.",
        "- No manifest change was made.",
    ]
    (out/"GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("MULTIORIGIN_SUCCESS")

if __name__=="__main__":
    main()
