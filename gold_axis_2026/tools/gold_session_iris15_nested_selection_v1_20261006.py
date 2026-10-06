from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
MA15_PATH=AX/"tools"/"gold_session_iris15_crossmetal_v2_maintaware_20261006.py"
OUT=AX/"SESSION_IRIS15_NESTED_SELECTION_V1_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m

ma15=loadmod("ma15",MA15_PATH)
v15=ma15.v1
base=ma15.base

CORE3=list(ma15.CORE3)
BLOCK=5
MIN_TRAIN=180
INNER_MIN=120
INNER_VAL=20
CS=[0.03,0.10,0.30,1.00,3.00]
REFIT_C=0.30
SEED=20261006

def make_l2():
    return LogisticRegression(C=REFIT_C,solver="lbfgs",max_iter=5000,random_state=SEED)

def fit_selector(df,features,C):
    X=df[features].astype(float).to_numpy()
    y=df.y_up.to_numpy(int)
    sc=StandardScaler().fit(X)
    Xs=sc.transform(X)
    m=LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,random_state=SEED)
    m.fit(Xs,y)
    coef=m.coef_.ravel()
    idx=np.flatnonzero(np.abs(coef)>1e-10)
    selected=[features[i] for i in idx]
    coefs={features[i]:float(coef[i]) for i in idx}
    return selected,coefs

def fit_refit_predict(tr,te,selected):
    if not selected:
        p=np.full(len(te),float(tr.y_up.mean()))
        return p
    Xtr=tr[selected].astype(float).to_numpy()
    Xte=te[selected].astype(float).to_numpy()
    y=tr.y_up.to_numpy(int)
    sc=StandardScaler().fit(Xtr)
    m=make_l2().fit(sc.transform(Xtr),y)
    return m.predict_proba(sc.transform(Xte))[:,1]

def inner_splits(tr):
    n=len(tr)
    if n<MIN_TRAIN:return []
    start=max(INNER_MIN,n-3*INNER_VAL)
    # Align backward so the final 60-ish observations form three sequential validations.
    starts=[]
    s=start
    while s+INNER_VAL<=n and len(starts)<3:
        starts.append(s);s+=INNER_VAL
    if len(starts)<3:
        starts=[n-60,n-40,n-20]
    out=[]
    for s in starts:
        va=tr.iloc[s:min(s+INNER_VAL,n)].copy()
        if va.empty:continue
        cutoff=va.start_utc.min()
        it=tr[(tr.end_utc<=cutoff)&(tr.start_utc<cutoff)].copy()
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:
            continue
        out.append((it,va))
    return out

def choose_C(tr,features):
    folds=inner_splits(tr)
    if len(folds)<2:
        return 0.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)}
    rows=[]
    for C in CS:
        ys=[];ps=[];sel_ns=[]
        valid=True
        for it,va in folds:
            try:
                sel,_=fit_selector(it,features,C)
                p=fit_refit_predict(it,va,sel)
            except Exception:
                valid=False;break
            ys.extend(va.y_up.astype(int).tolist());ps.extend(map(float,p));sel_ns.append(len(sel))
        if not valid or not ys:continue
        y=np.asarray(ys,int);p=np.asarray(ps,float);pred=(p>=.5).astype(int)
        ba=float(balanced_accuracy_score(y,pred))
        brier=float(np.mean((p-y)**2))
        rows.append({"C":C,"ba":ba,"brier":brier,"mean_selected":float(np.mean(sel_ns)),"n":len(y)})
    if not rows:
        return 0.30,{"fallback":"NO_VALID_CANDIDATE","folds":len(folds)}
    best_ba=max(r["ba"] for r in rows)
    shortlist=[r for r in rows if r["ba"]>=best_ba-0.01]
    # Within 1pp of best inner BA, prefer calibration, then parsimony, then stronger sparsity.
    chosen=sorted(shortlist,key=lambda r:(r["brier"],r["mean_selected"],r["C"]))[0]
    return float(chosen["C"]),{"candidates":rows,"chosen":chosen,"folds":len(folds)}

def baseline_predict(tr,te,features):
    Xtr=tr[features].astype(float).to_numpy();Xte=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(Xtr)
    m=LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED).fit(sc.transform(Xtr),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xte))[:,1]

