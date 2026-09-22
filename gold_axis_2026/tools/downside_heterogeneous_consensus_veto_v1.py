from __future__ import annotations

import json, sys
from datetime import date
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

sys.path.insert(0, str(Path("gold_axis_2026/tools").resolve()))
import downside_cbr_dtw_path_v1 as dtw
import downside_sp500_crossmarket_veto_v1 as spv

IDENTITY="DOWNSIDE_HETEROGENEOUS_CONSENSUS_VETO_V1_RESEARCH"
YEARS=(2024,2025,2026)

def auc(y,s):
    y=np.asarray(y,int); s=np.asarray(s,float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if not n1 or not n0: return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def confusion(y,pred):
    y=np.asarray(y,int); pred=np.asarray(pred,bool)
    tp=int(np.sum(pred&(y==1))); fp=int(np.sum(pred&(y==0)))
    fn=int(np.sum((~pred)&(y==1))); tn=int(np.sum((~pred)&(y==0)))
    rec=tp/(tp+fn) if tp+fn else None
    spec=tn/(tn+fp) if tn+fp else None
    prec=tp/(tp+fp) if tp+fp else None
    ba=(rec+spec)/2 if rec is not None and spec is not None else None
    return {"n":len(y),"actual_down":int(np.sum(y)),"confirm_count":int(np.sum(pred)),
            "tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":prec,"recall":rec,
            "specificity":spec,"balanced_accuracy":ba}

def add_ref(m,ref):
    m["false_alarm_reduction_count"]=ref["fp"]-m["fp"]
    m["false_alarm_reduction_rate"]=(ref["fp"]-m["fp"])/ref["fp"] if ref["fp"] else None
    m["true_down_retention_rate"]=m["tp"]/ref["tp"] if ref["tp"] else None
    return m

def key(r): return (r["origin_date"],r["target_date"])

def prepare():
    parent=dtw.load_parent()
    rawpaths=dtw.load_paths([r["origin_date"] for r in parent])
    prow=dtw.enrich(parent,rawpaths)

    sp=spv.load_sp500()
    srows,stale=spv.align(spv.load_parent(),sp)

    smap={key(r):r for r in srows}
    merged=[]
    for r in prow:
        s=smap.get(key(r))
        if s is None: continue
        z=dict(r)
        for k in ("sp_date","sp_age_days","sp_ret1","sp_ret5","sp_vol20","sp_z1","gold_risk_margin"):
            z[k]=s[k]
        merged.append(z)
    return merged,stale

def year_eval(rows,year):
    cutoff=date(year-1,12,31)
    hist=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
    test=[r for r in rows if int(r["evaluation_year"])==year and int(r["sqrt_high_risk_alert"])==1]
    if not test: raise RuntimeError(f"NO_TEST_ALERTS:{year}")

    path_train=[r for r in hist if int(r["sqrt_high_risk_alert"])==1]
    sp_train=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
    if len(path_train)<dtw.K: raise RuntimeError(f"PATH_TRAIN_TOO_SMALL:{year}")
    spfit=spv.fit_logit(sp_train)
    psp=spv.probs(spfit,test)

    ppath=[];dists=[]
    for t in test:
        p,d=dtw.case_prob(path_train,t)
        if p is None: raise RuntimeError(f"PATH_PROB_FAIL:{year}")
        ppath.append(p);dists.append(d)
    ppath=np.asarray(ppath,float); psp=np.asarray(psp,float)
    pc=np.maximum(ppath,psp)
    pred=pc>=0.50

    y=np.asarray([int(r["meta_y"]) for r in test],int)
    ref=confusion(y,np.ones(len(y),bool))
    m=add_ref(confusion(y,pred),ref)
    m.update({
        "auc":auc(y,pc),
        "brier":float(np.mean((pc-y)**2)),
        "mean_path_p":float(np.mean(ppath)),
        "mean_sp_p":float(np.mean(psp)),
        "mean_consensus_p":float(np.mean(pc)),
        "mean_path_neighbor_distance":float(np.mean(dists)),
        "both_confirm":int(np.sum((ppath>=.5)&(psp>=.5))),
        "path_only_confirm":int(np.sum((ppath>=.5)&(psp<.5))),
        "sp_only_confirm":int(np.sum((ppath<.5)&(psp>=.5))),
        "both_veto":int(np.sum((ppath<.5)&(psp<.5)))
    })
    promising=bool(
        m["false_alarm_reduction_rate"] is not None and m["false_alarm_reduction_rate"]>=0.20
        and m["recall"] is not None and m["recall"]>=0.70
        and m["balanced_accuracy"] is not None and m["balanced_accuracy"]>0.55
        and m["auc"] is not None and m["auc"]>0.55
    )
    return {
        "test_alarm_n":len(test),
        "path_train_n":len(path_train),
        "sp_context_train_n":len(sp_train),
        "reference_all_as_down":ref,
        "consensus":m,
        "exploratory_label":"EXPLORATORY_CONSENSUS_PROMISING" if promising else "EXPLORATORY_CONSENSUS_NOT_PROMISING"
    }

def main():
    out=Path("consensus_veto_out"); out.mkdir(exist_ok=True)
    rows,stale=prepare()
    years={str(y):year_eval(rows,y) for y in YEARS}
    result={
        "identity":IDENTITY,
        "manifest_modified":False,
        "production_write":"NONE",
        "status_class":"EXPLORATORY_POST_RESULT_DESIGNED_NOT_CONFIRMATORY",
        "aligned_rows":len(rows),
        "stale_exclusions":stale,
        "years":years
    }
    (out/"GOLD_CONTROL_DOWNSIDE_HETEROGENEOUS_CONSENSUS_VETO_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))
    lines=["# GOLD CONTROL — HETEROGENEOUS CONSENSUS VETO V1 RESULT","",
           "**Status:** EXPLORATORY / POST-RESULT-DESIGNED / NOT CONFIRMATORY  ",
           "**Manifest modified:** NO  ","",
           "| Year | TP | FP | FN | TN | Precision | Recall | BA | AUC | FA reduction | DOWN retained | Both veto | Label |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    def fmt(v): return "-" if v is None else f"{v:.4f}"
    for y in YEARS:
        b=years[str(y)];m=b["consensus"]
        lines.append(f"| {y} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | "
                     f"{fmt(m['precision'])} | {fmt(m['recall'])} | {fmt(m['balanced_accuracy'])} | "
                     f"{fmt(m['auc'])} | {fmt(m['false_alarm_reduction_rate'])} | {fmt(m['true_down_retention_rate'])} | "
                     f"{m['both_veto']} | {b['exploratory_label']} |")
    (out/"GOLD_CONTROL_DOWNSIDE_HETEROGENEOUS_CONSENSUS_VETO_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("CONSENSUS_VETO_SUCCESS")

if __name__=="__main__":
    main()
