from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
CTRL=AX/"tools"/"gold_session_stage1_global_controls_2025_v2_continuous_20261007.py"
OUT=AX/"SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

ctrl=loadmod("ctrl",CTRL)
BLOCK=5
MIN_TRAIN=180
INNER_MIN=140
INNER_VAL=20
CS=[0.03,0.10,0.30,1.00,3.00]
MIN_FREEZE=3
MAX_FREEZE=8
SEED=20261007

def final_lr():
    return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED)

def selector_lr(C):
    return LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,
                              class_weight="balanced",random_state=SEED)

def fit_l2(tr,te,features):
    X=tr[features].astype(float).to_numpy();Xt=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=final_lr().fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def fit_selector(tr,features,C):
    X=tr[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=selector_lr(C).fit(sc.transform(X),tr.y_up.to_numpy(int))
    co=m.coef_.ravel()
    idx=np.flatnonzero(np.abs(co)>1e-10)
    sel=[features[i] for i in idx]
    cmap={features[i]:float(co[i]) for i in idx}
    return sel,cmap

def inner_splits(tr):
    tr=tr.sort_values("start_utc").reset_index(drop=True)
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

def choose_features(tr,features):
    folds=inner_splits(tr)
    if len(folds)<2:
        sel,co=fit_selector(tr,features,0.30)
        return (sel or features[:3]),0.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)},co

    rows=[]
    for C in CS:
        ys=[];ps=[];ns=[];sets=[];ok=True
        for it,va in folds:
            try:
                sel,_=fit_selector(it,features,C)
                if not sel:
                    pp=np.full(len(va),float(it.y_up.mean()))
                else:
                    pp=fit_l2(it,va,sel)
            except Exception:
                ok=False;break
            ys.extend(va.y_up.astype(int).tolist());ps.extend(map(float,pp));ns.append(len(sel));sets.append(sel)
        if not ok or not ys:continue
        mm=ctrl.base.metrics(ys,ps)
        rows.append({"C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
                     "mean_selected":float(np.mean(ns)),"fold_selected":sets})
    if not rows:
        sel,co=fit_selector(tr,features,0.30)
        return (sel or features[:3]),0.30,{"fallback":"NO_VALID_CANDIDATE"},co

    best=max(r["ba"] for r in rows)
    short=[r for r in rows if r["ba"]>=best-0.01]
    chosen=sorted(short,key=lambda r:(r["brier"],r["mean_selected"],r["C"]))[0]
    sel,co=fit_selector(tr,features,float(chosen["C"]))
    if not sel:sel=features[:3]
    return sel,float(chosen["C"]),{"candidates":rows,"chosen":chosen},co

def build_panel():
    p,_=ctrl.panel()
    p=p.reset_index(drop=True);p["row_id"]=np.arange(len(p))
    h=ctrl.x1h(ctrl.raw15())
    p=ctrl.r1h.attach(p,h,"g1h","1h")
    fs=list(ctrl.r1h.feature_names("g1h"))
    p=p.dropna(subset=fs+["direction"]).copy()
    p["start_utc"]=pd.to_datetime(p.start_utc,utc=True)
    p["end_utc"]=pd.to_datetime(p.end_utc,utc=True)
    p["year"]=p.start_utc.dt.year
    p["y_up"]=(p.direction=="UP").astype(int)
    # r1h.attach is the canonical Stage-1 clock-safe helper.
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True),fs

