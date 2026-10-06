from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V2_PATH=AX/"tools"/"gold_session_structural_iris_crossmetal_v2_clocksafe_20261006.py"
V1_PATH=AX/"tools"/"gold_session_structural_iris_crossmetal_v1_20261006.py"
OUT=AX/"SESSION_CROSSMETAL_V3_EXACTCLOCK_OUT"; OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader is not None; s.loader.exec_module(m); return m

v2=loadmod("v2",V2_PATH)
v1=loadmod("v1",V1_PATH)

CORE3=list(v2.CORE3)
HORIZONS=[1,3,6,12,24,48]
MAX_LAG_MIN=120.0
EPS_MIN=1e-6

def attach_exact(panel,raw,tag):
    src=raw[["ts","available_at_utc","value"]].copy().sort_values("available_at_utc")
    src["value"]=pd.to_numeric(src["value"],errors="raise").astype(float)
    out=panel.copy().reset_index(drop=True)
    out["_rid"]=np.arange(len(out),dtype=int)

    ar=src.rename(columns={
        "ts":f"{tag}_anchor_bar_open",
        "available_at_utc":f"{tag}_anchor_available",
        "value":f"{tag}_anchor_value",
    })
    out=pd.merge_asof(
        out.sort_values("start_utc"),ar.sort_values(f"{tag}_anchor_available"),
        left_on="start_utc",right_on=f"{tag}_anchor_available",
        direction="backward",allow_exact_matches=False
    )
    out[f"{tag}_anchor_lag_min"]=(out["start_utc"]-out[f"{tag}_anchor_available"]).dt.total_seconds()/60.0

    feats=[]
    quality=[]
    for h in HORIZONS:
        cutoff_col=f"{tag}_ref_cutoff_{h}h"
        out[cutoff_col]=out["start_utc"]-pd.Timedelta(hours=h)
        rr=src.rename(columns={
            "ts":f"{tag}_ref_bar_open_{h}h",
            "available_at_utc":f"{tag}_ref_available_{h}h",
            "value":f"{tag}_ref_value_{h}h",
        })
        temp=out[["_rid",cutoff_col]].sort_values(cutoff_col)
        temp=pd.merge_asof(
            temp,rr.sort_values(f"{tag}_ref_available_{h}h"),
            left_on=cutoff_col,right_on=f"{tag}_ref_available_{h}h",
            direction="backward",allow_exact_matches=False
        )
        out=out.merge(temp.drop(columns=[cutoff_col]),on="_rid",how="left",validate="one_to_one")
        refa=f"{tag}_ref_available_{h}h"
        out[f"{tag}_ref_lag_{h}h_min"]=(out[cutoff_col]-out[refa]).dt.total_seconds()/60.0
        out[f"{tag}_span_{h}h_min"]=(out[f"{tag}_anchor_available"]-out[refa]).dt.total_seconds()/60.0
        out[f"{tag}_exact_{h}h"]=(out[f"{tag}_span_{h}h_min"]-60.0*h).abs()<=EPS_MIN
        feat=f"{tag}_ret_{h}h_clock"
        out[feat]=np.log(out[f"{tag}_anchor_value"].astype(float)/out[f"{tag}_ref_value_{h}h"].astype(float))
        feats.append(feat)

        q=out[[f"{tag}_exact_{h}h",f"{tag}_span_{h}h_min",f"{tag}_ref_lag_{h}h_min"]].dropna()
        quality.append({
            "source":tag,"horizon_h":h,
            "rows_with_reference":int(len(q)),
            "exact_span_rows":int(q[f"{tag}_exact_{h}h"].sum()) if len(q) else 0,
            "exact_span_rate":float(q[f"{tag}_exact_{h}h"].mean()) if len(q) else None,
            "median_span_min":float(q[f"{tag}_span_{h}h_min"].median()) if len(q) else None,
            "median_ref_lag_min":float(q[f"{tag}_ref_lag_{h}h_min"].median()) if len(q) else None,
        })

    valid=out[f"{tag}_anchor_available"].notna()
    if (out.loc[valid,f"{tag}_anchor_available"]>=out.loc[valid,"start_utc"]).any():
        raise RuntimeError(f"{tag}_ANCHOR_NOT_STRICT")
    return out.sort_values("_rid").drop(columns=["_rid"]).reset_index(drop=True),feats,quality

def retained_mask(q,tags):
    mask=pd.Series(True,index=q.index)
    for tag in tags:
        lag=q[f"{tag}_anchor_lag_min"]
        mask &= lag.gt(0)&lag.le(MAX_LAG_MIN)
        for h in HORIZONS:
            rlag=q[f"{tag}_ref_lag_{h}h_min"]
            mask &= rlag.gt(0)&rlag.le(MAX_LAG_MIN)&q[f"{tag}_exact_{h}h"].fillna(False)
            mask &= q[f"{tag}_ref_available_{h}h"] < q[f"{tag}_ref_cutoff_{h}h"]
            mask &= q[f"{tag}_ref_available_{h}h"] < q["start_utc"]
    return mask

def audit_samples(q,tags):
    picks=[]
    for (part,win),g in q.groupby(["partition","window"],sort=True):
        g=g.sort_values("start_utc")
        for r in pd.concat([g.head(2),g.tail(2)]).drop_duplicates("start_utc").itertuples(index=False):
            for tag in tags:
                row={
                    "label_date":r.label_date,"partition":part,"window":win,
                    "target_start_utc":r.start_utc.isoformat(),"source":tag,
                    "anchor_available_utc":getattr(r,f"{tag}_anchor_available").isoformat(),
                    "anchor_lag_min":float(getattr(r,f"{tag}_anchor_lag_min")),
                }
                for h in HORIZONS:
                    row[f"ref_{h}h_available_utc"]=getattr(r,f"{tag}_ref_available_{h}h").isoformat()
                    row[f"span_{h}h_min"]=float(getattr(r,f"{tag}_span_{h}h_min"))
                picks.append(row)
    return pd.DataFrame(picks)

