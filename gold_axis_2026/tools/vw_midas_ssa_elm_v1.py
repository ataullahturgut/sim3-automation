from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"

HIDDEN=16
ALPHA=1e-3

def act(z):
    return 1.0/(1.0+np.exp(-np.clip(z,-40,40)))

def arrays(samples,t):
    ks=sorted(k for k in samples if k<t)
    if len(ks)<30: raise RuntimeError(f"TRAIN_TOO_SMALL {t} n={len(ks)}")
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks]); tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def decode(theta,d=8,h=HIDDEN):
    n=d*h
    return theta[:n].reshape(d,h), theta[n:n+h]

def fit_beta(X,Y,W,b):
    H=act(X@W+b)
    A=H.T@H + ALPHA*np.eye(H.shape[1])
    B=H.T@Y
    try: beta=np.linalg.solve(A,B)
    except np.linalg.LinAlgError: beta=np.linalg.pinv(A)@B
    return beta

def fitness(theta,X,Y):
    n=len(X); nval=max(6,int(round(0.20*n))); split=n-nval
    Xtr,Ytr=X[:split],Y[:split]; Xv,Yv=X[split:],Y[split:]
    W,b=decode(theta)
    beta=fit_beta(Xtr,Ytr,W,b)
    pred=act(Xv@W+b)@beta
    mae_all=np.mean(np.abs(pred-Yv))
    mae_gold=np.mean(np.abs(pred[:,0]-Yv[:,0]))
    return float(0.7*mae_gold+0.3*mae_all)

def ssa_optimize(X,Y,seed,pop_size=24,iters=35,producer_ratio=0.2,aware_ratio=0.15,ST=0.8):
    rng=np.random.default_rng(seed)
    dim=8*HIDDEN+HIDDEN
    lo,hi=-2.0,2.0
    pop=rng.uniform(lo,hi,size=(pop_size,dim))
    fit=np.array([fitness(ind,X,Y) for ind in pop])

    n_prod=max(1,int(round(pop_size*producer_ratio)))
    n_aware=max(1,int(round(pop_size*aware_ratio)))
    eps=1e-12

    for t in range(1,iters+1):
        order=np.argsort(fit)
        best=pop[order[0]].copy(); best_fit=float(fit[order[0]])
        worst=pop[order[-1]].copy(); worst_fit=float(fit[order[-1]])

        # Producers: exploration under safe conditions, random walk under alarm
        R2=float(rng.random())
        for rank_idx,idx in enumerate(order[:n_prod],start=1):
            if R2 < ST:
                decay=np.exp(-rank_idx/(rng.uniform(0.2,1.0)*iters+eps))
                pop[idx]=pop[idx]*decay
            else:
                pop[idx]=pop[idx]+rng.normal(0,1,size=dim)
            pop[idx]=np.clip(pop[idx],lo,hi)

        # Scroungers: follow best or move away from worst
        for rank_idx,idx in enumerate(order[n_prod:],start=n_prod+1):
            if rank_idx > pop_size/2:
                q=float(rng.normal())
                step=np.exp(np.clip((worst-pop[idx])/((rank_idx**2)+eps),-10,10))
                pop[idx]=q*step
            else:
                signs=np.where(rng.random(dim)<0.5,-1.0,1.0)
                pop[idx]=best + np.abs(pop[idx]-best)*signs*rng.random(dim)
            pop[idx]=np.clip(pop[idx],lo,hi)

        # Danger-aware sparrows
        aware_idx=rng.choice(pop_size,size=n_aware,replace=False)
        current_fit=np.array([fitness(ind,X,Y) for ind in pop])
        best_i=int(np.argmin(current_fit)); best=pop[best_i].copy(); best_fit=float(current_fit[best_i])
        worst_i=int(np.argmax(current_fit)); worst=pop[worst_i].copy(); worst_fit=float(current_fit[worst_i])
        for idx in aware_idx:
            fi=float(current_fit[idx])
            if fi > best_fit:
                pop[idx]=best + rng.normal(0,1,size=dim)*np.abs(pop[idx]-best)
            else:
                K=float(rng.uniform(-1,1))
                pop[idx]=pop[idx] + K*np.abs(pop[idx]-worst)/(abs(fi-worst_fit)+eps)
            pop[idx]=np.clip(pop[idx],lo,hi)

        fit=np.array([fitness(ind,X,Y) for ind in pop])

    bi=int(np.argmin(fit))
    return pop[bi].copy(),float(fit[bi])

def predict(samples,t):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    theta,fit=ssa_optimize(X,Y,seed=7711+sum(map(ord,t)))
    W,b=decode(theta)
    beta=fit_beta(X,Y,W,b)
    p=(act(tx@W+b)@beta)[0]*ys+ym
    return p,len(ks),fit

def ev(b,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
        p,n,fit=predict(cache[t],t); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"train_rows":n,"ssa_inner_fitness":fit,
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
    out={"model_id":"VW_MIDAS_SSA_ELM_V1",
         "method":{"elm_hidden":HIDDEN,"activation":"sigmoid","ridge_alpha":ALPHA,
                   "ssa_scope":"hidden_input_weights_and_biases","population":24,"iterations":35,
                   "producer_ratio":0.2,"aware_ratio":0.15,"safety_threshold":0.8,
                   "fitness":"chronological_last20pct_training_only; 0.7*Gold_MAE + 0.3*all_outputs_MAE",
                   "bounds":"[-2,2]","seed":"deterministic_by_target"},
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "base_elm_architecture":"FROZEN_FROM_PRIOR_ELM_BASELINE_16_SIGMOID_ALPHA_0.001",
                      "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_ssa_elm_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
