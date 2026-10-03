from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

S1=AX/"GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_ORS_V1_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_ORS_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_STATE=AX/"GOLD_H3_ORS_V1_STATE_DIAGNOSTICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_ORS_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_ORS_V1_RESULT_2026-10-04.md"

MIN_LIB=160
K=40
P_MAX=.10

ZCOLS=[
    "p_v5_cont",
    "v5_confidence",
    "abs_h_ret_12",
    "trend_strength",
    "path_consistency",
    "adverse_excursion",
    "opposite_semivar_share",
    "deceleration_6h",
]

def parse_bool(s):
    if s.dtype==bool:
        return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    s=pd.read_csv(S1)
    f=pd.read_csv(FEAT)
    for d in [s,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns:
                d[c]=pd.to_datetime(d[c])

    keep=[
        "feature_cutoff_date",
        "y_up",
        "v5_confidence",
        "abs_h_ret_12",
        "trend_strength",
        "path_consistency",
        "adverse_excursion",
        "opposite_semivar_share",
        "deceleration_6h",
        "p_helios_v5_dce",
        "momentum_up",
        "eligible_v5_continuation",
        "rescue_target",
        "opal_override_check",
    ]
    z=s.merge(f[keep],on="feature_cutoff_date",how="left",validate="one_to_one",suffixes=("","_f"))

    # Canonical eligible and labels from the feature panel where duplicated.
    for c in ["momentum_up","eligible_v5_continuation","rescue_target"]:
        cf=c+"_f"
        if cf in z.columns:
            z[c]=z[cf]

    if "opal_override_check" not in z.columns and "opal_override_check_f" in z.columns:
        z["opal_override_check"]=z["opal_override_check_f"]
    elif "opal_override_check_f" in z.columns:
        z["opal_override_check"]=z["opal_override_check"].fillna(z["opal_override_check_f"])

    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["eligible_v5_continuation"]=parse_bool(z.eligible_v5_continuation)

    z["p_v5_cont"]=np.where(
        z.momentum_up.astype(int)==1,
        z.p_helios_v5_dce.astype(float),
        1.0-z.p_helios_v5_dce.astype(float)
    )
    z["month_key"]=z.forecast_issue_date.dt.to_period("M").astype(str)
    z=z[z.eligible_v5_continuation].copy()
    z=z.dropna(subset=ZCOLS+["F_reversal","F_continuation","S3","rescue_target"])
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)

    # Identity check already known, but enforce again locally.
    terminal_reversal=(z.y_up.astype(int)!=z.momentum_up.astype(int)).astype(int)
    mismatch=int((terminal_reversal!=z.rescue_target.astype(int)).sum())
    if mismatch:
        raise RuntimeError(f"Identity mismatch in eligible universe: {mismatch}")
    return z

def std_state(train,test):
    mu=train[ZCOLS].mean()
    sd=train[ZCOLS].std(ddof=0).replace(0,1.0)
    A=((train[ZCOLS]-mu)/sd).to_numpy(float)
    B=((test[ZCOLS]-mu)/sd).to_numpy(float)
    return A,B

