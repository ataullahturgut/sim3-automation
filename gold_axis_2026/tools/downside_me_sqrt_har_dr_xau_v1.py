from __future__ import annotations

import csv, hashlib, json, math, os
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from scipy.stats import rankdata, norm

IDENTITY="DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_RESEARCH"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
YEARS=(2022,2023,2024,2025,2026)
PRE_YEARS=(2022,2023,2024)
EPS=1e-14

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,float)
    k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_days():
    sql=f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date d,
        observation_ts,
        close::double precision close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) prev_close
      from {TABLE}
      where extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    r as (
      select d, observation_ts, close,
             case when prev_close>0 then ln(close/prev_close) end ret
      from b
    ),
    a as (
      select d,
             count(*)::int bars,
             count(ret)::int m,
             (array_agg(close order by observation_ts desc))[1]::double precision close,
             sum(case when ret<0 then ret*ret else 0 end)::double precision dr,
             sum(case when ret<0 then power(ret,4) else 0 end)::double precision neg_r4
      from r group by d
    )
    select d,bars,m,close,dr,neg_r4
    from a
    where bars >= {MIN_BARS}
    order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql)
            raw=cur.fetchall()
    ds=[]; close=[]; dr=[]; rqminus=[]; mret=[]
    for d,bars,m,c,x,r4 in raw:
        c=float(c); x=float(x); r4=float(r4); m=int(m)
        if not(math.isfinite(c) and c>0 and math.isfinite(x) and x>0 and math.isfinite(r4) and r4>=0 and m>0):
            raise RuntimeError(f"BAD_DAY:{d}")
        rq=(2.0*m/3.0)*r4
        if rq<=0 or not math.isfinite(rq): raise RuntimeError(f"BAD_RQMINUS:{d}")
        ds.append(d); close.append(c); dr.append(x); rqminus.append(rq); mret.append(m)
    return ds,np.array(close),np.array(dr),np.array(rqminus),np.array(mret)

def panel_hash(ds,close,dr,rq,m):
    s="\n".join(f"{d.isoformat()}|{c:.12f}|{x:.16g}|{q:.16g}|{int(mm)}"
                  for d,c,x,q,mm in zip(ds,close,dr,rq,m))
    return hashlib.sha256(s.encode()).hexdigest()

def build_rows(ds,close,dr,rq,m):
    sd=np.sqrt(dr)
    qt=np.power(dr,0.25)
    me=np.sqrt(5.0*rq/(16.0*m*dr))
    dret=np.full(len(ds),np.nan); dret[1:]=np.log(close[1:]/close[:-1])
    rows=[]
    for i in range(21,len(ds)-1):
        t=i+1
        rows.append({
          "origin_date":ds[i].isoformat(),"target_date":ds[t].isoformat(),
          "dr_d":float(dr[i]),"dr_w":float(np.mean(dr[i-4:i+1])),"dr_m":float(np.mean(dr[i-21:i+1])),
          "sd_d":float(sd[i]),"sd_w":float(np.mean(sd[i-4:i+1])),"sd_m":float(np.mean(sd[i-21:i+1])),
          "qt_d":float(qt[i]),"qt_w":float(np.mean(qt[i-4:i+1])),"qt_m":float(np.mean(qt[i-21:i+1])),
          "rqminus":float(rq[i]),"m_intraday_returns":int(m[i]),"me_sd":float(me[i]),
          "me_interaction":float(me[i]*sd[i]),
          "target_dr":float(dr[t]),"target_sd":float(sd[t]),"target_qt":float(qt[t]),
          "target_close_return":float(dret[t])
        })
    return rows

