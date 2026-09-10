from __future__ import annotations

import math
import numpy as np


def sigmoid(z):
    z=np.clip(np.asarray(z,dtype=float),-35.0,35.0)
    return 1.0/(1.0+np.exp(-z))


def fit_ridge_logistic(X,y,lam:float,discount:float=1.0,max_iter:int=50):
    X=np.asarray(X,float); y=np.asarray(y,float)
    if X.ndim!=2 or len(X)!=len(y) or len(y)==0: raise ValueError("invalid training arrays")
    if not (0<discount<=1) or lam<0: raise ValueError("invalid regularization")
    age=np.arange(len(y)-1,-1,-1,dtype=float); weights=discount**age
    beta=np.zeros(X.shape[1],float); penalty=np.eye(X.shape[1])*lam; penalty[0,0]=0.0
    for _ in range(max_iter):
        p=sigmoid(X@beta); w=weights*np.maximum(p*(1-p),1e-8)
        grad=X.T@(weights*(y-p))-penalty@beta
        hess=X.T@(w[:,None]*X)+penalty+np.eye(X.shape[1])*1e-10
        step=np.linalg.solve(hess,grad); beta=beta+step
        if np.max(np.abs(step))<1e-10: break
    return beta


def predict_probability(beta,x,epsilon:float):
    return float(np.clip(sigmoid(np.asarray(x,float)@np.asarray(beta,float)),epsilon,1-epsilon))


def fit_platt(raw,y,lam:float=0.0001,epsilon:float=1e-6):
    raw=np.clip(np.asarray(raw,float),epsilon,1-epsilon)
    z=np.log(raw/(1-raw)); X=np.column_stack([np.ones(len(z)),z])
    return fit_ridge_logistic(X,np.asarray(y,float),lam=lam,discount=1.0)


def apply_platt(raw,coef,epsilon:float=1e-6):
    p=float(np.clip(raw,epsilon,1-epsilon)); z=math.log(p/(1-p))
    return predict_probability(coef,np.array([1.0,z]),epsilon)


def binary_log_loss(p,y,epsilon=1e-6):
    p=np.clip(np.asarray(p,float),epsilon,1-epsilon); y=np.asarray(y,float)
    return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))

