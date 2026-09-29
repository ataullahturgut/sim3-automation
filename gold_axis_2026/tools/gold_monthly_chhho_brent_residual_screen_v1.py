from __future__ import annotations

import argparse, json, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_f4_b1_transform_parity_v1 as b1

BLOCKS={
    "BRENT_R1_MR1":["BRENT_MR1"],
    "BRENT_R2_VW":["BRENT_VW"],
    "BRENT_R3_MR1_VW":["BRENT_MR1","BRENT_VW"],
}

def build_brent_features(external_v2, rows, dsn):
    extdoc=json.loads(Path(external_v2).read_text())
    series={
        "NOM10":b1.nested_daily(extdoc,"h15_daily","DGS10"),
        "REAL10":b1.nested_daily(extdoc,"h15_daily","DFII10"),
        "BROADUSD":b1.nested_daily(extdoc,"h10_daily","BROAD_USD_INDEX"),
        "VIX":b1.flat_daily(extdoc,"vix_daily"),
        "NDX":b1.flat_daily(extdoc,"nasdaq100_daily"),
        "WTI":b1.flat_daily(extdoc,"wti_daily"),
        "BRENT":b1.flat_daily(extdoc,"brent_daily"),
    }
    bundle=base.load_data(dsn)
    out={}
    meta={}
    for r in rows:
        target=r["target"]; origin=r["origin"]; pp=b1.mshift(origin,-1)
        if origin not in bundle.gpr_vintages:
            raise RuntimeError(f"GPR_VINTAGE_MISSING {origin}")
        gh=bundle.gpr_vintages[origin]
        z=base.gpr_norm(gh,pp)
        feat,obs=b1.transform_for_sample(series,origin,z)
        out[origin]={
            "BRENT_MR1":float(feat["BRENT_MR1"]),
            "BRENT_VW":float(feat["BRENT_VW"]),
        }
        meta[origin]={
            "target":target,
            "z_gpr":float(z),
            "obs":obs["BRENT"],
        }
    return extdoc,out,meta,bundle

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    extdoc,ext,feature_meta,bundle=build_brent_features(a.external_v2,m["dev"],dsn)

    result={
      "schema":"GOLD_MONTHLY_CHHHO_BRENT_RESIDUAL_SCREEN_V1_2026-09-29",
      "authority":{
        "base_model_frozen":True,
        "base_artifact_id":10989389723,
        "external_authority_v2_artifact_id":11028494060,
        "selection":"DEV_2022-04..2024-12_ONLY",
        "2025_used_for_selection":False,
        "2026_used_for_selection":False,
        "random_split":False,
        "database_access":"READ_ONLY",
        "residual_target":"price residual = actual price - frozen base forecast price",
        "learner":"Ridge",
        "ridge_alpha":core.RIDGE_ALPHA,
        "min_prior_residuals":core.MIN_HISTORY,
        "cap_multiple":core.CAP_MULT,
        "scaler":"StandardScaler fit on prior eligible residual rows only",
        "chronology":"prequential; prior DEV residuals only",
        "brent_release_lag_calendar_days":b1.LAGS["BRENT"],
        "feature_definitions":{
          "BRENT_MR1":"log(mean eligible Brent in origin month / mean eligible Brent in previous month)",
          "BRENT_VW":"GPR-weighted daily Brent log-return summary using exact CURRENT8 weighting formula"
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

    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv=base.authority_invariants(cur)
    if inv!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    result["authority_invariants_before"]=bundle.invariants_before
    result["authority_invariants_after"]=inv

    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_BRENT_RESIDUAL_SCREEN_GATE=PASS")
    print(json.dumps({
      "base":result["base_metrics"],
      "selected_on_dev":result["selected_on_dev"],
      "blocks":{
        k:{
          "full_sum_ae":v["full_metrics"]["sum_ae"],
          "full_direction":v["full_metrics"]["direction_correct"],
          "gate":v["gate"],
        } for k,v in result["blocks"].items()
      }
    },sort_keys=True))

if __name__=="__main__":
    main()
