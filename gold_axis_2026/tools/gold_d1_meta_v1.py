from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"D1_META_V1_OUT"
OUT.mkdir(exist_ok=True)

AURORA=AX/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
RIFT=AX/"GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
VEGA=AX/"GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
RIFT_PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
ORBIT=AX/"GOLD_H3_ORBIT_D1_V1_PANEL_2026-10-02.csv"
PRICE=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
CIG=AX/"GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv"

F1=[
 "p_aurora","p_v5","p_rift","p_vega","p_opal_reversal",
 "opal_override","rift_override","vega_override","candidate_reversal","gt_flip_share",
 "expert_mean","expert_std","expert_range","gap_v5_rift","gap_v5_vega"
]
F2=F1+[
 "h_ret_12","trend_strength","opposite_semivar_share","deceleration_6h",
 "session_against_trend","path_consistency","trend_close_location",
 "opposite_extreme_recency","jump_concentration","trend_to_range","adverse_excursion"
]
F3=F2+[
 "broadusd_r1","nom10_d1","real10_d1","be10_d1","vix_r1","ndx_r1",
 "xag_r1","metal_breadth1","gold_minus_basket1"
]
FAMILIES={"F1_EXPERT":F1,"F2_EXPERT_PATH":F2,"F3_EXPERT_PATH_MACRO":F3}
MODELS=["LOGIT_L2","HGB_SMALL"]
THRESH=[0.55,0.60,0.65,0.70]

def dt(s): return pd.to_datetime(s,errors="coerce").dt.normalize()
def boolcol(s): return s.astype(str).str.lower().isin(["true","1","yes"])
def pct(x): return "—" if x is None or (isinstance(x,float) and np.isnan(x)) else f"{100*x:.2f}%"

def load_panel():
    a=pd.read_csv(AURORA); a["feature_cutoff_date"]=dt(a["feature_cutoff_date"]); a["forecast_issue_date"]=dt(a["forecast_issue_date"])
    v=pd.read_csv(V5); v["feature_cutoff_date"]=dt(v["feature_cutoff_date"])
    r=pd.read_csv(RIFT); r["feature_cutoff_date"]=dt(r["feature_cutoff_date"])
    g=pd.read_csv(VEGA); g["feature_cutoff_date"]=dt(g["feature_cutoff_date"])
    rp=pd.read_csv(RIFT_PANEL); rp["feature_cutoff_date"]=dt(rp["feature_cutoff_date"])
    o=pd.read_csv(ORBIT); o["feature_cutoff_date"]=dt(o["feature_cutoff_date"])
    px=pd.read_csv(PRICE); px["date"]=dt(px["date"]); pmap=dict(zip(px.date,px.gold.astype(float)))

    z=a[["feature_cutoff_date","forecast_issue_date","p_aurora"]].copy()
    z=z.merge(v[[
      "feature_cutoff_date","p_helios_v5_dce","p_opal_reversal",
      "opal_override","rift_override","vega_override","candidate_reversal","gt_flip_share"
    ]],on="feature_cutoff_date",how="inner")
    z=z.merge(r[["feature_cutoff_date","p_rift"]],on="feature_cutoff_date",how="inner")
    z=z.merge(g[["feature_cutoff_date","p_vega"]],on="feature_cutoff_date",how="inner")
    z=z.merge(rp[[
      "feature_cutoff_date","h_ret_12","trend_strength","opposite_semivar_share",
      "deceleration_6h","session_against_trend","path_consistency","trend_close_location",
      "opposite_extreme_recency","jump_concentration","trend_to_range","adverse_excursion"
    ]],on="feature_cutoff_date",how="inner")
    z=z.merge(o[[
      "feature_cutoff_date","broadusd_r1","nom10_d1","real10_d1","be10_d1",
      "vix_r1","ndx_r1","xag_r1","metal_breadth1","gold_minus_basket1"
    ]],on="feature_cutoff_date",how="inner")

    z=z.rename(columns={"p_helios_v5_dce":"p_v5"})
    for c in ["opal_override","rift_override","vega_override","candidate_reversal"]:
        z[c]=boolcol(z[c]).astype(int)

    probs=z[["p_aurora","p_v5","p_rift","p_vega"]].astype(float)
    z["expert_mean"]=probs.mean(axis=1)
    z["expert_std"]=probs.std(axis=1,ddof=0)
    z["expert_range"]=probs.max(axis=1)-probs.min(axis=1)
    z["gap_v5_rift"]=(z.p_v5.astype(float)-z.p_rift.astype(float)).abs()
    z["gap_v5_vega"]=(z.p_v5.astype(float)-z.p_vega.astype(float)).abs()

    z["gold0"]=z.feature_cutoff_date.map(pmap)
    z["gold1"]=z.forecast_issue_date.map(pmap)
    z=z.dropna(subset=["gold0","gold1"]).copy()
    z["d1_up"]=(z.gold1>z.gold0).astype(int)
    z["year"]=z.forecast_issue_date.dt.year.astype(int)
    z["half"]=np.where(z.forecast_issue_date.dt.month<=6,"H1","H2")
    z=z[(z.forecast_issue_date>=pd.Timestamp("2022-11-01")) & (z.forecast_issue_date<=pd.Timestamp("2026-09-25"))].copy()

    for c in sorted(set(F3)):
        z[c]=pd.to_numeric(z[c],errors="coerce")
    return z.sort_values("forecast_issue_date").reset_index(drop=True)

