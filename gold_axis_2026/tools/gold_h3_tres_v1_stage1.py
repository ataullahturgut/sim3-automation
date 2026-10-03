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

OUT_PRED=AX/"GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_TRES_V1_STAGE1_BLOCK_METRICS_2026-10-04.csv"
OUT_QUINT=AX/"GOLD_H3_TRES_V1_STAGE1_QUINTILES_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_TRES_V1_STAGE1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_TRES_V1_STAGE1_RESULT_2026-10-04.md"

SEED=20261004
MIN_TRAIN_ORIGINS=250
IDENTITY_TOL=1e-10

FEATURES=[
    "momentum_up",
    "abs_h_ret_12",
    "trend_strength",
    "opposite_semivar_share",
    "deceleration_6h",
    "path_consistency",
    "trend_close_location",
    "opposite_extreme_recency",
    "jump_concentration",
    "trend_to_range",
    "adverse_excursion",
    "v5_confidence",
    "gc_dlog_volume_1",
    "gc_volume_z20",
    "gc_volume_accel_5",
    "signed_opt_pressure",
    "signed_d_opt_pressure",
    "opt_total_z20",
]
LONG_FEATURES=FEATURES+["day2","day3"]

def load():
    e=pd.read_csv(EVENT)
    f=pd.read_csv(FEAT)
    for d in [e,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns:
                d[c]=pd.to_datetime(d[c])

    keep=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "year","month","y_up","target_r3","momentum_up","rescue_target",
        "eligible_v5_continuation","v5_pred","p_helios_v5_dce"
    ]+FEATURES
    keep=list(dict.fromkeys(keep))
    z=e.merge(
        f[keep],
        on=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"],
        how="inner",
        suffixes=("_event","")
    )
    # Prefer event-side canonical labels where duplicated.
    for c in ["year","y_up","target_r3","momentum_up"]:
        ce=c+"_event"
        if ce in z.columns:
            z[c]=z[ce]
    z["terminal_reversal"]=z["terminal_reversal"].astype(int)
    z["event_type"]=z["event_type_1p0"].astype(str)
    z["event_day"]=z["event_day_1p0"]
    z["month_key"]=z.forecast_issue_date.dt.to_period("M").astype(str)
    z=z.dropna(subset=FEATURES).sort_values("forecast_issue_date").reset_index(drop=True)
    return z

def long_rows(origins):
    rows=[]
    for r in origins.itertuples():
        et=str(r.event_type)
        ed=None if pd.isna(r.event_day) else int(r.event_day)
        base={c:float(getattr(r,c)) for c in FEATURES}
        for h in [1,2,3]:
            cls=0
            if et!="CENSORED" and ed==h:
                cls=1 if et=="CONTINUATION" else 2
            rr={**base,"day2":float(h==2),"day3":float(h==3),"class":cls}
            rows.append(rr)
            if cls!=0:
                break
    return pd.DataFrame(rows)

def model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=.50,solver="lbfgs",penalty="l2",
            max_iter=3000,random_state=SEED
        ))
    ])

def probs_for_origin(m,r):
    X=[]
    base=[float(getattr(r,c)) for c in FEATURES]
    for h in [1,2,3]:
        X.append(base+[float(h==2),float(h==3)])
    pp=m.predict_proba(np.asarray(X,float))
    classes=list(m.named_steps["model"].classes_)
    idx={int(c):i for i,c in enumerate(classes)}
    if set(idx)!={0,1,2}:
        raise RuntimeError(f"Missing hazard class in fitted model: {classes}")
    S=1.0
    FR=0.0
    FC=0.0
    hR=[]
    hC=[]
    h0=[]
    event_day_num=0.0
    event_prob=0.0
    for h,row in enumerate(pp,1):
        p0=float(row[idx[0]])
        pc=float(row[idx[1]])
        pr=float(row[idx[2]])
        h0.append(p0); hC.append(pc); hR.append(pr)
        cause_mass=S*(pc+pr)
        event_day_num += h*cause_mass
        event_prob += cause_mass
        FC += S*pc
        FR += S*pr
        S *= p0
    exp_day=event_day_num/event_prob if event_prob>0 else np.nan
    ident=abs(FR+FC+S-1.0)
    return {
        "F_reversal":FR,"F_continuation":FC,"S3":S,
        "hR1":hR[0],"hR2":hR[1],"hR3":hR[2],
        "hC1":hC[0],"hC2":hC[1],"hC3":hC[2],
        "h01":h0[0],"h02":h0[1],"h03":h0[2],
        "expected_event_day":exp_day,
        "identity_error":ident
    }

