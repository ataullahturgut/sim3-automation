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

IDENTITY = "RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESEARCH"
FEATURES = [
    "downside_share",
    "max_drawdown_norm",
    "trough_position",
    "recovery_to_close_ratio",
    "close_location",
    "post_trough_return_norm",
    "last_quarter_return_norm",
    "post_trough_positive_fraction",
]
Z90 = 1.2815515655446004
MIN_PREQUENTIAL_HISTORY = 40
MIN_DOWN_CAL = 20


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_SPEC_FAIL:{name}:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def wilson_lcb(k: int, n: int):
    if n <= 0:
        return None
    p = k / n
    z = Z90
    den = 1.0 + z*z/n
    center = p + z*z/(2*n)
    rad = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return (center-rad)/den


def nearest_rank(values, q: float):
    x = sorted(float(v) for v in values)
    if not x:
        return None
    k = max(1, min(len(x), int(math.ceil(q*len(x)))))
    return x[k-1]


def safe_corr(x, y):
    a=np.asarray(x,float); b=np.asarray(y,float)
    if len(a)<2:
        return None
    sa=float(np.std(a)); sb=float(np.std(b))
    if sa<=1e-15 or sb<=1e-15:
        return 1.0 if np.allclose(a,b,atol=1e-12,rtol=0) else 0.0
    return float(np.corrcoef(a,b)[0,1])


def morphology_features(rets):
    r=np.asarray(rets,float)
    if len(r)<239:
        raise RuntimeError(f"TOO_FEW_RETURNS:{len(r)}")
    rv=float(np.sum(r*r))
    if not (rv>0):
        raise RuntimeError("ZERO_RV")
    scale=math.sqrt(rv)

    # Include the session start at cumulative return 0.
    path=np.concatenate(([0.0],np.cumsum(r)))
    trough_idx=int(np.argmin(path))
    trough=float(path[trough_idx])
    peak_before=float(np.max(path[:trough_idx+1]))
    drawdown=max(0.0,peak_before-trough)
    close=float(path[-1])
    pmin=float(np.min(path)); pmax=float(np.max(path))
    span=max(pmax-pmin,1e-8)

    recovery=close-trough
    recovery_ratio=recovery/max(drawdown,1e-8)
    trough_position=trough_idx/len(r)

    # Returns after the trough point. If the trough is at close, no post-trough
    # returns exist and the preregistered neutral value 0.5 is used.
    post=r[trough_idx:] if trough_idx < len(r) else np.asarray([],float)
    post_pos_frac=float(np.mean(post>0)) if len(post) else 0.5

    qn=max(1,int(math.ceil(0.25*len(r))))
    dr=float(np.sum(np.where(r<0,r*r,0.0)))
    out={
        "downside_share":dr/rv,
        "max_drawdown_norm":drawdown/scale,
        "trough_position":trough_position,
        "recovery_to_close_ratio":recovery_ratio,
        "close_location":(close-pmin)/span,
        "post_trough_return_norm":recovery/scale,
        "last_quarter_return_norm":float(np.sum(r[-qn:]))/scale,
        "post_trough_positive_fraction":post_pos_frac,
    }
    for k,v in out.items():
        if not math.isfinite(float(v)):
            raise RuntimeError(f"NONFINITE_MORPH:{k}")
    return out


def load_parent(path: Path):
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y=int(r["evaluation_year"])
            if y not in (2022,2023,2024,2025):
                continue
            out.append({
                "evaluation_year":y,
                "origin_date":r["origin_date"],
                "target_date":r["target_date"],
                "sqrt_alert":int(r["sqrt_high_risk_alert"]),
                "actual_up":int(float(r["target_close_return"])>0),
            })
    return out


def build_governed_router_rows(base, days):
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)
    return base.build_router_rows(trows,bmaps,lmaps,contexts)


def enrich_case(case, rets, source):
    z={
        "evaluation_year":int(case["evaluation_year"]),
        "origin_date":case["origin_date"],
        "target_date":case["target_date"],
        "actual_up":int(case["actual_up"]),
        "source":source,
        **morphology_features(rets),
    }
    return z


