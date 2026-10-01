from __future__ import annotations

import json, os, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

OUT=Path(os.environ.get("OUT_DIR","global_xau_bridge_out"))
OUT.mkdir(parents=True,exist_ok=True)

HIST="XAU_STAKTRAKR_RESEARCH_DAILY_R1"
LIVE="XAU_EOD_TWELVE_NY17"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def read_series(cur,sid):
    cur.execute("""
        SELECT observation_ts, value, source, source_symbol, quality_status, retrieved_at
        FROM observations
        WHERE series_id=%s
        ORDER BY observation_ts, retrieved_at
    """,(sid,))
    rows=cur.fetchall()
    if not rows:
        return pd.DataFrame(columns=["observation_ts","value","source","source_symbol","quality_status","retrieved_at"])
    x=pd.DataFrame(rows,columns=["observation_ts","value","source","source_symbol","quality_status","retrieved_at"])
    x["observation_ts"]=pd.to_datetime(x["observation_ts"],utc=True)
    x["retrieved_at"]=pd.to_datetime(x["retrieved_at"],utc=True)
    # Keep latest retrieval per exact observation timestamp; values should be identical for these research/canonical price rows.
    x=x.sort_values(["observation_ts","retrieved_at"]).drop_duplicates("observation_ts",keep="last")
    x["date_ny"]=x["observation_ts"].dt.tz_convert("America/New_York").dt.date
    x["date_utc"]=x["observation_ts"].dt.date
    x["value"]=pd.to_numeric(x["value"],errors="coerce")
    return x

