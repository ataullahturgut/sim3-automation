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

IDENTITY="UP2_REGIME_CONDITIONED_FAILURE_DETECTOR_V1_RESEARCH"
FEATURES=["last_hour_trend_r2","sqrt_score","late_downside_intensity"]


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


def build_rows(ledger,paths,mech):
    rows=[]; errs=[]
    for r in ledger:
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025):
            continue
        if int(r["up2_call"])!=1:
            continue
        od=r["origin_date"]
        if od not in paths:
            errs.append(f"PATH_MISSING:{od}")
            continue
        mf=mech.features(paths[od])
        actual_up=int(r["actual_up"])
        z={
            "evaluation_year":y,
            "origin_date":od,
            "target_date":r["target_date"],
            "actual_up":actual_up,
            "failure":1-actual_up,
            "last_hour_trend_r2":float(mf["last_hour_trend_r2"]),
            "sqrt_score":float(r["sqrt_score"]),
            "late_downside_intensity":float(mf["late_downside_intensity"]),
        }
        for f in FEATURES:
            if not math.isfinite(z[f]):
                errs.append(f"NONFINITE:{od}:{f}")
        rows.append(z)
    return rows,errs


def fit_model(rows):
    X=np.asarray([[r[f] for f in FEATURES] for r in rows],float)
    y=np.asarray([r["failure"] for r in rows],int)
    if set(y.tolist())!={0,1}:
        raise RuntimeError("TRAIN_ONE_CLASS")
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=0)
    sd=np.where(sd<1e-12,1.0,sd)
    Xs=(X-mu)/sd
    model=LogisticRegression(
        penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000
    )
    model.fit(Xs,y)
    return model,mu,sd


def score_rows(model,mu,sd,rows):
    if not rows:
        return []
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


