from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
OUT=AX/"GOLD_H3_RTE_2025_SHOCK_DIAGNOSTIC.json"
MD=AX/"GOLD_H3_RTE_2025_SHOCK_DIAGNOSTIC.md"

p=pd.read_csv(PRED)
f=pd.read_csv(FEAT)
for d in [p,f]:
    d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
    d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
z=p.merge(f[["feature_cutoff_date","signed_opt_pressure","signed_d_opt_pressure",
             "cf_signed_opt_pressure_gap","cf_signed_d_opt_pressure_gap",
             "cf_opt_total_z20_gap","deceleration_6h","path_consistency",
             "adverse_excursion","opposite_extreme_recency"]],
          on="feature_cutoff_date",how="left",validate="one_to_one")
z=z.sort_values("forecast_issue_date").reset_index(drop=True)
z["prev_p_rte"]=z.p_rte.shift(1); z["prev_mom"]=z.momentum_up.shift(1); z["prev_date"]=z.feature_cutoff_date.shift(1)
same=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
z["dp_rte"]=np.where(same,z.p_rte-z.prev_p_rte,np.nan)
q=z[z.year==2025].copy()

rows=[]
for th in [0.65,0.70,0.75,0.80]:
    for dp_mode,maskdp in [
        ("ALL",pd.Series(True,index=q.index)),
        ("PLATEAU",q.dp_rte<=0.05),
        ("SHOCK",q.dp_rte>0.05),
        ("BIG_SHOCK",q.dp_rte>0.15),
    ]:
        c=(q.p_rte>=th)&maskdp.fillna(False)
        y=q.rescue_target.astype(bool)
        r=int((c&y).sum()); b=int((c&~y).sum())
        rows.append({"threshold":th,"mode":dp_mode,"candidate_n":int(c.sum()),"rescued":r,"broken":b,
                     "net":r-b,"precision":r/max(int(c.sum()),1),"rate":float(c.mean())})

features=["p_rte","p_inst","dp_rte","signed_opt_pressure","signed_d_opt_pressure",
          "cf_signed_opt_pressure_gap","cf_signed_d_opt_pressure_gap","cf_opt_total_z20_gap",
          "deceleration_6h","path_consistency","adverse_excursion","opposite_extreme_recency"]
sep=[]
rev=q[q.rescue_target==1]; cont=q[q.rescue_target==0]
for c in features:
    a=rev[c].dropna().to_numpy(float); b=cont[c].dropna().to_numpy(float)
    if len(a)>1 and len(b)>1:
        s=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
        smd=(np.mean(a)-np.mean(b))/s if s>0 else np.nan
    else: smd=np.nan
    sep.append({"feature":c,"rev_median":float(rev[c].median()),"cont_median":float(cont[c].median()),"smd":float(smd)})

out={"grid":rows,"separation":sep,"n":len(q),"reversals":int(q.rescue_target.sum())}
OUT.write_text(json.dumps(out,indent=2,default=str)+"\n")
lines=["# RTE 2025 shock-transition diagnostic","",
       "**Scope:** failed 2025 confirmation reused as development. 2026 remains unopened.","",
       f"- eligible origins: **{len(q)}**",
       f"- V5 missed reversals: **{int(q.rescue_target.sum())}**","",
       "## Tension level × transition shape","",
       "| pRTE | Shape | Cand | Rescue | Broken | Net | Precision | Rate |",
       "|---:|---|---:|---:|---:|---:|---:|---:|"]
for r in rows:
    lines.append(f"| {r['threshold']:.2f} | {r['mode']} | {r['candidate_n']} | {r['rescued']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.2f}% | {100*r['rate']:.2f}% |")
lines += ["","## Largest 2025 reversal-vs-continuation separations","",
          "| Feature | SMD | reversal median | continuation median |",
          "|---|---:|---:|---:|"]
for x in sorted(sep,key=lambda x:abs(x["smd"]) if np.isfinite(x["smd"]) else -1,reverse=True):
    lines.append(f"| {x['feature']} | {x['smd']:+.3f} | {x['rev_median']:.4f} | {x['cont_median']:.4f} |")
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())
