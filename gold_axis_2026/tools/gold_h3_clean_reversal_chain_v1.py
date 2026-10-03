from __future__ import annotations

import json, os
from pathlib import Path

import numpy as np
import pandas as pd

import gold_h3_iris_v1 as iris
import gold_h3_rift_v1 as rift
import gold_h3_turn_v1 as turn
import gold_h3_vega_v1 as vega
import gold_h3_opal_v1 as opal
import gold_h3_helios_v1 as h1
import gold_h3_helios_v2 as h2
import gold_h3_helios_v3_gt as h3
import gold_h3_helios_v4_rge as h4
import gold_h3_helios_v5_dce as h5

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_clean_reversal_chain_out"))
OUT.mkdir(parents=True,exist_ok=True)

CLEAN_AURORA=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"

OLD={
 "AURORA":ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv",
 "V2":ROOT/"gold_axis_2026"/"GOLD_H3_HELIOS_V2_PREDICTIONS_2026-10-03.csv",
 "V3":ROOT/"gold_axis_2026"/"GOLD_H3_HELIOS_V3_GT_PREDICTIONS_2026-10-03.csv",
 "V4":ROOT/"gold_axis_2026"/"GOLD_H3_HELIOS_V4_RGE_PREDICTIONS_2026-10-03.csv",
 "V5":ROOT/"gold_axis_2026"/"GOLD_H3_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv",
}

def metrics(y,p):
    return h3.metrics(y,p)

def score_one(g,col,period):
    z=g[g.year==period].copy() if isinstance(period,int) else g[g.year.isin(period)].copy()
    return metrics(z.y_up,z[col])

def cache_hourly():
    hist=iris.load_neon_hourly()
    succ,api_calls=iris.fetch_extension()
    _,bridge=iris.bridge_metrics(hist,succ)
    if not bridge["pass"]:
        raise RuntimeError(f"CLEAN_CHAIN_SOURCE_BRIDGE_FAIL {bridge}")
    iris.load_neon_hourly=lambda: hist.copy()
    iris.fetch_extension=lambda: (succ.copy(),api_calls)
    return bridge,api_calls

def run_experts():
    rift.AURORA=CLEAN_AURORA
    turn.AURORA=CLEAN_AURORA
    vega.AURORA=CLEAN_AURORA
    opal.AURORA=CLEAN_AURORA

    rp,_,_=rift.load_panel()
    rpred=rift.run_rift(rp)
    rfile=OUT/"clean_rift_predictions.csv"; rpred.to_csv(rfile,index=False)

    tpred,_,_=turn.apply_turn()
    tfile=OUT/"clean_turn_predictions.csv"; tpred.to_csv(tfile,index=False)

    vp,_,_,_=vega.load_panel()
    vpred=vega.run_vega(vp)
    vfile=OUT/"clean_vega_predictions.csv"; vpred.to_csv(vfile,index=False)

    op,_,_,cot,cotmeta=opal.load_panel()
    opred=opal.run_opal(op)
    ofile=OUT/"clean_opal_predictions.csv"; opred.to_csv(ofile,index=False)

    return {
      "rift":rpred,"turn":tpred,"vega":vpred,"opal":opred,
      "paths":{"rift":rfile,"turn":tfile,"vega":vfile,"opal":ofile},
      "cot_meta":cotmeta,
    }

def run_helios(ex):
    h1.AURORA=CLEAN_AURORA
    h1.RIFT=ex["paths"]["rift"]
    h1.TURN=ex["paths"]["turn"]
    h1.VEGA=ex["paths"]["vega"]
    h1.OPAL=ex["paths"]["opal"]
    g1,sw1=h1.build_ledger()
    f1=OUT/"clean_helios_v1_predictions.csv"; g1.to_csv(f1,index=False)
    sw1.to_csv(OUT/"clean_helios_v1_switches.csv",index=False)

    h2.V1=f1
    g2=h2.build_v2()
    f2=OUT/"clean_helios_v2_predictions.csv"; g2.to_csv(f2,index=False)

    h3.H1=f1; h3.H2=f2; h3.OPAL=ex["paths"]["opal"]
    b3=h3.load_base()
    g3=h3.simulate_market(b3)
    f3=OUT/"clean_helios_v3_gt_predictions.csv"; g3.to_csv(f3,index=False)

    h4.V3=f3
    b4=h4.attach_v3(b3)
    g4,sw4=h4.simulate_rge(b4)
    f4=OUT/"clean_helios_v4_rge_predictions.csv"; g4.to_csv(f4,index=False)
    sw4.to_csv(OUT/"clean_helios_v4_rge_switches.csv",index=False)

    g5=h5.apply_dce(g4)
    f5=OUT/"clean_helios_v5_dce_predictions.csv"; g5.to_csv(f5,index=False)

    return {"v1":g1,"v2":g2,"v3":g3,"v4":g4,"v5":g5,"sw1":sw1,"sw4":sw4}

