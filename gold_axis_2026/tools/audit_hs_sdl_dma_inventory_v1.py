from __future__ import annotations

import argparse, json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hs_sdl_dma_v1.data import build_targets,file_sha256,load_role_replay

DEFAULT=ROOT/"data_pipeline/audits/component_role_replays_v145/ny17_context_role_replay_v145.csv"


def build(path:Path)->dict:
    d=load_role_replay(path)
    inventory=[]
    specs={
      "FAST":("fast_state","DIRECTION_CAPABLE","PASS"),
      "SLOW":("slow_state","DIRECTION_CAPABLE","PASS"),
      "MONTHLY_DIRECTION_3M":("monthly_direction_3m","DIRECTION_CAPABLE","PASS"),
      "EMERGENCY_LEVEL":("emergency_level","CONTEXT_ONLY","PASS_NOT_ADMITTED_INITIAL_CORE"),
      "EMERGENCY_REVERSAL":("emergency_reversal","CONTEXT_ONLY","PASS_NOT_ADMITTED_INITIAL_CORE"),
      "BOCPD_RETURN_SUCCESSOR_V1":(None,"CONTEXT_ONLY","BLOCKED_PIT_DAILY_ORIGIN_PANEL_NOT_PROVEN"),
      "GVZ_RISK":(None,"CONTEXT_ONLY","BLOCKED_PIT_EXACT_ASOF_JOIN_NOT_IN_DIRECTION_PANEL"),
      "MACRO_EVENT_SUCCESSOR_V2":(None,"CONTEXT_ONLY","BLOCKED_PIT_RELEASE_ASOF_DAILY_PANEL_NOT_PROVEN"),
    }
    for engine,(field,role,status) in specs.items():
        inventory.append({
          "engine_id":engine,"role":role,"historical_field":field or "NOT_FOUND_IN_PANEL",
          "value_type":"CATEGORICAL" if field else "NOT_PROVEN",
          "coverage_start":d.date.min().strftime("%Y-%m-%d") if field else None,
          "coverage_end":d.date.max().strftime("%Y-%m-%d") if field else None,
          "rows":int(len(d)) if field else 0,
          "missing":int(d[field].isna().sum()) if field else None,
          "levels":sorted(d[field].astype(str).unique().tolist()) if field else [],
          "pit_reconstructibility":status,
          "evidence_lineage":str(path.relative_to(ROOT)) if field else "NOT_PROVEN",
        })
    targets={}
    for h in (1,3):
        t=build_targets(d,h)
        targets[f"NEXT_NY17_{h}D"]={"matured_rows":int(len(t)),"first_origin":t.origin_date.min().strftime("%Y-%m-%d"),"last_origin":t.origin_date.max().strftime("%Y-%m-%d"),"last_target":t.target_date.max().strftime("%Y-%m-%d")}
    return {
      "audit_id":"HS_SDL_DMA_HISTORICAL_INVENTORY_V1","status":"PASS_DIRECTION_CORE_WITH_CONTEXT_PIT_EXCLUSIONS",
      "source_artifact":str(path.relative_to(ROOT)),"source_sha256":file_sha256(path),
      "origin_rows":int(len(d)),"origin_start":d.date.min().strftime("%Y-%m-%d"),"origin_end":d.date.max().strftime("%Y-%m-%d"),
      "duplicate_origins":int(d.date.duplicated().sum()),"targets":targets,"inventory":inventory,
      "core_feature_schema":"PASS_DIRECTION_ONLY","context_interactions":"NOT_ADMITTED_INITIAL_CORE",
      "database_access":"READ_ONLY_SEPARATE_CURRENT_STATE_SNAPSHOT","database_writes":"NONE","prospective_claim":False
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,default=DEFAULT); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    out=build(a.input); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"STATUS={out['status']}"); print(f"ORIGINS={out['origin_rows']}"); print(f"1D={out['targets']['NEXT_NY17_1D']['matured_rows']}"); print(f"3D={out['targets']['NEXT_NY17_3D']['matured_rows']}")

if __name__=="__main__": main()
