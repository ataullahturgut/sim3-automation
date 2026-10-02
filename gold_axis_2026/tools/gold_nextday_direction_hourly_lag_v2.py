from __future__ import annotations
import json, os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, confusion_matrix, recall_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SERIES_ID="XAU_USD_TWELVE_1H_RESEARCH_V1"
OUT=Path(os.environ.get("OUT_DIR","gold_nextday_hourly_lag_v2_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001

V1_FEATURES=[
    "ret_1h","ret_3h","ret_6h","ret_12h","ret_24h",
    "rv_6h","rv_12h","rv_24h",
    "upfrac_6h","upfrac_12h","upfrac_24h",
    "range_12h","range_24h",
    "slope_6h","slope_12h","slope_24h",
    "session_ret",
]

LAG_FEATURES=[f"hr_ret_lag{i}" for i in range(24)] + [
    "block_24_29","block_30_35","block_36_41","block_42_47",
    "rv_6h","rv_12h","rv_24h",
    "prev_anchor_rv_6h","prev_anchor_rv_12h","prev_anchor_rv_24h",
    "upfrac_6h","upfrac_12h","upfrac_24h",
    "max_pos_24h","max_neg_24h","age_max_pos_24h","age_max_neg_24h",
    "same_sign_streak",
    "session_ret","prev_session_ret",
    "range_12h","range_24h",
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
    return float(np.sum((x-xm)*(a-ym))/den) if den>0 else np.nan

def age_of_extreme(a,kind):
    a=np.asarray(a,float)
    if len(a)==0 or not np.isfinite(a).all():
        return np.nan
    # 0 = current hour, larger = further back
    rev=a[::-1]
    if kind=="max":
        return float(np.argmax(rev))
    return float(np.argmin(rev))

def same_sign_streak(a):
    a=np.asarray(a,float)
    if len(a)==0 or not np.isfinite(a).all():
        return np.nan
    last=np.sign(a[-1])
    if last==0:
        return 0.0
    n=0
    for x in a[::-1]:
        if np.sign(x)==last:
            n+=1
        else:
            break
    return float(n if last>0 else -n)

def build_daily(df):
    q=df.copy()
    q["ts_ny"]=q.ts.dt.tz_convert("America/New_York")
    q["local_date"]=q.ts_ny.dt.date
    q["local_hour"]=q.ts_ny.dt.hour
    q["local_minute"]=q.ts_ny.dt.minute
    q["logp"]=np.log(q.value.astype(float))
    q["hr"]=q.logp.diff()

    for h in [1,3,6,12,24]:
        q[f"ret_{h}h"]=q.logp-q.logp.shift(h)
    for h in [6,12,24]:
        q[f"rv_{h}h"]=q.hr.rolling(h,min_periods=h).std(ddof=0)
        q[f"upfrac_{h}h"]=(q.hr>0).astype(float).rolling(h,min_periods=h).mean()
        q[f"range_{h}h"]=q.logp.rolling(h,min_periods=h).max()-q.logp.rolling(h,min_periods=h).min()
        q[f"slope_{h}h"]=q.logp.rolling(h,min_periods=h).apply(slope,raw=True)

    first_log=q.groupby("local_date")["logp"].transform("first")
    q["session_ret"]=q.logp-first_log

    for i in range(24):
        q[f"hr_ret_lag{i}"]=q.hr.shift(i)

    q["block_24_29"]=sum(q.hr.shift(i) for i in range(24,30))
    q["block_30_35"]=sum(q.hr.shift(i) for i in range(30,36))
    q["block_36_41"]=sum(q.hr.shift(i) for i in range(36,42))
    q["block_42_47"]=sum(q.hr.shift(i) for i in range(42,48))

    q["max_pos_24h"]=q.hr.rolling(24,min_periods=24).max()
    q["max_neg_24h"]=q.hr.rolling(24,min_periods=24).min()
    q["age_max_pos_24h"]=q.hr.rolling(24,min_periods=24).apply(lambda a: age_of_extreme(a,"max"),raw=True)
    q["age_max_neg_24h"]=q.hr.rolling(24,min_periods=24).apply(lambda a: age_of_extreme(a,"min"),raw=True)
    q["same_sign_streak"]=q.hr.rolling(24,min_periods=24).apply(same_sign_streak,raw=True)

    anchors=q[(q.local_hour==16)&(q.local_minute==0)].copy().sort_values("ts").reset_index(drop=True)
    anchors["prev_session_ret"]=anchors.session_ret.shift(1)
    for h in [6,12,24]:
        anchors[f"prev_anchor_rv_{h}h"]=anchors[f"rv_{h}h"].shift(1)

    anchors["target_ts"]=anchors.ts.shift(-1)
    anchors["target_ret"]=anchors.logp.shift(-1)-anchors.logp
    anchors["y_up"]=(anchors.target_ret>0).astype(float)
    anchors.loc[anchors.target_ret.isna(),"y_up"]=np.nan
    anchors["issue_year"]=anchors.ts_ny.dt.year
    anchors["issue_month"]=anchors.ts_ny.dt.to_period("M").astype(str)
    anchors["issue_date"]=anchors.ts_ny.dt.date.astype(str)
    anchors["target_date"]=pd.to_datetime(anchors.target_ts,utc=True).dt.tz_convert("America/New_York").dt.date.astype(str)

    required=sorted(set(V1_FEATURES+LAG_FEATURES+["target_ret","y_up"]))
    anchors=anchors.dropna(subset=required).copy().reset_index(drop=True)
    return anchors

def make_models():
    return {
        "V1_LOGIT_L2": Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=2000,random_state=SEED))
        ]),
        "LAG_LOGIT_L2": Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))
        ]),
        "LAG_ELASTIC_LOGIT": Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(
                C=0.20,penalty="elasticnet",solver="saga",l1_ratio=0.50,
                max_iter=5000,tol=1e-4,random_state=SEED
            ))
        ]),
        "LAG_MLP_16": Pipeline([
            ("scale",StandardScaler()),
            ("model",MLPClassifier(
                hidden_layer_sizes=(16,),activation="tanh",solver="lbfgs",
                alpha=0.01,max_iter=1500,random_state=SEED
            ))
        ]),
    }

