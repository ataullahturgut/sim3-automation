from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MAT=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_FRS_V1_TOURNAMENT_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_FRS_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_FRS_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_FRS_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_FRS_V1_SHADOW_FREEZE_2026-10-04.json"

START=pd.Timestamp("2024-07-01")
REPRESENTATIONS=["T1","IFS","PYTHAGOREAN","QRUNG3","HESITANT","PICTURE","NEUTROSOPHIC","IT2"]

RAW=[
    "v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
    "path_consistency","adverse_excursion","signed_opt_pressure"
]

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

    keep_f=[
        "feature_cutoff_date","v5_confidence","trend_strength","opposite_semivar_share",
        "deceleration_6h","path_consistency","adverse_excursion","signed_opt_pressure",
        "opal_override_check"
    ]
    z=p.merge(f[keep_f],on="feature_cutoff_date",how="left",validate="one_to_one",suffixes=("","_f"))
    z=z.merge(m[["feature_cutoff_date","p_material"]],on="feature_cutoff_date",how="left",validate="one_to_one")
    if "v5_confidence_f" in z.columns:
        z["v5_confidence"]=z["v5_confidence"].fillna(z["v5_confidence_f"])
    if "opal_override_check_f" in z.columns:
        z["opal_override_check"]=z["opal_override_check"].fillna(z["opal_override_check_f"])
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    return z.dropna(subset=RAW+["p_rte","p_material"]).reset_index(drop=True)

def empirical_pct(arr,x):
    a=np.asarray(arr,float)
    a=a[np.isfinite(a)]
    if len(a)==0: return np.nan
    return float((1+np.sum(a<=x))/(len(a)+1))

def month_transform(train,test):
    mu=train[[
        "trend_strength","path_consistency","v5_confidence",
        "adverse_excursion","opposite_semivar_share","deceleration_6h"
    ]].mean()
    sd=train[[
        "trend_strength","path_consistency","v5_confidence",
        "adverse_excursion","opposite_semivar_share","deceleration_6h"
    ]].std(ddof=0).replace(0,1.0)

    def axes(df):
        q=df.copy()
        for c in mu.index:
            q[c+"_z"]=(q[c]-mu[c])/sd[c]
        q["persistence_axis"]=(
            q["trend_strength_z"]+q["path_consistency_z"]+q["v5_confidence_z"]
            -q["adverse_excursion_z"]-q["opposite_semivar_share_z"]
        )/5.0
        q["fragility_axis"]=(
            q["deceleration_6h_z"]+q["opposite_semivar_share_z"]+q["adverse_excursion_z"]
            -q["path_consistency_z"]
        )/4.0
        return q
    tr=axes(train); te=axes(test)
    return tr,te

def evidence_rows(z):
    rows=[]
    test=z[z.forecast_issue_date>=START].copy()
    test["month_key"]=test.forecast_issue_date.dt.to_period("M").astype(str)

    for mk in sorted(test.month_key.unique()):
        te=test[test.month_key==mk].copy()
        first_issue=te.forecast_issue_date.min()
        tr=z[z.forecast_issue_date<first_issue].copy()
        if len(tr)<100:
            continue
        tr,te=month_transform(tr,te)

        opt_hist=tr.signed_opt_pressure.to_numpy(float)
        frag_hist=tr.fragility_axis.to_numpy(float)
        pers_hist=tr.persistence_axis.to_numpy(float)

        for r in te.itertuples():
            opt=empirical_pct(opt_hist,float(r.signed_opt_pressure))
            frag=empirical_pct(frag_hist,float(r.fragility_axis))
            pers=empirical_pct(pers_hist,float(r.persistence_axis))

            HR=np.array([
                float(r.p_rte),
                float(r.p_material),
                opt,
                frag
            ],float)
            HC=np.array([
                float(r.v5_confidence),
                pers,
                1.0-opt,
                1.0-frag
            ],float)

            R=float(HR.mean()); C=float(HC.mean())
            D=float(np.clip((HR.std(ddof=0)+HC.std(ddof=0))/2.0,0,1))
            K=float(min(R,C))

            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "v5_pred":int(r.v5_pred),
                "p_v5":float(r.p_helios_v5_dce),
                "rescue_target":int(r.rescue_target),
                "opal_candidate":bool(r.opal_candidate),
                "rte":HR[0],"material":HR[1],"options":HR[2],"fragility":HR[3],
                "v5_confidence_e":HC[0],"persistence":HC[1],
                "options_support":HC[2],"path_support":HC[3],
                "R":R,"C":C,"D":D,"K":K,
                "HR_q25":float(np.quantile(HR,.25)),
                "HR_q75":float(np.quantile(HR,.75)),
                "HC_q25":float(np.quantile(HC,.25)),
                "HC_q75":float(np.quantile(HC,.75)),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def generic_action(S,Q):
    if Q<.35:
        return "ABSTAIN"
    if S>=.15 and Q>=.55:
        return "FLIP"
    if S>0 and Q>=.35:
        return "DAMP"
    return "KEEP"

