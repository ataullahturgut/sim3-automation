from __future__ import annotations
import json, os, urllib.request
from pathlib import Path
import numpy as np, pandas as pd, psycopg

OUT=Path(os.environ.get("OUT_DIR","gold_h3_stak_upstream_audit_out")); OUT.mkdir(parents=True,exist_ok=True)
DSN=os.environ["NEON_DATABASE_URL"]
REF="54fdf1c8d39b7b6c7b874d0f30f784296e886044"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"h3-integrity-audit/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r: return r.read()

def robust_z(a):
    x=np.asarray(a,float); med=np.nanmedian(x); mad=np.nanmedian(np.abs(x-med)); s=1.4826*mad
    if not np.isfinite(s) or s<=0: s=np.nanstd(x)
    return (x-med)/(s if s>0 else 1),float(med),float(s)

def main():
    rows=[]
    for y in range(2022,2027):
        raw=json.loads(get(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{REF}/data/spot-history-{y}.json"))
        for r in raw:
            if r.get("metal")!="Gold": continue
            ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
            if pd.isna(ts) or ts.weekday()>=5: continue
            try:v=float(r.get("spot"))
            except:continue
            rows.append({"date":ts.normalize(),"stak":v,"source":r.get("source"),"provider":r.get("provider")})
    st=pd.DataFrame(rows).sort_values("date").drop_duplicates("date",keep="last")
    with psycopg.connect(DSN,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
              SELECT observation_ts,value FROM observations
              WHERE series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1'
              ORDER BY observation_ts
            """)
            nr=cur.fetchall()
        conn.rollback()
    ny=pd.DataFrame(nr,columns=["ts","ny17"])
    ny["date"]=pd.to_datetime(ny.ts,utc=True).dt.tz_localize(None).dt.normalize()
    q=st.merge(ny[["date","ny17"]],on="date",how="inner",validate="one_to_one")
    q["log_ratio"]=np.log(q.stak/q.ny17)
    z,med,scale=robust_z(q.log_ratio); q["ratio_z"]=z
    q["dev_from_normal"]=np.abs(np.expm1(q.log_ratio-med))
    q["flag_3pct"]=q.dev_from_normal>=.03
    q["flag_5pct"]=q.dev_from_normal>=.05
    q["flag_z8"]=q.ratio_z.abs()>=8
    q.to_csv(OUT/"stak_upstream_vs_ny17.csv",index=False)
    flags=q[q.flag_3pct|q.flag_z8].sort_values("dev_from_normal",ascending=False)
    flags.to_csv(OUT/"stak_upstream_flags.csv",index=False)

    # Source-type diagnostics.
    src=q.groupby(q.source.fillna("NA")).agg(
      n=("date","size"),
      median_abs_dev=("dev_from_normal","median"),
      max_abs_dev=("dev_from_normal","max"),
      flags3=("flag_3pct","sum"),
      flags5=("flag_5pct","sum"),
      flagsz8=("flag_z8","sum"),
    ).reset_index().sort_values("max_abs_dev",ascending=False)
    src.to_csv(OUT/"stak_source_type_diagnostics.csv",index=False)

    # Also inspect all weekday 2026 four-metal sqld rows for synchronized robust anomalies.
    metals={"Gold":"gold","Silver":"silver","Platinum":"platinum","Palladium":"palladium"}
    rr=[]
    raw=json.loads(get(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{REF}/data/spot-history-2026.json"))
    for r in raw:
        if r.get("metal") not in metals: continue
        ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
        if pd.isna(ts) or ts.weekday()>=5: continue
        try:v=float(r.get("spot"))
        except:continue
        rr.append({"date":ts.normalize(),"metal":metals[r["metal"]],"value":v,"source":r.get("source")})
    m=pd.DataFrame(rr)
    p=m.pivot_table(index="date",columns="metal",values="value",aggfunc="last").sort_index()
    for c in metals.values():
        p[f"{c}_ret"]=np.log(p[c]/p[c].shift())
        zz,_,_=robust_z(p[f"{c}_ret"]); p[f"{c}_z"]=zz
    zc=[f"{c}_z" for c in metals.values()]
    p["extreme8_n"]=(p[zc].abs()>=8).sum(axis=1)
    p["max_abs_z"]=p[zc].abs().max(axis=1)
    p.reset_index().to_csv(OUT/"stak_2026_four_metal.csv",index=False)
    mf=p[(p.extreme8_n>=2)|(p.max_abs_z>=12)].reset_index().sort_values("max_abs_z",ascending=False)
    mf.to_csv(OUT/"stak_2026_multi_extreme_flags.csv",index=False)

    summ={
      "schema":"GOLD_H3_STAK_UPSTREAM_AUDIT_V1",
      "frozen_stak_ref":REF,
      "overlap_n":int(len(q)),
      "median_stak_ny17_ratio":float(np.exp(med)),
      "flags_3pct_n":int(q.flag_3pct.sum()),
      "flags_5pct_n":int(q.flag_5pct.sum()),
      "flags_z8_n":int(q.flag_z8.sum()),
      "flag_dates":flags.date.dt.strftime("%Y-%m-%d").tolist(),
      "source_diagnostics":src.to_dict(orient="records"),
      "multi_metal_2026_flags":mf.to_dict(orient="records"),
    }
    (OUT/"summary.json").write_text(json.dumps(summ,indent=2,default=str)+"\n")
    lines=["# GOLD H3 FROZEN STAKTRAKR UPSTREAM AUDIT — 2026-10-03","",
      f"- pinned ref: `{REF}`",
      f"- overlap with independent NY17-derived XAU: **{len(q)}** dates",
      f"- >=3% cross-source deviations: **{int(q.flag_3pct.sum())}**",
      f"- >=5% deviations: **{int(q.flag_5pct.sum())}**",
      f"- robust |z|>=8 deviations: **{int(q.flag_z8.sum())}**","",
      "## Cross-source flags","",
      "| Date | Stak | NY17 | Source | Deviation | z |",
      "|---|---:|---:|---|---:|---:|"]
    for r in flags.head(50).itertuples():
        lines.append(f"| {r.date.date()} | {r.stak:.4f} | {r.ny17:.4f} | {r.source} | {100*r.dev_from_normal:.2f}% | {r.ratio_z:.1f} |")
    lines+=["","## Source-type diagnostics","",
      "| Source | n | Median dev | Max dev | >3% | >5% | |z|>=8 |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for r in src.itertuples():
        lines.append(f"| {r.source} | {r.n} | {100*r.median_abs_dev:.2f}% | {100*r.max_abs_dev:.2f}% | {r.flags3} | {r.flags5} | {r.flagsz8} |")
    (OUT/"RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"RESULT.md").read_text())
if __name__=="__main__":main()
