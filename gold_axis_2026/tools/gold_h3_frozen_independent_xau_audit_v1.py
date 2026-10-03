from __future__ import annotations
import json, os, math
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_frozen_independent_xau_audit_out"))
OUT.mkdir(parents=True,exist_ok=True)
DSN=os.environ["NEON_DATABASE_URL"]
FROZEN=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"
PATCH_DATE=pd.Timestamp("2026-02-27")
PATCH_GOLD=5183.80

def main():
    f=pd.read_csv(FROZEN)
    f["date"]=pd.to_datetime(f.date).dt.normalize()
    f["gold_original"]=pd.to_numeric(f.gold,errors="coerce")
    f["gold_clean"]=f.gold_original
    f.loc[f.date==PATCH_DATE,"gold_clean"]=PATCH_GOLD

    with psycopg.connect(DSN,autocommit=False) as conn:
      with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
        cur.execute("""
          SELECT observation_ts,value,retrieved_at
          FROM observations
          WHERE series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1'
          ORDER BY observation_ts,retrieved_at
        """)
        rows=cur.fetchall()
      conn.rollback()
    x=pd.DataFrame(rows,columns=["ts","ny17","retrieved_at"])
    x["ts"]=pd.to_datetime(x.ts,utc=True)
    x["date"]=x.ts.dt.tz_localize(None).dt.normalize()
    x["retrieved_at"]=pd.to_datetime(x.retrieved_at,utc=True)
    x["ny17"]=pd.to_numeric(x.ny17,errors="coerce")
    x=x.sort_values("retrieved_at").drop_duplicates("date",keep="last").sort_values("date")

    g=f[["date","gold_original","gold_clean"]].merge(x[["date","ny17"]],on="date",how="left")
    q=g.dropna(subset=["ny17"]).copy()
    for c in ["original","clean"]:
        q[f"log_ratio_{c}"]=np.log(q[f"gold_{c}"]/q.ny17)
        med=float(q[f"log_ratio_{c}"].median())
        q[f"dev_{c}"]=np.abs(np.expm1(q[f"log_ratio_{c}"]-med))
    q.to_csv(OUT/"frozen_vs_ny17_levels.csv",index=False)

    # H3 targets on exactly the frozen retained-date clock.
    g["target_date_h3"]=g.date.shift(-3)
    g["frozen_clean_r3"]=np.log(g.gold_clean.shift(-3)/g.gold_clean)
    g["frozen_original_r3"]=np.log(g.gold_original.shift(-3)/g.gold_original)
    ny=dict(zip(x.date,x.ny17))
    g["ny17_start"]=g.date.map(ny)
    g["ny17_end"]=g.target_date_h3.map(ny)
    g["ny17_r3"]=np.log(g.ny17_end/g.ny17_start)
    t=g.dropna(subset=["frozen_clean_r3","ny17_r3"]).copy()
    t["frozen_dir"]=(t.frozen_clean_r3>0).astype(int)
    t["ny17_dir"]=(t.ny17_r3>0).astype(int)
    t["dir_disagree"]=t.frozen_dir!=t.ny17_dir
    t["year"]=t.date.dt.year
    t["abs_frozen_move"]=t.frozen_clean_r3.abs()
    t["abs_ny17_move"]=t.ny17_r3.abs()
    t["max_abs_move"]=t[["abs_frozen_move","abs_ny17_move"]].max(axis=1)
    t.to_csv(OUT/"h3_target_source_comparison.csv",index=False)

    dis=t[t.dir_disagree].copy().sort_values("date")
    dis.to_csv(OUT/"h3_target_direction_disagreements.csv",index=False)

    years=[]
    for y,z in t.groupby("year"):
      if y<2022: continue
      d=z[z.dir_disagree]
      years.append({
        "year":int(y),"n":int(len(z)),"direction_disagree_n":int(len(d)),
        "direction_disagree_pct":100*len(d)/len(z),
        "disagree_both_moves_ge_0_5pct":int(((d.abs_frozen_move>=.005)&(d.abs_ny17_move>=.005)).sum()),
        "disagree_both_moves_ge_1pct":int(((d.abs_frozen_move>=.01)&(d.abs_ny17_move>=.01)).sum()),
      })
    yd=pd.DataFrame(years); yd.to_csv(OUT/"h3_target_source_yearly.csv",index=False)

    z26=t[t.year==2026].copy()
    d26=z26[z26.dir_disagree].copy()
    summary={
      "schema":"GOLD_H3_FROZEN_INDEPENDENT_XAU_AUDIT_V1",
      "level_overlap_n":int(len(q)),
      "clean_level_dev_ge_1pct":int((q.dev_clean>=.01).sum()),
      "clean_level_dev_ge_2pct":int((q.dev_clean>=.02).sum()),
      "clean_level_dev_ge_3pct":int((q.dev_clean>=.03).sum()),
      "clean_level_dev_ge_5pct":int((q.dev_clean>=.05).sum()),
      "clean_max_dev_pct":float(100*q.dev_clean.max()),
      "clean_max_dev_date":str(q.loc[q.dev_clean.idxmax(),"date"].date()),
      "h3_target_overlap_n":int(len(t)),
      "h3_direction_disagree_n":int(t.dir_disagree.sum()),
      "h3_direction_disagree_pct":float(100*t.dir_disagree.mean()),
      "2026_n":int(len(z26)),
      "2026_direction_disagree_n":int(len(d26)),
      "2026_direction_disagree_pct":float(100*len(d26)/len(z26)) if len(z26) else None,
      "2026_disagree_both_moves_ge_0_5pct":int(((d26.abs_frozen_move>=.005)&(d26.abs_ny17_move>=.005)).sum()),
      "2026_disagree_both_moves_ge_1pct":int(((d26.abs_frozen_move>=.01)&(d26.abs_ny17_move>=.01)).sum()),
      "yearly":yd.to_dict(orient="records"),
    }
    (OUT/"frozen_independent_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 FROZEN vs INDEPENDENT XAU AUDIT — 2026-10-03","",
      "Independent comparator: Neon `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`. "
      "The clean frozen series uses only the already-confirmed 2026-02-27 patch; no other values are changed.","",
      "## Level consistency","",
      f"- overlap: **{len(q)}** dates",
      f"- deviation from normal source ratio >=1%: **{int((q.dev_clean>=.01).sum())}**",
      f"- >=2%: **{int((q.dev_clean>=.02).sum())}**",
      f"- >=3%: **{int((q.dev_clean>=.03).sum())}**",
      f"- >=5%: **{int((q.dev_clean>=.05).sum())}**",
      f"- max clean deviation: **{100*q.dev_clean.max():.2f}%** on **{q.loc[q.dev_clean.idxmax(),'date'].date()}**","",
      "## H3 target-direction source sensitivity","",
      f"- comparable H3 origins: **{len(t)}**",
      f"- direction disagreements: **{int(t.dir_disagree.sum())} ({100*t.dir_disagree.mean():.2f}%)**",
      f"- 2026 comparable origins: **{len(z26)}**",
      f"- 2026 direction disagreements: **{len(d26)} ({100*len(d26)/len(z26):.2f}%)**",
      f"- 2026 disagreements where BOTH sources imply >=0.5% absolute H3 move: **{int(((d26.abs_frozen_move>=.005)&(d26.abs_ny17_move>=.005)).sum())}**",
      f"- 2026 disagreements where BOTH imply >=1.0% absolute H3 move: **{int(((d26.abs_frozen_move>=.01)&(d26.abs_ny17_move>=.01)).sum())}**","",
      "## Yearly","",
      "| Year | N | Direction disagreements | % | Both >=0.5% | Both >=1% |",
      "|---:|---:|---:|---:|---:|---:|"]
    for r in yd.itertuples():
      lines.append(f"| {r.year} | {r.n} | {r.direction_disagree_n} | {r.direction_disagree_pct:.2f}% | {r.disagree_both_moves_ge_0_5pct} | {r.disagree_both_moves_ge_1pct} |")
    lines += ["","## 2026 disagreement events","",
      "| Start | H3 end | Frozen r3 | NY17 r3 | Frozen dir | NY17 dir |",
      "|---|---|---:|---:|---|---|"]
    for r in d26.itertuples():
      lines.append(f"| {r.date.date()} | {r.target_date_h3.date()} | {100*r.frozen_clean_r3:+.3f}% | {100*r.ny17_r3:+.3f}% | {'UP' if r.frozen_dir else 'DOWN'} | {'UP' if r.ny17_dir else 'DOWN'} |")
    lines += ["","## Interpretation","",
      "Source-time differences can legitimately flip labels when the three-session move is close to zero. "
      "Disagreements where both sources show large opposite moves are materially more suspicious and require event-level verification before any model rerun."
    ]
    (OUT/"FROZEN_INDEPENDENT_XAU_AUDIT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"FROZEN_INDEPENDENT_XAU_AUDIT.md").read_text())

if __name__=="__main__": main()
