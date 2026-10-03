from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

IFBC=AX/"GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv"
LLRS=AX/"GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv"
TRES=AX/"GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv"

OUT_PRED=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_SAGE_SELECTIVE_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_SAGE_SELECTIVE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_SAGE_SELECTIVE_V1_RESULT_2026-10-04.md"

START=pd.Timestamp("2025-07-01")

def as_bool(s):
    if s.dtype==bool:
        return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def parse_dates(df):
    for c in [
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "hourly_cutoff","hourly_source_ts","hourly_last_ts","train_max_target_end"
    ]:
        if c in df.columns:
            df[c]=pd.to_datetime(df[c],errors="coerce",utc=("hourly_" in c))
    return df

def load():
    i=parse_dates(pd.read_csv(IFBC))
    l=parse_dates(pd.read_csv(LLRS))
    t=parse_dates(pd.read_csv(TRES))

    dup_i=int(i.feature_cutoff_date.duplicated().sum())
    dup_l=int(l.feature_cutoff_date.duplicated().sum())
    dup_t=int(t.feature_cutoff_date.duplicated().sum())
    if dup_i or dup_l or dup_t:
        raise RuntimeError(f"Duplicate keys IFBC={dup_i}, LLRS={dup_l}, TRES={dup_t}")

    req_i=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "y_up","momentum_up","v5_pred","rescue_target",
        "ifbc_score","ifbc_count60","hourly_last_ts"
    ]
    req_l=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "y_up","momentum_up","v5_pred","rescue_target",
        "llrs_pressure","llrs_incremental","llrs_external_opposes",
        "hourly_cutoff","hourly_source_ts"
    ]
    req_t=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "terminal_reversal","eligible_v5_continuation","rescue_target",
        "v5_pred","p_v5","F_reversal","F_continuation","S3",
        "train_max_target_end"
    ]
    for name,df,req in [("IFBC",i,req_i),("LLRS",l,req_l),("TRES",t,req_t)]:
        miss=[c for c in req if c not in df.columns]
        if miss:
            raise RuntimeError(f"{name} missing columns: {miss}")

    i2=i[req_i].rename(columns={
        "forecast_issue_date":"ifbc_issue",
        "target_end_date_h3":"ifbc_target_end",
        "y_up":"ifbc_y",
        "momentum_up":"ifbc_mom",
        "v5_pred":"ifbc_v5",
        "rescue_target":"ifbc_rescue",
    })
    l2=l[req_l].rename(columns={
        "forecast_issue_date":"llrs_issue",
        "target_end_date_h3":"llrs_target_end",
        "y_up":"llrs_y",
        "momentum_up":"llrs_mom",
        "v5_pred":"llrs_v5",
        "rescue_target":"llrs_rescue",
    })
    t2=t[req_t].copy()

    z=t2.merge(i2,on="feature_cutoff_date",how="inner",validate="one_to_one")
    z=z.merge(l2,on="feature_cutoff_date",how="inner",validate="one_to_one")
    z=z[z.forecast_issue_date>=START].copy()
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)

    mismatch=0
    mismatch += int((z.ifbc_issue.dt.date != z.forecast_issue_date.dt.date).sum())
    mismatch += int((z.llrs_issue.dt.date != z.forecast_issue_date.dt.date).sum())
    mismatch += int((z.ifbc_target_end.dt.date != z.target_end_date_h3.dt.date).sum())
    mismatch += int((z.llrs_target_end.dt.date != z.target_end_date_h3.dt.date).sum())
    mismatch += int((z.ifbc_y.astype(int) != z.llrs_y.astype(int)).sum())
    mismatch += int((z.ifbc_mom.astype(int) != z.llrs_mom.astype(int)).sum())
    mismatch += int((z.ifbc_v5.astype(int) != z.v5_pred.astype(int)).sum())
    mismatch += int((z.llrs_v5.astype(int) != z.v5_pred.astype(int)).sum())
    mismatch += int((z.ifbc_rescue.astype(int) != z.rescue_target.astype(int)).sum())
    mismatch += int((z.llrs_rescue.astype(int) != z.rescue_target.astype(int)).sum())

    y=z.ifbc_y.astype(int)
    mom=z.ifbc_mom.astype(int)
    elig=(z.v5_pred.astype(int)==mom)
    identity=(z.rescue_target.astype(int)==((z.v5_pred.astype(int)!=y).astype(int)))
    mismatch += int((~identity).sum())

    leak=0
    if "train_max_target_end" in z.columns:
        leak += int((z.train_max_target_end.dt.tz_localize(None) > z.feature_cutoff_date).sum())
    leak += int((z.hourly_source_ts > z.hourly_cutoff).fillna(False).sum())
    ifbc_last_date=z.hourly_last_ts.dt.tz_convert(None).dt.normalize()
    leak += int((ifbc_last_date > z.feature_cutoff_date.dt.normalize()).fillna(False).sum())

    if mismatch:
        raise RuntimeError(f"SAGE source identity mismatch count={mismatch}")
    if leak:
        raise RuntimeError(f"SAGE source leakage check failed count={leak}")

    z["momentum_up"]=mom
    z["y_up"]=y
    z["eligible_v5_continuation"]=elig

    z["ifbc_condition"]=(z.ifbc_count60.astype(float)>=4) & (z.ifbc_score.astype(float)>=.70)
    z["llrs_condition"]=(
        as_bool(z.llrs_external_opposes)
        & (z.llrs_incremental.astype(float)>0)
        & (z.llrs_pressure.astype(float)>=.10)
    )
    z["ocs_candidate"]=z.ifbc_condition & z.llrs_condition & z.eligible_v5_continuation

    z["tres_continuation_safe"]=(
        z.F_continuation.astype(float)>=z.F_reversal.astype(float)
    ) & (
        z.F_continuation.astype(float)>=z.S3.astype(float)
    )

    actions=[]
    assisted=[]
    for r in z.itertuples():
        v5=int(r.v5_pred)
        if not bool(r.eligible_v5_continuation):
            a="KEEP"
            pred=v5
        elif bool(r.ocs_candidate):
            a="FLIP"
            pred=1-v5
        elif bool(r.tres_continuation_safe):
            a="KEEP"
            pred=v5
        else:
            a="ABSTAIN"
            pred=v5
        actions.append(a)
        assisted.append(pred)

    z["action"]=actions
    z["assisted_pred_forced"]=assisted
    z["v5_correct"]=z.v5_pred.astype(int)==z.y_up.astype(int)
    z["assisted_correct_forced"]=z.assisted_pred_forced.astype(int)==z.y_up.astype(int)
    z["block"]=z.forecast_issue_date.map(lambda d:f"{d.year}_{'H1' if d.month<=6 else 'H2'}")
    return z,mismatch,leak

