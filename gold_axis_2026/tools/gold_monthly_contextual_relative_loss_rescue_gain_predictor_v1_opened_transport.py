from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from gold_monthly_contextual_high_alarm_rescueability_v1 import MODELS, load_models, load

NUM = [
    "p_high","p_elevated","semantic_probability","direction_agreement",
    "dispersion_pct","chhho_abs_median_gap_pct","chhho_iqr_distance",
    "chhho_forecast_percentile","active_signal_count","awake_expert_count",
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage1-json",required=True)
    ap.add_argument("--state-json",required=True)
    ap.add_argument("--exact16-json",required=True)
    ap.add_argument("--reference-rows",required=True)
    ap.add_argument("--deabc-json",required=True)
    ap.add_argument("--gpr-json",required=True)
    ap.add_argument("--pls-json",required=True)
    ap.add_argument("--boost-json",required=True)
    ap.add_argument("--svr-json",required=True)
    ap.add_argument("--seq-cnnlstm-lb3",required=True)
    ap.add_argument("--seq-cnnlstm-lb6",required=True)
    ap.add_argument("--seq-lstm-lb3",required=True)
    ap.add_argument("--seq-lstm-lb6",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    dev=load(a.stage1_json)
    if len(dev["rows"])!=33 or dev["models"]!=MODELS:
        raise RuntimeError("STAGE1_FREEZE_MISMATCH")
    alts=[m for m in MODELS if m!="ChHHO_ANFIS"]
    fc=load_models(a)

    targets=[f"2025-{m:02d}" for m in range(1,13)]+[f"2026-{m:02d}" for m in range(1,8)]
    for m in MODELS:
        miss=[t for t in targets if t not in fc[m]]
        if miss: raise RuntimeError(("MISSING_OPENED_MODEL_ROWS",m,miss))

    exact=load(a.exact16_json)
    xmap={str(r["target"]):r for r in exact["rows"] if str(r["target"]) in targets}
    state=load(a.state_json)
    smap={str(r["target"]):r for r in state["periods"]["opened_2025_2026"]["EXPANDING_REFIT"]["rows"] if str(r["target"]) in targets}
    if len(xmap)!=19 or len(smap)!=19:
        raise RuntimeError(("OPENED_CONTEXT_COVERAGE",len(xmap),len(smap)))

    opened=[]
    for t in targets:
        xr=xmap[t]; sr=smap[t]
        actual=float(fc["ChHHO_ANFIS"][t]["actual"])
        ch=float(fc["ChHHO_ANFIS"][t]["forecast"])
        ch_ae=abs(ch-actual)
        forecasts={m:float(fc[m][t]["forecast"]) for m in MODELS}
        aes={m:abs(forecasts[m]-actual) for m in MODELS}
        farr=np.asarray([forecasts[m] for m in MODELS],float)
        med=float(np.median(farr)); q25,q75=np.quantile(farr,[.25,.75]); iqr=float(q75-q25)
        opened.append({
            "target":t,"router_warn":bool(xr["router_warn"]),"severity":xr["severity"],
            "p_high":float(xr["p_high"]),"p_elevated":float(xr["p_elevated"]),
            "semantic_probability":float(sr["semantic_probability"]),
            "direction_agreement":float(xr["exact16_direction_agreement"]),
            "dispersion_pct":float(xr["exact16_dispersion_pct"]),
            "chhho_abs_median_gap_pct":abs(ch-med)/abs(med)*100.0 if med else 0.0,
            "chhho_iqr_distance":abs(ch-med)/iqr if iqr>1e-12 else 0.0,
            "chhho_forecast_percentile":float((np.sum(farr<ch)+.5*np.sum(farr==ch))/len(farr)),
            "active_signal_count":len(xr["active_signals"]),
            "awake_expert_count":len(xr["awake_experts"]),
            "actual":actual,"chhho_forecast":ch,"chhho_ae":ch_ae,
            "model_forecasts":forecasts,"model_ae":aes,
            "semantic_label":sr["semantic_label"],"state_category":sr["state_category"],
        })

    Xtr=pd.DataFrame([{
        "p_high":float(r["p_high"]),"p_elevated":float(r["p_elevated"]),
        "semantic_probability":float(r["semantic_probability"]),
        "direction_agreement":float(r["direction_agreement"]),
        "dispersion_pct":float(r["dispersion_pct"]),
        "chhho_abs_median_gap_pct":float(r["chhho_abs_median_gap_pct"]),
        "chhho_iqr_distance":float(r["chhho_iqr_distance"]),
        "chhho_forecast_percentile":float(r["chhho_forecast_percentile"]),
        "active_signal_count":float(len(r["active_signals"])),
        "awake_expert_count":float(len(r["awake_experts"])),
    } for r in dev["rows"]])
    Xop=pd.DataFrame([{k:float(r[k]) for k in NUM} for r in opened])
    Y=np.asarray([
        [float(r["rescue_gain"][m])/max(abs(float(r["chhho_forecast"])),1e-9) for m in alts]
        for r in dev["rows"]
    ],float)

    # Frozen DEV research leader: RIDGE_CORE_A10 + DIRECT_SWITCH.
    pipe=Pipeline([
        ("pre",ColumnTransformer([("num",StandardScaler(),NUM)],remainder="drop",sparse_threshold=0)),
        ("ridge",Ridge(alpha=10.0,fit_intercept=True)),
    ])
    pipe.fit(Xtr,Y)
    pred=np.asarray(pipe.predict(Xop),float)

    records=[]
    for i,r in enumerate(opened):
        j=int(np.argmax(pred[i])); m=alts[j]
        pred_gain=float(pred[i,j]*abs(r["chhho_forecast"]))
        action="SWITCH" if (r["router_warn"] and pred_gain>0) else "KEEP"
        used=float(r["model_forecasts"][m]) if action=="SWITCH" else float(r["chhho_forecast"])
        ae=abs(used-r["actual"])
        records.append({
            "target":r["target"],"severity":r["severity"],"router_warn":r["router_warn"],
            "action":action,"chosen_model":m,"pred_gain_usd":pred_gain,
            "actual_gain_vs_keep":float(r["chhho_ae"]-ae),"action_ae":float(ae),
            "chhho_ae":float(r["chhho_ae"]),"semantic_label":r["semantic_label"],
            "state_category":r["state_category"],
        })

    warn=[r for r in records if r["router_warn"]]
    if len(warn)!=12:
        raise RuntimeError(("OPENED_WARNING_COUNT",len(warn)))
    keep=float(sum(r["chhho_ae"] for r in warn))
    policy=float(sum(r["action_ae"] for r in warn))
    gain=keep-policy
    beneficial=sum(r["action"]=="SWITCH" and r["actual_gain_vs_keep"]>1e-9 for r in warn)
    harmful=sum(r["action"]=="SWITCH" and r["actual_gain_vs_keep"]<-1e-9 for r in warn)
    worst=max([0.0]+[-r["actual_gain_vs_keep"] for r in warn if r["action"]=="SWITCH" and r["actual_gain_vs_keep"]<0])

    out={
        "schema":"GOLD_MONTHLY_CONTEXTUAL_RELATIVE_LOSS_RESCUE_GAIN_PREDICTOR_V1_OPENED_TRANSPORT_2026-10-01",
        "status":"COMPLETE","selection_frozen_from_dev":True,
        "predictor":"RIDGE_CORE_A10","policy":"DIRECT_SWITCH","alpha":10.0,
        "coverage":{"opened":["2025-01","2026-07"],"months":19,"warning_n":12,
                    "2026_08":"EXCLUDED_FULL16_UNAVAILABLE"},
        "keep_sum_ae":keep,"policy_sum_ae":policy,"gain_vs_keep":gain,
        "beneficial_switches":beneficial,"harmful_switches":harmful,
        "worst_incremental_harm":float(worst),
        "action_counts":dict(Counter(r["action"] for r in warn)),
        "chosen_model_counts":dict(Counter(r["chosen_model"] for r in warn if r["action"]=="SWITCH")),
        "warning_rows":warn,
        "governance":{"retuned_on_opened":False,"feature_set_changed":False,"alpha_changed":False,
                      "policy_changed":False,"production_authorized":False},
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    md=[
        "# GOLD MONTHLY — Rescue-Gain Predictor V1 Opened Transport","",
        "**Date:** 2026-10-01  ",
        "**Status:** COMPLETE / FROZEN DEV LEADER / OPENED TRANSPORT ONLY / NO PRODUCTION SWITCH","",
        "- frozen predictor: **RIDGE_CORE_A10**",
        "- frozen policy: **DIRECT_SWITCH**",
        "- opened coverage: **2025-01..2026-07**",
        "- warning months: **12**",
        f"- KEEP ΣAE: **{keep:.2f} USD**",
        f"- frozen selector ΣAE: **{policy:.2f} USD**",
        f"- gain vs KEEP: **{gain:+.2f} USD**",
        f"- beneficial / harmful switches: **{beneficial} / {harmful}**",
        f"- worst incremental harm: **{worst:.2f} USD**","",
        "The frozen selector improves cumulative opened warning-month AE, but tail risk remains material. In particular, 2026-03 is a shared-hard month where the frozen selector switches and suffers a large incremental loss. Production switching remains unauthorized.","",
        "## Warning-month actions","",
        "| Target | Severity | Action | Challenger | Pred gain | Actual gain vs KEEP |",
        "|---|---|---|---|---:|---:|",
    ]
    for r in warn:
        md.append(f"| {r['target']} | {r['severity']} | {r['action']} | {r['chosen_model']} | {r['pred_gain_usd']:+.2f} | {r['actual_gain_vs_keep']:+.2f} |")
    Path(a.output_md).write_text("\n".join(md)+"\n")
    print("OPENED_TRANSPORT_COMPLETE")
    print(json.dumps({"keep":keep,"policy":policy,"gain":gain,"beneficial":beneficial,"harmful":harmful,"worst_harm":worst},sort_keys=True))

if __name__=="__main__":
    main()
