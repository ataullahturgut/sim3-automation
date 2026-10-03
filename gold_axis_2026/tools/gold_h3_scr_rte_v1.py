from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MAT=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_REPLAY=AX/"GOLD_H3_SCR_RTE_V1_RETRO_REPLAY_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_SCR_RTE_V1_RETRO_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_SCR_RTE_V1_RETRO_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_SCR_RTE_V1_PROSPECTIVE_FREEZE_2026-10-04.json"

RAW=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","adverse_excursion","gc_dlog_volume_1","gc_volume_z20",
"gc_volume_accel_5","signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]
AXES=["persistence","fragility","option_opposition","participation_shock"]

MIN_LIB=15
SUPPORT_K=5
LOCAL_K=15
SUPPORT_P_MIN=.10
LOCAL_PREC_MIN=.60
WILSON_Z=.8416212335729143  # one-sided 80%
START=pd.Timestamp("2024-07-01")
FREEZE_CUTOFF=pd.Timestamp("2026-10-04")

def bool_series(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    m=pd.read_csv(MAT)
    for d in [p,f,m]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])

    z=p.merge(
        f[["feature_cutoff_date"]+RAW],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    )
    z=z.merge(
        m[["feature_cutoff_date","p_material"]],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    )
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    z["opal_candidate"]=bool_series(z.opal_override_check)

    z["prev_p_rte"]=z.p_rte.shift(1)
    z["prev_mom"]=z.momentum_up.shift(1)
    z["prev_date"]=z.feature_cutoff_date.shift(1)
    seq=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
    z["dp_rte"]=np.where(seq,z.p_rte-z.prev_p_rte,np.nan)

    z["sb"]=(z.p_rte>=.75)&(z.prev_p_rte>=.60)&(z.dp_rte<=.05)
    z["opt"]=(z.p_rte>=.65)&(z.p_inst>=.50)&(z.signed_opt_pressure>0)
    z["mat"]=z.p_material.fillna(-1)>=.70
    z["proposal"]=z.sb|z.opt|z.mat
    return z.dropna(subset=RAW).reset_index(drop=True)

def transform_axes(train, df):
    mu=train[RAW].mean()
    sd=train[RAW].std(ddof=0).replace(0,1.0)
    q=df.copy()
    for c in RAW:
        q[c+"_z"]=(q[c]-mu[c])/sd[c]
    q["persistence"]=(
        q.trend_strength_z+q.path_consistency_z+q.v5_confidence_z
        -q.adverse_excursion_z-q.opposite_semivar_share_z
    )/5.0
    q["fragility"]=(
        q.deceleration_6h_z+q.opposite_semivar_share_z+q.adverse_excursion_z
        -q.path_consistency_z
    )/4.0
    q["option_opposition"]=(
        q.signed_opt_pressure_z+q.signed_d_opt_pressure_z+q.opt_total_z20_z
    )/3.0
    q["participation_shock"]=(
        q.gc_volume_z20_z+q.gc_volume_accel_5_z+q.gc_dlog_volume_1_z
    )/3.0
    return q,mu,sd

def euclid(A,b):
    return np.sqrt(((A-b)**2).sum(axis=1))

def loo_kth_scores(A,k):
    n=len(A)
    out=[]
    for i in range(n):
        d=np.sqrt(((A-A[i])**2).sum(axis=1))
        d=np.delete(d,i)
        if len(d)<k: return None
        out.append(float(np.partition(d,k-1)[k-1]))
    return np.array(out,float)

def wilson_lower(success,n,z=WILSON_Z):
    if n<=0: return 0.0
    p=success/n
    den=1+z*z/n
    center=p+z*z/(2*n)
    adj=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)
    return max(0.0,(center-adj)/den)

def build_month_snapshot(z, first_cutoff):
    train=z[(z.target_end_date_h3<=first_cutoff)&(z.forecast_issue_date<first_cutoff)].copy()
    train_ax,mu,sd=transform_axes(train,train)
    libs={}
    for spec in ["sb","opt","mat"]:
        q=train_ax[train_ax[spec]].copy()
        if len(q)<MIN_LIB:
            libs[spec]={"n":len(q),"eligible":False}
            continue
        A=q[AXES].to_numpy(float)
        cal=loo_kth_scores(A,SUPPORT_K)
        libs[spec]={
            "n":len(q),"eligible":cal is not None,
            "states":A,
            "labels":q.rescue_target.astype(int).to_numpy(),
            "dates":q.feature_cutoff_date.astype(str).tolist(),
            "cal_scores":cal
        }
    return train,mu,sd,libs

