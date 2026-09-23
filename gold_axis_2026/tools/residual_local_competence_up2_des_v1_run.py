from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

IDENTITY = "RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESEARCH"
FEATURES = [
    "sqrt_score",
    "lag1_close_return",
    "downside_share",
    "intraday_end_norm",
    "close_location",
    "trough_recovery_norm",
    "last_quarter_return_norm",
    "direct_up_fraction",
    "legacy_up_fraction",
]
EXPERTS = [
    "TTSM_S2",
    "TTSM_S1",
    "BONATO_AR1_RM_QBOOST_H1",
    "AR1_RM_LOGIT",
    "RM_LOGIT",
]
TIE_ORDER = {e:i for i,e in enumerate(EXPERTS)}
K_NEIGHBORS = 25
MIN_LOCAL_CALLS = 5
Z90 = 1.2815515655446004


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


def safe_corr(x, y):
    a=np.asarray(x,float); b=np.asarray(y,float)
    if len(a)<2:
        return None
    sa=float(np.std(a)); sb=float(np.std(b))
    if sa<=1e-15 or sb<=1e-15:
        return 1.0 if np.allclose(a,b,atol=1e-12,rtol=0) else 0.0
    return float(np.corrcoef(a,b)[0,1])


def raw_path_features(rets):
    r=np.asarray(rets,float)
    if len(r)<239:
        raise RuntimeError(f"TOO_FEW_RETURNS:{len(r)}")
    rv=float(np.sum(r*r))
    if not (rv>0):
        raise RuntimeError("ZERO_RV")
    scale=math.sqrt(rv)
    cum=np.cumsum(r)
    cmin=float(np.min(cum)); cmax=float(np.max(cum)); cend=float(cum[-1])
    span=cmax-cmin
    qn=max(1,int(math.ceil(0.25*len(r))))
    dr=float(np.sum(np.where(r<0,r*r,0.0)))
    return {
        "downside_share":dr/rv,
        "intraday_end_norm":cend/scale,
        "close_location":(cend-cmin)/span if span>1e-15 else 0.5,
        "trough_recovery_norm":(cend-cmin)/scale,
        "last_quarter_return_norm":float(np.sum(r[-qn:]))/scale,
    }


def lag_map_from_spine(spine):
    rows=sorted(spine,key=lambda r:r["date"])
    out={}
    prev=None
    for r in rows:
        if prev is not None and prev>0 and r["close"]>0:
            out[r["date"]]=math.log(r["close"]/prev)
        prev=r["close"]
    return out


def lag_map_from_base_days(days):
    out={}
    prev=None
    for d in days:
        if prev is not None and prev>0 and d.close>0:
            out[d.d.isoformat()]=math.log(d.close/prev)
        prev=d.close
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
                "sqrt_score":float(r["sqrt_normalized_risk_score"]),
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


def enrich_case(case, sqrt_score, router_row, lag1, rets, source):
    pf=raw_path_features(rets)
    direct_count=sum(int(router_row[k]) for k in EXPERTS)
    z={
        "evaluation_year":int(case["evaluation_year"]),
        "origin_date":case["origin_date"],
        "target_date":case["target_date"],
        "actual_up":int(case["actual_up"]),
        "source":source,
        "sqrt_score":float(sqrt_score),
        "lag1_close_return":float(lag1),
        **pf,
        "direct_up_fraction":direct_count/5.0,
        "legacy_up_fraction":int(router_row["legacy_up_count"])/3.0,
    }
    for e in EXPERTS:
        z[e]=int(router_row[e])
    for k in FEATURES:
        if not math.isfinite(float(z[k])):
            raise RuntimeError(f"NONFINITE_FEATURE:{k}:{z['origin_date']}")
    return z


