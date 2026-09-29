from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np

import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_f4_b1_transform_parity_v1 as b1

COLS=["vix_change"]
AUG_2026_ACTUAL=4411.0
AUG_2026_RW=4073.0

def build_vix_change(external_v2, origins):
    doc=json.loads(Path(external_v2).read_text())
    vix=b1.flat_daily(doc,"vix_daily")
    out={}
    meta={}
    for origin in sorted(set(origins)):
        prev=b1.mshift(origin,-1)
        vp,last_p,np_=b1.eligible_month_values(vix,origin,b1.LAGS["VIX"])
        vq,last_q,nq=b1.eligible_month_values(vix,prev,b1.LAGS["VIX"])
        out[origin]={"vix_change":float(np.mean(vp)-np.mean(vq))}
        meta[origin]={
            "origin_mean":float(np.mean(vp)),
            "previous_mean":float(np.mean(vq)),
            "origin_n":int(np_),"previous_n":int(nq),
            "origin_last":last_p,"previous_last":last_q,
        }
    return doc,out,meta

def direction_ok(row, forecast_key):
    return bool(np.sign(float(row[forecast_key])-float(row["rw"])) ==
                np.sign(float(row["actual"])-float(row["rw"])))

def summarize(rows, forecast_key):
    m=core.metrics(rows, forecast_key)
    return m

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
        "target":"2026-08",
        "origin":"2026-07",
        "forecast":float(augrow["base_forecast"]),
        "actual":AUG_2026_ACTUAL,
        "rw":AUG_2026_RW,
        "actual_source":"World Bank / Commodity Markets Review London PM monthly average, as recorded in GOLD_MONTHLY_2026_AUG_SEP_LIVE_AUDIT_2026-09-26.md",
    })

    origins=[r["origin"] for r in m["dev"]+rows2025+rows2026]
    extdoc,ext,meta=build_vix_change(a.external_v2,origins)

    corr25,fit25=core.freeze_fit_apply(m["dev"],rows2025,ext,COLS)
    corr26,fit26=core.freeze_fit_apply(m["dev"],rows2026,ext,COLS)

    if fit25 != fit26:
        raise RuntimeError("FROZEN_FIT_MISMATCH")

    corr25=decorate(corr25)
    corr26=decorate(corr26)

    b25=summarize(rows2025,"forecast")
    c25=summarize(corr25,"corrected_forecast")
    b26=summarize(rows2026,"forecast")
    c26=summarize(corr26,"corrected_forecast")

    out={
      "schema":"GOLD_MONTHLY_CHHHO_VIX_R1_FROZEN_TRANSPORT_2025_2026_V1_2026-09-29",
      "authority":{
        "selected_on_dev":"VIX_R1_CHANGE",
        "selection_run":36585834751,
        "selection_artifact":11041975865,
        "base_model_frozen":True,
        "base_artifact_id":10989389723,
        "residual_target":"actual price - frozen BASE forecast price",
        "feature":"vix_change = origin-month mean eligible VIX - previous-month mean eligible VIX",
        "vix_release_lag_calendar_days":b1.LAGS["VIX"],
        "learner":"Ridge",
        "ridge_alpha":core.RIDGE_ALPHA,
        "cap_multiple":core.CAP_MULT,
        "scaler":"StandardScaler fit on full DEV only",
        "fit_period":"DEV 2022-04..2024-12 only",
        "2025_residual_updating":False,
        "2026_residual_updating":False,
        "random_split":False,
        "neon_reads":0,
        "september_2026":"BLOCKED_CANONICAL_BASE_MISSING_AUGUST_FOUR_METAL_ORIGIN_INPUTS",
      },
      "external_authority_v2_payload_sha256":extdoc.get("payload_sha256"),
      "frozen_fit":fit25,
      "metrics":{
        "2025":{
          "base":b25,"corrected":c25,
          "sum_ae_improvement":float(b25["sum_ae"]-c25["sum_ae"]),
          "direction_delta":int(c25["direction_correct"]-b25["direction_correct"]),
        },
        "2026_jan_aug":{
          "base":b26,"corrected":c26,
          "sum_ae_improvement":float(b26["sum_ae"]-c26["sum_ae"]),
          "direction_delta":int(c26["direction_correct"]-b26["direction_correct"]),
        }
      },
      "rows_2025":corr25,
      "rows_2026_jan_aug":corr26,
      "vix_feature_meta":meta,
      "september_2026":{
        "status":"BLOCKED",
        "reason":"Canonical ChHHO BASE requires August Gold/Silver/Platinum/Palladium origin inputs; governed canonical four-metal history is incomplete for August.",
      }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_VIX_R1_FROZEN_TRANSPORT_GATE=PASS")
    print(json.dumps({
      "frozen_fit":fit25,
      "metrics":out["metrics"],
      "rows_2025":corr25,
      "rows_2026_jan_aug":corr26,
      "september_2026":out["september_2026"],
    },sort_keys=True))

if __name__=="__main__":
    main()
