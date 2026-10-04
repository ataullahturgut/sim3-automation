from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

PANEL=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"

OUT_PRED=AX/"GOLD_H3_CDE_V1_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_CDE_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_CDE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_CDE_V1_RESULT_2026-10-04.md"

GAPS=[
    "cf_deceleration_6h_gap",
    "cf_opposite_semivar_share_gap",
    "cf_adverse_excursion_gap",
    "cf_signed_opt_pressure_gap",
    "cf_signed_d_opt_pressure_gap",
    "cf_opt_total_z20_gap",
]

def as_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def block_name(d):
    d=pd.Timestamp(d)
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def load():
    p=pd.read_csv(PANEL)
    s=pd.read_csv(SAGE)
    for d in [p,s]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","cme_trade_date"]:
            if c in d.columns:
                d[c]=pd.to_datetime(d[c],errors="coerce")

    if p.feature_cutoff_date.duplicated().any():
        raise RuntimeError("Duplicate feature_cutoff_date in RTE panel")
    if s.feature_cutoff_date.duplicated().any():
        raise RuntimeError("Duplicate feature_cutoff_date in SAGE ledger")

    p["eligible_v5_continuation"]=as_bool(p.eligible_v5_continuation)
    p["opal_candidate"]=as_bool(p.opal_override_check)

    complete=p[GAPS].notna().all(axis=1)
    z=p[p.eligible_v5_continuation & complete].copy()
    if z.empty:
        raise RuntimeError("No complete-gap eligible rows")

    # Source chronology inherited from RTE: prior CME trade date only.
    leak=int((z.cme_trade_date>=z.feature_cutoff_date).fillna(False).sum())
    if leak:
        raise RuntimeError(f"CME chronology failure count={leak}")

    # Structural sign-concurrence, frozen in prereg.
    vote_cols=[]
    for c in GAPS:
        vc="vote_"+c.replace("cf_","").replace("_gap","")
        z[vc]=z[c].astype(float)>0
        vote_cols.append(vc)
    z["cde_count"]=z[vote_cols].sum(axis=1).astype(int)
    z["cde_candidate"]=z.cde_count>=5

    # OCS coverage/candidate from frozen SAGE development ledger.
    sm=s[["feature_cutoff_date","action"]].copy()
    sm["ocs_covered"]=True
    sm["ocs_candidate"]=sm.action.astype(str).eq("FLIP")
    z=z.merge(sm[["feature_cutoff_date","ocs_covered","ocs_candidate"]],
              on="feature_cutoff_date",how="left",validate="one_to_one")
    z["ocs_covered"]=z.ocs_covered.fillna(False).astype(bool)
    z["ocs_candidate"]=z.ocs_candidate.fillna(False).astype(bool)

    v5=z.v5_pred.astype(int).to_numpy()
    y=z.y_up.astype(int).to_numpy()
    cde=z.cde_candidate.to_numpy(bool)
    assisted=np.where(cde,1-v5,v5)
    z["cde_pred"]=assisted
    z["v5_correct"]=v5==y
    z["cde_correct"]=assisted==y
    z["block"]=z.forecast_issue_date.map(block_name)
    return z,leak

def metrics(g):
    c=g.cde_candidate.astype(bool)
    resc=int((c&(g.rescue_target==1)).sum())
    broken=int((c&(g.rescue_target==0)).sum())
    return {
        "n":len(g),
        "candidate_n":int(c.sum()),
        "candidate_rate":float(c.mean()) if len(g) else np.nan,
        "rescued":resc,
        "broken":broken,
        "net":resc-broken,
        "precision":resc/max(int(c.sum()),1),
        "v5_accuracy":float(g.v5_correct.mean()),
        "assisted_accuracy":float(g.cde_correct.mean()),
        "opal_no_candidate_missed_n":int(((g.rescue_target==1)&(~g.opal_candidate)).sum()),
        "hits_opal_no_candidate":int((c&(g.rescue_target==1)&(~g.opal_candidate)).sum()),
    }

