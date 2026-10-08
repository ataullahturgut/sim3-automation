"""Observed first passage of FIXED 50bps barriers for XAU night sessions.

Different label: route to ±0.50% first hit, rather than sign of final price.
M15 close crossing, NOT intrabar high/low nor certified execution quote.
Gapped source paths are quarantined; no gap interpolation or future input.
"""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_primary_native_restricted_diagnostic_20261008 as direct
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as targets
NAME="GOLD_EXECUTION_2026_FIRSTPASSAGE_COMPETING_BARRIER_DIAGNOSTIC_20261008"
UP=np.log(1.005)
DOWN=np.log(.995)
def source_sets():
    q,t=src.source_load()
    zm,check=mirror.load_approved()
    qm=zm.set_index("bar_start_utc")[["bid_open","bid_close"]]
    qm=qm.rename(columns={"bid_open":"open","bid_close":"close"})
    tm,_=targets.candidate_targets(t,qm)
    qold,told,qn,tn,qc=direct.load()
    return q,t,[("MIRROR_JAN_AUG20",qm,tm),("NATIVE_DIRECT_JAN_OCT07",qn,tn)]
def per_night(q,one):
    d=pd.Timestamp(one.date)
    if d.dayofweek>=4 or one.overnight_gate!="COMPLETE_SINGLE_SOURCE":
        return None
    start=pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=14)
    stop=start+pd.Timedelta(hours=15,minutes=45)
    grid=pd.date_range(start,stop,freq="15min")
    bars=q.reindex(grid)
    valid=bars.close.notna().to_numpy(bool)
    if not(valid[0] and valid[-1]) or valid.sum()<56:
        return {"accepted":False,"reason":"SOURCE_MINUTE_GAP"}
    gap_runs=np.diff(np.r_[0,np.flatnonzero(~valid),len(valid)-1])
    if ((~valid).sum()>5):
        return {"accepted":False,"reason":"SESSION_GAP_TOO_WIDE"}
    entry=float(bars.open.iloc[0])
    if entry<=0:return {"accepted":False,"reason":"INVALID_ENTRY"}
    ret=np.log(bars.close.to_numpy(float)[valid]/entry)
    hits_up=np.flatnonzero(ret>=UP)
    hits_down=np.flatnonzero(ret<=DOWN)
    first_up=int(hits_up[0]) if len(hits_up) else None
    first_down=int(hits_down[0]) if len(hits_down) else None
    if first_up is None and first_down is None:which="NO_HIT"
    elif first_down is None:which="UP_FIRST"
    elif first_up is None:which="DOWN_FIRST"
    else:which="UP_FIRST" if first_up<first_down else "DOWN_FIRST"
    final_up=int(ret[-1]>0)
    if int(float(one.y_OVN))!=final_up:raise ValueError("PASSAGE_FINAL_DIRECTION_LABEL_CONFLICT")
    return {"accepted":True,"date":str(d.date()),"year":d.year,
       "first_hit":which,"final_up":final_up,"later_opposite_hit":bool(first_up is not None and first_down is not None),
       "first_hit_opposite_final":bool((which=="UP_FIRST" and not final_up) or (which=="DOWN_FIRST" and final_up)),
       "source_m15_closes":int(valid.sum()),"overnight_return":float(ret[-1])}
