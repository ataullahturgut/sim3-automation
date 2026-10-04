from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

RTE=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
LLRS=AX/"GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"

OUT=AX/"GOLD_H3_OLC_V1_PREDICTIONS_2026-10-04.csv"
OUTB=AX/"GOLD_H3_OLC_V1_BLOCK_METRICS_2026-10-04.csv"
OUTJ=AX/"GOLD_H3_OLC_V1_SUMMARY_2026-10-04.json"
OUTM=AX/"GOLD_H3_OLC_V1_RESULT_2026-10-04.md"

def b(s):
    if s.dtype==bool:return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def block(d):
    d=pd.Timestamp(d); return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def metrics(g):
    c=g.olc.astype(bool); y=g.rescue_target.astype(int)==1
    r=int((c&y).sum()); br=int((c&(~y)).sum())
    return dict(n=len(g),candidate_n=int(c.sum()),candidate_rate=float(c.mean()),
                rescued=r,broken=br,net=r-br,precision=r/max(int(c.sum()),1),
                v5_accuracy=float(g.v5_correct.mean()),
                assisted_accuracy=float(g.assisted_correct.mean()))

r=pd.read_csv(RTE); f=pd.read_csv(FEAT); l=pd.read_csv(LLRS); s=pd.read_csv(SAGE)
for d in [r,f,l,s]:
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","hourly_cutoff","hourly_source_ts"]:
        if c in d.columns: d[c]=pd.to_datetime(d[c],errors="coerce",utc=("hourly_" in c))

z=r[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","p_inst","p_rte"]].merge(
    f[["feature_cutoff_date","y_up","momentum_up","v5_pred","rescue_target","eligible_v5_continuation",
       "signed_opt_pressure","signed_d_opt_pressure"]],
    on="feature_cutoff_date",how="inner",validate="one_to_one"
)
z=z.merge(
    l[["feature_cutoff_date","llrs_pressure","llrs_incremental","llrs_external_opposes","hourly_cutoff","hourly_source_ts"]],
    on="feature_cutoff_date",how="inner",validate="one_to_one"
)
z["eligible_v5_continuation"]=b(z.eligible_v5_continuation)
z["llrs_external_opposes"]=b(z.llrs_external_opposes)

sm=s[["feature_cutoff_date","action"]].copy()
sm["ocs_covered"]=True; sm["ocs"]=sm.action.astype(str).eq("FLIP")
z=z.merge(sm[["feature_cutoff_date","ocs_covered","ocs"]],on="feature_cutoff_date",how="left",validate="one_to_one")
z["ocs_covered"]=z.ocs_covered.fillna(False); z["ocs"]=z.ocs.fillna(False)

leak=int((z.hourly_source_ts>z.hourly_cutoff).fillna(False).sum())
identity=int((z.rescue_target.astype(int)!=((z.v5_pred.astype(int)!=z.y_up.astype(int)).astype(int))).sum())
if leak or identity: raise RuntimeError(f"integrity fail leak={leak} identity={identity}")

z=z[z.eligible_v5_continuation].copy()
z["oar"]=(z.p_rte>=.60)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
z["llrs"]=(z.llrs_external_opposes)&(z.llrs_incremental>0)&(z.llrs_pressure>=.10)
z["olc"]=z.oar&z.llrs
z["v5_correct"]=z.v5_pred.astype(int)==z.y_up.astype(int)
z["assisted_pred"]=np.where(z.olc,1-z.v5_pred.astype(int),z.v5_pred.astype(int))
z["assisted_correct"]=z.assisted_pred.astype(int)==z.y_up.astype(int)
z["block"]=z.forecast_issue_date.map(block)
z.to_csv(OUT,index=False)

agg=metrics(z)
blocks=[]
for k,g in z.groupby("block",sort=False):
    x=metrics(g);x["block"]=k;blocks.append(x)
bdf=pd.DataFrame(blocks); bdf.to_csv(OUTB,index=False)

common=z[z.ocs_covered].copy()
olc=common.olc.astype(bool); ocs=common.ocs.astype(bool); y=common.rescue_target.astype(int)==1
def rb(mask):
    rr=int((mask&y).sum()); bb=int((mask&(~y)).sum())
    return {"n":int(mask.sum()),"rescued":rr,"broken":bb,"net":rr-bb,"precision":rr/max(int(mask.sum()),1)}
comp={"olc_only":rb(olc&~ocs),"ocs_only":rb(ocs&~olc),"overlap":rb(ocs&olc),"union":rb(ocs|olc)}
inc=comp["olc_only"]["rescued"]

positive=sum(1 for x in blocks if x["net"]>0)
worst=min(x["net"] for x in blocks)
gate=bool(agg["candidate_n"]>=6 and agg["precision"]>=.60 and agg["net"]>=3 and
          agg["candidate_rate"]<=.15 and worst>=-1 and positive>=2 and inc>=2 and leak==0 and identity==0)
status="OLC_H3_V1_PROMISING" if gate else "OLC_H3_V1_FAIL"

summary={"schema":"OLC_H3_V1","status":status,"integrity_failures":leak+identity,
         "first":str(z.feature_cutoff_date.min().date()),"last":str(z.feature_cutoff_date.max().date()),
         "aggregate":agg,"blocks":blocks,"complementarity":comp,"incremental_true_olc_only":inc}
OUTJ.write_text(json.dumps(summary,indent=2,default=str)+"\n")

lines=["# OLC-H3 V1 — OPTIONS / LEAD-LAG CONCURRENCE RESULT","",
       f"**Status:** **{status}**  ",f"- coverage: **{summary['first']} .. {summary['last']}**",
       f"- integrity failures: **{leak+identity}**","",
       "## Aggregate","",
       f"- candidates: **{agg['candidate_n']} ({100*agg['candidate_rate']:.2f}%)**",
       f"- rescue / broken / net: **{agg['rescued']} / {agg['broken']} / {agg['net']:+d}**",
       f"- precision: **{100*agg['precision']:.2f}%**",
       f"- V5 -> assisted: **{100*agg['v5_accuracy']:.2f}% -> {100*agg['assisted_accuracy']:.2f}%**","",
       "## Blocks","",
       "| Block | N | Cand | Rescue | Broken | Net | Precision |",
       "|---|---:|---:|---:|---:|---:|---:|"]
for x in blocks:
    lines.append(f"| {x['block']} | {x['n']} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net']:+d} | {100*x['precision']:.1f}% |")
lines += ["","## Complementarity vs OCS",""]
for k,v in comp.items():
    lines.append(f"- {k}: **{v['n']}**, rescue/broken/net **{v['rescued']}/{v['broken']}/{v['net']:+d}**, precision **{100*v['precision']:.1f}%**")
lines += [f"- incremental true OLC-only rescues: **{inc}**"]
OUTM.write_text("\n".join(lines)+"\n")
print(OUTM.read_text())
