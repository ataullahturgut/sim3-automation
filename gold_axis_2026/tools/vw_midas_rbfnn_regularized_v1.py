from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np, psycopg
from sklearn.cluster import KMeans
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as metrics_mod

DEV_START,DEV_END="2022-04","2024-12"; TR_START,TR_END="2025-01","2025-12"; ST_START,ST_END="2026-01","2026-07"
CENTER_GRID=(4,6,8,12)
WIDTH_GRID=(0.5,1.0,1.5,2.0)
RIDGE_GRID=(0.0,1e-4,1e-3,1e-2,1e-1)
VAL_FRAC=.20; MIN_VAL=6; MIN_TRAIN=30

def scale_fit(X,Y):
    xm,xs=X.mean(0),X.std(0); ym,ys=Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    return xm,xs,ym,ys

def fit_centers(X,k,seed):
    km=KMeans(n_clusters=k,random_state=seed,n_init=20)
    lab=km.fit_predict(X); c=km.cluster_centers_.astype(float)
    w=np.zeros(k,float)
    for j in range(k):
        pts=X[lab==j]
        if len(pts)>=2:
            w[j]=float(np.sqrt(np.mean(np.sum((pts-c[j])**2,axis=1))))
        else:
            oth=np.delete(c,j,axis=0)
            w[j]=float(np.min(np.linalg.norm(oth-c[j],axis=1))) if len(oth) else 1.0
    pos=w[(w>1e-9)&np.isfinite(w)]
    fb=float(np.median(pos)) if len(pos) else 1.0
    w=np.where((w>1e-9)&np.isfinite(w),w,fb)
    return c,np.clip(w,.10,10.0)

def design(X,c,w,scale):
    ww=np.clip(w*scale,.05,20.0)
    d=X[:,None,:]-c[None,:,:]
    d2=np.sum(d*d,axis=2)
    return np.c_[np.ones(len(X)),np.exp(-.5*d2/(ww[None,:]**2))]

def fit_beta(P,Y,ridge):
    A=P.T@P + ridge*np.diag([0.0]+[1.0]*(P.shape[1]-1))
    B=P.T@Y
    try: return np.linalg.solve(A,B)
    except np.linalg.LinAlgError: return np.linalg.pinv(A)@B

def objective(pred,Y):
    g=np.mean(np.abs(pred[:,0]-Y[:,0])); a=np.mean(np.abs(pred-Y))
    return float(.7*g+.3*a)

def select_spec(samples,target):
    keys=sorted(k for k in samples if k<target)
    X0=np.stack([samples[k][0] for k in keys]); Y0=np.stack([samples[k][1] for k in keys])
    nval=max(MIN_VAL,int(round(VAL_FRAC*len(keys)))); split=len(keys)-nval
    if split<MIN_TRAIN: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL {target}")
    xm,xs,ym,ys=scale_fit(X0[:split],Y0[:split])
    Xtr=(X0[:split]-xm)/xs; Ytr=(Y0[:split]-ym)/ys
    Xv=(X0[split:]-xm)/xs; Yv=(Y0[split:]-ym)/ys
    seed=92001+sum(map(ord,target))
    best=None
    for k in CENTER_GRID:
      c,w=fit_centers(Xtr,k,seed+k)
      for ws in WIDTH_GRID:
        Pt=design(Xtr,c,w,ws); Pv=design(Xv,c,w,ws)
        for r in RIDGE_GRID:
          b=fit_beta(Pt,Ytr,r); val=objective(Pv@b,Yv)
          rec=(val,k,ws,r)
          if best is None or rec<best: best=rec
    return best[1:],len(keys)

def predict(samples,target):
    (k,ws,r),n=select_spec(samples,target)
    keys=sorted(k0 for k0 in samples if k0<target)
    X0=np.stack([samples[k0][0] for k0 in keys]); Y0=np.stack([samples[k0][1] for k0 in keys]); tx0=samples[target][0][None,:]
    xm,xs,ym,ys=scale_fit(X0,Y0); X=(X0-xm)/xs; Y=(Y0-ym)/ys; tx=(tx0-xm)/xs
    seed=92001+sum(map(ord,target))
    c,w=fit_centers(X,k,seed+k); P=design(X,c,w,ws); b=fit_beta(P,Y,r)
    pred=(design(tx,c,w,ws)@b)[0]*ys+ym
    return pred,{"centers":k,"width_scale":ws,"ridge":r,"train_rows":n,"condition":float(np.linalg.cond(P))}

def ev(bundle,cache,a,z):
    rows=[]
    for t in base.month_range(a,z):
      p,d=predict(cache[t],t); o=base.month_shift(t,-1)
      rows.append({"target":t,"origin":o,"diag":d,"pred_log_return_gold":float(p[0]),
        "forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),"actual":float(bundle.core_gold[t]),"rw":float(bundle.core_gold[o])})
    return rows

def inv(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
      with cn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def main():
    dsn=os.environ["NEON_DATABASE_URL"]; b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=ev(b,cache,DEV_START,DEV_END); tr=ev(b,cache,TR_START,TR_END); st=ev(b,cache,ST_START,ST_END)
    for r in dev+tr+st:
      if not math.isfinite(r["forecast"]) or abs(r["pred_log_return_gold"])>=1: raise RuntimeError("SCIENTIFIC_GATE_FAIL "+r["target"])
    after=inv(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={"model_id":"VW_MIDAS_RBFNN_REGULARIZED_V1",
      "search":{"centers":CENTER_GRID,"width_scale":WIDTH_GRID,"ridge":RIDGE_GRID,
        "selection":"chronological_last20pct_min6 weighted standardized MAE","random_split":"NONE"},
      "authority":{"selection_period":f"{DEV_START}..{DEV_END}","2025_role":"REPORTING_ONLY","2026_role":"REPORTING_ONLY","database_access":"READ_ONLY"},
      "dev":{"metrics":metrics_mod.active_metrics(dev),"yearly":metrics_mod.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":metrics_mod.active_metrics(tr),"rows":tr},
      "stress_2026":{"metrics":metrics_mod.active_metrics(st),"rows":st}}
    Path("vw_midas_rbfnn_regularized_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("SCIENTIFIC_GATE=PASS"); print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
