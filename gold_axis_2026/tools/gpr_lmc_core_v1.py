"""Exact two-component LMC algebra; activation governed by Stage3C authority.
K = B1 kron K_RBF + B2 kron K_M32 + noise kron I, exact dense inference.
Vector-valued kernels authority: Alvarez/Rosasco/Lawrence 2012, section4.2.
"""
import numpy as np
from scipy.linalg import cho_factor,cho_solve
import gpr_core_v1 as g
LOW=np.r_[np.full(16,np.log(.05)),g.LOW[8:18],g.LOW[8:18],g.LOW[18:22]]
HIGH=np.r_[np.full(16,np.log(20)),g.HIGH[8:18],g.HIGH[8:18],g.HIGH[18:22]]
PRIOR=np.r_[np.zeros(8),np.full(8,np.log(2)),np.full(4,np.log(np.sqrt(.5))),np.zeros(6),np.full(4,np.log(np.sqrt(.5))),np.zeros(6),np.full(4,np.log(.3))]

def decode(theta):
 t=np.asarray(theta);assert t.shape==(40,)
 if not np.isfinite(t).all() or np.any(t<LOW-1e-8) or np.any(t>HIGH+1e-8):raise g.ScientificFailure('INVALID_LMC_THETA')
 Bs=[]
 for p in [16,26]:
  L=np.diag(np.exp(t[p:p+4]));L[g.OFF]=t[p+4:p+10];Bs.append(L@L.T)
 return [np.exp(t[:8]),np.exp(t[8:16])],Bs,np.exp(2*t[36:40])

def covariance(theta,X,Z):
 ell,Bs,noise=decode(theta)
 return sum(np.kron(B,g.kernel(X,Z,e,k)) for B,e,k in zip(Bs,ell,['RBF','M32']))

def fit(theta,X,Y):
 ell,Bs,noise=decode(theta);C=covariance(theta,X,X)+np.kron(np.diag(noise+g.JITTER),np.eye(len(X)))
 cf=cho_factor(C,lower=True,check_finite=False);y=Y.T.ravel();alpha=cho_solve(cf,y,check_finite=False)
 nll=.5*(y@alpha+2*np.log(np.diag(cf[0])).sum()+len(y)*np.log(2*np.pi))
 if not np.isfinite(nll):raise g.ScientificFailure('NONFINITE_LMC_NLL')
 bound=float(np.max(np.sum(abs(C),axis=1))/min(noise+g.JITTER))
 if bound>1e12:raise g.ScientificFailure('LMC_CONDITION_BOUND_EXCEEDED')
 return {'theta':theta.copy(),'X':X,'factor':cf,'alpha':alpha,'nll':float(nll),'noise':noise,'Bsum':sum(Bs),'condition_upper_bound':bound}

def predict(f,Z,variance=True):
 cross=covariance(f['theta'],f['X'],Z);mu=(cross.T@f['alpha']).reshape(4,len(Z)).T
 if not variance:return mu,None
 prior=np.repeat(np.diag(f['Bsum']),len(Z));reduction=np.sum(cross*cho_solve(f['factor'],cross,check_finite=False),axis=0)
 var=(prior-reduction).reshape(4,len(Z)).T
 if var.min() < -1e-7 or not np.isfinite(var).all():raise g.ScientificFailure('INVALID_LMC_VARIANCE')
 return mu,np.maximum(var,0)+f['noise']

def value_gradient(theta,X,Y):
 """Exact Gaussian NLL derivative, GPML5: .5 tr((C^-1-aaT)dC)."""
 f=fit(theta,X,Y);N=len(X);inv=cho_solve(f['factor'],np.eye(4*N),check_finite=False)
 Q=(inv-np.outer(f['alpha'],f['alpha'])).reshape(4,N,4,N)
 ell,Bs,noise=decode(theta);grad=np.zeros(40)
 for component,(length,B,kind,start) in enumerate(zip(ell,Bs,['RBF','M32'],[16,26])):
  K=g.kernel(X,X,length,kind);G=.5*np.einsum('aibj,ij->ab',Q,K,optimize=True)
  L=np.diag(np.exp(theta[start:start+4]));L[g.OFF]=theta[start+4:start+10]
  GL=(G+G.T)@L;grad[start:start+4]=np.diag(GL)*np.diag(L);grad[start+4:start+10]=GL[g.OFF]
  weighted=.5*np.einsum('ab,aibj->ij',B,Q,optimize=True)
  scaled=(X[:,None,:]-X[None,:,:])/length
  if kind=='M32':rad=np.sqrt(np.sum(scaled**2,axis=2));factor=3*np.exp(-np.sqrt(3)*rad)
  else:factor=K
  grad[component*8:component*8+8]=np.einsum('ij,ijd->d',weighted*factor,scaled**2,optimize=True)
 for a in range(4):grad[36+a]=noise[a]*np.trace(Q[a,:,a,:])
 if not np.isfinite(grad).all():raise g.ScientificFailure('NONFINITE_LMC_GRADIENT')
 return f['nll'],grad
