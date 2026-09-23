from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

IDENTITY="UP2_CONTINUATION_MIMIC_VETO_V1_RESEARCH"
MIN_HISTORY=40
MIN_UP_CAL=20


def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_FAIL:{name}:{path}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def read_csv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def nearest_rank(vals,q):
    x=sorted(float(v) for v in vals)
    if not x:return None
    k=max(1,min(len(x),int(math.ceil(q*len(x)))))
    return x[k-1]


def fit_model(rows):
    x=np.asarray([[r["last_hour_trend_r2"]] for r in rows],float)
    y=np.asarray([1-int(r["actual_up"]) for r in rows],int)
    mu=x.mean(axis=0)
    sd=x.std(axis=0)
    sd=np.where(sd<1e-12,1.0,sd)
    model=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000)
    model.fit((x-mu)/sd,y)
    return model,mu,sd


def predict(model,mu,sd,rows):
    x=np.asarray([[r["last_hour_trend_r2"]] for r in rows],float)
    return model.predict_proba((x-mu)/sd)[:,1]


def safe_corr(a,b):
    x=np.asarray(a,float); y=np.asarray(b,float)
    if len(x)<2:return None
    if np.std(x)<1e-15 or np.std(y)<1e-15:
        return 1.0 if np.allclose(x,y,atol=1e-12,rtol=0) else 0.0
    return float(np.corrcoef(x,y)[0,1])


