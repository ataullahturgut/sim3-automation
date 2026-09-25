import math
import numpy as np

HG=[12,16,24]
AG=[1e-4,1e-3,1e-2]
LO,HI=-2.0,2.0
POP,ITERS=24,35

def sig(z): return 1/(1+np.exp(-np.clip(z,-40,40)))
def dec(z,h):
    n=8*h
    return z[:n].reshape(8,h),z[n:n+h]
def beta(X,Y,W,b,a):
    H=sig(X@W+b); A=H.T@H+a*np.eye(H.shape[1])
    try: return np.linalg.solve(A,H.T@Y)
    except np.linalg.LinAlgError: return np.linalg.pinv(A)@(H.T@Y)
def loss(z,X,Y,h,a):
    n=len(X); nv=max(6,round(.2*n)); s=n-nv
    W,b=dec(z,h); B=beta(X[:s],Y[:s],W,b,a); p=sig(X[s:]@W+b)@B
    return float(.7*np.mean(abs(p[:,0]-Y[s:,0]))+.3*np.mean(abs(p-Y[s:])))

def unpack(q):
    q=np.clip(q,[0.2,0.2,0.2,0.05,0.0,0.0,0,0],[0.95,3.0,3.0,0.8,1.0,2.0,2,2])
    w,c1,c2,vf,mix,tlbo_gain=[float(x) for x in q[:6]]
    h=HG[int(round(q[6]))]; a=AG[int(round(q[7]))]
    return w,c1,c2,vf,mix,tlbo_gain,h,a

def run_hybrid(X,Y,q,seed):
    w,c1,c2,vf,mix,tgain,h,a=unpack(q)
    r=np.random.default_rng(seed); d=9*h
    P=r.uniform(LO,HI,(POP,d)); V=np.zeros_like(P)
    F=np.array([loss(x,X,Y,h,a) for x in P])
    PB=P.copy(); PF=F.copy()
    gi=int(np.argmin(PF)); GB=PB[gi].copy(); GF=float(PF[gi])
    vmax=vf*(HI-LO)
    for t in range(ITERS):
        tau=t/max(1,ITERS-1)
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=1 if tau<0.5 else 2
        for i in range(POP):
            r1=r.random(d); r2=r.random(d)
            V[i]=np.clip(w*V[i]+c1*r1*(PB[i]-P[i])+c2*r2*(GB-P[i]),-vmax,vmax)
            pso_cand=np.clip(P[i]+V[i],LO,HI)
            tlbo_cand=np.clip(P[i]+tgain*r.random(d)*(teacher-tf*mean),LO,HI)
            cand=np.clip((1-mix)*pso_cand+mix*tlbo_cand,LO,HI)
            cf=loss(cand,X,Y,h,a)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
            if F[i]<PF[i]:
                PB[i]=P[i].copy(); PF[i]=F[i]
                if F[i]<GF:
                    GF=float(F[i]); GB=P[i].copy()
        # learner phase
        for i in range(POP):
            j=i
            while j==i:
                j=int(r.integers(0,POP))
            direction=(P[i]-P[j]) if F[i]<F[j] else (P[j]-P[i])
            cand=np.clip(P[i]+mix*tgain*r.random(d)*direction,LO,HI)
            cf=loss(cand,X,Y,h,a)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
                if cf<PF[i]:
                    PB[i]=cand.copy(); PF[i]=cf
                    if cf<GF:
                        GF=float(cf); GB=cand.copy()
    return GB,GF,h,a,(w,c1,c2,vf,mix,tgain)

def outer_score(q,X,Y,seed):
    return float(np.mean([run_hybrid(X,Y,q,seed+97*j)[1] for j in range(2)]))

def tune_outer(X,Y,seed):
    r=np.random.default_rng(seed)
    lo=np.array([0.2,0.2,0.2,0.05,0.0,0.0,0,0])
    hi=np.array([0.95,3.0,3.0,0.8,1.0,2.0,2,2])
    cand=[]
    for _ in range(6):
        q=r.uniform(lo,hi)
        cand.append((outer_score(q,X,Y,seed+1000+len(cand)),q))
    cand.sort(key=lambda z:z[0]); best=cand[0][1].copy(); bestf=float(cand[0][0])
    for it in range(2):
        for k in range(4):
            scale=(hi-lo)*(0.16/(it+1))
            q=np.clip(best+r.normal(0,1,8)*scale,lo,hi)
            f=outer_score(q,X,Y,seed+10000+it*100+k)
            if f<bestf:
                bestf=float(f); best=q.copy()
    return best,bestf
