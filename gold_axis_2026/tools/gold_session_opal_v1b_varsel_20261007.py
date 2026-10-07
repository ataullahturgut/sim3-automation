from __future__ import annotations

# workflow trigger: OPAL V1B contract unchanged

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
OPALP=AX/"tools"/"gold_session_opal_v1_20261007.py"
OUT=AX/"SESSION_OPAL_V1B_VARSEL_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

opal=loadmod("opal",OPALP)
FEATURES=list(opal.FEATURES)
DIRECT=FEATURES[:14]
CONTEXT=FEATURES[14:]
CS=[0.03,0.10,0.30,1.00,3.00]
INNER_MIN=50
INNER_VAL=15
MIN_FEATURES=3
MAX_FEATURES=8

def l1_model(C):
    return LogisticRegression(
        C=C,penalty="l1",solver="liblinear",max_iter=5000,
        class_weight="balanced",random_state=opal.SEED
    )

def final_model():
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,
        class_weight="balanced",random_state=opal.SEED
    )

def rev_metrics(y,p):
    return opal.metric(y,p)

def enforce_identity(sel,cmap):
    sel=list(dict.fromkeys(sel))
    ranked=sorted(FEATURES,key=lambda f:abs(float(cmap.get(f,0.0))),reverse=True)
    if not any(f in DIRECT for f in sel):
        cand=[f for f in ranked if f in DIRECT]
        if cand:sel.append(cand[0])
    if not any(f in CONTEXT for f in sel):
        cand=[f for f in ranked if f in CONTEXT]
        if cand:sel.append(cand[0])
    for f in ranked:
        if len(sel)>=MIN_FEATURES:break
        if f not in sel:sel.append(f)
    return sel

def selector_fit(tr,C):
    X=tr[FEATURES].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=l1_model(C).fit(sc.transform(X),tr.reversal_target.astype(int).to_numpy())
    co=m.coef_.ravel()
    cmap={FEATURES[i]:float(co[i]) for i in range(len(FEATURES))}
    sel=[f for f in FEATURES if abs(cmap[f])>1e-10]
    sel=enforce_identity(sel,cmap)
    return sel,cmap

def inner_splits(tr):
    tr=tr.sort_values("start_utc").reset_index(drop=True)
    n=len(tr);out=[]
    for s in [n-45,n-30,n-15]:
        if s<INNER_MIN:continue
        va=tr.iloc[s:s+INNER_VAL].copy()
        if va.empty or va.reversal_target.nunique()<2:continue
        cut=va.start_utc.min()
        it=tr[(tr.end_utc<=cut)&(tr.start_utc<cut)].copy()
        if len(it)<INNER_MIN or it.reversal_target.nunique()<2:continue
        out.append((it,va))
    return out

def choose_features(tr):
    folds=inner_splits(tr)
    if len(folds)<2:
        sel,cmap=selector_fit(tr,.30)
        return sel,.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)},cmap

    rows=[]
    for C in CS:
        ys=[];ps=[];ns=[];ok=True
        for it,va in folds:
            try:
                sel,_=selector_fit(it,C)
                sc=StandardScaler().fit(it[sel].astype(float).to_numpy())
                m=final_model().fit(sc.transform(it[sel].astype(float).to_numpy()),
                                    it.reversal_target.astype(int).to_numpy())
                pv=m.predict_proba(sc.transform(va[sel].astype(float).to_numpy()))[:,1]
            except Exception:
                ok=False;break
            ys.extend(va.reversal_target.astype(int).tolist())
            ps.extend(map(float,pv));ns.append(len(sel))
        if not ok or not ys:continue
        mm=rev_metrics(ys,ps)
        rows.append({"C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
                     "mean_selected":float(np.mean(ns))})
    if not rows:
        sel,cmap=selector_fit(tr,.30)
        return sel,.30,{"fallback":"NO_VALID_CANDIDATE"},cmap

    best=max(r["ba"] for r in rows)
    short=[r for r in rows if r["ba"]>=best-.01]
    chosen=sorted(short,key=lambda r:(r["brier"],r["mean_selected"],r["C"]))[0]
    sel,cmap=selector_fit(tr,float(chosen["C"]))
    return sel,float(chosen["C"]),{"scores":rows,"chosen":chosen},cmap

def correction_rows(te,p_rev,features,train_n,model_name):
    rows=[]
    for r,pr in zip(te.itertuples(index=False),p_rev):
        follows=bool(r.aurora_follows_momentum)
        override=bool(follows and float(pr)>=opal.THRESH)
        pa=float(r.p_aurora)
        if override:
            po=float(1-pr) if int(r.momentum_up)==1 else float(pr)
        else:
            po=pa
        rows.append({
            "model":model_name,"partition":r.partition,"window":r.window,
            "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
            "year":int(r.year),"y_up":int(r.y_up),"p_aurora":pa,
            "p_reversal":float(pr),"momentum_up":int(r.momentum_up),
            "aurora_follows_momentum":follows,"override":override,
            "p_opal":po,"train_n":int(train_n),"features":"|".join(features)
        })
    return rows

