from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

EVENT=AX/"GOLD_H3_TRES_V1_STAGE0_EVENT_LEDGER_2026-10-04.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_TRES_V2_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_TRES_V2_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_TRES_V2_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_TRES_V2_RESULT_2026-10-04.md"

SEED=20261004
MIN_TRAIN=250
FEATURES=[
    "momentum_up","abs_h_ret_12","trend_strength","opposite_semivar_share",
    "deceleration_6h","path_consistency","trend_close_location",
    "opposite_extreme_recency","jump_concentration","trend_to_range",
    "adverse_excursion","v5_confidence","gc_dlog_volume_1","gc_volume_z20",
    "gc_volume_accel_5","signed_opt_pressure","signed_d_opt_pressure","opt_total_z20"
]
# 0 unresolved, 1 continuation last, 2 reversal last
LABEL_NAMES={0:"UNRESOLVED",1:"CONTINUATION_LAST",2:"REVERSAL_LAST"}

def parse_bool(s):
    if s.dtype==bool:return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def path_label(r):
    b=float(r.barrier_1p0)
    last=0
    for g in [float(r.g1),float(r.g2),float(r.g3)]:
        if g>=b: last=1
        elif g<=-b: last=2
    return last

def load():
    e=pd.read_csv(EVENT)
    f=pd.read_csv(FEAT)
    for d in [e,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns:d[c]=pd.to_datetime(d[c])
    e["path_state"]=e.apply(path_label,axis=1)
    keep=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3","year","month",
        "y_up","target_r3","momentum_up","rescue_target","eligible_v5_continuation",
        "v5_pred","p_helios_v5_dce","opal_override_check"
    ]+FEATURES
    keep=list(dict.fromkeys(keep))
    z=e.merge(f[keep],on=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"],how="inner",suffixes=("_event",""))
    for c in ["year","y_up","target_r3","momentum_up"]:
        ce=c+"_event"
        if ce in z.columns:z[c]=z[ce]
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["month_key"]=z.forecast_issue_date.dt.to_period("M").astype(str)
    z=z.dropna(subset=FEATURES).sort_values("forecast_issue_date").reset_index(drop=True)
    return z

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=.50,solver="lbfgs",penalty="l2",max_iter=3000,random_state=SEED))
    ])

def replay(z):
    rows=[]
    leak=0
    for mk in sorted(z.month_key.unique()):
        te=z[z.month_key==mk].copy()
        if te.empty:continue
        first_cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=z[(z.target_end_date_h3<=first_cutoff)&(z.forecast_issue_date<first_issue)].copy()
        if len(tr)<MIN_TRAIN or tr.path_state.nunique()<3:continue
        if (tr.target_end_date_h3>first_cutoff).any():
            leak+=1;continue
        m=make_model()
        m.fit(tr[FEATURES].to_numpy(float),tr.path_state.astype(int).to_numpy())
        pp=m.predict_proba(te[FEATURES].to_numpy(float))
        cls=list(m.named_steps["model"].classes_)
        idx={int(c):i for i,c in enumerate(cls)}
        if set(idx)!={0,1,2}:raise RuntimeError(f"Missing class {cls}")
        for r,p in zip(te.itertuples(),pp):
            muU=float(p[idx[0]]);muC=float(p[idx[1]]);muR=float(p[idx[2]])
            v5=int(r.v5_pred);mom=int(r.momentum_up);y=int(r.y_up)
            eligible=(v5==mom)
            flip=bool(eligible and muR>muC and muR>muU)
            assisted=1-v5 if flip else v5
            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":y,"target_r3":float(r.target_r3),
                "momentum_up":mom,"v5_pred":v5,
                "eligible_v5_continuation":eligible,
                "rescue_target":int(r.rescue_target),
                "opal_candidate":bool(r.opal_candidate),
                "actual_path_state":int(r.path_state),
                "mu_unresolved":muU,"mu_continuation":muC,"mu_reversal":muR,
                "pred_path_state":int(np.argmax([muU,muC,muR])),
                "flip":flip,"assisted_pred":assisted,
                "v5_correct":v5==y,"assisted_correct":assisted==y,
                "train_n":len(tr),"train_max_target_end":tr.target_end_date_h3.max()
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True),leak

def logloss_path(g):
    vals=[]
    for r in g.itertuples():
        p=[r.mu_unresolved,r.mu_continuation,r.mu_reversal][int(r.actual_path_state)]
        vals.append(-math.log(max(min(float(p),1-1e-12),1e-12)))
    return float(np.mean(vals))

def block_name(d):
    d=pd.Timestamp(d);return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def metrics(g):
    flip=g.flip.astype(bool)
    eligible=g.eligible_v5_continuation.astype(bool)
    rescued=int((flip&(g.rescue_target==1)).sum())
    broken=int((flip&(g.rescue_target==0)).sum())
    elig_n=int(eligible.sum())
    opalmiss=(g.rescue_target==1)&eligible&(~g.opal_candidate)
    return {
        "n":len(g),"eligible_n":elig_n,
        "flip_n":int(flip.sum()),
        "candidate_rate":float(flip.sum()/max(elig_n,1)),
        "rescued":rescued,"broken":broken,"net":rescued-broken,
        "flip_precision":rescued/max(int(flip.sum()),1),
        "v5_accuracy":float(g.v5_correct.mean()),
        "assisted_accuracy":float(g.assisted_correct.mean()),
        "path_accuracy":float((g.pred_path_state==g.actual_path_state).mean()),
        "path_logloss":logloss_path(g),
        "opal_no_candidate_missed_n":int(opalmiss.sum()),
        "hits_opal_no_candidate":int((flip&opalmiss).sum())
    }

