from __future__ import annotations

# workflow trigger: model contract unchanged

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
BASEP=AX/"tools"/"gold_session_model01b_feature_selected_logistic_20261007.py"
OUT=AX/"SESSION_MODEL03B_A1_FEATURE_SELECTION_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

base=loadmod("m01b",BASEP)
CORE3=list(base.CORE3)
POOL=list(base.POOL)
BLOCK=5
RECENT=252
MIN_TRAIN=252
INNER_MIN=252
INNER_VAL=20
CS=[0.03,0.10,0.30,1.00,3.00]
MIN_FREEZE=3
MAX_FREEZE=8
SEED=20261007

def lr(bal=False):
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED,
        class_weight="balanced" if bal else None
    )

def fit_a1(tr,te,features):
    X=tr[features].astype(float).to_numpy();Xt=te[features].astype(float).to_numpy()
    y=tr.y_up.to_numpy(int)
    sc=StandardScaler().fit(X)
    mg=lr(False).fit(sc.transform(X),y)
    pg=mg.predict_proba(sc.transform(Xt))[:,1]

    rr=tr.tail(RECENT).copy()
    if rr.y_up.nunique()<2:
        return pg
    Xr=rr[features].astype(float).to_numpy()
    scr=StandardScaler().fit(Xr)
    mr=lr(True).fit(scr.transform(Xr),rr.y_up.to_numpy(int))
    pr=mr.predict_proba(scr.transform(Xt))[:,1]
    return .75*pg+.25*pr

