from __future__ import annotations

import csv, hashlib, json, math, os
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from scipy.optimize import minimize
from scipy.stats import rankdata, norm

IDENTITY="DOWNSIDE_HARK_SD_XAU_V1_RESEARCH"
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
      select d,observation_ts,close,
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
    ds=[]; close=[]; dr=[]; h=[]
    for d,bars,m,c,x,r4 in raw:
        c=float(c); x=float(x); r4=float(r4); m=int(m)
        if not(math.isfinite(c) and c>0 and math.isfinite(x) and x>0 and math.isfinite(r4) and r4>0 and m>0):
            raise RuntimeError(f"BAD_DAY:{d}")
        rq=(2.0*m/3.0)*r4
        ht=5.0*rq/(16.0*m*x)
        if not(math.isfinite(ht) and ht>0):
            raise RuntimeError(f"BAD_H:{d}")
        ds.append(d);close.append(c);dr.append(x);h.append(ht)
    return ds,np.asarray(close,float),np.asarray(dr,float),np.asarray(h,float)

def panel_hash(ds,close,dr,h):
    s="\n".join(f"{d.isoformat()}|{c:.12f}|{x:.16g}|{hh:.16g}"
                  for d,c,x,hh in zip(ds,close,dr,h))
    return hashlib.sha256(s.encode()).hexdigest()

def daily_return(close):
    out=np.full(len(close),np.nan)
    out[1:]=np.log(close[1:]/close[:-1])
    return out

def sqrt_ols_fit(sd,last_idx):
    rows=[];targets=[]
    for t in range(22,last_idx+1):
        rows.append([1.0,sd[t-1],float(np.mean(sd[t-5:t])),float(np.mean(sd[t-22:t]))])
        targets.append(sd[t])
    X=np.asarray(rows,float);y=np.asarray(targets,float)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    resid=y-X@b
    return b,float(np.var(resid,ddof=1)),len(y)

def sqrt_ols_predict(sd,b,idxs):
    p=[]
    for t in idxs:
        x=np.array([1.0,sd[t-1],np.mean(sd[t-5:t]),np.mean(sd[t-22:t])])
        z=float(x@b)
        p.append(z*z if z>0 else np.nan)
    return np.asarray(p,float)

def transition(beta):
    b0,bd,bw,bm=beta
    T=np.zeros((22,22),float)
    T[0,0]=bd+bw/5.0+bm/22.0
    T[0,1:5]=bw/5.0+bm/22.0
    T[0,5:22]=bm/22.0
    T[1:,0:-1]=np.eye(21)
    c=np.zeros(22,float);c[0]=b0
    return c,T

def initial_state(y,h_used):
    m=np.asarray(y[:22][::-1],float).copy()
    P=np.diag(np.asarray(h_used[:22][::-1],float))
    return m,P

def kalman_negloglike(theta,y,h_used):
    b=np.asarray(theta[:4],float);q=math.exp(float(theta[4]))
    c,T=transition(b)
    Q=np.zeros((22,22),float);Q[0,0]=q
    m,P=initial_state(y,h_used)
    nll=0.0
    for t in range(22,len(y)):
        mp=c+T@m
        Pp=T@P@T.T+Q
        F=float(Pp[0,0]+h_used[t])
        if not(math.isfinite(F) and F>1e-14):
            return 1e100
        v=float(y[t]-mp[0])
        nll+=0.5*(math.log(2*math.pi)+math.log(F)+(v*v/F))
        K=Pp[:,0]/F
        m=mp+K*v
        P=Pp-np.outer(K,Pp[0,:])
        P=(P+P.T)*0.5
        if not(np.all(np.isfinite(m)) and np.all(np.isfinite(P))):
            return 1e100
    return float(nll)

