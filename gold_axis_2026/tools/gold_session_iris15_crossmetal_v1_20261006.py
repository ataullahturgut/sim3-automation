from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V2_PATH=AX/"tools"/"gold_session_structural_iris_crossmetal_v2_clocksafe_20261006.py"
XAU15=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
SIPL15=AX/"GOLD_DATABENTO_SI_PL_OHLCV15M_N0_DERIVED_2022_2024.csv.gz"
OUT=AX/"SESSION_IRIS15_CROSSMETAL_V1_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m
v2=loadmod("v2",V2_PATH)

CORE3=list(v2.CORE3)
HRET=[1,3,6,12,24,48]
RVH=[6,12,24,48]
MAX_ANCHOR_LAG_MIN=30.0
BLOCK=5
MIN_TRAIN=180

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def load_xau15():
    q=pd.read_csv(XAU15)
    if "dt_utc" not in q.columns or "close" not in q.columns:
        raise RuntimeError(f"XAU15_SCHEMA_FAIL:{q.columns.tolist()}")
    q=q[["dt_utc","close"]].copy()
    q["ts"]=pd.to_datetime(q.pop("dt_utc"),utc=True,errors="raise")
    q["value"]=pd.to_numeric(q.pop("close"),errors="raise")
    q=q.dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    if (q.value<=0).any():raise RuntimeError("XAU15_NONPOSITIVE")
    q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
    return q[["ts","available_at_utc","value"]].reset_index(drop=True)

def load_fut15(symbol):
    q=pd.read_csv(SIPL15,compression="gzip")
    req={"symbol","ts_event","close","available_at_utc"}
    if not req.issubset(q.columns):
        raise RuntimeError(f"SIPL15_SCHEMA_FAIL:{q.columns.tolist()}")
    q=q[q.symbol.astype(str).eq(symbol)][["ts_event","available_at_utc","close"]].copy()
    q["ts"]=pd.to_datetime(q.pop("ts_event"),utc=True,errors="raise")
    q["available_at_utc"]=pd.to_datetime(q.available_at_utc,utc=True,errors="raise")
    q["value"]=pd.to_numeric(q.pop("close"),errors="raise")
    q=q.dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    if q.empty or (q.value<=0).any():raise RuntimeError(f"{symbol}_BAD_15M")
    expected=q.ts+pd.Timedelta(minutes=15)
    if not (expected.values==q.available_at_utc.values).all():
        raise RuntimeError(f"{symbol}_AVAILABLE_AT_FAIL")
    return q[["ts","available_at_utc","value"]].reset_index(drop=True)

def source_index(raw):
    q=raw.sort_values("available_at_utc").copy().reset_index(drop=True)
    if q.available_at_utc.duplicated().any():raise RuntimeError("DUPLICATE_AVAILABILITY")
    q["logp"]=np.log(q.value.astype(float))
    av=q.available_at_utc.to_numpy(dtype="datetime64[ns]")
    lp=q.logp.to_numpy(float)
    lookup={pd.Timestamp(t):float(v) for t,v in zip(q.available_at_utc,q.logp)}
    return q,av,lp,lookup

def slope_time(times, vals):
    if len(vals)<2:return np.nan
    x=(times-times[0]).total_seconds().to_numpy(float)/3600.0
    y=np.asarray(vals,float)
    xm=x.mean(); ym=y.mean(); den=np.sum((x-xm)**2)
    return np.nan if den<=0 else float(np.sum((x-xm)*(y-ym))/den)

def max_drawdown(a):
    a=np.asarray(a,float)
    return np.nan if len(a)<2 else float(np.min(a-np.maximum.accumulate(a)))

