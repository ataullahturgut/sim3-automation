from pathlib import Path
import numpy as np, pandas as pd, json
ROOT=Path(__file__).resolve().parents[2]; AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
OUT=AX/"GOLD_H3_CATALYST_EVENT_DIAGNOSTIC_V1B_RESULT_2026-10-04.md"
EVENTS={}
def add(k,ds):
    for d in ds: EVENTS.setdefault(pd.Timestamp(d).date(),[]).append(k)
add("CPI",["2025-01-15","2025-02-12","2025-03-12","2025-04-10","2025-05-13","2025-06-11","2025-07-15","2025-08-12","2025-09-11","2026-01-13","2026-02-13","2026-03-11","2026-04-10","2026-05-12","2026-06-10","2026-07-14","2026-08-12","2026-09-11"])
add("NFP",["2025-01-10","2025-02-07","2025-03-07","2025-04-04","2025-05-02","2025-06-06","2025-07-03","2025-08-01","2025-09-05","2026-01-09","2026-02-11","2026-03-06","2026-04-03","2026-05-08","2026-06-05","2026-07-02","2026-08-07","2026-09-04"])
add("FOMC",["2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16"])
def b(s): return s.astype(str).str.lower().isin(["true","1","yes"])
v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
p=pd.read_csv(PANEL,usecols=["feature_cutoff_date","momentum_up"],parse_dates=["feature_cutoff_date"])
z=v.merge(p,on="feature_cutoff_date",how="left",validate="one_to_one")
z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
s=pd.read_csv(SAGE,usecols=["feature_cutoff_date","ocs_candidate"],parse_dates=["feature_cutoff_date"]); s["ocs_candidate"]=b(s.ocs_candidate)
z=z.merge(s,on="feature_cutoff_date",how="left",validate="one_to_one"); z["ocs_candidate"]=z.ocs_candidate.fillna(False)
z["sage_pred"]=np.where(z.ocs_candidate,1-z.v5_pred,z.v5_pred).astype(int)
z["true_reversal"]=z.y_up.astype(int).ne(z.momentum_up.astype(int))
z["v5_missrev"]=z.true_reversal & z.v5_pred.eq(z.momentum_up.astype(int))
z["sage_missrev"]=z.true_reversal & z.sage_pred.eq(z.momentum_up.astype(int))
z["v5_err"]=z.v5_pred.ne(z.y_up.astype(int)); z["sage_err"]=z.sage_pred.ne(z.y_up.astype(int))
z=z[(z.feature_cutoff_date>=pd.Timestamp("2025-01-01"))&(z.feature_cutoff_date<=pd.Timestamp("2026-09-24"))].copy()
z["event_types"]=z.feature_cutoff_date.dt.date.map(lambda d:"+".join(EVENTS.get(d,[])))
lines=["# CATALYST V1B — EVENT TYPE × YEAR","", "| Year | Type | N | Reversal | V5 err | V5 miss-rev | SAGE err | SAGE miss-rev | Mean |H3| |","|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
for y in [2025,2026]:
  for k in ["CPI","NFP","FOMC"]:
    g=z[(z.feature_cutoff_date.dt.year==y)&z.event_types.str.contains(k,regex=False)]
    lines.append(f"| {y} | {k} | {len(g)} | {100*g.true_reversal.mean():.2f}% | {100*g.v5_err.mean():.2f}% | {int(g.v5_missrev.sum())} | {100*g.sage_err.mean():.2f}% | {int(g.sage_missrev.sum())} | {100*g.target_r3.abs().mean():.2f}% |")
OUT.write_text("\n".join(lines)+"\n"); print(OUT.read_text())