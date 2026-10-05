from __future__ import annotations

import importlib.util
import json, os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m

base=loadmod("base2025",AX/"tools"/"gold_h3_2025_source_backfill_dptc_replay_v1.py")

OUTJ=AX/"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_2026-10-05.json"
OUTM=AX/"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_2026-10-05.md"
OUTC=AX/"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_GRID_2026-10-05.csv"
OUTA=AX/"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_ACTIONS_2026-10-05.csv"

DATASET="GLBX.MDP3";SCHEMA="ohlcv-1h"
START="2022-01-01";END="2025-01-01";MAX_COST_USD=3.50
ROOTS=["GC","SI","NQ","ZN","CL"];ROLLS=["c","n","v"]
SELLR_THR=base.SELLR_THR;Q99_RUN=base.Q99_RUN

VARIANTS={
 "BASE":{"GC":"v","SI":"v","NQ":"v","ZN":"n","CL":"c"},
 "SI_n":{"GC":"v","SI":"n","NQ":"v","ZN":"n","CL":"c"},
 "NQ_n":{"GC":"v","SI":"v","NQ":"n","ZN":"n","CL":"c"},
 "ZN_v":{"GC":"v","SI":"v","NQ":"v","ZN":"v","CL":"c"},
 "CL_v":{"GC":"v","SI":"v","NQ":"v","ZN":"n","CL":"v"},
 "GC_n":{"GC":"n","SI":"v","NQ":"v","ZN":"n","CL":"c"},
 "NQ_c":{"GC":"v","SI":"v","NQ":"c","ZN":"n","CL":"c"},
}

H3=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
PHASE=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv"
SELLR=AX/"GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv"
RF_SUM=AX/"GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_SUMMARY_2026-10-04.json"

def fetch_groups():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key);costs={}
    for roll in ROLLS:
        syms=[f"{r}.{roll}.0" for r in ROOTS]
        costs[roll]=float(client.metadata.get_cost(dataset=DATASET,schema=SCHEMA,symbols=syms,stype_in="continuous",start=START,end=END))
    total=float(sum(costs.values()))
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
    return groups,costs,total

def selected_long(groups,mapping):
    parts=[]
    for root,roll in mapping.items():
        sym=f"{root}.{roll}.0"
        q=groups[roll][groups[roll].symbol==sym][["ts","instrument_id","close","volume"]].copy()
        q["root"]=root;parts.append(q)
    return pd.concat(parts,ignore_index=True)

def build_vast(d,h3):
    parts={}
    for root in ["GC","SI"]:
        q=d[d.root==root][["ts","close","volume"]].copy().sort_values("ts").drop_duplicates("ts")
        q=q.rename(columns={"close":f"{root}_close","volume":f"{root}_volume"})
        q[f"{root}_volume"]=pd.to_numeric(q[f"{root}_volume"],errors="coerce").fillna(0).clip(lower=0)
        q=base.same_hour_volume_z(q,root);parts[root]=q
    x=parts["GC"].merge(parts["SI"],on="ts",how="inner").sort_values("ts").reset_index(drop=True)
    x["GC_ret1"]=np.log(x.GC_close).diff();x["SI_ret1"]=np.log(x.SI_close).diff()
    hh=h3[h3.eligible_v5_continuation.map(base.B)].copy().sort_values("forecast_issue_date")
    rows=[]
    for r in hh.itertuples():
        co=base.cutoff_ts(r.feature_cutoff_date)
        w=x[(x.ts<=co)&(x.ts>=co-pd.Timedelta(hours=18))].tail(12).copy()
        if len(w)<12:continue
        if (co-w.ts.iloc[-1]).total_seconds()/3600>3:continue
        if (w.ts.iloc[-1]-w.ts.iloc[0]).total_seconds()/3600>18:continue
        if w[["GC_ret1","SI_ret1"]].isna().any(axis=None):continue
        s=1.0 if int(r.momentum_up)==1 else -1.0;out=r._asdict()
        for h in [3,6,12]:
            z=w.tail(h)
            out[f"gc_flow_{h}"]=base.vol_flow(z.GC_ret1.to_numpy(),z.GC_volume.to_numpy(),s)
            out[f"gc_opp_vol_share_{h}"]=base.opp_share(z.GC_ret1.to_numpy(),z.GC_volume.to_numpy(),s)
        for h in [6,12]:
            z=w.tail(h);out[f"gc_efficiency_{h}"]=base.efficiency(z.GC_ret1.to_numpy())
        for h in [6,12]:
            z=w.tail(h)
            out[f"si_flow_{h}"]=base.vol_flow(z.SI_ret1.to_numpy(),z.SI_volume.to_numpy(),s)
            out[f"si_opp_vol_share_{h}"]=base.opp_share(z.SI_ret1.to_numpy(),z.SI_volume.to_numpy(),s)
        out["gc_si_flow_gap12"]=float(out["gc_flow_12"]-out["si_flow_12"])
        out["joint_opposition_share12"]=float((out["gc_opp_vol_share_12"]+out["si_opp_vol_share_12"])/2)
        out["hourly_last_ts"]=w.ts.iloc[-1];rows.append(out)
    return pd.DataFrame(rows).sort_values("feature_cutoff_date").reset_index(drop=True)