def fit_hark(sd,h,last_idx,constant_noise):
    yraw=np.asarray(sd[:last_idx+1],float)
    hraw=np.asarray(h[:last_idx+1],float)
    scale=float(np.median(yraw))
    if not(scale>0): raise RuntimeError("BAD_SCALE")
    y=yraw/scale
    hs=hraw/(scale*scale)
    if constant_noise:
        hc=float(np.median(hs))
        hused=np.full_like(hs,hc)
    else:
        hused=hs.copy()

    b_ols,q0,_=sqrt_ols_fit(y,last_idx)
    q0=max(q0,1e-8)
    theta0=np.r_[b_ols,math.log(q0)]
    bounds=[(-5,5),(-3,3),(-3,3),(-3,3),(-20,5)]
    res=minimize(kalman_negloglike,theta0,args=(y,hused),method="L-BFGS-B",
                 bounds=bounds,options={"maxiter":3000,"ftol":1e-10,"maxls":50})
    if not res.success:
        raise RuntimeError(f"HARK_OPT_FAIL:{constant_noise}:{res.message}")
    bscaled=np.asarray(res.x[:4],float)
    b=np.array([bscaled[0]*scale,bscaled[1],bscaled[2],bscaled[3]],float)
    q_orig=math.exp(float(res.x[4]))*scale*scale
    return {
      "theta_scaled":[float(x) for x in res.x],
      "beta_original":[float(x) for x in b],
      "q_original":float(q_orig),
      "scale":scale,
      "nll":float(res.fun),
      "iterations":int(res.nit),
      "constant_noise":bool(constant_noise),
      "h_const_original":float(np.median(hraw)) if constant_noise else None
    }

def run_filter_forecasts(sd,h,fit,last_form_idx,target_idxs):
    scale=float(fit["scale"])
    theta=np.asarray(fit["theta_scaled"],float)
    beta=theta[:4];q=math.exp(float(theta[4]))
    c,T=transition(beta)
    Q=np.zeros((22,22),float);Q[0,0]=q
    y=np.asarray(sd,float)/scale
    hs=np.asarray(h,float)/(scale*scale)
    if fit["constant_noise"]:
        hc=float(fit["h_const_original"]/(scale*scale))
        hused=np.full_like(hs,hc)
    else:
        hused=hs

    m,P=initial_state(y[:last_form_idx+1],hused[:last_form_idx+1])
    gains=[]
    for t in range(22,last_form_idx+1):
        mp=c+T@m;Pp=T@P@T.T+Q
        F=float(Pp[0,0]+hused[t]);v=float(y[t]-mp[0]);K=Pp[:,0]/F
        m=mp+K*v;P=Pp-np.outer(K,Pp[0,:]);P=(P+P.T)*0.5
        gains.append(float(K[0]))

    preds=[];oos_gains=[]
    expected=last_form_idx+1
    for t in target_idxs:
        if t!=expected:
            raise RuntimeError(f"NONCONTIG_TARGET:{expected}:{t}")
        mp=c+T@m;Pp=T@P@T.T+Q
        latent_pred=float(mp[0]*scale)
        if not(math.isfinite(latent_pred) and latent_pred>0):
            preds.append(np.nan)
        else:
            preds.append(latent_pred*latent_pred)
        F=float(Pp[0,0]+hused[t]);v=float(y[t]-mp[0]);K=Pp[:,0]/F
        m=mp+K*v;P=Pp-np.outer(K,Pp[0,:]);P=(P+P.T)*0.5
        oos_gains.append(float(K[0]))
        expected+=1
    return np.asarray(preds,float),{
      "formation_gain_mean":float(np.mean(gains)),"formation_gain_min":float(np.min(gains)),"formation_gain_max":float(np.max(gains)),
      "oos_gain_mean":float(np.mean(oos_gains)),"oos_gain_min":float(np.min(oos_gains)),"oos_gain_max":float(np.max(oos_gains))
    }

