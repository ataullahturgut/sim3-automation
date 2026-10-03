from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

OUT=Path(os.environ.get("OUT_DIR","gold_h3_neon_cross_source_out"))
OUT.mkdir(parents=True,exist_ok=True)
DSN=os.environ["NEON_DATABASE_URL"]

SERIES=[
 "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
 "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
 "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
 "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
 "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1",
 "XAU_EOD_TWELVE_NY17",
 "XAU_DAILY_XAUS",
]

def robust_z(x):
    a=pd.to_numeric(x,errors="coerce").astype(float)
    med=float(np.nanmedian(a))
    mad=float(np.nanmedian(np.abs(a-med)))
    s=1.4826*mad
    if not np.isfinite(s) or s<=0:
        s=float(np.nanstd(a,ddof=0))
    return (a-med)/(s if s>0 else 1.0),med,s

def main():
    with psycopg.connect(DSN,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
              WITH base AS (
                SELECT series_id,observation_ts,value,retrieved_at
                FROM observations
                WHERE series_id = ANY(%s)
              ),
              stats AS (
                SELECT series_id,observation_ts,
                       COUNT(*) AS revision_n,
                       COUNT(DISTINCT value) AS distinct_value_n
                FROM base
                GROUP BY series_id,observation_ts
              ),
              latest AS (
                SELECT series_id,observation_ts,value,retrieved_at,
                       ROW_NUMBER() OVER(PARTITION BY series_id,observation_ts ORDER BY retrieved_at DESC) rn
                FROM base
              )
              SELECT l.series_id,l.observation_ts,l.value,l.retrieved_at,
                     s.revision_n,s.distinct_value_n
              FROM latest l
              JOIN stats s USING(series_id,observation_ts)
              WHERE l.rn=1
              ORDER BY l.series_id,l.observation_ts
            """,(SERIES,))
            rows=cur.fetchall(); cols=[d.name for d in cur.description]
        conn.rollback()

    d=pd.DataFrame(rows,columns=cols)
    d["observation_ts"]=pd.to_datetime(d.observation_ts,utc=True)
    d["date"]=d.observation_ts.dt.date
    d["value"]=pd.to_numeric(d.value,errors="coerce")
    d.to_csv(OUT/"selected_series_latest.csv",index=False)

    # Exact Feb/Mar focus.
    focus=d[(d.date>=pd.Timestamp("2026-02-24").date())&(d.date<=pd.Timestamp("2026-03-04").date())].copy()
    focus.to_csv(OUT/"focus_2026_02_24_03_04.csv",index=False)

    # XAU cross-source level consistency by UTC date.
    x=d[d.series_id.str.startswith("XAU_")].copy()
    piv=x.pivot_table(index="date",columns="series_id",values="value",aggfunc="last").sort_index()

    a="XAU_STAKTRAKR_RESEARCH_DAILY_R1"
    b="XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
    pair=piv[[a,b]].dropna().copy()
    pair["log_ratio"]=np.log(pair[a]/pair[b])
    z,med,scale=robust_z(pair.log_ratio)
    pair["ratio_robust_z"]=z
    pair["ratio_dev_from_median"]=pair.log_ratio-med
    pair["abs_pct_dev_approx"]=np.abs(np.expm1(pair.ratio_dev_from_median))
    pair.to_csv(OUT/"xau_stak_vs_ny17_all.csv")

    severe=pair[(pair.abs_pct_dev_approx>=0.05)|(pair.ratio_robust_z.abs()>=8)].copy()
    severe=severe.sort_values(["abs_pct_dev_approx"],ascending=False)
    severe.to_csv(OUT/"xau_stak_vs_ny17_flags.csv")

    # Four-metal return anomaly coincidence.
    metal_map={
      "XAU_STAKTRAKR_RESEARCH_DAILY_R1":"gold",
      "XAG_STAKTRAKR_RESEARCH_DAILY_R1":"silver",
      "XPT_STAKTRAKR_RESEARCH_DAILY_R1":"platinum",
      "XPD_STAKTRAKR_RESEARCH_DAILY_R1":"palladium",
    }
    m=d[d.series_id.isin(metal_map)].copy()
    mp=m.pivot_table(index="date",columns="series_id",values="value",aggfunc="last").sort_index()
    out=pd.DataFrame(index=mp.index)
    for sid,name in metal_map.items():
        lr=np.log(mp[sid]/mp[sid].shift(1))
        z,rm,rs=robust_z(lr)
        out[f"{name}_value"]=mp[sid]
        out[f"{name}_logret"]=lr
        out[f"{name}_robust_z"]=z
    zcols=[c for c in out if c.endswith("_robust_z")]
    out["extreme8_n"]=(out[zcols].abs()>=8).sum(axis=1)
    out["extreme6_n"]=(out[zcols].abs()>=6).sum(axis=1)
    out["max_abs_z"]=out[zcols].abs().max(axis=1)
    out.to_csv(OUT/"four_metal_return_audit.csv")
    multi=out[(out.extreme8_n>=2)|(out.extreme6_n>=3)].copy().sort_values(["extreme8_n","max_abs_z"],ascending=False)
    multi.to_csv(OUT/"four_metal_multi_extreme_flags.csv")

    # XAUS revision conflicts.
    xa=d[d.series_id=="XAU_DAILY_XAUS"].copy()
    xaconf=xa[xa.distinct_value_n.astype(int)>1].copy()
    xaconf.to_csv(OUT/"xau_daily_xaus_conflict_timestamps.csv",index=False)

    # Pairwise source overlap diagnostics.
    pairs=[]
    xau_cols=[c for c in piv.columns if str(c).startswith("XAU_")]
    for i in range(len(xau_cols)):
        for j in range(i+1,len(xau_cols)):
            c1,c2=xau_cols[i],xau_cols[j]
            q=piv[[c1,c2]].dropna()
            if len(q)<5: continue
            lr=np.log(q[c1]/q[c2])
            zz,mm,ss=robust_z(lr)
            dev=np.abs(np.expm1(lr-mm))
            pairs.append({
              "series_a":c1,"series_b":c2,"n":int(len(q)),
              "median_level_ratio":float(np.exp(mm)),
              "robust_scale_logratio":float(ss),
              "max_abs_pct_dev_from_median":float(dev.max()),
              "n_dev_gt_3pct":int((dev>=.03).sum()),
              "n_dev_gt_5pct":int((dev>=.05).sum()),
              "n_robust_z_gt8":int((zz.abs()>=8).sum()),
            })
    pdf=pd.DataFrame(pairs).sort_values(["n_dev_gt_5pct","max_abs_pct_dev_from_median"],ascending=False)
    pdf.to_csv(OUT/"xau_pairwise_source_diagnostics.csv",index=False)

    summary={
      "schema":"GOLD_H3_NEON_CROSS_SOURCE_AUDIT_V1",
      "read_only":True,
      "focus_rows":int(len(focus)),
      "stak_vs_ny17_overlap_n":int(len(pair)),
      "stak_vs_ny17_median_ratio":float(np.exp(med)),
      "stak_vs_ny17_robust_scale_logratio":float(scale),
      "stak_vs_ny17_severe_flags_n":int(len(severe)),
      "multi_metal_extreme_flags_n":int(len(multi)),
      "xau_daily_xaus_distinct_value_conflict_timestamps":int(len(xaconf)),
      "focus":focus.assign(observation_ts=focus.observation_ts.astype(str),date=focus.date.astype(str)).to_dict(orient="records"),
      "top_stak_vs_ny17_flags":severe.head(30).reset_index().assign(date=lambda z:z.date.astype(str)).to_dict(orient="records"),
      "top_multi_metal_flags":multi.head(30).reset_index().assign(date=lambda z:z.date.astype(str)).to_dict(orient="records"),
    }
    (OUT/"cross_source_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 NEON CROSS-SOURCE AUDIT — 2026-10-03","",
      "**Mode:** READ ONLY.","",
      "## 2026-02-24 .. 2026-03-04 exact database values","",
      "| Series | Date | Value | Revisions | Distinct values |",
      "|---|---|---:|---:|---:|"
    ]
    for r in focus.sort_values(["date","series_id"]).itertuples():
        lines.append(f"| {r.series_id} | {r.date} | {r.value:.6f} | {int(r.revision_n)} | {int(r.distinct_value_n)} |")
    lines += ["","## StakTrakr XAU vs independent NY17 hourly-derived XAU","",
      f"- overlap: **{len(pair)}** dates",
      f"- median level ratio Stak/NY17: **{np.exp(med):.6f}**",
      f"- severe flags (>=5% deviation from normal ratio OR robust |z|>=8): **{len(severe)}**","",
      "| Date | Stak | NY17-derived | Approx dev from normal ratio | Robust z |",
      "|---|---:|---:|---:|---:|"]
    for r in severe.head(40).reset_index().itertuples():
        lines.append(f"| {r.date} | {getattr(r,a):.4f} | {getattr(r,b):.4f} | {100*r.abs_pct_dev_approx:.2f}% | {r.ratio_robust_z:.2f} |")
    lines += ["","## Multi-metal coincident extremes","",
      f"- flagged dates: **{len(multi)}**","",
      "| Date | >=8z assets | >=6z assets | Max | Gold r | Silver r | Platinum r | Palladium r |",
      "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in multi.head(40).reset_index().itertuples():
        lines.append(f"| {r.date} | {int(r.extreme8_n)} | {int(r.extreme6_n)} | {r.max_abs_z:.1f} | {100*r.gold_logret:+.2f}% | {100*r.silver_logret:+.2f}% | {100*r.platinum_logret:+.2f}% | {100*r.palladium_logret:+.2f}% |")
    lines += ["","## XAUS daily revisions","",
      f"- latest-dedup timestamps with conflicting stored values: **{len(xaconf)}**",
      "",
      "Flags are candidates only. A large true market move can be a statistical outlier; correction requires independent source confirmation."
    ]
    (OUT/"NEON_CROSS_SOURCE_AUDIT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"NEON_CROSS_SOURCE_AUDIT.md").read_text())

if __name__=="__main__": main()
