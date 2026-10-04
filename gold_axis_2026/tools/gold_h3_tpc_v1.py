from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

IFBC=AX/"GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv"
LLRS=AX/"GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv"

OUT_PRED=AX/"GOLD_H3_TPC_V1_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_TPC_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_TPC_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_TPC_V1_RESULT_2026-10-04.md"

START=pd.Timestamp("2025-07-01")

def b(x):
    if x.dtype==bool:
        return x
    return x.astype(str).str.lower().isin(["true","1","yes"])

def dates(df):
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","hourly_cutoff","hourly_source_ts","hourly_last_ts"]:
        if c in df.columns:
            df[c]=pd.to_datetime(df[c],errors="coerce",utc=("hourly_" in c))
    return df

def load():
    i=dates(pd.read_csv(IFBC))
    l=dates(pd.read_csv(LLRS))

    req_i=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "y_up","momentum_up","v5_pred","rescue_target","opal_override_check",
        "ifbc_score","ifbc_count60",
        "gc_opp_vol_share_3","gc_opp_vol_share_12",
        "gc_flow_3","gc_flow_12",
        "gc_late_rejection_3","si_late_rejection_3",
        "gc_efficiency_6","gc_efficiency_12",
        "hourly_last_ts"
    ]
    req_l=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "y_up","momentum_up","v5_pred","rescue_target",
        "llrs_pressure","llrs_incremental","llrs_external_opposes",
        "hourly_cutoff","hourly_source_ts"
    ]
    for name,df,req in [("IFBC",i,req_i),("LLRS",l,req_l)]:
        miss=[c for c in req if c not in df.columns]
        if miss:
            raise RuntimeError(f"{name} missing {miss}")
        if df.feature_cutoff_date.duplicated().any():
            raise RuntimeError(f"{name} duplicate feature_cutoff_date")

    ii=i[req_i].copy().rename(columns={
        "forecast_issue_date":"forecast_issue_date_i",
        "target_end_date_h3":"target_end_date_i",
        "y_up":"y_i","momentum_up":"mom_i","v5_pred":"v5_i",
        "rescue_target":"rescue_i",
    })
    ll=l[req_l].copy().rename(columns={
        "forecast_issue_date":"forecast_issue_date_l",
        "target_end_date_h3":"target_end_date_l",
        "y_up":"y_l","momentum_up":"mom_l","v5_pred":"v5_l",
        "rescue_target":"rescue_l",
    })

    z=ii.merge(ll,on="feature_cutoff_date",how="inner",validate="one_to_one")
    z=z[z.forecast_issue_date_i>=START].copy().sort_values("forecast_issue_date_i").reset_index(drop=True)

    mismatch=0
    mismatch+=int((z.forecast_issue_date_i.dt.date!=z.forecast_issue_date_l.dt.date).sum())
    mismatch+=int((z.target_end_date_i.dt.date!=z.target_end_date_l.dt.date).sum())
    mismatch+=int((z.y_i.astype(int)!=z.y_l.astype(int)).sum())
    mismatch+=int((z.mom_i.astype(int)!=z.mom_l.astype(int)).sum())
    mismatch+=int((z.v5_i.astype(int)!=z.v5_l.astype(int)).sum())
    mismatch+=int((z.rescue_i.astype(int)!=z.rescue_l.astype(int)).sum())
    if mismatch:
        raise RuntimeError(f"source identity mismatch={mismatch}")

    leak=0
    leak+=int((z.hourly_source_ts>z.hourly_cutoff).fillna(False).sum())
    last=z.hourly_last_ts.dt.tz_convert(None).dt.normalize()
    leak+=int((last>z.feature_cutoff_date.dt.normalize()).fillna(False).sum())
    if leak:
        raise RuntimeError(f"source leakage failures={leak}")

    z["forecast_issue_date"]=z.forecast_issue_date_i
    z["target_end_date_h3"]=z.target_end_date_i
    z["y_up"]=z.y_i.astype(int)
    z["momentum_up"]=z.mom_i.astype(int)
    z["v5_pred"]=z.v5_i.astype(int)
    z["rescue_target"]=z.rescue_i.astype(int)
    z["eligible_v5_continuation"]=z.v5_pred==z.momentum_up

    z["flag_opp_accel"]=z.gc_opp_vol_share_3>z.gc_opp_vol_share_12
    z["flag_flow_deterioration"]=z.gc_flow_3<z.gc_flow_12
    z["flag_gc_rejection"]=z.gc_late_rejection_3>0
    z["flag_si_rejection"]=z.si_late_rejection_3>0
    z["flag_efficiency_decay"]=z.gc_efficiency_6<z.gc_efficiency_12

    flags=[
        "flag_opp_accel","flag_flow_deterioration","flag_gc_rejection",
        "flag_si_rejection","flag_efficiency_decay"
    ]
    z["propagation_count"]=z[flags].astype(int).sum(axis=1)

    z["external_stress"]=(
        b(z.llrs_external_opposes)
        & (z.llrs_incremental.astype(float)>0)
        & (z.llrs_pressure.astype(float)>=.10)
    )
    z["tpc_candidate"]=(
        z.eligible_v5_continuation
        & z.external_stress
        & (z.propagation_count>=3)
    )

    z["ocs_candidate"]=(
        z.eligible_v5_continuation
        & (z.ifbc_count60.astype(float)>=4)
        & (z.ifbc_score.astype(float)>=.70)
        & z.external_stress
    )

    z["tpc_only"]=z.tpc_candidate & (~z.ocs_candidate)
    z["ocs_only"]=z.ocs_candidate & (~z.tpc_candidate)
    z["overlap"]=z.tpc_candidate & z.ocs_candidate
    z["union_candidate"]=z.tpc_candidate | z.ocs_candidate

    z["tpc_pred"]=np.where(z.tpc_candidate,1-z.v5_pred,z.v5_pred)
    z["union_pred"]=np.where(z.union_candidate,1-z.v5_pred,z.v5_pred)
    z["v5_correct"]=z.v5_pred==z.y_up
    z["tpc_correct"]=z.tpc_pred==z.y_up
    z["union_correct"]=z.union_pred==z.y_up
    z["opal_candidate"]=b(z.opal_override_check)
    z["block"]=z.forecast_issue_date.map(lambda d:f"{d.year}_{'H1' if d.month<=6 else 'H2'}")
    return z,mismatch,leak

