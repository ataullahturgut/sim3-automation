from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
A0P=AX/"tools"/"gold_session_nova_a0_core3_raw_replay_v1_20261006.py"
MA15P=AX/"tools"/"gold_session_iris15_crossmetal_v2_maintaware_20261006.py"

WARM=AX/"GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
X22=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
X35=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_MODEL01B_FEATURE_SELECTED_LOGISTIC_OUT";OUT.mkdir(exist_ok=True)

SEED=20261007
BLOCK=5
MIN_TRAIN=180
INNER_MIN=120
INNER_VAL=20
CS=[0.03,0.10,0.30,1.00,3.00]
MIN_FREEZE=3
MAX_FREEZE=8

def mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

a0=mod("a0",A0P)
ma15=mod("ma15",MA15P)
CORE3=list(a0.CORE3)
XAU15_FEATURES=list(ma15.v1.feature_names("g"))
POOL=CORE3+XAU15_FEATURES

def metrics(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp),
    }

def fit_l2(tr,te,features):
    X=tr[features].astype(float).to_numpy();Xt=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED)
    m.fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def fit_l1_selector(tr,features,C):
    X=tr[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,
                         random_state=SEED,class_weight="balanced")
    m.fit(sc.transform(X),tr.y_up.to_numpy(int))
    coef=m.coef_.ravel()
    idx=np.flatnonzero(np.abs(coef)>1e-10)
    sel=[features[i] for i in idx]
    co={features[i]:float(coef[i]) for i in idx}
    return sel,co

def load_targets():
    frames=[]
    w=pd.read_csv(WARM);w=w[w.final_trainable.astype(str).str.lower().eq("true")].copy();frames.append(w)
    for p in [WGC,SOB]:
        q=pd.read_csv(p);q=q[q.final_trainable.astype(str).str.lower().eq("true")].copy();frames.append(q)
    q=pd.concat(frames,ignore_index=True,sort=False)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["year"]=q.start_utc.dt.year
    q["y_up"]=(q.direction=="UP").astype(int)
    return q

def load_xau15():
    a=pd.read_csv(X22,usecols=["dt_utc","close"])
    b=pd.read_csv(X35,usecols=["dt_utc","close"])
    q=pd.concat([a,b],ignore_index=True)
    q["ts"]=pd.to_datetime(q.pop("dt_utc"),utc=True,errors="raise")
    q["value"]=pd.to_numeric(q.pop("close"),errors="raise")
    q=q.dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    if (q.value<=0).any():raise RuntimeError("XAU_NONPOS")
    q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
    return q[["ts","available_at_utc","value"]].reset_index(drop=True)

def build_panel():
    old=a0.YEARS;a0.YEARS=range(2010,2026)
    try: metals,hashes=a0.load_raw_metals()
    finally:a0.YEARS=old
    p=a0.align_daily_features(load_targets(),metals).dropna(subset=CORE3+["direction","obs_date"]).copy()
    p["start_utc"]=pd.to_datetime(p.start_utc,utc=True);p["end_utc"]=pd.to_datetime(p.end_utc,utc=True)
    p["year"]=p.start_utc.dt.year;p["y_up"]=(p.direction=="UP").astype(int)
    p=p.reset_index(drop=True);p["row_id"]=np.arange(len(p))
    ma15.base.audit_target_clocks(p)
    p=ma15.attach(p,load_xau15(),"g")
    p=p.dropna(subset=POOL+["direction"]).copy()
    if not (p.g_anchor_available<p.start_utc).all():raise RuntimeError("TARGET_START_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():raise RuntimeError("XAU_REFERENCE_STALE")
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True),hashes

def inner_splits(tr):
    n=len(tr);starts=[]
    s=max(INNER_MIN,n-3*INNER_VAL)
    while s+INNER_VAL<=n and len(starts)<3:
        starts.append(s);s+=INNER_VAL
    out=[]
    for pos in starts:
        va=tr.iloc[pos:pos+INNER_VAL].copy()
        if va.empty:continue
        cut=va.start_utc.min()
        it=tr[(tr.end_utc<=cut)&(tr.start_utc<cut)].copy()
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:continue
        out.append((it,va))
    return out