def metrics(g):
    flip=g.action=="FLIP"
    abst=g.action=="ABSTAIN"
    keep=g.action=="KEEP"
    action=~abst

    resc=int((flip&(g.rescue_target==1)).sum())
    broken=int((flip&(g.rescue_target==0)).sum())

    acted_correct=np.where(
        g.loc[action,"action"].to_numpy()=="FLIP",
        g.loc[action,"assisted_correct_forced"].to_numpy(bool),
        g.loc[action,"v5_correct"].to_numpy(bool)
    ) if action.any() else np.array([],dtype=bool)

    return {
        "n":len(g),
        "flip_n":int(flip.sum()),
        "rescued":resc,
        "broken":broken,
        "net":resc-broken,
        "flip_precision":resc/max(int(flip.sum()),1),
        "keep_n":int(keep.sum()),
        "abstain_n":int(abst.sum()),
        "action_n":int(action.sum()),
        "action_coverage":float(action.mean()) if len(g) else np.nan,
        "action_accuracy":float(acted_correct.mean()) if len(acted_correct) else np.nan,
        "keep_accuracy":float(g.loc[keep,"v5_correct"].mean()) if keep.any() else np.nan,
        "abstain_v5_accuracy":float(g.loc[abst,"v5_correct"].mean()) if abst.any() else np.nan,
        "v5_accuracy":float(g.v5_correct.mean()) if len(g) else np.nan,
        "forced_assisted_accuracy":float(g.assisted_correct_forced.mean()) if len(g) else np.nan,
    }

