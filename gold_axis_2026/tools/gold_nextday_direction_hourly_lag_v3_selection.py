from __future__ import annotations
import json, os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_nextday_direction_hourly_lag_v2 as v2

OUT=Path(os.environ.get("OUT_DIR","gold_nextday_hourly_lag_v3_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001

BASE=list(v2.V1_FEATURES)
LAGS=[f"hr_ret_lag{i}" for i in range(24)]
MAX_KEEP=6
MIN_BA_GAIN=0.005
MAX_BRIER_WORSEN=0.002
MAX_ACC_DROP=0.005

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))
    ])

def metric(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    tn,fp,fn,tp=[int(x) for x in confusion_matrix(y,pred,labels=[0,1]).ravel()]
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "mean_p_up":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
        "tn":tn,"fp":fp,"fn":fn,"tp":tp,
    }

def oos_year(daily,features,year,tag):
    test=daily[daily.issue_year==year].copy()
    rows=[]; fitlog=[]
    for month in sorted(test.issue_month.unique()):
        te=test[test.issue_month==month].copy()
        month_start=te.ts.min()
        tr=daily[(daily.target_ts<month_start)&(daily.issue_year<=year)].copy()
        if len(tr)<150:
            raise RuntimeError(f"TRAIN_TOO_SMALL {year} {month} {len(tr)}")
        Xtr=tr[features].to_numpy(float)
        Xte=te[features].to_numpy(float)
        ytr=tr.y_up.astype(int).to_numpy()
        m=make_model(); m.fit(Xtr,ytr)
        p=m.predict_proba(Xte)[:,1]
        fitlog.append({
            "tag":tag,"year":year,"month":month,
            "train_n":int(len(tr)),"test_n":int(len(te)),
            "feature_count":len(features),
            "train_end":str(tr.issue_date.max()),
        })
        for r,pp in zip(te.itertuples(),p):
            rows.append({
                "tag":tag,
                "year":int(year),
                "month":r.issue_month,
                "issue_date":r.issue_date,
                "target_date":r.target_date,
                "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                "p_up":float(pp),
                "predicted_direction":"UP" if pp>=.5 else "DOWN",
                "correct":bool((pp>=.5)==(int(r.y_up)==1)),
            })
    led=pd.DataFrame(rows)
    y=(led.actual_direction=="UP").astype(int).to_numpy()
    met=metric(y,led.p_up.to_numpy(float))
    return met,led,pd.DataFrame(fitlog)

def delta_row(lag,m,base):
    return {
        "lag":lag,
        **{f"{k}":v for k,v in m.items()},
        "delta_accuracy":float(m["accuracy"]-base["accuracy"]),
        "delta_balanced_accuracy":float(m["balanced_accuracy"]-base["balanced_accuracy"]),
        "delta_brier":float(m["brier"]-base["brier"]),
        "delta_logloss":float(m["logloss"]-base["logloss"]),
        "delta_up_recall":float(m["up_recall"]-base["up_recall"]),
        "delta_down_recall":float(m["down_recall"]-base["down_recall"]),
    }

def final_coefficients(daily,features,cutoff_year):
    d=daily[daily.issue_year<=cutoff_year].copy()
    m=make_model(); m.fit(d[features].to_numpy(float),d.y_up.astype(int).to_numpy())
    coef=m.named_steps["model"].coef_[0]
    return pd.DataFrame({
        "cutoff_year":cutoff_year,
        "feature":features,
        "coefficient":coef,
        "abs_coefficient":np.abs(coef),
    }).sort_values("abs_coefficient",ascending=False)

