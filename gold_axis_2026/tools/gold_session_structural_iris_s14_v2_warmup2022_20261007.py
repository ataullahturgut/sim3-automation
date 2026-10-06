from __future__ import annotations

import importlib.util,json
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
WARM_TGT=AX/"GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
WARM_RAW=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
WARM_SUM=AX/"GOLD_SESSION_2022_WARMUP_V5_SUMMARY_2026-10-07.json"
EXIST_RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
BLUEPRINT=AX/"GOLD_SESSION_IRIS15_VARIABLE_SELECTION_DEV_BLUEPRINT_2026-10-06.json"
OUT=AX/"SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

a1=loadmod("a1",A1_PATH)
ma15=loadmod("ma15",MA15_PATH)
res1h=loadmod("res1h",RES1H_PATH)
v15=ma15.v1;base=ma15.base

BLOCK=5;MIN_STRUCT_TRAIN=80
INNER_MIN=50;INNER_VAL=15
CS=[0.03,0.10,0.30,1.00,3.00]
SEED=20261007

def clip_logit(p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6);return np.log(p/(1-p))

def combined_raw15():
    a=pd.read_csv(WARM_RAW);b=pd.read_csv(EXIST_RAW)
    for q in [a,b]:
        q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True)
        q["close"]=pd.to_numeric(q.close,errors="raise")
    b=b[b.dt_utc<pd.Timestamp("2025-01-01",tz="UTC")].copy()
    q=pd.concat([a[["dt_utc","close"]],b[["dt_utc","close"]]],ignore_index=True)
    q=q.sort_values("dt_utc").drop_duplicates("dt_utc",keep="last")
    q=q[(q.dt_utc>=pd.Timestamp("2022-01-01",tz="UTC"))&(q.dt_utc<pd.Timestamp("2025-01-01",tz="UTC"))].copy()
    q=q.rename(columns={"dt_utc":"ts","close":"value"})
    q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
    return q[["ts","available_at_utc","value"]].reset_index(drop=True)

def xau1h_from_15m(raw):
    q=raw.copy();q["hour"]=q.ts.dt.floor("1h");q["minute"]=q.ts.dt.minute
    rows=[]
    for h,g in q.groupby("hour",sort=True):
        mins=tuple(sorted(set(map(int,g.minute))))
        if len(g)==4 and mins==(0,15,30,45):
            rows.append({"ts":pd.Timestamp(h),"available_at_utc":pd.Timestamp(h)+pd.Timedelta(hours=1),
                         "value":float(g.sort_values("ts").iloc[-1].value)})
    return pd.DataFrame(rows).sort_values("ts").reset_index(drop=True)

def build_panel():
    warm=pd.read_csv(WARM_TGT)
    warm=warm[warm.final_trainable.astype(str).str.lower().eq("true")].copy()
    core=base.base.verify_v5_targets()
    core=core[pd.to_datetime(core.label_date).dt.year.isin([2023,2024])].copy()
    targets=pd.concat([warm,core],ignore_index=True,sort=False)
    targets["start_utc"]=pd.to_datetime(targets.start_utc,utc=True)
    targets["end_utc"]=pd.to_datetime(targets.end_utc,utc=True)

    metals,hashes=base.base.load_raw_metals()
    panel=base.base.align_daily_features(targets,metals)
    panel=panel.dropna(subset=base.CORE3+["direction","obs_date"]).copy()
    return panel,hashes

def fresh_a1_with_warmup(panel):
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.start_utc.dt.year.isin([2023,2024])].copy().reset_index(drop=True)
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<a1.RECENT_N:continue
            mg=a1.global_model();mg.fit(tr[a1.CORE3].astype(float),tr.y_up.to_numpy(int))
            p0=mg.predict_proba(te[a1.CORE3].astype(float))[:,1]
            rr=tr.tail(a1.RECENT_N)
            mr=a1.recent_model();mr.fit(rr[a1.CORE3].astype(float),rr.y_up.to_numpy(int))
            pr=mr.predict_proba(te[a1.CORE3].astype(float))[:,1]
            p=.75*p0+.25*pr
            for r,pa,p00,prr in zip(te.itertuples(index=False),p,p0,pr):
                rows.append({"partition":part,"window":win,"start_utc":r.start_utc,
                             "p_A1_arcr":float(pa),"p_A0_global":float(p00),"p_recent252":float(prr),
                             "a1_logit":float(clip_logit([pa])[0]),"a1_train_n":len(tr)})
    return pd.DataFrame(rows)

