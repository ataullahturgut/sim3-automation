from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

TAU=0.50
AGREE_THR=0.80

EXPECTED_COMPETITIVE = [
    "AOA_ELM",
    "BOOST_CATBOOST_ORDERED",
    "BOOST_RANDOM_FOREST_ANCHOR",
    "ChHHO_ANFIS",
    "DE_ABC_RBFNN",
    "FULL7_ANN",
    "LMC2_RBF_M32",
    "PLS1_V1",
    "REDUCED4_ANN",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1",
    "SVR_CURRENT8",
    "SVR_DAILY_SUMMARY12",
    "SVR_MIXED20",
]


def load_json(path):
    return json.loads(Path(path).read_text())


def rows_map(rows):
    return {str(r["target"]):r for r in rows}


def combine_rows(*groups):
    out={}
    for rows in groups:
        for r in rows:
            t=str(r["target"])
            if t in out:
                raise RuntimeError(("DUP_TARGET",t))
            out[t]=r
    return out


def load_all_models(args):
    ref=load_json(args.reference_rows)
    models={}
    for name in ["AOA_ELM","ChHHO_ANFIS","FULL7_ANN","REDUCED4_ANN"]:
        p=ref["models"][name]
        models[name]=combine_rows(p["dev"],p["transport_2025"],p["stress_2026"])

    d=load_json(args.deabc_json)
    models["DE_ABC_RBFNN"]=combine_rows(d["dev"]["rows"],d["transport_2025"]["rows"],d["stress_2026"]["rows"])

    d=load_json(args.gpr_json)
    models["LMC2_RBF_M32"]=combine_rows(d["dev"]["rows"],d["transport_2025"]["rows"],d["stress_2026"]["rows"])

    d=load_json(args.pls_json)
    models["PLS1_V1"]=combine_rows(d["dev"]["rows"],d["holdout_2025"]["rows"],d["stress_2026"]["rows"])

    b=load_json(args.boost_transport_json)
    models["BOOST_CATBOOST_ORDERED"]=combine_rows(
        b["dev_reproduced"]["CATBOOST_ORDERED"],b["transport"]["CATBOOST_ORDERED"]
    )
    models["BOOST_RANDOM_FOREST_ANCHOR"]=combine_rows(
        b["dev_reproduced"]["RANDOM_FOREST_ANCHOR"],b["transport"]["RANDOM_FOREST_ANCHOR"]
    )

    s=load_json(args.svr_transport_json)
    for rep in ["CURRENT8","DAILY_SUMMARY12","MIXED20"]:
        models[f"SVR_{rep}"]=combine_rows(s["dev_reproduced"][rep],s["transport"][rep])

    for p in args.seq_transport_json:
        q=load_json(p)
        name="SEQ_"+q["model_id"]
        models[name]=combine_rows(q["dev_reproduced"],q["transport"])

    if sorted(models)!=sorted(EXPECTED_COMPETITIVE):
        raise RuntimeError(("MODEL_SET_MISMATCH",sorted(models),EXPECTED_COMPETITIVE))
    return models


def exact16_transport_features(models,suppressor):
    frozen_dev_features=suppressor["features"]
    if len(frozen_dev_features)!=33:
        raise RuntimeError(("DEV_FEATURE_COUNT",len(frozen_dev_features)))
    history=[float(r["dispersion_pct"]) for r in frozen_dev_features]

    features=[]
    for target in [f"2025-{m:02d}" for m in range(1,13)] + [f"2026-{m:02d}" for m in range(1,8)]:
        missing=[m for m in EXPECTED_COMPETITIVE if target not in models[m]]
        if missing:
            raise RuntimeError(("MISSING_TRANSPORT_TARGET",target,missing))
        vals=np.asarray([float(models[m][target]["forecast"]) for m in EXPECTED_COMPETITIVE],float)
        base=models["ChHHO_ANFIS"][target]
        rw=float(base["rw"])
        ch=float(base["forecast"])
        med=float(np.median(vals))
        q25,q75=np.quantile(vals,[.25,.75])
        disp=float((q75-q25)/abs(med)*100.0) if med!=0 else np.nan
        dirs=np.sign(vals-rw)
        chdir=np.sign(ch-rw)
        agree=float(np.mean(dirs==chdir)) if chdir!=0 else float(np.mean(dirs==0))
        prior_med=float(np.median(np.asarray(history,float)))
        veto=bool(agree>=AGREE_THR and disp<=prior_med)
        r={
            "target":target,
            "origin":str(base["origin"]),
            "model_count":16,
            "median_fcst":med,
            "dispersion_pct":disp,
            "prior_disp_median":prior_med,
            "chhho_direction_agreement":agree,
            "V2_STRONG_DIRECTION_CONSENSUS":veto,
        }
        features.append(r)
        history.append(disp)
    return features


