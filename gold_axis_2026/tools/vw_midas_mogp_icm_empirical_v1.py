from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"

def rbf(X,Z,g):
    xx=np.sum(X*X,1)[:,None]; zz=np.sum(Z*Z,1)[None,:]
    return np.exp(-g*np.maximum(xx+zz-2*X@Z.T,0.0))

def arrays(samples,t):
    ks=sorted(k for k in samples if k<t)
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks])
    tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def fit_predict(samples,t,spec):
    gscale,noise,shrink=spec
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    N,d=X.shape
    K=rbf(X,X,gscale/d)+1e-8*np.eye(N)
    B=np.cov(Y,rowvar=False)
    B=(1-shrink)*B+shrink*np.eye(Y.shape[1])
    B=0.5*(B+B.T)+1e-8*np.eye(Y.shape[1])
    lx,U=np.linalg.eigh(K); lb,V=np.linalg.eigh(B)
    lx=np.maximum(lx,1e-10); lb=np.maximum(lb,1e-10)
    Yt=U.T@Y@V
    At=Yt/(lx[:,None]*lb[None,:]+noise)
    # posterior mean: k_*^T A B
    k=rbf(X,tx,gscale/d)[:,0]
    ku=k@U
    predz=(ku[:,None]*At*lb[None,:]).sum(axis=0)@V.T
    pred=predz*ys+ym
    return pred,len(ks),np.linalg.eigvalsh(B)

def row(b,t,pred,n,eigs,spec):
    p=base.month_shift(t,-1)
    return {"target":t,"origin":p,"spec":list(spec),"train_rows":n,
            "task_cov_eigenvalues":[float(x) for x in eigs],
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
            "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p])}

def ev(b,cache,spec,a,z):
    rs=[]; es=[]
    for t in base.month_range(a,z):
        pred,n,e=fit_predict(cache[t],t,spec)
        rs.append(row(b,t,pred,n,e,spec))
        p=base.month_shift(t,-1)
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][p])
        es.append(abs(float(pred[0])-ar))
    return float(np.mean(es)),rs

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    specs=[(g,n,s) for g in (0.5,1.0) for n in (0.01,0.05,0.1) for s in (0.0,0.25,0.5)]
    cand=[]; saved={}
    for spec in specs:
        obj,rs=ev(b,cache,spec,DEV_START,DEV_END); saved[spec]=rs
        cand.append({"spec":spec,"dev_logret_mae":obj,"dev_metrics":base.metrics(rs)})
    cand.sort(key=lambda x:(x["dev_logret_mae"],x["spec"]))
    best=tuple(cand[0]["spec"]); dev=saved[best]
    _,tr=ev(b,cache,best,TR_START,TR_END); _,st=ev(b,cache,best,ST_START,ST_END)
    out={"model_id":"VW_MIDAS_MOGP_ICM_EMPIRICAL_V1",
         "method_binding":{"family":"multi-output Gaussian process / intrinsic coregionalization",
                           "covariance":"K_input kron K_task","task_covariance":"training-fold empirical covariance with shrinkage"},
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                      "selection_period":f"{DEV_START}..{DEV_END}",
                      "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "candidates":cand,"selected_spec":best,
         "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_mogp_icm_empirical_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"selected_spec":best,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