def main():
    z,mismatch,leak=load()
    if z.empty:
        raise RuntimeError("No common mature SAGE coverage")
    z.to_csv(OUT_PRED,index=False)

    agg=metrics(z)
    blocks=[]
    for b,g in z.groupby("block",sort=False):
        x=metrics(g);x["block"]=b;blocks.append(x)
    bdf=pd.DataFrame(blocks)
    bdf.to_csv(OUT_BLOCK,index=False)

    nblocks=len(bdf)
    positive=int((bdf.net>0).sum())
    nonnegative=int((bdf.net>=0).sum())
    worst=int(bdf.net.min())

    gate=bool(
        agg["flip_n"]>=6
        and agg["flip_precision"]>=.60
        and agg["net"]>=3
        and nonnegative==nblocks
        and positive>=2
        and worst>=0
        and agg["action_coverage"]>=.50
        and agg["action_accuracy"]>=.70
        and agg["action_accuracy"]>agg["v5_accuracy"]
        and (np.isnan(agg["abstain_v5_accuracy"]) or agg["abstain_v5_accuracy"]<agg["action_accuracy"])
        and mismatch==0
        and leak==0
    )
    status="SAGE_H3_V1_DEVELOPMENT_PASS" if gate else "SAGE_H3_V1_FAIL"

    summary={
        "schema":"SAGE_H3_SELECTIVE_V1",
        "status":status,
        "historical_status":"development_only",
        "first_scored_origin":str(z.feature_cutoff_date.min().date()),
        "last_scored_origin":str(z.feature_cutoff_date.max().date()),
        "common_rows":len(z),
        "source_identity_mismatches":mismatch,
        "leakage_failures":leak,
        "aggregate":agg,
        "blocks":blocks,
        "positive_blocks":positive,
        "nonnegative_blocks":nonnegative,
        "worst_block_net":worst,
        "ocs_rule":{
            "ifbc_count60_min":4,
            "ifbc_score_min":.70,
            "llrs_external_opposes":True,
            "llrs_incremental_gt":0,
            "llrs_pressure_min":.10
        },
        "tres_rule":"F_continuation >= max(F_reversal,S3)"
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SAGE-H3 V1 — SELECTIVE ACTION + GUARDED EXCEPTION RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective development only; no clean historical promotion claim.","",
        f"- common mature rows: **{len(z)}**",
        f"- scored origins: **{summary['first_scored_origin']} .. {summary['last_scored_origin']}**",
        f"- source identity mismatches: **{mismatch}**",
        f"- leakage failures: **{leak}**","",
        "## Aggregate","",
        f"- OCS FLIP candidates: **{agg['flip_n']}**",
        f"- rescue / broken / net: **{agg['rescued']} / {agg['broken']} / {agg['net']:+d}**",
        f"- FLIP precision: **{100*agg['flip_precision']:.2f}%**",
        f"- KEEP: **{agg['keep_n']}**",
        f"- ABSTAIN: **{agg['abstain_n']}**",
        f"- selective action coverage: **{100*agg['action_coverage']:.2f}%**",
        f"- selective action accuracy: **{100*agg['action_accuracy']:.2f}%**",
        f"- KEEP accuracy: **{100*agg['keep_accuracy']:.2f}%**",
        f"- ABSTAIN rows — counterfactual V5 accuracy: **{100*agg['abstain_v5_accuracy']:.2f}%**",
        f"- full V5 accuracy: **{100*agg['v5_accuracy']:.2f}%**",
        f"- forced full-direction assisted accuracy: **{100*agg['forced_assisted_accuracy']:.2f}%**","",
        "## Half-year blocks","",
        "| Block | N | Flip | Rescue | Broken | Net | Flip precision | Abstain | Coverage | Action acc | V5 acc | Forced assisted |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.n} | {r.flip_n} | {r.rescued} | {r.broken} | {r.net:+d} | "
            f"{100*r.flip_precision:.1f}% | {r.abstain_n} | {100*r.action_coverage:.1f}% | "
            f"{100*r.action_accuracy:.1f}% | {100*r.v5_accuracy:.1f}% | {100*r.forced_assisted_accuracy:.1f}% |"
        )

    lines += ["","## Gate","",
              f"- positive FLIP-net blocks: **{positive}/{nblocks}**",
              f"- non-negative FLIP-net blocks: **{nonnegative}/{nblocks}**",
              f"- worst block FLIP net: **{worst:+d}**"]
    if gate:
        lines += [
            "- SAGE V1 passed the frozen development gate.",
            "- The architecture is eligible for a separately frozen prospective shadow evaluation.",
            "- HELIOS V5-DCE remains binding until prospective promotion criteria are met."
        ]
    else:
        lines += [
            "- SAGE V1 failed at least one frozen development criterion.",
            "- No threshold or action rule may be tuned on this same replay."
        ]

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: sage-selective-v1-ready
