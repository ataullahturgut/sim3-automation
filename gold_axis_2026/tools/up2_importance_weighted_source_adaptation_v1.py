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
from sklearn.metrics import roc_auc_score

IDENTITY="UP2_IMPORTANCE_WEIGHTED_SOURCE_ADAPTATION_V1_RESEARCH"
FEATURES=["last_hour_trend_r2","sqrt_score","late_downside_intensity"]
WEIGHT_CAP=10.0
ESS_MIN=20.0


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


def safe_corr(a,b):
    x=np.asarray(a,float); y=np.asarray(b,float)
    if len(x)<2: return None
    sx=float(np.std(x)); sy=float(np.std(y))
    if sx<=1e-15 or sy<=1e-15:
        return 1.0 if np.allclose(x,y,atol=1e-12,rtol=0) else 0.0
    return float(np.corrcoef(x,y)[0,1])


def source_rows(route,sqrt_mod,base,mech,spine,raw):
    daily=route.load_external_daily_for_sqrt(spine)
    sqrt_rows,sqrt_summary=route.external_sqrt_cases(sqrt_mod,daily)
    router_rows,router_summary=route.external_router_rows(base,spine)
    residual,route_summary=route.route_external_sqrt_cases(sqrt_rows,router_rows)

    expected_sqrt={"2020":{"alarms":212,"down":97,"up":115},"2021":{"alarms":28,"down":16,"up":12}}
    expected_router={
        "2020":{"n":260,"router_up":185,"tp":111,"fp":74},
        "2021":{"n":258,"router_up":33,"tp":19,"fp":14},
    }
    expected_route={
        "2020":{"sqrt_alarms":212,"router_up_overlap":140,"overlap_actual_up":80,"overlap_actual_down":60,
                "router_abstain":72,"abstain_actual_down":37,"abstain_actual_up":35},
        "2021":{"sqrt_alarms":28,"router_up_overlap":2,"overlap_actual_up":1,"overlap_actual_down":1,
                "router_abstain":26,"abstain_actual_down":15,"abstain_actual_up":11},
    }
    if sqrt_summary!=expected_sqrt:
        raise RuntimeError(f"SOURCE_SQRT_MISMATCH:{sqrt_summary}")
    if router_summary!=expected_router:
        raise RuntimeError(f"SOURCE_ROUTER_MISMATCH:{router_summary}")
    if route_summary!=expected_route:
        raise RuntimeError(f"SOURCE_ROUTE_MISMATCH:{route_summary}")

    smap={(r["origin_date"],r["target_date"]):r for r in sqrt_rows}
    out=[]
    for r in residual:
        key=(r["origin_date"],r["target_date"])
        if r["origin_date"] not in raw:
            raise RuntimeError(f"SOURCE_RAW_MISSING:{key}")
        s=smap[key]
        mf=mech.features(raw[r["origin_date"]]["rets"])
        z={
            "evaluation_year":int(r["evaluation_year"]),
            "origin_date":r["origin_date"],
            "target_date":r["target_date"],
            "actual_up":int(r["actual_up"]),
            "failure":1-int(r["actual_up"]),
            "last_hour_trend_r2":float(mf["last_hour_trend_r2"]),
            "sqrt_score":float(s["sqrt_normalized_risk_score"]),
            "late_downside_intensity":float(mf["late_downside_intensity"]),
        }
        if not all(math.isfinite(z[f]) for f in FEATURES):
            raise RuntimeError(f"SOURCE_NONFINITE:{key}")
        out.append(z)
    if len(out)!=98 or sum(r["actual_up"] for r in out)!=46:
        raise RuntimeError(f"SOURCE_COUNT_FAIL:{len(out)}/{sum(r['actual_up'] for r in out)}")
    return out,sqrt_summary,router_summary,route_summary


def target_call_rows(ledger,gov_paths,mech):
    out=[]; errs=[]
    for r in ledger:
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025) or int(r["up2_call"])!=1:
            continue
        od=r["origin_date"]
        if od not in gov_paths:
            errs.append(f"GOV_PATH_MISSING:{od}")
            continue
        mf=mech.features(gov_paths[od])
        z={
            "evaluation_year":y,
            "origin_date":od,
            "target_date":r["target_date"],
            "actual_up":int(r["actual_up"]),
            "failure":1-int(r["actual_up"]),
            "last_hour_trend_r2":float(mf["last_hour_trend_r2"]),
            "sqrt_score":float(r["sqrt_score"]),
            "late_downside_intensity":float(mf["late_downside_intensity"]),
        }
        if not all(math.isfinite(z[f]) for f in FEATURES):
            errs.append(f"GOV_NONFINITE:{od}")
        out.append(z)
    exp={2022:(7,4,3),2023:(1,1,0),2024:(3,3,0),2025:(25,13,12)}
    for y,(n,u,d) in exp.items():
        rr=[r for r in out if r["evaluation_year"]==y]
        got=(len(rr),sum(r["actual_up"] for r in rr),sum(r["failure"] for r in rr))
        if got!=(n,u,d):
            errs.append(f"CALL_COUNT_MISMATCH:{y}:{got}:{(n,u,d)}")
    return out,errs


