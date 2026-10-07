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
S14P=AX/"tools"/"gold_session_structural_iris_s14_v2_warmup22_20261007.py"
OUT=AX/"SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

s14=loadmod("s14",S14P)
BLOCK=5
RECENT_N=252
MIN_STRUCT=80
INNER_MIN=50
INNER_VAL=15
CS=[0.03,0.10,0.30,1.00,3.00]
MIN_FREEZE=3
MAX_FREEZE=8
SEED=20261007

def final_lr():
    return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED)

def selector_lr(C):
    return LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,
                              class_weight="balanced",random_state=SEED)

def clip_logit(p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return np.log(p/(1-p))

def load_targets_extended():
    warm=[]
    for p in [s14.W22,s14.S22]:
        z=pd.read_csv(p)
        z=z[z.final_trainable.astype(str).str.lower().eq("true")].copy()
        warm.append(z)
    t22=pd.concat(warm,ignore_index=True)
    t35=s14.a0.verify_v5_targets()
    t35=t35[pd.to_datetime(t35.label_date).dt.year.isin([2023,2024,2025])].copy()
    q=pd.concat([t22,t35],ignore_index=True,sort=False)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["year"]=q.start_utc.dt.year
    q["y_up"]=(q.direction=="UP").astype(int)
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def load_panel_extended():
    old=s14.a0.YEARS
    s14.a0.YEARS=range(2010,2026)
    try:
        metals,hashes=s14.a0.load_raw_metals()
    finally:
        s14.a0.YEARS=old
    q=s14.a0.align_daily_features(load_targets_extended(),metals)
    q=q.dropna(subset=s14.CORE3+["direction","obs_date"]).copy()
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["year"]=q.start_utc.dt.year
    q["y_up"]=(q.direction=="UP").astype(int)
    return q,hashes

def load_xau15_extended():
    a=pd.read_csv(s14.X22,usecols=["dt_utc","close"])
    b=pd.read_csv(s14.X23,usecols=["dt_utc","close"])
    for q in [a,b]:
        q["ts"]=pd.to_datetime(q.pop("dt_utc"),utc=True,errors="raise")
        q["value"]=pd.to_numeric(q.pop("close"),errors="raise")
    q=pd.concat([a,b],ignore_index=True).dropna().sort_values("ts")
    d=q[q.duplicated("ts",keep=False)]
    if not d.empty and d.groupby("ts").value.nunique().gt(1).any():
        raise RuntimeError("XAU15_OVERLAP_CONFLICT")
    q=q.drop_duplicates("ts",keep="last").reset_index(drop=True)
    q=q[(q.ts>=pd.Timestamp("2021-12-30",tz="UTC"))&
        (q.ts<pd.Timestamp("2026-01-01",tz="UTC"))].copy()
    q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
    return q

def load_xau1h(raw):
    q=raw.copy();q["hour"]=q.ts.dt.floor("1h");q["minute"]=q.ts.dt.minute
    rows=[]
    for hour,g in q.groupby("hour",sort=True):
        mins=tuple(sorted(set(map(int,g.minute))))
        if len(g)==4 and mins==(0,15,30,45):
            gg=g.sort_values("ts")
            rows.append({"ts":pd.Timestamp(hour),
                         "available_at_utc":pd.Timestamp(hour)+pd.Timedelta(hours=1),
                         "value":float(gg.iloc[-1].value)})
    z=pd.DataFrame(rows)
    if z.empty:raise RuntimeError("NO_XAU1H")
    return z

def fresh_a1_extended(panel):
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.year.isin([2023,2024,2025])].copy()
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)&
                 (g.year.isin([2022,2023,2024,2025]))].copy()
            if len(tr)<RECENT_N or tr.y_up.nunique()<2:continue
            X=tr[s14.CORE3].astype(float).to_numpy()
            Xt=te[s14.CORE3].astype(float).to_numpy()
            sc=StandardScaler().fit(X)
            mg=LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED)
            mg.fit(sc.transform(X),tr.y_up.to_numpy(int))
            pg=mg.predict_proba(sc.transform(Xt))[:,1]

            rr=tr.tail(RECENT_N).copy()
            Xr=rr[s14.CORE3].astype(float).to_numpy()
            scr=StandardScaler().fit(Xr)
            mr=LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED,
                                  class_weight="balanced")
            mr.fit(scr.transform(Xr),rr.y_up.to_numpy(int))
            pr=mr.predict_proba(scr.transform(Xt))[:,1]
            pa=.75*pg+.25*pr
            for r,p in zip(te.itertuples(index=False),pa):
                rows.append({"partition":part,"window":win,"start_utc":r.start_utc,
                             "p_A1_arcr":float(p),"a1_logit":float(clip_logit([p])[0]),
                             "a1_train_n":int(len(tr))})
    q=pd.DataFrame(rows)
    if q.empty:raise RuntimeError("NO_A1")
    return q