def feature_harmonization(ext_raw,ext_spine,gov_raw,gov_days):
    ext_lag=lag_map_from_spine(ext_spine)
    gov_lag=lag_map_from_base_days(gov_days)
    names=[
        "lag1_close_return","downside_share","intraday_end_norm",
        "close_location","trough_recovery_norm","last_quarter_return_norm"
    ]
    common=[]
    vals={k:{"ext":[],"gov":[]} for k in names}
    for d in sorted(set(ext_raw)&set(gov_raw)&set(ext_lag)&set(gov_lag)):
        er=np.asarray(ext_raw[d]["rets"],float)
        gr=np.asarray(gov_raw[d],float)
        if len(er)<239 or len(gr)<239:
            continue
        if not (float(np.sum(er*er))>0 and float(np.sum(gr*gr))>0):
            continue
        ef=raw_path_features(er); gf=raw_path_features(gr)
        ef["lag1_close_return"]=ext_lag[d]
        gf["lag1_close_return"]=gov_lag[d]
        common.append(d)
        for k in names:
            vals[k]["ext"].append(float(ef[k]))
            vals[k]["gov"].append(float(gf[k]))
    diag={}
    for k in names:
        diag[k]={
            "pearson":safe_corr(vals[k]["ext"],vals[k]["gov"]),
            "median_abs_diff":float(np.median(np.abs(np.asarray(vals[k]["ext"])-np.asarray(vals[k]["gov"])))) if common else None,
        }
    sign_agree=float(np.mean(
        np.sign(vals["lag1_close_return"]["ext"])==np.sign(vals["lag1_close_return"]["gov"])
    )) if common else None
    passed=bool(
        len(common)>=300
        and sign_agree is not None and sign_agree>=0.90
        and all(diag[k]["pearson"] is not None and diag[k]["pearson"]>=0.90 for k in names)
    )
    return {
        "passed":passed,
        "overlap_n":len(common),
        "lag1_sign_agreement":sign_agree,
        "features":diag,
    }


def standardization(train):
    X=np.asarray([[r[k] for k in FEATURES] for r in train],float)
    mu=np.mean(X,axis=0)
    sd=np.std(X,axis=0,ddof=0)
    sd=np.where(sd<1e-12,1.0,sd)
    return mu,sd


def local_neighbors(train,row,mu,sd):
    X=np.asarray([[r[k] for k in FEATURES] for r in train],float)
    x=np.asarray([row[k] for k in FEATURES],float)
    d=np.sqrt(np.sum(((X-mu)/sd - (x-mu)/sd)**2,axis=1))
    order=np.argsort(d,kind="mergesort")[:min(K_NEIGHBORS,len(train))]
    out=[]
    for i in order:
        z=dict(train[int(i)])
        z["_distance"]=float(d[int(i)])
        out.append(z)
    return out


def expert_local_stats(neighbors,expert):
    calls=[r for r in neighbors if int(r[expert])==1]
    n=len(calls)
    if n==0:
        return None
    tp=sum(int(r["actual_up"])==1 for r in calls)
    fp=n-tp
    actual_down=sum(int(r["actual_up"])==0 for r in neighbors)
    precision=tp/n
    fpr=fp/actual_down if actual_down else 1.0
    return {
        "local_calls":n,
        "tp":tp,
        "fp":fp,
        "precision":precision,
        "fpr":fpr,
        "lcb":wilson_lcb(tp,n),
    }


def score_one(train,row,mu,sd):
    neigh=local_neighbors(train,row,mu,sd)
    eligible=[]
    candidates={}
    for e in EXPERTS:
        if int(row[e])!=1:
            continue
        st=expert_local_stats(neigh,e)
        candidates[e]=st
        if st is None:
            continue
        if st["local_calls"] < MIN_LOCAL_CALLS:
            continue
        if st["precision"] <= 0.50:
            continue
        if st["fpr"] >= 0.50:
            continue
        if st["lcb"] is None or st["lcb"] <= 0.50:
            continue
        eligible.append((e,st))
    if eligible:
        eligible.sort(key=lambda x:(
            -x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],TIE_ORDER[x[0]]
        ))
        selected,st=eligible[0]
        call=1
    else:
        selected=""
        st=None
        call=0
    provenance=Counter(f"{r['source']}:{r['evaluation_year']}" for r in neigh)
    return {
        "up2_des_call":call,
        "selected_expert":selected,
        "selected_local_calls":None if st is None else st["local_calls"],
        "selected_local_precision":None if st is None else st["precision"],
        "selected_local_fpr":None if st is None else st["fpr"],
        "selected_local_lcb":None if st is None else st["lcb"],
        "mean_neighbor_distance":float(np.mean([r["_distance"] for r in neigh])),
        "neighbor_provenance":dict(provenance),
        "current_up_experts":[e for e in EXPERTS if int(row[e])==1],
        "candidate_local_stats":candidates,
    }


