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
VEGAP=AX/"tools"/"gold_session_vega_v1_20261007.py"
OUT=AX/"SESSION_VEGA_V1B_VARSEL_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

v0=loadmod("vegav1",VEGAP)
FEATURES=list(v0.FEATURES)
CS=[0.03,0.10,0.30,1.00,3.00]
INNER_MIN=60
MIN_SELECTED=2
MAX_FROZEN=6
SEED=20261007

def selector(C):
    return LogisticRegression(
        C=C,penalty="l1",solver="liblinear",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def final_model():
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def rev_metrics(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    tp=((pred==1)&(y==1)).sum();fn=((pred==0)&(y==1)).sum()
    tn=((pred==0)&(y==0)).sum();fp=((pred==1)&(y==0)).sum()
    rr=tp/(tp+fn) if tp+fn else 0.0
    rn=tn/(tn+fp) if tn+fp else 0.0
    return {"balanced_accuracy":float((rr+rn)/2),"brier":float(np.mean((p-y)**2))}

def fit_selector(tr,C):
    X=tr[FEATURES].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=selector(C).fit(sc.transform(X),tr.reversal_target.to_numpy(int))
    co=m.coef_.ravel()
    cmap={FEATURES[i]:float(co[i]) for i in range(len(FEATURES))}
    sel=[f for f in FEATURES if abs(cmap[f])>1e-10]
    if len(sel)<MIN_SELECTED:
        ranked=sorted(FEATURES,key=lambda f:abs(cmap[f]),reverse=True)
        for f in ranked:
            if f not in sel:sel.append(f)
            if len(sel)>=MIN_SELECTED:break
    return sel,cmap

def fit_predict(tr,te,features):
    X=tr[features].astype(float).to_numpy()
    Xt=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=final_model().fit(sc.transform(X),tr.reversal_target.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def inner_month_folds(tr):
    tr=tr.sort_values("start_utc").reset_index(drop=True)
    out=[]
    for mo in sorted(tr.month_key.unique())[-3:]:
        va=tr[tr.month_key.eq(mo)].copy()
        if va.empty or va.reversal_target.nunique()<2:continue
        cut=va.start_utc.min()
        it=tr[(tr.end_utc<=cut)&(tr.start_utc<cut)].copy()
        if len(it)<INNER_MIN or it.reversal_target.nunique()<2:continue
        out.append((it,va,mo))
    return out

def choose_features(tr):
    folds=inner_month_folds(tr)
    if len(folds)<2:
        try:
            sel,cmap=fit_selector(tr,.30)
            return sel,.30,{"fallback":"INSUFFICIENT_INNER_MONTHS","folds":len(folds)},cmap
        except Exception:
            return FEATURES.copy(),1.0,{"fallback":"SELECTOR_FAILURE_FULL"},{f:0.0 for f in FEATURES}

    scores=[]
    for C in CS:
        ys=[];ps=[];ns=[];ok=True
        for it,va,mo in folds:
            try:
                sel,_=fit_selector(it,C)
                pp=fit_predict(it,va,sel)
            except Exception:
                ok=False;break
            ys.extend(va.reversal_target.astype(int).tolist())
            ps.extend(map(float,pp));ns.append(len(sel))
        if not ok or not ys:continue
        mm=rev_metrics(ys,ps)
        scores.append({"C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
                       "mean_selected":float(np.mean(ns))})
    if not scores:
        sel,cmap=fit_selector(tr,.30)
        return sel,.30,{"fallback":"NO_VALID_CANDIDATE"},cmap

    best=max(x["ba"] for x in scores)
    short=[x for x in scores if x["ba"]>=best-.01]
    chosen=sorted(short,key=lambda x:(x["brier"],x["mean_selected"],x["C"]))[0]
    sel,cmap=fit_selector(tr,float(chosen["C"]))
    return sel,float(chosen["C"]),{"scores":scores,"chosen":chosen},cmap

def replay_selected(panel):
    rows=[];events=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        teall=g[g.year.isin([2023,2024])].copy()
        for mo in sorted(teall.month_key.unique()):
            te=teall[teall.month_key.eq(mo)].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<v0.MIN_TRAIN or tr.reversal_target.nunique()<2:continue
            sel,C,detail,cmap=choose_features(tr)
            pp=fit_predict(tr,te,sel)
            events.append({
                "partition":part,"window":win,"outer_month":mo,
                "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),
                "train_n":int(len(tr)),"selector_C":C,
                "selected_features":json.dumps(sel,separators=(",",":")),
                "coefficients":json.dumps(cmap,separators=(",",":")),
                "detail":json.dumps(detail,separators=(",",":"))
            })
            for rr,pv in zip(te.itertuples(index=False),pp):
                rows.append({
                    "partition":part,"window":win,"label_date":rr.label_date,
                    "start_utc":rr.start_utc,"end_utc":rr.end_utc,
                    "year":int(rr.year),"y_up":int(rr.y_up),
                    "momentum_up":int(rr.momentum_up),
                    "reversal_target":int(rr.reversal_target),
                    "p_reversal":float(pv),
                    "gvz_date_used":pd.Timestamp(rr.gvz_date_used).date().isoformat(),
                    "train_n":int(len(tr)),
                    "selected_features":"|".join(sel)
                })
    return pd.DataFrame(rows),pd.DataFrame(events)

def freeze(events):
    out=[]
    for (part,win),e in events.groupby(["partition","window"],sort=True):
        counts=Counter();years=defaultdict(set);mag=defaultdict(list)
        for r in e.itertuples(index=False):
            fs=json.loads(r.selected_features);cm=json.loads(r.coefficients)
            counts.update(fs)
            for f in fs:
                years[f].add(int(r.outer_year))
                mag[f].append(abs(float(cm.get(f,0.0))))
        total=max(1,len(e))
        rows=[]
        for f,n in counts.items():
            rows.append({"feature":f,"freq":n/total,"both_years":len(years[f])>=2,
                         "mean_abs_coef":float(np.mean(mag[f])) if mag[f] else 0.0})
        q=pd.DataFrame(rows).sort_values(
            ["both_years","freq","mean_abs_coef"],ascending=[False,False,False]
        )
        chosen=q[q.both_years].feature.tolist()[:MAX_FROZEN]
        if len(chosen)<MIN_SELECTED:
            for f in q.feature.tolist():
                if f not in chosen:chosen.append(f)
                if len(chosen)>=MIN_SELECTED:break
        if not chosen:chosen=FEATURES[:MIN_SELECTED]
        chosen=chosen[:MAX_FROZEN]
        out.append({"partition":part,"window":win,"frozen_features":chosen,
                    "n_features":len(chosen),"outer_months":int(total)})
    return out

def correction_metrics(pred):
    metrics=[];changed=[]
    for name,b in v0.rift.load_baselines().items():
        z,rows=v0.rift.correct(b,pred,name)
        metrics.extend(rows)
        if not z.empty:
            q=z[z.override].copy()
            if not q.empty:
                q["baseline_name"]=name;changed.append(q)
    mdf=pd.DataFrame(metrics)
    gate=v0.rift.pass_table(mdf)
    ch=pd.concat(changed,ignore_index=True) if changed else pd.DataFrame()
    return mdf,gate,ch

def main():
    panel=v0.build_panel()
    pred,events=replay_selected(panel)
    frozen=freeze(events)
    mdf,gate,changed=correction_metrics(pred)

    pred.to_csv(OUT/"vega_selected_predictions.csv",index=False)
    events.to_csv(OUT/"selection_events.csv",index=False)
    pd.DataFrame(frozen).to_json(OUT/"frozen_features.json",orient="records",indent=2)
    mdf.to_csv(OUT/"correction_metrics.csv",index=False)
    gate.to_csv(OUT/"transport_eligibility.csv",index=False)
    changed.to_csv(OUT/"changed_calls.csv",index=False)

    summary={
        "status":"SESSION_VEGA_V1B_VARSEL_DEVELOPMENT_COMPLETE",
        "scope":"2022 warm-up; 2023-2024 nested variable selection; 2025 unopened",
        "threshold":v0.THRESH,
        "gvz_rule":"latest observation dated <= NY origin date D-1 calendar day",
        "candidate_features":FEATURES,
        "frozen_features":frozen,
        "transport_eligible":gate[gate.transport_eligible].to_dict("records"),
        "guardrails":[
            "No new feature family added.",
            "D-1 GVZ rule unchanged.",
            "Reversal target unchanged.",
            "Final balanced Logistic C=1.0 unchanged.",
            "Correction threshold remains 0.70.",
            "No 2025 or 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION VEGA V1B — VARIABLE-SELECTION DEVELOPMENT RESULT","",
           "**Status:** complete; 2025 unopened.","",
           "## Frozen per-session variables","",
           "| Partition | Window | Frozen variables |","|---|---|---|"]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_features'])} |")
    lines += ["","## Pre-2025 downstream transport eligibility",""]
    e=gate[gate.transport_eligible]
    if e.empty:lines.append("- none")
    else:
        for r in e.itertuples(index=False):
            lines.append(f"- {r.partition} / {r.window} / {r.baseline}")
    lines += ["","2025 remained closed throughout this run."]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({"status":summary["status"],"frozen_features":frozen,
                      "transport_eligible":summary["transport_eligible"]},indent=2,default=str))

if __name__=="__main__":
    main()
