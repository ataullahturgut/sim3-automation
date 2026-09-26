"""Independent dense covariance oracle; no project labels or DB."""
import numpy as np
from scipy.linalg import cho_factor,cho_solve
import gpr_core_v1 as g

def run():
 rng=np.random.default_rng(709);X=rng.normal(size=(17,8));Y=rng.normal(size=(17,4));Z=rng.normal(size=(3,8))
 theta=g.PRIOR.copy();theta[12:18]=[.2,-.1,.4,.1,.3,-.2]
 for kind in ['RBF','M32','M52']:
  f=g.fit(theta,X,Y,kind);mu,var=g.predict(f,Z);ell,B,noise=g.decode(theta)
  K=g.kernel(X,X,ell,kind);C=np.kron(B,K)+np.kron(np.diag(noise+g.JITTER),np.eye(len(X)));y=Y.T.ravel();cf=cho_factor(C,lower=True)
  cross=np.kron(B,g.kernel(X,Z,ell,kind));alpha=cho_solve(cf,y)
  dense_mu=(cross.T@alpha).reshape(4,len(Z)).T
  dense_var=(np.diag(np.kron(B,g.kernel(Z,Z,ell,kind))-cross.T@cho_solve(cf,cross))).reshape(4,len(Z)).T+noise
  nll=.5*(y@alpha+2*np.log(np.diag(cf[0])).sum()+len(y)*np.log(2*np.pi))
  assert np.allclose(mu,dense_mu,atol=1e-9) and np.allclose(var,dense_var,atol=1e-9) and abs(f['nll']-nll)<1e-8
  actual=np.linalg.cond(C);assert actual<=g.condition(f)*(1+1e-8)
 f=g.fit(theta,X,Y);before=g.predict(f,Z)[0][:,0];Y[:,1]+=1;after=g.predict(g.fit(theta,X,Y),Z)[0][:,0];assert np.max(abs(before-after))>1e-5
 diagonal=theta.copy();diagonal[12:18]=0
 y1=Y.copy();y1[:,1]+=99;assert np.allclose(g.predict(g.fit(diagonal,X,Y),Z)[0][:,0],g.predict(g.fit(diagonal,X,y1),Z)[0][:,0])
 print('PASS dense oracle: RBF/M32/M52 means, observation variances, NLL, condition bound; real cross-output transfer; independent limit')
if __name__=='__main__':run()

# Tests the production chronology with synthetic labels only.
if __name__=='__main__':
 import gpr_experiment_v1 as e
 e.REPEATS=1
 rng=np.random.default_rng(881)
 keys=[f'{2017+i//12:04d}-{i%12+1:02d}' for i in range(52)]
 data={k:(rng.normal(size=8),rng.normal(0,.02,size=4)) for k in keys};t=keys[50]
 f=e.tune(data,t,'VANILLA_ICM_RBF');a=e.forecast(data,t,f)[0]
 changed={k:(x.copy(),y.copy()) for k,(x,y) in data.items()}
 for k in keys[50:]:changed[k]=(changed[k][0],changed[k][1]+1e6)
 f2=e.tune(changed,t,'VANILLA_ICM_RBF');b=e.forecast(changed,t,f2)[0]
 assert np.array_equal(f[0],f2[0]) and np.array_equal(a,b)
 print('PASS production tune/forecast target and future label invariance')
