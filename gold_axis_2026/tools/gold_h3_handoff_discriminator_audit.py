from pathlib import Path
import importlib.util
import json
import math
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

HSM=AX/"tools"/"gold_h3_handoff_state_machine_v1.py"
RTEP=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
RTEF=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
OIP=AX/"GOLD_H3_FLOW_PRELIM_OI_V1_FAST_PREDICTIONS_2026-10-03.csv"
EV25=AX/"GOLD_H3_RULEFLOW_DISCOVERY_V1_EVENTS_2026-10-04.csv"
EV26=AX/"GOLD_H3_RULEFLOW_V2_Q2Q3_STRESS_EVENTS_2026-10-04.csv"

OUT_MD=AX/"GOLD_H3_HANDOFF_DISCRIMINATOR_AUDIT_RESULT_2026-10-04.md"
OUT_JSON=AX/"GOLD_H3_HANDOFF_DISCRIMINATOR_AUDIT_SUMMARY_2026-10-04.json"
OUT_FEATURES=AX/"GOLD_H3_HANDOFF_DISCRIMINATOR_AUDIT_FEATURES_2026-10-04.csv"
OUT_ALARMS=AX/"GOLD_H3_HANDOFF_DISCRIMINATOR_AUDIT_ALARMS_2026-10-04.csv"

spec=importlib.util.spec_from_file_location("hsm",HSM)
hsm=importlib.util.module_from_spec(spec); spec.loader.exec_module(hsm)

def auc_raw(y,x):
    y=np.asarray(y,int); x=np.asarray(x,float)
    m=np.isfinite(x)&np.isfinite(y)
    y=y[m]; x=x[m]
    n1=int((y==1).sum()); n0=int((y==0).sum())
    if n1==0 or n0==0:return np.nan
    r=rankdata(x,method="average")
    rs=float(r[y==1].sum())
    return float((rs-n1*(n1+1)/2)/(n1*n0))