def all_router_rows(router):
    out=[]
    seen=set()
    for period in ["DEV_2022_04_2024_12","OPENED_2025","OPENED_2026"]:
        for r in router["periods"][period]["rows"]:
            if r["target"] in seen:
                raise RuntimeError(("DUP_ROUTER_TARGET",r["target"]))
            seen.add(r["target"])
            x=dict(r)
            x["router_warn"]=bool(float(x["p_high"])>=TAU)
            out.append(x)
    return sorted(out,key=lambda r:r["target"])


def annotate(rows,features,suppressor):
    fmap={r["target"]:r for r in features}
    devmap={r["target"]:r for r in suppressor["rows"]}
    out=[]
    for r in rows:
        x=dict(r)
        if "2022-04"<=x["target"]<="2024-12":
            d=devmap[x["target"]]
            x["exact16_feature_available"]=True
            x["exact16_veto_eligible"]=bool(d["veto_eligible"])
            x["exact16_veto"]=bool(d["V2_STRONG_DIRECTION_CONSENSUS"])
            x["exact16_dispersion_pct"]=d["dispersion_pct"]
            x["exact16_prior_disp_median"]=d["prior_disp_median"]
            x["exact16_direction_agreement"]=d["chhho_direction_agreement"]
        elif x["target"] in fmap:
            d=fmap[x["target"]]
            x["exact16_feature_available"]=True
            x["exact16_veto_eligible"]=True
            x["exact16_veto"]=bool(d["V2_STRONG_DIRECTION_CONSENSUS"])
            x["exact16_dispersion_pct"]=d["dispersion_pct"]
            x["exact16_prior_disp_median"]=d["prior_disp_median"]
            x["exact16_direction_agreement"]=d["chhho_direction_agreement"]
        else:
            x["exact16_feature_available"]=False
            x["exact16_veto_eligible"]=False
            x["exact16_veto"]=False
            x["exact16_dispersion_pct"]=None
            x["exact16_prior_disp_median"]=None
            x["exact16_direction_agreement"]=None
        x["overlay_warn"]=bool(
            x["router_warn"] and not (
                x["exact16_feature_available"] and x["exact16_veto_eligible"] and x["exact16_veto"]
            )
        )
        out.append(x)
    return out


def subset(rows,a,b):
    return [r for r in rows if a<=r["target"]<=b]


def metrics(rows,field):
    fired=[r for r in rows if bool(r[field])]
    high_all=sum(r["severity"]=="HIGH" for r in rows)
    elev_all=sum(r["severity"] in ("HIGH","MEDIUM") for r in rows)
    hh=sum(r["severity"]=="HIGH" for r in fired)
    mh=sum(r["severity"]=="MEDIUM" for r in fired)
    fc=sum(r["severity"]=="NORMAL" for r in fired)
    return {
        "events":len(fired),
        "high_hits":int(hh),
        "medium_hits":int(mh),
        "false_calls":int(fc),
        "high_recall":None if high_all==0 else float(hh/high_all),
        "elevated_recall":None if elev_all==0 else float((hh+mh)/elev_all),
        "false_call_rate":None if not fired else float(fc/len(fired)),
        "useful_call_rate":None if not fired else float((hh+mh)/len(fired)),
        "event_targets":[r["target"] for r in fired],
    }


