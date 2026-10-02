from __future__ import annotations
import io, json, os, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","gold_forecasting_challenge_v1_select_out"))
OUT.mkdir(parents=True,exist_ok=True)

SEED=20261001
BLOCK=5

GOLD_ONLY=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
CORE3=GOLD_ONLY+[
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]
CORE4=CORE3+[
    "palladium_r1","palladium_r5","palladium_r21","palladium_age_days",
]
SAFE_EXT=[
    "DGS10","DFII10","BREAKEVEN10_PROXY",
    "BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD",
    "VIX","NDX",
]
BLOCKS={
    "GOLD_ONLY":GOLD_ONLY,
    "CORE3":CORE3,
    "CORE4":CORE4,
    "CORE3_SAFE_EXTERNAL":CORE3+SAFE_EXT,
}
BLOCK_ORDER={k:i for i,k in enumerate(BLOCKS)}
MODEL_ORDER={k:i for i,k in enumerate(["LOGIT_L2","LOGIT_EN","LDA_SHRINK","HGB","RANDOM_FOREST","EXTRA_TREES"])}

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"gold-challenge-v1-select"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
    if len(names)!=1: raise RuntimeError(names)
    df=pd.read_csv(io.BytesIO(z.read(names[0])))
    for c in ["date","feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
    # Fail closed: model-selection process has no access to post-2020 rows.
    df=df[df.forecast_issue_date < pd.Timestamp("2021-01-01")].copy()
    return df.sort_values("feature_cutoff_date").reset_index(drop=True)

def fill_train_test(tr,te,features):
    a=tr[features].copy()
    b=te[features].copy()
    for c in features:
        a[c]=pd.to_numeric(a[c],errors="coerce")
        b[c]=pd.to_numeric(b[c],errors="coerce")
        med=a[c].median(skipna=True)
        val=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(val)
        b[c]=b[c].fillna(val)
    return a.to_numpy(float),b.to_numpy(float)

def make_model(name):
    if name=="LOGIT_L2":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED)),
        ])
    if name=="LOGIT_EN":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(
                C=0.30,solver="saga",penalty="elasticnet",l1_ratio=0.50,
                max_iter=5000,tol=1e-4,random_state=SEED
            )),
        ])
    if name=="LDA_SHRINK":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",LinearDiscriminantAnalysis(solver="lsqr",shrinkage="auto")),
        ])
    if name=="HGB":
        return HistGradientBoostingClassifier(
            learning_rate=0.03,max_iter=150,max_depth=3,min_samples_leaf=30,
            l2_regularization=1.0,random_state=SEED,
        )
    if name=="RANDOM_FOREST":
        return RandomForestClassifier(
            n_estimators=300,max_depth=4,min_samples_leaf=20,max_features="sqrt",
            class_weight="balanced",random_state=SEED,n_jobs=1,
        )
    if name=="EXTRA_TREES":
        return ExtraTreesClassifier(
            n_estimators=300,max_depth=4,min_samples_leaf=20,max_features="sqrt",
            class_weight="balanced",random_state=SEED,n_jobs=1,
        )
    raise KeyError(name)

def metrics(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    tn,fp,fn,tp=[int(x) for x in confusion_matrix(y,pred,labels=[0,1]).ravel()]
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "prediction_std":float(np.std(p)),
        "tn":tn,"fp":fp,"fn":fn,"tp":tp,
    }

def run_candidate(df,block_name,model_name):
    features=BLOCKS[block_name]
    val=df[
        df.forecast_issue_date.dt.year.between(2019,2020) &
        df.target_r3.notna()
    ].copy().reset_index(drop=True)
    rows=[]
    for bs in range(0,len(val),BLOCK):
        te=val.iloc[bs:bs+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=cutoff)
        ].copy()
        if len(tr)<1000:
            raise RuntimeError(f"{block_name}/{model_name} train too small {len(tr)}")
        Xtr,Xte=fill_train_test(tr,te,features)
        ytr=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
        yte=(te.target_r3.astype(float)>0).astype(int).to_numpy()
        m=make_model(model_name)
        m.fit(Xtr,ytr)
        p=m.predict_proba(Xte)[:,1]
        for r,yy,pp in zip(te.itertuples(),yte,p):
            rows.append({
                "feature_block":block_name,
                "model":model_name,
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "year":int(r.forecast_issue_date.year),
                "y_up":int(yy),
                "p_up":float(pp),
            })
    led=pd.DataFrame(rows)
    met=metrics(led.y_up,led.p_up)
    return led,met

