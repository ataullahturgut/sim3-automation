from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
VEGAP=AX/"tools"/"gold_session_vega_v1_20261007.py"
GLOBAL25=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
OUT=AX/"SESSION_VEGA_FROZEN_2025_TRANSPORT_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

v=loadmod("vega",VEGAP)
FEATURES=list(v.FEATURES)
THRESH=float(v.THRESH)
MIN_TRAIN=int(v.MIN_TRAIN)
SEED=int(v.SEED)
EPS=1e-8

PART="WGC_2026_NY3"
WIN="US"
BASELINE="PATH_GLOBAL_1H"

def asbool(s):
    return s.astype(str).str.lower().eq("true")

def load_targets_extended():
    frames=[]
    w=pd.read_csv(v.rift.WARM)
    w=w[asbool(w.final_trainable)].copy()
    frames.append(w)
    for p in [v.rift.WGC,v.rift.SOB]:
        q=pd.read_csv(p)
        q=q[asbool(q.final_trainable)].copy()
        q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
        q=q[q.start_utc.dt.year.isin([2023,2024,2025])].copy()
        frames.append(q)
    q=pd.concat(frames,ignore_index=True,sort=False)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["label_date"]=pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    q["year"]=q.start_utc.dt.year
    q["y_up"]=(q.direction=="UP").astype(int)
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def load_raw15_extended():
    a=pd.read_csv(v.rift.RAW22,usecols=["dt_utc","close"])
    b=pd.read_csv(v.rift.RAW35,usecols=["dt_utc","close"])
    for q in [a,b]:
        q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True)
        q["close"]=pd.to_numeric(q.close,errors="raise")
    q=pd.concat([a,b],ignore_index=True).sort_values("dt_utc")
    q=q[q.dt_utc<pd.Timestamp("2026-01-01",tz="UTC")].copy()
    d=q[q.duplicated("dt_utc",keep=False)]
    if not d.empty and d.groupby("dt_utc").close.nunique().gt(1).any():
        raise RuntimeError("RAW_OVERLAP_CONFLICT")
    q=q.drop_duplicates("dt_utc",keep="last")
    q=q.rename(columns={"dt_utc":"ts","close":"value"})
    q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
    return q[["ts","available_at_utc","value"]].reset_index(drop=True)

def load_gvz_extended():
    q=pd.read_csv(v.GVZ_PATH)
    q["date"]=pd.to_datetime(q.date,errors="raise")
    q["value"]=pd.to_numeric(q.value,errors="raise")
    q=q.dropna().sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True)
    if q.date.max()<pd.Timestamp("2025-12-01"):
        raise RuntimeError(f"GVZ_2025_COVERAGE_FAIL max={q.date.max()}")
    return q

def gvz_features(gvz,origin_ny_date):
    cutoff=pd.Timestamp(origin_ny_date)-pd.Timedelta(days=1)
    q=gvz[gvz.date<=cutoff]
    if len(q)<253:return None
    vals=q.value.to_numpy(float)
    cur=float(vals[-1])
    hist252=vals[-253:-1]
    med20=float(np.median(vals[-21:-1]))
    mu=float(np.mean(hist252));sd=float(np.std(hist252,ddof=0))
    return {
        "gvz_date_used":q.iloc[-1].date,
        "gvz_level":cur,
        "gvz_z252":(cur-mu)/(sd if sd>EPS else 1.0),
        "gvz_r1":float(math.log(cur/vals[-2])),
        "gvz_r3":float(math.log(cur/vals[-4])),
        "gvz_r5":float(math.log(cur/vals[-6])),
        "gvz_vs_med20":float(math.log(cur/med20)),
    }

