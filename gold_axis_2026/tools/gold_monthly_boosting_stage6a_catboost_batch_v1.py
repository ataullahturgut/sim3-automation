#!/usr/bin/env python3
import argparse, json, hashlib, math, os, sys
from pathlib import Path
import numpy as np
import psycopg

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import gold_monthly_boosting_stage6a_meta_screen_v1 as core

BATCHES = {
    1: ["PSO","GA","DE","MPA","ABC"],
    2: ["SSA","GWO","WOA","HHO","ACO","BAT"],
    3: ["FA","MFO","FPA","FA_FPA","CS","SCA"],
    4: ["SALP","SMA","GOA","ALO","TLBO","JAYA"],
    5: ["HGS","CHOA","HGSO","AOA","CPA","KRILL"],
    6: ["CROW","DE_ABC","MULTISWARM","CHHHO_PW_PM4"],
}

def checkpoint_path(batch):
    return Path(f"gold_monthly_boosting_stage6a_catboost_batch{batch}_result.json")

def write_checkpoint(batch, methods, rows, status):
    summary=[]
    for method in ["VANILLA"] + methods:
        rr=[r for r in rows if r["method"]==method]
        if not rr:
            continue
        ratios=np.asarray([r["ratio_vs_vanilla"] for r in rr],float)
        outer_ae=np.asarray([r["outer_diagnostic"]["absolute_error"] for r in rr],float)
        dirs=np.asarray([r["outer_diagnostic"]["direction_correct"] for r in rr],bool)
        summary.append({
            "method":method,
            "anchors":len(rr),
            "mean_ratio_vs_vanilla":float(np.mean(ratios)),
            "median_ratio_vs_vanilla":float(np.median(ratios)),
            "worst_ratio_vs_vanilla":float(np.max(ratios)),
            "anchors_better_than_vanilla":int(np.sum(ratios < 1.0-1e-12)),
            "outer_anchor_sum_abs_error_diagnostic":float(np.sum(outer_ae)),
            "outer_anchor_direction_correct_diagnostic":int(np.sum(dirs)),
        })
    ranking=sorted(summary,key=lambda z:(z["mean_ratio_vs_vanilla"],z["median_ratio_vs_vanilla"],z["worst_ratio_vs_vanilla"],z["method"]))
    payload={
        "scope":"BOOSTING_STAGE6A_CATBOOST_BATCH_V1",
        "lane":"CATBOOST",
        "batch":batch,
        "methods":["VANILLA"]+methods,
        "anchors":list(core.DEV_ANCHORS),
        "budget":{"population_reference":core.POP_SIZE,"hard_objective_calls":core.MAX_EVALS,
                  "generations_ceiling":core.GENERATIONS,"repeats_per_anchor":1},
        "authority":{"database":"READ_ONLY","random_split":"NONE",
                     "2025_role":"NOT_OPENED_NOT_EVALUATED","2026_role":"NOT_OPENED_NOT_EVALUATED"},
        "status":status,
        "rows":rows,
        "summary":summary,
        "ranking":ranking,
    }
    payload["payload_sha256"]=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    checkpoint_path(batch).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return payload

def run_batch(batch):
    methods=BATCHES[batch]
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle=core.base.load_data(dsn)
    cache={t:core.base.all_samples_at_origin(bundle,t,governed=True) for t in core.DEV_ANCHORS}
    rows=[]
    total=len(core.DEV_ANCHORS)*(1+len(methods))
    done=0
    write_checkpoint(batch,methods,rows,"IN_PROGRESS")
    for ai,target in enumerate(core.DEV_ANCHORS,1):
        data=core.prepare_anchor(bundle,cache[target],target,"CATBOOST")
        print(f"PROGRESS batch={batch} anchor={ai}/{len(core.DEV_ANCHORS)} target={target} method=VANILLA start",flush=True)
        vtheta,vloss,vcalls=core.run_optimizer("VANILLA","CATBOOST",target,data)
        vdiag=core.outer_diag("CATBOOST",data,vtheta)
        rows.append({"lane":"CATBOOST","batch":batch,"method":"VANILLA","anchor":target,
                     "inner_relative_sum_abs_error":float(vloss),"ratio_vs_vanilla":1.0,
                     "objective_calls":vcalls,"outer_diagnostic":vdiag})
        done+=1
        write_checkpoint(batch,methods,rows,"IN_PROGRESS")
        print(f"PROGRESS done={done}/{total} batch={batch} anchor={ai}/{len(core.DEV_ANCHORS)} method=VANILLA",flush=True)
        for mi,method in enumerate(methods,1):
            print(f"PROGRESS batch={batch} anchor={ai}/{len(core.DEV_ANCHORS)} target={target} method={mi}/{len(methods)}:{method} start",flush=True)
            theta,loss,calls=core.run_optimizer(method,"CATBOOST",target,data)
            diag=core.outer_diag("CATBOOST",data,theta)
            rows.append({"lane":"CATBOOST","batch":batch,"method":method,"anchor":target,
                         "inner_relative_sum_abs_error":float(loss),
                         "ratio_vs_vanilla":float(loss/max(vloss,1e-12)),
                         "objective_calls":calls,"outer_diagnostic":diag})
            done+=1
            write_checkpoint(batch,methods,rows,"IN_PROGRESS")
            print(f"PROGRESS done={done}/{total} batch={batch} anchor={ai}/{len(core.DEV_ANCHORS)} method={mi}/{len(methods)}:{method} complete",flush=True)
    after=core.read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    payload=write_checkpoint(batch,methods,rows,"PASS")
    payload["authority_invariants_before"]=bundle.invariants_before
    payload["authority_invariants_after"]=after
    checkpoint_path(batch).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"batch":batch,"top":payload["ranking"][:6],"payload_sha256":payload["payload_sha256"]},sort_keys=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--batch",type=int,required=True,choices=sorted(BATCHES))
    args=ap.parse_args()
    run_batch(args.batch)

if __name__=="__main__":
    main()
