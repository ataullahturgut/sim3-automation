from __future__ import annotations

import io
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUTJ=AX/"GOLD_H3_YAHOO_ROLL_REVERSE_ENGINEERING_2025_2026-10-05.json"
OUTM=AX/"GOLD_H3_YAHOO_ROLL_REVERSE_ENGINEERING_2025_2026-10-05.md"
OUTC=AX/"GOLD_H3_YAHOO_ROLL_REVERSE_ENGINEERING_SWITCHES_2025_2026-10-05.csv"

DATASET="GLBX.MDP3"
SCHEMA="ohlcv-1h"
ROOTS=["GC","SI","NQ","ZN","CL"]
ROLLS=["c","n","v"]
START="2025-01-02"
END="2026-01-01"
MAX_COST_USD=1.00
CONFIDENT_BPS=3.0

FROZEN_REF="origin/gold-h3-llrs-v1-20261004"
FROZEN_PATH="gold_axis_2026/GOLD_H3_LLRS_V1_HOURLY_PANEL_2026-10-04.csv"

def load_yahoo():
    raw=subprocess.check_output(["git","show",f"{FROZEN_REF}:{FROZEN_PATH}"],text=True)
    d=pd.read_csv(io.StringIO(raw))
    d["ts"]=pd.to_datetime(d["ts"],utc=True)
    d=d[(d.ts>=pd.Timestamp(START,tz="UTC"))&(d.ts<pd.Timestamp(END,tz="UTC"))].copy()
    return d.sort_values("ts").drop_duplicates("ts")

def fetch_groups():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key: raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)
    costs={}
    for roll in ROLLS:
        syms=[f"{r}.{roll}.0" for r in ROOTS]
        costs[roll]=float(client.metadata.get_cost(
            dataset=DATASET,schema=SCHEMA,symbols=syms,stype_in="continuous",start=START,end=END))
    total=float(sum(costs.values()))
    if total>MAX_COST_USD:
        raise RuntimeError(f"ESTIMATED_COST_EXCEEDS_CAP:{total:.6f}>{MAX_COST_USD:.2f}")
    groups={}
    for roll in ROLLS:
        syms=[f"{r}.{roll}.0" for r in ROOTS]
        data=client.timeseries.get_range(
            dataset=DATASET,schema=SCHEMA,symbols=syms,stype_in="continuous",start=START,end=END)
        q=data.to_df().reset_index()
        if "ts_event" not in q.columns and "index" in q.columns:
            q=q.rename(columns={"index":"ts_event"})
        q["ts"]=pd.to_datetime(q["ts_event"],utc=True)
        q["symbol"]=q["symbol"].astype(str)
        q["close"]=pd.to_numeric(q["close"],errors="coerce")
        q=q[np.isfinite(q.close)&(q.close>0)].copy()
        groups[roll]=q[["ts","symbol","instrument_id","close"]]
    return client,groups,costs,total

