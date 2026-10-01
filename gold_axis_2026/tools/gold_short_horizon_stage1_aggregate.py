import os,glob,json,hashlib
from pathlib import Path
import pandas as pd
import numpy as np

OUT=Path("stage1_all")
OUT.mkdir(exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

# collect per-horizon artifacts staged by workflow download steps
metrics=[]; qsum=[]; qdetail=[]
for p in glob.glob("h*/stage1_h*_metrics.csv"):
    metrics.append(pd.read_csv(p))
for p in glob.glob("h*/stage1_h*_quantile_summary.csv"):
    qsum.append(pd.read_csv(p))
for p in glob.glob("h*/stage1_h*_quantile_metrics.csv"):
    qdetail.append(pd.read_csv(p))
m=pd.concat(metrics,ignore_index=True)
qs=pd.concat(qsum,ignore_index=True)
qd=pd.concat(qdetail,ignore_index=True)
m.to_csv(OUT/"stage1_metrics_all.csv",index=False)
qs.to_csv(OUT/"stage1_quantile_summary_all.csv",index=False)
qd.to_csv(OUT/"stage1_quantile_metrics_all.csv",index=False)

decisions=[]
for h in [1,3,5]:
    z=m[m.horizon==h]
    # direction
    zd=z[z.head=="direction"].copy()
    base=zd[zd.feature_block=="BASE"]
    bb=float(base.brier.min()); bll=float(base.logloss.min())
    cand=zd[zd.feature_block!="BASE"].copy()
    cand["rel_improve"]=(bb-cand.brier)/bb
    cand["gate"]=(cand.rel_improve>=0.01)&(cand.logloss<=bll)&(cand.prediction_std>1e-5)
    cpass=cand[cand.gate]
    bestd=(cpass if len(cpass) else cand).sort_values("rel_improve",ascending=False).iloc[0]
    decisions.append({
        "horizon":h,"head":"direction","status":"PASS" if bool(bestd.gate) else "NO_PASS",
        "feature_block":bestd.feature_block,"model":bestd.model,
        "primary":float(bestd.brier),"baseline":bb,"rel_improve":float(bestd.rel_improve)
    })
    # return
    zr=z[z.head=="return"].copy()
    base=zr[zr.feature_block=="BASE"]
    bmae=float(base.mae.min()); brmse=float(base.rmse.min())
    cand=zr[zr.feature_block!="BASE"].copy()
    cand["rel_improve"]=(bmae-cand.mae)/bmae
    cand["gate"]=(cand.rel_improve>=0.01)&(cand.rmse<=brmse)
    cpass=cand[cand.gate]
    bestr=(cpass if len(cpass) else cand).sort_values("rel_improve",ascending=False).iloc[0]
    decisions.append({
        "horizon":h,"head":"return","status":"PASS" if bool(bestr.gate) else "NO_PASS",
        "feature_block":bestr.feature_block,"model":bestr.model,
        "primary":float(bestr.mae),"baseline":bmae,"rel_improve":float(bestr.rel_improve)
    })
    # quantile
    zq=qs[qs.horizon==h].copy()
    base=zq[zq.feature_block=="BASE"]
    bpin=float(base.mean_pinball.min())
    cand=zq[zq.feature_block!="BASE"].copy()
    cand["rel_improve"]=(bpin-cand.mean_pinball)/bpin
    cand["gate"]=cand.rel_improve>=0.01
    cpass=cand[cand.gate]
    bestq=(cpass if len(cpass) else cand).sort_values("rel_improve",ascending=False).iloc[0]
    decisions.append({
        "horizon":h,"head":"quantile","status":"PASS" if bool(bestq.gate) else "NO_PASS",
        "feature_block":bestq.feature_block,"model":bestq.model,
        "primary":float(bestq.mean_pinball),"baseline":bpin,"rel_improve":float(bestq.rel_improve)
    })

d=pd.DataFrame(decisions)
d.to_csv(OUT/"stage1_decisions.csv",index=False)

lines=[
"# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 1 First Model Screen Result","",
"## Target decisions","",
"| Horizon | Head | Status | Best feature | Best model | Primary | Baseline | Relative improvement |",
"|---|---|---|---|---|---:|---:|---:|",
]
for _,r in d.iterrows():
    lines.append(f"| H{int(r.horizon)} | {r.head} | {r.status} | {r.feature_block} | {r.model} | {r.primary:.6f} | {r.baseline:.6f} | {100*r.rel_improve:.2f}% |")

# Horizon summary using number and magnitude of passes
hs=[]
for h in [1,3,5]:
    q=d[d.horizon==h]
    hs.append({
        "horizon":h,
        "pass_heads":int((q.status=="PASS").sum()),
        "mean_rel_improve":float(q.rel_improve.mean())
    })
hdf=pd.DataFrame(hs)
hdf.to_csv(OUT/"stage1_horizon_summary.csv",index=False)

lines += ["","## Horizon summary",""]
for _,r in hdf.iterrows():
    lines.append(f"- H{int(r.horizon)}: {int(r.pass_heads)}/3 forecast heads PASS; mean relative improvement across heads {100*r.mean_rel_improve:.2f}%.")

overall="PASS" if (d.status=="PASS").any() else "NO_SIGNAL"
lines += ["","## Binding interpretation",f"Stage 1 overall status: **{overall}**.",""]
if overall=="PASS":
    lines.append("At least one horizon/head contains pre-2025 predictive signal. Freeze the successful first-screen evidence before any 2025 transport. Do not yet build the tactical allocation layer until head reconciliation is complete.")
else:
    lines.append("No first-screen head clears its frozen baseline gate. Do not inspect 2025 to rescue the screen; revise features/targets on DEV only.")

(OUT/"STAGE1_RESULT.md").write_text("\n".join(lines),encoding="utf-8")

files=list(OUT.iterdir())
summary={
    "status":overall,
    "decisions":d.to_dict(orient="records"),
    "horizons":hdf.to_dict(orient="records"),
    "hashes":{p.name:sha(p) for p in files}
}
(OUT/"stage1_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("STAGE1_SUMMARY="+json.dumps(summary,separators=(",",":")))
print((OUT/"STAGE1_RESULT.md").read_text())