def eval_rep(row,rep):
    R=float(row.R); C=float(row.C); D=float(row.D)

    if rep=="T1":
        mu,nu=R,C
        S=mu-nu
        Q=abs(S)
        return {"S":S,"Q":Q,"action":generic_action(S,Q),
                "a":mu,"b":nu,"u":1-Q}

    if rep=="IFS":
        s=max(1.0,R+C)
        mu=R/s; nu=C/s
        pi=max(0.0,1-mu-nu)
        S=mu-nu; Q=1-pi
        return {"S":S,"Q":Q,"action":generic_action(S,Q),
                "a":mu,"b":nu,"u":pi}

    if rep=="PYTHAGOREAN":
        s=max(1.0,math.sqrt(R*R+C*C))
        mu=R/s; nu=C/s
        pi=math.sqrt(max(0.0,1-mu*mu-nu*nu))
        S=mu*mu-nu*nu; Q=1-pi
        return {"S":S,"Q":Q,"action":generic_action(S,Q),
                "a":mu,"b":nu,"u":pi}

    if rep=="QRUNG3":
        q=3.0
        s=max(1.0,(R**q+C**q)**(1/q))
        mu=R/s; nu=C/s
        pi=max(0.0,1-mu**q-nu**q)**(1/q)
        S=mu**q-nu**q; Q=1-pi
        return {"S":S,"Q":Q,"action":generic_action(S,Q),
                "a":mu,"b":nu,"u":pi}

    if rep=="HESITANT":
        S=R-C
        H=D
        Q=1-H
        return {"S":S,"Q":Q,"action":generic_action(S,Q),
                "a":R,"b":C,"u":H}

    if rep=="PICTURE":
        P=max(R-C,0.0)
        N=max(C-R,0.0)
        U=min(R,C)
        F=max(0.0,1-max(R,C))
        if F>=max(P,N,U):
            action="ABSTAIN"
        elif P>=.15 and P>U and P>F:
            action="FLIP"
        elif P>N:
            action="DAMP"
        else:
            action="KEEP"
        S=P-N
        Q=1-(U+F)
        return {"S":S,"Q":Q,"action":action,
                "a":P,"b":N,"u":U,"refusal":F}

    if rep=="NEUTROSOPHIC":
        T=R; F=C
        I=float(np.clip(.5*(1-abs(R-C))+.5*D,0,1))
        S=T-F; Q=1-I
        return {"S":S,"Q":Q,"action":generic_action(S,Q),
                "a":T,"b":F,"u":I}

    if rep=="IT2":
        RL=float(row.HR_q25); RH=float(row.HR_q75)
        CL=float(row.HC_q25); CH=float(row.HC_q75)
        L=RL-CH
        U=RH-CL
        W=float(np.clip(U-L,0,1))
        if L<=0<=U and W>=.50:
            action="ABSTAIN"
        elif L>=.10:
            action="FLIP"
        elif U>0 and L<.10:
            action="DAMP"
        elif U<=0:
            action="KEEP"
        else:
            action="KEEP"
        S=(L+U)/2
        Q=1-W
        return {"S":S,"Q":Q,"action":action,
                "a":L,"b":U,"u":W}

    raise KeyError(rep)

