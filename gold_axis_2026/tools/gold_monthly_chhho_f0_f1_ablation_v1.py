from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_elmfis_baseline_v1 as eb

DEV_START, DEV_END = "2022-04","2024-12"
FEATURES = [
    "Gold_MR","Gold_VW","Silver_MR","Silver_VW",
    "Platinum_MR","Platinum_VW","Palladium_MR","Palladium_VW"
]
VARIANTS = {
    "CURRENT8": list(range(8)),
    "MR_ONLY": [0,2,4,6],
    "VW_ONLY": [1,3,5,7],
    "GOLD_ONLY": [0,1],
    "GOLD_SILVER": [0,1,2,3],
    "GOLD_SILVER_PLATINUM": [0,1,2,3,4,5],
    "NO_GOLD": [2,3,4,5,6,7],
    "NO_SILVER": [0,1,4,5,6,7],
    "NO_PLATINUM": [0,1,2,3,6,7],
    "NO_PALLADIUM": [0,1,2,3,4,5],
}
BASE_SIGMAAE=1413.0297794085
BASE_DIRECTION=23

def masked_samples(samples,target,keep):
    keep=set(keep)
    keys=sorted(k for k in samples if k<target)
    X=np.stack([samples[k][0] for k in keys])
    means=X.mean(axis=0)
    out={}
    for k,(x,y) in samples.items():
        z=np.asarray(x,float).copy()
        for j in range(8):
            if j not in keep:
                z[j]=means[j]
        out[k]=(z,np.asarray(y,float).copy())
    return out

def eval_variant(bundle,variant):
    keep=VARIANTS[variant]
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        samples=base.all_samples_at_origin(bundle,target,governed=True)
        if variant!="CURRENT8":
            samples=masked_samples(samples,target,keep)
        p,n,d=anfis.select(samples,target,"CHHHO")
        origin=base.month_shift(target,-1)
        rows.append({
          "target":target,"origin":origin,"variant":variant,
          "kept_features":[FEATURES[i] for i in keep],
          "masked_features":[FEATURES[i] for i in range(8) if i not in keep],
          "mask_semantics":"OMITTED_COLUMNS_SET_TO_PRE_TARGET_TRAINING_MEAN; standardized value=0; no target info",
          "train_rows":n,"diag":d,
          "pred_log_return_gold":float(p[0]),
          "forecast":float(bundle.core_gold[origin]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[target]),
          "rw":float(bundle.core_gold[origin]),
        })
    return rows

def summarize(rows):
    m=eb.active_metrics(rows)
    return {"metrics":m,"yearly":eb.yearly(rows),"rows":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--variant",choices=sorted(VARIANTS),required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    bundle,meta=snap.load_snapshot(a.snapshot)
    rows=eval_variant(bundle,a.variant)
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F0_F1_ABLATION_V1_2026-09-29",
      "variant":a.variant,
      "features":FEATURES,
      "kept_indices":VARIANTS[a.variant],
      "kept_features":[FEATURES[i] for i in VARIANTS[a.variant]],
      "authority":{
        "dev":"2022-04..2024-12",
        "random_split":"NONE",
        "2025_used":False,
        "2026_used":False,
        "external_features_used":False,
        "representation_changed":False,
        "lag_changed":False,
        "architecture":"ChHHO-ANFIS frozen algorithm; 8D architecture retained",
        "ablation_method":"training-mean masking of omitted raw CURRENT8 columns at each outer target",
        "mask_mean_scope":"strictly pre-target rows within each outer-origin sample set",
        "neon_reads":0,
        "snapshot_payload_sha256":meta["payload_sha256"],
      },
      "dev":summarize(rows),
    }
    if a.variant=="CURRENT8":
        got=out["dev"]["metrics"]["sum_abs_error"]
        gotdir=out["dev"]["metrics"]["direction_correct"]
        out["f0_parity"]={
          "reference_sum_abs_error":BASE_SIGMAAE,
          "observed_sum_abs_error":got,
          "abs_diff":abs(got-BASE_SIGMAAE),
          "reference_direction_correct":BASE_DIRECTION,
          "observed_direction_correct":gotdir,
          "pass":abs(got-BASE_SIGMAAE)<1e-4 and gotdir==BASE_DIRECTION,
        }
        if not out["f0_parity"]["pass"]:
            raise RuntimeError(f"F0_PARITY_FAIL {out['f0_parity']}")
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F0_F1_VARIANT_GATE=PASS")
    print(json.dumps({
      "variant":a.variant,
      "sum_abs_error":out["dev"]["metrics"]["sum_abs_error"],
      "direction_correct":out["dev"]["metrics"]["direction_correct"],
      "mae":out["dev"]["metrics"]["mae"],
      "rmse":out["dev"]["metrics"]["rmse"],
      "f0_parity":out.get("f0_parity"),
    },sort_keys=True))

if __name__=="__main__": main()