def main():
    hourly=v2.load_hourly()
    daily=v2.build_daily(hourly)

    # Exact shared-sample V1 baseline for 2023 selection.
    base23,base23_led,base23_fit=oos_year(daily,BASE,2023,"BASE_V1_2023")

    # Stage A: one-at-a-time audit.
    audit=[]
    for lag in LAGS:
        m,_,_=oos_year(daily,BASE+[lag],2023,f"ADD_{lag}")
        audit.append(delta_row(lag,m,base23))
    adf=pd.DataFrame(audit).sort_values(
        ["delta_balanced_accuracy","delta_accuracy","delta_brier"],
        ascending=[False,False,True]
    )
    adf.to_csv(OUT/"lag_v3_one_at_a_time_2023.csv",index=False)

    # Stage B: greedy forward retention, all choices from 2023 only.
    kept=[]
    remaining=LAGS.copy()
    current_features=BASE.copy()
    current_metrics=base23
    selection_steps=[]
    while remaining and len(kept)<MAX_KEEP:
        candidates=[]
        for lag in remaining:
            m,_,_=oos_year(daily,current_features+[lag],2023,f"GREEDY_{len(kept)+1}_{lag}")
            candidates.append((lag,m))
        candidates.sort(
            key=lambda x: (
                x[1]["balanced_accuracy"],
                x[1]["accuracy"],
                -x[1]["brier"],
            ),
            reverse=True
        )
        best_lag,best_m=candidates[0]
        dba=best_m["balanced_accuracy"]-current_metrics["balanced_accuracy"]
        dacc=best_m["accuracy"]-current_metrics["accuracy"]
        db=best_m["brier"]-current_metrics["brier"]
        qualify=(dba>=MIN_BA_GAIN and db<=MAX_BRIER_WORSEN and dacc>=-MAX_ACC_DROP)
        selection_steps.append({
            "step":len(kept)+1,
            "candidate":best_lag,
            "accepted":bool(qualify),
            "before_accuracy":current_metrics["accuracy"],
            "after_accuracy":best_m["accuracy"],
            "delta_accuracy":dacc,
            "before_balanced_accuracy":current_metrics["balanced_accuracy"],
            "after_balanced_accuracy":best_m["balanced_accuracy"],
            "delta_balanced_accuracy":dba,
            "before_brier":current_metrics["brier"],
            "after_brier":best_m["brier"],
            "delta_brier":db,
            "after_logloss":best_m["logloss"],
        })
        if not qualify:
            break
        kept.append(best_lag)
        remaining.remove(best_lag)
        current_features=BASE+kept
        current_metrics=best_m

    sdf=pd.DataFrame(selection_steps)
    sdf.to_csv(OUT/"lag_v3_forward_selection_steps.csv",index=False)

    # Exact 2023 selected-ledger and frozen 2024 confirmation.
    sel23,sel23_led,sel23_fit=oos_year(daily,BASE+kept,2023,"V3_SELECTED")
    base24,base24_led,base24_fit=oos_year(daily,BASE,2024,"BASE_V1")
    sel24,sel24_led,sel24_fit=oos_year(daily,BASE+kept,2024,"V3_SELECTED")

    led=pd.concat([base23_led,sel23_led,base24_led,sel24_led],ignore_index=True)
    led.to_csv(OUT/"lag_v3_predictions.csv",index=False)
    pd.concat([base23_fit,sel23_fit,base24_fit,sel24_fit],ignore_index=True).to_csv(
        OUT/"lag_v3_fitlog.csv",index=False
    )

    comp=[]
    for label,yr,m in [
        ("BASE_V1",2023,base23),("V3_SELECTED",2023,sel23),
        ("BASE_V1",2024,base24),("V3_SELECTED",2024,sel24),
    ]:
        comp.append({"model":label,"period":str(yr),**m,"false_call_rate":1-m["accuracy"]})
    # combined 2023-24 for descriptive continuity
    for label in ["BASE_V1","V3_SELECTED"]:
        g=led[led.tag.str.startswith(label) | (led.tag==label)].copy()
        # BASE 2023 tag differs, handle explicitly
        if label=="BASE_V1":
            g=led[led.tag.isin(["BASE_V1_2023","BASE_V1"])]
        else:
            g=led[led.tag=="V3_SELECTED"]
        y=(g.actual_direction=="UP").astype(int).to_numpy()
        m=metric(y,g.p_up.to_numpy(float))
        comp.append({"model":label,"period":"2023-2024","false_call_rate":1-m["accuracy"],**m})
    cdf=pd.DataFrame(comp)
    cdf.to_csv(OUT/"lag_v3_comparison_metrics.csv",index=False)

    coeff23=final_coefficients(daily,BASE+kept,2023)
    coeff23.to_csv(OUT/"lag_v3_selected_coefficients_through_2023.csv",index=False)

    top_individual=adf.head(10)[[
        "lag","delta_accuracy","delta_balanced_accuracy","delta_brier","delta_logloss"
    ]].to_dict(orient="records")

    result={
        "schema":"GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V3_SELECTION",
        "selection_year":2023,
        "confirmation_year":2024,
        "candidate_lags":LAGS,
        "selected_lags":kept,
        "selected_count":len(kept),
        "selection_steps":selection_steps,
        "base_2023":base23,
        "selected_2023":sel23,
        "base_2024":base24,
        "selected_2024":sel24,
        "top_individual_2023":top_individual,
        "governance_note":"2024 is confirmation within an already-opened research history, not a pristine untouched lockbox."
    }
    (OUT/"lag_v3_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    def row(model,period):
        r=cdf[(cdf.model==model)&(cdf.period==period)].iloc[0]
        return (
            f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*r.false_call_rate:.2f}% |"
        )

    lines=[
        "# GOLD NEXT-DAY DIRECTION — HOURLY LAG V3 SELECTION","",
        "2023 = lag selection/development. 2024 = frozen-subset confirmation.","",
        f"Selected lags: **{', '.join(kept) if kept else 'NONE'}**.","",
        "## One-at-a-time 2023 leaders","",
        "| Lag | Δ accuracy | Δ balanced acc | Δ Brier | Δ log loss |",
        "|---|---:|---:|---:|---:|"
    ]
    for r in adf.head(10).itertuples():
        lines.append(
            f"| {r.lag} | {100*r.delta_accuracy:+.2f} pp | {100*r.delta_balanced_accuracy:+.2f} pp | "
            f"{r.delta_brier:+.4f} | {r.delta_logloss:+.4f} |"
        )
    lines += ["","## Frozen comparison","",
              "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | False calls |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
              row("BASE_V1","2023"),row("V3_SELECTED","2023"),
              row("BASE_V1","2024"),row("V3_SELECTED","2024"),
              row("BASE_V1","2023-2024"),row("V3_SELECTED","2023-2024"),"",
              "All 24 hourly lags were tested individually. The final subset was chosen only from 2023 under the frozen greedy rule."]
    (OUT/"HOURLY_LAG_V3_RESULT.md").write_text("\n".join(lines)+"\n")
    print("LAG_V3_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"HOURLY_LAG_V3_RESULT.md").read_text())

if __name__=="__main__":
    main()
