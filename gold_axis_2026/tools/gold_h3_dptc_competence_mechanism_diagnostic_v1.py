from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.stats import fisher_exact

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m

base=loadmod("base2025",AX/"tools"/"gold_h3_2025_source_backfill_dptc_replay_v1.py")

OUTJ=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_DIAGNOSTIC_V1_2026-10-05.json"
OUTM=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_DIAGNOSTIC_V1_2026-10-05.md"
OUTF=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_FEATURES_V1_2026-10-05.csv"
OUTA=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_ACTIONS_V1_2026-10-05.csv"

DATASET="GLBX.MDP3"; SCHEMA="ohlcv-1h"
START="2022-01-01"; END="2026-10-03"; MAX_COST_USD=2.25
MAPPING={"GC":"GC.v.0","SI":"SI.v.0","NQ":"NQ.v.0","ZN":"ZN.n.0","CL":"CL.c.0"}
ROOTS=["GC","SI","NQ","ZN","CL"]

H3=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
PHASE=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv"
ACT_PRE=AX/"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_ACTIONS_2026-10-05.csv"
ACT25=AX/"GOLD_H3_2025_BACKFILL_DPTC_ACTIONS_2026-10-05.csv"
ACT26=AX/"GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv"
STATE25=AX/"GOLD_H3_2025_BACKFILL_HANDOFF_STATE_2026-10-05.csv"
TL26=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"

SHIFT_METRICS=["spd_shift","energy_shift","tail_shift","te_shift","leadlag_shift"]
CAL_END=pd.Timestamp("2026-01-01")
Q_ANOM=0.95
MIN_PRE_ACTION_SUPPORT=6
RNG=np.random.default_rng(2601005)

def fetch_panel():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key: raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)
    symbols=list(MAPPING.values())
    cost=float(client.metadata.get_cost(dataset=DATASET,schema=SCHEMA,symbols=symbols,stype_in="continuous",start=START,end=END))
    if cost>MAX_COST_USD: raise RuntimeError(f"COST_CAP:{cost:.6f}>{MAX_COST_USD:.2f}")
    q=client.timeseries.get_range(dataset=DATASET,schema=SCHEMA,symbols=symbols,stype_in="continuous",start=START,end=END).to_df().reset_index()
    if "ts_event" not in q.columns and "index" in q.columns: q=q.rename(columns={"index":"ts_event"})
    q["ts"]=pd.to_datetime(q.ts_event,utc=True); q["symbol"]=q.symbol.astype(str)
    q["close"]=pd.to_numeric(q.close,errors="coerce")
    q=q[np.isfinite(q.close)&(q.close>0)].copy()
    rev={v:k for k,v in MAPPING.items()}; q["root"]=q.symbol.map(rev);q=q[q.root.notna()].copy()
    p=q.pivot_table(index="ts",columns="root",values="close",aggfunc="last").reset_index()
    p=p.dropna(subset=ROOTS).sort_values("ts").reset_index(drop=True)
    for r in ROOTS: p[r]=np.log(p[r].astype(float)).diff()
    p=p.dropna(subset=ROOTS).reset_index(drop=True)
    return p[["ts"]+ROOTS],cost

def corr_spd(x):
    c=np.corrcoef(x,rowvar=False)
    c=np.nan_to_num(c,nan=0.0,posinf=0.0,neginf=0.0)
    c=(c+c.T)/2
    c=.95*c+.05*np.eye(c.shape[0])
    return c

def spd_log(c):
    w,v=np.linalg.eigh(c)
    w=np.clip(w,1e-8,None)
    return (v*np.log(w))@v.T

def spd_dist(a,b):
    return float(np.linalg.norm(spd_log(a)-spd_log(b),ord="fro"))

def energy_shift(recent,ref):
    mu=np.nanmedian(ref,axis=0)
    mad=np.nanmedian(np.abs(ref-mu),axis=0)*1.4826
    sd=np.nanstd(ref,axis=0)
    sc=np.where((mad>1e-10)&np.isfinite(mad),mad,np.where(sd>1e-10,sd,1.0))
    a=(recent-mu)/sc; b=(ref-mu)/sc
    dxy=cdist(a,b).mean()
    dxx=cdist(a,a).mean()
    dyy=cdist(b,b).mean()
    return float(max(0.0,2*dxy-dxx-dyy))

