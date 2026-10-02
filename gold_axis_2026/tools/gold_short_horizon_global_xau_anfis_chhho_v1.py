from __future__ import annotations
import io, json, math, os, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler

import gold_short_horizon_global_xau_anfis_vanilla_v1 as v

REPO=v.REPO
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_anfis_chhho_out")); OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5
POP=8
GENS=8
LOCAL_MAX=60
D=len(v.CORE3); R=v.RULES
NANT=D*R
LO=np.r_[np.full(NANT,-4.0),np.full(NANT,math.log(v.SFLOOR))]
HI=np.r_[np.full(NANT, 4.0),np.full(NANT,math.log(v.SCEIL))]
CENTER_SIG=.70
LOGSPREAD_SIG=.30

def encode(c,l):
    return np.clip(np.r_[np.asarray(c).ravel(),np.asarray(l).ravel()],LO,HI)

def decode(theta):
    z=np.asarray(theta,float)
    c=z[:NANT].reshape(R,D)
    l=z[NANT:].reshape(R,D)
    return c,np.clip(l,math.log(v.SFLOOR),math.log(v.SCEIL))

def logistic_sequence(n,seed):
    rng=np.random.default_rng(seed)
    x=float(rng.uniform(.1,.9)); a=np.empty(n)
    for i in range(n):
        x=4*x*(1-x); a[i]=x
    return a

def initial_anchor(X):
    c,s,_=v.init_antecedents(X)
    return encode(c,np.log(np.clip(s,v.SFLOOR,v.SCEIL)))

def init_chaotic(anchor,seed):
    z=logistic_sequence((POP-1)*len(anchor),seed).reshape(POP-1,-1)
    P=np.empty((POP,len(anchor)),float); P[0]=anchor
    nlocal=(POP-1)//2
    sig=np.r_[np.full(NANT,CENTER_SIG),np.full(NANT,LOGSPREAD_SIG)]
    if nlocal:
        P[1:1+nlocal]=np.clip(anchor+(2*z[:nlocal]-1)*sig,LO,HI)
    if 1+nlocal<POP:
        zz=z[nlocal:]
        P[1+nlocal:]=LO+zz*(HI-LO)
    return np.clip(P,LO,HI)

def candidate_fit(theta,X,y):
    c,l=decode(theta); beta=v.lse(X,y,c,l)
    pred=(v.design(X,c,l)@beta).ravel()
    return float(np.mean((pred-y)**2))

def candidate_check(theta,X,y,Xc,yc):
    c,l=decode(theta); beta=v.lse(X,y,c,l)
    p=np.clip((v.design(Xc,c,l)@beta).ravel(),1e-6,1-1e-6)
    return float(np.mean((p-yc)**2))

def pop_fit(P,X,y):
    return np.array([candidate_fit(z,X,y) for z in P],float)

