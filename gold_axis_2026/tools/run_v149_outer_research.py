from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from gold_axis_2026.v149_research.common import canonical_frame_hash,sha256_file,write_json
from gold_axis_2026.v149_research.monthly import build_same_origin_panel,evaluate_monthly_candidates,monthly_audit
from gold_axis_2026.v149_research.short_horizon import run_outer

OUT=ROOT/"gold_axis_2026/data_pipeline/audits/v149_research"
FREEZE=ROOT/"gold_axis_2026/v149_research/contracts/limited_candidate_freeze_v149.json"


def main():
    if not FREEZE.exists(): raise RuntimeError("CANDIDATE_FREEZE_NOT_FOUND")
    freeze=json.loads(FREEZE.read_text())
    if not freeze.get("frozen_before_outer_scoring"): raise RuntimeError("GOVERNANCE_FAIL")
    panel,_=build_same_origin_panel(); mout,msum=evaluate_monthly_candidates(panel,freeze["monthly"]["outer_start"])
    full_monthly_diagnostic=monthly_audit(panel,development_end="2026-07")
    full_monthly_diagnostic["use_for_candidate_selection"]=False
    full_monthly_diagnostic["label"]="POST_FREEZE_FULL_RETROSPECTIVE_DIAGNOSTIC"
    write_json(OUT/"monthly_complementarity_full_v149.json",full_monthly_diagnostic)
    mout.to_csv(OUT/"monthly_outer_v149.csv",index=False,float_format="%.12g")
    frames,ssum=run_outer(freeze)
    for key,frame in frames.items(): frame.to_csv(OUT/(key.lower()+"_outer_v149.csv"),index=False,float_format="%.12g")
    code_sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    payload={
      "run_metadata":{
        "code_sha":code_sha,
        "manifest_version":"1.49",
        "manifest_sha256":sha256_file(ROOT/"gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md"),
        "candidate_freeze_sha256":sha256_file(FREEZE),
        "input_fingerprints":{
          "monthly_frozen_replay":sha256_file(ROOT/"gold_axis_2026/production_closure/production_history_43.csv"),
          "monthly_core5_diagnostic_not_pit":sha256_file(ROOT/"gold_axis_2026/core5_monthly.csv.gz.b64"),
          "short_ny17_context_replay":sha256_file(ROOT/"gold_axis_2026/data_pipeline/audits/component_role_replays_v145/ny17_context_role_replay_v145.csv")
        },
        "monthly_origins":mout.forecast_origin.astype(str).tolist(),
        "monthly_targets":mout.target_month.astype(str).tolist(),
        "short_origins":{k:v.origin_date.dt.strftime("%Y-%m-%d").tolist() for k,v in frames.items()},
        "short_targets":{k:v.target_date.dt.strftime("%Y-%m-%d").tolist() for k,v in frames.items()}
      },
      "evidence_class":"RETROSPECTIVE_RESEARCH_DIAGNOSTIC_NOT_PROSPECTIVE","monthly":msum,"short_horizon":ssum,
      "auto_selector":"OFF","auto_ensemble":"OFF","production_authority":False,"production_writes":"NONE",
      "output_hashes":{"monthly":canonical_frame_hash(mout),**{k:canonical_frame_hash(v) for k,v in frames.items()}}
    }
    write_json(OUT/"v149_outer_results.json",payload)
    print(json.dumps(payload,indent=2,sort_keys=True))


if __name__=="__main__": main()