def make_model(name):
    if name=="LOGIT_L2":
        return Pipeline([
          ("imp",SimpleImputer(strategy="median")),
          ("scaler",StandardScaler()),
          ("model",LogisticRegression(C=0.5,penalty="l2",solver="lbfgs",max_iter=3000,random_state=20261005))
        ])
    if name=="HGB_SMALL":
        return Pipeline([
          ("imp",SimpleImputer(strategy="median")),
          ("model",HistGradientBoostingClassifier(
             max_depth=2,learning_rate=0.05,max_iter=150,min_samples_leaf=25,
             l2_regularization=1.0,random_state=20261005))
        ])
    raise ValueError(name)

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pred=(p>=.5).astype(int)
    return {
      "n":int(len(y)),
      "accuracy":float(accuracy_score(y,pred)),
      "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
      "brier":float(brier_score_loss(y,p)),
      "logloss":float(log_loss(y,p,labels=[0,1]))
    }

def fit_score(train,test,features,model_name):
    m=make_model(model_name)
    m.fit(train[features],train.d1_up.astype(int))
    p=m.predict_proba(test[features])[:,1]
    return m,p,metrics(test.d1_up,p)

def selective_metrics(y,p,t):
    y=np.asarray(y,int); p=np.asarray(p,float)
    mask=(p>=t)|(p<=1-t)
    pred=(p>=.5).astype(int)
    return {
      "threshold":float(t),"n":int(len(y)),"actions":int(mask.sum()),
      "coverage":float(mask.mean()) if len(mask) else None,
      "correct":int((pred[mask]==y[mask]).sum()) if mask.any() else 0,
      "accuracy":float((pred[mask]==y[mask]).mean()) if mask.any() else None
    }

def cstat(df,col):
    a=df[df[col]!="UNCERTAIN"]
    return {
      "n":int(len(df)),"actions":int(len(a)),
      "coverage":float(len(a)/len(df)) if len(df) else None,
      "correct":int((a[col]==a.actual).sum()),
      "accuracy":float((a[col]==a.actual).mean()) if len(a) else None
    }