def transfer_audit(mech,ext_raw,gov_raw):
    vals={f:{"ext":[],"gov":[]} for f in ("last_hour_trend_r2","late_downside_intensity")}
    common=[]
    for d in sorted(set(ext_raw)&set(gov_raw)):
        er=ext_raw[d]["rets"]; gr=gov_raw[d]
        if len(er)<239 or len(gr)<239: continue
        ef=mech.features(er); gf=mech.features(gr)
        common.append(d)
        for f in vals:
            vals[f]["ext"].append(float(ef[f]))
            vals[f]["gov"].append(float(gf[f]))
    out={"overlap_n":len(common),"features":{}}
    for f in vals:
        x=np.asarray(vals[f]["ext"]); y=np.asarray(vals[f]["gov"])
        out["features"][f]={
            "pearson":safe_corr(x,y),
            "median_abs_diff":float(np.median(np.abs(x-y))) if len(x) else None,
        }
    out["passed"]=bool(
        len(common)>=300
        and out["features"]["late_downside_intensity"]["pearson"] is not None
        and out["features"]["late_downside_intensity"]["pearson"]>=0.90
        and out["features"]["last_hour_trend_r2"]["pearson"] is not None
        and out["features"]["last_hour_trend_r2"]["pearson"]>=0.80
        and out["features"]["last_hour_trend_r2"]["median_abs_diff"] is not None
        and out["features"]["last_hour_trend_r2"]["median_abs_diff"]<=0.15
    )
    return out


def fit_domain_weights(source,target):
    Xs=np.asarray([[r[f] for f in FEATURES] for r in source],float)
    Xt=np.asarray([[r[f] for f in FEATURES] for r in target],float)
    X=np.vstack([Xs,Xt])
    d=np.asarray([0]*len(Xs)+[1]*len(Xt),int)
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=0)
    sd=np.where(sd<1e-12,1.0,sd)
    Z=(X-mu)/sd
    model=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000)
    model.fit(Z,d)
    p=model.predict_proba(Z)[:,1]
    auc=float(roc_auc_score(d,p))
    eta=np.clip(model.predict_proba((Xs-mu)/sd)[:,1],1e-6,1-1e-6)
    ratio=(eta/(1.0-eta))*(len(Xs)/len(Xt))
    capped=np.minimum(ratio,WEIGHT_CAP)
    mean=float(np.mean(capped))
    if mean<=0:
        raise RuntimeError("ZERO_MEAN_WEIGHT")
    w=capped/mean
    ess=float((np.sum(w)**2)/np.sum(w*w))
    return {
        "weights":w,
        "raw_ratio":ratio,
        "capped_ratio":capped,
        "domain_auc":auc,
        "domain_coef":{f:float(v) for f,v in zip(FEATURES,model.coef_[0])},
        "domain_intercept":float(model.intercept_[0]),
        "combined_mean":{f:float(v) for f,v in zip(FEATURES,mu)},
        "combined_std":{f:float(v) for f,v in zip(FEATURES,sd)},
        "ess":ess,
    }


def fit_failure(source,sample_weight=None):
    X=np.asarray([[r[f] for f in FEATURES] for r in source],float)
    y=np.asarray([r["failure"] for r in source],int)
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=0)
    sd=np.where(sd<1e-12,1.0,sd)
    model=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000)
    model.fit((X-mu)/sd,y,sample_weight=sample_weight)
    return model,mu,sd


def score(model,mu,sd,rows):
    if not rows: return []
    X=np.asarray([[r[f] for f in FEATURES] for r in rows],float)
    p=model.predict_proba((X-mu)/sd)[:,1]
    out=[]
    for r,pp in zip(rows,p):
        z=dict(r)
        z["p_fail"]=float(pp)
        z["veto"]=int(pp>=0.50)
        z["keep_up"]=1-z["veto"]
        out.append(z)
    return out


