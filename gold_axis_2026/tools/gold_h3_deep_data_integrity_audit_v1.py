from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_integrity_deep_audit_out"))
OUT.mkdir(parents=True,exist_ok=True)
DSN=os.environ["NEON_DATABASE_URL"]
FROZEN=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"

METALS={
 "gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
 "silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
 "platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
 "palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
REV_SERIES=["XAU_DAILY_XAUS","VIX_CBOE","GVZ_CBOE"]

def main():
    frozen=pd.read_csv(FROZEN)
    frozen["date"]=pd.to_datetime(frozen.date).dt.normalize()

    with psycopg.connect(DSN,autocommit=False) as conn:
      with conn.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")

        cur.execute("""
          SELECT series_id,observation_ts,value,retrieved_at
          FROM observations
          WHERE series_id = ANY(%s)
          ORDER BY series_id,observation_ts,retrieved_at
        """,(list(METALS.values()),))
        rr=cur.fetchall()
        metal=pd.DataFrame(rr,columns=["series_id","observation_ts","value","retrieved_at"])
        metal["observation_ts"]=pd.to_datetime(metal.observation_ts,utc=True)
        metal["date"]=metal.observation_ts.dt.tz_localize(None).dt.normalize()
        metal["value"]=pd.to_numeric(metal.value,errors="coerce")

        cur.execute("""
          SELECT series_id,observation_ts,value,retrieved_at
          FROM observations
          WHERE series_id = ANY(%s)
          ORDER BY series_id,observation_ts,retrieved_at
        """,(REV_SERIES,))
        rr=cur.fetchall()
        rev=pd.DataFrame(rr,columns=["series_id","observation_ts","value","retrieved_at"])
        rev["observation_ts"]=pd.to_datetime(rev.observation_ts,utc=True)
        rev["retrieved_at"]=pd.to_datetime(rev.retrieved_at,utc=True)
        rev["value"]=pd.to_numeric(rev.value,errors="coerce")

        cur.execute("""
          SELECT observation_ts,value,retrieved_at
          FROM observations
          WHERE series_id='XAU_USD_TWELVE_1H_RESEARCH_V1'
          ORDER BY observation_ts,retrieved_at
        """)
        rr=cur.fetchall()
        h=pd.DataFrame(rr,columns=["ts","value","retrieved_at"])
        h["ts"]=pd.to_datetime(h.ts,utc=True)
        h["retrieved_at"]=pd.to_datetime(h.retrieved_at,utc=True)
        h["value"]=pd.to_numeric(h.value,errors="coerce")
      conn.rollback()

    # Current DB Stak latest values by common calendar date.
    inv={v:k for k,v in METALS.items()}
    ml=metal.sort_values("retrieved_at").drop_duplicates(["series_id","date"],keep="last")
    piv=ml.pivot(index="date",columns="series_id",values="value").rename(columns=inv).sort_index()

    max_db_date=piv.index.max()
    cmp=frozen[frozen.date<=max_db_date].set_index("date").join(piv,how="outer",lsuffix="_frozen",rsuffix="_neon")
    rows=[]
    for d,r in cmp.iterrows():
      for m in METALS:
        a=r.get(f"{m}_frozen",np.nan); c=r.get(f"{m}_neon",np.nan)
        if pd.isna(a) and pd.isna(c): continue
        status="MATCH"
        rel=np.nan
        if pd.isna(a): status="NEON_ONLY"
        elif pd.isna(c): status="FROZEN_ONLY"
        else:
          rel=abs(float(a)-float(c))/max(abs(float(c)),1e-12)
          if rel>1e-9: status="VALUE_DIFF"
        if status!="MATCH":
          rows.append({"date":d,"metal":m,"status":status,"frozen_value":a,"neon_value":c,"rel_diff":rel})
    mism=pd.DataFrame(rows)
    if len(mism):
      mism=mism.sort_values(["date","metal"])
    mism.to_csv(OUT/"frozen_vs_neon_mismatches.csv",index=False)

    # Date-level common-row availability mismatch.
    fdates=set(frozen.loc[frozen.date<=max_db_date,"date"])
    common_db=set(piv.dropna(subset=list(METALS)).index)
    frozen_only_dates=sorted(fdates-common_db)
    neon_only_dates=sorted(common_db-fdates)
    pd.DataFrame({"date":frozen_only_dates}).to_csv(OUT/"frozen_only_dates.csv",index=False)
    pd.DataFrame({"date":neon_only_dates}).to_csv(OUT/"neon_only_dates.csv",index=False)

    # Revision chronology.
    rev_rows=[]
    for (sid,ts),g in rev.groupby(["series_id","observation_ts"],sort=True):
      if len(g)<2: continue
      g=g.sort_values("retrieved_at")
      first=float(g.iloc[0].value); last=float(g.iloc[-1].value)
      mn=float(g.value.min()); mx=float(g.value.max())
      denom=max(abs(first),1e-12)
      rev_rows.append({
        "series_id":sid,"observation_ts":ts,"revision_n":int(len(g)),
        "distinct_value_n":int(g.value.nunique(dropna=True)),
        "first_value":first,"last_value":last,"min_value":mn,"max_value":mx,
        "first_retrieved_at":g.iloc[0].retrieved_at,"last_retrieved_at":g.iloc[-1].retrieved_at,
        "first_to_last_pct":100*(last-first)/denom,
        "max_range_pct":100*(mx-mn)/max(abs(mn),1e-12),
      })
    rdf=pd.DataFrame(rev_rows)
    if len(rdf): rdf=rdf.sort_values("max_range_pct",ascending=False)
    rdf.to_csv(OUT/"revision_chronology.csv",index=False)

    revsum=[]
    for sid in REV_SERIES:
      z=rdf[rdf.series_id==sid].copy() if len(rdf) else pd.DataFrame()
      revsum.append({
        "series_id":sid,
        "revised_timestamps":int(len(z)),
        "conflicting_timestamps":int((z.distinct_value_n>1).sum()) if len(z) else 0,
        "median_abs_first_to_last_pct":float(z.first_to_last_pct.abs().median()) if len(z) else 0.0,
        "p95_abs_first_to_last_pct":float(z.first_to_last_pct.abs().quantile(.95)) if len(z) else 0.0,
        "max_abs_first_to_last_pct":float(z.first_to_last_pct.abs().max()) if len(z) else 0.0,
        "max_range_pct":float(z.max_range_pct.max()) if len(z) else 0.0,
      })
    rs=pd.DataFrame(revsum)
    rs.to_csv(OUT/"revision_summary.csv",index=False)

    # Hourly XAU latest-dedup + spike/reversion pattern.
    hh=h.sort_values("retrieved_at").drop_duplicates("ts",keep="last").sort_values("ts").reset_index(drop=True)
    hh["r1"]=np.log(hh.value/hh.value.shift(1))
    hh["rnext"]=hh.r1.shift(-1)
    hh["gap_prev_h"]=(hh.ts-hh.ts.shift(1)).dt.total_seconds()/3600
    hh["gap_next_h"]=(hh.ts.shift(-1)-hh.ts).dt.total_seconds()/3600
    hh["roundtrip"]=hh.r1+hh.rnext
    # suspicious tick: both adjacent moves >=1.25%, opposite sign, each 1h apart, round-trip residual <=0.35%
    sp=hh[
      (hh.r1.abs()>=.0125)&(hh.rnext.abs()>=.0125)&
      (hh.r1*hh.rnext<0)&
      (hh.gap_prev_h<=1.1)&(hh.gap_next_h<=1.1)&
      (hh.roundtrip.abs()<=.0035)
    ].copy()
    sp.to_csv(OUT/"hourly_spike_reversion_candidates.csv",index=False)

    summary={
      "schema":"GOLD_H3_DEEP_DATA_INTEGRITY_AUDIT_V1",
      "read_only":True,
      "neon_common_metal_last_date":str(pd.Timestamp(max_db_date).date()),
      "frozen_rows_through_db_end":int((frozen.date<=max_db_date).sum()),
      "frozen_vs_neon_mismatch_cells":int(len(mism)),
      "value_diff_cells":int((mism.status=="VALUE_DIFF").sum()) if len(mism) else 0,
      "frozen_only_cells":int((mism.status=="FROZEN_ONLY").sum()) if len(mism) else 0,
      "neon_only_cells":int((mism.status=="NEON_ONLY").sum()) if len(mism) else 0,
      "frozen_only_dates_n":int(len(frozen_only_dates)),
      "frozen_only_dates":[str(pd.Timestamp(x).date()) for x in frozen_only_dates],
      "neon_only_dates_n":int(len(neon_only_dates)),
      "neon_only_dates":[str(pd.Timestamp(x).date()) for x in neon_only_dates],
      "revision_summary":rs.to_dict(orient="records"),
      "hourly_spike_reversion_candidates_n":int(len(sp)),
      "hourly_spike_reversion_candidates":sp.head(50).assign(ts=sp.ts.astype(str)).to_dict(orient="records"),
    }
    (OUT/"deep_integrity_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 DEEP DATA-INTEGRITY AUDIT — 2026-10-03","",
      "**Mode:** READ ONLY. No database writes.","",
      "## Frozen daily file vs Neon StakTrakr","",
      f"- Neon four-metal common coverage ends: **{pd.Timestamp(max_db_date).date()}**",
      f"- mismatch cells through that date: **{len(mism)}**",
      f"- actual value differences on dates present in both: **{int((mism.status=='VALUE_DIFF').sum()) if len(mism) else 0}**",
      f"- frozen-only dates: **{len(frozen_only_dates)}**",
      f"- Neon-only dates: **{len(neon_only_dates)}**",""
    ]
    if len(mism):
      lines += ["| Date | Metal | Status | Frozen | Neon | Rel diff |",
                "|---|---|---|---:|---:|---:|"]
      for r in mism.head(100).itertuples():
        rd="" if pd.isna(r.rel_diff) else f"{100*r.rel_diff:.4f}%"
        lines.append(f"| {pd.Timestamp(r.date).date()} | {r.metal} | {r.status} | {r.frozen_value} | {r.neon_value} | {rd} |")
    else:
      lines.append("- no mismatches")

    lines += ["","## Revisioned live/database series","",
      "| Series | Revised timestamps | Conflicting | Median | P95 | Max first→last | Max range |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for r in rs.itertuples():
      lines.append(f"| {r.series_id} | {r.revised_timestamps} | {r.conflicting_timestamps} | {r.median_abs_first_to_last_pct:.4f}% | {r.p95_abs_first_to_last_pct:.4f}% | {r.max_abs_first_to_last_pct:.4f}% | {r.max_range_pct:.4f}% |")

    lines += ["","## Binding historical hourly XAU spike/reversion screen","",
      f"- suspicious 1-hour spike+immediate-reversal candidates: **{len(sp)}**",""]
    if len(sp):
      lines += ["| Time | Value | r1 | next r1 | roundtrip |",
                "|---|---:|---:|---:|---:|"]
      for r in sp.head(50).itertuples():
        lines.append(f"| {r.ts} | {r.value:.4f} | {100*r.r1:+.3f}% | {100*r.rnext:+.3f}% | {100*r.roundtrip:+.3f}% |")
    else:
      lines.append("- none")

    lines += ["","## Interpretation rule","",
      "A frozen-only date is not automatically an error, because the pinned external snapshot can contain observations not present in the current Neon import. "
      "However, any frozen-only row that is also inconsistent with an independent trusted XAU source must be quarantined before model scoring."
    ]
    (OUT/"DEEP_DATA_INTEGRITY_AUDIT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"DEEP_DATA_INTEGRITY_AUDIT.md").read_text())

if __name__=="__main__": main()
