from pathlib import Path
import importlib.util
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
HSM=AX/"tools"/"gold_h3_handoff_state_machine_v1.py"

OUT_MD=AX/"GOLD_H3_HANDOFF_DELAYED_V1B_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_DELAYED_V1B_SUMMARY_2026-10-04.json"
OUT_GRID=AX/"GOLD_H3_HANDOFF_DELAYED_V1B_2025_GRID_2026-10-04.csv"
OUT_ACTIONS=AX/"GOLD_H3_HANDOFF_DELAYED_V1B_ACTIONS_2026-10-04.csv"

Q_EXT=[0.60,0.67,0.75]
Q_INT=[0.60,0.67,0.75]
DELTAS=[0.00,0.05,0.10,0.15]

spec=importlib.util.spec_from_file_location("hsm",HSM)
hsm=importlib.util.module_from_spec(spec)
spec.loader.exec_module(hsm)

def delayed_mask(df,qe,qi,delta):
    complete=(df.leadlag_score_premax.notna()&df.internal_now.notna()&df.internal_d1.notna())
    armed=complete & (df.leadlag_score_premax>=qe) & (df.internal_now>=qi) & (df.internal_d1>=delta)
    armed_prev=armed.shift(1,fill_value=False)
    same_momentum=df.momentum_up.astype(int)==df.momentum_up.shift(1).fillna(-9).astype(int)
    still_momentum=df.baseline_pred.astype(int)==df.momentum_up.astype(int)
    veto=df.strong_pro_risk.fillna(False).astype(bool)
    return armed_prev & same_momentum & still_momentum & (~veto)

