from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MAT=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_BLOCK=AX/"GOLD_H3_RC_RTE_V2_FUSE_BLOCK_RESULTS_2026-10-04.csv"
OUT_REG=AX/"GOLD_H3_RC_RTE_V2_FUSE_REGIME_AUDIT_2026-10-04.csv"
OUT_CHRON=AX/"GOLD_H3_RC_RTE_V2_FUSE_CHRONOLOGY_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_RC_RTE_V2_FUSE_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_RC_RTE_V2_FUSE_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_RC_RTE_V2_FUSE_2026_HOLDOUT_2026-10-04.csv"

SEED=20261004
K=3

RAW_STATE=[
    "v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
    "path_consistency","adverse_excursion","gc_dlog_volume_1","gc_volume_z20",
    "gc_volume_accel_5","signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]
AXES=["persistence","fragility","option_opposition","participation_shock"]

def parse_bool(s):
    if s.dtype==bool:
        return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    m=pd.read_csv(MAT)

    for d in [p,f,m]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns:
                d[c]=pd.to_datetime(d[c])

    z=p.merge(
        f[["feature_cutoff_date"]+RAW_STATE],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    )
    z=z.merge(
        m[["feature_cutoff_date","p_material"]],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    )
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    z["opal_candidate"]=parse_bool(z.opal_override_check)

    z["prev_p_rte"]=z.p_rte.shift(1)
    z["prev_mom"]=z.momentum_up.shift(1)
    z["prev_date"]=z.feature_cutoff_date.shift(1)
    seq=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
    z["dp_rte"]=np.where(seq,z.p_rte-z.prev_p_rte,np.nan)

    z["sb"]=(z.p_rte>=.75)&(z.prev_p_rte>=.60)&(z.dp_rte<=.05)
    z["opt"]=(z.p_rte>=.65)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)
    z["mat"]=z.p_material.fillna(-1)>=.70
    z["proposal"]=z.sb|z.opt|z.mat

    return z.dropna(subset=RAW_STATE).reset_index(drop=True)

def fit_axes(train,test):
    mu=train[RAW_STATE].mean()
    sd=train[RAW_STATE].std(ddof=0).replace(0,1.0)

    def transform(df):
        q=df.copy()
        for c in RAW_STATE:
            q[c+"_z"]=(q[c]-mu[c])/sd[c]
        q["persistence"]=(
            q["trend_strength_z"]+q["path_consistency_z"]+q["v5_confidence_z"]
            -q["adverse_excursion_z"]-q["opposite_semivar_share_z"]
        )/5.0
        q["fragility"]=(
            q["deceleration_6h_z"]+q["opposite_semivar_share_z"]
            +q["adverse_excursion_z"]-q["path_consistency_z"]
        )/4.0
        q["option_opposition"]=(
            q["signed_opt_pressure_z"]+q["signed_d_opt_pressure_z"]+q["opt_total_z20_z"]
        )/3.0
        q["participation_shock"]=(
            q["gc_volume_z20_z"]+q["gc_volume_accel_5_z"]+q["gc_dlog_volume_1_z"]
        )/3.0
        return q
    return transform(train),transform(test)

def static_regime_audit(train):
    rows=[]
    enabled=[]
    for reg,g in train.groupby("regime"):
        q=g[g.proposal].copy()
        n=len(q)
        rescue=int(q.rescue_target.sum())
        broken=int(n-rescue)
        net=rescue-broken
        precision=rescue/max(n,1)
        ok=bool(n>=8 and precision>=.55 and net>0)
        rows.append({
            "regime":int(reg),
            "proposal_support":n,
            "rescued":rescue,
            "broken":broken,
            "net_rescue":net,
            "rescue_precision":precision,
            "enabled":ok,
            "state_persistence":float(g.persistence.mean()),
            "state_fragility":float(g.fragility.mean()),
            "state_option_opposition":float(g.option_opposition.mean()),
            "state_participation_shock":float(g.participation_shock.mean()),
        })
        if ok:
            enabled.append(int(reg))
    return rows,enabled