def features_for(model):
    return V1_FEATURES if model=="V1_LOGIT_L2" else LAG_FEATURES

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

def main():
    hourly=load_hourly()
    daily=build_daily(hourly)
    test=daily[daily.issue_year.isin([2023,2024])].copy()
    if test.empty:
        raise RuntimeError("NO_TEST_ROWS")

    rows=[]; fitlog=[]
    model_names=list(make_models().keys())
    for month in sorted(test.issue_month.unique()):
        te=test[test.issue_month==month].copy()
        month_start=te.ts.min()
        tr=daily[(daily.target_ts<month_start)&(daily.issue_year<=2024)].copy()
        if len(tr)<150:
            raise RuntimeError(f"TRAIN_TOO_SMALL {month} {len(tr)}")
        fitlog.append({
            "month":month,"train_n":int(len(tr)),"test_n":int(len(te)),
            "train_start":str(tr.issue_date.min()),"train_end":str(tr.issue_date.max()),
            "test_start":str(te.issue_date.min()),"test_end":str(te.issue_date.max()),
            "train_up_rate":float(tr.y_up.mean()),
        })
        models=make_models()
        for name in model_names:
            feat=features_for(name)
            Xtr=tr[feat].to_numpy(float)
            Xte=te[feat].to_numpy(float)
            ytr=tr.y_up.astype(int).to_numpy()
            m=models[name]
            m.fit(Xtr,ytr)
            p=m.predict_proba(Xte)[:,1]
            for r,pp in zip(te.itertuples(),p):
                rows.append({
                    "model":name,
                    "issue_date":r.issue_date,"target_date":r.target_date,
                    "year":int(r.issue_year),"month":r.issue_month,
                    "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                    "actual_nextday_log_return":float(r.target_ret),
                    "p_up":float(pp),
                    "predicted_direction":"UP" if pp>=.5 else "DOWN",
                    "correct":bool((pp>=.5)==(int(r.y_up)==1)),
                })
        pmaj=float(tr.y_up.mean())
        for r in te.itertuples():
            rows.append({
                "model":"MAJORITY_PROB",
                "issue_date":r.issue_date,"target_date":r.target_date,
                "year":int(r.issue_year),"month":r.issue_month,
                "actual_direction":"UP" if int(r.y_up)==1 else "DOWN",
                "actual_nextday_log_return":float(r.target_ret),
                "p_up":pmaj,
                "predicted_direction":"UP" if pmaj>=.5 else "DOWN",
                "correct":bool((pmaj>=.5)==(int(r.y_up)==1)),
            })

    led=pd.DataFrame(rows)
    led.to_csv(OUT/"hourly_lag_v2_predictions.csv",index=False)
    pd.DataFrame(fitlog).to_csv(OUT/"hourly_lag_v2_fitlog.csv",index=False)

    metrics=[]
    for model,g0 in led.groupby("model"):
        for period,g in [("2023-2024",g0),("2023",g0[g0.year==2023]),("2024",g0[g0.year==2024])]:
            y=(g.actual_direction=="UP").astype(int).to_numpy()
            p=g.p_up.to_numpy(float)
            metrics.append({"model":model,"period":period,**metric(y,p)})
        for mo,g in g0.groupby("month"):
            y=(g.actual_direction=="UP").astype(int).to_numpy()
            p=g.p_up.to_numpy(float)
            metrics.append({"model":model,"period":mo,**metric(y,p)})
    mdf=pd.DataFrame(metrics)
    mdf.to_csv(OUT/"hourly_lag_v2_metrics.csv",index=False)

    # Final pre-2025 coefficient audit for lag linear models.
    final=daily[daily.issue_year<=2024].copy()
    coeff_rows=[]
    for name in ["LAG_LOGIT_L2","LAG_ELASTIC_LOGIT"]:
        m=make_models()[name]
        m.fit(final[LAG_FEATURES].to_numpy(float),final.y_up.astype(int).to_numpy())
        coef=m.named_steps["model"].coef_[0]
        for f,c in zip(LAG_FEATURES,coef):
            coeff_rows.append({
                "model":name,"feature":f,"coefficient":float(c),
                "abs_coefficient":float(abs(c)),
                "nonzero":bool(abs(c)>1e-10),
            })
    cdf=pd.DataFrame(coeff_rows).sort_values(["model","abs_coefficient"],ascending=[True,False])
    cdf.to_csv(OUT/"hourly_lag_v2_coefficients.csv",index=False)

    head=mdf[(mdf.period=="2023-2024")].copy().sort_values(["accuracy","balanced_accuracy"],ascending=False)
    result={
        "schema":"GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V2",
        "source_series":SERIES_ID,
        "hourly_rows":int(len(hourly)),
        "usable_anchor_rows":int(len(daily)),
        "oos_n":int(len(test)),
        "first_issue":str(daily.issue_date.min()),
        "last_issue":str(daily.issue_date.max()),
        "lag_feature_count":len(LAG_FEATURES),
        "headline":head.to_dict(orient="records"),
        "elastic_nonzero_count":int(cdf[(cdf.model=="LAG_ELASTIC_LOGIT") & cdf.nonzero].shape[0]),
    }
    (OUT/"hourly_lag_v2_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD NEXT-DAY DIRECTION — HOURLY LAG V2","",
        f"Raw hourly rows: **{len(hourly):,}**. Usable issue rows: **{len(daily):,}**. Strict OOS 2023-2024: **{len(test):,}** days.",
        f"Ordered lag representation: **{len(LAG_FEATURES)} features**.","",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | False calls |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    order=["V1_LOGIT_L2","LAG_LOGIT_L2","LAG_ELASTIC_LOGIT","LAG_MLP_16","MAJORITY_PROB"]
    for model in order:
        for period in ["2023-2024","2023","2024"]:
            r=mdf[(mdf.model==model)&(mdf.period==period)].iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                f"{r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*(1-r.accuracy):.2f}% |"
            )
    lines += ["",f"Elastic-Net nonzero coefficients in final pre-2025 fit: **{result['elastic_nonzero_count']} / {len(LAG_FEATURES)}**.",
              "Prediction ledger, monthly metrics, fit log and coefficient audit were saved."]
    (OUT/"HOURLY_LAG_V2_RESULT.md").write_text("\n".join(lines)+"\n")
    print("HOURLY_LAG_V2_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"HOURLY_LAG_V2_RESULT.md").read_text())

if __name__=="__main__":
    main()
