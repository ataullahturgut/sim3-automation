from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_meta_screen_v6 as av6
import vw_midas_elmfis_baseline_v1 as eb
import gold_monthly_f4_rates_parity_shard_v1 as rates


def zscore_matrix(X):
    X=np.asarray(X,float)
    m=X.mean(0); s=X.std(0)
    s=np.where(s<1e-12,1.0,s)
    return (X-m)/s


def design_diagnostics(bundle, ext):
    series=rates.build_rate_series(ext)
    samples=rates.rates_samples(bundle, rates.DEV_END, series)
    keys=sorted(k for k in samples if k < rates.DEV_END)
    X=np.stack([samples[k][0] for k in keys])
    if X.shape[1] != 12:
        raise RuntimeError(f"BAD_DIAG_MATRIX {X.shape}")

    Xz=zscore_matrix(X)
    corr=np.corrcoef(Xz,rowvar=False)
    np.fill_diagonal(corr,0.0)

    current8_names=[
        f"{metal}_{rep}"
        for metal in ("Gold","Silver","Platinum","Palladium")
        for rep in ("MR1","VW")
    ]
    names=current8_names+rates.RATE_FEATURES

    rate_idx=range(8,12)
    within=[]
    for i in rate_idx:
        for j in range(i+1,12):
            within.append((abs(float(corr[i,j])),names[i],names[j],float(corr[i,j])))
    within.sort(reverse=True)

    cross=[]
    for i in range(8):
        for j in rate_idx:
            cross.append((abs(float(corr[i,j])),names[i],names[j],float(corr[i,j])))
    cross.sort(reverse=True)

    base_cond=float(np.linalg.cond(Xz[:,:8]))
    rates_cond=float(np.linalg.cond(Xz))

    return {
        "diagnostic_outer_target":"2024-12",
        "pre_target_history_first":keys[0],
        "pre_target_history_last":keys[-1],
        "pre_target_rows":len(keys),
        "base_rank":int(np.linalg.matrix_rank(Xz[:,:8])),
        "rates_augmented_rank":int(np.linalg.matrix_rank(Xz)),
        "base_condition_number":base_cond,
        "rates_augmented_condition_number":rates_cond,
        "condition_number_ratio_rates_over_base":(
            rates_cond/base_cond if base_cond>0 else None
        ),
        "max_abs_within_rates_correlation":{
            "abs_corr":within[0][0],
            "feature_a":within[0][1],
            "feature_b":within[0][2],
            "signed_corr":within[0][3],
        },
        "max_abs_rate_vs_current8_correlation":{
            "abs_corr":cross[0][0],
            "feature_a":cross[0][1],
            "feature_b":cross[0][2],
            "signed_corr":cross[0][3],
        },
        "all_within_rates_pairs":[
            {"abs_corr":a,"feature_a":b,"feature_b":c,"signed_corr":d}
            for a,b,c,d in within
        ],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",required=True)
    ap.add_argument("--base",required=True)
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    root=Path(a.dir)
    base_doc=json.loads(Path(a.base).read_text())
    if not base_doc.get("baseline_parity",{}).get("pass"):
        raise RuntimeError("BASE_PARITY_NOT_PASS")

    shard_files=sorted(root.rglob("rates_shard_*.json"))
    if len(shard_files)!=6:
        raise RuntimeError(f"EXPECTED_6_SHARDS got={len(shard_files)} {shard_files}")

    rows=[]; labels=[]; authority=None
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
    expected=list(base.month_range("2022-04","2024-12"))
    if targets!=expected or len(set(targets))!=33:
        raise RuntimeError(f"TARGET_COVERAGE_FAIL {targets}")

    metrics=eb.active_metrics(rows)
    yearly=eb.yearly(rows)

    br={r["target"]:r for r in base_doc["dev"]["rows"]}
    if sorted(br)!=targets:
        raise RuntimeError("BASE_TARGET_SET_MISMATCH")

    b_ae=np.array([abs(float(br[t]["forecast"])-float(br[t]["actual"])) for t in targets])
    r_ae=np.array([abs(float(r["forecast"])-float(r["actual"])) for r in rows])
    paired=b_ae-r_ae

    wins=int(np.sum(paired>1e-12))
    losses=int(np.sum(paired<-1e-12))
    ties=int(len(paired)-wins-losses)
    bsum=float(b_ae.sum()); rsum=float(r_ae.sum())

    yearly_cmp={}
    for y in ("2022","2023","2024"):
        ix=[i for i,t in enumerate(targets) if t.startswith(y)]
        bs=float(b_ae[ix].sum()); rs=float(r_ae[ix].sum())
        yearly_cmp[y]={
            "base_sum_abs_error":bs,
            "rates_sum_abs_error":rs,
            "delta_base_minus_rates":bs-rs,
        }

    loo=[]
    for i,t in enumerate(targets):
        loo.append({
            "left_out_target":t,
            "base_minus_rates_improvement":float((bsum-b_ae[i])-(rsum-r_ae[i])),
        })

    signed=np.array([float(r["forecast"])-float(r["actual"]) for r in rows])

    bundle,smeta=snap.load_snapshot(a.snapshot)
    ext=json.loads(Path(a.external_v2).read_text())
    if smeta["payload_sha256"]!=authority["snapshot_payload_sha256"]:
        raise RuntimeError("SNAPSHOT_PAYLOAD_MISMATCH")
    if ext["payload_sha256"]!=authority["external_v2_payload_sha256"]:
        raise RuntimeError("EXTERNAL_PAYLOAD_MISMATCH")
    diag=design_diagnostics(bundle,ext)

    summary={
        "schema":"GOLD_MONTHLY_F4_RATES_PARITY_RESULT_V1_2026-09-29",
        "family":"RATES",
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
            "rates_inputs":4,
            "total_inputs":12,
            "population":36,
            "diagnostic_not_final_promotion":True,
        },
        "base":{
            "sum_abs_error":float(base_doc["dev"]["metrics"]["sum_abs_error"]),
            "direction_correct":int(base_doc["dev"]["metrics"]["direction_correct"]),
            "metrics":base_doc["dev"]["metrics"],
        },
        "rates":{
            "sum_abs_error":float(metrics["sum_abs_error"]),
            "direction_correct":int(metrics["direction_correct"]),
            "metrics":metrics,
            "yearly":yearly,
            "rows":rows,
        },
        "comparison":{
            "delta_sum_abs_error_base_minus_rates":float(bsum-rsum),
            "relative_improvement_pct":float((bsum-rsum)/bsum*100.0),
            "direction_delta_correct":int(metrics["direction_correct"])-int(base_doc["dev"]["metrics"]["direction_correct"]),
            "paired_wins":wins,
            "paired_losses":losses,
            "paired_ties":ties,
            "median_paired_abs_error_improvement":float(np.median(paired)),
            "mean_paired_abs_error_improvement":float(np.mean(paired)),
            "worst_rates_abs_error":float(r_ae.max()),
            "worst_rates_target":targets[int(np.argmax(r_ae))],
            "rates_signed_bias_mean":float(signed.mean()),
            "yearly":yearly_cmp,
            "leave_one_origin":{
                "min_improvement":float(min(x["base_minus_rates_improvement"] for x in loo)),
                "max_improvement":float(max(x["base_minus_rates_improvement"] for x in loo)),
                "all":loo,
            },
        },
        "redundancy_diagnostics":diag,
        "interpretation":{
            "dev_sum_abs_error_improved":bool(rsum<bsum),
            "direction_improved":bool(int(metrics["direction_correct"])>int(base_doc["dev"]["metrics"]["direction_correct"])),
            "direction_not_worse":bool(int(metrics["direction_correct"])>=int(base_doc["dev"]["metrics"]["direction_correct"])),
            "median_paired_improvement_positive":bool(float(np.median(paired))>0),
            "all_leave_one_origin_improvements_positive":bool(min(x["base_minus_rates_improvement"] for x in loo)>0),
        },
    }

    Path(a.output).write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_RATES_PARITY_SUMMARY_GATE=PASS")
    print(json.dumps({
        "base_sum_abs_error":summary["base"]["sum_abs_error"],
        "base_direction":summary["base"]["direction_correct"],
        "rates_sum_abs_error":summary["rates"]["sum_abs_error"],
        "rates_direction":summary["rates"]["direction_correct"],
        "comparison":{k:v for k,v in summary["comparison"].items() if k not in {"leave_one_origin","yearly"}},
        "yearly":summary["comparison"]["yearly"],
        "redundancy_diagnostics":summary["redundancy_diagnostics"],
        "interpretation":summary["interpretation"],
    },sort_keys=True))


if __name__=="__main__":
    main()
