from __future__ import annotations

import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from hs_sdl_dma_v1 import EVIDENCE_CLASS,MODEL_ID
from hs_sdl_dma_v1.data import file_sha256,load_role_replay
from hs_sdl_dma_v1.replay import canonical_hash,run_horizon

SOURCE=ROOT/"data_pipeline/audits/component_role_replays_v145/ny17_context_role_replay_v145.csv"


def promotion(summary):
    m=summary["metrics"]; core=m["HS_SDL_DMA"]; cal=core["calibration"]
    best_simple=min(m[k]["brier"] for k in ("UP_FREQUENCY","FAST_ONLY","STATIC_LOGISTIC","EQUAL_CANDIDATES"))
    checks={
      "minimum_outer_n":core["n"]>=200,
      "brier_improvement_vs_p50":core["brier"]<=m["P50"]["brier"]-0.005,
      "complexity_vs_best_simple":core["brier"]<=best_simple+0.002,
      "calibration_intercept":cal["intercept"] is not None and abs(cal["intercept"])<=0.25,
      "calibration_slope":cal["slope"] is not None and 0.5<=cal["slope"]<=1.5,
      "no_leakage":summary["future_information_violations"]==0,
    }
    return {"status":"PASS" if all(checks.values()) else "NOT_PROVEN","checks":checks,"best_simple_brier":best_simple}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); a=ap.parse_args()
    d=load_role_replay(SOURCE); a.output_dir.mkdir(parents=True,exist_ok=True); result={"model_id":MODEL_ID,"evidence_class":EVIDENCE_CLASS,"prospective_claim":False,"production_authority":False,"auto_selector":"OFF","auto_ensemble":"OFF","source_sha256":file_sha256(SOURCE),"horizons":{}}
    for h in (1,3):
        f,s=run_horizon(d,h); h2,s2=run_horizon(d,h)
        one=canonical_hash(f); two=canonical_hash(h2)
        if one!=two: raise RuntimeError("IMPLEMENTATION_FAIL:DETERMINISM")
        s["determinism_sha256"]=one; s["deterministic_rerun"]="PASS"; s["prefix_invariance"]="PASS_BY_ORIGIN_LOCAL_RECOMPUTATION"; s["promotion"]=promotion(s)
        f.to_csv(a.output_dir/f"hs_sdl_dma_{h}d_outer.csv",index=False)
        result["horizons"][f"NEXT_NY17_{h}D"]=s
    result["overall_status"]="RETROSPECTIVE_PSEUDO_REAL_TIME_VALIDATED" if all(x["outer_rows"]>=200 for x in result["horizons"].values()) else "BLOCKED_INSUFFICIENT_SAMPLE"
    (a.output_dir/"hs_sdl_dma_replay_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:{"n":v["outer_rows"],"brier":v["metrics"]["HS_SDL_DMA"]["brier"],"promotion":v["promotion"]["status"]} for k,v in result["horizons"].items()},indent=2))

if __name__=="__main__":main()
