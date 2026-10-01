import os, io, json, math, hashlib, zipfile, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.metrics import log_loss, average_precision_score, roc_auc_score, balanced_accuracy_score, precision_score, recall_score

from lightgbm import LGBMClassifier, LGBMRegressor
from xgboost import XGBClassifier, XGBRegressor

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=11181284118
OUT=Path(os.environ.get("OUT_DIR","global_xau_stage1_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5

GOLD_ONLY=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
CORE3=GOLD_ONLY+[
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
]
SAFE_EXT=[
    "DGS10","DFII10","BREAKEVEN10_PROXY",
    "BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD",
    "VIX","NDX"
]
CORE4=CORE3+["palladium_r1","palladium_r5","palladium_r21","palladium_age_days"]\nBLOCKS={"GOLD_ONLY":GOLD_ONLY,"CORE3":CORE3,"CORE4":CORE4,"CORE3_SAFE_EXTERNAL":CORE3+SAFE_EXT}

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage1"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1: raise RuntimeError((suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    df=read_csv(z,"global_xau_readiness_panel.csv")
    for c in ["date","signal_date"]:
        df[c]=pd.to_datetime(df[c])
    df=df.sort_values("date").reset_index(drop=True)
    return df

def mature_mask(df,start,h):
    # target_rh for row i is known only after h future observations.
    maturity=df["date"].shift(-h)
    return maturity.notna() & (maturity<=start) & (df["signal_date"]<pd.Timestamp("2025-01-01"))

def fill_train_test(train,test,features):
    a=train[features].copy(); b=test[features].copy()
    for c in features:
        med=a[c].median(skipna=True)
        val=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(val); b[c]=b[c].fillna(val)
    return a,b

def cls_model(name):
    if name=="LOGIT_L2":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED))
        ])
    if name=="LGBM_CLASS":
        return LGBMClassifier(
            n_estimators=100,learning_rate=0.03,num_leaves=7,max_depth=3,
            min_child_samples=40,reg_lambda=1.0,subsample=1.0,colsample_bytree=1.0,
            random_state=SEED,n_jobs=1,verbosity=-1
        )
    if name=="XGB_CLASS":
        return XGBClassifier(
            n_estimators=100,learning_rate=0.03,max_depth=3,min_child_weight=20,
            subsample=1.0,colsample_bytree=1.0,reg_lambda=1.0,
            objective="binary:logistic",eval_metric="logloss",
            random_state=SEED,n_jobs=1,tree_method="hist"
        )
    raise KeyError(name)

def reg_model(name):
    if name=="ELASTIC_NET":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",ElasticNet(alpha=0.0005,l1_ratio=0.5,max_iter=10000,random_state=SEED))
        ])
    if name=="LGBM_REG":
        return LGBMRegressor(
            n_estimators=100,learning_rate=0.03,num_leaves=7,max_depth=3,
            min_child_samples=40,reg_lambda=1.0,random_state=SEED,n_jobs=1,verbosity=-1
        )
    if name=="XGB_REG":
        return XGBRegressor(
            n_estimators=100,learning_rate=0.03,max_depth=3,min_child_weight=20,
            subsample=1.0,colsample_bytree=1.0,reg_lambda=1.0,
            objective="reg:squarederror",random_state=SEED,n_jobs=1,tree_method="hist"
        )
    raise KeyError(name)

def quant_model(q):
    return LGBMRegressor(
        objective="quantile",alpha=q,n_estimators=100,learning_rate=0.03,
        num_leaves=7,max_depth=3,min_child_samples=40,reg_lambda=1.0,
        random_state=SEED,n_jobs=1,verbosity=-1
    )

def safe_auc(y,p,kind):
    try:
        return float(roc_auc_score(y,p) if kind=="roc" else average_precision_score(y,p))
    except:
        return None

