from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

IDENTITY="UP2_STRICT_PREQUENTIAL_ERROR_POOL_EXTENSION_V1_RESEARCH"
MIN_HISTORY=40
MIN_DOWN_CAL=20


def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_FAIL:{name}:{path}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def safe_corr(a,b):
    x=np.asarray(a,float); y=np.asarray(b,float)
    if len(x)<2: return None
    sx=float(np.std(x)); sy=float(np.std(y))
    if sx<=1e-15 or sy<=1e-15:
        return 1.0 if np.allclose(x,y,atol=1e-12,rtol=0) else 0.0
    return float(np.corrcoef(x,y)[0,1])


def cliffs(a,b):
    aa=[float(v) for v in a]; bb=[float(v) for v in b]
    if not aa or not bb: return None
    gt=lt=0
    for x in aa:
        for y in bb:
            if x>y: gt+=1
            elif x<y: lt+=1
    return (gt-lt)/(len(aa)*len(bb))


def group(actual,call):
    if actual==1 and call==1: return "CAPTURED_UP"
    if actual==1 and call==0: return "MISSED_UP"
    if actual==0 and call==1: return "FALSE_UP_ACTUAL_DOWN"
    return "REJECTED_DOWN"


def nested_calibration(up2,rows,upto):
    cal=[]
    for j in range(MIN_HISTORY,upto):
        prior=rows[:j]
        if len({r["actual_up"] for r in prior})<2:
            continue
        model,mu,sd=up2.standardize_fit(prior)
        p=float(up2.predict_rows(model,mu,sd,[rows[j]])[0])
        cal.append({"actual_up":rows[j]["actual_up"],"p_up":p,"target_date":rows[j]["target_date"]})
    down=[r["p_up"] for r in cal if r["actual_up"]==0]
    if len(down)<MIN_DOWN_CAL:
        return None,cal,down
    q80=up2.nearest_rank(down,0.80)
    return max(0.50,float(q80)),cal,down