def classify_feature(name):
    source="DAILY"
    if name.startswith("g_"):source="XAU15"
    elif name.startswith("si_"):source="SI15"
    elif name.startswith("pl_"):source="PL15"
    elif name.startswith("gold_"):source="GOLD_DAILY"
    elif name.startswith("silver_"):source="SILVER_DAILY"
    elif name.startswith("platinum_"):source="PLATINUM_DAILY"

    family="OTHER";horizon=None
    m=re.search(r"_ret_(\d+)h$",name)
    if m:family="RETURN";horizon=int(m.group(1))
    elif name.endswith("_lag2"):family="LAG2";horizon=2
    else:
        m=re.search(r"_rv_(\d+)$",name)
        if m:family="RV";horizon=int(m.group(1))
        elif "semivol" in name:family="SEMIVOL";horizon=24
        elif "jump_concentration" in name:family="JUMP";horizon=24
        elif "_range_24" in name:family="RANGE";horizon=24
        elif "_slope_" in name:
            family="SLOPE";horizon=int(name.rsplit("_",1)[-1])
        elif any(k in name for k in ["upfrac_24","max_drawdown_24","recovery_24","close_location_24","age_max_pos_24","age_max_neg_24"]):
            family="SHAPE";horizon=24
        elif name=="sigma20":family="SIGMA";horizon=20
        elif "sigma20" in name:family="SIGMA";horizon=20
        elif re.search(r"_r\d+$",name):
            family="DAILY_RETURN";horizon=int(re.search(r"_r(\d+)$",name).group(1))
        elif name.endswith("_age_days"):family="AGE"

    return source,family,horizon

