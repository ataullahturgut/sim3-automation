from __future__ import annotations

import importlib.util, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V1_PATH=AX/"tools"/"gold_session_iris15_crossmetal_v1_20261006.py"
V2_PATH=AX/"tools"/"gold_session_structural_iris_crossmetal_v2_clocksafe_20261006.py"
OUT=AX/"SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m
v1=loadmod("iris15v1",V1_PATH)
base=v1.v2

CORE3=list(v1.CORE3)
HRET=list(v1.HRET); RVH=list(v1.RVH)
MIN_TRAIN=180

def in_ny_maintenance(t):
    ny=pd.Timestamp(t).tz_convert("America/New_York")
    return ny.hour==17

def is_wgc_asia_reopen(part,win,target_start):
    if part!="WGC_2026_NY3" or win!="ASIA":return False
    ny=pd.Timestamp(target_start).tz_convert("America/New_York")
    return ny.hour==18 and ny.minute==0

def source_index(raw):
    q=raw.sort_values("available_at_utc").copy().reset_index(drop=True)
    q["logp"]=np.log(q.value.astype(float))
    av=pd.DatetimeIndex(q.available_at_utc)
    return q,av

def asof_state(q,av,cutoff,allow_maintenance=True):
    cutoff=pd.Timestamp(cutoff)
    i=int(av.searchsorted(cutoff,side="right")-1)
    if i<0:return None
    actual=pd.Timestamp(av[i]); stale=(cutoff-actual).total_seconds()/60.0
    if stale<0:return None
    if stale>0:
        if not allow_maintenance or not in_ny_maintenance(cutoff) or stale>60:
            return None
    return i,float(q.iloc[i].logp),actual,float(stale)

def slope_time(times,vals):
    if len(vals)<2:return np.nan
    x=(pd.DatetimeIndex(times)-pd.Timestamp(times[0])).total_seconds().to_numpy(float)/3600.0
    y=np.asarray(vals,float); xm=x.mean();ym=y.mean();den=np.sum((x-xm)**2)
    return np.nan if den<=0 else float(np.sum((x-xm)*(y-ym))/den)

def max_drawdown(a):
    a=np.asarray(a,float)
    return np.nan if len(a)<2 else float(np.min(a-np.maximum.accumulate(a)))

