from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np, psycopg
from sklearn.cluster import KMeans
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as metrics_mod

DEV_START,DEV_END="2022-04","2024-12"; TR_START,TR_END="2025-01","2025-12"; ST_START,ST_END="2026-01","2026-07"
CENTER_GRID=(4,6,8,12); WIDTH_GRID=(0.5,1.0,1.5,2.0); RIDGE_GRID=(0.0,1e-4,1e-3,1e-2,1e-1)
VAL_FRAC=.20; MIN_VAL=6; MIN_TRAIN=30
POP=20; GENS=30; REFIT_GENS=12; REPEATS=3
CENTER_DELTA=1.0; LOGW_LO,LOGW_HI=math.log(.25),math.log(4.0)

def scale_fit(X,Y):
    xm,xs=X.mean(0),X.std(0); ym,ys=Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.,xs); ys=np.where(ys<1e-9,1.,ys)
    return xm,xs,ym,ys

def fit_centers(X,k,seed):
    km=KMeans(n_clusters=k,random_state=seed,n_init=20)
    lab=km.fit_predict(X); c=km.cluster_centers_.astype(float)
    w=np.zeros(k,float)
    for j in range(k):
        pts=X[lab==j]
        if len(pts)>=2: w[j]=float(np.sqrt(np.mean(np.sum((pts-c[j])**2,axis=1))))
        else:
            oth=np.delete(c,j,axis=0); w[j]=float(np.min(np.linalg.norm(oth-c[j],axis=1))) if len(oth) else 1.
    pos=w[(w>1e-9)&np.isfinite(w)]; fb=float(np.median(pos)) if len(pos) else 1.
    return c,np.clip(np.where((w>1e-9)&np.isfinite(w),w,fb),.10,10.)

def design(X,c,w):
    d=X[:,None,:]-c[None,:,:]; d2=np.sum(d*d,axis=2)
    return np.c_[np.ones(len(X)),np.exp(-.5*d2/(w[None,:]**2))]

def beta(P,Y,r):
    A=P.T@P+r*np.diag([0.]+[1.]*(P.shape[1]-1)); B=P.T@Y
    try:return np.linalg.solve(A,B)
    except np.linalg.LinAlgError:return np.linalg.pinv(A)@B

def obj(pred,Y):
    return float(.7*np.mean(np.abs(pred[:,0]-Y[:,0]))+.3*np.mean(np.abs(pred-Y)))

def select_base(Xtr,Ytr,Xv,Yv,target):
    seed=93001+sum(map(ord,target)); best=None
    for k in CENTER_GRID:
      c,w0=fit_centers(Xtr,k,seed+k)
      for ws in WIDTH_GRID:
        w=w0*ws; Pt=design(Xtr,c,w); Pv=design(Xv,c,w)
        for r in RIDGE_GRID:
          b=beta(Pt,Ytr,r); val=obj(Pv@b,Yv); rec=(val,k,ws,r,c,w0)
          if best is None or rec[0]<best[0]: best=rec
    return best

def decode(theta,c0,w0):
    k,d=c0.shape; nc=k*d
    dc=theta[:nc].reshape(k,d); lm=theta[nc:]
    c=c0+dc
    w=np.clip(w0*np.exp(lm),.05,20.)
    return c,w

def fitness(theta,X,Y,c0,w0,r):
    c,w=decode(theta,c0,w0); P=design(X,c,w); b=beta(P,Y,r)
    return obj(P@b,Y)

def valfit(theta,X,Y,Xv,Yv,c0,w0,r):
    c,w=decode(theta,c0,w0); b=beta(design(X,c,w),Y,r)
    return obj(design(Xv,c,w)@b,Yv)

def init_pop(rng,dim,center=None):
    if center is None:
        P=np.c_[rng.uniform(-.25,.25,size=(POP,dim-len_center_placeholder)),]
    return None

def bounds(k,d):
    lo=np.r_[np.full(k*d,-CENTER_DELTA),np.full(k,LOGW_LO)]
    hi=np.r_[np.full(k*d, CENTER_DELTA),np.full(k,LOGW_HI)]
    return lo,hi

def make_pop(rng,lo,hi,center=None):
    dim=len(lo)
    if center is None:
        P=rng.uniform(lo,hi,size=(POP,dim))
        P[0]=0.0
    else:
        P=np.clip(center[None,:]+rng.normal(0,.12,size=(POP,dim)),lo,hi); P[0]=center
    return P

