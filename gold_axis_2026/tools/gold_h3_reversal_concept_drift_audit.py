from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
SEC=AX/"GOLD_H3_SECULAR_REJOIN_DIAGNOSTIC_2026-10-04.csv"
OUT=AX/"GOLD_H3_REVERSAL_CONCEPT_DRIFT_AUDIT_2026-10-04.json"
MD=AX/"GOLD_H3_REVERSAL_CONCEPT_DRIFT_AUDIT_2026-10-04.md"

FEATURES=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","trend_close_location","opposite_extreme_recency","adverse_excursion",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20",
"cf_deceleration_6h_gap","cf_opposite_semivar_share_gap","cf_adverse_excursion_gap",
"cf_signed_opt_pressure_gap","cf_signed_d_opt_pressure_gap","cf_gc_dlog_volume_1_gap",
"cf_opt_total_z20_gap","p_rte","p_inst","rte_tension"
]

p=pd.read_csv(PRED); f=pd.read_csv(FEAT); s=pd.read_csv(SEC)
for d in [p,f,s]:
    if "feature_cutoff_date" in d: d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
z=p.merge(f[["feature_cutoff_date"]+[c for c in FEATURES if c not in p.columns]],
          on="feature_cutoff_date",how="left",validate="one_to_one")
z=z[z.year.isin([2024,2025,2026])].copy()
z=z[
    (z.p_rte>=.60)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
].copy()

def smd_pos_neg(q,c):
    a=q[q.rescue_target==1][c].dropna().to_numpy(float)
    b=q[q.rescue_target==0][c].dropna().to_numpy(float)
    if len(a)<2 or len(b)<2: return np.nan
    sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
    return (np.mean(a)-np.mean(b))/sp if sp>0 else np.nan

rows=[]
dev=z[z.year.isin([2024,2025])]
tst=z[z.year==2026]
for c in FEATURES:
    sd=smd_pos_neg(dev,c); s26=smd_pos_neg(tst,c)
    rows.append({
        "feature":c,
        "smd_2024_2025":float(sd) if np.isfinite(sd) else np.nan,
        "smd_2026":float(s26) if np.isfinite(s26) else np.nan,
        "same_sign":bool(np.sign(sd)==np.sign(s26)) if np.isfinite(sd) and np.isfinite(s26) else None,
        "abs_change":float(abs(s26-sd)) if np.isfinite(sd) and np.isfinite(s26) else np.nan,
        "dev_rescue_median":float(dev[dev.rescue_target==1][c].median()),
        "dev_broken_median":float(dev[dev.rescue_target==0][c].median()),
        "y26_rescue_median":float(tst[tst.rescue_target==1][c].median()),
        "y26_broken_median":float(tst[tst.rescue_target==0][c].median()),
    })
rdf=pd.DataFrame(rows)
valid=rdf.dropna(subset=["smd_2024_2025","smd_2026"])
sign_ret=float(valid.same_sign.mean()) if len(valid) else np.nan
corr=float(valid.smd_2024_2025.corr(valid.smd_2026)) if len(valid)>1 else np.nan

# Unconditional state shift between OAR candidates, separate from conditional label relation.
shift=[]
for c in FEATURES:
    a=dev[c].dropna().to_numpy(float); b=tst[c].dropna().to_numpy(float)
    if len(a)>1 and len(b)>1:
        sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
        d=(np.mean(b)-np.mean(a))/sp if sp>0 else np.nan
    else: d=np.nan
    shift.append({"feature":c,"smd_2026_minus_dev":float(d)})

out={
    "oar_dev_n":len(dev),"oar_2026_n":len(tst),
    "dev_rescue_rate":float(dev.rescue_target.mean()),
    "y26_rescue_rate":float(tst.rescue_target.mean()),
    "conditional_smd_sign_retention":sign_ret,
    "conditional_smd_correlation":corr,
    "conditional_effects":rows,
    "unconditional_shift":shift
}
OUT.write_text(json.dumps(out,indent=2,default=str)+"\n")

lines=["# REVERSAL CONCEPT-DRIFT AUDIT — OAR CANDIDATES","",
       "**Evidence class:** post-holdout diagnostic. 2026 is development evidence here.","",
       f"- OAR 2024-2025: **{len(dev)}**, rescue rate **{100*dev.rescue_target.mean():.2f}%**",
       f"- OAR 2026: **{len(tst)}**, rescue rate **{100*tst.rescue_target.mean():.2f}%**",
       f"- rescue-vs-broken feature-effect sign retention: **{100*sign_ret:.1f}%**",
       f"- correlation of feature SMDs (2024-25 vs 2026): **{corr:+.3f}**","",
       "## Largest conditional-effect changes","",
       "| Feature | SMD 2024-25 | SMD 2026 | Same sign | |ΔSMD| |",
       "|---|---:|---:|---|---:|"]
for r in rdf.sort_values("abs_change",ascending=False).itertuples():
    lines.append(f"| {r.feature} | {r.smd_2024_2025:+.3f} | {r.smd_2026:+.3f} | {r.same_sign} | {r.abs_change:.3f} |")
lines += ["","## Largest unconditional OAR-state shifts into 2026","",
          "| Feature | SMD 2026 - 2024/25 |",
          "|---|---:|"]
for r in sorted(shift,key=lambda x:abs(x["smd_2026_minus_dev"]) if np.isfinite(x["smd_2026_minus_dev"]) else -1,reverse=True):
    lines.append(f"| {r['feature']} | {r['smd_2026_minus_dev']:+.3f} |")
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())

# trigger: concept-drift-ready