def confidence_cutoffs(led):
    c=np.abs(led.p_up.to_numpy(float)-0.5)
    # cutoff yielding about top 60% and top 40% most confident validation calls
    return {
        "coverage_60_conf_cutoff":float(np.quantile(c,0.40)),
        "coverage_40_conf_cutoff":float(np.quantile(c,0.60)),
    }

def main():
    df=load_panel()
    all_led=[]; leaderboard=[]
    for b in BLOCKS:
        for m in MODEL_ORDER:
            led,met=run_candidate(df,b,m)
            all_led.append(led)
            leaderboard.append({"feature_block":b,"model":m,**met})

    ldf=pd.DataFrame(leaderboard)
    ldf["block_order"]=ldf.feature_block.map(BLOCK_ORDER)
    ldf["model_order"]=ldf.model.map(MODEL_ORDER)
    ldf=ldf.sort_values(
        ["balanced_accuracy","brier","logloss","block_order","model_order"],
        ascending=[False,True,True,True,True],
    ).reset_index(drop=True)
    ldf.to_csv(OUT/"challenge_v1_validation_leaderboard.csv",index=False)

    preds=pd.concat(all_led,ignore_index=True)
    preds.to_csv(OUT/"challenge_v1_validation_predictions.csv",index=False)

    champ=ldf.iloc[0].to_dict()
    cled=preds[
        (preds.feature_block==champ["feature_block"]) &
        (preds.model==champ["model"])
    ].copy()
    cuts=confidence_cutoffs(cled)

    # annual validation diagnostics for champion only
    annual=[]
    for yr,g in cled.groupby("year"):
        annual.append({"year":int(yr),**metrics(g.y_up,g.p_up)})
    pd.DataFrame(annual).to_csv(OUT/"challenge_v1_champion_validation_annual.csv",index=False)

    result={
        "schema":"GOLD_FORECASTING_CHALLENGE_V1_SELECTION",
        "selection_window":"2019-2020",
        "post_2020_rows_loaded":False,
        "candidate_count":int(len(ldf)),
        "champion":{
            "feature_block":champ["feature_block"],
            "model":champ["model"],
            "metrics":{k:champ[k] for k in [
                "n","accuracy","balanced_accuracy","brier","logloss",
                "up_recall","down_recall","prediction_std","tn","fp","fn","tp"
            ]},
            "confidence_cutoffs":cuts,
        },
        "top10":ldf.head(10).drop(columns=["block_order","model_order"]).to_dict(orient="records"),
    }
    (OUT/"challenge_v1_selection_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD FORECASTING CHALLENGE V1 — VALIDATION SELECTION","",
        "Validation only: **2019-2020**. The selection program loaded no post-2020 rows.","",
        "| Rank | Feature block | Model | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for i,r in ldf.head(10).iterrows():
        lines.append(
            f"| {i+1} | {r.feature_block} | {r.model} | {int(r.n)} | "
            f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    lines += ["",
              f"Champion to lock: **{champ['feature_block']} + {champ['model']}**.",
              f"Validation confidence cutoffs: 60% coverage ≈ **{cuts['coverage_60_conf_cutoff']:.6f}**, 40% coverage ≈ **{cuts['coverage_40_conf_cutoff']:.6f}**.",
              "",
              "No 2021 target was inspected by this selection script."]
    (OUT/"CHALLENGE_V1_SELECTION_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"CHALLENGE_V1_SELECTION_RESULT.md").read_text())

if __name__=="__main__":
    main()
