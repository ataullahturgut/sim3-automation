from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, accuracy_score, brier_score_loss, log_loss

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"HAG_D1_V1_OUT"
OUT.mkdir(exist_ok=True)

PRICE=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
MATRIX=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv"
OPAL=AX/"GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"
OPAL_PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv"
ORBIT=AX/"GOLD_H3_ORBIT_D1_V1_PANEL_2026-10-02.csv"
AURORA=AX/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
RIFT=AX/"GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
VEGA=AX/"GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
CIG=AX/"GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv"

CORE=[
 "p_reversal","aurora_margin","trend_strength",
 "h_ret_1","h_ret_3","h_ret_6","h_ret_12","h_ret_24","h_session_ret"
]
MACRO=CORE+["broadusd_r1","nom10_d1","real10_d1","vix_r1","ndx_r1"]
FUSED=MACRO+["xag_r1","metal_breadth1","gold_minus_basket1"]
FAMILIES={"CORE":CORE,"MACRO":MACRO,"FUSED":FUSED}
PRIMARY_LOW=0.40
PRIMARY_HIGH=0.60
SENS=[(0.45,0.55),(0.40,0.60),(0.35,0.65)]

def d(x):
    return pd.to_datetime(x,errors="coerce").dt.normalize()

def b(x):
    return x.astype(str).str.lower().eq("true")

def direction(p):
    return (p.astype(float)>=0.5).astype(int)