def replay_dev(g,part,win,features):
    g=g.sort_values("start_utc").reset_index(drop=True)
    teall=g[g.year.isin([2023,2024])].copy().reset_index(drop=True)
    preds=[];events=[]
    for bs in range(0,len(teall),BLOCK):
        te=teall.iloc[bs:bs+BLOCK].copy()
        if te.empty:continue
        cut=te.start_utc.min()
        tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
        if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue

        sel,C,detail,co=choose_features(tr,features)
        pb=fit_l2(tr,te,features)
        ps=fit_l2(tr,te,sel)
        for model,pp,feats in [
            ("BASELINE_PATH_GLOBAL",pb,features),
            ("SELECTED_PATH_GLOBAL",ps,sel),
        ]:
            for r,p in zip(te.itertuples(index=False),pp):
                preds.append({
                    "model":model,"partition":part,"window":win,
                    "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
                    "year":int(r.year),"y_up":int(r.y_up),"p_up":float(p),
                    "train_n":int(len(tr)),"outer_block":int(bs//BLOCK),
                    "features":"|".join(feats)
                })
        events.append({
            "partition":part,"window":win,"outer_block":int(bs//BLOCK),
            "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),"train_n":int(len(tr)),
            "selector_C":C,"selected_features":json.dumps(sel,separators=(",",":")),
            "selected_coefficients":json.dumps(co,separators=(",",":")),
            "inner_detail":json.dumps(detail,separators=(",",":"))
        })
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
        total=max(1,len(e))
        rows=[]
        for f,n in counts.items():
            rows.append({"feature":f,"freq":n/total,"both_years":len(years[f])>=2,
                         "mean_abs_coef":float(np.mean(absco[f])) if absco[f] else 0.0})
        q=pd.DataFrame(rows).sort_values(["both_years","freq","mean_abs_coef"],
                                        ascending=[False,False,False])
        feats=q[q.both_years].feature.tolist()[:MAX_FREEZE]
        if len(feats)<MIN_FREEZE:
            for f in q.feature.tolist():
                if f not in feats:feats.append(f)
                if len(feats)>=MIN_FREEZE:break
        feats=feats[:MAX_FREEZE]
        out.append({"partition":part,"window":win,"frozen_features":feats,
                    "n_features":len(feats),"eligible_outer_blocks":int(total)})
    return out

def replay_2025(g,part,win,all_features,selected_features):
    g=g.sort_values("start_utc").reset_index(drop=True)
    teall=g[g.year.isin([2023,2024,2025])].copy().reset_index(drop=True)
    rows=[]
    for bs in range(0,len(teall),BLOCK):
        te=teall.iloc[bs:bs+BLOCK].copy()
        if te.empty:continue
        cut=te.start_utc.min()
        tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
        if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
        for model,feats in [
            ("BASELINE_PATH_GLOBAL",all_features),
            ("SELECTED_PATH_GLOBAL",selected_features),
        ]:
            pp=fit_l2(tr,te,feats)
            for r,p in zip(te.itertuples(index=False),pp):
                if int(r.year)!=2025:continue
                rows.append({
                    "model":model,"partition":part,"window":win,
                    "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
                    "year":2025,"y_up":int(r.y_up),"p_up":float(p),
                    "train_n":int(len(tr)),"continuous_block":int(bs//BLOCK),
                    "features":"|".join(feats)
                })
    return pd.DataFrame(rows)

def summarize(pred,period):
    rows=[]
    for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        rows.append({"period":period,"model":m,"partition":part,"window":win,
                     **ctrl.base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def main():
    panel,features=build_panel()
    dp=[];ev=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        p,e=replay_dev(g,part,win,features)
        if not p.empty:dp.append(p)
        if not e.empty:ev.append(e)

    dev_pred=pd.concat(dp,ignore_index=True)
    events=pd.concat(ev,ignore_index=True)
    dev_metrics=summarize(dev_pred,"DEV_2023_2024_COMMON_ROWS")
    frozen=freeze_features(events)

    tp=[]
    for x in frozen:
        g=panel[(panel.partition==x["partition"])&(panel.window==x["window"])].copy()
        z=replay_2025(g,x["partition"],x["window"],features,x["frozen_features"])
        if not z.empty:tp.append(z)
    tr_pred=pd.concat(tp,ignore_index=True)
    tr_metrics=summarize(tr_pred,"FROZEN_SPEC_2025")

    OUT.mkdir(exist_ok=True)
    dev_pred.to_csv(OUT/"dev_predictions.csv",index=False)
    events.to_csv(OUT/"selection_events.csv",index=False)
    dev_metrics.to_csv(OUT/"dev_metrics.csv",index=False)
    tr_pred.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    tr_metrics.to_csv(OUT/"transport_2025_metrics.csv",index=False)
    (OUT/"frozen_features.json").write_text(json.dumps(frozen,indent=2)+"\n")

    summary={
        "status":"SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_COMPLETE",
        "baseline":"PATH_GLOBAL 1h all original hourly PATH/VOL/SHAPE variables",
        "challenger":"same final Logistic L2 C=1.0 with session-specific frozen subset",
        "candidate_features":features,
        "clock_policy":"canonical r1h.attach; hourly bar-close available_at <= target_start",
        "chronology":"2022 warm-up; 2023-2024 development/selection; 2025 frozen-spec transport; 2026 unopened",
        "frozen_features":frozen,
        "development_metrics":dev_metrics.to_dict("records"),
        "transport_2025_metrics":tr_metrics.to_dict("records"),
        "guardrails":[
            "No 15m, cross-metal, macro, GVZ, COT, or model-output feature added.",
            "Only original PATH_GLOBAL hourly variables may be selected.",
            "Final estimator fixed at Logistic L2 C=1.0.",
            "Threshold fixed at 0.50.",
            "Exact common rows used for baseline/challenger comparison.",
            "No 2025 feature selection or tuning.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION MODEL-04B — PATH_GLOBAL FEATURE-SELECTION CHALLENGER","",
           "**Status:** complete.","","## Frozen session-specific features","",
           "| Partition | Window | Frozen features |","|---|---|---|"]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_features'])} |")
    lines += ["","## 2025 exact common-row transport","",
              "| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in tr_metrics.sort_values(["partition","window","model"]).itertuples(index=False):
        lines.append(f"| {r.model} | {r.partition} | {r.window} | {int(r.n)} | "
                     f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                     f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"frozen_features":frozen,
                      "transport_2025_metrics":tr_metrics.to_dict("records")},indent=2,default=str))

if __name__=="__main__":
    main()
