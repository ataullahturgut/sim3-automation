"""Technical invariance checks, not predictive performance evidence."""
import numpy as np
import rbfnn_stage4_v1 as s
import rbfnn_mols_literature_v1 as m

def run():
    rng=np.random.default_rng(762);P=rng.normal(size=(33,4));y=rng.normal(size=33)
    W,V=s.prequential_weights(P,y)
    changed=P.copy();labels=y.copy();changed[17:]+=rng.normal(100,10,size=changed[17:].shape);labels[17:]-=900
    W2,V2=s.prequential_weights(changed,labels)
    assert np.allclose(W[:18],W2[:18]) and np.allclose(V[:18],V2[:18])
    assert np.allclose(W.sum(axis=1),1) and W.min()>=0 and np.allclose(W[:6],.25)
    exact=s.simplex(np.array([[0.,1.],[1.,0.]]),np.array([.3,.7]));assert np.allclose(exact,[.7,.3])
    X=rng.normal(size=(50,8));Y=rng.normal(size=(50,4))
    candidates=np.unique(X,axis=0);phi=m.r.vanilla.design(X,candidates,np.full(50,3.))[:,1:]
    phi-=phi.mean(axis=0);gain=np.sum((phi.T@Y)**2,axis=1)/np.sum(phi**2,axis=0)
    chosen=m.order_centers(X,Y,3.);assert np.allclose(chosen[0],candidates[np.argmax(gain)])
    keys=[f'{2017+i//12:04d}-{i%12+1:02d}' for i in range(62)]
    data={k:(rng.normal(size=8),rng.normal(0,.01,size=4)) for k in keys}
    target=keys[60];g=m.fit_geometry(data,target);a,_=m.forecast(data,target,g)
    changed={k:(x.copy(),v.copy()) for k,(x,v) in data.items()}
    for k in keys[60:]:changed[k]=(changed[k][0],changed[k][1]+999.)
    g2=m.fit_geometry(changed,target);b,_=m.forecast(changed,target,g2)
    assert np.allclose(a,b) and np.array_equal(g[0],g2[0])
    print('PASS: prequential future-label/forecast invariance; simplex exact fixture; MOLS explained-trace selection; target/future-label invariance')

if __name__=='__main__':run()
