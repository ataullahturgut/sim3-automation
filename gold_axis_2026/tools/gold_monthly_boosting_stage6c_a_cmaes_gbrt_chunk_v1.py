#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

import gold_monthly_boosting_stage6c_a_cmaes_gbrt_v1 as core

def run_chunk(start,end):
    if start < core.DEV_START or end > core.DEV_END or start > end:
        raise RuntimeError(f"INVALID_CHUNK {start}..{end}")
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle=core.base.load_data(dsn)
    targets=list(core.base.month_range(start,end))
    rows=[]
    for i,target in enumerate(targets,1):
        data=core.build_origin_data(bundle,target)
        baseline_inner=core.inner_loss(data,core.BASELINE_PARAMS)
        bp,bf=core.outer_forecast(data,core.BASELINE_PARAMS)
        theta,params,cma_inner,calls,unique,seed=core.cma_optimize(data,target)
        cp,cf=core.outer_forecast(data,params)

        if target not in bundle.core_gold:
            raise RuntimeError(f"DEV_ACTUAL_MISSING {target}")
        actual=float(bundle.core_gold[target])
        rw=float(data["anchor_prev"])
        row={
            "target":target,
            "origin":data["origin"],
            "train_first":data["keys"][0],
            "train_last":data["keys"][-1],
            "train_rows":len(data["keys"]),
            "inner_train_n":len(data["inner_train_keys"]),
            "inner_val_n":len(data["inner_val_keys"]),
            "inner_val_first":data["inner_val_keys"][0],
            "inner_val_last":data["inner_val_keys"][-1],
            "baseline_inner_relative_sum_abs_error":float(baseline_inner),
            "cma_inner_relative_sum_abs_error":float(cma_inner),
            "inner_ratio_vs_baseline":float(cma_inner/max(baseline_inner,1e-12)),
            "cma_objective_calls":calls,
            "cma_unique_decoded_candidates":unique,
            "cma_seed":seed,
            "selected_theta":[float(x) for x in theta],
            "selected_params":params,
            "baseline_params":core.BASELINE_PARAMS,
            "baseline_pred_log_return_gold":float(bp),
            "baseline_forecast":float(bf),
            "cma_pred_log_return_gold":float(cp),
            "cma_forecast":float(cf),
            "actual":actual,
            "rw":rw,
            "baseline_absolute_error":float(abs(bf-actual)),
            "cma_absolute_error":float(abs(cf-actual)),
            "baseline_direction_correct":bool(int(np.sign(bf-rw))==int(np.sign(actual-rw))),
            "cma_direction_correct":bool(int(np.sign(cf-rw))==int(np.sign(actual-rw))),
        }
        rows.append(row)
        print(
            f"PROGRESS chunk={start}_{end} target={i}/{len(targets)} month={target} "
            f"baseAE={row['baseline_absolute_error']:.6f} cmaAE={row['cma_absolute_error']:.6f} "
            f"ratio={row['inner_ratio_vs_baseline']:.6f}",
            flush=True
        )

    after=core.read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    if any(r["cma_objective_calls"]!=core.MAX_EVALS for r in rows):
        raise RuntimeError("OBJECTIVE_BUDGET_FAIL")

    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    payload={
        "scope":"BOOSTING_STAGE6C_A_CMAES_GBRT_DEV_CHUNK_V1",
        "chunk":f"{start}..{end}",
        "freeze_file":"GOLD_MONTHLY_BOOSTING_STAGE6C_A_CMAES_GBRT_FREEZE_2026-09-27.md",
        "contract":{
            "full_dev_parent":"2022-04..2024-12",
            "chunk_start":start,
            "chunk_end":end,
            "representation":core.REP,
            "loss":"absolute_error",
            "cma_max_objective_calls_per_origin":core.MAX_EVALS,
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"QUARANTINED_NOT_USED_IN_DEVELOPMENT",
        },
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "rows":rows,
        "payload_sha256":digest,
    }
    out=Path(f"gold_monthly_boosting_stage6c_a_cmaes_gbrt_{start}_{end}.json")
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS",flush=True)
    print("CHUNK_RESULT="+json.dumps({"chunk":payload["chunk"],"rows":rows,"payload_sha256":digest},sort_keys=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--start",required=True)
    ap.add_argument("--end",required=True)
    a=ap.parse_args()
    run_chunk(a.start,a.end)

if __name__=="__main__":
    main()