def prepare_h3():
    h=pd.read_csv(H3)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:h[c]=pd.to_datetime(h[c])
    for c in ["eligible_v5_continuation","opal_override_check"]:
        if c in h.columns:h[c]=h[c].map(base.B)
    return h[(h.feature_cutoff_date>=pd.Timestamp("2022-10-01"))&(h.feature_cutoff_date<pd.Timestamp("2025-01-01"))].copy()

def build_state(groups,mapping,h3,ifbc_cache):
    key=(mapping["GC"],mapping["SI"])
    if key not in ifbc_cache:
        d=selected_long(groups,mapping)
        ifbc_cache[key]=base.build_ifbc_scores(build_vast(d,h3))
    ifbc=ifbc_cache[key]
    d=selected_long(groups,mapping)
    raw=d.pivot_table(index="ts",columns="root",values="close",aggfunc="last").reset_index()
    raw=raw.dropna(subset=ROOTS).sort_values("ts").reset_index(drop=True)
    hourly=base.llrs_prepare_hourly(raw[["ts","GC","ZN","NQ","SI","CL"]])
    llrs=base.llrs_origin_scores(hourly,h3,"2022-11-01")
    state=base.build_handoff_scores(ifbc,llrs)
    return ifbc,llrs,state,int(len(raw))

def confusion(y,p):
    y=np.asarray(y,int);p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum());tn=int(((y==0)&(p==0)).sum());fp=int(((y==0)&(p==1)).sum());fn=int(((y==1)&(p==0)).sum())
    return {"n":len(y),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "balanced_accuracy":float(((tp/max(tp+fn,1))+(tn/max(tn+fp,1)))/2),"tp":tp,"tn":tn,"fp":fp,"fn":fn}

def decision_panel(h3,state,year,baseline_mode,rf_dates,phase,sellr):
    z=h3[h3.feature_cutoff_date.dt.year==year].copy().sort_values("feature_cutoff_date")
    z["baseline_pred"]=(pd.to_numeric(z.p_helios_v5_dce,errors="coerce")>=.5).astype(int)
    if baseline_mode=="V5_RF":
        z.loc[z.feature_cutoff_date.dt.strftime("%Y-%m-%d").isin(rf_dates.get(str(year),[])),"baseline_pred"]=1-z.loc[z.feature_cutoff_date.dt.strftime("%Y-%m-%d").isin(rf_dates.get(str(year),[])),"baseline_pred"]
    z["baseline_correct"]=z.baseline_pred==z.y_up.astype(int)
    z=z.merge(state,on="feature_cutoff_date",how="left")
    z=z.merge(phase[["feature_cutoff_date","strong_pro_risk","strong_run","dep_shift95","dependence_phase"]],on="feature_cutoff_date",how="left")
    z["phase_q95"]=z.dependence_phase.map(base.B)
    z["phase_q99"]=z.strong_pro_risk.map(base.B)&((pd.to_numeric(z.strong_run,errors="coerce")>Q99_RUN)|z.dep_shift95.map(base.B))
    sc=sellr[["feature_cutoff_date","sellr_score","baseline_pred","momentum_up"]].rename(columns={"baseline_pred":"sellr_baseline_pred","momentum_up":"sellr_momentum_up"})
    z=z.merge(sc,on="feature_cutoff_date",how="left")
    z["sellr_fire"]=(pd.to_numeric(z.sellr_score,errors="coerce")>=SELLR_THR)&(pd.to_numeric(z.sellr_baseline_pred,errors="coerce")==pd.to_numeric(z.sellr_momentum_up,errors="coerce"))
    z["handoff_alarm"]=(pd.to_numeric(z.leadlag_score_premax,errors="coerce")>=.60)&(pd.to_numeric(z.internal_now,errors="coerce")>=.60)&(pd.to_numeric(z.internal_d1,errors="coerce")>=0)&(z.baseline_pred.astype(int)==z.momentum_up.astype(int))
    z["competence_y"]=(~z.baseline_correct).astype(int)
    return z

