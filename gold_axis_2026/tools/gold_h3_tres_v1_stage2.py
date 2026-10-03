from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

S1=AX/"GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_TRES_V1_STAGE2_PREDICTIONS_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_TRES_V1_STAGE2_BLOCK_METRICS_2026-10-04.csv"
OUT_COEF=AX/"GOLD_H3_TRES_V1_STAGE2_SURVIVAL_COEFFICIENTS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_TRES_V1_STAGE2_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_TRES_V1_STAGE2_RESULT_2026-10-04.md"

SEED=20261004
MIN_TRAIN=120

BASE_FEATURES=[
    "v5_confidence",
    "abs_h_ret_12",
    "trend_strength",
    "opposite_semivar_share",
    "deceleration_6h",
    "path_consistency",
    "adverse_excursion",
    "gc_volume_z20",
    "signed_opt_pressure",
    "signed_d_opt_pressure",
    "opt_total_z20",
]
SURV_FEATURES=["F_reversal","F_continuation","hR1","expected_event_day"]
AUG_FEATURES=BASE_FEATURES+SURV_FEATURES

def load():
    s=pd.read_csv(S1)
    f=pd.read_csv(FEAT)
    for d in [s,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns:
                d[c]=pd.to_datetime(d[c])
    keep=["feature_cutoff_date"]+BASE_FEATURES
    z=s.merge(f[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z[z.eligible_v5_continuation.astype(bool)].copy()
    z=z.dropna(subset=AUG_FEATURES+["rescue_target"])
    z["month_key"]=z.forecast_issue_date.dt.to_period("M").astype(str)
    return z.sort_values("forecast_issue_date").reset_index(drop=True)

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=.50,solver="lbfgs",penalty="l2",
            max_iter=3000,random_state=SEED
        ))
    ])

def logloss(y,p):
    p=np.clip(np.asarray(p,float),1e-8,1-1e-8)
    y=np.asarray(y,int)
    return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))

def auc(y,p):
    y=np.asarray(y,int)
    if len(np.unique(y))<2:
        return np.nan
    return float(roc_auc_score(y,p))

def replay(z):
    rows=[]
    coef_rows=[]
    leakage_fail=0
    for mk in sorted(z.month_key.unique()):
        te=z[z.month_key==mk].copy()
        if te.empty: continue
        first_cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=z[
            (z.target_end_date_h3<=first_cutoff)
            & (z.forecast_issue_date<first_issue)
        ].copy()
        if len(tr)<MIN_TRAIN or tr.rescue_target.nunique()<2:
            continue
        if (tr.target_end_date_h3>first_cutoff).any():
            leakage_fail+=1
            continue

        mb=make_model()
        ma=make_model()
        ytr=tr.rescue_target.astype(int).to_numpy()
        mb.fit(tr[BASE_FEATURES].to_numpy(float),ytr)
        ma.fit(tr[AUG_FEATURES].to_numpy(float),ytr)

        pb=mb.predict_proba(te[BASE_FEATURES].to_numpy(float))[:,1]
        pa=ma.predict_proba(te[AUG_FEATURES].to_numpy(float))[:,1]

        scaler=ma.named_steps["scale"]
        lr=ma.named_steps["model"]
        coefs=lr.coef_[0]
        for sf in SURV_FEATURES:
            i=AUG_FEATURES.index(sf)
            coef_rows.append({
                "month_key":mk,
                "train_n":len(tr),
                "feature":sf,
                "coef_standardized":float(coefs[i])
            })

        for r,p0,p1 in zip(te.itertuples(),pb,pa):
            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),
                "month":str(r.month),
                "rescue_target":int(r.rescue_target),
                "terminal_reversal":int(r.terminal_reversal),
                "F_reversal":float(r.F_reversal),
                "F_continuation":float(r.F_continuation),
                "hR1":float(r.hR1),
                "expected_event_day":float(r.expected_event_day),
                "p_error_base":float(p0),
                "p_error_aug":float(p1),
                "train_n":len(tr),
                "train_max_target_end":tr.target_end_date_h3.max(),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True),pd.DataFrame(coef_rows),leakage_fail

