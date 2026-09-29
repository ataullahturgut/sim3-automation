from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np


def load_one(root: Path, variant: str):
    matches = list(root.rglob(f"all6_{variant}.json"))
    if len(matches) != 1:
        raise RuntimeError(f"EXPECTED_ONE_{variant}_RESULT got={len(matches)} {matches}")
    return json.loads(matches[0].read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    root = Path(a.dir)
    base = load_one(root, "BASE")
    all6 = load_one(root, "ALL6")

    if not base.get("baseline_parity", {}).get("pass"):
        raise RuntimeError("BASE_PARITY_NOT_PASS")

    br = {r["target"]: r for r in base["dev"]["rows"]}
    ar = {r["target"]: r for r in all6["dev"]["rows"]}
    if sorted(br) != sorted(ar):
        raise RuntimeError("TARGET_SET_MISMATCH")

    targets = sorted(br)
    b_ae = np.array([float(br[t]["abs_error"]) for t in targets])
    a_ae = np.array([float(ar[t]["abs_error"]) for t in targets])
    paired = b_ae - a_ae

    wins = int(np.sum(paired > 1e-12))
    losses = int(np.sum(paired < -1e-12))
    ties = int(len(paired) - wins - losses)

    yearly = {}
    for y in sorted(set(t[:4] for t in targets)):
        idx = [i for i,t in enumerate(targets) if t.startswith(y)]
        bs = float(b_ae[idx].sum())
        aa = float(a_ae[idx].sum())
        yearly[y] = {
            "base_sum_abs_error": bs,
            "all6_sum_abs_error": aa,
            "delta_base_minus_all6": bs-aa,
        }

    bsum = float(b_ae.sum())
    asum = float(a_ae.sum())
    loo = []
    for i,t in enumerate(targets):
        imp = float((bsum-b_ae[i]) - (asum-a_ae[i]))
        loo.append({"left_out_target":t,"base_minus_all6_improvement":imp})

    signed = np.array([float(ar[t]["signed_error"]) for t in targets])
    base_metrics = base["dev"]["metrics"]
    all6_metrics = all6["dev"]["metrics"]

    summary = {
        "schema":"GOLD_MONTHLY_F4_ALL6_COMPACT_DIAGNOSTIC_SUMMARY_V1_2026-09-29",
        "authority":{
            "selection_period":"2022-04..2024-12",
            "2025_used":False,
            "2026_used":False,
            "base_parity_pass":True,
            "all6_inputs":22,
            "all6_population":66,
            "diagnostic_not_final_promotion":True,
        },
        "base":{
            "sum_abs_error":float(base_metrics["sum_abs_error"]),
            "direction_correct":int(base_metrics["direction_correct"]),
            "metrics":base_metrics,
        },
        "all6":{
            "sum_abs_error":float(all6_metrics["sum_abs_error"]),
            "direction_correct":int(all6_metrics["direction_correct"]),
            "metrics":all6_metrics,
        },
        "comparison":{
            "delta_sum_abs_error_base_minus_all6":float(bsum-asum),
            "direction_delta_correct":int(all6_metrics["direction_correct"])-int(base_metrics["direction_correct"]),
            "paired_wins":wins,
            "paired_losses":losses,
            "paired_ties":ties,
            "median_paired_abs_error_improvement":float(np.median(paired)),
            "mean_paired_abs_error_improvement":float(np.mean(paired)),
            "worst_all6_abs_error":float(a_ae.max()),
            "worst_all6_target":targets[int(np.argmax(a_ae))],
            "all6_signed_bias_mean":float(np.mean(signed)),
            "yearly":yearly,
            "leave_one_origin":{
                "min_improvement":float(min(x["base_minus_all6_improvement"] for x in loo)),
                "max_improvement":float(max(x["base_minus_all6_improvement"] for x in loo)),
                "all":loo,
            },
        },
        "interpretation":{
            "dev_sum_abs_error_improved":bool(asum < bsum),
            "direction_improved":bool(int(all6_metrics["direction_correct"]) > int(base_metrics["direction_correct"])),
            "direction_not_worse":bool(int(all6_metrics["direction_correct"]) >= int(base_metrics["direction_correct"])),
            "median_paired_improvement_positive":bool(float(np.median(paired)) > 0),
            "all_leave_one_origin_improvements_positive":bool(min(x["base_minus_all6_improvement"] for x in loo) > 0),
            "next_step_if_not_improved":"FAMILY_DECOMPOSITION_AND_DIMENSIONALITY_REDUNDANCY_DIAGNOSIS__DO_NOT_REJECT_ALL_EXTERNAL_FAMILIES",
            "next_step_if_improved":"FAMILY_DECOMPOSITION_AND_CONSTRAINED_COMPACT_SELECTION",
        },
    }

    Path(a.output).write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_ALL6_SUMMARY_GATE=PASS")
    print(json.dumps({
        "base_sum_abs_error":summary["base"]["sum_abs_error"],
        "base_direction":summary["base"]["direction_correct"],
        "all6_sum_abs_error":summary["all6"]["sum_abs_error"],
        "all6_direction":summary["all6"]["direction_correct"],
        "comparison":{k:v for k,v in summary["comparison"].items() if k not in {"leave_one_origin","yearly"}},
        "yearly":summary["comparison"]["yearly"],
        "interpretation":summary["interpretation"],
    },sort_keys=True))


if __name__ == "__main__":
    main()