def transform_one(row,mu,sd):
    d={}
    for c in RAW:
        d[c+"_z"]=(float(getattr(row,c))-float(mu[c]))/float(sd[c] if sd[c]!=0 else 1.0)
    d["persistence"]=(d["trend_strength_z"]+d["path_consistency_z"]+d["v5_confidence_z"]-d["adverse_excursion_z"]-d["opposite_semivar_share_z"])/5
    d["fragility"]=(d["deceleration_6h_z"]+d["opposite_semivar_share_z"]+d["adverse_excursion_z"]-d["path_consistency_z"])/4
    d["option_opposition"]=(d["signed_opt_pressure_z"]+d["signed_d_opt_pressure_z"]+d["opt_total_z20_z"])/3
    d["participation_shock"]=(d["gc_volume_z20_z"]+d["gc_volume_accel_5_z"]+d["gc_dlog_volume_1_z"])/3
    return np.array([d[c] for c in AXES],float),d

def specialist_eval(lib,x):
    if not lib.get("eligible",False):
        return {"pass":False,"reason":"LIBRARY_TOO_SMALL","n":lib.get("n",0)}
    A=lib["states"]; labels=lib["labels"]; cal=lib["cal_scores"]
    d=euclid(A,x)
    if len(d)<SUPPORT_K:
        return {"pass":False,"reason":"SUPPORT_TOO_SMALL","n":len(d)}
    kth=float(np.partition(d,SUPPORT_K-1)[SUPPORT_K-1])
    ps=(1+int((cal>=kth).sum()))/(len(cal)+1)
    if ps<SUPPORT_P_MIN:
        return {"pass":False,"reason":"OOD_SUPPORT","n":len(d),"p_support":ps,"candidate_score":kth}
    idx=np.argsort(d)[:LOCAL_K]
    y=labels[idx]
    succ=int(y.sum()); n=len(y); prec=succ/max(n,1)
    wl=wilson_lower(succ,n)
    ok=prec>=LOCAL_PREC_MIN and wl>.50
    return {
        "pass":bool(ok),
        "reason":"PASS" if ok else "LOCAL_COMPETENCE",
        "n":len(d),"p_support":ps,"candidate_score":kth,
        "local_n":n,"local_rescue":succ,"local_precision":prec,"wilson80":wl,
        "trust":wl*ps if ok else 0.0
    }