def run_one(z,variant_name,baseline_mode,year):
    base_met=confusion(z.y_up,z.baseline_pred)
    alarms=z[z.handoff_alarm].copy()
    rows=[];acts=[]
    for name,col in [("Q95","phase_q95"),("Q99","phase_q99")]:
        _,a,e,r,b=base.simulate_dptc(alarms,col)
        pred=z.baseline_pred.to_numpy(int).copy()
        aset=set(a.feature_cutoff_date)
        mask=z.feature_cutoff_date.isin(aset).to_numpy();pred[mask]=1-pred[mask]
        m=confusion(z.y_up,pred)
        rows.append({"source_variant":variant_name,"baseline_mode":baseline_mode,"year":year,"dptc":name,
                     "origins":len(z),"baseline_correct":base_met["correct"],"baseline_accuracy":base_met["accuracy"],"baseline_ba":base_met["balanced_accuracy"],
                     "handoff_alarms":len(alarms),"actions":len(a),"rescue":r,"broken":b,"net":r-b,
                     "precision":r/max(len(a),1),"assisted_correct":m["correct"],"assisted_accuracy":m["accuracy"],"assisted_ba":m["balanced_accuracy"],
                     "entry":None if e is None else e.date().isoformat()})
        if len(a):
            aa=a[["feature_cutoff_date","mode","competence_y","sellr_fire"]].copy()
            aa["source_variant"]=variant_name;aa["baseline_mode"]=baseline_mode;aa["year"]=year;aa["dptc"]=name
            acts.append(aa)
    return rows,acts

def action_robustness(actions,baseline_mode,year,dptc):
    q=actions[(actions.baseline_mode==baseline_mode)&(actions.year==year)&(actions.dptc==dptc)].copy()
    if q.empty:return {"union_n":0,"intersection_n":0,"dates_all":[],"date_support":{}}
    supp=q.groupby("feature_cutoff_date").source_variant.nunique().sort_index()
    nvar=len(VARIANTS)
    return {"union_n":int(len(supp)),"intersection_n":int((supp==nvar).sum()),
            "dates_all":[d.date().isoformat() for d in supp[supp==nvar].index],
            "date_support":{d.date().isoformat():int(v) for d,v in supp.items()}}