def calc_at_target(raw_index,target_start,prefix):
    q,av,lp,lookup=raw_index
    ts=np.datetime64(pd.Timestamp(target_start).tz_convert("UTC").tz_localize(None))
    # np array from tz-aware series is UTC-naive ns representation.
    i=int(np.searchsorted(av,ts,side="left")-1)
    if i<0:return None
    row=q.iloc[i]
    A=pd.Timestamp(row.available_at_utc)
    lag=(pd.Timestamp(target_start)-A).total_seconds()/60.0
    if not (0 < lag <= MAX_ANCHOR_LAG_MIN):return None
    anchor=float(row.logp)

    f={
        f"{prefix}_anchor_available":A,
        f"{prefix}_anchor_lag_min":float(lag),
    }

    # Exact target-clock returns: same staleness at anchor and reference.
    for h in HRET:
        rt=A-pd.Timedelta(hours=h)
        ref=lookup.get(rt)
        if ref is None:return None
        f[f"{prefix}_ret_{h}h"]=anchor-ref

    # Original IRIS lag2 semantics: 1h return ending two hours before anchor.
    p2=lookup.get(A-pd.Timedelta(hours=2))
    p3=lookup.get(A-pd.Timedelta(hours=3))
    if p2 is None or p3 is None:return None
    f[f"{prefix}_lag2"]=p2-p3

    # Fixed-clock path statistics from observed 15m closes inside each window.
    cache={}
    for h in RVH:
        cut=A-pd.Timedelta(hours=h)
        lo=int(np.searchsorted(av,np.datetime64(cut.tz_localize(None)),side="left"))
        hi=i+1
        w=q.iloc[lo:hi]
        # Require exact clock boundary and a minimally informative path.
        if w.empty or pd.Timestamp(w.iloc[0].available_at_utc)!=cut or len(w)<2:return None
        vals=w.logp.to_numpy(float)
        dr=np.diff(vals)
        if len(dr)==0:return None
        rv=float(np.sqrt(np.sum(dr*dr)))
        f[f"{prefix}_rv_{h}"]=rv
        cache[h]=(w,vals,dr)

    w24,vals24,dr24=cache[24]
    pos=np.clip(dr24,0,None); neg=np.clip(dr24,None,0)
    upsv=float(np.sqrt(np.sum(pos*pos))); dnsv=float(np.sqrt(np.sum(neg*neg)))
    rv24=float(f[f"{prefix}_rv_24"])
    trough=float(np.min(vals24)); hi=float(np.max(vals24))
    f[f"{prefix}_up_semivol_24"]=upsv
    f[f"{prefix}_down_semivol_24"]=dnsv
    f[f"{prefix}_down_up_semivol_ratio_24"]=dnsv/(upsv+1e-8)
    f[f"{prefix}_jump_concentration_24"]=float(np.max(np.abs(dr24))/(rv24+1e-8))
    f[f"{prefix}_range_24"]=hi-trough
    f[f"{prefix}_upfrac_24"]=float(np.mean(dr24>0))
    f[f"{prefix}_max_drawdown_24"]=max_drawdown(vals24)
    f[f"{prefix}_recovery_24"]=anchor-trough
    f[f"{prefix}_close_location_24"]=(anchor-trough)/(hi-trough+1e-8)

    # Time-aware slope, not bar-index slope.
    for h in [6,24]:
        w,vals,_=cache[h]
        f[f"{prefix}_slope_{h}"]=slope_time(
            pd.DatetimeIndex(w.available_at_utc),vals
        )

    # Age of largest positive/negative observed move, measured in clock hours.
    end_times=pd.DatetimeIndex(w24.available_at_utc.iloc[1:])
    imax=int(np.argmax(dr24)); imin=int(np.argmin(dr24))
    f[f"{prefix}_age_max_pos_24"]=(A-end_times[imax]).total_seconds()/3600.0
    f[f"{prefix}_age_max_neg_24"]=(A-end_times[imin]).total_seconds()/3600.0
    f[f"{prefix}_obs_returns_24h"]=int(len(dr24))

    return f

