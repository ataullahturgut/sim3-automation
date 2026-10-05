from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta, fisher_exact

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

FEATURES=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_FEATURES_V1_2026-10-05.csv"
ACT_PRE=AX/"GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_ACTIONS_2026-10-05.csv"
ACT25=AX/"GOLD_H3_2025_BACKFILL_DPTC_ACTIONS_2026-10-05.csv"
ACT26=AX/"GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv"
SUM25=AX/"GOLD_H3_2025_BACKFILL_DPTC_SUMMARY_2026-10-05.json"
SUM26=AX/"GOLD_H3_DPTC_V1_SUMMARY_2026-10-05.json"

OUTJ=AX/"GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_2026-10-05.json"
OUTM=AX/"GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_2026-10-05.md"
OUTC=AX/"GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_RESULTS_2026-10-05.csv"
OUTA=AX/"GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_ACTIONS_2026-10-05.csv"

MIN_SOURCE_SUPPORT=6
PRIMARY="TCG_V1_STRONG_PRO_RISK"

def B(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def load_actions():
    f=pd.read_csv(FEATURES,parse_dates=["feature_cutoff_date"])

    allp=pd.read_csv(ACT_PRE,parse_dates=["feature_cutoff_date"])
    p=allp[(allp.dptc.astype(str)=="Q95") & (allp.source_variant.astype(str)=="BASE") & (allp.baseline_mode.astype(str)=="V5_ONLY")].copy()
    sup=(allp[(allp.dptc.astype(str)=="Q95")&(allp.baseline_mode.astype(str)=="V5_ONLY")]
         .groupby("feature_cutoff_date").source_variant.nunique())
    p=p[p.feature_cutoff_date.map(sup).fillna(0)>=MIN_SOURCE_SUPPORT].copy()
    p["source_support"]=p.feature_cutoff_date.map(sup).astype(int)
    p["year"]=p.feature_cutoff_date.dt.year
    p["lineage"]="DATABENTO_SOURCE_ROBUST"

    a25=pd.read_csv(ACT25,parse_dates=["feature_cutoff_date"])
    a25=a25[a25.variant.astype(str)=="Q95"].copy()
    a25["year"]=2025;a25["source_support"]=7;a25["lineage"]="YAHOO_EXACT"

    a26=pd.read_csv(ACT26,parse_dates=["feature_cutoff_date"])
    a26=a26[a26.variant.astype(str)=="Q95"].copy()
    a26["year"]=2026;a26["source_support"]=7;a26["lineage"]="YAHOO_EXACT"

    keep=["feature_cutoff_date","competence_y","year","source_support","lineage"]
    a=pd.concat([p[keep],a25[keep],a26[keep]],ignore_index=True)
    a=a.drop_duplicates(["feature_cutoff_date","year"]).sort_values("feature_cutoff_date")
    a=a.merge(f,on="feature_cutoff_date",how="left",suffixes=("","_feat"))

    a["TCG_V1_STRONG_PRO_RISK"]=a.strong_pro_risk.map(B)
    a["TCG_V1_PHASE"]=a.dependence_phase.map(B)
    a["TCG_P3"]=a.strong_pro_risk.map(B)&(pd.to_numeric(a.strong_run,errors="coerce")>=3)
    a["TCG_OIL_NEG"]=a.strong_pro_risk.map(B)&(pd.to_numeric(a.corr_gc_cl,errors="coerce")<0)
    a["TCG_P3_OIL_NEG"]=a["TCG_P3"]&(pd.to_numeric(a.corr_gc_cl,errors="coerce")<0)
    a["TCG_TRIAD"]=(
        a.strong_pro_risk.map(B)&
        (pd.to_numeric(a.corr_gc_nq,errors="coerce")>0)&
        (pd.to_numeric(a.corr_gc_cl,errors="coerce")<0)
    )
    return a

def jeffreys(r,n,alpha=.05):
    if n<=0:return (None,None)
    return (float(beta.ppf(alpha/2,r+.5,n-r+.5)),float(beta.ppf(1-alpha/2,r+.5,n-r+.5)))

def gate_eval(a,gate,year=None):
    z=a if year is None else a[a.year==year]
    q=z[z[gate].map(B)].copy()
    r=int(q.competence_y.sum());b=int(len(q)-r);net=r-b
    lo,hi=jeffreys(r,len(q))
    return {
        "year":"ALL" if year is None else int(year),
        "gate":gate,"actions":int(len(q)),"rescue":r,"broken":b,"net":net,
        "precision":None if not len(q) else r/len(q),
        "jeffreys_lo":lo,"jeffreys_hi":hi,
        "dates":[d.date().isoformat() for d in q.feature_cutoff_date],
    }

def ungated_eval(a,year=None):
    z=a if year is None else a[a.year==year]
    r=int(z.competence_y.sum());b=int(len(z)-r)
    return {"actions":len(z),"rescue":r,"broken":b,"net":r-b,
            "precision":None if not len(z) else r/len(z)}

def exact_accuracy_projection(rows):
    s25=json.loads(SUM25.read_text())["2025"]
    s26=json.loads(SUM26.read_text())["variants"]["Q95"]["stress_2026"]
    b25=int(s25["baseline"]["correct"]);n25=int(s25["origins"])
    b26=int(s26["metrics"]["correct"]-s26["net"])
    n26=int(s26["metrics"]["tp"]+s26["metrics"]["tn"]+s26["metrics"]["fp"]+s26["metrics"]["fn"])
    out={}
    for gate in rows.gate.unique():
        y25=rows[(rows.gate==gate)&(rows.year==2025)].iloc[0]
        y26=rows[(rows.gate==gate)&(rows.year==2026)].iloc[0]
        c25=b25+int(y25.net);c26=b26+int(y26.net)
        out[gate]={
            "2025":{"baseline_correct":b25,"gated_correct":c25,"n":n25,"accuracy":c25/n25},
            "2026":{"baseline_correct":b26,"gated_correct":c26,"n":n26,"accuracy":c26/n26},
            "combined":{"baseline_correct":b25+b26,"gated_correct":c25+c26,"n":n25+n26,"accuracy":(c25+c26)/(n25+n26)}
        }
    return out

def main():
    a=load_actions()
    gates=["TCG_V1_STRONG_PRO_RISK","TCG_V1_PHASE","TCG_P3","TCG_OIL_NEG","TCG_P3_OIL_NEG","TCG_TRIAD"]
    rec=[]
    for g in gates:
        for y in [2023,2024,2025,2026]:
            rec.append(gate_eval(a,g,y))
        rec.append(gate_eval(a,g,None))
    r=pd.DataFrame(rec)
    r.to_csv(OUTC,index=False)

    proj=exact_accuracy_projection(r[r.year.isin([2025,2026])])

    inside=a[a[PRIMARY].map(B)];outside=a[~a[PRIMARY].map(B)]
    ri=int(inside.competence_y.sum());bi=int(len(inside)-ri)
    ro=int(outside.competence_y.sum());bo=int(len(outside)-ro)
    odds,p=fisher_exact([[ri,bi],[ro,bo]])
    rejected_broken_share=bo/max(len(outside),1)

    loyo=[]
    for omit in [2023,2024,2025,2026]:
        q=a[(a.year!=omit)&a[PRIMARY].map(B)]
        rr=int(q.competence_y.sum());bb=int(len(q)-rr)
        loyo.append({"omitted_year":omit,"actions":len(q),"rescue":rr,"broken":bb,"net":rr-bb,
                     "precision":None if not len(q) else rr/len(q)})

    pre=a[a.year<=2025]
    pre_q=pre[pre[PRIMARY].map(B)]
    pre_r=int(pre_q.competence_y.sum());pre_b=int(len(pre_q)-pre_r)

    audit_cols=["feature_cutoff_date","year","lineage","source_support","competence_y","strong_pro_risk","strong_run",
                "r_gn","r_gv","corr_gc_nq","corr_gc_cl"]+gates
    a[audit_cols].to_csv(OUTA,index=False)

    verdict={
        "primary_gate":PRIMARY,
        "rule":"strong_pro_risk == TRUE (Gold-Nasdaq positive and Gold-VIX negative under the frozen dependence-phase definition)",
        "year_results":{str(y):gate_eval(a,PRIMARY,y) for y in [2023,2024,2025,2026]},
        "all":gate_eval(a,PRIMARY,None),
        "pre2026":{"actions":len(pre_q),"rescue":pre_r,"broken":pre_b,"net":pre_r-pre_b,
                   "precision":None if not len(pre_q) else pre_r/len(pre_q)},
        "rejected_actions":{"n":len(outside),"rescue":ro,"broken":bo,"broken_share":rejected_broken_share},
        "enrichment":{"odds_ratio":float(odds),"fisher_p":float(p)},
        "leave_one_year_out":loyo,
        "exact_accuracy_projection_2025_2026":proj[PRIMARY],
    }

    out={
        "schema":"GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1",
        "date":"2026-10-05",
        "status":"POSTHOC_TOPOLOGY_GATE_CHALLENGER",
        "primary_gate_predeclared_before_evaluation":PRIMARY,
        "primary":verdict,
        "sensitivity_gates":{g:{
            "all":gate_eval(a,g,None),
            "by_year":{str(y):gate_eval(a,g,y) for y in [2023,2024,2025,2026]},
            "projection_2025_2026":proj[g]
        } for g in gates if g!=PRIMARY},
        "ungated_by_year":{str(y):ungated_eval(a,y) for y in [2023,2024,2025,2026]},
        "ungated_all":ungated_eval(a,None),
        "sample_note":"2023-2024 Q95 action dates require support from >=6/7 Databento source mappings; 2025-2026 use exact Yahoo-lineage Q95 actions.",
        "governance":{
            "outcome_used_to_define_primary_rule":False,
            "primary_rule_source":"previously frozen strong_pro_risk topology definition",
            "2026_consumed_development_evidence":True,
            "promotion_status":"challenger_only_until_prospective_validation"
        }
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    lines=[
        "# GOLD H3 — Topology Competence Gate V1 — 2026-10-05","",
        "**Status:** POSTHOC_TOPOLOGY_GATE_CHALLENGER — not prospectively validated.","",
        "## Frozen primary rule","",
        "**TCG-V1 = allow a DPTC flip only when strong_pro_risk is TRUE.**",
        "This is the already-defined label-free topology: Gold–Nasdaq positive and Gold–VIX negative, with the frozen significance condition. No RESCUE/BROKEN label is used to set a numeric threshold.","",
        "## Primary gate results","",
        "| Year | Ungated R/B/net | TCG actions | TCG R/B/net | TCG precision |",
        "|---:|---:|---:|---:|---:|"
    ]
    for y in [2023,2024,2025,2026]:
        u=ungated_eval(a,y);g=gate_eval(a,PRIMARY,y)
        pr="—" if g["precision"] is None else f"{100*g['precision']:.1f}%"
        lines.append(f"| {y} | {u['rescue']}/{u['broken']}/{u['net']:+d} | {g['actions']} | {g['rescue']}/{g['broken']}/{g['net']:+d} | {pr} |")
    ga=gate_eval(a,PRIMARY,None);ua=ungated_eval(a,None)
    lines += ["",f"- Across the harmonized 2023–2026 action sample: ungated **{ua['rescue']}/{ua['broken']} = net {ua['net']:+d}** on {ua['actions']} actions; TCG-V1 **{ga['rescue']}/{ga['broken']} = net {ga['net']:+d}** on {ga['actions']} actions.",
              f"- Primary-gate odds ratio for RESCUE vs rejected actions: **{odds:.2f}**, Fisher exact **p={p:.4f}**.",
              f"- Pre-2026 only: **{pre_r}/{len(pre_q)} rescue**, {pre_b} broken, net **{pre_r-pre_b:+d}**.","",
              "## Exact Yahoo-lineage accuracy projection","",
              "| Period | Baseline | TCG-V1 | Accuracy |",
              "|---|---:|---:|---:|"]
    for k in ["2025","2026","combined"]:
        z=proj[PRIMARY][k]
        lines.append(f"| {k} | {z['baseline_correct']}/{z['n']} | {z['gated_correct']}/{z['n']} | {100*z['accuracy']:.2f}% |")
    lines += ["","## Sensitivity family","",
              "| Gate | 2023 net | 2024 net | 2025 net | 2026 net | All R/B/net | Actions |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for g in gates:
        by={y:gate_eval(a,g,y) for y in [2023,2024,2025,2026]};allg=gate_eval(a,g,None)
        lines.append(f"| {g} | {by[2023]['net']:+d} | {by[2024]['net']:+d} | {by[2025]['net']:+d} | {by[2026]['net']:+d} | {allg['rescue']}/{allg['broken']}/{allg['net']:+d} | {allg['actions']} |")
    lines += ["","## Scientific reading","",
              "- The primary gate is intentionally simple. It asks whether the cross-asset topology associated with competence is present; it does not ask whether the market is generally volatile or structurally anomalous.",
              "- 2023–2024 are source-robust historical reconstructions, not exact Yahoo lineage.",
              "- 2025–2026 projections use the exact frozen Yahoo-lineage action outcomes.",
              "- Because the topology hypothesis was diagnosed using consumed 2026 evidence, TCG-V1 cannot be called independently validated. It is a challenger for prospective shadow evaluation.",
              "- Sensitivity gates are reported to show how persistence and oil-decoupling restrictions affect selectivity; they are not selected by best historical performance."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
