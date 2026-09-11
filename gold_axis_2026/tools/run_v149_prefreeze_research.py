from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from gold_axis_2026.v149_research.common import write_json
from gold_axis_2026.v149_research.monthly import build_same_origin_panel,monthly_audit
from gold_axis_2026.v149_research.short_horizon import development_block_audit,inventory

OUT=ROOT/"gold_axis_2026/data_pipeline/audits/v149_research"
CONTRACT=ROOT/"gold_axis_2026/v149_research/contracts"


def main():
    OUT.mkdir(parents=True,exist_ok=True); CONTRACT.mkdir(parents=True,exist_ok=True)
    panel,meta=build_same_origin_panel(); panel.to_csv(OUT/"monthly_same_origin_panel_v149.csv",index=False,float_format="%.12g")
    audit=monthly_audit(panel); inv=inventory(); inc=development_block_audit(dev_end_index=240)
    write_json(OUT/"monthly_panel_metadata_v149.json",meta)
    write_json(OUT/"monthly_complementarity_development_v149.json",audit)
    write_json(OUT/"short_horizon_inventory_v149.json",inv)
    write_json(OUT/"short_horizon_incremental_development_v149.json",inc)
    short={}
    for key,res in inc.items():
        retained=[0,4] if res["block4_decision"]=="RETAIN" else [0]
        short[key]={"retained_blocks":retained,"outer_start_index":240,"block4_development_decision":res["block4_decision"]}
    freeze={
      "contract":"GOLD_CONTROL_V149_LIMITED_CANDIDATE_FREEZE","frozen_before_outer_scoring":True,
      "monthly":{"candidates":["RW","SIMPLE_EQUAL_4"],"complex_integration":"BLOCKED_PIT","outer_start":"2025-01"},
      "short_horizon":short,
      "short_model_configs":["LOGISTIC_C0.1","LOGISTIC_C1","LOGISTIC_C10","GBRT_D1","GBRT_D2","HISTGB_D2","HISTGB_D3"],
      "selection":"prior matured origins only; lexicographic ties","calibration":"expanding prior-only Platt; minimum 40 predictions",
      "promotion":{"short_brier_gain_vs_p50":0.005,"calibration_intercept_abs_max":0.25,"calibration_slope_range":[0.5,1.5],"second_half_brier_tolerance":0.02},
      "random_seed":20260911,"auto_selector":"OFF","auto_ensemble":"OFF","production_authority":False
    }
    write_json(CONTRACT/"limited_candidate_freeze_v149.json",freeze)
    print(json.dumps({"monthly":meta,"short_inventory":inv["targets"],"short_incremental":inc,"freeze":freeze},indent=2,sort_keys=True))


if __name__=="__main__": main()
