"""Independent strict origin-date feature X and origin anchor study.

A second **research variant**: full original CHHHO retraining, but every
origin-period 8-feature X uses Gold/Ag/Pt/Pd daily samples through the day
BEFORE each month's last calendar day, while historical train Y remains a
completed full-month realized return. Does NOT certify first-print timestamps.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snapshot
import gold_monthly_chhho_origin_anchor_replay_v1 as baseline
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho

def prefix_feature_data(dated):
    """Rebuild all four metal prefix-price channels using explicit date cutoffs."""
    accum={metal:defaultdict(list) for metal in base.METALS}
    for item in dated:
        m=item["date"][:7]
        if item["date"]>baseline.origin_cutoff(m,strict=True):
            continue
        for metal in base.METALS:
            price=float(item[metal])
            if not math.isfinite(price) or price<=0:
                raise RuntimeError(f"BAD_PREFIX_METAL_PRICE {metal} {item['date']}")
            accum[metal][m].append(price)
    daily={metal:{m:np.array(p,float) for m,p in hist.items()}
           for metal,hist in accum.items()}
    monthly={metal:{m:float(v.mean()) for m,v in hist.items()}
             for metal,hist in daily.items()}
    return daily,monthly

def samples_strict_X_full_Y(bundle, prefix_daily, prefix_monthly, target):
    origin=base.month_shift(target,-1)
    history=bundle.gpr_vintages[origin]
    prefix_context=base.DataBundle(
        core_gold=bundle.core_gold,
        core_gpr=bundle.core_gpr,
        daily_month_values=prefix_daily,
        monthly_metal=prefix_monthly,
        gpr_vintages=bundle.gpr_vintages,
        source_checks=bundle.source_checks,
        invariants_before=bundle.invariants_before,
    )
    samples={}
    for t in base.month_range("2010-03",origin):
        try:
            x=base.feature_for_target(prefix_context,t,history,True)
            y=base.label_for_target(bundle,t)
        except RuntimeError:
            continue
        samples[t]=(x,y)
    samples[target]=(base.feature_for_target(prefix_context,target,history,True),None)
    return samples

def run(path):
    bundle,meta=snapshot.load_snapshot(path)
    if meta["payload_sha256"]!=baseline.EXPECTED_SHA:
        raise RuntimeError("FROZEN_SNAPSHOT_HASH_MISMATCH")
    doc=json.loads(Path(path).read_text(encoding="utf-8"))
    dated=doc["payload"]["daily_common_rows"]
    daily,monthly=prefix_feature_data(dated)
    if any(m>="2025-01" for v in monthly.values() for m in v):
        raise RuntimeError("FUTURE_FEATURE_MONTH")
    out=[]
    for target in base.month_range("2022-04","2024-12"):
        origin=base.month_shift(target,-1)
        samples=samples_strict_X_full_Y(bundle,daily,monthly,target)
        if samples[target][1] is not None:
            raise RuntimeError("TARGET_Y_LEAKED")
        pred,n,diagnostics=chhho.select(samples,target,"CHHHO")
        anchor=baseline.prefix_origin_price(dated,origin,strict=True)
        if abs(anchor["anchor_usd_oz"]-monthly["Gold"][origin])>1e-9:
            raise RuntimeError("ANCHOR_FEATURE_SOURCE_MISMATCH")
        level=anchor["anchor_usd_oz"]
        forecast=float(level*math.exp(float(pred[0])))
        out.append({
            "target":target,"origin":origin,"training_rows":n,
            "pred_log_return_gold":float(pred[0]),
            "origin_date_cutoff":anchor["cutoff_day_inclusive"],
            "source_n":anchor["observed_business_day_count"],
            "anchors":{"STRICT_FEATURE_STRICT_ANCHOR":level},
            "forecasts":{"STRICT_FEATURE_STRICT_ANCHOR":forecast},
            "targets":{
                "CORE5_FINAL_HISTORICAL":float(bundle.core_gold[target]),
                "STAK_MONTHLY_MATCHED":float(bundle.monthly_metal["Gold"][target])
            },
            "optimizer_diagnostics":diagnostics,
        })
        print(f"STRICT_FEATURE_FULL_OPTIMIZER_PROGRESS {target} {len(out)}/33",flush=True)
    if len(out)!=33 or out[0]["training_rows"]<140:
        raise RuntimeError("BAD_TRAINING_OR_COVERAGE")
    scores={
        "vs_CORE5_FINAL_HISTORICAL":baseline.metrics(out,"STRICT_FEATURE_STRICT_ANCHOR","CORE5_FINAL_HISTORICAL"),
        "vs_STAK_MONTHLY_MATCHED":baseline.metrics(out,"STRICT_FEATURE_STRICT_ANCHOR","STAK_MONTHLY_MATCHED"),
    }
    return {
        "schema":"GOLD_MONTHLY_STRICT_FEATURE_AND_ANCHOR_REPLAY_V1",
        "scope":"DEV_ONLY_SOURCE_RECONSTRUCTION_NOT_CERTIFIED_FIRSTPRINT",
        "new_feature_contract":"all four metal monthly origin-price MR and VW prefix through day before month-end; retrospective historical label Y remains full month",
        "original_optimizer_unchanged":True,
        "training_target_y_absent":True,
        "origin_daily_firstprint_verified":False,
        "snapshot_sha256":meta["payload_sha256"],
        "source_target_2025_2026_used":False,
        "scores":scores,"rows":out,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=run(args.snapshot)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("STRICT_FEATURE_FULL_REPLAY_GATE=PASS",flush=True)
    print(json.dumps({"scores":result["scores"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
