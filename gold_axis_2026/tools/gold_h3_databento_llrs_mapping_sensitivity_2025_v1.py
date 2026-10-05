from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

inv=loadmod("inv2025",AX/"tools"/"gold_h3_databento_downstream_invariance_2025_v1.py")
base=inv.base

OUTJ=AX/"GOLD_H3_DATABENTO_LLRS_MAPPING_SENSITIVITY_2025_2026-10-05.json"
OUTM=AX/"GOLD_H3_DATABENTO_LLRS_MAPPING_SENSITIVITY_2025_2026-10-05.md"
OUTC=AX/"GOLD_H3_DATABENTO_LLRS_MAPPING_SENSITIVITY_GRID_2025_2026-10-05.csv"

DATASET="GLBX.MDP3"
SCHEMA="ohlcv-1h"
START="2024-10-10"
END="2026-10-04"
MAX_COST_USD=1.60
ROOTS=["GC","SI","NQ","ZN","CL"]
ROLLS=["c","n","v"]

BASEMAP={"GC":"v","SI":"v","NQ":"v","ZN":"n","CL":"c"}
CONFIGS={
    "BASE":BASEMAP,
    "GC_n":{**BASEMAP,"GC":"n"},
    "SI_n":{**BASEMAP,"SI":"n"},
    "NQ_c":{**BASEMAP,"NQ":"c"},
    "NQ_n":{**BASEMAP,"NQ":"n"},
    "ZN_v":{**BASEMAP,"ZN":"v"},
    "CL_v":{**BASEMAP,"CL":"v"},
}

OLD_LLRS=AX/"GOLD_H3_2025_BACKFILL_LLRS_EXTENDED_2026-10-05.csv"
OLD_STATE=AX/"GOLD_H3_2025_BACKFILL_HANDOFF_STATE_2026-10-05.csv"
OLD_ACT=AX/"GOLD_H3_2025_BACKFILL_DPTC_ACTIONS_2026-10-05.csv"

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
        d=data.to_df().reset_index()
        if "ts_event" not in d.columns and "index" in d.columns:
            d=d.rename(columns={"index":"ts_event"})
        d["ts"]=pd.to_datetime(d["ts_event"],utc=True)
        d["symbol"]=d["symbol"].astype(str)
        d["close"]=pd.to_numeric(d["close"],errors="coerce")
        d["volume"]=pd.to_numeric(d["volume"],errors="coerce")
        d=d[np.isfinite(d.close)&(d.close>0)].copy()
        groups[roll]=d[["ts","symbol","instrument_id","close","volume"]]
    return groups,costs,total

def selected_long(groups,mapping):
    parts=[]
    for root,roll in mapping.items():
        sym=f"{root}.{roll}.0"
        q=groups[roll][groups[roll].symbol==sym].copy()
        q["root"]=root
        parts.append(q)
    return pd.concat(parts,ignore_index=True)

def raw_wide(groups,mapping):
    d=selected_long(groups,mapping)
    p=d.pivot_table(index="ts",columns="root",values="close",aggfunc="last").reset_index()
    need=["GC","ZN","NQ","SI","CL"]
    p=p.dropna(subset=need).sort_values("ts").reset_index(drop=True)
    return p[["ts"]+need],d

def label_free_handoff(h3,state):
    z=h3[h3.feature_cutoff_date.dt.year==2025].copy().sort_values("feature_cutoff_date")
    z["v5_pred"]=(pd.to_numeric(z.p_helios_v5_dce,errors="coerce")>=.5).astype(int)
    sg=pd.read_csv(base.SAGE,parse_dates=["feature_cutoff_date"])
    sdates=set(sg[(sg.feature_cutoff_date.dt.year==2025)&sg.ocs_candidate.map(base.B)].feature_cutoff_date)
    rf=pd.read_csv(base.RF,parse_dates=["date"])
    rdates=set(rf[(rf.period.astype(str)=="2025")&rf.v3_candidate.map(base.B)].date)
    flips=sdates|rdates
    z["baseline_pred"]=np.where(z.feature_cutoff_date.isin(flips),1-z.v5_pred,z.v5_pred).astype(int)
    z=z.merge(state,on="feature_cutoff_date",how="left")
    z["handoff_alarm"]=(
        (pd.to_numeric(z.leadlag_score_premax,errors="coerce")>=.60)&
        (pd.to_numeric(z.internal_now,errors="coerce")>=.60)&
        (pd.to_numeric(z.internal_d1,errors="coerce")>=0)&
        (z.baseline_pred.astype(int)==z.momentum_up.astype(int))
    )
    return z