def main():
    panel,hashes=v2.load_panel()
    clock=v2.audit_target_clocks(panel)

    xau=v1.load_xau_hourly()
    si=v1.load_si_hourly()
    pl,pl_meta=v1.fetch_pl_hourly()
    if pl is None: raise RuntimeError(f"PL_GATE_FAIL:{pl_meta}")

    quality=[]
    panel,gf,q=attach_exact(panel,xau,"g"); quality+=q
    panel,sif,q=attach_exact(panel,si,"si"); quality+=q
    panel,plf,q=attach_exact(panel,pl,"pl"); quality+=q

    mask=retained_mask(panel,["g","si","pl"])
    before=len(panel)
    panel=panel[mask].dropna(subset=CORE3+gf+sif+plf+["direction"]).copy()
    if panel.empty: raise RuntimeError("NO_EXACT_CLOCK_ROWS")

    for tag in ["g","si","pl"]:
        if not (panel[f"{tag}_anchor_available"]<panel["start_utc"]).all():
            raise RuntimeError(f"{tag}_ANCHOR_GATE_FAIL")
        for h in HORIZONS:
            if not panel[f"{tag}_exact_{h}h"].all():
                raise RuntimeError(f"{tag}_{h}H_SPAN_GATE_FAIL")

    variants={
        "CORE3_XAU_PATH_EXACTCLOCK":CORE3+gf,
        "CORE3_XAU_SI_PATH_EXACTCLOCK":CORE3+gf+sif,
        "CORE3_XAU_SI_PL_PATH_EXACTCLOCK":CORE3+gf+sif+plf,
    }
    preds=[]
    for name,feats in variants.items():
        z=v2.causal_replay(panel,name,feats)
        if not z.empty: preds.append(z)
    pred=pd.concat(preds,ignore_index=True)
    mdf=v2.summarize(pred)

    cov=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        cov.append({
            "partition":part,"window":win,"rows":int(len(g)),
            "first_start":g.start_utc.min().isoformat(),"last_start":g.start_utc.max().isoformat(),
            "median_g_anchor_lag_min":float(g.g_anchor_lag_min.median()),
            "median_si_anchor_lag_min":float(g.si_anchor_lag_min.median()),
            "median_pl_anchor_lag_min":float(g.pl_anchor_lag_min.median()),
        })
    cdf=pd.DataFrame(cov)
    qdf=pd.DataFrame(quality)
    samples=audit_samples(panel,["g","si","pl"])

    pred.to_csv(OUT/"predictions_2023_2024.csv",index=False)
    mdf.to_csv(OUT/"metrics_2023_2024.csv",index=False)
    cdf.to_csv(OUT/"coverage_2023_2024.csv",index=False)
    qdf.to_csv(OUT/"clock_quality.csv",index=False)
    samples.to_csv(OUT/"clock_samples.csv",index=False)

    summary={
        "status":"CROSSMETAL_V3_EXACTCLOCK_COMPLETE",
        "scope":"2023-2024 only; 2025/2026 unopened",
        "target_clock_audit":{"status":"PASS","rows":int(len(clock)),"timezone":"America/New_York"},
        "clock_policy":{
            "anchor":"latest completed hourly close with available_at STRICTLY LESS THAN target_start",
            "reference":"for each h, latest completed hourly close with available_at STRICTLY LESS THAN target_start-h",
            "retained_row_requirement":"anchor-to-reference available_at span must equal exactly h*60 minutes",
            "max_anchor_or_reference_lag_minutes":MAX_LAG_MIN,
            "exact_boundary_allowed":False,
            "session_ret_used":False,
        },
        "rows_before_exact_span_gate":int(before),
        "common_exact_clock_rows":int(len(panel)),
        "pl_gate":pl_meta,
        "daily_stak_hashes":hashes,
        "features":variants,
        "metrics":mdf.to_dict("records"),
        "guardrails":[
            "Frozen Sobti-5/WGC-3 target clocks asserted in America/New_York.",
            "No hourly bar completing at target start is used.",
            "Each PATH horizon is target-clock anchored; last-N-bar approximation is not used.",
            "Rows with non-exact anchor-to-reference clock span are rejected.",
            "Only matured same-window labels enter training.",
            "All variants use identical retained rows.",
            "2025/2026 remain unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# CROSS-METAL V3 — EXACT-CLOCK SESSION PATH","",
        "**Status:** CROSSMETAL_V3_EXACTCLOCK_COMPLETE","",
        "- Scope: 2023–2024 only; 2025/2026 unopened.",
        "- Hourly anchor is strictly before target start.",
        "- Every 1/3/6/12/24/48h reference is anchored to target_start-h.",
        "- Rows are retained only when anchor-reference elapsed time is exactly the requested horizon.",
        "- No NY-calendar session_ret feature.","",
        "## Metrics","",
        "| Model | Partition | Window | Period | N | Acc | Balanced | UP recall | DOWN recall | Brier |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in mdf.itertuples(index=False):
        lines.append(
            f"| {r.model} | {r.partition} | {r.window} | {r.period} | {int(r.n)} | "
            f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |"
        )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({
        "status":summary["status"],
        "target_clock_audit":summary["target_clock_audit"],
        "rows_before_exact_span_gate":before,
        "common_exact_clock_rows":len(panel),
        "pl_gate":pl_meta,
        "metric_rows":len(mdf),
    },indent=2,default=str))

if __name__=="__main__":
    main()
