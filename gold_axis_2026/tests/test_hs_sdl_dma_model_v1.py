from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from hs_sdl_dma_v1.data import build_targets
from hs_sdl_dma_v1.model import apply_platt,fit_platt,fit_ridge_logistic,predict_probability
from hs_sdl_dma_v1.replay import block_superior_set,candidate_predictions,config_ids


def test_logistic_is_deterministic():
    X=np.column_stack([np.ones(8),[0,0,1,1,0,1,0,1]]); y=np.array([0,0,1,1,0,1,0,1])
    a=fit_ridge_logistic(X,y,1.0,.99); b=fit_ridge_logistic(X,y,1.0,.99)
    assert np.array_equal(a,b); assert 0<predict_probability(a,X[0],1e-6)<1


def test_calibration_does_not_need_outer_target():
    coef=fit_platt([.2,.3,.7,.8],[0,0,1,1])
    assert 0<apply_platt(.6,coef)<1


def test_three_day_maturity_excludes_unmatured_labels():
    d=pd.DataFrame({"date":pd.date_range('2026-01-01',periods=8),"close":range(100,108)})
    t=build_targets(d,3)
    at_origin_5=t[t.target_index<=5]
    assert at_origin_5.origin_index.max()==2
    assert not (at_origin_5.origin_index>2).any()


def test_config_grid_frozen_and_unique():
    c=config_ids(); assert len(c)==27; assert len({x[3] for x in c})==27


def test_overlap_inference_is_seed_deterministic():
    losses={"a":np.array([.1,.2,.1,.2]),"b":np.array([.2,.3,.2,.3])}
    assert block_superior_set(losses,4,reps=50)==block_superior_set(losses,4,reps=50)


def test_candidate_prediction_prefix_invariance():
    n=72
    d=pd.DataFrame({
      "date":pd.date_range('2025-01-01',periods=n),"close":100+np.sin(np.arange(n)/3)+np.arange(n)*.02,
      "fast_state":np.resize(["MIXED","ROBUST_UP","ROBUST_DOWN"],n),
      "slow_state":np.resize(["NOT_YET_ROBUST","ROBUST_UP","ROBUST_DOWN"],n),
      "monthly_direction_3m":np.resize(["NEUTRAL","UP","DOWN"],n),
      "emergency_level":"NEUTRAL","emergency_reversal":"OFF"})
    full,_=candidate_predictions(d,1,1.0,.99); prefix,_=candidate_predictions(d.iloc[:70].copy(),1,1.0,.99)
    for name in full:
        assert prefix[name]=={k:v for k,v in full[name].items() if k<70}