def model_predict(tr,te,features,C=1.0,balanced=False):
    Xtr=tr[features].astype(float).to_numpy();Xte=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(Xtr)
    m=LogisticRegression(C=C,solver="lbfgs",max_iter=5000,random_state=SEED,
                         class_weight="balanced" if balanced else None)
    m.fit(sc.transform(Xtr),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xte))[:,1]

def l1_select(tr,features,C,balanced):
    X=tr[features].astype(float).to_numpy();y=tr.y_up.to_numpy(int)
    sc=StandardScaler().fit(X)
    m=LogisticRegression(C=C,penalty="l1",solver="liblinear",max_iter=5000,random_state=SEED,
                         class_weight="balanced" if balanced else None)
    m.fit(sc.transform(X),y)
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
        if len(it)>=INNER_MIN and it.y_up.nunique()==2 and va.y_up.nunique()==2:out.append((it,va))
    return out

def choose_path(tr,path_features,balanced):
    candidates=["a1_logit"]+path_features;folds=inner_splits(tr)
    if len(folds)<2:return path_features,None,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)}
    scores=[]
    for C in CS:
        ys=[];ps=[];ns=[]
        for it,va in folds:
            sel=l1_select(it,candidates,C,balanced)
            if "a1_logit" not in sel:sel=["a1_logit"]+sel
            p=model_predict(it,va,sel,C=.30,balanced=balanced)
            ys+=va.y_up.astype(int).tolist();ps+=list(map(float,p));ns.append(len(sel))
        y=np.asarray(ys,int);p=np.asarray(ps,float);pred=(p>=.5).astype(int)
        scores.append({"C":C,"ba":float(balanced_accuracy_score(y,pred)),
                       "brier":float(np.mean((p-y)**2)),"mean_selected":float(np.mean(ns))})
    best=max(z["ba"] for z in scores);short=[z for z in scores if z["ba"]>=best-.01]
    ch=sorted(short,key=lambda z:(z["brier"],z["mean_selected"],z["C"]))[0]
    sel=l1_select(tr,candidates,float(ch["C"]),balanced)
    if "a1_logit" not in sel:sel=["a1_logit"]+sel
    return [x for x in sel if x!="a1_logit"],float(ch["C"]),{"candidates":scores,"chosen":ch}

