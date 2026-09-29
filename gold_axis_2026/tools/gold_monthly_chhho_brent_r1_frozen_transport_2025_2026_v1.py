from __future__ import annotations

import argparse, json, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_f4_b1_transform_parity_v1 as b1

COLS=["BRENT_MR1"]
AUG_2026_ACTUAL=4411.0
AUG_2026_RW=4073.0

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
    out={}; meta={}
    for r in rows:
        origin=r["origin"]; pp=b1.mshift(origin,-1)
        if origin not in bundle.gpr_vintages:
            raise RuntimeError(f"GPR_VINTAGE_MISSING {origin}")
        gh=bundle.gpr_vintages[origin]
        z=base.gpr_norm(gh,pp)
        feat,obs=b1.transform_for_sample(series,origin,z)
        out[origin]={"BRENT_MR1":float(feat["BRENT_MR1"])}
        meta[origin]={"z_gpr":float(z),"obs":obs["BRENT"]}
    return extdoc,out,meta,bundle

def direction_ok(row,key):
    return bool(np.sign(float(row[key])-float(row["rw"]))==np.sign(float(row["actual"])-float(row["rw"])))

def decorate(rows):
    out=[]
    for r in rows:
        z=dict(r)
        z["base_abs_error"]=abs(float(z["forecast"])-float(z["actual"]))
        z["corrected_abs_error"]=abs(float(z["corrected_forecast"])-float(z["actual"]))
        z["base_direction_correct"]=direction_ok(z,"forecast")
        z["corrected_direction_correct"]=direction_ok(z,"corrected_forecast")
        out.append(z)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--augsep",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    raw=json.loads(Path(a.chhho).read_text())
    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    aug=json.loads(Path(a.augsep).read_text())
    augrow=next(r for r in aug["rows"] if r["target"]=="2026-08" and r["status"]=="OK")

    rows2025=[dict(r) for r in m["tr"]]
    rows2026=[{
        "target":r["target"],"origin":r["origin"],"forecast":float(r["forecast"]),
        "actual":float(r["actual"]),"rw":float(r["rw"])
    } for r in raw["stress_2026"]["rows"]]
    rows2026.append({
        "target":"2026-08","origin":"2026-07",
        "forecast":float(augrow["base_forecast"]),
        "actual":AUG_2026_ACTUAL,"rw":AUG_2026_RW,
        "actual_source":"World Bank / Commodity Markets Review London PM monthly average"
    })

    allrows=m["dev"]+rows2025+rows2026
    extdoc,ext,meta,bundle=build_brent(a.external_v2,allrows,dsn)

    corr25,fit25=core.freeze_fit_apply(m["dev"],rows2025,ext,COLS)
    corr26,fit26=core.freeze_fit_apply(m["dev"],rows2026,ext,COLS)
    if fit25!=fit26: raise RuntimeError("FROZEN_FIT_MISMATCH")
    corr25=decorate(corr25); corr26=decorate(corr26)

    b25=core.metrics(rows2025); c25=core.metrics(corr25,"corrected_forecast")
    b26=core.metrics(rows2026); c26=core.metrics(corr26,"corrected_forecast")

    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv=base.authority_invariants(cur)
    if inv!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
      "schema":"GOLD_MONTHLY_CHHHO_BRENT_R1_FROZEN_TRANSPORT_2025_2026_V1_2026-09-29",
      "authority":{
        "selected_on_dev":"BRENT_R1_MR1",
        "selection_run":36590486319,
        "base_model_frozen":True,
        "base_artifact_id":10989389723,
        "feature":"BRENT_MR1",
        "feature_definition":"log(mean eligible Brent in origin month / mean eligible Brent in previous month)",
        "release_lag_calendar_days":b1.LAGS["BRENT"],
        "learner":"Ridge",
        "ridge_alpha":core.RIDGE_ALPHA,
        "cap_multiple":core.CAP_MULT,
        "fit_period":"DEV 2022-04..2024-12 only",
        "2025_residual_updating":False,
        "2026_residual_updating":False,
        "random_split":False,
        "database_access":"READ_ONLY",
        "september_2026":"BLOCKED_CANONICAL_BASE_MISSING_AUGUST_FOUR_METAL_ORIGIN_INPUTS"
      },
      "frozen_fit":fit25,
      "metrics":{
        "2025":{
          "base":b25,"corrected":c25,
          "sum_ae_improvement":float(b25["sum_ae"]-c25["sum_ae"]),
          "direction_delta":int(c25["direction_correct"]-b25["direction_correct"])
        },
        "2026_jan_aug":{
          "base":b26,"corrected":c26,
          "sum_ae_improvement":float(b26["sum_ae"]-c26["sum_ae"]),
          "direction_delta":int(c26["direction_correct"]-b26["direction_correct"])
        }
      },
      "rows_2025":corr25,
      "rows_2026_jan_aug":corr26,
      "brent_feature_meta":meta,
      "authority_invariants_before":bundle.invariants_before,
      "authority_invariants_after":inv,
      "september_2026":{
        "status":"BLOCKED",
        "reason":"Canonical ChHHO BASE requires August Gold/Silver/Platinum/Palladium origin inputs."
      }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_BRENT_R1_FROZEN_TRANSPORT_GATE=PASS")
    print(json.dumps({
      "frozen_fit":fit25,"metrics":out["metrics"],
      "rows_2025":corr25,"rows_2026_jan_aug":corr26,
      "september_2026":out["september_2026"]
    },sort_keys=True))

if __name__=="__main__":
    main()