def roc_auc(y,s):
    y=np.asarray(y,int);s=np.asarray(s,float)
    n1=int(np.sum(y==1));n0=int(np.sum(y==0))
    if n1==0 or n0==0:return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qloss(y,f):
    y=max(float(y),EPS);f=max(float(f),EPS);z=y/f
    return z-math.log(z)-1

def calibration(y,p):
    Z=np.column_stack([np.ones(len(p)),p]);b=np.linalg.lstsq(Z,y,rcond=None)[0]
    return float(b[0]),float(b[1])

def metrics(y,p,pers,mean_dr,hi,ret,ext):
    mse=float(np.mean((p-y)**2));mm=float(np.mean((mean_dr-y)**2))
    high=(y>=hi).astype(int);alert=p>=hi
    tp=int(np.sum(alert&(high==1)));fp=int(np.sum(alert&(high==0)))
    fn=int(np.sum((~alert)&(high==1)));tn=int(np.sum((~alert)&(high==0)))
    precision=tp/(tp+fp) if tp+fp else None;recall=tp/(tp+fn) if tp+fn else None
    f1=2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else 0.0
    ci,cs=calibration(y,p);down=ret<0;extreme=ret<=ext
    return {
      "n":len(y),"mse":mse,"mae":float(np.mean(np.abs(p-y))),
      "historical_mean_mse":mm,"persistence_mse":float(np.mean((pers-y)**2)),
      "oos_r2_vs_historical_mean":float(1-mse/mm),
      "dr_qlike":float(np.mean([qloss(a,b) for a,b in zip(y,p)])),
      "historical_mean_dr_qlike":float(np.mean([qloss(a,mean_dr) for a in y])),
      "persistence_dr_qlike":float(np.mean([qloss(a,b) for a,b in zip(y,pers)])),
      "correlation":float(np.corrcoef(p,y)[0,1]),
      "forecast_mean":float(np.mean(p)),"realized_mean":float(np.mean(y)),
      "calibration_intercept":ci,"calibration_slope":cs,"calibration_slope_abs_error":abs(cs-1),
      "pred_min":float(np.min(p)),"pred_median":float(np.median(p)),"pred_max":float(np.max(p)),
      "high_risk_event_rate":float(np.mean(high)),"high_risk_roc_auc":roc_auc(high,p),
      "alert_coverage":float(np.mean(alert)),"alert_precision":precision,"alert_recall":recall,"alert_f1":f1,
      "tp":tp,"fp":fp,"fn":fn,"tn":tn,
      "unconditional_down_day_rate":float(np.mean(down)),
      "down_day_rate_given_alert":float(np.mean(down[alert])) if np.sum(alert) else None,
      "unconditional_extreme_negative_return_rate":float(np.mean(extreme)),
      "extreme_negative_return_rate_given_alert":float(np.mean(extreme[alert])) if np.sum(alert) else None
    }

def nw(diff,L):
    x=np.asarray(diff,float);n=len(x);mu=float(np.mean(x));d=x-mu
    lrv=float(np.dot(d,d)/n)
    for k in range(1,min(L,n-1)+1):
        g=float(np.dot(d[k:],d[:-k])/n);lrv+=2*(1-k/(L+1))*g
    se=math.sqrt(max(lrv,0)/n);t=mu/se if se>0 else None
    return {"mean":mu,"se":se,"t":t,"p_two_sided":2*(1-norm.cdf(abs(t))) if t is not None else None}