def main():
    dsn=os.environ["NEON_DATABASE_URL"]
    with psycopg.connect(dsn,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
                SELECT series_id, count(*) AS n,
                       min(observation_ts) AS first_ts,
                       max(observation_ts) AS last_ts,
                       min(retrieved_at) AS first_retrieval,
                       max(retrieved_at) AS last_retrieval,
                       count(*) FILTER (WHERE value IS NULL OR value<=0) AS nonpositive_or_null
                FROM observations
                WHERE series_id ILIKE 'XAU%%'
                   OR series_id ILIKE '%%GOLD%%'
                   OR series_id ILIKE '%%STAKTRAKR%%'
                GROUP BY series_id
                ORDER BY series_id
            """)
            inv=pd.DataFrame(cur.fetchall(),columns=["series_id","n","first_ts","last_ts","first_retrieval","last_retrieval","nonpositive_or_null"])
            hist=read_series(cur,HIST)
            live=read_series(cur,LIVE)
        conn.rollback()

    inv.to_csv(OUT/"global_xau_neon_inventory.csv",index=False)

    meta={}
    for sid,x in [(HIST,hist),(LIVE,live)]:
        weekdays=int(pd.Series(x["date_ny"]).map(lambda d:d.weekday()<5).sum()) if len(x) else 0
        meta[sid]={
            "n":int(len(x)),
            "first_obs":None if len(x)==0 else x.observation_ts.min().isoformat(),
            "last_obs":None if len(x)==0 else x.observation_ts.max().isoformat(),
            "weekday_rows":weekdays,
            "source_values":sorted(set(x.source.dropna().astype(str))),
            "source_symbols":sorted(set(x.source_symbol.dropna().astype(str))),
            "quality_values":sorted(set(x.quality_status.dropna().astype(str))),
            "nonpositive":int((x.value<=0).sum()) if len(x) else 0,
            "duplicate_trade_dates_ny":int(x.duplicated("date_ny").sum()) if len(x) else 0,
        }

    # Historical chronology counts, target-only.
    chronology={}
    if len(hist):
        h=hist.copy()
        h=h[h["value"].notna() & (h["value"]>0)].copy()
        h["date"]=pd.to_datetime(h["date_ny"].astype(str))
        h=h[h.date.dt.weekday<5]
        h=h.sort_values("date").drop_duplicates("date",keep="last")
        for label,a,b in [
            ("PREDEV_TO_2021","1900-01-01","2021-12-31"),
            ("DEV_2022_2024","2022-01-01","2024-12-31"),
            ("FROZEN_2025","2025-01-01","2025-12-31"),
            ("RETRO_2026_TO_JUL","2026-01-01","2026-07-31"),
        ]:
            z=h[(h.date>=a)&(h.date<=b)]
            chronology[label]={"n":int(len(z)),"first":None if len(z)==0 else str(z.date.min().date()),"last":None if len(z)==0 else str(z.date.max().date())}
        vals=np.log(h.value.to_numpy(float))
        h["r1"]=np.r_[np.nan,np.diff(vals)]
        # Eligible forward-origin counts by horizon, calendar bounded within each split.
        for label,a,b in [("DEV","2022-01-01","2024-12-31"),("FROZEN_2025","2025-01-01","2025-12-31")]:
            zidx=np.where((h.date>=a)&(h.date<=b))[0]
            chronology[label+"_eligible"]={}
            for H in [1,3,5]:
                n=sum((i+H)<len(h) and h.date.iloc[i+H]<=pd.Timestamp(b) for i in zidx)
                chronology[label+"_eligible"][f"H{H}"]=int(n)

    # Bridge using NY trade date. Historical series is date-labelled; live is exact NY17.
    bridge={}
    bridge_df=pd.DataFrame()
    if len(hist) and len(live):
        hh=hist[["date_ny","value"]].rename(columns={"value":"hist_price"}).copy()
        ll=live[["date_ny","value"]].rename(columns={"value":"ny17_price"}).copy()
        hh=hh.groupby("date_ny",as_index=False).last()
        ll=ll.groupby("date_ny",as_index=False).last()
        b=hh.merge(ll,on="date_ny",how="inner").sort_values("date_ny").reset_index(drop=True)
        b["hist_r1"]=np.log(b.hist_price).diff()
        b["ny17_r1"]=np.log(b.ny17_price).diff()
        q=b.dropna(subset=["hist_r1","ny17_r1"]).copy()
        if len(q):
            pear=float(q.hist_r1.corr(q.ny17_r1))
            spear=float(q.hist_r1.corr(q.ny17_r1,method="spearman"))
            diff=q.hist_r1-q.ny17_r1
            sign=float(((q.hist_r1>0)==(q.ny17_r1>0)).mean())
            ratio=b.hist_price/b.ny17_price
            bridge={
                "common_level_dates":int(len(b)),
                "common_return_pairs":int(len(q)),
                "first_common":str(b.date_ny.min()),
                "last_common":str(b.date_ny.max()),
                "pearson_r1":pear,
                "spearman_r1":spear,
                "sign_agreement":sign,
                "mean_abs_return_diff":float(diff.abs().mean()),
                "return_diff_sd":float(diff.std(ddof=0)),
                "median_level_ratio_hist_over_ny17":float(ratio.median()),
                "level_ratio_cv":float(ratio.std(ddof=0)/ratio.mean()),
            }
            bridge["pass"]=bool(
                len(q)>=30 and pear>=0.90 and spear>=0.88 and sign>=0.85 and bridge["return_diff_sd"]<=0.005
            )
        bridge_df=b
    bridge_df.to_csv(OUT/"global_xau_hist_vs_ny17_bridge.csv",index=False)

    summary={"meta":meta,"chronology":chronology,"bridge":bridge}
    (OUT/"global_xau_bridge_summary.json").write_text(json.dumps(summary,indent=2,default=str),encoding="utf-8")
    lines=[
        "# GOLD SHORT-HORIZON GLOBAL XAU — Target Bridge Audit Result","",
        "## Existing series",
    ]
    for sid in [HIST,LIVE]:
        m=meta[sid]
        lines.append(f"- {sid}: n={m['n']}, first={m['first_obs']}, last={m['last_obs']}, sources={m['source_values']}, quality={m['quality_values']}")
    lines += ["","## Historical chronology",json.dumps(chronology,indent=2),
              "","## Historical-to-NY17 bridge",json.dumps(bridge,indent=2),
              "","## Decision"]
    if bridge.get("pass"):
        lines.append("BRIDGE PASS — historical XAU return target may be used for development while NY17 remains the prospective live target anchor.")
    else:
        lines.append("BRIDGE FAIL — do not stitch the historical series to NY17 without another authority solution.")
    (OUT/"GLOBAL_XAU_BRIDGE_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    hashes={p.name:sha(p) for p in files}
    (OUT/"hashes.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
    print("GLOBAL_XAU_BRIDGE_SUMMARY="+json.dumps(summary,separators=(",",":"),default=str))
    print((OUT/"GLOBAL_XAU_BRIDGE_RESULT.md").read_text())

if __name__=="__main__":
    main()