def fit_l1_selector(tr,features,C):
    X=tr[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=LogisticRegression(
        C=C,penalty="l1",solver="liblinear",max_iter=5000,
        random_state=SEED,class_weight="balanced"
    )
    m.fit(sc.transform(X),tr.y_up.to_numpy(int))
    coef=m.coef_.ravel()
    idx=np.flatnonzero(np.abs(coef)>1e-10)
    sel=[features[i] for i in idx]
    co={features[i]:float(coef[i]) for i in idx}
    return sel,co

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
        sel,co=fit_l1_selector(tr,POOL,0.30)
        return (sel or CORE3[:3]),0.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)},co

    rows=[]
    for C in CS:
        ys=[];ps=[];ns=[];foldsets=[];ok=True
        for it,va in folds:
            try:
                sel,_=fit_l1_selector(it,POOL,C)
                if not sel:
                    pp=np.full(len(va),float(it.y_up.mean()))
                else:
                    pp=fit_a1(it,va,sel)
            except Exception:
                ok=False;break
            ys.extend(va.y_up.astype(int).tolist());ps.extend(map(float,pp));ns.append(len(sel));foldsets.append(sel)
        if not ok or not ys:continue
        mm=base.metrics(ys,ps)
        rows.append({"C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
                     "mean_selected":float(np.mean(ns)),"fold_selected":foldsets})
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
        pb=fit_a1(tr,te,CORE3)
        ps=fit_a1(tr,te,sel)

        for model,pp,feats in [
            ("BASELINE_A1_ARCR",pb,CORE3),
            ("SELECTED_A1_ARCR",ps,sel),
        ]:
            for r,p in zip(te.itertuples(index=False),pp):
                preds.append({
                    "model":model,"partition":part,"window":win,"label_date":r.label_date,
                    "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),
                    "y_up":int(r.y_up),"p_up":float(p),"train_n":int(len(tr)),
                    "outer_block":int(bs//BLOCK),"features":"|".join(feats)
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
            rows.append({
                "feature":f,"freq":n/total,"both_years":len(years[f])>=2,
                "mean_abs_coef":float(np.mean(absco[f])) if absco[f] else 0.0
            })
        q=pd.DataFrame(rows).sort_values(["both_years","freq","mean_abs_coef"],ascending=[False,False,False])
        feats=q[q.both_years].feature.tolist()[:MAX_FREEZE]
        if len(feats)<MIN_FREEZE:
            for f in q.feature.tolist():
                if f not in feats:feats.append(f)
                if len(feats)>=MIN_FREEZE:break
        feats=feats[:MAX_FREEZE]
        out.append({
            "partition":part,"window":win,"frozen_features":feats,
            "n_features":len(feats),"eligible_outer_blocks":int(total)
        })
    return out

def replay_2025(g,part,win,features):
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
            ("BASELINE_A1_ARCR",CORE3),
            ("SELECTED_A1_ARCR",features),
        ]:
            pp=fit_a1(tr,te,feats)
            for r,p in zip(te.itertuples(index=False),pp):
                if int(r.year)!=2025:continue
                rows.append({
                    "model":model,"partition":part,"window":win,"label_date":r.label_date,
                    "start_utc":r.start_utc,"end_utc":r.end_utc,"year":2025,
                    "y_up":int(r.y_up),"p_up":float(p),"train_n":int(len(tr)),
                    "continuous_block":int(bs//BLOCK),"features":"|".join(feats)
                })
    return pd.DataFrame(rows)

def summarize(pred,period):
    rows=[]
    for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        rows.append({"period":period,"model":m,"partition":part,"window":win,**base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def main():
    panel,hashes=base.build_panel()

    dp=[];ev=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        p,e=replay_dev(g,part,win)
        if not p.empty:dp.append(p)
        if not e.empty:ev.append(e)
    dev_pred=pd.concat(dp,ignore_index=True)
    events=pd.concat(ev,ignore_index=True)
    dev_metrics=summarize(dev_pred,"DEV_2023_2024_COMMON_ROWS")
    frozen=freeze_features(events)

    tp=[]
    for x in frozen:
        g=panel[(panel.partition==x["partition"])&(panel.window==x["window"])].copy()
        z=replay_2025(g,x["partition"],x["window"],x["frozen_features"])
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
        "status":"SESSION_MODEL03B_A1_FEATURE_SELECTION_COMPLETE",
        "baseline":"A1_ARCR = 0.75 global CORE3 + 0.25 recent252 balanced CORE3",
        "challenger":"same A1 mixture with session-specific frozen selected features",
        "candidate_pool":{"daily_core3":CORE3,"xau15_session_clock":base.XAU15_FEATURES},
        "clock_policy":{
            "daily":"strictly earlier America/New_York calendar date",
            "xau15":"available_at strictly less than target_start",
            "target_window_data":"prohibited"
        },
        "chronology":"2022 warm-up; 2023-2024 development/selection; 2025 frozen-spec transport; 2026 unopened",
        "frozen_features":frozen,
        "development_metrics":dev_metrics.to_dict("records"),
        "transport_2025_metrics":tr_metrics.to_dict("records"),
        "guardrails":[
            "A1 weights 0.75/0.25 unchanged.",
            "Recent window fixed at 252.",
            "Threshold fixed at 0.50.",
            "Feature selection evaluated by the actual A1 mixture.",
            "Exact common rows used for baseline/challenger comparison.",
            "No 2025 feature selection or tuning.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION MODEL-03B — NOVA A1 / ARCR FEATURE-SELECTED CHALLENGER","",
        "**Status:** complete.","",
        "## Frozen session-specific features","",
        "| Partition | Window | Frozen features |","|---|---|---|"
    ]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_features'])} |")
    lines += [
        "","## 2025 exact common-row transport","",
        "| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|"
    ]
    for r in tr_metrics.sort_values(["partition","window","model"]).itertuples(index=False):
        lines.append(
            f"| {r.model} | {r.partition} | {r.window} | {int(r.n)} | "
            f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |"
        )
    lines += ["","All candidate inputs are available strictly before the relevant session start."]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({
        "status":summary["status"],
        "frozen_features":frozen,
        "transport_2025_metrics":tr_metrics.to_dict("records")
    },indent=2,default=str))

if __name__=="__main__":
    main()
