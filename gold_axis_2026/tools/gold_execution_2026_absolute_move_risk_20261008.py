"""2026 origin-safe gold next-session absolute-move and DOWN-tail risk study."""
from __future__ import annotations
import os,sys,json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from scipy.stats import spearmanr
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_2020_2025_training_start_sensitivity_20261008 as old
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as direct
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_primary_native_restricted_diagnostic_20261008 as primary
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
NAME="GOLD_EXECUTION_2026_ABSOLUTE_SESSION_RISK_TEST_20261008"
def panel(q,t,q26,t26):
    bars=pd.concat([q,q26]).sort_index()
    labels=pd.concat([t,t26],ignore_index=True).sort_values("date")
    z=b.features(bars,labels,min_year=2020,max_year=2026,gvz_csv=old.GVZ_FULL)
    z=v.joined(z)
    z=z[z.target=="OVN"].copy()
    r=labels[["date","ret_OVN"]].rename(columns={"ret_OVN":"realized_return"})
    z=z.merge(r,on="date",how="left",validate="many_to_one")
    if z.realized_return.isna().any():raise RuntimeError("MISSING_RETURNS")
    z["x_rv"]=np.log(np.maximum(1e-8,z.pre4h_rv))
    z["x_prevday"]=np.log(np.maximum(1e-8,z.prior_day.abs()))
    z["x_gvz"]=z.gvz_log
    z["x_jump"]=z.pre4h_jump_share
    z["x_semidown"]=z.pre4h_down_semivol/np.maximum(1e-8,z.pre4h_rv)
    z["abs_move"]=z.realized_return.abs()
    if not (z.abs_move>=0).all():raise RuntimeError("INVALID_ABS_MOVE")
    return z
FEATURES=["x_rv","x_prevday","x_gvz","x_jump","x_semidown"]

def produce_predictions(z,tag):
    out=[]
    for year in (2023,2024,2025,2026):
        sub=z[z.year==year].sort_values("date")
        cache={}
        for period,now in sub.groupby(sub.date.dt.to_period("M")):
            month=period.to_timestamp()
            freeze=month if year<=2024 else pd.Timestamp(f"{year}-01-01")
            if freeze not in cache:
                tr=z[(z.date<freeze)&(z.next_date<=freeze)].copy()
                if len(tr)<175:raise RuntimeError("RISK_HISTORY_TOO_SHORT")
                m=Pipeline([("scale",StandardScaler()),("ridge",Ridge(alpha=20.))])
                m.fit(tr[FEATURES].to_numpy(float),np.log(tr.abs_move.to_numpy(float)+1e-5))
                risks=np.maximum(0,np.exp(m.predict(tr[FEATURES].to_numpy(float)))-1e-5)
                cache[freeze]=(m,float(np.quantile(risks,.75)),
                     float(np.quantile(tr.abs_move,.75)),
                     float(np.quantile(tr.realized_return,.10)),
                     float(tr.abs_move.median()))
