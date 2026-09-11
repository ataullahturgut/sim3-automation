from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from gold_axis_2026.v149_research.common import canonical_frame_hash,write_json
from gold_axis_2026.v149_research.monthly import build_same_origin_panel,evaluate_monthly_candidates
from gold_axis_2026.v149_research.short_horizon import run_outer

OUT=ROOT/"gold_axis_2026/data_pipeline/audits/v149_research"
FREEZE=ROOT/"gold_axis_2026/v149_research/contracts/limited_candidate_freeze_v149.json"


def main():
    if not FREEZE.exists(): raise RuntimeError("CANDIDATE_FREEZE_NOT_FOUND")
    freeze=json.loads(FREEZE.read_text())
    if not freeze.get("frozen_before_outer_scoring"): raise RuntimeError("GOVERNANCE_FAIL")
    panel,_=build_same_origin_panel(); mout,msum=evaluate_monthly_candidates(panel,freeze["monthly"]["outer_start"])
    mout.to_csv(OUT/"monthly_outer_v149.csv",index=False,float_format="%.12g")
    frames,ssum=run_outer(freeze)
    for key,frame in frames.items(): frame.to_csv(OUT/(key.lower()+"_outer_v149.csv"),index=False,float_format="%.12g")
    payload={"evidence_class":"RETROSPECTIVE_RESEARCH_DIAGNOSTIC_NOT_PROSPECTIVE","monthly":msum,"short_horizon":ssum,"auto_selector":"OFF","auto_ensemble":"OFF","production_authority":False,"production_writes":"NONE","output_hashes":{"monthly":canonical_frame_hash(mout),**{k:canonical_frame_hash(v) for k,v in frames.items()}}}
    write_json(OUT/"v149_outer_results.json",payload)
    print(json.dumps(payload,indent=2,sort_keys=True))


if __name__=="__main__": main()