def feature_harmonization(ext_raw,gov_raw):
    vals={k:{"ext":[],"gov":[]} for k in FEATURES}
    common=[]
    trough_abs=[]
    for d in sorted(set(ext_raw)&set(gov_raw)):
        er=np.asarray(ext_raw[d]["rets"],float)
        gr=np.asarray(gov_raw[d],float)
        if len(er)<239 or len(gr)<239:
            continue
        if not (float(np.sum(er*er))>0 and float(np.sum(gr*gr))>0):
            continue
        ef=morphology_features(er)
        gf=morphology_features(gr)
        common.append(d)
        trough_abs.append(abs(ef["trough_position"]-gf["trough_position"]))
        for k in FEATURES:
            vals[k]["ext"].append(float(ef[k]))
            vals[k]["gov"].append(float(gf[k]))

    diag={}
    for k in FEATURES:
        diag[k]={
            "pearson":safe_corr(vals[k]["ext"],vals[k]["gov"]),
            "median_abs_diff":float(np.median(np.abs(np.asarray(vals[k]["ext"])-np.asarray(vals[k]["gov"])))) if common else None,
        }

    passed=bool(
        len(common)>=300
        and all(
            diag[k]["pearson"] is not None
            and diag[k]["pearson"] >= (0.85 if k=="post_trough_positive_fraction" else 0.90)
            for k in FEATURES
        )
        and float(np.median(trough_abs))<=0.05
    )
    return {
        "passed":passed,
        "overlap_n":len(common),
        "median_abs_trough_position_diff":float(np.median(trough_abs)) if common else None,
        "features":diag,
    }


def standardize_fit(train_rows):
    X=np.asarray([[r[k] for k in FEATURES] for r in train_rows],float)
    y=np.asarray([r["actual_up"] for r in train_rows],int)
    if len(np.unique(y))<2:
        raise RuntimeError("ONE_CLASS_TRAIN")
    mu=np.mean(X,axis=0)
    sd=np.std(X,axis=0,ddof=0)
    sd=np.where(sd<1e-12,1.0,sd)
    model=LogisticRegression(
        penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000
    )
    model.fit((X-mu)/sd,y)
    return model,mu,sd


def predict_rows(model,mu,sd,rows):
    X=np.asarray([[r[k] for k in FEATURES] for r in rows],float)
    return model.predict_proba((X-mu)/sd)[:,1]


def prequential_threshold(train_rows):
    rows=sorted(train_rows,key=lambda r:r["target_date"])
    cal=[]
    for i in range(MIN_PREQUENTIAL_HISTORY,len(rows)):
        prior=rows[:i]
        if len({r["actual_up"] for r in prior})<2:
            continue
        model,mu,sd=standardize_fit(prior)
        p=float(predict_rows(model,mu,sd,[rows[i]])[0])
        cal.append({
            "target_date":rows[i]["target_date"],
            "actual_up":rows[i]["actual_up"],
            "p_up":p,
        })
    down_scores=[r["p_up"] for r in cal if r["actual_up"]==0]
    if len(down_scores)<MIN_DOWN_CAL:
        return None,{
            "status":"BLOCKED_CALIBRATION_SUPPORT",
            "calibration_n":len(cal),
            "down_calibration_n":len(down_scores),
        }
    q80=nearest_rank(down_scores,0.80)
    tau=max(0.50,float(q80))
    return tau,{
        "status":"OK",
        "calibration_n":len(cal),
        "down_calibration_n":len(down_scores),
        "q80_down_prequential":float(q80),
        "tau":tau,
    }


def auc_safe(y,p):
    y=np.asarray(y,int)
    if len(np.unique(y))<2:
        return None
    return float(roc_auc_score(y,p))