def summarize(pred):
    rows=[]
    for (model,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        met=base.metrics(g.y_up,g.p_up)
        rows.append({"model":model,"partition":part,"window":win,"period":"2024","n":len(g),**{k:v for k,v in met.items() if k!="n"}})
    return pd.DataFrame(rows)

def main():
    panel,_=base.load_panel();base.audit_target_clocks(panel)
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))

    xau=v15.load_xau15();si=v15.load_fut15("SI.n.0");pl=v15.load_fut15("PL.n.0")
    panel=ma15.attach(panel,xau,"g")
    panel=ma15.attach(panel,si,"si")
    panel=ma15.attach(panel,pl,"pl")

    gf=v15.feature_names("g");sif=v15.feature_names("si");plf=v15.feature_names("pl")
    xau_pool=CORE3+gf
    all_pool=CORE3+gf+sif+plf
    common=panel.dropna(subset=all_pool+["direction"]).copy()

    for p in ["g","si","pl"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():raise RuntimeError(f"{p}_LEAK")
        if common[f"{p}_max_reference_stale_min"].gt(60).any():raise RuntimeError(f"{p}_STALE")

    preds=[];events=[]
    for (part,win),g0 in common.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        for bs in range(0,len(g),BLOCK):
            te=g.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue

            # Fixed full-XAU reference on exact same rows.
            pb=baseline_predict(tr,te,xau_pool)
            for r,p in zip(te.itertuples(index=False),pb):
                preds.append({"model":"FULL_XAU15_L2_C1","label_date":r.label_date,"partition":part,"window":win,
                              "start_utc":r.start_utc.isoformat(),"y_up":int(r.y_up),"p_up":float(p),"train_n":len(tr)})

            for model,pool in [("SELECT_XAU15",xau_pool),("SELECT_ALL15",all_pool)]:
                C,inner=choose_C(tr,pool)
                sel,coef=fit_selector(tr,pool,C)
                p=fit_refit_predict(tr,te,sel)
                block_id=f"{part}|{win}|{pd.Timestamp(cutoff).isoformat()}"
                events.append({
                    "block_id":block_id,"partition":part,"window":win,"cutoff":pd.Timestamp(cutoff).isoformat(),
                    "model":model,"train_n":len(tr),"test_n":len(te),"chosen_C":C,
                    "selected_n":len(sel),"selected_features":json.dumps(sel,separators=(",",":")),
                    "selected_coefficients":json.dumps(coef,separators=(",",":")),
                    "inner_detail":json.dumps(inner,separators=(",",":")),
                })
                for r,pp in zip(te.itertuples(index=False),p):
                    preds.append({"model":model,"label_date":r.label_date,"partition":part,"window":win,
                                  "start_utc":r.start_utc.isoformat(),"y_up":int(r.y_up),"p_up":float(pp),"train_n":len(tr),
                                  "chosen_C":C,"selected_n":len(sel)})

    pred=pd.DataFrame(preds)
    ev=pd.DataFrame(events)
    mdf=summarize(pred)

    # Selection stability by window/model/feature across outer training blocks.
    stab=[]
    for (model,part,win),e in ev.groupby(["model","partition","window"],sort=True):
        total=len(e);counts=Counter();abscoef=defaultdict(list)
        for rr in e.itertuples(index=False):
            feats=json.loads(rr.selected_features);co=json.loads(rr.selected_coefficients)
            counts.update(feats)
            for k,v in co.items():abscoef[k].append(abs(float(v)))
        for feat,n in counts.items():
            source,family,horizon=classify_feature(feat)
            stab.append({
                "model":model,"partition":part,"window":win,"feature":feat,
                "source":source,"family":family,"horizon":horizon,
                "selected_blocks":n,"eligible_blocks":total,"selection_frequency":n/total,
                "mean_abs_l1_coef_when_selected":float(np.mean(abscoef[feat])),
            })
    sdf=pd.DataFrame(stab).sort_values(["model","partition","window","selection_frequency","mean_abs_l1_coef_when_selected"],ascending=[True,True,True,False,False])

    # Aggregate lag/family stability.
    lrows=[]
    if not sdf.empty:
        for keys,z in sdf.groupby(["model","partition","window","source","family","horizon"],dropna=False,sort=True):
            model,part,win,source,family,horizon=keys
            lrows.append({
                "model":model,"partition":part,"window":win,"source":source,"family":family,
                "horizon":horizon,"max_feature_selection_frequency":float(z.selection_frequency.max()),
                "mean_feature_selection_frequency":float(z.selection_frequency.mean()),
                "features_in_group":int(len(z)),
            })
    ldf=pd.DataFrame(lrows)

    # Summary of cross-metal admission.
    xmetal=[]
    for (part,win),e in ev[ev.model.eq("SELECT_ALL15")].groupby(["partition","window"],sort=True):
        n=len(e);si=pln=both=0
        for rr in e.itertuples(index=False):
            s=json.loads(rr.selected_features)
            hs=any(x.startswith("si_") or x.startswith("silver_") for x in s)
            hp=any(x.startswith("pl_") or x.startswith("platinum_") for x in s)
            si+=hs;pln+=hp;both+=(hs and hp)
        xmetal.append({"partition":part,"window":win,"blocks":n,
                       "silver_selected_block_rate":si/n,"platinum_selected_block_rate":pln/n,
                       "both_selected_block_rate":both/n})
    xdf=pd.DataFrame(xmetal)

    pred.to_csv(OUT/"predictions.csv",index=False)
    ev.to_csv(OUT/"selection_events.csv",index=False)
    mdf.to_csv(OUT/"metrics.csv",index=False)
    sdf.to_csv(OUT/"feature_stability.csv",index=False)
    ldf.to_csv(OUT/"lag_family_stability.csv",index=False)
    xdf.to_csv(OUT/"crossmetal_admission.csv",index=False)

    # Compact top features for report.
    top=[]
    for (model,part,win),z in sdf.groupby(["model","partition","window"],sort=True):
        q=z.head(12)
        top.append({"model":model,"partition":part,"window":win,
                    "top_features":[{"feature":r.feature,"freq":r.selection_frequency,"source":r.source,"family":r.family,"horizon":r.horizon}
                                    for r in q.itertuples(index=False)]})

    summary={
        "status":"SESSION_IRIS15_NESTED_SELECTION_V1_COMPLETE",
        "scope":"2023-2024 development chronology only; 2025/2026 unopened",
        "selection_contract":{
            "outer_replay":"same-window expanding causal blocks of 5; training labels must mature before cutoff",
            "inner_validation":"up to 3 chronological expanding validation folds of 20 rows inside outer training only",
            "selector":"StandardScaler + L1 LogisticRegression(liblinear)",
            "C_grid":CS,
            "C_choice":"maximize inner balanced accuracy; among candidates within 1pp of max BA choose lowest Brier, then fewer features, then smaller C",
            "post_selection_refit":f"StandardScaler + L2 LogisticRegression C={REFIT_C}",
            "pools":{
                "SELECT_XAU15":"daily CORE3 + XAU15 full IRIS",
                "SELECT_ALL15":"daily CORE3 + XAU15 + SI15 + PL15 full IRIS"
            },
            "fixed_reference":"FULL_XAU15_L2_C1",
            "no_global_outcome_selection":True,
        },
        "common_rows":int(len(common)),
        "metrics":mdf.to_dict("records"),
        "crossmetal_admission":xdf.to_dict("records"),
        "top_features":top,
        "guardrails":[
            "No 2024 test block is used to select its own variables or lag hyperparameter.",
            "No 2025 or 2026 outcome is opened.",
            "Gold sigma20 and all daily/intraday candidate variables are selectable, not forced.",
            "Silver/Platinum can enter only through training-only sparse selection.",
            "Selection stability is reported by outer block; one-off selections are not architecture evidence."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# SESSION IRIS15 — NESTED VARIABLE / LAG SELECTION V1","",
      "**Status:** SESSION_IRIS15_NESTED_SELECTION_V1_COMPLETE","",
      "- 2023–2024 development chronology only; 2025/2026 unopened.",
      "- Every outer test block selects variables using only earlier training data.",
      "- L1 selects variables/lags; selected set is refit with L2 C=0.30.",
      "- Silver/Platinum are optional candidates, never forced.","",
      "## 2024 outer-replay metrics","",
      "| Model | Partition | Window | N | Acc | BA | Brier |",
      "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in mdf.itertuples(index=False):
        lines.append(f"| {r.model} | {r.partition} | {r.window} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} |")
    lines += ["","## Cross-metal selection rates","","| Partition | Window | Blocks | Silver selected | Platinum selected | Both |","|---|---|---:|---:|---:|---:|"]
    for r in xdf.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {r.blocks} | {100*r.silver_selected_block_rate:.1f}% | {100*r.platinum_selected_block_rate:.1f}% | {100*r.both_selected_block_rate:.1f}% |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({"status":summary["status"],"common_rows":len(common),"metrics":mdf.to_dict("records"),"crossmetal":xdf.to_dict("records")},indent=2))

if __name__=="__main__":
    main()