def block_name(d):
    d=pd.Timestamp(d)
    return f"{d.year}_{'H1' if d.month<=6 else 'H2'}"

def met(g):
    y=g.rescue_target.astype(int).to_numpy()
    pb=g.p_error_base.to_numpy(float)
    pa=g.p_error_aug.to_numpy(float)
    return {
        "n":len(g),
        "base_auc":auc(y,pb),
        "aug_auc":auc(y,pa),
        "auc_delta":auc(y,pa)-auc(y,pb) if np.isfinite(auc(y,pa)) and np.isfinite(auc(y,pb)) else np.nan,
        "base_brier":float(np.mean((pb-y)**2)),
        "aug_brier":float(np.mean((pa-y)**2)),
        "brier_delta":float(np.mean((pa-y)**2)-np.mean((pb-y)**2)),
        "base_logloss":logloss(y,pb),
        "aug_logloss":logloss(y,pa),
        "logloss_delta":logloss(y,pa)-logloss(y,pb),
        "error_rate":float(y.mean())
    }

def top_bottom(g):
    lo=float(g.p_error_aug.quantile(.20))
    hi=float(g.p_error_aug.quantile(.80))
    low=g[g.p_error_aug<=lo]
    high=g[g.p_error_aug>=hi]
    return {
        "low_cut":lo,"high_cut":hi,
        "low_n":len(low),"high_n":len(high),
        "low_error_rate":float(low.rescue_target.mean()),
        "high_error_rate":float(high.rescue_target.mean()),
        "separation":float(high.rescue_target.mean()-low.rescue_target.mean())
    }