def smd(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    a=a[np.isfinite(a)]; b=b[np.isfinite(b)]
    if len(a)<2 or len(b)<2:return np.nan
    va=np.var(a,ddof=1); vb=np.var(b,ddof=1)
    den=len(a)+len(b)-2
    if den<=0:return np.nan
    sp=math.sqrt(max(0.0,((len(a)-1)*va+(len(b)-1)*vb)/den))
    return float((np.mean(a)-np.mean(b))/sp) if sp>1e-12 else np.nan

def safe_num(s):
    return pd.to_numeric(s,errors="coerce")

def build():
    z=hsm.load_frame().sort_values("feature_cutoff_date").reset_index(drop=True)

    # Topology transitions computed on the full chronology before alarm filtering.
    z["ndx_r60_d1"]=safe_num(z.ndx_r60)-safe_num(z.ndx_r60).shift(1)
    z["vix_r60_d1"]=safe_num(z.vix_r60)-safe_num(z.vix_r60).shift(1)
    z["topology_rotation_mag"]=np.sqrt(z.ndx_r60_d1**2+z.vix_r60_d1**2)
    # Positive safe_rotation means movement toward Gold-vs-Nasdaq negative / Gold-vs-VIX positive.
    z["safe_rotation_d1"]=-z.ndx_r60_d1+z.vix_r60_d1
    z["safe_topology_score"]=-safe_num(z.ndx_r60)+safe_num(z.vix_r60)

    # Broad union/core Handoff alarm BEFORE topology veto.
    z["handoff_alarm"]=(safe_num(z.leadlag_score_premax)>=0.60)&(safe_num(z.internal_now)>=0.60)&(safe_num(z.internal_d1)>=0.0)&(z.baseline_pred.astype(int)==z.momentum_up.astype(int))
    z["alarm_rescue"]=(~z.baseline_correct).astype(int)
    z["alarm_outcome"]=np.where(z.alarm_rescue.astype(bool),"RESCUE","BROKEN")

    # RTE origin-safe option/participation features.
    rp=pd.read_csv(RTEP,parse_dates=["feature_cutoff_date"])
    rf=pd.read_csv(RTEF,parse_dates=["feature_cutoff_date"])
    rte_cols=["feature_cutoff_date","p_inst","rte_tension","p_rte"]
    feat_cols=["feature_cutoff_date","gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
               "opt_vol_imbalance","d_opt_vol_imbalance_1","opt_total_z20",
               "signed_opt_pressure","signed_d_opt_pressure"]
    z=z.merge(rp[rte_cols],on="feature_cutoff_date",how="left")
    z=z.merge(rf[feat_cols],on="feature_cutoff_date",how="left")

    # Preliminary OI panel, already strict prior-trade-date PIT.
    oi=pd.read_csv(OIP,parse_dates=["feature_cutoff_date"])
    oi=oi[["feature_cutoff_date","flow_trade_date","flow_stale_days","flow_volume","flow_oi","p_flow_reversal"]].copy()
    oi["flow_volume"]=safe_num(oi.flow_volume); oi["flow_oi"]=safe_num(oi.flow_oi)
    oi=oi.sort_values("feature_cutoff_date")
    oi["flow_volume_chg1"]=oi.flow_volume.pct_change(fill_method=None)
    oi["flow_oi_chg1"]=oi.flow_oi.pct_change(fill_method=None)
    z=z.merge(oi,on="feature_cutoff_date",how="left")

    # Sparse scheduled-event context, only where an existing event ledger is available.
    evs=[]
    if EV25.exists():
        e=pd.read_csv(EV25,parse_dates=["date"])
        for c in ["step_bp","gross3","conflict_ratio","current_dominance","reaction_decay","first_ret","post_first_ret","event_total_ret"]:
            if c not in e.columns:e[c]=np.nan
        e=e[["date","event","step_bp","gross3","conflict_ratio","current_dominance","reaction_decay","first_ret","post_first_ret","event_total_ret"]]
        e=e.rename(columns={"date":"feature_cutoff_date"})
        e["event_ledger"]="2025_DISCOVERY"
        evs.append(e)
    if EV26.exists():
        e=pd.read_csv(EV26,parse_dates=["date"])
        for c in ["step_bp","gross3","conflict_ratio","current_dominance","reaction_decay","first_ret","post_first_ret","event_total_ret"]:
            if c not in e.columns:e[c]=np.nan
        e=e[["date","event","step_bp","gross3","conflict_ratio","current_dominance","reaction_decay","first_ret","post_first_ret","event_total_ret"]]
        e=e.rename(columns={"date":"feature_cutoff_date"})
        e["event_ledger"]="2026_Q2Q3"
        evs.append(e)
    if evs:
        ev=pd.concat(evs,ignore_index=True).sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date",keep="last")
        z=z.merge(ev,on="feature_cutoff_date",how="left")
    else:
        z["event"]=np.nan
        z["event_ledger"]=np.nan
    z["scheduled_event_known"]=z["event"].notna().astype(int)
    return z

FEATURES=[
"leadlag_score_premax","internal_now","internal_d1","fragility_score","flow_score","leadlag_score",
"p_rte","p_inst","rte_tension",
"signed_opt_pressure","signed_d_opt_pressure","opt_vol_imbalance","d_opt_vol_imbalance_1","opt_total_z20",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"p_flow_reversal","flow_volume_chg1","flow_oi_chg1",
"ndx_r60","vix_r60","ndx_r60_d1","vix_r60_d1","topology_rotation_mag","safe_rotation_d1","safe_topology_score",
"strong_pro_risk","scheduled_event_known","step_bp","gross3","conflict_ratio","current_dominance"
]

def feature_stats(q,feature,period):
    x=safe_num(q[feature]) if feature in q.columns else pd.Series(np.nan,index=q.index)
    y=q.alarm_rescue.astype(int)
    m=np.isfinite(x)
    qr=q[m & (y==1)]; qb=q[m & (y==0)]
    xr=safe_num(qr[feature]); xb=safe_num(qb[feature])
    raw=auc_raw(y[m],x[m])
    oriented=np.nan if not np.isfinite(raw) else max(raw,1-raw)
    direction=None if not np.isfinite(raw) else ("HIGHER_RESCUE" if raw>=0.5 else "LOWER_RESCUE")
    return {
      "period":period,"feature":feature,
      "n_nonmissing":int(m.sum()),"coverage":float(m.mean()) if len(q) else np.nan,
      "rescue_n":int(len(qr)),"broken_n":int(len(qb)),
      "rescue_mean":float(xr.mean()) if len(xr) else np.nan,
      "broken_mean":float(xb.mean()) if len(xb) else np.nan,
      "rescue_median":float(xr.median()) if len(xr) else np.nan,
      "broken_median":float(xb.median()) if len(xb) else np.nan,
      "smd":smd(xr,xb),"auc_raw":raw,"auc_oriented":oriented,"direction":direction
    }

def main():
    z=build()
    q=z[z.handoff_alarm & z.feature_cutoff_date.dt.year.isin([2025,2026])].copy()
    q["year"]=q.feature_cutoff_date.dt.year

    results=[]
    for year in [2025,2026]:
        yy=q[q.year==year]
        for f in FEATURES:
            if f in yy.columns:results.append(feature_stats(yy,f,str(year)))
    for f in FEATURES:
        if f in q.columns:results.append(feature_stats(q,f,"POOLED"))
    rdf=pd.DataFrame(results)

    # Cross-year stability according to prereg.
    stab=[]
    for f in FEATURES:
        a=rdf[(rdf.period=="2025")&(rdf.feature==f)]
        b=rdf[(rdf.period=="2026")&(rdf.feature==f)]
        if a.empty or b.empty:continue
        a=a.iloc[0]; b=b.iloc[0]
        sign_ok=np.isfinite(a.smd) and np.isfinite(b.smd) and np.sign(a.smd)==np.sign(b.smd) and np.sign(a.smd)!=0
        n_ok=min(a.rescue_n,a.broken_n,b.rescue_n,b.broken_n)>=3
        mag_ok=np.isfinite(a.smd) and np.isfinite(b.smd) and abs(a.smd)>=.20 and abs(b.smd)>=.20
        stab.append({"feature":f,"stable_descriptive":bool(sign_ok and n_ok and mag_ok),
                     "smd_2025":a.smd,"smd_2026":b.smd,
                     "auc_2025":a.auc_oriented,"auc_2026":b.auc_oriented,
                     "direction_2025":a.direction,"direction_2026":b.direction,
                     "coverage_2025":a.coverage,"coverage_2026":b.coverage,
                     "min_group_n":int(min(a.rescue_n,a.broken_n,b.rescue_n,b.broken_n))})
    sdf=pd.DataFrame(stab)
    if len(sdf):
        sdf["min_abs_smd"]=sdf[["smd_2025","smd_2026"]].abs().min(axis=1)
        sdf=sdf.sort_values(["stable_descriptive","min_abs_smd"],ascending=[False,False])

    # Event / topology categorical context.
    cats={}
    for year in [2025,2026]:
        yy=q[q.year==year]
        cats[str(year)]={
          "n":int(len(yy)),"rescue":int(yy.alarm_rescue.sum()),"broken":int((1-yy.alarm_rescue).sum()),
          "precision":float(yy.alarm_rescue.mean()) if len(yy) else np.nan,
          "strong_pro_risk":{
            "rescue_true":int(((yy.alarm_rescue==1)&yy.strong_pro_risk.fillna(False)).sum()),
            "broken_true":int(((yy.alarm_rescue==0)&yy.strong_pro_risk.fillna(False)).sum()),
            "rescue_false":int(((yy.alarm_rescue==1)&(~yy.strong_pro_risk.fillna(False))).sum()),
            "broken_false":int(((yy.alarm_rescue==0)&(~yy.strong_pro_risk.fillna(False))).sum())
          },
          "scheduled_event":{
            "rescue_event":int(((yy.alarm_rescue==1)&(yy.scheduled_event_known==1)).sum()),
            "broken_event":int(((yy.alarm_rescue==0)&(yy.scheduled_event_known==1)).sum()),
            "rescue_nonevent":int(((yy.alarm_rescue==1)&(yy.scheduled_event_known==0)).sum()),
            "broken_nonevent":int(((yy.alarm_rescue==0)&(yy.scheduled_event_known==0)).sum())
          }
        }

    # Pre-existing HSM thresholds only: descriptive stratification, no new cut-point search.
    strat=[]
    for year in [2025,2026]:
        yy=q[q.year==year].copy()
        for th in [0.60,0.67,0.75]:
            hi=yy.leadlag_score_premax>=th
            for name,mask in [
                (f"leadlag_ge_{th:.2f}",hi),
                (f"leadlag_ge_{th:.2f}_strong_pro",hi & yy.strong_pro_risk.fillna(False)),
                (f"leadlag_ge_{th:.2f}_other_topology",hi & (~yy.strong_pro_risk.fillna(False))),
            ]:
                qq=yy[mask]
                strat.append({"year":year,"stratum":name,"n":int(len(qq)),
                              "rescue":int(qq.alarm_rescue.sum()),"broken":int((1-qq.alarm_rescue).sum()),
                              "precision":float(qq.alarm_rescue.mean()) if len(qq) else np.nan})
        # Natural sign split for option volume imbalance, not a fitted threshold.
        for name,mask in [
            ("opt_vol_imbalance_gt0", safe_num(yy.opt_vol_imbalance)>0),
            ("opt_vol_imbalance_le0", safe_num(yy.opt_vol_imbalance)<=0),
        ]:
            qq=yy[mask]
            strat.append({"year":year,"stratum":name,"n":int(len(qq)),
                          "rescue":int(qq.alarm_rescue.sum()),"broken":int((1-qq.alarm_rescue).sum()),
                          "precision":float(qq.alarm_rescue.mean()) if len(qq) else np.nan})
    stratdf=pd.DataFrame(strat)

    rdf.to_csv(OUT_FEATURES,index=False)
    alarm_cols=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","year","momentum_up","y_up","target_r3",
                "v5_pred","baseline_pred","baseline_correct","alarm_outcome",
                "leadlag_score_premax","internal_now","internal_d1","fragility_score","flow_score",
                "p_rte","p_inst","rte_tension","signed_opt_pressure","signed_d_opt_pressure",
                "gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5","p_flow_reversal",
                "flow_volume_chg1","flow_oi_chg1","ndx_r60","vix_r60","safe_rotation_d1",
                "safe_topology_score","strong_pro_risk","scheduled_event_known","event","step_bp","conflict_ratio","current_dominance"]
    for c in alarm_cols:
        if c not in q.columns:q[c]=np.nan
    q[alarm_cols].to_csv(OUT_ALARMS,index=False)

    stable=sdf[sdf.stable_descriptive] if len(sdf) else pd.DataFrame()
    summary={
      "schema":"GOLD_H3_HANDOFF_RESCUE_VS_BROKEN_DISCRIMINATOR_AUDIT",
      "status":"RETROSPECTIVE_MECHANISM_DIAGNOSTIC",
      "canonical_alarm":"external_premax>=0.60 & internal_now>=0.60 & internal_d1>=0 & baseline==momentum; pre-topology-veto",
      "years":cats,
      "pooled":{"n":int(len(q)),"rescue":int(q.alarm_rescue.sum()),"broken":int((1-q.alarm_rescue).sum()),"precision":float(q.alarm_rescue.mean()) if len(q) else np.nan},
      "stable_descriptive_features":stable.replace({np.nan:None}).to_dict("records") if len(stable) else [],
      "all_cross_year":sdf.replace({np.nan:None}).to_dict("records") if len(sdf) else [],
      "preexisting_threshold_stratification":stratdf.replace({np.nan:None}).to_dict("records")
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — Handoff Rescue-vs-Broken Discriminator Audit","",
           "**Status:** retrospective mechanism diagnostic only; no new trade rule.","",
           "## Canonical broad Handoff alarm","",
           "`external_premax >= 0.60 AND internal_now >= 0.60 AND internal_d1 >= 0 AND combined baseline == momentum`",
           "",
           "Topology veto is intentionally not applied before this audit, because topology is one of the candidate discriminators.",""]
    for year in [2025,2026]:
        c=cats[str(year)]
        lines += [f"## {year} alarm outcomes","",
                  f"- alarms: **{c['n']}**",
                  f"- rescue / broken: **{c['rescue']} / {c['broken']}**",
                  f"- raw flip precision: **{100*c['precision']:.2f}%**",""]
    lines += ["## Stable descriptive discriminators","",
              "Requirement: same rescue-vs-broken direction in 2025 and 2026, >=3 observations in every rescue/broken group, and |SMD|>=0.20 in both years.","",
              "| Feature | 2025 SMD | 2026 SMD | 2025 AUC | 2026 AUC | Direction 2025 | Direction 2026 | Cov25 | Cov26 |",
              "|---|---:|---:|---:|---:|---|---|---:|---:|"]
    if len(stable):
        for r in stable.itertuples():
            lines.append(f"| {r.feature} | {r.smd_2025:+.3f} | {r.smd_2026:+.3f} | {r.auc_2025:.3f} | {r.auc_2026:.3f} | {r.direction_2025} | {r.direction_2026} | {100*r.coverage_2025:.1f}% | {100*r.coverage_2026:.1f}% |")
    else:
        lines.append("| _none_ | | | | | | | | |")

    lines += ["","## Strongest cross-year candidates, including non-stable","",
              "| Feature | Stable | 2025 SMD | 2026 SMD | 2025 AUC | 2026 AUC | Min group N |",
              "|---|---|---:|---:|---:|---:|---:|"]
    if len(sdf):
        for r in sdf.head(15).itertuples():
            lines.append(f"| {r.feature} | {r.stable_descriptive} | {r.smd_2025:+.3f} | {r.smd_2026:+.3f} | {r.auc_2025:.3f} | {r.auc_2026:.3f} | {r.min_group_n} |")

    lines += ["","## Existing-threshold stratification","",
              "| Year | Stratum | N | Rescue | Broken | Precision |",
              "|---:|---|---:|---:|---:|---:|"]
    for r in stratdf.itertuples():
        pv="NA" if not np.isfinite(r.precision) else f"{100*r.precision:.1f}%"
        lines.append(f"| {r.year} | {r.stratum} | {r.n} | {r.rescue} | {r.broken} | {pv} |")
    lines += ["","## Topology contingency","",
              "| Year | Strong pro-risk: rescue/broken | Other topology: rescue/broken |",
              "|---|---:|---:|"]
    for year in [2025,2026]:
        c=cats[str(year)]["strong_pro_risk"]
        lines.append(f"| {year} | {c['rescue_true']}/{c['broken_true']} | {c['rescue_false']}/{c['broken_false']} |")

    lines += ["","## Scheduled-event context","",
              "| Year | Event rescue/broken | Non-event rescue/broken |",
              "|---|---:|---:|"]
    for year in [2025,2026]:
        c=cats[str(year)]["scheduled_event"]
        lines.append(f"| {year} | {c['rescue_event']}/{c['broken_event']} | {c['rescue_nonevent']}/{c['broken_nonevent']} |")

    lines += ["","## Interpretation discipline","",
              "- This audit asks what distinguishes a true Handoff reversal from a false Handoff alarm; it does not choose a threshold.",
              "- Preliminary OI is incomplete after 2026-03-19 and cannot be promoted as a full-year discriminator.",
              "- Sparse scheduled-event ledgers are context only; absence of a ledger row is not proof that no macro catalyst existed.",
              "- Features derived from H3 future outcomes were excluded.",
              "- Any apparent discriminator must be separately frozen and tested; no 2026 accuracy is modified here."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: fixed-threshold-stratification