def online_fuse(test,enabled,block_name):
    q=test.sort_values("forecast_issue_date").copy()
    accepted=[]
    chronology=[]
    suppressed_overlap=0
    suppressed_fuse=0
    suppressed_static=0

    for r in q.itertuples():
        if not bool(r.proposal):
            continue

        reg=int(r.regime)

        # Determine settled accepted events in this regime as of this origin.
        same_reg=[x for x in accepted if x["regime"]==reg]
        matured=[x for x in same_reg if x["target_end_date_h3"]<=r.feature_cutoff_date]
        unresolved=[x for x in same_reg if x["target_end_date_h3"]>r.feature_cutoff_date]

        live_score=int(sum(x["utility"] for x in matured))

        reason=None
        accept=False
        if reg not in enabled:
            reason="STATIC_PROTECTED"
            suppressed_static+=1
        elif live_score<0:
            reason="FUSE_CLOSED"
            suppressed_fuse+=1
        elif len(unresolved)>0:
            reason="OVERLAP_SUPPRESSED"
            suppressed_overlap+=1
        else:
            accept=True
            reason="ACCEPTED"
            utility=1 if int(r.rescue_target)==1 else -1
            accepted.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "regime":reg,
                "utility":utility,
                "rescue_target":int(r.rescue_target),
                "y_up":int(r.y_up),
                "v5_pred":int(r.v5_pred),
                "opal_candidate":bool(r.opal_candidate),
            })

        chronology.append({
            "block":block_name,
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "regime":reg,
            "sb":bool(r.sb),"opt":bool(r.opt),"mat":bool(r.mat),
            "proposal":True,
            "static_enabled":reg in enabled,
            "matured_same_regime_n":len(matured),
            "matured_same_regime_score":live_score,
            "unresolved_same_regime_n":len(unresolved),
            "decision":reason,
            "accepted":accept,
            "outcome_if_accepted":"RESCUE" if accept and int(r.rescue_target)==1 else ("BROKEN" if accept else ""),
        })

    if accepted:
        adf=pd.DataFrame(accepted)
        rescued=int((adf.utility==1).sum())
        broken=int((adf.utility==-1).sum())
        net=int(adf.utility.sum())
        precision=rescued/max(len(adf),1)
    else:
        rescued=broken=net=0
        precision=0.0

    accepted_dates=set(x["feature_cutoff_date"] for x in accepted)
    cand=q.feature_cutoff_date.isin(accepted_dates)
    v=q.v5_pred.astype(int).to_numpy()
    y=q.y_up.astype(int).to_numpy()
    assisted=np.where(cand.to_numpy(),1-v,v)

    metrics={
        "eligible_n":len(q),
        "proposal_n":int(q.proposal.sum()),
        "candidate_n":int(cand.sum()),
        "candidate_rate":float(cand.mean()) if len(q) else np.nan,
        "suppressed_overlap_n":suppressed_overlap,
        "suppressed_fuse_n":suppressed_fuse,
        "suppressed_static_n":suppressed_static,
        "rescued":rescued,"broken":broken,"net_rescue":net,
        "rescue_precision":precision,
        "v5_accuracy":float((v==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((assisted==y).mean()) if len(q) else np.nan,
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&cand).sum()),
    }
    return metrics,chronology,cand,assisted

def run_block(z,name,train_end,test_start,test_end):
    train=z[z.forecast_issue_date<train_end].copy()
    test=z[(z.forecast_issue_date>=test_start)&(z.forecast_issue_date<=test_end)].copy()

    train,test=fit_axes(train,test)

    km=KMeans(n_clusters=K,n_init=50,random_state=SEED)
    km.fit(train[AXES].to_numpy(float))
    train["regime"]=km.predict(train[AXES].to_numpy(float))
    test["regime"]=km.predict(test[AXES].to_numpy(float))

    audit,enabled=static_regime_audit(train)
    met,chron,_,_=online_fuse(test,enabled,name)

    met.update({
        "block":name,
        "train_n":len(train),
        "enabled_regimes":";".join(map(str,enabled))
    })
    for r in audit:
        r["block"]=name

    return met,audit,chron

def final_2026(z):
    train=z[z.forecast_issue_date<pd.Timestamp("2026-01-01")].copy()
    test=z[z.year==2026].copy()

    train,test=fit_axes(train,test)
    km=KMeans(n_clusters=K,n_init=50,random_state=SEED)
    km.fit(train[AXES].to_numpy(float))
    train["regime"]=km.predict(train[AXES].to_numpy(float))
    test["regime"]=km.predict(test[AXES].to_numpy(float))

    audit,enabled=static_regime_audit(train)
    met,chron,cand,assisted=online_fuse(test,enabled,"2026_HOLDOUT")

    test["rc_v2_candidate"]=cand.to_numpy()
    test["rc_v2_pred"]=assisted
    test["rc_v2_correct"]=test.rc_v2_pred.astype(int)==test.y_up.astype(int)

    return met,test,audit,enabled,chron

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int)
    y=z.y_up.astype(int)
    base=int((pred==y).sum())
    n=len(z)
    return {
        "n":n,
        "v5_correct":base,
        "assisted_correct":base+net,
        "v5_accuracy":base/max(n,1),
        "assisted_accuracy":(base+net)/max(n,1)
    }

