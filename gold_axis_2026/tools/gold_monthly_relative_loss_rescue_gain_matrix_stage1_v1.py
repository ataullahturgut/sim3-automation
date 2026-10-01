from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

from gold_monthly_contextual_high_alarm_rescueability_v1 import MODELS, load_models, load

def corr(a,b):
    aa=[]; bb=[]
    for x,y in zip(a,b):
        if x is not None and y is not None and np.isfinite(float(x)) and np.isfinite(float(y)):
            aa.append(float(x)); bb.append(float(y))
    if len(aa)<3 or np.std(aa)<1e-12 or np.std(bb)<1e-12:
        return None
    return float(np.corrcoef(aa,bb)[0,1])

def summarize(rows):
    base=float(sum(r["chhho_ae"] for r in rows))
    ranked=[]
    for m in MODELS:
        if m=="ChHHO_ANFIS": continue
        ae=float(sum(r["model_ae"][m] for r in rows))
        gains=[r["rescue_gain"][m] for r in rows]
        ranked.append({
            "model":m,"n":len(rows),"chhho_sum_ae":base,"model_sum_ae":ae,
            "gain_vs_chhho":base-ae,"wins":sum(g>1e-9 for g in gains),
            "win_rate":sum(g>1e-9 for g in gains)/len(rows),
            "median_gain":float(np.median(gains))
        })
    ranked.sort(key=lambda z:(-z["gain_vs_chhho"],-z["wins"],z["model"]))
    best_alt=float(sum(min(r["model_ae"][m] for m in MODELS if m!="ChHHO_ANFIS") for r in rows))
    keep_best=float(sum(min(r["chhho_ae"],min(r["model_ae"][m] for m in MODELS if m!="ChHHO_ANFIS")) for r in rows))
    return {
        "n":len(rows),"chhho_sum_ae":base,"fixed_challengers":ranked,
        "oracle_best_alt_gain":base-best_alt,
        "oracle_keep_or_best_gain":base-keep_best,
        "best_alt_frequency":dict(Counter(r["best_alt_model"] for r in rows)),
        "mean_alternatives_better":float(np.mean([r["alternatives_better"] for r in rows]))
    }

