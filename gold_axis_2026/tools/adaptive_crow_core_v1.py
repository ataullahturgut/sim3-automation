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
    q=np.clip(q,[0.02,0.05,0.0,0.2,0,0],[0.8,3.0,1.0,3.0,2,2])
    ap0=float(q[0]); fl0=float(q[1]); ap_slope=float(q[2]); fl_decay=float(q[3])
    h=HG[int(round(q[4]))]; a=AG[int(round(q[5]))]
    return ap0,fl0,ap_slope,fl_decay,h,a

def run_crow(X,Y,q,seed):
    ap0,fl0,ap_slope,fl_decay,h,a=unpack(q)
    r=np.random.default_rng(seed); d=9*h
    P=r.uniform(LO,HI,(POP,d))
    M=P.copy()
    F=np.array([loss(x,X,Y,h,a) for x in P])
    MF=F.copy()
    for t in range(ITERS):
        tau=t/max(1,ITERS-1)
        ap=np.clip(ap0+ap_slope*tau,0.01,0.95)
        fl=max(0.02,fl0*(1-tau)**(1/fl_decay))
        NP=P.copy()
        for i in range(POP):
            j=i
            while j==i:
                j=int(r.integers(0,POP))
            if r.random()>=ap:
                cand=P[i]+fl*r.random(d)*(M[j]-P[i])
            else:
                cand=r.uniform(LO,HI,d)
            NP[i]=np.clip(cand,LO,HI)
        NF=np.array([loss(x,X,Y,h,a) for x in NP])
        improve=NF<F
        P[improve]=NP[improve]; F[improve]=NF[improve]
        mem=F<MF
        M[mem]=P[mem]; MF[mem]=F[mem]
    i=int(np.argmin(MF))
    return M[i],float(MF[i]),h,a,(ap0,fl0,ap_slope,fl_decay)

def outer_score(q,X,Y,seed):
    return float(np.mean([run_crow(X,Y,q,seed+97*j)[1] for j in range(2)]))

def tune_outer(X,Y,seed):
    r=np.random.default_rng(seed)
    lo=np.array([0.02,0.05,0.0,0.2,0,0]); hi=np.array([0.8,3.0,1.0,3.0,2,2])
    cand=[]
    for _ in range(6):
        q=r.uniform(lo,hi); cand.append((outer_score(q,X,Y,seed+1000+len(cand)),q))
    cand.sort(key=lambda z:z[0]); best=cand[0][1].copy(); bestf=float(cand[0][0])
    for it in range(2):
        for k in range(4):
            scale=(hi-lo)*(0.18/(it+1))
            q=np.clip(best+r.normal(0,1,6)*scale,lo,hi)
            f=outer_score(q,X,Y,seed+10000+it*100+k)
            if f<bestf:
                bestf=float(f); best=q.copy()
    return best,bestf
