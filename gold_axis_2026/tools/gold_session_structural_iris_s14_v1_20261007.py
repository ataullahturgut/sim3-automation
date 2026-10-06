from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
A1_PATH=AX/"tools"/"gold_session_nova_a1_arcr_raw_replay_v1_20261006.py"
MA15_PATH=AX/"tools"/"gold_session_iris15_crossmetal_v2_maintaware_20261006.py"
RES1H_PATH=AX/"tools"/"gold_session_iris_resolution_matched_v2_derivedxau_20261006.py"
BLUEPRINT=AX/"GOLD_SESSION_IRIS15_VARIABLE_SELECTION_DEV_BLUEPRINT_2026-10-06.json"
OUT=AX/"SESSION_STRUCTURAL_IRIS_S14_V1_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m

a1=loadmod("a1fresh",A1_PATH)
ma15=loadmod("ma15",MA15_PATH)
res1h=loadmod("res1h",RES1H_PATH)
v15=ma15.v1
base=ma15.base

BLOCK=5
MIN_STRUCT_TRAIN=80
INNER_MIN=50
INNER_VAL=15
CS=[0.03,0.10,0.30,1.00,3.00]
SEED=20261006

def clip_logit(p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return np.log(p/(1-p))

def fresh_a1(panel):
    out=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        z=a1.replay_window(g.copy())
        if not z.empty:out.append(z)
    if not out:raise RuntimeError("NO_FRESH_A1")
    q=pd.concat(out,ignore_index=True)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["a1_logit"]=clip_logit(q.p_A1_arcr)
    return q[["partition","window","start_utc","p_A1_arcr","a1_logit","train_n"]].rename(columns={"train_n":"a1_train_n"})

def model_predict(tr,te,features,C=1.0,balanced=False):
    Xtr=tr[features].astype(float).to_numpy(); Xte=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(Xtr)
    m=LogisticRegression(C=C,solver="lbfgs",max_iter=5000,random_state=SEED,
                         class_weight="balanced" if balanced else None)
    m.fit(sc.transform(Xtr),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xte))[:,1]

def l1_select(tr,features,C,balanced):
    X=tr[features].astype(float).to_numpy(); y=tr.y_up.to_numpy(int)
    sc=StandardScaler().fit(X)
    m=LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,random_state=SEED,
                         class_weight="balanced" if balanced else None)
    m.fit(sc.transform(X),y)
    idx=np.flatnonzero(np.abs(m.coef_.ravel())>1e-10)
    return [features[i] for i in idx]

def inner_splits(tr):
    n=len(tr)
    starts=[n-45,n-30,n-15]
    out=[]
    for s in starts:
        if s<INNER_MIN:continue
        va=tr.iloc[s:s+INNER_VAL].copy()
        if va.empty:continue
        cutoff=va.start_utc.min()
        it=tr[(tr.end_utc<=cutoff)&(tr.start_utc<cutoff)].copy()
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:continue
        out.append((it,va))
    return out

def choose_path(tr,path_features,balanced):
    candidates=["a1_logit"]+path_features
    folds=inner_splits(tr)
    if len(folds)<2:
        return path_features,0.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)}
    scores=[]
    for C in CS:
        ys=[];ps=[];ns=[]
        for it,va in folds:
            sel=l1_select(it,candidates,C,balanced)
            # Structural identity: A1 is mandatory even if L1 shrinks it.
            if "a1_logit" not in sel:sel=["a1_logit"]+sel
            try:p=model_predict(it,va,sel,C=0.30,balanced=balanced)
            except Exception:continue
            ys.extend(va.y_up.astype(int).tolist());ps.extend(map(float,p));ns.append(len(sel))
        if not ys:continue
        y=np.asarray(ys,int);p=np.asarray(ps,float);pred=(p>=.5).astype(int)
        ba=float(balanced_accuracy_score(y,pred)); brier=float(np.mean((p-y)**2))
        scores.append({"C":C,"ba":ba,"brier":brier,"mean_selected":float(np.mean(ns))})
    if not scores:return path_features,0.30,{"fallback":"NO_VALID_C"}
    best=max(x["ba"] for x in scores)
    short=[x for x in scores if x["ba"]>=best-0.01]
    chosen=sorted(short,key=lambda x:(x["brier"],x["mean_selected"],x["C"]))[0]
    sel=l1_select(tr,candidates,float(chosen["C"]),balanced)
    if "a1_logit" not in sel:sel=["a1_logit"]+sel
    path=[x for x in sel if x!="a1_logit"]
    return path,float(chosen["C"]),{"candidates":scores,"chosen":chosen}

def metrics(y,p):
    return base.metrics(y,p)

