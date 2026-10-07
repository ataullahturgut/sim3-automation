from __future__ import annotations

import importlib.util, json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
A0_PATH=AX/"tools"/"gold_session_nova_a0_core3_raw_replay_v1_20261006.py"
MA15_PATH=AX/"tools"/"gold_session_iris15_crossmetal_v2_maintaware_20261006.py"
RES1H_PATH=AX/"tools"/"gold_session_iris_resolution_matched_v2_derivedxau_20261006.py"
W22=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2022.csv"
S22=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2022.csv"
X22=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_OVERLAP.csv"
X23=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m
a0=loadmod("a0",A0_PATH)
ma15=loadmod("ma15",MA15_PATH)
res1h=loadmod("res1h",RES1H_PATH)
v15=ma15.v1
base=ma15.base

CORE3=list(a0.CORE3)
BLOCK=5
RECENT_N=252
MIN_STRUCT_TRAIN=80
SEED=20261006
CS=[0.03,0.10,0.30,1.00,3.00]
INNER_MIN=50
INNER_VAL=15

def clip_logit(p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return np.log(p/(1-p))

def load_targets_all():
    # 2022 governed warmup authority.
    z22=[]
    for p in [W22,S22]:
        z=pd.read_csv(p)
        z=z[z.final_trainable.astype(str).str.lower().eq("true")].copy()
        z22.append(z)
    t22=pd.concat(z22,ignore_index=True)
    # 2023-2024 existing V5 authority, independently raw-verified by a0.
    t34=a0.verify_v5_targets()
    t34=t34[pd.to_datetime(t34.label_date).dt.year.isin([2023,2024])].copy()
    q=pd.concat([t22,t34],ignore_index=True)
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    if q.duplicated(["label_date","partition","window"]).any():raise RuntimeError("TARGET_DUPLICATE")
    return q

def load_panel():
    metals,hashes=a0.load_raw_metals()
    targets=load_targets_all()
    panel=a0.align_daily_features(targets,metals)
    panel=panel.dropna(subset=CORE3+["direction","obs_date"]).copy()
    panel["start_utc"]=pd.to_datetime(panel.start_utc,utc=True)
    panel["end_utc"]=pd.to_datetime(panel.end_utc,utc=True)
    panel["year"]=panel.start_utc.dt.year
    panel["y_up"]=(panel.direction=="UP").astype(int)
    return panel,hashes

def load_xau15_combined():
    cols=["dt_utc","close"]
    a=pd.read_csv(X22,usecols=cols);b=pd.read_csv(X23,usecols=cols)
    q=pd.concat([a,b],ignore_index=True)
    q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
    q["value"]=pd.to_numeric(q.close,errors="raise")
    q=q[["ts","value"]].dropna().sort_values("ts")
    # Exact-overlap audit has already passed; dedup must therefore be value-consistent.
    d=q[q.duplicated("ts",keep=False)]
    if not d.empty and d.groupby("ts").value.nunique().gt(1).any():raise RuntimeError("XAU15_OVERLAP_CONFLICT")
    q=q.drop_duplicates("ts",keep="last").reset_index(drop=True)
    q=q[(q.ts>=pd.Timestamp("2021-12-30",tz="UTC"))&(q.ts<pd.Timestamp("2025-01-01",tz="UTC"))].copy()
    q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
    return q

def load_xau1h_from_15m(raw):
    q=raw.copy();q["hour"]=q.ts.dt.floor("1h");q["minute"]=q.ts.dt.minute
    rows=[]
    for hour,g in q.groupby("hour",sort=True):
        mins=tuple(sorted(set(map(int,g.minute))))
        if len(g)==4 and mins==(0,15,30,45):
            gg=g.sort_values("ts")
            rows.append({"ts":pd.Timestamp(hour),"available_at_utc":pd.Timestamp(hour)+pd.Timedelta(hours=1),
                         "value":float(gg.iloc[-1].value)})
    z=pd.DataFrame(rows)
    if z.empty:raise RuntimeError("NO_XAU1H")
    return z

def global_model(bal=False,C=1.0):
    return LogisticRegression(C=C,solver="lbfgs",max_iter=5000,random_state=SEED,
                              class_weight="balanced" if bal else None)

def fresh_a1(panel):
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.year.isin([2023,2024])].copy()
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)&(g.year.isin([2022,2023,2024]))].copy()
            if len(tr)<RECENT_N or tr.y_up.nunique()<2:continue
            Xtr=tr[CORE3].astype(float).to_numpy();Xte=te[CORE3].astype(float).to_numpy()
            sc0=StandardScaler().fit(Xtr);m0=global_model(False,1.0).fit(sc0.transform(Xtr),tr.y_up.to_numpy(int))
            p0=m0.predict_proba(sc0.transform(Xte))[:,1]
            rr=tr.tail(RECENT_N).copy()
            Xr=rr[CORE3].astype(float).to_numpy();scr=StandardScaler().fit(Xr)
            mr=global_model(True,1.0).fit(scr.transform(Xr),rr.y_up.to_numpy(int))
            pr=mr.predict_proba(scr.transform(Xte))[:,1]
            p=.75*p0+.25*pr
            for r,pp in zip(te.itertuples(index=False),p):
                rows.append({"partition":part,"window":win,"start_utc":r.start_utc,
                             "p_A1_arcr":float(pp),"a1_logit":float(clip_logit([pp])[0]),
                             "a1_train_n":len(tr),"a1_recent_n":RECENT_N})
    q=pd.DataFrame(rows)
    if q.empty:raise RuntimeError("NO_A1")
    return q