def apply_action(pv5,v5_pred,action):
    if action=="KEEP":
        return float(pv5),int(v5_pred)
    if action=="DAMP":
        p=.5+.5*(float(pv5)-.5)
        return p,int(v5_pred)
    if action=="FLIP":
        p=1-float(pv5)
        return p,1-int(v5_pred)
    if action=="ABSTAIN":
        return .5,int(v5_pred)  # full-benchmark direction defaults to V5; action remains abstain
    raise KeyError(action)

def logloss(y,p):
    p=float(np.clip(p,1e-6,1-1e-6))
    return -(y*math.log(p)+(1-y)*math.log(1-p))

def expand_reps(ev):
    out=[]
    for r in ev.itertuples():
        for rep in REPRESENTATIONS:
            e=eval_rep(r,rep)
            p_adj,pred=apply_action(r.p_v5,r.v5_pred,e["action"])
            out.append({
                **r._asdict(),
                "representation":rep,
                "score":e["S"],"certainty":e["Q"],"component_a":e["a"],
                "component_b":e["b"],"uncertainty":e["u"],
                "refusal":e.get("refusal",np.nan),
                "action":e["action"],
                "p_adj":p_adj,"assisted_pred":pred,
                "v5_correct":int(r.v5_pred)==int(r.y_up),
                "assisted_correct":pred==int(r.y_up),
                "brier":(p_adj-int(r.y_up))**2,
                "logloss":logloss(int(r.y_up),p_adj)
            })
    return pd.DataFrame(out)

def block_name(dt):
    d=pd.Timestamp(dt)
    if d.year==2024:
        return "2024_H2"
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def metrics(g):
    flip=g.action=="FLIP"
    damp=g.action=="DAMP"
    abst=g.action=="ABSTAIN"
    resc=int((flip&(g.rescue_target==1)).sum())
    broken=int((flip&(g.rescue_target==0)).sum())
    opal_miss=(g.rescue_target==1)&(~g.opal_candidate)
    return {
        "n":len(g),
        "flip_n":int(flip.sum()),
        "flip_rate":float(flip.mean()) if len(g) else np.nan,
        "rescued":resc,"broken":broken,"net":resc-broken,
        "flip_precision":resc/max(int(flip.sum()),1),
        "damp_n":int(damp.sum()),
        "abstain_n":int(abst.sum()),
        "action_coverage":float((~abst).mean()) if len(g) else np.nan,
        "v5_accuracy":float(g.v5_correct.mean()) if len(g) else np.nan,
        "assisted_accuracy":float(g.assisted_correct.mean()) if len(g) else np.nan,
        "brier":float(g.brier.mean()) if len(g) else np.nan,
        "logloss":float(g.logloss.mean()) if len(g) else np.nan,
        "opal_no_candidate_missed_reversal_n":int(opal_miss.sum()),
        "hits_opal_no_candidate":int((flip&opal_miss).sum())
    }

