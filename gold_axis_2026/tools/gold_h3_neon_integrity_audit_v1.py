from __future__ import annotations
import json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

OUT=Path(os.environ.get("OUT_DIR","gold_h3_neon_integrity_audit_out"))
OUT.mkdir(parents=True,exist_ok=True)
DSN=os.environ["NEON_DATABASE_URL"]
PRIMARY="XAU_USD_TWELVE_1H_RESEARCH_V1"

def qdf(cur,sql,params=None):
    cur.execute(sql,params or ())
    rows=cur.fetchall()
    cols=[d.name for d in cur.description]
    return pd.DataFrame(rows,columns=cols)

def main():
    with psycopg.connect(DSN,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")

            tables=qdf(cur,"""
              SELECT table_schema, table_name
              FROM information_schema.tables
              WHERE table_schema NOT IN ('pg_catalog','information_schema')
              ORDER BY table_schema,table_name
            """)
            tables.to_csv(OUT/"db_tables.csv",index=False)

            cols=qdf(cur,"""
              SELECT table_schema, table_name, ordinal_position, column_name, data_type, is_nullable
              FROM information_schema.columns
              WHERE table_schema NOT IN ('pg_catalog','information_schema')
              ORDER BY table_schema,table_name,ordinal_position
            """)
            cols.to_csv(OUT/"db_columns.csv",index=False)

            inv=qdf(cur,"""
              SELECT
                series_id,
                COUNT(*) AS raw_n,
                COUNT(DISTINCT observation_ts) AS distinct_ts_n,
                COUNT(*)-COUNT(DISTINCT observation_ts) AS duplicate_rows,
                MIN(observation_ts) AS first_ts,
                MAX(observation_ts) AS last_ts,
                MIN(retrieved_at) AS first_retrieved_at,
                MAX(retrieved_at) AS last_retrieved_at,
                COUNT(*) FILTER (WHERE value IS NULL) AS null_value_n,
                MIN(value) AS min_value,
                MAX(value) AS max_value
              FROM observations
              GROUP BY series_id
              ORDER BY raw_n DESC,series_id
            """)
            inv.to_csv(OUT/"series_inventory.csv",index=False)

            dup=qdf(cur,"""
              WITH g AS (
                SELECT series_id, observation_ts,
                       COUNT(*) AS revision_n,
                       COUNT(DISTINCT value) AS distinct_value_n,
                       MIN(value) AS min_value,
                       MAX(value) AS max_value,
                       MIN(retrieved_at) AS first_retrieved_at,
                       MAX(retrieved_at) AS last_retrieved_at
                FROM observations
                GROUP BY series_id, observation_ts
                HAVING COUNT(*)>1
              )
              SELECT *,
                     CASE
                       WHEN min_value>0 AND max_value>0
                       THEN ABS(LN(max_value/min_value))
                       ELSE ABS(max_value-min_value)
                     END AS revision_spread
              FROM g
              ORDER BY revision_spread DESC NULLS LAST, revision_n DESC, observation_ts
              LIMIT 5000
            """)
            dup.to_csv(OUT/"duplicate_revisions.csv",index=False)

            jumps=qdf(cur,"""
              WITH latest AS (
                SELECT series_id,observation_ts,value,retrieved_at,
                       ROW_NUMBER() OVER(PARTITION BY series_id,observation_ts ORDER BY retrieved_at DESC) rn
                FROM observations
                WHERE value IS NOT NULL
              ),
              d AS (
                SELECT series_id,observation_ts,value,retrieved_at,
                       LAG(observation_ts) OVER(PARTITION BY series_id ORDER BY observation_ts) prev_ts,
                       LAG(value) OVER(PARTITION BY series_id ORDER BY observation_ts) prev_value
                FROM latest WHERE rn=1
              ),
              s AS (
                SELECT *,
                  EXTRACT(EPOCH FROM (observation_ts-prev_ts))/3600.0 AS gap_hours,
                  CASE WHEN value>0 AND prev_value>0
                       THEN LN(value/prev_value) ELSE NULL END AS log_change,
                  CASE WHEN value IS NOT NULL AND prev_value IS NOT NULL
                       THEN value-prev_value ELSE NULL END AS abs_change
                FROM d
              ),
              ranked AS (
                SELECT *,
                       ROW_NUMBER() OVER(
                         PARTITION BY series_id
                         ORDER BY ABS(log_change) DESC NULLS LAST
                       ) AS jump_rank
                FROM s
              )
              SELECT * FROM ranked
              WHERE jump_rank<=25
              ORDER BY series_id,jump_rank
            """)
            jumps.to_csv(OUT/"series_top_jumps.csv",index=False)

            gaps=qdf(cur,"""
              WITH latest AS (
                SELECT series_id,observation_ts,
                       ROW_NUMBER() OVER(PARTITION BY series_id,observation_ts ORDER BY retrieved_at DESC) rn
                FROM observations
              ),
              d AS (
                SELECT series_id,observation_ts,
                       LAG(observation_ts) OVER(PARTITION BY series_id ORDER BY observation_ts) prev_ts
                FROM latest WHERE rn=1
              ),
              r AS (
                SELECT *,
                  EXTRACT(EPOCH FROM (observation_ts-prev_ts))/3600.0 AS gap_hours,
                  ROW_NUMBER() OVER(
                    PARTITION BY series_id
                    ORDER BY EXTRACT(EPOCH FROM (observation_ts-prev_ts)) DESC NULLS LAST
                  ) gap_rank
                FROM d
              )
              SELECT * FROM r
              WHERE gap_rank<=25
              ORDER BY series_id,gap_rank
            """)
            gaps.to_csv(OUT/"series_top_gaps.csv",index=False)

            prim=qdf(cur,"""
              WITH latest AS (
                SELECT observation_ts,value,retrieved_at,
                       ROW_NUMBER() OVER(PARTITION BY observation_ts ORDER BY retrieved_at DESC) rn,
                       COUNT(*) OVER(PARTITION BY observation_ts) revision_n
                FROM observations WHERE series_id=%s
              )
              SELECT observation_ts,value,retrieved_at,revision_n
              FROM latest WHERE rn=1
              ORDER BY observation_ts
            """,(PRIMARY,))
            prim.to_csv(OUT/"primary_xau_latest.csv",index=False)

        conn.rollback()

    if prim.empty:
        raise RuntimeError("PRIMARY_SERIES_EMPTY")

    prim["observation_ts"]=pd.to_datetime(prim.observation_ts,utc=True)
    prim["value"]=pd.to_numeric(prim.value,errors="coerce")
    prim["prev_value"]=prim.value.shift(1)
    prim["prev_ts"]=prim.observation_ts.shift(1)
    prim["gap_hours"]=(prim.observation_ts-prim.prev_ts).dt.total_seconds()/3600
    prim["logret"]=np.log(prim.value/prim.prev_value)
    prim["abs_logret"]=prim.logret.abs()

    # Gold 1-hour moves above 2.5% are audit candidates, not automatically errors.
    pj=prim[prim.abs_logret>=0.025].copy().sort_values("abs_logret",ascending=False)
    pj.to_csv(OUT/"primary_xau_jump_candidates.csv",index=False)

    # Check regularity within adjacent observations. Weekend/holiday gaps are reported separately.
    pg=prim[prim.gap_hours>4].copy().sort_values("gap_hours",ascending=False)
    pg.to_csv(OUT/"primary_xau_gap_candidates.csv",index=False)

    # Duplicate revisions specifically for the binding H3 source.
    pdp=dup[dup.series_id.astype(str)==PRIMARY].copy()
    pdp.to_csv(OUT/"primary_xau_duplicate_revisions.csv",index=False)

    # Robust return diagnostics.
    r=prim.logret.dropna().to_numpy(float)
    med=float(np.median(r))
    mad=float(np.median(np.abs(r-med)))
    scale=1.4826*mad if mad>0 else float(np.std(r,ddof=0))
    prim["robust_z_ret"]=(prim.logret-med)/(scale if scale>0 else 1.0)
    rz=prim[prim.robust_z_ret.abs()>=8].copy().sort_values("robust_z_ret",key=lambda x:x.abs(),ascending=False)
    rz.to_csv(OUT/"primary_xau_robust_outliers.csv",index=False)

    # Summary.
    summary={
      "schema":"GOLD_H3_NEON_INTEGRITY_AUDIT_V1",
      "read_only":True,
      "primary_series":PRIMARY,
      "tables_n":int(len(tables)),
      "series_n":int(len(inv)),
      "series_with_duplicate_rows":int((inv.duplicate_rows.astype(int)>0).sum()),
      "duplicate_timestamp_groups_n":int(len(dup)),
      "duplicate_value_conflict_groups_n":int((pd.to_numeric(dup.distinct_value_n,errors="coerce")>1).sum()) if len(dup) else 0,
      "primary":{
        "rows":int(len(prim)),
        "first_ts":str(prim.observation_ts.min()),
        "last_ts":str(prim.observation_ts.max()),
        "revision_rows":int((prim.revision_n.astype(int)>1).sum()),
        "jump_candidates_abs_logret_ge_2_5pct":int(len(pj)),
        "robust_outliers_abs_z_ge_8":int(len(rz)),
        "gap_candidates_gt_4h":int(len(pg)),
        "median_hourly_logret":med,
        "mad_scale":scale,
        "max_abs_hourly_logret":float(prim.abs_logret.max()),
      }
    }
    (OUT/"neon_integrity_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 NEON DATABASE INTEGRITY AUDIT — 2026-10-03","",
      "**Mode:** READ ONLY. No database rows were changed.","",
      "## Inventory","",
      f"- user tables: **{len(tables)}**",
      f"- observation series: **{len(inv)}**",
      f"- series with duplicate observation timestamps: **{summary['series_with_duplicate_rows']}**",
      f"- duplicate timestamp groups inspected: **{summary['duplicate_timestamp_groups_n']}**",
      f"- duplicate groups with conflicting values: **{summary['duplicate_value_conflict_groups_n']}**","",
      "## Binding H3 hourly XAU source","",
      f"- series: `{PRIMARY}`",
      f"- deduped rows: **{len(prim)}**",
      f"- range: **{prim.observation_ts.min()} -> {prim.observation_ts.max()}**",
      f"- timestamps with >1 stored revision: **{summary['primary']['revision_rows']}**",
      f"- abs 1h log-return >=2.5% candidates: **{len(pj)}**",
      f"- robust |z|>=8 return outliers: **{len(rz)}**",
      f"- gaps >4h: **{len(pg)}**",
      f"- max abs adjacent log return: **{100*summary['primary']['max_abs_hourly_logret']:.3f}%**","",
      "## Largest primary XAU jump candidates","",
      "| Timestamp | Prev timestamp | Prev | Value | Log return | Revision n |",
      "|---|---|---:|---:|---:|---:|"
    ]
    for x in pj.head(30).itertuples():
        lines.append(f"| {x.observation_ts} | {x.prev_ts} | {x.prev_value:.4f} | {x.value:.4f} | {100*x.logret:+.3f}% | {int(x.revision_n)} |")
    lines += ["","## Primary XAU conflicting revisions",""]
    if pdp.empty:
        lines.append("- none")
    else:
        lines += ["| Timestamp | Revisions | Distinct values | Min | Max | Spread |",
                  "|---|---:|---:|---:|---:|---:|"]
        for x in pdp.head(50).itertuples():
            lines.append(f"| {x.observation_ts} | {int(x.revision_n)} | {int(x.distinct_value_n)} | {x.min_value} | {x.max_value} | {x.revision_spread} |")
    lines += ["","## Governance","",
      "Jump and gap flags are screening candidates, not automatic data errors. Any flagged H3 source point must be independently cross-checked against the original provider before correction."
    ]
    (OUT/"NEON_INTEGRITY_AUDIT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"NEON_INTEGRITY_AUDIT.md").read_text())

if __name__=="__main__":
    main()
