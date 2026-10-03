from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MAT=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"
OUT=AX/"GOLD_H3_RC_RTE_SPECIALIST_REGIME_AUDIT_PRE2026_2026-10-04.csv"
MD=AX/"GOLD_H3_RC_RTE_SPECIALIST_REGIME_AUDIT_PRE2026_2026-10-04.md"

SEED=20261004
RAW=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","adverse_excursion","gc_dlog_volume_1","gc_volume_z20",
"gc_volume_accel_5","signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]
AXES=["persistence","fragility","option_opposition","participation_shock"]

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
z=z.dropna(subset=RAW)
train=z[z.forecast_issue_date<pd.Timestamp("2026-01-01")].copy()

mu=train[RAW].mean(); sd=train[RAW].std(ddof=0).replace(0,1)
for c in RAW: train[c+"_z"]=(train[c]-mu[c])/sd[c]
train["persistence"]=(train.trend_strength_z+train.path_consistency_z+train.v5_confidence_z-train.adverse_excursion_z-train.opposite_semivar_share_z)/5
train["fragility"]=(train.deceleration_6h_z+train.opposite_semivar_share_z+train.adverse_excursion_z-train.path_consistency_z)/4
train["option_opposition"]=(train.signed_opt_pressure_z+train.signed_d_opt_pressure_z+train.opt_total_z20_z)/3
train["participation_shock"]=(train.gc_volume_z20_z+train.gc_volume_accel_5_z+train.gc_dlog_volume_1_z)/3

km=KMeans(n_clusters=3,n_init=50,random_state=SEED)
train["regime"]=km.fit_predict(train[AXES])

rows=[]
for reg,g in train.groupby("regime"):
    for spec in ["sb","opt","mat"]:
        q=g[g[spec]].copy()
        n=len(q); r=int(q.rescue_target.sum()); b=n-r
        rows.append({
            "regime":int(reg),"specialist":spec.upper(),"support":n,
            "rescued":r,"broken":b,"net":r-b,"precision":r/max(n,1),
            "regime_persistence":float(g.persistence.mean()),
            "regime_fragility":float(g.fragility.mean()),
            "regime_option_opposition":float(g.option_opposition.mean()),
            "regime_participation_shock":float(g.participation_shock.mean())
        })
    # exact proposal combinations to expose interaction/overlap
    combos={
        "SB_ONLY":g.sb & ~g.opt & ~g.mat,
        "OPT_ONLY":g.opt & ~g.sb & ~g.mat,
        "MAT_ONLY":g.mat & ~g.sb & ~g.opt,
        "MULTI":(g[["sb","opt","mat"]].sum(axis=1)>=2)
    }
    for name,mask in combos.items():
        q=g[mask].copy()
        n=len(q); r=int(q.rescue_target.sum()); b=n-r
        rows.append({
            "regime":int(reg),"specialist":name,"support":n,
            "rescued":r,"broken":b,"net":r-b,"precision":r/max(n,1),
            "regime_persistence":float(g.persistence.mean()),
            "regime_fragility":float(g.fragility.mean()),
            "regime_option_opposition":float(g.option_opposition.mean()),
            "regime_participation_shock":float(g.participation_shock.mean())
        })

df=pd.DataFrame(rows)
df.to_csv(OUT,index=False)

lines=["# RC-RTE — PRE-2026 REGIME × SPECIALIST AUDIT","",
       "**Scope:** training through 2025 only. This audit is computed after the 2026 holdout was spent, so it is diagnostic for future designs and must not be used to claim a clean 2026 improvement.","",
       "| Regime | Specialist | Support | Rescue | Broken | Net | Precision |",
       "|---:|---|---:|---:|---:|---:|---:|"]
for r in df.itertuples():
    lines.append(f"| {r.regime} | {r.specialist} | {r.support} | {r.rescued} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% |")
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())