def main():
    ap=argparse.ArgumentParser()
    for name in ["router-json","state-json","exact16-json","reference-rows","deabc-json","gpr-json","pls-json","boost-json","svr-json",
                 "seq-cnnlstm-lb3","seq-cnnlstm-lb6","seq-lstm-lb3","seq-lstm-lb6","output-json","output-md"]:
        ap.add_argument("--"+name, required=True)
    a=ap.parse_args()

    fc=load_models(a)
    exact=load(a.exact16_json)
    state=load(a.state_json)
    if exact["competitive_models"] != MODELS:
        raise RuntimeError("EXACT16_MODEL_POOL_MISMATCH")

    targets=sorted(fc["ChHHO_ANFIS"])
    targets=[t for t in targets if "2022-04" <= t <= "2024-12"]
    if len(targets)!=33:
        raise RuntimeError(("DEV_TARGET_COUNT",len(targets)))
    for m in MODELS:
        if any(t not in fc[m] for t in targets):
            raise RuntimeError(("MISSING_MODEL_DEV",m))

    xmap={str(r["target"]):r for r in exact["rows"] if "2022-04"<=str(r["target"])<="2024-12"}
    smap={str(r["target"]):r for r in state["periods"]["dev_2022_04_2024_12"]["EXPANDING_REFIT"]["rows"]}

    rows=[]
    for t in targets:
        xr=xmap[t]; sr=smap[t]
        actual=float(fc["ChHHO_ANFIS"][t]["actual"])
        ch=float(fc["ChHHO_ANFIS"][t]["forecast"])
        ch_ae=abs(ch-actual)
        forecasts={m:float(fc[m][t]["forecast"]) for m in MODELS}
        aes={m:abs(forecasts[m]-actual) for m in MODELS}
        gains={m:ch_ae-aes[m] for m in MODELS if m!="ChHHO_ANFIS"}
        vals=sorted([(m,aes[m],gains[m]) for m in gains], key=lambda z:z[1])
        farr=np.asarray([forecasts[m] for m in MODELS],float)
        med=float(np.median(farr)); q25,q75=np.quantile(farr,[.25,.75]); iqr=float(q75-q25)
        rows.append({
            "origin":xr["origin"],"target":t,"severity":xr["severity"],"router_warn":bool(xr["router_warn"]),
            "p_high":float(xr["p_high"]),"p_elevated":float(xr["p_elevated"]),
            "active_signals":xr["active_signals"],"awake_experts":xr["awake_experts"],
            "actual":actual,"chhho_forecast":ch,"chhho_ae":ch_ae,
            "semantic_label":sr["semantic_label"],"state_category":sr["state_category"],
            "transition_v2_status":sr["transition_v2_status"],"extreme_status":sr["extreme_status"],
            "origin_regime_ood":bool(sr["origin_regime_ood"]),
            "direction_agreement":xr.get("exact16_direction_agreement"),
            "dispersion_pct":xr.get("exact16_dispersion_pct"),
            "chhho_abs_median_gap_pct":abs(ch-med)/abs(med)*100 if med else None,
            "chhho_iqr_distance":abs(ch-med)/iqr if iqr>1e-12 else None,
            "chhho_forecast_percentile":float((np.sum(farr<ch)+.5*np.sum(farr==ch))/len(farr)),
            "model_forecasts":forecasts,"model_ae":aes,"rescue_gain":gains,
            "best_alt_model":vals[0][0],"best_alt_ae":vals[0][1],"best_alt_gain":vals[0][2],
            "alternatives_better":sum(g>1e-9 for g in gains.values())
        })

    warn=[r for r in rows if r["router_warn"]]
    elev=[r for r in warn if r["severity"]!="NORMAL"]
    false=[r for r in warn if r["severity"]=="NORMAL"]
    non=[r for r in rows if not r["router_warn"]]
    if (len(warn),len(elev),len(false),len(non)) != (20,10,10,13):
        raise RuntimeError("WARNING_PARTITION_MISMATCH")

    contexts={}
    for key,fn in {
        "semantic_label":lambda r:r["semantic_label"],
        "state_category":lambda r:r["state_category"],
        "transition_v2_status":lambda r:r["transition_v2_status"],
        "ood":lambda r:"OOD" if r["origin_regime_ood"] else "IN_DOMAIN",
    }.items():
        groups=defaultdict(list)
        for r in warn: groups[str(fn(r))].append(r)
        contexts[key]=[]
        for val,sub in sorted(groups.items()):
            contexts[key].append({
                "value":val,"n":len(sub),"elevated_n":sum(r["severity"]!="NORMAL" for r in sub),
                "mean_best_alt_gain":float(np.mean([r["best_alt_gain"] for r in sub])),
                "mean_alternatives_better":float(np.mean([r["alternatives_better"] for r in sub])),
                "keep_main_hindsight_n":sum(r["best_alt_gain"]<=0 for r in sub)
            })

    y=[r["best_alt_gain"] for r in warn]
    feature_corr={
        "p_high":corr([r["p_high"] for r in warn],y),
        "direction_agreement":corr([r["direction_agreement"] for r in warn],y),
        "dispersion_pct":corr([r["dispersion_pct"] for r in warn],y),
        "chhho_abs_median_gap_pct":corr([r["chhho_abs_median_gap_pct"] for r in warn],y),
        "chhho_iqr_distance":corr([r["chhho_iqr_distance"] for r in warn],y),
        "chhho_forecast_percentile":corr([r["chhho_forecast_percentile"] for r in warn],y)
    }

    out={
        "schema":"GOLD_MONTHLY_RELATIVE_LOSS_RESCUE_GAIN_MATRIX_STAGE1_V1_2026-10-01",
        "status":"COMPLETE","scientific_gate":"PASS","selection_authority":"DEV_ONLY",
        "coverage":{"dev":["2022-04","2024-12"],"n":33,"warning_n":20,"elevated_warning_n":10,"false_warning_n":10,"nonwarning_n":13},
        "models":MODELS,"main_model":"ChHHO_ANFIS",
        "gain_definition":"abs_error_ChHHO - abs_error_challenger; positive means challenger beats ChHHO",
        "periods":{
            "ALL_DEV_33":summarize(rows),"WARNING_20":summarize(warn),
            "ELEVATED_WARNING_10":summarize(elev),"FALSE_WARNING_10":summarize(false),"NONWARNING_13":summarize(non)
        },
        "warning_context_diagnostics":contexts,
        "warning_feature_correlations_with_best_alt_gain":feature_corr,
        "rows":rows,
        "governance":{"pool_changed":False,"2025_2026_used_for_selection":False,"production_switch_authorized":False,"predictor_fit_in_stage1":False}
    }

    bw=out["periods"]["WARNING_20"]["fixed_challengers"][0]
    be=out["periods"]["ELEVATED_WARNING_10"]["fixed_challengers"][0]
    if bw["model"]!="LMC2_RBF_M32" or abs(bw["gain_vs_chhho"]+16.11)>0.03:
        raise RuntimeError(("PRIOR_RESCUEABILITY_REGRESSION_WARNING",bw))
    if be["model"]!="LMC2_RBF_M32" or abs(be["gain_vs_chhho"]-101.76)>0.03 or be["wins"]!=8:
        raise RuntimeError(("PRIOR_RESCUEABILITY_REGRESSION_ELEVATED",be))
    if abs(out["periods"]["WARNING_20"]["oracle_keep_or_best_gain"]-469.73)>0.05:
        raise RuntimeError("PRIOR_ORACLE_REGRESSION")

    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    md=[
        "# GOLD MONTHLY — Relative-Loss / Rescue-Gain Matrix Stage 1 V1",
        "",
        "**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / DEV-ONLY SELECTION AUTHORITY / NO SWITCH AUTHORIZED",
        "",
        f"- DEV: 33 months; warnings: 20 = 10 elevated + 10 false; non-warning: 13.",
        f"- Best fixed all-33 challenger: {out['periods']['ALL_DEV_33']['fixed_challengers'][0]['model']} with gain {out['periods']['ALL_DEV_33']['fixed_challengers'][0]['gain_vs_chhho']:.2f} USD.",
        f"- Best fixed warning challenger: {bw['model']} with gain {bw['gain_vs_chhho']:.2f} USD.",
        f"- Elevated-warning hindsight: {be['model']} gain {be['gain_vs_chhho']:.2f} USD, wins {be['wins']}/10.",
        f"- KEEP-or-best oracle warning gain: {out['periods']['WARNING_20']['oracle_keep_or_best_gain']:.2f} USD.",
        "- No fixed fallback is promoted. Next stage is a low-capacity chronological DEV-only relative-loss predictor preserving KEEP/ABSTAIN."
    ]
    Path(a.output_md).write_text("\n".join(md)+"\n")
    print("STAGE1_GATE=PASS")

if __name__=="__main__":
    main()
