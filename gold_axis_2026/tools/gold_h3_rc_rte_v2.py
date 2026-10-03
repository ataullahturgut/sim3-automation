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

OUT_BLOCK=AX/"GOLD_H3_RC_RTE_V2_BLOCK_RESULTS_2026-10-04.csv"
OUT_REG=AX/"GOLD_H3_RC_RTE_V2_REGIME_AUDIT_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_RC_RTE_V2_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_RC_RTE_V2_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_RC_RTE_V2_2026_HOLDOUT_2026-10-04.csv"

SEED=20261004
K=3
MEMORY=3

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
    p=pd.read_csv(PRED); f=pd.read_csv(FEAT); m=pd.read_csv(MAT)
    for d in [p,f,m]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    z=p.merge(f[["feature_cutoff_date"]+RAW_STATE],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.merge(m[["feature_cutoff_date","p_material"]],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    z["opal_candidate"]=parse_bool(z.opal_override_check)

    z["prev_p_rte"]=z.p_rte.shift(1); z["prev_mom"]=z.momentum_up.shift(1); z["prev_date"]=z.feature_cutoff_date.shift(1)
    seq=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
    z["dp_rte"]=np.where(seq,z.p_rte-z.prev_p_rte,np.nan)

    z["sb"]=(z.p_rte>=.75)&(z.prev_p_rte>=.60)&(z.dp_rte<=.05)
    z["opt"]=(z.p_rte>=.65)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)
    z["mat"]=z.p_material.fillna(-1)>=.70
    z["proposal"]=z.sb|z.opt|z.mat
    z["shadow_utility"]=np.where(z.rescue_target.astype(int)==1,1,-1)

    return z.dropna(subset=RAW_STATE).reset_index(drop=True)

def fit_axes(train,test):
    mu=train[RAW_STATE].mean(); sd=train[RAW_STATE].std(ddof=0).replace(0,1.0)
    def tr(df):
        q=df.copy()
        for c in RAW_STATE: q[c+"_z"]=(q[c]-mu[c])/sd[c]
        q["persistence"]=(q.trend_strength_z+q.path_consistency_z+q.v5_confidence_z-q.adverse_excursion_z-q.opposite_semivar_share_z)/5.0
        q["fragility"]=(q.deceleration_6h_z+q.opposite_semivar_share_z+q.adverse_excursion_z-q.path_consistency_z)/4.0
        q["option_opposition"]=(q.signed_opt_pressure_z+q.signed_d_opt_pressure_z+q.opt_total_z20_z)/3.0
        q["participation_shock"]=(q.gc_volume_z20_z+q.gc_volume_accel_5_z+q.gc_dlog_volume_1_z)/3.0
        return q
    return tr(train),tr(test)

def static_enable(train):
    audit=[]; enabled=[]
    for reg,g in train.groupby("regime"):
        q=g[g.proposal]
        n=len(q); r=int(q.rescue_target.sum()); b=n-r
        net=r-b; prec=r/max(n,1)
        ok=bool(n>=8 and prec>=.55 and net>0)
        audit.append({
            "regime":int(reg),"proposal_support":n,"rescued":r,"broken":b,
            "net_rescue":net,"rescue_precision":prec,"static_enabled":ok,
            "state_persistence":float(g.persistence.mean()),
            "state_fragility":float(g.fragility.mean()),
            "state_option_opposition":float(g.option_opposition.mean()),
            "state_participation_shock":float(g.participation_shock.mean())
        })
        if ok: enabled.append(int(reg))
    return audit,enabled

def sequential_score(test,static_enabled):
    q=test.sort_values("forecast_issue_date").copy()
    actions=[]; health_n=[]; health_net=[]; permissions=[]
    transitions={int(r):0 for r in sorted(q.regime.unique())}
    last_perm={int(r):None for r in sorted(q.regime.unique())}

    for r in q.itertuples():
        reg=int(r.regime)
        prior=q[
            (q.proposal)
            & (q.regime==reg)
            & (q.target_end_date_h3<=r.feature_cutoff_date)
            & (q.forecast_issue_date<r.forecast_issue_date)
        ].sort_values("target_end_date_h3")
        recent=prior.tail(MEMORY)
        n=len(recent)
        net=int(recent.shadow_utility.sum()) if n else 0

        if reg not in static_enabled:
            perm=False
        elif n<MEMORY:
            perm=True
        else:
            perm=bool(net>=1)

        if last_perm[reg] is not None and perm!=last_perm[reg]:
            transitions[reg]+=1
        last_perm[reg]=perm

        act=bool(r.proposal and perm)
        actions.append(act); health_n.append(n); health_net.append(net); permissions.append(perm)

    q["dynamic_permission"]=permissions
    q["shadow_recent_n"]=health_n
    q["shadow_recent_net"]=health_net
    q["rc_candidate"]=actions

    c=q.rc_candidate.astype(bool)
    v=q.v5_pred.astype(int).to_numpy(); y=q.y_up.astype(int).to_numpy()
    a=np.where(c.to_numpy(),1-v,v)
    resc=int((c.to_numpy()&(v!=y)&(a==y)).sum())
    broken=int((c.to_numpy()&(v==y)&(a!=y)).sum())

    met={
        "eligible_n":len(q),"proposal_n":int(q.proposal.sum()),
        "candidate_n":int(c.sum()),"candidate_rate":float(c.mean()) if len(q) else np.nan,
        "rescued":resc,"broken":broken,"net_rescue":resc-broken,
        "rescue_precision":resc/max(resc+broken,1),
        "v5_accuracy":float((v==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((a==y).mean()) if len(q) else np.nan,
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&c).sum()),
        "permission_transitions":sum(transitions.values()),
        "permission_transitions_by_regime":transitions
    }
    q["rc_pred"]=a
    q["rc_correct"]=q.rc_pred.astype(int)==q.y_up.astype(int)
    return met,q

def run_block(z,name,train_end,test_start,test_end):
    train=z[z.forecast_issue_date<train_end].copy()
    test=z[(z.forecast_issue_date>=test_start)&(z.forecast_issue_date<=test_end)].copy()
    train,test=fit_axes(train,test)
    km=KMeans(n_clusters=K,n_init=50,random_state=SEED)
    km.fit(train[AXES].to_numpy(float))
    train["regime"]=km.predict(train[AXES].to_numpy(float))
    test["regime"]=km.predict(test[AXES].to_numpy(float))
    audit,enabled=static_enable(train)
    met,_=sequential_score(test,enabled)
    met.update({"block":name,"train_n":len(train),"static_enabled_regimes":";".join(map(str,enabled))})
    for a in audit: a["block"]=name
    return met,audit

def final_2026(z):
    train=z[z.forecast_issue_date<pd.Timestamp("2026-01-01")].copy()
    test=z[z.year==2026].copy()
    train,test=fit_axes(train,test)
    km=KMeans(n_clusters=K,n_init=50,random_state=SEED)
    km.fit(train[AXES].to_numpy(float))
    train["regime"]=km.predict(train[AXES].to_numpy(float))
    test["regime"]=km.predict(test[AXES].to_numpy(float))
    audit,enabled=static_enable(train)
    met,out=sequential_score(test,enabled)
    return met,out,audit,enabled

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026]
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    z=load()
    specs=[
        ("2024_H2",pd.Timestamp("2024-07-01"),pd.Timestamp("2024-07-01"),pd.Timestamp("2024-12-31")),
        ("2025_H1",pd.Timestamp("2025-01-01"),pd.Timestamp("2025-01-01"),pd.Timestamp("2025-06-30")),
        ("2025_H2",pd.Timestamp("2025-07-01"),pd.Timestamp("2025-07-01"),pd.Timestamp("2025-12-31")),
    ]
    block_rows=[]; audits=[]
    for name,tr,ts,te in specs:
        met,aud=run_block(z,name,tr,ts,te)
        block_rows.append(met); audits.extend(aud)

    bdf=pd.DataFrame([{k:v for k,v in r.items() if k!="permission_transitions_by_regime"} for r in block_rows])
    adf=pd.DataFrame(audits)
    bdf.to_csv(OUT_BLOCK,index=False); adf.to_csv(OUT_REG,index=False)

    cand=int(bdf.candidate_n.sum()); resc=int(bdf.rescued.sum()); broken=int(bdf.broken.sum())
    net=resc-broken; prec=resc/max(cand,1)
    pos=int((bdf.net_rescue>0).sum()); minnet=int(bdf.net_rescue.min())
    n=int(bdf.eligible_n.sum())
    base_correct=sum(int(round(r.v5_accuracy*r.eligible_n)) for r in bdf.itertuples())
    assisted_correct=base_correct+net
    base_acc=base_correct/max(n,1); ass_acc=assisted_correct/max(n,1)
    robust=bool(cand>=10 and net>=4 and prec>=.58 and pos>=2 and minnet>=-1 and ass_acc>base_acc)

    hold=None; whole=None; final_audit=None; enabled=None
    if robust:
        status="RC_RTE_V2_ROBUST_PASS_2026_OPENED"
        hold,hold_df,final_audit,enabled=final_2026(z)
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
    else:
        status="NO_ROBUST_RC_RTE_V2_RULE"

    summary={
        "schema":"RC_RTE_SHADOW_H3_V2","status":status,
        "blocks":block_rows,
        "pooled_pre2026":{
            "eligible_n":n,"candidate_n":cand,"rescued":resc,"broken":broken,
            "net_rescue":net,"rescue_precision":prec,"positive_blocks":pos,
            "min_block_net":minnet,"v5_accuracy":base_acc,"assisted_accuracy":ass_acc,
            "robust_pass":robust
        },
        "holdout_2026":hold,"whole_2026":whole,
        "final_static_enabled_regimes":enabled,"final_regime_audit":final_audit
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# RC-RTE-H3 V2 — SHADOW CREDIBILITY RESULT","",
           f"**Status:** **{status}**  ",
           "**Dynamic rule:** static regime enablement + last-3 matured shadow proposal credibility.","",
           "## Sequential pre-2026 blocks","",
           "| Block | Static regimes | Proposals | Actions | Rescue | Broken | Net | Precision | Transitions | V5 acc | Assisted acc |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in block_rows:
        lines.append(
            f"| {r['block']} | {r['static_enabled_regimes'] or '-'} | {r['proposal_n']} | {r['candidate_n']} | "
            f"{r['rescued']} | {r['broken']} | {r['net_rescue']:+d} | {100*r['rescue_precision']:.2f}% | "
            f"{r['permission_transitions']} | {100*r['v5_accuracy']:.2f}% | {100*r['assisted_accuracy']:.2f}% |"
        )
    lines += ["","## Pooled robustness","",
              f"- candidates: **{cand}**",
              f"- rescued / broken / net: **{resc} / {broken} / {net:+d}**",
              f"- rescue precision: **{100*prec:.2f}%**",
              f"- positive blocks: **{pos}/3**",
              f"- worst block: **{minnet:+d}**",
              f"- V5 -> assisted accuracy: **{100*base_acc:.2f}% -> {100*ass_acc:.2f}%**",
              f"- robustness gate: **{'PASS' if robust else 'FAIL'}**"]

    if robust and hold is not None:
        lines += ["","## 2026 final holdout","",
                  f"- static enabled regimes: **{enabled}**",
                  f"- proposals / actions: **{hold['proposal_n']} / {hold['candidate_n']}**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- rescue precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- credibility transitions: **{hold['permission_transitions']}**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "Shadow outcomes enter memory only after target maturity. Vetoed proposals remain observable in shadow mode, allowing a regime to recover without risking a live flip. 2026 is opened only after the full pre-2026 robustness gate."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