def calc(q,av,target_start,part,win,prefix):
    T=pd.Timestamp(target_start)
    i=int(av.searchsorted(T,side="left")-1)  # strict pre-target availability
    if i<0:return None
    A=pd.Timestamp(av[i]); anchor_lag=(T-A).total_seconds()/60.0
    if is_wgc_asia_reopen(part,win,T):
        if not (0<anchor_lag<=60):return None
        anchor_maintenance_exception=True
    else:
        if not (0<anchor_lag<=30):return None
        anchor_maintenance_exception=False
    anchor=float(q.iloc[i].logp)
    f={f"{prefix}_anchor_available":A,f"{prefix}_anchor_lag_min":anchor_lag,
       f"{prefix}_anchor_maintenance_exception":anchor_maintenance_exception}
    stales=[]

    for h in HRET:
        z=asof_state(q,av,A-pd.Timedelta(hours=h),True)
        if z is None:return None
        _,ref,actual,stale=z
        f[f"{prefix}_ret_{h}h"]=anchor-ref
        f[f"{prefix}_ret_{h}h_ref_stale_min"]=stale
        stales.append(stale)

    z2=asof_state(q,av,A-pd.Timedelta(hours=2),True)
    z3=asof_state(q,av,A-pd.Timedelta(hours=3),True)
    if z2 is None or z3 is None:return None
    f[f"{prefix}_lag2"]=z2[1]-z3[1]
    stales += [z2[3],z3[3]]

    cache={}
    for h in RVH:
        cut=A-pd.Timedelta(hours=h)
        z=asof_state(q,av,cut,True)
        if z is None:return None
        ri,ref,actual,stale=z; stales.append(stale)
        # Exact-clock as-of path: carry the last known real price to the cutoff only
        # when cutoff lies inside the known 17:00-18:00 NY maintenance interval.
        w=q[(q.available_at_utc>cut)&(q.available_at_utc<=A)].copy()
        times=[cut]; vals=[ref]
        times += list(pd.DatetimeIndex(w.available_at_utc))
        vals += list(w.logp.astype(float))
        # Deduplicate any coincident point while preserving last value.
        tmp=pd.DataFrame({"t":times,"v":vals}).drop_duplicates("t",keep="last").sort_values("t")
        vals=np.asarray(tmp.v,float); times=pd.DatetimeIndex(tmp.t)
        if len(vals)<2:return None
        dr=np.diff(vals); rv=float(np.sqrt(np.sum(dr*dr)))
        f[f"{prefix}_rv_{h}"]=rv
        cache[h]=(times,vals,dr)

    t24,v24,d24=cache[24]
    pos=np.clip(d24,0,None);neg=np.clip(d24,None,0)
    up=float(np.sqrt(np.sum(pos*pos)));dn=float(np.sqrt(np.sum(neg*neg)))
    trough=float(np.min(v24));hi=float(np.max(v24));rv24=float(f[f"{prefix}_rv_24"])
    f[f"{prefix}_up_semivol_24"]=up
    f[f"{prefix}_down_semivol_24"]=dn
    f[f"{prefix}_down_up_semivol_ratio_24"]=dn/(up+1e-8)
    f[f"{prefix}_jump_concentration_24"]=float(np.max(np.abs(d24))/(rv24+1e-8))
    f[f"{prefix}_range_24"]=hi-trough
    f[f"{prefix}_upfrac_24"]=float(np.mean(d24>0))
    f[f"{prefix}_max_drawdown_24"]=max_drawdown(v24)
    f[f"{prefix}_recovery_24"]=anchor-trough
    f[f"{prefix}_close_location_24"]=(anchor-trough)/(hi-trough+1e-8)
    for h in [6,24]:
        tt,vv,_=cache[h];f[f"{prefix}_slope_{h}"]=slope_time(tt,vv)
    end_times=t24[1:]
    imax=int(np.argmax(d24));imin=int(np.argmin(d24))
    f[f"{prefix}_age_max_pos_24"]=(A-end_times[imax]).total_seconds()/3600.0
    f[f"{prefix}_age_max_neg_24"]=(A-end_times[imin]).total_seconds()/3600.0
    f[f"{prefix}_obs_returns_24h"]=int(len(d24))
    f[f"{prefix}_max_reference_stale_min"]=float(max(stales) if stales else 0)
    return f

def attach(panel,raw,prefix):
    q,av=source_index(raw); rec=[]
    for r in panel.itertuples(index=False):
        f=calc(q,av,r.start_utc,r.partition,r.window,prefix)
        if f is None:rec.append({"row_id":r.row_id})
        else:f["row_id"]=r.row_id;rec.append(f)
    return panel.merge(pd.DataFrame(rec),on="row_id",how="left",validate="one_to_one")