def main():
    # Fresh raw daily structural panel and V5 targets.
    panel,_=base.load_panel()
    base.audit_target_clocks(panel)
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))

    # Fresh A1: generated in this process, never read from archived predictions.
    fa1=fresh_a1(panel)
    panel=panel.merge(fa1,on=["partition","window","start_utc"],how="left",validate="one_to_one")

    # Fresh 15m XAU full IRIS features from governed raw XAU15.
    x15=v15.load_xau15()
    panel=ma15.attach(panel,x15,"g15")
    f15=v15.feature_names("g15")

    # Canonical hourly XAU path, deterministically derived from the same governed XAU15 source.
    x1=res1h.load_xau1h_from_15m()
    panel=res1h.attach(panel,x1,"g1h","1h")
    f1h=res1h.feature_names("g1h")

    common=panel.dropna(subset=["a1_logit"]+f15+f1h+["direction"]).copy()
    if common.empty:raise RuntimeError("EMPTY_S14_COMMON_PANEL")
    for p in ["g15","g1h"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():raise RuntimeError(f"{p}_LEAK")
        if common[f"{p}_max_reference_stale_min"].gt(60).any():raise RuntimeError(f"{p}_STALE")

    bp=json.loads(BLUEPRINT.read_text())
    mode={}
    for h in bp["heads"]:
        key=(h["partition"],h["window"]);choice=h["choice"]
        if choice=="SELECT_XAU15_BAL":mode[key]="SELECT_BAL"
        elif choice=="SELECT_XAU15":mode[key]="SELECT"
        else:mode[key]="FULL"

    rows=[];events=[]
    for (part,win),g0 in common.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        # Only rows with fresh A1 exist in g. The downstream head starts after 80 matured A1-feature rows.
        for bs in range(0,len(g),BLOCK):
            te=g.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<MIN_STRUCT_TRAIN or tr.y_up.nunique()<2:continue

            # Direct fresh A1 comparator on exactly the same scored rows.
            for r in te.itertuples(index=False):
                rows.append({"model":"A1_DIRECT_MATCHED","partition":part,"window":win,
                             "label_date":r.label_date,"start_utc":r.start_utc.isoformat(),
                             "end_utc":r.end_utc.isoformat(),"y_up":int(r.y_up),
                             "p_up":float(r.p_A1_arcr),"train_n":len(tr),
                             "a1_train_n":int(r.a1_train_n)})

            # Canonical S1.4: fresh A1 structural logit + hourly full PATH.
            feats1=["a1_logit"]+f1h
            p1=model_predict(tr,te,feats1,C=1.0,balanced=False)
            for r,p in zip(te.itertuples(index=False),p1):
                rows.append({"model":"S14_A1_PLUS_1H_FULL","partition":part,"window":win,
                             "label_date":r.label_date,"start_utc":r.start_utc.isoformat(),
                             "end_utc":r.end_utc.isoformat(),"y_up":int(r.y_up),"p_up":float(p),
                             "train_n":len(tr),"a1_train_n":int(r.a1_train_n)})

            # 15m full-resolution structural challenger.
            feats15=["a1_logit"]+f15
            p15=model_predict(tr,te,feats15,C=1.0,balanced=False)
            for r,p in zip(te.itertuples(index=False),p15):
                rows.append({"model":"S14_A1_PLUS_15M_FULL","partition":part,"window":win,
                             "label_date":r.label_date,"start_utc":r.start_utc.isoformat(),
                             "end_utc":r.end_utc.isoformat(),"y_up":int(r.y_up),"p_up":float(p),
                             "train_n":len(tr),"a1_train_n":int(r.a1_train_n)})

            # Development-blueprint mode: selection is still recomputed only from current training history.
            m=mode.get((part,win),"FULL")
            if m=="FULL":
                selpath=f15; chosenC=None; detail={"mode":"FULL_FROM_FROZEN_BLUEPRINT"}
                pp=p15
            else:
                bal=(m=="SELECT_BAL")
                selpath,chosenC,detail=choose_path(tr,f15,bal)
                feats=["a1_logit"]+selpath
                pp=model_predict(tr,te,feats,C=0.30,balanced=bal)
            events.append({
                "partition":part,"window":win,"cutoff":pd.Timestamp(cutoff).isoformat(),
                "blueprint_mode":m,"train_n":len(tr),"test_n":len(te),
                "chosen_C":chosenC,"selected_path_n":len(selpath),
                "selected_path_features":json.dumps(selpath,separators=(",",":")),
                "selection_detail":json.dumps(detail,separators=(",",":")),
            })
            for r,p in zip(te.itertuples(index=False),pp):
                rows.append({"model":"S14_A1_PLUS_15M_BLUEPRINT","partition":part,"window":win,
                             "label_date":r.label_date,"start_utc":r.start_utc.isoformat(),
                             "end_utc":r.end_utc.isoformat(),"y_up":int(r.y_up),"p_up":float(p),
                             "train_n":len(tr),"a1_train_n":int(r.a1_train_n)})

    pred=pd.DataFrame(rows); ev=pd.DataFrame(events)
    if pred.empty:raise RuntimeError("NO_S14_PREDICTIONS")

    mrows=[]
    for (model,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        mm=metrics(g.y_up,g.p_up)
        mrows.append({"model":model,"partition":part,"window":win,"period":"2024_SCORED",
                      **mm})
    mdf=pd.DataFrame(mrows)

    # Paired deltas to A1 and canonical 1h on exact same rows.
    pairs=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        piv=g.pivot(index=["label_date","start_utc","y_up"],columns="model",values="p_up").dropna().reset_index()
        if piv.empty:continue
        y=piv.y_up.to_numpy(int)
        mets={}
        for model in ["A1_DIRECT_MATCHED","S14_A1_PLUS_1H_FULL","S14_A1_PLUS_15M_FULL","S14_A1_PLUS_15M_BLUEPRINT"]:
            if model in piv:mets[model]=metrics(y,piv[model].to_numpy(float))
        if "A1_DIRECT_MATCHED" not in mets:continue
        for model,mm in mets.items():
            pairs.append({
                "partition":part,"window":win,"model":model,"n":len(piv),
                "accuracy":mm["accuracy"],"balanced_accuracy":mm["balanced_accuracy"],
                "brier":mm["brier"],"up_recall":mm["up_recall"],"down_recall":mm["down_recall"],
                "delta_ba_vs_A1_pp":100*(mm["balanced_accuracy"]-mets["A1_DIRECT_MATCHED"]["balanced_accuracy"]),
                "delta_brier_vs_A1":mm["brier"]-mets["A1_DIRECT_MATCHED"]["brier"],
                "eligible_n80":bool(len(piv)>=80),
                "recall_floor30":bool(min(mm["up_recall"],mm["down_recall"])>=0.30),
            })
    pdf=pd.DataFrame(pairs)

    cov=[]
    for (part,win),g in common.groupby(["partition","window"],sort=True):
        scored=pred[(pred.partition==part)&(pred.window==win)&(pred.model=="S14_A1_PLUS_1H_FULL")]
        cov.append({
            "partition":part,"window":win,"fresh_a1_feature_rows":len(g),
            "s14_scored_rows":len(scored),
            "first_a1_start":g.start_utc.min().isoformat(),
            "first_s14_scored":None if scored.empty else scored.start_utc.min(),
            "last_s14_scored":None if scored.empty else scored.start_utc.max(),
            "blueprint_mode":mode.get((part,win),"FULL"),
        })
    cdf=pd.DataFrame(cov)

    pred.to_csv(OUT/"predictions.csv",index=False)
    mdf.to_csv(OUT/"metrics.csv",index=False)
    pdf.to_csv(OUT/"paired.csv",index=False)
    ev.to_csv(OUT/"selection_events.csv",index=False)
    cdf.to_csv(OUT/"coverage.csv",index=False)

    summary={
        "status":"S1_4_STRUCTURAL_IRIS_FRESH_COMPLETE",
        "scope":"2023-2024 chronology only; all scored rows occur after fresh A1 warm-up; 2025/2026 unopened",
        "identity":{
            "canonical":"NOVA A1 structural logit + 1h XAU full IRIS PATH",
            "resolution_challenger":"NOVA A1 structural logit + 15m XAU full IRIS PATH",
            "blueprint_challenger":"NOVA A1 structural logit + 15m XAU PATH with previously frozen per-window selection mode; selection recomputed from current training only",
        },
        "freshness":{
            "A1":"regenerated in-process from raw daily Gold/Silver/Platinum CORE3; no archived A1 prediction input",
            "XAU15":"rebuilt in-process from governed raw XAU/USD 15m archive",
            "XAU1h":"deterministically aggregated from the same governed XAU15 archive",
            "target":"V5 target panel independently loaded/reproduced by raw replay functions",
        },
        "training":{
            "A1_recent_n":a1.RECENT_N,
            "structural_min_matured_train":MIN_STRUCT_TRAIN,
            "block":BLOCK,
            "blueprint_path_selection_C_grid":CS,
        },
        "coverage":cov,
        "metrics":mdf.to_dict("records"),
        "paired":pdf.to_dict("records"),
        "guardrails":[
            "Fresh A1 probabilities are generated inside this run; archived A1/IRIS prediction artifacts are not read.",
            "A1 logit is mandatory in every Structural-IRIS fit.",
            "No bar completing at target start is used.",
            "Only matured same-window outcomes enter downstream training.",
            "Selection mode was frozen before S1.4; variable selection inside selected heads uses training history only.",
            "2025 and 2026 are unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# S1.4 STRUCTURAL_IRIS — FRESH A1 + PATH","",
      "**Status:** S1_4_STRUCTURAL_IRIS_FRESH_COMPLETE","",
      "- Fresh A1 regenerated from raw daily metals in-process.",
      "- Canonical head: A1 logit + same-source-derived 1h XAU full IRIS PATH.",
      "- Challengers: A1 + 15m full PATH and A1 + 15m frozen-selection-mode PATH.",
      "- No archived A1/IRIS predictions used.",
      "- 2025/2026 unopened.","",
      "## Paired metrics on exact scored rows","",
      "| Partition | Window | Model | N | Acc | BA | UP | DOWN | Brier | ΔBA vs A1 |",
      "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in pdf.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {r.model} | {r.n} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} | {r.delta_ba_vs_A1_pp:+.2f} pp |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({"status":summary["status"],"coverage":cov,"paired":pdf.to_dict("records")},indent=2,default=str))

if __name__=="__main__":
    main()
