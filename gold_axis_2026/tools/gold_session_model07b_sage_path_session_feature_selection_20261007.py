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
TRANSPORT=AX/"tools"/"gold_session_sage_frozen_2025_transport_v2_continuous_20261007.py"
OUT=AX/"SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_OUT"
OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

t=loadmod("sage_transport",TRANSPORT)
v1=t.v1
base=t.base
PATH=list(t.res1h.feature_names("g1h"))
SAGE=list(v1.SESSION_ALL)
ALL=PATH+SAGE

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
    return LogisticRegression(
        C=C,penalty="l1",solver="liblinear",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def fit_l2(tr,te,features):
    X=tr[features].astype(float).to_numpy()
    Xt=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=final_lr().fit(sc.transform(X),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xt))[:,1]

def fit_selector(tr,C):
    X=tr[ALL].astype(float).to_numpy()
    sc=StandardScaler().fit(X)
    m=selector_lr(C).fit(sc.transform(X),tr.y_up.to_numpy(int))
    co=m.coef_.ravel()
    cmap={ALL[i]:float(co[i]) for i in range(len(ALL))}
    sel=[f for f,v in cmap.items() if abs(v)>1e-10]
    # Preserve true PATH+SESSION identity.
    if not any(f in PATH for f in sel):
        sel.append(max(PATH,key=lambda f:abs(cmap[f])))
    if not any(f in SAGE for f in sel):
        sel.append(max(SAGE,key=lambda f:abs(cmap[f])))
    sel=list(dict.fromkeys(sel))
    return sel,cmap

def metrics(y,p):
    return base.metrics(np.asarray(y,int),np.asarray(p,float))

def build_panel():
    r=t.raw()
    p=t.targets().reset_index(drop=True)
    p["row_id"]=np.arange(len(p))
    c=t.cycles(r)
    p=pd.merge_asof(
        p.sort_values("start_utc"),c,
        left_on="start_utc",right_on="sage_ready_utc",
        direction="backward",allow_exact_matches=False
    )
    valid=p.sage_ready_utc.notna()
    if not (p.loc[valid,"sage_ready_utc"]<p.loc[valid,"start_utc"]).all():
        raise RuntimeError("SAGE_LEAK")
    p=t.res1h.attach(p,t.x1h(r),"g1h","1h")
    p=p.dropna(subset=ALL+["direction"]).copy()
    p["start_utc"]=pd.to_datetime(p.start_utc,utc=True)
    p["end_utc"]=pd.to_datetime(p.end_utc,utc=True)
    p["year"]=p.start_utc.dt.year
    p["y_up"]=(p.direction=="UP").astype(int)
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def inner_splits(tr):
    tr=tr.sort_values("start_utc").reset_index(drop=True)
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
        if len(it)<INNER_MIN or it.y_up.nunique()<2 or va.y_up.nunique()<2:
            continue
        out.append((it,va))
    return out

def choose_features(tr):
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
                pp=fit_l2(it,va,sel)
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

    best=max(x["ba"] for x in rows)
    short=[x for x in rows if x["ba"]>=best-.01]
    chosen=sorted(short,key=lambda x:(x["brier"],x["mean_selected"],x["C"]))[0]
    sel,cmap=fit_selector(tr,float(chosen["C"]))
    return sel,float(chosen["C"]),{"scores":rows,"chosen":chosen},cmap