def main():
    panel,hashes=base.load_panel();base.audit_target_clocks(panel)
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))
    xau=v1.load_xau15();si=v1.load_fut15("SI.n.0");pl=v1.load_fut15("PL.n.0")
    panel=attach(panel,xau,"g");panel=attach(panel,si,"si");panel=attach(panel,pl,"pl")
    gf=v1.feature_names("g");sif=v1.feature_names("si");plf=v1.feature_names("pl")
    common=panel.dropna(subset=CORE3+gf+sif+plf+["direction"]).copy()

    for p in ["g","si","pl"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():raise RuntimeError(f"{p}_LEAK")
        # Any stale reference >0 must be maintenance-derived and capped <=60 by calc().
        if common[f"{p}_max_reference_stale_min"].gt(60).any():raise RuntimeError(f"{p}_REF_STALE")

    variants={
      "CORE3_XAU15_FULL_IRIS_MA":CORE3+gf,
      "CORE3_XAU15_SI15_FULL_IRIS_MA":CORE3+gf+sif,
      "CORE3_XAU15_SI15_PL15_FULL_IRIS_MA":CORE3+gf+sif+plf,
    }
    preds=[]; old=base.MIN_TRAIN;base.MIN_TRAIN=MIN_TRAIN
    try:
        for n,feats in variants.items():
            z=base.causal_replay(common,n,feats)
            if not z.empty:preds.append(z)
    finally:base.MIN_TRAIN=old
    pred=pd.concat(preds,ignore_index=True);mdf=base.summarize(pred)

    cov=[]
    for (part,win),g in common.groupby(["partition","window"],sort=True):
        cov.append({
          "partition":part,"window":win,"common_rows":int(len(g)),
          "first_start":g.start_utc.min().isoformat(),"last_start":g.start_utc.max().isoformat(),
          "median_g_lag_min":float(g.g_anchor_lag_min.median()),
          "median_si_lag_min":float(g.si_anchor_lag_min.median()),
          "median_pl_lag_min":float(g.pl_anchor_lag_min.median()),
          "max_g_ref_stale_min":float(g.g_max_reference_stale_min.max()),
          "max_si_ref_stale_min":float(g.si_max_reference_stale_min.max()),
          "max_pl_ref_stale_min":float(g.pl_max_reference_stale_min.max()),
          "anchor_maintenance_exceptions":int(g.g_anchor_maintenance_exception.astype(bool).sum()),
        })
    cdf=pd.DataFrame(cov)

    # Samples proving Asia maintenance handling.
    samp=common[common.window.isin(["ASIA_MORNING_LIT","ASIA"])][[
      "label_date","partition","window","start_utc",
      "g_anchor_available","g_anchor_lag_min","g_max_reference_stale_min",
      "si_anchor_available","si_anchor_lag_min","si_max_reference_stale_min",
      "pl_anchor_available","pl_anchor_lag_min","pl_max_reference_stale_min"
    ]].head(40)

    pred.to_csv(OUT/"predictions_2023_2024.csv",index=False)
    mdf.to_csv(OUT/"metrics_2023_2024.csv",index=False)
    cdf.to_csv(OUT/"coverage.csv",index=False)
    samp.to_csv(OUT/"asia_maintenance_samples.csv",index=False)

    summary={
      "status":"SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_COMPLETE",
      "scope":"2023-2024 only; 2025/2026 unopened",
      "clock_policy":{
        "normal_anchor":"latest completed 15m close strictly before target; <=30m old",
        "WGC_Asia_18NY_anchor":"known 17:00-18:00 NY maintenance exception; last real pre-maintenance close allowed up to 60m old",
        "reference_cutoff":"exact clock cutoff relative to anchor",
        "maintenance_reference":"if cutoff falls inside 17:00-18:00 NY maintenance only, use last known real price as-of cutoff; max staleness 60m",
        "outside_maintenance":"no stale reference/forward-fill permitted",
        "synthetic_market_bar":"NONE; maintenance as-of state is metadata-level carry of last observed real price, not a fabricated OHLC bar",
      },
      "rows":{"panel":int(len(panel)),"common":int(len(common))},
      "features":variants,"metrics":mdf.to_dict("records"),
      "coverage":cov,
      "guardrails":[
        "Daily CORE3 including Gold sigma20 retained.",
        "IRIS lag2, RV, semivolatility and shape features retained on 15m input.",
        "No target-start bar is used.",
        "Maintenance handling is deterministic from the known NY 17:00-18:00 market break, not outcome-selected.",
        "All variants use identical common rows.",
        "Only matured same-window outcomes enter training.",
        "2025/2026 remain unopened."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    lines=["# SESSION IRIS15 CROSS-METAL V2 — MAINTENANCE-AWARE","",
      "**Status:** SESSION_IRIS15_CROSSMETAL_V2_MAINTAWARE_COMPLETE","",
      "- 2023–2024 only; 2025/2026 unopened.",
      "- Known 17:00–18:00 New York maintenance is handled as an as-of state, never as a fabricated market bar.",
      "- Outside maintenance, stale exact-clock references are rejected.","",
      "## Metrics","",
      "| Model | Partition | Window | Period | N | Acc | Balanced | UP recall | DOWN recall | Brier |",
      "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in mdf.itertuples(index=False):
        lines.append(f"| {r.model} | {r.partition} | {r.window} | {r.period} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"common":len(common),"coverage":cov,"metric_rows":len(mdf)},indent=2))

if __name__=="__main__":main()
