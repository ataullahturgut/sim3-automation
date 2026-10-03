from pathlib import Path
import json, numpy as np, pandas as pd
from sklearn.cluster import KMeans

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MAT=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"
OUT=AX/"GOLD_H3_RC_RTE_2025H2_CANDIDATE_CHRONOLOGY_2026-10-04.csv"
MD=AX/"GOLD_H3_RC_RTE_2025H2_CANDIDATE_CHRONOLOGY_2026-10-04.md"

RAW=["v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","adverse_excursion","gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"]
AXES=["persistence","fragility","option_opposition","participation_shock"]

def load():
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
    return z.dropna(subset=RAW).reset_index(drop=True)

def axes(train,df):
    mu=train[RAW].mean(); sd=train[RAW].std(ddof=0).replace(0,1)
    q=df.copy()
    for c in RAW: q[c+"_z"]=(q[c]-mu[c])/sd[c]
    q["persistence"]=(q.trend_strength_z+q.path_consistency_z+q.v5_confidence_z-q.adverse_excursion_z-q.opposite_semivar_share_z)/5
    q["fragility"]=(q.deceleration_6h_z+q.opposite_semivar_share_z+q.adverse_excursion_z-q.path_consistency_z)/4
    q["option_opposition"]=(q.signed_opt_pressure_z+q.signed_d_opt_pressure_z+q.opt_total_z20_z)/3
    q["participation_shock"]=(q.gc_volume_z20_z+q.gc_volume_accel_5_z+q.gc_dlog_volume_1_z)/3
    return q

z=load()
train=z[z.forecast_issue_date<pd.Timestamp("2025-07-01")].copy()
test=z[(z.forecast_issue_date>=pd.Timestamp("2025-07-01"))&(z.forecast_issue_date<=pd.Timestamp("2025-12-31"))].copy()
train=axes(train,train); test=axes(train,test)
km=KMeans(n_clusters=3,n_init=50,random_state=20261004)
km.fit(train[AXES])
train["regime"]=km.predict(train[AXES]); test["regime"]=km.predict(test[AXES])
enabled=[]
audit=[]
for reg,g in train.groupby("regime"):
    q=g[g.proposal]
    r=int(q.rescue_target.sum()); b=len(q)-r
    ok=len(q)>=8 and r/max(len(q),1)>=.55 and r-b>0
    audit.append((int(reg),len(q),r,b,r-b,r/max(len(q),1),ok))
    if ok: enabled.append(int(reg))
test["static_candidate"]=test.proposal&test.regime.isin(enabled)
q=test[test.static_candidate].copy()
q["effect"]=np.where(q.rescue_target==1,"RESCUE","BROKEN")
q["utility"]=np.where(q.rescue_target==1,1,-1)
q["cum_utility"]=q.utility.cumsum()
# outcome becomes available only at target_end; for each candidate, matured prior candidate utility
hist=[]
for r in q.itertuples():
    prior=q[(q.target_end_date_h3<=r.feature_cutoff_date)&(q.forecast_issue_date<r.forecast_issue_date)]
    preg=prior[prior.regime==r.regime]
    row=r._asdict()
    row["matured_prior_all_n"]=len(prior)
    row["matured_prior_all_net"]=int(prior.utility.sum()) if len(prior) else 0
    row["matured_prior_regime_n"]=len(preg)
    row["matured_prior_regime_net"]=int(preg.utility.sum()) if len(preg) else 0
    row["matured_prior_regime_last5_net"]=int(preg.tail(5).utility.sum()) if len(preg) else 0
    hist.append(row)
h=pd.DataFrame(hist)
h.to_csv(OUT,index=False)
lines=["# RC-RTE 2025 H2 — CANDIDATE CHRONOLOGY","",
       f"- enabled regimes from pre-H2 training: **{enabled}**",
       f"- static candidates: **{len(h)}**",
       f"- rescue / broken / net: **{int((h.effect=='RESCUE').sum())} / {int((h.effect=='BROKEN').sum())} / {int(h.utility.sum()):+d}**","",
       "## Pre-H2 regime audit","",
       "| Regime | Support | Rescue | Broken | Net | Precision | Enabled |",
       "|---:|---:|---:|---:|---:|---:|---|"]
for x in audit:
    lines.append(f"| {x[0]} | {x[1]} | {x[2]} | {x[3]} | {x[4]:+d} | {100*x[5]:.1f}% | {x[6]} |")
lines += ["","## Candidate sequence","",
          "| Issue | End | Regime | SB | OPT | MAT | Effect | Cum net | Matured regime n | Matured regime net | Last5 net |",
          "|---|---|---:|---|---|---|---|---:|---:|---:|---:|"]
for r in h.itertuples():
    lines.append(f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | {r.regime} | {r.sb} | {r.opt} | {r.mat} | {r.effect} | {r.cum_utility:+d} | {r.matured_prior_regime_n} | {r.matured_prior_regime_net:+d} | {r.matured_prior_regime_last5_net:+d} |")
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())
