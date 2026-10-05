from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m

inv=loadmod("inv2025",AX/"tools"/"gold_h3_databento_downstream_invariance_2025_v1.py")
base=inv.base

OUTJ=AX/"GOLD_H3_DATABENTO_CONSENSUS_ROLL_BRIDGE_2025_2026-10-05.json"
OUTM=AX/"GOLD_H3_DATABENTO_CONSENSUS_ROLL_BRIDGE_2025_2026-10-05.md"
OUTC=AX/"GOLD_H3_DATABENTO_CONSENSUS_ROLL_ORIGIN_COMPARE_2025_2026-10-05.csv"

DATASET="GLBX.MDP3";SCHEMA="ohlcv-1h"
ROOTS=["GC","SI","NQ","ZN","CL"];ROLLS=["c","n","v"]
START="2024-10-10";END="2026-10-04";MAX_COST_USD=1.70
YSTART=pd.Timestamp("2025-01-02",tz="UTC");YEND=pd.Timestamp("2026-01-01",tz="UTC")
FROZEN_REF="origin/gold-h3-llrs-v1-20261004"
FROZEN_PATH="gold_axis_2026/GOLD_H3_LLRS_V1_HOURLY_PANEL_2026-10-04.csv"
OLD_IFBC=AX/"GOLD_H3_2025_BACKFILL_IFBC_EXTENDED_2026-10-05.csv"
OLD_LLRS=AX/"GOLD_H3_2025_BACKFILL_LLRS_EXTENDED_2026-10-05.csv"
OLD_STATE=AX/"GOLD_H3_2025_BACKFILL_HANDOFF_STATE_2026-10-05.csv"
OLD_ACT=AX/"GOLD_H3_2025_BACKFILL_DPTC_ACTIONS_2026-10-05.csv"

def yahoo():
    raw=subprocess.check_output(["git","show",f"{FROZEN_REF}:{FROZEN_PATH}"],text=True)
    d=pd.read_csv(io.StringIO(raw));d["ts"]=pd.to_datetime(d["ts"],utc=True)
    return d[(d.ts>=YSTART)&(d.ts<YEND)].copy()

def fetch():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key);costs={}
    for roll in ROLLS:
        syms=[f"{r}.{roll}.0" for r in ROOTS]
        costs[roll]=float(client.metadata.get_cost(dataset=DATASET,schema=SCHEMA,symbols=syms,stype_in="continuous",start=START,end=END))
    total=sum(costs.values())
    if total>MAX_COST_USD:raise RuntimeError(f"COST_CAP:{total}>{MAX_COST_USD}")
    groups={}
    for roll in ROLLS:
        syms=[f"{r}.{roll}.0" for r in ROOTS]
        q=client.timeseries.get_range(dataset=DATASET,schema=SCHEMA,symbols=syms,stype_in="continuous",start=START,end=END).to_df().reset_index()
        if "ts_event" not in q.columns and "index" in q.columns:q=q.rename(columns={"index":"ts_event"})
        q["ts"]=pd.to_datetime(q.ts_event,utc=True);q["symbol"]=q.symbol.astype(str)
        q["close"]=pd.to_numeric(q.close,errors="coerce");q["volume"]=pd.to_numeric(q.volume,errors="coerce")
        q=q[np.isfinite(q.close)&(q.close>0)].copy()
        groups[roll]=q[["ts","symbol","instrument_id","close","volume"]]
    return groups,costs,float(total)

def merged_root(root,groups):
    z=None
    for roll in ROLLS:
        sym=f"{root}.{roll}.0"
        q=groups[roll][groups[roll].symbol==sym][["ts","instrument_id","close","volume"]].copy()
        q=q.rename(columns={"instrument_id":f"id_{roll}","close":f"px_{roll}","volume":f"vol_{roll}"})
        z=q if z is None else z.merge(q,on="ts",how="outer")
    return z.sort_values("ts").drop_duplicates("ts")

def learn_tiebreak(root,z,y):
    q=y[["ts",root]].rename(columns={root:"y"}).merge(z,on="ts",how="inner").dropna(subset=["y"])
    votes={r:0 for r in ROLLS};n=0
    for row in q.itertuples(index=False):
        ids=[getattr(row,f"id_{r}") for r in ROLLS]
        valid=[int(x) for x in ids if not pd.isna(x)]
        if len(valid)<2:continue
        counts=pd.Series(valid).value_counts()
        if counts.iloc[0]>=2:continue
        errs={}
        for r in ROLLS:
            px=getattr(row,f"px_{r}")
            if pd.isna(px):continue
            errs[r]=abs(np.log(float(px)/float(row.y)))*10000
        if not errs:continue
        win=min(errs,key=errs.get);votes[win]+=1;n+=1
    priority=sorted(ROLLS,key=lambda r:(-votes[r],ROLLS.index(r)))
    return priority,{"tie_hours":n,"wins":votes,"priority":priority}