def main():
    ws=json.loads(WARM_SUM.read_text())
    if ws.get("status")!="2022_V5_EQUIVALENT_WARMUP_GATE_PASS":raise RuntimeError("WARMUP_GATE_NOT_PASS")
    ov=ws["twelve"]["overlap_with_governed_archive"]
    if any(ov[f"{c}_mismatch_n"] for c in ["open","high","low","close"]):raise RuntimeError("WARMUP_OVERLAP_MISMATCH")

    panel,metal_hashes=build_panel()
    fa1=fresh_a1_with_warmup(panel)
    panel=panel.merge(fa1,on=["partition","window","start_utc"],how="left",validate="one_to_one")

    raw15=combined_raw15()
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))
    panel=ma15.attach(panel,raw15,"g15");f15=v15.feature_names("g15")
    raw1h=xau1h_from_15m(raw15)
    panel=res1h.attach(panel,raw1h,"g1h","1h");f1h=res1h.feature_names("g1h")

    common=panel[(panel.start_utc.dt.year.isin([2023,2024]))].dropna(subset=["a1_logit"]+f15+f1h+["direction"]).copy()
    for p in ["g15","g1h"]:
        if not (common[f"{p}_anchor_available"]<common.start_utc).all():raise RuntimeError(f"{p}_LEAK")
        if common[f"{p}_max_reference_stale_min"].gt(60).any():raise RuntimeError(f"{p}_STALE")

    bp=json.loads(BLUEPRINT.read_text());mode={}
    for h in bp["heads"]:
        ch=h["choice"];mode[(h["partition"],h["window"])]="SELECT_BAL" if ch=="SELECT_XAU15_BAL" else ("SELECT" if ch=="SELECT_XAU15" else "FULL")

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
                             "start_utc":r.start_utc,"end_utc":r.end_utc,"year":r.start_utc.year,
                             "y_up":int(r.y_up),"p_up":float(r.p_A1_arcr),"train_n":len(tr),"a1_train_n":int(r.a1_train_n)})

            p1=model_predict(tr,te,["a1_logit"]+f1h,C=1.0)
            p15=model_predict(tr,te,["a1_logit"]+f15,C=1.0)
            for name,pp in [("S14_A1_PLUS_1H_FULL",p1),("S14_A1_PLUS_15M_FULL",p15)]:
                for r,p in zip(te.itertuples(index=False),pp):
                    rows.append({"model":name,"partition":part,"window":win,"label_date":r.label_date,
                                 "start_utc":r.start_utc,"end_utc":r.end_utc,"year":r.start_utc.year,
                                 "y_up":int(r.y_up),"p_up":float(p),"train_n":len(tr),"a1_train_n":int(r.a1_train_n)})

            md=mode.get((part,win),"FULL")
            if md=="FULL":
                sel=f15;C=None;detail={"mode":"FULL_FROZEN"}
                pp=p15
            else:
                bal=md=="SELECT_BAL";sel,C,detail=choose_path(tr,f15,bal)
                pp=model_predict(tr,te,["a1_logit"]+sel,C=.30,balanced=bal)
            events.append({"partition":part,"window":win,"cutoff":cutoff,"mode":md,"train_n":len(tr),
                           "test_n":len(te),"chosen_C":C,"selected_path_n":len(sel),
                           "selected_path_features":json.dumps(sel,separators=(",",":")),
                           "detail":json.dumps(detail,separators=(",",":"))})
            for r,p in zip(te.itertuples(index=False),pp):
                rows.append({"model":"S14_A1_PLUS_15M_BLUEPRINT","partition":part,"window":win,"label_date":r.label_date,
                             "start_utc":r.start_utc,"end_utc":r.end_utc,"year":r.start_utc.year,
                             "y_up":int(r.y_up),"p_up":float(p),"train_n":len(tr),"a1_train_n":int(r.a1_train_n)})

    pred=pd.DataFrame(rows);ev=pd.DataFrame(events)
    if pred.empty:raise RuntimeError("NO_PREDICTIONS")

    mrows=[]
    for (model,part,win,yr),g in pred.groupby(["model","partition","window","year"],sort=True):
        mrows.append({"model":model,"partition":part,"window":win,"period":str(yr),**base.metrics(g.y_up,g.p_up)})
    for (model,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        mrows.append({"model":model,"partition":part,"window":win,"period":"2023-2024_SCORED",**base.metrics(g.y_up,g.p_up)})
    mdf=pd.DataFrame(mrows)

    paired=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        piv=g.pivot(index=["label_date","start_utc","year","y_up"],columns="model",values="p_up").dropna().reset_index()
        for period,pg in [("2023",piv[piv.year==2023]),("2024",piv[piv.year==2024]),("2023-2024_SCORED",piv)]:
            if pg.empty:continue
            y=pg.y_up.to_numpy(int);mets={}
            for model in ["A1_DIRECT_MATCHED","S14_A1_PLUS_1H_FULL","S14_A1_PLUS_15M_FULL","S14_A1_PLUS_15M_BLUEPRINT"]:
                mets[model]=base.metrics(y,pg[model].to_numpy(float))
            for model,mm in mets.items():
                paired.append({"partition":part,"window":win,"period":period,"model":model,"n":len(pg),
                               "accuracy":mm["accuracy"],"balanced_accuracy":mm["balanced_accuracy"],
                               "brier":mm["brier"],"up_recall":mm["up_recall"],"down_recall":mm["down_recall"],
                               "delta_ba_vs_A1_pp":100*(mm["balanced_accuracy"]-mets["A1_DIRECT_MATCHED"]["balanced_accuracy"]),
                               "delta_brier_vs_A1":mm["brier"]-mets["A1_DIRECT_MATCHED"]["brier"],
                               "eligible_n80":bool(len(pg)>=80),
                               "recall_floor30":bool(min(mm["up_recall"],mm["down_recall"])>=.30)})
    pdf=pd.DataFrame(paired)

    cov=[]
    for (part,win),g in common.groupby(["partition","window"],sort=True):
        s=pred[(pred.partition==part)&(pred.window==win)&(pred.model=="S14_A1_PLUS_1H_FULL")]
        cov.append({"partition":part,"window":win,"fresh_a1_feature_rows":len(g),"s14_scored_rows":len(s),
                    "scored_2023":int((s.year==2023).sum()),"scored_2024":int((s.year==2024).sum()),
                    "first_a1_start":g.start_utc.min(),"first_scored":None if s.empty else s.start_utc.min(),
                    "last_scored":None if s.empty else s.start_utc.max(),"blueprint_mode":mode.get((part,win),"FULL")})
    cdf=pd.DataFrame(cov)

    pred.to_csv(OUT/"predictions.csv",index=False);mdf.to_csv(OUT/"metrics.csv",index=False)
    pdf.to_csv(OUT/"paired.csv",index=False);ev.to_csv(OUT/"selection_events.csv",index=False);cdf.to_csv(OUT/"coverage.csv",index=False)

    summary={"status":"S1_4_STRUCTURAL_IRIS_WARMUP2022_COMPLETE",
      "scope":"2022 warmup/training only; 2023-2024 scored; 2025/2026 unopened",
      "warmup_authority":{"summary":WARM_SUM.name,"raw":WARM_RAW.name,"targets":WARM_TGT.name,
                          "overlap_OHLC_mismatches":0,"final_trainable_2022":int(sum(x["final_trainable"] for x in ws["coverage"]))},
      "identity":{"canonical":"fresh NOVA A1 logit + same-source-derived 1h XAU full IRIS PATH",
                  "challenger_15m":"fresh NOVA A1 logit + XAU15 full IRIS",
                  "challenger_blueprint":"fresh NOVA A1 logit + XAU15 path with frozen per-window selection mode"},
      "training":{"A1_recent_n":a1.RECENT_N,"structural_min_matured_A1_feature_rows":MIN_STRUCT_TRAIN,"block":BLOCK},
      "coverage":cov,"paired":pdf.to_dict("records"),
      "guardrails":["2022 is warmup only and never reported as evaluation.","Fresh A1 regenerated from raw daily metals; no archived predictions read.",
                    "2023-2024 V5 targets remain the existing frozen authority.","A1 logit mandatory in all Structural-IRIS models.",
                    "No target-start bar is consumed.","2025/2026 unopened."]}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# S1.4 STRUCTURAL_IRIS V2 — 2022 WARMUP / 2023-2024 SCORE","",
      "**Status:** S1_4_STRUCTURAL_IRIS_WARMUP2022_COMPLETE","",
      "- 2022: warm-up/training only.","- 2023–2024: scoring.","- 2025/2026: unopened.","",
      "## Paired combined metrics","",
      "| Partition | Window | Model | N | Acc | BA | UP | DOWN | Brier | ΔBA vs A1 |",
      "|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in pdf[pdf.period=="2023-2024_SCORED"].itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {r.model} | {r.n} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} | {r.delta_ba_vs_A1_pp:+.2f} pp |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"coverage":cov,"combined":pdf[pdf.period=="2023-2024_SCORED"].to_dict("records")},indent=2,default=str))

if __name__=="__main__":main()
