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
    try:return np.linalg.solve(A,B)
    except np.linalg.LinAlgError:return np.linalg.pinv(A)@B
def fitness(theta,X,Y):
    n=len(X); nv=max(6,int(round(.2*n))); s=n-nv
    W,b=decode(theta); beta=fit_beta(X[:s],Y[:s],W,b)
    pred=act(X[s:]@W+b)@beta
    return float(.7*np.mean(np.abs(pred[:,0]-Y[s:,0]))+.3*np.mean(np.abs(pred-Y[s:])))

def hgs(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for t in range(iters):
        order=np.argsort(fit); best=x[order[0]].copy()
        worst=float(fit[order[-1]]); bestf=float(fit[order[0]])
        hunger=np.zeros(pop)
        span=max(1e-12,worst-bestf)
        for i in range(pop):
            hunger[i]=((fit[i]-bestf)/span)+rng.random()*0.1
        hnorm=hunger/(hunger.max()+1e-12)
        shrink=1-t/max(1,iters-1)
        for i in range(pop):
            r1=rng.random(DIM); r2=rng.random(DIM)
            W1=2*r1*shrink-1
            W2=2*r2*(1-hnorm[i])
            cand=x[i]*(1-rng.random()) + W1*np.abs(best-x[i]) + W2*best
            if rng.random()<0.03: cand=rng.uniform(LO,HI,DIM)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def choa(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for t in range(iters):
        order=np.argsort(fit)
        leaders=[x[order[k]].copy() for k in range(4)]
        f=2.5-2.0*t/max(1,iters-1)
        new=np.empty_like(x)
        for i in range(pop):
            cand=np.zeros(DIM)
            for leader in leaders:
                r1=rng.random(DIM); r2=rng.random(DIM)
                a=2*f*r1-f; c=2*r2
                d=np.abs(c*leader-x[i])
                cand += leader-a*d
            cand/=4.0
            if rng.random()<0.1:
                cand += 0.05*rng.normal(0,1,DIM)
            new[i]=np.clip(cand,LO,HI)
        x=new; fit=np.array([fitness(z,X,Y) for z in x])
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def hgso(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    H=rng.uniform(0.1,1.0,pop); C=rng.uniform(0.1,1.0,pop)
    for t in range(iters):
        best=x[int(np.argmin(fit))].copy()
        T=np.exp(-t/max(1,iters))
        for i in range(pop):
            H[i]=H[i]*np.exp(-C[i]*(1/T-1))
            gamma=np.exp(-(fit[i]-fit.min())/(abs(fit.max()-fit.min())+1e-12))
            direction=(best-x[i])
            cand=x[i]+rng.uniform(-1,1,DIM)*H[i]*direction + gamma*rng.normal(0,0.05,DIM)
            if rng.random()<0.1:
                cand += rng.uniform(-1,1,DIM)*(HI-LO)*0.02
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def aoa(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    alpha=5.0; mu=0.5
    for t in range(iters):
        best=x[int(np.argmin(fit))].copy()
        moa=0.2 + (1.0-0.2)*(t/max(1,iters-1))
        mop=1-(t/max(1,iters))**(1/alpha)
        for i in range(pop):
            r1,r2,r3=rng.random(),rng.random(),rng.random()
            if r1>moa:
                if r2<0.5:
                    cand=best/(mop+1e-12)*(mu*(HI-LO)+LO)
                else:
                    cand=best*mop*(mu*(HI-LO)+LO)
            else:
                if r3<0.5:
                    cand=best-mop*(mu*(HI-LO)+LO)
                else:
                    cand=best+mop*(mu*(HI-LO)+LO)
            cand=np.asarray(cand)
            if cand.ndim==0: cand=np.full(DIM,float(cand))
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def cpa(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for t in range(iters):
        best=x[int(np.argmin(fit))].copy()
        scale=1-t/max(1,iters-1)
        for i in range(pop):
            j=int(rng.integers(0,pop))
            if rng.random()<0.5:
                cand=x[i]+rng.random(DIM)*(best-x[i])+scale*rng.random(DIM)*(x[j]-x[i])
            else:
                cand=best+scale*rng.normal(0,1,DIM)*np.abs(best-x[i])
            if rng.random()<0.05: cand=rng.uniform(LO,HI,DIM)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

OPTIMIZERS={"HGS":hgs,"CHOA":choa,"HGSO":hgso,"AOA":aoa,"CPA":cpa}
SEEDS={k:25711+i*1000 for i,k in enumerate(OPTIMIZERS)}
def predict(samples,t,name):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    theta,fit=OPTIMIZERS[name](X,Y,SEEDS[name]+sum(map(ord,t)))
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
    out={"model_id":"VW_MIDAS_ELM_META_BATCH_21_25_V1",
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "base_elm_architecture":"FROZEN_16_SIGMOID_ALPHA_0.001",
                      "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
                      "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},"models":{}}
    for name in OPTIMIZERS:
        dev=ev(b,cache,DEV_START,DEV_END,name); tr=ev(b,cache,TR_START,TR_END,name); st=ev(b,cache,ST_START,ST_END,name)
        out["models"][name]={
            "dev":{"metrics":base.metrics(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st}}
        print(name,json.dumps({"dev":out["models"][name]["dev"]["metrics"],
                              "transport_2025":out["models"][name]["transport_2025"]["metrics"],
                              "stress_2026":out["models"][name]["stress_2026"]["metrics"]},sort_keys=True))
    Path("vw_midas_elm_meta_batch_21_25_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
