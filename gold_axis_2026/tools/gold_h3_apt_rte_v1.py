from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_BLOCK=AX/"GOLD_H3_APT_RTE_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_APT_RTE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_APT_RTE_V1_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_APT_RTE_V1_2026_HOLDOUT_2026-10-04.csv"

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED); f=pd.read_csv(FEAT)
    for d in [p,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    z=p.merge(
        f[["feature_cutoff_date","signed_opt_pressure","signed_d_opt_pressure",
           "gc_dlog_volume_1","gc_volume_accel_5"]],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    ).sort_values("forecast_issue_date").reset_index(drop=True)
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["apt_candidate"]=(
        (z.p_rte>=.60)
        &(z.p_inst>=.50)
        &(z.signed_opt_pressure>0)
        &(z.signed_d_opt_pressure>0)
        &(z.gc_dlog_volume_1<0)
        &(z.gc_volume_accel_5<0)
    )
    return z

def stat(q):
    c=q.apt_candidate.astype(bool)
    v=q.v5_pred.astype(int).to_numpy(); y=q.y_up.astype(int).to_numpy()
    a=np.where(c.to_numpy(),1-v,v)
    r=int((c.to_numpy()&(v!=y)&(a==y)).sum())
    b=int((c.to_numpy()&(v==y)&(a!=y)).sum())
    return {
        "eligible_n":len(q),"candidate_n":int(c.sum()),
        "candidate_rate":float(c.mean()) if len(q) else np.nan,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(r+b,1),
        "v5_accuracy":float((v==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((a==y).mean()) if len(q) else np.nan,
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&c).sum())
    },q.assign(apt_pred=a,apt_correct=(a==y))

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    z=load()
    d=z.forecast_issue_date
    masks={
        "2024_H1":(z.year==2024)&(d.dt.month<=6),
        "2024_H2":(z.year==2024)&(d.dt.month>=7),
        "2025_H1":(z.year==2025)&(d.dt.month<=6),
        "2025_H2":(z.year==2025)&(d.dt.month>=7),
    }
    rows=[]
    for name,mask in masks.items():
        s,_=stat(z[mask].copy())
        rows.append({"block":name,**s})
    bdf=pd.DataFrame(rows)
    bdf.to_csv(OUT_BLOCK,index=False)

    cand=int(bdf.candidate_n.sum()); resc=int(bdf.rescued.sum()); broken=int(bdf.broken.sum())
    net=resc-broken; prec=resc/max(cand,1)
    nonneg=int((bdf.net_rescue>=0).sum()); mn=int(bdf.net_rescue.min())
    n=int(bdf.eligible_n.sum())
    base_correct=sum(int(round(r.v5_accuracy*r.eligible_n)) for r in bdf.itertuples())
    ass_correct=base_correct+net
    base_acc=base_correct/max(n,1); ass_acc=ass_correct/max(n,1)
    rate=cand/max(n,1)

    robust=bool(
        cand>=8 and net>=4 and prec>=.65 and rate<=.10
        and nonneg>=3 and mn>=-1 and ass_acc>base_acc
    )

    hold=None; whole=None
    if robust:
        status="APT_RTE_ROBUST_PASS_2026_OPENED"
        hold,hold_df=stat(z[z.year==2026].copy())
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
    else:
        status="NO_ROBUST_APT_RTE_RULE"

    summary={
        "schema":"APT_RTE_H3_V1","status":status,
        "block_metrics":bdf.to_dict("records"),
        "pooled_pre2026":{
            "eligible_n":n,"candidate_n":cand,"candidate_rate":rate,
            "rescued":resc,"broken":broken,"net_rescue":net,
            "rescue_precision":prec,"nonnegative_blocks":nonneg,
            "min_block_net":mn,"v5_accuracy":base_acc,"assisted_accuracy":ass_acc,
            "robust_pass":robust
        },
        "holdout_2026":hold,"whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# APT-RTE-H3 V1 — ASYMMETRIC PRESSURE TRANSFER RESULT","",
           f"**Status:** **{status}**  ",
           "**Rule:** options pressure against momentum and rising, while GC futures volume level-change and acceleration are both negative.","",
           "## 2024-2025 development blocks","",
           "| Block | Cand | Rescue | Broken | Net | Precision | Rate | V5 acc | Assisted acc |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {100*r.v5_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% |"
        )
    lines += ["","## Pooled pre-2026 gate","",
              f"- candidates: **{cand} ({100*rate:.2f}%)**",
              f"- rescue / broken / net: **{resc} / {broken} / {net:+d}**",
              f"- rescue precision: **{100*prec:.2f}%**",
              f"- nonnegative blocks: **{nonneg}/4**",
              f"- worst block: **{mn:+d}**",
              f"- V5 -> assisted accuracy: **{100*base_acc:.2f}% -> {100*ass_acc:.2f}%**",
              f"- robustness: **{'PASS' if robust else 'FAIL'}**"]

    if robust and hold is not None:
        lines += ["","## 2026 final holdout","",
                  f"- candidates: **{hold['candidate_n']} ({100*hold['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- rescue precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "The pressure-transfer rule has no fitted cut points beyond the previously frozen RTE/OAR probability levels; all new participation conditions are structural sign tests. 2026 is opened only after the full pre-2026 robustness gate."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
