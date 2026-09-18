#!/usr/bin/env python3
"""Boundary-safe weekly B-CARS(1,1) research implementation.

Authority:
  GOLD_CONTROL_DIRECTION_BCARS_SV_V1_PREREG_2026-09-18.md
"""

from __future__ import annotations
import argparse,csv,json,math
from datetime import date
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import beta as beta_dist

MIN_WEEK=date(2022,3,7)
INITIAL_WINDOW=52
STARTS=[
 ((.25,.25,.25,.25),1.0),
 ((.10,.70,.10,.10),.5),
 ((.05,.85,.05,.05),1.0),
 ((.10,.20,.60,.10),.5),
 ((.20,.30,.30,.20),2.0),
]

def unpack(theta):
    a,b,c,lb=map(float,theta)
    z=np.array([a,b,c,0.0]); z-=z.max()
    w=np.exp(z); w/=w.sum()
    return float(w[0]),float(w[1]),float(w[2]),float(w[3]),float(math.exp(lb))

def start_theta(weights,beta):
    o,g,t,s=weights
    return np.array([math.log(o/s),math.log(g/s),math.log(t/s),math.log(beta)])

def kpath(y,theta):
    o,g,t,s,b=unpack(theta)
    den=1-g-t
    if den<=0: raise FloatingPointError
    k=np.empty(len(y)); k[0]=o/den
    if not 0<k[0]<1: raise FloatingPointError
    for i in range(1,len(y)):
        k[i]=o+g*k[i-1]+t*y[i-1]
        if not 0<k[i]<1: raise FloatingPointError
    return k,(o,g,t,s,b)

def nll(theta,y):
    try:
        k,pars=kpath(y,theta); b=pars[-1]
        a=k*b/(1-k)
        ll=gammaln(a+b)-gammaln(a)-gammaln(b)+(a-1)*np.log(y)+(b-1)*np.log1p(-y)
        v=-float(np.sum(ll))
        return v if math.isfinite(v) else 1e100
    except Exception:
        return 1e100

def fit(raw_y):
    n=len(raw_y)
    # Smithson-Verkuilen boundary transformation.
    y=(raw_y*(n-1)+.5)/n
    fits=[]
    for weights,b0 in STARTS:
        r=minimize(nll,start_theta(weights,b0),args=(y,),method="L-BFGS-B",
                   bounds=[(-12,12),(-12,12),(-12,12),(-8,8)],
                   options={"maxiter":3000,"ftol":1e-12,"gtol":1e-8,"maxls":50})
        if r.success and math.isfinite(float(r.fun)): fits.append(r)
    if not fits: raise RuntimeError("MODEL_FIT_BLOCKED:NO_CONVERGED_START")
    best=min(fits,key=lambda r:float(r.fun))
    k,(o,g,t,s,b)=kpath(y,best.x)
    kt=o+g*k[-1]+t*y[-1]
    kraw=(n*kt-.5)/(n-1)
    if not 0<=kraw<=1: raise RuntimeError("INVERSE_BOUNDARY_TRANSFORM_OUTSIDE_UNIT_INTERVAL")
    alpha=kt*b/(1-kt)
    pext=float(1-beta_dist.cdf(.5,alpha,b))
    return {"omega":o,"gamma":g,"tau":t,"slack":s,"beta":b,
            "k_transformed":float(kt),"k_raw":float(kraw),
            "p_ext_up":pext,"loglik":-float(best.fun),
            "converged_starts":len(fits)}

def load(path):
    rows=[]
    with Path(path).open(encoding="utf-8",newline="") as fh:
        for r in csv.DictReader(fh):
            d=date.fromisoformat(r["week_start"])
            if d<MIN_WEEK: continue
            ur=float(r["up_ratio"]); ret=float(r["return_log"])
            if not 0<=ur<=1: raise RuntimeError("UP_RATIO_OUTSIDE_UNIT_INTERVAL")
            if (ret>0)!=(ur>.5): raise RuntimeError("DIRECTION_IDENTITY_FAIL")
            rows.append((d,ur,ret))
    return rows

def forecasts(rows):
    out=[]
    for j in range(INITIAL_WINDOW,len(rows)):
        train=rows[:j]; target=rows[j]
        y=np.array([x[1] for x in train],dtype=float)
        f=fit(y)
        out.append({
          "origin_week":train[-1][0].isoformat(),"target_week":target[0].isoformat(),
          "n_train":j,**f,"historical_mean_ur":float(np.mean(y)),
          "forecast_direction":"UP" if f["k_transformed"]>.5 else "DOWN",
          "actual_direction":"UP" if target[2]>0 else "DOWN",
          "previous_week_direction":"UP" if train[-1][2]>0 else "DOWN",
          "actual_up_ratio":target[1],
        })
    return out

def metrics(rows):
    n=len(rows); up=sum(r["actual_direction"]=="UP" for r in rows); dn=n-up
    tp=sum(r["forecast_direction"]=="UP" and r["actual_direction"]=="UP" for r in rows)
    tn=sum(r["forecast_direction"]=="DOWN" and r["actual_direction"]=="DOWN" for r in rows)
    fp=sum(r["forecast_direction"]=="UP" and r["actual_direction"]=="DOWN" for r in rows)
    fn=sum(r["forecast_direction"]=="DOWN" and r["actual_direction"]=="UP" for r in rows)
    sse=sum((r["actual_up_ratio"]-r["k_raw"])**2 for r in rows)
    sse0=sum((r["actual_up_ratio"]-r["historical_mean_ur"])**2 for r in rows)
    eps=1e-12
    brier=sum((r["p_ext_up"]-(r["actual_direction"]=="UP"))**2 for r in rows)/n
    logloss=-sum((1 if r["actual_direction"]=="UP" else 0)*math.log(min(max(r["p_ext_up"],eps),1-eps))+
                 (0 if r["actual_direction"]=="UP" else 1)*math.log(min(max(1-r["p_ext_up"],eps),1-eps))
                 for r in rows)/n
    return {"n":n,"accuracy":(tp+tn)/n,
            "balanced_accuracy":((tp/up)+(tn/dn))/2,
            "actual_up":up,"actual_down":dn,"forecast_up":tp+fp,"forecast_down":tn+fn,
            "up_sensitivity":tp/up,"down_sensitivity":tn/dn,
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,
            "always_up_accuracy":up/n,
            "previous_sign_accuracy":sum(r["previous_week_direction"]==r["actual_direction"] for r in rows)/n,
            "mse_up_ratio_bcars":sse/n,"mse_up_ratio_historical_mean":sse0/n,
            "r2_oos_up_ratio":1-sse/sse0,
            "brier_p_ext":brier,"log_loss_p_ext":logloss}

def main():
    p=argparse.ArgumentParser(); p.add_argument("input_csv"); p.add_argument("--through-year",type=int,required=True)
    a=p.parse_args(); rows=load(a.input_csv); fc=forecasts(rows)
    fc=[r for r in fc if int(r["target_week"][:4])<=a.through_year]
    years=sorted({r["target_week"][:4] for r in fc})
    print(json.dumps({"by_year":{y:metrics([r for r in fc if r["target_week"].startswith(y)]) for y in years},
                      "all":metrics(fc)},indent=2))
if __name__=="__main__": main()
