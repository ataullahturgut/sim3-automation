from __future__ import annotations

import gzip, hashlib, json, os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "DATABENTO_SI_PL_1M_15M_VALIDATION_OUT"
OUT.mkdir(exist_ok=True)

DATASET = "GLBX.MDP3"
START = "2022-01-01"
END = "2025-01-01"
SYMBOLS = ["SI.n.0", "PL.n.0"]
MAX_COST_USD = 8.00
PRICE_ATOL = 1e-8
PRICE_RTOL = 1e-10
VOLUME_ATOL = 0.0

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize(store, schema: str) -> pd.DataFrame:
    q=store.to_df().reset_index()
    if "ts_event" not in q.columns and "index" in q.columns:
        q=q.rename(columns={"index":"ts_event"})
    req=["ts_event","symbol","instrument_id","open","high","low","close","volume"]
    miss=[c for c in req if c not in q.columns]
    if miss:
        raise RuntimeError(f"{schema}_MISSING_COLUMNS:{miss}; cols={q.columns.tolist()}")
    q=q[req].copy()
    q["ts_event"]=pd.to_datetime(q["ts_event"],utc=True,errors="raise")
    q["symbol"]=q["symbol"].astype(str)
    q["instrument_id"]=pd.to_numeric(q["instrument_id"],errors="raise").astype("int64")
    for c in ["open","high","low","close","volume"]:
        q[c]=pd.to_numeric(q[c],errors="raise")
    if set(q.symbol.unique()) != set(SYMBOLS):
        raise RuntimeError(f"{schema}_SYMBOL_SET_FAIL:{sorted(q.symbol.unique())}")
    dup=int(q.duplicated(["symbol","ts_event"]).sum())
    if dup:
        raise RuntimeError(f"{schema}_DUPLICATE:{dup}")
    if (q[["open","high","low","close"]]<=0).any(axis=None):
        raise RuntimeError(f"{schema}_NONPOSITIVE_PRICE")
    bad=((q.high < q[["open","close","low"]].max(axis=1)) |
         (q.low > q[["open","close","high"]].min(axis=1)))
    if bad.any():
        raise RuntimeError(f"{schema}_BAD_OHLC:{int(bad.sum())}")
    if (q.volume<0).any():
        raise RuntimeError(f"{schema}_NEG_VOLUME:{int((q.volume<0).sum())}")
    return q.sort_values(["symbol","ts_event"]).reset_index(drop=True)

def aggregate(q: pd.DataFrame, freq: str) -> pd.DataFrame:
    x=q.copy()
    x["bucket"]=x.ts_event.dt.floor(freq)
    grp=x.groupby(["symbol","bucket"],sort=True,observed=True)
    out=grp.agg(
        open=("open","first"),
        high=("high","max"),
        low=("low","min"),
        close=("close","last"),
        volume=("volume","sum"),
        first_ts=("ts_event","min"),
        last_ts=("ts_event","max"),
        minute_bars=("ts_event","size"),
        instrument_id_count=("instrument_id","nunique"),
        instrument_id_first=("instrument_id","first"),
        instrument_id_last=("instrument_id","last"),
    ).reset_index().rename(columns={"bucket":"ts_event"})
    mins=int(pd.Timedelta(freq).total_seconds()/60)
    out["available_at_utc"]=out["ts_event"]+pd.Timedelta(minutes=mins)
    out["roll_ambiguous"]=out.instrument_id_count.gt(1)
    return out

