from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
OUT_JSON=AX/"GOLD_H3_RC_RTE_STATE_SHIFT_2025H1_H2_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_RC_RTE_STATE_SHIFT_2025H1_H2_2026-10-04.md"

STATE=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","trend_close_location","opposite_extreme_recency","adverse_excursion",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]

f=pd.read_csv(FEAT)
p=pd.read_csv(PRED)
for d in (f,p):
    d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
    d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
z=p.merge(f[["feature_cutoff_date"]+STATE],on="feature_cutoff_date",how="left",validate="one_to_one")
z=z[z.year==2025].copy()
h1=z[z.forecast_issue_date.dt.month<=6]
h2=z[z.forecast_issue_date.dt.month>=7]

rows=[]
for c in STATE:
    a=h1[c].dropna().to_numpy(float); b=h2[c].dropna().to_numpy(float)
    va=np.var(a,ddof=1); vb=np.var(b,ddof=1); sp=np.sqrt((va+vb)/2)
    smd=(np.mean(b)-np.mean(a))/sp if sp>0 else np.nan
    rows.append({
        "feature":c,
        "h1_mean":float(np.mean(a)),"h2_mean":float(np.mean(b)),
        "h1_median":float(np.median(a)),"h2_median":float(np.median(b)),
        "smd_h2_minus_h1":float(smd)
    })

# Mechanism-level custom state axes, standardized on all 2024-2025 development.
dev=pd.concat([pd.read_csv(FEAT)],ignore_index=True)
dev["forecast_issue_date"]=pd.to_datetime(dev.forecast_issue_date)
dev=dev[dev.forecast_issue_date.dt.year.isin([2024,2025])].copy()
mu=dev[STATE].mean(); sd=dev[STATE].std(ddof=0).replace(0,1.0)
for df in [h1,h2]:
    for c in STATE:
        df[c+"_z"]=(df[c]-mu[c])/sd[c]

def axes(df):
    return pd.DataFrame({
        "persistence":(
            df["trend_strength_z"] + df["path_consistency_z"] + df["v5_confidence_z"]
            - df["adverse_excursion_z"] - df["opposite_semivar_share_z"]
        )/5.0,
        "fragility":(
            df["deceleration_6h_z"] + df["opposite_semivar_share_z"]
            + df["adverse_excursion_z"] - df["path_consistency_z"]
        )/4.0,
        "option_opposition":(
            df["signed_opt_pressure_z"] + df["signed_d_opt_pressure_z"]
            + df["opt_total_z20_z"]
        )/3.0,
        "participation_shock":(
            df["gc_volume_z20_z"] + df["gc_volume_accel_5_z"]
            + df["gc_dlog_volume_1_z"]
        )/3.0
    },index=df.index)

a1=axes(h1); a2=axes(h2)
axis_rows=[]
for c in a1.columns:
    x=a1[c].dropna().to_numpy(); y=a2[c].dropna().to_numpy()
    sp=np.sqrt((np.var(x,ddof=1)+np.var(y,ddof=1))/2)
    axis_rows.append({
        "axis":c,"h1_mean":float(np.mean(x)),"h2_mean":float(np.mean(y)),
        "smd_h2_minus_h1":float((np.mean(y)-np.mean(x))/sp if sp>0 else np.nan)
    })

out={"n_h1":len(h1),"n_h2":len(h2),
     "feature_shifts":rows,"axis_shifts":axis_rows}
OUT_JSON.write_text(json.dumps(out,indent=2)+"\n")
lines=["# RC-RTE — 2025 H1 → H2 ORIGIN-STATE SHIFT","",
       "**Scope:** origin-observable state only. This diagnostic does not use 2026 outcomes.","",
       f"- 2025 H1 eligible origins: **{len(h1)}**",
       f"- 2025 H2 eligible origins: **{len(h2)}**","",
       "## Largest feature shifts","",
       "| Feature | SMD H2-H1 | H1 median | H2 median |",
       "|---|---:|---:|---:|"]
for r in sorted(rows,key=lambda x:abs(x["smd_h2_minus_h1"]),reverse=True):
    lines.append(f"| {r['feature']} | {r['smd_h2_minus_h1']:+.3f} | {r['h1_median']:.4f} | {r['h2_median']:.4f} |")
lines += ["","## Mechanistic state-axis shifts","",
          "| Axis | SMD H2-H1 | H1 mean | H2 mean |",
          "|---|---:|---:|---:|"]
for r in sorted(axis_rows,key=lambda x:abs(x["smd_h2_minus_h1"]),reverse=True):
    lines.append(f"| {r['axis']} | {r['smd_h2_minus_h1']:+.3f} | {r['h1_mean']:.4f} | {r['h2_mean']:.4f} |")
OUT_MD.write_text("\n".join(lines)+"\n")
print(OUT_MD.read_text())
