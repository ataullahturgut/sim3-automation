import math
import numpy as np
HG=[12,16,24]; AG=[1e-4,1e-3,1e-2]; LO,HI=-2.,2.; PP,PI,DP,DI=12,20,8,6

def sig(z): return 1/(1+np.exp(-np.clip(z,-40,40)))
def dec(z,h):
    n=8*h
    return z[:n].reshape(8,h),z[n:n+h]
def beta(X,Y,W,b,a):
    H=sig(X@W+b); A=H.T@H+a*np.eye(H.shape[1])
    try: return np.linalg.solve(A,H.T@Y)
    except np.linalg.LinAlgError: return np.linalg.pinv(A)@(H.T@Y)
def loss(z,X,Y,h,a):
    n=len(X); v=max(6,round(.2*n)); s=n-v
    W,b=dec(z,h); B=beta(X[:s],Y[:s],W,b,a); p=sig(X[s:]@W+b)@B
    return float(.7*np.mean(abs(p[:,0]-Y[s:,0]))+.3*np.mean(abs(p-Y[s:])))
def pars(q):
    q=np.clip(q,[.2,.2,.2,.05,0,0],[.95,3,3,.8,2,2])
    return q[:4],HG[int(round(q[4]))],AG[int(round(q[5]))]
def pso(X,Y,q,seed):
    (w,c1,c2,vf),h,a=pars(q); r=np.random.default_rng(seed); d=9*h
    x=r.uniform(LO,HI,(PP,d)); v=np.zeros_like(x)
    f=np.array([loss(z,X,Y,h,a) for z in x]); pb=x.copy(); pf=f.copy()
    g=int(np.argmin(pf)); gb=pb[g].copy(); gf=float(pf[g]); vm=vf*(HI-LO)
    for _ in range(PI):
        for i in range(PP):
            v[i]=np.clip(w*v[i]+c1*r.random(d)*(pb[i]-x[i])+c2*r.random(d)*(gb-x[i]),-vm,vm)
            x[i]=np.clip(x[i]+v[i],LO,HI); cf=loss(x[i],X,Y,h,a)
            if cf<pf[i]:
                pb[i]=x[i].copy(); pf[i]=cf
                if cf<gf: gf=float(cf); gb=x[i].copy()
    return gb,gf,h,a,(float(w),float(c1),float(c2),float(vf))
def score(q,X,Y,seed):
    return float(np.mean([pso(X,Y,q,seed+97*j)[1] for j in range(2)]))
def de_tune(X,Y,seed):
    r=np.random.default_rng(seed)
    lo=np.array([.2,.2,.2,.05,0,0]); hi=np.array([.95,3,3,.8,2,2])
    P=r.uniform(lo,hi,(DP,6)); F=np.array([score(q,X,Y,seed+1000+i) for i,q in enumerate(P)])
    for g in range(DI):
        for i in range(DP):
            idx=[j for j in range(DP) if j!=i]
            a,b,c=r.choice(idx,3,replace=False)
            mutant=np.clip(P[a]+0.7*(P[b]-P[c]),lo,hi)
            mask=r.random(6)<0.9; mask[r.integers(0,6)]=True
            q=np.where(mask,mutant,P[i])
            f=score(q,X,Y,seed+10000+g*100+i)
            if f<F[i]: P[i]=q; F[i]=f
    i=int(np.argmin(F)); return P[i],float(F[i])
