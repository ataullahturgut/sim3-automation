from __future__ import annotations
import io, json, os, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, confusion_matrix, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","gold_forecasting_challenge_v1_test_out"))
OUT.mkdir(parents=True,exist_ok=True)
LOCK_PATH=Path("gold_axis_2026/GOLD_FORECASTING_CHALLENGE_V1_CHAMPION_LOCK_2026-10-02.json")
BLOCK=5

CORE3=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"gold-challenge-v1-test"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
    if len(names)!=1: raise RuntimeError(names)
    df=pd.read_csv(io.BytesIO(z.read(names[0])))
    for c in ["date","feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
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

def champion_model(lock):
    m=lock["model"]
    if lock["feature_block"]!="CORE3" or lock["features"]!=CORE3 or m["name"]!="LOGIT_EN":
        raise RuntimeError("LOCK_SPEC_UNEXPECTED")
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=float(m["C"]),solver=m["solver"],penalty=m["penalty"],
            l1_ratio=float(m["l1_ratio"]),max_iter=int(m["max_iter"]),
            tol=float(m["tol"]),random_state=int(m["random_state"])
        )),
    ])

def comparator_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=20261001)),
    ])

def metrics(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    tn,fp,fn,tp=[int(x) for x in confusion_matrix(y,pred,labels=[0,1]).ravel()]
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "false_call_rate":float(np.mean(pred!=y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "prediction_std":float(np.std(p)),
        "mean_p_up":float(np.mean(p)),
        "actual_up_rate":float(np.mean(y)),
        "tn":tn,"fp":fp,"fn":fn,"tp":tp,
    }

def selective_metrics(y,p,cutoff):
    y=np.asarray(y,int); p=np.asarray(p,float)
    conf=np.abs(p-0.5)
    mask=conf>=float(cutoff)
    if mask.sum()==0:
        return {"n_calls":0,"coverage":0.0}
    yy=y[mask]; pp=p[mask]; pred=(pp>=0.5).astype(int)
    tn,fp,fn,tp=[int(x) for x in confusion_matrix(yy,pred,labels=[0,1]).ravel()]
    return {
        "n_calls":int(mask.sum()),
        "coverage":float(mask.mean()),
        "accuracy":float(np.mean(pred==yy)),
        "balanced_accuracy":float(balanced_accuracy_score(yy,pred)),
        "false_call_rate":float(np.mean(pred!=yy)),
        "up_recall":float(recall_score(yy,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(yy,pred,pos_label=0,zero_division=0)),
        "up_calls":int(np.sum(pred==1)),
        "down_calls":int(np.sum(pred==0)),
        "tn":tn,"fp":fp,"fn":fn,"tp":tp,
    }

def main():
    lock=json.loads(LOCK_PATH.read_text())
    if int(lock["sealed_test_year"])!=2021 or lock["integrity"]["test_labels_inspected_before_lock"] is not False:
        raise RuntimeError("LOCK_INTEGRITY_INVALID")

    df=load_panel()
    te_all=df[
        (df.forecast_issue_date.dt.year==2021) &
        df.target_r3.notna()
    ].copy().reset_index(drop=True)
    if len(te_all)<240: raise RuntimeError(f"TEST_TOO_SMALL {len(te_all)}")

    rows=[]
    for bs in range(0,len(te_all),BLOCK):
        te=te_all.iloc[bs:bs+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=cutoff) &
            (df.forecast_issue_date<pd.Timestamp("2021-01-01"))
        ].copy()
        # For later 2021 blocks, allow matured earlier 2021 labels exactly as a real expanding deployment would.
        tr2=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=cutoff)
        ].copy()
        tr=tr2
        if len(tr)<2000: raise RuntimeError(f"TRAIN_TOO_SMALL {len(tr)}")
        Xtr,Xte=fill_train_test(tr,te,CORE3)
        ytr=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
        yte=(te.target_r3.astype(float)>0).astype(int).to_numpy()

        champ=champion_model(lock)
        champ.fit(Xtr,ytr)
        pc=champ.predict_proba(Xte)[:,1]

        comp=comparator_model()
        comp.fit(Xtr,ytr)
        pl2=comp.predict_proba(Xte)[:,1]

        pbase=float(ytr.mean())

        for r,yy,a,b in zip(te.itertuples(),yte,pc,pl2):
            common={
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "target_end_date_h3":str(r.target_end_date_h3.date()),
                "y_up":int(yy),
                "train_n":int(len(tr)),
            }
            rows.append({**common,"model":"CHAMPION_CORE3_LOGIT_EN","p_up":float(a)})
            rows.append({**common,"model":"COMPARATOR_CORE3_LOGIT_L2","p_up":float(b)})
            rows.append({**common,"model":"EXPANDING_PRIOR","p_up":pbase})

    led=pd.DataFrame(rows)
    led.to_csv(OUT/"challenge_v1_2021_predictions.csv",index=False)

    full=[]
    for name,g in led.groupby("model"):
        full.append({"model":name,**metrics(g.y_up,g.p_up)})
    mdf=pd.DataFrame(full)
    mdf.to_csv(OUT/"challenge_v1_2021_metrics.csv",index=False)

    cg=led[led.model=="CHAMPION_CORE3_LOGIT_EN"].copy()
    y=cg.y_up.to_numpy(int); p=cg.p_up.to_numpy(float)
    sel=[]
    for label,key in [
        ("VALIDATION_60PCT_COVERAGE_CUTOFF","coverage_60_conf_cutoff"),
        ("VALIDATION_40PCT_COVERAGE_CUTOFF","coverage_40_conf_cutoff"),
    ]:
        sm=selective_metrics(y,p,lock["confidence_cutoffs"][key])
        sel.append({"rule":label,"confidence_cutoff":lock["confidence_cutoffs"][key],**sm})
    sdf=pd.DataFrame(sel)
    sdf.to_csv(OUT/"challenge_v1_2021_selective_metrics.csv",index=False)

    champ_row=mdf[mdf.model=="CHAMPION_CORE3_LOGIT_EN"].iloc[0].to_dict()
    comp_row=mdf[mdf.model=="COMPARATOR_CORE3_LOGIT_L2"].iloc[0].to_dict()
    base_row=mdf[mdf.model=="EXPANDING_PRIOR"].iloc[0].to_dict()
    result={
        "schema":"GOLD_FORECASTING_CHALLENGE_V1_SEALED_TEST",
        "test_year":2021,
        "lock_file":str(LOCK_PATH),
        "lock_selection_commit":lock["selection_commit"],
        "champion_lock_model":lock["model"],
        "champion":champ_row,
        "comparator":comp_row,
        "baseline":base_row,
        "selective":sel,
    }
    (OUT/"challenge_v1_2021_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD FORECASTING CHALLENGE V1 — SEALED 2021 TEST","",
        f"Locked champion: **{lock['feature_block']} + {lock['model']['name']}**.",
        f"Selection commit recorded in lock: \`{lock['selection_commit']}\`.","",
        "## Full coverage","",
        "| Model | N | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    order=["EXPANDING_PRIOR","COMPARATOR_CORE3_LOGIT_L2","CHAMPION_CORE3_LOGIT_EN"]
    for name in order:
        r=mdf[mdf.model==name].iloc[0]
        lines.append(
            f"| {name} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.false_call_rate:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    lines += ["","## Frozen confidence filters","",
              "| Validation-frozen rule | Calls | Coverage | Accuracy | Balanced acc | False calls | UP calls | DOWN calls |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in sdf.itertuples():
        lines.append(
            f"| {r.rule} | {int(r.n_calls)} | {100*r.coverage:.2f}% | "
            f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.false_call_rate:.2f}% | {int(r.up_calls)} | {int(r.down_calls)} |"
        )
    lines += ["","This is the single sealed-test report for Challenge V1. Any model modification belongs to a new challenge version."]
    (OUT/"CHALLENGE_V1_2021_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"CHALLENGE_V1_2021_RESULT.md").read_text())

if __name__=="__main__":
    main()
