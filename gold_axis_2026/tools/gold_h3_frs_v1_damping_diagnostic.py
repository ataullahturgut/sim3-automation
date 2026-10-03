from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
P=AX/"GOLD_H3_FRS_V1_TOURNAMENT_PREDICTIONS_2026-10-04.csv"
OUT=AX/"GOLD_H3_FRS_V1_DAMPING_DIAGNOSTIC_2026-10-04.md"
OUTJ=AX/"GOLD_H3_FRS_V1_DAMPING_DIAGNOSTIC_2026-10-04.json"

p=pd.read_csv(P)
reps=sorted(p.representation.unique())

def ll(y,p):
    p=np.clip(p,1e-6,1-1e-6)
    return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))

# Baseline from one representation copy because the eligible rows are identical.
base=p[p.representation==reps[0]].copy()
y=base.y_up.astype(int).to_numpy()
pv=base.p_v5.to_numpy(float)
baseline={
    "n":len(base),
    "accuracy":float((base.v5_pred.astype(int).to_numpy()==y).mean()),
    "brier":float(np.mean((pv-y)**2)),
    "logloss":ll(y,pv)
}

rows=[]
for rep in reps:
    q=p[p.representation==rep].copy()
    y=q.y_up.astype(int).to_numpy()
    pv=q.p_v5.to_numpy(float)

    # DAMP-only interpretation: all fuzzy FLIP actions become DAMP; KEEP stays KEEP;
    # native DAMP stays DAMP; ABSTAIN returns p=0.5. Direction is never flipped.
    pa=[]
    for r in q.itertuples():
        if r.action=="KEEP":
            x=float(r.p_v5)
        elif r.action in ("DAMP","FLIP"):
            x=0.5+0.5*(float(r.p_v5)-0.5)
        else:
            x=0.5
        pa.append(x)
    pa=np.array(pa,float)

    rows.append({
        "representation":rep,
        "native_flip_n":int((q.action=="FLIP").sum()),
        "native_damp_n":int((q.action=="DAMP").sum()),
        "native_abstain_n":int((q.action=="ABSTAIN").sum()),
        "damp_only_brier":float(np.mean((pa-y)**2)),
        "damp_only_logloss":ll(y,pa),
        "brier_delta_vs_v5":float(np.mean((pa-y)**2)-baseline["brier"]),
        "logloss_delta_vs_v5":ll(y,pa)-baseline["logloss"]
    })

OUTJ.write_text(json.dumps({"baseline":baseline,"rows":rows},indent=2)+"\n")
lines=["# FRS-H3 V1 — DAMPING / CALIBRATION DIAGNOSTIC","",
       "**Status:** retrospective development diagnostic only.","",
       "This diagnostic does not change the fuzzy evidence layer. It asks whether fuzzy uncertainty should be used to shrink V5 confidence rather than reverse its direction.","",
       "## Same-universe V5 baseline","",
       f"- n: **{baseline['n']}**",
       f"- accuracy: **{100*baseline['accuracy']:.2f}%**",
       f"- Brier: **{baseline['brier']:.4f}**",
       f"- Log loss: **{baseline['logloss']:.4f}**","",
       "## Fuzzy DAMP-only comparison","",
       "| Representation | Native flips | Damps | Abstain | DAMP-only Brier | Δ Brier | DAMP-only logloss | Δ logloss |",
       "|---|---:|---:|---:|---:|---:|---:|---:|"]
for r in sorted(rows,key=lambda x:x["damp_only_brier"]):
    lines.append(
        f"| {r['representation']} | {r['native_flip_n']} | {r['native_damp_n']} | {r['native_abstain_n']} | "
        f"{r['damp_only_brier']:.4f} | {r['brier_delta_vs_v5']:+.4f} | "
        f"{r['damp_only_logloss']:.4f} | {r['logloss_delta_vs_v5']:+.4f} |"
    )
OUT.write_text("\n".join(lines)+"\n")
print(OUT.read_text())

# trigger: frs-damping-ready
