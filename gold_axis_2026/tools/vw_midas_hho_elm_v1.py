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

def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/
           (math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,size=shape)
    v=rng.normal(0,1,size=shape)
    return u/(np.abs(v)**(1/beta)+1e-12)

def hho_optimize(X,Y,seed,pop_size=24,iters=35):
    rng=np.random.default_rng(seed)
    dim=8*HIDDEN+HIDDEN
    lo,hi=-2.0,2.0
    hawks=rng.uniform(lo,hi,size=(pop_size,dim))
    fit=np.array([fitness(h,X,Y) for h in hawks])
    bi=int(np.argmin(fit))
    rabbit=hawks[bi].copy(); rabbit_fit=float(fit[bi])

    for t in range(iters):
        E1=2*(1-(t/max(1,iters-1)))
        mean_h=np.mean(hawks,axis=0)
        new=np.empty_like(hawks)

        for i in range(pop_size):
            E0=2*float(rng.random())-1
            escaping=E1*E0
            q=float(rng.random())
            r=float(rng.random())

            if abs(escaping) >= 1:
                # Exploration
                if q < 0.5:
                    rand_h=hawks[int(rng.integers(0,pop_size))]
                    Xn=rand_h-rng.random(dim)*np.abs(rand_h-2*rng.random(dim)*hawks[i])
                else:
                    Xn=(rabbit-mean_h)-rng.random(dim)*(lo+rng.random(dim)*(hi-lo))
            else:
                # Exploitation
                J=2*(1-float(rng.random()))
                if r >= 0.5 and abs(escaping) >= 0.5:
                    # soft besiege
                    Xn=(rabbit-hawks[i])-escaping*np.abs(J*rabbit-hawks[i])
                elif r >= 0.5 and abs(escaping) < 0.5:
                    # hard besiege
                    Xn=rabbit-escaping*np.abs(rabbit-hawks[i])
                elif r < 0.5 and abs(escaping) >= 0.5:
                    # soft besiege with progressive rapid dives
                    Ypos=rabbit-escaping*np.abs(J*rabbit-hawks[i])
                    Zpos=Ypos+rng.random(dim)*levy(rng,(dim,))
                    Ypos=np.clip(Ypos,lo,hi); Zpos=np.clip(Zpos,lo,hi)
                    fy=fitness(Ypos,X,Y); fz=fitness(Zpos,X,Y); fi=fit[i]
                    Xn=Ypos if fy<min(fi,fz) else (Zpos if fz<fi else hawks[i])
                else:
                    # hard besiege with progressive rapid dives
                    Ypos=rabbit-escaping*np.abs(J*rabbit-mean_h)
                    Zpos=Ypos+rng.random(dim)*levy(rng,(dim,))
                    Ypos=np.clip(Ypos,lo,hi); Zpos=np.clip(Zpos,lo,hi)
                    fy=fitness(Ypos,X,Y); fz=fitness(Zpos,X,Y); fi=fit[i]
                    Xn=Ypos if fy<min(fi,fz) else (Zpos if fz<fi else hawks[i])

            new[i]=np.clip(Xn,lo,hi)

        hawks=new
        fit=np.array([fitness(h,X,Y) for h in hawks])
        bi=int(np.argmin(fit))
        if float(fit[bi])<rabbit_fit:
            rabbit_fit=float(fit[bi]); rabbit=hawks[bi].copy()

    return rabbit,rabbit_fit

def predict(samples,t):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    theta,fit=hho_optimize(X,Y,seed=10711+sum(map(ord,t)))
    W,b=decode(theta)
    beta=fit_beta(X,Y,W,b)
    p=(act(tx@W+b)@beta)[0]*ys+ym
    return p,len(ks),fit

def ev(b,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
        p,n,fit=predict(cache[t],t); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"train_rows":n,"hho_inner_fitness":fit,
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
    out={"model_id":"VW_MIDAS_HHO_ELM_V1",
         "method":{"elm_hidden":HIDDEN,"activation":"sigmoid","ridge_alpha":ALPHA,
                   "hho_scope":"hidden_input_weights_and_biases","population":24,"iterations":35,
                   "fitness":"chronological_last20pct_training_only; 0.7*Gold_MAE + 0.3*all_outputs_MAE",
                   "bounds":"[-2,2]","seed":"deterministic_by_target"},
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "base_elm_architecture":"FROZEN_FROM_PRIOR_ELM_BASELINE_16_SIGMOID_ALPHA_0.001",
                      "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_hho_elm_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
