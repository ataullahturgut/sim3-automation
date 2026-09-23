from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

IDENTITY="UP2_LAST_HOUR_TREND_R2_THRESHOLD_ANATOMY_V1_RESEARCH"
GRID=[i/20 for i in range(21)]


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


def scan(rows):
    captured=[r for r in rows if r["actual_up"]==1]
    false=[r for r in rows if r["actual_up"]==0]
    out=[]
    for t in GRID:
        cap_lost=sum(r["r2"]>=t for r in captured)
        fp_removed=sum(r["r2"]>=t for r in false)
        cap_keep=len(captured)-cap_lost
        fp_keep=len(false)-fp_removed
        calls_keep=cap_keep+fp_keep
        precision=cap_keep/calls_keep if calls_keep else None
        out.append({
            "threshold":t,
            "captured_up_total":len(captured),
            "false_up_total":len(false),
            "captured_up_lost":cap_lost,
            "captured_up_retained":cap_keep,
            "captured_up_retention_rate":cap_keep/len(captured) if captured else None,
            "false_up_removed":fp_removed,
            "false_up_remaining":fp_keep,
            "false_up_removal_rate":fp_removed/len(false) if false else None,
            "remaining_calls":calls_keep,
            "remaining_precision":precision,
        })
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--up2-ledger",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--mechanism-code",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    cbr=load_mod("cbr_authority",a.cbr_code)
    mech=load_mod("mech_authority",a.mechanism_code)

    ledger=read_csv(a.up2_ledger)
    paths=cbr.load_paths(["2022-01-01","2025-12-31"])

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
        feat=mech.features(paths[od])
        rows.append({
            "evaluation_year":y,
            "origin_date":od,
            "target_date":r["target_date"],
            "actual_up":int(r["actual_up"]),
            "r2":float(feat["last_hour_trend_r2"]),
        })

    pre=[r for r in rows if r["evaluation_year"]<=2024]
    y25=[r for r in rows if r["evaluation_year"]==2025]
    pre_cap=sum(r["actual_up"]==1 for r in pre); pre_fp=sum(r["actual_up"]==0 for r in pre)
    y25_cap=sum(r["actual_up"]==1 for r in y25); y25_fp=sum(r["actual_up"]==0 for r in y25)

    if (len(pre),pre_cap,pre_fp)!=(11,8,3):
        errs.append(f"PRE_COUNTS:{len(pre)}/{pre_cap}/{pre_fp}")
    if (len(y25),y25_cap,y25_fp)!=(25,13,12):
        errs.append(f"Y25_COUNTS:{len(y25)}/{y25_cap}/{y25_fp}")

    pre_scan=scan(pre)
    y25_scan=scan(y25)
    y25_by_t={x["threshold"]:x for x in y25_scan}

    useful=[]
    strict=[]
    transport=[]
    for p in pre_scan:
        t=p["threshold"]
        is_useful=(p["false_up_removed"]>=2 and p["captured_up_retained"]>=6)
        is_strict=(p["false_up_removed"]==3 and p["captured_up_retained"]>=6)
        if is_useful:
            useful.append(t)
            q=y25_by_t[t]
            if q["false_up_removal_rate"]>=0.25 and q["captured_up_retention_rate"]>=0.75:
                transport.append(t)
        if is_strict:
            strict.append(t)

    if errs:
        status="BLOCKED_INTEGRITY"
    elif transport:
        status="STABLE_DIAGNOSTIC_SCALAR_VETO_ZONE_EXISTS"
    elif useful:
        status="PRE2025_ONLY_DIAGNOSTIC_ZONE_NOT_TRANSPORT_STABLE"
    else:
        status="NO_USEFUL_SCALAR_VETO_ZONE"

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":errs,
        "semantics":"veto UP2 iff last_hour_trend_r2 >= threshold",
        "threshold_grid":GRID,
        "pre2025_counts":{"calls":len(pre),"captured_up":pre_cap,"false_up_actual_down":pre_fp},
        "locked2025_counts":{"calls":len(y25),"captured_up":y25_cap,"false_up_actual_down":y25_fp},
        "pre2025_scan":pre_scan,
        "locked2025_scan":y25_scan,
        "useful_pre2025_zone_thresholds":useful,
        "strict_pre2025_zone_thresholds":strict,
        "transport_consistent_thresholds":transport,
        "row_values_pre2025":sorted(pre,key=lambda r:r["r2"]),
        "row_values_locked2025":sorted(y25,key=lambda r:r["r2"]),
        "governance":{
            "model_fitted":False,
            "random_split":False,
            "threshold_grid_frozen_before_scan":True,
            "2025_used_for_threshold_selection":False,
            "2026_used":False,
            "runtime_promotion":False
        }
    }
    (a.out/"GOLD_CONTROL_UP2_LAST_HOUR_TREND_R2_THRESHOLD_ANATOMY_V1_RESULT_2026-09-23.json").write_text(
        json.dumps(result,indent=2),encoding="utf-8"
    )

    lines=[
        "# GOLD CONTROL — UP-2 LAST-HOUR TREND-R2 THRESHOLD ANATOMY V1","",
        f"**Status:** `{status}`","",
        f"Pre-2025 calls: {len(pre)} = {pre_cap} captured UP + {pre_fp} false-UP actual-DOWN.  ",
        f"Locked 2025 calls: {len(y25)} = {y25_cap} captured UP + {y25_fp} false-UP actual-DOWN.","",
        f"Useful pre-2025 grid thresholds: `{useful}`  ",
        f"Strict pre-2025 grid thresholds: `{strict}`  ",
        f"Transport-consistent thresholds: `{transport}`","",
        "## Fixed-grid scan","",
        "| t | pre false removed | pre true retained | pre remaining precision | 2025 false removed | 2025 true retained | 2025 remaining precision |",
        "|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for p in pre_scan:
        q=y25_by_t[p["threshold"]]
        pprec="" if p["remaining_precision"] is None else f"{100*p['remaining_precision']:.1f}%"
        qprec="" if q["remaining_precision"] is None else f"{100*q['remaining_precision']:.1f}%"
        lines.append(
            f"| {p['threshold']:.2f} | {p['false_up_removed']}/{p['false_up_total']} | "
            f"{p['captured_up_retained']}/{p['captured_up_total']} | {pprec} | "
            f"{q['false_up_removed']}/{q['false_up_total']} | "
            f"{q['captured_up_retained']}/{q['captured_up_total']} | {qprec} |"
        )
    lines += ["","Diagnostic only. No veto rule is authorized by this scan."]
    (a.out/"GOLD_CONTROL_UP2_LAST_HOUR_TREND_R2_THRESHOLD_ANATOMY_V1_RESULT_2026-09-23.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2))
    return 0 if not errs else 2

if __name__=="__main__":
    raise SystemExit(main())
