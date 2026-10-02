from __future__ import annotations
import io, json, os, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score, log_loss, recall_score
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","gold_target_research_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5

FEATURES=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]

TARGETS={
    "DIR_H1":{"kind":"binary","h":1},
    "DIR_H3":{"kind":"binary","h":3},
    "DIR_H5":{"kind":"binary","h":5},
    "BARRIER_H3_K050":{"kind":"barrier","h":3,"k":0.50},
    "BARRIER_H3_K075":{"kind":"barrier","h":3,"k":0.75},
    "BARRIER_H3_K100":{"kind":"barrier","h":3,"k":1.00},
    "BARRIER_H5_K075":{"kind":"barrier","h":5,"k":0.75},
}

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"target-research"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
    if len(names)!=1: raise RuntimeError(names)
    df=pd.read_csv(io.BytesIO(z.read(names[0])))
    for c in ["date","feature_cutoff_date","forecast_issue_date","target_start_date",
              "target_end_date_h1","target_end_date_h3","target_end_date_h5"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
    return df.sort_values("feature_cutoff_date").reset_index(drop=True)

def add_barriers(df):
    q=df.copy()
    r1=pd.to_numeric(q["target_r1"],errors="coerce").to_numpy(float)
    sig=pd.to_numeric(q["sigma20"],errors="coerce").to_numpy(float)
    n=len(q)
    for name,spec in TARGETS.items():
        if spec["kind"]!="barrier": continue
        h=int(spec["h"]); k=float(spec["k"])
        lab=np.full(n,None,dtype=object)
        for i in range(n):
            if not np.isfinite(sig[i]) or sig[i]<=0: continue
            vals=r1[i:i+h]
            if len(vals)<h or not np.isfinite(vals).all(): continue
            cum=np.cumsum(vals)
            up=k*sig[i]; dn=-k*sig[i]
            u=np.where(cum>=up)[0]
            d=np.where(cum<=dn)[0]
            ui=int(u[0]) if len(u) else 10**9
            di=int(d[0]) if len(d) else 10**9
            if ui<di: lab[i]="UP"
            elif di<ui: lab[i]="DOWN"
            else: lab[i]="NO_MOVE"
        q[name]=lab
    return q

def model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,penalty="l2",solver="lbfgs",max_iter=3000,random_state=SEED
        ))
    ])

def binary_metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(accuracy_score(y,pred)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "prediction_std":float(np.std(p)),
        "actual_up_rate":float(np.mean(y)),
    }

