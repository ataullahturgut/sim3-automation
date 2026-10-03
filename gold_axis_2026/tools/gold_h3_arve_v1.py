from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
RTE=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_ARVE_V1_RETRO_PREDICTIONS_2026-10-04.csv"
OUT_GRID=AX/"GOLD_H3_ARVE_V1_POLICY_GRID_2026-10-04.csv"
OUT_BLOCKS=AX/"GOLD_H3_ARVE_V1_POLICY_BLOCKS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_ARVE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_ARVE_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_ARVE_V1_PROSPECTIVE_FREEZE_2026-10-04.json"

SEED=20261004
BOOT=21
HALF_LIVES=[90,180,360]
FLOORS=[0.58,0.62,0.66]
C=.5
MIN_TRAIN=100
START=pd.Timestamp("2024-07-01")

BASE_FEATURES=[
"v5_confidence","abs_h_ret_12","trend_strength","opposite_semivar_share",
"deceleration_6h","path_consistency","adverse_excursion","gc_volume_z20",
"gc_volume_accel_5","signed_opt_pressure","signed_d_opt_pressure","opt_total_z20",
"p_rte","p_inst"
]
HEALTH=[
"health_error_20","health_error_60","health_same_momentum_20",
"health_large_error_20","health_mean_abs_move_20","health_since_last_error"
]
FEATURES=BASE_FEATURES+HEALTH

def as_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    f=pd.read_csv(FEAT)
    r=pd.read_csv(RTE)
    for d in [f,r]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])

    keep=["feature_cutoff_date","p_rte","p_inst","base_rate","train_n"]
    z=f.merge(r[keep],on="feature_cutoff_date",how="inner",validate="one_to_one")
    z=z[z.eligible_v5_continuation.astype(bool)].copy()
    z["v5_correct"]=(z.v5_pred.astype(int)==z.y_up.astype(int))
    z["rescue_target"]=(~z.v5_correct).astype(int)
    z["opal_candidate"]=as_bool(z.opal_override_check)
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    z["month_key"]=z.forecast_issue_date.dt.to_period("M").astype(str)
    return z

def health_features(z):
    q=z.copy()
    vals={c:[] for c in HEALTH}
    for r in q.itertuples():
        hist=q[
            (q.target_end_date_h3<=r.feature_cutoff_date)
            & (q.forecast_issue_date<r.forecast_issue_date)
        ].sort_values("forecast_issue_date")

        h20=hist.tail(20)
        h60=hist.tail(60)
        same=hist[hist.momentum_up.astype(int)==int(r.momentum_up)].tail(20)

        vals["health_error_20"].append(float(h20.rescue_target.mean()) if len(h20) else np.nan)
        vals["health_error_60"].append(float(h60.rescue_target.mean()) if len(h60) else np.nan)
        vals["health_same_momentum_20"].append(float(same.rescue_target.mean()) if len(same) else np.nan)
        vals["health_large_error_20"].append(
            float(((h20.rescue_target==1)&(h20.target_r3.abs()>=.01)).mean()) if len(h20) else np.nan
        )
        vals["health_mean_abs_move_20"].append(float(h20.target_r3.abs().mean()) if len(h20) else np.nan)

        if len(hist):
            rev=hist.reset_index(drop=True)
            idx=np.where(rev.rescue_target.to_numpy()==1)[0]
            since=int(len(rev)-1-idx[-1]) if len(idx) else 20
            vals["health_since_last_error"].append(float(min(since,20)))
        else:
            vals["health_since_last_error"].append(np.nan)

    for c,v in vals.items():
        q[c]=v
    return q

def block_name(ts):
    ts=pd.Timestamp(ts)
    if ts.year==2024: return "2024_H2"
    return f"{ts.year}_{'H1' if ts.month<=6 else 'H2'}"

