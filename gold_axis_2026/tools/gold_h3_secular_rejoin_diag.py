from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
TOOLS=AX/"tools"
sys.path.insert(0,str(TOOLS))
import gold_h3_iris_v1 as iris

PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
OUT_CSV=AX/"GOLD_H3_SECULAR_REJOIN_DIAGNOSTIC_2026-10-04.csv"
OUT_JSON=AX/"GOLD_H3_SECULAR_REJOIN_DIAGNOSTIC_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_SECULAR_REJOIN_DIAGNOSTIC_2026-10-04.md"

def build_daily(hourly):
    q=hourly.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"]=q.ts.dt.tz_convert(iris.TZ)
    q["local_date"]=q.ts_ny.dt.date
    q["local_hour"]=q.ts_ny.dt.hour
    q["local_minute"]=q.ts_ny.dt.minute
    q["logp"]=np.log(q.value.astype(float))
    a=q[(q.local_hour==16)&(q.local_minute==0)].copy()
    a=a.sort_values("ts").drop_duplicates("local_date",keep="last").reset_index(drop=True)
    a["dret1"]=a.logp.diff()
    for h in [5,20,60]:
        a[f"d_ret_{h}"]=a.logp-a.logp.shift(h)
    a["d_rv_20"]=np.sqrt(a.dret1.pow(2).rolling(20,min_periods=15).sum())
    a["d_rv_60"]=np.sqrt(a.dret1.pow(2).rolling(60,min_periods=45).sum())
    a["trend_strength_20"]=a.d_ret_20.abs()/(a.d_rv_20+1e-8)
    a["trend_strength_60"]=a.d_ret_60.abs()/(a.d_rv_60+1e-8)
    return a[["local_date","ts","value","d_ret_5","d_ret_20","d_ret_60","d_rv_20","d_rv_60","trend_strength_20","trend_strength_60"]].dropna()

def metric(g):
    n=len(g); r=int(g.rescue_target.sum()); b=n-r
    return {"n":n,"rescued":r,"broken":b,"net":r-b,"precision":r/max(n,1)}

def main():
    hist=iris.load_neon_hourly()
    succ,api_calls=iris.fetch_extension()
    _,bridge=iris.bridge_metrics(hist,succ)
    if not bridge["pass"]:
        raise RuntimeError(f"SOURCE_BRIDGE_FAIL {bridge}")
    ext=succ[succ.ts>=pd.Timestamp("2025-01-01",tz="UTC")].copy()
    hourly=pd.concat([hist,ext],ignore_index=True).sort_values("ts").drop_duplicates("ts",keep="first").reset_index(drop=True)
    daily=build_daily(hourly)

    p=pd.read_csv(PRED); f=pd.read_csv(FEAT)
    for d in [p,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    z=p.merge(f[["feature_cutoff_date","signed_opt_pressure","signed_d_opt_pressure"]],
              on="feature_cutoff_date",how="left",validate="one_to_one")
    z["feature_date"]=z.feature_cutoff_date.dt.date
    z=z.merge(daily,left_on="feature_date",right_on="local_date",how="inner",validate="many_to_one")
    z=z[z.year.isin([2024,2025,2026])].copy()
    z["oar"]=(z.p_rte>=.60)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
    q=z[z.oar].copy()
    sign=np.where(q.momentum_up.astype(int)==1,1.0,-1.0)
    q["signed_ret5"]=sign*q.d_ret_5
    q["signed_ret20"]=sign*q.d_ret_20
    q["signed_ret60"]=sign*q.d_ret_60
    q["secular_state"]=np.select(
        [
            (q.signed_ret20<0)&(q.signed_ret60<0),
            (q.signed_ret20>0)&(q.signed_ret60>0),
        ],
        ["REJOIN_BOTH","ALIGN_BOTH"],
        default="MIXED"
    )
    q.to_csv(OUT_CSV,index=False)

    rows=[]
    for y in [2024,2025,2026]:
        gy=q[q.year==y]
        for state in ["REJOIN_BOTH","MIXED","ALIGN_BOTH"]:
            g=gy[gy.secular_state==state]
            rows.append({"year":y,"state":state,**metric(g),
                         "median_signed20":float(g.signed_ret20.median()) if len(g) else np.nan,
                         "median_signed60":float(g.signed_ret60.median()) if len(g) else np.nan})
        rows.append({"year":y,"state":"ALL_OAR",**metric(gy),
                     "median_signed20":float(gy.signed_ret20.median()) if len(gy) else np.nan,
                     "median_signed60":float(gy.signed_ret60.median()) if len(gy) else np.nan})

    # Candidate success split by simple secular sign rules.
    rules={
        "REJOIN20":q.signed_ret20<0,
        "REJOIN60":q.signed_ret60<0,
        "REJOIN_EITHER":(q.signed_ret20<0)|(q.signed_ret60<0),
        "REJOIN_BOTH":(q.signed_ret20<0)&(q.signed_ret60<0),
        "ALIGN_BOTH":(q.signed_ret20>0)&(q.signed_ret60>0),
    }
    rule_rows=[]
    for name,m in rules.items():
        g=q[m].copy()
        rule_rows.append({"rule":name,**metric(g)})
        for y in [2024,2025,2026]:
            gy=g[g.year==y]
            rule_rows.append({"rule":f"{name}_{y}",**metric(gy)})

    out={"bridge":bridge,"api_calls":api_calls,"year_state":rows,"rules":rule_rows}
    OUT_JSON.write_text(json.dumps(out,indent=2,default=str)+"\n")

    lines=["# SECULAR REJOIN DIAGNOSTIC — OAR CANDIDATES","",
           "**Evidence class:** post-holdout development. 2026 is diagnostic, not independent validation.","",
           f"- hourly source bridge pass: **{bridge['pass']}**",
           f"- OAR candidates 2024-2026: **{len(q)}**","",
           "## OAR performance by secular state","",
           "| Year | State | N | Rescue | Broken | Net | Precision | median signed20 | median signed60 |",
           "|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['year']} | {r['state']} | {r['n']} | {r['rescued']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.2f}% | {r['median_signed20']:+.4f} | {r['median_signed60']:+.4f} |")
    lines += ["","## Structural sign-rule audit","",
              "| Rule | N | Rescue | Broken | Net | Precision |",
              "|---|---:|---:|---:|---:|---:|"]
    for r in rule_rows:
        lines.append(f"| {r['rule']} | {r['n']} | {r['rescued']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.2f}% |")
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
