from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
MA15_PATH=AX/"tools"/"gold_session_iris15_crossmetal_v2_maintaware_20261006.py"
H1_PATH=AX/"tools"/"gold_session_iris_hourly_raw_replay_v1_20261006.py"
SIPL1H=AX/"GOLD_DATABENTO_SI_PL_NATIVE_OHLCV1H_N0_2022_2024.csv.gz"
OUT=AX/"SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m

ma15=loadmod("ma15",MA15_PATH)
h1mod=loadmod("h1mod",H1_PATH)
v15=ma15.v1
base=ma15.base

CORE3=list(ma15.CORE3)
HRET=list(ma15.HRET)
RVH=list(ma15.RVH)
MIN_TRAIN=180

def maintenance_state_cutoff(t):
    ny=pd.Timestamp(t).tz_convert("America/New_York")
    # Registered metals maintenance: 17:00 <= time <= 18:00 NY.
    # At exactly 18:00, no post-reopen bar has completed yet; 17:00 remains
    # the last genuinely observed state.
    return (ny.hour==17) or (ny.hour==18 and ny.minute==0 and ny.second==0)

def is_wgc_asia_reopen(part,win,target_start):
    if part!="WGC_2026_NY3" or win!="ASIA": return False
    ny=pd.Timestamp(target_start).tz_convert("America/New_York")
    return ny.hour==18 and ny.minute==0

def load_fut1h(symbol):
    q=pd.read_csv(SIPL1H,compression="gzip")
    req={"symbol","ts_event","close"}
    if not req.issubset(q.columns):
        raise RuntimeError(f"SIPL1H_SCHEMA_FAIL:{q.columns.tolist()}")
    q=q[q.symbol.astype(str).eq(symbol)][["ts_event","close"]].copy()
    q["ts"]=pd.to_datetime(q.pop("ts_event"),utc=True,errors="raise")
    q["value"]=pd.to_numeric(q.pop("close"),errors="raise")
    q=q.dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    if q.empty or (q.value<=0).any(): raise RuntimeError(f"{symbol}_BAD_1H")
    q["available_at_utc"]=q.ts+pd.Timedelta(hours=1)
    return q[["ts","available_at_utc","value"]].reset_index(drop=True)


def load_xau1h_from_15m():
    q=v15.load_xau15().copy()
    q["hour"]=q.ts.dt.floor("1h")
    q["minute"]=q.ts.dt.minute
    rows=[]
    for hour,g in q.groupby("hour",sort=True):
        mins=tuple(sorted(set(map(int,g.minute))))
        if len(g)==4 and mins==(0,15,30,45):
            rows.append({
              "ts":pd.Timestamp(hour),
              "available_at_utc":pd.Timestamp(hour)+pd.Timedelta(hours=1),
              "value":float(g.sort_values("ts").iloc[-1].value),
            })
    out=pd.DataFrame(rows)
    if out.empty: raise RuntimeError("NO_DERIVED_XAU1H")
    return out.sort_values("ts").reset_index(drop=True)

def source_index(raw):
    q=raw.sort_values("available_at_utc").copy().reset_index(drop=True)
    q["logp"]=np.log(q.value.astype(float))
    return q,pd.DatetimeIndex(q.available_at_utc)

def asof_state(q,av,cutoff):
    cutoff=pd.Timestamp(cutoff)
    i=int(av.searchsorted(cutoff,side="right")-1)
    if i<0:return None
    actual=pd.Timestamp(av[i])
    stale=(cutoff-actual).total_seconds()/60.0
    if stale<0:return None
    if stale>0 and (not maintenance_state_cutoff(cutoff) or stale>60):
        return None
    return i,float(q.iloc[i].logp),actual,float(stale)

def slope_time(times,vals):
    if len(vals)<2:return np.nan
    tt=pd.DatetimeIndex(times)
    x=(tt-tt[0]).total_seconds().to_numpy(float)/3600.0
    y=np.asarray(vals,float);xm=x.mean();ym=y.mean();den=np.sum((x-xm)**2)
    return np.nan if den<=0 else float(np.sum((x-xm)*(y-ym))/den)