def corr_mae(new,old,col):
    q=new[["feature_cutoff_date",col]].merge(
        old[["feature_cutoff_date",col]],on="feature_cutoff_date",suffixes=("_db","_yh"))
    a=pd.to_numeric(q[f"{col}_db"],errors="coerce")
    b=pd.to_numeric(q[f"{col}_yh"],errors="coerce")
    z=pd.DataFrame({"a":a,"b":b}).dropna()
    if not len(z): return None,None,0
    return (None if len(z)<2 else float(z.a.corr(z.b))),float(np.mean(np.abs(z.a-z.b))),int(len(z))

def setcmp(a,b):
    a=set(pd.to_datetime(list(a))); b=set(pd.to_datetime(list(b)))
    u=a|b;i=a&b
    return {
        "new_n":len(a),"old_n":len(b),"matched":len(i),
        "jaccard":1.0 if not u else len(i)/len(u),
        "added":[x.date().isoformat() for x in sorted(a-b)],
        "missing":[x.date().isoformat() for x in sorted(b-a)]
    }

def main():
    groups,costs,total=fetch_groups()
    h3=inv.prep_h3()
    old_l=pd.read_csv(OLD_LLRS,parse_dates=["feature_cutoff_date"])
    old_s=pd.read_csv(OLD_STATE,parse_dates=["feature_cutoff_date"])
    old_a=pd.read_csv(OLD_ACT,parse_dates=["feature_cutoff_date"])
    old_alarm_dates=old_s[old_s.handoff_alarm.map(base.B)].feature_cutoff_date

    # Keep IFBC fixed at the already source-best GC/SI volume mapping.
    _,base_long=raw_wide(groups,BASEMAP)
    vast=inv.build_vast_from_db(base_long,h3)
    ifbc=base.build_ifbc_scores(vast)

    rows=[]
    cache={}
    for name,mapping in CONFIGS.items():
        raw,_=raw_wide(groups,mapping)
        hourly=base.llrs_prepare_hourly(raw)
        llrs=base.llrs_origin_scores(hourly,h3,"2024-12-01")
        state=base.build_handoff_scores(ifbc,llrs)
        hz=label_free_handoff(h3,state)
        cmp=setcmp(hz[hz.handoff_alarm].feature_cutoff_date,old_alarm_dates)
        pc,pm,pn=corr_mae(llrs,old_l,"llrs_pressure")
        ic,im,in_=corr_mae(llrs,old_l,"llrs_incremental")
        lc,lm,ln=corr_mae(state,old_s,"leadlag_score_premax")
        rows.append({
            "config":name,
            "mapping":json.dumps(mapping,sort_keys=True),
            "handoff_new_n":cmp["new_n"],"handoff_old_n":cmp["old_n"],"handoff_matched":cmp["matched"],
            "handoff_jaccard":cmp["jaccard"],"handoff_added_n":len(cmp["added"]),"handoff_missing_n":len(cmp["missing"]),
            "added_dates":";".join(cmp["added"]),"missing_dates":";".join(cmp["missing"]),
            "llrs_pressure_corr":pc,"llrs_pressure_mae":pm,
            "llrs_incremental_corr":ic,"llrs_incremental_mae":im,
            "leadlag_premax_corr":lc,"leadlag_premax_mae":lm,
        })
        cache[name]=(mapping,llrs,state,hz,cmp)

    grid=pd.DataFrame(rows)
    grid=grid.sort_values(
        ["handoff_jaccard","handoff_matched","handoff_added_n","handoff_missing_n","leadlag_premax_corr","llrs_pressure_corr"],
        ascending=[False,False,True,True,False,False]
    ).reset_index(drop=True)
    grid.to_csv(OUTC,index=False)
    best_name=str(grid.iloc[0].config)
    mapping,llrs,state,hz,cmp=cache[best_name]

    # Mapping is frozen here using label-free source agreement only.
    # Only after freezing do we inspect DPTC action transport.
    z=inv.make_decision_panel(h3,state)
    alarms=z[z.handoff_alarm].copy()
    variants={}
    for name,col in [("Q95","phase_q95"),("Q99","phase_q99")]:
        _,a,entry,rescue,broken=base.simulate_dptc(alarms,col)
        oldv=old_a[old_a.variant.astype(str)==name]
        ac=setcmp(a.feature_cutoff_date,oldv.feature_cutoff_date)
        variants[name]={
            "actions":int(len(a)),"rescue":int(rescue),"broken":int(broken),"net":int(rescue-broken),
            "entry":None if entry is None else entry.date().isoformat(),
            "action_set":ac,
        }

    source_pass=bool(cmp["jaccard"]>=0.90)
    dptc_pass=bool(min(variants["Q95"]["action_set"]["jaccard"],variants["Q99"]["action_set"]["jaccard"])>=0.90)
    out={
        "schema":"GOLD_H3_DATABENTO_LLRS_MAPPING_SENSITIVITY_2025_V1",
        "date":"2026-10-05",
        "selection_rule":"label-free Yahoo-vs-Databento Handoff alarm agreement; no RESCUE/BROKEN outcomes",
        "estimated_cost_usd":total,"cost_by_roll_usd":costs,"cost_cap_usd":MAX_COST_USD,
        "ifbc_mapping_fixed":{"GC":"v","SI":"v"},
        "candidate_configs":list(CONFIGS.keys()),
        "best_config":best_name,"frozen_mapping_candidate":mapping,
        "best_handoff":cmp,
        "source_bridge_handoff_pass_90pct":source_pass,
        "postfreeze_dptc_transport":variants,
        "postfreeze_dptc_action_pass_90pct":dptc_pass,
        "status":"LABEL_FREE_SOURCE_BRIDGE_PASS" if source_pass and dptc_pass else "LABEL_FREE_SOURCE_BRIDGE_REQUIRES_REVIEW",
        "raw_vendor_values_committed":False,
        "thresholds_retuned":False,
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    lines=[
        "# GOLD H3 — Databento LLRS Mapping Sensitivity (2025) — 2026-10-05","",
        f"**Status:** **{out['status']}**  ",
        f"Estimated Databento cost: **USD {total:.4f}** (cap USD {MAX_COST_USD:.2f}).  ",
        "**Mapping selection is label-free: only Yahoo↔Databento LLRS/Handoff source agreement is used.**","",
        "## One-channel sensitivity grid","",
        "| Config | Handoff matched | New/Old | Jaccard | Added | Missing | Leadlag corr | LLRS pressure corr |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.config} | {r.handoff_matched} | {r.handoff_new_n}/{r.handoff_old_n} | {100*r.handoff_jaccard:.1f}% | "
            f"{r.handoff_added_n} | {r.handoff_missing_n} | {r.leadlag_premax_corr:.4f} | {r.llrs_pressure_corr:.4f} |"
        )
    lines += ["",f"## Label-free winner: {best_name}","",
              f"- Mapping: **{mapping}**",
              f"- Handoff: **{cmp['matched']} matched**, Databento {cmp['new_n']} vs Yahoo {cmp['old_n']}, Jaccard **{100*cmp['jaccard']:.1f}%**.",
              f"- Added: **{', '.join(cmp['added']) if cmp['added'] else 'none'}**.",
              f"- Missing: **{', '.join(cmp['missing']) if cmp['missing'] else 'none'}**.","",
              "## Post-freeze DPTC transport","",
              "| Variant | DB actions | Yahoo actions | Matched | Jaccard | DB R/B/net |",
              "|---|---:|---:|---:|---:|---:|"]
    for n in ["Q95","Q99"]:
        v=variants[n];a=v["action_set"]
        lines.append(f"| {n} | {a['new_n']} | {a['old_n']} | {a['matched']} | {100*a['jaccard']:.1f}% | {v['rescue']}/{v['broken']}/{v['net']:+d} |")
    lines += ["","## Governance","",
              "- No competence outcome, RESCUE/BROKEN label or forecast correctness is used to pick the mapping.",
              "- Only single-channel substitutions around the raw-source winner are tested; this is a source-lineage diagnosis, not model tuning.",
              "- DPTC outcomes are inspected only after the source mapping is frozen.",
              "- Passing this audit supports a source-bridged reconstruction, not a claim that Databento bars are byte-identical to Yahoo."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
