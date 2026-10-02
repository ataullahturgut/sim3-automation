from __future__ import annotations
import io, json, math, os, zipfile, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_anfis_vanilla_out")); OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5
RULES=5
MAX_EPOCHS=100
K0=.01; KINC=1.1; KDEC=.9
SFLOOR=.20; SCEIL=5.0
CHECK_FRAC=.20
CORE3=[
 "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
 "silver_r1","silver_r5","silver_r21","silver_age_days",
 "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"daily-anfis-vanilla"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_panel():
    z=get_zip(READINESS_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
    if len(names)!=1: raise RuntimeError(names)
    df=pd.read_csv(io.BytesIO(z.read(names[0])))
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        df[c]=pd.to_datetime(df[c])
    return df.sort_values("feature_cutoff_date").reset_index(drop=True)

def impute_fit(train,test):
    a=train[CORE3].apply(pd.to_numeric,errors="coerce").copy()
    b=test[CORE3].apply(pd.to_numeric,errors="coerce").copy()
    med=a.median()
    a=a.fillna(med).fillna(0.0); b=b.fillna(med).fillna(0.0)
    return a.to_numpy(float),b.to_numpy(float),med.to_dict()

def init_antecedents(X):
    km=KMeans(n_clusters=RULES,random_state=SEED,n_init=10,algorithm="lloyd")
    labels=km.fit_predict(X); c=km.cluster_centers_.copy()
    gs=np.std(X,axis=0,ddof=0); gs=np.where(gs<SFLOOR,1.0,gs)
    s=np.empty_like(c)
    for r in range(RULES):
        xr=X[labels==r]
        if len(xr)>=3: sr=np.std(xr,axis=0,ddof=0)
        else: sr=gs.copy()
        s[r]=np.clip(np.where(sr<1e-6,gs,sr),SFLOOR,SCEIL)
    return c,s,labels

def fire(X,c,l):
    s=np.exp(l)
    z=(X[:,None,:]-c[None,:,:])/s[None,:,:]
    a=-.5*np.sum(z*z,axis=2); a-=a.max(axis=1,keepdims=True)
    w=np.exp(a)
    return w/np.maximum(w.sum(axis=1,keepdims=True),1e-12)

def design(X,c,l):
    q=fire(X,c,l); b=np.c_[np.ones(len(X)),X]
    return (q[:,:,None]*b[:,None,:]).reshape(len(X),-1)

def lse(X,y,c,l):
    H=design(X,c,l)
    return np.linalg.lstsq(H,y.reshape(-1,1),rcond=1e-6)[0]

def rule_outputs(X,beta):
    d=X.shape[1]+1
    b=beta.reshape(RULES,d,1)
    a=np.c_[np.ones(len(X)),X]
    return np.einsum("nd,rdo->nro",a,b)

def loss_grad(X,y,c,l,beta):
    Y=y.reshape(-1,1)
    q=fire(X,c,l); fr=rule_outputs(X,beta); yh=(q[:,:,None]*fr).sum(axis=1)
    e=yh-Y; loss=float(np.mean(e*e))
    infl=(2/len(X))*np.einsum("no,nro->nr",e,q[:,:,None]*(fr-yh[:,None,:]))
    s=np.exp(l); d=X[:,None,:]-c[None,:,:]
    gc=np.einsum("nr,nrd->rd",infl,d/(s[None,:,:]**2))
    gl=np.einsum("nr,nrd->rd",infl,(d*d)/(s[None,:,:]**2))
    return loss,gc,gl

def run_epochs(X,y,epochs,Xcheck=None,ycheck=None):
    c,s,labels=init_antecedents(X); l=np.log(np.clip(s,SFLOOR,SCEIL))
    k=K0; hist=[]; best=(math.inf,1)
    for ep in range(epochs):
        beta=lse(X,y,c,l)
        loss,gc,gl=loss_grad(X,y,c,l,beta)
        hist.append(loss)
        if Xcheck is not None:
            p=np.clip((design(Xcheck,c,l)@beta).ravel(),1e-6,1-1e-6)
            chk=float(np.mean((p-ycheck)**2))
            if chk<best[0]-1e-12: best=(chk,ep+1)
        g=np.r_[gc.ravel(),gl.ravel()]; gn=float(np.linalg.norm(g))
        if np.isfinite(gn) and gn>1e-15:
            eta=k/gn; c-=eta*gc; l-=eta*gl
            l=np.clip(l,math.log(SFLOOR),math.log(SCEIL))
        if len(hist)>=5:
            d=np.diff(hist[-5:]); sg=np.sign(d)
            if np.all(d<0): k*=KINC
            elif np.all(sg[:-1]*sg[1:]<0): k*=KDEC
    beta=lse(X,y,c,l)
    return c,l,beta,labels,{"first_train_brier":hist[0],"last_train_brier":hist[-1],
                             "best_check_brier":best[0],"best_check_epoch":best[1]}

def fit_predict_anfis(train,test):
    Xraw,Xtest_raw,med=impute_fit(train,test); y=(train.target_r3.to_numpy(float)>0).astype(float)
    ncheck=max(60,int(round(CHECK_FRAC*len(train))))
    split=len(train)-ncheck
    if split<500: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL {split}")
    scaler=StandardScaler().fit(Xraw[:split])
    Xfit=scaler.transform(Xraw[:split]); Xcheck=scaler.transform(Xraw[split:])
    _,_,_,_,sel=run_epochs(Xfit,y[:split],MAX_EPOCHS,Xcheck,y[split:])
    chosen=int(sel["best_check_epoch"])
    scaler_full=StandardScaler().fit(Xraw)
    Xfull=scaler_full.transform(Xraw); Xtest=scaler_full.transform(Xtest_raw)
    c,l,beta,labels,fit=run_epochs(Xfull,y,chosen)
    p=np.clip((design(Xtest,c,l)@beta).ravel(),1e-6,1-1e-6)
    diag={"train_n":len(train),"inner_fit_n":split,"inner_check_n":ncheck,"selected_epochs":chosen,
          "best_check_brier":float(sel["best_check_brier"]),"refit_first_brier":float(fit["first_train_brier"]),
          "refit_last_brier":float(fit["last_train_brier"]),
          "rule_counts":[int((labels==r).sum()) for r in range(RULES)]}
    return p,diag

def fit_predict_logit(train,test):
    Xtr,Xte,_=impute_fit(train,test); y=(train.target_r3.to_numpy(float)>0).astype(int)
    m=Pipeline([("scale",StandardScaler()),("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED))])
    m.fit(Xtr,y)
    return m.predict_proba(Xte)[:,1]

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pred=(p>=.5).astype(int)
    return {"n":int(len(y)),"brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,p,labels=[0,1])),
            "accuracy":float(np.mean(pred==y)),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),
            "prediction_std":float(np.std(p)),"mean_prediction":float(np.mean(p)),"actual_up_rate":float(np.mean(y))}

def main():
    df=read_panel()
    dev=df[(df.forecast_issue_date.dt.year.between(2022,2024)) & df.target_r3.notna()].copy().reset_index(drop=True)
    rows=[]; block_diags=[]
    for start in range(0,len(dev),BLOCK):
        te=dev.iloc[start:start+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=df[df.target_r3.notna() & df.target_end_date_h3.notna() &
              (df.target_end_date_h3<=cutoff) & (df.forecast_issue_date<pd.Timestamp("2025-01-01"))].copy()
        pa,diag=fit_predict_anfis(tr,te)
        pl=fit_predict_logit(tr,te)
        block_diags.append({"block":start//BLOCK,"test_start":str(te.forecast_issue_date.min().date()),**diag})
        for r,p1,p0 in zip(te.itertuples(),pa,pl):
            y=int(r.target_r3>0)
            rows.append({"feature_cutoff_date":str(r.feature_cutoff_date.date()),
                         "forecast_issue_date":str(r.forecast_issue_date.date()),
                         "target_end_date_h3":str(r.target_end_date_h3.date()),
                         "y_up":y,"p_anfis":float(p1),"p_logit":float(p0)})
    led=pd.DataFrame(rows); led.to_csv(OUT/"anfis_vanilla_dev_predictions.csv",index=False)
    pd.DataFrame(block_diags).to_csv(OUT/"anfis_vanilla_fit_diagnostics.csv",index=False)
    ma=metrics(led.y_up,led.p_anfis); ml=metrics(led.y_up,led.p_logit)
    rel=(ml["brier"]-ma["brier"])/ml["brier"]
    annual=[]
    led["year"]=pd.to_datetime(led.forecast_issue_date).dt.year
    for yr,g in led.groupby("year"):
        a=metrics(g.y_up,g.p_anfis); l=metrics(g.y_up,g.p_logit)
        annual.append({"year":int(yr),**a,"logit_brier":l["brier"],
                       "relative_brier_improvement_vs_logit":float((l["brier"]-a["brier"])/l["brier"])})
    adf=pd.DataFrame(annual); adf.to_csv(OUT/"anfis_vanilla_dev_annual.csv",index=False)
    nonneg=int((adf.relative_brier_improvement_vs_logit>=0).sum())
    worst=float(adf.relative_brier_improvement_vs_logit.min())
    gate=bool(rel>=0.005 and ma["logloss"]<=ml["logloss"] and ma["prediction_std"]>=0.02 and nonneg>=2 and worst>=-0.02)
    summary={"model_id":"GLOBAL_XAU_DAILY_H3_VANILLA_ANFIS_V1","status":"PASS" if gate else "NOT_PROMOTED",
             "architecture":{"inputs":14,"rules":5,"membership":"Gaussian","consequent":"first_order_Sugeno_TSK_LSE",
                             "premise_learning":"Jang_normalized_gradient","max_epochs":MAX_EPOCHS,
                             "checking":"chronological_last_20pct_min60","metaheuristic":"NONE"},
             "dev_metrics":ma,"frozen_logit_metrics":ml,"relative_brier_improvement_vs_logit":rel,
             "annual":annual,"gate":{"pass":gate,"nonnegative_years":nonneg,"worst_year_relative":worst}}
    (OUT/"anfis_vanilla_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    lines=["# GLOBAL XAU DAILY H3 — Vanilla ANFIS V1","",
           f"**Status:** **{summary['status']}**","",
           "| Model | Brier | Log loss | Accuracy | Balanced acc | Pred SD |",
           "|---|---:|---:|---:|---:|---:|",
           f"| Vanilla ANFIS | {ma['brier']:.6f} | {ma['logloss']:.6f} | {100*ma['accuracy']:.2f}% | {100*ma['balanced_accuracy']:.2f}% | {ma['prediction_std']:.4f} |",
           f"| Frozen Logistic L2 | {ml['brier']:.6f} | {ml['logloss']:.6f} | {100*ml['accuracy']:.2f}% | {100*ml['balanced_accuracy']:.2f}% | {ml['prediction_std']:.4f} |","",
           f"Relative Brier improvement vs Logistic: **{100*rel:.2f}%**.","",
           "## Annual","",
           "| Year | ANFIS Brier | Logistic Brier | Relative |","|---|---:|---:|---:|"]
    for r in adf.itertuples():
        lines.append(f"| {r.year} | {r.brier:.6f} | {r.logit_brier:.6f} | {100*r.relative_brier_improvement_vs_logit:.2f}% |")
    lines += ["",f"Challenger gate: **{gate}**.","",
              "2025/2026 were not used in this DEV decision."]
    (OUT/"ANFIS_VANILLA_RESULT.md").write_text("\n".join(lines)+"\n")
    print("ANFIS_VANILLA_SUMMARY="+json.dumps(summary,separators=(",",":")))
    print((OUT/"ANFIS_VANILLA_RESULT.md").read_text())

if __name__=="__main__": main()