def main():
    z=hsm.load_frame()

    # 2025 development rows: the action at t can only use an armed state from the immediately previous available origin.
    dev=z[z.feature_cutoff_date.dt.year==2025].copy().reset_index(drop=True)
    rows=[]
    for qe in Q_EXT:
        for qi in Q_INT:
            for d in DELTAS:
                m=delayed_mask(dev,qe,qi,d)
                st=hsm.rule_stats(dev,m)
                rows.append({
                    "q_external":qe,"q_internal":qi,"delta":d,
                    **{k:v for k,v in st.items() if k!="monthly_net"},
                    "monthly_net_json":json.dumps(st["monthly_net"],sort_keys=True),
                    "eligible":hsm.eligible(st)
                })
    grid=pd.DataFrame(rows)
    grid.to_csv(OUT_GRID,index=False)

    eg=grid[grid.eligible].copy()
    selected=None
    if len(eg):
        eg=eg.sort_values(["net","precision","actions","q_external","q_internal","delta"],
                          ascending=[False,False,True,False,False,False])
        selected=eg.iloc[0].to_dict()

    summary={
      "schema":"GOLD_H3_HANDOFF_DELAYED_V1B",
      "status":"NO_2025_ELIGIBLE_RULE" if selected is None else "2025_SELECTED_2026_OPENED",
      "dev_2025":{
        "n":int(len(dev)),
        "baseline":hsm.confusion(dev.y_up,dev.baseline_pred),
      },
      "selected_rule":None,
      "stress_2026":None,
    }

    action_frames=[]
    if selected is not None:
        qe=float(selected["q_external"]); qi=float(selected["q_internal"]); delta=float(selected["delta"])
        md=delayed_mask(dev,qe,qi,delta)
        sd=hsm.rule_stats(dev,md)
        summary["selected_rule"]={"q_external":qe,"q_internal":qi,"delta":delta,"dev_stats":sd}

        # Need previous-origin state to carry across the year boundary, so evaluate mask on full frame then subset 2026.
        mall=delayed_mask(z,qe,qi,delta)
        test=z[z.feature_cutoff_date.dt.year==2026].copy()
        mt=mall[z.feature_cutoff_date.dt.year==2026].reset_index(drop=True)
        test=test.reset_index(drop=True)

        if len(test)!=191:
            raise RuntimeError(f"Expected 191 2026 origins, got {len(test)}")
        if int(test.baseline_correct.sum())!=126:
            raise RuntimeError(f"Expected combined baseline 126/191, got {int(test.baseline_correct.sum())}")

        st=hsm.rule_stats(test,mt)
        assisted=test.baseline_pred.to_numpy(int).copy()
        assisted[mt.to_numpy()]=1-assisted[mt.to_numpy()]
        base_metrics=hsm.confusion(test.y_up,test.baseline_pred)
        assisted_metrics=hsm.confusion(test.y_up,assisted)
        remaining53=(~test.baseline_correct)&test.is_reversal

        q=test[mt].copy()
        q["handoff_pred"]=1-q.baseline_pred
        q["handoff_outcome"]=np.where(q.baseline_correct,"BROKEN","RESCUE")
        q["year"]=2026

        summary["stress_2026"]={
          "actions":st,
          "baseline_metrics":base_metrics,
          "assisted_metrics":assisted_metrics,
          "rescued_remaining53":int((mt&remaining53).sum()),
          "broken_correct_continuations":int((mt&test.baseline_correct&(~test.is_reversal)).sum()),
          "broken_correct_reversals":int((mt&test.baseline_correct&test.is_reversal).sum()),
          "overlap_sage":int((mt&test.sage_flip).sum()),
          "overlap_ruleflow":int((mt&test.ruleflow_flip).sum()),
        }

        qd=dev[md].copy()
        qd["handoff_pred"]=1-qd.baseline_pred
        qd["handoff_outcome"]=np.where(qd.baseline_correct,"BROKEN","RESCUE")
        qd["year"]=2025
        action_frames=[qd,q]

    if action_frames:
        act=pd.concat(action_frames,ignore_index=True)
        cols=["year","feature_cutoff_date","forecast_issue_date","target_end_date_h3","momentum_up","y_up",
              "v5_pred","sage_flip","ruleflow_flip","baseline_pred","baseline_correct",
              "leadlag_score_premax","internal_now","internal_d1","fragility_score","flow_score",
              "strong_pro_risk","ndx_r60","vix_r60","handoff_pred","handoff_outcome"]
        act[cols].to_csv(OUT_ACTIONS,index=False)
    else:
        pd.DataFrame().to_csv(OUT_ACTIONS,index=False)

    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Handoff Delayed V1b Result","",
           "**Status:** "+summary["status"],"",
           "## 2025 development","",
           f"- origins: **{summary['dev_2025']['n']}**",
           f"- combined baseline: **{summary['dev_2025']['baseline']['correct']}/{summary['dev_2025']['baseline']['n']} = {100*summary['dev_2025']['baseline']['accuracy']:.2f}%**","",
           "## 2025 grid","",
           "| qExt | qInt | delta | Act | Rescue | Broken | Net | Precision | Rate | Nonneg action months | Worst | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.sort_values(["eligible","net","precision"],ascending=[False,False,False]).itertuples():
        lines.append(f"| {r.q_external:.2f} | {r.q_internal:.2f} | {r.delta:.2f} | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.1f}% | {100*r.rate:.1f}% | {100*r.nonnegative_action_month_share:.1f}% | {r.worst_action_month_net:+d} | {r.eligible} |")

    if selected is None:
        lines += ["","## Decision","","No delayed Handoff rule passed the frozen 2025 gate. V1b closes; 2026 was not opened for rule selection."]
    else:
        sr=summary["selected_rule"]; s26=summary["stress_2026"]
        lines += ["","## Selected 2025 rule","",
                  f"- qExternal **{sr['q_external']:.2f}**, qInternal **{sr['q_internal']:.2f}**, delta **{sr['delta']:.2f}**",
                  f"- actions/rescue/broken/net: **{sr['dev_stats']['actions']} / {sr['dev_stats']['rescue']} / {sr['dev_stats']['broken']} / {sr['dev_stats']['net']:+d}**",
                  f"- precision: **{100*sr['dev_stats']['precision']:.2f}%**","",
                  "## Frozen 2026 stress","",
                  f"- actions/rescue/broken/net: **{s26['actions']['actions']} / {s26['actions']['rescue']} / {s26['actions']['broken']} / {s26['actions']['net']:+d}**",
                  f"- precision: **{100*s26['actions']['precision']:.2f}%**",
                  f"- remaining-53 rescued: **{s26['rescued_remaining53']}**",
                  f"- baseline: **{s26['baseline_metrics']['correct']}/{s26['baseline_metrics']['n']} = {100*s26['baseline_metrics']['accuracy']:.2f}%**, BA **{100*s26['baseline_metrics']['balanced_accuracy']:.2f}%**",
                  f"- + delayed Handoff: **{s26['assisted_metrics']['correct']}/{s26['assisted_metrics']['n']} = {100*s26['assisted_metrics']['accuracy']:.2f}%**, BA **{100*s26['assisted_metrics']['balanced_accuracy']:.2f}%**","",
                  "## 2026 action dates","",
                  "| Date | Momentum | Baseline | Actual | Ext pre | Internal | d1 | Strong pro-risk | Outcome |",
                  "|---|---:|---:|---:|---:|---:|---:|---|---|"]
        for r in action_frames[-1].itertuples():
            lines.append(f"| {r.feature_cutoff_date.date()} | {r.momentum_up} | {r.baseline_pred} | {r.y_up} | {r.leadlag_score_premax:.2f} | {r.internal_now:.2f} | {r.internal_d1:+.2f} | {r.strong_pro_risk} | {r.handoff_outcome} |")
        lines += ["","## Interpretation","",
                  "- V1b changes timing only: Handoff evidence at t arms the next available origin.",
                  "- 2026 thresholds were not tuned.",
                  "- The result remains retrospective evidence because the broader Handoff hypothesis was motivated by 2026 diagnostics."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
