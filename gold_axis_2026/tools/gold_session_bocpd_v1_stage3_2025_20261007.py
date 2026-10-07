from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_BOCPD_V1_STAGE3_OUT"
OUT.mkdir(exist_ok=True)

PREREG=AX/"GOLD_SESSION_BOCPD_V1_STAGE3_2025_PREREG_2026-10-07.md"
B2P=AX/"tools"/"gold_session_bocpd_v1_stage2_20261007.py"
M05P=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
SAGE25P=AX/"tools"/"gold_session_sage_frozen_2025_transport_20261007.py"
INCP=AX/"tools"/"gold_session_incremental_disagreement_v1_20261007.py"
FROZEN_STRUCT=AX/"GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_FROZEN_FEATURES_2026-10-07.json"
STAGE2_GATE=AX/"GOLD_SESSION_BOCPD_V1_STAGE2_GATE_2026-10-07.csv"

DATASET="GLBX.MDP3"
SCHEMA="ohlcv-1h"
START="2025-01-01"
END="2026-01-01"
BASE_SYMBOLS=["GC.v.0","SI.v.0","NQ.v.0","ZN.n.0","CL.c.0"]
MAX_COST_USD=2.00

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader is not None
    s.loader.exec_module(m)
    return m

b2=loadmod("bocpd_stage2",B2P)
m05=loadmod("model05b",M05P)
sage25=loadmod("sage25",SAGE25P)
inc=loadmod("incremental",INCP)

def fetch_2025_databento():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)
    req=dict(dataset=DATASET,schema=SCHEMA,symbols=BASE_SYMBOLS,stype_in="continuous",start=START,end=END)
    cost=float(client.metadata.get_cost(**req))
    if cost>MAX_COST_USD:
        raise RuntimeError(f"COST_CAP_EXCEEDED:{cost:.6f}")
    q=client.timeseries.get_range(**req).to_df().reset_index()
    if "ts_event" not in q.columns and "index" in q.columns:
        q=q.rename(columns={"index":"ts_event"})
    need=["ts_event","symbol","instrument_id","open","high","low","close","volume"]
    miss=[c for c in need if c not in q.columns]
    if miss:
        raise RuntimeError(f"DATABENTO_MISSING_COLUMNS:{miss}")
    q=q[need].copy()
    q["ts_event"]=pd.to_datetime(q.ts_event,utc=True,errors="raise")
    q["symbol"]=q.symbol.astype(str)
    for c in ["open","high","low","close","volume"]:
        q[c]=pd.to_numeric(q[c],errors="raise")
    if set(BASE_SYMBOLS)-set(q.symbol.unique()):
        raise RuntimeError("DATABENTO_MISSING_SYMBOLS")
    if q.duplicated(["ts_event","symbol"]).any():
        raise RuntimeError("DATABENTO_DUPLICATE_TS_SYMBOL")
    q=q.sort_values(["symbol","ts_event"]).reset_index(drop=True)
    q.to_csv(OUT/"databento_base_2025.csv.gz",index=False,compression="gzip")
    return q,cost

def combined_archives(raw25):
    hist=b2.load_archives()
    out={}
    for roll in ["c","n","v"]:
        h=hist[roll].copy()
        suffix="."+roll+".0"
        z=raw25[raw25.symbol.str.endswith(suffix)].copy()
        z["available_at_utc"]=z.ts_event+pd.Timedelta(hours=1)
        z=z[["ts_event","available_at_utc","symbol","close","volume"]]
        q=pd.concat([h,z],ignore_index=True,sort=False)
        q=q.sort_values(["symbol","ts_event"]).drop_duplicates(["symbol","ts_event"],keep="last")
        out[roll]=q.reset_index(drop=True)
    return out

def build_path_panel_extended():
    p=m05.load_targets_extended().copy()
    p=p[p.start_utc.dt.year.isin([2022,2023,2024,2025])].reset_index(drop=True)
    p["row_id"]=np.arange(len(p))
    x15=m05.load_xau15_extended()
    p=m05.s14.ma15.attach(p,x15,"g")
    req=["g_ret_6h","g_ret_12h","g_rv_12","g_up_semivol_24","g_down_semivol_24",
         "g_upfrac_24","g_close_location_24","g_age_max_neg_24","g_age_max_pos_24",
         "g_jump_concentration_24","g_range_24","g_max_drawdown_24","g_recovery_24",
         "g_anchor_available","g_max_reference_stale_min"]
    p=p.dropna(subset=req+["direction"]).copy()
    if not (p.g_anchor_available<p.start_utc).all():
        raise RuntimeError("STAGE3_XAU_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():
        raise RuntimeError("STAGE3_XAU_STALE")
    sign=np.where(p.g_ret_12h.to_numpy(float)>=0,1.0,-1.0)
    up2=p.g_up_semivol_24.to_numpy(float)**2
    dn2=p.g_down_semivol_24.to_numpy(float)**2
    total=up2+dn2+b2.EPS
    p["trend_strength"]=np.abs(p.g_ret_12h)/(p.g_rv_12+b2.EPS)
    p["opposite_semivar_share"]=np.where(sign>0,dn2/total,up2/total)
    p["deceleration_6h"]=-sign*(2.0*p.g_ret_6h-p.g_ret_12h)/(p.g_rv_12+b2.EPS)
    p["path_consistency"]=sign*(2.0*p.g_upfrac_24-1.0)
    p["trend_close_location"]=np.where(sign>0,p.g_close_location_24,1.0-p.g_close_location_24)
    p["opposite_extreme_recency"]=np.where(sign>0,1.0/(1.0+p.g_age_max_neg_24),1.0/(1.0+p.g_age_max_pos_24))
    p["jump_concentration_24"]=p.g_jump_concentration_24
    p["trend_to_range"]=np.abs(p.g_ret_12h)/(p.g_range_24+b2.EPS)
    p["adverse_excursion"]=np.where(sign>0,-p.g_max_drawdown_24/(p.g_range_24+b2.EPS),p.g_recovery_24/(p.g_range_24+b2.EPS))
    p["momentum_up"]=(p.g_ret_12h>=0).astype(int)
    p["year"]=p.start_utc.dt.year
    p["y_up"]=(p.direction=="UP").astype(int)
    h=m05.load_xau1h(x15)
    h["logp"]=np.log(h.value.astype(float))
    h["ny_date"]=h.available_at_utc.dt.tz_convert("America/New_York").dt.date
    vals=[]
    for r in p.itertuples(index=False):
        T=pd.Timestamp(r.start_utc)
        q=h[h.available_at_utc<T]
        d=q[q.ny_date==T.tz_convert("America/New_York").date()]
        if d.empty:
            vals.append(np.nan)
            continue
        sess=float(d.iloc[-1].logp-d.iloc[0].logp)
        s=1.0 if float(r.g_ret_12h)>=0 else -1.0
        vals.append(float(-s*sess/(float(r.g_rv_12)+b2.EPS)))
    p["session_against_trend"]=vals
    p=p.dropna(subset=["trend_strength","session_against_trend","trend_close_location","adverse_excursion","momentum_up"])
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True)
