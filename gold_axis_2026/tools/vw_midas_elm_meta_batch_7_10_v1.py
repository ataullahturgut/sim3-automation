from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"
HIDDEN=16; ALPHA=1e-3
DIM=8*HIDDEN+HIDDEN; LO,HI=-2.0,2.0

def act(z): return 1/(1+np.exp(-np.clip(z,-40,40)))

def arrays(samples,t):
    ks=sorted(k for k in samples if k<t)
    if len(ks)<30: raise RuntimeError(f"TRAIN_TOO_SMALL {t} n={len(ks)}")
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks]); tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def decode(theta):
    n=8*HIDDEN
    return theta[:n].reshape(8,HIDDEN),theta[n:n+HIDDEN]

def fit_beta(X,Y,W,b):
    H=act(X@W+b); A=H.T@H+ALPHA*np.eye(H.shape[1]); B=H.T@Y
    try: return np.linalg.solve(A,B)
    except np.linalg.LinAlgError: return np.linalg.pinv(A)@B

def fitness(theta,X,Y):
    n=len(X); nv=max(6,int(round(.2*n))); s=n-nv
    W,b=decode(theta)
    beta=fit_beta(X[:s],Y[:s],W,b)
    pred=act(X[s:]@W+b)@beta
    return float(.7*np.mean(np.abs(pred[:,0]-Y[s:,0]))+.3*np.mean(np.abs(pred-Y[s:])))

def aco(X,Y,seed,pop=24,iters=35):
    # Continuous ACO / ACOR-style archive sampling
    rng=np.random.default_rng(seed)
    archive=rng.uniform(LO,HI,(pop,DIM))
    fit=np.array([fitness(x,X,Y) for x in archive])
    elite_n=8; q=.35; xi=.85
    for _ in range(iters):
        order=np.argsort(fit); elite=archive[order[:elite_n]]; efit=fit[order[:elite_n]]
        ranks=np.arange(elite_n); w=np.exp(-(ranks**2)/(2*(q*elite_n)**2)); w/=w.sum()
        samples=[]
        for _j in range(pop):
            k=int(rng.choice(elite_n,p=w))
            sigma=xi*np.mean(np.abs(elite[k]-elite),axis=0)+1e-3
            samples.append(np.clip(elite[k]+rng.normal(0,1,DIM)*sigma,LO,HI))
        cand=np.stack(samples); cfit=np.array([fitness(x,X,Y) for x in cand])
        archive=np.vstack([elite,cand]); fit=np.concatenate([efit,cfit])
        keep=np.argsort(fit)[:pop]; archive=archive[keep]; fit=fit[keep]
    i=int(np.argmin(fit)); return archive[i],float(fit[i])

def bat(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed)
    x=rng.uniform(LO,HI,(pop,DIM)); v=np.zeros_like(x)
    fit=np.array([fitness(z,X,Y) for z in x]); i=int(np.argmin(fit)); best=x[i].copy(); bf=float(fit[i])
    A=np.full(pop,.9); pulse=np.full(pop,.5)
    for _ in range(iters):
        for i in range(pop):
            freq=2*rng.random()
            v[i]=v[i]+(x[i]-best)*freq
            cand=x[i]+v[i]
            if rng.random()>pulse[i]:
                cand=best+0.05*rng.normal(0,1,DIM)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i] and rng.random()<A[i]:
                x[i]=cand; fit[i]=cf; A[i]*=.97; pulse[i]=min(.95,pulse[i]+.01)
            if cf<bf:
                best=cand.copy(); bf=float(cf)
    return best,bf

def firefly(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed)
    x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    beta0=1.0; gamma=1.0/DIM; alpha=.25
    for _ in range(iters):
        order=np.argsort(fit); x=x[order]; fit=fit[order]
        for i in range(1,pop):
            for j in range(i):
                if fit[j] < fit[i]:
                    r2=np.mean((x[i]-x[j])**2)
                    beta=beta0*np.exp(-gamma*r2)
                    cand=x[i]+beta*(x[j]-x[i])+alpha*rng.normal(0,1,DIM)
                    cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
                    if cf<fit[i]: x[i]=cand; fit[i]=cf
        alpha*=.97
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def mfo(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed)
    moth=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in moth])
    flames=moth[np.argsort(fit)].copy(); ffit=np.sort(fit).copy()
    b=1.0
    for t in range(iters):
        flame_no=max(1,int(round(pop-(t*(pop-1)/max(1,iters-1)))))
        new=np.empty_like(moth)
        for i in range(pop):
            fidx=min(i,flame_no-1)
            flame=flames[fidx]
            dist=np.abs(flame-moth[i])
            l=rng.uniform(-1,1,DIM)
            new[i]=dist*np.exp(b*l)*np.cos(2*np.pi*l)+flame
        moth=np.clip(new,LO,HI); fit=np.array([fitness(z,X,Y) for z in moth])
        combined=np.vstack([flames,moth]); cfit=np.concatenate([ffit,fit])
        keep=np.argsort(cfit)[:pop]; flames=combined[keep].copy(); ffit=cfit[keep].copy()
    return flames[0],float(ffit[0])

OPTIMIZERS={"ACO":aco,"BAT":bat,"FA":firefly,"MFO":mfo}
SEED_BASE={"ACO":11711,"BAT":12711,"FA":13711,"MFO":14711}

def predict(samples,t,name):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    theta,fit=OPTIMIZERS[name](X,Y,seed=SEED_BASE[name]+sum(map(ord,t)))
    W,b=decode(theta); beta=fit_beta(X,Y,W,b)
    p=(act(tx@W+b)@beta)[0]*ys+ym
    return p,len(ks),fit

def ev(b,cache,a,z,name):
    rows=[]
    for t in base.month_range(a,z):
        p,n,fit=predict(cache[t],t,name); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"train_rows":n,"inner_fitness":fit,
                     "pred_log_return_gold":float(p[0]),
                     "forecast":float(b.core_gold[pm]*math.exp(float(p[0]))),
                     "actual":float(b.core_gold[t]),"rw":float(b.core_gold[pm])})
    return rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    out={"model_id":"VW_MIDAS_ELM_META_BATCH_7_10_V1",
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "base_elm_architecture":"FROZEN_16_SIGMOID_ALPHA_0.001",
                      "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
                      "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},"models":{}}
    for name in OPTIMIZERS:
        dev=ev(b,cache,DEV_START,DEV_END,name)
        tr=ev(b,cache,TR_START,TR_END,name)
        st=ev(b,cache,ST_START,ST_END,name)
        out["models"][name]={
            "dev":{"metrics":base.metrics(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st}}
        print(name,json.dumps({
            "dev":out["models"][name]["dev"]["metrics"],
            "transport_2025":out["models"][name]["transport_2025"]["metrics"],
            "stress_2026":out["models"][name]["stress_2026"]["metrics"]},sort_keys=True))
    Path("vw_midas_elm_meta_batch_7_10_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()
