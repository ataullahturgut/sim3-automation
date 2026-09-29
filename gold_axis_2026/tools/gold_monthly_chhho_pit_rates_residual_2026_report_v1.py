from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np

import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_external_pit_residual_v1 as pit

COLS=pit.BLOCKS["PIT_RATES"]

def load_extension(path):
    d=json.loads(Path(path).read_text())
    lev={r["origin_month"]:(float(r["dgs10"]),float(r["dff"])) for r in d["rows"]}
    ext={}
    months=sorted(lev)
    for m in months:
        y,mo=map(int,m.split("-"))
        z=y*12+mo-2
        p=f"{z//12:04d}-{z%12+1:02d}"
        if p not in lev:
            continue
        dg=lev[m][0]-lev[p][0]
        df=lev[m][1]-lev[p][1]
        ext[m]={
            "dgs10_change":float(dg),
            "dff_change":float(df),
            "curve_proxy_change":float(dg-df),
        }
    return d,ext

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--pit",required=True)
    ap.add_argument("--extension",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    raw=json.loads(Path(a.chhho).read_text())
    snap,ext=pit.load_ext(a.pit)
    exdoc,ext26=load_extension(a.extension)
    ext.update(ext26)

    stress=[{
      "target":r["target"],"origin":r["origin"],"forecast":float(r["forecast"]),
      "actual":float(r["actual"]),"rw":float(r["rw"])
    } for r in raw["stress_2026"]["rows"]]

    corrected,fit=core.freeze_fit_apply(m["dev"],stress,ext,COLS)
    bmet=core.metrics(stress)
    cmet=core.metrics(corrected,"corrected_forecast")

    rows=[]
    for b,c in zip(stress,corrected):
        rows.append({
          "target":b["target"],"origin":b["origin"],"actual":b["actual"],"rw":b["rw"],
          "base_forecast":b["forecast"],"correction":c["correction"],
          "corrected_forecast":c["corrected_forecast"],
          "base_abs_error":abs(b["forecast"]-b["actual"]),
          "corrected_abs_error":abs(c["corrected_forecast"]-b["actual"]),
          "base_direction_correct":bool(np.sign(b["forecast"]-b["rw"])==np.sign(b["actual"]-b["rw"])),
          "corrected_direction_correct":bool(np.sign(c["corrected_forecast"]-b["rw"])==np.sign(b["actual"]-b["rw"])),
          "rates_features":ext[b["origin"]],
        })

    out={
      "schema":"GOLD_MONTHLY_CHHHO_PIT_RATES_RESIDUAL_2026_REPORT_V1_2026-09-29",
      "authority":{
        "base_model":"frozen ChHHO-ANFIS authority artifact 10989389723",
        "residual_fit":"DEV 2022-04..2024-12 only",
        "2025_used_in_residual_fit":False,
        "2026_used_in_residual_fit":False,
        "residual_target":"price residual actual-base_forecast",
        "features":COLS,
        "ridge_alpha":core.RIDGE_ALPHA,
        "cap_multiple":core.CAP_MULT,
        "scaler":"StandardScaler fit on DEV only",
        "transport_rule":"frozen DEV fit applied to 2026; no updating from 2025 or 2026 residuals",
        "pit_snapshot":snap["schema"],
        "pit_extension":exdoc["schema"],
      },
      "fit":fit,
      "base_metrics":bmet,
      "corrected_metrics":cmet,
      "improvement":{
        "sum_abs_error":float(bmet["sum_ae"]-cmet["sum_ae"]),
        "mae":float(bmet["mae"]-cmet["mae"]),
        "direction_delta":int(cmet["direction_correct"]-bmet["direction_correct"]),
      },
      "rows":rows,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_PIT_RATES_2026_REPORT_GATE=PASS")
    print(json.dumps({
      "base_metrics":bmet,
      "corrected_metrics":cmet,
      "improvement":out["improvement"],
      "fit":fit,
      "rows":rows
    },sort_keys=True))

if __name__=="__main__": main()
