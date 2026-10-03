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

OUT_BLOCK=AX/"GOLD_H3_RC_RTE_V1_BLOCK_RESULTS_2026-10-04.csv"
OUT_REG=AX/"GOLD_H3_RC_RTE_V1_REGIME_AUDIT_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_RC_RTE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_RC_RTE_V1_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_RC_RTE_V1_2026_HOLDOUT_2026-10-04.csv"

SEED=20261004
K=3

RAW_STATE=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","adverse_excursion","gc_dlog_volume_1","gc_volume_z20",
"gc_volume_accel_5","signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]
AXES=["persistence","fragility","option_opposition","participation_shock"]

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    m=pd.read_csv(MAT)
    for d in [p,f,m]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])

    fkeep=["feature_cutoff_date"]+RAW_STATE
    mkeep=["feature_cutoff_date","p_material"]
    z=p.merge(f[fkeep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.merge(m[mkeep],on="feature_cutoff_date",how="left",validate="one_to_one")

    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    z["opal_candidate"]=parse_bool(z.opal_override_check)

    z["prev_p_rte"]=z.p_rte.shift(1)
    z["prev_mom"]=z.momentum_up.shift(1)
    z["prev_date"]=z.feature_cutoff_date.shift(1)
    seq=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
    z["dp_rte"]=np.where(seq,z.p_rte-z.prev_p_rte,np.nan)

    z["sb"]=(z.p_rte>=.75)&(z.prev_p_rte>=.60)&(z.dp_rte<=.05)
    z["opt"]=(z.p_rte>=.65)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)
    z["mat"]=(z.p_material.fillna(-1)>=.70)
    z["proposal"]=z.sb|z.opt|z.mat

    z=z.dropna(subset=RAW_STATE).reset_index(drop=True)
    return z

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

def regime_enable(train):
    rows=[]; enabled=[]
    for reg,g in train.groupby("regime"):
        q=g[g.proposal].copy()
        n=len(q)
        resc=int(q.rescue_target.sum())
        broken=int(n-resc)
        net=resc-broken
        prec=resc/max(n,1)
        ok=bool(n>=8 and prec>=.55 and net>0)
        rows.append({
            "regime":int(reg),"proposal_support":n,
            "rescued":resc,"broken":broken,"net_rescue":net,
            "rescue_precision":prec,"enabled":ok,
            "state_persistence":float(g.persistence.mean()),
            "state_fragility":float(g.fragility.mean()),
            "state_option_opposition":float(g.option_opposition.mean()),
            "state_participation_shock":float(g.participation_shock.mean()),
        })
        if ok: enabled.append(int(reg))
    return rows,enabled

def score(test,enabled):
    cand=test.proposal & test.regime.isin(enabled)
    v=test.v5_pred.astype(int).to_numpy()
    y=test.y_up.astype(int).to_numpy()
    a=np.where(cand.to_numpy(),1-v,v)
    resc=int((cand.to_numpy()&(v!=y)&(a==y)).sum())
    broken=int((cand.to_numpy()&(v==y)&(a!=y)).sum())
    return {
        "eligible_n":len(test),
        "proposal_n":int(test.proposal.sum()),
        "candidate_n":int(cand.sum()),
        "candidate_rate":float(cand.mean()) if len(test) else np.nan,
        "rescued":resc,"broken":broken,"net_rescue":resc-broken,
        "rescue_precision":resc/max(resc+broken,1),
        "v5_accuracy":float((v==y).mean()) if len(test) else np.nan,
        "assisted_accuracy":float((a==y).mean()) if len(test) else np.nan,
        "missed_opal_no_candidate_n":int(((test.rescue_target==1)&(~test.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((test.rescue_target==1)&(~test.opal_candidate)&cand).sum())
    },cand,a

def run_block(z,name,train_end,test_start,test_end):
    train=z[z.forecast_issue_date<train_end].copy()
    test=z[(z.forecast_issue_date>=test_start)&(z.forecast_issue_date<=test_end)].copy()
    train,test=fit_axes(train,test)
    km=KMeans(n_clusters=K,n_init=50,random_state=SEED)
    km.fit(train[AXES].to_numpy(float))
    train["regime"]=km.predict(train[AXES].to_numpy(float))
    test["regime"]=km.predict(test[AXES].to_numpy(float))
    audit,enabled=regime_enable(train)
    met,cand,a=score(test,enabled)
    met.update({"block":name,"train_n":len(train),"enabled_regimes":";".join(map(str,enabled))})
    for r in audit:
        r.update({"block":name})
    return met,audit

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def final_2026(z):
    train=z[z.forecast_issue_date<pd.Timestamp("2026-01-01")].copy()
    test=z[z.year==2026].copy()
    train,test=fit_axes(train,test)
    km=KMeans(n_clusters=K,n_init=50,random_state=SEED)
    km.fit(train[AXES].to_numpy(float))
    train["regime"]=km.predict(train[AXES].to_numpy(float))
    test["regime"]=km.predict(test[AXES].to_numpy(float))
    audit,enabled=regime_enable(train)
    met,cand,a=score(test,enabled)
    test["rc_candidate"]=cand.to_numpy()
    test["rc_pred"]=a
    test["rc_correct"]=test.rc_pred.astype(int)==test.y_up.astype(int)
    return met,test,audit,enabled

def main():
    z=load()

    specs=[
        ("2024_H2",pd.Timestamp("2024-07-01"),pd.Timestamp("2024-07-01"),pd.Timestamp("2024-12-31")),
        ("2025_H1",pd.Timestamp("2025-01-01"),pd.Timestamp("2025-01-01"),pd.Timestamp("2025-06-30")),
        ("2025_H2",pd.Timestamp("2025-07-01"),pd.Timestamp("2025-07-01"),pd.Timestamp("2025-12-31")),
    ]
    block_rows=[]; audits=[]
    for name,train_end,ts,te in specs:
        met,aud=run_block(z,name,train_end,ts,te)
        block_rows.append(met); audits.extend(aud)

    bdf=pd.DataFrame(block_rows)
    adf=pd.DataFrame(audits)
    bdf.to_csv(OUT_BLOCK,index=False); adf.to_csv(OUT_REG,index=False)

    total_candidates=int(bdf.candidate_n.sum())
    total_resc=int(bdf.rescued.sum()); total_broken=int(bdf.broken.sum())
    total_net=total_resc-total_broken
    precision=total_resc/max(total_candidates,1)
    positive_blocks=int((bdf.net_rescue>0).sum())
    min_block=int(bdf.net_rescue.min())
    pooled_n=int(bdf.eligible_n.sum())
    v5_correct=sum(int(round(r.v5_accuracy*r.eligible_n)) for r in bdf.itertuples())
    assisted_correct=v5_correct+total_net
    pooled_v5=v5_correct/max(pooled_n,1)
    pooled_assisted=assisted_correct/max(pooled_n,1)

    robust=bool(
        total_candidates>=10
        and total_net>=4
        and precision>=.58
        and positive_blocks>=2
        and min_block>=-1
        and pooled_assisted>pooled_v5
    )

    hold=None; whole=None; final_audit=None; enabled_final=None
    if robust:
        status="RC_RTE_ROBUST_PASS_2026_OPENED"
        hold,hold_df,final_audit,enabled_final=final_2026(z)
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
    else:
        status="NO_ROBUST_RC_RTE_RULE"

    summary={
        "schema":"RC_RTE_H3_V1","status":status,
        "sequential_blocks":block_rows,
        "pooled_pre2026":{
            "eligible_n":pooled_n,"candidate_n":total_candidates,
            "rescued":total_resc,"broken":total_broken,"net_rescue":total_net,
            "rescue_precision":precision,"positive_blocks":positive_blocks,
            "min_block_net":min_block,"v5_accuracy":pooled_v5,
            "assisted_accuracy":pooled_assisted,"robust_pass":robust
        },
        "holdout_2026":hold,"whole_2026":whole,
        "final_enabled_regimes":enabled_final,
        "final_regime_audit":final_audit
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# RC-RTE-H3 V1 — REGIME-CONDITIONAL REVERSAL TRANSITION RESULT","",
           f"**Status:** **{status}**  ",
           "**Regime map:** K=3 unsupervised mechanism-state clusters; reversal proposals are allowed only in historically reversal-enabled regimes.","",
           "## Sequential pre-2026 blocks","",
           "| Block | Train n | Enabled regimes | Proposals | Gated | Rescue | Broken | Net | Precision | V5 acc | Assisted acc |",
           "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.train_n} | {r.enabled_regimes or '-'} | {r.proposal_n} | {r.candidate_n} | "
            f"{r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% | "
            f"{100*r.v5_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% |"
        )
    lines += ["","## Pooled pre-2026 robustness","",
              f"- candidates: **{total_candidates}**",
              f"- rescued / broken / net: **{total_resc} / {total_broken} / {total_net:+d}**",
              f"- rescue precision: **{100*precision:.2f}%**",
              f"- positive blocks: **{positive_blocks}/3**",
              f"- worst block net: **{min_block:+d}**",
              f"- V5 -> assisted pooled accuracy: **{100*pooled_v5:.2f}% -> {100*pooled_assisted:.2f}%**",
              f"- robustness gate: **{'PASS' if robust else 'FAIL'}**"]

    lines += ["","## Training-regime audits","",
              "| Block | Regime | Support | Rescue | Broken | Net | Precision | Enabled | Persistence | Fragility | Option opposition | Participation |",
              "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|"]
    for r in adf.itertuples():
        lines.append(
            f"| {r.block} | {r.regime} | {r.proposal_support} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {r.enabled} | {r.state_persistence:+.3f} | {r.state_fragility:+.3f} | "
            f"{r.state_option_opposition:+.3f} | {r.state_participation_shock:+.3f} |"
        )

    if robust and hold is not None:
        lines += ["","## 2026 final holdout","",
                  f"- final enabled regimes: **{enabled_final}**",
                  f"- candidates: **{hold['candidate_n']} ({100*hold['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- rescue precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "2026 was opened only if the three sequential pre-2026 blocks passed the preregistered robustness gate. "
              "Regime construction uses origin-observable state only; outcomes are used only to enable or protect regimes within matured training data."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
