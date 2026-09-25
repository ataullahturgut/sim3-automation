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

def sma(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for t in range(iters):
        order=np.argsort(fit); best=x[order[0]].copy(); worst=x[order[-1]].copy()
        fbest,fworst=fit[order[0]],fit[order[-1]]
        W=np.ones((pop,DIM))
        for rank,idx in enumerate(order):
            ratio=(fbest-fit[idx])/(fbest-fworst+1e-12)
            r=rng.random(DIM)
            if rank<pop/2: W[idx]=1+r*np.log10(abs(ratio)+1)
            else: W[idx]=1-r*np.log10(abs(ratio)+1)
        a=np.arctanh(max(1e-6,1-(t+1)/iters))
        b=1-(t+1)/iters
        new=np.empty_like(x)
        for i in range(pop):
            if rng.random()<0.03:
                new[i]=rng.uniform(LO,HI,DIM)
            else:
                p=np.tanh(abs(fit[i]-fbest))
                vb=rng.uniform(-a,a,DIM); vc=rng.uniform(-b,b,DIM)
                A,B=rng.choice(pop,2,replace=False)
                if rng.random()<p:
                    new[i]=best+vb*(W[i]*x[A]-x[B])
                else:
                    new[i]=vc*x[i]
        x=np.clip(new,LO,HI); fit=np.array([fitness(z,X,Y) for z in x])
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def goa(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    cmax,cmin=1.0,0.00004
    for t in range(iters):
        best=x[int(np.argmin(fit))].copy()
        c=cmax-(cmax-cmin)*t/max(1,iters-1)
        new=np.empty_like(x)
        for i in range(pop):
            ssum=np.zeros(DIM)
            for j in range(pop):
                if i==j: continue
                dist=np.linalg.norm(x[j]-x[i])+1e-12
                dij=2+np.mod(dist,2)
                s=0.5*np.exp(-dij/1.5)-np.exp(-dij)
                ssum += ((x[j]-x[i])/dist)*s
            new[i]=c*ssum+best
        x=np.clip(new,LO,HI); fit=np.array([fitness(z,X,Y) for z in x])
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def alo(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); ants=rng.uniform(LO,HI,(pop,DIM)); antlions=rng.uniform(LO,HI,(pop,DIM))
    afit=np.array([fitness(z,X,Y) for z in ants]); lfit=np.array([fitness(z,X,Y) for z in antlions])
    elite=antlions[int(np.argmin(lfit))].copy(); elite_fit=float(np.min(lfit))
    for t in range(iters):
        quality=1/(1+lfit); probs=quality/quality.sum()
        shrink=1+10*(t/max(1,iters-1))
        for i in range(pop):
            sel=int(rng.choice(pop,p=probs))
            center=(antlions[sel]+elite)/2
            radius=(HI-LO)/shrink
            ants[i]=np.clip(center+rng.uniform(-1,1,DIM)*radius,LO,HI)
        afit=np.array([fitness(z,X,Y) for z in ants])
        combined=np.vstack([antlions,ants]); cfit=np.concatenate([lfit,afit])
        keep=np.argsort(cfit)[:pop]; antlions=combined[keep]; lfit=cfit[keep]
        if float(lfit[0])<elite_fit: elite_fit=float(lfit[0]); elite=antlions[0].copy()
    return elite,elite_fit

def tlbo(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for _ in range(iters):
        teacher=x[int(np.argmin(fit))].copy(); mean=x.mean(0); TF=int(rng.integers(1,3))
        for i in range(pop):
            cand=x[i]+rng.random(DIM)*(teacher-TF*mean)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
        for i in range(pop):
            j=i
            while j==i: j=int(rng.integers(0,pop))
            direction=(x[i]-x[j]) if fit[i]<fit[j] else (x[j]-x[i])
            cand=x[i]+rng.random(DIM)*direction
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def jaya(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    for _ in range(iters):
        best=x[int(np.argmin(fit))].copy(); worst=x[int(np.argmax(fit))].copy()
        for i in range(pop):
            r1=rng.random(DIM); r2=rng.random(DIM)
            cand=x[i]+r1*(best-np.abs(x[i]))-r2*(worst-np.abs(x[i]))
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
    i=int(np.argmin(fit)); return x[i],float(fit[i])

OPTIMIZERS={"SMA":sma,"GOA":goa,"ALO":alo,"TLBO":tlbo,"JAYA":jaya}
SEEDS={k:20711+i*1000 for i,k in enumerate(OPTIMIZERS)}
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
    out={"model_id":"VW_MIDAS_ELM_META_BATCH_16_20_V1",
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
    Path("vw_midas_elm_meta_batch_16_20_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
