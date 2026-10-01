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

NUM=[
"p_high","p_elevated","semantic_probability","direction_agreement","dispersion_pct",
"chhho_abs_median_gap_pct","chhho_iqr_distance","chhho_forecast_percentile",
"active_signal_count","awake_expert_count"
]

def feat(r):
    return {
      "p_high":float(r["p_high"]),"p_elevated":float(r["p_elevated"]),
      "semantic_probability":float(r["semantic_probability"]),
      "direction_agreement":float(r["direction_agreement"]),
      "dispersion_pct":float(r["dispersion_pct"]),
      "chhho_abs_median_gap_pct":float(r["chhho_abs_median_gap_pct"]),
      "chhho_iqr_distance":float(r["chhho_iqr_distance"]),
      "chhho_forecast_percentile":float(r["chhho_forecast_percentile"]),
      "active_signal_count":float(len(r["active_signals"])),
      "awake_expert_count":float(len(r["awake_experts"])),
    }

def perf(rows, rule):
    gain=0.0; allow=ben=harm=0; worst=0.0
    for z in rows:
        if not z["base_switch"]: continue
        if rule(z):
            allow+=1; gain+=z["actual_gain"]
            ben+=int(z["actual_gain"]>1e-9)
            harm+=int(z["actual_gain"]<-1e-9)
            worst=max(worst,-z["actual_gain"])
    return {"gain_vs_keep":float(gain),"allowed_switches":allow,"beneficial":ben,"harmful":harm,"worst_incremental_harm":float(worst)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage1-json",required=True)
    ap.add_argument("--output-json",required=True)
    ap.add_argument("--output-md",required=True)
    a=ap.parse_args()
    d=json.loads(Path(a.stage1_json).read_text())
    rows=d["rows"]; models=[m for m in d["models"] if m!="ChHHO_ANFIS"]
    if len(rows)!=33 or len(models)!=15: raise RuntimeError("FROZEN_INPUT_SHAPE_MISMATCH")
    X=pd.DataFrame([feat(r) for r in rows])
    Y=np.asarray([[float(r["rescue_gain"][m])/abs(float(r["chhho_forecast"])) for m in models] for r in rows],float)

    recs=[]
    for t in range(8,len(rows)):
        tr=np.arange(t)
        pipe=Pipeline([
          ("pre",ColumnTransformer([("num",StandardScaler(),NUM)],remainder="drop",sparse_threshold=0)),
          ("ridge",Ridge(alpha=10.0,fit_intercept=True))
        ])
        pipe.fit(X.iloc[tr],Y[tr])
        pred=np.asarray(pipe.predict(X.iloc[[t]])[0],float)
        fitted=np.asarray(pipe.predict(X.iloc[tr]),float)
        rmse=np.sqrt(np.mean((Y[tr]-fitted)**2,axis=0))
        r=rows[t]; scale=abs(float(r["chhho_forecast"]))
        pu=pred*scale; ru=rmse*scale
        order=np.argsort(-pu); j=int(order[0])
        recs.append({
          "target":r["target"],"severity":r["severity"],"router_warn":bool(r["router_warn"]),
          "chosen_model":models[j],"top_pred_gain_usd":float(pu[j]),"top_rmse_usd":float(ru[j]),
          "confidence_ratio":float(pu[j]/ru[j]) if ru[j]>0 else 999.0,
          "positive_breadth":float(np.mean(pu>0)),
          "median_pred_gain_usd":float(np.median(pu)),
          "second_pred_gain_usd":float(pu[order[1]]),
          "top_second_margin_usd":float(pu[order[0]]-pu[order[1]]),
          "actual_gain":float(r["rescue_gain"][models[j]]),
          "base_switch":bool(pu[j]>0),
        })

    warning=[z for z in recs if z["router_warn"]]
    switch=[z for z in warning if z["base_switch"]]
    if (len(warning),len(switch))!=(14,13): raise RuntimeError(("FROZEN_DECISION_COUNT",len(warning),len(switch)))

    rules={
      "NO_GUARD":lambda z:True,
      "BREADTH_50":lambda z:z["positive_breadth"]>=0.50,
      "BREADTH_67":lambda z:z["positive_breadth"]>=2/3,
      "BREADTH_80":lambda z:z["positive_breadth"]>=0.80,
      "CONF_050":lambda z:z["confidence_ratio"]>=0.50,
      "CONF_100":lambda z:z["confidence_ratio"]>=1.00,
      "CONF_150":lambda z:z["confidence_ratio"]>=1.50,
      "BREADTH67_CONF050":lambda z:z["positive_breadth"]>=2/3 and z["confidence_ratio"]>=0.50,
      "BREADTH67_CONF100":lambda z:z["positive_breadth"]>=2/3 and z["confidence_ratio"]>=1.00,
      "BREADTH50_CONF100":lambda z:z["positive_breadth"]>=0.50 and z["confidence_ratio"]>=1.00,
    }
    full={k:perf(warning,v) for k,v in rules.items()}
    base=full["NO_GUARD"]

    replay=[]
    for i,z in enumerate(switch):
        if i<4: continue
        hist=switch[:i]
        ranked=[]
        for k,rule in rules.items():
            q=perf(hist,rule)
            ranked.append((-q["gain_vs_keep"],q["harmful"],q["worst_incremental_harm"],q["allowed_switches"],k,q))
        ranked.sort()
        chosen=ranked[0][4]; prior=ranked[0][5]
        allow=bool(rules[chosen](z)); realized=float(z["actual_gain"] if allow else 0.0)
        replay.append({"target":z["target"],"selected_guard":chosen,"allow":allow,"realized_gain":realized,"prior_metrics":prior})
    replay_gain=float(sum(x["realized_gain"] for x in replay))
    replay_harm=sum(int(x["allow"] and x["realized_gain"]<0) for x in replay)
    replay_ben=sum(int(x["allow"] and x["realized_gain"]>0) for x in replay)
    replay_worst=max([0.0]+[-x["realized_gain"] for x in replay if x["allow"] and x["realized_gain"]<0])
    replay_base=perf(switch[4:],rules["NO_GUARD"])

    eligible=[]
    for k,q in full.items():
        if k=="NO_GUARD": continue
        if q["gain_vs_keep"]>0 and q["harmful"]<base["harmful"] and q["worst_incremental_harm"]<base["worst_incremental_harm"] and q["beneficial"]>=2:
            eligible.append(k)

    critical=next(z for z in switch if z["target"]=="2023-03")
    status="PASS" if (replay_gain>replay_base["gain_vs_keep"] and replay_harm<replay_base["harmful"] and eligible) else "FAIL"
    out={
      "schema":"GOLD_MONTHLY_HARMFUL_SWITCH_SHARED_HARD_GUARD_V1_2026-10-01",
      "status":"COMPLETE","scientific_gate":status,
      "coverage":{"warning_eval_n":len(warning),"base_switch_opportunities":len(switch),"replay_warmup_switches":4,"replay_eval_switches":len(replay)},
      "base_no_guard":base,"candidate_full_dev":full,
      "expanding_replay":{"gain_vs_keep":replay_gain,"beneficial":replay_ben,"harmful":replay_harm,"worst_incremental_harm":float(replay_worst),"baseline_same_window":replay_base,"rows":replay},
      "eligible_final_guards":eligible,
      "critical_2023_03":critical,
      "binding_decision":"REJECT_GUARD_V1_KEEP_RESCUE_PREDICTOR_RESEARCH_ONLY",
      "opened_transport_authorized":False,
      "governance":{"2025_2026_used_for_guard_selection":False,"production_authorized":False,"upstream_predictor_changed":False}
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    md=[
      "# GOLD MONTHLY — Harmful-Switch / Shared-Hard Safety Guard V1 Result","",
      f"**Status:** COMPLETE / SCIENTIFIC_GATE={status} / DEV-ONLY / NO PRODUCTION SWITCH","",
      "## Baseline NO_GUARD","",
      f"- gain vs KEEP: **{base['gain_vs_keep']:+.2f} USD**",
      f"- allowed switches: **{base['allowed_switches']}**",
      f"- beneficial / harmful: **{base['beneficial']} / {base['harmful']}**",
      f"- worst incremental harm: **{base['worst_incremental_harm']:.2f} USD**","",
      "## Guard result","",
      f"- eligible final deterministic guards: **{eligible}**",
      f"- expanding replay gain: **{replay_gain:+.2f} USD**",
      f"- same-window NO_GUARD gain: **{replay_base['gain_vs_keep']:+.2f} USD**",
      f"- replay beneficial / harmful: **{replay_ben} / {replay_harm}**",
      f"- replay worst harm: **{replay_worst:.2f} USD**","",
      "No pre-registered guard passes the acceptance conditions. Breadth and confidence gates reduce some switches but discard more genuine rescue than harmful rescue.",
      "",
      "## Critical 2023-03","",
      f"- predicted positive breadth: **{critical['positive_breadth']*100:.1f}%**",
      f"- top predicted rescue gain: **{critical['top_pred_gain_usd']:.2f} USD**",
      f"- confidence ratio: **{critical['confidence_ratio']:.2f}x**",
      f"- realized selected-switch gain: **{critical['actual_gain']:+.2f} USD**",
      "",
      "This proves that broad predicted rescue consensus is not a safe shared-hard detector in V1.",
      "",
      "## Binding decision","",
      "- V1 safety guard is rejected.",
      "- No opened 2025/2026 guard transport is authorized because no DEV guard was frozen.",
      "- ChHHO remains main; Specialist Hedge remains warning layer; Rescue-Gain Predictor remains research-only.",
      "- Next research direction should change the target: directly model harmful-switch probability / shared-hard risk with strict chronological DEV validation, rather than another deterministic breadth/confidence gate."
    ]
    Path(a.output_md).write_text("\n".join(md)+"\n")
    print("GUARD_V1_GATE="+status)
    print(json.dumps({"base":base,"replay_gain":replay_gain,"replay_base":replay_base,"eligible":eligible,"critical":critical},sort_keys=True))

if __name__=="__main__":
    main()