def collect_selection_events(p):
    events=[]
    for (part,win),g0 in p.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.year.isin([2023,2024])].reset_index(drop=True)
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
            sel,C,detail,cmap=choose_features(tr)
            events.append({
                "partition":part,"window":win,"outer_block":int(bs//BLOCK),
                "outer_year":int(te.year.iloc[0]),"cutoff":str(cut),
                "train_n":int(len(tr)),"selector_C":C,
                "selected_features":json.dumps(sel,separators=(",",":")),
                "coefficients":json.dumps(cmap,separators=(",",":")),
                "detail":json.dumps(detail,separators=(",",":"))
            })
    return pd.DataFrame(events)

def freeze_features(events):
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
            rows.append({
                "feature":f,"family":"PATH" if f in PATH else "SAGE",
                "freq":n/total,"both_years":len(years[f])>=2,
                "mean_abs_coef":float(np.mean(mag[f])) if mag[f] else 0.0
            })
        q=pd.DataFrame(rows).sort_values(
            ["both_years","freq","mean_abs_coef"],
            ascending=[False,False,False]
        )
        chosen=q[q.both_years].feature.tolist()[:MAX_FREEZE]
        if len(chosen)<MIN_FREEZE:
            for f in q.feature.tolist():
                if f not in chosen:chosen.append(f)
                if len(chosen)>=MIN_FREEZE:break

        # Enforce PATH+SAGE identity.
        if not any(f in PATH for f in chosen):
            cand=q[q.family.eq("PATH")].feature.tolist()
            if cand:chosen.append(cand[0])
        if not any(f in SAGE for f in chosen):
            cand=q[q.family.eq("SAGE")].feature.tolist()
            if cand:chosen.append(cand[0])

        # If over cap after group enforcement, retain best-ranked but preserve both groups.
        rank={f:i for i,f in enumerate(q.feature.tolist())}
        chosen=list(dict.fromkeys(chosen))
        while len(chosen)>MAX_FREEZE:
            removable=sorted(chosen,key=lambda f:rank.get(f,999),reverse=True)
            removed=False
            for f in removable:
                trial=[x for x in chosen if x!=f]
                if any(x in PATH for x in trial) and any(x in SAGE for x in trial):
                    chosen=trial;removed=True;break
            if not removed:break

        path_sel=[f for f in chosen if f in PATH]
        sage_sel=[f for f in chosen if f in SAGE]
        out.append({
            "partition":part,"window":win,
            "frozen_features":chosen,
            "frozen_path_features":path_sel,
            "frozen_sage_features":sage_sel,
            "n_features":len(chosen),
            "eligible_outer_blocks":int(total)
        })
    return out

def replay_frozen(p,frozen,years,continuous=False):
    fmap={(x["partition"],x["window"]):x for x in frozen}
    rows=[]
    for (part,win),g0 in p.groupby(["partition","window"],sort=True):
        if (part,win) not in fmap:continue
        spec=fmap[(part,win)]
        sel=spec["frozen_features"]
        path_sel=spec["frozen_path_features"]
        if not path_sel or not spec["frozen_sage_features"]:
            raise RuntimeError("IDENTITY_COLLAPSE")
        g=g0.sort_values("start_utc").reset_index(drop=True)
        if continuous:
            teall=g[g.year.isin([2023,2024,2025])].reset_index(drop=True)
        else:
            teall=g[g.year.isin(years)].reset_index(drop=True)
        for bs in range(0,len(teall),BLOCK):
            te=teall.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cut=te.start_utc.min()
            tr=g[(g.end_utc<=cut)&(g.start_utc<cut)].copy()
            if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
            models=[
                ("SELECTED_PATH_MATCHED",path_sel),
                ("SELECTED_PATH_SESSION",sel),
                ("CANONICAL_PATH_GLOBAL",PATH),
                ("CANONICAL_PATH_SESSION",ALL)
            ]
            for name,fs in models:
                pp=fit_l2(tr,te,fs)
                for r,pv in zip(te.itertuples(index=False),pp):
                    if int(r.year) not in years:continue
                    rows.append({
                        "model":name,"partition":part,"window":win,
                        "label_date":r.label_date,"start_utc":r.start_utc,
                        "end_utc":r.end_utc,"year":int(r.year),"y_up":int(r.y_up),
                        "p_up":float(pv),"train_n":int(len(tr)),
                        "block":int(bs//BLOCK),"features":"|".join(fs)
                    })
    return pd.DataFrame(rows)

def paired(pred,cand,comp):
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
    p=build_panel()
    events=collect_selection_events(p)
    frozen=freeze_features(events)

    dev=replay_frozen(p,frozen,[2023,2024],continuous=False)
    dev_pairs=paired(dev,"SELECTED_PATH_SESSION","SELECTED_PATH_MATCHED")
    gate=eligibility(dev_pairs)

    eligible_keys={(r.partition,r.window) for r in gate.itertuples(index=False) if bool(r.eligible)}
    frozen_eligible=[x for x in frozen if (x["partition"],x["window"]) in eligible_keys]

    if frozen_eligible:
        tr=replay_frozen(p,frozen_eligible,[2025],continuous=True)
        tr_pairs=paired(tr,"SELECTED_PATH_SESSION","SELECTED_PATH_MATCHED")
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
        "status":"SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_COMPLETE",
        "baseline":"S16_PATH_SESSION",
        "challenger":"SELECTED_PATH_SESSION",
        "matched_comparator":"SELECTED_PATH_MATCHED using exactly the same frozen PATH subset",
        "candidate_families":{"path":PATH,"sage":SAGE},
        "identity_constraint":"at least one PATH + at least one SAGE variable",
        "clock_policy":"canonical SAGE strict sage_ready_utc < target_start plus canonical pre-target hourly PATH",
        "chronology":"2022 warm-up; 2023-2024 selection/gate; 2025 only pre-eligible heads; 2026 unopened",
        "frozen_features":frozen,
        "eligibility":gate.to_dict("records"),
        "transport_2025_paired":tr_pairs.to_dict("records"),
        "guardrails":[
            "No A1, 15m, cross-metal, macro, GVZ, COT or model-output features added.",
            "Selected PATH_SESSION cannot collapse to PATH-only or SESSION-only.",
            "2025 is opened only for heads passing the frozen paired development gate.",
            "No 2025 feature reselection, threshold tuning, C tuning or eligibility rescue.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SESSION MODEL-07B — SAGE PATH_SESSION FEATURE-SELECTION RESULT","",
        "**Status:** complete.","",
        "## Frozen representations","",
        "| Partition | Window | PATH variables | SAGE variables |",
        "|---|---|---|---|"
    ]
    for x in frozen:
        lines.append(f"| {x['partition']} | {x['window']} | {', '.join(x['frozen_path_features'])} | {', '.join(x['frozen_sage_features'])} |")
    lines += ["","## Pre-2025 eligibility","",
              "| Partition | Window | N | Candidate BA | Comparator BA | UP | DOWN | Eligible | Reason |",
              "|---|---|---:|---:|---:|---:|---:|---|---|"]
    for r in gate.itertuples(index=False):
        lines.append(f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.candidate_ba:.2f}% | "
                     f"{100*r.comparator_ba:.2f}% | {100*r.candidate_up_recall:.2f}% | "
                     f"{100*r.candidate_down_recall:.2f}% | {r.eligible} | {r.reason} |")
    lines += ["","## 2025 transport",""]
    if tr_pairs.empty:
        lines.append("No selected PATH_SESSION head passed the pre-2025 paired gate; 2025 remained closed.")
    else:
        lines += ["| Partition | Window | N | Candidate BA | Comparator BA | Delta BA | Candidate Brier | Comparator Brier |",
                  "|---|---|---:|---:|---:|---:|---:|---:|"]
        for r in tr_pairs[tr_pairs.period.eq("2025")].itertuples(index=False):
            lines.append(f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.candidate_ba:.2f}% | "
                         f"{100*r.comparator_ba:.2f}% | {r.delta_ba_pp:+.2f} pp | "
                         f"{r.candidate_brier:.4f} | {r.comparator_brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"eligibility":summary["eligibility"],
                      "transport_2025_paired":summary["transport_2025_paired"]},indent=2,default=str))

if __name__=="__main__":
    main()
