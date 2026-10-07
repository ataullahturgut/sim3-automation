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
SAGE_TRANSPORT=AX/"tools"/"gold_session_sage_frozen_2025_transport_v2_continuous_20261007.py"
OUT=AX/"SESSION_MODEL06B_SAGE_FEATURE_SELECTION_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m

st=loadmod("sage_transport",SAGE_TRANSPORT)
v1=st.v1
SESSION_ALL=list(v1.SESSION_ALL)
BLOCK=5
MIN_TRAIN=120
INNER_MIN=100
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
    X=tr[features].astype(float).to_numpy()
    Xt=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=final_lr().fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def fit_selector(tr,C):
    X=tr[SESSION_ALL].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=selector_lr(C).fit(sc.transform(X),tr.y_up.to_numpy(int))
    co=m.coef_.ravel()
    idx=np.flatnonzero(np.abs(co)>1e-10)
    sel=[SESSION_ALL[i] for i in idx]
    cmap={SESSION_ALL[i]:float(co[i]) for i in idx}
    return sel,cmap

def build_panel():
    r=st.raw()
    p=st.targets().reset_index(drop=True)
    p["row_id"]=np.arange(len(p))
    c=st.cycles(r)
    p=pd.merge_asof(
        p.sort_values("start_utc"),
        c,
        left_on="start_utc",
        right_on="sage_ready_utc",
        direction="backward",
        allow_exact_matches=False
    )
    ok=p.sage_ready_utc.notna()
    if not (p.loc[ok,"sage_ready_utc"]<p.loc[ok,"start_utc"]).all():
        raise RuntimeError("SAGE_LEAK")

    # Preserve canonical S1.5/S1.6 common-row population: SAGE + 1h readiness.
    p=st.res1h.attach(p,st.x1h(r),"g1h","1h")
    f1=list(st.res1h.feature_names("g1h"))
    p=p.dropna(subset=SESSION_ALL+f1+["direction"]).copy()
    p["year"]=p.start_utc.dt.year
    p["y_up"]=(p.direction=="UP").astype(int)
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True),f1

def inner_splits(tr):
    tr=tr.sort_values("start_utc").reset_index(drop=True)
    n=len(tr); starts=[]
    s=max(INNER_MIN,n-3*INNER_VAL)
    while s+INNER_VAL<=n and len(starts)<3:
        starts.append(s); s+=INNER_VAL
    out=[]
    for pos in starts:
        va=tr.iloc[pos:pos+INNER_VAL].copy()
        if va.empty: continue
        cut=va.start_utc.min()
        it=tr[(tr.end_utc<=cut)&(tr.start_utc<cut)].copy()
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:
            continue
        out.append((it,va))
    return out

def choose_features(tr):
    folds=inner_splits(tr)
    if len(folds)<2:
        sel,co=fit_selector(tr,.30)
        return (sel or SESSION_ALL[:3]),.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)},co

    scores=[]
    for C in CS:
        ys=[];ps=[];ns=[];ok=True
        for it,va in folds:
            try:
                sel,_=fit_selector(it,C)
                if not sel: sel=SESSION_ALL[:3]
                pp=fit_l2(it,va,sel)
            except Exception:
                ok=False; break
            ys.extend(va.y_up.astype(int).tolist())
            ps.extend(map(float,pp))
            ns.append(len(sel))
        if not ok or not ys: continue
        mm=st.base.metrics(ys,ps)
        scores.append({
            "C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
            "mean_selected":float(np.mean(ns))
        })
    if not scores:
        sel,co=fit_selector(tr,.30)
        return (sel or SESSION_ALL[:3]),.30,{"fallback":"NO_VALID_CANDIDATE"},co

    best=max(x["ba"] for x in scores)
    short=[x for x in scores if x["ba"]>=best-.01]
    chosen=sorted(short,key=lambda x:(x["brier"],x["mean_selected"],x["C"]))[0]
    sel,co=fit_selector(tr,float(chosen["C"]))
    if not sel: sel=SESSION_ALL[:3]
    return sel,float(chosen["C"]),{"scores":scores,"chosen":chosen},co