def main():
    z=load()
    ev=evidence_rows(z)
    pred=expand_reps(ev)
    pred["block"]=pred.forecast_issue_date.map(block_name)
    pred.to_csv(OUT_PRED,index=False)

    block_rows=[]
    summary_rows=[]
    for rep in REPRESENTATIONS:
        q=pred[pred.representation==rep].copy()
        bm=[]
        for block,g in q.groupby("block",sort=False):
            m=metrics(g); m.update({"representation":rep,"block":block})
            block_rows.append(m); bm.append(m)
        agg=metrics(q)
        nonneg=sum(1 for x in bm if x["net"]>=0)
        worst=min(x["net"] for x in bm)
        promising=bool(
            agg["net"]>0
            and agg["flip_precision"]>=.55
            and nonneg>=3
            and worst>=-2
            and agg["assisted_accuracy"]>=agg["v5_accuracy"]
            and agg["flip_rate"]<=.35
        )
        summary_rows.append({
            "representation":rep,**agg,
            "nonnegative_blocks":nonneg,"worst_block_net":worst,
            "development_promising":promising
        })

    bdf=pd.DataFrame(block_rows)
    sdf=pd.DataFrame(summary_rows)
    bdf.to_csv(OUT_BLOCK,index=False)

    promising=sdf[sdf.development_promising].copy()
    winner=None
    if len(promising):
        promising=promising.sort_values(
            ["net","flip_precision","worst_block_net","flip_rate","brier"],
            ascending=[False,False,False,True,True]
        )
        winner=str(promising.iloc[0].representation)

    status="NO_PROMISING_FUZZY_REPRESENTATION" if winner is None else "SHADOW_CANDIDATE_SELECTED"

    freeze={
        "schema":"FRS_H3_V1_SHADOW_FREEZE",
        "freeze_date":"2026-10-04",
        "historical_status":"development_only",
        "first_clean_origin":"2026-10-05",
        "status":status,
        "winner":winner,
        "representations":REPRESENTATIONS,
        "common_evidence":["p_rte","p_material","options_percentile","fragility_percentile",
                           "v5_confidence","persistence_percentile","1-options_percentile","1-fragility_percentile"],
        "action_thresholds":{
            "generic_flip_score":.15,"generic_flip_certainty":.55,
            "generic_damp_score_gt":0,"generic_damp_certainty":.35,
            "generic_abstain_certainty_lt":.35,
            "it2_flip_lower":.10,"it2_abstain_width":.50,
            "q_rung":3
        }
    }
    OUT_FREEZE.write_text(json.dumps(freeze,indent=2)+"\n")

    summary={
        "schema":"FRS_H3_V1_TOURNAMENT",
        "status":status,
        "winner":winner,
        "aggregate":sdf.to_dict("records"),
        "blocks":bdf.to_dict("records"),
        "prospective_freeze":freeze
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# FRS-H3 V1 — FUZZY / UNCERTAINTY REPRESENTATION TOURNAMENT","",
        "**Status:** **%s**  " % status,
        "**Historical 2024H2–2026Sep results are development/stress-test only.**","",
        "## Aggregate comparison","",
        "| Representation | Flip | Rescue | Broken | Net | Flip precision | DAMP | Abstain | V5 acc | Assisted acc | Brier | Nonneg blocks | Worst | Promising |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for r in sdf.itertuples():
        lines.append(
            f"| {r.representation} | {r.flip_n} | {r.rescued} | {r.broken} | {r.net:+d} | "
            f"{100*r.flip_precision:.2f}% | {r.damp_n} | {r.abstain_n} | "
            f"{100*r.v5_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% | {r.brier:.4f} | "
            f"{r.nonnegative_blocks} | {r.worst_block_net:+d} | {r.development_promising} |"
        )

    lines += ["","## Block stability","",
              "| Representation | Block | Flip | Rescue | Broken | Net | Precision | Assisted acc |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.representation} | {r.block} | {r.flip_n} | {r.rescued} | {r.broken} | "
            f"{r.net:+d} | {100*r.flip_precision:.2f}% | {100*r.assisted_accuracy:.2f}% |"
        )

    lines += ["","## Decision",""]
    if winner:
        lines += [
            f"- development winner: **{winner}**",
            "- status: **shadow challenger only**",
            "- first possible clean evidence: **2026-10-05 origin and later**"
        ]
    else:
        lines += [
            "- no representation satisfied the frozen development gate.",
            "- no fuzzy representation is promoted to prospective challenger in this version."
        ]

    lines += ["","The tournament changed only uncertainty geometry; the evidence layer was identical across all representations."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
