from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
P=AX/"GOLD_H3_FRS_V1_TOURNAMENT_PREDICTIONS_2026-10-04.csv"
OUT=AX/"GOLD_H3_FRS_V1_DAMPING_BLOCK_STABILITY_2026-10-04.md"
OUTJ=AX/"GOLD_H3_FRS_V1_DAMPING_BLOCK_STABILITY_2026-10-04.json"

p=pd.read_csv(P)
p["forecast_issue_date"]=pd.to_datetime(p.forecast_issue_date)

def block_name(d):
    if d.year==2024: return "2024_H2"
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def ll(y,p):
    p=np.clip(p,1e-6,1-1e-6)
    return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))

rows=[]
for rep in ["IFS","HESITANT","NEUTROSOPHIC"]:
    q=p[p.representation==rep].copy()
    q["block"]=q.forecast_issue_date.map(block_name)
    for block,g in q.groupby("block",sort=False):
        y=g.y_up.astype(int).to_numpy()
        pv=g.p_v5.to_numpy(float)
        pa=[]
        for r in g.itertuples():
            if r.action=="KEEP":
                x=float(r.p_v5)
            elif r.action in ("DAMP","FLIP"):
                x=.5+.5*(float(r.p_v5)-.5)
            else:
                x=.5
            pa.append(x)
        pa=np.array(pa,float)
        bb=float(np.mean((pv-y)**2)); ba=float(np.mean((pa-y)**2))
        lb=ll(y,pv); la=ll(y,pa)
        rows.append({"representation":rep,"block":block,"n":len(g),
                     "v5_brier":bb,"damp_brier":ba,"delta_brier":ba-bb,
                     "v5_logloss":lb,"damp_logloss":la,"delta_logloss":la-lb})
OUTJ.write_text(json.dumps(rows,indent=2)+"\n")
lines=["# FRS V1 — FUZZY DAMPING BLOCK STABILITY","",
       "**Retrospective development diagnostic only.**","",
       "| Representation | Block | n | V5 Brier | DAMP Brier | Δ Brier | V5 logloss | DAMP logloss | Δ logloss |",
       "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
for r in rows:
    lines.append(f"| {r['representation']} | {r['block']} | {r['n']} | {r['v5_brier']:.4f} | {r['damp_brier']:.4f} | {r['delta_brier']:+.4f} | {r['v5_logloss']:.4f} | {r['damp_logloss']:.4f} | {r['delta_logloss']:+.4f} |")
OUT.write_text("\n".join(lines)+"\n")
print(OUT.read_text())

# trigger: frs-damping-block-stability-ready
