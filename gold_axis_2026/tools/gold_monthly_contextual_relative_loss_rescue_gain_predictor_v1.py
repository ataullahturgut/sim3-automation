from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

NUM = [
    "p_high","p_elevated","semantic_probability","direction_agreement",
    "dispersion_pct","chhho_abs_median_gap_pct","chhho_iqr_distance",
    "chhho_forecast_percentile","active_signal_count","awake_expert_count",
]
CAT = ["semantic_label","state_category","transition_v2_status","extreme_status","ood_label"]

def make_feature_rows(rows):
    out=[]
    for r in rows:
        out.append({
            "p_high":float(r["p_high"]),
            "p_elevated":float(r["p_elevated"]),
            "semantic_probability":float(r["semantic_probability"]),
            "direction_agreement":float(r["direction_agreement"]),
            "dispersion_pct":float(r["dispersion_pct"]),
            "chhho_abs_median_gap_pct":float(r["chhho_abs_median_gap_pct"]),
            "chhho_iqr_distance":float(r["chhho_iqr_distance"]),
            "chhho_forecast_percentile":float(r["chhho_forecast_percentile"]),
            "active_signal_count":float(len(r["active_signals"])),
            "awake_expert_count":float(len(r["awake_experts"])),
            "semantic_label":str(r["semantic_label"]),
            "state_category":str(r["state_category"]),
            "transition_v2_status":str(r["transition_v2_status"]),
            "extreme_status":str(r["extreme_status"]),
            "ood_label":"OOD" if r["origin_regime_ood"] else "IN_DOMAIN",
        })
    return pd.DataFrame(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage1-json",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()

    d=json.loads(Path(a.stage1_json).read_text())
    rows=d["rows"]
    models=[m for m in d["models"] if m!="ChHHO_ANFIS"]
    if len(rows)!=33 or len(models)!=15:
        raise RuntimeError("FROZEN_STAGE1_SHAPE_MISMATCH")

    X=make_feature_rows(rows)
    Y=np.asarray([
        [float(r["rescue_gain"][m])/max(abs(float(r["chhho_forecast"])),1e-9) for m in models]
        for r in rows
    ],float)

    predictors={"EXPANDING_MEAN":("mean",None,None)}
    for fset,ncols,ccols in [("CORE",NUM,[]),("STATE",NUM,CAT)]:
        for alpha in [1.0,10.0,100.0]:
            predictors[f"RIDGE_{fset}_A{int(alpha)}"]=("ridge",alpha,(ncols,ccols))

    start=8
    pred_records=[]
    for t in range(start,len(rows)):
        train=list(range(t))
        ytr=Y[train]
        for name,(kind,alpha,sets) in predictors.items():
            if kind=="mean":
                pred=ytr.mean(axis=0)
                resid=ytr-pred[None,:]
            else:
                ncols,ccols=sets
                tr=[]
                if ncols: tr.append(("num",StandardScaler(),ncols))
                if ccols: tr.append(("cat",OneHotEncoder(handle_unknown="ignore",sparse_output=False),ccols))
                pipe=Pipeline([
                    ("pre",ColumnTransformer(tr,remainder="drop",sparse_threshold=0)),
                    ("ridge",Ridge(alpha=alpha,fit_intercept=True)),
                ])
                pipe.fit(X.iloc[train],ytr)
                pred=np.asarray(pipe.predict(X.iloc[[t]])[0],float)
                resid=ytr-np.asarray(pipe.predict(X.iloc[train]),float)
            rmse=np.sqrt(np.mean(resid**2,axis=0))
            j=int(np.argmax(pred))
            r=rows[t]
            pred_records.append({
                "target":r["target"],"row_index":t,"router_warn":bool(r["router_warn"]),
                "severity":r["severity"],"predictor":name,"chosen_model":models[j],
                "pred_scaled_gain":float(pred[j]),
                "pred_gain_usd":float(pred[j]*abs(r["chhho_forecast"])),
                "resid_rmse_scaled":float(rmse[j]),
                "actual_chosen_gain_usd":float(r["rescue_gain"][models[j]]),
            })

    warning_rows=[r for r in rows[start:] if r["router_warn"]]
    if len(warning_rows)!=14:
        raise RuntimeError(("WARNING_EVAL_COUNT",len(warning_rows)))
    keep_sum=float(sum(r["chhho_ae"] for r in warning_rows))
    results=[]; action_rows=[]
    for pname in predictors:
        recs=[z for z in pred_records if z["predictor"]==pname and z["router_warn"]]
        for policy in ["DIRECT_SWITCH","CONSERVATIVE_SWITCH","CONSERVATIVE_BLEND"]:
            total=0.; beneficial=harmful=nonkeep=0; worst=0.; ac=Counter(); mc=Counter()
            for z in recs:
                r=rows[z["row_index"]]; pred=z["pred_scaled_gain"]; thr=.5*z["resid_rmse_scaled"]
                m=z["chosen_model"]; main=float(r["chhho_forecast"]); alt=float(r["model_forecasts"][m]); actual=float(r["actual"])
                if policy=="DIRECT_SWITCH":
                    action="SWITCH" if pred>0 else "KEEP"
                    used=alt if action=="SWITCH" else main
                elif policy=="CONSERVATIVE_SWITCH":
                    if pred>thr: action="SWITCH"; used=alt
                    elif pred>0: action="ABSTAIN"; used=main
                    else: action="KEEP"; used=main
                else:
                    if pred>thr: action="SWITCH"; used=alt
                    elif pred>0: action="BLEND50"; used=.5*(main+alt)
                    else: action="KEEP"; used=main
                ae=abs(used-actual); gain=float(r["chhho_ae"]-ae)
                total+=ae; ac[action]+=1
                if action not in ("KEEP","ABSTAIN"):
                    nonkeep+=1; mc[m]+=1
                    beneficial+=int(gain>1e-9); harmful+=int(gain<-1e-9); worst=max(worst,-gain)
                action_rows.append({
                    **z,"policy":policy,"action":action,"action_forecast":float(used),
                    "action_ae":float(ae),"gain_vs_keep":gain,
                    "threshold_usd":float(thr*abs(main)),
                })
            results.append({
                "predictor":pname,"policy":policy,"warning_n":len(recs),
                "keep_sum_ae":keep_sum,"policy_sum_ae":float(total),
                "gain_vs_keep":float(keep_sum-total),"nonkeep_actions":nonkeep,
                "beneficial_nonkeep":beneficial,"harmful_nonkeep":harmful,
                "worst_incremental_harm":float(worst),"action_counts":dict(ac),
                "chosen_model_counts":dict(mc),
            })
    results.sort(key=lambda z:(-z["gain_vs_keep"],z["harmful_nonkeep"],z["worst_incremental_harm"]))
    leader=results[0]

    fixed=[]
    for m in models:
        ae=float(sum(r["model_ae"][m] for r in warning_rows))
        fixed.append({"model":m,"sum_ae":ae,"gain_vs_keep":keep_sum-ae,
                      "wins":sum(r["rescue_gain"][m]>1e-9 for r in warning_rows)})
    fixed.sort(key=lambda z:-z["gain_vs_keep"])
    keepbest=sum(min(r["chhho_ae"],min(r["model_ae"][m] for m in models)) for r in warning_rows)

    out={
        "schema":"GOLD_MONTHLY_CONTEXTUAL_RELATIVE_LOSS_RESCUE_GAIN_PREDICTOR_V1_2026-10-01",
        "status":"COMPLETE","scientific_gate":"PASS" if leader["gain_vs_keep"]>0 else "FAIL",
        "robustness_assessment":"WEAK" if 0 < leader["gain_vs_keep"] < 10 else "MATERIAL",
        "authority":{"warmup_targets":8,"eval_start":rows[start]["target"],"eval_end":rows[-1]["target"],
                     "warning_eval_n":len(warning_rows),"2025_2026_used_for_selection":False},
        "models":{"main":"ChHHO_ANFIS","challengers":models},
        "baseline_keep_sum_ae":keep_sum,"candidate_results":results,"leader":leader,
        "leader_action_rows":[x for x in action_rows if x["predictor"]==leader["predictor"] and x["policy"]==leader["policy"]],
        "same_window_best_fixed_challenger":fixed[0],
        "oracle_keep_or_best_gain":float(keep_sum-keepbest),
        "governance":{"production_authorized":False,"price_model_refit":False,"pool_changed":False,
                      "future_target_features_used":False,"opened_2025_2026_used_for_selection":False},
    }

    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    md=[
        "# GOLD MONTHLY — Contextual Relative-Loss / Rescue-Gain Predictor V1 Result","",
        "**Date:** 2026-10-01  ",
        f"**Status:** COMPLETE / SCIENTIFIC_GATE={out['scientific_gate']} / ROBUSTNESS={out['robustness_assessment']} / DEV-ONLY / NO PRODUCTION SWITCH","",
        f"- warm-up: **8 DEV targets**",
        f"- chronological evaluation: **{rows[start]['target']}..{rows[-1]['target']}**",
        f"- evaluated Specialist Hedge warnings: **{len(warning_rows)}**",
        f"- KEEP baseline ΣAE: **{keep_sum:.2f} USD**","",
        "## Leader","",
        f"- predictor: **{leader['predictor']}**",
        f"- policy: **{leader['policy']}**",
        f"- ΣAE: **{leader['policy_sum_ae']:.2f} USD**",
        f"- gain vs KEEP: **{leader['gain_vs_keep']:+.2f} USD**",
        f"- beneficial / harmful non-KEEP: **{leader['beneficial_nonkeep']} / {leader['harmful_nonkeep']}**",
        f"- worst incremental harm: **{leader['worst_incremental_harm']:.2f} USD**","",
        "Formal gate is positive, but the margin is small and harmful actions outnumber beneficial actions. This is a weak research pass, not a production switch rule.",
        "",
        "## Next permitted check","",
        "Transport the frozen DEV leader to already-opened 2025..2026 without retuning. Do not use opened outcomes to alter predictor, alpha, feature set, or policy.",
    ]
    Path(a.output_md).write_text("\n".join(md)+"\n")
    print("PREDICTOR_GATE="+out["scientific_gate"])
    print(json.dumps({"leader":leader,"fixed":fixed[0],"oracle_keepbest_gain":out["oracle_keep_or_best_gain"]},sort_keys=True))

if __name__=="__main__":
    main()