def replay(z):
    test=z[z.forecast_issue_date>=START].copy().sort_values("forecast_issue_date")
    rows=[]
    accepted=[]
    current_month=None
    mu=sd=libs=None
    month_train_n=0
    live_scores={"sb":0,"opt":0,"mat":0}

    for r in test.itertuples():
        month=pd.Timestamp(r.forecast_issue_date).to_period("M")
        if current_month!=month:
            current_month=month
            month_rows=test[test.forecast_issue_date.dt.to_period("M")==month]
            first_cutoff=month_rows.feature_cutoff_date.min()
            train,mu,sd,libs=build_month_snapshot(z,first_cutoff)
            month_train_n=len(train)
            live_scores={"sb":0,"opt":0,"mat":0}

        active=[s for s in ["sb","opt","mat"] if bool(getattr(r,s))]
        decision="NO_PROPOSAL"
        selected=None
        evals={}
        x,axes=transform_one(r,mu,sd)

        if active:
            passed=[]
            for s in active:
                ev=specialist_eval(libs[s],x)
                evals[s]=ev
                if ev.get("pass"):
                    passed.append(s)

            if not passed:
                reasons=[evals[s].get("reason","") for s in active]
                if "OOD_SUPPORT" in reasons: decision="SUPPRESS_OOD"
                elif "LOCAL_COMPETENCE" in reasons: decision="SUPPRESS_COMPETENCE"
                else: decision="SUPPRESS_LIBRARY"
            else:
                passed=sorted(
                    passed,
                    key=lambda s:(evals[s]["trust"],evals[s]["local_precision"],evals[s]["p_support"],{"sb":3,"opt":2,"mat":1}[s]),
                    reverse=True
                )
                selected=passed[0]

                # Mature previously accepted selected-specialist events as of this origin.
                hist=[a for a in accepted if a["specialist"]==selected]
                matured=[a for a in hist if a["target_end_date_h3"]<=r.feature_cutoff_date]
                unresolved=[a for a in hist if a["target_end_date_h3"]>r.feature_cutoff_date]

                # Monthly live score uses only events accepted in the current month and matured by now.
                maturing_month=[
                    a for a in matured
                    if pd.Timestamp(a["forecast_issue_date"]).to_period("M")==month
                ]
                live_scores[selected]=int(sum(a["utility"] for a in maturing_month))

                if unresolved:
                    decision="SUPPRESS_OVERLAP"
                elif live_scores[selected]<0:
                    decision="SUPPRESS_FUSE"
                else:
                    decision="ACCEPT"
                    utility=1 if int(r.rescue_target)==1 else -1
                    accepted.append({
                        "specialist":selected,
                        "forecast_issue_date":r.forecast_issue_date,
                        "feature_cutoff_date":r.feature_cutoff_date,
                        "target_end_date_h3":r.target_end_date_h3,
                        "utility":utility
                    })

        accepted_flag=decision=="ACCEPT"
        assisted_pred=1-int(r.v5_pred) if accepted_flag else int(r.v5_pred)
        row={
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),"month":str(r.month),
            "y_up":int(r.y_up),"target_r3":float(r.target_r3),
            "v5_pred":int(r.v5_pred),"rescue_target":int(r.rescue_target),
            "opal_candidate":bool(r.opal_candidate),
            "sb":bool(r.sb),"opt":bool(r.opt),"mat":bool(r.mat),
            "proposal":bool(r.proposal),"decision":decision,
            "selected_specialist":selected or "",
            "accepted":accepted_flag,
            "assisted_pred":assisted_pred,
            "v5_correct":int(r.v5_pred)==int(r.y_up),
            "assisted_correct":assisted_pred==int(r.y_up),
            "month_train_n":month_train_n,
            **{f"axis_{k}":float(v) for k,v in axes.items()}
        }
        for s in ["sb","opt","mat"]:
            ev=evals.get(s,{})
            row[f"{s}_p_support"]=ev.get("p_support",np.nan)
            row[f"{s}_local_precision"]=ev.get("local_precision",np.nan)
            row[f"{s}_wilson80"]=ev.get("wilson80",np.nan)
            row[f"{s}_trust"]=ev.get("trust",np.nan)
            row[f"{s}_reason"]=ev.get("reason","")
        rows.append(row)
    return pd.DataFrame(rows)

def block_name(d):
    d=pd.Timestamp(d)
    if d.year==2024: return "2024_H2"
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def summarize(df):
    q=df.copy()
    q["block"]=q.forecast_issue_date.map(block_name)
    blocks=[]
    for name,g in q.groupby("block",sort=False):
        c=g.accepted.astype(bool)
        resc=int((c & (g.rescue_target==1)).sum())
        broken=int((c & (g.rescue_target==0)).sum())
        blocks.append({
            "block":name,"eligible_n":len(g),"proposal_n":int(g.proposal.sum()),
            "accepted_n":int(c.sum()),"rescued":resc,"broken":broken,"net":resc-broken,
            "precision":resc/max(int(c.sum()),1),
            "v5_accuracy":float(g.v5_correct.mean()),
            "assisted_accuracy":float(g.assisted_correct.mean()),
            "ood_suppressed":int((g.decision=="SUPPRESS_OOD").sum()),
            "competence_suppressed":int((g.decision=="SUPPRESS_COMPETENCE").sum()),
            "library_suppressed":int((g.decision=="SUPPRESS_LIBRARY").sum()),
            "overlap_suppressed":int((g.decision=="SUPPRESS_OVERLAP").sum()),
            "fuse_suppressed":int((g.decision=="SUPPRESS_FUSE").sum()),
        })
    return blocks