def model_summary(chain,ex):
    maps={
      "AURORA":(chain["v5"],"p_aurora"),
      "OPAL":(chain["v5"],"p_opal_raw"),
      "V2":(chain["v5"],"p_helios_v2"),
      "V3":(chain["v5"],"p_helios_v3_gt"),
      "V4":(chain["v5"],"p_helios_v4_rge"),
      "V5":(chain["v5"],"p_helios_v5_dce"),
    }
    rows=[]
    for period,label in [([2023],"2023"),([2024],"2024"),([2025],"2025"),([2026],"2026"),([2025,2026],"2025-2026")]:
        for name,(g,col) in maps.items():
            z=g[g.year.isin(period)]
            m=metrics(z.y_up,z[col])
            rows.append({"model":name,"period":label,**m})
    return pd.DataFrame(rows)

def route_summary(g):
    rows=[]
    for y in [2025,2026]:
        z=g[g.year==y].copy()
        a=(z.p_aurora>=.5).astype(int)
        p=(z.p_helios_v5_dce>=.5).astype(int)
        yy=z.y_up.astype(int)
        ch=a!=p
        rows.append({
          "year":y,"n":int(len(z)),"routed":int(ch.sum()),
          "rescued":int((ch&(a!=yy)&(p==yy)).sum()),
          "broken":int((ch&(a==yy)&(p!=yy)).sum()),
          "net_rescue":int((ch&(a!=yy)&(p==yy)).sum()-(ch&(a==yy)&(p!=yy)).sum()),
          "dce_exceptions":int(z.dce_exception.sum()),
        })
    return pd.DataFrame(rows)

def compare_old_clean(clean_metrics):
    rows=[]
    colmap={"AURORA":"p_aurora","V2":"p_helios_v2","V3":"p_helios_v3_gt","V4":"p_helios_v4_rge","V5":"p_helios_v5_dce"}
    clean5=pd.read_csv(OUT/"clean_helios_v5_dce_predictions.csv")
    for name,path in OLD.items():
        if name=="AURORA":
            old=pd.read_csv(path,usecols=["forecast_issue_date","p_aurora"])
        else:
            old=pd.read_csv(path,usecols=["forecast_issue_date",colmap[name]])
        old["forecast_issue_date"]=pd.to_datetime(old.forecast_issue_date)
        z=clean5[clean5.year==2026][["forecast_issue_date","y_up"]].copy()
        z["forecast_issue_date"]=pd.to_datetime(z.forecast_issue_date)
        z=z.merge(old,on="forecast_issue_date",how="inner",validate="one_to_one")
        mo=metrics(z.y_up,z[colmap[name]])
        mc=clean_metrics[(clean_metrics.model==name)&(clean_metrics.period=="2026")].iloc[0]
        rows.append({
          "model":name,
          "old_preclean_accuracy_on_old_labels":None,
          "old_probability_accuracy_on_clean_labels":mo["accuracy"],
          "clean_refit_accuracy":float(mc.accuracy),
          "clean_refit_brier":float(mc.brier),
          "delta_clean_refit_vs_oldprob_cleanlabel":float(mc.accuracy-mo["accuracy"]),
        })
    return pd.DataFrame(rows)

def expert_metrics(ex):
    rows=[]
    specs=[
      ("RIFT",ex["rift"],"p_rift"),
      ("TURN",ex["turn"],"p_turn"),
      ("VEGA",ex["vega"],"p_vega"),
      ("OPAL",ex["opal"],"p_opal"),
    ]
    for name,g,col in specs:
        for y in [2025,2026]:
            z=g[g.year==y]
            m=metrics(z.y_up,z[col]); b=metrics(z.y_up,z.p_aurora)
            override=int(z.override.astype(bool).sum())
            ap=(z.p_aurora>=.5).astype(int); cp=(z[col]>=.5).astype(int); yy=z.y_up.astype(int)
            ch=ap!=cp
            rows.append({
              "expert":name,"year":y,"n":len(z),"override_n":override,
              "accuracy":m["accuracy"],"balanced_accuracy":m["balanced_accuracy"],"brier":m["brier"],
              "aurora_accuracy":b["accuracy"],
              "rescued":int((ch&(ap!=yy)&(cp==yy)).sum()),
              "broken":int((ch&(ap==yy)&(cp!=yy)).sum()),
            })
    return pd.DataFrame(rows)