def tail_vec(w,q=.15):
    out=[]
    g=w[:,0]
    gr=pd.Series(g).rank(pct=True).to_numpy()
    for j in range(1,w.shape[1]):
        xr=pd.Series(w[:,j]).rank(pct=True).to_numpy()
        lo=float(np.mean((gr<=q)&(xr<=q))/q)
        hi=float(np.mean((gr>=1-q)&(xr>=1-q))/q)
        out.extend([lo,hi])
    return np.asarray(out,float)

def disc3(x):
    q=np.nanquantile(x,[1/3,2/3])
    return np.digitize(x,q,right=False).astype(int)

def cmi(y,x,z,k=3):
    # I(Y;X|Z), all discrete in {0,1,2}
    n=len(y)
    if n<60:return np.nan
    cnt=np.zeros((k,k,k),float)
    for a,b,c in zip(y,x,z): cnt[a,b,c]+=1
    cnt+=0.25
    p=cnt/cnt.sum()
    pyz=p.sum(axis=1)
    pxz=p.sum(axis=0)
    pz=p.sum(axis=(0,1))
    val=0.0
    for iy in range(k):
        for ix in range(k):
            for iz in range(k):
                num=p[iy,ix,iz]*pz[iz]
                den=pyz[iy,iz]*pxz[ix,iz]
                val += p[iy,ix,iz]*math.log(max(num,1e-15)/max(den,1e-15))
    return float(max(val,0.0))

def te_vec(w):
    ds=[disc3(w[:,j]) for j in range(w.shape[1])]
    g=ds[0];out=[]
    for j in range(1,len(ds)):
        x=ds[j]
        x_to_g=cmi(g[1:],x[:-1],g[:-1])
        g_to_x=cmi(x[1:],g[:-1],x[:-1])
        out.append(float(x_to_g-g_to_x))
    return np.asarray(out,float)

def lag_vec(w,maxlag=6):
    g=w[:,0];out=[]
    for j in range(1,w.shape[1]):
        x=w[:,j]
        xl=[];gl=[]
        for lag in range(1,maxlag+1):
            a=x[:-lag];b=g[lag:]
            c=g[:-lag];d=x[lag:]
            rx=np.corrcoef(a,b)[0,1] if np.std(a)>1e-12 and np.std(b)>1e-12 else 0
            rg=np.corrcoef(c,d)[0,1] if np.std(c)>1e-12 and np.std(d)>1e-12 else 0
            xl.append(abs(rx));gl.append(abs(rg))
        out.append(float(max(xl)-max(gl)))
    return np.asarray(out,float)

def calc_features(panel,origins):
    ts_ns=panel.ts.astype("int64").to_numpy()
    x=panel[ROOTS].to_numpy(float)
    rows=[]
    for d in origins:
        co=base.cutoff_ts(d)
        idx=np.searchsorted(ts_ns,int(co.value),side="right")
        if idx<760: continue
        # windows by synchronized hourly observations
        rec120=x[idx-120:idx]; ref480=x[idx-600:idx-120]
        rec96=x[idx-96:idx]; ref384=x[idx-480:idx-96]
        rec240=x[idx-240:idx]; refte=x[idx-720:idx-240]
        if min(len(rec120),len(ref480),len(rec96),len(ref384),len(rec240),len(refte))<90: continue
        cr=corr_spd(rec120); cp=corr_spd(ref480)
        ev=np.linalg.eigvalsh(cr)
        tail_r=tail_vec(rec240);tail_p=tail_vec(refte)
        te_r=te_vec(rec240);te_p=te_vec(refte)
        lag_r=lag_vec(rec240);lag_p=lag_vec(refte)
        corr_gc={f"corr_gc_{ROOTS[j].lower()}":float(cr[0,j]) for j in range(1,5)}
        rows.append({
            "feature_cutoff_date":pd.Timestamp(d),
            "cutoff_ts":co,
            "spd_shift":spd_dist(cr,cp),
            "energy_shift":energy_shift(rec96,ref384),
            "tail_shift":float(np.linalg.norm(tail_r-tail_p)),
            "te_shift":float(np.linalg.norm(te_r-te_p)),
            "leadlag_shift":float(np.linalg.norm(lag_r-lag_p)),
            "eig1_share":float(ev[-1]/max(ev.sum(),1e-12)),
            "te_nq_to_gc_diff":float(te_r[1]),
            "leadlag_nq_to_gc":float(lag_r[1]),
            **corr_gc
        })
    return pd.DataFrame(rows)