def score_year(train,test,year):
    tau,cal=prequential_threshold(train)
    if tau is None:
        return [],{
            "status":"BLOCKED_CALIBRATION_SUPPORT",
            "year":year,
            "train_n":len(train),
            **cal,
        }
    model,mu,sd=standardize_fit(train)
    probs=predict_rows(model,mu,sd,test)
    scored=[]
    for r,p in zip(test,probs):
        z=dict(r)
        z["p_up"]=float(p)
        z["tau"]=float(tau)
        z["up2_morph_call"]=int(p>tau)
        scored.append(z)

    y=np.asarray([r["actual_up"] for r in scored],int)
    pred=np.asarray([r["up2_morph_call"] for r in scored],int)
    tp=int(np.sum((pred==1)&(y==1)))
    fp=int(np.sum((pred==1)&(y==0)))
    fn=int(np.sum((pred==0)&(y==1)))
    tn=int(np.sum((pred==0)&(y==0)))
    calls=tp+fp; au=tp+fn; ad=fp+tn

    return scored,{
        "status":"OK",
        "year":year,
        "n":len(scored),
        "actual_up":au,
        "actual_down":ad,
        "up2_morph_calls":calls,
        "true_up":tp,
        "false_up":fp,
        "missed_up":fn,
        "true_down_abstain":tn,
        "up_precision":tp/calls if calls else None,
        "missed_up_recall":tp/au if au else None,
        "false_up_fpr":fp/ad if ad else None,
        "coverage":calls/len(scored) if scored else None,
        "wilson90_lcb_up_precision":wilson_lcb(tp,calls),
        "auc":auc_safe(y,probs),
        "brier":float(np.mean((probs-y)**2)) if len(y) else None,
        "tau":float(tau),
        "train_n":len(train),
        "train_up":sum(r["actual_up"] for r in train),
        "train_down":sum(1-r["actual_up"] for r in train),
        "calibration":cal,
        "standardized_coefficients":{
            k:float(v) for k,v in zip(FEATURES,model.coef_[0])
        },
        "intercept":float(model.intercept_[0]),
    }


