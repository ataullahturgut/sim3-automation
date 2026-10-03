from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
OUT_PANEL=AX/"GOLD_H3_HAZARD_V1_PANEL_2026-10-03.csv"
OUT_PRED=AX/"GOLD_H3_HAZARD_V1_PREDICTIONS_2026-10-03.csv"
OUT_GRID=AX/"GOLD_H3_HAZARD_V1_THRESHOLD_GRID_2026-10-03.csv"
OUT_JSON=AX/"GOLD_H3_HAZARD_V1_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_HAZARD_V1_RESULT_2026-10-03.md"

SEED=20261003
THRESH_GRID=[0.35,0.40,0.45,0.50,0.55,0.60]
FEATURES=[
    "trend_age","log_trend_age","trend_age_sq",
    "switches_10","switches_20",
    "trend_strength","trend_strength_sq","trend_strength_cu",
    "deceleration_6h","session_against_trend","opposite_semivar_share",
    "distance_from_trend_extreme","adverse_excursion","jump_concentration",
    "age_x_deceleration","age_x_opposite_semivar","age_x_adverse_excursion",
]

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def build_panel():
    p=pd.read_csv(PANEL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        p[c]=pd.to_datetime(p[c],errors="raise")
    p=p.sort_values("feature_cutoff_date").reset_index(drop=True)
    # Duration of current momentum sign across origin observations.
    ages=[]; prev=None; age=0
    for m in p.momentum_up.astype(int):
        if prev is None or m!=prev: age=1
        else: age+=1
        ages.append(age); prev=m
    p["trend_age"]=np.asarray(ages,float)
    p["log_trend_age"]=np.log1p(p.trend_age)
    cap_age=np.minimum(p.trend_age,20.0)
    p["trend_age_sq"]=(cap_age**2)/400.0

    sw=(p.momentum_up.astype(int)!=p.momentum_up.astype(int).shift(1)).astype(float)
    sw.iloc[0]=0.0
    p["switches_10"]=sw.rolling(10,min_periods=1).sum()
    p["switches_20"]=sw.rolling(20,min_periods=1).sum()

    ts=np.minimum(pd.to_numeric(p.trend_strength),5.0)
    p["trend_strength_sq"]=ts**2
    p["trend_strength_cu"]=ts**3
    p["distance_from_trend_extreme"]=1.0-p.trend_close_location.astype(float)
    p["age_x_deceleration"]=p.log_trend_age*p.deceleration_6h
    p["age_x_opposite_semivar"]=p.log_trend_age*p.opposite_semivar_share
    p["age_x_adverse_excursion"]=p.log_trend_age*p.adverse_excursion
    p["month_key"]=p.forecast_issue_date.dt.to_period("M").astype(str)
    q=p.dropna(subset=FEATURES+["reversal_target","aurora_follows_momentum"]).copy()
    return q.reset_index(drop=True)

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=4000,
                                    class_weight="balanced",random_state=SEED))
    ])

def walk(panel):
    test=panel[panel.forecast_issue_date>=pd.Timestamp("2023-01-01")].copy()
    rows=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        first_issue=te.forecast_issue_date.min()
        tr=panel[(panel.target_end_date_h3<=cutoff)&(panel.forecast_issue_date<first_issue)].copy()
        if len(tr)<80 or tr.reversal_target.nunique()<2: continue
        model=make_model()
        model.fit(tr[FEATURES].to_numpy(float),tr.reversal_target.astype(int).to_numpy())
        pr=model.predict_proba(te[FEATURES].to_numpy(float))[:,1]
        for r,pv in zip(te.itertuples(),pr):
            rows.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "p_aurora":float(r.p_aurora),"momentum_up":int(r.momentum_up),
                "reversal_target":int(r.reversal_target),"aurora_pred":int(r.aurora_pred),
                "aurora_follows_momentum":bool(r.aurora_follows_momentum),
                "trend_age":float(r.trend_age),"switches_10":float(r.switches_10),
                "switches_20":float(r.switches_20),"trend_strength":float(r.trend_strength),
                "p_hazard_reversal":float(pv),"train_n":int(len(tr))
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def f2(p,r):
    if p<=0 or r<=0: return 0.0
    return 5*p*r/(4*p+r)