def fit_bootstrap_ensemble(train,test,half_life,cutoff):
    Xtr=train[FEATURES].to_numpy(float)
    y=train.rescue_target.astype(int).to_numpy()
    Xte=test[FEATURES].to_numpy(float)

    scaler=StandardScaler()
    Xtr_s=scaler.fit_transform(Xtr)
    Xte_s=scaler.transform(Xte)

    age=np.maximum(0,(cutoff-train.target_end_date_h3).dt.days.to_numpy(float))
    decay=np.power(.5, age/float(half_life))

    months=train.month_key.to_numpy()
    uniq=np.array(sorted(pd.unique(months)))
    preds=[]

    # Include deterministic full-sample model as one ensemble member.
    full=LogisticRegression(C=C,solver="lbfgs",max_iter=3000,random_state=SEED)
    full.fit(Xtr_s,y,sample_weight=decay)
    preds.append(full.predict_proba(Xte_s)[:,1])

    for b in range(BOOT-1):
        rng=np.random.default_rng(SEED+b+1+half_life)
        sampled=rng.choice(uniq,size=len(uniq),replace=True)
        idx=[]
        for mo in sampled:
            idx.extend(np.where(months==mo)[0].tolist())
        idx=np.array(idx,dtype=int)
        yy=y[idx]
        if len(np.unique(yy))<2:
            continue
        m=LogisticRegression(C=C,solver="lbfgs",max_iter=3000,random_state=SEED+b+1)
        m.fit(Xtr_s[idx],yy,sample_weight=decay[idx])
        preds.append(m.predict_proba(Xte_s)[:,1])

    P=np.vstack(preds)
    return P.mean(axis=0),np.quantile(P,.20,axis=0),len(preds)

def monthly_walk(z):
    test=z[z.forecast_issue_date>=START].copy()
    rows=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].dropna(subset=FEATURES).copy()
        if te.empty: continue
        first_cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=z[
            (z.target_end_date_h3<=first_cutoff)
            & (z.forecast_issue_date<first_issue)
        ].dropna(subset=FEATURES+["rescue_target"]).copy()
        if len(tr)<MIN_TRAIN or tr.rescue_target.nunique()<2:
            continue

        predmap={}
        for hl in HALF_LIVES:
            mean,q20,nens=fit_bootstrap_ensemble(tr,te,hl,first_cutoff)
            predmap[hl]=(mean,q20,nens)

        for i,r in enumerate(te.itertuples()):
            d={
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "v5_pred":int(r.v5_pred),"v5_correct":bool(r.v5_correct),
                "rescue_target":int(r.rescue_target),
                "opal_candidate":bool(r.opal_candidate),
                "momentum_up":int(r.momentum_up),
                "train_n":len(tr)
            }
            for hl in HALF_LIVES:
                d[f"pmean_{hl}"]=float(predmap[hl][0][i])
                d[f"q20_{hl}"]=float(predmap[hl][1][i])
                d[f"ensemble_n_{hl}"]=int(predmap[hl][2])
            rows.append(d)
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def eval_config(pred,hl,floor):
    q=pred.copy()
    c=(q[f"q20_{hl}"]>.50)&(q[f"pmean_{hl}"]>=floor)
    resc=int((c&(q.rescue_target==1)).sum())
    broken=int((c&(q.rescue_target==0)).sum())
    n=int(c.sum())
    blocks=[]
    qq=q.copy(); qq["block"]=qq.forecast_issue_date.map(block_name)
    for name,g in qq.groupby("block",sort=False):
        cc=(g[f"q20_{hl}"]>.50)&(g[f"pmean_{hl}"]>=floor)
        rr=int((cc&(g.rescue_target==1)).sum())
        bb=int((cc&(g.rescue_target==0)).sum())
        blocks.append({
            "half_life":hl,"mean_floor":floor,"block":name,
            "eligible_n":len(g),"accepted_n":int(cc.sum()),
            "rescued":rr,"broken":bb,"net":rr-bb,
            "precision":rr/max(int(cc.sum()),1),
            "v5_accuracy":float(g.v5_correct.mean()),
            "assisted_accuracy":float((np.where(cc.to_numpy(),1-g.v5_pred.astype(int).to_numpy(),g.v5_pred.astype(int).to_numpy())==g.y_up.astype(int).to_numpy()).mean())
        })
    pos=sum(1 for b in blocks if b["net"]>0)
    minnet=min([b["net"] for b in blocks],default=0)
    return {
        "half_life":hl,"mean_floor":floor,
        "accepted_n":n,"rescued":resc,"broken":broken,"net_rescue":resc-broken,
        "precision":resc/max(n,1),
        "positive_blocks":pos,"min_block_net":minnet,
        "eligible":bool(n>=12 and resc-broken>=5 and resc/max(n,1)>=.60 and pos>=3 and minnet>=-2)
    },blocks