def multi_metrics(y,p,classes):
    y=np.asarray(y,object); p=np.asarray(p,float)
    idx={c:i for i,c in enumerate(classes)}
    pred=np.array([classes[i] for i in np.argmax(p,axis=1)],dtype=object)
    Y=np.zeros_like(p)
    for i,v in enumerate(y): Y[i,idx[v]]=1.0
    recalls={}
    for c in classes:
        mask=(y==c)
        recalls[c]=float(np.mean(pred[mask]==c)) if mask.any() else np.nan
    dir_mask=np.isin(pred,["UP","DOWN"])
    sel_acc=float(np.mean(pred[dir_mask]==y[dir_mask])) if dir_mask.any() else np.nan
    return {
        "n":int(len(y)),
        "accuracy":float(accuracy_score(y,pred)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "macro_f1":float(f1_score(y,pred,labels=classes,average="macro",zero_division=0)),
        "multiclass_brier":float(np.mean(np.sum((p-Y)**2,axis=1))),
        "logloss":float(log_loss(y,p,labels=classes)),
        "up_recall":recalls.get("UP"),
        "down_recall":recalls.get("DOWN"),
        "no_move_recall":recalls.get("NO_MOVE"),
        "actual_no_move_share":float(np.mean(y=="NO_MOVE")),
        "pred_directional_coverage":float(np.mean(dir_mask)),
        "selective_directional_accuracy":sel_acc,
    }

def majority_baseline(y,kind):
    vals=pd.Series(y).value_counts()
    maj=vals.index[0]
    acc=float((pd.Series(y)==maj).mean())
    if kind=="binary":
        return {"majority_class":str(maj),"majority_accuracy":acc,"majority_balanced_accuracy":0.5}
    return {"majority_class":str(maj),"majority_accuracy":acc,"majority_balanced_accuracy":1/3}

def valid_features(df):
    return df[FEATURES].apply(pd.to_numeric,errors="coerce").notna().all(axis=1)

def run_target(df,name,spec):
    h=int(spec["h"]); kind=spec["kind"]
    endcol=f"target_end_date_h{h}"
    if kind=="binary":
        yseries=np.where(pd.to_numeric(df[f"target_r{h}"],errors="coerce")>0,"UP","DOWN").astype(object)
        label_ok=df[f"target_r{h}"].notna()
    else:
        yseries=df[name].to_numpy(object)
        label_ok=df[name].notna()
    tmp=df.copy(); tmp["_y"]=yseries

    dev=tmp[
        tmp.forecast_issue_date.dt.year.between(2022,2024) &
        label_ok & valid_features(tmp)
    ].copy().reset_index(drop=True)

    pred_rows=[]
    for bs in range(0,len(dev),BLOCK):
        te=dev.iloc[bs:bs+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=tmp[
            tmp["_y"].notna() &
            tmp[endcol].notna() &
            (tmp[endcol]<=cutoff) &
            (tmp.forecast_issue_date<pd.Timestamp("2025-01-01")) &
            valid_features(tmp)
        ].copy()
        if len(tr)<500: raise RuntimeError(f"{name} train too small {len(tr)}")
        m=model()
        m.fit(tr[FEATURES].to_numpy(float),tr["_y"].to_numpy(object))
        pp=m.predict_proba(te[FEATURES].to_numpy(float))
        cls=[str(x) for x in m.named_steps["model"].classes_]
        for row,probs in zip(te.itertuples(),pp):
            rec={
                "target":name,
                "forecast_issue_date":str(row.forecast_issue_date.date()),
                "year":int(row.forecast_issue_date.year),
                "actual":str(row._y),
            }
            for c,p in zip(cls,probs): rec[f"p_{c}"]=float(p)
            pred_rows.append(rec)

    led=pd.DataFrame(pred_rows)
    metrics=[]
    periods=[("2022-2024",led)]
    for yr in [2022,2023,2024]: periods.append((str(yr),led[led.year==yr]))
    for period,g in periods:
        y=g.actual.to_numpy(object)
        if kind=="binary":
            p=g.get("p_UP",pd.Series(np.zeros(len(g)))).to_numpy(float)
            met=binary_metrics((y=="UP").astype(int),p)
            base=majority_baseline(y,kind)
        else:
            classes=["DOWN","NO_MOVE","UP"]
            p=np.column_stack([g.get(f"p_{c}",pd.Series(np.zeros(len(g)))).to_numpy(float) for c in classes])
            # fail if a class absent from a trained block left all zeros for a row
            rs=p.sum(axis=1)
            if np.any(rs<=0): raise RuntimeError(f"{name} zero prob row")
            p=p/rs[:,None]
            met=multi_metrics(y,p,classes)
            base=majority_baseline(y,kind)
        metrics.append({"target":name,"kind":kind,"horizon":h,"period":period,**met,**base})
    return led,pd.DataFrame(metrics)

def main():
    df=add_barriers(load_panel())
    all_led=[]; all_met=[]
    for name,spec in TARGETS.items():
        led,met=run_target(df,name,spec)
        all_led.append(led); all_met.append(met)
    preds=pd.concat(all_led,ignore_index=True)
    mets=pd.concat(all_met,ignore_index=True)
    preds.to_csv(OUT/"target_research_predictions.csv",index=False)
    mets.to_csv(OUT/"target_research_metrics.csv",index=False)

    head=mets[mets.period=="2022-2024"].copy()
    result={
        "schema":"GOLD_SHORT_HORIZON_TARGET_RESEARCH_V1",
        "identity":"GLOBAL_XAU_PUBLIC_STAKTRAKR_R2",
        "dev":"2022-2024",
        "features":FEATURES,
        "targets":TARGETS,
        "headline":head.to_dict(orient="records"),
    }
    (OUT/"target_research_result.json").write_text(json.dumps(result,indent=2,sort_keys=True,default=str)+"\n")

    lines=["# GOLD SHORT-HORIZON — TARGET RESEARCH V1","",
           "Same CORE3 features and same fixed Logistic model for every target. DEV only: 2022-2024.","",
           "## Ordinary direction targets","",
           "| Target | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | Majority acc |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name in ["DIR_H1","DIR_H3","DIR_H5"]:
        r=head[head.target==name].iloc[0]
        lines.append(f"| {name} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*r.majority_accuracy:.2f}% |")
    lines += ["","## Volatility-normalized first-close-hit targets","",
              "| Target | N | Accuracy | Balanced acc | Macro F1 | Brier | Log loss | NO_MOVE share | Pred directional coverage | Selective dir acc | Majority acc |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name in ["BARRIER_H3_K050","BARRIER_H3_K075","BARRIER_H3_K100","BARRIER_H5_K075"]:
        r=head[head.target==name].iloc[0]
        lines.append(f"| {name} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.macro_f1:.4f} | {r.multiclass_brier:.4f} | {r.logloss:.4f} | {100*r.actual_no_move_share:.2f}% | {100*r.pred_directional_coverage:.2f}% | {100*r.selective_directional_accuracy:.2f}% | {100*r.majority_accuracy:.2f}% |")
    lines += ["","Annual metrics and full prediction ledger are saved separately."]
    (OUT/"TARGET_RESEARCH_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"TARGET_RESEARCH_RESULT.md").read_text())

if __name__=="__main__":
    main()
