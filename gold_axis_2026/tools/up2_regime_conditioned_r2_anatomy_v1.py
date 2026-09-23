from __future__ import annotations

import argparse, csv, importlib.util, json, math, sys
from pathlib import Path
import numpy as np

IDENTITY="UP2_REGIME_CONDITIONED_R2_ANATOMY_V1_RESEARCH"
R2_THRESHOLD=0.50
AXES=["sqrt_score","rv60_ratio","downside_share","late_downside_intensity","lag1_close_return"]


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


def median(xs):
    return float(np.median(np.asarray(xs,float)))


def classify(actual):
    return "CAPTURED_UP" if actual==1 else "FALSE_UP_ACTUAL_DOWN"


def eval_rule(rows,axis,cut,side):
    def cond(r):
        return r[axis] >= cut if side=="HIGH" else r[axis] < cut
    veto=[r for r in rows if r["r2"]>=R2_THRESHOLD and cond(r)]
    cap=[r for r in rows if r["actual_up"]==1]
    fp=[r for r in rows if r["actual_up"]==0]
    cap_lost=sum(r in veto for r in cap)
    fp_removed=sum(r in veto for r in fp)
    cap_keep=len(cap)-cap_lost
    fp_keep=len(fp)-fp_removed
    rem=cap_keep+fp_keep
    return {
        "axis":axis,"side":side,"cutpoint":cut,
        "regime_n":sum(cond(r) for r in rows),
        "veto_n":len(veto),
        "false_up_removed":fp_removed,
        "false_up_total":len(fp),
        "false_up_removal_rate":fp_removed/len(fp) if fp else None,
        "captured_up_lost":cap_lost,
        "captured_up_retained":cap_keep,
        "captured_up_total":len(cap),
        "captured_up_retention_rate":cap_keep/len(cap) if cap else None,
        "remaining_calls":rem,
        "remaining_precision":cap_keep/rem if rem else None,
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
    led=read_csv(a.up2_ledger)

    paths=cbr.load_paths(["2021-01-01","2025-12-31"])
    all_dates=sorted(paths)
    rv={d:float(np.sum(np.asarray(paths[d],float)**2)) for d in all_dates}
    idx={d:i for i,d in enumerate(all_dates)}

    rows=[]; errs=[]
    for r in led:
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025) or int(r["up2_call"])!=1:
            continue
        od=r["origin_date"]
        if od not in paths:
            errs.append(f"PATH_MISSING:{od}"); continue
        i=idx[od]
        prev=all_dates[max(0,i-60):i]
        if len(prev)<40:
            errs.append(f"RV60_HISTORY_SHORT:{od}:{len(prev)}"); continue
        medrv=median([rv[d] for d in prev])
        feat=mech.features(paths[od])
        row={
            "evaluation_year":y,
            "origin_date":od,
            "target_date":r["target_date"],
            "actual_up":int(r["actual_up"]),
            "group":classify(int(r["actual_up"])),
            "r2":float(feat["last_hour_trend_r2"]),
            "sqrt_score":float(r["sqrt_score"]),
            "rv60_ratio":rv[od]/medrv if medrv>0 else 0.0,
            "downside_share":float(r["downside_share"]),
            "late_downside_intensity":float(feat["late_downside_intensity"]),
            "lag1_close_return":float(r["lag1_close_return"]),
        }
        if not all(math.isfinite(float(row[k])) for k in ["r2",*AXES]):
            errs.append(f"NONFINITE:{od}")
        rows.append(row)

    pre=[r for r in rows if r["evaluation_year"]<=2024]
    y25=[r for r in rows if r["evaluation_year"]==2025]
    if (len(pre),sum(r["actual_up"] for r in pre))!=(11,8):
        errs.append(f"PRE_COUNT:{len(pre)}/{sum(r['actual_up'] for r in pre)}")
    if (len(y25),sum(r["actual_up"] for r in y25))!=(25,13):
        errs.append(f"Y25_COUNT:{len(y25)}/{sum(r['actual_up'] for r in y25)}")

    cuts={axis:median([r[axis] for r in pre]) for axis in AXES}
    results=[]
    transport=[]
    useful=[]
    for axis in AXES:
        for side in ("HIGH","LOW"):
            p=eval_rule(pre,axis,cuts[axis],side)
            q=eval_rule(y25,axis,cuts[axis],side)
            pre_useful=(p["false_up_removed"]>=2 and p["captured_up_retained"]>=6)
            transport_consistent=bool(pre_useful and q["false_up_removed"]>=3 and q["captured_up_retained"]>=10)
            rec={"axis":axis,"side":side,"cutpoint":cuts[axis],
                 "pre2025":p,"locked2025":q,
                 "pre2025_useful":pre_useful,
                 "transport_consistent":transport_consistent}
            results.append(rec)
            if pre_useful: useful.append(f"{axis}:{side}")
            if transport_consistent: transport.append(f"{axis}:{side}")

    # Unconditional t=.50 baseline for context only.
    def base(rows):
        cap=[r for r in rows if r["actual_up"]==1]
        fp=[r for r in rows if r["actual_up"]==0]
        veto=[r for r in rows if r["r2"]>=R2_THRESHOLD]
        return {
            "false_up_removed":sum(r in veto for r in fp),"false_up_total":len(fp),
            "captured_up_retained":len(cap)-sum(r in veto for r in cap),"captured_up_total":len(cap)
        }

    if errs:
        status="BLOCKED_INTEGRITY"
    elif transport:
        status="REGIME_CONDITIONED_DIAGNOSTIC_SIGNAL_EXISTS"
    elif useful:
        status="PRE2025_REGIME_SIGNAL_NOT_TRANSPORT_STABLE"
    else:
        status="NO_USEFUL_REGIME_CONDITION"

    result={
        "identity":IDENTITY,"date":"2026-09-23","status":status,
        "integrity_errors":errs,
        "fixed_r2_threshold":R2_THRESHOLD,
        "axes":AXES,
        "pre2025_median_cutpoints":cuts,
        "unconditional_baseline":{"pre2025":base(pre),"locked2025":base(y25)},
        "rules":results,
        "pre2025_useful_rules":useful,
        "transport_consistent_rules":transport,
        "row_values_pre2025":pre,
        "row_values_locked2025":y25,
        "governance":{
            "model_fitted":False,"threshold_search":False,"random_split":False,
            "2025_used_for_design_or_cutpoint":False,"2026_used":False,"runtime_promotion":False
        }
    }
    (a.out/"GOLD_CONTROL_UP2_REGIME_CONDITIONED_R2_ANATOMY_V1_RESULT_2026-09-23.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8")

    lines=["# GOLD CONTROL — UP-2 REGIME-CONDITIONED R2 ANATOMY V1","",
           f"**Status:** `{status}`","",
           f"Fixed R2 veto threshold: {R2_THRESHOLD}.","",
           f"Pre-2025 useful rules: `{useful}`  ",
           f"Transport-consistent rules: `{transport}`","",
           "| Axis | Side | Pre cut | Pre false removed | Pre true retained | 2025 false removed | 2025 true retained | Transport |",
           "|---|---|---:|---:|---:|---:|---:|---|"]
    for z in results:
        p=z["pre2025"]; q=z["locked2025"]
        lines.append(
            f"| {z['axis']} | {z['side']} | {z['cutpoint']:.6g} | "
            f"{p['false_up_removed']}/{p['false_up_total']} | "
            f"{p['captured_up_retained']}/{p['captured_up_total']} | "
            f"{q['false_up_removed']}/{q['false_up_total']} | "
            f"{q['captured_up_retained']}/{q['captured_up_total']} | "
            f"{z['transport_consistent']} |")
    lines += ["","Diagnostic only. No regime-conditioned veto is authorized."]
    (a.out/"GOLD_CONTROL_UP2_REGIME_CONDITIONED_R2_ANATOMY_V1_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if not errs else 2

if __name__=="__main__":
    raise SystemExit(main())
