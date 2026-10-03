from __future__ import annotations

import json, math, os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_short_horizon_global_xau_stage1_r2 as s1
import gold_h3_nova_v1 as nova
import gold_h3_sentry_v1 as sentry
import gold_h3_dart_v1 as dart
import gold_h3_aurora_v1 as aurora
import gold_h3_iris_v1 as iris

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_clean_core_rebuild_out"))
OUT.mkdir(parents=True,exist_ok=True)

PRICES=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"
MATRIX=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv"
OLD_AURORA=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

PATCH_DATE=pd.Timestamp("2026-02-27")
PATCH={
 "gold":5183.80,
 "silver":88.14,
 "platinum":2369.25,
 "palladium":1789.96,
}
PATCH_PROVENANCE={
 "gold":"GoldPrice.org 2026-02-27 close",
 "silver":"GoldPrice.org 2026-02-27 close",
 "platinum":"StatMuse XPT 2026-02-27 close",
 "palladium":"StatMuse XPD 2026-02-27 close",
}

PATH=list(iris.PATH)


def fill_xy(tr,te,features):
    a=tr[features].copy(); b=te[features].copy()
    for c in features:
        a[c]=pd.to_numeric(a[c],errors="coerce")
        b[c]=pd.to_numeric(b[c],errors="coerce")
        med=a[c].median(skipna=True)
        v=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(v); b[c]=b[c].fillna(v)
    return a.to_numpy(float),b.to_numpy(float)


def model():
    return Pipeline([
      ("scale",StandardScaler()),
      ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=20261002)),
    ])


def patched_readiness():
    base=s1.load_panel().copy().sort_values("date").reset_index(drop=True)
    px=pd.read_csv(PRICES)
    px["date"]=pd.to_datetime(px.date)
    if PATCH_DATE not in set(px.date):
        raise RuntimeError("PATCH_DATE_MISSING")
    before=px.loc[px.date==PATCH_DATE,["gold","silver","platinum","palladium"]].iloc[0].to_dict()
    for k,v in PATCH.items():
        px.loc[px.date==PATCH_DATE,k]=float(v)

    px=px.sort_values("date").reset_index(drop=True)
    if not np.array_equal(base.date.to_numpy(dtype="datetime64[ns]"),px.date.iloc[:len(base)].to_numpy(dtype="datetime64[ns]")):
        # readiness may stop one row before frozen snapshot because forecast issue shifts.
        q=px[px.date.isin(base.date)].copy().sort_values("date")
        if len(q)!=len(base):
            raise RuntimeError(f"DATE_ALIGNMENT_FAIL base={len(base)} px={len(q)}")
        px=q.reset_index(drop=True)

    lg=np.log(px.gold.astype(float))
    metal_cols={}
    for h in [1,3,5]:
        metal_cols[f"target_end_date_h{h}"]=px.date.shift(-h)
        metal_cols[f"target_r{h}"]=np.log(px.gold.shift(-h)/px.gold)
    for h in [1,3,5,10,21]:
        metal_cols[f"gold_r{h}"]=lg.diff(h)
    metal_cols["sigma20"]=lg.diff().rolling(20).std(ddof=0)
    for name in ["silver","platinum","palladium"]:
        lp=np.log(px[name].astype(float))
        for h in [1,5,21]:
            metal_cols[f"{name}_r{h}"]=lp.diff(h)
        metal_cols[f"{name}_age_days"]=0.0

    clean=base.copy()
    for c,v in metal_cols.items():
        clean[c]=v.to_numpy()[:len(clean)]

    # Recompute NOVA's external-state derived transforms exactly.
    for c in nova.RATE_EXT:
        clean[f"{c}_d5"]=pd.to_numeric(clean[c],errors="coerce").diff(5)
    for c in nova.LOG_EXT:
        x=pd.to_numeric(clean[c],errors="coerce")
        clean[f"{c}_lr5"]=np.log(x.where(x>0)).diff(5)

    audit={
      "patch_date":str(PATCH_DATE.date()),
      "old_values":{k:float(before[k]) for k in PATCH},
      "new_values":PATCH,
      "provenance":PATCH_PROVENANCE,
      "base_rows":int(len(base)),
    }
    return clean,audit


def build_clean_a1(clean):
    led=nova.run_base_sequence(clean,2017,2026)
    keep=[
      "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
      "year","month","target_r3","y_up","p_A0_global","p_recent252","p_A1_arcr","train_n"
    ]
    out=led[keep].copy()
    out.to_csv(OUT/"clean_nova_a1_predictions.csv",index=False)
    return out


