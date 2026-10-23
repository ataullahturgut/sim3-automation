"""Active target-label and post-target poisoning tests for frozen ANN algorithms.

Consume an identical immutable 54-month historical source artifact. The same
original ANN component is run on 3 origins first with no target label, then
with deliberately forged target label (all four metals) AND a 2099 future
observation. The original mathematical model must produce the same prediction.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import gold_monthly_h1_ann_frozen_snapshot_replay_v2 as frozen
import gold_monthly_2026_aug_sep_topmodels_v1 as original

TARGETS=("2022-04","2025-01","2026-09")
def with_label(record, poison):
    samples={}
    for t,(x,y) in record["samples"].items():
        samples[t]=(np.asarray(x,dtype=float),None if y is None else np.asarray(y,dtype=float))
    if poison:
        t=record["target_month"]
        assert samples[t][1] is None
        # A synthetic but massive future label: any accidental test leakage
        # should change training if original code violates strict t < target.
        samples[t]=(samples[t][0].copy(),np.array([1e9,-1e9,1e8,-1e8]))
        samples["2099-01"]=(np.full(8,999999.0),np.full(4,-999999.0))
    return samples

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--snapshot",required=True)
    a.add_argument("--component",choices=frozen.COMPONENTS,required=True)
    a.add_argument("--output",required=True)
    args=a.parse_args()
    snap=frozen.read_snapshot(args.snapshot)
    selected=[r for r in snap["records"] if r["target_month"] in TARGETS]
    assert len(selected)==3
    out=[]
    for r in selected:
        t=r["target_month"]
        x1=with_label(r,False);x2=with_label(r,True)
        assert all(k<t for k in x1 if k!=t)
        assert "2099-01" in x2 and x2[t][1] is not None and x1[t][1] is None
        p1,m1=original.pred_component(x1,t,args.component)
        p2,m2=original.pred_component(x2,t,args.component)
        a1=np.asarray(p1,float)
        a2=np.asarray(p2,float)
        if a1.shape!=(4,) or not np.isfinite(a1).all() or not np.isfinite(a2).all():
            raise RuntimeError("TEST_LEAKAGE_BAD_FORECAST_VECTOR")
        maxdiff=float(np.max(np.abs(a1-a2)))
        if maxdiff>1e-10:
            raise RuntimeError(f"TARGET_OR_FUTURE_LEAKAGE_DETECTED component={args.component} month={t} maxdiff={maxdiff}")
        if int(m1["train_rows"])!=r["training_rows"] or int(m2["train_rows"])!=r["training_rows"]:
            raise RuntimeError("FUTURE_OR_TARGET_IN_TRAINING")
        out.append({"month":t,"component":args.component,
                    "target_label_poisoned":True,"far_future_sample_added":True,
                    "baseline_forecast":r["origin_gold_average"]*math.exp(float(a1[0])),
                    "poisoned_forecast":r["origin_gold_average"]*math.exp(float(a2[0])),
                    "max_four_metal_return_delta":maxdiff,
                    "training_rows_before_after":r["training_rows"],
                    "leakage":False})
        print("FROZEN_ANN_ACTIVE_LEAK_GATE_PASS",args.component,t,maxdiff,flush=True)
    payload={"status":"ACTIVE_TARGET_FUTURE_POISONING_TEST_PASS",
             "component":args.component,"source_sha256":snap["snapshot_sha256"],
             "source_firstprint_certified":False,
             "original_model_modified":False,"cases":out}
    Path(args.output).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("ANN_ACTIVE_LEAKAGE_TEST_ALL_PASS",args.component,len(out))

if __name__=="__main__":main()
