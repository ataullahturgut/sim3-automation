from __future__ import annotations

import json, math
from pathlib import Path
import numpy as np
import pandas as pd
import requests

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

H3=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_HOURLY=AX/"GOLD_H3_LLRS_V1_HOURLY_PANEL_2026-10-04.csv"
OUT_ORIGIN=AX/"GOLD_H3_LLRS_V1_ORIGIN_SCORES_2026-10-04.csv"
OUT_GRID=AX/"GOLD_H3_LLRS_V1_THRESHOLD_GRID_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_LLRS_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_LLRS_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_LLRS_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_LLRS_V1_PROSPECTIVE_FREEZE_2026-10-04.json"

SYMS={"GC":"GC=F","ZN":"ZN=F","NQ":"NQ=F","SI":"SI=F","CL":"CL=F"}
START=pd.Timestamp("2025-01-01",tz="UTC")
END=pd.Timestamp("2026-10-04",tz="UTC")
WINDOW_DAYS=60
MIN_TRAIN=500
ALPHA=10.0
QGRID=[0.25,0.50,0.75,1.00]
SEED=20261004

EXT_FEATURES=[
    "ZN_r1","ZN_r3","ZN_r6",
    "NQ_r1","NQ_r3","NQ_r6",
    "SI_r1","SI_r3","SI_r6",
    "CL_r1","CL_r3","CL_r6",
]
GC_FEATURES=["GC_r1","GC_r3","GC_r6"]

SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def fetch(sym):
    p1=int(START.timestamp()); p2=int(END.timestamp())
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(sym,safe='')}"
        params={"period1":p1,"period2":p2,"interval":"1h","events":"history","includeAdjustedClose":"true"}
        try:
            r=SESSION.get(url,params=params,timeout=60)
            if r.status_code!=200:
                last=f"{host} HTTP {r.status_code}: {r.text[:200]}"
                continue
            j=r.json()["chart"]
            if j.get("error") or not j.get("result"):
                last=f"{host} chart_error={j.get('error')}"
                continue
            z=j["result"][0]
            ts=z.get("timestamp",[])
            close=z["indicators"]["quote"][0].get("close",[])
            rows=[]
            for t,c in zip(ts,close):
                if c is None: continue
                v=float(c)
                if not np.isfinite(v) or v<=0: continue
                rows.append((pd.to_datetime(t,unit="s",utc=True),v))
            if len(rows)<3000:
                last=f"{host} too few rows={len(rows)}"
                continue
            return pd.DataFrame(rows,columns=["ts",sym]).drop_duplicates("ts").sort_values("ts")
        except Exception as e:
            last=f"{host}: {type(e).__name__}: {e}"
    raise RuntimeError(f"FETCH_FAIL {sym}: {last}")

def build_hourly():
    merged=None
    counts={}
    for name,sym in SYMS.items():
        d=fetch(sym).rename(columns={sym:name})
        counts[name]=len(d)
        merged=d if merged is None else merged.merge(d,on="ts",how="inner")
    x=merged.sort_values("ts").reset_index(drop=True)
    for name in SYMS:
        lv=np.log(x[name].astype(float))
        for h in [1,3,6]:
            x[f"{name}_r{h}"]=lv-lv.shift(h)

    # Forward 6 synchronized trading-hour bars, but reject large wall-clock gaps.
    x["target_ts_6h"]=x.ts.shift(-6)
    x["GC_fwd6"]=np.log(x.GC.shift(-6))-np.log(x.GC)
    wall=(x.target_ts_6h-x.ts).dt.total_seconds()/3600.0
    x.loc[(wall<5.0)|(wall>8.5),"GC_fwd6"]=np.nan
    x["target_wall_hours"]=wall
    return x,counts

def ridge():
    return Pipeline([
        ("scale",StandardScaler()),
        ("ridge",Ridge(alpha=ALPHA))
    ])

def cutoff_ts(d):
    # Conservative last usable timestamp: 16:00 New York, one hour before 17:00 reference.
    return pd.Timestamp(d.date()).tz_localize("America/New_York")+pd.Timedelta(hours=16)

def block_name(ts):
    t=pd.Timestamp(ts)
    return f"{t.year}_{'H1' if t.month<=6 else 'H2'}"