def harmonization(mech,ext_raw,gov_raw):
    common=[]
    vals={f:{"ext":[],"gov":[]} for f in mech.FEATURES}
    for d in sorted(set(ext_raw)&set(gov_raw)):
        er=ext_raw[d]["rets"]
        gr=gov_raw[d]
        if len(er)<239 or len(gr)<239: continue
        ef=mech.features(er); gf=mech.features(gr)
        common.append(d)
        for f in mech.FEATURES:
            vals[f]["ext"].append(float(ef[f]))
            vals[f]["gov"].append(float(gf[f]))
    diag={}
    for f in mech.FEATURES:
        x=np.asarray(vals[f]["ext"]); y=np.asarray(vals[f]["gov"])
        diag[f]={
            "pearson":safe_corr(x,y),
            "median_abs_diff":float(np.median(np.abs(x-y))) if len(x) else None,
        }
    gate=bool(
        len(common)>=300
        and diag["late_downside_intensity"]["pearson"] is not None
        and diag["late_downside_intensity"]["pearson"]>=0.90
        and diag["last_hour_trend_r2"]["pearson"] is not None
        and diag["last_hour_trend_r2"]["pearson"]>=0.80
        and diag["last_hour_trend_r2"]["median_abs_diff"] is not None
        and diag["last_hour_trend_r2"]["median_abs_diff"]<=0.15
    )
    return {"overlap_n":len(common),"features":diag,"promoted_feature_transfer_gate_passed":gate}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--up2-module",type=Path,required=True)
    ap.add_argument("--mechanism-module",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    up2=load_mod("up2_authority",a.up2_module)
    mech=load_mod("mechanism_authority",a.mechanism_module)
    route=load_mod("route_authority",a.route_module)
    base=load_mod("base_authority",a.base_module)
    cbr=load_mod("cbr_authority",a.cbr_code)
    sqrt_mod=route.load_sqrt_mod(a.sqrt_code)

    ext_spine=route.load_external_spine(a.external_spine)
    ext_raw=route.build_external_5m(a.raw_root)
    ext_audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]:
        raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")

    ext_daily=route.load_external_daily_for_sqrt(ext_spine)
    ext_sqrt,ext_sqrt_summary=route.external_sqrt_cases(sqrt_mod,ext_daily)
    ext_router,ext_router_summary=route.external_router_rows(base,ext_spine)
    ext_unresolved,ext_route_summary=route.route_external_sqrt_cases(ext_sqrt,ext_router)

    expected_route={
        "2020":{"sqrt_alarms":212,"router_up_overlap":140,"overlap_actual_up":80,"overlap_actual_down":60,
                "router_abstain":72,"abstain_actual_down":37,"abstain_actual_up":35},
        "2021":{"sqrt_alarms":28,"router_up_overlap":2,"overlap_actual_up":1,"overlap_actual_down":1,
                "router_abstain":26,"abstain_actual_down":15,"abstain_actual_up":11},
    }
    if ext_route_summary!=expected_route:
        raise RuntimeError(f"ROUTE_MISMATCH:{ext_route_summary}")

    router_map={(r["origin_date"],r["target_date"]):r for r in ext_router}
    sqrt_map={(r["origin_date"],r["target_date"]):r for r in ext_sqrt}
    lag=up2.lag_map_from_spine(ext_spine)
    cases=[]
    for r in ext_unresolved:
        key=(r["origin_date"],r["target_date"])
        rr=router_map[key]; sr=sqrt_map[key]
        z=up2.enrich_case(
            r,sr["sqrt_normalized_risk_score"],rr,lag[r["origin_date"]],
            ext_raw[r["origin_date"]]["rets"],"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"
        )
        z.update(mech.features(ext_raw[r["origin_date"]]["rets"]))
        cases.append(z)
    cases=sorted(cases,key=lambda r:r["target_date"])
    if len(cases)!=98 or sum(r["actual_up"] for r in cases)!=46:
        raise RuntimeError("EXTERNAL_CASE_COUNT_FAIL")

    gov_raw=cbr.load_paths(["2020-01-02","2021-12-31"])
    harmon=harmonization(mech,ext_raw,gov_raw)

    ledger=[]
    for i,row in enumerate(cases):
        z={
            "index":i,
            "evaluation_year":row["evaluation_year"],
            "origin_date":row["origin_date"],
            "target_date":row["target_date"],
            "actual_up":row["actual_up"],
        }
        if i<MIN_HISTORY:
            z.update({"status":"NOT_SCORABLE_PREQUENTIAL_SUPPORT","calibration_n":0,"down_calibration_n":0})
            ledger.append(z); continue
        tau,cal,down=nested_calibration(up2,cases,i)
        if tau is None:
            z.update({
                "status":"NOT_SCORABLE_PREQUENTIAL_SUPPORT",
                "calibration_n":len(cal),
                "down_calibration_n":len(down),
            })
            ledger.append(z); continue
        model,mu,sd=up2.standardize_fit(cases[:i])
        p=float(up2.predict_rows(model,mu,sd,[row])[0])
        call=int(p>tau)
        z.update({
            "status":"SCORABLE",
            "calibration_n":len(cal),
            "down_calibration_n":len(down),
            "tau":tau,
            "p_up":p,
            "up2_call":call,
            "group":group(row["actual_up"],call),
            "last_hour_trend_r2":row["last_hour_trend_r2"],
            "late_downside_intensity":row["late_downside_intensity"],
        })
        for f in mech.FEATURES:
            z[f]=row[f]
        ledger.append(z)

    scored=[r for r in ledger if r["status"]=="SCORABLE"]
    calls=[r for r in scored if r["up2_call"]==1]
    tp=sum(r["actual_up"]==1 for r in calls)
    fp=sum(r["actual_up"]==0 for r in calls)
    au=sum(r["actual_up"]==1 for r in scored)
    ad=len(scored)-au
    groups={g:sum(r.get("group")==g for r in scored) for g in ["CAPTURED_UP","MISSED_UP","FALSE_UP_ACTUAL_DOWN","REJECTED_DOWN"]}

    cap=[r for r in scored if r.get("group")=="CAPTURED_UP"]
    false=[r for r in scored if r.get("group")=="FALSE_UP_ACTUAL_DOWN"]
    missed=[r for r in scored if r.get("group")=="MISSED_UP"]

    candidate_support=bool(len(calls)>=5 and len(false)>=2 and harmon["promoted_feature_transfer_gate_passed"])

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":"ERROR_POOL_EXTENSION_SUPPORTIVE" if candidate_support else "ERROR_POOL_EXTENSION_INSUFFICIENT",
        "integrity_errors":[],
        "external_reconstruction":ext_audit,
        "external_sqrt_summary":ext_sqrt_summary,
        "external_router_summary":ext_router_summary,
        "external_route_summary":ext_route_summary,
        "feature_harmonization":harmon,
        "total_external_residual_n":len(cases),
        "scorable_n":len(scored),
        "first_scorable_target_date":scored[0]["target_date"] if scored else None,
        "last_scorable_target_date":scored[-1]["target_date"] if scored else None,
        "calls":len(calls),
        "true_up":tp,
        "false_up":fp,
        "precision":tp/len(calls) if calls else None,
        "recall":tp/au if au else None,
        "false_up_fpr":fp/ad if ad else None,
        "coverage":len(calls)/len(scored) if scored else None,
        "error_cells":groups,
        "mechanism_checks":{
            "captured_vs_false_last_hour_trend_r2":{
                "captured_median":float(np.median([r["last_hour_trend_r2"] for r in cap])) if cap else None,
                "false_median":float(np.median([r["last_hour_trend_r2"] for r in false])) if false else None,
                "cliffs_delta":cliffs([r["last_hour_trend_r2"] for r in cap],[r["last_hour_trend_r2"] for r in false]),
            },
            "captured_vs_missed_late_downside_intensity":{
                "captured_median":float(np.median([r["late_downside_intensity"] for r in cap])) if cap else None,
                "missed_median":float(np.median([r["late_downside_intensity"] for r in missed])) if missed else None,
                "cliffs_delta":cliffs([r["late_downside_intensity"] for r in cap],[r["late_downside_intensity"] for r in missed]),
            },
        },
        "future_veto_prereg_allowed_by_sample_gate":candidate_support,
        "governance":{
            "strictly_prequential":True,
            "random_split":False,
            "frozen_up2_modified":False,
            "2025_used":False,
            "2026_used":False,
            "veto_fitted":False,
        }
    }
    (a.out/"GOLD_CONTROL_UP2_STRICT_PREQUENTIAL_ERROR_POOL_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    fields=[
        "index","evaluation_year","origin_date","target_date","actual_up","status",
        "calibration_n","down_calibration_n","tau","p_up","up2_call","group",
        *mech.FEATURES
    ]
    with (a.out/"GOLD_CONTROL_UP2_STRICT_PREQUENTIAL_ERROR_POOL_EXTENSION_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in ledger: w.writerow({k:r.get(k,"") for k in fields})

    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
