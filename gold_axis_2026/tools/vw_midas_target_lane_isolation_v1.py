from __future__ import annotations

import json, math, os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import vw_midas_estimator_headswap_v1 as hs
import vw_midas_fmrvr_v1 as fmr

START, END = "2022-04", "2026-07"
DEV_END = "2024-12"

SPECS = {
    "MSVR": ("MSVR", None, {"C":1.0,"epsilon":0.05,"gamma_scale":0.5}),
    "FMRVR": 2.5,
    "PLS2": ("PLS2", None, {"n_components":4}),
}

def make_core_samples(b, samples):
    out={}
    for k,(x,y) in samples.items():
        p=base.month_shift(k,-1)
        if k not in b.core_gold or p not in b.core_gold:
            continue
        yy=np.asarray(y,float).copy()
        yy[0]=math.log(float(b.core_gold[k])/float(b.core_gold[p]))
        out[k]=(np.asarray(x,float).copy(),yy)
    return out

def predict_model(samples,t,m):
    if m=="FMRVR":
        pred,n,_,_=fmr.fit_predict(samples,t,SPECS[m])
        return float(pred[0]),n
    pred,n=hs.predict_gold(samples,t,*SPECS[m])
    return float(pred),n

def eval_lane(b, raw_cache, lane):
    rows=[]
    for t in base.month_range(START,END):
        samples=raw_cache[t] if lane=="STAK_TO_STAK" else make_core_samples(b,raw_cache[t])
        if t not in samples:
            raise RuntimeError(f"{lane} TARGET_NOT_AVAILABLE {t}")
        p=base.month_shift(t,-1)
        if lane=="STAK_TO_STAK":
            anchor=float(b.monthly_metal["Gold"][p]); actual=float(b.monthly_metal["Gold"][t])
        else:
            anchor=float(b.core_gold[p]); actual=float(b.core_gold[t])
        r={"target":t,"origin":p,"anchor":anchor,"actual":actual}
        for m in ("MSVR","FMRVR","PLS2"):
            phat,n=predict_model(samples,t,m)
            fc=anchor*math.exp(phat)
            r[m]={"pred_logret":phat,"forecast":fc,"ape_pct":100*abs(fc-actual)/actual,"train_rows":n}
        rows.append(r)
    return rows

def metric(rows,m,a,z):
    rr=[{"target":r["target"],"forecast":r[m]["forecast"],"actual":r["actual"],"rw":r["anchor"]}
        for r in rows if a<=r["target"]<=z]
    return base.metrics(rr)

def summarize(rows):
    out={}
    periods=[("DEV","2022-04","2024-12"),("2025","2025-01","2025-12"),("2026","2026-01","2026-07")]
    for label,a,z in periods:
        out[label]={m:metric(rows,m,a,z) for m in ("MSVR","FMRVR","PLS2")}
    return out

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    raw_cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(START,END)}
    stak=eval_lane(b,raw_cache,"STAK_TO_STAK")
    core=eval_lane(b,raw_cache,"CORE5_TO_CORE5")

    # Direct bridge comparison for each model/year.
    comp={}
    for period,a,z in [("DEV","2022-04","2024-12"),("2025","2025-01","2025-12"),("2026","2026-01","2026-07")]:
        comp[period]={}
        for m in ("MSVR","FMRVR","PLS2"):
            sm=metric(stak,m,a,z); cm=metric(core,m,a,z)
            comp[period][m]={
                "stak_mape_pct":sm["mape_pct"],
                "core5_mape_pct":cm["mape_pct"],
                "core5_minus_stak_mape_pp":cm["mape_pct"]-sm["mape_pct"],
                "stak_mae":sm["mae"],"core5_mae":cm["mae"],
                "stak_direction_accuracy_pct":sm["direction_accuracy_pct"],
                "core5_direction_accuracy_pct":cm["direction_accuracy_pct"],
            }

    out={
        "model_id":"VW_MIDAS_TARGET_LANE_ISOLATION_V1",
        "authority":{
            "database_access":"READ_ONLY",
            "x_feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "model_specs":"FROZEN_FROM_PREVIOUS_PRE2025_SELECTION_NO_RETUNING",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
        },
        "definitions":{
            "STAK_TO_STAK":"Gold y[0]=StakTrakr monthly Gold return; anchor/actual=StakTrakr monthly Gold",
            "CORE5_TO_CORE5":"Gold y[0]=CORE5 monthly Gold return; anchor/actual=CORE5 Gold; Silver/Pt/Pd outputs remain frozen StakTrakr targets",
        },
        "stak_to_stak":{"summary":summarize(stak),"rows":stak},
        "core5_to_core5":{"summary":summarize(core),"rows":core},
        "comparison":comp,
    }
    Path("vw_midas_target_lane_isolation_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"comparison":comp},sort_keys=True))

if __name__=="__main__": main()
