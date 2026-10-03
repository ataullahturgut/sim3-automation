from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_FOLDS=AX/"GOLD_H3_PGR_V1_CROSS_YEAR_FOLDS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_PGR_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_PGR_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_PGR_V1_FROZEN_PROTOTYPES_2026-10-04.json"

YEARS=[2024,2025,2026]
FEATURES=[
"opposite_extreme_recency","gc_volume_accel_5","gc_dlog_volume_1",
"path_consistency","v5_confidence","trend_strength"
]

def load():
    p=pd.read_csv(PRED); f=pd.read_csv(FEAT)
    for d in [p,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    z=p.merge(f[["feature_cutoff_date"]+FEATURES+["signed_opt_pressure","signed_d_opt_pressure"]],
              on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z[z.year.isin(YEARS)].copy()
    z["oar"]=(z.p_rte>=.60)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
    return z.sort_values("forecast_issue_date").reset_index(drop=True)

def fit_proto(train):
    q=train[train.oar].dropna(subset=FEATURES).copy()
    mu=q[FEATURES].mean()
    sd=q[FEATURES].std(ddof=0).replace(0,1.0)
    zz=(q[FEATURES]-mu)/sd
    resc=zz[q.rescue_target.astype(int)==1]
    brok=zz[q.rescue_target.astype(int)==0]
    if len(resc)<3 or len(brok)<3:
        raise RuntimeError(f"INSUFFICIENT_PROTOTYPE_SUPPORT rescue={len(resc)} broken={len(brok)}")
    return mu,sd,resc.median(),brok.median(),len(q),len(resc),len(brok)

def apply_proto(test,mu,sd,rp,bp):
    q=test.copy()
    X=(q[FEATURES]-mu)/sd
    dr=(X-rp).abs().sum(axis=1)
    db=(X-bp).abs().sum(axis=1)
    q["prototype_margin"]=db-dr
    q["prototype_trusted"]=q.oar&(q.prototype_margin>0)
    return q

def met(q,col):
    c=q[col].astype(bool)
    y=q.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "candidate_n":n,"rescued":r,"broken":b,"net_rescue":r-b,
        "precision":r/max(n,1),"rate":n/max(len(q),1)
    }

def main():
    z=load()
    rows=[]
    pooled=[]
    for y in YEARS:
        train=z[z.year!=y].copy()
        test=z[z.year==y].copy()
        mu,sd,rp,bp,ntrain,nr,nb=fit_proto(train)
        q=apply_proto(test,mu,sd,rp,bp)
        base=met(q,"oar")
        guard=met(q,"prototype_trusted")
        rows.append({
            "heldout_year":y,"eligible_n":len(q),
            "train_oar_n":ntrain,"train_rescue_n":nr,"train_broken_n":nb,
            **{f"oar_{k}":v for k,v in base.items()},
            **{f"guard_{k}":v for k,v in guard.items()}
        })
        pooled.append(q)

    rdf=pd.DataFrame(rows)
    rdf.to_csv(OUT_FOLDS,index=False)
    allq=pd.concat(pooled,ignore_index=True)
    g=met(allq,"prototype_trusted")
    nonneg=int((rdf.guard_net_rescue>=0).sum())
    worst=int(rdf.guard_net_rescue.min())
    viable=bool(
        g["candidate_n"]>=10 and g["net_rescue"]>0 and g["precision"]>=.60
        and nonneg>=2 and worst>=-1
    )

    frozen=None
    if viable:
        mu,sd,rp,bp,ntrain,nr,nb=fit_proto(z)
        frozen={
            "schema":"PGR_H3_V1_FROZEN_PROTOTYPES_V1",
            "frozen_at":"2026-10-04",
            "first_prospective_feature_cutoff":"2026-10-05",
            "base_oar_rule":{
                "p_rte_min":0.60,"p_inst_min":0.50,
                "signed_opt_pressure_gt":0.0,"signed_d_opt_pressure_gt":0.0
            },
            "features":FEATURES,
            "scaler_mean":{c:float(mu[c]) for c in FEATURES},
            "scaler_std":{c:float(sd[c]) for c in FEATURES},
            "rescue_median_z":{c:float(rp[c]) for c in FEATURES},
            "broken_median_z":{c:float(bp[c]) for c in FEATURES},
            "training_oar_n":ntrain,"training_rescue_n":nr,"training_broken_n":nb,
            "trust_rule":{
                "prototype_margin_gt":0.0,
                "shadow_matured_min":5,
                "recent_window":5,
                "recent_net_min":1,
                "fallback":"HELIOS_V5_DCE"
            },
            "evidence_class":"POST_HOLDOUT_DEVELOPMENT_FROZEN_FOR_PROSPECTIVE_USE"
        }
        OUT_FREEZE.write_text(json.dumps(frozen,indent=2)+"\n")

    summary={
        "schema":"PGR_H3_V1","status":"PROSPECTIVE_FREEZE_READY" if viable else "PGR_DEVELOPMENT_NOT_VIABLE",
        "folds":rows,
        "pooled_guard":g,
        "nonnegative_years":nonneg,"worst_year_net":worst,
        "development_viable":viable,
        "frozen_prototypes":frozen
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# PGR-H3 V1 — PROSPECTIVE GUARDED REVERSAL RESULT","",
           f"**Status:** **{'PROSPECTIVE_FREEZE_READY' if viable else 'PGR_DEVELOPMENT_NOT_VIABLE'}**  ",
           "**Evidence class:** post-holdout development; 2024-2026 cross-year results are not independent holdout evidence.","",
           "## Leave-one-year-out development audit","",
           "| Held-out year | OAR cand | OAR rescue/broken/net | OAR precision | Guard cand | Guard rescue/broken/net | Guard precision |",
           "|---:|---:|---|---:|---:|---|---:|"]
    for r in rdf.itertuples():
        lines.append(
            f"| {r.heldout_year} | {r.oar_candidate_n} | {r.oar_rescued}/{r.oar_broken}/{r.oar_net_rescue:+d} | "
            f"{100*r.oar_precision:.2f}% | {r.guard_candidate_n} | {r.guard_rescued}/{r.guard_broken}/{r.guard_net_rescue:+d} | "
            f"{100*r.guard_precision:.2f}% |"
        )
    lines += ["","## Pooled prototype guard","",
              f"- acted candidates: **{g['candidate_n']}**",
              f"- rescue / broken / net: **{g['rescued']} / {g['broken']} / {g['net_rescue']:+d}**",
              f"- precision: **{100*g['precision']:.2f}%**",
              f"- nonnegative held-out years: **{nonneg}/3**",
              f"- worst held-out year net: **{worst:+d}**",
              f"- development viability: **{'PASS' if viable else 'FAIL'}**"]

    if viable:
        lines += ["","## Prospective freeze","",
                  "- prototype scaler and rescue/broken medians frozen using all matured 2024-2026 development candidates;",
                  "- first prospective feature cutoff: **2026-10-05**;",
                  "- candidate must be OAR and closer to the historical RESCUE prototype than BROKEN prototype;",
                  "- initially **SHADOW ONLY**;",
                  "- live override authority requires at least **5 matured prospective PGR candidates** and recent-5 net >= **+1**;",
                  "- if trust falls below that level, authority automatically returns to SHADOW;",
                  "- fallback remains **HELIOS V5-DCE**."]

    lines += ["","## Governance","",
              "No result in this file is presented as a new 2026 holdout result. The architecture is intended to be frozen now and judged on origins that occur after the freeze."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