def build_expert_matrix(a1):
    m=pd.read_csv(MATRIX)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        m[c]=pd.to_datetime(m[c],errors="raise")
    z=m.drop(columns=["target_end_date_h3","target_r3","y_up","p_A1_arcr","base_logit"]).merge(
      a1[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","target_r3","y_up","p_A1_arcr"]],
      on=["feature_cutoff_date","forecast_issue_date"],how="inner",validate="one_to_one"
    )
    if len(z)!=len(m):
        raise RuntimeError(f"MATRIX_MATCH_FAIL old={len(m)} clean={len(z)}")
    p=np.clip(z.p_A1_arcr.astype(float).to_numpy(),1e-6,1-1e-6)
    z["base_logit"]=np.log(p/(1-p))
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)
    return z


def expert_ledger(panel):
    panel=panel.dropna(subset=["target_r3","y_up","base_logit"]+PATH).copy()
    panel["year"]=panel.forecast_issue_date.dt.year.astype(int)
    panel["month"]=panel.forecast_issue_date.dt.to_period("M").astype(str)
    test=panel[(panel.forecast_issue_date>=pd.Timestamp("2022-04-01"))&(panel.forecast_issue_date.dt.year<=2026)].copy()
    rows=[]
    for mo in sorted(test.month.unique()):
        te=test[test.month==mo].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=panel[(panel.target_end_date_h3<=cutoff)&(panel.forecast_issue_date<te.forecast_issue_date.min())].copy()
        if len(tr)<80: continue
        ytr=tr.y_up.astype(int).to_numpy()
        X1,T1=fill_xy(tr,te,["base_logit"]+PATH)
        X2,T2=fill_xy(tr,te,PATH)
        m1=model(); m2=model()
        m1.fit(X1,ytr); m2.fit(X2,ytr)
        p1=m1.predict_proba(T1)[:,1]; p2=m2.predict_proba(T2)[:,1]
        for r,a,b in zip(te.itertuples(),p1,p2):
            rows.append({
              "feature_cutoff_date":r.feature_cutoff_date,
              "forecast_issue_date":r.forecast_issue_date,
              "target_end_date_h3":r.target_end_date_h3,
              "year":int(r.year),"month":str(r.month),
              "y_up":int(r.y_up),"target_r3":float(r.target_r3),
              "p_structural":float(a),"p_path_global":float(b),
              "train_n":int(len(tr)),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)


def build_clean_aurora(expert):
    s,ss=sentry.apply_sentry(expert)
    d,ds,dis=dart.apply_dart(expert)

    dk=["forecast_issue_date","p_dart","matured_disagreements","q_path","prob_path_superior",
        "expected_run_length","changepoint_mass"]
    sk=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","year","month","y_up","target_r3",
        "p_structural","p_path_global","p_sentry","matured_pair_n","net_rescue_63","rescues_63","breaks_63"]
    x=s[sk].merge(d[dk],on="forecast_issue_date",how="left",validate="one_to_one")
    a,sw=aurora.apply_aurora(x)
    return a,sw,s,d


def metrics(y,p):
    y=np.asarray(y,int); p=np.asarray(p,float); pred=(p>=.5).astype(int)
    tn=((pred==0)&(y==0)).sum(); fp=((pred==1)&(y==0)).sum()
    fn=((pred==0)&(y==1)).sum(); tp=((pred==1)&(y==1)).sum()
    return {
      "n":int(len(y)),"accuracy":float(np.mean(pred==y)),
      "balanced_accuracy":float(.5*(tp/max(tp+fn,1)+tn/max(tn+fp,1))),
      "brier":float(np.mean((p-y)**2)),
      "logloss":float(log_loss(y,np.clip(p,1e-6,1-1e-6),labels=[0,1])),
      "up_recall":float(tp/max(tp+fn,1)),"down_recall":float(tn/max(tn+fp,1)),
    }


