"""Check LMC scalar indexing against dense block covariance definitions."""
import numpy as np
from scipy.linalg import cho_factor,cho_solve
import gpr_lmc_core_v1 as l

def run():
 rng=np.random.default_rng(14);X=rng.normal(size=(9,8));Y=rng.normal(size=(9,4));Z=rng.normal(size=(2,8));t=l.PRIOR.copy();t[20:26]=[.1,.3,-.2,.1,-.2,.4];t[30:36]=[-.2,.1,.3,.1,.4,-.1]
 ell,Bs,noise=l.decode(t);f=l.fit(t,X,Y);mu,var=l.predict(f,Z)
 # Independent loops over observations and output indices, not kron assembly.
 N=len(X);C=np.zeros((4*N,4*N));R=np.zeros((4*N,4*len(Z)))
 for a in range(4):
  for b in range(4):
   for i in range(N):
    for j in range(N):
     C[a*N+i,b*N+j]=sum(B[a,b]*l.g.kernel(X[i:i+1],X[j:j+1],e,k)[0,0] for B,e,k in zip(Bs,ell,['RBF','M32']))+(noise[a]+l.g.JITTER if a==b and i==j else 0)
    for j in range(len(Z)):R[a*N+i,b*len(Z)+j]=sum(B[a,b]*l.g.kernel(X[i:i+1],Z[j:j+1],e,k)[0,0] for B,e,k in zip(Bs,ell,['RBF','M32']))
 cf=cho_factor(C,lower=True);oracle=(R.T@cho_solve(cf,Y.T.ravel())).reshape(4,len(Z)).T
 diag=np.repeat(np.diag(sum(Bs)),len(Z))-np.sum(R*cho_solve(cf,R),axis=0);obs=diag.reshape(4,len(Z)).T+noise
 assert np.allclose(mu,oracle,atol=1e-9) and np.allclose(var,obs,atol=1e-9)
 assert np.linalg.cond(C)<=f['condition_upper_bound']*(1+1e-8)
 nll,grad=l.value_gradient(t,X,Y);numeric=[]
 for j in range(40):
  u=t.copy();v=t.copy();u[j]+=1e-5;v[j]-=1e-5;numeric.append((l.fit(u,X,Y)['nll']-l.fit(v,X,Y)['nll'])/2e-5)
 assert abs(nll-f['nll'])<1e-10 and np.allclose(grad,numeric,rtol=2e-5,atol=2e-6)
 print('PASS all40 analytic LMC derivatives vs central finite differences')
 print('PASS LMC two-kernel indexing, posterior mean/variance and condition bound; no production model run')
if __name__=='__main__':run()

if __name__=='__main__':
 import gpr_lmc_experiment_v1 as e
 rng=np.random.default_rng(881)
 keys=[f'{2017+i//12:04d}-{i%12+1:02d}' for i in range(45)]
 data={k:(rng.normal(size=8),rng.normal(0,.02,size=4)) for k in keys};target=keys[43]
 fitted=e.tune(data,target,e.METHOD);before=e.forecast(data,target,fitted)[0]
 changed={k:(x.copy(),y.copy()) for k,(x,y) in data.items()}
 for k in keys[43:]:changed[k]=(changed[k][0],changed[k][1]+1e6)
 fitted2=e.tune(changed,target,e.METHOD);after=e.forecast(changed,target,fitted2)[0]
 assert np.array_equal(fitted[0],fitted2[0]) and np.array_equal(before,after)
 print('PASS LMC production tune/forecast target and future label invariance; synthetic only')