def replay(z):
    rows=[]
    leakage_fail=0
    months=sorted(z.month_key.unique())
    for mk in months:
        te=z[z.month_key==mk].copy()
        if te.empty: continue
        first_cutoff=te.feature_cutoff_date.min()
        tr=z[
            (z.target_end_date_h3<=first_cutoff)
            & (z.forecast_issue_date<te.forecast_issue_date.min())
        ].copy()
        if len(tr)<MIN_TRAIN_ORIGINS:
            continue
        if (tr.target_end_date_h3>first_cutoff).any():
            leakage_fail+=1
            continue
        L=long_rows(tr)
        if L["class"].nunique()<3:
            continue
        m=model()
        m.fit(L[LONG_FEATURES].to_numpy(float),L["class"].astype(int).to_numpy())
        for r in te.itertuples():
            p=probs_for_origin(m,r)
            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),
                "month":str(r.month),
                "event_type":str(r.event_type),
                "event_day":None if pd.isna(r.event_day) else int(r.event_day),
                "terminal_reversal":int(r.terminal_reversal),
                "eligible_v5_continuation":bool(r.eligible_v5_continuation),
                "rescue_target":int(r.rescue_target),
                "v5_pred":int(r.v5_pred),
                "p_v5":float(r.p_helios_v5_dce),
                "train_origins":len(tr),
                "train_max_target_end":tr.target_end_date_h3.max(),
                **p
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True),leakage_fail

def first_event_class(s):
    return 0 if s=="CENSORED" else (1 if s=="CONTINUATION" else 2)

def multiclass_logloss(df):
    vals=[]
    for r in df.itertuples():
        probs=[r.S3,r.F_continuation,r.F_reversal]
        y=first_event_class(r.event_type)
        p=float(np.clip(probs[y],1e-12,1.0))
        vals.append(-math.log(p))
    return float(np.mean(vals))

def block_name(d):
    d=pd.Timestamp(d)
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def top_bottom(g,target_col):
    q=g.dropna(subset=["F_reversal",target_col]).copy()
    if len(q)<20:
        return None
    lo=float(q.F_reversal.quantile(.20))
    hi=float(q.F_reversal.quantile(.80))
    low=q[q.F_reversal<=lo]
    high=q[q.F_reversal>=hi]
    if len(low)==0 or len(high)==0:
        return None
    return {
        "low_cut":lo,"high_cut":hi,
        "low_n":len(low),"high_n":len(high),
        "low_rate":float(low[target_col].mean()),
        "high_rate":float(high[target_col].mean()),
        "separation":float(high[target_col].mean()-low[target_col].mean())
    }

def quintiles(df):
    rows=[]
    for scope,g in [("ALL",df)]+[(b,h) for b,h in df.groupby("block",sort=False)]:
        q=g.copy()
        if len(q)<20: continue
        try:
            q["q"]=pd.qcut(q.F_reversal,5,labels=False,duplicates="drop")+1
        except Exception:
            continue
        for qi,h in q.groupby("q"):
            ev=(h.event_type=="REVERSAL").astype(int)
            rows.append({
                "scope":scope,"quintile":int(qi),"n":len(h),
                "mean_F_reversal":float(h.F_reversal.mean()),
                "first_passage_reversal_rate":float(ev.mean()),
                "terminal_reversal_rate":float(h.terminal_reversal.mean()),
                "v5_wrong_rate_eligible":float(h.loc[h.eligible_v5_continuation,"rescue_target"].mean())
                    if h.eligible_v5_continuation.any() else np.nan
            })
    return pd.DataFrame(rows)

