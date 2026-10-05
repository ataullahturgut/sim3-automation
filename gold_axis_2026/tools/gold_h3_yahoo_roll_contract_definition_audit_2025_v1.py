from __future__ import annotations

import json, os
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
SW=AX/"GOLD_H3_YAHOO_ROLL_REVERSE_ENGINEERING_SWITCHES_2025_2026-10-05.csv"
OUTJ=AX/"GOLD_H3_YAHOO_ROLL_CONTRACT_DEFINITION_AUDIT_2025_2026-10-05.json"
OUTM=AX/"GOLD_H3_YAHOO_ROLL_CONTRACT_DEFINITION_AUDIT_2025_2026-10-05.md"
OUTC=AX/"GOLD_H3_YAHOO_ROLL_CONTRACT_DEFINITION_SWITCHES_2025_2026-10-05.csv"

DATASET="GLBX.MDP3"
PARENTS=["GC.FUT","SI.FUT","NQ.FUT","ZN.FUT","CL.FUT"]
ANCHORS=["2025-01-02","2025-04-01","2025-07-01","2025-10-01","2025-12-01"]
MAX_COST_USD=.50

def main():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)
    sw=pd.read_csv(SW)
    ids=set(sw.old_id.astype(int))|set(sw.new_id.astype(int))

    costs=[];defs=[]
    for a in ANCHORS:
        b=(pd.Timestamp(a)+pd.Timedelta(days=1)).date().isoformat()
        c=float(client.metadata.get_cost(dataset=DATASET,schema="definition",symbols=PARENTS,stype_in="parent",start=a,end=b))
        costs.append(c)
    total=float(sum(costs))
    if total>MAX_COST_USD:raise RuntimeError(f"COST_CAP:{total}>{MAX_COST_USD}")

    for a in ANCHORS:
        b=(pd.Timestamp(a)+pd.Timedelta(days=1)).date().isoformat()
        q=client.timeseries.get_range(dataset=DATASET,schema="definition",symbols=PARENTS,stype_in="parent",start=a,end=b).to_df().reset_index()
        if "ts_event" not in q.columns and "index" in q.columns:q=q.rename(columns={"index":"ts_event"})
        q["anchor"]=a
        q["instrument_id"]=pd.to_numeric(q.instrument_id,errors="coerce")
        q=q[q.instrument_id.isin(ids)].copy()
        keep=[c for c in ["anchor","instrument_id","raw_symbol","asset","instrument_class","expiration","activation","maturity_year","maturity_month"] if c in q.columns]
        defs.append(q[keep])
    d=pd.concat(defs,ignore_index=True) if defs else pd.DataFrame()
    if not d.empty:
        d=d.sort_values(["instrument_id","anchor"]).drop_duplicates("instrument_id",keep="last")

    mp={}
    for r in d.itertuples(index=False):
        iid=int(r.instrument_id)
        mp[iid]={
            "raw_symbol":str(getattr(r,"raw_symbol","")),
            "asset":str(getattr(r,"asset","")),
            "expiration":None if pd.isna(getattr(r,"expiration",np.nan)) else str(getattr(r,"expiration")),
            "activation":None if pd.isna(getattr(r,"activation",np.nan)) else str(getattr(r,"activation")),
            "maturity_year":None if not hasattr(r,"maturity_year") or pd.isna(r.maturity_year) else int(r.maturity_year),
            "maturity_month":None if not hasattr(r,"maturity_month") or pd.isna(r.maturity_month) else int(r.maturity_month),
        }

    rows=[]
    for r in sw.itertuples(index=False):
        o=mp.get(int(r.old_id),{});n=mp.get(int(r.new_id),{})
        sd=pd.Timestamp(r.date)
        oe=pd.to_datetime(o.get("expiration"),utc=True,errors="coerce")
        ne=pd.to_datetime(n.get("expiration"),utc=True,errors="coerce")
        rows.append({
            "root":r.root,"switch_date":r.date,"first_support_ts":r.first_support_ts,
            "old_id":int(r.old_id),"old_symbol":o.get("raw_symbol"),
            "old_expiration":None if pd.isna(oe) else oe.isoformat(),
            "days_to_old_expiry":None if pd.isna(oe) else int((oe.tz_convert(None).normalize()-sd.normalize()).days),
            "new_id":int(r.new_id),"new_symbol":n.get("raw_symbol"),
            "new_expiration":None if pd.isna(ne) else ne.isoformat(),
            "days_to_new_expiry":None if pd.isna(ne) else int((ne.tz_convert(None).normalize()-sd.normalize()).days),
            "matched_rolls":r.matched_rolls,"hour_share":float(r.hour_share)
        })
    outdf=pd.DataFrame(rows)
    outdf.to_csv(OUTC,index=False)

    summary={}
    for root,g in outdf.groupby("root"):
        vals=pd.to_numeric(g.days_to_old_expiry,errors="coerce").dropna()
        summary[root]={
            "switches":int(len(g)),
            "old_symbols":g.old_symbol.dropna().astype(str).tolist(),
            "new_symbols":g.new_symbol.dropna().astype(str).tolist(),
            "days_to_old_expiry":vals.astype(int).tolist(),
            "median_days_to_old_expiry":None if vals.empty else float(vals.median()),
            "min_days_to_old_expiry":None if vals.empty else int(vals.min()),
            "max_days_to_old_expiry":None if vals.empty else int(vals.max()),
        }

    out={"schema":"GOLD_H3_YAHOO_ROLL_CONTRACT_DEFINITION_AUDIT_2025_V1","date":"2026-10-05",
         "estimated_cost_usd":total,"cost_cap_usd":MAX_COST_USD,"anchors":ANCHORS,
         "mapped_instrument_ids":len(mp),"needed_instrument_ids":len(ids),
         "summary":summary,"status":"CONTRACT_DEFINITIONS_MAPPED" if len(mp)>=len(ids)*.8 else "CONTRACT_DEFINITION_MAPPING_PARTIAL",
         "raw_vendor_prices_committed":False,"outcome_labels_used":False}
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    lines=["# GOLD H3 — Yahoo Roll Contract Definition Audit (2025) — 2026-10-05","",
           f"**Status:** **{out['status']}**  ",f"Estimated Databento definition cost: **USD {total:.4f}**.","",
           f"Mapped instrument IDs: **{len(mp)}/{len(ids)}**.","",
           "## Switches with actual contracts","",
           "| Root | Switch | Old contract | Old expiry | Days before old expiry | New contract | New expiry |",
           "|---|---|---|---|---:|---|---|"]
    for r in outdf.itertuples(index=False):
        lines.append(f"| {r.root} | {r.switch_date} | {r.old_symbol or '—'} | {r.old_expiration or '—'} | {r.days_to_old_expiry if pd.notna(r.days_to_old_expiry) else '—'} | {r.new_symbol or '—'} | {r.new_expiration or '—'} |")
    lines += ["","## Product-level expiry distance","",
              "| Root | Switches | Median days before old expiry | Range |",
              "|---|---:|---:|---|"]
    for root,s in summary.items():
        lines.append(f"| {root} | {s['switches']} | {s['median_days_to_old_expiry'] if s['median_days_to_old_expiry'] is not None else '—'} | {s['min_days_to_old_expiry']}..{s['max_days_to_old_expiry']} |")
    lines += ["","## Interpretation","",
              "- Stable expiry-distance by product would support a portable calendar roll emulator.",
              "- Commodity products may roll before exchange expiration because delivery/first-notice conventions matter; therefore raw-symbol month sequence is also reported.",
              "- No controller outcomes are used."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":main()
