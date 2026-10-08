"""Causal 2026 XAU/USD research experiment."""
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def weighted_logit(x,y,ages):
    weights=np.exp(-np.log(2)*ages/252)
    model=Pipeline([("scale",StandardScaler()),("reg",LogisticRegression(C=.3))])
    model.fit(x,y,reg__sample_weight=weights)
    return model

from pathlib import Path
import sys,json
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as direct
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
import gold_execution_2020_2025_training_start_sensitivity_20261008 as old
GVZ=b.PRICE+["gvz_log","gvz_x_early","gvz_x_late"]
VIX=v.COLS
def build_features():
    q,t=src.source_load()
    z,audit=mirror.load_approved()
    f=z.set_index("bar_start_utc")[["bid_open","bid_close"]]
    f=f.rename(columns={"bid_open":"open","bid_close":"close"})
    targets,_=direct.candidate_targets(t,f)
    both=pd.concat([q,f]).sort_index()
    dates=pd.concat([t,targets],ignore_index=True).sort_values("date")
    x=b.features(both,dates,min_year=2020,max_year=2026,gvz_csv=old.GVZ_FULL)
    return v.joined(x)