def replay_dev(panel):
    preds=[];events=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.year.isin([2023,2024])].copy().reset_index(drop=True)
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue

            sel,C,detail,co=choose_features(tr)
            for model,features in [
                ("S15_SESSION_ONLY_BASELINE",SESSION_ALL),
                ("S15_SESSION_ONLY_SELECTED_BLOCK",sel),
            ]:
                pp=fit_l2(tr,te,features)
                for r,p in zip(te.itertuples(index=False),pp):
                    preds.append({
                        "model":model,"partition":part,"window":win,
                        "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
                        "year":int(r.year),"y_up":int(r.y_up),"p_up":float(p),
                        "train_n":int(len(tr)),"outer_block":int(bs//BLOCK),
                        "features":"|".join(features)
                    })
            events.append({
                "partition":part,"window":win,"outer_block":int(bs//BLOCK),
                "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),"train_n":int(len(tr)),
                "selector_C":C,"selected_features":json.dumps(sel,separators=(",",":")),
                "selected_coefficients":json.dumps(co,separators=(",",":")),
                "detail":json.dumps(detail,separators=(",",":"))
            })
    return pd.DataFrame(preds),pd.DataFrame(events)

def summarize(pred,period):
    rows=[]
    for (model,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        rows.append({"period":period,"model":model,"partition":part,"window":win,
                     **st.base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def yearly_metrics(pred,model):
    rows=[]
    q=pred[pred.model==model].copy()
    for (part,win,yr),g in q.groupby(["partition","window","year"],sort=True):
        rows.append({"partition":part,"window":win,"year":int(yr),**st.base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def selected_gate(dev_metrics,year_metrics):
    rows=[]
    q=dev_metrics[dev_metrics.model=="S15_SESSION_ONLY_SELECTED_BLOCK"].copy()
    for r in q.itertuples(index=False):
        yy=year_metrics[(year_metrics.partition==r.partition)&(year_metrics.window==r.window)]
        year_ok=True
        for y in yy.itertuples(index=False):
            if y.n>=40 and y.balanced_accuracy<.50:
                year_ok=False
        eligible=bool(
            r.n>=80 and
            min(r.up_recall,r.down_recall)>=.30 and
            r.balanced_accuracy>=.52 and
            year_ok
        )
        reasons=[]
        if r.n<80:reasons.append("N_LT_80")
        if min(r.up_recall,r.down_recall)<.30:reasons.append("RECALL_FLOOR")
        if r.balanced_accuracy<.52:reasons.append("BA_LT_52")
        if not year_ok:reasons.append("YEAR_BA_LT_50")
        rows.append({
            "partition":r.partition,"window":r.window,"n":int(r.n),
            "balanced_accuracy":float(r.balanced_accuracy),
            "up_recall":float(r.up_recall),"down_recall":float(r.down_recall),
            "brier":float(r.brier),"eligible":eligible,
            "reason":"PASS" if eligible else "|".join(reasons)
        })
    return pd.DataFrame(rows)

def freeze_features(events):
    out=[]
    for (part,win),e in events.groupby(["partition","window"],sort=True):
        counts=Counter();years=defaultdict(set);absco=defaultdict(list)
        for r in e.itertuples(index=False):
            fs=json.loads(r.selected_features); co=json.loads(r.selected_coefficients)
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
        q=pd.DataFrame(rows).sort_values(
            ["both_years","freq","mean_abs_coef"],ascending=[False,False,False]
        )
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

def replay_selected_2025(panel,frozen,gates):
    fmap={(x["partition"],x["window"]):x["frozen_features"] for x in frozen}
    allowed={(r.partition,r.window) for r in gates.itertuples(index=False) if bool(r.eligible)}
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        if (part,win) not in allowed:continue
        feats=fmap[(part,win)]
        g=g0.sort_values("start_utc").reset_index(drop=True)
        teall=g[g.year.isin([2023,2024,2025])].copy().reset_index(drop=True)
        for bs in range(0,len(teall),BLOCK):
            te=teall.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
            pp=fit_l2(tr,te,feats)
            for r,p in zip(te.itertuples(index=False),pp):
                if int(r.year)!=2025:continue
                rows.append({
                    "model":"S15_SESSION_ONLY_SELECTED_FROZEN",
                    "partition":part,"window":win,"label_date":r.label_date,
                    "start_utc":r.start_utc,"year":2025,"y_up":int(r.y_up),
                    "p_up":float(p),"train_n":int(len(tr)),
                    "continuous_block":int(bs//BLOCK),"features":"|".join(feats)
                })
    return pd.DataFrame(rows)

def main():
    panel,_=build_panel()
    dev_pred,events=replay_dev(panel)
    dev_metrics=summarize(dev_pred,"DEV_2023_2024_COMMON_ROWS")
    years=yearly_metrics(dev_pred,"S15_SESSION_ONLY_SELECTED_BLOCK")
    gates=selected_gate(dev_metrics,years)
    frozen=freeze_features(events)

    # 2025 is opened ONLY for selected-SAGE heads that passed the dev gate.
    tr_pred=replay_selected_2025(panel,frozen,gates)
    tr_metrics=summarize(tr_pred,"FROZEN_SPEC_2025") if not tr_pred.empty else pd.DataFrame()

    OUT.mkdir(exist_ok=True)
    dev_pred.to_csv(OUT/"dev_predictions.csv",index=False)
    events.to_csv(OUT/"selection_events.csv",index=False)
    dev_metrics.to_csv(OUT/"dev_metrics.csv",index=False)
    years.to_csv(OUT/"selected_year_metrics.csv",index=False)
    gates.to_csv(OUT/"selected_transport_eligibility.csv",index=False)
    tr_pred.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    tr_metrics.to_csv(OUT/"transport_2025_metrics.csv",index=False)
    (OUT/"frozen_features.json").write_text(json.dumps(frozen,indent=2)+"\n")

    summary={
        "status":"SESSION_MODEL06B_SAGE_FEATURE_SELECTION_COMPLETE",
        "baseline":"S15_SESSION_ONLY canonical 14 SESSION_ALL variables",
        "challenger":"session-specific frozen subset of SESSION_ALL",
        "candidate_features":SESSION_ALL,
        "chronology":"2022 warm-up; 2023-2024 nested selection/development; 2025 only dev-eligible selected heads; 2026 unopened",
        "selected_transport_eligibility":gates.to_dict("records"),
        "frozen_features":frozen,
        "development_metrics":dev_metrics.to_dict("records"),
        "transport_2025_metrics":tr_metrics.to_dict("records") if not tr_metrics.empty else [],
        "guardrails":[
            "Only canonical SAGE SESSION_ALL variables are selectable.",
            "SAGE clock remains 16:15 NY ready with strict sage_ready < target_start.",
            "Canonical S1.5/S1.6 common-row population preserved by requiring 1h readiness.",
            "Selected head must pass frozen development gate before 2025 is opened.",
            "Rejected baseline heads are not opened in 2025 for comparison.",
            "No 2025 feature selection, eligibility rescue, threshold tuning or clock change.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION MODEL-06B — SAGE SESSION_ONLY FEATURE SELECTION","",
        "**Status:** complete.","",
        "## Pre-2025 selected-SAGE eligibility","",
        "| Partition | Window | N | BA | UP recall | DOWN recall | Eligible | Reason |",
        "|---|---|---:|---:|---:|---:|---|---|"
    ]
    for r in gates.sort_values(["partition","window"]).itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {bool(r.eligible)} | {r.reason} |"
        )
    lines += ["","## Frozen selected features","",
              "| Partition | Window | Features |","|---|---|---|"]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_features'])} |")
    lines += ["","## 2025 transport — only development-eligible selected heads",""]
    if tr_metrics.empty:
        lines.append("No selected-SAGE head passed the pre-2025 gate; 2025 remained closed.")
    else:
        lines += ["| Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |",
                  "|---|---|---:|---:|---:|---:|---:|---:|"]
        for r in tr_metrics.sort_values(["partition","window"]).itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | "
                f"{100*r.down_recall:.2f}% | {r.brier:.4f} |"
            )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({
        "status":summary["status"],
        "eligibility":gates.to_dict("records"),
        "transport":summary["transport_2025_metrics"]
    },indent=2,default=str))

if __name__=="__main__":
    main()
