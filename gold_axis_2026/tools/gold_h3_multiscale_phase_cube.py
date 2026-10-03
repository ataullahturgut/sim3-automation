from pathlib import Path
import json, itertools
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
SRC=AX/"GOLD_H3_SECULAR_REJOIN_DIAGNOSTIC_2026-10-04.csv"
OUT=AX/"GOLD_H3_MULTISCALE_PHASE_CUBE_2024_2026_2026-10-04.csv"
OUTJ=AX/"GOLD_H3_MULTISCALE_PHASE_CUBE_2024_2026_2026-10-04.json"
MD=AX/"GOLD_H3_MULTISCALE_PHASE_CUBE_2024_2026_2026-10-04.md"

z=pd.read_csv(SRC)
z["forecast_issue_date"]=pd.to_datetime(z.forecast_issue_date)
z=z[z.oar.astype(bool)].copy()

def sgn(x):
    return np.where(x>0,"+",np.where(x<0,"-","0"))

z["s5"]=sgn(z.signed_ret5)
z["s20"]=sgn(z.signed_ret20)
z["s60"]=sgn(z.signed_ret60)
z["phase"]=z.s5+z.s20+z.s60

rows=[]
for phase,g in z.groupby("phase"):
    r=int(g.rescue_target.sum()); b=len(g)-r
    row={"phase":phase,"n":len(g),"rescued":r,"broken":b,"net":r-b,"precision":r/max(len(g),1)}
    for y in [2024,2025,2026]:
        q=g[g.year==y]
        rr=int(q.rescue_target.sum()); bb=len(q)-rr
        row[f"n_{y}"]=len(q); row[f"net_{y}"]=rr-bb
        row[f"precision_{y}"]=rr/max(len(q),1)
    rows.append(row)
rdf=pd.DataFrame(rows).sort_values(["net","precision","n"],ascending=[False,False,False])
rdf.to_csv(OUT,index=False)

# Mechanistic coarse families using only sign combinations.
families={
    "SHORT_COUNTER_LONG_ALIGN": (z.s5=="-")&(z.s20=="+")&(z.s60=="+"),
    "SHORT_ALIGN_LONG_COUNTER": (z.s5=="+")&(z.s20=="-")&(z.s60=="-"),
    "ALL_COUNTER": (z.s5=="-")&(z.s20=="-")&(z.s60=="-"),
    "ALL_ALIGN": (z.s5=="+")&(z.s20=="+")&(z.s60=="+"),
    "LONG60_COUNTER": z.s60=="-",
    "LONG60_ALIGN": z.s60=="+",
    "SHORT5_COUNTER": z.s5=="-",
    "SHORT5_ALIGN": z.s5=="+",
}
frows=[]
for name,m in families.items():
    g=z[m].copy(); r=int(g.rescue_target.sum()); b=len(g)-r
    row={"family":name,"n":len(g),"rescued":r,"broken":b,"net":r-b,"precision":r/max(len(g),1)}
    for y in [2024,2025,2026]:
        q=g[g.year==y]; rr=int(q.rescue_target.sum()); bb=len(q)-rr
        row[f"n_{y}"]=len(q); row[f"net_{y}"]=rr-bb; row[f"precision_{y}"]=rr/max(len(q),1)
    frows.append(row)

out={"phase_rows":rdf.to_dict("records"),"families":frows}
OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n")

lines=["# MULTI-SCALE 5/20/60-DAY PHASE CUBE — OAR CANDIDATES","",
       "**Evidence class:** post-holdout development. 2026 is diagnostic, not independent validation.","",
       f"- OAR candidates: **{len(z)}**","",
       "## Exact sign phases","",
       "| Phase (5/20/60) | N | Rescue | Broken | Net | Precision | 2024 N/net | 2025 N/net | 2026 N/net |",
       "|---|---:|---:|---:|---:|---:|---|---|---|"]
for r in rdf.itertuples():
    lines.append(
        f"| {r.phase} | {r.n} | {r.rescued} | {r.broken} | {r.net:+d} | {100*r.precision:.1f}% | "
        f"{r.n_2024}/{r.net_2024:+d} | {r.n_2025}/{r.net_2025:+d} | {r.n_2026}/{r.net_2026:+d} |"
    )
lines += ["","## Mechanistic coarse families","",
          "| Family | N | Rescue | Broken | Net | Precision | 2024 N/net | 2025 N/net | 2026 N/net |",
          "|---|---:|---:|---:|---:|---:|---|---|---|"]
for r in frows:
    lines.append(
        f"| {r['family']} | {r['n']} | {r['rescued']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.1f}% | "
        f"{r['n_2024']}/{r['net_2024']:+d} | {r['n_2025']}/{r['net_2025']:+d} | {r['n_2026']}/{r['net_2026']:+d} |"
    )
MD.write_text("\n".join(lines)+"\n")
print(MD.read_text())