def main():
    z=load_panel()
    base=z[z.forecast_issue_date<pd.Timestamp("2024-01-01")].copy()
    h1=z[(z.forecast_issue_date>=pd.Timestamp("2024-01-01"))&(z.forecast_issue_date<pd.Timestamp("2024-07-01"))].copy()
    h2=z[(z.forecast_issue_date>=pd.Timestamp("2024-07-01"))&(z.forecast_issue_date<pd.Timestamp("2025-01-01"))].copy()
    y25=z[z.year==2025].copy()
    y26=z[z.year==2026].copy()

    rows=[]
    for fam,features in FAMILIES.items():
        for model_name in MODELS:
            _,p,m=fit_score(base,h1,features,model_name)
            rows.append({"family":fam,"model":model_name,**m})
    sel=pd.DataFrame(rows)
    famord={k:i for i,k in enumerate(FAMILIES)}
    modord={k:i for i,k in enumerate(MODELS)}
    sel["_fo"]=sel.family.map(famord); sel["_mo"]=sel.model.map(modord)
    sel=sel.sort_values(["brier","balanced_accuracy","accuracy","_fo","_mo"],ascending=[True,False,False,True,True])
    chosen=sel.iloc[0]
    family=str(chosen.family); model_name=str(chosen.model); features=FAMILIES[family]

    train_h2=z[z.forecast_issue_date<pd.Timestamp("2024-07-01")].copy()
    m24,p24,_=fit_score(train_h2,h2,features,model_name)
    thr_rows=[selective_metrics(h2.d1_up,p24,t) for t in THRESH]
    thr=pd.DataFrame(thr_rows)
    elig=thr[thr.coverage>=.50].copy()
    if len(elig):
        elig=elig.sort_values(["accuracy","coverage","threshold"],ascending=[False,False,False])
        threshold=float(elig.iloc[0].threshold)
        threshold_eligible=True
    else:
        threshold=0.55
        threshold_eligible=False

    train25=z[z.forecast_issue_date<pd.Timestamp("2025-01-01")].copy()
    m25,p25,m25full=fit_score(train25,y25,features,model_name)
    s25=selective_metrics(y25.d1_up,p25,threshold)
    confirm=bool(s25["accuracy"] is not None and s25["accuracy"]>=.70 and s25["coverage"]>=.50 and m25full["balanced_accuracy"]>=.55)

    train26=z[z.forecast_issue_date<pd.Timestamp("2026-01-01")].copy()
    m26,p26,m26full=fit_score(train26,y26,features,model_name)
    s26=selective_metrics(y26.d1_up,p26,threshold)
    pred26=y26[["feature_cutoff_date","forecast_issue_date","d1_up"]].copy()
    pred26["p_d1_up"]=p26
    pred26["meta_action"]=np.where(p26>=threshold,"UP",np.where(p26<=1-threshold,"DOWN","UNCERTAIN"))
    pred26["meta_correct"]=np.where(pred26.meta_action=="UNCERTAIN",np.nan,((pred26.meta_action=="UP").astype(int)==pred26.d1_up).astype(int))

    # Integrate with refreshed 2026 CIG.
    cig=pd.read_csv(CIG); cig["feature_cutoff_date"]=dt(cig["feature_cutoff_date"]); cig["forecast_issue_date"]=dt(cig["forecast_issue_date"])
    q=cig.merge(pred26[["feature_cutoff_date","p_d1_up","meta_action"]],on="feature_cutoff_date",how="left")
    q["actual"]=q.d1_actual

    resolve=[]
    veto=[]
    for r in q.itertuples(index=False):
        meta=r.meta_action if isinstance(r.meta_action,str) else "UNCERTAIN"
        cur=r.consensus
        ro=cur
        vr=cur
        if cur=="UNCERTAIN" and meta!="UNCERTAIN":
            ro=meta
            vr=meta
        elif cur!="UNCERTAIN" and meta!="UNCERTAIN" and meta!=cur:
            vr="UNCERTAIN"
        resolve.append(ro); veto.append(vr)
    q["resolve_only"]=resolve
    q["veto_resolve"]=veto

    overall={
      "original":cstat(q,"consensus"),
      "resolve_only":cstat(q,"resolve_only"),
      "veto_resolve":cstat(q,"veto_resolve")
    }
    aug=q[q.forecast_issue_date.dt.strftime("%Y-%m")=="2026-08"].copy()
    aug_stats={
      "original":cstat(aug,"consensus"),
      "resolve_only":cstat(aug,"resolve_only"),
      "veto_resolve":cstat(aug,"veto_resolve")
    }
    months=[]
    for mm,gp in q.groupby(q.forecast_issue_date.dt.strftime("%Y-%m")):
        months.append({"month":mm,"original":cstat(gp,"consensus"),"resolve_only":cstat(gp,"resolve_only"),"veto_resolve":cstat(gp,"veto_resolve")})

    promote_resolve=bool(confirm and overall["resolve_only"]["accuracy"]>=overall["original"]["accuracy"] and overall["resolve_only"]["coverage"]>=.75 and aug_stats["resolve_only"]["accuracy"]>=.75 and aug_stats["resolve_only"]["coverage"]>aug_stats["original"]["coverage"])
    promote_veto=bool(confirm and overall["veto_resolve"]["accuracy"]>=overall["original"]["accuracy"] and overall["veto_resolve"]["coverage"]>=.75 and aug_stats["veto_resolve"]["accuracy"]>=.75 and aug_stats["veto_resolve"]["coverage"]>aug_stats["original"]["coverage"])

    out={
      "identity":"D1_META_V1",
      "selected":{"family":family,"model":model_name,"threshold":threshold,"threshold_eligible":threshold_eligible,"features":features},
      "selection_2024_h1":sel.drop(columns=["_fo","_mo"]).to_dict("records"),
      "threshold_2024_h2":thr.to_dict("records"),
      "confirmation_2025":{"full":m25full,"selective":s25,"pass":confirm},
      "test_2026":{"full":m26full,"selective":s26},
      "cig_2026":overall,
      "august_2026":aug_stats,
      "promotion":{"resolve_only":promote_resolve,"veto_resolve":promote_veto},
      "months":months
    }

    sel.drop(columns=["_fo","_mo"]).to_csv(OUT/"D1_META_V1_MODEL_SELECTION_2024H1.csv",index=False)
    thr.to_csv(OUT/"D1_META_V1_THRESHOLD_SELECTION_2024H2.csv",index=False)
    pred26.to_csv(OUT/"D1_META_V1_2026_PREDICTIONS.csv",index=False)
    q.to_csv(OUT/"D1_META_V1_CIG_INTEGRATION_2026.csv",index=False)
    (OUT/"D1_META_V1_RESULT.json").write_text(json.dumps(out,indent=2,default=str)+"\n")

    lines=[
      "# D1-META V1 — DIRECT NEXT-DAY SELECTIVE STACK RESULT","",
      f"**Selected:** {family} / {model_name}  ",
      f"**Frozen threshold:** {threshold:.2f}  ",
      f"**2025 confirmation:** {'PASS' if confirm else 'FAIL'}","",
      "## 2024-H1 model selection","",
      "| Family | Model | N | Acc | BA | Brier | Log loss |",
      "|---|---|---:|---:|---:|---:|---:|"
    ]
    for rr in sel.drop(columns=["_fo","_mo"]).itertuples(index=False):
        lines.append(f"| {rr.family} | {rr.model} | {rr.n} | {pct(rr.accuracy)} | {pct(rr.balanced_accuracy)} | {rr.brier:.4f} | {rr.logloss:.4f} |")
    lines += ["","## 2024-H2 threshold selection","",
      "| t | Actions | Coverage | Correct | Accuracy |",
      "|---:|---:|---:|---:|---:|"]
    for rr in thr.itertuples(index=False):
        lines.append(f"| {rr.threshold:.2f} | {rr.actions} | {pct(rr.coverage)} | {rr.correct} | {pct(rr.accuracy)} |")
    lines += ["","## 2025 frozen confirmation","",
      f"- full accuracy: **{pct(m25full['accuracy'])}**",
      f"- full balanced accuracy: **{pct(m25full['balanced_accuracy'])}**",
      f"- selective: **{s25['correct']}/{s25['actions']} = {pct(s25['accuracy'])}**, coverage **{pct(s25['coverage'])}**",
      f"- confirmation: **{'PASS' if confirm else 'FAIL'}**","",
      "## 2026 frozen test","",
      f"- full accuracy: **{pct(m26full['accuracy'])}**",
      f"- full balanced accuracy: **{pct(m26full['balanced_accuracy'])}**",
      f"- standalone selective: **{s26['correct']}/{s26['actions']} = {pct(s26['accuracy'])}**, coverage **{pct(s26['coverage'])}**","",
      "## CIG integration","",
      "| Policy | 2026 actions | 2026 accuracy | Coverage | Aug actions | Aug accuracy | Aug coverage |",
      "|---|---:|---:|---:|---:|---:|---:|"
    ]
    for pol in ["original","resolve_only","veto_resolve"]:
        a1=overall[pol]; a2=aug_stats[pol]
        lines.append(f"| {pol} | {a1['actions']} | {pct(a1['accuracy'])} | {pct(a1['coverage'])} | {a2['actions']} | {pct(a2['accuracy'])} | {pct(a2['coverage'])} |")
    lines += ["","## Promotion","",
      f"- RESOLVE_ONLY: **{'PASS' if promote_resolve else 'FAIL'}**",
      f"- VETO_RESOLVE: **{'PASS' if promote_veto else 'FAIL'}**",
      "",
      "No 2025/2026 outcome altered model family, feature family, hyperparameters, or the selective threshold."
    ]
    (OUT/"D1_META_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"D1_META_V1_RESULT.md").read_text())
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__":
    main()
