"""No forecast data: future invariance and an independent LP fixture."""
import numpy as np
from gpr_stage4_v1 import prequential_weights,simplex

def run():
 rng=np.random.default_rng(762);P=rng.normal(size=(33,4));y=rng.normal(size=33)
 W,V=prequential_weights(P,y);Q=P.copy();z=y.copy();Q[17:]+=100;z[17:]-=900
 W2,V2=prequential_weights(Q,z)
 assert np.allclose(W[:18],W2[:18]) and np.allclose(V[:18],V2[:18])
 assert np.allclose(W.sum(axis=1),1) and W.min()>=0 and np.allclose(W[:6],.25)
 assert np.allclose(simplex(np.array([[0.,1.],[1.,0.]]),np.array([.3,.7])),[.7,.3])
 print('PASS prequential target/future-loss invariance, simplex feasibility and exact analytic fixture')
if __name__=='__main__':run()