def feature_names(prefix):
    path=[f"{prefix}_ret_{h}h" for h in HRET]+[f"{prefix}_lag2"]
    vol=[f"{prefix}_rv_{h}" for h in RVH]+[
        f"{prefix}_up_semivol_24",f"{prefix}_down_semivol_24",
        f"{prefix}_down_up_semivol_ratio_24",f"{prefix}_jump_concentration_24",
        f"{prefix}_range_24",
    ]
    shape=[
        f"{prefix}_upfrac_24",f"{prefix}_slope_6",f"{prefix}_slope_24",
        f"{prefix}_max_drawdown_24",f"{prefix}_recovery_24",
        f"{prefix}_close_location_24",f"{prefix}_age_max_pos_24",
        f"{prefix}_age_max_neg_24",
    ]
    return path+vol+shape

def attach(panel,raw,prefix):
    idx=source_index(raw)
    rec=[]
    for r in panel.itertuples(index=False):
        f=calc_at_target(idx,r.start_utc,prefix)
        if f is None:
            rec.append({"_key":r._key})
        else:
            f["_key"]=r._key;rec.append(f)
    return panel.merge(pd.DataFrame(rec),on="_key",how="left",validate="one_to_one")

def timing_samples(panel):
    rows=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        z=pd.concat([g.sort_values("start_utc").head(2),g.sort_values("start_utc").tail(2)]).drop_duplicates("start_utc")
        for r in z.itertuples(index=False):
            for p in ["g","si","pl"]:
                a=getattr(r,f"{p}_anchor_available")
                rows.append({
                    "label_date":r.label_date,"partition":part,"window":win,
                    "target_start_utc":r.start_utc.isoformat(),"source":p,
                    "anchor_available_utc":pd.Timestamp(a).isoformat(),
                    "lag_minutes":float(getattr(r,f"{p}_anchor_lag_min")),
                    "obs_returns_24h":int(getattr(r,f"{p}_obs_returns_24h")),
                    "strictly_before_target":bool(pd.Timestamp(a)<r.start_utc),
                })
    return pd.DataFrame(rows)

