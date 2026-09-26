"""Synthetic technical checks; never used as forecasting performance evidence."""
import copy
import numpy as np
import vw_midas_rbfnn_stage1_v1 as r

def main():
    r.GENS=2; r.REPEATS=1
    rng=np.random.default_rng(42)
    samples={k:(rng.normal(size=8),rng.normal(0,.01,size=4))
             for k in r.base.month_range('2015-01','2020-01')}
    for method in sum(r.BATCHES,[]):
        p,d=r.predict(samples,'2020-01',method)
        assert len(p)==4 and np.isfinite(p).all()
        assert d['inner_train_last']<d['validation_first']
    p,_=r.predict(samples,'2020-01','PSO')
    altered=copy.deepcopy(samples)
    altered['2020-01']=(altered['2020-01'][0],np.full(4,999.))
    altered['2021-01']=(np.full(8,999.),np.full(4,999.))
    q,_=r.predict(altered,'2020-01','PSO')
    assert np.array_equal(p,q), 'Target-label/future leakage'
    obj=r.Objective(np.zeros((8,8)),np.ones(8),.001)
    try:obj.fit(np.zeros(72),rng.normal(size=(40,8)),rng.normal(size=(40,4)))
    except r.ScientificFailure as e:assert str(e)=='CENTER_COLLAPSE'
    else:raise AssertionError('Center collapse must fail')
    P=np.c_[np.ones(50),rng.normal(size=(50,8))];Y=rng.normal(size=(50,4))
    b=r.analytic(P,Y,.01)
    expected=np.linalg.solve(P.T@P+.01*np.diag([0.]+[1.]*8),P.T@Y)
    assert np.allclose(b,expected,rtol=1e-10,atol=1e-10)
    print('PASS: 32 optimizer interfaces; target/future invariance; collapse gate; analytic ridge')

if __name__=='__main__':main()