def build_panel():
    p=load_targets_extended().reset_index(drop=True)
    p["row_id"]=np.arange(len(p))
    p=v.rift.ma15.attach(p,load_raw15_extended(),"g")
    req=["g_ret_12h","g_rv_12","g_rv_24","g_rv_48","g_anchor_available","g_max_reference_stale_min"]
    p=p.dropna(subset=req+["direction"]).copy()
    if not (p.g_anchor_available<p.start_utc).all():raise RuntimeError("VEGA_XAU_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():raise RuntimeError("VEGA_REFERENCE_STALE")

    gvz=load_gvz_extended()
    rows=[]
    for r in p.itertuples(index=False):
        origin_ny_date=pd.Timestamp(r.start_utc).tz_convert("America/New_York").date()
        gf=gvz_features(gvz,origin_ny_date)
        if gf is None:continue
        implied_daily=float(gf["gvz_level"])/100.0/math.sqrt(252.0)
        rv24=float(r.g_rv_24)
        rv48_daily=float(r.g_rv_48)/math.sqrt(2.0)
        trend_strength=abs(float(r.g_ret_12h))/(float(r.g_rv_12)+EPS)
        d=r._asdict()
        d.update({
            **gf,
            "origin_ny_date":str(origin_ny_date),
            "trend_strength":trend_strength,
            "iv_rv24_gap":float(math.log((implied_daily+EPS)/(rv24+EPS))),
            "iv_rv48_gap":float(math.log((implied_daily+EPS)/(rv48_daily+EPS))),
            "gvz_shock_x_trend":float(gf["gvz_r3"])*trend_strength,
            "momentum_up":int(float(r.g_ret_12h)>=0),
        })
        d["reversal_target"]=int(int(r.y_up)!=d["momentum_up"])
        rows.append(d)

    q=pd.DataFrame(rows)
    if q.empty:raise RuntimeError("VEGA_EMPTY")
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["year"]=q.start_utc.dt.year
    q["month_key"]=q.start_utc.dt.to_period("M").astype(str)
    q["gvz_date_used"]=pd.to_datetime(q.gvz_date_used)
    origin_dates=pd.to_datetime(q.origin_ny_date)
    if not (q.gvz_date_used<=origin_dates-pd.Timedelta(days=1)).all():
        raise RuntimeError("VEGA_GVZ_DMINUS1_FAIL")
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def model():
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def predict_2025(panel):
    rows=[]
    g=panel[(panel.partition==PART)&(panel.window==WIN)].sort_values("start_utc").reset_index(drop=True)
    teall=g[g.year.eq(2025)].copy()
    for mo in sorted(teall.month_key.unique()):
        te=teall[teall.month_key.eq(mo)].copy()
        if te.empty:continue
        cut=te.start_utc.min()
        tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
        if len(tr)<MIN_TRAIN or tr.reversal_target.nunique()<2:continue
        X=tr[FEATURES].astype(float).to_numpy()
        Xt=te[FEATURES].astype(float).to_numpy()
        sc=StandardScaler().fit(X)
        m=model().fit(sc.transform(X),tr.reversal_target.to_numpy(int))
        pp=m.predict_proba(sc.transform(Xt))[:,1]
        for r,pv in zip(te.itertuples(index=False),pp):
            rows.append({
                "partition":PART,"window":WIN,"label_date":r.label_date,
                "start_utc":r.start_utc,"end_utc":r.end_utc,"year":2025,
                "y_up":int(r.y_up),"momentum_up":int(r.momentum_up),
                "reversal_target":int(r.reversal_target),"p_reversal":float(pv),
                "gvz_date_used":pd.Timestamp(r.gvz_date_used).date().isoformat(),
                "train_n":int(len(tr))
            })
    return pd.DataFrame(rows)

def load_baseline():
    q=pd.read_csv(GLOBAL25)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["label_date"]=pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    q=q[(q.partition==PART)&(q.window==WIN)&(q.model==BASELINE)].copy()
    return q[["partition","window","label_date","start_utc","y_up","p_up"]]

def metric(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
    }

def apply(base,vega):
    key=["partition","window","label_date","start_utc","y_up"]
    z=base.merge(vega[key+["momentum_up","p_reversal","gvz_date_used","train_n"]],
                 on=key,how="inner",validate="one_to_one")
    if z.empty:raise RuntimeError("NO_MATCHED_2025")
    bp=(z.p_up>=.5).astype(int)
    follows=bp.eq(z.momentum_up.astype(int))
    override=follows&z.p_reversal.ge(THRESH)
    z["p_corrected"]=z.p_up.astype(float)
    upmom=z.momentum_up.astype(int).eq(1)
    z.loc[override&upmom,"p_corrected"]=1.0-z.loc[override&upmom,"p_reversal"]
    z.loc[override&(~upmom),"p_corrected"]=z.loc[override&(~upmom),"p_reversal"]

    rp=(z.p_corrected>=.5).astype(int);y=z.y_up.astype(int)
    changed=bp.ne(rp)
    rescued=int((changed&bp.ne(y)&rp.eq(y)).sum())
    broken=int((changed&bp.eq(y)&rp.ne(y)).sum())
    mb=metric(z.y_up,z.p_up);mc=metric(z.y_up,z.p_corrected)
    return z,mb,mc,{
        "override_n":int(override.sum()),"changed_n":int(changed.sum()),
        "rescued":rescued,"broken":broken,"net_rescue":rescued-broken
    }

def main():
    panel=build_panel()
    vega=predict_2025(panel)
    base=load_baseline()
    z,mb,mc,chg=apply(base,vega)

    vega.to_csv(OUT/"vega_2025_predictions.csv",index=False)
    z.to_csv(OUT/"matched_predictions.csv",index=False)

    summary={
        "status":"SESSION_VEGA_FROZEN_2025_TRANSPORT_COMPLETE",
        "scope":"WGC US + PATH_GLOBAL_1H only; canonical VEGA V1; no selected VEGA transport",
        "threshold":THRESH,
        "features":FEATURES,
        "baseline_metrics":mb,
        "corrected_metrics":mc,
        "correction":chg,
        "guardrails":[
            "2025 opened only for the sole pre-2025 eligible canonical VEGA pair.",
            "Canonical nine VEGA features and threshold 0.70 are unchanged.",
            "GVZ is D-1 calendar day or earlier relative to actual NY origin date.",
            "Monthly expanding causal refit uses only matured outcomes before each 2025 month.",
            "Feature-selected VEGA V1B remains closed because it had no pre-2025 eligible pair.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION VEGA — FROZEN 2025 TRANSPORT","",
        "**Eligible pair:** WGC US + PATH_GLOBAL_1H","",
        f"- N: {mb['n']}",
        f"- Base Accuracy: {100*mb['accuracy']:.2f}%",
        f"- Corrected Accuracy: {100*mc['accuracy']:.2f}%",
        f"- Base Balanced Accuracy: {100*mb['balanced_accuracy']:.2f}%",
        f"- Corrected Balanced Accuracy: {100*mc['balanced_accuracy']:.2f}%",
        f"- Base Brier: {mb['brier']:.4f}",
        f"- Corrected Brier: {mc['brier']:.4f}",
        f"- Corrected UP recall: {100*mc['up_recall']:.2f}%",
        f"- Corrected DOWN recall: {100*mc['down_recall']:.2f}%",
        f"- Overrides: {chg['override_n']}",
        f"- Rescues: {chg['rescued']}",
        f"- Breaks: {chg['broken']}",
        f"- Net rescue: {chg['net_rescue']:+d}",
        "",
        "Feature-selected VEGA V1B was not opened in 2025 because no selected pair passed its pre-2025 transport gate."
    ]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