def prospective_snapshot(z,chosen):
    cutoff=pd.Timestamp("2026-10-05")
    tr=z[
        (z.target_end_date_h3<=pd.Timestamp("2026-09-29"))
        & (z.forecast_issue_date<cutoff)
    ].dropna(subset=FEATURES+["rescue_target"]).copy()
    snap={
        "schema":"ARVE_H3_V1_PROSPECTIVE_FREEZE",
        "freeze_date":"2026-10-04",
        "first_clean_origin":"2026-10-05",
        "historical_2026_status":"development_only",
        "chosen_policy":chosen,
        "train_n":int(len(tr)),
        "train_rescue_rate":float(tr.rescue_target.mean()),
        "max_matured_target_end":str(tr.target_end_date_h3.max().date()) if len(tr) else None,
        "features":FEATURES,
        "estimator":{"type":"StandardScaler + LogisticRegression bootstrap ensemble","C":C,"bootstraps":BOOT,"lower_quantile":.20}
    }
    OUT_FREEZE.write_text(json.dumps(snap,indent=2)+"\n")
    return snap

def main():
    z=health_features(load())
    pred=monthly_walk(z)
    pred.to_csv(OUT_PRED,index=False)

    grid=[]; blockrows=[]
    for hl in HALF_LIVES:
        for floor in FLOORS:
            g,b=eval_config(pred,hl,floor)
            grid.append(g); blockrows.extend(b)
    gdf=pd.DataFrame(grid)
    bdf=pd.DataFrame(blockrows)
    gdf.to_csv(OUT_GRID,index=False); bdf.to_csv(OUT_BLOCKS,index=False)

    elig=gdf[gdf.eligible].copy()
    chosen=None
    if elig.empty:
        status="NO_ELIGIBLE_ARVE_V1_POLICY"
    else:
        elig=elig.sort_values(
            ["net_rescue","precision","rescued","accepted_n","half_life","mean_floor"],
            ascending=[False,False,False,True,False,False]
        )
        r=elig.iloc[0]
        chosen={"half_life":int(r.half_life),"mean_floor":float(r.mean_floor)}
        status="ARVE_V1_POLICY_SELECTED_FOR_PROSPECTIVE_SHADOW"

    snap=prospective_snapshot(z,chosen)

    summary={
        "schema":"ARVE_H3_V1",
        "status":status,
        "policy_grid":grid,
        "chosen_policy":chosen,
        "prospective_freeze":snap
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# ARVE-H3 V1 — ADAPTIVE RESCUE VALUE ENGINE","",
        f"**Status:** **{status}**  ",
        "**Historical evidence:** retrospective development only; 2026 is not a clean holdout.","",
        "## Policy grid","",
        "| Half-life | Mean floor | Flips | Rescue | Broken | Net | Precision | + blocks | Worst block | Eligible |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for r in gdf.itertuples():
        lines.append(
            f"| {r.half_life} | {r.mean_floor:.2f} | {r.accepted_n} | {r.rescued} | {r.broken} | "
            f"{r.net_rescue:+d} | {100*r.precision:.2f}% | {r.positive_blocks} | {r.min_block_net:+d} | {r.eligible} |"
        )

    if chosen:
        cb=bdf[(bdf.half_life==chosen["half_life"])&(np.isclose(bdf.mean_floor,chosen["mean_floor"]))]
        lines += ["",f"## Selected development policy: half-life {chosen['half_life']}d / mean floor {chosen['mean_floor']:.2f}","",
                  "| Block | Flips | Rescue | Broken | Net | Precision | V5 acc | Assisted |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for r in cb.itertuples():
            lines.append(f"| {r.block} | {r.accepted_n} | {r.rescued} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% | {100*r.v5_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% |")

    lines += ["","## Prospective status","",
              f"- first clean origin: **{snap['first_clean_origin']}**",
              f"- matured training rows: **{snap['train_n']}**",
              f"- max matured target end: **{snap['max_matured_target_end']}**",
              "",
              "ARVE earns no promotion from this retrospective replay. Only post-freeze prospective outcomes may establish a new clean improvement."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
