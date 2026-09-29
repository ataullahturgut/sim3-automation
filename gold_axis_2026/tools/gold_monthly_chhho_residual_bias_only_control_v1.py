from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import gold_monthly_external_driver_residual_v1 as core

AUG_2026_ACTUAL=4411.0
AUG_2026_RW=4073.0

def prequential_bias(rows):
    out=[]
    for i,r in enumerate(rows):
        z=dict(r); z["correction"]=0.0; z["corrected_forecast"]=float(r["forecast"]); z["eligible"]=False
        prior=rows[:i]
        if len(prior)>=core.MIN_HISTORY:
            y=np.asarray([q["actual"]-q["forecast"] for q in prior],float)
            pred=float(np.mean(y))
            cap=core.CAP_MULT*float(np.median(np.abs(y)))
            pred=float(np.clip(pred,-cap,cap))
            z["correction"]=pred
            z["corrected_forecast"]=float(r["forecast"]+pred)
            z["eligible"]=True
        out.append(z)
    return out

def frozen_bias(dev,rows):
    y=np.asarray([q["actual"]-q["forecast"] for q in dev],float)
    pred=float(np.mean(y))
    cap=core.CAP_MULT*float(np.median(np.abs(y)))
    pred=float(np.clip(pred,-cap,cap))
    out=[]
    for r in rows:
        z=dict(r); z["correction"]=pred; z["corrected_forecast"]=float(r["forecast"]+pred); out.append(z)
    return out,{"n":len(dev),"mean_residual":float(np.mean(y)),"cap":cap,"correction":pred}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--augsep",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    raw=json.loads(Path(a.chhho).read_text())
    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    aug=json.loads(Path(a.augsep).read_text())
    augrow=next(r for r in aug["rows"] if r["target"]=="2026-08" and r["status"]=="OK")

    devcorr=prequential_bias(m["dev"])
    devgate=core.stability_gate(m["dev"],devcorr)

    rows2025=[dict(r) for r in m["tr"]]
    rows2026=[{"target":r["target"],"origin":r["origin"],"forecast":float(r["forecast"]),"actual":float(r["actual"]),"rw":float(r["rw"])} for r in raw["stress_2026"]["rows"]]
    rows2026.append({"target":"2026-08","origin":"2026-07","forecast":float(augrow["base_forecast"]),"actual":AUG_2026_ACTUAL,"rw":AUG_2026_RW})

    c25,fit=frozen_bias(m["dev"],rows2025)
    c26,fit2=frozen_bias(m["dev"],rows2026)
    if fit!=fit2: raise RuntimeError("FIT_MISMATCH")

    bdev=core.metrics(m["dev"]); cdev=core.metrics(devcorr,"corrected_forecast")
    b25=core.metrics(rows2025); m25=core.metrics(c25,"corrected_forecast")
    b26=core.metrics(rows2026); m26=core.metrics(c26,"corrected_forecast")

    out={
      "schema":"GOLD_MONTHLY_CHHHO_RESIDUAL_BIAS_ONLY_CONTROL_V1_2026-09-29",
      "authority":{
        "purpose":"Determine whether external residual gains exceed a plain historical mean-residual correction",
        "dev_selection_use":False,
        "learner":"no external features; prior mean residual with same minimum history and cap",
        "min_prior_residuals":core.MIN_HISTORY,
        "cap_multiple":core.CAP_MULT,
        "transport_fit":"full DEV mean residual only",
        "2025_2026_updating":False
      },
      "dev":{"base":bdev,"bias_corrected":cdev,"gate":devgate},
      "frozen_fit":fit,
      "transport_2025":{"base":b25,"bias_corrected":m25,"improvement":float(b25["sum_ae"]-m25["sum_ae"])},
      "transport_2026_jan_aug":{"base":b26,"bias_corrected":m26,"improvement":float(b26["sum_ae"]-m26["sum_ae"])},
      "rows_dev":devcorr,"rows_2025":c25,"rows_2026":c26
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_RESIDUAL_BIAS_ONLY_CONTROL_GATE=PASS")
    print(json.dumps({
      "dev":out["dev"],"frozen_fit":fit,
      "transport_2025":out["transport_2025"],
      "transport_2026_jan_aug":out["transport_2026_jan_aug"]
    },sort_keys=True))
if __name__=="__main__": main()
