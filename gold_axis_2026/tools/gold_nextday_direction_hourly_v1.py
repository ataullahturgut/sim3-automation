from __future__ import annotations
import json, math, os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SERIES_ID="XAU_USD_TWELVE_1H_RESEARCH_V1"
OUT=Path(os.environ.get("OUT_DIR","gold_nextday_hourly_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001

FEATURES=[
    "ret_1h","ret_3h","ret_6h","ret_12h","ret_24h",
    "rv_6h","rv_12h","rv_24h",
    "upfrac_6h","upfrac_12h","upfrac_24h",
    "range_12h","range_24h",
    "slope_6h","slope_12h","slope_24h",
    "session_ret",
]

def load_hourly():
    dsn=os.environ["NEON_DATABASE_URL"]
    with psycopg.connect(dsn,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
                SELECT observation_ts, value, retrieved_at
                FROM observations
                WHERE series_id=%s
                ORDER BY observation_ts, retrieved_at
            """,(SERIES_ID,))
            rows=cur.fetchall()
        conn.rollback()
    if not rows:
        raise RuntimeError("NO_HOURLY_ROWS")
    df=pd.DataFrame(rows,columns=["ts","value","retrieved_at"])
    df["ts"]=pd.to_datetime(df.ts,utc=True)
    df["value"]=pd.to_numeric(df.value,errors="coerce")
    df=df.dropna(subset=["value"])
    df=df[df.value>0].copy()
    df=df.sort_values(["ts","retrieved_at"]).drop_duplicates("ts",keep="last").sort_values("ts").reset_index(drop=True)
    if len(df)<10000:
        raise RuntimeError(f"TOO_FEW_ROWS {len(df)}")
    return df

def slope(a):
    a=np.asarray(a,float)
    if len(a)<2 or not np.isfinite(a).all():
        return np.nan
    x=np.arange(len(a),dtype=float)
    xm=x.mean(); ym=a.mean()
    den=np.sum((x-xm)**2)
    if den<=0: return np.nan
    return float(np.sum((x-xm)*(a-ym))/den)

def build_daily(df):
    q=df.copy()
    q["ts_ny"]=q.ts.dt.tz_convert("America/New_York")
    q["local_date"]=q.ts_ny.dt.date
    q["local_hour"]=q.ts_ny.dt.hour
    q["local_minute"]=q.ts_ny.dt.minute
    q["logp"]=np.log(q.value.astype(float))
    q["hr"]=q.logp.diff()

    # rolling bar-count features; all are available by the anchor row
    for h in [1,3,6,12,24]:
        q[f"ret_{h}h"]=q.logp-q.logp.shift(h)
    for h in [6,12,24]:
        q[f"rv_{h}h"]=q.hr.rolling(h,min_periods=h).std(ddof=0)
        q[f"upfrac_{h}h"]=(q.hr>0).astype(float).rolling(h,min_periods=h).mean()
        q[f"range_{h}h"]=q.logp.rolling(h,min_periods=h).max()-q.logp.rolling(h,min_periods=h).min()
        q[f"slope_{h}h"]=q.logp.rolling(h,min_periods=h).apply(slope,raw=True)

    first_log=q.groupby("local_date")["logp"].transform("first")
    q["session_ret"]=q.logp-first_log

    anchors=q[(q.local_hour==16)&(q.local_minute==0)].copy()
    if len(anchors)<600:
        raise RuntimeError(f"TOO_FEW_16H_ANCHORS {len(anchors)}")
    anchors=anchors.sort_values("ts").reset_index(drop=True)

    # next available trading-day 16:00 anchor
    anchors["target_ts"]=anchors.ts.shift(-1)
    anchors["target_date"]=anchors.local_date.shift(-1)
    anchors["target_ret"]=anchors.logp.shift(-1)-anchors.logp
    anchors["y_up"]=(anchors.target_ret>0).astype(float)
    anchors.loc[anchors.target_ret.isna(),"y_up"]=np.nan

    # Drop rows with missing features/target.
    anchors=anchors.dropna(subset=FEATURES+["target_ret","y_up"]).copy()
    anchors["issue_year"]=anchors.ts_ny.dt.year
    anchors["issue_month"]=anchors.ts_ny.dt.to_period("M").astype(str)
    anchors["issue_date"]=anchors.ts_ny.dt.date.astype(str)
    anchors["target_date_str"]=pd.to_datetime(anchors.target_ts,utc=True).dt.tz_convert("America/New_York").dt.date.astype(str)
    return anchors

def make_models():
    logit=Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=2000,random_state=SEED))
    ])
    hgb=HistGradientBoostingClassifier(
        learning_rate=0.05,
        max_iter=150,
        max_depth=3,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=SEED,
    )
    return {"LOGIT_L2":logit,"HGB":hgb}

def metric(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    cm=confusion_matrix(y,pred,labels=[0,1])
    tn,fp,fn,tp=[int(x) for x in cm.ravel()]
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

def main():
    hourly=load_hourly()
    daily=build_daily(hourly)

    # 2022 initial train; 2023-2024 expanding monthly OOS.
    test=daily[daily.issue_year.isin([2023,2024])].copy()
    if test.empty:
        raise RuntimeError("NO_TEST_ROWS")

    rows=[]
    fitlog=[]
    for month in sorted(test.issue_month.unique()):
        te=test[test.issue_month==month].copy()
        month_start=te.ts.min()
        tr=daily[(daily.target_ts<month_start)&(daily.issue_year<=2024)].copy()
        if len(tr)<150:
            raise RuntimeError(f"TRAIN_TOO_SMALL {month} {len(tr)}")
        Xtr=tr[FEATURES].to_numpy(float)
        ytr=tr.y_up.astype(int).to_numpy()
        Xte=te[FEATURES].to_numpy(float)
        models=make_models()
        fitlog.append({"month":month,"train_n":int(len(tr)),"test_n":int(len(te)),
                       "train_start":str(tr.issue_date.min()),"train_end":str(tr.issue_date.max()),
                       "test_start":str(te.issue_date.min()),"test_end":str(te.issue_date.max()),
                       "train_up_rate":float(ytr.mean())})
        for name,m in models.items():
            m.fit(Xtr,ytr)
            p=m.predict_proba(Xte)[:,1]
            for r,pp in zip(te.itertuples(),p):
                rows.append({
                    "model":name,
                    "issue_date":r.issue_date,
                    "target_date":r.target_date_str,
                    "year":int(r.issue_year),
                    "month":r.issue_month,
                    "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                    "actual_nextday_log_return":float(r.target_ret),
                    "p_up":float(pp),
                    "predicted_direction":"UP" if pp>=.5 else "DOWN",
                    "correct":bool((pp>=.5)==(int(r.y_up)==1)),
                })
        # baselines recorded once per test row
        pmaj=float(ytr.mean())
        for r in te.itertuples():
            pm=1.0 if r.session_ret>0 else 0.0
            rows.append({
                "model":"MAJORITY_PROB",
                "issue_date":r.issue_date,"target_date":r.target_date_str,
                "year":int(r.issue_year),"month":r.issue_month,
                "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                "actual_nextday_log_return":float(r.target_ret),
                "p_up":pmaj,
                "predicted_direction":"UP" if pmaj>=.5 else "DOWN",
                "correct":bool((pmaj>=.5)==(int(r.y_up)==1)),
            })
            rows.append({
                "model":"SESSION_MOMENTUM",
                "issue_date":r.issue_date,"target_date":r.target_date_str,
                "year":int(r.issue_year),"month":r.issue_month,
                "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                "actual_nextday_log_return":float(r.target_ret),
                "p_up":pm,
                "predicted_direction":"UP" if pm>=.5 else "DOWN",
                "correct":bool((pm>=.5)==(int(r.y_up)==1)),
            })

    led=pd.DataFrame(rows)
    led.to_csv(OUT/"nextday_hourly_predictions.csv",index=False)
    pd.DataFrame(fitlog).to_csv(OUT/"nextday_hourly_fitlog.csv",index=False)

    metrics=[]
    for model,g0 in led.groupby("model"):
        for period,g in [("2023-2024",g0),("2023",g0[g0.year==2023]),("2024",g0[g0.year==2024])]:
            y=(g.actual_direction=="UP").astype(int).to_numpy()
            p=g.p_up.to_numpy(float)
            mm=metric(y,p)
            metrics.append({"model":model,"period":period,**mm})
        for mo,g in g0.groupby("month"):
            y=(g.actual_direction=="UP").astype(int).to_numpy()
            p=g.p_up.to_numpy(float)
            mm=metric(y,p)
            metrics.append({"model":model,"period":mo,**mm})
    mdf=pd.DataFrame(metrics)
    mdf.to_csv(OUT/"nextday_hourly_metrics.csv",index=False)

    # final 2022-2024 fit importances where available
    final=daily[daily.issue_year<=2024].copy()
    X=final[FEATURES].to_numpy(float); y=final.y_up.astype(int).to_numpy()
    imps=[]
    hgb=make_models()["HGB"]; hgb.fit(X,y)
    # HGB has no standard feature_importances_, preserve permutation-free contract by not inventing importances.
    # Logistic standardized coefficients are interpretable for a first audit.
    logit=make_models()["LOGIT_L2"]; logit.fit(X,y)
    coef=logit.named_steps["model"].coef_[0]
    for f,c in zip(FEATURES,coef):
        imps.append({"model":"LOGIT_L2","feature":f,"coefficient":float(c),"abs_coefficient":float(abs(c))})
    pd.DataFrame(imps).sort_values("abs_coefficient",ascending=False).to_csv(OUT/"nextday_hourly_logit_coefficients.csv",index=False)

    headline=mdf[(mdf.period=="2023-2024") & (mdf.model.isin(["LOGIT_L2","HGB","MAJORITY_PROB","SESSION_MOMENTUM"]))].copy()
    result={
        "schema":"GOLD_NEXTDAY_DIRECTION_HOURLY_V1",
        "source_series":SERIES_ID,
        "hourly_rows":int(len(hourly)),
        "anchor_rows":int(len(daily)),
        "first_issue":str(daily.issue_date.min()),
        "last_issue":str(daily.issue_date.max()),
        "oos_test":"2023-2024 expanding monthly refit",
        "features":FEATURES,
        "headline":headline.to_dict(orient="records"),
    }
    (OUT/"nextday_hourly_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD NEXT-DAY DIRECTION — XAU 1H V1","",
        f"Raw hourly rows: **{len(hourly):,}**. Daily 16:00 NY issue rows after feature/target maturity: **{len(daily):,}**.",
        "Strict expanding OOS: 2022 initial history; 2023-2024 scored.","",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    order=["LOGIT_L2","HGB","MAJORITY_PROB","SESSION_MOMENTUM"]
    for model in order:
        for period in ["2023-2024","2023","2024"]:
            r=mdf[(mdf.model==model)&(mdf.period==period)].iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                f"{r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )
    lines += ["","Prediction ledger, monthly metrics, fit logs and standardized Logistic coefficients were saved."]
    (OUT/"NEXTDAY_HOURLY_RESULT.md").write_text("\n".join(lines)+"\n")
    print("NEXTDAY_HOURLY_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"NEXTDAY_HOURLY_RESULT.md").read_text())

if __name__=="__main__":
    main()