def cand_metrics(z,th):
    e=z[z.aurora_follows_momentum.astype(bool)].copy()
    c=e.p_hazard_reversal>=th
    y=e.reversal_target.astype(bool)
    tp=int((c&y).sum()); fp=int((c&~y).sum()); fn=int((~c&y).sum())
    precision=tp/max(tp+fp,1); recall=tp/max(tp+fn,1)
    rate=float(c.mean()) if len(c) else 0.0
    return {"threshold":float(th),"eligible_n":int(len(e)),"candidate_n":int(c.sum()),
            "true_reversal_n":int(y.sum()),"tp":tp,"fp":fp,"fn":fn,
            "precision":precision,"recall":recall,"candidate_rate":rate,
            "f2":f2(precision,recall),
            "eligible":bool(precision>=.45 and rate<=.40)}

def merge_v5(pred):
    v=pd.read_csv(V5)
    v["feature_cutoff_date"]=pd.to_datetime(v.feature_cutoff_date)
    keep=["feature_cutoff_date","p_helios_v5_dce","opal_override_check"]
    z=pred.merge(v[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z

def period_stats(z,th,year):
    q=z[(z.year==year)&z.aurora_follows_momentum.astype(bool)].copy()
    q["hazard_candidate"]=q.p_hazard_reversal>=th
    y=q.reversal_target.astype(bool); c=q.hazard_candidate.astype(bool)
    tp=int((c&y).sum()); fp=int((c&~y).sum())
    precision=tp/max(tp+fp,1); recall=tp/max(int(y.sum()),1)
    rate=float(c.mean()) if len(c) else 0.0
    op=q.opal_candidate.astype(bool)
    op_tp=int((op&y).sum())
    op_rec=op_tp/max(int(y.sum()),1)
    op_prec=op_tp/max(int(op.sum()),1)
    only=int((c&y&~op).sum())
    union=(c|op)
    union_rec=float((union&y).sum()/max(int(y.sum()),1))
    brier=float(np.mean((q.p_hazard_reversal-q.reversal_target)**2)) if len(q) else np.nan
    ll=float(log_loss(q.reversal_target,np.clip(q.p_hazard_reversal,1e-6,1-1e-6),labels=[0,1])) if len(q) else np.nan
    return {
        "year":int(year),"eligible_n":int(len(q)),"true_reversal_n":int(y.sum()),
        "hazard_candidate_n":int(c.sum()),"hazard_precision":precision,
        "hazard_recall":recall,"hazard_candidate_rate":rate,
        "opal_candidate_n":int(op.sum()),"opal_precision":op_prec,"opal_recall":op_rec,
        "hazard_only_true_reversal_n":only,"union_recall":union_rec,
        "brier":brier,"logloss":ll
    }

def main():
    panel=build_panel()
    panel.to_csv(OUT_PANEL,index=False)
    pred=walk(panel)
    if pred.empty: raise RuntimeError("NO_HAZARD_PREDICTIONS")
    pred=merge_v5(pred)

    dev=pred[pred.year.isin([2023,2024])].copy()
    grid=pd.DataFrame([cand_metrics(dev,t) for t in THRESH_GRID])
    grid.to_csv(OUT_GRID,index=False)
    elig=grid[grid.eligible].copy()

    selected=None; confirm=None; holdout=None; status=None
    if elig.empty:
        status="NO_ELIGIBLE_HAZARD_THRESHOLD"
    else:
        elig=elig.sort_values(["f2","recall","precision","candidate_rate","threshold"],
                              ascending=[False,False,False,True,False])
        selected=float(elig.iloc[0].threshold)
        s25=period_stats(pred,selected,2025)
        confirm=bool(
            s25["hazard_recall"]>s25["opal_recall"]
            and s25["hazard_only_true_reversal_n"]>=1
            and s25["hazard_precision"]>=.40
            and s25["union_recall"]>s25["opal_recall"]
        )
        status="CONFIRM_PASS" if confirm else "CONFIRM_FAIL"
        if confirm:
            holdout=period_stats(pred,selected,2026)
            z=pred[(pred.year==2026)&pred.aurora_follows_momentum.astype(bool)].copy()
            z["hazard_candidate"]=z.p_hazard_reversal>=selected
            miss=(z.reversal_target==1)&(z.v5_pred==z.momentum_up)&(~z.opal_candidate)
            flowdir=1-z.momentum_up.astype(int)
            changed=z.hazard_candidate & (flowdir!=z.v5_pred)
            rescue=int((changed&(z.v5_pred!=z.y_up)&(flowdir==z.y_up)).sum())
            broken=int((changed&(z.v5_pred==z.y_up)&(flowdir!=z.y_up)).sum())
            holdout.update({
                "v5_missed_reversal_opal_no_candidate_n":int(miss.sum()),
                "hazard_hits_in_v5_missed_opal_no_candidate":int((miss&z.hazard_candidate).sum()),
                "diagnostic_v5_rescue":rescue,
                "diagnostic_v5_broken":broken,
                "diagnostic_v5_net":rescue-broken
            })
    pred.to_csv(OUT_PRED,index=False)
    summ={
        "schema":"HAZARD_H3_V1","status":status,"features":FEATURES,
        "selected_threshold":selected,
        "threshold_grid":grid.to_dict("records"),
        "confirmation_2025":period_stats(pred,selected,2025) if selected is not None else None,
        "confirmation_pass":confirm,
        "holdout_2026":holdout
    }
    OUT_JSON.write_text(json.dumps(summ,indent=2,default=str)+"\n")

    lines=["# HAZARD-H3 V1 — RESULT","",f"**Status:** **{status}**  ",
           "**Target:** duration-dependent termination of current 12h momentum within H3.","",
           "## DEV 2023-2024 threshold grid","",
           "| Th | Cand | Precision | Recall | Rate | F2 | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(f"| {r.threshold:.2f} | {r.candidate_n} | {100*r.precision:.2f}% | {100*r.recall:.2f}% | {100*r.candidate_rate:.2f}% | {r.f2:.4f} | {r.eligible} |")
    if selected is not None:
        s=period_stats(pred,selected,2025)
        lines += ["",f"## Selected threshold: {selected:.2f}","",
                  "## 2025 confirmation","",
                  f"- HAZARD recall: **{100*s['hazard_recall']:.2f}%**",
                  f"- OPAL recall same universe: **{100*s['opal_recall']:.2f}%**",
                  f"- HAZARD precision: **{100*s['hazard_precision']:.2f}%**",
                  f"- HAZARD-only true OPAL-missed reversals: **{s['hazard_only_true_reversal_n']}**",
                  f"- OPAL ∪ HAZARD recall: **{100*s['union_recall']:.2f}%**",
                  f"- Confirmation: **{'PASS' if confirm else 'FAIL'}**"]
        if confirm and holdout is not None:
            h=holdout
            lines += ["","## 2026 final holdout","",
                      f"- HAZARD recall: **{100*h['hazard_recall']:.2f}%**",
                      f"- HAZARD precision: **{100*h['hazard_precision']:.2f}%**",
                      f"- OPAL recall same universe: **{100*h['opal_recall']:.2f}%**",
                      f"- OPAL ∪ HAZARD recall: **{100*h['union_recall']:.2f}%**",
                      f"- HAZARD-only true reversals: **{h['hazard_only_true_reversal_n']}**",
                      f"- V5 missed reversal + OPAL no-candidate universe: **{h['v5_missed_reversal_opal_no_candidate_n']}**",
                      f"- HAZARD hits inside that universe: **{h['hazard_hits_in_v5_missed_opal_no_candidate']}**",
                      f"- Diagnostic V5 forced-flip rescue / broken / net: **{h['diagnostic_v5_rescue']} / {h['diagnostic_v5_broken']} / {h['diagnostic_v5_net']:+d}**"]
    lines += ["","## Governance","",
              "2026 was opened only after the preregistered 2025 confirmation gate. No HAZARD rule is promoted to HELIOS from this result alone."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
