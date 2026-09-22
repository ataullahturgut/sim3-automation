from __future__ import annotations

import json, sys
from datetime import date
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path("gold_axis_2026/tools").resolve()))
import downside_cbr_dtw_path_v1 as dtw
import downside_sp500_crossmarket_veto_v1 as spv

IDENTITY="DOWNSIDE_SELECTIVE_TRIAGE_V1_RESEARCH"
YEARS=(2024,2025,2026)

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

def group_stats(y,mask):
    n=int(np.sum(mask))
    if n==0:
        return {"n":0,"coverage":0.0,"down_n":0,"down_rate":None}
    yy=y[mask]
    return {"n":n,"down_n":int(np.sum(yy)),"down_rate":float(np.mean(yy))}

def year_eval(rows,year):
    cutoff=date(year-1,12,31)
    hist=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
    test=[r for r in rows if int(r["evaluation_year"])==year and int(r["sqrt_high_risk_alert"])==1]
    path_train=[r for r in hist if int(r["sqrt_high_risk_alert"])==1]
    sp_train=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
    if len(path_train)<dtw.K: raise RuntimeError(f"PATH_TRAIN_TOO_SMALL:{year}")
    spfit=spv.fit_logit(sp_train)
    psp=spv.probs(spfit,test)
    ppath=np.asarray([dtw.case_prob(path_train,t)[0] for t in test],float)
    y=np.asarray([int(r["meta_y"]) for r in test],int)

    confirm=(ppath>=.5)&(psp>=.5)
    veto=(ppath<.5)&(psp<.5)
    uncertain=~(confirm|veto)

    gs={}
    for name,mask in [("CONFIRM_DOWN",confirm),("VETO_SUSPECT",veto),("UNCERTAIN",uncertain)]:
        d=group_stats(y,mask);d["coverage"]=float(np.mean(mask));gs[name]=d

    separation=None
    if gs["CONFIRM_DOWN"]["down_rate"] is not None and gs["VETO_SUSPECT"]["down_rate"] is not None:
        separation=gs["CONFIRM_DOWN"]["down_rate"]-gs["VETO_SUSPECT"]["down_rate"]

    decided=confirm|veto
    decided_acc=None
    if np.sum(decided):
        pred=confirm[decided].astype(int)
        decided_acc=float(np.mean(pred==y[decided]))

    return {
        "test_alarm_n":len(test),
        "actual_down_n":int(np.sum(y)),
        "path_train_n":len(path_train),
        "sp_context_train_n":len(sp_train),
        "groups":gs,
        "confirm_minus_veto_down_rate":separation,
        "decided_coverage":float(np.mean(decided)),
        "decided_accuracy":decided_acc
    }

def main():
    out=Path("selective_triage_out");out.mkdir(exist_ok=True)
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
    (out/"GOLD_CONTROL_DOWNSIDE_SELECTIVE_TRIAGE_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))
    lines=["# GOLD CONTROL — SELECTIVE TRIAGE V1 RESULT","",
           "**Status:** EXPLORATORY / POST-RESULT-DESIGNED / NOT CONFIRMATORY  ",
           "**Manifest modified:** NO  ","",
           "| Year | Confirm n | Confirm DOWN% | Veto n | Veto DOWN% | Uncertain n | Uncertain DOWN% | Decided coverage | Decided accuracy | Separation |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    def f(v): return "-" if v is None else f"{v:.4f}"
    for y in YEARS:
        b=years[str(y)];g=b["groups"]
        lines.append(f"| {y} | {g['CONFIRM_DOWN']['n']} | {f(g['CONFIRM_DOWN']['down_rate'])} | "
                     f"{g['VETO_SUSPECT']['n']} | {f(g['VETO_SUSPECT']['down_rate'])} | "
                     f"{g['UNCERTAIN']['n']} | {f(g['UNCERTAIN']['down_rate'])} | "
                     f"{f(b['decided_coverage'])} | {f(b['decided_accuracy'])} | {f(b['confirm_minus_veto_down_rate'])} |")
    (out/"GOLD_CONTROL_DOWNSIDE_SELECTIVE_TRIAGE_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("SELECTIVE_TRIAGE_SUCCESS")

if __name__=="__main__": main()
