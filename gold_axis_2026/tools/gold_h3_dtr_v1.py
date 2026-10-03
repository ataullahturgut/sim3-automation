from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_DTR_V1_DEVELOPMENT_PREDICTIONS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_DTR_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_DTR_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_DTR_V1_PROSPECTIVE_FREEZE_2026-10-04.json"

WINDOW=60
MIN_PRIOR=20

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    for d in [p,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    keep=[
        "feature_cutoff_date","v5_confidence","trend_strength",
        "cf_opposite_semivar_share_gap","signed_opt_pressure","signed_d_opt_pressure"
    ]
    z=p.merge(f[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.sort_values("feature_cutoff_date").reset_index(drop=True)
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["oar"]=(
        (z.p_rte>=.60)&(z.p_inst>=.50)
        &(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
    )

    med_conf=[]; med_trend=[]; nprior=[]
    for r in z.itertuples():
        h=z[z.feature_cutoff_date<r.feature_cutoff_date].tail(WINDOW)
        med_conf.append(float(h.v5_confidence.median()) if len(h) else np.nan)
        med_trend.append(float(h.trend_strength.median()) if len(h) else np.nan)
        nprior.append(len(h))
    z["roll_median_v5_confidence"]=med_conf
    z["roll_median_trend_strength"]=med_trend
    z["prior_state_n"]=nprior
    z["high_persistence"]=(
        (z.prior_state_n>=MIN_PRIOR)
        &(z.v5_confidence>z.roll_median_v5_confidence)
        &(z.trend_strength>z.roll_median_trend_strength)
    )
    z["dtr_branch"]=np.where(z.high_persistence,"PREEMPTIVE","EXHAUSTION")
    z["dtr_candidate"]=(
        z.oar
        &(z.prior_state_n>=MIN_PRIOR)
        &np.where(
            z.high_persistence,
            z.cf_opposite_semivar_share_gap<0,
            z.cf_opposite_semivar_share_gap>0
        )
    )
    return z

def metric(q):
    c=q.dtr_candidate.astype(bool)
    r=int((c&(q.rescue_target==1)).sum())
    b=int((c&(q.rescue_target==0)).sum())
    n=int(c.sum())
    return {
        "eligible_n":len(q),"oar_n":int(q.oar.sum()),"candidate_n":n,
        "candidate_rate":n/max(len(q),1),
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(n,1),
        "preemptive_candidates":int((c&(q.dtr_branch=="PREEMPTIVE")).sum()),
        "exhaustion_candidates":int((c&(q.dtr_branch=="EXHAUSTION")).sum()),
    }

def main():
    z=load()
    z=z[z.year.isin([2024,2025,2026])].copy()
    z.to_csv(OUT_PRED,index=False)

    yrs={}
    for y in [2024,2025,2026]:
        yrs[str(y)]=metric(z[z.year==y].copy())
    pooled=metric(z)
    nonneg=sum(1 for y in yrs.values() if y["net_rescue"]>=0)
    worst=min(y["net_rescue"] for y in yrs.values())
    viable=bool(
        pooled["candidate_n"]>=10
        and pooled["net_rescue"]>0
        and pooled["rescue_precision"]>=.60
        and nonneg>=2
        and worst>=-1
    )
    status="DTR_PROSPECTIVE_FREEZE_READY" if viable else "DTR_DEVELOPMENT_NOT_VIABLE"

    freeze=None
    if viable:
        freeze={
            "schema":"DTR_H3_V1_PROSPECTIVE_FREEZE_V1",
            "frozen_at":"2026-10-04",
            "first_prospective_feature_cutoff":"2026-10-05",
            "evidence_class":"POST_HOLDOUT_DEVELOPMENT_FROZEN_FOR_PROSPECTIVE_USE",
            "base_oar":{
                "p_rte_min":0.60,"p_inst_min":0.50,
                "signed_opt_pressure_gt":0.0,"signed_d_opt_pressure_gt":0.0
            },
            "state":{
                "window_prior_origins":WINDOW,"minimum_prior_origins":MIN_PRIOR,
                "high_persistence":"v5_confidence > prior60_median AND trend_strength > prior60_median"
            },
            "branches":{
                "PREEMPTIVE":"HIGH_PERSISTENCE AND cf_opposite_semivar_share_gap < 0",
                "EXHAUSTION":"NOT HIGH_PERSISTENCE AND cf_opposite_semivar_share_gap > 0"
            },
            "prospective_trust":{
                "initial_mode":"SHADOW_ONLY",
                "matured_candidates_required":5,
                "recent_window":5,
                "recent_net_min":1,
                "fallback":"HELIOS_V5_DCE"
            }
        }
        OUT_FREEZE.write_text(json.dumps(freeze,indent=2)+"\n")

    summary={
        "schema":"DTR_H3_V1","status":status,
        "years":yrs,"pooled":pooled,
        "nonnegative_years":nonneg,"worst_year_net":worst,
        "development_viable":viable,
        "prospective_freeze":freeze
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# DTR-H3 V1 — DUAL-TRANSITION REVERSAL RESULT","",
           f"**Status:** **{status}**  ",
           "**Evidence class:** post-holdout development; 2024-2026 are development data.","",
           "## Development performance","",
           "| Year | OAR | DTR cand | Rescue | Broken | Net | Precision | Preemptive | Exhaustion |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in [2024,2025,2026]:
        r=yrs[str(y)]
        lines.append(
            f"| {y} | {r['oar_n']} | {r['candidate_n']} | {r['rescued']} | {r['broken']} | "
            f"{r['net_rescue']:+d} | {100*r['rescue_precision']:.2f}% | "
            f"{r['preemptive_candidates']} | {r['exhaustion_candidates']} |"
        )
    lines += ["","## Pooled development","",
              f"- candidates: **{pooled['candidate_n']}**",
              f"- rescue / broken / net: **{pooled['rescued']} / {pooled['broken']} / {pooled['net_rescue']:+d}**",
              f"- rescue precision: **{100*pooled['rescue_precision']:.2f}%**",
              f"- nonnegative years: **{nonneg}/3**",
              f"- worst year net: **{worst:+d}**",
              f"- development viability: **{'PASS' if viable else 'FAIL'}**"]
    if viable:
        lines += ["","## Prospective freeze","",
                  "- exact DTR rule frozen on **2026-10-04**;",
                  "- first independent feature cutoff: **2026-10-05**;",
                  "- initially **SHADOW ONLY**;",
                  "- live authority requires 5 matured prospective candidates with recent-5 net >= +1;",
                  "- otherwise live decision remains **HELIOS V5-DCE**."]
    lines += ["","## Governance","",
              "No retrospective DTR result is an independent holdout. No further retrospective threshold search is permitted under this version."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
