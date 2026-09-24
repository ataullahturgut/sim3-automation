from __future__ import annotations
import argparse, json, os
from pathlib import Path
import daily_midas_clean_pilot_v2 as base

def fit_block_core(p, features, name):
    res={"features":features,"models":{}}
    up=base.walk(p,features,"L2","up")
    dn=base.walk(p,features,"L2","mat_down")
    res["models"]["L2"]={
        "UP":base.periods(up),
        "MAT_DOWN":base.periods(dn),
        "prediction_counts":{"UP":len(up),"MAT_DOWN":len(dn)}
    }
    return res

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIDAS_CLEAN_CORE_V2_RESULT_2026-09-25.json")
    a=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    old=base.fit_block
    base.fit_block=fit_block_core
    try:
        o=base.run(dsn)
    finally:
        base.fit_block=old
    o["identity"]="GOLD_CONTROL_DAILY_MIDAS_CLEAN_CORE_V2_RESEARCH"
    o["method"]["model_families"]=["L2 logistic only (core fast pass)"]
    Path(a.out).write_text(json.dumps(o,indent=2,default=str),encoding="utf-8")
    print(json.dumps({
      "identity":o["identity"],"status":o["status"],
      "calendar_audit":o["calendar_audit"],"results":o["results"],
      "invariants":o["authority_invariants_unchanged"]
    },indent=2,default=str))

if __name__=="__main__": main()