def predict_l2(tr,te,features,C=1.0,balanced=False):
    X=tr[features].astype(float).to_numpy();Xt=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=global_model(balanced,C).fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def l1_select(tr,features,C,balanced):
    X=tr[features].astype(float).to_numpy();y=tr.y_up.to_numpy(int);sc=StandardScaler().fit(X)
    m=LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,random_state=SEED,
                         class_weight="balanced" if balanced else None).fit(sc.transform(X),y)
    idx=np.flatnonzero(np.abs(m.coef_.ravel())>1e-10)
    return [features[i] for i in idx]

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

def choose_select(tr,path_features,balanced):
    candidates=["a1_logit"]+path_features;folds=inner_splits(tr)
    if len(folds)<2:return path_features,0.30,{"fallback":"INSUFFICIENT_INNER_FOLDS"}
    scores=[]
    for C in CS:
        ys=[];ps=[];ns=[]
        for it,va in folds:
            sel=l1_select(it,candidates,C,balanced)
            if "a1_logit" not in sel:sel=["a1_logit"]+sel
            p=predict_l2(it,va,sel,C=.30,balanced=balanced)
            ys.extend(va.y_up.astype(int));ps.extend(p);ns.append(len(sel))
        y=np.asarray(ys,int);p=np.asarray(ps,float);pred=(p>=.5).astype(int)
        scores.append({"C":C,"ba":float(balanced_accuracy_score(y,pred)),
                       "brier":float(np.mean((p-y)**2)),"mean_selected":float(np.mean(ns))})
    best=max(x["ba"] for x in scores);short=[x for x in scores if x["ba"]>=best-.01]
    chosen=sorted(short,key=lambda x:(x["brier"],x["mean_selected"],x["C"]))[0]
    sel=l1_select(tr,candidates,float(chosen["C"]),balanced)
    if "a1_logit" not in sel:sel=["a1_logit"]+sel
    return [x for x in sel if x!="a1_logit"],float(chosen["C"]),{"scores":scores,"chosen":chosen}