def freeze_snapshot(z):
    # Prospective October refit uses all outcomes already matured by the last historical cutoff.
    # The last available panel target end is 2026-09-29.
    eligible=z[z.target_end_date_h3<=pd.Timestamp("2026-09-29")].copy()
    train,mu,sd,libs=build_month_snapshot(z,pd.Timestamp("2026-10-05"))
    snap={
        "schema":"SCR_RTE_H3_V1_PROSPECTIVE_FREEZE",
        "freeze_date":"2026-10-04",
        "first_clean_origin":"2026-10-05",
        "historical_status":"development_only",
        "train_rows":int(len(train)),
        "max_matured_target_end":str(train.target_end_date_h3.max().date()) if len(train) else None,
        "constants":{
            "min_library":MIN_LIB,"support_k":SUPPORT_K,"local_k":LOCAL_K,
            "support_p_min":SUPPORT_P_MIN,"local_precision_min":LOCAL_PREC_MIN,
            "wilson_one_sided_level":0.80
        },
        "scaler":{
            "mean":{c:float(mu[c]) for c in RAW},
            "std":{c:float(sd[c]) for c in RAW}
        },
        "specialists":{
            s:{
                "proposal_library_n":int(libs[s].get("n",0)),
                "support_ready":bool(libs[s].get("eligible",False))
            } for s in ["sb","opt","mat"]
        }
    }
    OUT_FREEZE.write_text(json.dumps(snap,indent=2)+"\n")
    return snap

def main():
    z=load()
    replay_df=replay(z)
    replay_df.to_csv(OUT_REPLAY,index=False)
    blocks=summarize(replay_df)
    snap=freeze_snapshot(z)

    total_c=int(replay_df.accepted.sum())
    total_resc=int(((replay_df.accepted)&(replay_df.rescue_target==1)).sum())
    total_broken=int(((replay_df.accepted)&(replay_df.rescue_target==0)).sum())
    total_net=total_resc-total_broken
    total_prec=total_resc/max(total_c,1)
    v5acc=float(replay_df.v5_correct.mean())
    aacc=float(replay_df.assisted_correct.mean())

    summary={
        "schema":"SCR_RTE_H3_V1_RETRO_DEVELOPMENT",
        "status":"RETROSPECTIVE_DEVELOPMENT_ONLY",
        "accepted_n":total_c,"rescued":total_resc,"broken":total_broken,
        "net_rescue":total_net,"precision":total_prec,
        "v5_accuracy":v5acc,"assisted_accuracy":aacc,
        "blocks":blocks,"prospective_freeze":snap
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# SCR-RTE-H3 V1 — RETROSPECTIVE DEVELOPMENT REPLAY","",
        "**Status:** **RETROSPECTIVE DEVELOPMENT ONLY — NOT A CLEAN 2026 VALIDATION**  ",
        "**Architecture:** specialist-specific conformal support + local competence + arbitration + overlap/fuse safety.","",
        "## Forward development replay","",
        "| Block | Eligible | Proposals | Accepted | Rescue | Broken | Net | Precision | V5 acc | Assisted | OOD suppr | Competence suppr |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in blocks:
        lines.append(
            f"| {r['block']} | {r['eligible_n']} | {r['proposal_n']} | {r['accepted_n']} | "
            f"{r['rescued']} | {r['broken']} | {r['net']:+d} | {100*r['precision']:.2f}% | "
            f"{100*r['v5_accuracy']:.2f}% | {100*r['assisted_accuracy']:.2f}% | "
            f"{r['ood_suppressed']} | {r['competence_suppressed']} |"
        )
    lines += [
        "","## Aggregate development replay","",
        f"- accepted: **{total_c}**",
        f"- rescue / broken / net: **{total_resc} / {total_broken} / {total_net:+d}**",
        f"- rescue precision: **{100*total_prec:.2f}%**",
        f"- V5 -> SCR-RTE assisted accuracy: **{100*v5acc:.2f}% -> {100*aacc:.2f}%**",
        "","## Prospective freeze","",
        f"- first clean origin: **{snap['first_clean_origin']}**",
        f"- training rows at freeze: **{snap['train_rows']}**",
        f"- max matured target end: **{snap['max_matured_target_end']}**",
        f"- SB library: **{snap['specialists']['sb']['proposal_library_n']}**",
        f"- OPT library: **{snap['specialists']['opt']['proposal_library_n']}**",
        f"- MAT library: **{snap['specialists']['mat']['proposal_library_n']}**",
        "",
        "Historical 2026 outcomes are part of development. The prospective frozen version may only earn a new clean claim on post-freeze origins."
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