def choose_features(tr):
    folds=inner_splits(tr)
    if len(folds)<2:
        # deterministic fallback from training-only full fit
        sel,co=fit_l1_selector(tr,POOL,0.30)
        return (sel or CORE3[:3]),0.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)},co

    rows=[]
    for C in CS:
        ys=[];ps=[];ns=[];foldsels=[]
        ok=True
        for it,va in folds:
            try:
                sel,co=fit_l1_selector(it,POOL,C)
                if not sel:
                    pp=np.full(len(va),float(it.y_up.mean()))
                else:
                    pp=fit_l2(it,va,sel)
            except Exception:
                ok=False;break
            ys.extend(va.y_up.astype(int).tolist());ps.extend(map(float,pp));ns.append(len(sel));foldsels.append(sel)
        if not ok or not ys:continue
        mm=metrics(ys,ps)
        rows.append({"C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
                     "mean_selected":float(np.mean(ns)),"fold_selected":foldsels})
    if not rows:
        sel,co=fit_l1_selector(tr,POOL,0.30)
        return (sel or CORE3[:3]),0.30,{"fallback":"NO_VALID_CANDIDATE"},co
    best=max(r["ba"] for r in rows)
    short=[r for r in rows if r["ba"]>=best-0.01]
    chosen=sorted(short,key=lambda r:(r["brier"],r["mean_selected"],r["C"]))[0]
    sel,co=fit_l1_selector(tr,POOL,float(chosen["C"]))
    if not sel:sel=CORE3[:3]
    return sel,float(chosen["C"]),{"candidates":rows,"chosen":chosen},co

