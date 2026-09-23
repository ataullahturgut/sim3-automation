from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

IDENTITY = "CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_RESEARCH"

EXPECTED_FALSE_DOWN = {2022:4, 2023:0, 2024:3, 2025:16}


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_SPEC_FAIL:{name}:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def read_cbr_false_down(path: Path) -> list[dict]:
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if int(r["down_call"])==1 and int(r["actual_up"])==1:
                out.append({
                    "evaluation_year":int(r["evaluation_year"]),
                    "origin_date":r["origin_date"],
                    "target_date":r["target_date"],
                    "actual_up":1,
                    "p_down":float(r["p_down"]),
                })
    return out


def load_parent(path: Path):
    rows=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "evaluation_year":int(r["evaluation_year"]),
                "origin_date":r["origin_date"],
                "target_date":r["target_date"],
                "sqrt_high_risk_alert":int(r["sqrt_high_risk_alert"]),
                "target_close_log_return":float(r["target_close_return"]),
            })
    return rows


def build_router(base):
    days=base.load_days()
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)
    return base.build_router_rows(trows,bmaps,lmaps,contexts)


def simple_from_log(x: float) -> float:
    return math.exp(x)-1.0


def classify_recovery(loss: float, next_ret: float | None):
    if next_ret is None:
        return "NO_SIGNAL"
    if next_ret <= 0:
        return "NEGATIVE"
    if next_ret + 1e-15 >= loss:
        return "FULL"
    return "PARTIAL"