def evaluate(rows):
    calls=len(rows)
    orig_true=sum(r["actual_up"]==1 for r in rows)
    orig_false=calls-orig_true
    vetoed=[r for r in rows if r["veto_call"]==1]
    bad_removed=sum(r["actual_up"]==0 for r in vetoed)
    good_lost=sum(r["actual_up"]==1 for r in vetoed)
    kept=[r for r in rows if r["veto_call"]==0]
    kept_true=sum(r["actual_up"]==1 for r in kept)
    kept_false=len(kept)-kept_true
    return {
        "original_calls":calls,
        "original_true_up":orig_true,
        "original_false_up":orig_false,
        "veto_calls":len(vetoed),
        "false_up_removed":bad_removed,
        "true_up_incorrectly_vetoed":good_lost,
        "false_up_reduction":bad_removed/orig_false if orig_false else None,
        "true_up_retention":kept_true/orig_true if orig_true else None,
        "remaining_calls":len(kept),
        "remaining_true_up":kept_true,
        "remaining_false_up":kept_false,
        "remaining_precision":kept_true/len(kept) if kept else None,
        "median_pdown_true_up":float(np.median([r["p_down"] for r in rows if r["actual_up"]==1])) if orig_true else None,
        "median_pdown_false_up":float(np.median([r["p_down"] for r in rows if r["actual_up"]==0])) if orig_false else None,
    }


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
    ap.add_argument("--up2-ledger",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",a.route_module)
    base=load_mod("base_authority",a.base_module)
    up2=load_mod("up2_authority",a.up2_module)
    mech=load_mod("mech_authority",a.mechanism_module)
    cbr=load_mod("cbr_authority",a.cbr_code)
    sqrt_mod=route.load_sqrt_mod(a.sqrt_code)

    spine=route.load_external_spine(a.external_spine)
    ext_raw=route.build_external_5m(a.raw_root)
    audit=route.external_reconstruction_audit(ext_raw,spine)
    if not audit["passed"]: raise RuntimeError("EXTERNAL_RECON_FAIL")
    daily=route.load_external_daily_for_sqrt(spine)
    ext_sqrt,ext_sqrt_summary=route.external_sqrt_cases(sqrt_mod,daily)
    ext_router,ext_router_summary=route.external_router_rows(base,spine)
    ext_unresolved,ext_route_summary=route.route_external_sqrt_cases(ext_sqrt,ext_router)
    if len(ext_unresolved)!=98 or sum(r["actual_up"] for r in ext_unresolved)!=46:
        raise RuntimeError("EXTERNAL_RESIDUAL_MISMATCH")

    ext_cases=[]
    for r in ext_unresolved:
        z={"origin_date":r["origin_date"],"target_date":r["target_date"],"actual_up":int(r["actual_up"])}
        z.update(mech.features(ext_raw[r["origin_date"]]["rets"]))
        ext_cases.append(z)
    ext_cases=sorted(ext_cases,key=lambda r:r["target_date"])

    cal=[]
    for j in range(MIN_HISTORY,len(ext_cases)):
        prior=ext_cases[:j]
        if len({r["actual_up"] for r in prior})<2: continue
        model,mu,sd=fit_model(prior)
        p=float(predict(model,mu,sd,[ext_cases[j]])[0])
        cal.append({"actual_up":ext_cases[j]["actual_up"],"p_down":p})
    up_scores=[r["p_down"] for r in cal if r["actual_up"]==1]
    if len(up_scores)<MIN_UP_CAL:
        raise RuntimeError(f"CAL_UP_TOO_SHORT:{len(up_scores)}")
    q80=nearest_rank(up_scores,.80)
    tau=max(0.50,float(q80))

    model,mu,sd=fit_model(ext_cases)

    gov_paths=cbr.load_paths(["2020-01-02","2025-12-31"])

    # Recompute promoted feature transfer.
    extv=[]; govv=[]
    for d in sorted(set(ext_raw)&set(gov_paths)):
        if len(ext_raw[d]["rets"])<239 or len(gov_paths[d])<239: continue
        extv.append(mech.features(ext_raw[d]["rets"])["last_hour_trend_r2"])
        govv.append(mech.features(gov_paths[d])["last_hour_trend_r2"])
    transfer={
        "n":len(extv),
        "pearson":safe_corr(extv,govv),
        "median_abs_diff":float(np.median(np.abs(np.asarray(extv)-np.asarray(govv)))) if extv else None,
    }

    led=read_csv(a.up2_ledger)
    gov_calls=[]
    for r in led:
        if int(r["up2_call"])!=1: continue
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025): continue
        od=r["origin_date"]
        if od not in gov_paths: raise RuntimeError(f"GOV_PATH_MISSING:{od}")
        feat=mech.features(gov_paths[od])["last_hour_trend_r2"]
        z={
            "evaluation_year":y,"origin_date":od,"target_date":r["target_date"],
            "actual_up":int(r["actual_up"]),"last_hour_trend_r2":feat
        }
        p=float(predict(model,mu,sd,[z])[0])
        z["p_down"]=p; z["tau_veto"]=tau; z["veto_call"]=int(p>tau)
        gov_calls.append(z)

    pre=[r for r in gov_calls if r["evaluation_year"]<=2024]
    y25=[r for r in gov_calls if r["evaluation_year"]==2025]
    if len(pre)!=11 or sum(r["actual_up"] for r in pre)!=8:
        raise RuntimeError("PRE_CALL_COUNT_MISMATCH")
    if len(y25)!=25 or sum(r["actual_up"] for r in y25)!=13:
        raise RuntimeError("Y25_CALL_COUNT_MISMATCH")

    pre_m=evaluate(pre); y25_m=evaluate(y25)
    supported=bool(
        pre_m["false_up_removed"]>=1
        and pre_m["false_up_reduction"] is not None and pre_m["false_up_reduction"]>=1/3
        and pre_m["true_up_retention"] is not None and pre_m["true_up_retention"]>=0.75
        and pre_m["remaining_precision"] is not None and pre_m["remaining_precision"]>(8/11)
    )
    status="VETO_V1_FEASIBILITY_SUPPORTED" if supported else "VETO_V1_FEASIBILITY_NOT_SUPPORTED"

    result={
        "identity":IDENTITY,"date":"2026-09-23","status":status,"integrity_errors":[],
        "method":{
            "feature":"last_hour_trend_r2",
            "target":"actual_down",
            "model":"L2 LogisticRegression C=1.0 lbfgs",
            "threshold":"max(0.50, nearest-rank q80 of strictly prequential external actual-UP p(DOWN) scores)",
            "retrospective_feature_selection":True,
        },
        "external_reconstruction":audit,
        "external_sqrt_summary":ext_sqrt_summary,
        "external_router_summary":ext_router_summary,
        "external_route_summary":ext_route_summary,
        "external_train_n":len(ext_cases),
        "external_train_up":sum(r["actual_up"] for r in ext_cases),
        "external_train_down":sum(1-r["actual_up"] for r in ext_cases),
        "prequential_calibration_n":len(cal),
        "prequential_actual_up_calibration_n":len(up_scores),
        "q80_up_pdown":q80,
        "tau_veto":tau,
        "model_coef_standardized":float(model.coef_[0][0]),
        "model_intercept":float(model.intercept_[0]),
        "feature_transfer":transfer,
        "governed_2022_2024":pre_m,
        "locked_2025":y25_m,
        "governance":{
            "random_split":False,"2025_tuning":False,"2026_used":False,
            "feature_sweep":False,"runtime_promotion":False,
        }
    }
    (a.out/"GOLD_CONTROL_UP2_CONTINUATION_MIMIC_VETO_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    fields=["evaluation_year","origin_date","target_date","actual_up","last_hour_trend_r2","p_down","tau_veto","veto_call"]
    with (a.out/"GOLD_CONTROL_UP2_CONTINUATION_MIMIC_VETO_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in gov_calls:w.writerow({k:r[k] for k in fields})

    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