def replay_dev(g,part,win):
    g=g.sort_values("start_utc").reset_index(drop=True)
    teall=g[g.year.isin([2023,2024])].copy().reset_index(drop=True)
    preds=[];events=[]
    for bs in range(0,len(teall),BLOCK):
        te=teall.iloc[bs:bs+BLOCK].copy()
        if te.empty:continue
        cut=te.start_utc.min()
        tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
        if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
        sel,C,detail,co=choose_features(tr)
        pb=fit_l2(tr,te,CORE3)
        ps=fit_l2(tr,te,sel)
        for model,pp,feats in [("CORE3_CLASSICAL",pb,CORE3),("SELECTED_CLASSICAL",ps,sel)]:
            for r,p in zip(te.itertuples(index=False),pp):
                preds.append({"model":model,"partition":part,"window":win,"label_date":r.label_date,
                              "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),"y_up":int(r.y_up),
                              "p_up":float(p),"train_n":int(len(tr)),"outer_block":int(bs//BLOCK),
                              "features":"|".join(feats)})
        events.append({"partition":part,"window":win,"outer_block":int(bs//BLOCK),
                       "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),"train_n":int(len(tr)),
                       "selector_C":C,"selected_features":json.dumps(sel,separators=(",",":")),
                       "selected_coefficients":json.dumps(co,separators=(",",":")),
                       "inner_detail":json.dumps(detail,separators=(",",":"))})
    return pd.DataFrame(preds),pd.DataFrame(events)

def freeze_features(events):
    out=[]
    for (part,win),e in events.groupby(["partition","window"],sort=True):
        counts=Counter();years=defaultdict(set);absco=defaultdict(list)
        for r in e.itertuples(index=False):
            fs=json.loads(r.selected_features);co=json.loads(r.selected_coefficients)
            counts.update(fs)
            for f in fs:years[f].add(int(r.outer_year))
            for f,v in co.items():absco[f].append(abs(float(v)))
        total=max(1,len(e));rows=[]
        for f,n in counts.items():
            rows.append({"feature":f,"freq":n/total,"both_years":len(years[f])>=2,
                         "mean_abs_coef":float(np.mean(absco[f])) if absco[f] else 0.0})
        q=pd.DataFrame(rows).sort_values(["both_years","freq","mean_abs_coef"],ascending=[False,False,False])
        feats=q[q.both_years].feature.tolist()[:MAX_FREEZE]
        if len(feats)<MIN_FREEZE:
            for f in q.feature.tolist():
                if f not in feats:feats.append(f)
                if len(feats)>=MIN_FREEZE:break
        feats=feats[:MAX_FREEZE]
        out.append({"partition":part,"window":win,"frozen_features":feats,"n_features":len(feats),
                    "eligible_outer_blocks":int(total)})
    return out

def replay_2025(g,part,win,features):
    g=g.sort_values("start_utc").reset_index(drop=True)
    teall=g[g.year.isin([2023,2024,2025])].copy().reset_index(drop=True)
    rows=[]
    for bs in range(0,len(teall),BLOCK):
        te=teall.iloc[bs:bs+BLOCK].copy()
        if te.empty:continue
        cut=te.start_utc.min();tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
        if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
        variants=[
            ("CORE3_CLASSICAL_COMMON_2025",CORE3),
            ("MODEL01B_FROZEN_FEATURES",features),
        ]
        for model_name,feats in variants:
            pp=fit_l2(tr,te,feats)
            for r,p in zip(te.itertuples(index=False),pp):
                if int(r.year)!=2025:continue
                rows.append({"model":model_name,"partition":part,"window":win,
                             "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
                             "year":2025,"y_up":int(r.y_up),"p_up":float(p),"train_n":int(len(tr)),
                             "continuous_block":int(bs//BLOCK),"features":"|".join(feats)})
    return pd.DataFrame(rows)

def summarize(pred,period):
    rows=[]
    for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        rows.append({"period":period,"model":m,"partition":part,"window":win,**metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def main():
    panel,hashes=build_panel()
    dp=[];ev=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        p,e=replay_dev(g,part,win)
        if not p.empty:dp.append(p)
        if not e.empty:ev.append(e)
    dev_pred=pd.concat(dp,ignore_index=True);events=pd.concat(ev,ignore_index=True)
    dev_metrics=summarize(dev_pred,"DEV_2023_2024_COMMON_ROWS")
    frozen=freeze_features(events)

    tp=[]
    for x in frozen:
        g=panel[(panel.partition==x["partition"])&(panel.window==x["window"])].copy()
        z=replay_2025(g,x["partition"],x["window"],x["frozen_features"])
        if not z.empty:tp.append(z)
    tr_pred=pd.concat(tp,ignore_index=True)
    tr_metrics=summarize(tr_pred,"FROZEN_SPEC_2025")

    cov=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        cov.append({"partition":part,"window":win,
                    "rows_2022":int((g.year==2022).sum()),"rows_2023":int((g.year==2023).sum()),
                    "rows_2024":int((g.year==2024).sum()),"rows_2025":int((g.year==2025).sum()),
                    "median_anchor_lag_min":float(g.g_anchor_lag_min.median()),
                    "max_reference_stale_min":float(g.g_max_reference_stale_min.max())})

    dev_pred.to_csv(OUT/"dev_predictions.csv",index=False)
    events.to_csv(OUT/"selection_events.csv",index=False)
    dev_metrics.to_csv(OUT/"dev_metrics.csv",index=False)
    tr_pred.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    tr_metrics.to_csv(OUT/"transport_2025_metrics.csv",index=False)
    (OUT/"frozen_features.json").write_text(json.dumps(frozen,indent=2)+"\n")

    summary={
      "status":"SESSION_MODEL01B_FEATURE_SELECTED_CLASSICAL_LOGISTIC_COMPLETE",
      "final_estimator":{"scale":"StandardScaler","model":"LogisticRegression","penalty":"L2","C":1.0,
                         "class_weight":None,"threshold":0.5},
      "candidate_pool":{"daily_core3":CORE3,"xau15_session_clock":XAU15_FEATURES},
      "clock_policy":{
        "daily":"strictly earlier America/New_York calendar date",
        "xau15":"latest completed 15m state strictly before target_start; equality rejected",
        "maintenance":"governed NY 17:00-18:00 deterministic as-of exception; no synthetic bar"
      },
      "chronology":"2022 warm-up; 2023-2024 development/feature selection; 2025 frozen-specification causal transport; 2026 unopened",
      "frozen_features":frozen,
      "development_metrics":dev_metrics.to_dict("records"),
      "transport_2025_metrics":tr_metrics.to_dict("records"),
      "coverage":cov,
      "stak_annual_hashes":hashes,
      "guardrails":[
        "2025 comparison uses CORE3 and Model-01B on the exact same common rows and identical causal block chronology.",
        "Model-01 baseline is not overwritten.",
        "Final estimator remains Classical Logistic L2 C=1.0.",
        "No target-start bar or target-window XAU15 observation is used.",
        "Outer test rows never select their own variables.",
        "No 2025 outcome is used for feature selection.",
        "No 2026 outcome is opened."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION MODEL-01B — FEATURE-SELECTED CLASSICAL LOGISTIC","",
           "**Status:** complete.","",
           "Final estimator remains the same Classical Logistic as Model-01; only the feature representation changes.","",
           "## Frozen session-specific features","",
           "| Partition | Window | Frozen features |","|---|---|---|"]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_features'])} |")
    lines += ["","## 2025 frozen-specification transport","",
              "| Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in tr_metrics.sort_values(["partition","window"]).itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                     f"{100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | "
                     f"{100*r.down_recall:.2f}% | {r.brier:.4f} |")
    lines += ["","All XAU15 variables are computed from observations available strictly before each specific session start."]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"frozen":frozen,
                      "transport":tr_metrics.to_dict("records")},indent=2,default=str))

if __name__=="__main__":main()
