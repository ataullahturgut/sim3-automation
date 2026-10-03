from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
OUT=AX/"GOLD_H3_OAR_Q60_FALSE_ALARM_DIAGNOSTIC_2026-10-04.json"
MD=AX/"GOLD_H3_OAR_Q60_FALSE_ALARM_DIAGNOSTIC_2026-10-04.md"

FEATURES=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","trend_close_location","opposite_extreme_recency","adverse_excursion",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20",
"cf_deceleration_6h_gap","cf_opposite_semivar_share_gap","cf_adverse_excursion_gap",
"cf_signed_opt_pressure_gap","cf_signed_d_opt_pressure_gap","cf_gc_dlog_volume_1_gap",
"cf_opt_total_z20_gap","p_rte","p_inst","rte_tension"
]

p=pd.read_csv(PRED); f=pd.read_csv(FEAT)
for d in [p,f]:
    d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
    d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
z=p.merge(f[["feature_cutoff_date"]+[c for c in FEATURES if c not in p.columns]],
          on="feature_cutoff_date",how="left",validate="one_to_one")
q=z[
    z.year.isin([2024,2025])
    &(z.p_rte>=.60)&(z.p_inst>=.50)
    &(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
].copy()
q["effect"]=np.where(q.rescue_target==1,"RESCUE","BROKEN")

resc=q[q.effect=="RESCUE"]; brok=q[q.effect=="BROKEN"]
rows=[]
for c in FEATURES:
    a=resc[c].dropna().to_numpy(float); b=brok[c].dropna().to_numpy(float)
    if len(a)>1 and len(b)>1:
        sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
        smd=(np.mean(a)-np.mean(b))/sp if sp>0 else np.nan
    else: smd=np.nan
    rows.append({
        "feature":c,"smd_rescue_minus_broken":float(smd),
        "rescue_median":float(np.median(a)) if len(a) else np.nan,
        "broken_median":float(np.median(b)) if len(b) else np.nan
    })

# H2 2025 candidate rows for direct inspection.
h2=q[(q.year==2025)&(q.forecast_issue_date.dt.month>=7)].copy()
out={"n":len(q),"rescued":len(resc),"broken":len(brok),
     "separation":rows,
     "h2_2025":h2[["forecast_issue_date","target_end_date_h3","effect"]+FEATURES].to_dict("records")}
OUT.write_text(json.dumps(out,indent=2,default=str)+"\n")
lines=["# OAR q=0.60 — FALSE-ALARM DIAGNOSTIC","",
       "**Scope:** 2024-2025 development only. 2026 unopened.","",
       f"- candidates: **{len(q)}**",
       f"- rescue / broken: **{len(resc)} / {len(brok)}**","",
       "## Largest rescue-vs-broken separations","",
       "| Feature | SMD rescue-broken | Rescue median | Broken median |",
       "|---|---:|---:|---:|"]
for r in sorted(rows,key=lambda x:abs(x["smd_rescue_minus_broken"]) if np.isfinite(x["smd_rescue_minus_broken"]) else -1,reverse=True):
    lines.append(f"| {r['feature']} | {r['smd_rescue_minus_broken']:+.3f} | {r['rescue_median']:.4f} | {r['broken_median']:.4f} |")
lines += ["","## 2025 H2 OAR candidates","",
          "| Issue | End | Effect | V5 conf | Trend str | Path consistency | Adverse | Opt pressure | dOpt pressure | pRTE | pInst |",
          "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for r in h2.itertuples():
    lines.append(
        f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | {r.effect} | "
        f"{r.v5_confidence:.3f} | {r.trend_strength:.3f} | {r.path_consistency:.3f} | {r.adverse_excursion:.3f} | "
        f"{r.signed_opt_pressure:.3f} | {r.signed_d_opt_pressure:.3f} | {r.p_rte:.3f} | {r.p_inst:.3f} |"
    )
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())