def add_label_free_gates(f):
    pre=f[f.feature_cutoff_date<CAL_END].copy()
    th={}
    for c in SHIFT_METRICS:
        vals=pd.to_numeric(pre[c],errors="coerce").dropna()
        th[c]=float(vals.quantile(Q_ANOM))
        f[f"anom_{c}"]=pd.to_numeric(f[c],errors="coerce")>=th[c]
        # percentile against pre-2026 calibration
        arr=np.sort(vals.to_numpy(float))
        f[f"pct_{c}"]=[float(np.searchsorted(arr,v,side="right")/(len(arr)+1)) if np.isfinite(v) else np.nan for v in pd.to_numeric(f[c],errors="coerce")]
    f["structural_count95"]=sum(f[f"anom_{c}"].astype(int) for c in SHIFT_METRICS)
    f["structural_broad"]=f.structural_count95>=2
    f["structural_strict"]=f.structural_count95>=3
    for col in ["structural_broad","structural_strict"]:
        run=[];r=0
        for v in f[col].astype(bool):
            r=r+1 if v else 0;run.append(r)
        f[f"{col}_run"]=run
        f[f"{col}_persistent3"]=f[f"{col}_run"]>=3
    return f,th

def multiview_changepoint(f,start="2024-01-01",end="2026-10-01",minseg=40,nboot=400):
    q=f[(f.feature_cutoff_date>=pd.Timestamp(start))&(f.feature_cutoff_date<=pd.Timestamp(end))].copy()
    cols=SHIFT_METRICS+["eig1_share"]
    x=q[cols].apply(pd.to_numeric,errors="coerce").to_numpy(float)
    # robust scale from pre-2026
    pre=q.feature_cutoff_date<CAL_END
    med=np.nanmedian(x[pre],axis=0);mad=np.nanmedian(np.abs(x[pre]-med),axis=0)*1.4826
    sd=np.nanstd(x[pre],axis=0);sc=np.where((mad>1e-9)&np.isfinite(mad),mad,np.where(sd>1e-9,sd,1.0))
    z=np.nan_to_num((x-med)/sc,nan=0.0,posinf=0.0,neginf=0.0)
    def best(arr):
        n=len(arr);bestv=-1;bestk=None
        for k in range(minseg,n-minseg):
            d=arr[:k].mean(0)-arr[k:].mean(0)
            s=math.sqrt(k*(n-k)/n)*float(np.linalg.norm(d))
            if s>bestv:bestv=s;bestk=k
        return bestv,bestk
    score,k=best(z)
    # moving-block permutation of 20-origin blocks
    b=20;blocks=[z[i:i+b] for i in range(0,len(z),b)]
    sims=[]
    for _ in range(nboot):
        order=RNG.permutation(len(blocks))
        zz=np.vstack([blocks[i] for i in order])
        zz=zz[:len(z)]
        sims.append(best(zz)[0])
    p=float((1+sum(s>=score for s in sims))/(len(sims)+1))
    return {"date":None if k is None else q.iloc[k].feature_cutoff_date.date().isoformat(),
            "score":float(score),"block_permutation_p":p,"n":int(len(q))}

