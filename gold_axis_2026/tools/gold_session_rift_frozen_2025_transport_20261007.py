from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, recall_score, log_loss
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RIFTP=AX/"tools"/"gold_session_rift_v1_20261007.py"
FROZEN=AX/"GOLD_SESSION_RIFT_V1B_VARSEL_FROZEN_FEATURES_2026-10-07.json"
GLOBAL25=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
S1425=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
OUT=AX/"SESSION_RIFT_FROZEN_2025_TRANSPORT_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

r0=loadmod("riftv1",RIFTP)
FULL=list(r0.FEATURES)
THRESH=float(r0.THRESH)
MIN_TRAIN=int(r0.MIN_TRAIN)
SEED=20261007
PART="SOBTI_5_ET"
WIN="ASIA_AFTERNOON_LIT"
EPS=1e-8

def asbool(s):
    return s.astype(str).str.lower().eq("true")

def load_targets_extended():
    w=pd.read_csv(r0.WARM)
    w=w[asbool(w.final_trainable)].copy()
    z=[]
    for p in [r0.WGC,r0.SOB]:
        q=pd.read_csv(p)
        q=q[asbool(q.final_trainable)].copy()
        q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
        q=q[q.start_utc.dt.year.isin([2023,2024,2025])].copy()
        z.append(q)
    q=pd.concat([w]+z,ignore_index=True,sort=False)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True,errors="raise")
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True,errors="raise")
    q["label_date"]=pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    q["year"]=q.start_utc.dt.year
    q["y_up"]=(q.direction=="UP").astype(int)
    if q.duplicated(["partition","window","label_date"]).any():
        raise RuntimeError("TARGET_DUPLICATE")
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def load_raw15_extended():
    a=pd.read_csv(r0.RAW22,usecols=["dt_utc","close"])
    b=pd.read_csv(r0.RAW35,usecols=["dt_utc","close"])
    for q in [a,b]:
        q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
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

