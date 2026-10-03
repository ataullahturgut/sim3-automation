from __future__ import annotations
import json, os
from pathlib import Path
import pandas as pd
import gold_h3_helios_v5_dce as h5

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_clean_inference_out"))
OUT.mkdir(parents=True,exist_ok=True)
V4=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_HELIOS_V4_RGE_PREDICTIONS_2026-10-03.csv"
V5=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

def main():
    base=pd.read_csv(V4)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","cot_report_date","cot_available_date"]:
        if c in base.columns: base[c]=pd.to_datetime(base[c],errors="raise")
    for c in ["v4_route","gate_active","opal_override","candidate_reversal"]:
        base[c]=h5.as_bool(base[c])
    g=pd.read_csv(V5)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","cot_report_date","cot_available_date"]:
        if c in g.columns: g[c]=pd.to_datetime(g[c],errors="raise")
    for c in ["v5_route","dce_exception","v4_route","gate_active","opal_override","candidate_reversal"]:
        if c in g.columns: g[c]=h5.as_bool(g[c])

    inf=h5.inference(g); inf.to_csv(OUT/"clean_v5_inference.csv",index=False)
    cinf=h5.cluster_inference(g); cinf.to_csv(OUT/"clean_v5_cluster_inference.csv",index=False)
    sens=h5.sensitivity(base); sens.to_csv(OUT/"clean_v5_sensitivity.csv",index=False)
    met=h5.score_periods(g); met.to_csv(OUT/"clean_v5_metrics_detailed.csv",index=False)

    summary={
      "schema":"GOLD_H3_CLEAN_V5_INFERENCE",
      "inference":inf.to_dict(orient="records"),
      "cluster":cinf.to_dict(orient="records"),
      "sensitivity":sens.to_dict(orient="records"),
    }
    (OUT/"clean_v5_inference_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 CLEAN V5 INFERENCE — 2026-10-03","",
      "Binding V5-DCE thresholds remain PATH posterior >0.50 and GT share >0.50. Sensitivity is diagnostic only.","",
      "## Binding inference",""]
    for r in inf.itertuples():
        scale=100 if r.metric=="accuracy" else 1
        unit=" pp" if r.metric=="accuracy" else ""
        lines.append(f"- {r.comparison} / {r.period} / {r.metric} / block{r.block_len}: diff={scale*r.observed_diff:+.4f}{unit}; 95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; P(improve)={100*r.bootstrap_improve_share:.1f}%.")
    lines+=["","## COT-vintage cluster",""]
    for r in cinf.itertuples():
        lines.append(f"- {r.period}: net {r.net_rescue:+.0f}, clusters {r.cluster_n}, 95%=[{r.ci95_low:+.0f},{r.ci95_high:+.0f}], P(net>0)={100*r.p_net_positive:.1f}%.")
    lines+=["","## Sensitivity 2025-2026",""]
    for r in sens[sens.period=="2025-2026"].itertuples():
        lines.append(f"- {r.sensitivity}: path>{r.threshold:.2f}, GT>{r.gt_threshold:.2f}: Acc {100*r.accuracy:.2f}%, BA {100*r.balanced_accuracy:.2f}%, Brier {r.brier:.4f}, exceptions {r.exception_n}, net {r.net_rescue:+d}.")
    (OUT/"CLEAN_V5_INFERENCE_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"CLEAN_V5_INFERENCE_RESULT.md").read_text())

if __name__=="__main__": main()