def choose_series(root,z,priority):
    rows=[]
    for row in z.itertuples(index=False):
        by_id={}
        for roll in ROLLS:
            iid=getattr(row,f"id_{roll}")
            px=getattr(row,f"px_{roll}");vol=getattr(row,f"vol_{roll}")
            if pd.isna(iid) or pd.isna(px):continue
            iid=int(iid)
            by_id.setdefault(iid,[]).append(roll)
        if not by_id:continue
        counts=sorted(((len(v),iid,v) for iid,v in by_id.items()),reverse=True)
        if counts[0][0]>=2:
            selected_id=counts[0][1]
            aliases=by_id[selected_id]
            source=next((r for r in priority if r in aliases),aliases[0])
            mode="majority"
        else:
            source=next((r for r in priority if not pd.isna(getattr(row,f"id_{r}"))),None)
            if source is None:continue
            selected_id=int(getattr(row,f"id_{source}"));aliases=[source];mode="tie"
        rows.append({
            "ts":row.ts,"root":root,"instrument_id":selected_id,
            "close":float(getattr(row,f"px_{source}")),
            "volume":float(getattr(row,f"vol_{source}")) if not pd.isna(getattr(row,f"vol_{source}")) else 0.0,
            "source_alias":source,"selection_mode":mode,
        })
    return pd.DataFrame(rows)

def identity_stats(root,selected,y):
    q=y[["ts",root]].rename(columns={root:"y"}).merge(selected[["ts","close","selection_mode"]],on="ts",how="inner")
    err=np.abs(np.log(q.close.astype(float)/q.y.astype(float)))*10000
    return {
        "n":int(len(q)),"median_bps":float(err.median()),"p95_bps":float(err.quantile(.95)),
        "share_le_0_1bps":float((err<=0.1).mean()),"share_le_1bps":float((err<=1.0).mean()),
        "tie_share":float((q.selection_mode=="tie").mean()),
    }

def setstats(a,b):
    a=set(pd.to_datetime(list(a)));b=set(pd.to_datetime(list(b)));u=a|b;i=a&b
    return {"new_n":len(a),"old_n":len(b),"matched":len(i),"jaccard":1.0 if not u else len(i)/len(u),
            "added":[x.date().isoformat() for x in sorted(a-b)],"missing":[x.date().isoformat() for x in sorted(b-a)]}