def main():
    bridge,api_calls=cache_hourly()
    ex=run_experts()
    chain=run_helios(ex)

    cm=model_summary(chain,ex); cm.to_csv(OUT/"clean_chain_metrics.csv",index=False)
    rs=route_summary(chain["v5"]); rs.to_csv(OUT/"clean_v5_routes.csv",index=False)
    em=expert_metrics(ex); em.to_csv(OUT/"clean_reversal_expert_metrics.csv",index=False)
    comp=compare_old_clean(cm); comp.to_csv(OUT/"clean_vs_preclean_2026.csv",index=False)

    # V5 call-by-call 2026
    z=chain["v5"][chain["v5"].year==2026].copy()
    z["v5_dir"]=np.where(z.p_helios_v5_dce>=.5,"UP","DOWN")
    z["actual_dir"]=np.where(z.y_up==1,"UP","DOWN")
    z["correct"]=z.v5_dir==z.actual_dir
    z["aurora_dir"]=np.where(z.p_aurora>=.5,"UP","DOWN")
    z["changed_from_aurora"]=z.v5_dir!=z.aurora_dir
    z.to_csv(OUT/"clean_v5_2026_call_by_call.csv",index=False)

    summary={
      "schema":"GOLD_H3_CLEAN_REVERSAL_CHAIN",
      "source_bridge":bridge,"hourly_api_calls":int(api_calls),
      "cot_meta":ex["cot_meta"],
      "helios_v1_switches":chain["sw1"].to_dict(orient="records"),
      "v4_switches":chain["sw4"].to_dict(orient="records"),
      "metrics":cm.to_dict(orient="records"),
      "v5_routes":rs.to_dict(orient="records"),
      "expert_metrics":em.to_dict(orient="records"),
      "clean_vs_preclean":comp.to_dict(orient="records"),
      "v5_exceptions":z[z.dce_exception][["forecast_issue_date","target_end_date_h3","p_aurora","p_helios_v5_dce","y_up","target_r3","prob_path_superior","gt_flip_share"]].to_dict(orient="records"),
    }
    (OUT/"clean_reversal_chain_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 CLEAN REVERSAL CHAIN — 2026-10-03","",
      "**Status:** full fixed-rule clean rerun from corrected AURORA through V5-DCE.","",
      "No threshold was retuned. Original frozen/prospective artifacts were not overwritten.","",
      "## Model metrics","",
      "| Model | Period | Accuracy | BA | Brier | Logloss |",
      "|---|---|---:|---:|---:|---:|"
    ]
    for r in cm.itertuples():
        lines.append(f"| {r.model} | {r.period} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} |")
    lines += ["","## Clean V5 routing","",
      "| Year | Routed | Rescue | Broken | Net | DCE exceptions |",
      "|---:|---:|---:|---:|---:|---:|"]
    for r in rs.itertuples():
        lines.append(f"| {r.year} | {r.routed} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {r.dce_exceptions} |")
    lines += ["","## Clean reversal experts","",
      "| Expert | Year | Accuracy | AURORA | Overrides | Rescue | Broken |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for r in em.itertuples():
        lines.append(f"| {r.expert} | {r.year} | {100*r.accuracy:.2f}% | {100*r.aurora_accuracy:.2f}% | {r.override_n} | {r.rescued} | {r.broken} |")
    lines += ["","## 2026 clean-refit vs old probabilities on clean labels","",
      "| Model | Old probability / clean labels | Clean refit | Delta | Clean Brier |",
      "|---|---:|---:|---:|---:|"]
    for r in comp.itertuples():
        lines.append(f"| {r.model} | {100*r.old_probability_accuracy_on_clean_labels:.2f}% | {100*r.clean_refit_accuracy:.2f}% | {100*r.delta_clean_refit_vs_oldprob_cleanlabel:+.2f} pp | {r.clean_refit_brier:.4f} |")
    lines += ["","## Governance","",
      "All values in the previous pre-clean HELIOS V2/V3/V4/V5 2026 reports must be treated as historical/provisional. "
      "This clean chain is the valid retrospective integrity rerun, but remains post-hoc research rather than prospective confirmation."
    ]
    (OUT/"CLEAN_REVERSAL_CHAIN_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"CLEAN_REVERSAL_CHAIN_RESULT.md").read_text())

if __name__=="__main__":
    main()
