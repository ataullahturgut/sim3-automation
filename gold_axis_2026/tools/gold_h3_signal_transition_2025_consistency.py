from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
SCORES=AX/"GOLD_H3_REMAINING53_SIGNAL_AUDIT_ORIGINS_2026-10-04.csv"
# Rebuild score history by importing the already frozen audit implementation.
import importlib.util
spec=importlib.util.spec_from_file_location("audit",AX/"tools"/"gold_h3_remaining53_signal_audit.py")
audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)

OUT=AX/"GOLD_H3_SIGNAL_TRANSITION_2025_CONSISTENCY_2026-10-04.md"
OUTJ=AX/"GOLD_H3_SIGNAL_TRANSITION_2025_CONSISTENCY_2026-10-04.json"

def smd(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    a=a[np.isfinite(a)]; b=b[np.isfinite(b)]
    if len(a)<3 or len(b)<3:return np.nan
    va=np.var(a,ddof=1); vb=np.var(b,ddof=1)
    sp=np.sqrt(((len(a)-1)*va+(len(b)-1)*vb)/(len(a)+len(b)-2))
    return float((np.mean(a)-np.mean(b))/sp) if sp>1e-12 else np.nan

scores,_=audit.build_scores()
for m in ["fragility_score","flow_score","leadlag_score","reaction_score"]:
    scores[f"{m}_d1"]=scores[m]-scores[f"{m}_lag1"]
    scores[f"{m}_d2"]=scores[m]-scores[f"{m}_lag2"]
scores["internal_now"]=scores[["fragility_score","flow_score"]].max(axis=1)
scores["internal_lag1"]=scores[["fragility_score_lag1","flow_score_lag1"]].max(axis=1)
scores["internal_lag2"]=scores[["fragility_score_lag2","flow_score_lag2"]].max(axis=1)
scores["internal_d1"]=scores.internal_now-scores.internal_lag1
scores["internal_d2"]=scores.internal_now-scores.internal_lag2
scores["handoff_gap"]=scores.internal_now-scores.leadlag_score
scores["leadlag_premax_minus_now"]=scores.leadlag_score_premax-scores.leadlag_score

v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])[["feature_cutoff_date","momentum_up"]]
z=v.merge(p,on="feature_cutoff_date",how="left").merge(scores,on="feature_cutoff_date",how="left")
z=z[(z.feature_cutoff_date.dt.year==2025)&(z.feature_cutoff_date>=pd.Timestamp("2025-05-09"))].copy()
z["v5_pred"]=(pd.to_numeric(z.p_helios_v5_dce,errors="coerce")>=.5).astype(int)
z["is_reversal"]=z.y_up.astype(int)!=z.momentum_up.astype(int)
z["v5_correct"]=z.v5_pred.astype(int)==z.y_up.astype(int)
z["missed_reversal"]=(~z.v5_correct)&z.is_reversal
z["correct_continuation"]=z.v5_correct&(~z.is_reversal)

cols=["internal_d1","internal_d2","fragility_score_d1","fragility_score_d2","flow_score_d1","flow_score_d2",
      "leadlag_score_d1","leadlag_score_d2","handoff_gap","leadlag_premax_minus_now"]
rows=[]
for c in cols:
    a=pd.to_numeric(z.loc[z.missed_reversal,c],errors="coerce")
    b=pd.to_numeric(z.loc[z.correct_continuation,c],errors="coerce")
    rows.append({"feature":c,"miss_mean":float(a.mean()),"control_mean":float(b.mean()),"smd":smd(a,b)})
rdf=pd.DataFrame(rows).sort_values("smd",ascending=False)

patterns={
 "LEADLAG_PRE_TO_INTERNAL_NOW_067":(z.leadlag_score_premax>=.67)&((z.fragility_score>=.67)|(z.flow_score>=.67)),
 "EXTERNAL_PRE_TO_INTERNAL_NOW_067":((z.leadlag_score_premax>=.67)|(z.reaction_score_premax>=.67))&((z.fragility_score>=.67)|(z.flow_score>=.67)),
 "FLOW_PRE_TO_FRAGILITY_NOW_067":(z.flow_score_premax>=.67)&(z.fragility_score>=.67),
}
seq=[]
for name,mask in patterns.items():
    mm=z.missed_reversal.astype(bool); cc=z.correct_continuation.astype(bool)
    mc=float(mask[mm].mean()); cp=float(mask[cc].mean())
    seq.append({"pattern":name,"miss_coverage":mc,"control_prevalence":cp,"lift":float(mc/cp) if cp>0 else np.nan})

summary={"coverage_start":"2025-05-09","n":int(len(z)),"missed_reversals":int(z.missed_reversal.sum()),
         "correct_continuations":int(z.correct_continuation.sum()),"transition":rdf.replace({np.nan:None}).to_dict("records"),"sequences":seq}
OUTJ.write_text(json.dumps(summary,indent=2)+"\n")
lines=["# 2025 SIGNAL-TRANSITION CONSISTENCY DIAGNOSTIC","",
       "**Status:** historical consistency check only; not independent validation.","",
       f"- coverage: 2025-05-09 onward, N={len(z)}",
       f"- V5 missed reversals: {int(z.missed_reversal.sum())}",
       f"- correct continuations: {int(z.correct_continuation.sum())}","",
       "## Transition signs","",
       "| Feature | Miss mean | Control mean | SMD |","|---|---:|---:|---:|"]
for r in rdf.itertuples():
    lines.append(f"| {r.feature} | {r.miss_mean:+.3f} | {r.control_mean:+.3f} | {r.smd:+.3f} |")
lines+=["","## Sequence patterns","",
        "| Pattern | Miss coverage | Control prevalence | Lift |","|---|---:|---:|---:|"]
for r in seq:
    lines.append(f"| {r['pattern']} | {100*r['miss_coverage']:.1f}% | {100*r['control_prevalence']:.1f}% | {r['lift']:.2f}x |")
OUT.write_text("\n".join(lines)+"\n")
print(OUT.read_text())
