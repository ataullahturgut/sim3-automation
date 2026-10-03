from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_DEV=AX/"GOLD_H3_OAR_CRED_V2_DEV_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_OAR_CRED_V2_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_OAR_CRED_V2_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_OAR_CRED_V2_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_OAR_CRED_V2_2026_HOLDOUT_2026-10-04.csv"

Q=.60
MEMORY=3

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    for d in [p,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    z=p.merge(
        f[["feature_cutoff_date","signed_opt_pressure","signed_d_opt_pressure"]],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    ).sort_values("forecast_issue_date").reset_index(drop=True)
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["oar_proposal"]=(
        (z.p_rte>=Q)
        &(z.p_inst>=.50)
        &(z.signed_opt_pressure>0)
        &(z.signed_d_opt_pressure>0)
    )
    z["shadow_utility"]=np.where(z.rescue_target.astype(int)==1,1,-1)
    return z

def apply_credibility(z):
    q=z.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    perms=[]; recent_n=[]; recent_net=[]
    for r in q.itertuples():
        prior=q[
            q.oar_proposal
            &(q.target_end_date_h3<=r.feature_cutoff_date)
            &(q.forecast_issue_date<r.forecast_issue_date)
        ].sort_values("target_end_date_h3").tail(MEMORY)
        n=len(prior); net=int(prior.shadow_utility.sum()) if n else 0
        perm=True if n<MEMORY else bool(net>=1)
        perms.append(perm); recent_n.append(n); recent_net.append(net)
    q["cred_permission"]=perms
    q["shadow_recent_n"]=recent_n
    q["shadow_recent_net"]=recent_net
    q["oar_cred_candidate"]=q.oar_proposal&q.cred_permission
    return q

def stats(q):
    c=q.oar_cred_candidate.astype(bool)
    v=q.v5_pred.astype(int).to_numpy(); y=q.y_up.astype(int).to_numpy()
    a=np.where(c.to_numpy(),1-v,v)
    r=int((c.to_numpy()&(v!=y)&(a==y)).sum())
    b=int((c.to_numpy()&(v==y)&(a!=y)).sum())
    proposal_rows=q[q.oar_proposal].copy()
    transitions=0
    if len(proposal_rows)>1:
        s=proposal_rows.cred_permission.astype(int).to_numpy()
        transitions=int(np.sum(s[1:]!=s[:-1]))
    return {
        "eligible_n":len(q),"proposal_n":int(q.oar_proposal.sum()),
        "candidate_n":int(c.sum()),"candidate_rate":float(c.mean()) if len(q) else np.nan,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(r+b,1),
        "permission_transitions":transitions,
        "v5_accuracy":float((v==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((a==y).mean()) if len(q) else np.nan,
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&c).sum())
    },q.assign(oar_cred_pred=a,oar_cred_correct=(a==y))

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    z=load()

    # Development sequence only: do not permit 2026 outcomes into the pre-2026 gate.
    devseq=apply_credibility(z[z.year<=2025].copy())
    devseq.to_csv(OUT_DEV,index=False)

    d=devseq.forecast_issue_date
    masks={
        "2024_H1":(devseq.year==2024)&(d.dt.month<=6),
        "2024_H2":(devseq.year==2024)&(d.dt.month>=7),
        "2025_H1":(devseq.year==2025)&(d.dt.month<=6),
        "2025_H2":(devseq.year==2025)&(d.dt.month>=7),
    }
    rows=[]
    for name,mask in masks.items():
        s,_=stats(devseq[mask].copy())
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

    robust=bool(
        cand>=10 and net>=8 and prec>=.65 and nonneg>=3 and mn>=-1 and ass_acc>base_acc
    )

    hold=None; whole=None
    if robust:
        status="OAR_CRED_V2_ROBUST_PASS_2026_OPENED"
        full=apply_credibility(z.copy())
        hold,hold_df=stats(full[full.year==2026].copy())
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
    else:
        status="NO_ROBUST_OAR_CRED_V2"

    summary={
        "schema":"OAR_CRED_H3_V2","status":status,"q":Q,"memory":MEMORY,
        "block_metrics":bdf.to_dict("records"),
        "pooled_pre2026":{
            "candidate_n":cand,"rescued":resc,"broken":broken,"net_rescue":net,
            "rescue_precision":prec,"nonnegative_blocks":nonneg,"min_block_net":mn,
            "v5_accuracy":base_acc,"assisted_accuracy":ass_acc,"robust_pass":robust
        },
        "holdout_2026":hold,"whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# OAR-CRED-H3 V2 — SHADOW CREDIBILITY RESULT","",
           f"**Status:** **{status}**  ",
           f"**Frozen OAR:** q={Q:.2f}, options pressure against momentum and rising.  ",
           f"**Credibility:** last {MEMORY} matured OAR shadow outcomes; act when fewer than 3 or last-3 net >= +1.","",
           "## 2024-2025 development","",
           "| Block | Proposals | Actions | Rescue | Broken | Net | Precision | Transitions | V5 acc | Assisted acc |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.proposal_n} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {r.permission_transitions} | {100*r.v5_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% |"
        )

    lines += ["","## Pooled pre-2026 gate","",
              f"- acted candidates: **{cand}**",
              f"- rescue / broken / net: **{resc} / {broken} / {net:+d}**",
              f"- rescue precision: **{100*prec:.2f}%**",
              f"- nonnegative blocks: **{nonneg}/4**",
              f"- worst block: **{mn:+d}**",
              f"- V5 -> assisted accuracy: **{100*base_acc:.2f}% -> {100*ass_acc:.2f}%**",
              f"- robustness: **{'PASS' if robust else 'FAIL'}**"]

    if robust and hold is not None:
        lines += ["","## 2026 final holdout","",
                  f"- proposals / actions: **{hold['proposal_n']} / {hold['candidate_n']}**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- rescue precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- credibility transitions: **{hold['permission_transitions']}**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "The pre-2026 robustness gate is computed on a sequence truncated at 2025-12-31. 2026 outcomes are used only if that gate passes. Vetoed proposals still update shadow credibility after maturity."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