def build_common():
    panel,hashes=load_panel_extended()
    s14.base.audit_target_clocks(panel)
    fa1=fresh_a1_extended(panel)
    dev=panel[panel.year.isin([2023,2024,2025])].copy()
    dev=dev.merge(fa1,on=["partition","window","start_utc"],how="inner",validate="one_to_one")
    dev=dev.reset_index(drop=True);dev["row_id"]=np.arange(len(dev))

    x15=load_xau15_extended()
    x1=load_xau1h(x15)
    dev=s14.res1h.attach(dev,x1,"g1h","1h")
    f1h=list(s14.res1h.feature_names("g1h"))
    common=dev.dropna(subset=["a1_logit"]+f1h+["direction"]).copy()
    if not (common["g1h_anchor_available"]<common.start_utc).all():
        raise RuntimeError("G1H_LEAK")
    if common["g1h_max_reference_stale_min"].gt(60).any():
        raise RuntimeError("G1H_STALE")
    return common.sort_values(["partition","window","start_utc"]).reset_index(drop=True),f1h,hashes

def fit_l2(tr,te,path_features):
    feats=["a1_logit"]+list(path_features)
    X=tr[feats].astype(float).to_numpy();Xt=te[feats].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=final_lr().fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def l1_path_select(tr,path_features,C):
    feats=["a1_logit"]+list(path_features)
    X=tr[feats].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=selector_lr(C).fit(sc.transform(X),tr.y_up.to_numpy(int))
    coef=m.coef_.ravel()
    selected=[]
    cmap={}
    for i,f in enumerate(feats):
        if f=="a1_logit":
            continue
        if abs(coef[i])>1e-10:
            selected.append(f);cmap[f]=float(coef[i])
    return selected,cmap

def inner_splits(tr):
    n=len(tr);out=[]
    for s in [n-45,n-30,n-15]:
        if s<INNER_MIN:continue
        va=tr.iloc[s:s+INNER_VAL].copy()
        if va.empty:continue
        cutoff=va.start_utc.min()
        it=tr[(tr.end_utc<=cutoff)&(tr.start_utc<cutoff)].copy()
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:continue
        out.append((it,va))
    return out

def choose_path(tr,path_features):
    folds=inner_splits(tr)
    if len(folds)<2:
        sel,co=l1_path_select(tr,path_features,.30)
        return (sel or path_features[:3]),.30,{"fallback":"INSUFFICIENT_INNER_FOLDS"},co

    rows=[]
    for C in CS:
        ys=[];ps=[];ns=[];ok=True
        for it,va in folds:
            try:
                sel,_=l1_path_select(it,path_features,C)
                if not sel:sel=path_features[:3]
                pp=fit_l2(it,va,sel)
            except Exception:
                ok=False;break
            ys.extend(va.y_up.astype(int).tolist());ps.extend(map(float,pp));ns.append(len(sel))
        if not ok or not ys:continue
        mm=s14.base.metrics(ys,ps)
        rows.append({"C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
                     "mean_selected":float(np.mean(ns))})
    if not rows:
        sel,co=l1_path_select(tr,path_features,.30)
        return (sel or path_features[:3]),.30,{"fallback":"NO_VALID_CANDIDATE"},co

    best=max(x["ba"] for x in rows)
    short=[x for x in rows if x["ba"]>=best-.01]
    chosen=sorted(short,key=lambda x:(x["brier"],x["mean_selected"],x["C"]))[0]
    sel,co=l1_path_select(tr,path_features,float(chosen["C"]))
    if not sel:sel=path_features[:3]
    return sel,float(chosen["C"]),{"scores":rows,"chosen":chosen},co

