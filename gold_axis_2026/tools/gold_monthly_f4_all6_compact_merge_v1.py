from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

import vw_midas_elmfis_baseline_v1 as eb


def find_one(root: Path, pattern: str):
    xs=list(root.rglob(pattern))
    if len(xs)!=1:
        raise RuntimeError(f"EXPECTED_ONE {pattern} got={len(xs)} {xs}")
    return xs[0]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",required=True)
    ap.add_argument("--base",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    root=Path(a.dir)
    base=json.loads(Path(a.base).read_text())
    if not base.get("baseline_parity",{}).get("pass"):
        raise RuntimeError("BASE_PARITY_NOT_PASS")

    shard_files=sorted(root.rglob("all6_shard_*.json"))
    if len(shard_files)!=6:
        raise RuntimeError(f"EXPECTED_6_SHARDS got={len(shard_files)} {shard_files}")

    rows=[]
    labels=[]
    authority=None
    for p in shard_files:
        d=json.loads(p.read_text())
        labels.append(d["label"])
        if authority is None:
            authority=d["authority"]
        else:
            for k in ("snapshot_payload_sha256","external_v2_payload_sha256","b2_gate_schema"):
                if d["authority"].get(k)!=authority.get(k):
                    raise RuntimeError(f"SHARD_AUTHORITY_MISMATCH {p} {k}")
        rows.extend(d["rows"])

    rows=sorted(rows,key=lambda r:r["target"])
    targets=[r["target"] for r in rows]
    expected=[]
    y,m=2022,4
    while True:
        expected.append(f"{y:04d}-{m:02d}")
        if y==2024 and m==12: break
        m+=1
        if m==13:
            y+=1;m=1
    if targets!=expected:
        raise RuntimeError(f"TARGET_COVERAGE_FAIL targets={targets}")

    if len(set(targets))!=33:
        raise RuntimeError("DUPLICATE_OR_MISSING_TARGETS")

    metrics=eb.active_metrics(rows)
    yearly=eb.yearly(rows)

    br={r["target"]:r for r in base["dev"]["rows"]}
    ar={r["target"]:r for r in rows}
    if sorted(br)!=targets:
        raise RuntimeError("BASE_TARGET_SET_MISMATCH")

    b_ae=np.array([abs(float(br[t]["forecast"])-float(br[t]["actual"])) for t in targets])
    a_ae=np.array([abs(float(ar[t]["forecast"])-float(ar[t]["actual"])) for t in targets])
    paired=b_ae-a_ae

    wins=int(np.sum(paired>1e-12))
    losses=int(np.sum(paired<-1e-12))
    ties=int(len(paired)-wins-losses)
    bsum=float(b_ae.sum())
    asum=float(a_ae.sum())

    yearly_cmp={}
    for y in ("2022","2023","2024"):
        ix=[i for i,t in enumerate(targets) if t.startswith(y)]
        bs=float(b_ae[ix].sum()); aa=float(a_ae[ix].sum())
        yearly_cmp[y]={
            "base_sum_abs_error":bs,
            "all6_sum_abs_error":aa,
            "delta_base_minus_all6":bs-aa,
        }

    loo=[]
    for i,t in enumerate(targets):
        loo.append({
            "left_out_target":t,
            "base_minus_all6_improvement":float((bsum-b_ae[i])-(asum-a_ae[i])),
        })

    signed=np.array([float(ar[t]["forecast"])-float(ar[t]["actual"]) for t in targets])

    summary={
        "schema":"GOLD_MONTHLY_F4_ALL6_COMPACT_DIAGNOSTIC_SUMMARY_V1_2026-09-29",
        "execution":{
            "mode":"PARALLEL_OUTER_ORIGIN_SHARDS",
            "shards":labels,
            "exact_equivalence_note":"Each outer target is independent; CHHHO seeds depend on target and repeat, not execution order.",
        },
        "authority":{
            "selection_period":"2022-04..2024-12",
            "2025_used":False,
            "2026_used":False,
            "base_parity_pass":True,
            "snapshot_payload_sha256":authority["snapshot_payload_sha256"],
            "external_v2_payload_sha256":authority["external_v2_payload_sha256"],
            "b2_gate_schema":authority["b2_gate_schema"],
            "all6_inputs":22,
            "all6_population":66,
            "diagnostic_not_final_promotion":True,
        },
        "base":{
            "sum_abs_error":float(base["dev"]["metrics"]["sum_abs_error"]),
            "direction_correct":int(base["dev"]["metrics"]["direction_correct"]),
            "metrics":base["dev"]["metrics"],
        },
        "all6":{
            "sum_abs_error":float(metrics["sum_abs_error"]),
            "direction_correct":int(metrics["direction_correct"]),
            "metrics":metrics,
            "yearly":yearly,
            "rows":rows,
        },
        "comparison":{
            "delta_sum_abs_error_base_minus_all6":float(bsum-asum),
            "direction_delta_correct":int(metrics["direction_correct"])-int(base["dev"]["metrics"]["direction_correct"]),
            "paired_wins":wins,
            "paired_losses":losses,
            "paired_ties":ties,
            "median_paired_abs_error_improvement":float(np.median(paired)),
            "mean_paired_abs_error_improvement":float(np.mean(paired)),
            "worst_all6_abs_error":float(a_ae.max()),
            "worst_all6_target":targets[int(np.argmax(a_ae))],
            "all6_signed_bias_mean":float(signed.mean()),
            "yearly":yearly_cmp,
            "leave_one_origin":{
                "min_improvement":float(min(x["base_minus_all6_improvement"] for x in loo)),
                "max_improvement":float(max(x["base_minus_all6_improvement"] for x in loo)),
                "all":loo,
            },
        },
        "interpretation":{
            "dev_sum_abs_error_improved":bool(asum<bsum),
            "direction_improved":bool(int(metrics["direction_correct"])>int(base["dev"]["metrics"]["direction_correct"])),
            "direction_not_worse":bool(int(metrics["direction_correct"])>=int(base["dev"]["metrics"]["direction_correct"])),
            "median_paired_improvement_positive":bool(float(np.median(paired))>0),
            "all_leave_one_origin_improvements_positive":bool(min(x["base_minus_all6_improvement"] for x in loo)>0),
            "next_step_if_not_improved":"FAMILY_DECOMPOSITION_AND_DIMENSIONALITY_REDUNDANCY_DIAGNOSIS__DO_NOT_REJECT_ALL_EXTERNAL_FAMILIES",
            "next_step_if_improved":"FAMILY_DECOMPOSITION_AND_CONSTRAINED_COMPACT_SELECTION",
        },
    }

    Path(a.output).write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_ALL6_SHARDED_SUMMARY_GATE=PASS")
    print(json.dumps({
        "base_sum_abs_error":summary["base"]["sum_abs_error"],
        "base_direction":summary["base"]["direction_correct"],
        "all6_sum_abs_error":summary["all6"]["sum_abs_error"],
        "all6_direction":summary["all6"]["direction_correct"],
        "comparison":{k:v for k,v in summary["comparison"].items() if k not in {"leave_one_origin","yearly"}},
        "yearly":summary["comparison"]["yearly"],
        "interpretation":summary["interpretation"],
    },sort_keys=True))


if __name__=="__main__":
    main()