def replay(z):
    rows=[]
    leak=0
    for mk in sorted(z.month_key.unique()):
        te=z[z.month_key==mk].copy()
        if te.empty:
            continue
        first_cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=z[
            (z.target_end_date_h3<=first_cutoff)
            & (z.forecast_issue_date<first_issue)
        ].copy()

        if len(tr)<MIN_LIB:
            continue
        if (tr.target_end_date_h3>first_cutoff).any():
            leak+=1
            continue

        A,B=std_state(tr,te)
        fr_hist=tr.F_reversal.to_numpy(float)

        for j,r in enumerate(te.itertuples()):
            d=np.sqrt(((A-B[j])**2).sum(axis=1))
            idx=np.argsort(d)[:K]
            neigh_fr=fr_hist[idx]
            cur=float(r.F_reversal)
            p=(1+int((neigh_fr>=cur).sum()))/(K+1)
            surprise=1-p

            dominant=bool(cur>float(r.F_continuation) and cur>float(r.S3))
            high=bool(p<=P_MAX)
            if high and dominant:
                action="FLIP"
            elif high:
                action="DAMP"
            else:
                action="KEEP"

            v5=int(r.v5_pred)
            assisted=1-v5 if action=="FLIP" else v5

            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),
                "month":str(r.month),
                "y_up":int(r.y_up),
                "target_r3":float(r.target_r3),
                "momentum_up":int(r.momentum_up),
                "v5_pred":v5,
                "rescue_target":int(r.rescue_target),
                "opal_candidate":bool(r.opal_candidate),
                "F_reversal":cur,
                "F_continuation":float(r.F_continuation),
                "S3":float(r.S3),
                "p_surprise":float(p),
                "surprise":float(surprise),
                "reversal_dominant":dominant,
                "action":action,
                "flip":action=="FLIP",
                "damp":action=="DAMP",
                "assisted_pred":assisted,
                "v5_correct":v5==int(r.y_up),
                "assisted_correct":assisted==int(r.y_up),
                "neighbor_mean_distance":float(d[idx].mean()),
                "neighbor_max_distance":float(d[idx].max()),
                "neighbor_mean_F_reversal":float(neigh_fr.mean()),
                "neighbor_q90_F_reversal":float(np.quantile(neigh_fr,.90)),
                "train_n":len(tr),
                "train_max_target_end":tr.target_end_date_h3.max(),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True),leak

def block_name(d):
    d=pd.Timestamp(d)
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def metrics(g):
    flip=g.flip.astype(bool)
    resc=int((flip&(g.rescue_target==1)).sum())
    broken=int((flip&(g.rescue_target==0)).sum())
    opalmiss=(g.rescue_target==1)&(~g.opal_candidate)
    return {
        "n":len(g),
        "flip_n":int(flip.sum()),
        "damp_n":int(g.damp.sum()),
        "candidate_rate":float(flip.mean()) if len(g) else np.nan,
        "rescued":resc,
        "broken":broken,
        "net":resc-broken,
        "flip_precision":resc/max(int(flip.sum()),1),
        "v5_accuracy":float(g.v5_correct.mean()),
        "assisted_accuracy":float(g.assisted_correct.mean()),
        "opal_no_candidate_missed_n":int(opalmiss.sum()),
        "hits_opal_no_candidate":int((flip&opalmiss).sum()),
        "mean_neighbor_distance":float(g.neighbor_mean_distance.mean())
    }

def quintile_diag(g):
    q=g.copy()
    q["surprise_quintile"]=pd.qcut(q.surprise,5,labels=False,duplicates="drop")+1
    rows=[]
    for qi,h in q.groupby("surprise_quintile"):
        rows.append({
            "scope":"ALL",
            "surprise_quintile":int(qi),
            "n":len(h),
            "mean_surprise":float(h.surprise.mean()),
            "terminal_reversal_rate":float(h.rescue_target.mean()),
            "dominant_share":float(h.reversal_dominant.mean())
        })
    return rows

def state_diag(g):
    masks=[
        ("HIGH_SURPRISE_DOMINANT",(g.p_surprise<=P_MAX)&g.reversal_dominant),
        ("HIGH_SURPRISE_NONDominant",(g.p_surprise<=P_MAX)&(~g.reversal_dominant)),
        ("LOW_SURPRISE",(g.p_surprise>P_MAX)),
    ]
    rows=[]
    for name,mask in masks:
        h=g[mask]
        rows.append({
            "state":name,
            "n":len(h),
            "terminal_reversal_rate":float(h.rescue_target.mean()) if len(h) else np.nan,
            "mean_F_reversal":float(h.F_reversal.mean()) if len(h) else np.nan,
            "mean_surprise":float(h.surprise.mean()) if len(h) else np.nan,
        })
    return rows

