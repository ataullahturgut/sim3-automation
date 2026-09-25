from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"

HIDDEN_GRID=[12,16,24]
ALPHA_GRID=[1e-4,1e-3,1e-2]
POP=18
ITERS=35
LO,HI=-2.0,2.0

def act(z): return 1/(1+np.exp(-np.clip(z,-40,40)))

def arrays(samples,t):
    ks=sorted(k for k in samples if k<t)
    if len(ks)<30: raise RuntimeError(f"TRAIN_TOO_SMALL {t} n={len(ks)}")
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks]); tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def decode(theta,h):
    n=8*h
    return theta[:n].reshape(8,h),theta[n:n+h]

def fit_beta(X,Y,W,b,alpha):
    H=act(X@W+b); A=H.T@H+alpha*np.eye(H.shape[1]); B=H.T@Y
    try:return np.linalg.solve(A,B)
    except np.linalg.LinAlgError:return np.linalg.pinv(A)@B

def inner_split(X,Y):
    n=len(X); nv=max(6,int(round(.2*n))); s=n-nv
    return X[:s],Y[:s],X[s:],Y[s:]

def fitness(theta,X,Y,h,alpha):
    Xtr,Ytr,Xv,Yv=inner_split(X,Y)
    W,b=decode(theta,h); beta=fit_beta(Xtr,Ytr,W,b,alpha)
    pred=act(Xv@W+b)@beta
    return float(.7*np.mean(np.abs(pred[:,0]-Yv[:,0]))+.3*np.mean(np.abs(pred-Yv)))

def adaptive_pso_optimize(X,Y,h,alpha,seed,pop=POP,iters=ITERS):
    rng=np.random.default_rng(seed)
    dim=8*h+h
    x=rng.uniform(LO,HI,(pop,dim))
    v=np.zeros_like(x)
    fit=np.array([fitness(z,X,Y,h,alpha) for z in x])
    pbest=x.copy(); pfit=fit.copy()
    gi=int(np.argmin(pfit)); gbest=pbest[gi].copy(); gfit=float(pfit[gi])
    vmax=0.4*(HI-LO)
    for t in range(iters):
        tau=t/max(1,iters-1)
        # adaptive schedules: exploration -> exploitation
        w=0.9-0.5*tau
        c1=2.5-2.0*tau
        c2=0.5+2.0*tau
        for i in range(pop):
            r1=rng.random(dim); r2=rng.random(dim)
            v[i]=w*v[i]+c1*r1*(pbest[i]-x[i])+c2*r2*(gbest-x[i])
            v[i]=np.clip(v[i],-vmax,vmax)
            x[i]=np.clip(x[i]+v[i],LO,HI)
            cf=fitness(x[i],X,Y,h,alpha)
            if cf<pfit[i]:
                pbest[i]=x[i].copy(); pfit[i]=cf
                if cf<gfit:
                    gfit=float(cf); gbest=x[i].copy()
    return gbest,gfit

def tune_structure(X,Y,target_seed):
    best=None
    for h in HIDDEN_GRID:
        for alpha in ALPHA_GRID:
            theta,score=adaptive_pso_optimize(X,Y,h,alpha,seed=target_seed+100*h+int(round(-math.log10(alpha))))
            cand=(score,h,alpha,theta)
            if best is None or score<best[0]: best=cand
    return best

def predict(samples,t):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    score,h,alpha,theta=tune_structure(X,Y,seed_base(t))
    W,b=decode(theta,h); beta=fit_beta(X,Y,W,b,alpha)
    p=(act(tx@W+b)@beta)[0]*ys+ym
    return p,len(ks),score,h,alpha

def seed_base(t): return 40711+sum(map(ord,t))

def ev(b,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
        p,n,score,h,alpha=predict(cache[t],t); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"train_rows":n,"inner_fitness":score,
                     "selected_hidden":h,"selected_alpha":alpha,
                     "pred_log_return_gold":float(p[0]),
                     "forecast":float(b.core_gold[pm]*math.exp(float(p[0]))),
                     "actual":float(b.core_gold[t]),"rw":float(b.core_gold[pm])})
    return rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=ev(b,cache,DEV_START,DEV_END)
    tr=ev(b,cache,TR_START,TR_END)
    st=ev(b,cache,ST_START,ST_END)
    out={"model_id":"VW_MIDAS_ADAPTIVE_PSO_ELM_V1",
         "method":{"pso":"adaptive inertia and acceleration schedules",
                   "w_schedule":"0.9 -> 0.4","c1_schedule":"2.5 -> 0.5","c2_schedule":"0.5 -> 2.5",
                   "velocity_limit":"0.4*(hi-lo)","population":POP,"iterations":ITERS,
                   "hidden_grid":HIDDEN_GRID,"alpha_grid":ALPHA_GRID,
                   "structure_selection":"training-only chronological inner tail",
                   "fitness":"0.7*Gold standardized MAE + 0.3*all-output standardized MAE"},
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
                      "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_adaptive_pso_elm_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
