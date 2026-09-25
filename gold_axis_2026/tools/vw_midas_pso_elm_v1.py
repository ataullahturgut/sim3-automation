from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"

HIDDEN=16
ACTIVATION="sigmoid"
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
    W=theta[:n].reshape(d,h)
    b=theta[n:n+h]
    return W,b

def fit_beta(X,Y,W,b,alpha=ALPHA):
    H=act(X@W+b)
    A=H.T@H + alpha*np.eye(H.shape[1])
    B=H.T@Y
    try: beta=np.linalg.solve(A,B)
    except np.linalg.LinAlgError: beta=np.linalg.pinv(A)@B
    return beta

def validation_fitness(theta,X,Y):
    # Chronological inner holdout only from training history.
    n=len(X); nval=max(6,int(round(0.20*n))); split=n-nval
    Xtr,Ytr=X[:split],Y[:split]; Xv,Yv=X[split:],Y[split:]
    W,b=decode(theta)
    beta=fit_beta(Xtr,Ytr,W,b)
    pred=act(Xv@W+b)@beta
    # Gold-centered but preserve four-output multi-target structure.
    mae_all=np.mean(np.abs(pred-Yv))
    mae_gold=np.mean(np.abs(pred[:,0]-Yv[:,0]))
    return float(0.7*mae_gold + 0.3*mae_all)

def pso_optimize(X,Y,seed,swarm=18,iters=35):
    rng=np.random.default_rng(seed)
    dim=8*HIDDEN+HIDDEN
    lo,hi=-2.0,2.0
    pos=rng.uniform(lo,hi,size=(swarm,dim))
    vel=rng.normal(0,0.15,size=(swarm,dim))
    pbest=pos.copy()
    pfit=np.array([validation_fitness(p,X,Y) for p in pos])
    gi=int(np.argmin(pfit)); gbest=pbest[gi].copy(); gfit=float(pfit[gi])
    w=0.72; c1=1.45; c2=1.45
    for _ in range(iters):
        r1=rng.random((swarm,dim)); r2=rng.random((swarm,dim))
        vel=w*vel + c1*r1*(pbest-pos) + c2*r2*(gbest-pos)
        vel=np.clip(vel,-0.6,0.6)
        pos=np.clip(pos+vel,lo,hi)
        fit=np.array([validation_fitness(p,X,Y) for p in pos])
        imp=fit<pfit
        if np.any(imp):
            pbest[imp]=pos[imp]; pfit[imp]=fit[imp]
        gi=int(np.argmin(pfit))
        if float(pfit[gi])<gfit:
            gfit=float(pfit[gi]); gbest=pbest[gi].copy()
    return gbest,gfit

def predict(samples,t):
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    theta,fit=pso_optimize(X,Y,seed=2711+sum(map(ord,t)))
    W,b=decode(theta)
    beta=fit_beta(X,Y,W,b)
    p=(act(tx@W+b)@beta)[0]*ys+ym
    return p,len(ks),fit

def ev(b,cache,a,z):
    rows=[]; errs=[]
    for t in base.month_range(a,z):
        p,n,fit=predict(cache[t],t); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"train_rows":n,"pso_inner_fitness":fit,
                     "pred_log_return_gold":float(p[0]),
                     "forecast":float(b.core_gold[pm]*math.exp(float(p[0]))),
                     "actual":float(b.core_gold[t]),"rw":float(b.core_gold[pm])})
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][pm]); errs.append(abs(float(p[0])-ar))
    return float(np.mean(errs)),rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    _,dev=ev(b,cache,DEV_START,DEV_END)
    _,tr=ev(b,cache,TR_START,TR_END)
    _,st=ev(b,cache,ST_START,ST_END)
    out={
      "model_id":"VW_MIDAS_PSO_ELM_V1",
      "method":{
        "elm_hidden":HIDDEN,"activation":ACTIVATION,"ridge_alpha":ALPHA,
        "pso_scope":"hidden_input_weights_and_biases",
        "pso_swarm":18,"pso_iterations":35,
        "fitness":"chronological_last20pct_training_only; 0.7*Gold_MAE + 0.3*all_outputs_MAE",
        "bounds":"[-2,2]","seed":"deterministic_by_target"
      },
      "authority":{
        "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
        "base_elm_architecture":"FROZEN_FROM_STEP1_PRE2025_SELECTION_16_SIGMOID_ALPHA_0.001",
        "inner_validation":"CHRONOLOGICAL_TAIL_ONLY_NO_RANDOM_SPLIT",
        "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"
      },
      "dev":{"metrics":base.metrics(dev),"rows":dev},
      "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
      "stress_2026":{"metrics":base.metrics(st),"rows":st}
    }
    Path("vw_midas_pso_elm_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