def main():
    z=load()
    pred,leak=replay(z)
    if pred.empty:
        raise RuntimeError("No ORS predictions generated")

    pred["block"]=pred.forecast_issue_date.map(block_name)
    pred.to_csv(OUT_PRED,index=False)

    agg=metrics(pred)
    block_rows=[]
    for b,g in pred.groupby("block",sort=False):
        x=metrics(g);x["block"]=b;block_rows.append(x)
    bdf=pd.DataFrame(block_rows)
    bdf.to_csv(OUT_BLOCK,index=False)

    states=state_diag(pred)
    qrows=quintile_diag(pred)
    sdf=pd.DataFrame(states+qrows)
    sdf.to_csv(OUT_STATE,index=False)

    nblocks=len(bdf)
    need_nonneg=math.ceil(.8*nblocks)
    need_pos=math.ceil(.5*nblocks)
    nonneg=int((bdf.net>=0).sum())
    positive=int((bdf.net>0).sum())
    worst=int(bdf.net.min())

    gate=bool(
        agg["flip_n"]>=8
        and agg["flip_precision"]>=.60
        and agg["net"]>=3
        and agg["candidate_rate"]<=.15
        and agg["assisted_accuracy"]>=agg["v5_accuracy"]+.005
        and nonneg>=need_nonneg
        and positive>=need_pos
        and worst>=-2
        and leak==0
    )
    status="ORS_H3_V1_PROMISING" if gate else "ORS_H3_V1_FAIL"

    summary={
        "schema":"ORS_H3_V1",
        "status":status,
        "prediction_rows":len(pred),
        "first_scored_origin":str(pred.feature_cutoff_date.min().date()),
        "last_scored_origin":str(pred.feature_cutoff_date.max().date()),
        "aggregate":agg,
        "blocks":block_rows,
        "states":states,
        "surprise_quintiles":qrows,
        "nonnegative_blocks":nonneg,
        "nonnegative_required":need_nonneg,
        "positive_blocks":positive,
        "positive_required":need_pos,
        "worst_block_net":worst,
        "maturity_leakage_failures":leak
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# ORS-H3 V1 — ORTHOGONAL REVERSAL SURPRISE RESULT","",
        f"**Status:** **{status}**  ",
        f"- predictions: **{len(pred)}**",
        f"- scored origins: **{summary['first_scored_origin']} .. {summary['last_scored_origin']}**",
        f"- maturity leakage failures: **{leak}**","",
        "## Aggregate","",
        f"- FLIP candidates: **{agg['flip_n']} ({100*agg['candidate_rate']:.2f}%)**",
        f"- DAMP candidates: **{agg['damp_n']}**",
        f"- rescue / broken / net: **{agg['rescued']} / {agg['broken']} / {agg['net']:+d}**",
        f"- FLIP precision: **{100*agg['flip_precision']:.2f}%**",
        f"- V5 -> assisted accuracy: **{100*agg['v5_accuracy']:.2f}% -> {100*agg['assisted_accuracy']:.2f}%**",
        f"- OPAL-no-candidate missed reversals hit: **{agg['hits_opal_no_candidate']}/{agg['opal_no_candidate_missed_n']}**","",
        "## State diagnostic","",
        "| State | N | Terminal reversal | Mean F_R | Mean surprise |",
        "|---|---:|---:|---:|---:|"
    ]
    for x in states:
        lines.append(f"| {x['state']} | {x['n']} | {100*x['terminal_reversal_rate']:.2f}% | {x['mean_F_reversal']:.3f} | {x['mean_surprise']:.3f} |")

    lines += ["","## Half-year stability","",
              "| Block | N | Flip | Damp | Rescue | Broken | Net | Precision | V5 acc | Assisted |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.n} | {r.flip_n} | {r.damp_n} | {r.rescued} | {r.broken} | "
            f"{r.net:+d} | {100*r.flip_precision:.1f}% | {100*r.v5_accuracy:.1f}% | {100*r.assisted_accuracy:.1f}% |"
        )

    lines += ["","## Gate","",
              f"- non-negative blocks: **{nonneg}/{nblocks}** (required {need_nonneg})",
              f"- positive blocks: **{positive}/{nblocks}** (required {need_pos})",
              f"- worst block net: **{worst:+d}**"]
    if gate:
        lines += [
            "- ORS V1 passed the frozen development gate.",
            "- A separate prospective freeze is required before any clean claim."
        ]
    else:
        lines += [
            "- ORS V1 failed the frozen development gate.",
            "- K and surprise threshold must not be tuned on this same replay."
        ]

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
