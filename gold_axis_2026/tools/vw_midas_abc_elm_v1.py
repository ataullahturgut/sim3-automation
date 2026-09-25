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

def abc_optimize(X,Y,seed,colony=24,cycles=35,limit=12):
    rng=np.random.default_rng(seed)
    dim=8*HIDDEN+HIDDEN
    lo,hi=-2.0,2.0
    food_n=colony//2
    food=rng.uniform(lo,hi,size=(food_n,dim))
    fit=np.array([fitness(x,X,Y) for x in food])
    trials=np.zeros(food_n,dtype=int)

    def neighbor(i):
        k=i
        while k==i:
            k=int(rng.integers(0,food_n))
        j=int(rng.integers(0,dim))
        phi=float(rng.uniform(-1,1))
        v=food[i].copy()
        v[j]=food[i,j]+phi*(food[i,j]-food[k,j])
        v[j]=np.clip(v[j],lo,hi)
        return v

    for _ in range(cycles):
        # employed bees
        for i in range(food_n):
            v=neighbor(i); vf=fitness(v,X,Y)
            if vf<fit[i]:
                food[i]=v; fit[i]=vf; trials[i]=0
            else:
                trials[i]+=1

        # onlooker bees
        quality=1.0/(1.0+fit)
        probs=quality/quality.sum()
        for _b in range(food_n):
            i=int(rng.choice(food_n,p=probs))
            v=neighbor(i); vf=fitness(v,X,Y)
            if vf<fit[i]:
                food[i]=v; fit[i]=vf; trials[i]=0
            else:
                trials[i]+=1

        # scouts
        for i in range(food_n):
            if trials[i]>=limit:
                food[i]=rng.uniform(lo,hi,size=dim)
                fit[i]=fitness(food[i],X,Y)
                trials[i]=0

    bi=int(np.argmin(fit))
    return food[bi].copy(),float(fit[bi])

def predict(samples,t):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    theta,fit=abc_optimize(X,Y,seed=6711+sum(map(ord,t)))
    W,b=decode(theta)
    beta=fit_beta(X,Y,W,b)
    p=(act(tx@W+b)@beta)[0]*ys+ym
    return p,len(ks),fit

def ev(b,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
        p,n,fit=predict(cache[t],t); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"train_rows":n,"abc_inner_fitness":fit,
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
    out={"model_id":"VW_MIDAS_ABC_ELM_V1",
         "method":{"elm_hidden":HIDDEN,"activation":"sigmoid","ridge_alpha":ALPHA,
                   "abc_scope":"hidden_input_weights_and_biases","colony":24,"cycles":35,"limit":12,
                   "fitness":"chronological_last20pct_training_only; 0.7*Gold_MAE + 0.3*all_outputs_MAE",
                   "bounds":"[-2,2]","seed":"deterministic_by_target"},
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "base_elm_architecture":"FROZEN_FROM_PRIOR_ELM_BASELINE_16_SIGMOID_ALPHA_0.001",
                      "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_abc_elm_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