def main():
    clean,audit=patched_readiness()
    clean.to_csv(OUT/"clean_readiness_panel.csv",index=False)

    a1=build_clean_a1(clean)
    matrix=build_expert_matrix(a1)
    matrix.to_csv(OUT/"clean_expert_matrix.csv",index=False)

    expert=expert_ledger(matrix)
    expert.to_csv(OUT/"clean_expert_ledger.csv",index=False)

    a,sw,s,d=build_clean_aurora(expert)
    a.to_csv(OUT/"clean_aurora_predictions.csv",index=False)
    sw.to_csv(OUT/"clean_aurora_switches.csv",index=False)

    old=pd.read_csv(OLD_AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        old[c]=pd.to_datetime(old[c],errors="raise")
    cmp=old.merge(a[["forecast_issue_date","p_aurora","active_expert","y_up","target_r3"]],
      on="forecast_issue_date",how="inner",suffixes=("_old","_clean"),validate="one_to_one")
    cmp["old_dir"]=(cmp.p_aurora_old>=.5).astype(int)
    cmp["clean_dir"]=(cmp.p_aurora_clean>=.5).astype(int)
    cmp["direction_changed"]=cmp.old_dir!=cmp.clean_dir
    cmp["label_changed"]=cmp.y_up_old.astype(int)!=cmp.y_up_clean.astype(int)
    cmp["p_abs_diff"]=(cmp.p_aurora_old-cmp.p_aurora_clean).abs()
    cmp.to_csv(OUT/"clean_aurora_comparison.csv",index=False)

    rows=[]
    for period,mask in [
      ("2023",a.year==2023),("2024",a.year==2024),("2025",a.year==2025),("2026",a.year==2026),
      ("2025-2026",a.year.isin([2025,2026]))
    ]:
        z=a[mask]
        rows.append({"model":"AURORA_CLEAN","period":period,**metrics(z.y_up,z.p_aurora)})
        zo=old[old.forecast_issue_date.isin(z.forecast_issue_date)]
        # evaluate old probabilities on clean labels for apples-to-apples
        zz=z[["forecast_issue_date","y_up"]].merge(zo[["forecast_issue_date","p_aurora"]],on="forecast_issue_date")
        rows.append({"model":"AURORA_OLD_PROB_CLEAN_LABEL","period":period,**metrics(zz.y_up,zz.p_aurora)})
    mdf=pd.DataFrame(rows); mdf.to_csv(OUT/"clean_core_metrics.csv",index=False)

    audit.update({
      "clean_aurora_rows":int(len(a)),
      "comparison_rows":int(len(cmp)),
      "label_changed_n":int(cmp.label_changed.sum()),
      "direction_changed_n":int(cmp.direction_changed.sum()),
      "max_p_abs_diff":float(cmp.p_abs_diff.max()),
      "changed_direction_dates":cmp.loc[cmp.direction_changed,"forecast_issue_date"].dt.strftime("%Y-%m-%d").tolist(),
      "label_changed_dates":cmp.loc[cmp.label_changed,"forecast_issue_date"].dt.strftime("%Y-%m-%d").tolist(),
      "clean_switches":sw.to_dict(orient="records"),
    })
    (OUT/"clean_core_summary.json").write_text(json.dumps(audit,indent=2,default=str)+"\n")

    lines=[
      "# GOLD H3 CLEAN CORE REBUILD — 2026-10-03","",
      "**Status:** CLEAN-OVERLAY REBUILD; original frozen artifacts preserved.","",
      "## Corrected source row","",
      f"- date: **{PATCH_DATE.date()}**",
      f"- old: {json.dumps(audit['old_values'],sort_keys=True)}",
      f"- clean: {json.dumps(PATCH,sort_keys=True)}","",
      "## AURORA clean-core metrics","",
      "| Model | Period | Accuracy | BA | Brier | Logloss |",
      "|---|---|---:|---:|---:|---:|"
    ]
    for r in mdf.itertuples():
        lines.append(f"| {r.model} | {r.period} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} |")
    lines += ["","## Old vs clean AURORA call audit","",
      f"- labels changed: **{audit['label_changed_n']}**",
      f"- AURORA directions changed after full clean refit: **{audit['direction_changed_n']}**",
      f"- max absolute p(UP) change: **{audit['max_p_abs_diff']:.4f}**",
      f"- direction-changed issue dates: **{', '.join(audit['changed_direction_dates']) or 'none'}**",
      f"- label-changed issue dates: **{', '.join(audit['label_changed_dates']) or 'none'}**","",
      "This rebuild does not overwrite the original AURORA prospective freeze. It is a retrospective integrity correction branch of evidence."
    ]
    (OUT/"CLEAN_CORE_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"CLEAN_CORE_RESULT.md").read_text())


if __name__=="__main__":
    main()
