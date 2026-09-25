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

def krill(X,Y,seed,pop=24,iters=35):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    N=np.zeros_like(x); F=np.zeros_like(x)
    dt=0.5
    for t in range(iters):
        order=np.argsort(fit); best=x[order[0]].copy(); worst=x[order[-1]].copy()
        fbest=float(fit[order[0]]); fworst=float(fit[order[-1]])
        new=np.empty_like(x)
        for i in range(pop):
            d=np.linalg.norm(x-x[i],axis=1)
            neigh=np.argsort(d)[1:min(5,pop)]
            local=np.mean(x[neigh],axis=0) if len(neigh) else best
            alpha_local=(local-x[i])
            alpha_target=(best-x[i])
            N[i]=0.6*N[i]+0.8*(alpha_local+alpha_target)
            beta_food=(best-x[i])*(1-t/max(1,iters-1))
            F[i]=0.5*F[i]+0.8*beta_food
            diffusion=0.01*(1-t/max(1,iters))*rng.normal(0,1,DIM)
            cand=x[i]+dt*(N[i]+F[i])+diffusion
            if rng.random()<0.05:
                cand += rng.uniform(-1,1,DIM)*0.05*(HI-LO)
            new[i]=np.clip(cand,LO,HI)
        x=new; fit=np.array([fitness(z,X,Y) for z in x])
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def crow(X,Y,seed,pop=24,iters=35,fl=2.0,ap=0.1):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); mem=x.copy()
    fit=np.array([fitness(z,X,Y) for z in x]); mfit=fit.copy()
    for _ in range(iters):
        for i in range(pop):
            j=i
            while j==i: j=int(rng.integers(0,pop))
            if rng.random()>ap:
                cand=x[i]+rng.random(DIM)*fl*(mem[j]-x[i])
            else:
                cand=rng.uniform(LO,HI,DIM)
            cand=np.clip(cand,LO,HI); cf=fitness(cand,X,Y)
            x[i]=cand; fit[i]=cf
            if cf<mfit[i]: mem[i]=cand; mfit[i]=cf
    i=int(np.argmin(mfit)); return mem[i],float(mfit[i])

def de_abc(X,Y,seed,pop=24,iters=35,F=.7,CR=.9,limit=10):
    rng=np.random.default_rng(seed); x=rng.uniform(LO,HI,(pop,DIM)); fit=np.array([fitness(z,X,Y) for z in x])
    trials=np.zeros(pop,dtype=int)
    for _ in range(iters):
        # DE phase
        for i in range(pop):
            idx=[j for j in range(pop) if j!=i]
            a,b,c=rng.choice(idx,3,replace=False)
            mutant=np.clip(x[a]+F*(x[b]-x[c]),LO,HI)
            mask=rng.random(DIM)<CR; mask[rng.integers(0,DIM)]=True
            cand=np.where(mask,mutant,x[i]); cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf; trials[i]=0
            else: trials[i]+=1
        # ABC phase
        q=1/(1+fit); probs=q/q.sum()
        for _b in range(pop):
            i=int(rng.choice(pop,p=probs)); k=i
            while k==i:k=int(rng.integers(0,pop))
            j=int(rng.integers(0,DIM)); phi=rng.uniform(-1,1)
            cand=x[i].copy(); cand[j]=x[i,j]+phi*(x[i,j]-x[k,j]); cand=np.clip(cand,LO,HI)
            cf=fitness(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf; trials[i]=0
            else: trials[i]+=1
        for i in range(pop):
            if trials[i]>=limit:
                x[i]=rng.uniform(LO,HI,DIM); fit[i]=fitness(x[i],X,Y); trials[i]=0
    i=int(np.argmin(fit)); return x[i],float(fit[i])

def multiswarm(X,Y,seed,pop=24,iters=35,swarms=3):
    rng=np.random.default_rng(seed)
    per=pop//swarms
    xs=[rng.uniform(LO,HI,(per,DIM)) for _ in range(swarms)]
    fits=[np.array([fitness(z,X,Y) for z in sw]) for sw in xs]
    vel=[np.zeros_like(sw) for sw in xs]
    pbest=[sw.copy() for sw in xs]; pfit=[f.copy() for f in fits]
    for t in range(iters):
        gbests=[]; gfits=[]
        for s in range(swarms):
            i=int(np.argmin(pfit[s])); gbests.append(pbest[s][i].copy()); gfits.append(float(pfit[s][i]))
        global_best=gbests[int(np.argmin(gfits))].copy()
        w=0.9-0.5*t/max(1,iters-1)
        for s in range(swarms):
            for i in range(per):
                r1=rng.random(DIM); r2=rng.random(DIM); r3=rng.random(DIM)
                vel[s][i]=w*vel[s][i]+1.4*r1*(pbest[s][i]-xs[s][i])+1.2*r2*(gbests[s]-xs[s][i])+0.4*r3*(global_best-xs[s][i])
                xs[s][i]=np.clip(xs[s][i]+vel[s][i],LO,HI)
                cf=fitness(xs[s][i],X,Y)
                if cf<pfit[s][i]: pbest[s][i]=xs[s][i].copy(); pfit[s][i]=cf
        if (t+1)%10==0:
            # exchange elites
            order=np.argsort(gfits)
            src=gbests[order[0]].copy()
            for s in order[1:]:
                wi=int(np.argmax(pfit[s]))
                xs[s][wi]=np.clip(src+rng.normal(0,.05,DIM),LO,HI)
                pbest[s][wi]=xs[s][wi].copy(); pfit[s][wi]=fitness(xs[s][wi],X,Y)
    allb=[]; allf=[]
    for s in range(swarms):
        i=int(np.argmin(pfit[s])); allb.append(pbest[s][i]); allf.append(float(pfit[s][i]))
    j=int(np.argmin(allf)); return allb[j],allf[j]

OPTIMIZERS={"KRILL":krill,"CROW":crow,"DE_ABC":de_abc,"MULTISWARM":multiswarm}
SEEDS={k:30711+i*1000 for i,k in enumerate(OPTIMIZERS)}
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
    out={"model_id":"VW_MIDAS_ELM_META_BATCH_26_29_V1",
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
    Path("vw_midas_elm_meta_batch_26_29_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