def development_selection(common,path_features):
    preds=[];events=[]
    for (part,win),g0 in common.groupby(["partition","window"],sort=True):
        g=g0[g0.year.isin([2023,2024])].sort_values("start_utc").reset_index(drop=True)
        for bs in range(0,len(g),BLOCK):
            te=g.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<MIN_STRUCT or tr.y_up.nunique()<2:continue

            sel,C,detail,co=choose_path(tr,path_features)
            for model,feats in [
                ("S14_A1_PLUS_1H_FULL",path_features),
                ("S14_A1_PLUS_1H_SELECTED_BLOCK",sel),
            ]:
                pp=fit_l2(tr,te,feats)
                for r,p in zip(te.itertuples(index=False),pp):
                    preds.append({"model":model,"partition":part,"window":win,
                                  "label_date":r.label_date,"start_utc":r.start_utc,
                                  "end_utc":r.end_utc,"year":int(r.year),"y_up":int(r.y_up),
                                  "p_up":float(p),"train_n":int(len(tr)),
                                  "outer_block":int(bs//BLOCK),"features":"|".join(feats)})
            events.append({"partition":part,"window":win,"outer_block":int(bs//BLOCK),
                           "outer_year":int(te.year.iloc[0]),"cutoff":str(cutoff),
                           "train_n":int(len(tr)),"selector_C":C,
                           "selected_path_features":json.dumps(sel,separators=(",",":")),
                           "selected_coefficients":json.dumps(co,separators=(",",":")),
                           "detail":json.dumps(detail,separators=(",",":"))})
    return pd.DataFrame(preds),pd.DataFrame(events)

def freeze_paths(events):
    out=[]
    for (part,win),e in events.groupby(["partition","window"],sort=True):
        counts=Counter();years=defaultdict(set);absco=defaultdict(list)
        for r in e.itertuples(index=False):
            fs=json.loads(r.selected_path_features);co=json.loads(r.selected_coefficients)
            counts.update(fs)
            for f in fs:years[f].add(int(r.outer_year))
            for f,v in co.items():absco[f].append(abs(float(v)))
        total=max(1,len(e));rows=[]
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
        out.append({"partition":part,"window":win,"frozen_path_features":feats,
                    "n_path_features":len(feats),"eligible_outer_blocks":int(total)})
    return out

def transport_2025(common,path_features,frozen):
    fmap={(x["partition"],x["window"]):x["frozen_path_features"] for x in frozen}
    rows=[]
    for (part,win),g0 in common.groupby(["partition","window"],sort=True):
        if (part,win) not in fmap:continue
        sel=fmap[(part,win)]
        g=g0[g0.year.isin([2023,2024,2025])].sort_values("start_utc").reset_index(drop=True)
        for bs in range(0,len(g),BLOCK):
            te=g.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<MIN_STRUCT or tr.y_up.nunique()<2:continue
            for model,feats in [
                ("S14_A1_PLUS_1H_FULL",path_features),
                ("S14_A1_PLUS_1H_SELECTED",sel),
            ]:
                pp=fit_l2(tr,te,feats)
                for r,p in zip(te.itertuples(index=False),pp):
                    if int(r.year)!=2025:continue
                    rows.append({"model":model,"partition":part,"window":win,
                                 "label_date":r.label_date,"start_utc":r.start_utc,
                                 "end_utc":r.end_utc,"year":2025,"y_up":int(r.y_up),
                                 "p_up":float(p),"train_n":int(len(tr)),
                                 "continuous_block":int(bs//BLOCK),"features":"|".join(feats)})
    return pd.DataFrame(rows)

def summarize(pred,period):
    rows=[]
    for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        rows.append({"period":period,"model":m,"partition":part,"window":win,
                     **s14.base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def main():
    common,path_features,hashes=build_common()

    dev_pred,events=development_selection(common,path_features)
    dev_metrics=summarize(dev_pred,"DEV_2023_2024_COMMON_ROWS")
    frozen=freeze_paths(events)

    tr_pred=transport_2025(common,path_features,frozen)
    tr_metrics=summarize(tr_pred,"FROZEN_SPEC_2025")

    OUT.mkdir(exist_ok=True)
    dev_pred.to_csv(OUT/"dev_predictions.csv",index=False)
    events.to_csv(OUT/"selection_events.csv",index=False)
    dev_metrics.to_csv(OUT/"dev_metrics.csv",index=False)
    tr_pred.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    tr_metrics.to_csv(OUT/"transport_2025_metrics.csv",index=False)
    (OUT/"frozen_features.json").write_text(json.dumps(frozen,indent=2)+"\n")

    summary={
        "status":"SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_COMPLETE",
        "baseline":"S14_A1_PLUS_1H_FULL",
        "challenger":"S14_A1_PLUS_1H_SELECTED",
        "mandatory_feature":"a1_logit",
        "selectable_path_features":path_features,
        "final_estimator":{"scale":"StandardScaler","model":"LogisticRegression",
                           "penalty":"L2","C":1.0,"threshold":0.5},
        "chronology":"2022 upstream warm-up; 2023-2024 development/selection; 2025 frozen transport; 2026 unopened",
        "frozen_features":frozen,
        "development_metrics":dev_metrics.to_dict("records"),
        "transport_2025_metrics":tr_metrics.to_dict("records"),
        "guardrails":[
            "a1_logit is mandatory in every challenger fit.",
            "Only canonical 1h PATH features are selectable.",
            "No 15m or cross-metal variables added.",
            "Final Logistic L2 C=1.0 and threshold 0.50 unchanged.",
            "Exact common rows used for baseline/challenger comparison.",
            "No 2025 feature selection or tuning.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION MODEL-05B — STRUCTURAL_IRIS 1H FEATURE-SELECTION CHALLENGER","",
           "**Status:** complete.","",
           "A1 structural logit is mandatory; only the canonical 1h PATH block is reduced.","",
           "## Frozen path variables","",
           "| Partition | Window | Frozen path features |","|---|---|---|"]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_path_features'])} |")
    lines += ["","## 2025 exact common-row transport","",
              "| Model | Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in tr_metrics.sort_values(["partition","window","model"]).itertuples(index=False):
        lines.append(f"| {r.model} | {r.partition} | {r.window} | {int(r.n)} | "
                     f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                     f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({"status":summary["status"],"frozen":frozen,
                      "transport":tr_metrics.to_dict("records")},indent=2,default=str))

if __name__=="__main__":
    main()
