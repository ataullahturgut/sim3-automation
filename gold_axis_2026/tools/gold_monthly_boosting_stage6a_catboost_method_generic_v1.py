#!/usr/bin/env python3
import argparse, json, hashlib, os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import gold_monthly_boosting_stage6a_meta_screen_v1 as core

METHODS = [
    "PSO","GA","DE","MPA","ABC","SSA","GWO","WOA","HHO","ACO","BAT",
    "FA","MFO","FPA","FA_FPA","CS","SCA","SALP","SMA","GOA","ALO","TLBO",
    "JAYA","HGS","CHOA","HGSO","AOA","CPA","KRILL","CROW","DE_ABC","MULTISWARM",
    "CHHHO_PW_PM4"
]

def run_method(method):
    if method not in METHODS:
        raise SystemExit(f"Unsupported method: {method}")
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle=core.base.load_data(dsn)
    cache={t:core.base.all_samples_at_origin(bundle,t,governed=True) for t in core.DEV_ANCHORS}
    rows=[]

    for ai,target in enumerate(core.DEV_ANCHORS,1):
        data=core.prepare_anchor(bundle,cache[target],target,"CATBOOST")

        vtheta,vloss,vcalls=core.run_optimizer("VANILLA","CATBOOST",target,data)
        vdiag=core.outer_diag("CATBOOST",data,vtheta)
        rows.append({
            "lane":"CATBOOST","method":"VANILLA","anchor":target,
            "inner_relative_sum_abs_error":float(vloss),
            "ratio_vs_vanilla":1.0,
            "objective_calls":vcalls,
            "outer_diagnostic":vdiag,
        })

        print(f"PROGRESS method={method} anchor={ai}/{len(core.DEV_ANCHORS)} target={target} start", flush=True)
        theta,loss,calls=core.run_optimizer(method,"CATBOOST",target,data)
        diag=core.outer_diag("CATBOOST",data,theta)
        rows.append({
            "lane":"CATBOOST","method":method,"anchor":target,
            "inner_relative_sum_abs_error":float(loss),
            "ratio_vs_vanilla":float(loss/max(vloss,1e-12)),
            "objective_calls":calls,
            "outer_diagnostic":diag,
        })
        print(f"PROGRESS method={method} anchor={ai}/{len(core.DEV_ANCHORS)} target={target} complete", flush=True)

    after=core.read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    def summarize(m):
        rr=[r for r in rows if r["method"]==m]
        ratios=np.asarray([r["ratio_vs_vanilla"] for r in rr],float)
        outer_ae=np.asarray([r["outer_diagnostic"]["absolute_error"] for r in rr],float)
        dirs=np.asarray([r["outer_diagnostic"]["direction_correct"] for r in rr],bool)
        return {
            "method":m,
            "anchors":len(rr),
            "mean_ratio_vs_vanilla":float(np.mean(ratios)),
            "median_ratio_vs_vanilla":float(np.median(ratios)),
            "worst_ratio_vs_vanilla":float(np.max(ratios)),
            "anchors_better_than_vanilla":int(np.sum(ratios < 1.0-1e-12)),
            "outer_anchor_sum_abs_error_diagnostic":float(np.sum(outer_ae)),
            "outer_anchor_direction_correct_diagnostic":int(np.sum(dirs)),
        }

    payload={
        "scope":"BOOSTING_STAGE6A_CATBOOST_METHOD_JOB_GENERIC_V1",
        "lane":"CATBOOST",
        "method":method,
        "anchors":list(core.DEV_ANCHORS),
        "budget":{"population_reference":core.POP_SIZE,"hard_objective_calls":core.MAX_EVALS,
                  "generations_ceiling":core.GENERATIONS,"repeats_per_anchor":1},
        "authority":{"database":"READ_ONLY","random_split":"NONE",
                     "2025_role":"NOT_OPENED_NOT_EVALUATED","2026_role":"NOT_OPENED_NOT_EVALUATED"},
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "rows":rows,
        "vanilla":summarize("VANILLA"),
        "result":summarize(method),
    }
    payload["payload_sha256"]=hashlib.sha256(
        json.dumps(rows,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()

    out=Path(f"gold_monthly_boosting_stage6a_catboost_{method.lower()}_result.json")
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "method":method,
        "result":payload["result"],
        "vanilla":payload["vanilla"],
        "payload_sha256":payload["payload_sha256"],
    },sort_keys=True), flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=METHODS)
    args=ap.parse_args()
    run_method(args.method)

if __name__=="__main__":
    main()
