from __future__ import annotations

import json, math, os
from pathlib import Path
import numpy as np
from scipy.linalg import solve_sylvester

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TRANSPORT_START, TRANSPORT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

def rbf(X, Z, gamma):
    xx=np.sum(X*X,axis=1)[:,None]; zz=np.sum(Z*Z,axis=1)[None,:]
    return np.exp(-gamma*np.maximum(xx+zz-2*X@Z.T,0.0))

def arrays(samples,target):
    keys=sorted(k for k in samples if k<target)
    if len(keys)<24: raise RuntimeError(f"TRAINING_ROWS_TOO_FEW {target}")
    X=np.stack([samples[k][0] for k in keys])
    Y=np.stack([samples[k][1] for k in keys])
    tx=samples[target][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    return keys,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def nuclear_subgrad(S):
    U,s,Vt=np.linalg.svd(S,full_matrices=False)
    mask=(s>1e-10).astype(float)
    return (U*mask)@Vt

def objective(Yq,A,S,K,lam,beta,gamma):
    N=K.shape[0]
    E=Yq-S@A@K
    return float((E*E).sum()/N + lam*np.trace(A@K@A.T)
                 + beta*np.linalg.svd(S,compute_uv=False).sum()
                 + gamma*(S*S).sum())

def fit_mmr(X,Y,lam,beta,gamma_reg,gamma_scale,max_outer=18):
    # Paper Eq. (9), (12), (26)-(27); deterministic S=I initialization.
    N,d=X.shape; Q=Y.shape[1]
    kg=float(gamma_scale)/d
    K=rbf(X,X,kg)
    K=0.5*(K+K.T)+1e-6*np.eye(N)
    Kinv=np.linalg.pinv(K,rcond=1e-10)
    Yq=Y.T
    S=np.eye(Q)
    A=np.zeros((Q,N))
    prev=float("inf")
    for _ in range(max_outer):
        left=S.T@S
        right=lam*N*Kinv
        rhs=S.T@Yq@Kinv
        A=solve_sylvester(left,right,rhs)
        cur=objective(Yq,A,S,K,lam,beta,gamma_reg)

        # Eq. (26)-(27), backtracking line search.
        AK=A@K
        grad=-(2.0/N)*(Yq-S@AK)@AK.T + beta*nuclear_subgrad(S) + 2.0*gamma_reg*S
        eta=0.2
        accepted=False
        for _ls in range(30):
            Sn=S-eta*grad
            nv=objective(Yq,A,Sn,K,lam,beta,gamma_reg)
            if nv <= cur + 1e-10:
                S=Sn; cur=nv; accepted=True; break
            eta*=0.5
        if not accepted:
            break
        if prev<1e100 and abs(prev-cur)/(abs(prev)+1e-12)<1e-5:
            break
        prev=cur
    return {"X":X,"A":A,"S":S,"kg":kg,"obj":prev}

def predict(model,tx):
    k=rbf(model["X"],tx,model["kg"])[:,0]
    return model["S"]@(model["A"]@k)

def fit_predict(samples,target,spec):
    lam,beta,gamma_reg,gscale=spec
    keys,X,Y,tx,ym,ys=arrays(samples,target)
    m=fit_mmr(X,Y,lam,beta,gamma_reg,gscale)
    pz=predict(m,tx)
    return pz*ys+ym,len(keys),m["obj"],np.linalg.svd(m["S"],compute_uv=False)

def make_row(b,t,pred,n,obj,sv,spec):
    p=base.month_shift(t,-1)
    return {"target":t,"origin":p,"spec":list(spec),"train_rows":n,
            "objective":float(obj),"structure_singular_values":[float(x) for x in sv],
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
            "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p])}

def eval_spec(b,cache,spec,start,end):
    rows=[]; errs=[]
    for t in base.month_range(start,end):
        pred,n,obj,sv=fit_predict(cache[t],t,spec)
        rows.append(make_row(b,t,pred,n,obj,sv,spec))
        p=base.month_shift(t,-1)
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][p])
        errs.append(abs(float(pred[0])-ar))
    return float(np.mean(errs)),rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True)
           for t in base.month_range(DEV_START,STRESS_END)}

    # Restricted log-scale grid, all selected before 2025.
    specs=[
      (1e-2,1e-3,1e-3,0.5),(1e-2,1e-2,1e-3,0.5),
      (1e-1,1e-3,1e-3,0.5),(1e-1,1e-2,1e-3,0.5),
      (1e-2,1e-3,1e-2,1.0),(1e-2,1e-2,1e-2,1.0),
      (1e-1,1e-3,1e-2,1.0),(1e-1,1e-2,1e-2,1.0),
    ]
    cand=[]
    for s in specs:
        obj,rows=eval_spec(b,cache,s,DEV_START,DEV_END)
        cand.append({"spec":s,"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
    cand.sort(key=lambda z:(z["dev_logret_mae"],z["spec"]))
    best=tuple(cand[0]["spec"])
    _,dev=eval_spec(b,cache,best,DEV_START,DEV_END)
    _,tr=eval_spec(b,cache,best,TRANSPORT_START,TRANSPORT_END)
    _,st=eval_spec(b,cache,best,STRESS_START,STRESS_END)
    result={
      "model_id":"VW_MIDAS_MMR_MEN_V1",
      "method_binding":{
        "paper":"Zhen et al. Multi-Target Regression via Robust Low-Rank Learning",
        "objective":"Eq9",
        "A_update":"Sylvester Eq12",
        "S_update":"nuclear-norm gradient Eq26-27",
        "kernel":"RBF",
        "initialization":"DETERMINISTIC_IDENTITY_S",
      },
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                   "selection_period":f"{DEV_START}..{DEV_END}",
                   "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
                   "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
      "source_checks":b.source_checks,
      "candidates":cand,"selected_spec":best,
      "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
      "stress_2026":{"metrics":base.metrics(st),"rows":st},
    }
    Path("vw_midas_mmr_men_v1_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"selected_spec":best,
                      "dev":result["dev"]["metrics"],
                      "transport_2025":result["transport_2025"]["metrics"],
                      "stress_2026":result["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__": main()
