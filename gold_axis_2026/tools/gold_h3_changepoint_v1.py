from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gold_axis_2026"
PANEL = OUT / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
OPAL = OUT / "GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"
V5 = OUT / "GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

SEED = 20261003
THRESHOLDS = [0.35,0.40,0.45,0.50,0.55,0.60]
BASE_STATES = [
    "trend_strength","opposite_semivar_share","deceleration_6h",
    "session_against_trend","path_consistency","trend_close_location",
    "jump_concentration","adverse_excursion"
]
WEAK_MAP = {
    "trend_strength": -1.0,
    "opposite_semivar_share": 1.0,
    "deceleration_6h": 1.0,
    "session_against_trend": 1.0,
    "path_consistency": -1.0,
    "trend_close_location": -1.0,
    "jump_concentration": 1.0,
    "adverse_excursion": 1.0,
}
ZNAME = {
    "trend_strength":"weak_trend_strength_z60",
    "opposite_semivar_share":"weak_opposite_semivar_z60",
    "deceleration_6h":"weak_deceleration_z60",
    "session_against_trend":"weak_session_z60",
    "path_consistency":"weak_path_consistency_z60",
    "trend_close_location":"weak_close_location_z60",
    "jump_concentration":"weak_jump_z60",
    "adverse_excursion":"weak_adverse_excursion_z60",
}
FEATURES = list(ZNAME.values()) + [
    "weakening_impulse","weakening_cusum_3","weakening_cusum_5",
    "weakening_share_5","dd_deceleration_1","dd_path_consistency_1",
    "dd_adverse_excursion_1"
]

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,solver="lbfgs",max_iter=3000,
            class_weight="balanced",random_state=SEED
        ))
    ])

def f2(precision, recall):
    if precision <= 0 or recall <= 0: return 0.0
    return 5*precision*recall/(4*precision+recall)

def candidate_metrics(y, cand):
    y=np.asarray(y,int); cand=np.asarray(cand,bool)
    tp=int(((y==1)&cand).sum()); fp=int(((y==0)&cand).sum()); fn=int(((y==1)&(~cand)).sum())
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    rate=float(cand.mean()) if len(cand) else 0.0
    return dict(eligible_n=int(len(y)),candidate_n=int(cand.sum()),true_reversal_n=int((y==1).sum()),
                tp=tp,fp=fp,fn=fn,precision=precision,recall=recall,candidate_rate=rate,f2=f2(precision,recall))

def build_panel():
    p=pd.read_csv(PANEL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        p[c]=pd.to_datetime(p[c],errors="raise")
    p=p.sort_values("feature_cutoff_date").reset_index(drop=True)

    for x in BASE_STATES:
        dx=f"d_{x}_1"
        p[dx]=p[x].astype(float).diff()
        weak=f"weak_{x}"
        p[weak]=WEAK_MAP[x]*p[dx]
        hist=p[weak].shift(1)
        mu=hist.rolling(60,min_periods=60).mean()
        sd=hist.rolling(60,min_periods=60).std(ddof=0)
        p[ZNAME[x]]=(p[weak]-mu)/(sd+1e-8)

    p["weakening_impulse"]=p[list(ZNAME.values())].mean(axis=1)
    pos=p["weakening_impulse"].clip(lower=0)
    p["weakening_cusum_3"]=pos.rolling(3,min_periods=3).sum()
    p["weakening_cusum_5"]=pos.rolling(5,min_periods=5).sum()
    p["weakening_share_5"]=(p["weakening_impulse"]>0).astype(float).rolling(5,min_periods=5).mean()

    p["dd_deceleration_1"]=p["d_deceleration_6h_1"].diff()
    p["dd_path_consistency_1"]=p["d_path_consistency_1"].diff()
    p["dd_adverse_excursion_1"]=p["d_adverse_excursion_1"].diff()

    p=p.dropna(subset=FEATURES+["reversal_target"]).copy()
    p["month_key"]=p["forecast_issue_date"].dt.to_period("M").astype(str)
    return p.reset_index(drop=True)

def expanding_predictions(panel):
    out=[]
    test=panel[panel.forecast_issue_date>=pd.Timestamp("2023-01-01")].copy()
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=panel[panel.target_end_date_h3<=cutoff].copy()
        if len(tr)<80 or tr.reversal_target.nunique()<2:
            continue
        m=make_model()
        m.fit(tr[FEATURES].to_numpy(float),tr.reversal_target.astype(int).to_numpy())
        pr=m.predict_proba(te[FEATURES].to_numpy(float))[:,1]
        q=te[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","year","month","y_up","target_r3","p_aurora",
              "h_ret_12","momentum_up","reversal_target","aurora_pred","aurora_follows_momentum"]].copy()
        q["p_changepoint_reversal"]=pr
        q["train_n"]=len(tr)
        out.append(q)
    return pd.concat(out,ignore_index=True).sort_values("forecast_issue_date").reset_index(drop=True)

