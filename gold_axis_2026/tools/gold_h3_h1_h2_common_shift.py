from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
OUT=AX/"GOLD_H3_H1_H2_COMMON_STATE_SHIFT_2024_2025_2026-10-04.json"
MD=AX/"GOLD_H3_H1_H2_COMMON_STATE_SHIFT_2024_2025_2026-10-04.md"

STATE=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","trend_close_location","opposite_extreme_recency","adverse_excursion",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]

f=pd.read_csv(FEAT); p=pd.read_csv(PRED)
for d in [f,p]:
    d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
    d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
z=p.merge(f[["feature_cutoff_date"]+STATE],on="feature_cutoff_date",how="left",validate="one_to_one")

rows=[]
for y in [2024,2025]:
    q=z[z.year==y].copy()
    h1=q[q.forecast_issue_date.dt.month<=6]; h2=q[q.forecast_issue_date.dt.month>=7]
    for c in STATE:
        a=h1[c].dropna().to_numpy(float); b=h2[c].dropna().to_numpy(float)
        sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
        smd=(np.mean(b)-np.mean(a))/sp if sp>0 else np.nan
        rows.append({"year":y,"feature":c,"smd_h2_minus_h1":float(smd),
                     "h1_mean":float(np.mean(a)),"h2_mean":float(np.mean(b))})
perf=[]
for y in [2024,2025]:
    for half,mask in [("H1",z.forecast_issue_date.dt.month<=6),("H2",z.forecast_issue_date.dt.month>=7)]:
        q=z[(z.year==y)&mask].copy()
        perf.append({"year":y,"half":half,"n":len(q),
                     "v5_accuracy":float((q.v5_pred.astype(int)==q.y_up.astype(int)).mean()),
                     "missed_reversal_rate":float(q.rescue_target.mean())})

r=pd.DataFrame(rows)
wide=r.pivot(index="feature",columns="year",values="smd_h2_minus_h1").reset_index()
wide["same_sign"]=np.sign(wide[2024])==np.sign(wide[2025])
wide["common_strength"]=np.where(wide.same_sign,np.minimum(np.abs(wide[2024]),np.abs(wide[2025])),0.0)
wide=wide.sort_values("common_strength",ascending=False)

out={"feature_shifts":rows,"common":wide.to_dict("records"),"performance":perf}
OUT.write_text(json.dumps(out,indent=2,default=str)+"\n")
lines=["# H1→H2 COMMON STATE SHIFT — 2024 & 2025","",
       "## V5 continuation-universe performance","",
       "| Year | Half | n | V5 accuracy | Missed-reversal rate |",
       "|---:|---|---:|---:|---:|"]
for x in perf:
    lines.append(f"| {x['year']} | {x['half']} | {x['n']} | {100*x['v5_accuracy']:.2f}% | {100*x['missed_reversal_rate']:.2f}% |")
lines += ["","## State shifts repeated in both years","",
          "| Feature | 2024 SMD H2-H1 | 2025 SMD H2-H1 | Same sign | Common strength |",
          "|---|---:|---:|---|---:|"]
for x in wide.itertuples():
    lines.append(f"| {x.feature} | {getattr(x,'_2'):+.3f} | {getattr(x,'_3'):+.3f} | {x.same_sign} | {x.common_strength:.3f} |")
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())