def dev_nested(panel):
    preds=[];events=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.year.isin([2023,2024])].copy()
        for mo in sorted(test.month_key.unique()):
            te=test[test.month_key.eq(mo)].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<opal.MIN_TRAIN or tr.reversal_target.nunique()<2:continue
            sel,C,detail,cmap=choose_features(tr)
            sc=StandardScaler().fit(tr[sel].astype(float).to_numpy())
            m=final_model().fit(sc.transform(tr[sel].astype(float).to_numpy()),
                                tr.reversal_target.astype(int).to_numpy())
            pr=m.predict_proba(sc.transform(te[sel].astype(float).to_numpy()))[:,1]
            preds.extend(correction_rows(te,pr,sel,len(tr),"SELECTED_OPAL_NESTED"))
            events.append({
                "partition":part,"window":win,"month":mo,
                "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),
                "train_n":int(len(tr)),"selector_C":C,
                "selected_features":json.dumps(sel,separators=(",",":")),
                "coefficients":json.dumps(cmap,separators=(",",":")),
                "detail":json.dumps(detail,separators=(",",":"))
            })
    return pd.DataFrame(preds),pd.DataFrame(events)

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
        total=max(1,len(e));rows=[]
        for f,n in counts.items():
            rows.append({
                "feature":f,"freq":n/total,"both_years":len(years[f])>=2,
                "mean_abs_coef":float(np.mean(mag[f])) if mag[f] else 0.0
            })
        q=pd.DataFrame(rows).sort_values(
            ["both_years","freq","mean_abs_coef"],ascending=[False,False,False]
        )
        chosen=q[q.both_years].feature.tolist()[:MAX_FEATURES]
        if len(chosen)<MIN_FEATURES:
            for f in q.feature.tolist():
                if f not in chosen:chosen.append(f)
                if len(chosen)>=MIN_FEATURES:break
        rank=q.feature.tolist()
        if not any(f in DIRECT for f in chosen):
            cand=[f for f in rank if f in DIRECT]
            if cand:chosen.append(cand[0])
        if not any(f in CONTEXT for f in chosen):
            cand=[f for f in rank if f in CONTEXT]
            if cand:chosen.append(cand[0])
        chosen=list(dict.fromkeys(chosen))
        while len(chosen)>MAX_FEATURES:
            removed=False
            for f in reversed(rank):
                if f not in chosen:continue
                trial=[x for x in chosen if x!=f]
                if len(trial)>=MIN_FEATURES and any(x in DIRECT for x in trial) and any(x in CONTEXT for x in trial):
                    chosen=trial;removed=True;break
            if not removed:break
        out.append({
            "partition":part,"window":win,"frozen_features":chosen,
            "n_features":len(chosen),"selection_events":int(total)
        })
    return out

def gate_nested(pred):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        reasons=[]
        for yr in [2023,2024]:
            z=g[g.year.eq(yr)]
            if z.empty:continue
            ma=opal.metric(z.y_up,z.p_aurora);mo=opal.metric(z.y_up,z.p_opal)
            if mo["accuracy"]+.01+1e-12<ma["accuracy"]:reasons.append(f"{yr}_ACC")
            if mo["brier"]>ma["brier"]+.003+1e-12:reasons.append(f"{yr}_BRIER")
        ma=opal.metric(g.y_up,g.p_aurora);mo=opal.metric(g.y_up,g.p_opal)
        ad=(g.p_aurora>=.5).astype(int);od=(g.p_opal>=.5).astype(int);y=g.y_up.astype(int)
        ch=ad.ne(od);resc=int((ch&ad.ne(y)&od.eq(y)).sum());brok=int((ch&ad.eq(y)&od.ne(y)).sum())
        net=resc-brok
        if mo["balanced_accuracy"]+1e-12<ma["balanced_accuracy"]:reasons.append("DEV_BA")
        if min(mo["up_recall"],mo["down_recall"])<.30:reasons.append("RECALL_FLOOR")
        if net<=0:reasons.append("NET_RESCUE_NOT_POSITIVE")
        if int(g.override.sum())==0:reasons.append("NO_OVERRIDE")
        rows.append({
            "partition":part,"window":win,"eligible":len(reasons)==0,
            "reason":"PASS" if not reasons else "|".join(reasons),
            "dev_n":int(len(g)),"aurora_ba":ma["balanced_accuracy"],
            "opal_ba":mo["balanced_accuracy"],"opal_up_recall":mo["up_recall"],
            "opal_down_recall":mo["down_recall"],"aurora_brier":ma["brier"],
            "opal_brier":mo["brier"],"override_n":int(g.override.sum()),
            "rescued":resc,"broken":brok,"net_rescue":net
        })
    return pd.DataFrame(rows)