def main():
    z=load()
    pred,coef,leakage_fail=replay(z)
    if pred.empty:
        raise RuntimeError("No Stage2 predictions generated")
    pred["block"]=pred.forecast_issue_date.map(block_name)
    pred.to_csv(OUT_PRED,index=False)
    coef.to_csv(OUT_COEF,index=False)

    agg=met(pred)
    tb=top_bottom(pred)

    block_rows=[]
    for b,g in pred.groupby("block",sort=False):
        x=met(g); x["block"]=b
        x["top_bottom_sep"]=top_bottom(g)["separation"]
        block_rows.append(x)
    bdf=pd.DataFrame(block_rows)
    bdf.to_csv(OUT_BLOCK,index=False)

    nblocks=len(bdf)
    not_worse_req=math.ceil(.75*nblocks)
    improve_req=math.ceil(.50*nblocks)
    not_worse=int((bdf.aug_auc>=bdf.base_auc-.02).sum())
    improve=int((bdf.aug_auc>bdf.base_auc).sum())

    gate=bool(
        agg["aug_auc"]>=.62
        and agg["aug_auc"]>=agg["base_auc"]+.01
        and agg["aug_brier"]<agg["base_brier"]
        and agg["aug_logloss"]<agg["base_logloss"]
        and tb["separation"]>=.25
        and not_worse>=not_worse_req
        and improve>=improve_req
        and leakage_fail==0
    )
    status="TRES_ERROR_RISK_PASS" if gate else "NO_INCREMENTAL_TRES_ERROR_RISK"

    coef_summary=[]
    for sf,g in coef.groupby("feature"):
        coef_summary.append({
            "feature":sf,
            "months":len(g),
            "mean_coef":float(g.coef_standardized.mean()),
            "median_coef":float(g.coef_standardized.median()),
            "positive_share":float((g.coef_standardized>0).mean())
        })

    corr=float(pred[["F_reversal","p_error_aug"]].corr().iloc[0,1])

    # cross-state diagnostic without threshold tuning: median splits.
    fr_med=float(pred.F_reversal.median())
    pe_med=float(pred.p_error_aug.median())
    cross=[]
    for name,mask in [
        ("HIGH_FR_HIGH_ERR",(pred.F_reversal>=fr_med)&(pred.p_error_aug>=pe_med)),
        ("HIGH_FR_LOW_ERR",(pred.F_reversal>=fr_med)&(pred.p_error_aug<pe_med)),
        ("LOW_FR_HIGH_ERR",(pred.F_reversal<fr_med)&(pred.p_error_aug>=pe_med)),
        ("LOW_FR_LOW_ERR",(pred.F_reversal<fr_med)&(pred.p_error_aug<pe_med)),
    ]:
        g=pred[mask]
        cross.append({"state":name,"n":len(g),"error_rate":float(g.rescue_target.mean()) if len(g) else np.nan})

    summary={
        "schema":"TRES_H3_V1_STAGE2",
        "status":status,
        "prediction_rows":len(pred),
        "first_scored_origin":str(pred.feature_cutoff_date.min().date()),
        "last_scored_origin":str(pred.feature_cutoff_date.max().date()),
        "aggregate":agg,
        "top_bottom":tb,
        "blocks":block_rows,
        "not_worse_blocks":not_worse,
        "not_worse_required":not_worse_req,
        "improved_auc_blocks":improve,
        "improved_required":improve_req,
        "training_maturity_leakage_failures":leakage_fail,
        "survival_coefficient_summary":coef_summary,
        "F_reversal_p_error_corr":corr,
        "median_cross_states":cross
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# TRES-H3 V1 — STAGE 2 V5 ERROR-RISK RESULT","",
        f"**Status:** **{status}**  ",
        f"- predictions: **{len(pred)}**",
        f"- scored origins: **{summary['first_scored_origin']} .. {summary['last_scored_origin']}**",
        f"- maturity leakage failures: **{leakage_fail}**","",
        "## Aggregate baseline vs survival-augmented error risk","",
        "| Metric | Baseline | + Survival | Delta |",
        "|---|---:|---:|---:|",
        f"| ROC AUC | {agg['base_auc']:.4f} | {agg['aug_auc']:.4f} | {agg['auc_delta']:+.4f} |",
        f"| Brier | {agg['base_brier']:.4f} | {agg['aug_brier']:.4f} | {agg['brier_delta']:+.4f} |",
        f"| Log loss | {agg['base_logloss']:.4f} | {agg['aug_logloss']:.4f} | {agg['logloss_delta']:+.4f} |",
        "",
        "## Augmented p_error concentration","",
        f"- bottom quintile error rate: **{100*tb['low_error_rate']:.2f}%**",
        f"- top quintile error rate: **{100*tb['high_error_rate']:.2f}%**",
        f"- separation: **{100*tb['separation']:+.2f} pp**","",
        "## Half-year stability","",
        "| Block | N | Base AUC | Aug AUC | ΔAUC | ΔBrier | ΔLogloss | Top-bottom error sep |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in bdf.itertuples():
        lines.append(
            f"| {r.block} | {r.n} | {r.base_auc:.3f} | {r.aug_auc:.3f} | {r.auc_delta:+.3f} | "
            f"{r.brier_delta:+.4f} | {r.logloss_delta:+.4f} | {100*r.top_bottom_sep:+.1f}pp |"
        )

    lines += ["","## Survival feature coefficient stability","",
              "| Feature | Mean standardized coef | Median | Positive months |",
              "|---|---:|---:|---:|"]
    for x in coef_summary:
        lines.append(f"| {x['feature']} | {x['mean_coef']:+.3f} | {x['median_coef']:+.3f} | {100*x['positive_share']:.1f}% |")

    lines += ["","## Gate","",
              f"- AUC non-worse blocks: **{not_worse}/{nblocks}** (required {not_worse_req})",
              f"- AUC improved blocks: **{improve}/{nblocks}** (required {improve_req})"]
    if gate:
        lines += [
            "- Stage 2 passed. Stage 3 confidence-governor design is authorized.",
            "- No intervention threshold has been selected yet."
        ]
    else:
        lines += [
            "- Survival outputs do not add enough stable incremental V5 error-risk information under the frozen gate.",
            "- Stage 3 is not authorized under TRES V1."
        ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