def mat(rows,kind):
    if kind=="raw":
        X=np.array([[1,r["dr_d"],r["dr_w"],r["dr_m"]] for r in rows],float); y=np.array([r["target_dr"] for r in rows])
    elif kind=="sqrt":
        X=np.array([[1,r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],float); y=np.array([r["target_sd"] for r in rows])
    elif kind=="quartic":
        X=np.array([[1,r["qt_d"],r["qt_w"],r["qt_m"]] for r in rows],float); y=np.array([r["target_qt"] for r in rows])
    elif kind=="me":
        X=np.array([[1,r["sd_d"],r["sd_w"],r["sd_m"],r["me_interaction"]] for r in rows],float); y=np.array([r["target_sd"] for r in rows])
    else: raise ValueError(kind)
    return X,y

def fit(rows,kind):
    X,y=mat(rows,kind)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    return b,float(np.linalg.cond(X))

def auc(y,s):
    y=np.asarray(y,int);s=np.asarray(s,float)
    n1=int(np.sum(y==1));n0=int(np.sum(y==0))
    if n1==0 or n0==0:return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qloss(y,f):
    y=max(float(y),EPS); f=max(float(f),EPS); z=y/f
    return z-math.log(z)-1

def calibration(y,p):
    Z=np.column_stack([np.ones(len(p)),p])
    b=np.linalg.lstsq(Z,y,rcond=None)[0]
    return float(b[0]),float(b[1])

def metrics(rows,p,mean_dr,hi,ext):
    y=np.array([r["target_dr"] for r in rows],float)
    pers=np.array([r["dr_d"] for r in rows],float)
    meanp=np.full(len(y),mean_dr)
    mse=float(np.mean((p-y)**2)); mm=float(np.mean((meanp-y)**2))
    high=(y>=hi).astype(int); alert=p>=hi
    tp=int(np.sum(alert&(high==1)));fp=int(np.sum(alert&(high==0)))
    fn=int(np.sum((~alert)&(high==1)));tn=int(np.sum((~alert)&(high==0)))
    prec=tp/(tp+fp) if tp+fp else None; rec=tp/(tp+fn) if tp+fn else None
    f1=2*prec*rec/(prec+rec) if prec is not None and rec is not None and prec+rec else 0.0
    ret=np.array([r["target_close_return"] for r in rows]); down=ret<0; extreme=ret<=ext
    ci,cs=calibration(y,p)
    return {
      "n":len(y),"mse":mse,"mae":float(np.mean(np.abs(p-y))),
      "historical_mean_mse":mm,"persistence_mse":float(np.mean((pers-y)**2)),
      "oos_r2_vs_historical_mean":float(1-mse/mm),
      "dr_qlike":float(np.mean([qloss(a,b) for a,b in zip(y,p)])),
      "historical_mean_dr_qlike":float(np.mean([qloss(a,b) for a,b in zip(y,meanp)])),
      "persistence_dr_qlike":float(np.mean([qloss(a,b) for a,b in zip(y,pers)])),
      "correlation":float(np.corrcoef(p,y)[0,1]),
      "forecast_mean":float(np.mean(p)),"realized_mean":float(np.mean(y)),
      "calibration_intercept":ci,"calibration_slope":cs,"calibration_slope_abs_error":abs(cs-1),
      "pred_min":float(np.min(p)),"pred_median":float(np.median(p)),"pred_max":float(np.max(p)),
      "high_risk_event_rate":float(np.mean(high)),"high_risk_roc_auc":auc(high,p),
      "alert_coverage":float(np.mean(alert)),"alert_precision":prec,"alert_recall":rec,"alert_f1":f1,
      "tp":tp,"fp":fp,"fn":fn,"tn":tn,
      "unconditional_down_day_rate":float(np.mean(down)),
      "down_day_rate_given_alert":float(np.mean(down[alert])) if np.sum(alert) else None,
      "unconditional_extreme_negative_return_rate":float(np.mean(extreme)),
      "extreme_negative_return_rate_given_alert":float(np.mean(extreme[alert])) if np.sum(alert) else None
    }

def predict(rows,b,kind):
    X,_=mat(rows,kind); z=X@b
    if np.any(~np.isfinite(z)): raise RuntimeError(f"NONFINITE:{kind}")
    nonpos=int(np.sum(z<=0))
    if kind=="raw":
        if nonpos: raise RuntimeError(f"NONPOSITIVE_RAW:{nonpos}")
        return z,nonpos
    if nonpos: return np.full(len(z),np.nan),nonpos
    if kind in ("sqrt","me"): return z*z,0
    if kind=="quartic": return z**4,0
    raise ValueError(kind)

def nw(diff,L):
    x=np.asarray(diff,float); n=len(x); mu=float(np.mean(x)); d=x-mu
    lrv=float(np.dot(d,d)/n)
    for k in range(1,min(L,n-1)+1):
        g=float(np.dot(d[k:],d[:-k])/n)
        lrv+=2*(1-k/(L+1))*g
    se=math.sqrt(max(lrv,0)/n); t=mu/se if se>0 else None
    return {"mean":mu,"se":se,"t":t,"p_two_sided":2*(1-norm.cdf(abs(t))) if t is not None else None}

def eval_year(rows,year):
    train=[r for r in rows if date.fromisoformat(r["target_date"])<=date(year-1,12,31)]
    test=[r for r in rows if date.fromisoformat(r["target_date"]).year==year]
    if len(train)<250 or not test: raise RuntimeError(f"BAD_SUPPORT:{year}:{len(train)}:{len(test)}")
    betas={};conds={};preds={};domain={}
    for k in ("raw","sqrt","quartic","me"):
        betas[k],conds[k]=fit(train,k)
        preds[k],domain[k]=predict(test,betas[k],k)
    if any(domain[k]>0 for k in ("sqrt","quartic","me")):
        raise RuntimeError(f"TRANSFORM_DOMAIN_FAILURE:{year}:{domain}")
    ytr=np.array([r["target_dr"] for r in train])
    mean_dr=float(np.mean(ytr)); hi=nearest_rank(ytr,.8)
    ext=nearest_rank(np.array([r["target_close_return"] for r in train]),.05)
    mets={k:metrics(test,preds[k],mean_dr,hi,ext) for k in preds}
    aug=[]
    for j,r in enumerate(test):
        rr=dict(r);rr.update({"evaluation_year":year,"high_risk_threshold":hi,"extreme_return_threshold":ext})
        for k in preds: rr[f"{k}_forecast_dr"]=float(preds[k][j])
        aug.append(rr)
    return {
      "formation_n":len(train),"test_n":len(test),"formation_cutoff":f"{year-1}-12-31",
      "betas":{k:[float(x) for x in betas[k]] for k in betas},
      "condition_numbers":conds,
      "bME":float(betas["me"][4]),
      "domain_nonpositive_counts":domain,
      "RAW_HAR_DR":mets["raw"],"SQRT_HAR_DR":mets["sqrt"],
      "QUARTIC_HAR_DR_NAIVE":mets["quartic"],"ME_SQRT_HAR_DR":mets["me"]
    },aug

def pooled(rows,model_a,model_b):
    y=np.array([r["target_dr"] for r in rows])
    a=np.array([r[f"{model_a}_forecast_dr"] for r in rows]); b=np.array([r[f"{model_b}_forecast_dr"] for r in rows])
    d_mse=(a-y)**2-(b-y)**2
    d_q=np.array([qloss(yy,aa)-qloss(yy,bb) for yy,aa,bb in zip(y,a,b)])
    return {
      "n":len(y),"a_mse":float(np.mean((a-y)**2)),"b_mse":float(np.mean((b-y)**2)),
      "a_qlike":float(np.mean([qloss(yy,aa) for yy,aa in zip(y,a)])),
      "b_qlike":float(np.mean([qloss(yy,bb) for yy,bb in zip(y,b)])),
      "raw_minus_candidate_mse_nw5":nw(d_mse,5),"raw_minus_candidate_mse_nw10":nw(d_mse,10),
      "raw_minus_candidate_qlike_nw5":nw(d_q,5),"raw_minus_candidate_qlike_nw10":nw(d_q,10)
    }

def main():
    out=Path("me_sqrt_out");out.mkdir(exist_ok=True)
    ds,close,dr,rq,m=load_days(); rows=build_rows(ds,close,dr,rq,m)
    years={}; all_aug=[]
    for y in YEARS:
        b,a=eval_year(rows,y); years[str(y)]=b; all_aug+=a
        print(json.dumps({"year":y,"bME":b["bME"],
          "sqrt_mse":b["SQRT_HAR_DR"]["mse"],"quartic_mse":b["QUARTIC_HAR_DR_NAIVE"]["mse"],
          "me_mse":b["ME_SQRT_HAR_DR"]["mse"],"me_auc":b["ME_SQRT_HAR_DR"]["high_risk_roc_auc"]},sort_keys=True))
    pre=[r for r in all_aug if int(r["evaluation_year"]) in PRE_YEARS]
    p_me=pooled(pre,"sqrt","me"); p_qt=pooled(pre,"sqrt","quartic")
    mse_wins=sum(years[str(y)]["ME_SQRT_HAR_DR"]["mse"]<years[str(y)]["SQRT_HAR_DR"]["mse"] for y in PRE_YEARS)
    cal_wins=sum(years[str(y)]["ME_SQRT_HAR_DR"]["calibration_slope_abs_error"]<years[str(y)]["SQRT_HAR_DR"]["calibration_slope_abs_error"] for y in PRE_YEARS)
    auc_ok=all(years[str(y)]["ME_SQRT_HAR_DR"]["high_risk_roc_auc"]>=years[str(y)]["SQRT_HAR_DR"]["high_risk_roc_auc"]-.02 for y in PRE_YEARS)
    neg_b=sum(years[str(y)]["bME"]<0 for y in PRE_YEARS)
    gate=bool(mse_wins>=2 and p_me["b_mse"]<p_me["a_mse"] and p_me["b_qlike"]<=p_me["a_qlike"]
              and cal_wins>=2 and auc_ok and neg_b>=2)
    result={
      "identity":IDENTITY,"panel_first_day":ds[0].isoformat(),"panel_last_day":ds[-1].isoformat(),
      "panel_sha256":panel_hash(ds,close,dr,rq,m),"manifest_modified":False,"production_write":"NONE",
      "evidence_classification":"RETROSPECTIVE_DEVELOPMENT_AND_STRESS_ONLY_NOT_PRISTINE_CONFIRMATION",
      "years":years,"pooled_2022_2024_sqrt_vs_me":p_me,"pooled_2022_2024_sqrt_vs_quartic":p_qt,
      "feasibility_gate":{
        "mse_wins_vs_sqrt":int(mse_wins),"calibration_wins_vs_sqrt":int(cal_wins),
        "auc_tolerance_all":auc_ok,"negative_bME_years":int(neg_b),
        "passed":gate,
        "decision":"RETROSPECTIVE_MECHANISM_SUPPORTED" if gate else "RETROSPECTIVE_MECHANISM_NOT_SUPPORTED"
      }
    }
    (out/"GOLD_CONTROL_DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))
    with open(out/"GOLD_CONTROL_DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_FORECASTS_2026-09-22.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(all_aug[0].keys()));w.writeheader();w.writerows(all_aug)
    lines=["# GOLD CONTROL — ME-SQRT-HAR-DR V1 RESULT","",
      f"**Decision:** {result['feasibility_gate']['decision']}  ",
      "**Manifest modified:** NO  ","",
      "| Year | SQRT MSE | QUARTIC MSE | ME-SQRT MSE | SQRT R2 | ME R2 | SQRT AUC | ME AUC | bME |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in YEARS:
        b=years[str(y)];s=b["SQRT_HAR_DR"];q=b["QUARTIC_HAR_DR_NAIVE"];me=b["ME_SQRT_HAR_DR"]
        lines.append(f"| {y} | {s['mse']:.6g} | {q['mse']:.6g} | {me['mse']:.6g} | {s['oos_r2_vs_historical_mean']:.4f} | {me['oos_r2_vs_historical_mean']:.4f} | {s['high_risk_roc_auc']:.4f} | {me['high_risk_roc_auc']:.4f} | {b['bME']:.6g} |")
    (out/"GOLD_CONTROL_DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("ME_SQRT_SUCCESS")

if __name__=="__main__": main()