def build_panel():
    p=load_targets_extended().reset_index(drop=True)
    p["row_id"]=np.arange(len(p))
    p=r0.ma15.attach(p,load_raw15_extended(),"g")

    req=[
        "g_ret_6h","g_ret_12h","g_rv_12",
        "g_up_semivol_24","g_down_semivol_24",
        "g_upfrac_24","g_close_location_24",
        "g_age_max_neg_24","g_age_max_pos_24",
        "g_jump_concentration_24","g_range_24",
        "g_max_drawdown_24","g_recovery_24",
        "g_anchor_available","g_max_reference_stale_min",
    ]
    p=p.dropna(subset=req+["direction"]).copy()
    if not (p.g_anchor_available<p.start_utc).all():
        raise RuntimeError("RIFT_XAU_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():
        raise RuntimeError("RIFT_REFERENCE_STALE")

    sign=np.where(p.g_ret_12h.to_numpy(float)>=0,1.0,-1.0)
    up2=p.g_up_semivol_24.to_numpy(float)**2
    dn2=p.g_down_semivol_24.to_numpy(float)**2
    total=up2+dn2+EPS

    p["trend_strength"]=np.abs(p.g_ret_12h)/(p.g_rv_12+EPS)
    p["opposite_semivar_share"]=np.where(sign>0,dn2/total,up2/total)
    p["deceleration_6h"]=-sign*(2.0*p.g_ret_6h-p.g_ret_12h)/(p.g_rv_12+EPS)
    p["path_consistency"]=sign*(2.0*p.g_upfrac_24-1.0)
    p["trend_close_location"]=np.where(sign>0,p.g_close_location_24,1.0-p.g_close_location_24)
    p["opposite_extreme_recency"]=np.where(
        sign>0,1.0/(1.0+p.g_age_max_neg_24),1.0/(1.0+p.g_age_max_pos_24)
    )
    p["jump_concentration_24"]=p.g_jump_concentration_24
    p["trend_to_range"]=np.abs(p.g_ret_12h)/(p.g_range_24+EPS)
    p["adverse_excursion"]=np.where(
        sign>0,
        -p.g_max_drawdown_24/(p.g_range_24+EPS),
        p.g_recovery_24/(p.g_range_24+EPS)
    )

    p["momentum_up"]=(p.g_ret_12h>=0).astype(int)
    p["reversal_target"]=(p.y_up.astype(int)!=p.momentum_up.astype(int)).astype(int)
    p["month_key"]=p.start_utc.dt.to_period("M").astype(str)
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def model():
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def predict_rift(panel,features,name):
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        if part!=PART or win!=WIN:continue
        g=g0.sort_values("start_utc").reset_index(drop=True)
        teall=g[g.year.eq(2025)].copy()
        for mo in sorted(teall.month_key.unique()):
            te=teall[teall.month_key.eq(mo)].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.reversal_target.nunique()<2:continue
            X=tr[features].astype(float).to_numpy()
            Xt=te[features].astype(float).to_numpy()
            sc=StandardScaler().fit(X)
            m=model().fit(sc.transform(X),tr.reversal_target.astype(int).to_numpy())
            pp=m.predict_proba(sc.transform(Xt))[:,1]
            for rr,pv in zip(te.itertuples(index=False),pp):
                rows.append({
                    "rift_variant":name,
                    "partition":part,"window":win,
                    "label_date":rr.label_date,
                    "start_utc":rr.start_utc,"end_utc":rr.end_utc,
                    "year":2025,"y_up":int(rr.y_up),
                    "momentum_up":int(rr.momentum_up),
                    "reversal_target":int(rr.reversal_target),
                    "p_reversal":float(pv),
                    "train_n":int(len(tr)),
                    "features":"|".join(features)
                })
    return pd.DataFrame(rows)

def selected_features():
    data=json.loads(FROZEN.read_text())
    for x in data:
        if x["partition"]==PART and x["window"]==WIN:
            return list(x["frozen_features"])
    raise RuntimeError("NO_FROZEN_SELECTED_FEATURES")

def load_baselines():
    out={}
    g=pd.read_csv(GLOBAL25)
    g["start_utc"]=pd.to_datetime(g.start_utc,utc=True)
    g["label_date"]=pd.to_datetime(g.label_date).dt.strftime("%Y-%m-%d")
    g=g[(g.partition==PART)&(g.window==WIN)].copy()
    for name in ["A0_CORE3","PATH_GLOBAL_1H"]:
        q=g[g.model.eq(name)][["partition","window","label_date","start_utc","y_up","p_up"]].copy()
        out[name]=q

    s=pd.read_csv(S1425)
    s["start_utc"]=pd.to_datetime(s.start_utc,utc=True)
    s["label_date"]=pd.to_datetime(s.label_date).dt.strftime("%Y-%m-%d")
    s=s[(s.partition==PART)&(s.window==WIN)].copy()
    out["A1_ARCR"]=s[s.model.eq("A1_DIRECT_MATCHED")][
        ["partition","window","label_date","start_utc","y_up","p_up"]
    ].copy()
    out["STRUCTURAL_IRIS_A1_PLUS_1H"]=s[s.model.eq("S14_A1_PLUS_1H_FULL")][
        ["partition","window","label_date","start_utc","y_up","p_up"]
    ].copy()
    return out

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

def apply_correction(base,rift,baseline_name,variant):
    key=["partition","window","label_date","start_utc","y_up"]
    z=base.merge(
        rift[key+["momentum_up","p_reversal"]],
        on=key,how="inner",validate="one_to_one"
    )
    if z.empty:raise RuntimeError(f"NO_MATCH {baseline_name} {variant}")

    bp=(z.p_up>=.5).astype(int)
    follows=bp.eq(z.momentum_up.astype(int))
    override=follows&z.p_reversal.ge(THRESH)
    z["p_corrected"]=z.p_up.astype(float)

    upmom=z.momentum_up.astype(int).eq(1)
    z.loc[override&upmom,"p_corrected"]=1.0-z.loc[override&upmom,"p_reversal"]
    z.loc[override&(~upmom),"p_corrected"]=z.loc[override&(~upmom),"p_reversal"]

    rp=(z.p_corrected>=.5).astype(int)
    y=z.y_up.astype(int)
    changed=bp.ne(rp)
    rescued=int((changed&bp.ne(y)&rp.eq(y)).sum())
    broken=int((changed&bp.eq(y)&rp.ne(y)).sum())

    mb=metric(z.y_up,z.p_up)
    mr=metric(z.y_up,z.p_corrected)
    row={
        "baseline":baseline_name,"rift_variant":variant,
        "partition":PART,"window":WIN,
        "n":int(len(z)),
        "override_n":int(override.sum()),
        "changed_n":int(changed.sum()),
        "rescued":rescued,"broken":broken,"net_rescue":rescued-broken,
    }
    row.update({f"base_{k}":v for k,v in mb.items()})
    row.update({f"corrected_{k}":v for k,v in mr.items()})
    z["baseline"]=baseline_name;z["rift_variant"]=variant;z["override"]=override
    return row,z

def main():
    panel=build_panel()
    sel=selected_features()

    full=predict_rift(panel,FULL,"FULL_RIFT_V1")
    selected=predict_rift(panel,sel,"SELECTED_RIFT_V1B")
    full.to_csv(OUT/"full_rift_2025_predictions.csv",index=False)
    selected.to_csv(OUT/"selected_rift_2025_predictions.csv",index=False)

    baselines=load_baselines()
    rows=[];detail=[]
    for bname,bdf in baselines.items():
        for variant,rdf in [("FULL_RIFT_V1",full),("SELECTED_RIFT_V1B",selected)]:
            row,z=apply_correction(bdf,rdf,bname,variant)
            rows.append(row);detail.append(z)

    mdf=pd.DataFrame(rows)
    mdf.to_csv(OUT/"metrics.csv",index=False)
    pd.concat(detail,ignore_index=True).to_csv(OUT/"matched_predictions.csv",index=False)

    summary={
        "status":"SESSION_RIFT_FROZEN_2025_TRANSPORT_COMPLETE",
        "scope":"Sobti Asia Afternoon only; four pre-2025 eligible upstream baselines; frozen full and selected RIFT; no 2025 tuning",
        "threshold":THRESH,
        "full_features":FULL,
        "selected_features":sel,
        "metrics":mdf.to_dict("records"),
        "guardrails":[
            "2025 opened only after full and selected RIFT pre-2025 gates were frozen.",
            "Monthly expanding causal refit uses only matured labels before each 2025 month.",
            "No threshold, feature, baseline or session selection uses 2025 outcomes.",
            "A1 and Structural baselines preserve the S1.4 matched-population identity used in RIFT development.",
            "2026 remains unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION RIFT — FROZEN 2025 TRANSPORT","",
        "**Window:** Sobti Asia Afternoon","",
        "| Baseline | RIFT | N | Base BA | Corrected BA | Base Brier | Corrected Brier | UP recall | DOWN recall | Overrides | Rescue | Break | Net |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in mdf.itertuples(index=False):
        lines.append(
            f"| {r.baseline} | {r.rift_variant} | {r.n} | "
            f"{100*r.base_balanced_accuracy:.2f}% | {100*r.corrected_balanced_accuracy:.2f}% | "
            f"{r.base_brier:.4f} | {r.corrected_brier:.4f} | "
            f"{100*r.corrected_up_recall:.2f}% | {100*r.corrected_down_recall:.2f}% | "
            f"{r.override_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} |"
        )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"metrics":summary["metrics"]},indent=2,default=str))

if __name__=="__main__":
    main()