def cross_resolution(agg1h: pd.DataFrame, native1h: pd.DataFrame):
    a=agg1h.copy()
    n=native1h.copy()
    m=a.merge(n,on=["symbol","ts_event"],how="inner",suffixes=("_agg","_native"))
    rows=[]
    for sym,g in m.groupby("symbol",sort=True):
        usable=g[~g.roll_ambiguous].copy()
        rec={"symbol":sym,"matched_hours":int(len(g)),"non_roll_ambiguous_hours":int(len(usable))}
        for col in ["open","high","low","close"]:
            aa=usable[f"{col}_agg"].to_numpy(float)
            bb=usable[f"{col}_native"].to_numpy(float)
            ok=np.isclose(aa,bb,rtol=PRICE_RTOL,atol=PRICE_ATOL,equal_nan=False)
            rec[f"{col}_match_n"]=int(ok.sum())
            rec[f"{col}_mismatch_n"]=int((~ok).sum())
            rec[f"{col}_max_abs_diff"]=float(np.max(np.abs(aa-bb))) if len(aa) else None
        va=usable["volume_agg"].to_numpy(float)
        vb=usable["volume_native"].to_numpy(float)
        vok=np.isclose(va,vb,rtol=0,atol=VOLUME_ATOL,equal_nan=False)
        rec["volume_match_n"]=int(vok.sum())
        rec["volume_mismatch_n"]=int((~vok).sum())
        rec["volume_max_abs_diff"]=float(np.max(np.abs(va-vb))) if len(va) else None
        rec["all_ohlcv_match_n"]=int(np.logical_and.reduce([
            np.isclose(usable[f"{c}_agg"].to_numpy(float),usable[f"{c}_native"].to_numpy(float),
                       rtol=PRICE_RTOL,atol=PRICE_ATOL)
            for c in ["open","high","low","close"]
        ] + [vok]).sum()) if len(usable) else 0
        rows.append(rec)
    return pd.DataFrame(rows),m

def save_gz(df: pd.DataFrame, path: Path):
    with gzip.open(path,"wt",encoding="utf-8",newline="") as f:
        df.to_csv(f,index=False)

