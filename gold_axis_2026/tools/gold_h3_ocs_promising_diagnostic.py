from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
IFBC=AX/"GOLD_H3_IFBC_V1_SCORES_2026-10-04.csv"
LLRS=AX/"GOLD_H3_LLRS_V1_ORIGIN_SCORES_2026-10-04.csv"
OUT=AX/"GOLD_H3_OCS_V1_PROMISING_070_010_DIAGNOSTIC_2026-10-04.md"
CSV=AX/"GOLD_H3_OCS_V1_PROMISING_070_010_EVENTS_2026-10-04.csv"

a=pd.read_csv(IFBC); b=pd.read_csv(LLRS)
for d in [a,b]:
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        if c in d.columns: d[c]=pd.to_datetime(d[c])
keep=["feature_cutoff_date","llrs_pressure","llrs_incremental","llrs_external_opposes","pred_ext_6h","pred_gc_6h"]
z=a.merge(b[keep],on="feature_cutoff_date",how="inner",validate="one_to_one")
z["llrs_external_opposes"]=z.llrs_external_opposes.astype(str).str.lower().isin(["true","1","yes"])
z["block"]=z.forecast_issue_date.apply(lambda t:f"{t.year}_{'H1' if t.month<=6 else 'H2'}")
cand=(z.ifbc_count60>=4)&(z.ifbc_score>=.70)&z.llrs_external_opposes&(z.llrs_incremental>0)&(z.llrs_pressure>=.10)
q=z[cand].copy()
q["effect"]=np.where(q.rescue_target==1,"RESCUE","BROKEN")
q["opal_candidate"]=q.opal_override_check.astype(str).str.lower().isin(["true","1","yes"])
q["abs_h3"]=q.target_r3.abs()
q.to_csv(CSV,index=False)

miss=q[(q.rescue_target==1)&(~q.opal_candidate)]
lines=["# OCS V1 — PROMISING 0.70 / 0.10 CONFIGURATION DIAGNOSTIC","",
       "**Status:** post-V1 development diagnostic only. This does not retroactively pass V1.","",
       f"- candidates: **{len(q)}**",
       f"- rescue / broken / net: **{int((q.effect=='RESCUE').sum())} / {int((q.effect=='BROKEN').sum())} / {int((q.rescue_target*2-1).sum()):+d}**",
       f"- precision: **{100*q.rescue_target.mean():.2f}%**",
       f"- OPAL-no-candidate rescues: **{len(miss)}**","",
       "## Events","",
       "| Issue | Target end | Block | H3 return | IFBC | LLRS | Incr | OPAL cand | Effect |",
       "|---|---|---|---:|---:|---:|---:|---|---|"]
for r in q.itertuples():
    lines.append(
        f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | {r.block} | "
        f"{100*r.target_r3:+.2f}% | {r.ifbc_score:.3f} | {r.llrs_pressure:.3f} | {r.llrs_incremental:.3f} | "
        f"{r.opal_candidate} | {r.effect} |"
    )
lines += ["","## Magnitude","",
          f"- rescue median |H3|: **{100*q.loc[q.rescue_target==1,'abs_h3'].median():.2f}%**",
          f"- broken |H3|: **{100*q.loc[q.rescue_target==0,'abs_h3'].median():.2f}%**",
          f"- rescue with |H3| >=1%: **{int(((q.rescue_target==1)&(q.abs_h3>=.01)).sum())}/{int((q.rescue_target==1).sum())}**"]
OUT.write_text("\n".join(lines)+"\n")
print(OUT.read_text())