def safe_logloss(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return float(log_loss(y,p,labels=[0,1]))

def metrics(y,p):
    y=np.asarray(y,int); p=np.asarray(p,float); pred=(p>=0.5).astype(int)
    return {
      "n":int(len(y)),
      "accuracy":float(accuracy_score(y,pred)),
      "balanced_accuracy":float(balanced_accuracy_score(y,pred)) if len(np.unique(y))>1 else None,
      "brier":float(brier_score_loss(y,p)),
      "logloss":safe_logloss(y,p),
      "mean_target":float(y.mean()),
      "mean_p":float(p.mean()),
    }

def fit_model(X,y):
    return Pipeline([
      ("scaler",StandardScaler()),
      ("logit",LogisticRegression(C=0.5,class_weight="balanced",solver="lbfgs",max_iter=3000,random_state=0))
    ]).fit(X,y)

def action_from_p(p,lo,hi):
    if p>=hi:return 1
    if p<=lo:return 0
    return None

def main():
    px=pd.read_csv(PRICE); px["date"]=d(px["date"]); pmap=dict(zip(px.date,px.gold.astype(float)))

    m=pd.read_csv(MATRIX); m["feature_cutoff_date"]=d(m["feature_cutoff_date"]); m["forecast_issue_date"]=d(m["forecast_issue_date"])
    o=pd.read_csv(OPAL); o["feature_cutoff_date"]=d(o["feature_cutoff_date"]); o["forecast_issue_date"]=d(o["forecast_issue_date"])
    op=pd.read_csv(OPAL_PANEL); op["feature_cutoff_date"]=d(op["feature_cutoff_date"])
    orb=pd.read_csv(ORBIT); orb["feature_cutoff_date"]=d(orb["feature_cutoff_date"])
    a=pd.read_csv(AURORA); a["feature_cutoff_date"]=d(a["feature_cutoff_date"]); a["forecast_issue_date"]=d(a["forecast_issue_date"])
    v=pd.read_csv(V5); v["feature_cutoff_date"]=d(v["feature_cutoff_date"])
    r=pd.read_csv(RIFT); r["feature_cutoff_date"]=d(r["feature_cutoff_date"])
    g=pd.read_csv(VEGA); g["feature_cutoff_date"]=d(g["feature_cutoff_date"])

    # Build the candidate timing panel only on genuine final V5-vs-AURORA flips
    z=o.merge(a[["feature_cutoff_date","p_aurora"]],on="feature_cutoff_date",suffixes=("","_clean"),how="inner")
    z=z.merge(v[["feature_cutoff_date","p_helios_v5_dce"]],on="feature_cutoff_date",how="inner")
    z=z.merge(m[["feature_cutoff_date"]+[c for c in CORE if c.startswith("h_")]],on="feature_cutoff_date",how="inner")
    z=z.merge(op[["feature_cutoff_date","trend_strength"]],on="feature_cutoff_date",how="inner",suffixes=("","_panel"))
    z=z.merge(orb[["feature_cutoff_date","broadusd_r1","nom10_d1","real10_d1","vix_r1","ndx_r1","xag_r1","metal_breadth1","gold_minus_basket1"]],on="feature_cutoff_date",how="inner")
    z["p_reversal"]=z["p_reversal"].astype(float)
    z["aurora_margin"]=(z["p_aurora_clean"].astype(float)-0.5).abs()
    z["aurora_dir"]=(z["p_aurora_clean"].astype(float)>=0.5).astype(int)
    z["v5_dir"]=(z["p_helios_v5_dce"].astype(float)>=0.5).astype(int)
    z["opal_dir"]=(z["p_opal"].astype(float)>=0.5).astype(int)
    z["opal_override"]=b(z["override"])
    z["final_v5_flip"]=z["aurora_dir"]!=z["v5_dir"]
    # Timing model is learned on every OPAL override event. Older V5/DCE layers
    # sometimes cancel OPAL before the final V5 direction, so restricting training
    # to final flips would erase the historical timing sample.
    z=z[z["opal_override"]].copy()
    z["d1_actual"]=z.apply(lambda x:int(pmap.get(x.forecast_issue_date,np.nan)>pmap.get(x.feature_cutoff_date,np.nan)) if x.feature_cutoff_date in pmap and x.forecast_issue_date in pmap else np.nan,axis=1)
    z=z.dropna(subset=["d1_actual"]).copy()
    z["d1_actual"]=z["d1_actual"].astype(int)
    # y_immediate=1 => OPAL H3 reversal direction is already correct next day;
    # 0 => base AURORA direction remains correct on D1.
    z["y_immediate"]=(z["d1_actual"]==z["opal_dir"]).astype(int)
    z["year"]=z["forecast_issue_date"].dt.year.astype(int)

    for c in sorted(set(sum(FAMILIES.values(),[]))):
        z[c]=pd.to_numeric(z[c],errors="coerce")

    dev=z[z.year<=2023].copy()
    confirm=z[z.year==2024].copy()
    test=z[z.year>=2025].copy()

    family_rows=[]
    fitted={}
    for name,features in FAMILIES.items():
        tr=dev.dropna(subset=features+["y_immediate"])
        te=confirm.dropna(subset=features+["y_immediate"])
        if len(tr)<10 or len(te)<5:
            continue
        model=fit_model(tr[features],tr.y_immediate)
        p=model.predict_proba(te[features])[:,1]
        mm=metrics(te.y_immediate,p)
        family_rows.append({"family":name,"train_n":len(tr),"confirm_n":len(te),**mm})
        fitted[name]=(model,features)

    fam=pd.DataFrame(family_rows)
    if fam.empty: raise RuntimeError("NO_FAMILY_RESULTS")
    # Predeclared selection: best 2024 balanced accuracy; ties by lower Brier, then simpler family.
    fam["_ba"]=fam.balanced_accuracy.fillna(-1)
    simplicity={"CORE":0,"MACRO":1,"FUSED":2}
    fam["_simp"]=fam.family.map(simplicity)
    fam=fam.sort_values(["_ba","brier","_simp"],ascending=[False,True,True])
    selected=str(fam.iloc[0].family)
    features=FAMILIES[selected]

    train_pre2025=z[z.year<=2024].dropna(subset=features+["y_immediate"]).copy()
    model=fit_model(train_pre2025[features],train_pre2025.y_immediate)

    scored=z.dropna(subset=features).copy()
    scored["p_immediate"]=model.predict_proba(scored[features])[:,1]
    scored["primary_action"]=scored.p_immediate.apply(lambda p:action_from_p(float(p),PRIMARY_LOW,PRIMARY_HIGH))
    scored["primary_dir"]=scored.apply(lambda x: np.nan if pd.isna(x.primary_action) else int(x.opal_dir if int(x.primary_action)==1 else x.aurora_dir),axis=1)
    scored["primary_correct"]=scored.apply(lambda x: np.nan if pd.isna(x.primary_dir) else int(int(x.primary_dir)==int(x.d1_actual)),axis=1)

    eval_rows=[]
    for yr in [2025,2026]:
        q=scored[(scored.year==yr) & scored.final_v5_flip].copy()
        act=q[q.primary_action.notna()]
        eval_rows.append({
          "period":str(yr),"flip_cases":len(q),
          "always_v5_correct":int((q.v5_dir==q.d1_actual).sum()),
          "always_v5_accuracy":float((q.v5_dir==q.d1_actual).mean()) if len(q) else None,
          "always_aurora_correct":int((q.aurora_dir==q.d1_actual).sum()),
          "always_aurora_accuracy":float((q.aurora_dir==q.d1_actual).mean()) if len(q) else None,
          "hag_actions":len(act),"hag_coverage":float(len(act)/len(q)) if len(q) else None,
          "hag_correct":int(act.primary_correct.sum()) if len(act) else 0,
          "hag_accuracy":float(act.primary_correct.mean()) if len(act) else None,
          "mean_p_immediate":float(q.p_immediate.mean()) if len(q) else None,
        })
    q=scored[(scored.year>=2025) & scored.final_v5_flip].copy(); act=q[q.primary_action.notna()]
    eval_rows.append({
      "period":"2025-2026","flip_cases":len(q),
      "always_v5_correct":int((q.v5_dir==q.d1_actual).sum()),
      "always_v5_accuracy":float((q.v5_dir==q.d1_actual).mean()),
      "always_aurora_correct":int((q.aurora_dir==q.d1_actual).sum()),
      "always_aurora_accuracy":float((q.aurora_dir==q.d1_actual).mean()),
      "hag_actions":len(act),"hag_coverage":float(len(act)/len(q)),
      "hag_correct":int(act.primary_correct.sum()),
      "hag_accuracy":float(act.primary_correct.mean()) if len(act) else None,
      "mean_p_immediate":float(q.p_immediate.mean()),
    })
    eval_df=pd.DataFrame(eval_rows)

    sens=[]
    for lo,hi in SENS:
        for period,qq in [("2025",scored[(scored.year==2025)&scored.final_v5_flip]),("2026",scored[(scored.year==2026)&scored.final_v5_flip]),("2025-2026",scored[(scored.year>=2025)&scored.final_v5_flip])]:
            dirs=[]
            for x in qq.itertuples(index=False):
                aa=action_from_p(float(x.p_immediate),lo,hi)
                dirs.append(np.nan if aa is None else (int(x.opal_dir) if aa==1 else int(x.aurora_dir)))
            dirs=pd.Series(dirs,index=qq.index)
            mask=dirs.notna()
            sens.append({"low":lo,"high":hi,"period":period,"flip_cases":len(qq),"actions":int(mask.sum()),"coverage":float(mask.mean()) if len(mask) else None,"accuracy":float((dirs[mask].astype(int).to_numpy()==qq.loc[mask,"d1_actual"].astype(int).to_numpy()).mean()) if mask.any() else None})
    sens_df=pd.DataFrame(sens)

    # Integrate only into existing CIG UNCERTAIN rows that share the same cutoff and are genuine OPAL/V5 flips.
    cig=pd.read_csv(CIG); cig["feature_cutoff_date"]=d(cig["feature_cutoff_date"]); cig["forecast_issue_date"]=d(cig["forecast_issue_date"])
    score_map=scored.set_index("feature_cutoff_date")
    integ=[]
    for x in cig.itertuples(index=False):
        current=x.consensus
        new=current
        source="UNCHANGED"
        pimm=np.nan
        if current=="UNCERTAIN" and x.feature_cutoff_date in score_map.index:
            h=score_map.loc[x.feature_cutoff_date]
            if isinstance(h,pd.DataFrame): h=h.iloc[0]
            if not bool(h.final_v5_flip):
                integ.append({
                  "feature_cutoff_date":x.feature_cutoff_date,
                  "forecast_issue_date":x.forecast_issue_date,
                  "actual":x.d1_actual,
                  "original_consensus":current,
                  "hag_consensus":new,
                  "p_immediate":pimm,
                  "hag_source":source,
                  "original_correct":np.nan if current=="UNCERTAIN" else int(current==x.d1_actual),
                  "hag_correct":np.nan if new=="UNCERTAIN" else int(new==x.d1_actual),
                })
                continue
            pimm=float(h.p_immediate)
            aa=action_from_p(pimm,PRIMARY_LOW,PRIMARY_HIGH)
            if aa is not None:
                new="UP" if (int(h.opal_dir) if aa==1 else int(h.aurora_dir))==1 else "DOWN"
                source="HAG_RESOLVED_V5" if aa==1 else "HAG_RESOLVED_AURORA"
            else:
                source="HAG_ABSTAIN"
        integ.append({
          "feature_cutoff_date":x.feature_cutoff_date,
          "forecast_issue_date":x.forecast_issue_date,
          "actual":x.d1_actual,
          "original_consensus":current,
          "hag_consensus":new,
          "p_immediate":pimm,
          "hag_source":source,
          "original_correct":np.nan if current=="UNCERTAIN" else int(current==x.d1_actual),
          "hag_correct":np.nan if new=="UNCERTAIN" else int(new==x.d1_actual),
        })
    integ=pd.DataFrame(integ)

    def cigstat(q,col):
        a=q[q[col]!="UNCERTAIN"]
        return {"n":len(q),"actions":len(a),"coverage":float(len(a)/len(q)),"correct":int((a[col]==a.actual).sum()),"accuracy":float((a[col]==a.actual).mean()) if len(a) else None}

    summary={}
    for period,qq in [("2025",integ[integ.forecast_issue_date.dt.year==2025]),("2026",integ[integ.forecast_issue_date.dt.year==2026]),("2025-2026",integ[integ.forecast_issue_date.dt.year>=2025]),("2026-08",integ[integ.forecast_issue_date.dt.strftime("%Y-%m")=="2026-08"])]:
        summary[period]={"original":cigstat(qq,"original_consensus"),"hag":cigstat(qq,"hag_consensus")}

    aug=integ[integ.forecast_issue_date.dt.strftime("%Y-%m")=="2026-08"].copy()
    aug_unc=aug[aug.original_consensus=="UNCERTAIN"].copy()

    fam.drop(columns=["_ba","_simp"],errors="ignore").to_csv(OUT/"HAG_D1_V1_FAMILY_CONFIRMATION.csv",index=False)
    eval_df.to_csv(OUT/"HAG_D1_V1_FLIP_EVALUATION.csv",index=False)
    sens_df.to_csv(OUT/"HAG_D1_V1_THRESHOLD_SENSITIVITY.csv",index=False)
    scored.to_csv(OUT/"HAG_D1_V1_SCORED_FLIPS.csv",index=False)
    integ.to_csv(OUT/"HAG_D1_V1_CIG_INTEGRATION.csv",index=False)
    aug_unc.to_csv(OUT/"HAG_D1_V1_AUGUST_UNCERTAIN.csv",index=False)

    result={
      "identity":"HAG_D1_V1",
      "status":"RETROSPECTIVE_CHALLENGER_NOT_PROMOTED",
      "target":"On OPAL override events, predict whether the H3 reversal direction is already correct on next-day D1; apply only when that OPAL mechanism survives to a final V5-vs-AURORA flip.",
      "selection":{"development":"<=2023","confirmation":"2024","selected_family":selected,"C":0.5,"class_weight":"balanced","primary_low":PRIMARY_LOW,"primary_high":PRIMARY_HIGH,"features":features},
      "family_confirmation":fam.drop(columns=["_ba","_simp"],errors="ignore").to_dict("records"),
      "flip_evaluation":eval_df.to_dict("records"),
      "cig_summary":summary,
      "august_uncertain":aug_unc.assign(feature_cutoff_date=aug_unc.feature_cutoff_date.astype(str),forecast_issue_date=aug_unc.forecast_issue_date.astype(str)).to_dict("records"),
      "governance":[
        "No 2025 or 2026 outcome is used to select feature family or fit model coefficients.",
        "2024 is the frozen family-selection confirmation year; selected family is refit on all <=2024 rows before 2025-2026 scoring.",
        "Primary action band 0.40/0.60 is predeclared; sensitivity bands are descriptive only.",
        "HAG learns timing on all OPAL override events, but acts only on genuine OPAL-driven final V5-vs-AURORA direction flips and only attempts to resolve existing CIG UNCERTAIN states.",
        "This is retrospective challenger evidence, not prospective OOS validation."
      ]
    }
    (OUT/"HAG_D1_V1_RESULT.json").write_text(json.dumps(result,indent=2,default=str)+"\n")

    def pct(x): return "—" if x is None or (isinstance(x,float) and np.isnan(x)) else f"{100*x:.2f}%"
    lines=[
      "# HAG-D1 V1 — Horizon Alignment Gate","",
      "**Status:** RETROSPECTIVE CHALLENGER — NOT PROMOTED","",
      "Goal: learn timing from all OPAL override events; when an OPAL reversal survives into a final V5-vs-AURORA flip, estimate whether that reversal is already aligned with the next-day D1 move or is delayed/not immediate.","",
      "## Design","",
      "- Development: through 2023.",
      "- Family confirmation/selection: 2024 only.",
      "- Refit selected family on all <=2024 flip cases.",
      "- 2025 and 2026 are untouched by feature-family selection and coefficient fitting.",
      "- Fixed primary action band: p(immediate) >= 0.60 => use V5/OPAL flip; <= 0.40 => use AURORA/base direction; otherwise ABSTAIN.","",
      f"Selected family: **{selected}**","",
      "## 2024 family confirmation","",
      "| Family | Train N | Confirm N | Accuracy | BA | Brier | Log loss |",
      "|---|---:|---:|---:|---:|---:|---:|"
    ]
    for rr in fam.drop(columns=["_ba","_simp"],errors="ignore").itertuples(index=False):
        lines.append(f"| {rr.family} | {rr.train_n} | {rr.confirm_n} | {pct(rr.accuracy)} | {pct(rr.balanced_accuracy) if rr.balanced_accuracy is not None else '—'} | {rr.brier:.4f} | {rr.logloss:.4f} |")
    lines += ["","## Flip-case evaluation","",
      "| Period | Flip cases | Always V5 | Always AURORA | HAG actions | HAG coverage | HAG accuracy |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for rr in eval_df.itertuples(index=False):
        lines.append(f"| {rr.period} | {rr.flip_cases} | {rr.always_v5_correct}/{rr.flip_cases} ({pct(rr.always_v5_accuracy)}) | {rr.always_aurora_correct}/{rr.flip_cases} ({pct(rr.always_aurora_accuracy)}) | {rr.hag_actions} | {pct(rr.hag_coverage)} | {rr.hag_correct}/{rr.hag_actions if rr.hag_actions else 0} ({pct(rr.hag_accuracy)}) |")
    lines += ["","## CIG integration","",
      "| Period | Original actions | Original acc | HAG actions | HAG acc | Original coverage | HAG coverage |",
      "|---|---:|---:|---:|---:|---:|---:|"]
    for period in ["2025","2026","2025-2026","2026-08"]:
        q=summary[period]
        lines.append(f"| {period} | {q['original']['actions']} | {pct(q['original']['accuracy'])} | {q['hag']['actions']} | {pct(q['hag']['accuracy'])} | {pct(q['original']['coverage'])} | {pct(q['hag']['coverage'])} |")
    lines += ["","## August 2026 — original UNCERTAIN days","",
      "| Issue | Actual | p(immediate) | HAG result | Correct |",
      "|---|---|---:|---|---:|"]
    for rr in aug_unc.itertuples(index=False):
        lines.append(f"| {rr.forecast_issue_date.date()} | {rr.actual} | {'' if pd.isna(rr.p_immediate) else f'{rr.p_immediate:.3f}'} | {rr.hag_consensus} ({rr.hag_source}) | {'' if pd.isna(rr.hag_correct) else int(rr.hag_correct)} |")
    lines += ["","## Governance","",
      "HAG-D1 V1 is a timing/horizon challenger, not a replacement for OPAL H3. No 2025/2026 outcome is used in feature-family selection or coefficient fitting. The 0.40/0.60 action band is fixed before test scoring. Sensitivity bands are reported but not used to choose the result.",
    ]
    (OUT/"HAG_D1_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"HAG_D1_V1_RESULT.md").read_text())
    print(json.dumps(result,indent=2,default=str))

if __name__=="__main__":
    main()
