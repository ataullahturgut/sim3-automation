from __future__ import annotations

import argparse, json, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_external_pit_residual_v1 as pit
import gold_monthly_f4_b1_transform_parity_v1 as b1

RATES_COLS=["dgs10_change","dff_change","curve_proxy_change"]
BRENT_COLS=["BRENT_MR1"]
COMBINED_COLS=RATES_COLS+BRENT_COLS

def build_brent(external_v2, rows, dsn):
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
        origin=r["origin"]; pp=b1.mshift(origin,-1)
        gh=bundle.gpr_vintages[origin]
        z=base.gpr_norm(gh,pp)
        feat,obs=b1.transform_for_sample(series,origin,z)
        out[origin]={"BRENT_MR1":float(feat["BRENT_MR1"])}
        meta[origin]={"z_gpr":float(z),"obs":obs["BRENT"]}
    return extdoc,out,meta,bundle

def merge_ext(rates,brent,origins):
    out={}
    for o in origins:
        z={}
        z.update(rates.get(o,{}))
        z.update(brent.get(o,{}))
        out[o]=z
    return out

def run_block(rows,ext,cols):
    corr=core.prequential(rows,ext,cols)
    return {
      "columns":cols,
      "full_metrics":core.metrics(corr,"corrected_forecast"),
      "gate":core.stability_gate(rows,corr),
      "diagnostics":core.diagnostic(rows,ext,cols),
      "rows":corr,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--pit-rates",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    pitsnap,rates=pit.load_ext(a.pit_rates)
    extdoc,brent,brent_meta,bundle=build_brent(a.external_v2,m["dev"],dsn)
    origins=[r["origin"] for r in m["dev"]]
    ext=merge_ext(rates,brent,origins)

    blocks={
      "RATES_CONTROL":run_block(m["dev"],ext,RATES_COLS),
      "BRENT_CONTROL":run_block(m["dev"],ext,BRENT_COLS),
      "RATES_PLUS_BRENT":run_block(m["dev"],ext,COMBINED_COLS),
    }

    base_m=core.metrics(m["dev"])
    ranked=[]
    for name,z in blocks.items():
        if z["gate"].get("pass"):
            ranked.append((z["gate"]["eligible_corrected"]["sum_ae"],name))
    ranked.sort()

    result={
      "schema":"GOLD_MONTHLY_CHHHO_RATES_PLUS_BRENT_RESIDUAL_SCREEN_V1_2026-09-29",
      "authority":{
        "base_model_frozen":True,
        "base_artifact_id":10989389723,
        "selection":"DEV_2022-04..2024-12_ONLY",
        "2025_used_for_selection":False,
        "2026_used_for_selection":False,
        "random_split":False,
        "database_access":"READ_ONLY",
        "learner":"Ridge",
        "ridge_alpha":core.RIDGE_ALPHA,
        "min_prior_residuals":core.MIN_HISTORY,
        "cap_multiple":core.CAP_MULT,
        "chronology":"prequential; prior DEV residuals only",
        "rates_representation":"strict-PIT dgs10_change + dff_change + curve_proxy_change",
        "brent_representation":"BRENT_MR1 selected independently before combination",
        "combined_columns":COMBINED_COLS,
        "combination_opened_only_after_brent_isolated_pass":True,
      },
      "pit_rates_schema":pitsnap.get("schema"),
      "external_authority_v2_payload_sha256":extdoc.get("payload_sha256"),
      "base_metrics":base_m,
      "brent_feature_meta":brent_meta,
      "blocks":blocks,
      "selected_on_dev":ranked[0][1] if ranked else "BASE",
    }

    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv=base.authority_invariants(cur)
    if inv!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    result["authority_invariants_before"]=bundle.invariants_before
    result["authority_invariants_after"]=inv

    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_RATES_PLUS_BRENT_RESIDUAL_SCREEN_GATE=PASS")
    print(json.dumps({
      "base":base_m,
      "selected_on_dev":result["selected_on_dev"],
      "blocks":{
        k:{
          "full_sum_ae":v["full_metrics"]["sum_ae"],
          "full_direction":v["full_metrics"]["direction_correct"],
          "gate":v["gate"],
        } for k,v in blocks.items()
      }
    },sort_keys=True))

if __name__=="__main__":
    main()