def metrics(rows):
    y=np.asarray([r["actual_up"] for r in rows],int)
    p=np.asarray([r["up2_des_call"] for r in rows],int)
    tp=int(np.sum((p==1)&(y==1)))
    fp=int(np.sum((p==1)&(y==0)))
    fn=int(np.sum((p==0)&(y==1)))
    tn=int(np.sum((p==0)&(y==0)))
    calls=tp+fp; au=tp+fn; ad=fp+tn
    selected=[r for r in rows if r["up2_des_call"]==1]
    return {
        "n":len(rows),
        "actual_up":au,
        "actual_down":ad,
        "up2_des_calls":calls,
        "true_up":tp,
        "false_up":fp,
        "missed_up":fn,
        "true_down_abstain":tn,
        "up_precision":tp/calls if calls else None,
        "missed_up_recall":tp/au if au else None,
        "false_up_fpr":fp/ad if ad else None,
        "coverage":calls/len(rows) if rows else None,
        "wilson90_lcb_up_precision":wilson_lcb(tp,calls),
        "selected_expert_counts":dict(Counter(r["selected_expert"] for r in selected)),
        "mean_selected_local_calls":float(np.mean([r["selected_local_calls"] for r in selected])) if selected else None,
        "mean_selected_local_precision":float(np.mean([r["selected_local_precision"] for r in selected])) if selected else None,
        "mean_selected_local_fpr":float(np.mean([r["selected_local_fpr"] for r in selected])) if selected else None,
        "mean_selected_local_lcb":float(np.mean([r["selected_local_lcb"] for r in selected])) if selected else None,
        "mean_neighbor_distance":float(np.mean([r["mean_neighbor_distance"] for r in rows])) if rows else None,
    }


def score_year(train,test,year):
    if len(train)<K_NEIGHBORS:
        raise RuntimeError(f"TRAIN_TOO_SMALL:{year}:{len(train)}")
    mu,sd=standardization(train)
    scored=[]
    for row in test:
        z=dict(row)
        z.update(score_one(train,row,mu,sd))
        scored.append(z)
    m=metrics(scored)
    m.update({
        "year":year,
        "train_n":len(train),
        "train_up":sum(r["actual_up"] for r in train),
        "train_down":sum(1-r["actual_up"] for r in train),
        "k_neighbors":K_NEIGHBORS,
        "min_local_calls":MIN_LOCAL_CALLS,
    })
    return scored,m


