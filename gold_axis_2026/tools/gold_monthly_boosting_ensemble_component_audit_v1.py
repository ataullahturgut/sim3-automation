#!/usr/bin/env python3
from __future__ import annotations

import json, os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage5_regularization_v1 as s5

DEV_START, DEV_END="2022-04","2024-12"

SPECS={
    "CATBOOST_PRICE":("CATBOOST_PRICE","CB_R0_BASELINE"),
    "CATBOOST_BALANCED":("CATBOOST_BALANCED","CB_R0_BASELINE"),
    "GBRT":("GBRT_PRICE_BALANCED","G_R0_BASELINE"),
    "LIGHTGBM":("LIGHTGBM_PRICE_BALANCED","L_R0_BASELINE"),
    "XGB_DIRECTION":("XGBOOST_DIRECTION","X_R1_L2_5"),
    "RF":("RF_COMPARATOR","R_R0_BASELINE"),
}

REFS={
    "CATBOOST_PRICE":(1460.433935309605,20),
    "CATBOOST_BALANCED":(1481.261937710369,22),
    "GBRT":(1500.42946858865,22),
    "LIGHTGBM":(1534.6087211346264,22),
    "XGB_DIRECTION":(1679.8371517758826,23),
    "RF":(1491.5506937156672,20),
}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in targets}

    out={}
    for name,(lane_name,profile_name) in SPECS.items():
        lane=next(x for x in s5.LANES if x["lane"]==lane_name)
        profile,reg=next(x for x in lane["profiles"] if x[0]==profile_name)
        r=s5.evaluate(b,cache,lane,profile,reg)
        m=r["metrics"]; refae,refdir=REFS[name]
        if abs(float(m["sum_abs_error"])-refae)>1e-8 or int(m["direction_correct"])!=refdir:
            raise RuntimeError(f"REPRO_FAIL {name} {m}")
        out[name]=r

    actual=np.asarray([x["actual"] for x in out["CATBOOST_PRICE"]["rows"]],float)
    rw=np.asarray([x["rw"] for x in out["CATBOOST_PRICE"]["rows"]],float)
    names=list(SPECS)

    signed_errors={}
    corr={}
    for name in names:
        rows=out[name]["rows"]
        if [r["target"] for r in rows] != targets:
            raise RuntimeError(f"ALIGN_FAIL {name}")
        f=np.asarray([r["forecast"] for r in rows],float)
        signed_errors[name]=f-actual

    C=np.corrcoef(np.column_stack([signed_errors[n] for n in names]),rowvar=False)
    for i,a in enumerate(names):
        corr[a]={b:float(C[i,j]) for j,b in enumerate(names)}

    leader="CATBOOST_PRICE"
    leader_dirs=np.asarray([r["direction_correct"] for r in out[leader]["rows"]],bool)
    comp={}
    for name in names:
        if name==leader: continue
        dirs=np.asarray([r["direction_correct"] for r in out[name]["rows"]],bool)
        disagree=dirs!=leader_dirs
        comp[name]={
            "direction_disagreements_vs_leader":int(disagree.sum()),
            "rescues_leader_misses":int(np.sum((~leader_dirs)&dirs)),
            "loses_leader_hits":int(np.sum(leader_dirs&(~dirs))),
            "both_correct":int(np.sum(leader_dirs&dirs)),
            "both_wrong":int(np.sum((~leader_dirs)&(~dirs))),
        }

    # Pairwise monthly absolute-error wins.
    ae={}
    for name in names:
        f=np.asarray([r["forecast"] for r in out[name]["rows"]],float)
        ae[name]=np.abs(f-actual)
    pairwise={}
    for a in names:
        pairwise[a]={}
        for bname in names:
            pairwise[a][bname]={
                "a_better":int(np.sum(ae[a]<ae[bname]-1e-12)),
                "tie":int(np.sum(np.isclose(ae[a],ae[bname],rtol=0,atol=1e-12))),
                "b_better":int(np.sum(ae[bname]<ae[a]-1e-12)),
            }

    payload={
        "scope":"BOOSTING_ENSEMBLE_COMPONENT_AUDIT_PRE_FREEZE_V1",
        "dev":f"{DEV_START}..{DEV_END}",
        "contract":{
            "ensemble_predictions_computed":False,
            "purpose":"component role/diversity audit only",
            "random_split":"NONE",
            "2025_role":"NOT_OPENED_NOT_EVALUATED",
            "2026_role":"QUARANTINED_NOT_USED",
            "database":"READ_ONLY",
        },
        "component_metrics":{n:out[n]["metrics"] for n in names},
        "signed_error_correlation":corr,
        "direction_complementarity_vs_catboost_price":comp,
        "pairwise_monthly_ae":pairwise,
        "rows":{n:out[n]["rows"] for n in names},
    }
    Path("gold_monthly_boosting_ensemble_component_audit_v1_result.json").write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "component_metrics":payload["component_metrics"],
        "signed_error_correlation":corr,
        "direction_complementarity_vs_catboost_price":comp,
    },sort_keys=True))

if __name__=="__main__":
    main()