def max_drawdown(a):
    a=np.asarray(a,float)
    return np.nan if len(a)<2 else float(np.min(a-np.maximum.accumulate(a)))

def calc_generic(q,av,target_start,part,win,prefix,resolution):
    T=pd.Timestamp(target_start)
    i=int(av.searchsorted(T,side="left")-1)  # STRICTLY before target
    if i<0:return None
    A=pd.Timestamp(av[i]); anchor_lag=(T-A).total_seconds()/60.0

    if resolution=="15m":
        max_lag=60.0 if is_wgc_asia_reopen(part,win,T) else 30.0
    elif resolution=="1h":
        max_lag=60.0
    else:
        raise ValueError(resolution)
    if not (0<anchor_lag<=max_lag):return None

    anchor=float(q.iloc[i].logp)
    f={
      f"{prefix}_anchor_available":A,
      f"{prefix}_anchor_lag_min":float(anchor_lag),
      f"{prefix}_anchor_maintenance_exception":bool(is_wgc_asia_reopen(part,win,T) and anchor_lag>30),
    }
    stales=[]

    for h in HRET:
        z=asof_state(q,av,A-pd.Timedelta(hours=h))
        if z is None:return None
        _,ref,actual,stale=z
        f[f"{prefix}_ret_{h}h"]=anchor-ref
        f[f"{prefix}_ret_{h}h_ref_stale_min"]=stale
        stales.append(stale)

    z2=asof_state(q,av,A-pd.Timedelta(hours=2))
    z3=asof_state(q,av,A-pd.Timedelta(hours=3))
    if z2 is None or z3 is None:return None
    f[f"{prefix}_lag2"]=z2[1]-z3[1]
    stales += [z2[3],z3[3]]

    cache={}
    for h in RVH:
        cut=A-pd.Timedelta(hours=h)
        z=asof_state(q,av,cut)
        if z is None:return None
        _,ref,_,stale=z;stales.append(stale)
        w=q[(q.available_at_utc>cut)&(q.available_at_utc<=A)].copy()
        times=[cut]+list(pd.DatetimeIndex(w.available_at_utc))
        vals=[ref]+list(w.logp.astype(float))
        tmp=pd.DataFrame({"t":times,"v":vals}).drop_duplicates("t",keep="last").sort_values("t")
        tt=pd.DatetimeIndex(tmp.t);vv=np.asarray(tmp.v,float)
        if len(vv)<2:return None
        dr=np.diff(vv)
        f[f"{prefix}_rv_{h}"]=float(np.sqrt(np.sum(dr*dr)))
        cache[h]=(tt,vv,dr)

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
        tt,vv,_=cache[h]
        f[f"{prefix}_slope_{h}"]=slope_time(tt,vv)

    end_times=t24[1:]
    imax=int(np.argmax(d24));imin=int(np.argmin(d24))
    f[f"{prefix}_age_max_pos_24"]=(A-end_times[imax]).total_seconds()/3600.0
    f[f"{prefix}_age_max_neg_24"]=(A-end_times[imin]).total_seconds()/3600.0
    f[f"{prefix}_obs_returns_24h"]=int(len(d24))
    f[f"{prefix}_max_reference_stale_min"]=float(max(stales) if stales else 0)
    return f

def attach(panel,raw,prefix,resolution):
    q,av=source_index(raw);rec=[]
    for r in panel.itertuples(index=False):
        f=calc_generic(q,av,r.start_utc,r.partition,r.window,prefix,resolution)
        if f is None:rec.append({"row_id":r.row_id})
        else:
            f["row_id"]=r.row_id
            rec.append(f)
    return panel.merge(pd.DataFrame(rec),on="row_id",how="left",validate="one_to_one")

def feature_names(prefix):
    return v15.feature_names(prefix)