def origin_scores(hourly):
    h3=pd.read_csv(H3)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        h3[c]=pd.to_datetime(h3[c])
    h3=h3[h3.eligible_v5_continuation.astype(bool)].copy()
    h3=h3[h3.forecast_issue_date>=pd.Timestamp("2025-01-01")].sort_values("forecast_issue_date")

    feature_cols=EXT_FEATURES+GC_FEATURES+["GC_fwd6","target_ts_6h"]
    ready=hourly.dropna(subset=feature_cols).copy()
    rows=[]

    for r in h3.itertuples():
        co=cutoff_ts(pd.Timestamp(r.feature_cutoff_date))
        co_utc=co.tz_convert("UTC")
        hist=ready[
            (ready.ts>=co_utc-pd.Timedelta(days=WINDOW_DAYS))
            & (ready.target_ts_6h<co_utc)
        ].copy()
        if len(hist)<MIN_TRAIN:
            continue

        cur=hourly[hourly.ts<=co_utc].tail(1).copy()
        if cur.empty or cur[EXT_FEATURES+GC_FEATURES].isna().any(axis=None):
            continue

        # freshness: last synchronized hourly bar may be at most 3h old.
        stale_h=(co_utc-cur.ts.iloc[0]).total_seconds()/3600.0
        if stale_h<0 or stale_h>3.0:
            continue

        me=ridge(); mg=ridge()
        Xext=hist[EXT_FEATURES].to_numpy(float)
        Xgc=hist[GC_FEATURES].to_numpy(float)
        y=hist.GC_fwd6.to_numpy(float)
        me.fit(Xext,y); mg.fit(Xgc,y)

        pred_ext=float(me.predict(cur[EXT_FEATURES].to_numpy(float))[0])
        pred_gc=float(mg.predict(cur[GC_FEATURES].to_numpy(float))[0])
        resid=y-me.predict(Xext)
        sigma=float(np.std(resid,ddof=1))
        if not np.isfinite(sigma) or sigma<=1e-9:
            continue

        s=1.0 if int(r.momentum_up)==1 else -1.0
        pressure=float(-s*pred_ext/sigma)
        incremental=float(-s*(pred_ext-pred_gc)/sigma)
        opp=bool(s*pred_ext<0)

        d={
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),"month":str(r.month),
            "y_up":int(r.y_up),"target_r3":float(r.target_r3),
            "momentum_up":int(r.momentum_up),
            "v5_pred":int(r.v5_pred),
            "rescue_target":int(r.rescue_target),
            "opal_override_check":r.opal_override_check,
            "hourly_cutoff":co_utc,
            "hourly_source_ts":cur.ts.iloc[0],
            "hourly_stale_h":float(stale_h),
            "hourly_train_n":int(len(hist)),
            "pred_ext_6h":pred_ext,
            "pred_gc_6h":pred_gc,
            "lead_delta":pred_ext-pred_gc,
            "ext_resid_sigma":sigma,
            "llrs_pressure":pressure,
            "llrs_incremental":incremental,
            "llrs_external_opposes":opp,
        }
        rows.append(d)
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def smd(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if len(a)<2 or len(b)<2: return np.nan
    sp=np.sqrt((np.var(a,ddof=1)+np.var(b,ddof=1))/2)
    return float((np.mean(a)-np.mean(b))/sp) if sp>1e-12 else np.nan

def mechanism_blocks(z):
    out=[]
    z=z.copy(); z["block"]=z.forecast_issue_date.map(block_name)
    for name,g in z.groupby("block",sort=False):
        r=g[g.rescue_target==1]; c=g[g.rescue_target==0]
        if g.rescue_target.nunique()==2:
            try: auc=float(roc_auc_score(g.rescue_target,g.llrs_pressure))
            except: auc=np.nan
        else: auc=np.nan
        out.append({
            "block":name,"n":len(g),"reversal_n":int(g.rescue_target.sum()),
            "reversal_pressure_median":float(r.llrs_pressure.median()) if len(r) else np.nan,
            "continuation_pressure_median":float(c.llrs_pressure.median()) if len(c) else np.nan,
            "pressure_smd":smd(r.llrs_pressure,c.llrs_pressure),
            "pressure_auc":auc,
            "incremental_smd":smd(r.llrs_incremental,c.llrs_incremental)
        })
    return out

def candidate_mask(z,q):
    return z.llrs_external_opposes.astype(bool)&(z.llrs_incremental>0)&(z.llrs_pressure>=q)

def metrics(z,q):
    c=candidate_mask(z,q)
    y=z.rescue_target.astype(bool)
    resc=int((c&y).sum()); broken=int((c&~y).sum()); n=int(c.sum())
    return {
        "q":float(q),"eligible_n":len(z),"candidate_n":n,
        "rescued":resc,"broken":broken,"net_rescue":resc-broken,
        "precision":resc/max(n,1),
        "recall":resc/max(int(y.sum()),1),
        "candidate_rate":n/max(len(z),1)
    }

def policy_blocks(z,q):
    zz=z.copy(); zz["block"]=zz.forecast_issue_date.map(block_name)
    out=[]
    for name,g in zz.groupby("block",sort=False):
        m=metrics(g,q)
        out.append({"block":name,**m})
    return out

def prospective_snapshot(hourly,origin,selected):
    last=hourly.ts.max()
    return {
        "schema":"LLRS_H3_V1_PROSPECTIVE_FREEZE",
        "freeze_date":"2026-10-04",
        "first_clean_origin":"2026-10-05",
        "historical_status":"development_only",
        "selected_q":selected,
        "channels":SYMS,
        "hourly_rows":int(len(hourly)),
        "hourly_first":str(hourly.ts.min()),
        "hourly_last":str(last),
        "origin_score_rows":int(len(origin)),
        "constants":{
            "window_days":WINDOW_DAYS,
            "min_train":MIN_TRAIN,
            "ridge_alpha":ALPHA,
            "target_horizon_trading_hours":6,
            "origin_last_allowed_bar_et":"16:00",
            "q_grid":QGRID
        }
    }

def main():
    hourly,counts=build_hourly()
    # Store only synchronized columns and derived returns, not raw provider metadata.
    hourly.to_csv(OUT_HOURLY,index=False)
    z=origin_scores(hourly)
    z.to_csv(OUT_ORIGIN,index=False)

    mechanism=mechanism_blocks(z)

    grid=[]
    all_blocks=[]
    for q in QGRID:
        agg=metrics(z,q)
        blocks=policy_blocks(z,q)
        positive=sum(1 for b in blocks if b["net_rescue"]>0)
        minnet=min([b["net_rescue"] for b in blocks],default=0)
        agg["positive_blocks"]=positive
        agg["min_block_net"]=minnet
        agg["eligible"]=bool(
            agg["candidate_n"]>=10
            and agg["net_rescue"]>0
            and agg["precision"]>=.55
            and positive>=2
            and minnet>=-2
        )
        grid.append(agg)
        all_blocks.extend(blocks)

    gdf=pd.DataFrame(grid); bdf=pd.DataFrame(all_blocks)
    gdf.to_csv(OUT_GRID,index=False); bdf.to_csv(OUT_BLOCK,index=False)

    elig=gdf[gdf.eligible].copy()
    selected=None
    if elig.empty:
        status="NO_ELIGIBLE_LLRS_V1_MECHANISM"
    else:
        elig=elig.sort_values(
            ["net_rescue","precision","rescued","candidate_n","q"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].q)
        status="LLRS_V1_MECHANISM_PASS_PROSPECTIVE_SHADOW"

    freeze=prospective_snapshot(hourly,z,selected)
    OUT_FREEZE.write_text(json.dumps(freeze,indent=2,default=str)+"\n")

    summary={
        "schema":"LLRS_H3_V1","status":status,
        "source_counts":counts,
        "origin_rows":len(z),
        "mechanism_blocks":mechanism,
        "threshold_grid":grid,
        "selected_q":selected,
        "prospective_freeze":freeze
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# LLRS-H3 V1 — LEAD-LAG REPRICING STRESS RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective hourly-futures proxy mechanism; not a clean historical holdout.","",
        "## Hourly synchronized coverage","",
        f"- synchronized rows: **{len(hourly)}**",
        f"- first / last UTC: **{hourly.ts.min()} / {hourly.ts.max()}**",
        f"- H3 origins scored: **{len(z)}**","",
        "## Mechanism anatomy","",
        "| Block | n | Reversals | Reversal pressure med | Continuation med | Pressure SMD | AUC | Incremental SMD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for x in mechanism:
        lines.append(
            f"| {x['block']} | {x['n']} | {x['reversal_n']} | "
            f"{x['reversal_pressure_median']:.3f} | {x['continuation_pressure_median']:.3f} | "
            f"{x['pressure_smd']:+.3f} | {x['pressure_auc']:.3f} | {x['incremental_smd']:+.3f} |"
        )

    lines += ["","## Frozen candidate grid","",
              "| q | Cand | Rescue | Broken | Net | Precision | Recall | Rate | + blocks | Worst | Eligible |",
              "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for x in grid:
        lines.append(
            f"| {x['q']:.2f} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net_rescue']:+d} | "
            f"{100*x['precision']:.2f}% | {100*x['recall']:.2f}% | {100*x['candidate_rate']:.2f}% | "
            f"{x['positive_blocks']} | {x['min_block_net']:+d} | {x['eligible']} |"
        )

    if selected is not None:
        sel=bdf[np.isclose(bdf.q,selected)]
        lines += ["",f"## Selected development q: {selected:.2f}","",
                  "| Block | Cand | Rescue | Broken | Net | Precision | Recall |",
                  "|---|---:|---:|---:|---:|---:|---:|"]
        for r in sel.itertuples():
            lines.append(f"| {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.precision:.2f}% | {100*r.recall:.2f}% |")

    lines += ["","## Governance","",
              "Historical 2025-2026 is development/stress-test evidence. A successful mechanism may only become a shadow prospective challenger from the post-freeze period. "
              "Yahoo hourly futures are research proxies; production use requires an authoritative prospective source."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
