"""Gold nonparametric 16-bar trajectory analogy, preregistered, never logistic."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as shape
import gold_execution_2020_2025_training_start_sensitivity_20261008 as frozen
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as targets
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_primary_native_restricted_diagnostic_20261008 as direct
NAME="GOLD_EXECUTION_2026_FULL_TRAJECTORY_CBR_20261008"
def source_sets():
    q,t=src.source_load()
    if len(q)!=141890 or len(t)!=1549:raise ValueError("HISTORY_CONTRACT_CHANGED")
    z,proof=mirror.load_approved()
    qm=z.set_index("bar_start_utc")[["bid_open","bid_close"]]
    qm=qm.rename(columns={"bid_open":"open","bid_close":"close"})
    tm,_=targets.candidate_targets(t,qm)
    qhist,thist,qd,td,quality=direct.load()
    if len(qhist)!=len(q):raise ValueError("HISTORICAL_CONTRACT_DIFF")
    return q,t,[("SAME_UPSTREAM_MIRROR_JAN_AUG20",qm,tm),
                ("DIRECT_DUKASCOPY_NATIVE_THROUGH_OCT07",qd,td)]
def panel(q,t,qs,ts):
    qfull=pd.concat([q,qs]).sort_index()
    if qfull.index.duplicated().any():raise ValueError("OVERLAPPING_QUOTE_TIMESTAMPS")
    tfull=pd.concat([t,ts],ignore_index=True).sort_values("date")
    if tfull.date.duplicated().any():raise ValueError("OVERLAPPING_ORIGIN_DATES")
    z=shape.features(qfull,tfull,min_year=2020,max_year=2026,gvz_csv=frozen.GVZ_FULL)
    path=[]
    for r in z.itertuples(index=False):
        origin=pd.Timestamp(r.date.date(),tz="Europe/Istanbul")+pd.Timedelta(hours=shape.ORIGIN[r.target])
        grid=pd.date_range(origin.tz_convert("UTC")-pd.Timedelta(hours=4),periods=16,freq="15min")
        bars=qfull.reindex(grid)
        if bars[["open","close"]].isna().any().any():raise ValueError("HIDDEN_PREORIGIN_PRICE_GAP")
        increments=np.log(bars.close.to_numpy(float)/bars.open.to_numpy(float))
        cum=np.cumsum(increments.reshape(8,2).sum(axis=1))
        path.append(cum/(np.sqrt(np.square(increments).sum())+1e-10))
    paths=np.array(path)
    for i in range(8):z["path_"+str(i)]=paths[:,i]
    z["log_pre_rv"]=np.log(z.pre4h_rv)
    if z.duplicated(["date","target"]).any():raise ValueError("DUPLICATE_MATURITY")
    return z