def threshold_grid(pred):
    d=pred[pred.year.isin([2023,2024]) & pred.aurora_follows_momentum.astype(bool)].copy()
    rows=[]
    for th in THRESHOLDS:
        m=candidate_metrics(d.reversal_target,(d.p_changepoint_reversal>=th))
        elig=bool(m["precision"]>=0.45 and m["candidate_rate"]<=0.40)
        rows.append({"threshold":th,**m,"eligible":elig})
    tab=pd.DataFrame(rows)
    e=tab[tab.eligible].copy()
    if e.empty: return tab,None
    e=e.sort_values(["f2","recall","precision","candidate_rate","threshold"],ascending=[False,False,False,True,False])
    return tab,float(e.iloc[0].threshold)

def load_opal():
    o=pd.read_csv(OPAL)
    o["forecast_issue_date"]=pd.to_datetime(o.forecast_issue_date)
    o["opal_candidate"]=o["override"].astype(str).str.lower().eq("true")
    return o[["forecast_issue_date","opal_candidate"]]

def confirmation(pred,th):
    d=pred[(pred.year==2025)&pred.aurora_follows_momentum.astype(bool)].copy()
    d=d.merge(load_opal(),on="forecast_issue_date",how="left",validate="one_to_one")
    d["opal_candidate"]=d.opal_candidate.fillna(False).astype(bool)
    d["cp_candidate"]=d.p_changepoint_reversal>=th
    cp=candidate_metrics(d.reversal_target,d.cp_candidate)
    op=candidate_metrics(d.reversal_target,d.opal_candidate)
    union=candidate_metrics(d.reversal_target,d.cp_candidate|d.opal_candidate)
    cp_only_true=int(((d.reversal_target==1)&d.cp_candidate&(~d.opal_candidate)).sum())
    passed=bool(cp["recall"]>op["recall"] and cp_only_true>=1 and cp["precision"]>=0.40 and union["recall"]>op["recall"])
    return dict(pass_gate=passed,changepoint=cp,opal=op,union=union,changepoint_only_true=cp_only_true)

def holdout_2026(pred,th):
    d=pred[(pred.year==2026)&pred.aurora_follows_momentum.astype(bool)].copy()
    d=d.merge(load_opal(),on="forecast_issue_date",how="left",validate="one_to_one")
    d["opal_candidate"]=d.opal_candidate.fillna(False).astype(bool)
    d["cp_candidate"]=d.p_changepoint_reversal>=th
    cp=candidate_metrics(d.reversal_target,d.cp_candidate)
    op=candidate_metrics(d.reversal_target,d.opal_candidate)
    union=candidate_metrics(d.reversal_target,d.cp_candidate|d.opal_candidate)
    cp_only_true=int(((d.reversal_target==1)&d.cp_candidate&(~d.opal_candidate)).sum())

    v=pd.read_csv(V5)
    v["forecast_issue_date"]=pd.to_datetime(v.forecast_issue_date)
    v["v5_pred"]=(v.p_helios_v5_dce.astype(float)>=0.5).astype(int)
    d=d.merge(v[["forecast_issue_date","v5_pred"]],on="forecast_issue_date",how="left",validate="one_to_one")
    forced=np.where(d.cp_candidate,1-d.momentum_up.astype(int),d.v5_pred.astype(int))
    rescued=int(((d.v5_pred!=d.y_up)&(forced==d.y_up)).sum())
    broken=int(((d.v5_pred==d.y_up)&(forced!=d.y_up)).sum())
    missed_opal=(d.v5_pred!=d.y_up)&(d.reversal_target==1)&(~d.opal_candidate)
    missed_n=int(missed_opal.sum())
    missed_nominated=int((missed_opal&d.cp_candidate).sum())
    return dict(changepoint=cp,opal=op,union=union,changepoint_only_true=cp_only_true,
                v5_missed_opal_no_candidate_n=missed_n,
                v5_missed_opal_no_candidate_nominated=missed_nominated,
                diagnostic_forced_flip_rescued=rescued,
                diagnostic_forced_flip_broken=broken,
                diagnostic_forced_flip_net=rescued-broken)