def main():
    panel,hashes=v2.load_panel()
    v2.audit_target_clocks(panel)
    panel=panel.reset_index(drop=True)
    panel["_key"]=np.arange(len(panel),dtype=int)

    xau=load_xau15(); si=load_fut15("SI.n.0"); pl=load_fut15("PL.n.0")
    panel=attach(panel,xau,"g")
    panel=attach(panel,si,"si")
    panel=attach(panel,pl,"pl")

    gf=feature_names("g"); sif=feature_names("si"); plf=feature_names("pl")
    req=CORE3+gf+sif+plf+["direction"]
    common=panel.dropna(subset=req).copy()

    # Hard no-leakage check.
    for p in ["g","si","pl"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():
            raise RuntimeError(f"{p}_ANCHOR_LEAK")
        if not common[f"{p}_anchor_lag_min"].gt(0).all():
            raise RuntimeError(f"{p}_NONPOSITIVE_LAG")
        if not common[f"{p}_anchor_lag_min"].le(MAX_ANCHOR_LAG_MIN).all():
            raise RuntimeError(f"{p}_STALE")

    variants={
        "CORE3_XAU15_FULL_IRIS":CORE3+gf,
        "CORE3_XAU15_SI15_FULL_IRIS":CORE3+gf+sif,
        "CORE3_XAU15_SI15_PL15_FULL_IRIS":CORE3+gf+sif+plf,
    }
    preds=[]
    old_min=v2.MIN_TRAIN
    v2.MIN_TRAIN=MIN_TRAIN
    try:
        for name,feats in variants.items():
            z=v2.causal_replay(common,name,feats)
            if not z.empty:preds.append(z)
    finally:
        v2.MIN_TRAIN=old_min
    pred=pd.concat(preds,ignore_index=True)
    mdf=v2.summarize(pred)

    cov=[]
    for (part,win),g in common.groupby(["partition","window"],sort=True):
        cov.append({
            "partition":part,"window":win,"common_rows":int(len(g)),
            "first_start":g.start_utc.min().isoformat(),"last_start":g.start_utc.max().isoformat(),
            "median_g_lag_min":float(g.g_anchor_lag_min.median()),
            "median_si_lag_min":float(g.si_anchor_lag_min.median()),
            "median_pl_lag_min":float(g.pl_anchor_lag_min.median()),
            "median_g_obs_returns_24h":float(g.g_obs_returns_24h.median()),
            "median_si_obs_returns_24h":float(g.si_obs_returns_24h.median()),
            "median_pl_obs_returns_24h":float(g.pl_obs_returns_24h.median()),
        })
    cdf=pd.DataFrame(cov)
    tsamp=timing_samples(common)

    pred.to_csv(OUT/"predictions_2023_2024.csv",index=False)
    mdf.to_csv(OUT/"metrics_2023_2024.csv",index=False)
    cdf.to_csv(OUT/"coverage.csv",index=False)
    tsamp.to_csv(OUT/"timing_samples.csv",index=False)

    summary={
        "status":"SESSION_IRIS15_CROSSMETAL_V1_COMPLETE",
        "scope":"2023-2024 only; 2025/2026 unopened",
        "representation":{
            "daily_core3":"unchanged raw-derived NOVA CORE3 including Gold sigma20",
            "intraday_frequency":"15-minute",
            "xau_source":"governed Twelve XAU/USD 15m backfill",
            "silver_source":"Databento GLBX.MDP3 SI.n.0, 1m->15m validated archive",
            "platinum_source":"Databento GLBX.MDP3 PL.n.0, 1m->15m validated archive",
            "anchor_rule":"latest completed 15m bar with available_at STRICTLY LESS THAN target start",
            "max_anchor_lag_minutes":MAX_ANCHOR_LAG_MIN,
            "ret_horizons_hours":HRET,
            "lag2_semantics":"exact 1h return ending 2h before the anchor",
            "rv_horizons_hours":RVH,
            "rv_sampling":"observed 15m closes inside fixed clock window; squared log-return sum",
            "session_ret":"EXCLUDED; prior NY-calendar session_ret is not equivalent to frozen target-session clock",
            "shape":"IRIS shape family retained; slopes and age-of-extreme are expressed in clock time",
        },
        "source_hashes":{
            "xau15":sha256(XAU15),"si_pl_derived15":sha256(SIPL15),
            "daily_stak":hashes,
        },
        "rows":{"panel_before_intraday_gate":int(len(panel)),"common_feature_rows":int(len(common))},
        "features":variants,
        "metrics":mdf.to_dict("records"),
        "guardrails":[
            "All target clocks asserted against frozen Sobti-5/WGC-3 America/New_York contract.",
            "No 15m bar completing at target start is used.",
            "Return horizons and lag2 use exact clock timestamps, not last-N-bar approximations.",
            "Daily sigma20 is retained through CORE3.",
            "IRIS realized-volatility, semivolatility and shape families are retained at fixed clock horizons using 15m observations.",
            "All three model variants use exactly the same common target rows.",
            "Only matured same-window labels enter training.",
            "2025/2026 remain unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION IRIS15 CROSS-METAL V1","",
        "**Status:** SESSION_IRIS15_CROSSMETAL_V1_COMPLETE","",
        "- 2023–2024 only; 2025/2026 unopened.",
        "- Daily CORE3 retained, including Gold sigma20.",
        "- Intraday IRIS lag/realized-volatility/semivolatility/shape families rebuilt from 15m data.",
        "- Exact target-clock returns; strict pre-target 15m anchor.",
        "- Prior NY-calendar session_ret intentionally excluded.","",
        "## Metrics","",
        "| Model | Partition | Window | Period | N | Acc | Balanced | UP recall | DOWN recall | Brier |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in mdf.itertuples(index=False):
        lines.append(
            f"| {r.model} | {r.partition} | {r.window} | {r.period} | {int(r.n)} | "
            f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |"
        )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({
        "status":summary["status"],"common_feature_rows":len(common),
        "metric_rows":len(mdf),"coverage":cov
    },indent=2,default=str))

if __name__=="__main__":
    main()