def val_pick(P,F,X,y,Xc,yc,best=None,bestv=math.inf):
    k=max(2,len(P)//4)
    for i in np.argsort(F)[:k]:
        q=candidate_check(P[i],X,y,Xc,yc)
        if q<bestv:
            best=P[i].copy(); bestv=float(q)
    return best,bestv

def hho_phase(X,y,Xc,yc,seed):
    rng=np.random.default_rng(seed)
    anchor=initial_anchor(X)
    P=init_chaotic(anchor,seed); F=pop_fit(P,X,y)
    vb,vf=val_pick(P,F,X,y,Xc,yc)
    for t in range(GENS):
        rabbit=P[int(np.argmin(F))].copy()
        E1=2*(1-(t+1)/GENS); mean=P.mean(axis=0)
        NP=P.copy()
        for i in range(POP):
            E0=2*rng.random()-1; E=E1*E0; q=rng.random(); J=2*(1-rng.random())
            if abs(E)>=1:
                if q>=.5:
                    xr=P[int(rng.integers(0,POP))]
                    cand=xr-rng.random(len(anchor))*np.abs(xr-2*rng.random(len(anchor))*P[i])
                else:
                    cand=(rabbit-mean)-rng.random(len(anchor))*(LO+rng.random(len(anchor))*(HI-LO))
            else:
                if rng.random()>=.5:
                    cand=rabbit-E*np.abs(J*rabbit-P[i])
                else:
                    Yc=rabbit-E*np.abs(J*rabbit-P[i])
                    Z=Yc+rng.standard_cauchy(len(anchor))*.01
                    ycand=np.clip(Yc,LO,HI); zcand=np.clip(Z,LO,HI)
                    cand=ycand if candidate_fit(ycand,X,y)<=candidate_fit(zcand,X,y) else zcand
            NP[i]=np.clip(cand,LO,HI)
        NF=pop_fit(NP,X,y)
        imp=NF<F; P[imp]=NP[imp]; F[imp]=NF[imp]
        vb,vf=val_pick(P,F,X,y,Xc,yc,vb,vf)
    if vb is None:
        vb=P[int(np.argmin(F))].copy(); vf=candidate_check(vb,X,y,Xc,yc)
    return vb,float(vf)

def local_step(c,l,X,y,k,hist):
    beta=v.lse(X,y,c,l); loss,gc,gl=v.loss_grad(X,y,c,l,beta)
    g=np.r_[gc.ravel(),gl.ravel()]; gn=float(np.linalg.norm(g))
    if np.isfinite(gn) and gn>1e-15:
        eta=k/gn; c=c-eta*gc; l=l-eta*gl
        l=np.clip(l,math.log(v.SFLOOR),math.log(v.SCEIL))
    hist.append(loss)
    if len(hist)>=5:
        d=np.diff(hist[-5:]); sg=np.sign(d)
        if np.all(d<0): k*=v.KINC
        elif np.all(sg[:-1]*sg[1:]<0): k*=v.KDEC
    return c,l,k,float(loss)

def choose_local_epochs(theta,X,y,Xc,yc):
    c,l=decode(theta); k=v.K0; hist=[]; best=(math.inf,1)
    for ep in range(LOCAL_MAX):
        beta=v.lse(X,y,c,l)
        p=np.clip((v.design(Xc,c,l)@beta).ravel(),1e-6,1-1e-6)
        chk=float(np.mean((p-yc)**2))
        if chk<best[0]-1e-12: best=(chk,ep+1)
        c,l,k,_=local_step(c,l,X,y,k,hist)
    return int(best[1]),float(best[0])

def local_refit(theta,X,y,epochs):
    c,l=decode(theta); k=v.K0; hist=[]
    for _ in range(epochs):
        c,l,k,_=local_step(c,l,X,y,k,hist)
    beta=v.lse(X,y,c,l)
    return c,l,beta,{"first_brier":hist[0] if hist else None,"last_brier":hist[-1] if hist else None}

def map_theta_to_full(theta,sc_inner,sc_full):
    c,l=decode(theta); s=np.exp(l)
    raw_c=c*sc_inner.scale_[None,:]+sc_inner.mean_[None,:]
    raw_s=s*sc_inner.scale_[None,:]
    cf=(raw_c-sc_full.mean_[None,:])/sc_full.scale_[None,:]
    sf=raw_s/sc_full.scale_[None,:]
    return encode(np.clip(cf,-4,4),np.log(np.clip(sf,v.SFLOOR,v.SCEIL)))

def fit_predict_hybrid(train,test,block_id):
    Xraw,Xtest_raw,_=v.impute_fit(train,test)
    y=(train.target_r3.to_numpy(float)>0).astype(float)
    ncheck=max(60,int(round(v.CHECK_FRAC*len(train)))); split=len(train)-ncheck
    sc=StandardScaler().fit(Xraw[:split])
    X=sc.transform(Xraw[:split]); Xc=sc.transform(Xraw[split:])
    seed=771100+1009*block_id
    theta,meta_check=hho_phase(X,y[:split],Xc,y[split:],seed)
    epochs,local_check=choose_local_epochs(theta,X,y[:split],Xc,y[split:])
    scf=StandardScaler().fit(Xraw)
    full_theta=map_theta_to_full(theta,sc,scf)
    Xf=scf.transform(Xraw); Xte=scf.transform(Xtest_raw)
    c,l,beta,fit=local_refit(full_theta,Xf,y,epochs)
    p=np.clip((v.design(Xte,c,l)@beta).ravel(),1e-6,1-1e-6)
    return p,{"train_n":len(train),"inner_fit_n":split,"inner_check_n":ncheck,
              "population":POP,"generations":GENS,"seed":seed,
              "meta_check_brier":meta_check,"selected_local_epochs":epochs,
              "local_check_brier":local_check,**fit}

def main():
    df=v.read_panel()
    dev=df[(df.forecast_issue_date.dt.year.between(2022,2024)) & df.target_r3.notna()].copy().reset_index(drop=True)
    rows=[]; diags=[]
    for start in range(0,len(dev),BLOCK):
        te=dev.iloc[start:start+BLOCK].copy(); cutoff=te.feature_cutoff_date.min()
        tr=df[df.target_r3.notna() & df.target_end_date_h3.notna() &
              (df.target_end_date_h3<=cutoff) & (df.forecast_issue_date<pd.Timestamp("2025-01-01"))].copy()
        ph,diag=fit_predict_hybrid(tr,te,start//BLOCK)
        pl=v.fit_predict_logit(tr,te)
        diags.append({"block":start//BLOCK,"test_start":str(te.forecast_issue_date.min().date()),**diag})
        for r,p1,p0 in zip(te.itertuples(),ph,pl):
            rows.append({"feature_cutoff_date":str(r.feature_cutoff_date.date()),
                         "forecast_issue_date":str(r.forecast_issue_date.date()),
                         "target_end_date_h3":str(r.target_end_date_h3.date()),
                         "y_up":int(r.target_r3>0),"p_chhho_anfis":float(p1),"p_logit":float(p0)})
    led=pd.DataFrame(rows); led.to_csv(OUT/"anfis_chhho_dev_predictions.csv",index=False)
    pd.DataFrame(diags).to_csv(OUT/"anfis_chhho_fit_diagnostics.csv",index=False)
    mh=v.metrics(led.y_up,led.p_chhho_anfis); ml=v.metrics(led.y_up,led.p_logit)
    rel=(ml["brier"]-mh["brier"])/ml["brier"]
    led["year"]=pd.to_datetime(led.forecast_issue_date).dt.year
    annual=[]
    for yr,g in led.groupby("year"):
        a=v.metrics(g.y_up,g.p_chhho_anfis); l=v.metrics(g.y_up,g.p_logit)
        annual.append({"year":int(yr),**a,"logit_brier":l["brier"],
                       "relative_brier_improvement_vs_logit":float((l["brier"]-a["brier"])/l["brier"])})
    adf=pd.DataFrame(annual); adf.to_csv(OUT/"anfis_chhho_dev_annual.csv",index=False)
    nonneg=int((adf.relative_brier_improvement_vs_logit>=0).sum()); worst=float(adf.relative_brier_improvement_vs_logit.min())
    gate=bool(rel>=0.005 and mh["logloss"]<=ml["logloss"] and mh["prediction_std"]>=0.02 and nonneg>=2 and worst>=-0.02)
    summary={"model_id":"GLOBAL_XAU_DAILY_H3_CHHHO_ANFIS_V1","status":"PASS" if gate else "NOT_PROMOTED",
             "architecture":{"inputs":14,"rules":5,"membership":"Gaussian","consequent":"first_order_Sugeno_TSK_LSE",
                             "hybrid":"chaotic_initialization_plus_HHO_premise_optimization_plus_Jang_local_refinement",
                             "population":POP,"generations":GENS,"local_max_epochs":LOCAL_MAX},
             "dev_metrics":mh,"frozen_logit_metrics":ml,"relative_brier_improvement_vs_logit":rel,
             "annual":annual,"gate":{"pass":gate,"nonnegative_years":nonneg,"worst_year_relative":worst}}
    (OUT/"anfis_chhho_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    lines=["# GLOBAL XAU DAILY H3 — ChHHO-ANFIS V1","",
           f"**Status:** **{summary['status']}**","",
           "| Model | Brier | Log loss | Accuracy | Balanced acc | Pred SD |",
           "|---|---:|---:|---:|---:|---:|",
           f"| ChHHO-ANFIS | {mh['brier']:.6f} | {mh['logloss']:.6f} | {100*mh['accuracy']:.2f}% | {100*mh['balanced_accuracy']:.2f}% | {mh['prediction_std']:.4f} |",
           f"| Frozen Logistic L2 | {ml['brier']:.6f} | {ml['logloss']:.6f} | {100*ml['accuracy']:.2f}% | {100*ml['balanced_accuracy']:.2f}% | {ml['prediction_std']:.4f} |","",
           f"Relative Brier improvement vs Logistic: **{100*rel:.2f}%**.","",
           "## Annual","",
           "| Year | ChHHO Brier | Logistic Brier | Relative |","|---|---:|---:|---:|"]
    for r in adf.itertuples():
        lines.append(f"| {r.year} | {r.brier:.6f} | {r.logit_brier:.6f} | {100*r.relative_brier_improvement_vs_logit:.2f}% |")
    lines += ["",f"Challenger gate: **{gate}**.","",
              "2025/2026 were not used in this DEV decision."]
    (OUT/"ANFIS_CHHHO_RESULT.md").write_text("\n".join(lines)+"\n")
    print("ANFIS_CHHHO_SUMMARY="+json.dumps(summary,separators=(",",":")))
    print((OUT/"ANFIS_CHHHO_RESULT.md").read_text())

if __name__=="__main__": main()
