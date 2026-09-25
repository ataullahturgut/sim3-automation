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

def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/(math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,shape); v=rng.normal(0,1,shape)
    return u/(np.abs(v)**(1/beta)+1e-12)

def fpa(X,Y,seed,pop=24,iters=35,p=0.8):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for _ in range(iters):
        bi=int(np.argmin(fit)); best=x[bi].copy()
        for i in range(pop):
            if rng.random()<p:
                step=0.01*levy(rng,(DIM,))
                cand=x[i]+step*(best-x[i])
            else:
                j,k=rng.choice(pop,2,replace=False); eps=rng.random()
                cand=x[i]+eps*(x[j]-x[k])
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def fa_fpa(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    beta0=1.0; gamma=1.0/DIM; alpha=.2
    for t in range(iters):
        order=np.argsort(fit); best=x[order[0]].copy()
        # firefly half-step
        for i in range(1,pop):
            j=int(order[rng.integers(0,max(1,pop//3))])
            r2=np.mean((x[i]-x[j])**2); beta=beta0*np.exp(-gamma*r2)
            cand=x[i]+beta*(x[j]-x[i])+alpha*rng.normal(0,1,DIM)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
        # FPA diversification
        for i in range(pop):
            if rng.random()<.75:
                cand=x[i]+0.01*levy(rng,(DIM,))*(best-x[i])
            else:
                j,k=rng.choice(pop,2,replace=False); cand=x[i]+rng.random()*(x[j]-x[k])
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
        alpha*=.97
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def cuckoo(X,Y,seed,pop=24,iters=35,pa=.25):
    rng=np.random.default_rng(seed); nests=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in nests])
    for _ in range(iters):
        bi=int(np.argmin(fit)); best=nests[bi].copy()
        for i in range(pop):
            cand=nests[i]+0.01*levy(rng,(DIM,))*(nests[i]-best)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            j=int(rng.integers(0,pop))
            if cf<fit[j]: nests[j]=cand; fit[j]=cf
        abandon=rng.random(pop)<pa
        for i in np.where(abandon)[0]:
            j,k=rng.choice(pop,2,replace=False)
            cand=nests[i]+rng.random(DIM)*(nests[j]-nests[k])
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: nests[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return nests[i],float(fit[i])

def sca(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for t in range(iters):
        best=x[int(np.argmin(fit))].copy(); r1=2-2*t/max(1,iters-1)
        for i in range(pop):
            r2=2*np.pi*rng.random(DIM); r3=2*rng.random(DIM); r4=rng.random(DIM)
            trig=np.where(r4<.5,np.sin(r2),np.cos(r2))
            cand=x[i]+r1*trig*np.abs(r3*best-x[i])
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def salp(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for t in range(iters):
        food=x[int(np.argmin(fit))].copy()
        c1=2*np.exp(-((4*t/max(1,iters))**2))
        new=x.copy()
        # leader
        c2=rng.random(DIM); c3=rng.random(DIM)
        step=((HI-LO)*c2+LO)
        new[0]=food+np.where(c3<.5,1,-1)*c1*step
        # followers
        for i in range(1,pop): new[i]=0.5*(x[i]+new[i-1])
        new=np.clip(new,LO,HI); nfit=np.array([fitness(z,X,Y) for z in new])
        improve=nfit<fit; x[improve]=new[improve]; fit[improve]=nfit[improve]
    i=int(np.argmin(fit)); return x[i],float(fit[i])

OPTIMIZERS={"FPA":fpa,"FA_FPA":fa_fpa,"CS":cuckoo,"SCA":sca,"SALP":salp}
SEEDS={k:15711+i*1000 for i,k in enumerate(OPTIMIZERS)}

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
    out={"model_id":"VW_MIDAS_ELM_META_BATCH_11_15_V1",
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
    Path("vw_midas_elm_meta_batch_11_15_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
