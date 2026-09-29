from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_elmfis_baseline_v1 as eb

def configure_input_dimension(d):
    common=anfis.common
    rules=common.RULES
    n_ant=rules*d
    common.INPUTS=d
    common.N_ANT=n_ant
    common.PARAM_DIM=2*n_ant
    common.LOWER=np.concatenate([
        np.full(n_ant,common.CENTER_LOW),
        np.full(n_ant,math.log(common.SPREAD_LOW)),
    ])
    common.UPPER=np.concatenate([
        np.full(n_ant,common.CENTER_HIGH),
        np.full(n_ant,math.log(common.SPREAD_HIGH)),
    ])
    common.LOCAL_SIGMA=np.concatenate([np.full(n_ant,.45),np.full(n_ant,.30)])
    common.REFIT_SIGMA=np.concatenate([np.full(n_ant,.16),np.full(n_ant,.12)])
    anfis.D=common.PARAM_DIM
    anfis.LO=common.LOWER
    anfis.HI=common.UPPER

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

def subset_samples(samples,keep):
    out={}
    idx=np.asarray(keep,dtype=int)
    for k,(x,y) in samples.items():
        out[k]=(np.asarray(x,float)[idx].copy(),np.asarray(y,float).copy())
    return out

def eval_variant(bundle,variant):
    keep=VARIANTS[variant]
    configure_input_dimension(len(keep))
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        samples=base.all_samples_at_origin(bundle,target,governed=True)
        if variant!="CURRENT8":
            samples=subset_samples(samples,keep)
        p,n,d=anfis.select(samples,target,"CHHHO")
        origin=base.month_shift(target,-1)
        rows.append({
          "target":target,"origin":origin,"variant":variant,
          "kept_features":[FEATURES[i] for i in keep],
          "masked_features":[FEATURES[i] for i in range(8) if i not in keep],
          "ablation_semantics":"OMITTED_COLUMNS_REMOVED_FROM_INPUT_SPACE; same rule count/optimizer/chronology",
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
        "architecture":"ChHHO-ANFIS algorithm/rule count frozen; input dimension equals retained feature count",
        "ablation_method":"true reduced-input ablation; omitted CURRENT8 columns removed",
        "capacity_note":"consequent/premise parameter count changes mechanically with input dimension; optimizer settings and rule count unchanged",
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