def paired_summary(pred):
    families={
      "XAU_ONLY":("IRIS15_XAU","IRIS1H_XAU"),
      "XAU_SI":("IRIS15_XAU_SI","IRIS1H_XAU_SI"),
      "XAU_SI_PL":("IRIS15_XAU_SI_PL","IRIS1H_XAU_SI_PL"),
    }
    rows=[]
    keys=["label_date","partition","window","start_utc","y_up"]
    for fam,(m15,m1) in families.items():
        a=pred[pred.model.eq(m15)].copy()
        b=pred[pred.model.eq(m1)].copy()
        z=a.merge(b,on=keys,suffixes=("_15m","_1h"),validate="one_to_one")
        for (part,win),g in z.groupby(["partition","window"],sort=True):
            y=g.y_up.to_numpy(int)
            p15=g.p_up_15m.to_numpy(float);p1=g.p_up_1h.to_numpy(float)
            m15s=base.metrics(y,p15);m1s=base.metrics(y,p1)
            c15=(p15>=.5).astype(int)==y;c1=(p1>=.5).astype(int)==y
            rows.append({
              "family":fam,"partition":part,"window":win,"n":int(len(g)),
              "acc_15m":m15s["accuracy"],"acc_1h":m1s["accuracy"],
              "delta_acc_pp":100*(m15s["accuracy"]-m1s["accuracy"]),
              "ba_15m":m15s["balanced_accuracy"],"ba_1h":m1s["balanced_accuracy"],
              "delta_ba_pp":100*(m15s["balanced_accuracy"]-m1s["balanced_accuracy"]),
              "brier_15m":m15s["brier"],"brier_1h":m1s["brier"],
              "brier_improvement_15m":m1s["brier"]-m15s["brier"],
              "only_15m_correct":int((c15&~c1).sum()),
              "only_1h_correct":int((c1&~c15).sum()),
              "both_correct":int((c1&c15).sum()),
              "both_wrong":int((~c1&~c15).sum()),
            })
    return pd.DataFrame(rows)

