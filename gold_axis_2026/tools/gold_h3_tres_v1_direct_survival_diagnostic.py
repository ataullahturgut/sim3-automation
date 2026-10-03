from pathlib import Path
import json, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
S1=AX/"GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv"
S2=AX/"GOLD_H3_TRES_V1_STAGE2_PREDICTIONS_2026-10-04.csv"

OUT=AX/"GOLD_H3_TRES_V1_STAGE2_DIRECT_SURVIVAL_DIAGNOSTIC_2026-10-04.md"
OUTJ=AX/"GOLD_H3_TRES_V1_STAGE2_DIRECT_SURVIVAL_DIAGNOSTIC_2026-10-04.json"

s=pd.read_csv(S1)
s["forecast_issue_date"]=pd.to_datetime(s.forecast_issue_date)
q=s[s.eligible_v5_continuation.astype(bool)].copy()
q["cause_share"]=q.F_reversal/(q.F_reversal+q.F_continuation).replace(0,np.nan)
q["cause_dominance"]=q.F_reversal-q.F_continuation
q["block"]=q.forecast_issue_date.map(lambda d:f"{d.year}_{'H1' if d.month<=6 else 'H2'}")

# identity check: in eligible universe V5 wrong must equal terminal reversal.
identity_mismatch=int((q.rescue_target.astype(int)!=q.terminal_reversal.astype(int)).sum())

def auc(g,c):
    y=g.rescue_target.astype(int)
    if y.nunique()<2:return np.nan
    return float(roc_auc_score(y,g[c]))

def tb(g,c):
    lo=g[c].quantile(.20); hi=g[c].quantile(.80)
    a=g[g[c]<=lo]; b=g[g[c]>=hi]
    return {
        "low_rate":float(a.rescue_target.mean()),"high_rate":float(b.rescue_target.mean()),
        "sep":float(b.rescue_target.mean()-a.rescue_target.mean()),
        "low_n":len(a),"high_n":len(b)
    }

scores=["F_reversal","cause_share","cause_dominance"]
rows=[]
for c in scores:
    a=auc(q,c); t=tb(q,c)
    br=[]
    for b,g in q.groupby("block",sort=False):
        x=tb(g,c)
        br.append({"block":b,"auc":auc(g,c),**x})
    rows.append({"score":c,"auc":a,**t,"blocks":br})

# compare Stage2 output on its narrower scored universe
s2=pd.read_csv(S2)
meta={
    "n":len(s2),
    "p_error_aug_auc":float(roc_auc_score(s2.rescue_target,s2.p_error_aug)),
    "F_reversal_auc_same_universe":float(roc_auc_score(s2.rescue_target,s2.F_reversal))
}

OUTJ.write_text(json.dumps({"eligible_n":len(q),"identity_mismatch":identity_mismatch,"scores":rows,"stage2_same_universe":meta},indent=2)+"\n")
lines=["# TRES Stage2 — DIRECT SURVIVAL SCORE DIAGNOSTIC","",
       "**Status:** diagnostic after the preregistered Stage-2 meta-model failed. No intervention threshold is selected here.","",
       f"- V5-continuation eligible origins: **{len(q)}**",
       f"- identity mismatches (V5 wrong != terminal reversal): **{identity_mismatch}**","",
       "## Direct scores","",
       "| Score | AUC | Bottom quintile error | Top quintile error | Separation |",
       "|---|---:|---:|---:|---:|"]
for r in rows:
    lines.append(f"| {r['score']} | {r['auc']:.4f} | {100*r['low_rate']:.2f}% | {100*r['high_rate']:.2f}% | {100*r['sep']:+.2f}pp |")
lines += ["","## Half-year stability","",
          "| Score | Block | AUC | Bottom error | Top error | Separation |",
          "|---|---|---:|---:|---:|---:|"]
for r in rows:
    for x in r["blocks"]:
        lines.append(f"| {r['score']} | {x['block']} | {x['auc']:.3f} | {100*x['low_rate']:.1f}% | {100*x['high_rate']:.1f}% | {100*x['sep']:+.1f}pp |")
lines += ["","## Same Stage-2 scored universe","",
          f"- p_error_aug AUC: **{meta['p_error_aug_auc']:.4f}**",
          f"- direct F_reversal AUC: **{meta['F_reversal_auc_same_universe']:.4f}**"]
OUT.write_text("\n".join(lines)+"\n")
print(OUT.read_text())