def infer_root(root,yahoo,groups):
    y=yahoo[["ts",root]].rename(columns={root:"yahoo"}).dropna().copy()
    z=y.copy()
    for roll in ROLLS:
        sym=f"{root}.{roll}.0"
        q=groups[roll][groups[roll].symbol==sym][["ts","instrument_id","close"]].copy()
        q=q.rename(columns={"instrument_id":f"id_{roll}","close":f"px_{roll}"})
        z=z.merge(q,on="ts",how="left")
    rows=[]
    for r in z.itertuples(index=False):
        candidates={}
        for roll in ROLLS:
            iid=getattr(r,f"id_{roll}",np.nan)
            px=getattr(r,f"px_{roll}",np.nan)
            if pd.isna(iid) or pd.isna(px): continue
            iid=int(iid);px=float(px)
            err=abs(np.log(px/float(r.yahoo)))*10000.0
            prev=candidates.get(iid)
            if prev is None or err<prev["err_bps"]:
                candidates[iid]={"id":iid,"err_bps":err,"aliases":[roll]}
            elif abs(err-prev["err_bps"])<1e-12:
                prev["aliases"].append(roll)
        if not candidates: continue
        vals=sorted(candidates.values(),key=lambda x:(x["err_bps"],x["id"]))
        best=vals[0]
        second=vals[1]["err_bps"] if len(vals)>1 else np.nan
        rows.append({
            "ts":r.ts,"root":root,"best_id":best["id"],"best_err_bps":best["err_bps"],
            "gap_bps":np.nan if not np.isfinite(second) else second-best["err_bps"],
            "best_aliases":"".join(sorted(best["aliases"])),
            "confident":bool(best["err_bps"]<=CONFIDENT_BPS),
            **{f"id_{roll}":None if pd.isna(getattr(r,f"id_{roll}",np.nan)) else int(getattr(r,f"id_{roll}")) for roll in ROLLS}
        })
    h=pd.DataFrame(rows)
    if h.empty: return h,pd.DataFrame(),{}
    h["et_date"]=h.ts.dt.tz_convert("America/New_York").dt.date.astype(str)

    # Daily Yahoo-implied actual contract = majority best instrument among confident hours.
    daily=[]
    for day,g in h.groupby("et_date",sort=True):
        c=g[g.confident].copy()
        if c.empty: c=g.copy()
        vc=c.best_id.value_counts()
        bid=int(vc.index[0])
        share=float(vc.iloc[0]/len(c))
        aliases=[]
        for roll in ROLLS:
            vals=g[f"id_{roll}"].dropna().astype(int)
            if len(vals) and float((vals==bid).mean())>=0.5:
                aliases.append(roll)
        daily.append({
            "root":root,"date":day,"yahoo_implied_id":bid,"hour_share":share,
            "confident_hours":int(g.confident.sum()),"hours":int(len(g)),
            "matched_rolls":"".join(aliases)
        })
    d=pd.DataFrame(daily)

    # Remove isolated one-day reversions A-B-A when B has weak majority.
    ids=d.yahoo_implied_id.to_list()
    shares=d.hour_share.to_list()
    for i in range(1,len(ids)-1):
        if ids[i-1]==ids[i+1] and ids[i]!=ids[i-1] and shares[i]<0.75:
            ids[i]=ids[i-1]
    d["smoothed_id"]=ids

    switches=[]
    prev=None
    for i,r in d.iterrows():
        if prev is None:
            prev=int(r.smoothed_id);continue
        cur=int(r.smoothed_id)
        if cur!=prev:
            day=r["date"]
            # First confident hourly observation that supports new contract on switch date.
            g=h[h.et_date==day].copy()
            cand=g[(g.best_id==cur)&g.confident].sort_values("ts")
            first_ts=None if cand.empty else cand.ts.iloc[0]
            switches.append({
                "root":root,"date":day,"first_support_ts":None if first_ts is None else str(first_ts),
                "old_id":prev,"new_id":cur,"matched_rolls":r.matched_rolls,
                "hour_share":float(r.hour_share)
            })
            prev=cur
    sw=pd.DataFrame(switches)

    stats={
        "hours":int(len(h)),
        "confident_hours":int(h.confident.sum()),
        "confident_share":float(h.confident.mean()),
        "median_best_err_bps":float(h.best_err_bps.median()),
        "p95_best_err_bps":float(h.best_err_bps.quantile(.95)),
        "daily_days":int(len(d)),
        "switches":int(len(sw)),
        "days_matching_c":int(d.matched_rolls.str.contains("c").sum()),
        "days_matching_n":int(d.matched_rolls.str.contains("n").sum()),
        "days_matching_v":int(d.matched_rolls.str.contains("v").sum()),
    }
    return h,sw,stats