def report(rows):
    router=metrics(rows,"router_warn")
    overlay=metrics(rows,"overlay_warn")
    suppressed=[]
    for r in rows:
        if r["router_warn"] and not r["overlay_warn"]:
            suppressed.append({
                "origin":r["origin"],
                "target":r["target"],
                "severity":r["severity"],
                "p_high":float(r["p_high"]),
                "awake_experts":r["awake_experts"],
                "active_signals":r["active_signals"],
                "direction_agreement":r["exact16_direction_agreement"],
                "dispersion_pct":r["exact16_dispersion_pct"],
                "prior_disp_median":r["exact16_prior_disp_median"],
            })
    return {
        "n":len(rows),
        "router":router,
        "overlay":overlay,
        "suppressed":suppressed,
        "false_removed":sum(x["severity"]=="NORMAL" for x in suppressed),
        "high_removed":sum(x["severity"]=="HIGH" for x in suppressed),
        "medium_removed":sum(x["severity"]=="MEDIUM" for x in suppressed),
        "no_feature_targets":[r["target"] for r in rows if not r["exact16_feature_available"]],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--router-json",required=True)
    ap.add_argument("--suppressor-json",required=True)
    ap.add_argument("--reference-rows",required=True)
    ap.add_argument("--deabc-json",required=True)
    ap.add_argument("--gpr-json",required=True)
    ap.add_argument("--pls-json",required=True)
    ap.add_argument("--boost-transport-json",required=True)
    ap.add_argument("--svr-transport-json",required=True)
    ap.add_argument("--seq-transport-json",required=True,nargs=4)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    router=load_json(args.router_json)
    supp=load_json(args.suppressor_json)
    if router["selected_candidate"]["params"]["id"]!="HEDGE_eta0.25_tau0.50":
        raise RuntimeError("ROUTER_NOT_FROZEN")
    if supp["schema"]!="GOLD_MONTHLY_ALARM_FALSE_CALL_SUPPRESSOR_SCREEN_V1_2026-09-30":
        raise RuntimeError("SUPPRESSOR_SCHEMA")

    competitive=supp["scope"]["competitive_models"]
    if competitive!=EXPECTED_COMPETITIVE:
        raise RuntimeError(("COMPETITIVE_ORDER_MISMATCH",competitive,EXPECTED_COMPETITIVE))

    models=load_all_models(args)
    features=exact16_transport_features(models,supp)
    rows=annotate(all_router_rows(router),features,supp)

    dev=report(subset(rows,"2022-04","2024-12"))
    y25=report(subset(rows,"2025-01","2025-12"))
    y26j=report(subset(rows,"2026-01","2026-07"))
    y26a=report(subset(rows,"2026-01","2026-08"))
    opened19=report(subset(rows,"2025-01","2026-07"))
    opened20=report(subset(rows,"2025-01","2026-08"))

    critical={}
    for t in ["2025-02","2025-09","2026-06","2026-08"]:
        r=next(x for x in rows if x["target"]==t)
        critical[t]={
            "origin":r["origin"],
            "severity":r["severity"],
            "router_warn":r["router_warn"],
            "exact16_feature_available":r["exact16_feature_available"],
            "exact16_veto":r["exact16_veto"],
            "overlay_warn":r["overlay_warn"],
            "p_high":float(r["p_high"]),
            "awake_experts":r["awake_experts"],
        }

    # Transport interpretation is frozen and outcome-descriptive only.
    if opened19["high_removed"]>0:
        interpretation="EXACT16_TRANSPORT_HARMFUL"
    elif opened19["medium_removed"]>0:
        interpretation="EXACT16_TRANSPORT_MEDIUM_HARM"
    elif opened19["false_removed"]>=1:
        interpretation="EXACT16_TRANSPORT_SUPPORTIVE"
    else:
        interpretation="EXACT16_TRANSPORT_NEUTRAL"

    out={
        "schema":"GOLD_MONTHLY_EXACT16_SAFE_VETO_TRANSPORT_V1_2026-09-30",
        "status":"COMPLETE",
        "scientific_gate":"PASS",
        "competitive_models":EXPECTED_COMPETITIVE,
        "transport_feature_period":["2025-01","2026-07"],
        "transport_features":features,
        "periods":{
            "DEV_2022_04_2024_12":dev,
            "OPENED_2025":y25,
            "OPENED_2026_JAN_JUL":y26j,
            "OPENED_2026_JAN_AUG_WITH_AUG_PASSTHROUGH":y26a,
            "OPENED_2025_2026_JUL":opened19,
            "OPENED_2025_2026_AUG_WITH_AUG_PASSTHROUGH":opened20,
        },
        "critical_checks":critical,
        "transport_interpretation":interpretation,
        "rows":rows,
        "governance":{
            "missing_model_contracts_changed":False,
            "competitive_pool_changed":False,
            "safe_veto_threshold_changed":False,
            "dispersion_rule_changed":False,
            "router_retuned":False,
            "2025_2026_used_for_selection":False,
            "target_actual_used_in_veto_features":False,
            "production_authorized":False,
        },
    }

    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "transport_interpretation":interpretation,
        "dev":dev,
        "opened_2025":y25,
        "opened_2026_jan_jul":y26j,
        "opened_2025_2026_jul":opened19,
        "opened_2026_jan_aug":y26a,
        "critical_checks":critical,
    },sort_keys=True))


if __name__=="__main__":
    main()