def replay_struct(common,f1h,f15):
    rows=[];events=[]
    for (part,win),g0 in common.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        for bs in range(0,len(g),BLOCK):
            te=g.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<MIN_STRUCT_TRAIN or tr.y_up.nunique()<2:continue

            for r in te.itertuples(index=False):
                rows.append({"model":"A1_DIRECT_MATCHED","partition":part,"window":win,"label_date":r.label_date,
                             "start_utc":r.start_utc.isoformat(),"end_utc":r.end_utc.isoformat(),"year":int(r.year),
                             "y_up":int(r.y_up),"p_up":float(r.p_A1_arcr),"train_n":len(tr)})

            for name,feats in [("S14_A1_PLUS_1H_FULL",["a1_logit"]+f1h),
                               ("S14_A1_PLUS_15M_FULL",["a1_logit"]+f15)]:
                p=predict_l2(tr,te,feats,C=1.0,balanced=False)
                for r,pp in zip(te.itertuples(index=False),p):
                    rows.append({"model":name,"partition":part,"window":win,"label_date":r.label_date,
                                 "start_utc":r.start_utc.isoformat(),"end_utc":r.end_utc.isoformat(),"year":int(r.year),
                                 "y_up":int(r.y_up),"p_up":float(pp),"train_n":len(tr)})

            for bal,name in [(False,"S14_A1_PLUS_15M_SELECT"),(True,"S14_A1_PLUS_15M_SELECT_BAL")]:
                path,C,detail=choose_select(tr,f15,bal)
                feats=["a1_logit"]+path
                p=predict_l2(tr,te,feats,C=.30,balanced=bal)
                events.append({"partition":part,"window":win,"cutoff":cutoff.isoformat(),"model":name,
                               "train_n":len(tr),"selected_path_n":len(path),"chosen_C":C,
                               "selected_path_features":json.dumps(path,separators=(",",":")),
                               "detail":json.dumps(detail,separators=(",",":"))})
                for r,pp in zip(te.itertuples(index=False),p):
                    rows.append({"model":name,"partition":part,"window":win,"label_date":r.label_date,
                                 "start_utc":r.start_utc.isoformat(),"end_utc":r.end_utc.isoformat(),"year":int(r.year),
                                 "y_up":int(r.y_up),"p_up":float(pp),"train_n":len(tr)})
    return pd.DataFrame(rows),pd.DataFrame(events)