def main():
    panel,hashes=base.load_panel();base.audit_target_clocks(panel)
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))

    # 15m governed sources
    x15=v15.load_xau15();si15=v15.load_fut15("SI.n.0");pl15=v15.load_fut15("PL.n.0")
    # 1h governed sources
    x1=load_xau1h_from_15m();si1=load_fut1h("SI.n.0");pl1=load_fut1h("PL.n.0")

    for raw,prefix,res in [
      (x15,"g15","15m"),(si15,"si15","15m"),(pl15,"pl15","15m"),
      (x1,"g1h","1h"),(si1,"si1h","1h"),(pl1,"pl1h","1h"),
    ]:
        panel=attach(panel,raw,prefix,res)

    f={
      "g15":feature_names("g15"),"si15":feature_names("si15"),"pl15":feature_names("pl15"),
      "g1h":feature_names("g1h"),"si1h":feature_names("si1h"),"pl1h":feature_names("pl1h"),
    }

    all_req=CORE3+sum(f.values(),[])+["direction"]
    common=panel.dropna(subset=all_req).copy()

    # Same target rows for every resolution and family.
    for p in ["g15","si15","pl15","g1h","si1h","pl1h"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():
            raise RuntimeError(f"{p}_ANCHOR_LEAK")
        if common[f"{p}_max_reference_stale_min"].gt(60).any():
            raise RuntimeError(f"{p}_REFERENCE_STALE")

    variants={
      "IRIS15_XAU":CORE3+f["g15"],
      "IRIS1H_XAU":CORE3+f["g1h"],
      "IRIS15_XAU_SI":CORE3+f["g15"]+f["si15"],
      "IRIS1H_XAU_SI":CORE3+f["g1h"]+f["si1h"],
      "IRIS15_XAU_SI_PL":CORE3+f["g15"]+f["si15"]+f["pl15"],
      "IRIS1H_XAU_SI_PL":CORE3+f["g1h"]+f["si1h"]+f["pl1h"],
    }

    preds=[];old=base.MIN_TRAIN;base.MIN_TRAIN=MIN_TRAIN
    try:
        for name,feats in variants.items():
            z=base.causal_replay(common,name,feats)
            if not z.empty:preds.append(z)
    finally:
        base.MIN_TRAIN=old
    pred=pd.concat(preds,ignore_index=True)
    mdf=base.summarize(pred)
    pair=paired_summary(pred)

    cov=[]
    for (part,win),g in common.groupby(["partition","window"],sort=True):
        cov.append({
          "partition":part,"window":win,"common_rows":int(len(g)),
          "first_start":g.start_utc.min().isoformat(),"last_start":g.start_utc.max().isoformat(),
          "xau15_median_anchor_lag_min":float(g.g15_anchor_lag_min.median()),
          "xau1h_median_anchor_lag_min":float(g.g1h_anchor_lag_min.median()),
          "si15_median_anchor_lag_min":float(g.si15_anchor_lag_min.median()),
          "si1h_median_anchor_lag_min":float(g.si1h_anchor_lag_min.median()),
          "pl15_median_anchor_lag_min":float(g.pl15_anchor_lag_min.median()),
          "pl1h_median_anchor_lag_min":float(g.pl1h_anchor_lag_min.median()),
          "g15_median_obs_returns_24h":float(g.g15_obs_returns_24h.median()),
          "g1h_median_obs_returns_24h":float(g.g1h_obs_returns_24h.median()),
        })
    cdf=pd.DataFrame(cov)

    pred.to_csv(OUT/"predictions.csv",index=False)
    mdf.to_csv(OUT/"metrics.csv",index=False)
    pair.to_csv(OUT/"paired_resolution_comparison.csv",index=False)
    cdf.to_csv(OUT/"coverage.csv",index=False)

    summary={
      "status":"SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_COMPLETE",
      "scope":"2023-2024 development chronology only; 2025/2026 unopened",
      "comparison_contract":{
        "same_target_rows":True,
        "same_daily_CORE3":True,
        "same_model":"StandardScaler + LogisticRegression C=1.0",
        "same_min_matured_same_window_train":MIN_TRAIN,
        "same_feature_families":"ret 1/3/6/12/24/48h, lag2, RV 6/12/24/48h, semivol, jump/range, shape",
        "session_ret":"excluded from both",
        "difference_under_test":"intraday sampling resolution and resulting strictly-pretarget anchor freshness/path sampling",\n        "xau_1h_source":"deterministically aggregated from the same governed XAU/USD 15m archive; native Twelve 1h is not used in this binding comparison",
        "maintenance":"same deterministic NY 17:00-18:00 as-of-state rule for both resolutions",
      },
      "common_rows":int(len(common)),
      "coverage":cov,
      "paired":pair.to_dict("records"),
      "metrics":mdf.to_dict("records"),
      "guardrails":[
        "All six models train and score on the same common target panel.",
        "No target-start bar is used at either resolution.",
        "15m and 1h use identical clock-horizon labels rather than last-N-bar horizon labels.",
        "Daily CORE3 including sigma20 is identical.",
        "Only matured same-window outcomes enter training.",
        "2025 and 2026 remain unopened."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# SESSION IRIS — MATCHED 15m vs DERIVED-1h RESOLUTION TEST","",
      "**Status:** SESSION_IRIS_RESOLUTION_MATCHED_V2_DERIVEDXAU_COMPLETE","",
      "- Same target rows, same CORE3, same model, same feature families.",
      "- XAU 1h is derived from the same governed XAU 15m archive; native 1h vendor bars are excluded from this binding comparison.\n      "- Difference under test: 15m vs 1h intraday sampling / pre-target freshness.",",
      "- 2025/2026 unopened.","",
      "## Paired comparison","",
      "| Family | Partition | Window | N | 15m Acc | 1h Acc | ΔAcc pp | 15m BA | 1h BA | ΔBA pp | 15m Brier | 1h Brier | 15m-only correct | 1h-only correct |",
      "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in pair.itertuples(index=False):
        lines.append(
          f"| {r.family} | {r.partition} | {r.window} | {r.n} | "
          f"{100*r.acc_15m:.2f}% | {100*r.acc_1h:.2f}% | {r.delta_acc_pp:+.2f} | "
          f"{100*r.ba_15m:.2f}% | {100*r.ba_1h:.2f}% | {r.delta_ba_pp:+.2f} | "
          f"{r.brier_15m:.4f} | {r.brier_1h:.4f} | {r.only_15m_correct} | {r.only_1h_correct} |"
        )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"common_rows":len(common),"paired":pair.to_dict("records")},indent=2))

if __name__=="__main__":
    main()
