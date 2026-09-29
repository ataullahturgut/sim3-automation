from __future__ import annotations
import argparse,json
from pathlib import Path

import gold_monthly_dev_snapshot_v1 as snap
import gold_monthly_chhho_f0_f1_ablation_v1 as core

SINGLE={
 "NO_GOLD_MR":[1,2,3,4,5,6,7],
 "NO_GOLD_VW":[0,2,3,4,5,6,7],
 "NO_SILVER_MR":[0,1,3,4,5,6,7],
 "NO_SILVER_VW":[0,1,2,4,5,6,7],
 "NO_PLATINUM_MR":[0,1,2,3,5,6,7],
 "NO_PLATINUM_VW":[0,1,2,3,4,6,7],
 "NO_PALLADIUM_MR":[0,1,2,3,4,5,7],
 "NO_PALLADIUM_VW":[0,1,2,3,4,5,6],
}
core.VARIANTS.update(SINGLE)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--variant",choices=sorted(SINGLE),required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    bundle,meta=snap.load_snapshot(a.snapshot)
    rows=core.eval_variant(bundle,a.variant)
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F1_FEATURE_ABLATION_V1_2026-09-29",
      "variant":a.variant,
      "features":core.FEATURES,
      "kept_indices":core.VARIANTS[a.variant],
      "kept_features":[core.FEATURES[i] for i in core.VARIANTS[a.variant]],
      "authority":{
        "dev":"2022-04..2024-12","random_split":"NONE",
        "2025_used":False,"2026_used":False,"external_features_used":False,
        "representation_changed":False,"lag_changed":False,
        "architecture":"ChHHO-ANFIS algorithm/rule count frozen; 7D true reduced-input ablation",
        "ablation_method":"leave exactly one CURRENT8 feature out",
        "neon_reads":0,"snapshot_payload_sha256":meta["payload_sha256"],
      },
      "dev":core.summarize(rows),
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F1_SINGLE_FEATURE_GATE=PASS")
    print(json.dumps({
      "variant":a.variant,
      "sum_abs_error":out["dev"]["metrics"]["sum_abs_error"],
      "direction_correct":out["dev"]["metrics"]["direction_correct"],
      "mae":out["dev"]["metrics"]["mae"],
      "rmse":out["dev"]["metrics"]["rmse"],
    },sort_keys=True))
if __name__=="__main__":main()