def main():
    z,leak=load()
    z.to_csv(OUT_PRED,index=False)

    agg=metrics(z)
    blocks=[]
    for b,g in z.groupby("block",sort=False):
        x=metrics(g);x["block"]=b;blocks.append(x)
    bdf=pd.DataFrame(blocks)
    bdf.to_csv(OUT_BLOCK,index=False)

    # Complementarity within OCS mature coverage only.
    common=z[z.ocs_covered].copy()
    cde=common.cde_candidate.astype(bool)
    ocs=common.ocs_candidate.astype(bool)
    rescue=common.rescue_target.astype(int)==1

    cde_only=cde&(~ocs)
    ocs_only=ocs&(~cde)
    overlap=cde&ocs
    union=cde|ocs

    def rb(mask):
        r=int((mask&rescue).sum())
        b=int((mask&(~rescue)).sum())
        return {"n":int(mask.sum()),"rescued":r,"broken":b,"net":r-b,
                "precision":r/max(int(mask.sum()),1)}

    complement={
        "common_rows":len(common),
        "cde_only":rb(cde_only),
        "ocs_only":rb(ocs_only),
        "overlap":rb(overlap),
        "union":rb(union),
        "incremental_true_cde_only":int((cde_only&rescue).sum())
    }

    nblocks=len(bdf)
    need_nonneg=math.ceil(.75*nblocks)
    need_pos=math.ceil(.50*nblocks)
    nonneg=int((bdf.net>=0).sum())
    positive=int((bdf.net>0).sum())
    worst=int(bdf.net.min())

    gate=bool(
        agg["candidate_n"]>=8
        and agg["precision"]>=.60
        and agg["net"]>=3
        and agg["candidate_rate"]<=.15
        and nonneg>=need_nonneg
        and positive>=need_pos
        and worst>=-2
        and complement["incremental_true_cde_only"]>=2
        and leak==0
    )
    status="CDE_H3_V1_PROMISING" if gate else "CDE_H3_V1_FAIL"

    summary={
        "schema":"CDE_H3_V1",
        "status":status,
        "historical_status":"development_only",
        "first_complete_origin":str(z.feature_cutoff_date.min().date()),
        "last_complete_origin":str(z.feature_cutoff_date.max().date()),
        "complete_eligible_rows":len(z),
        "leakage_failures":leak,
        "aggregate":agg,
        "blocks":blocks,
        "nonnegative_blocks":nonneg,
        "nonnegative_required":need_nonneg,
        "positive_blocks":positive,
        "positive_required":need_pos,
        "worst_block_net":worst,
        "complementarity_vs_ocs":complement,
        "rule":"at least 5 of 6 frozen counterfactual reversal-oriented gaps > 0"
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# CDE-H3 V1 — COUNTERFACTUAL DISLOCATION EXCEPTION RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective development only.","",
        f"- complete eligible rows: **{len(z)}**",
        f"- coverage: **{summary['first_complete_origin']} .. {summary['last_complete_origin']}**",
        f"- chronology/leakage failures: **{leak}**","",
        "## Aggregate CDE","",
        f"- candidates: **{agg['candidate_n']} ({100*agg['candidate_rate']:.2f}%)**",
        f"- rescue / broken / net: **{agg['rescued']} / {agg['broken']} / {agg['net']:+d}**",
        f"- precision: **{100*agg['precision']:.2f}%**",
        f"- V5 -> CDE-assisted: **{100*agg['v5_accuracy']:.2f}% -> {100*agg['assisted_accuracy']:.2f}%**",
        f"- OPAL-no-candidate missed reversals hit: **{agg['hits_opal_no_candidate']}/{agg['opal_no_candidate_missed_n']}**","",
        "## Half-year stability","",
        "| Block | N | Cand | Rescue | Broken | Net | Precision | V5 acc | Assisted |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.n} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net:+d} | "
            f"{100*r.precision:.1f}% | {100*r.v5_accuracy:.1f}% | {100*r.assisted_accuracy:.1f}% |"
        )

    lines += ["","## Complementarity vs frozen OCS (common mature coverage)","",
              f"- common rows: **{complement['common_rows']}**"]
    for k in ["cde_only","ocs_only","overlap","union"]:
        x=complement[k]
        lines.append(
            f"- {k}: **{x['n']}** candidates, rescue/broken/net **{x['rescued']}/{x['broken']}/{x['net']:+d}**, precision **{100*x['precision']:.1f}%**"
        )
    lines += [
        f"- incremental true CDE-only rescues: **{complement['incremental_true_cde_only']}**","",
        "## Gate","",
        f"- non-negative blocks: **{nonneg}/{nblocks}** (required {need_nonneg})",
        f"- positive blocks: **{positive}/{nblocks}** (required {need_pos})",
        f"- worst block net: **{worst:+d}**"
    ]
    if gate:
        lines += [
            "- CDE passed the frozen development gate.",
            "- It is a candidate independent exception channel, but still needs a separate prospective freeze."
        ]
    else:
        lines += [
            "- CDE failed the frozen development gate.",
            "- The 5/6 concurrence and signs must not be retuned on this same replay."
        ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