def main():
    z=load()

    specs=[
        ("2024_H2",pd.Timestamp("2024-07-01"),pd.Timestamp("2024-07-01"),pd.Timestamp("2024-12-31")),
        ("2025_H1",pd.Timestamp("2025-01-01"),pd.Timestamp("2025-01-01"),pd.Timestamp("2025-06-30")),
        ("2025_H2",pd.Timestamp("2025-07-01"),pd.Timestamp("2025-07-01"),pd.Timestamp("2025-12-31")),
    ]

    block_rows=[]
    audits=[]
    chron=[]
    for name,train_end,ts,te in specs:
        met,aud,ch=run_block(z,name,train_end,ts,te)
        block_rows.append(met)
        audits.extend(aud)
        chron.extend(ch)

    bdf=pd.DataFrame(block_rows)
    adf=pd.DataFrame(audits)
    cdf=pd.DataFrame(chron)

    total_candidates=int(bdf.candidate_n.sum())
    total_resc=int(bdf.rescued.sum())
    total_broken=int(bdf.broken.sum())
    total_net=total_resc-total_broken
    precision=total_resc/max(total_candidates,1)
    nonneg_blocks=int((bdf.net_rescue>=0).sum())
    positive_blocks=int((bdf.net_rescue>0).sum())
    min_block=int(bdf.net_rescue.min())

    pooled_n=int(bdf.eligible_n.sum())
    v5_correct=sum(int(round(r.v5_accuracy*r.eligible_n)) for r in bdf.itertuples())
    assisted_correct=v5_correct+total_net
    pooled_v5=v5_correct/max(pooled_n,1)
    pooled_assisted=assisted_correct/max(pooled_n,1)

    robust=bool(
        total_candidates>=6
        and total_net>=3
        and precision>=.60
        and pooled_assisted>pooled_v5
        and nonneg_blocks>=2
        and positive_blocks>=1
        and min_block>=-2
    )

    hold=None
    whole=None
    final_enabled=None
    final_audit=None
    final_chron=None

    if robust:
        status="RC_RTE_V2_FUSE_ROBUST_PASS_2026_OPENED"
        hold,hold_df,final_audit,final_enabled,final_chron=final_2026(z)
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
        cdf=pd.concat([cdf,pd.DataFrame(final_chron)],ignore_index=True)
    else:
        status="NO_ROBUST_RC_RTE_V2_FUSE"

    bdf.to_csv(OUT_BLOCK,index=False)
    adf.to_csv(OUT_REG,index=False)
    cdf.to_csv(OUT_CHRON,index=False)

    summary={
        "schema":"RC_RTE_H3_V2_FUSE",
        "status":status,
        "sequential_blocks":block_rows,
        "pooled_pre2026":{
            "eligible_n":pooled_n,
            "candidate_n":total_candidates,
            "rescued":total_resc,
            "broken":total_broken,
            "net_rescue":total_net,
            "rescue_precision":precision,
            "nonnegative_blocks":nonneg_blocks,
            "positive_blocks":positive_blocks,
            "min_block_net":min_block,
            "v5_accuracy":pooled_v5,
            "assisted_accuracy":pooled_assisted,
            "robust_pass":robust
        },
        "holdout_2026":hold,
        "whole_2026":whole,
        "final_enabled_regimes":final_enabled,
        "final_regime_audit":final_audit
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# RC-RTE-H3 V2 — ONLINE CREDIBILITY FUSE RESULT","",
        f"**Status:** **{status}**  ",
        "**Safety layer:** one unresolved event per regime + close regime after matured live score turns negative.","",
        "## Sequential pre-2026 blocks","",
        "| Block | Enabled | Proposals | Accepted | Ovlp suppr | Fuse suppr | Rescue | Broken | Net | Precision | V5 acc | Assisted |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.enabled_regimes or '-'} | {r.proposal_n} | {r.candidate_n} | "
            f"{r.suppressed_overlap_n} | {r.suppressed_fuse_n} | {r.rescued} | {r.broken} | "
            f"{r.net_rescue:+d} | {100*r.rescue_precision:.2f}% | "
            f"{100*r.v5_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% |"
        )

    lines += [
        "","## Pooled robustness","",
        f"- accepted candidates: **{total_candidates}**",
        f"- rescue / broken / net: **{total_resc} / {total_broken} / {total_net:+d}**",
        f"- precision: **{100*precision:.2f}%**",
        f"- non-negative blocks: **{nonneg_blocks}/3**",
        f"- positive blocks: **{positive_blocks}/3**",
        f"- worst block net: **{min_block:+d}**",
        f"- V5 -> assisted pooled accuracy: **{100*pooled_v5:.2f}% -> {100*pooled_assisted:.2f}%**",
        f"- robustness gate: **{'PASS' if robust else 'FAIL'}**"
    ]

    if robust and hold is not None:
        lines += [
            "","## 2026 final holdout","",
            f"- final static enabled regimes: **{final_enabled}**",
            f"- proposals / accepted: **{hold['proposal_n']} / {hold['candidate_n']}**",
            f"- overlap-suppressed: **{hold['suppressed_overlap_n']}**",
            f"- fuse-suppressed: **{hold['suppressed_fuse_n']}**",
            f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
            f"- precision: **{100*hold['rescue_precision']:.2f}%**",
            f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
            f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
            f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
            f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"
        ]

    lines += [
        "","## Governance","",
        "Every fuse decision used only previously matured accepted candidate outcomes. Overlapping unresolved H3 events were suppressed before their outcomes existed. "
        "2026 was opened only if the fixed pre-2026 robustness gate passed."
    ]

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
