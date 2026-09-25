import math
import numpy as np

HG=[12,16,24]
AG=[1e-4,1e-3,1e-2]
LO,HI=-2.0,2.0
POP,ITERS=24,35

def sig(z):
    return 1/(1+np.exp(-np.clip(z,-40,40)))

def dec(z,h):
    n=8*h
    return z[:n].reshape(8,h),z[n:n+h]

def beta(X,Y,W,b,a):
    H=sig(X@W+b)
    A=H.T@H+a*np.eye(H.shape[1])
    try:
        return np.linalg.solve(A,H.T@Y)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A)@(H.T@Y)

def loss(z,X,Y,h,a):
    n=len(X); nv=max(6,round(.2*n)); s=n-nv
    W,b=dec(z,h); B=beta(X[:s],Y[:s],W,b,a)
    p=sig(X[s:]@W+b)@B
    return float(.7*np.mean(abs(p[:,0]-Y[s:,0]))+.3*np.mean(abs(p-Y[s:])))

def tune_params(q):
    q=np.clip(q,[0.3,0.2,0.0,0.5,0,0],[1.8,1.8,1.0,3.0,2,2])
    teach_gain=float(q[0])
    learn_gain=float(q[1])
    tf_prob=float(q[2])
    decay=float(q[3])
    h=HG[int(round(q[4]))]
    a=AG[int(round(q[5]))]
    return teach_gain,learn_gain,tf_prob,decay,h,a

def run_itlbo(X,Y,q,seed):
    tg,lg,tfp,decay,h,a=tune_params(q)
    r=np.random.default_rng(seed)
    d=9*h
    P=r.uniform(LO,HI,(POP,d))
    F=np.array([loss(x,X,Y,h,a) for x in P])
    for t in range(ITERS):
        tau=t/max(1,ITERS-1)
        local_tg=tg*(1-tau)**(1/decay)+0.1
        local_lg=lg*(0.5+0.5*(1-tau))
        teacher=P[int(np.argmin(F))].copy()
        mean=P.mean(0)
        tf=2 if r.random()<tfp else 1
        for i in range(POP):
            cand=P[i]+local_tg*r.random(d)*(teacher-tf*mean)
            cand=np.clip(cand,LO,HI)
            cf=loss(cand,X,Y,h,a)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
        for i in range(POP):
            j=i
            while j==i:
                j=int(r.integers(0,POP))
            direction=(P[i]-P[j]) if F[i]<F[j] else (P[j]-P[i])
            cand=P[i]+local_lg*r.random(d)*direction
            cand=np.clip(cand,LO,HI)
            cf=loss(cand,X,Y,h,a)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
        if (t+1)%10==0:
            best=P[int(np.argmin(F))].copy()
            for _ in range(2):
                wi=int(np.argmax(F))
                cand=np.clip(best+r.normal(0,0.05,d),LO,HI)
                cf=loss(cand,X,Y,h,a)
                if cf<F[wi]:
                    P[wi]=cand; F[wi]=cf
    i=int(np.argmin(F))
    return P[i],float(F[i]),h,a,(tg,lg,tfp,decay)

def outer_score(q,X,Y,seed):
    vals=[]
    for j in range(2):
        vals.append(run_itlbo(X,Y,q,seed+97*j)[1])
    return float(np.mean(vals))

def tune_outer(X,Y,seed):
    r=np.random.default_rng(seed)
    lo=np.array([0.3,0.2,0.0,0.5,0,0])
    hi=np.array([1.8,1.8,1.0,3.0,2,2])
    cand=[]
    for _ in range(6):
        q=r.uniform(lo,hi)
        cand.append((outer_score(q,X,Y,seed+1000+len(cand)),q))
    cand.sort(key=lambda x:x[0])
    best=cand[0][1].copy()
    bestf=float(cand[0][0])
    for it in range(2):
        for k in range(4):
            scale=(hi-lo)*(0.18/(it+1))
            q=np.clip(best+r.normal(0,1,6)*scale,lo,hi)
            f=outer_score(q,X,Y,seed+10000+it*100+k)
            if f<bestf:
                bestf=float(f); best=q.copy()
    return best,bestf