def main():
    z=load()
    pred,leakage_fail=replay(z)
    if pred.empty:
        raise RuntimeError("No Stage1 predictions generated")
    pred["block"]=pred.forecast_issue_date.map(block_name)
    pred["first_passage_reversal"]=(pred.event_type=="REVERSAL").astype(int)
    pred.to_csv(OUT_PRED,index=False)

    identity_fail=int((pred.identity_error>IDENTITY_TOL).sum())
    max_identity=float(pred.identity_error.max())

    block_rows=[]
    for b,g in pred.groupby("block",sort=False):
        fp=top_bottom(g,"first_passage_reversal")
        tr=top_bottom(g,"terminal_reversal")
        if fp is None or tr is None: continue
        block_rows.append({
            "block":b,"n":len(g),
            "fp_low_rate":fp["low_rate"],"fp_high_rate":fp["high_rate"],
            "fp_separation":fp["separation"],
            "terminal_low_rate":tr["low_rate"],"terminal_high_rate":tr["high_rate"],
            "terminal_separation":tr["separation"],
            "multiclass_logloss":multiclass_logloss(g),
            "reversal_brier":float(np.mean((g.F_reversal-g.first_passage_reversal)**2)),
            "mean_F_reversal":float(g.F_reversal.mean()),
            "actual_fp_reversal":float(g.first_passage_reversal.mean())
        })
    bdf=pd.DataFrame(block_rows)
    bdf.to_csv(OUT_BLOCK,index=False)

    agg_fp=top_bottom(pred,"first_passage_reversal")
    agg_tr=top_bottom(pred,"terminal_reversal")
    nblocks=len(bdf)
    need=math.ceil(.8*nblocks) if nblocks else 999
    positive_fp=int((bdf.fp_separation>0).sum()) if nblocks else 0
    nonneg_tr=int((bdf.terminal_separation>=0).sum()) if nblocks else 0

    gate=bool(
        agg_fp is not None and agg_tr is not None
        and agg_fp["separation"]>=.20
        and positive_fp>=need
        and agg_tr["separation"]>=.10
        and nonneg_tr>=need
        and identity_fail==0
        and leakage_fail==0
    )
    status="TRES_EVENT_SIGNAL_PASS" if gate else "NO_TRES_EVENT_SIGNAL"

    qdf=quintiles(pred)
    qdf.to_csv(OUT_QUINT,index=False)

    summary={
        "schema":"TRES_H3_V1_STAGE1",
        "status":status,
        "prediction_rows":len(pred),
        "first_scored_origin":str(pred.feature_cutoff_date.min().date()),
        "last_scored_origin":str(pred.feature_cutoff_date.max().date()),
        "available_blocks":nblocks,
        "required_good_blocks":need,
        "positive_fp_blocks":positive_fp,
        "nonnegative_terminal_blocks":nonneg_tr,
        "aggregate_first_passage":agg_fp,
        "aggregate_terminal":agg_tr,
        "identity_failures":identity_fail,
        "max_identity_error":max_identity,
        "training_maturity_leakage_failures":leakage_fail,
        "multiclass_logloss":multiclass_logloss(pred),
        "reversal_brier":float(np.mean((pred.F_reversal-pred.first_passage_reversal)**2)),
        "block_metrics":bdf.to_dict("records"),
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# TRES-H3 V1 — STAGE 1 COMPETING-RISK RESULT","",
        f"**Status:** **{status}**  ",
        f"- predictions: **{len(pred)}**",
        f"- scored origins: **{summary['first_scored_origin']} .. {summary['last_scored_origin']}**",
        f"- cumulative-incidence identity failures: **{identity_fail}**",
        f"- training-maturity leakage failures: **{leakage_fail}**",
        f"- multiclass event log loss: **{summary['multiclass_logloss']:.4f}**",
        f"- first-passage reversal Brier: **{summary['reversal_brier']:.4f}**",
        "",
        "## Aggregate top-vs-bottom F_reversal quintile","",
        f"- first-passage reversal: **{100*agg_fp['low_rate']:.2f}% -> {100*agg_fp['high_rate']:.2f}%**, separation **{100*agg_fp['separation']:+.2f} pp**",
        f"- terminal H3 reversal: **{100*agg_tr['low_rate']:.2f}% -> {100*agg_tr['high_rate']:.2f}%**, separation **{100*agg_tr['separation']:+.2f} pp**",
        "",
        "## Half-year stability","",
        "| Block | N | FP low | FP high | FP sep | Terminal low | Terminal high | Terminal sep | Brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.n} | {100*r.fp_low_rate:.1f}% | {100*r.fp_high_rate:.1f}% | "
            f"{100*r.fp_separation:+.1f}pp | {100*r.terminal_low_rate:.1f}% | "
            f"{100*r.terminal_high_rate:.1f}% | {100*r.terminal_separation:+.1f}pp | {r.reversal_brier:.4f} |"
        )

    lines += ["","## Gate","",
              f"- positive first-passage blocks: **{positive_fp}/{nblocks}** (required {need})",
              f"- non-negative terminal-transfer blocks: **{nonneg_tr}/{nblocks}** (required {need})"]
    if gate:
        lines += [
            "- Stage 1 passed. Stage 2 V5 error-risk modeling is authorized.",
            "- No FLIP/DAMP threshold has been selected in Stage 1."
        ]
    else:
        lines += [
            "- Stage 1 failed the frozen information gate.",
            "- Stage 2 is not authorized under TRES V1."
        ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