def main():
    groups,costs,total=fetch();y=yahoo();priorities={};pstats={};selected=[];idstats={}
    for root in ROOTS:
        z=merged_root(root,groups)
        pr,ps=learn_tiebreak(root,z,y);priorities[root]=pr;pstats[root]=ps
        s=choose_series(root,z,pr);selected.append(s);idstats[root]=identity_stats(root,s,y)
    d=pd.concat(selected,ignore_index=True)

    h3=inv.prep_h3()
    vast=inv.build_vast_from_db(d,h3)
    ifbc=base.build_ifbc_scores(vast)
    raw=d.pivot_table(index="ts",columns="root",values="close",aggfunc="last").reset_index()
    raw=raw.dropna(subset=ROOTS).sort_values("ts").reset_index(drop=True)
    hourly=base.llrs_prepare_hourly(raw[["ts","GC","ZN","NQ","SI","CL"]])
    llrs=base.llrs_origin_scores(hourly,h3,"2024-12-01")
    state=base.build_handoff_scores(ifbc,llrs)
    zdec=inv.make_decision_panel(h3,state)

    oldi=pd.read_csv(OLD_IFBC,parse_dates=["feature_cutoff_date"])
    oldl=pd.read_csv(OLD_LLRS,parse_dates=["feature_cutoff_date"])
    olds=pd.read_csv(OLD_STATE,parse_dates=["feature_cutoff_date"])
    olda=pd.read_csv(OLD_ACT,parse_dates=["feature_cutoff_date"])

    _,ic=inv.scalar_compare(ifbc,oldi,"feature_cutoff_date",["ifbc_score"])
    _,lc=inv.scalar_compare(llrs,oldl,"feature_cutoff_date",["llrs_pressure","llrs_incremental"])
    _,sc=inv.scalar_compare(state,olds,"feature_cutoff_date",["leadlag_score_premax","internal_now","internal_d1"])

    anew=zdec[zdec.handoff_alarm]
    aold=olds[olds.handoff_alarm.map(base.B)]
    hs=setstats(anew.feature_cutoff_date,aold.feature_cutoff_date)

    variants={}
    for name,col in [("Q95","phase_q95"),("Q99","phase_q99")]:
        _,a,e,r,b=base.simulate_dptc(anew,col)
        ov=olda[olda.variant.astype(str)==name]
        ss=setstats(a.feature_cutoff_date,ov.feature_cutoff_date)
        variants[name]={"actions":len(a),"rescue":r,"broken":b,"net":r-b,"entry":None if e is None else e.date().isoformat(),"action_set":ss}

    compare=zdec[["feature_cutoff_date","handoff_alarm","leadlag_score_premax","internal_now","internal_d1"]].merge(
        olds[["feature_cutoff_date","handoff_alarm","leadlag_score_premax","internal_now","internal_d1"]],
        on="feature_cutoff_date",how="left",suffixes=("_cons","_yh"))
    compare.to_csv(OUTC,index=False)

    pass90=hs["jaccard"]>=.90 and min(variants["Q95"]["action_set"]["jaccard"],variants["Q99"]["action_set"]["jaccard"])>=.90
    out={"schema":"GOLD_H3_DATABENTO_CONSENSUS_ROLL_BRIDGE_2025_V1","date":"2026-10-05",
         "rule":"majority instrument_id among c/n/v; if all differ use product-specific priority learned from 2025 Yahoo price identity only",
         "estimated_cost_usd":total,"cost_by_roll_usd":costs,"cost_cap_usd":MAX_COST_USD,
         "tie_break_priorities":priorities,"tie_break_learning":pstats,"price_identity":idstats,
         "derived":{"ifbc":ic,"llrs":lc,"state":sc},"handoff":hs,"dptc":variants,
         "decision_invariance_pass_90pct":bool(pass90),
         "status":"CONSENSUS_SOURCE_BRIDGE_PASS" if pass90 else "CONSENSUS_SOURCE_BRIDGE_REQUIRES_REVIEW",
         "outcome_labels_used_for_rule":False,"thresholds_retuned":False,"raw_vendor_prices_committed":False}
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    def cm(obj,col):
        x=obj["columns"][col]
        return "—" if x["corr"] is None else f"corr={x['corr']:.5f}, MAE={x['mae']:.6g}"
    lines=["# GOLD H3 — Databento Consensus Roll Bridge (2025) — 2026-10-05","",
           f"**Status:** **{out['status']}**  ",f"Estimated Databento cost: **USD {total:.4f}**.","",
           "Rule: choose the instrument_id supported by at least 2 of calendar/open-interest/volume continuous aliases; when all three differ, use a root-specific priority learned only from Yahoo price identity.","",
           "## Tie-break rules","",
           "| Root | Priority | Tie hours | c wins | n wins | v wins | Median price error bps | P95 bps |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for root in ROOTS:
        ps=pstats[root];ii=idstats[root]
        lines.append(f"| {root} | {' > '.join(priorities[root])} | {ps['tie_hours']} | {ps['wins']['c']} | {ps['wins']['n']} | {ps['wins']['v']} | {ii['median_bps']:.5f} | {ii['p95_bps']:.5f} |")
    lines += ["","## Derived agreement","",
              f"- IFBC score: {cm(ic,'ifbc_score')}",
              f"- LLRS pressure: {cm(lc,'llrs_pressure')}",
              f"- LLRS incremental: {cm(lc,'llrs_incremental')}",
              f"- leadlag_score_premax: {cm(sc,'leadlag_score_premax')}",
              f"- internal_now: {cm(sc,'internal_now')}",
              f"- internal_d1: {cm(sc,'internal_d1')}","",
              "## Decision invariance","",
              f"- Handoff: {hs['matched']} matched; Databento {hs['new_n']} vs Yahoo {hs['old_n']}; Jaccard **{100*hs['jaccard']:.1f}%**.",
              f"- Added: {', '.join(hs['added']) if hs['added'] else 'none'}",
              f"- Missing: {', '.join(hs['missing']) if hs['missing'] else 'none'}","",
              "| Variant | DB actions | Yahoo actions | Matched | Jaccard | DB R/B/net |",
              "|---|---:|---:|---:|---:|---:|"]
    for n in ["Q95","Q99"]:
        v=variants[n];s=v["action_set"]
        lines.append(f"| {n} | {s['new_n']} | {s['old_n']} | {s['matched']} | {100*s['jaccard']:.1f}% | {v['rescue']}/{v['broken']}/{v['net']:+d} |")
    lines += ["","## Governance","",
              "- Tie-break priorities are selected solely from source-price identity in 2025; DPTC correctness is not consulted.",
              "- The same deterministic rule can therefore be applied unchanged to 2023–2024.",
              "- Passing supports a source-bridged historical reconstruction, not byte-identical Yahoo lineage."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":main()
