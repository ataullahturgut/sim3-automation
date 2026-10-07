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
M05B=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
SAGE_T=AX/"tools"/"gold_session_sage_frozen_2025_transport_v2_continuous_20261007.py"
OUT=AX/"SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_OUT"
OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

m05=loadmod("m05",M05B)
st=loadmod("sage_t",SAGE_T)
v1=st.v1
base=st.base

SAGE=list(v1.SESSION_ALL)
ALL=["a1_logit"]+SAGE
BLOCK=int(v1.BLOCK)
MIN_TRAIN=int(v1.MIN_A1)
INNER_MIN=50
INNER_VAL=15
CS=[0.03,0.10,0.30,1.00,3.00]
MIN_SAGE=2
MAX_SAGE=6
SEED=20261007

def final_lr():
    return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED)

def selector_lr(C):
    return LogisticRegression(
        C=C,penalty="l1",solver="liblinear",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def metrics(y,p):
    return base.metrics(np.asarray(y,int),np.asarray(p,float))

def fit_selected(tr,te,sage_features):
    feats=["a1_logit"]+list(sage_features)
    X=tr[feats].astype(float).to_numpy()
    Xt=te[feats].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=final_lr().fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def fit_selector(tr,C):
    X=tr[ALL].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=selector_lr(C).fit(sc.transform(X),tr.y_up.to_numpy(int))
    co=m.coef_.ravel()
    cmap={ALL[i]:float(co[i]) for i in range(len(ALL))}
    sage=[f for f in SAGE if abs(cmap[f])>1e-10]
    if len(sage)<MIN_SAGE:
        ranked=sorted(SAGE,key=lambda f:abs(cmap[f]),reverse=True)
        for f in ranked:
            if f not in sage:sage.append(f)
            if len(sage)>=MIN_SAGE:break
    return sage,cmap

def build_panel():
    panel,_=m05.load_panel_extended()
    panel=panel.reset_index(drop=True)
    panel["row_id"]=np.arange(len(panel))

    # Fresh A1 uses the same governed 2022 warmup and continuous 2023-2025 chronology.
    fa1=m05.fresh_a1_extended(panel)

    raw=st.raw()
    cyc=st.cycles(raw)
    panel=pd.merge_asof(
        panel.sort_values("start_utc"),
        cyc,
        left_on="start_utc",
        right_on="sage_ready_utc",
        direction="backward",
        allow_exact_matches=False
    )
    valid=panel.sage_ready_utc.notna()
    if not (panel.loc[valid,"sage_ready_utc"]<panel.loc[valid,"start_utc"]).all():
        raise RuntimeError("SAGE_TIME_LEAK")

    panel=panel.merge(
        fa1,on=["partition","window","start_utc"],
        how="inner",validate="one_to_one"
    )
    panel=panel.dropna(subset=ALL+["p_A1_arcr","direction"]).copy()
    panel["start_utc"]=pd.to_datetime(panel.start_utc,utc=True)
    panel["end_utc"]=pd.to_datetime(panel.end_utc,utc=True)
    panel["year"]=panel.start_utc.dt.year
    panel["y_up"]=(panel.direction=="UP").astype(int)
    return panel.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def inner_splits(tr):
    tr=tr.sort_values("start_utc").reset_index(drop=True)
    n=len(tr);out=[]
    for s in [n-45,n-30,n-15]:
        if s<INNER_MIN:continue
        va=tr.iloc[s:s+INNER_VAL].copy()
        if va.empty:continue
        cut=va.start_utc.min()
        it=tr[(tr.end_utc<=cut)&(tr.start_utc<cut)].copy()
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:continue
        out.append((it,va))
    return out

def choose_sage(tr):
    folds=inner_splits(tr)
    if len(folds)<2:
        sel,cmap=fit_selector(tr,.30)
        return sel,.30,{"fallback":"INSUFFICIENT_INNER_FOLDS","folds":len(folds)},cmap

    rows=[]
    for C in CS:
        ys=[];ps=[];ns=[];ok=True
        for it,va in folds:
            try:
                sel,_=fit_selector(it,C)
                pp=fit_selected(it,va,sel)
            except Exception:
                ok=False;break
            ys.extend(va.y_up.astype(int).tolist())
            ps.extend(map(float,pp))
            ns.append(len(sel))
        if not ok or not ys:continue
        mm=metrics(ys,ps)
        rows.append({
            "C":C,"ba":mm["balanced_accuracy"],"brier":mm["brier"],
            "mean_selected":float(np.mean(ns))
        })
    if not rows:
        sel,cmap=fit_selector(tr,.30)
        return sel,.30,{"fallback":"NO_VALID_CANDIDATE"},cmap

    best=max(r["ba"] for r in rows)
    short=[r for r in rows if r["ba"]>=best-.01]
    chosen=sorted(short,key=lambda r:(r["brier"],r["mean_selected"],r["C"]))[0]
    sel,cmap=fit_selector(tr,float(chosen["C"]))
    return sel,float(chosen["C"]),{"scores":rows,"chosen":chosen},cmap

def selection_events(panel):
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.year.isin([2023,2024])].reset_index(drop=True)
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
            sel,C,detail,cmap=choose_sage(tr)
            rows.append({
                "partition":part,"window":win,"outer_block":int(bs//BLOCK),
                "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),
                "train_n":int(len(tr)),"selector_C":C,
                "selected_sage":json.dumps(sel,separators=(",",":")),
                "coefficients":json.dumps(cmap,separators=(",",":")),
                "detail":json.dumps(detail,separators=(",",":"))
            })
    return pd.DataFrame(rows)

def freeze(events):
    out=[]
    for (part,win),e in events.groupby(["partition","window"],sort=True):
        counts=Counter();years=defaultdict(set);mag=defaultdict(list)
        for r in e.itertuples(index=False):
            fs=json.loads(r.selected_sage);cm=json.loads(r.coefficients)
            counts.update(fs)
            for f in fs:
                years[f].add(int(r.outer_year))
                mag[f].append(abs(float(cm.get(f,0.0))))
        total=max(1,len(e))
        rows=[]
        for f,n in counts.items():
            rows.append({
                "feature":f,"freq":n/total,
                "both_years":len(years[f])>=2,
                "mean_abs_coef":float(np.mean(mag[f])) if mag[f] else 0.0
            })
        q=pd.DataFrame(rows).sort_values(
            ["both_years","freq","mean_abs_coef"],
            ascending=[False,False,False]
        )
        chosen=q[q.both_years].feature.tolist()[:MAX_SAGE]
        if len(chosen)<MIN_SAGE:
            for f in q.feature.tolist():
                if f not in chosen:chosen.append(f)
                if len(chosen)>=MIN_SAGE:break
        chosen=chosen[:MAX_SAGE]
        out.append({
            "partition":part,"window":win,
            "frozen_sage_features":chosen,
            "n_sage_features":len(chosen),
            "eligible_outer_blocks":int(total)
        })
    return out

def replay(panel,frozen,years,continuous=False):
    fmap={(x["partition"],x["window"]):x["frozen_sage_features"] for x in frozen}
    rows=[]
    for (part,win),g0 in panel.groupby(["partition","window"],sort=True):
        if (part,win) not in fmap:continue
        sel=fmap[(part,win)]
        g=g0.sort_values("start_utc").reset_index(drop=True)
        teall=g[g.year.isin([2023,2024,2025] if continuous else years)].reset_index(drop=True)
        for bs in range(0,len(teall),BLOCK):
            te=teall.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue

            pp_sel=fit_selected(tr,te,sel)
            pp_full=fit_selected(tr,te,SAGE)
            for r,p_sel,p_full in zip(te.itertuples(index=False),pp_sel,pp_full):
                if int(r.year) not in years:continue
                common={
                    "partition":part,"window":win,"label_date":r.label_date,
                    "start_utc":r.start_utc,"end_utc":r.end_utc,
                    "year":int(r.year),"y_up":int(r.y_up),
                    "train_n":int(len(tr)),"block":int(bs//BLOCK)
                }
                rows.append({**common,"model":"SELECTED_A1_SESSION","p_up":float(p_sel),
                             "features":"a1_logit|"+"|".join(sel)})
                # Development reference only. In 2025 it is emitted only on a selected-eligible head.
                rows.append({**common,"model":"CANONICAL_A1_SESSION","p_up":float(p_full),
                             "features":"a1_logit|"+"|".join(SAGE)})
                rows.append({**common,"model":"DIRECT_A1","p_up":float(r.p_A1_arcr),
                             "features":"p_A1_arcr"})
    return pd.DataFrame(rows)

def paired(pred,cand="SELECTED_A1_SESSION",comp="DIRECT_A1"):
    rows=[]
    keys=["partition","window","label_date","start_utc","year","y_up"]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        a=g[g.model.eq(cand)]
        b=g[g.model.eq(comp)]
        z=a.merge(b,on=keys,suffixes=("_c","_b"),validate="one_to_one")
        for period,zz in [
            ("2023",z[z.year.eq(2023)]),
            ("2024",z[z.year.eq(2024)]),
            ("2023-2024_SCORED",z[z.year.isin([2023,2024])]),
            ("2025",z[z.year.eq(2025)])
        ]:
            if zz.empty:continue
            mc=metrics(zz.y_up,zz.p_up_c);mb=metrics(zz.y_up,zz.p_up_b)
            rows.append({
                "partition":part,"window":win,"period":period,
                "candidate":cand,"comparator":comp,"n":len(zz),
                "candidate_accuracy":mc["accuracy"],
                "candidate_ba":mc["balanced_accuracy"],
                "candidate_brier":mc["brier"],
                "candidate_up_recall":mc["up_recall"],
                "candidate_down_recall":mc["down_recall"],
                "comparator_ba":mb["balanced_accuracy"],
                "comparator_brier":mb["brier"],
                "delta_ba_pp":100*(mc["balanced_accuracy"]-mb["balanced_accuracy"]),
                "delta_brier":mc["brier"]-mb["brier"]
            })
    return pd.DataFrame(rows)

def eligibility(pdf):
    rows=[]
    for (part,win),g in pdf.groupby(["partition","window"],sort=True):
        comb=g[g.period.eq("2023-2024_SCORED")]
        if comb.empty:continue
        c=comb.iloc[0]
        y23=g[g.period.eq("2023")]
        y24=g[g.period.eq("2024")]
        year_ok=True
        if not y23.empty and not y24.empty and y23.iloc[0].n>=40 and y24.iloc[0].n>=40:
            if y23.iloc[0].candidate_ba+1e-12<y23.iloc[0].comparator_ba:year_ok=False
            if y24.iloc[0].candidate_ba+1e-12<y24.iloc[0].comparator_ba:year_ok=False
        ok=bool(
            c.n>=80
            and min(c.candidate_up_recall,c.candidate_down_recall)>=.30
            and c.candidate_ba+1e-12>=c.comparator_ba
            and c.candidate_brier<=c.comparator_brier+.010+1e-12
            and year_ok
        )
        reasons=[]
        if c.n<80:reasons.append("N_LT_80")
        if min(c.candidate_up_recall,c.candidate_down_recall)<.30:reasons.append("RECALL_FLOOR")
        if c.candidate_ba+1e-12<c.comparator_ba:reasons.append("BA_BELOW_COMPARATOR")
        if c.candidate_brier>c.comparator_brier+.010+1e-12:reasons.append("BRIER_GATE")
        if not year_ok:reasons.append("YEAR_SIGN_FAIL")
        rows.append({
            "partition":part,"window":win,"n":int(c.n),
            "candidate_ba":float(c.candidate_ba),
            "candidate_up_recall":float(c.candidate_up_recall),
            "candidate_down_recall":float(c.candidate_down_recall),
            "comparator_ba":float(c.comparator_ba),
            "candidate_brier":float(c.candidate_brier),
            "comparator_brier":float(c.comparator_brier),
            "eligible":ok,"reason":"PASS" if ok else "|".join(reasons)
        })
    return pd.DataFrame(rows)

def summary_metrics(pred,period):
    rows=[]
    for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
        rows.append({"period":period,"model":m,"partition":part,"window":win,**metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def main():
    panel=build_panel()
    events=selection_events(panel)
    frozen=freeze(events)

    dev=replay(panel,frozen,[2023,2024],continuous=False)
    dev_pairs=paired(dev)
    gate=eligibility(dev_pairs)

    eligible={(r.partition,r.window) for r in gate.itertuples(index=False) if bool(r.eligible)}
    fz=[x for x in frozen if (x["partition"],x["window"]) in eligible]

    if fz:
        tr=replay(panel,fz,[2025],continuous=True)
        tr_pairs=paired(tr)
    else:
        tr=pd.DataFrame(columns=dev.columns)
        tr_pairs=pd.DataFrame(columns=dev_pairs.columns)

    events.to_csv(OUT/"selection_events.csv",index=False)
    pd.DataFrame(frozen).to_json(OUT/"frozen_features.json",orient="records",indent=2)
    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    summary_metrics(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    dev_pairs.to_csv(OUT/"dev_paired.csv",index=False)
    gate.to_csv(OUT/"eligibility.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:
        summary_metrics(tr,"FROZEN_SPEC_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:
        pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)
    tr_pairs.to_csv(OUT/"transport_2025_paired.csv",index=False)

    summary={
        "status":"SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_COMPLETE",
        "baseline":"S17_A1_SESSION",
        "challenger":"SELECTED_A1_SESSION",
        "comparator":"DIRECT_A1 = fresh p_A1_arcr, no downstream refit",
        "mandatory_feature":"a1_logit",
        "selectable_features":SAGE,
        "clock_policy":"fresh causal A1 + canonical SAGE strict sage_ready_utc < target_start",
        "chronology":"2022 warm-up; 2023-2024 selection/gate; 2025 only pre-eligible heads; 2026 unopened",
        "frozen_features":frozen,
        "eligibility":gate.to_dict("records"),
        "transport_2025_paired":tr_pairs.to_dict("records"),
        "guardrails":[
            "a1_logit is mandatory in every selected model.",
            "At least two SAGE variables retained.",
            "No PATH, 15m, cross-metal, macro, GVZ, COT or downstream model state added.",
            "Comparator is direct fresh A1 probability.",
            "No 2025 feature reselection, threshold tuning, C tuning or eligibility rescue.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION MODEL-08B — SAGE A1_SESSION FEATURE-SELECTION RESULT","",
        "**Status:** complete.","",
        "## Frozen SAGE variables","",
        "| Partition | Window | SAGE variables |","|---|---|---|"
    ]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_sage_features'])} |")
    lines += ["","## Pre-2025 eligibility","",
              "| Partition | Window | N | Candidate BA | Direct A1 BA | UP | DOWN | Eligible | Reason |",
              "|---|---|---:|---:|---:|---:|---:|---|---|"]
    for r in gate.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.candidate_ba:.2f}% | "
                     f"{100*r.comparator_ba:.2f}% | {100*r.candidate_up_recall:.2f}% | "
                     f"{100*r.candidate_down_recall:.2f}% | {r.eligible} | {r.reason} |")
    lines += ["","## 2025 transport",""]
    if tr_pairs.empty:
        lines.append("No selected A1_SESSION head passed the pre-2025 paired gate; 2025 remained closed.")
    else:
        lines += ["| Partition | Window | N | Candidate BA | Direct A1 BA | Delta BA | Candidate Brier | Direct A1 Brier |",
                  "|---|---|---:|---:|---:|---:|---:|---:|"]
        for r in tr_pairs[tr_pairs.period.eq("2025")].itertuples(index=False):
            lines.append(f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.candidate_ba:.2f}% | "
                         f"{100*r.comparator_ba:.2f}% | {r.delta_ba_pp:+.2f} pp | "
                         f"{r.candidate_brier:.4f} | {r.comparator_brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")

    print(json.dumps({
        "status":summary["status"],
        "eligibility":summary["eligibility"],
        "transport_2025_paired":summary["transport_2025_paired"]
    },indent=2,default=str))

if __name__=="__main__":
    main()