def main():
    groups,costs,total=fetch_groups();h3=prepare_h3()
    phase=pd.read_csv(PHASE,parse_dates=["feature_cutoff_date"])
    sellr=pd.read_csv(SELLR,parse_dates=["feature_cutoff_date"])
    rf=json.loads(RF_SUM.read_text())["years"]
    rf_dates={y:rf[y]["v3_action_dates"] for y in rf}
    ifbc_cache={};grid=[];acts=[];coverage={}
    for vname,mapping in VARIANTS.items():
        ifbc,llrs,state,nraw=build_state(groups,mapping,h3,ifbc_cache)
        coverage[vname]={"sync_hourly_rows":nraw,"ifbc_origins":len(ifbc),"llrs_origins":len(llrs),"state_origins":len(state),
                         "first_state":None if state.empty else str(state.feature_cutoff_date.min().date())}
        for bm in ["V5_ONLY","V5_RF"]:
            for year in [2023,2024]:
                z=decision_panel(h3,state,year,bm,rf_dates,phase,sellr)
                rr,aa=run_one(z,vname,bm,year);grid.extend(rr);acts.extend(aa)
    g=pd.DataFrame(grid);g.to_csv(OUTC,index=False)
    adf=pd.concat(acts,ignore_index=True) if acts else pd.DataFrame()
    adf.to_csv(OUTA,index=False)

    robust={}
    for bm in ["V5_ONLY","V5_RF"]:
        robust[bm]={}
        for year in [2023,2024]:
            robust[bm][str(year)]={}
            for dptc in ["Q95","Q99"]:
                q=g[(g.baseline_mode==bm)&(g.year==year)&(g.dptc==dptc)].copy()
                nets=q.net.astype(int).tolist()
                robust[bm][str(year)][dptc]={
                    "net_by_variant":dict(zip(q.source_variant,nets)),
                    "min_net":int(min(nets)),"max_net":int(max(nets)),"median_net":float(np.median(nets)),
                    "positive_variants":int(sum(x>0 for x in nets)),"zero_variants":int(sum(x==0 for x in nets)),"negative_variants":int(sum(x<0 for x in nets)),
                    "all_same_sign":bool(all(x>0 for x in nets) or all(x<0 for x in nets) or all(x==0 for x in nets)),
                    "actions":action_robustness(adf,bm,year,dptc)
                }

    out={"schema":"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_V1","date":"2026-10-05",
         "status":"SOURCE_ROBUST_HISTORICAL_REPLAY_COMPLETE","source_window":[START,END],
         "estimated_cost_usd":total,"cost_by_roll_usd":costs,"cost_cap_usd":MAX_COST_USD,
         "source_variants":VARIANTS,"coverage":coverage,"ruleflow_dates":rf_dates,
         "sage_backcasted":False,"dptc_thresholds_retuned":False,"outcome_labels_used_for_source_choice":False,
         "robustness":robust}
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    lines=["# GOLD H3 — DPTC 2023–2024 Databento Source-Robust Replay — 2026-10-05","",
           "**Status:** SOURCE_ROBUST_HISTORICAL_REPLAY_COMPLETE — retrospective source-bridged evidence, not prospective validation.","",
           f"Databento estimated cost: **USD {total:.4f}**.","",
           "Seven fixed source mappings are replayed. DPTC Q95/Q99 thresholds are unchanged. SAGE is not backcast. RuleFlow is reported both excluded (V5_ONLY) and included as its fixed pre-2025 backcast (V5_RF).","",
           "## Main grid","",
           "| Baseline | Year | DPTC | Source | Base correct | Base acc | Handoff | Actions | R/B/net | Assisted correct | Assisted acc | BA |",
           "|---|---:|---|---|---:|---:|---:|---:|---|---:|---:|---:|"]
    for r in g.sort_values(["baseline_mode","year","dptc","source_variant"]).itertuples():
        lines.append(f"| {r.baseline_mode} | {r.year} | {r.dptc} | {r.source_variant} | {r.baseline_correct}/{r.origins} | {100*r.baseline_accuracy:.2f}% | {r.handoff_alarms} | {r.actions} | {r.rescue}/{r.broken}/{r.net:+d} | {r.assisted_correct}/{r.origins} | {100*r.assisted_accuracy:.2f}% | {100*r.assisted_ba:.2f}% |")
    lines += ["","## Source-robust verdict","",
              "| Baseline | Year | DPTC | Net range | Median | + / 0 / - variants | Actions common to all sources |",
              "|---|---:|---|---|---:|---|---:|"]
    for bm in ["V5_ONLY","V5_RF"]:
        for year in [2023,2024]:
            for dptc in ["Q95","Q99"]:
                s=robust[bm][str(year)][dptc]
                lines.append(f"| {bm} | {year} | {dptc} | {s['min_net']:+d}..{s['max_net']:+d} | {s['median_net']:+.1f} | {s['positive_variants']} / {s['zero_variants']} / {s['negative_variants']} | {s['actions']['intersection_n']} |")
    lines += ["","## Scientific interpretation","",
              "- A result is source-robust only when its sign and material conclusion survive all seven admissible Databento mappings.",
              "- 2023–2024 are historical backcasts reconstructed with Databento because Yahoo hourly futures history is no longer directly available.",
              "- No source mapping is selected by DPTC performance; all admissible mappings are reported.",
              "- SAGE remains absent because its frozen source contract did not exist in 2023–2024.",
              "- V5_RF includes only the already-fixed RuleFlow V3-TG historical calls (2023-10-03 and 2024-06-12)."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":main()