def summarize(pred):
    out=[]
    for (model,part,win,yr),g in pred.groupby(["model","partition","window","year"],sort=True):
        out.append({"model":model,"partition":part,"window":win,"period":str(yr),**base.metrics(g.y_up,g.p_up)})
    for (model,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        out.append({"model":model,"partition":part,"window":win,"period":"2023-2024_SCORED",**base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(out)

def pair_table(pred):
    rows=[]
    models=["A1_DIRECT_MATCHED","S14_A1_PLUS_1H_FULL","S14_A1_PLUS_15M_FULL",
            "S14_A1_PLUS_15M_SELECT","S14_A1_PLUS_15M_SELECT_BAL"]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        piv=g.pivot(index=["label_date","start_utc","year","y_up"],columns="model",values="p_up").dropna().reset_index()
        for period,z in [("2023",piv[piv.year.eq(2023)]),("2024",piv[piv.year.eq(2024)]),("2023-2024_SCORED",piv)]:
            if z.empty:continue
            y=z.y_up.to_numpy(int);ma=base.metrics(y,z["A1_DIRECT_MATCHED"].to_numpy(float))
            for m in models:
                mm=base.metrics(y,z[m].to_numpy(float))
                rows.append({"partition":part,"window":win,"period":period,"model":m,"n":len(z),
                             "accuracy":mm["accuracy"],"balanced_accuracy":mm["balanced_accuracy"],
                             "brier":mm["brier"],"up_recall":mm["up_recall"],"down_recall":mm["down_recall"],
                             "delta_ba_vs_A1_pp":100*(mm["balanced_accuracy"]-ma["balanced_accuracy"]),
                             "delta_brier_vs_A1":mm["brier"]-ma["brier"],
                             "recall_floor30":min(mm["up_recall"],mm["down_recall"])>=.30})
    return pd.DataFrame(rows)

def main():
    panel,hashes=load_panel()
    base.audit_target_clocks(panel)
    fa1=fresh_a1(panel)
    # Only 2023-2024 rows with fresh causal A1 are downstream candidates.
    dev=panel[panel.year.isin([2023,2024])].copy()
    dev=dev.merge(fa1,on=["partition","window","start_utc"],how="inner",validate="one_to_one")
    dev=dev.reset_index(drop=True);dev["row_id"]=np.arange(len(dev))

    x15=load_xau15_combined()
    dev=ma15.attach(dev,x15,"g15");f15=v15.feature_names("g15")
    x1=load_xau1h_from_15m(x15)
    dev=res1h.attach(dev,x1,"g1h","1h");f1h=res1h.feature_names("g1h")
    common=dev.dropna(subset=["a1_logit"]+f15+f1h+["direction"]).copy()
    for p in ["g15","g1h"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():raise RuntimeError(f"{p}_LEAK")
        if common[f"{p}_max_reference_stale_min"].gt(60).any():raise RuntimeError(f"{p}_STALE")

    pred,events=replay_struct(common,f1h,f15)
    mdf=summarize(pred);pdf=pair_table(pred)

    cov=[]
    for (part,win),g in common.groupby(["partition","window"],sort=True):
        p=pred[(pred.partition==part)&(pred.window==win)&(pred.model=="S14_A1_PLUS_1H_FULL")]
        cov.append({"partition":part,"window":win,"fresh_a1_rows":len(g),"s14_scored_rows":len(p),
                    "scored_2023":int((p.year==2023).sum()),"scored_2024":int((p.year==2024).sum()),
                    "first_a1":g.start_utc.min().isoformat(),"first_s14":None if p.empty else p.start_utc.min(),
                    "last_s14":None if p.empty else p.start_utc.max()})
    cdf=pd.DataFrame(cov)

    pred.to_csv(OUT/"predictions.csv",index=False);events.to_csv(OUT/"selection_events.csv",index=False)
    mdf.to_csv(OUT/"metrics.csv",index=False);pdf.to_csv(OUT/"paired.csv",index=False);cdf.to_csv(OUT/"coverage.csv",index=False)

    summary={"status":"S1_4_STRUCTURAL_IRIS_WARMUP22_COMPLETE",
             "scope":"2022 training/warm-up; 2023-2024 scored development; 2025/2026 unopened",
             "sources":{"daily_metals":"pinned Stak raw CORE3","xau15_2022":X22.name,"xau15_2023_2024":X23.name,
                        "xau1h":"deterministically derived from same combined XAU15"},
             "training":{"A1_recent_n":RECENT_N,"structural_min_matured_A1_rows":MIN_STRUCT_TRAIN,"block":BLOCK,
                         "nested_C_grid":CS},
             "coverage":cov,"metrics":mdf.to_dict("records"),"paired":pdf.to_dict("records"),
             "guardrails":["2022 labels use governed V3/V4/V5 authority and are training-only.",
                           "Fresh A1 is regenerated from raw daily metals with 2022-2024 matured same-window history.",
                           "No archived A1 or IRIS predictions are model inputs.",
                           "Nested selection uses only prior data inside each outer block.",
                           "No target-start bar is used.","2025 and 2026 remain unopened."]}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    lines=["# S1.4 STRUCTURAL_IRIS — 2022 WARM-UP EXTENDED REPLAY","",
           "**Status:** S1_4_STRUCTURAL_IRIS_WARMUP22_COMPLETE","",
           "- 2022 = training/warm-up only.",
           "- 2023–2024 = scored development.",
           "- 2025/2026 = unopened.","",
           "## Matched results","","| Partition | Window | Period | Model | N | Acc | BA | UP | DOWN | Brier | ΔBA vs A1 |",
           "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in pdf.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {r.period} | {r.model} | {r.n} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} | {r.delta_ba_vs_A1_pp:+.2f} pp |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"coverage":cov,"paired_combined":pdf[pdf.period.eq("2023-2024_SCORED")].to_dict("records")},indent=2,default=str))

if __name__=="__main__":main()