def main():
    panel=build_panel()
    pred=expanding_predictions(panel)
    grid,th=threshold_grid(pred)
    grid.to_csv(OUT/"GOLD_H3_CHANGEPOINT_V1_THRESHOLD_GRID_2026-10-03.csv",index=False)

    summary={"schema":"CHANGEPOINT_H3_V1","features":FEATURES,"selected_threshold":th,
             "threshold_grid":grid.to_dict(orient="records"),"confirmation_2025":None,"holdout_2026":None}
    status="NO_ELIGIBLE_CHANGEPOINT_THRESHOLD"
    if th is not None:
        conf=confirmation(pred,th)
        summary["confirmation_2025"]=conf
        if conf["pass_gate"]:
            summary["holdout_2026"]=holdout_2026(pred,th)
            status="CONFIRMATION_PASS_HOLDOUT_OPENED"
        else:
            status="CONFIRMATION_2025_FAIL"
    summary["status"]=status

    pred.to_csv(OUT/"GOLD_H3_CHANGEPOINT_V1_PREDICTIONS_2026-10-03.csv",index=False)
    panel[["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]+FEATURES].to_csv(
        OUT/"GOLD_H3_CHANGEPOINT_V1_FEATURE_PANEL_2026-10-03.csv",index=False)
    (OUT/"GOLD_H3_CHANGEPOINT_V1_SUMMARY_2026-10-03.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# CHANGEPOINT-H3 V1 — RESULT","",f"**Status:** **{status}**  ",
           f"**Selected DEV threshold:** **{th if th is not None else 'NONE'}**","",
           "## DEV 2023-2024 threshold grid","",
           "| Th | Cand | Precision | Recall | Rate | F2 | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(f"| {r.threshold:.2f} | {int(r.candidate_n)} | {100*r.precision:.2f}% | {100*r.recall:.2f}% | {100*r.candidate_rate:.2f}% | {r.f2:.4f} | {r.eligible} |")
    if summary["confirmation_2025"] is not None:
        c=summary["confirmation_2025"]
        lines += ["","## 2025 confirmation","",
                  f"- CHANGEPOINT precision: **{100*c['changepoint']['precision']:.2f}%**",
                  f"- CHANGEPOINT reversal recall: **{100*c['changepoint']['recall']:.2f}%**",
                  f"- OPAL reversal recall: **{100*c['opal']['recall']:.2f}%**",
                  f"- Union reversal recall: **{100*c['union']['recall']:.2f}%**",
                  f"- CHANGEPOINT-only true reversals: **{c['changepoint_only_true']}**",
                  f"- Confirmation PASS: **{c['pass_gate']}**"]
    if summary["holdout_2026"] is not None:
        h=summary["holdout_2026"]
        lines += ["","## 2026 frozen holdout","",
                  f"- CHANGEPOINT precision: **{100*h['changepoint']['precision']:.2f}%**",
                  f"- CHANGEPOINT reversal recall: **{100*h['changepoint']['recall']:.2f}%**",
                  f"- OPAL reversal recall: **{100*h['opal']['recall']:.2f}%**",
                  f"- Union reversal recall: **{100*h['union']['recall']:.2f}%**",
                  f"- CHANGEPOINT-only true reversals: **{h['changepoint_only_true']}**",
                  f"- V5-missed/OPAL-no-candidate reversals in scored universe: **{h['v5_missed_opal_no_candidate_n']}**",
                  f"- nominated by CHANGEPOINT: **{h['v5_missed_opal_no_candidate_nominated']}**",
                  f"- diagnostic forced-flip rescue / broken / net: **{h['diagnostic_forced_flip_rescued']} / {h['diagnostic_forced_flip_broken']} / {h['diagnostic_forced_flip_net']}**"]
    lines += ["","## Governance","",
              "The feature family, signs, rolling windows, threshold grid and gates were frozen before fitting. "
              "2026 is evaluated only after the 2025 confirmation gate passes."]
    (OUT/"GOLD_H3_CHANGEPOINT_V1_RESULT_2026-10-03.md").write_text("\n".join(lines)+"\n")
    print((OUT/"GOLD_H3_CHANGEPOINT_V1_RESULT_2026-10-03.md").read_text())

if __name__=="__main__":
    main()
