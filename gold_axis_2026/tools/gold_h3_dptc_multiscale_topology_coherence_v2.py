from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, beta

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

FEATURES=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_FEATURES_V1_2026-10-05.csv"
ACTIONS=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_ACTIONS_V1_2026-10-05.csv"
STATE25=AX/"GOLD_H3_2025_BACKFILL_HANDOFF_STATE_2026-10-05.csv"
TL26=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"

OUTJ=AX/"GOLD_H3_DPTC_MULTISCALE_TOPOLOGY_COHERENCE_V2_2026-10-05.json"
OUTM=AX/"GOLD_H3_DPTC_MULTISCALE_TOPOLOGY_COHERENCE_V2_2026-10-05.md"
OUTC=AX/"GOLD_H3_DPTC_MULTISCALE_TOPOLOGY_HANDOFF_V2_2026-10-05.csv"

def B(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def jeffreys(r,n):
    if n<=0:return [None,None]
    return [float(beta.ppf(.025,r+.5,n-r+.5)),float(beta.ppf(.975,r+.5,n-r+.5))]

def enrich(z,gate):
    g=z.dropna(subset=["competence_y"]).copy()
    inside=g[g[gate].fillna(False).astype(bool)]
    outside=g[~g[gate].fillna(False).astype(bool)]
    ri=int(inside.competence_y.sum());bi=int(len(inside)-ri)
    ro=int(outside.competence_y.sum());bo=int(len(outside)-ro)
    if len(inside) and len(outside):
        odds,p=fisher_exact([[ri,bi],[ro,bo]])
    else: odds,p=np.nan,np.nan
    return {
        "inside_n":int(len(inside)),"inside_rescue":ri,
        "inside_precision":None if not len(inside) else float(ri/len(inside)),
        "inside_jeffreys95":jeffreys(ri,len(inside)),
        "outside_n":int(len(outside)),"outside_rescue":ro,
        "outside_precision":None if not len(outside) else float(ro/len(outside)),
        "outside_jeffreys95":jeffreys(ro,len(outside)),
        "odds_ratio":None if not np.isfinite(odds) else float(odds),
        "fisher_p":None if not np.isfinite(p) else float(p),
    }

def robust_state_distance(f):
    cols=["corr_gc_nq","corr_gc_zn","corr_gc_cl","corr_gc_si","eig1_share","te_nq_to_gc_diff","leadlag_nq_to_gc","r_gn","r_gv"]
    pre=f[f.feature_cutoff_date<pd.Timestamp("2026-01-01")].copy()
    x=pre[cols].apply(pd.to_numeric,errors="coerce")
    med=x.median(); mad=(x-med).abs().median()*1.4826
    sd=x.std(ddof=0)
    sc=mad.where(mad>1e-8,sd).where(lambda s:s>1e-8,1.0)
    zz=(f[cols].apply(pd.to_numeric,errors="coerce")-med)/sc
    dist=np.sqrt(np.nansum(np.square(zz.to_numpy(float)),axis=1))
    pre_dist=dist[f.feature_cutoff_date<pd.Timestamp("2026-01-01")]
    q95=float(np.nanquantile(pre_dist,.95))
    return dist,q95,cols,med.to_dict(),sc.to_dict()

def make_gates(f):
    f=f.copy()
    f["daily_pro"]=f.strong_pro_risk.map(B)
    f["hourly_riskon"]=pd.to_numeric(f.corr_gc_nq,errors="coerce")>0
    f["oil_decoupled"]=pd.to_numeric(f.corr_gc_cl,errors="coerce")<0
    f["bond_confirm"]=pd.to_numeric(f.corr_gc_zn,errors="coerce")>0
    f["dual_scale_pro"]=f.daily_pro & f.hourly_riskon
    f["triad_coherent"]=f.dual_scale_pro & f.oil_decoupled
    f["quad_coherent"]=f.triad_coherent & f.bond_confirm
    f["settled_triad"]=f.triad_coherent & (pd.to_numeric(f.structural_count95,errors="coerce")<=1)
    for k in [2,3,4,5]:
        f[f"triad_run_ge{k}"]=f.triad_coherent & (pd.to_numeric(f.strong_run,errors="coerce")>=k)
        f[f"settled_triad_run_ge{k}"]=f.settled_triad & (pd.to_numeric(f.strong_run,errors="coerce")>=k)
    dist,q95,cols,med,sc=robust_state_distance(f)
    f["state_dist"]=dist
    f["state_dist_high"]=f.state_dist>=q95
    f["displaced_settled_triad"]=f.settled_triad & f.state_dist_high
    return f,{"state_cols":cols,"state_distance_q95_pre2026":q95,"pre2026_center":med,"pre2026_scale":sc}

def handoff():
    s=pd.read_csv(STATE25,parse_dates=["feature_cutoff_date"])
    s=s[s.handoff_alarm.map(B)][["feature_cutoff_date","competence_y"]].copy()
    s["year"]=2025
    t=pd.read_csv(TL26,parse_dates=["feature_cutoff_date"])
    t=t[t.period.astype(str)=="2026_STRESS"][["feature_cutoff_date","competence_y"]].copy()
    t["year"]=2026
    return pd.concat([s,t],ignore_index=True).drop_duplicates("feature_cutoff_date")

def quadrant_stats(z):
    rows={}
    for dp in [False,True]:
        for hr in [False,True]:
            q=z[(z.daily_pro==dp)&(z.hourly_riskon==hr)]
            r=int(q.competence_y.sum());n=len(q)
            rows[f"daily_pro={dp}|hourly_riskon={hr}"]={"n":n,"rescue":r,"precision":None if not n else r/n,"jeffreys95":jeffreys(r,n)}
    return rows

def sign_cube(z):
    rows={}
    for dp in [False,True]:
        for hr in [False,True]:
            for oil in [False,True]:
                q=z[(z.daily_pro==dp)&(z.hourly_riskon==hr)&(z.oil_decoupled==oil)]
                r=int(q.competence_y.sum());n=len(q)
                rows[f"d{int(dp)}_h{int(hr)}_o{int(oil)}"]={"n":n,"rescue":r,"precision":None if not n else r/n}
    return rows

def main():
    f=pd.read_csv(FEATURES,parse_dates=["feature_cutoff_date"])
    f,meta=make_gates(f)
    a=pd.read_csv(ACTIONS,parse_dates=["feature_cutoff_date"])
    # Drop feature columns from action file and remap from canonical V1 feature table.
    basecols=["feature_cutoff_date","source_support","competence_y","year","source","outcome"]
    a=a[basecols].merge(f,on="feature_cutoff_date",how="left")
    h=handoff().merge(f,on="feature_cutoff_date",how="left")
    h.to_csv(OUTC,index=False)

    gates=["daily_pro","dual_scale_pro","triad_coherent","quad_coherent","settled_triad",
           "triad_run_ge2","triad_run_ge3","triad_run_ge4","triad_run_ge5",
           "settled_triad_run_ge2","settled_triad_run_ge3","settled_triad_run_ge4","settled_triad_run_ge5",
           "state_dist_high","displaced_settled_triad"]
    hand={g:enrich(h,g) for g in gates}
    act={g:enrich(a,g) for g in gates}

    byyear={}
    for y,g in a.groupby("year"):
        byyear[str(int(y))]={
            "n":len(g),"rescue":int(g.competence_y.sum()),"precision":float(g.competence_y.mean()),
            "daily_pro":float(g.daily_pro.mean()),"dual_scale_pro":float(g.dual_scale_pro.mean()),
            "triad_coherent":float(g.triad_coherent.mean()),"quad_coherent":float(g.quad_coherent.mean()),
            "settled_triad":float(g.settled_triad.mean()),"state_dist_high":float(g.state_dist_high.mean()),
            "state_dist_mean":float(g.state_dist.mean())
        }

    # 2026 onset dates, no outcome use.
    onsets={}
    for g in gates:
        q=f[(f.feature_cutoff_date.dt.year==2026)&f[g].fillna(False).astype(bool)]
        onsets[g]=None if q.empty else q.feature_cutoff_date.iloc[0].date().isoformat()

    out={
        "schema":"GOLD_H3_DPTC_MULTISCALE_TOPOLOGY_COHERENCE_V2",
        "date":"2026-10-05",
        "status":"MULTISCALE_TOPOLOGY_DIAGNOSIS_COMPLETE",
        "hypothesis":"DPTC competence requires persistent cross-timescale topology coherence, not contemporaneous structural-shift magnitude.",
        "natural_sign_rules":{
            "daily_pro":"existing strong_pro_risk: daily Gold-Nasdaq positive and Gold-VIX negative with significance condition",
            "hourly_riskon":"hourly GC-NQ correlation > 0",
            "oil_decoupled":"hourly GC-CL correlation < 0",
            "bond_confirm":"hourly GC-ZN correlation > 0",
            "triad_coherent":"daily_pro AND hourly_riskon AND oil_decoupled",
            "quad_coherent":"triad_coherent AND bond_confirm",
            "settled_triad":"triad_coherent AND local structural anomaly count <= 1",
        },
        "state_distance":meta,
        "handoff_enrichment_2025_2026":hand,
        "dptc_action_enrichment_2023_2026":act,
        "handoff_daily_hourly_quadrants":quadrant_stats(h),
        "handoff_sign_cube":sign_cube(h),
        "year_action_profiles":byyear,
        "onsets_2026":onsets,
        "governance":{
            "sign_thresholds_are_natural_zero_crossings":True,
            "persistence_sensitivity_all_2_to_5_reported":True,
            "no_gate_selected_by_outcome_optimization":True,
            "posthoc_only":True
        }
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    def pp(x): return "—" if x is None else f"{100*x:.1f}%"
    lines=[
        "# GOLD H3 — DPTC Multiscale Topology Coherence V2 — 2026-10-05","",
        "**Status:** MULTISCALE_TOPOLOGY_DIAGNOSIS_COMPLETE — post-hoc mechanism diagnosis.","",
        "## Mechanism hypothesis","",
        "DPTC competence is tested as a **state-occupancy** phenomenon: daily dependence topology must agree with the hourly futures network, and the transition itself should already have settled. No RESCUE/BROKEN label is used to define sign thresholds.","",
        "## 2025–2026 canonical Handoff enrichment","",
        "| Gate | Inside R/N | Precision | Jeffreys 95% | Outside R/N | Precision | Odds | Fisher p |",
        "|---|---:|---:|---|---:|---:|---:|---:|"]
    for g in gates:
        s=hand[g]; ci=s["inside_jeffreys95"]; cis="—" if ci[0] is None else f"{100*ci[0]:.1f}–{100*ci[1]:.1f}%"
        odds="—" if s["odds_ratio"] is None else f"{s['odds_ratio']:.2f}"; p="—" if s["fisher_p"] is None else f"{s['fisher_p']:.4f}"
        lines.append(f"| {g} | {s['inside_rescue']}/{s['inside_n']} | {pp(s['inside_precision'])} | {cis} | {s['outside_rescue']}/{s['outside_n']} | {pp(s['outside_precision'])} | {odds} | {p} |")
    lines += ["","## Daily × hourly topology quadrants","",
              "| State | Rescue/N | Precision |","|---|---:|---:|"]
    for k,s in out["handoff_daily_hourly_quadrants"].items():
        lines.append(f"| {k} | {s['rescue']}/{s['n']} | {pp(s['precision'])} |")
    lines += ["","## DPTC action profiles by year","",
              "| Year | N | Precision | Daily pro | Dual-scale | Triad | Quad | Settled triad | State displacement |",
              "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y,s in byyear.items():
        lines.append(f"| {y} | {s['n']} | {100*s['precision']:.1f}% | {100*s['daily_pro']:.1f}% | {100*s['dual_scale_pro']:.1f}% | {100*s['triad_coherent']:.1f}% | {100*s['quad_coherent']:.1f}% | {100*s['settled_triad']:.1f}% | {100*s['state_dist_high']:.1f}% |")
    lines += ["","## 2026 label-free onset","",
              "| Gate | First origin |","|---|---|"]
    for g,v in onsets.items(): lines.append(f"| {g} | {v or 'none'} |")
    lines += ["","## Interpretation discipline","",
              "- V1 showed generic structural-shift magnitude is not competence-enriching; this V2 therefore tests stable topology occupancy rather than transition intensity.",
              "- Zero-sign rules are economically interpretable and are not fit to DPTC outcomes.",
              "- Persistence thresholds 2, 3, 4 and 5 are all shown; no retrospective winner is hidden.",
              "- State-distance uses a robust pre-2026 center and is label-free.",
              "- Any gate remains a development challenger until prospective evidence accumulates."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":main()
