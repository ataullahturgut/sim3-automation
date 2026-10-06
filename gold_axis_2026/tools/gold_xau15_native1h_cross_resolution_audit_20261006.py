from __future__ import annotations

import importlib.util, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
H1_PATH=AX/"tools"/"gold_session_iris_hourly_raw_replay_v1_20261006.py"
XAU15=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"XAU15_NATIVE1H_CROSS_RESOLUTION_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m
h1=loadmod("h1",H1_PATH)

def main():
    q=pd.read_csv(XAU15)
    if not {"dt_utc","close"}.issubset(q.columns):
        raise RuntimeError(f"XAU15_SCHEMA_FAIL:{q.columns.tolist()}")
    q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
    q["close"]=pd.to_numeric(q.close,errors="raise")
    q=q[(q.ts>="2023-01-01")&(q.ts<"2025-01-01")].dropna(subset=["ts","close"]).copy()
    q["hour"]=q.ts.dt.floor("1h")
    q["minute"]=q.ts.dt.minute

    # Only exact complete 00/15/30/45 UTC hour buckets.
    grp=q.groupby("hour",sort=True)
    agg=grp.agg(
      close_15m_agg=("close","last"),
      n15=("ts","size"),
      min_minute=("minute","min"),
      max_minute=("minute","max"),
      unique_minute=("minute","nunique"),
    ).reset_index()
    minute_sets=grp.minute.apply(lambda s: tuple(sorted(set(map(int,s))))).rename("minute_set").reset_index()
    agg=agg.merge(minute_sets,on="hour",validate="one_to_one")
    agg=agg[(agg.n15==4)&(agg.unique_minute==4)&agg.minute_set.eq((0,15,30,45))].copy()

    native=h1.load_hourly_raw().rename(columns={"ts":"hour","value":"close_native"})
    native=native[(native.hour>="2023-01-01")&(native.hour<"2025-01-01")][["hour","close_native"]].copy()
    m=agg.merge(native,on="hour",how="inner",validate="one_to_one")
    if m.empty:raise RuntimeError("NO_MATCHED_XAU_HOURS")

    m["abs_diff"]=(m.close_15m_agg-m.close_native).abs()
    m["rel_diff"]=m.abs_diff/m.close_native.abs()
    # report exact plus economically tiny tolerance; no silent rounding.
    m["exact"]=m.abs_diff.eq(0)
    for tol in [1e-8,1e-6,1e-4,1e-3,1e-2,0.1]:
        m[f"within_{tol:g}"]=m.abs_diff.le(tol)

    # samples: largest differences and spread through time
    largest=m.nlargest(30,"abs_diff")
    samples=pd.concat([m.head(5),largest,m.tail(5)]).drop_duplicates("hour").sort_values("hour")

    summary={
      "status":"XAU15_NATIVE1H_CROSS_RESOLUTION_AUDIT_COMPLETE",
      "source":"Twelve Data XAU/USD research series at two resolutions",
      "scope":"2023-2024 only",
      "matched_complete_hours":int(len(m)),
      "exact_matches":int(m.exact.sum()),
      "exact_match_rate":float(m.exact.mean()),
      "mismatch_n":int((~m.exact).sum()),
      "max_abs_diff":float(m.abs_diff.max()),
      "median_abs_diff":float(m.abs_diff.median()),
      "p95_abs_diff":float(m.abs_diff.quantile(.95)),
      "p99_abs_diff":float(m.abs_diff.quantile(.99)),
      "mean_abs_diff":float(m.abs_diff.mean()),
      "tolerance_counts":{c:int(m[c].sum()) for c in m.columns if c.startswith("within_")},
      "interpretation_rule":{
        "exact_equality":"preferred but not assumed across independently requested vendor resolutions",
        "model_resolution_claim":"if material close discrepancies exist, 15m-vs-1h performance cannot be attributed purely to sampling resolution without a same-source-derived 1h control",
        "next_if_mismatch":"derive 1h XAU deterministically from the governed 15m XAU archive and rerun the matched resolution test"
      }
    }
    m.to_csv(OUT/"matched_hours.csv",index=False)
    samples.to_csv(OUT/"samples.csv",index=False)
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
