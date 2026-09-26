"""Exact ICM inference. Bonilla/Chai/Williams 2007; GPML ch. 2,4,5.

Uses task-noise whitening and task eigendecomposition; mathematically identical
(to floating-point precision) to dense B kron K + D kron I. No sparse GP.
"""
import numpy as np
from scipy.linalg import cho_factor,cho_solve

JITTER=1e-8
LOW=np.r_[np.full(8,np.log(.05)),np.full(4,np.log(.1)),np.full(6,-2.),np.full(4,np.log(.01))]
HIGH=np.r_[np.full(8,np.log(20.)),np.full(4,np.log(3.)),np.full(6,2.),np.full(4,np.log(2.))]
PRIOR=np.r_[np.zeros(18),np.full(4,np.log(.3))]
OFF=np.tril_indices(4,-1)
class ScientificFailure(RuntimeError):pass

def decode(theta,single=False):
 theta=np.asarray(theta);assert theta.shape==(22,)
 if not np.isfinite(theta).all() or np.any(theta<LOW-1e-8) or np.any(theta>HIGH+1e-8):raise ScientificFailure('INVALID_THETA')
 L=np.diag(np.exp(theta[8:12]));L[OFF]=theta[12:18]
 B=L@L.T;noise=np.exp(2*theta[18:22]);q=1 if single else 4
 return np.exp(theta[:8]),B[:q,:q],noise[:q]

def kernel(X,Z,ell,kind='RBF'):
 A=X/ell;C=Z/ell
 d=np.maximum(np.sum(A*A,axis=1)[:,None]+np.sum(C*C,axis=1)[None,:]-2*A@C.T,0.)
 if kind=='RBF':return np.exp(-.5*d)
 if kind=='M32':
  t=np.sqrt(3*d);return (1+t)*np.exp(-t)
 if kind=='M52':
  t=np.sqrt(5*d);return (1+t+t*t/3)*np.exp(-t)
 raise ValueError(kind)

def fit(theta,X,Y,kind='RBF',single=False):
 ell,B,noise=decode(theta,single);Y=Y[:,:len(noise)];N,q=Y.shape
 D=noise+JITTER;inv=1/np.sqrt(D);S=inv[:,None]*B*inv[None,:]
 vals,U=np.linalg.eigh(S)
 if vals.min()<=0 or not np.isfinite(vals).all():raise ScientificFailure('NON_POSITIVE_TASK_COVARIANCE')
 K=kernel(X,X,ell,kind);Z=(Y*inv)@U;A=[];alpha=[];logdet=N*np.log(D).sum();quad=0.
 for j,v in enumerate(vals):
  C=v*K+np.eye(N);factor=cho_factor(C,lower=True,check_finite=False);a=cho_solve(factor,Z[:,j],check_finite=False)
  A.append(factor);alpha.append(a);quad+=Z[:,j]@a;logdet+=2*np.log(np.diag(factor[0])).sum()
 nll=.5*(quad+logdet+N*q*np.log(2*np.pi))
 if not np.isfinite(nll):raise ScientificFailure('NONFINITE_NLL')
 return {'X':X,'ell':ell,'B':B,'noise':noise,'D':D,'U':U,'vals':vals,'A':A,'alpha':np.array(alpha).T,'nll':float(nll),'kind':kind}

def predict(f,Z,variance=True):
 k=kernel(f['X'],Z,f['ell'],f['kind']);T=(f['B']/np.sqrt(f['D'])[None,:])@f['U']
 mu=k.T@f['alpha']@T.T
 if not variance:return mu,None
 rs=np.array([np.sum(k*cho_solve(a,k,check_finite=False),axis=0) for a in f['A']]).T
 var=np.diag(f['B'])[None,:]-rs@(T*T).T
 if var.min() < -1e-7 or not np.isfinite(var).all():raise ScientificFailure('INVALID_POSTERIOR_VARIANCE')
 return mu,np.maximum(var,0)+f['noise'][None,:]

def condition(f):
 # Certified upper bound for original covariance; no inversion needed.
 k=kernel(f['X'],f['X'],f['ell'],f['kind']);v=np.linalg.eigvalsh(k)
 bound=(f['D'].max()/f['D'].min())*(1+f['vals'].max()*max(v.max(),0))/(1+f['vals'].min()*max(v.min(),0))
 if not np.isfinite(bound) or bound>1e12:raise ScientificFailure('CONDITION_BOUND_EXCEEDED')
 return float(bound)