def adaptive_pso(X,Y,Xv,Yv,c0,w0,r,seed,gens,center=None):
    rng=np.random.default_rng(seed); lo,hi=bounds(*c0.shape); P=make_pop(rng,lo,hi,center)
    V=np.zeros_like(P); F=np.array([fitness(x,X,Y,c0,w0,r) for x in P])
    PB=P.copy(); PF=F.copy(); gi=int(np.argmin(PF)); G=PB[gi].copy()
    best=(math.inf,None)
    for x in P:
        v=valfit(x,X,Y,Xv,Yv,c0,w0,r)
        if v<best[0]: best=(v,x.copy())
    for g in range(gens):
        q=g/max(1,gens-1); w=.9-.5*q; c1=2.5-2.0*q; c2=.5+2.0*q
        vmax=.35*(hi-lo)
        V=w*V+c1*rng.random(P.shape)*(PB-P)+c2*rng.random(P.shape)*(G-P)
        V=np.clip(V,-vmax,vmax); P=np.clip(P+V,lo,hi)
        F=np.array([fitness(x,X,Y,c0,w0,r) for x in P])
        imp=F<PF; PB[imp]=P[imp]; PF[imp]=F[imp]; G=PB[int(np.argmin(PF))].copy()
        top=np.argsort(F)[:max(3,POP//4)]
        for i in top:
            v=valfit(P[i],X,Y,Xv,Yv,c0,w0,r)
            if v<best[0]: best=(v,P[i].copy())
    return best[1],best[0]

def adaptive_tlbo(X,Y,Xv,Yv,c0,w0,r,seed,gens,center=None):
    rng=np.random.default_rng(seed); lo,hi=bounds(*c0.shape); P=make_pop(rng,lo,hi,center)
    F=np.array([fitness(x,X,Y,c0,w0,r) for x in P]); best=(math.inf,None)
    for g in range(gens):
        q=g/max(1,gens-1); teach=1.2-.4*q; learn=.8+.4*q
        teacher=P[int(np.argmin(F))]; mean=P.mean(0); TF=2 if rng.random()<.5 else 1
        cand=np.clip(P+rng.random(P.shape)*teach*(teacher-TF*mean),lo,hi)
        CF=np.array([fitness(x,X,Y,c0,w0,r) for x in cand]); imp=CF<F; P[imp]=cand[imp]; F[imp]=CF[imp]
        for i in range(POP):
            j=int(rng.integers(0,POP-1)); j=j+1 if j>=i else j
            step=(P[j]-P[i]) if F[j]<F[i] else (P[i]-P[j])
            x=np.clip(P[i]+rng.random(len(lo))*learn*step,lo,hi); fx=fitness(x,X,Y,c0,w0,r)
            if fx<F[i]: P[i],F[i]=x,fx
        top=np.argsort(F)[:max(3,POP//4)]
        for i in top:
            v=valfit(P[i],X,Y,Xv,Yv,c0,w0,r)
            if v<best[0]: best=(v,P[i].copy())
    return best[1],best[0]

METHODS={"ADAPTIVE_PSO":adaptive_pso,"ADAPTIVE_TLBO":adaptive_tlbo}

def predict(samples,target,method):
    keys=sorted(k for k in samples if k<target)
    X0=np.stack([samples[k][0] for k in keys]); Y0=np.stack([samples[k][1] for k in keys]); tx0=samples[target][0][None,:]
    nval=max(MIN_VAL,int(round(VAL_FRAC*len(keys)))); split=len(keys)-nval
    xm,xs,ym,ys=scale_fit(X0[:split],Y0[:split]); Xtr=(X0[:split]-xm)/xs; Ytr=(Y0[:split]-ym)/ys; Xv=(X0[split:]-xm)/xs; Yv=(Y0[split:]-ym)/ys
    bsel=select_base(Xtr,Ytr,Xv,Yv,target); _,k,ws,r,c0,wbase=bsel; w0=wbase*ws
    fn=METHODS[method]; best=None
    for rep in range(REPEATS):
        th,v=fn(Xtr,Ytr,Xv,Yv,c0,w0,r,94001+1009*rep+sum(map(ord,target))+sum(map(ord,method)),GENS)
        if best is None or v<best[0]: best=(v,th,rep)
    _,th,rep=best
    xm,xs,ym,ys=scale_fit(X0,Y0); X=(X0-xm)/xs; Y=(Y0-ym)/ys; tx=(tx0-xm)/xs
    # rebuild base geometry on full pre-target history with frozen structural choices
    cfull,wbasefull=fit_centers(X,k,93001+sum(map(ord,target))+k); wfull=wbasefull*ws
    # transfer optimized perturbation vector to full-history geometry; short refit
    th2,_=fn(X,Y,X,Y,cfull,wfull,r,95001+1009*rep+sum(map(ord,target))+sum(map(ord,method)),REFIT_GENS,center=th)
    c,w=decode(th2,cfull,wfull); B=beta(design(X,c,w),Y,r); p=(design(tx,c,w)@B)[0]*ys+ym
    return p,{"k":k,"width_scale":ws,"ridge":r,"selected_repeat":rep,"inner_val":best[0]}

def ev(bundle,cache,method,a,z):
    rows=[]
    for t in base.month_range(a,z):
        p,d=predict(cache[t],t,method); o=base.month_shift(t,-1)
        rows.append({"target":t,"origin":o,"method":method,"diag":d,"pred_log_return_gold":float(p[0]),"forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),"actual":float(bundle.core_gold[t]),"rw":float(bundle.core_gold[o])})
    return rows

def inv(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
      with cn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def main():
    dsn=os.environ["NEON_DATABASE_URL"]; b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    out={"batch":"RBFNN_N13_BATCH1","models":{}}
    for method in METHODS:
        dev=ev(b,cache,method,DEV_START,DEV_END); tr=ev(b,cache,method,TR_START,TR_END); st=ev(b,cache,method,ST_START,ST_END)
        for rr in dev+tr+st:
            if not math.isfinite(rr["forecast"]) or abs(rr["pred_log_return_gold"])>=1: raise RuntimeError(f"SCIENTIFIC_GATE_FAIL {method} {rr['target']}")
        out["models"][method]={"dev":{"metrics":metrics_mod.active_metrics(dev),"yearly":metrics_mod.yearly(dev),"rows":dev},"transport_2025":{"metrics":metrics_mod.active_metrics(tr),"rows":tr},"stress_2026":{"metrics":metrics_mod.active_metrics(st),"rows":st}}
    if inv(dsn)!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    Path("vw_midas_rbfnn_n13_batch1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({m:{k:v[k]["metrics"] for k in ("dev","transport_2025","stress_2026")} for m,v in out["models"].items()},sort_keys=True))
if __name__=="__main__": main()