def cls_metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    return {
        "n":len(y),"brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "up_precision":float(precision_score(y,pred,zero_division=0)),
        "up_recall":float(recall_score(y,pred,zero_division=0)),
        "roc_auc":safe_auc(y,p,"roc"),"pr_auc":safe_auc(y,p,"pr"),
        "prediction_std":float(np.std(p))
    }

def reg_metrics(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float)
    e=p-y
    pred_sign=p>0; ysign=y>0
    sy=pd.Series(y).rank().to_numpy(); sp=pd.Series(p).rank().to_numpy()
    rho=float(np.corrcoef(sy,sp)[0,1]) if np.std(sp)>0 and np.std(sy)>0 else None
    return {
        "n":len(y),"mae":float(np.mean(np.abs(e))),
        "rmse":float(np.sqrt(np.mean(e**2))),
        "direction_accuracy":float(np.mean(pred_sign==ysign)),
        "spearman":rho,"prediction_std":float(np.std(p))
    }

def pinball(y,p,q):
    e=np.asarray(y,float)-np.asarray(p,float)
    return float(np.mean(np.maximum(q*e,(q-1)*e)))

def main():
    horizon=int(os.environ["HORIZON"])
    df=load_panel()
    target=f"target_r{horizon}"
    dev=df[(df["role"]=="DEV") & df[target].notna()].copy()
    if len(dev)<700: raise RuntimeError(f"DEV n {len(dev)} < 700")

    pred_rows=[]
    quant_rows=[]

    # Precompute baselines blockwise using matured prior labels.
    for block_id in range(0,len(dev),BLOCK):
        te=dev.iloc[block_id:block_id+BLOCK].copy()
        start=te["date"].min()
        mm=mature_mask(df,start,horizon) & df[target].notna()
        tr0=df[mm].copy()
        if len(tr0)<252: raise RuntimeError(f"insufficient train {len(tr0)}")

        ytr=tr0[target].astype(float)
        yte=te[target].astype(float).to_numpy()
        uptr=(ytr>0).astype(int)
        upte=(yte>0).astype(int)

        p_expand=float(uptr.mean()); p_roll=float(uptr.iloc[-252:].mean())
        mean_expand=float(ytr.mean()); mean_roll=float(ytr.iloc[-252:].mean())
        qexp={q:float(ytr.quantile(q)) for q in [0.1,0.5,0.9]}
        qroll={q:float(ytr.iloc[-252:].quantile(q)) for q in [0.1,0.5,0.9]}

        for ix,yv,yu in zip(te.index,yte,upte):
            common={
                "horizon":horizon,"row_index":int(ix),
                "origin_date":str(df.at[ix,"date"].date()),
                "signal_date":str(df.at[ix,"signal_date"].date()),
                "y_return":float(yv),"y_up":int(yu),"block_id":block_id//BLOCK,
                "train_n":int(len(tr0))
            }
            pred_rows += [
                {**common,"head":"direction","feature_block":"BASE","model":"EXPAND_PREV","prediction":p_expand},
                {**common,"head":"direction","feature_block":"BASE","model":"ROLL252_PREV","prediction":p_roll},
                {**common,"head":"return","feature_block":"BASE","model":"ZERO","prediction":0.0},
                {**common,"head":"return","feature_block":"BASE","model":"EXPAND_MEAN","prediction":mean_expand},
                {**common,"head":"return","feature_block":"BASE","model":"ROLL252_MEAN","prediction":mean_roll},
            ]
            for q in [0.1,0.5,0.9]:
                quant_rows += [
                    {**common,"feature_block":"BASE","model":"EXPAND_QUANT","quantile":q,"prediction":qexp[q]},
                    {**common,"feature_block":"BASE","model":"ROLL252_QUANT","quantile":q,"prediction":qroll[q]},
                ]

        for bname,features in BLOCKS.items():
            Xtr,Xte=fill_train_test(tr0,te,features)

            for mname in ["LOGIT_L2","LGBM_CLASS","XGB_CLASS"]:
                m=cls_model(mname); m.fit(Xtr,uptr)
                pp=m.predict_proba(Xte)[:,1]
                for ix,yv,yu,pv in zip(te.index,yte,upte,pp):
                    pred_rows.append({
                        "horizon":horizon,"row_index":int(ix),"origin_date":str(df.at[ix,"date"].date()),
                        "signal_date":str(df.at[ix,"signal_date"].date()),"y_return":float(yv),"y_up":int(yu),
                        "block_id":block_id//BLOCK,"train_n":int(len(tr0)),
                        "head":"direction","feature_block":bname,"model":mname,"prediction":float(pv)
                    })

            for mname in ["ELASTIC_NET","LGBM_REG","XGB_REG"]:
                m=reg_model(mname); m.fit(Xtr,ytr)
                pp=m.predict(Xte)
                for ix,yv,yu,pv in zip(te.index,yte,upte,pp):
                    pred_rows.append({
                        "horizon":horizon,"row_index":int(ix),"origin_date":str(df.at[ix,"date"].date()),
                        "signal_date":str(df.at[ix,"signal_date"].date()),"y_return":float(yv),"y_up":int(yu),
                        "block_id":block_id//BLOCK,"train_n":int(len(tr0)),
                        "head":"return","feature_block":bname,"model":mname,"prediction":float(pv)
                    })

            # quantile head only LightGBM
            for q in [0.1,0.5,0.9]:
                m=quant_model(q); m.fit(Xtr,ytr)
                pp=m.predict(Xte)
                for ix,yv,yu,pv in zip(te.index,yte,upte,pp):
                    quant_rows.append({
                        "horizon":horizon,"row_index":int(ix),"origin_date":str(df.at[ix,"date"].date()),
                        "signal_date":str(df.at[ix,"signal_date"].date()),"y_return":float(yv),"y_up":int(yu),
                        "block_id":block_id//BLOCK,"train_n":int(len(tr0)),
                        "feature_block":bname,"model":"LGBM_QUANT","quantile":q,"prediction":float(pv)
                    })

    pred=pd.DataFrame(pred_rows)
    quant=pd.DataFrame(quant_rows)
    pred.to_csv(OUT/f"global_xau_stage1_h{horizon}_predictions.csv",index=False)
    quant.to_csv(OUT/f"global_xau_stage1_h{horizon}_quantile_predictions.csv",index=False)

    metric_rows=[]
    for (head,fb,model),z in pred.groupby(["head","feature_block","model"]):
        if head=="direction":
            m=cls_metrics(z["y_up"],z["prediction"])
        else:
            m=reg_metrics(z["y_return"],z["prediction"])
        metric_rows.append({"horizon":horizon,"head":head,"feature_block":fb,"model":model,**m})

    qmetric=[]
    for (fb,model,q),z in quant.groupby(["feature_block","model","quantile"]):
        qmetric.append({
            "horizon":horizon,"feature_block":fb,"model":model,"quantile":float(q),
            "pinball":pinball(z["y_return"],z["prediction"],float(q)),
            "coverage":float((z["y_return"]<=z["prediction"]).mean())
        })
    qm=pd.DataFrame(qmetric)
    mm=pd.DataFrame(metric_rows)

    # Add mean 3-quantile score by model/block
    qmean=qm.groupby(["horizon","feature_block","model"],as_index=False)["pinball"].mean().rename(columns={"pinball":"mean_pinball"})
    qcov=qm.pivot_table(index=["horizon","feature_block","model"],columns="quantile",values="coverage").reset_index()
    qsum=qmean.merge(qcov,on=["horizon","feature_block","model"],how="left")

    mm.to_csv(OUT/f"global_xau_stage1_h{horizon}_metrics.csv",index=False)
    qm.to_csv(OUT/f"global_xau_stage1_h{horizon}_quantile_metrics.csv",index=False)
    qsum.to_csv(OUT/f"global_xau_stage1_h{horizon}_quantile_summary.csv",index=False)

    print(f"H{horizon}_COMPLETE metrics={len(mm)} qmetrics={len(qm)}",flush=True)

if __name__=="__main__":
    main()