def resolve_ids(client,ids):
    if not ids:return {}
    try:
        rr=client.symbology.resolve(
            dataset=DATASET,symbols=[str(x) for x in sorted(ids)],
            stype_in="instrument_id",stype_out="raw_symbol",
            start_date=START,end_date=END
        )
        payload=rr.to_dict() if hasattr(rr,"to_dict") else getattr(rr,"__dict__",{})
        result=payload.get("result",{}) if isinstance(payload,dict) else {}
        out={}
        for k,entries in result.items():
            vals=[]
            for e in entries or []:
                if isinstance(e,dict):
                    vals.append({"d0":str(e.get("d0")),"d1":str(e.get("d1")),"s":str(e.get("s"))})
                else:
                    vals.append(str(e))
            out[str(k)]=vals
        return out
    except Exception as e:
        return {"_error":repr(e)}

def main():
    yahoo=load_yahoo()
    client,groups,costs,total=fetch_groups()
    all_switches=[];stats={};allids=set()
    for root in ROOTS:
        _,sw,st=infer_root(root,yahoo,groups)
        stats[root]=st
        if not sw.empty:
            all_switches.append(sw)
            allids.update(sw.old_id.astype(int).tolist())
            allids.update(sw.new_id.astype(int).tolist())
    switches=pd.concat(all_switches,ignore_index=True) if all_switches else pd.DataFrame()
    if not switches.empty:switches.to_csv(OUTC,index=False)
    else:pd.DataFrame().to_csv(OUTC,index=False)
    raw_symbols=resolve_ids(client,allids)

    out={
        "schema":"GOLD_H3_YAHOO_ROLL_REVERSE_ENGINEERING_2025_V1",
        "date":"2026-10-05","window":[START,END],
        "estimated_cost_usd":total,"cost_by_roll_usd":costs,"cost_cap_usd":MAX_COST_USD,
        "confidence_threshold_bps":CONFIDENT_BPS,
        "stats":stats,
        "switch_count_total":int(len(switches)),
        "switches":switches.to_dict("records") if len(switches) else [],
        "instrument_id_to_raw_symbol":raw_symbols,
        "raw_vendor_prices_committed":False,
        "outcome_labels_used":False,
        "thresholds_retuned":False,
        "status":"YAHOO_ROLL_SWITCHES_INFERRED" if len(switches) else "ROLL_INFERENCE_FAILED"
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    lines=[
        "# GOLD H3 — Yahoo Roll Reverse Engineering (2025) — 2026-10-05","",
        f"**Status:** **{out['status']}**  ",
        f"Estimated Databento cost: **USD {total:.4f}** (cap USD {MAX_COST_USD:.2f}).  ",
        "**No model outcome labels are used. Yahoo active contract is inferred only from price identity against Databento c/n/v underlying instruments.**","",
        "## Contract-identity quality","",
        "| Root | Hours | Confident | Confident % | Median best error bps | P95 error bps | Switches | Days match c | n | v |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for root in ROOTS:
        s=stats[root]
        lines.append(f"| {root} | {s['hours']} | {s['confident_hours']} | {100*s['confident_share']:.2f}% | {s['median_best_err_bps']:.4f} | {s['p95_best_err_bps']:.4f} | {s['switches']} | {s['days_matching_c']} | {s['days_matching_n']} | {s['days_matching_v']} |")
    lines += ["","## Inferred Yahoo contract switches","",
              "| Root | Date | First supporting hour UTC | Old ID | New ID | New contract matches Databento roll(s) | Daily support |",
              "|---|---|---|---:|---:|---|---:|"]
    if len(switches):
        for r in switches.itertuples():
            lines.append(f"| {r.root} | {r.date} | {r.first_support_ts or '—'} | {r.old_id} | {r.new_id} | {r.matched_rolls or 'none'} | {100*r.hour_share:.1f}% |")
    lines += ["","## Interpretation","",
              "- If Yahoo switch dates consistently line up with one portable market rule (volume, open interest, calendar, or a stable lag/lead from one of them), that rule can be frozen and applied to 2023–2024.",
              "- If Yahoo switches use inconsistent vendor-specific stitching, exact emulation is not identifiable from standard continuous rules alone; then 2023–2024 must remain a source-bridged reconstruction.",
              "- Raw Databento prices are not committed."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