def eval_year(ds,close,dr,h,year):
    sd=np.sqrt(dr);ret=daily_return(close)
    cutoff=date(year-1,12,31)
    last_form=max(i for i,d in enumerate(ds) if d<=cutoff)
    target_idxs=[i for i,d in enumerate(ds) if d.year==year]
    if len(target_idxs)==0 or target_idxs[0]!=last_form+1:
        raise RuntimeError(f"TARGET_BOUNDARY:{year}:{last_form}:{target_idxs[:2]}")

    b_sqrt,_,ntrain=sqrt_ols_fit(sd,last_form)
    sqrt_pred=sqrt_ols_predict(sd,b_sqrt,target_idxs)
    tvfit=fit_hark(sd,h,last_form,False)
    cfit=fit_hark(sd,h,last_form,True)
    tv_pred,tvdiag=run_filter_forecasts(sd,h,tvfit,last_form,target_idxs)
    c_pred,cdiag=run_filter_forecasts(sd,h,cfit,last_form,target_idxs)
    for name,p in [("sqrt",sqrt_pred),("tv",tv_pred),("const",c_pred)]:
        if np.any(~np.isfinite(p)) or np.any(p<=0):
            raise RuntimeError(f"DOMAIN_FAILURE:{year}:{name}")

    form_idx=np.arange(22,last_form+1)
    mean_dr=float(np.mean(dr[form_idx]));hi=nearest_rank(dr[form_idx],.8);ext=nearest_rank(ret[form_idx],.05)
    ti=np.asarray(target_idxs,int);y=dr[ti];pers=dr[ti-1];r=ret[ti]
    blocks={
      "SQRT_HAR_DR":metrics(y,sqrt_pred,pers,mean_dr,hi,r,ext),
      "HARK_SD_CONST":metrics(y,c_pred,pers,mean_dr,hi,r,ext),
      "HARK_SD_TV":metrics(y,tv_pred,pers,mean_dr,hi,r,ext)
    }
    rows=[]
    for j,i in enumerate(ti):
        rows.append({
          "target_date":ds[i].isoformat(),"evaluation_year":year,"target_dr":float(y[j]),"target_close_return":float(r[j]),
          "high_risk_threshold":hi,"sqrt_forecast_dr":float(sqrt_pred[j]),
          "hark_const_forecast_dr":float(c_pred[j]),"hark_tv_forecast_dr":float(tv_pred[j]),
          "measurement_variance_h":float(h[i])
        })
    return {
      "formation_n_supervised":ntrain,"formation_last_date":ds[last_form].isoformat(),"test_n":len(ti),
      "sqrt_beta":[float(x) for x in b_sqrt],"hark_const_fit":cfit,"hark_tv_fit":tvfit,
      "hark_const_gain":cdiag,"hark_tv_gain":tvdiag,
      "formation_h_mean":float(np.mean(h[:last_form+1])),"oos_h_mean":float(np.mean(h[ti])),
      **blocks
    },rows