def summarize(rows):
    safe=[r for r in rows if r["failure"]==0]
    fail=[r for r in rows if r["failure"]==1]
    veto=[r for r in rows if r["veto"]==1]
    false_removed=sum(r["failure"]==1 for r in veto)
    true_lost=sum(r["failure"]==0 for r in veto)
    true_keep=len(safe)-true_lost
    false_keep=len(fail)-false_removed
    rem=true_keep+false_keep
    return {
        "n":len(rows),
        "captured_up":len(safe),
        "false_up_actual_down":len(fail),
        "vetoes":len(veto),
        "false_up_removed":false_removed,
        "captured_up_lost":true_lost,
        "captured_up_retained":true_keep,
        "false_up_removal_rate":false_removed/len(fail) if fail else None,
        "captured_up_retention_rate":true_keep/len(safe) if safe else None,
        "precision_before":len(safe)/len(rows) if rows else None,
        "precision_after":true_keep/rem if rem else None,
        "remaining_calls":rem,
    }


def model_report(model):
    return {
        "standardized_coefficients":{f:float(v) for f,v in zip(FEATURES,model.coef_[0])},
        "intercept":float(model.intercept_[0]),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--mechanism-code",type=Path,required=True)
    ap.add_argument("--up2-ledger",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",a.route_module)
    base=load_mod("base_authority",a.base_module)
    cbr=load_mod("cbr_authority",a.cbr_code)
    mech=load_mod("mechanism_authority",a.mechanism_code)
    sqrt_mod=route.load_sqrt_mod(a.sqrt_code)

    spine=route.load_external_spine(a.external_spine)
    ext_raw=route.build_external_5m(a.raw_root)
    ext_audit=route.external_reconstruction_audit(ext_raw,spine)
    if not ext_audit["passed"]:
        raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")

    source,sqrt_summary,router_summary,route_summary=source_rows(route,sqrt_mod,base,mech,spine,ext_raw)
    gov_paths=cbr.load_paths(["2020-01-02","2025-12-31"])
    transfer=transfer_audit(mech,ext_raw,{d:v for d,v in gov_paths.items() if d.startswith(("2020-","2021-"))})
    if not transfer["passed"]:
        raise RuntimeError(f"FEATURE_TRANSFER_FAILED:{transfer}")

    calls,errs=target_call_rows(read_csv(a.up2_ledger),gov_paths,mech)
    if errs:
        result={"identity":IDENTITY,"status":"BLOCKED_INTEGRITY","integrity_errors":errs}
        (a.out/"GOLD_CONTROL_UP2_IMPORTANCE_WEIGHTED_SOURCE_ADAPTATION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    target2022=[r for r in calls if r["evaluation_year"]==2022]
    guard=[r for r in calls if r["evaluation_year"] in (2023,2024)]
    locked=[r for r in calls if r["evaluation_year"]==2025]

    iw=fit_domain_weights(source,target2022)
    weights=iw["weights"]

    un_model,un_mu,un_sd=fit_failure(source,None)
    iw_model,iw_mu,iw_sd=fit_failure(source,weights)

    evaluations={}
    ledgers={}
    for name,model,mu,sd in [
        ("UNWEIGHTED_SOURCE",un_model,un_mu,un_sd),
        ("IMPORTANCE_WEIGHTED_SOURCE",iw_model,iw_mu,iw_sd),
    ]:
        s22=score(model,mu,sd,target2022)
        sg=score(model,mu,sd,guard)
        s25=score(model,mu,sd,locked)
        evaluations[name]={
            "target_2022_diagnostic":summarize(s22),
            "forward_guard_2023_2024":summarize(sg),
            "locked_2025":summarize(s25),
            "model":model_report(model),
        }
        ledgers[name]=s22+sg+s25

    ess_ok=iw["ess"]>=ESS_MIN
    w=evaluations["IMPORTANCE_WEIGHTED_SOURCE"]
    u=evaluations["UNWEIGHTED_SOURCE"]
    forward_ok=w["forward_guard_2023_2024"]["captured_up_retained"]>=3
    transport_ok=(
        w["locked_2025"]["false_up_removed"]>=3
        and w["locked_2025"]["captured_up_retained"]>=10
    )
    not_worse=(
        w["locked_2025"]["false_up_removed"]>=u["locked_2025"]["false_up_removed"]
        and w["locked_2025"]["captured_up_retained"]>=u["locked_2025"]["captured_up_retained"]
    )
    supportive=bool(ess_ok and forward_ok and transport_ok and not_worse)

    if not ess_ok:
        status="BLOCKED_IMPORTANCE_WEIGHT_ESS"
    elif supportive:
        status="IMPORTANCE_WEIGHTED_SIGNAL_SAMPLE_LIMITED_NOT_CERTIFIED"
    else:
        status="IMPORTANCE_WEIGHTED_ADAPTATION_NOT_SUPPORTED"

    raw=iw["raw_ratio"]; capped=iw["capped_ratio"]
    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":[],
        "scientific_role":"covariate-shift/sample-selection correction; source rows remain ordinary residual rows, not fabricated UP2 calls",
        "features":FEATURES,
        "external_reconstruction":ext_audit,
        "source_sqrt_summary":sqrt_summary,
        "source_router_summary":router_summary,
        "source_route_summary":route_summary,
        "feature_transfer":transfer,
        "source_counts":{
            "n":len(source),
            "actual_up":sum(r["actual_up"] for r in source),
            "actual_down":sum(r["failure"] for r in source),
        },
        "target_2022_covariate_n":len(target2022),
        "importance_weighting":{
            "method":"logistic domain classifier density ratio",
            "raw_ratio_cap":WEIGHT_CAP,
            "normalized_weight_mean":float(np.mean(weights)),
            "normalized_weight_min":float(np.min(weights)),
            "normalized_weight_median":float(np.median(weights)),
            "normalized_weight_max":float(np.max(weights)),
            "raw_ratio_min":float(np.min(raw)),
            "raw_ratio_median":float(np.median(raw)),
            "raw_ratio_max":float(np.max(raw)),
            "capped_ratio_max":float(np.max(capped)),
            "ess":iw["ess"],
            "ess_gate":ESS_MIN,
            "ess_gate_passed":ess_ok,
            "domain_classifier_auc_training_descriptive":iw["domain_auc"],
            "domain_coefficients":iw["domain_coef"],
            "domain_intercept":iw["domain_intercept"],
        },
        "evaluations":evaluations,
        "forward_guard_passed":forward_ok,
        "locked_2025_transport_supportive":transport_ok,
        "weighted_not_worse_than_unweighted_on_both_2025_components":not_worse,
        "adaptation_supportive":supportive,
        "governance":{
            "random_split":False,
            "fabricated_historical_up2_calls":False,
            "2022_outcomes_used_for_weight_estimation":False,
            "weight_cap_sweep":False,
            "feature_hyperparameter_threshold_sweep":False,
            "2025_used_for_tuning":False,
            "2026_used":False,
            "veto_means_down":False,
            "runtime_promotion":False,
            "certified":False,
        },
    }

    outj=a.out/"GOLD_CONTROL_UP2_IMPORTANCE_WEIGHTED_SOURCE_ADAPTATION_V1_RESULT_2026-09-23.json"
    outj.write_text(json.dumps(result,indent=2),encoding="utf-8")

    fields=["model","evaluation_year","origin_date","target_date","actual_up","failure",*FEATURES,"p_fail","veto","keep_up"]
    with (a.out/"GOLD_CONTROL_UP2_IMPORTANCE_WEIGHTED_SOURCE_ADAPTATION_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=fields); wr.writeheader()
        for name,rr in ledgers.items():
            for r in rr:
                z={"model":name,**r}
                wr.writerow({k:z.get(k,"") for k in fields})

    lines=[
        "# GOLD CONTROL — IMPORTANCE-WEIGHTED HISTORICAL SOURCE ADAPTATION V1","",
        f"**Status:** `{status}`","",
        f"Source: n={len(source)} (UP={sum(r['actual_up'] for r in source)}, DOWN={sum(r['failure'] for r in source)}).  ",
        f"2022 target covariate calls: n={len(target2022)}.  ",
        f"Importance-weight ESS={iw['ess']:.2f}; gate >= {ESS_MIN}; passed={ess_ok}.","",
        "| Model | 2023-24 true retained | 2025 false removed | 2025 true retained | 2025 precision before | 2025 precision after |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for name in ("UNWEIGHTED_SOURCE","IMPORTANCE_WEIGHTED_SOURCE"):
        g=evaluations[name]["forward_guard_2023_2024"]
        m=evaluations[name]["locked_2025"]
        after="" if m["precision_after"] is None else f"{100*m['precision_after']:.1f}%"
        lines.append(
            f"| {name} | {g['captured_up_retained']}/{g['captured_up']} | "
            f"{m['false_up_removed']}/{m['false_up_actual_down']} | "
            f"{m['captured_up_retained']}/{m['captured_up']} | "
            f"{100*m['precision_before']:.1f}% | {after} |"
        )
    lines += [
        "",
        "The 2022 call covariates were used for density-ratio estimation, but their outcome labels were not used to train either failure detector.",
        "No source row is treated as an actual historical UP2 call.",
        "Research-only; no veto is promoted."
    ]
    # avoid nested f-string quoting issue by reconstructing table rows if needed
    text="\n".join(lines)+"\n"
    # sanitize accidental nested format branch is resolved before execution
    (a.out/"GOLD_CONTROL_UP2_IMPORTANCE_WEIGHTED_SOURCE_ADAPTATION_V1_RESULT_2026-09-23.md").write_text(text,encoding="utf-8")

    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