def load_frozen_v1(path: Path):
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
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",args.route_module)
    cbr=load_mod("cbr_authority",args.cbr_code)
    sqrt_mod=route.load_sqrt_mod(args.sqrt_code)
    base=load_mod("base_authority",args.base_module)
    frozen_v1=load_frozen_v1(args.frozen_up2_v1_result)

    ext_spine=route.load_external_spine(args.external_spine)
    ext_raw=route.build_external_5m(args.raw_root)
    ext_audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]:
        raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")

    gov_raw=cbr.load_paths(["2020-01-02","2025-12-31"])
    gov_days=base.load_days()
    raw_harmon=feature_harmonization(ext_raw,ext_spine,gov_raw,gov_days)
    if not raw_harmon["passed"]:
        result={
            "identity":IDENTITY,
            "status":"BLOCKED_SOURCE_OR_ROUTE_INTEGRITY",
            "integrity_errors":["RAW_FEATURE_HARMONIZATION_FAILED"],
            "external_reconstruction":ext_audit,
            "raw_feature_harmonization":raw_harmon,
        }
        (args.out/"GOLD_CONTROL_RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
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

    ext_router_map={(r["origin_date"],r["target_date"]):r for r in ext_router}
    ext_sqrt_map={(r["origin_date"],r["target_date"]):r for r in ext_sqrt}
    ext_lag=lag_map_from_spine(ext_spine)
    external_cases=[]
    for r in ext_unresolved:
        key=(r["origin_date"],r["target_date"])
        rr=ext_router_map[key]; sr=ext_sqrt_map[key]
        external_cases.append(enrich_case(
            r,sr["sqrt_normalized_risk_score"],rr,ext_lag[r["origin_date"]],
            ext_raw[r["origin_date"]]["rets"],"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"
        ))
    if len(external_cases)!=98 or sum(r["actual_up"] for r in external_cases)!=46:
        raise RuntimeError("EXTERNAL_RESIDUAL_CASE_COUNT_FAIL")

    parent=load_parent(args.sqrt_parent)
    parent_map={(r["origin_date"],r["target_date"]):r for r in parent}
    gov_router=build_governed_router_rows(base,gov_days)
    gov_router_map={(r["origin_date"],r["target_date"]):r for r in gov_router}
    gov_lag=lag_map_from_base_days(gov_days)

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
        if pr is None or rr is None or int(rr["router_up"])!=0:
            raise RuntimeError(f"GOV_PRE_ROUTE_JOIN_FAIL:{key}")
        pre_cases.append(enrich_case(
            r,pr["sqrt_score"],rr,gov_lag[r["origin_date"]],
            gov_raw[r["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"
        ))

    stress25=route.reconstruct_2025(base,args.sqrt_parent)
    if len(stress25)!=74 or sum(int(r["actual_up"]) for r in stress25)!=35:
        raise RuntimeError("LOCKED25_ROUTE_MISMATCH")
    stress_cases=[]
    for r in stress25:
        key=(r["origin_date"],r["target_date"])
        pr=parent_map.get(key); rr=gov_router_map.get(key)
        if pr is None or rr is None or int(rr["router_up"])!=0:
            raise RuntimeError(f"GOV25_ROUTE_JOIN_FAIL:{key}")
        stress_cases.append(enrich_case(
            r,pr["sqrt_score"],rr,gov_lag[r["origin_date"]],
            gov_raw[r["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"
        ))

    all_hist=external_cases+pre_cases
    by_year={}
    scored_pre=[]
    provenance_pre=Counter()
    for year in (2022,2023,2024):
        train=[r for r in all_hist if int(r["evaluation_year"])<year]
        test=[r for r in pre_cases if int(r["evaluation_year"])==year]
        scored,m=score_year(train,test,year)
        by_year[str(year)]=m
        scored_pre.extend(scored)
        for r in scored:
            provenance_pre.update(r["neighbor_provenance"])

    pooled=metrics(scored_pre)
    pre_support=bool(
        pooled["n"]==26
        and pooled["up2_des_calls"]>=4
        and pooled["up_precision"] is not None and pooled["up_precision"]>0.50
        and pooled["wilson90_lcb_up_precision"] is not None and pooled["wilson90_lcb_up_precision"]>0.50
        and pooled["false_up_fpr"] is not None and pooled["false_up_fpr"]<=0.25
    )

    train25=[r for r in all_hist if int(r["evaluation_year"])<=2024]
    scored25,m25=score_year(train25,stress_cases,2025)
    transport_support=bool(
        m25["up2_des_calls"]>=5
        and m25["up_precision"] is not None and m25["up_precision"]>(35/74)
        and m25["false_up_fpr"] is not None and m25["false_up_fpr"]<0.50
    )
    m25["residual_up_base_rate"]=35/74
    m25["transport_supportive"]=transport_support

    if pre_support and transport_support:
        status="RESIDUAL_LOCAL_DES_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT"
    elif pre_support:
        status="PRE2025_RESIDUAL_LOCAL_DES_SIGNAL_ONLY"
    else:
        status="RESIDUAL_LOCAL_DES_V1_NOT_SUPPORTED"

    v1pre=frozen_v1["pooled_2022_2024"]
    v125=frozen_v1["locked_2025"]
    comparison={
        "pooled_2022_2024":{
            "one_sided_logit_v1":{
                "calls":v1pre["up2_calls"],
                "precision":v1pre["up_precision"],
                "recall":v1pre["missed_up_recall"],
                "fpr":v1pre["false_up_fpr"],
                "coverage":v1pre["coverage"],
            },
            "local_des_v1":{
                "calls":pooled["up2_des_calls"],
                "precision":pooled["up_precision"],
                "recall":pooled["missed_up_recall"],
                "fpr":pooled["false_up_fpr"],
                "coverage":pooled["coverage"],
            },
        },
        "locked_2025":{
            "one_sided_logit_v1":{
                "calls":v125["up2_calls"],
                "precision":v125["up_precision"],
                "recall":v125["missed_up_recall"],
                "fpr":v125["false_up_fpr"],
                "coverage":v125["coverage"],
            },
            "local_des_v1":{
                "calls":m25["up2_des_calls"],
                "precision":m25["up_precision"],
                "recall":m25["missed_up_recall"],
                "fpr":m25["false_up_fpr"],
                "coverage":m25["coverage"],
            },
        },
        "note":"Descriptive only; no hybrid/ensemble/winner-selection rule is authorized."
    }

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":[],
        "method":{
            "candidate_experts":EXPERTS,
            "context_features":FEATURES,
            "k_neighbors":K_NEIGHBORS,
            "min_local_calls":MIN_LOCAL_CALLS,
            "eligibility":"current expert UP AND local_calls>=5 AND precision>0.50 AND FPR<0.50 AND Wilson90 LCB>0.50",
            "selection":"highest LCB, lower FPR, higher precision, fixed expert order",
            "global_fallback":False,
            "output":["UP2_DES","ABSTAIN"],
        },
        "external_reconstruction":ext_audit,
        "raw_feature_harmonization":raw_harmon,
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
        "pooled_neighbor_provenance":dict(provenance_pre),
        "locked_2025":m25,
        "comparison_to_frozen_one_sided_logit_v1":comparison,
        "governance":{
            "random_split":False,
            "k_or_hyperparameter_sweep":False,
            "target_year_tuning":False,
            "2025_used_for_selection":False,
            "2026_used":False,
            "automatic_ensemble":False,
            "production_writes":False,
            "runtime_promotion":False,
        }
    }

    (args.out/"GOLD_CONTROL_RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESULT_2026-09-23.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8"
    )

    ledger=scored_pre+scored25
    fields=[
        "evaluation_year","origin_date","target_date","source","actual_up",
        *FEATURES,*EXPERTS,
        "up2_des_call","selected_expert","selected_local_calls",
        "selected_local_precision","selected_local_fpr","selected_local_lcb",
        "mean_neighbor_distance","current_up_experts","neighbor_provenance","candidate_local_stats"
    ]
    with (args.out/"GOLD_CONTROL_RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in ledger:
            z={k:r.get(k,"") for k in fields}
            for k in ("current_up_experts","neighbor_provenance","candidate_local_stats"):
                z[k]=json.dumps(z[k],sort_keys=True)
            w.writerow(z)

    lines=[
        "# GOLD CONTROL — RESIDUAL LOCAL-COMPETENCE UP-2 DES V1 RESULT","",
        f"**Status:** `{status}`  ","",
        "## Pre-2025 chronological results","",
        "| Year | n | Train n | Calls | True UP | False UP | Precision | Recall | FPR | Selected experts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for y in ("2022","2023","2024"):
        m=by_year[y]
        lines.append(
            f"| {y} | {m['n']} | {m['train_n']} | {m['up2_des_calls']} | {m['true_up']} | "
            f"{m['false_up']} | {m['up_precision']} | {m['missed_up_recall']} | "
            f"{m['false_up_fpr']} | {json.dumps(m['selected_expert_counts'],sort_keys=True)} |"
        )
    lines += [
        "",
        f"Pooled 2022–2024: n={pooled['n']}, calls={pooled['up2_des_calls']}, true UP={pooled['true_up']}, "
        f"false UP={pooled['false_up']}, precision={pooled['up_precision']}, recall={pooled['missed_up_recall']}, "
        f"FPR={pooled['false_up_fpr']}, Wilson90 LCB={pooled['wilson90_lcb_up_precision']}.",
        "",
        "## Locked 2025 transport","",
        f"n={m25['n']}; calls={m25['up2_des_calls']}; true UP={m25['true_up']}; false UP={m25['false_up']}; "
        f"precision={m25['up_precision']}; recall={m25['missed_up_recall']}; FPR={m25['false_up_fpr']}; "
        f"supportive={transport_support}.",
        "",
        "## Descriptive comparison to frozen One-Sided Logit V1","",
        f"`{json.dumps(comparison,sort_keys=True)}`","",
        "No random split, K sweep, 2025 tuning, automatic ensemble or 2026 use."
    ]
    (args.out/"GOLD_CONTROL_RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESULT_2026-09-23.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8"
    )

    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