def cliff_delta(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if not len(a) or not len(b):return np.nan
    return float((np.sum(a[:,None]>b[None,:])-np.sum(a[:,None]<b[None,:]))/(len(a)*len(b)))

def perm_p(a,b,n=4000):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if len(a)<2 or len(b)<2:return np.nan
    obs=abs(np.nanmean(a)-np.nanmean(b));z=np.concatenate([a,b]);na=len(a);hit=0
    for _ in range(n):
        p=RNG.permutation(z)
        if abs(np.nanmean(p[:na])-np.nanmean(p[na:]))>=obs-1e-15:hit+=1
    return float((hit+1)/(n+1))

def action_table():
    p=pd.read_csv(ACT_PRE,parse_dates=["feature_cutoff_date"])
    p=p[(p.baseline_mode=="V5_ONLY")&(p.dptc=="Q95")].copy()
    g=p.groupby("feature_cutoff_date").agg(
        source_support=("source_variant","nunique"),
        competence_y=("competence_y","first")
    ).reset_index()
    g=g[g.source_support>=MIN_PRE_ACTION_SUPPORT].copy()
    g["year"]=g.feature_cutoff_date.dt.year;g["source"]="DATABENTO_SOURCE_ROBUST"
    a25=pd.read_csv(ACT25,parse_dates=["feature_cutoff_date"])
    a25=a25[a25.variant.astype(str)=="Q95"][["feature_cutoff_date","competence_y"]].drop_duplicates()
    a25["source_support"]=7;a25["year"]=2025;a25["source"]="YAHOO_EXACT"
    a26=pd.read_csv(ACT26,parse_dates=["feature_cutoff_date"])
    a26=a26[a26.variant.astype(str)=="Q95"][["feature_cutoff_date","competence_y"]].drop_duplicates()
    a26["source_support"]=7;a26["year"]=2026;a26["source"]="YAHOO_EXACT"
    return pd.concat([g,a25,a26],ignore_index=True).sort_values("feature_cutoff_date")

def handoff_table():
    s25=pd.read_csv(STATE25,parse_dates=["feature_cutoff_date"])
    s25=s25[s25.handoff_alarm.map(base.B)][["feature_cutoff_date","competence_y"]].copy()
    s25["year"]=2025;s25["source"]="YAHOO_EXACT"
    t=pd.read_csv(TL26,parse_dates=["feature_cutoff_date"])
    t=t[t.period.astype(str)=="2026_STRESS"][["feature_cutoff_date","competence_y"]].copy()
    t["year"]=2026;t["source"]="YAHOO_EXACT"
    return pd.concat([s25,t],ignore_index=True).drop_duplicates("feature_cutoff_date").sort_values("feature_cutoff_date")

def gate_stats(q,gate):
    z=q.dropna(subset=["competence_y"]).copy()
    inside=z[z[gate].fillna(False).astype(bool)];outside=z[~z[gate].fillna(False).astype(bool)]
    ri=int(inside.competence_y.sum());bi=int(len(inside)-ri)
    ro=int(outside.competence_y.sum());bo=int(len(outside)-ro)
    odds,p=fisher_exact([[ri,bi],[ro,bo]]) if len(inside) and len(outside) else (np.nan,np.nan)
    return {"inside_n":len(inside),"inside_rescue":ri,"inside_precision":None if not len(inside) else ri/len(inside),
            "outside_n":len(outside),"outside_rescue":ro,"outside_precision":None if not len(outside) else ro/len(outside),
            "odds_ratio":None if not np.isfinite(odds) else float(odds),"fisher_p":None if not np.isfinite(p) else float(p)}

def first_date(f,col,year=2026):
    q=f[(f.feature_cutoff_date.dt.year==year)&f[col].fillna(False).astype(bool)]
    return None if q.empty else q.feature_cutoff_date.iloc[0].date().isoformat()

def main():
    panel,cost=fetch_panel()
    h3=pd.read_csv(H3,parse_dates=["feature_cutoff_date"])
    origins=h3[(h3.feature_cutoff_date>=pd.Timestamp("2023-01-01"))&(h3.feature_cutoff_date<=pd.Timestamp("2026-09-30"))].feature_cutoff_date.drop_duplicates().sort_values()
    f=calc_features(panel,origins)
    ph=pd.read_csv(PHASE,parse_dates=["feature_cutoff_date"])
    for c in ["strong_pro_risk","dependence_phase","dep_shift95"]:
        ph[c]=ph[c].map(base.B)
    f=f.merge(ph[["feature_cutoff_date","r_gn","r_gv","strong_pro_risk","strong_run","dependence_phase","dep_shift95"]],on="feature_cutoff_date",how="left")
    f,thresholds=add_label_free_gates(f)
    f["gate_broad_plus_pro"]=f.structural_broad & f.strong_pro_risk.fillna(False)
    f["gate_persistent_plus_pro"]=f.structural_broad_persistent3 & f.strong_pro_risk.fillna(False)
    f.to_csv(OUTF,index=False)

    acts=action_table().merge(f,on="feature_cutoff_date",how="left")
    hands=handoff_table().merge(f,on="feature_cutoff_date",how="left")
    acts["outcome"]=np.where(acts.competence_y.astype(int)==1,"RESCUE","BROKEN")
    acts.to_csv(OUTA,index=False)

    # Outcome diagnostics only after gates are frozen.
    effect={}
    cols=SHIFT_METRICS+["eig1_share","te_nq_to_gc_diff","leadlag_nq_to_gc","corr_gc_nq","corr_gc_zn","corr_gc_cl","corr_gc_si","r_gn","r_gv","strong_run"]
    for c in cols:
        a=pd.to_numeric(acts.loc[acts.competence_y==1,c],errors="coerce").dropna().to_numpy(float)
        b=pd.to_numeric(acts.loc[acts.competence_y==0,c],errors="coerce").dropna().to_numpy(float)
        effect[c]={"rescue_n":len(a),"broken_n":len(b),"rescue_mean":None if not len(a) else float(a.mean()),
                   "broken_mean":None if not len(b) else float(b.mean()),"cliffs_delta":None if not len(a) or not len(b) else cliff_delta(a,b),
                   "permutation_p":None if len(a)<2 or len(b)<2 else perm_p(a,b)}

    gates=["structural_broad","structural_strict","structural_broad_persistent3","gate_broad_plus_pro","gate_persistent_plus_pro","strong_pro_risk","dependence_phase"]
    action_gates={g:gate_stats(acts,g) for g in gates}
    handoff_gates={g:gate_stats(hands,g) for g in gates}

    # Year profiles at DPTC action origins.
    year_profile={}
    for y,g in acts.groupby("year"):
        year_profile[str(int(y))]={
            "n":len(g),"rescue":int(g.competence_y.sum()),"precision":float(g.competence_y.mean()),
            "structural_count95_mean":float(pd.to_numeric(g.structural_count95,errors="coerce").mean()),
            "broad_share":float(g.structural_broad.fillna(False).mean()),
            "pro_risk_share":float(g.strong_pro_risk.fillna(False).mean()),
            "broad_plus_pro_share":float(g.gate_broad_plus_pro.fillna(False).mean()),
            "spd_shift_mean":float(pd.to_numeric(g.spd_shift,errors="coerce").mean()),
            "tail_shift_mean":float(pd.to_numeric(g.tail_shift,errors="coerce").mean()),
            "te_shift_mean":float(pd.to_numeric(g.te_shift,errors="coerce").mean()),
            "energy_shift_mean":float(pd.to_numeric(g.energy_shift,errors="coerce").mean()),
        }

    cp_full=multiview_changepoint(f)
    f26=f[(f.feature_cutoff_date>=pd.Timestamp("2026-01-01"))&(f.feature_cutoff_date<=pd.Timestamp("2026-09-30"))].copy()
    cp_2026=multiview_changepoint(f26,start="2026-01-01",end="2026-09-30",minseg=25,nboot=400)

    onsets={
        "structural_broad":first_date(f,"structural_broad"),
        "structural_strict":first_date(f,"structural_strict"),
        "structural_broad_persistent3":first_date(f,"structural_broad_persistent3"),
        "gate_broad_plus_pro":first_date(f,"gate_broad_plus_pro"),
        "gate_persistent_plus_pro":first_date(f,"gate_persistent_plus_pro"),
        "dependence_phase":first_date(f,"dependence_phase"),
    }

    out={
        "schema":"GOLD_H3_DPTC_COMPETENCE_MECHANISM_DIAGNOSTIC_V1",
        "date":"2026-10-05",
        "status":"MECHANISM_DIAGNOSTIC_COMPLETE",
        "databento_mapping":MAPPING,"estimated_cost_usd":cost,"cost_cap_usd":MAX_COST_USD,
        "methods":{
            "spd_geometry":"log-Euclidean distance between recent and prior 5-market correlation matrices",
            "energy_shift":"multivariate energy distance of standardized joint returns",
            "tail_copula_shift":"empirical upper/lower tail co-movement vector shift",
            "information_flow_shift":"discrete transfer-entropy directionality vector shift",
            "leadlag_shift":"cross-correlation lead/lag asymmetry vector shift",
        },
        "calibration":{"period":"pre-2026","quantile":Q_ANOM,"thresholds":thresholds,"outcome_labels_used":False},
        "onsets_2026":onsets,
        "changepoint_full":cp_full,"changepoint_2026":cp_2026,
        "year_action_profiles":year_profile,
        "action_gate_enrichment":action_gates,
        "handoff_gate_enrichment_2025_2026":handoff_gates,
        "feature_effects_rescue_vs_broken":effect,
        "action_sample":{"n":len(acts),"by_year":acts.groupby("year").size().astype(int).to_dict(),
                         "pre2025_min_source_support":MIN_PRE_ACTION_SUPPORT},
        "governance":{
            "gates_frozen_before_outcome_evaluation":True,
            "pre2026_thresholds_label_free":True,
            "2026_used_for_posthoc_diagnosis":True,
            "claim":"mechanism diagnosis only; not prospective validation"
        }
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    def pct(v):
        return "—" if v is None else f"{100*v:.1f}%"
    lines=[
        "# GOLD H3 — DPTC Competence Mechanism Diagnostic V1 — 2026-10-05","",
        "**Status:** MECHANISM_DIAGNOSTIC_COMPLETE — post-hoc mechanism diagnosis, not prospective validation.","",
        f"Databento estimated cost: **USD {cost:.4f}**.","",
        "## Scientific design","",
        "Five label-free structural diagnostics are computed at each H3 origin: SPD covariance-geometry shift, multivariate energy distance, empirical tail-copula shift, directional transfer-entropy shift, and lead-lag asymmetry shift.",
        "All anomaly thresholds are frozen from pre-2026 data at the 95th percentile before any RESCUE/BROKEN outcome comparison.","",
        "## 2026 label-free onset dates","",
        "| Signal | First 2026 origin |","|---|---|"]
    for k,v in onsets.items():lines.append(f"| {k} | {v or 'none'} |")
    lines += ["","## Multiview change-point test","",
              f"- Full 2024–2026 multiview change point: **{cp_full['date']}**, score {cp_full['score']:.3f}, block-permutation p **{cp_full['block_permutation_p']:.4f}**.",
              f"- 2026-only multiview change point: **{cp_2026['date']}**, score {cp_2026['score']:.3f}, block-permutation p **{cp_2026['block_permutation_p']:.4f}**.","",
              "## DPTC action-year profiles","",
              "| Year | N | Rescue | Precision | Mean anomaly count | Broad shift | Strong-pro-risk | Broad + pro-risk |",
              "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y,s in year_profile.items():
        lines.append(f"| {y} | {s['n']} | {s['rescue']} | {100*s['precision']:.1f}% | {s['structural_count95_mean']:.2f} | {100*s['broad_share']:.1f}% | {100*s['pro_risk_share']:.1f}% | {100*s['broad_plus_pro_share']:.1f}% |")
    lines += ["","## Frozen gate enrichment on DPTC actions","",
              "| Gate | Inside R/N | Inside precision | Outside R/N | Outside precision | Odds ratio | Fisher p |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for g,s in action_gates.items():
        odds="—" if s["odds_ratio"] is None else f"{s['odds_ratio']:.2f}"
        pp="—" if s["fisher_p"] is None else f"{s['fisher_p']:.4f}"
        lines.append(f"| {g} | {s['inside_rescue']}/{s['inside_n']} | {pct(s['inside_precision'])} | {s['outside_rescue']}/{s['outside_n']} | {pct(s['outside_precision'])} | {odds} | {pp} |")
    lines += ["","## Strongest rescue-vs-broken feature separations","",
              "| Feature | Cliff delta | Permutation p | Rescue mean | Broken mean |",
              "|---|---:|---:|---:|---:|"]
    effrows=[]
    for c,s in effect.items():
        if s["cliffs_delta"] is not None:
            effrows.append((abs(s["cliffs_delta"]),c,s))
    for _,c,s in sorted(effrows,reverse=True)[:10]:
        pp="—" if s["permutation_p"] is None else f"{s['permutation_p']:.4f}"
        lines.append(f"| {c} | {s['cliffs_delta']:+.3f} | {pp} | {s['rescue_mean']:.4f} | {s['broken_mean']:.4f} |")
    lines += ["","## Interpretation discipline","",
              "- No structural threshold or gate is selected using DPTC correctness.",
              "- 2023–2024 actions are included only when supported by at least 6 of 7 admissible Databento source mappings.",
              "- 2025 and 2026 use the existing frozen Yahoo-lineage Q95 action evidence.",
              "- 2026 is already consumed development evidence; any proposed competence gate remains a challenger until prospective validation.",
              "- If several independent label-free structural diagnostics converge near the known competence transition and enrich RESCUE precision, that supports a mechanism-level regime interpretation rather than a generic volatility-regime label."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":main()