def frozen_2025(panel,frozen,eligible):
    fmap={(x["partition"],x["window"]):x["frozen_features"] for x in frozen}
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        if (part,win) not in eligible or (part,win) not in fmap:continue
        sel=fmap[(part,win)]
        g=g0.sort_values("start_utc").reset_index(drop=True)
        teall=g[g.year.eq(2025)].copy()
        for mo in sorted(teall.month_key.unique()):
            te=teall[teall.month_key.eq(mo)].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<opal.MIN_TRAIN or tr.reversal_target.nunique()<2:continue
            for name,fs in [("SELECTED_OPAL",sel),("CANONICAL_OPAL",FEATURES)]:
                sc=StandardScaler().fit(tr[fs].astype(float).to_numpy())
                m=final_model().fit(sc.transform(tr[fs].astype(float).to_numpy()),
                                    tr.reversal_target.astype(int).to_numpy())
                pr=m.predict_proba(sc.transform(te[fs].astype(float).to_numpy()))[:,1]
                rows.extend(correction_rows(te,pr,fs,len(tr),name))
    return pd.DataFrame(rows)

def metrics_by_model(pred,period):
    rows=[]
    for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        ma=opal.metric(g.y_up,g.p_aurora);mo=opal.metric(g.y_up,g.p_opal)
        ad=(g.p_aurora>=.5).astype(int);od=(g.p_opal>=.5).astype(int);y=g.y_up.astype(int)
        ch=ad.ne(od);resc=int((ch&ad.ne(y)&od.eq(y)).sum());brok=int((ch&ad.eq(y)&od.ne(y)).sum())
        rows.append({
            "period":period,"model":m,"partition":part,"window":win,
            "override_n":int(g.override.sum()),"rescued":resc,"broken":brok,
            "net_rescue":resc-brok,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"opal_{k}":v for k,v in mo.items()}
        })
    return pd.DataFrame(rows)

def main():
    panel=opal.build_panel()
    dev,events=dev_nested(panel)
    if dev.empty:raise RuntimeError("OPAL_VARSEL_NO_DEV")
    frozen=freeze(events)
    gate=gate_nested(dev)
    eligible={(r.partition,r.window) for r in gate.itertuples(index=False) if bool(r.eligible)}
    tr=frozen_2025(panel,frozen,eligible)

    events.to_csv(OUT/"selection_events.csv",index=False)
    pd.DataFrame(frozen).to_json(OUT/"frozen_features.json",orient="records",indent=2)
    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    gate.to_csv(OUT/"eligibility.csv",index=False)
    metrics_by_model(dev,"DEV_2023_2024_NESTED").to_csv(OUT/"dev_metrics.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        metrics_by_model(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)

    summary={
        "status":"SESSION_OPAL_V1B_VARSEL_COMPLETE",
        "candidate_features":FEATURES,
        "frozen_features":frozen,
        "development_gate":gate.to_dict("records"),
        "eligible_heads":[{"partition":p,"window":w} for p,w in sorted(eligible)],
        "transport_2025_metrics":metrics_by_model(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "guardrails":[
            "Variable selection uses 2023-2024 only.",
            "No new feature entered the OPAL family.",
            "Final estimator and reversal threshold 0.70 are unchanged.",
            "Every frozen subset contains direct COT positioning plus trend/context information.",
            "2025 is transport only.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION OPAL V1B — VARIABLE-SELECTION RESULT","",
           "## Frozen features","",
           "| Partition | Window | Features |","|---|---|---|"]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_features'])} |")
    lines += ["","## Pre-2025 nested eligibility","",
              "| Partition | Window | N | AURORA BA | Selected OPAL BA | UP | DOWN | Overrides | Net rescue | Eligible | Reason |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in gate.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.dev_n)} | "
                     f"{100*r.aurora_ba:.2f}% | {100*r.opal_ba:.2f}% | "
                     f"{100*r.opal_up_recall:.2f}% | {100*r.opal_down_recall:.2f}% | "
                     f"{int(r.override_n)} | {int(r.net_rescue):+d} | {r.eligible} | {r.reason} |")
    lines += ["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No selected OPAL head passed the frozen pre-2025 gate; 2025 remained closed.")
    else:
        tm=metrics_by_model(tr,"FROZEN_2025")
        lines += ["| Model | Partition | Window | N | OPAL BA | UP | DOWN | Brier | Overrides | Net rescue |",
                  "|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for r in tm.itertuples(index=False):
            lines.append(f"| {r.model} | {r.partition} | {r.window} | {int(r.opal_n)} | "
                         f"{100*r.opal_balanced_accuracy:.2f}% | {100*r.opal_up_recall:.2f}% | "
                         f"{100*r.opal_down_recall:.2f}% | {r.opal_brier:.4f} | "
                         f"{int(r.override_n)} | {int(r.net_rescue):+d} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
