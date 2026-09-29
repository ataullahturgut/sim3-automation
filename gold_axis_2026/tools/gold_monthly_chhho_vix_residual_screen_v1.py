from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np

import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_f4_b1_transform_parity_v1 as b1

BLOCKS = {
    "VIX_R1_CHANGE": ["vix_change"],
    "VIX_R2_LEVEL_CHANGE": ["vix_level","vix_change"],
    "VIX_R3_FULL_STRESS": ["vix_level","vix_change","vix_vol","vix_spike"],
}

def mshift(m,d):
    return b1.mshift(m,d)

def build_vix_features(external_v2, origins):
    ext=json.loads(Path(external_v2).read_text())
    vix=b1.flat_daily(ext,"vix_daily")
    out={}
    meta={}
    for origin in origins:
        prev=mshift(origin,-1)
        vp,last_p,np_=b1.eligible_month_values(vix,origin,b1.LAGS["VIX"])
        vq,last_q,nq=b1.eligible_month_values(vix,prev,b1.LAGS["VIX"])
        level=float(np.mean(vp))
        change=float(level-np.mean(vq))
        d=np.diff(vp)
        vol=float(np.std(d,ddof=0)) if len(d) else 0.0
        spike=float(np.max(vp)/level)
        out[origin]={
            "vix_level":level,
            "vix_change":change,
            "vix_vol":vol,
            "vix_spike":spike,
        }
        meta[origin]={
            "origin_n":int(np_),"previous_n":int(nq),
            "origin_last":last_p,"previous_last":last_q,
        }
    return ext,out,meta

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    origins=sorted({r["origin"] for r in m["dev"]})
    extdoc,ext,feature_meta=build_vix_features(a.external_v2,origins)

    result={
        "schema":"GOLD_MONTHLY_CHHHO_VIX_RESIDUAL_SCREEN_V1_2026-09-29",
        "authority":{
            "base_model_frozen":True,
            "base_artifact_id":10989389723,
            "external_authority_v2_artifact_id":11028494060,
            "selection":"DEV_2022-04..2024-12_ONLY",
            "2025_used_for_selection":False,
            "2026_used_for_selection":False,
            "random_split":False,
            "neon_reads":0,
            "residual_target":"price residual = actual price - frozen base forecast price",
            "learner":"Ridge",
            "ridge_alpha":core.RIDGE_ALPHA,
            "min_prior_residuals":core.MIN_HISTORY,
            "cap_multiple":core.CAP_MULT,
            "scaler":"StandardScaler fit on prior eligible residual rows only",
            "chronology":"prequential; prior DEV residuals only",
            "vix_release_lag_calendar_days":b1.LAGS["VIX"],
            "feature_definitions":{
                "vix_level":"mean of eligible daily VIX closes in origin month",
                "vix_change":"origin-month VIX mean minus previous-month VIX mean",
                "vix_vol":"population std of first differences of eligible daily VIX closes in origin month",
                "vix_spike":"max eligible daily VIX close divided by origin-month mean VIX",
            },
            "blocks_frozen_before_outcomes":BLOCKS,
        },
        "external_authority_v2_payload_sha256":extdoc.get("payload_sha256"),
        "base_metrics":core.metrics(m["dev"]),
        "feature_meta":feature_meta,
        "blocks":{},
    }

    candidates=[]
    for name,cols in BLOCKS.items():
        corr=core.prequential(m["dev"],ext,cols)
        gate=core.stability_gate(m["dev"],corr)
        full=core.metrics(corr,"corrected_forecast")
        diag=core.diagnostic(m["dev"],ext,cols)
        result["blocks"][name]={
            "columns":cols,
            "full_metrics":full,
            "gate":gate,
            "diagnostics":diag,
            "rows":corr,
        }
        if gate.get("pass"):
            candidates.append((gate["eligible_corrected"]["sum_ae"],name))

    candidates.sort()
    result["selected_on_dev"]=candidates[0][1] if candidates else "BASE"
    result["screen_pass"]=bool(candidates)

    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    summary={
        "base":result["base_metrics"],
        "selected_on_dev":result["selected_on_dev"],
        "blocks":{
            k:{
                "full_sum_ae":v["full_metrics"]["sum_ae"],
                "full_direction":v["full_metrics"]["direction_correct"],
                "gate":v["gate"],
            } for k,v in result["blocks"].items()
        }
    }
    print("CHHHO_VIX_RESIDUAL_SCREEN_GATE=PASS")
    print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    main()