def pooled_metrics(rows):
    y=np.asarray([r["actual_up"] for r in rows],int)
    p=np.asarray([r["up2_morph_call"] for r in rows],int)
    prob=np.asarray([r["p_up"] for r in rows],float)
    tp=int(np.sum((p==1)&(y==1)))
    fp=int(np.sum((p==1)&(y==0)))
    fn=int(np.sum((p==0)&(y==1)))
    tn=int(np.sum((p==0)&(y==0)))
    calls=tp+fp; au=tp+fn; ad=fp+tn
    return {
        "n":len(rows),
        "actual_up":au,
        "actual_down":ad,
        "up2_morph_calls":calls,
        "true_up":tp,
        "false_up":fp,
        "missed_up":fn,
        "true_down_abstain":tn,
        "up_precision":tp/calls if calls else None,
        "missed_up_recall":tp/au if au else None,
        "false_up_fpr":fp/ad if ad else None,
        "coverage":calls/len(rows) if rows else None,
        "wilson90_lcb_up_precision":wilson_lcb(tp,calls),
        "auc":auc_safe(y,prob) if len(rows) else None,
        "brier":float(np.mean((prob-y)**2)) if len(rows) else None,
    }


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--pre-ledger",type=Path,required=True)
    ap.add_argument("--frozen-up2-v1-result",type=Path,required=True)
    ap.add_argument("--frozen-des-v1-result",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",args.route_module)
    cbr=load_mod("cbr_authority",args.cbr_code)
    sqrt_mod=route.load_sqrt_mod(args.sqrt_code)
    base=load_mod("base_authority",args.base_module)
    up2_v1=load_json(args.frozen_up2_v1_result)
    des_v1=load_json(args.frozen_des_v1_result)

    ext_spine=route.load_external_spine(args.external_spine)
    ext_raw=route.build_external_5m(args.raw_root)
    ext_audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]:
        raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")

    gov_raw=cbr.load_paths(["2020-01-02","2025-12-31"])
    gov_days=base.load_days()
    harmon=feature_harmonization(ext_raw,gov_raw)
    if not harmon["passed"]:
        result={
            "identity":IDENTITY,
            "status":"BLOCKED_SOURCE_OR_ROUTE_INTEGRITY",
            "integrity_errors":["MORPHOLOGY_HARMONIZATION_FAILED"],
            "external_reconstruction":ext_audit,
            "morphology_harmonization":harmon,
        }
        (args.out/"GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    ext_daily=route.load_external_daily_for_sqrt(ext_spine)
    ext_sqrt,ext_sqrt_summary=route.external_sqrt_cases(sqrt_mod,ext_daily)
    expected_sqrt={"2020":{"alarms":212,"down":97,"up":115},"2021":{"alarms":28,"down":16,"up":12}}
    if ext_sqrt_summary!=expected_sqrt:
        raise RuntimeError(f"EXTERNAL_SQRT_MISMATCH:{ext_sqrt_summary}")

    ext_router,ext_router_summary=route.external_router_rows(base,ext_spine)
    expected_router={
        "2020":{"n":260,"router_up":185,"tp":111,"fp":74},
        "2021":{"n":258,"router_up":33,"tp":19,"fp":14},
    }
    if ext_router_summary!=expected_router:
        raise RuntimeError(f"EXTERNAL_ROUTER_MISMATCH:{ext_router_summary}")

    ext_unresolved,ext_route_summary=route.route_external_sqrt_cases(ext_sqrt,ext_router)
    expected_route={
        "2020":{"sqrt_alarms":212,"router_up_overlap":140,"overlap_actual_up":80,"overlap_actual_down":60,
                "router_abstain":72,"abstain_actual_down":37,"abstain_actual_up":35},
        "2021":{"sqrt_alarms":28,"router_up_overlap":2,"overlap_actual_up":1,"overlap_actual_down":1,
                "router_abstain":26,"abstain_actual_down":15,"abstain_actual_up":11},
    }
    if ext_route_summary!=expected_route:
        raise RuntimeError(f"EXTERNAL_ROUTE_MISMATCH:{ext_route_summary}")

    external_cases=[
        enrich_case(r,ext_raw[r["origin_date"]]["rets"],"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN")
        for r in ext_unresolved
    ]
    if len(external_cases)!=98 or sum(r["actual_up"] for r in external_cases)!=46:
        raise RuntimeError("EXTERNAL_RESIDUAL_CASE_COUNT_FAIL")

    parent=load_parent(args.sqrt_parent)
    parent_map={(r["origin_date"],r["target_date"]):r for r in parent}
    gov_router=build_governed_router_rows(base,gov_days)
    gov_router_map={(r["origin_date"],r["target_date"]):r for r in gov_router}

    pre=route.load_pre_unresolved(args.pre_ledger)
    expected_pre={2022:(11,5),2023:(2,1),2024:(13,7)}
    for y,(n,u) in expected_pre.items():
        sub=[r for r in pre if int(r["evaluation_year"])==y]
        if len(sub)!=n or sum(int(r["actual_up"]) for r in sub)!=u:
            raise RuntimeError(f"PRE_ROUTE_MISMATCH:{y}")

    pre_cases=[]
    for r in pre:
        key=(r["origin_date"],r["target_date"])
        pr=parent_map.get(key); rr=gov_router_map.get(key)
        if pr is None or rr is None or int(rr["router_up"])!=0 or int(pr["sqrt_alert"])!=1:
            raise RuntimeError(f"GOV_PRE_ROUTE_JOIN_FAIL:{key}")
        pre_cases.append(enrich_case(r,gov_raw[r["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"))

    stress25=route.reconstruct_2025(base,args.sqrt_parent)
    if len(stress25)!=74 or sum(int(r["actual_up"]) for r in stress25)!=35:
        raise RuntimeError("LOCKED25_ROUTE_MISMATCH")

    stress_cases=[]
    for r in stress25:
        key=(r["origin_date"],r["target_date"])
        pr=parent_map.get(key); rr=gov_router_map.get(key)
        if pr is None or rr is None or int(rr["router_up"])!=0 or int(pr["sqrt_alert"])!=1:
            raise RuntimeError(f"GOV25_ROUTE_JOIN_FAIL:{key}")
        stress_cases.append(enrich_case(r,gov_raw[r["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"))

    all_hist=external_cases+pre_cases
    by_year={}
    scored_pre=[]
    blocked=False
    for year in (2022,2023,2024):
        train=[r for r in all_hist if int(r["evaluation_year"])<year]
        test=[r for r in pre_cases if int(r["evaluation_year"])==year]
        scored,m=score_year(train,test,year)
        by_year[str(year)]=m
        if m.get("status")!="OK":
            blocked=True
        scored_pre.extend(scored)

    if blocked:
        result={
            "identity":IDENTITY,
            "status":"BLOCKED_CALIBRATION_SUPPORT",
            "integrity_errors":[],
            "external_reconstruction":ext_audit,
            "morphology_harmonization":harmon,
            "external_sqrt_summary":ext_sqrt_summary,
            "external_router_summary":ext_router_summary,
            "external_route_summary":ext_route_summary,
            "by_year":by_year,
        }
        (args.out/"GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    pooled=pooled_metrics(scored_pre)
    pre_support=bool(
        pooled["n"]==26
        and pooled["up2_morph_calls"]>=4
        and pooled["up_precision"] is not None and pooled["up_precision"]>0.50
        and pooled["wilson90_lcb_up_precision"] is not None and pooled["wilson90_lcb_up_precision"]>0.50
        and pooled["false_up_fpr"] is not None and pooled["false_up_fpr"]<=0.25
    )

    train25=[r for r in all_hist if int(r["evaluation_year"])<=2024]
    scored25,m25=score_year(train25,stress_cases,2025)
    if m25.get("status")!="OK":
        transport=False
    else:
        transport=bool(
            m25["up2_morph_calls"]>=5
            and m25["up_precision"] is not None and m25["up_precision"]>(35/74)
            and m25["false_up_fpr"] is not None and m25["false_up_fpr"]<0.50
        )
    m25["residual_up_base_rate"]=35/74
    m25["transport_supportive"]=transport

    if pre_support and transport:
        status="RESIDUAL_TRAJECTORY_UP2_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT"
    elif pre_support:
        status="PRE2025_RESIDUAL_TRAJECTORY_UP2_SIGNAL_ONLY"
    else:
        status="RESIDUAL_TRAJECTORY_UP2_V1_NOT_SUPPORTED"

    v1pre=up2_v1["pooled_2022_2024"]
    v125=up2_v1["locked_2025"]
    despre=des_v1["pooled_2022_2024"]
    des25=des_v1["locked_2025"]
    comparison={
        "pooled_2022_2024":{
            "one_sided_logit_v1":{
                "calls":v1pre["up2_calls"],"precision":v1pre["up_precision"],
                "recall":v1pre["missed_up_recall"],"fpr":v1pre["false_up_fpr"],
                "coverage":v1pre["coverage"],
            },
            "local_des_v1":{
                "calls":despre["up2_des_calls"],"precision":despre["up_precision"],
                "recall":despre["missed_up_recall"],"fpr":despre["false_up_fpr"],
                "coverage":despre["coverage"],
            },
            "trajectory_morph_v1":{
                "calls":pooled["up2_morph_calls"],"precision":pooled["up_precision"],
                "recall":pooled["missed_up_recall"],"fpr":pooled["false_up_fpr"],
                "coverage":pooled["coverage"],
            },
        },
        "locked_2025":{
            "one_sided_logit_v1":{
                "calls":v125["up2_calls"],"precision":v125["up_precision"],
                "recall":v125["missed_up_recall"],"fpr":v125["false_up_fpr"],
                "coverage":v125["coverage"],
            },
            "local_des_v1":{
                "calls":des25["up2_des_calls"],"precision":des25["up_precision"],
                "recall":des25["missed_up_recall"],"fpr":des25["false_up_fpr"],
                "coverage":des25["coverage"],
            },
            "trajectory_morph_v1":{
                "calls":m25["up2_morph_calls"],"precision":m25["up_precision"],
                "recall":m25["missed_up_recall"],"fpr":m25["false_up_fpr"],
                "coverage":m25["coverage"],
            },
        },
        "note":"Descriptive only; no result-dependent hybrid is authorized."
    }

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":[],
        "method":{
            "features":FEATURES,
            "model":"L2 LogisticRegression C=1.0 lbfgs",
            "threshold":"max(0.50, nearest-rank q80 of strictly prequential historical DOWN scores)",
            "min_prequential_history":MIN_PREQUENTIAL_HISTORY,
            "min_down_calibration":MIN_DOWN_CAL,
            "output":["UP2_MORPH","ABSTAIN"],
        },
        "external_reconstruction":ext_audit,
        "morphology_harmonization":harmon,
        "external_sqrt_summary":ext_sqrt_summary,
        "external_router_summary":ext_router_summary,
        "external_route_summary":ext_route_summary,
        "route_counts":{
            "external_n":len(external_cases),
            "external_up":sum(r["actual_up"] for r in external_cases),
            "pre2025_n":len(pre_cases),
            "pre2025_up":sum(r["actual_up"] for r in pre_cases),
            "locked2025_n":len(stress_cases),
            "locked2025_up":sum(r["actual_up"] for r in stress_cases),
        },
        "by_year_2022_2024":by_year,
        "pooled_2022_2024":pooled,
        "pre2025_supportive":pre_support,
        "locked_2025":m25,
        "comparison_to_prior_residual_up2_methods":comparison,
        "governance":{
            "random_split":False,
            "feature_or_hyperparameter_sweep":False,
            "target_year_tuning":False,
            "2025_used_for_selection":False,
            "2026_used":False,
            "automatic_ensemble":False,
            "production_writes":False,
            "runtime_promotion":False,
        }
    }

    (args.out/"GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESULT_2026-09-23.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8"
    )

    ledger=scored_pre+scored25
    fields=[
        "evaluation_year","origin_date","target_date","source","actual_up",
        *FEATURES,"p_up","tau","up2_morph_call"
    ]
    with (args.out/"GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in ledger:
            w.writerow({k:r.get(k,"") for k in fields})

    lines=[
        "# GOLD CONTROL — RESIDUAL TRAJECTORY / REBOUND MORPHOLOGY UP-2 V1 RESULT","",
        f"**Status:** `{status}`  ","",
        "## Pre-2025 chronological results","",
        "| Year | n | Train n | Calls | True UP | False UP | Precision | Recall | FPR | AUC | Tau |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for y in ("2022","2023","2024"):
        m=by_year[y]
        lines.append(
            f"| {y} | {m['n']} | {m['train_n']} | {m['up2_morph_calls']} | {m['true_up']} | "
            f"{m['false_up']} | {m['up_precision']} | {m['missed_up_recall']} | {m['false_up_fpr']} | "
            f"{m['auc']} | {m['tau']} |"
        )
    lines += [
        "",
        f"Pooled 2022–2024: n={pooled['n']}, calls={pooled['up2_morph_calls']}, true UP={pooled['true_up']}, "
        f"false UP={pooled['false_up']}, precision={pooled['up_precision']}, recall={pooled['missed_up_recall']}, "
        f"FPR={pooled['false_up_fpr']}, Wilson90 LCB={pooled['wilson90_lcb_up_precision']}, AUC={pooled['auc']}.",
        "",
        "## Locked 2025 transport","",
        f"n={m25.get('n')}; calls={m25.get('up2_morph_calls')}; true UP={m25.get('true_up')}; false UP={m25.get('false_up')}; "
        f"precision={m25.get('up_precision')}; recall={m25.get('missed_up_recall')}; FPR={m25.get('false_up_fpr')}; "
        f"AUC={m25.get('auc')}; tau={m25.get('tau')}; supportive={transport}.",
        "",
        "No random split, feature sweep, threshold sweep, 2025 tuning or 2026 use."
    ]
    (args.out/"GOLD_CONTROL_RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESULT_2026-09-23.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8"
    )

    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