def summary(rows):
    safe=[r for r in rows if r["failure"]==0]
    fail=[r for r in rows if r["failure"]==1]
    veto=[r for r in rows if r["veto"]==1]
    safe_lost=sum(r["failure"]==0 for r in veto)
    fail_removed=sum(r["failure"]==1 for r in veto)
    safe_keep=len(safe)-safe_lost
    fail_keep=len(fail)-fail_removed
    before_prec=len(safe)/len(rows) if rows else None
    after_n=safe_keep+fail_keep
    after_prec=safe_keep/after_n if after_n else None
    return {
        "n":len(rows),
        "captured_up":len(safe),
        "false_up_actual_down":len(fail),
        "vetoes":len(veto),
        "false_up_removed":fail_removed,
        "false_up_remaining":fail_keep,
        "captured_up_lost":safe_lost,
        "captured_up_retained":safe_keep,
        "captured_up_retention_rate":safe_keep/len(safe) if safe else None,
        "false_up_removal_rate":fail_removed/len(fail) if fail else None,
        "precision_before":before_prec,
        "precision_after":after_prec,
        "remaining_calls":after_n,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--up2-ledger",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--mechanism-code",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    cbr=load_mod("cbr_authority",a.cbr_code)
    mech=load_mod("mech_authority",a.mechanism_code)
    paths=cbr.load_paths(["2022-01-01","2025-12-31"])
    rows,errs=build_rows(read_csv(a.up2_ledger),paths,mech)

    train=[r for r in rows if r["evaluation_year"]==2022]
    y23=[r for r in rows if r["evaluation_year"]==2023]
    y24=[r for r in rows if r["evaluation_year"]==2024]
    y25=[r for r in rows if r["evaluation_year"]==2025]

    def count_pair(rr):
        return (len(rr),sum(r["failure"]==0 for r in rr),sum(r["failure"]==1 for r in rr))

    if count_pair(train)!=(7,4,3):
        errs.append(f"TRAIN_COUNTS:{count_pair(train)}")
    if count_pair(y23)!=(1,1,0):
        errs.append(f"Y23_COUNTS:{count_pair(y23)}")
    if count_pair(y24)!=(3,3,0):
        errs.append(f"Y24_COUNTS:{count_pair(y24)}")
    if count_pair(y25)!=(25,13,12):
        errs.append(f"Y25_COUNTS:{count_pair(y25)}")

    if errs:
        result={"identity":IDENTITY,"status":"BLOCKED_INTEGRITY","integrity_errors":errs}
        (a.out/"GOLD_CONTROL_UP2_REGIME_CONDITIONED_FAILURE_DETECTOR_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    model,mu,sd=fit_model(train)
    s22=score_rows(model,mu,sd,train)
    s23=score_rows(model,mu,sd,y23)
    s24=score_rows(model,mu,sd,y24)
    s25=score_rows(model,mu,sd,y25)
    s2324=s23+s24

    m22=summary(s22)
    m23=summary(s23)
    m24=summary(s24)
    m2324=summary(s2324)
    m25=summary(s25)

    forward_guard=(m2324["captured_up_retained"]>=3)
    transport=(
        m25["false_up_removed"]>=3
        and m25["captured_up_retained"]>=10
    )

    if not forward_guard:
        status="FAILURE_DETECTOR_V1_NOT_SUPPORTED"
    elif transport:
        status="TRANSPORT_SIGNAL_SAMPLE_LIMITED_NOT_CERTIFIED"
    else:
        status="FORWARD_RETENTION_OK_TRANSPORT_NOT_SUPPORTED"

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":[],
        "method":{
            "target":"1 = FALSE_UP_ACTUAL_DOWN, 0 = CAPTURED_UP",
            "features":FEATURES,
            "model":"L2 LogisticRegression C=1.0 lbfgs",
            "training_period":"2022 only",
            "veto_threshold":0.50,
            "veto_semantics":"VETO -> ABSTAIN, never DOWN",
        },
        "training_2022":m22,
        "forward_guard_2023":m23,
        "forward_guard_2024":m24,
        "forward_guard_2023_2024":m2324,
        "locked_2025":m25,
        "forward_guard_passed":forward_guard,
        "locked_2025_transport_supportive":transport,
        "training_standardization":{
            "mean":{f:float(v) for f,v in zip(FEATURES,mu)},
            "std":{f:float(v) for f,v in zip(FEATURES,sd)},
        },
        "standardized_coefficients":{
            f:float(v) for f,v in zip(FEATURES,model.coef_[0])
        },
        "intercept":float(model.intercept_[0]),
        "governance":{
            "random_split":False,
            "hyperparameter_search":False,
            "threshold_search":False,
            "2025_used_for_training_or_tuning":False,
            "2026_used":False,
            "runtime_promotion":False,
            "certified":False,
        }
    }

    (a.out/"GOLD_CONTROL_UP2_REGIME_CONDITIONED_FAILURE_DETECTOR_V1_RESULT_2026-09-23.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8"
    )

    fields=[
        "evaluation_year","origin_date","target_date","actual_up","failure",
        *FEATURES,"p_fail","veto","keep_up"
    ]
    with (a.out/"GOLD_CONTROL_UP2_REGIME_CONDITIONED_FAILURE_DETECTOR_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in s22+s23+s24+s25:
            w.writerow({k:r.get(k,"") for k in fields})

    lines=[
        "# GOLD CONTROL — UP-2 REGIME-CONDITIONED FAILURE DETECTOR V1","",
        f"**Status:** `{status}`","",
        "## Model","",
        f"Features: {FEATURES}  ",
        "Training: 2022 UP-2 calls only. Veto if p_fail >= 0.50. Veto -> ABSTAIN.","",
        "| Period | Calls | False UP removed | True UP retained | Precision before | Precision after |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for label,m in [("2022 train",m22),("2023",m23),("2024",m24),("2023-24 guard",m2324),("2025 locked",m25)]:
        pb="" if m["precision_before"] is None else f"{100*m['precision_before']:.1f}%"
        pa="" if m["precision_after"] is None else f"{100*m['precision_after']:.1f}%"
        lines.append(
            f"| {label} | {m['n']} | {m['false_up_removed']}/{m['false_up_actual_down']} | "
            f"{m['captured_up_retained']}/{m['captured_up']} | {pb} | {pa} |"
        )
    lines += [
        "",
        f"Standardized coefficients: `{json.dumps(result['standardized_coefficients'],sort_keys=True)}`",
        "",
        "Sample-limited research only. The pre-2025 forward guard has no false-UP cases, so this experiment cannot certify a failure detector."
    ]
    (a.out/"GOLD_CONTROL_UP2_REGIME_CONDITIONED_FAILURE_DETECTOR_V1_RESULT_2026-09-23.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8"
    )

    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