def cand_stats(g,col):
    c=g[col].astype(bool)
    resc=int((c&(g.rescue_target==1)).sum())
    broken=int((c&(g.rescue_target==0)).sum())
    n=int(c.sum())
    return {
        "candidate_n":n,
        "rescued":resc,
        "broken":broken,
        "net":resc-broken,
        "precision":resc/max(n,1),
        "candidate_rate":n/max(int(g.eligible_v5_continuation.sum()),1),
        "opal_no_candidate_rescues":int((c&(g.rescue_target==1)&(~g.opal_candidate)).sum()),
    }

def block_stats(z):
    rows=[]
    for block,g in z.groupby("block",sort=False):
        x=cand_stats(g,"tpc_candidate")
        x["block"]=block
        x["eligible_n"]=int(g.eligible_v5_continuation.sum())
        x["v5_accuracy"]=float(g.v5_correct.mean())
        x["tpc_accuracy"]=float(g.tpc_correct.mean())
        rows.append(x)
    return pd.DataFrame(rows)

def main():
    z,mismatch,leak=load()
    if z.empty:
        raise RuntimeError("no common rows")
    z.to_csv(OUT_PRED,index=False)

    tpc=cand_stats(z,"tpc_candidate")
    ocs=cand_stats(z,"ocs_candidate")
    only=cand_stats(z,"tpc_only")
    oonly=cand_stats(z,"ocs_only")
    overlap=cand_stats(z,"overlap")
    union=cand_stats(z,"union_candidate")

    bdf=block_stats(z)
    bdf.to_csv(OUT_BLOCK,index=False)

    positive=int((bdf.net>0).sum())
    worst=int(bdf.net.min()) if len(bdf) else 0

    gate=bool(
        tpc["candidate_n"]>=8
        and tpc["precision"]>=.60
        and tpc["net"]>=3
        and tpc["candidate_rate"]<=.12
        and worst>=-1
        and positive>=2
        and only["net"]>=0
        and union["net"]>ocs["net"]
        and mismatch==0
    )
    status="TPC_H3_V1_PROMISING" if gate else "TPC_H3_V1_FAIL"

    summary={
        "schema":"TPC_H3_V1",
        "status":status,
        "historical_status":"development_only",
        "rows":len(z),
        "first_issue":str(z.forecast_issue_date.min().date()),
        "last_issue":str(z.forecast_issue_date.max().date()),
        "source_identity_mismatches":mismatch,
        "leakage_failures":leak,
        "tpc":tpc,
        "ocs_reference":ocs,
        "tpc_only":only,
        "ocs_only":oonly,
        "overlap":overlap,
        "union":union,
        "v5_accuracy":float(z.v5_correct.mean()),
        "tpc_assisted_accuracy":float(z.tpc_correct.mean()),
        "union_assisted_accuracy":float(z.union_correct.mean()),
        "positive_blocks":positive,
        "worst_block_net":worst,
        "blocks":bdf.to_dict("records"),
        "flag_prevalence":{c:float(z[c].mean()) for c in [
            "flag_opp_accel","flag_flow_deterioration","flag_gc_rejection",
            "flag_si_rejection","flag_efficiency_decay"
        ]}
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# TPC-H3 V1 — TEMPORAL PROPAGATION CONCURRENCE RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective development/stress-test only.","",
        f"- common rows: **{len(z)}**",
        f"- issue dates: **{summary['first_issue']} .. {summary['last_issue']}**",
        f"- identity mismatches: **{mismatch}**",
        f"- leakage failures: **{leak}**","",
        "## TPC","",
        f"- candidates: **{tpc['candidate_n']}**",
        f"- rescue / broken / net: **{tpc['rescued']} / {tpc['broken']} / {tpc['net']:+d}**",
        f"- precision: **{100*tpc['precision']:.2f}%**",
        f"- candidate rate: **{100*tpc['candidate_rate']:.2f}%**",
        f"- V5 -> TPC-assisted accuracy: **{100*summary['v5_accuracy']:.2f}% -> {100*summary['tpc_assisted_accuracy']:.2f}%**","",
        "## Increment over OCS","",
        f"- OCS reference: **{ocs['candidate_n']} candidates, net {ocs['net']:+d}, precision {100*ocs['precision']:.2f}%**",
        f"- TPC-only: **{only['candidate_n']} candidates, {only['rescued']}/{only['broken']}, net {only['net']:+d}**",
        f"- OCS-only: **{oonly['candidate_n']} candidates, {oonly['rescued']}/{oonly['broken']}, net {oonly['net']:+d}**",
        f"- overlap: **{overlap['candidate_n']} candidates, net {overlap['net']:+d}**",
        f"- union: **{union['candidate_n']} candidates, net {union['net']:+d}, precision {100*union['precision']:.2f}%**",
        f"- V5 -> union-assisted accuracy: **{100*summary['v5_accuracy']:.2f}% -> {100*summary['union_assisted_accuracy']:.2f}%**","",
        "## Half-year stability","",
        "| Block | Eligible | Cand | Rescue | Broken | Net | Precision | V5 acc | TPC acc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.eligible_n} | {r.candidate_n} | {r.rescued} | {r.broken} | "
            f"{r.net:+d} | {100*r.precision:.1f}% | {100*r.v5_accuracy:.1f}% | {100*r.tpc_accuracy:.1f}% |"
        )
    lines += ["","## Gate","",
              f"- positive blocks: **{positive}/{len(bdf)}**",
              f"- worst block net: **{worst:+d}**",
              f"- TPC-only marginal net over OCS: **{only['net']:+d}**",
              f"- union net vs OCS: **{union['net']:+d} vs {ocs['net']:+d}**"]
    if gate:
        lines += [
            "- TPC V1 passed the frozen development gate.",
            "- A separate prospective freeze is required."
        ]
    else:
        lines += [
            "- TPC V1 failed at least one frozen development criterion.",
            "- Do not tune propagation_count or component signs on this replay."
        ]

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
