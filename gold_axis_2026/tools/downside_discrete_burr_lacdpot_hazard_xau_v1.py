from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from datetime import date, datetime
from pathlib import Path

import numpy as np
import psycopg
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import rankdata

IDENTITY="DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_RESEARCH"
SERIES="XAU_STAKTRAKR_RESEARCH_DAILY_R1"
FORM_END=date(2023,12,31)
VAL_START=date(2024,1,1); VAL_END=date(2024,12,31)
CH_START=date(2025,1,1); CH_END=date(2025,12,31)
Q_EVENT=0.95
Q_ALERT=0.95

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,dtype=float)
    if len(a)==0: raise RuntimeError("EMPTY_QUANTILE")
    k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_series(end_date):
    sql="""
    select observation_ts, value
    from public.usable_observations
    where series_id=%s
      and observation_ts::date <= %s::date
    order by observation_ts
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql,(SERIES,end_date.isoformat()))
            raw=cur.fetchall()
    by={}
    for ts,v in raw:
        d=ts.date()
        x=float(v)
        if not math.isfinite(x) or x<=0: raise RuntimeError(f"BAD_PRICE:{d}")
        if d in by and abs(by[d]-x)>1e-12: raise RuntimeError(f"DUPLICATE_DATE_CONFLICT:{d}")
        by[d]=x
    ds=sorted(by)
    if len(ds)<1500: raise RuntimeError(f"INSUFFICIENT_DAILY_HISTORY:{len(ds)}")
    px=np.array([by[d] for d in ds],dtype=float)
    loss=np.full(len(ds),np.nan)
    loss[1:]=-np.log(px[1:]/px[:-1])
    return ds,px,loss

def panel_hash(ds,px,through):
    s="\n".join(f"{d.isoformat()}|{p:.10f}" for d,p in zip(ds,px) if d<=through)
    return hashlib.sha256(s.encode()).hexdigest()

def unpack(z):
    omega, beta_raw, alpha, zeta, lk, eraw = z
    beta=0.995*math.tanh(beta_raw)
    kappa=0.05+math.exp(lk)
    frac=1/(1+math.exp(-eraw))
    eta=kappa*(0.02+0.96*frac)
    eta=min(eta,kappa*(1-1e-8))
    return omega,beta,alpha,zeta,kappa,eta

def log_phi(psi,kappa,eta):
    return (math.log(psi)+(1.0/kappa)*math.log(eta)+gammaln(1.0/eta)
            -gammaln(1.0+1.0/kappa)-gammaln(1.0/eta-1.0/kappa))

def survival(x,psi,kappa,eta):
    if x<=0: return 1.0
    lp=log_phi(psi,kappa,eta)
    log_ratio=kappa*(math.log(float(x))-lp)
    if log_ratio>700:
        log_term=math.log(eta)+log_ratio
    else:
        log_term=math.log1p(eta*math.exp(log_ratio))
    ls=-(1.0/eta)*log_term
    if ls<-745: return 0.0
    return math.exp(ls)

def interval_psis(xdur, excess, params):
    omega,beta,alpha,zeta,kappa,eta=params
    psis=np.empty(len(xdur),dtype=float)
    psis[0]=float(np.mean(xdur))
    for j in range(1,len(xdur)):
        le=math.log(max(float(excess[j]),1e-12))
        lp=omega+beta*math.log(psis[j-1])+alpha*math.log(float(xdur[j-1]))+zeta*le
        psis[j]=math.exp(min(50,max(-50,lp)))
    return psis

def nll(z,xdur,excess):
    try:
        params=unpack(z)
        psis=interval_psis(xdur,excess,params)
        _,_,_,_,kappa,eta=params
        ll=0.0
        for x,psi in zip(xdur,psis):
            s0=survival(int(x)-1,float(psi),kappa,eta)
            s1=survival(int(x),float(psi),kappa,eta)
            p=max(s0-s1,1e-300)
            ll+=math.log(p)
        if not math.isfinite(ll): return 1e100
        return -ll
    except Exception:
        return 1e100

def fit_model(xdur,excess):
    meanx=float(np.mean(xdur))
    candidates=[]
    inits=[
        [math.log(meanx)*0.4,0.5,0.2,-0.1,math.log(0.8),-1.0],
        [math.log(meanx)*0.6,0.8,0.1,-0.1,math.log(1.0),-0.5],
        [math.log(meanx)*0.3,0.2,0.3,-0.2,math.log(0.6),-1.5],
        [math.log(meanx)*0.5,-0.2,0.2,0.0,math.log(1.2),-1.0],
        [math.log(meanx)*0.7,1.0,0.0,-0.2,math.log(0.9),-0.2],
        [math.log(meanx)*0.5,0.4,0.4,-0.05,math.log(1.5),-1.5],
    ]
    for z0 in inits:
        res=minimize(nll,np.array(z0,dtype=float),args=(xdur,excess),method="L-BFGS-B",
                     options={"maxiter":3000,"ftol":1e-12,"gtol":1e-8})
        candidates.append(res)
    good=[r for r in candidates if math.isfinite(float(r.fun))]
    if not good: raise RuntimeError("ACD_FIT_FAILED")
    best=min(good,key=lambda r:float(r.fun))
    return unpack(best.x),float(best.fun),bool(best.success),str(best.message)

def event_state(ds,loss,u,end_date):
    idx=[i for i,d in enumerate(ds) if d<=end_date and i>0 and math.isfinite(loss[i]) and loss[i]>u]
    if len(idx)<40: raise RuntimeError(f"TOO_FEW_FORM_EVENTS:{len(idx)}")
    exc=np.array([loss[i]-u for i in idx],dtype=float)
    x=np.diff(np.array(idx,dtype=int))
    return idx,exc,x

def fitted_training_hazards(event_idx,exc,xdur,params,formation_last_idx):
    psis=interval_psis(xdur,exc,params)
    _,beta,alpha,zeta,kappa,eta=params
    hz=[]
    # Completed intervals.
    for j,x in enumerate(xdur):
        psi=float(psis[j])
        for elapsed in range(1,int(x)+1):
            s0=survival(elapsed-1,psi,kappa,eta)
            s1=survival(elapsed,psi,kappa,eta)
            hz.append(1.0-s1/max(s0,1e-300))
    # Open interval after last formation event.
    psi_last=float(psis[-1])
    last_x=int(xdur[-1]); last_exc=float(exc[-1])
    lp=params[0]+beta*math.log(psi_last)+alpha*math.log(last_x)+zeta*math.log(max(last_exc,1e-12))
    psi_next=math.exp(min(50,max(-50,lp)))
    last_event=event_idx[-1]
    for idx in range(last_event+1,formation_last_idx+1):
        elapsed=idx-last_event
        s0=survival(elapsed-1,psi_next,kappa,eta)
        s1=survival(elapsed,psi_next,kappa,eta)
        hz.append(1.0-s1/max(s0,1e-300))
    return np.array(hz,dtype=float),psi_next

def replay(ds,loss,u,params,formation_end,target_start,target_end):
    form_last=max(i for i,d in enumerate(ds) if d<=formation_end)
    event_idx,exc,xdur=event_state(ds,loss,u,formation_end)
    psis=interval_psis(xdur,exc,params)
    omega,beta,alpha,zeta,kappa,eta=params
    psi_last=float(psis[-1])
    last_x=int(xdur[-1]); last_exc=float(exc[-1])
    lp=omega+beta*math.log(psi_last)+alpha*math.log(last_x)+zeta*math.log(max(last_exc,1e-12))
    psi_next=math.exp(min(50,max(-50,lp)))
    last_event=event_idx[-1]
    rows=[]
    for i in range(form_last+1,len(ds)):
        d=ds[i]
        elapsed=i-last_event
        s0=survival(elapsed-1,psi_next,kappa,eta)
        s1=survival(elapsed,psi_next,kappa,eta)
        hazard=min(max(1.0-s1/max(s0,1e-300),1e-12),1-1e-12)
        event=int(math.isfinite(loss[i]) and loss[i]>u)
        if target_start<=d<=target_end:
            rows.append({
                "origin_date":ds[i-1].isoformat(),
                "target_date":d.isoformat(),
                "loss":float(loss[i]),
                "extreme_event":event,
                "hazard":hazard,
                "elapsed_since_last_extreme":elapsed,
            })
        if event:
            x=elapsed
            e=float(loss[i]-u)
            lp=omega+beta*math.log(psi_next)+alpha*math.log(float(x))+zeta*math.log(max(e,1e-12))
            psi_next=math.exp(min(50,max(-50,lp)))
            last_event=i
    return rows

def roc_auc(y,s):
    y=np.asarray(y,dtype=int); s=np.asarray(s,dtype=float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if n1==0 or n0==0: return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def avg_precision(y,s):
    y=np.asarray(y,dtype=int); s=np.asarray(s,dtype=float)
    n1=int(np.sum(y))
    if n1==0:return None
    order=np.argsort(-s,kind="mergesort"); yy=y[order]
    tp=np.cumsum(yy); k=np.arange(1,len(yy)+1)
    return float(np.sum((tp/k)*yy)/n1)

def metrics(rows,const_p,alert_thr):
    y=np.array([r["extreme_event"] for r in rows],dtype=int)
    p=np.array([r["hazard"] for r in rows],dtype=float)
    eps=1e-12
    brier=float(np.mean((p-y)**2))
    brier_const=float(np.mean((const_p-y)**2))
    ll=float(-np.mean(y*np.log(np.clip(p,eps,1-eps))+(1-y)*np.log(np.clip(1-p,eps,1-eps))))
    ll_const=float(-np.mean(y*np.log(const_p)+(1-y)*np.log(1-const_p)))
    alert=p>=alert_thr
    tp=int(np.sum(alert & (y==1))); fp=int(np.sum(alert & (y==0)))
    fn=int(np.sum((~alert)&(y==1))); tn=int(np.sum((~alert)&(y==0)))
    er=float(np.mean(y))
    event_h=p[y==1]; nonevent_h=p[y==0]
    topthr=nearest_rank(p,0.90)
    top=p>=topthr
    top_rate=float(np.mean(y[top])) if np.sum(top) else None
    return {
        "n":len(rows),"events":int(np.sum(y)),"event_rate":er,
        "mean_hazard":float(np.mean(p)),
        "brier":brier,"constant_brier":brier_const,
        "brier_skill":float(1-brier/brier_const) if brier_const>0 else None,
        "log_loss":ll,"constant_log_loss":ll_const,
        "roc_auc":roc_auc(y,p),"average_precision":avg_precision(y,p),
        "alert_threshold":alert_thr,"alert_coverage":float(np.mean(alert)),
        "alert_recall":float(tp/(tp+fn)) if tp+fn else None,
        "alert_precision":float(tp/(tp+fp)) if tp+fp else None,
        "false_alert_rate":float(fp/(fp+tn)) if fp+tn else None,
        "tp":tp,"fp":fp,"fn":fn,"tn":tn,
        "event_mean_hazard":float(np.mean(event_h)) if len(event_h) else None,
        "event_median_hazard":float(np.median(event_h)) if len(event_h) else None,
        "nonevent_mean_hazard":float(np.mean(nonevent_h)) if len(nonevent_h) else None,
        "top_decile_event_rate":top_rate,
        "top_decile_event_concentration_vs_base":float(top_rate/er) if top_rate is not None and er>0 else None,
    }

def gate24(m):
    return bool(m["brier_skill"] is not None and m["brier_skill"]>0
                and m["roc_auc"] is not None and m["roc_auc"]>=0.55
                and m["alert_recall"] is not None and m["alert_recall"]>=0.15
                and m["alert_precision"] is not None and m["alert_precision"]>m["event_rate"])

def gate25(m,passed24):
    return bool(passed24 and m["brier_skill"] is not None and m["brier_skill"]>0
                and m["roc_auc"] is not None and m["roc_auc"]>=0.50
                and m["alert_recall"] is not None and m["alert_recall"]>=0.10
                and m["alert_precision"] is not None and m["alert_precision"]>m["event_rate"])

def write_csv(path,rows):
    if not rows: return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=("pre2025","2025"),required=True)
    ap.add_argument("--outdir",required=True)
    ap.add_argument("--config"); ap.add_argument("--pre-result")
    a=ap.parse_args(); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)

    end=VAL_END if a.stage=="pre2025" else CH_END
    ds,px,loss=load_series(end)

    if a.stage=="pre2025":
        form_loss=np.array([loss[i] for i,d in enumerate(ds) if d<=FORM_END and i>0 and math.isfinite(loss[i])],dtype=float)
        u=nearest_rank(form_loss,Q_EVENT)
        event_idx,exc,xdur=event_state(ds,loss,u,FORM_END)
        params,fit_nll,success,msg=fit_model(xdur,exc)
        form_last=max(i for i,d in enumerate(ds) if d<=FORM_END)
        train_hz,_=fitted_training_hazards(event_idx,exc,xdur,params,form_last)
        alert_thr=nearest_rank(train_hz,Q_ALERT)
        const_p=float(np.mean(form_loss>u))
        rows24=replay(ds,loss,u,params,FORM_END,VAL_START,VAL_END)
        m24=metrics(rows24,const_p,alert_thr)
        passed=gate24(m24)
        cfg={
            "identity":IDENTITY,"series":SERIES,"formation_end":FORM_END.isoformat(),
            "threshold_u":u,"threshold_quantile":Q_EVENT,
            "constant_event_rate":const_p,"alert_threshold":alert_thr,
            "params":{"omega":params[0],"beta":params[1],"alpha":params[2],"zeta":params[3],
                      "kappa":params[4],"eta":params[5]},
            "fit_nll":fit_nll,"optimizer_success":success,"optimizer_message":msg,
            "formation_event_count":len(event_idx),"formation_duration_count":len(xdur),
            "panel_sha256_through_2024":panel_hash(ds,px,VAL_END),
            "frozen_before_2025":True,
        }
        res={"identity":IDENTITY,"status":"PRE2025_FROZEN","2024_validation":m24,
             "pre2025_gate_passed":passed,
             "decision":"PRE2025_EXTREME_DOWN_HAZARD_SUPPORTED" if passed else "PRE2025_EXTREME_DOWN_HAZARD_NOT_SUPPORTED"}
        (out/"GOLD_CONTROL_DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_FROZEN_CONFIG_2026-09-21.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
        (out/"GOLD_CONTROL_DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_PRE2025_RESULT_2026-09-21.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
        write_csv(out/"GOLD_CONTROL_DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_2024_FORECASTS_2026-09-21.csv",rows24)
        print("ACDPOT_PRE2025_SUCCESS")
    else:
        if not a.config or not a.pre_result: raise RuntimeError("CONFIG_PRE_RESULT_REQUIRED")
        cfg=json.loads(Path(a.config).read_text()); pre=json.loads(Path(a.pre_result).read_text())
        if cfg["identity"]!=IDENTITY or pre["identity"]!=IDENTITY: raise RuntimeError("IDENTITY_MISMATCH")
        if panel_hash(ds,px,VAL_END)!=cfg["panel_sha256_through_2024"]: raise RuntimeError("PANEL_PREFIX_CHANGED")
        p=cfg["params"]; params=(p["omega"],p["beta"],p["alpha"],p["zeta"],p["kappa"],p["eta"])
        rows25=replay(ds,loss,float(cfg["threshold_u"]),params,FORM_END,CH_START,CH_END)
        m25=metrics(rows25,float(cfg["constant_event_rate"]),float(cfg["alert_threshold"]))
        trans=gate25(m25,bool(pre["pre2025_gate_passed"]))
        res={"identity":IDENTITY,"status":"LOCKED_2025_REPLAY_COMPLETE","2025_challenge":m25,
             "pre2025_gate_passed":pre["pre2025_gate_passed"],"2025_transport_passed":trans,
             "decision":"2025_HAZARD_TRANSPORT_SUPPORTED" if trans else "2025_HAZARD_TRANSPORT_NOT_SUPPORTED"}
        (out/"GOLD_CONTROL_DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_2025_RESULT_2026-09-21.json").write_text(json.dumps(res,indent=2),encoding="utf-8")
        write_csv(out/"GOLD_CONTROL_DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_2025_FORECASTS_2026-09-21.csv",rows25)
        print("ACDPOT_2025_SUCCESS")

if __name__=="__main__":
    main()