def main():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)

    req1m=dict(dataset=DATASET,schema="ohlcv-1m",symbols=SYMBOLS,stype_in="continuous",start=START,end=END)
    req1h=dict(dataset=DATASET,schema="ohlcv-1h",symbols=SYMBOLS,stype_in="continuous",start=START,end=END)
    cost1m=float(client.metadata.get_cost(**req1m))
    cost1h=float(client.metadata.get_cost(**req1h))
    total=cost1m+cost1h

    preflight={"dataset":DATASET,"symbols":SYMBOLS,"start":START,"end":END,
               "cost_1m_usd":cost1m,"cost_native_1h_usd":cost1h,
               "estimated_total_usd":total,"cost_cap_usd":MAX_COST_USD}
    (OUT/"preflight_cost.json").write_text(json.dumps(preflight,indent=2)+"\n")
    if total > MAX_COST_USD:
        raise RuntimeError(f"COST_CAP_EXCEEDED estimated={total:.6f} cap={MAX_COST_USD:.2f}")

    raw1m=normalize(client.timeseries.get_range(**req1m),"ohlcv-1m")
    native1h=normalize(client.timeseries.get_range(**req1h),"ohlcv-1h")

    # Require full three-year presence for both identities.
    raw1m["year"]=raw1m.ts_event.dt.year
    for sym,g in raw1m.groupby("symbol"):
        miss={2022,2023,2024}-set(g.year.unique())
        if miss:
            raise RuntimeError(f"{sym}_1M_MISSING_YEARS:{sorted(miss)}")
    raw1m=raw1m.drop(columns=["year"])

    agg15=aggregate(raw1m,"15min")
    agg1h=aggregate(raw1m,"1h")
    audit,matched=cross_resolution(agg1h,native1h)

    # Hard validation: every non-roll-ambiguous matched hour must agree in OHLCV.
    fail_cols=[]
    for r in audit.itertuples(index=False):
        for col in ["open","high","low","close","volume"]:
            if getattr(r,f"{col}_mismatch_n") != 0:
                fail_cols.append((r.symbol,col,getattr(r,f"{col}_mismatch_n")))
    validation_status="PASS" if not fail_cols else "FAIL"

    # Coverage and cadence diagnostics for 15m output.
    coverage=[]
    for sym,g in agg15.groupby("symbol",sort=True):
        for y,gy in g.groupby(g.ts_event.dt.year):
            coverage.append({
                "symbol":sym,"year":int(y),"bars_15m":int(len(gy)),
                "first":gy.ts_event.min().isoformat(),"last":gy.ts_event.max().isoformat(),
                "roll_ambiguous_bars":int(gy.roll_ambiguous.sum()),
                "median_1m_rows_per_15m":float(gy.minute_bars.median()),
                "p01_1m_rows_per_15m":float(gy.minute_bars.quantile(.01)),
                "p99_1m_rows_per_15m":float(gy.minute_bars.quantile(.99)),
            })
    coverage=pd.DataFrame(coverage)

    # Sample exact rows for manual audit, spread across years/symbols.
    samples=[]
    for sym,g in matched.groupby("symbol",sort=True):
        g=g[~g.roll_ambiguous].sort_values("ts_event")
        for y in [2022,2023,2024]:
            gy=g[g.ts_event.dt.year.eq(y)]
            if gy.empty: continue
            for ix in sorted(set([0,len(gy)//2,len(gy)-1])):
                r=gy.iloc[ix]
                samples.append({
                    "symbol":sym,"ts_event":r.ts_event.isoformat(),
                    **{f"{c}_agg":float(r[f"{c}_agg"]) for c in ["open","high","low","close","volume"]},
                    **{f"{c}_native":float(r[f"{c}_native"]) for c in ["open","high","low","close","volume"]},
                })
    samples=pd.DataFrame(samples)

    raw_path=OUT/"databento_si_pl_ohlcv1m_n0_2022_2024.csv.gz"
    bar15_path=OUT/"databento_si_pl_ohlcv15m_from1m_n0_2022_2024.csv.gz"
    native_path=OUT/"databento_si_pl_native_ohlcv1h_n0_2022_2024.csv.gz"
    save_gz(raw1m,raw_path); save_gz(agg15,bar15_path); save_gz(native1h,native_path)
    audit.to_csv(OUT/"cross_resolution_audit.csv",index=False)
    coverage.to_csv(OUT/"coverage_15m.csv",index=False)
    samples.to_csv(OUT/"manual_samples.csv",index=False)

    summary={
        "status":"SI_PL_1M_15M_VALIDATION_"+validation_status,
        "source_identity":{
            "vendor":"Databento","dataset":DATASET,"stype_in":"continuous",
            "symbols":SYMBOLS,"raw_schema":"ohlcv-1m",
            "derived_schema":"15m deterministic UTC floor from 1m",
            "validation_schema":"native ohlcv-1h",
            "timestamp_semantics":"ts_event retained in UTC; OHLCV interval timestamp is interval start",
            "production_identity_rule":"A future live/replay implementation must keep the same dataset, continuous symbol identity, roll convention, timestamp semantics and completed-bar availability rule."
        },
        "preflight_cost":preflight,
        "raw_1m_rows":int(len(raw1m)),
        "derived_15m_rows":int(len(agg15)),
        "native_1h_rows":int(len(native1h)),
        "cross_resolution":audit.to_dict("records"),
        "mismatches":fail_cols,
        "files":{
            "raw_1m":{"name":raw_path.name,"sha256":sha256(raw_path),"bytes":raw_path.stat().st_size},
            "derived_15m":{"name":bar15_path.name,"sha256":sha256(bar15_path),"bytes":bar15_path.stat().st_size},
            "native_1h":{"name":native_path.name,"sha256":sha256(native_path),"bytes":native_path.stat().st_size},
        },
        "interpretation":[
            "Exact cross-vendor price equality is not required or expected when comparing spot XAG/XPT to COMEX SI/PL futures; they are different instruments.",
            "The binding integrity test is same-instrument, same-continuous-identity, same-vendor cross-resolution agreement: 1m aggregated to 1h versus native 1h.",
            "If this test fails, no 15m model experiment may proceed.",
            "If it passes, 15m bars are source-consistent with the production Databento identity, subject to the same completed-bar/PIT rules."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    if validation_status!="PASS":
        raise RuntimeError(f"CROSS_RESOLUTION_VALIDATION_FAIL:{fail_cols[:20]}")

    print(json.dumps({
        "status":summary["status"],
        "estimated_total_usd":total,
        "raw_1m_rows":len(raw1m),
        "derived_15m_rows":len(agg15),
        "native_1h_rows":len(native1h),
        "audit":audit.to_dict("records"),
        "files":summary["files"]
    },indent=2,default=str))

if __name__=="__main__":
    main()
