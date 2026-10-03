from pathlib import Path
import json, pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
P=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
OUT=AX/"GOLD_H3_RTE_CALIBRATION_DRIFT_2023_2025.json"
MD=AX/"GOLD_H3_RTE_CALIBRATION_DRIFT_2023_2025.md"

p=pd.read_csv(P)
p["feature_cutoff_date"]=pd.to_datetime(p.feature_cutoff_date)
p=p[p.year.isin([2023,2024,2025])].copy()
rows=[]
for y,g in p.groupby("year"):
    q=g.p_rte.quantile([.5,.75,.9,.95,.99]).to_dict()
    rows.append({"year":int(y),"n":len(g),"mean":float(g.p_rte.mean()),"std":float(g.p_rte.std()),
                 "q50":float(q[.5]),"q75":float(q[.75]),"q90":float(q[.9]),"q95":float(q[.95]),"q99":float(q[.99]),
                 "ge70":int((g.p_rte>=.70).sum()),"ge75":int((g.p_rte>=.75).sum()),"ge80":int((g.p_rte>=.80).sum())})
OUT.write_text(json.dumps(rows,indent=2)+"\n")
lines=["# RTE calibration drift diagnostic","",
       "**Scope:** 2023-2025 only; 2026 unopened.","",
       "| Year | n | mean | q75 | q90 | q95 | q99 | >=.70 | >=.75 | >=.80 |",
       "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for r in rows:
    lines.append(f"| {r['year']} | {r['n']} | {r['mean']:.3f} | {r['q75']:.3f} | {r['q90']:.3f} | {r['q95']:.3f} | {r['q99']:.3f} | {r['ge70']} | {r['ge75']} | {r['ge80']} |")
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())

# trigger: calibration-drift-ready