def summarize(rows, key):
    by=defaultdict(list)
    for r in rows:
        by[r["evaluation_year"]].append(r)
    out={}
    for y in sorted(EXPECTED_FALSE_DOWN):
        rr=by.get(y,[])
        signaled=[r for r in rr if r[key]==1]
        loss=sum(r["prior_short_loss_simple"] for r in rr)
        next_sum=sum(r["next_long_return_simple"] for r in signaled)
        net=sum((-r["prior_short_loss_simple"] + r["next_long_return_simple"]) for r in signaled)
        cats=defaultdict(int)
        for r in signaled:
            cats[r[f"{key}_recovery_class"]]+=1
        out[str(y)]={
            "false_down_n":len(rr),
            "signal_n":len(signaled),
            "signal_rate":len(signaled)/len(rr) if rr else None,
            "total_prior_false_down_loss":loss,
            "mean_prior_false_down_loss":loss/len(rr) if rr else None,
            "total_following_long_return_on_signaled_cases":next_sum,
            "additive_two_leg_net_on_signaled_cases":net,
            "full_recovery_n":cats["FULL"],
            "partial_recovery_n":cats["PARTIAL"],
            "negative_next_leg_n":cats["NEGATIVE"],
        }
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--cbr-ledger",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)

    false_down=read_cbr_false_down(args.cbr_ledger)
    counts={y:sum(r["evaluation_year"]==y for r in false_down) for y in EXPECTED_FALSE_DOWN}
    if counts!=EXPECTED_FALSE_DOWN:
        raise RuntimeError(f"FALSE_DOWN_COUNT_MISMATCH:{counts}!={EXPECTED_FALSE_DOWN}")

    base=load_mod("frozen_down_audit_base",args.base_module)
    router=build_router(base)
    r_origin={r["origin_date"]:r for r in router}

    parent=load_parent(args.sqrt_parent)
    p_origin={r["origin_date"]:r for r in parent}
    p_target={r["target_date"]:r for r in parent}

    rows=[]
    for fd in false_down:
        prior=p_target.get(fd["target_date"])
        if prior is None or prior["origin_date"]!=fd["origin_date"]:
            raise RuntimeError(f"PRIOR_PARENT_JOIN_FAIL:{fd}")
        prior_simple=simple_from_log(prior["target_close_log_return"])
        if prior_simple <= 0:
            raise RuntimeError(f"FALSE_DOWN_NOT_REALIZED_UP:{fd['target_date']}:{prior_simple}")

        rr=r_origin.get(fd["target_date"])
        pr=p_origin.get(fd["target_date"])
        if rr is None:
            raise RuntimeError(f"NEXT_ROUTER_NOT_FOUND:{fd['target_date']}")
        if pr is None:
            raise RuntimeError(f"NEXT_PARENT_NOT_FOUND:{fd['target_date']}")
        if rr["target_date"]!=pr["target_date"]:
            raise RuntimeError(f"NEXT_TARGET_MISMATCH:{fd['target_date']}:{rr['target_date']}:{pr['target_date']}")
        if int(rr["actual_up"]) != int(simple_from_log(pr["target_close_log_return"])>0):
            raise RuntimeError(f"NEXT_ACTUAL_MISMATCH:{fd['target_date']}")

        next_simple=simple_from_log(pr["target_close_log_return"])
        router_up=int(rr["router_up"])
        cascade_up=int(pr["sqrt_high_risk_alert"]==1 and router_up==1)

        row={
            **fd,
            "prior_short_loss_simple":prior_simple,
            "next_origin_date":fd["target_date"],
            "next_target_date":rr["target_date"],
            "next_router_up":router_up,
            "next_selected_expert":rr["selected_expert"],
            "next_sqrt_high_risk":int(pr["sqrt_high_risk_alert"]),
            "next_cascade_verified_up":cascade_up,
            "next_long_return_simple":next_simple,
            "standalone_up_recovery_class":classify_recovery(prior_simple,next_simple if router_up else None),
            "cascade_up_recovery_class":classify_recovery(prior_simple,next_simple if cascade_up else None),
            "standalone_up_two_leg_net_simple":(-prior_simple+next_simple) if router_up else None,
            "cascade_up_two_leg_net_simple":(-prior_simple+next_simple) if cascade_up else None,
        }
        row["next_router_up_recovery_class"]=row["standalone_up_recovery_class"]
        row["next_cascade_verified_up_recovery_class"]=row["cascade_up_recovery_class"]
        rows.append(row)

    standalone_summary=summarize(rows,"next_router_up")
    cascade_summary=summarize(rows,"next_cascade_verified_up")

    # Overall summaries
    def overall(summary_key):
        signaled=[r for r in rows if r[summary_key]==1]
        cats=defaultdict(int)
        for r in signaled:
            cats[r[f"{summary_key}_recovery_class"]]+=1
        return {
            "false_down_n":len(rows),
            "signal_n":len(signaled),
            "signal_rate":len(signaled)/len(rows),
            "total_prior_false_down_loss":sum(r["prior_short_loss_simple"] for r in rows),
            "total_following_long_return_on_signaled_cases":sum(r["next_long_return_simple"] for r in signaled),
            "additive_two_leg_net_on_signaled_cases":sum(-r["prior_short_loss_simple"]+r["next_long_return_simple"] for r in signaled),
            "full_recovery_n":cats["FULL"],
            "partial_recovery_n":cats["PARTIAL"],
            "negative_next_leg_n":cats["NEGATIVE"],
        }

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":"RETROSPECTIVE_NEXT_ORIGIN_RESCUE_AUDIT_COMPLETE",
        "integrity_errors":[],
        "false_down_counts":counts,
        "standalone_router_up_by_year":standalone_summary,
        "cascade_verified_up_by_year":cascade_summary,
        "standalone_router_up_overall":overall("next_router_up"),
        "cascade_verified_up_overall":overall("next_cascade_verified_up"),
        "interpretation_guardrails":{
            "t_close_signal_can_prevent_prior_loss":False,
            "next_origin_signal_only_affects_following_trade":True,
            "fees_spread_slippage_included":False,
            "leverage_included":False,
            "2025_used_for_tuning":False,
            "2026_used":False,
        }
    }

    out_json=args.out/"GOLD_CONTROL_CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_RESULT_2026-09-23.json"
    out_json.write_text(json.dumps(result,indent=2),encoding="utf-8")

    fields=[
        "evaluation_year","origin_date","target_date","p_down",
        "prior_short_loss_simple","next_origin_date","next_target_date",
        "next_router_up","next_selected_expert","next_sqrt_high_risk","next_cascade_verified_up",
        "next_long_return_simple","standalone_up_recovery_class","cascade_up_recovery_class",
        "standalone_up_two_leg_net_simple","cascade_up_two_leg_net_simple"
    ]
    with (args.out/"GOLD_CONTROL_CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

    lines=[
        "# GOLD CONTROL — CBR FALSE-DOWN NEXT-ORIGIN UP RESCUE AUDIT V1 RESULT","",
        "**Status:** RETROSPECTIVE_NEXT_ORIGIN_RESCUE_AUDIT_COMPLETE","",
        "This audit measures whether the frozen UP verifier emits an UP signal at the close of a CBR false-DOWN target day for the following trading day.",
        "That signal cannot erase the loss already realized on the false-DOWN day; it can only affect the next trade.","",
        "## Standalone Router-UP","",
        "| Year | False DOWN | Next-origin UP | Rate | Prior loss | Following long return | Two-leg net | Full | Partial | Negative |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for y in sorted(EXPECTED_FALSE_DOWN):
        m=standalone_summary[str(y)]
        lines.append(
            f"| {y} | {m['false_down_n']} | {m['signal_n']} | {m['signal_rate']} | "
            f"{m['total_prior_false_down_loss']} | {m['total_following_long_return_on_signaled_cases']} | "
            f"{m['additive_two_leg_net_on_signaled_cases']} | {m['full_recovery_n']} | {m['partial_recovery_n']} | {m['negative_next_leg_n']} |"
        )
    lines += ["","## Cascade VERIFIED-UP","",
        "| Year | False DOWN | Next cascade UP | Rate | Prior loss | Following long return | Two-leg net | Full | Partial | Negative |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in sorted(EXPECTED_FALSE_DOWN):
        m=cascade_summary[str(y)]
        lines.append(
            f"| {y} | {m['false_down_n']} | {m['signal_n']} | {m['signal_rate']} | "
            f"{m['total_prior_false_down_loss']} | {m['total_following_long_return_on_signaled_cases']} | "
            f"{m['additive_two_leg_net_on_signaled_cases']} | {m['full_recovery_n']} | {m['partial_recovery_n']} | {m['negative_next_leg_n']} |"
        )
    (args.out/"GOLD_CONTROL_CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