def pooled(rows,a,b):
    y=np.array([r["target_dr"] for r in rows],float)
    pa=np.array([r[a] for r in rows],float);pb=np.array([r[b] for r in rows],float)
    dm=(pa-y)**2-(pb-y)**2
    dq=np.array([qloss(yy,aa)-qloss(yy,bb) for yy,aa,bb in zip(y,pa,pb)])
    return {
      "n":len(y),"a_mse":float(np.mean((pa-y)**2)),"b_mse":float(np.mean((pb-y)**2)),
      "a_qlike":float(np.mean([qloss(yy,aa) for yy,aa in zip(y,pa)])),
      "b_qlike":float(np.mean([qloss(yy,bb) for yy,bb in zip(y,pb])),
      "mse_a_minus_b_nw5":nw(dm,5),"mse_a_minus_b_nw10":nw(dm,10),
      "qlike_a_minus_b_nw5":nw(dq,5),"qlike_a_minus_b_nw10":nw(dq,10)
    }

def main():
    out=Path("hark_sd_out");out.mkdir(exist_ok=True)
    ds,close,dr,h=load_days()
    years={};allrows=[]
    for y in YEARS:
        block,rows=eval_year(ds,close,dr,h,y);years[str(y)]=block;allrows+=rows
        print(json.dumps({"year":y,
          "sqrt_mse":block["SQRT_HAR_DR"]["mse"],
          "const_mse":block["HARK_SD_CONST"]["mse"],
          "tv_mse":block["HARK_SD_TV"]["mse"],
          "tv_auc":block["HARK_SD_TV"]["high_risk_roc_auc"],
          "tv_gain":block["hark_tv_gain"]["oos_gain_mean"]},sort_keys=True))
    pre=[r for r in allrows if int(r["evaluation_year"]) in PRE_YEARS]
    p_sqrt_tv=pooled(pre,"sqrt_forecast_dr","hark_tv_forecast_dr")
    p_const_tv=pooled(pre,"hark_const_forecast_dr","hark_tv_forecast_dr")
    msewins=sum(years[str(y)]["HARK_SD_TV"]["mse"]<years[str(y)]["SQRT_HAR_DR"]["mse"] for y in PRE_YEARS)
    calwins=sum(years[str(y)]["HARK_SD_TV"]["calibration_slope_abs_error"]<years[str(y)]["SQRT_HAR_DR"]["calibration_slope_abs_error"] for y in PRE_YEARS)
    aucok=all(years[str(y)]["HARK_SD_TV"]["high_risk_roc_auc"]>=years[str(y)]["SQRT_HAR_DR"]["high_risk_roc_auc"]-.02 for y in PRE_YEARS)
    gate=bool(msewins>=2 and p_sqrt_tv["b_mse"]<p_sqrt_tv["a_mse"] and p_sqrt_tv["b_qlike"]<=p_sqrt_tv["a_qlike"]
              and calwins>=2 and aucok
              and p_const_tv["b_mse"]<=p_const_tv["a_mse"] and p_const_tv["b_qlike"]<=p_const_tv["a_qlike"])
    result={
      "identity":IDENTITY,"manifest_modified":False,"production_write":"NONE",
      "panel_first_day":ds[0].isoformat(),"panel_last_day":ds[-1].isoformat(),"panel_sha256":panel_hash(ds,close,dr,h),
      "evidence_classification":"RETROSPECTIVE_ONLY_NOT_PRISTINE_CONFIRMATION",
      "years":years,"pooled_2022_2024_sqrt_vs_tv":p_sqrt_tv,"pooled_2022_2024_const_vs_tv":p_const_tv,
      "feasibility_gate":{
        "mse_wins_vs_sqrt":int(msewins),"calibration_wins_vs_sqrt":int(calwins),"auc_tolerance_all":aucok,
        "passed":gate,"decision":"RETROSPECTIVE_LATENT_STATE_SUPPORTED" if gate else "RETROSPECTIVE_LATENT_STATE_NOT_SUPPORTED"
      }
    }
    (out/"GOLD_CONTROL_DOWNSIDE_HARK_SD_XAU_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))
    with open(out/"GOLD_CONTROL_DOWNSIDE_HARK_SD_XAU_V1_FORECASTS_2026-09-22.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(allrows[0].keys()));w.writeheader();w.writerows(allrows)
    lines=["# GOLD CONTROL — DOWNSIDE HARK-SD V1 RESULT","",
      f"**Decision:** {result['feasibility_gate']['decision']}  ","**Manifest modified:** NO  ","",
      "| Year | SQRT MSE | HARK-Const MSE | HARK-TV MSE | SQRT R2 | TV R2 | SQRT AUC | TV AUC | TV gain |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in YEARS:
        b=years[str(y)];s=b["SQRT_HAR_DR"];c=b["HARK_SD_CONST"];tv=b["HARK_SD_TV"]
        lines.append(f"| {y} | {s['mse']:.6g} | {c['mse']:.6g} | {tv['mse']:.6g} | {s['oos_r2_vs_historical_mean']:.4f} | {tv['oos_r2_vs_historical_mean']:.4f} | {s['high_risk_roc_auc']:.4f} | {tv['high_risk_roc_auc']:.4f} | {b['hark_tv_gain']['oos_gain_mean']:.4f} |")
    (out/"GOLD_CONTROL_DOWNSIDE_HARK_SD_XAU_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("HARK_SD_SUCCESS")

if __name__=="__main__": main()