def top_bottom(g):
    lo=float(g.mu_reversal.quantile(.20));hi=float(g.mu_reversal.quantile(.80))
    a=g[g.mu_reversal<=lo];b=g[g.mu_reversal>=hi]
    return {
        "low_n":len(a),"high_n":len(b),
        "low_terminal_reversal":float((a.y_up!=a.momentum_up).mean()),
        "high_terminal_reversal":float((b.y_up!=b.momentum_up).mean()),
        "separation":float((b.y_up!=b.momentum_up).mean()-(a.y_up!=a.momentum_up).mean())
    }

def main():
    z=load()
    pred,leak=replay(z)
    if pred.empty:raise RuntimeError("No V2 predictions")
    pred["block"]=pred.forecast_issue_date.map(block_name)
    pred.to_csv(OUT_PRED,index=False)
    agg=metrics(pred);tb=top_bottom(pred)

    block_rows=[]
    for b,g in pred.groupby("block",sort=False):
        x=metrics(g);x["block"]=b;x["terminal_sep"]=top_bottom(g)["separation"];block_rows.append(x)
    bdf=pd.DataFrame(block_rows);bdf.to_csv(OUT_BLOCK,index=False)

    nblocks=len(bdf)
    need_nonneg=math.ceil(.8*nblocks)
    need_pos=math.ceil(.5*nblocks)
    nonneg=int((bdf.net>=0).sum());positive=int((bdf.net>0).sum());worst=int(bdf.net.min())

    gate=bool(
        agg["flip_precision"]>=.55
        and agg["net"]>0
        and agg["candidate_rate"]<=.25
        and agg["assisted_accuracy"]>=agg["v5_accuracy"]+.005
        and nonneg>=need_nonneg
        and positive>=need_pos
        and worst>=-2
        and tb["separation"]>=.25
        and leak==0
    )
    status="TRES_V2_PATH_GOVERNOR_PROMISING" if gate else "TRES_V2_PATH_GOVERNOR_FAIL"

    state_counts=[]
    for state,g in pred.groupby("actual_path_state"):
        state_counts.append({
            "state":LABEL_NAMES[int(state)],"n":len(g),
            "terminal_reversal_rate":float((g.y_up!=g.momentum_up).mean())
        })

    summary={
        "schema":"TRES_H3_V2_LAST_STATE","status":status,
        "prediction_rows":len(pred),
        "first_scored_origin":str(pred.feature_cutoff_date.min().date()),
        "last_scored_origin":str(pred.feature_cutoff_date.max().date()),
        "aggregate":agg,"top_bottom_muR":tb,"blocks":block_rows,
        "nonnegative_blocks":nonneg,"nonnegative_required":need_nonneg,
        "positive_blocks":positive,"positive_required":need_pos,
        "worst_block_net":worst,"maturity_leakage_failures":leak,
        "actual_state_counts":state_counts
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# TRES-H3 V2 — LAST-DECISIVE PATH STATE RESULT","",
        f"**Status:** **{status}**  ",
        f"- predictions: **{len(pred)}**",
        f"- scored origins: **{summary['first_scored_origin']} .. {summary['last_scored_origin']}**",
        f"- maturity leakage failures: **{leak}**","",
        "## Aggregate path governor","",
        f"- V5-continuation eligible: **{agg['eligible_n']}**",
        f"- FLIP candidates: **{agg['flip_n']} ({100*agg['candidate_rate']:.2f}%)**",
        f"- rescue / broken / net: **{agg['rescued']} / {agg['broken']} / {agg['net']:+d}**",
        f"- FLIP precision: **{100*agg['flip_precision']:.2f}%**",
        f"- V5 -> assisted accuracy: **{100*agg['v5_accuracy']:.2f}% -> {100*agg['assisted_accuracy']:.2f}%**",
        f"- path-state accuracy: **{100*agg['path_accuracy']:.2f}%**",
        f"- path-state log loss: **{agg['path_logloss']:.4f}**",
        f"- OPAL-no-candidate missed reversals hit: **{agg['hits_opal_no_candidate']}/{agg['opal_no_candidate_missed_n']}**",
        "",
        "## mu_R terminal-reversal concentration","",
        f"- bottom quintile: **{100*tb['low_terminal_reversal']:.2f}%**",
        f"- top quintile: **{100*tb['high_terminal_reversal']:.2f}%**",
        f"- separation: **{100*tb['separation']:+.2f} pp**","",
        "## Half-year stability","",
        "| Block | N | Flip | Rescue | Broken | Net | Precision | V5 acc | Assisted | Terminal sep |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.n} | {r.flip_n} | {r.rescued} | {r.broken} | {r.net:+d} | "
            f"{100*r.flip_precision:.1f}% | {100*r.v5_accuracy:.1f}% | {100*r.assisted_accuracy:.1f}% | "
            f"{100*r.terminal_sep:+.1f}pp |"
        )
    lines += ["","## Gate","",
              f"- non-negative blocks: **{nonneg}/{nblocks}** (required {need_nonneg})",
              f"- positive blocks: **{positive}/{nblocks}** (required {need_pos})",
              f"- worst block net: **{worst:+d}**"]
    if gate:
        lines += [
            "- V2 is development-promising.",
            "- A separate prospective freeze is required before shadow use."
        ]
    else:
        lines += [
            "- V2 fails the frozen development gate.",
            "- No prospective reversal FLIP challenger is authorized from this version."
        ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
