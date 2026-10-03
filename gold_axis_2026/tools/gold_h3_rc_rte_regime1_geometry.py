from pathlib import Path
import json, numpy as np, pandas as pd
from sklearn.cluster import KMeans

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MAT=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"
HOLD=AX/"GOLD_H3_RC_RTE_V2_FUSE_2026_HOLDOUT_2026-10-04.csv"
OUT=AX/"GOLD_H3_RC_RTE_REGIME1_GEOMETRY_DIAGNOSTIC_2026-10-04.md"

RAW=["v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","adverse_excursion","gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"]
AXES=["persistence","fragility","option_opposition","participation_shock"]
SEED=20261004

p=pd.read_csv(PRED); f=pd.read_csv(FEAT); m=pd.read_csv(MAT)
for d in [p,f,m]:
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        if c in d.columns: d[c]=pd.to_datetime(d[c])
z=p.merge(f[["feature_cutoff_date"]+RAW],on="feature_cutoff_date",how="left",validate="one_to_one")
z=z.merge(m[["feature_cutoff_date","p_material"]],on="feature_cutoff_date",how="left",validate="one_to_one")
z=z.sort_values("forecast_issue_date").reset_index(drop=True)
z["prev_p_rte"]=z.p_rte.shift(1); z["prev_mom"]=z.momentum_up.shift(1); z["prev_date"]=z.feature_cutoff_date.shift(1)
seq=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
z["dp_rte"]=np.where(seq,z.p_rte-z.prev_p_rte,np.nan)
z["sb"]=(z.p_rte>=.75)&(z.prev_p_rte>=.60)&(z.dp_rte<=.05)
z["opt"]=(z.p_rte>=.65)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)
z["mat"]=z.p_material.fillna(-1)>=.70
z["proposal"]=z.sb|z.opt|z.mat
z=z.dropna(subset=RAW)
tr=z[z.forecast_issue_date<pd.Timestamp("2026-01-01")].copy()

mu=tr[RAW].mean(); sd=tr[RAW].std(ddof=0).replace(0,1)
for c in RAW: tr[c+"_z"]=(tr[c]-mu[c])/sd[c]
tr["persistence"]=(tr.trend_strength_z+tr.path_consistency_z+tr.v5_confidence_z-tr.adverse_excursion_z-tr.opposite_semivar_share_z)/5
tr["fragility"]=(tr.deceleration_6h_z+tr.opposite_semivar_share_z+tr.adverse_excursion_z-tr.path_consistency_z)/4
tr["option_opposition"]=(tr.signed_opt_pressure_z+tr.signed_d_opt_pressure_z+tr.opt_total_z20_z)/3
tr["participation_shock"]=(tr.gc_volume_z20_z+tr.gc_volume_accel_5_z+tr.gc_dlog_volume_1_z)/3
km=KMeans(n_clusters=3,n_init=50,random_state=SEED)
tr["regime"]=km.fit_predict(tr[AXES])

q=tr[(tr.regime==1)&tr.proposal].copy()
res=q[q.rescue_target==1]; bro=q[q.rescue_target==0]

rows=[]
for c in AXES+RAW:
    a=res[c].dropna().to_numpy(float); b=bro[c].dropna().to_numpy(float)
    sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2) if len(a)>1 and len(b)>1 else np.nan
    smd=(np.mean(a)-np.mean(b))/sp if np.isfinite(sp) and sp>0 else np.nan
    rows.append((c,float(np.median(a)) if len(a) else np.nan,float(np.median(b)) if len(b) else np.nan,float(smd) if np.isfinite(smd) else np.nan))

hold=pd.read_csv(HOLD)
acc=hold[hold.rc_v2_candidate.astype(bool)].copy()
# holdout already contains axis columns calculated under the same final pre-2026 fit.
candidate={}
if len(acc):
    r=acc.iloc[0]
    candidate={c:float(r[c]) for c in AXES}
    candidate["issue"]=str(r.forecast_issue_date)
    candidate["target_r3"]=float(r.target_r3)
    candidate["rescue_target"]=int(r.rescue_target)

lines=["# RC-RTE — REGIME 1 GEOMETRY DIAGNOSTIC","",
       "**Status:** post-holdout diagnostic. 2026 is already spent; this document cannot support a clean 2026 improvement claim.","",
       f"- pre-2026 regime-1 proposals: **{len(q)}**",
       f"- rescue / broken: **{len(res)} / {len(bro)}**","",
       "## Rescue vs broken geometry inside regime 1","",
       "| Variable | Rescue median | Broken median | SMD rescue-broken |",
       "|---|---:|---:|---:|"]
for c,a,b,s in sorted(rows,key=lambda x:abs(x[3]) if np.isfinite(x[3]) else -1,reverse=True):
    lines.append(f"| {c} | {a:.4f} | {b:.4f} | {s:+.3f} |")
if candidate:
    lines += ["","## The single accepted 2026 candidate","",
              f"- issue: **{candidate['issue']}**",
              f"- target H3 return: **{100*candidate['target_r3']:.2f}%**",
              f"- rescue_target: **{candidate['rescue_target']}**"]
    for c in AXES:
        lines.append(f"- {c}: **{candidate[c]:+.3f}**")
OUT.write_text("\n".join(lines)+"\n")
print(OUT.read_text())
