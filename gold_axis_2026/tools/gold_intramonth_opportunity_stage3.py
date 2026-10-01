import os, io, json, math, hashlib, zipfile, warnings
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge, HuberRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import log_loss, average_precision_score, roc_auc_score

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
STAGE2_ARTIFACT=11161358194
OUT=Path(os.environ.get("OUT_DIR","stage3_out"))
OUT.mkdir(parents=True, exist_ok=True)
SEED=20261001

G_ONLY=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21",
    "sigma20","rv20","absret20","dd_high21","dist_low21",
    "reversal_1_vs_5",
]
FOUR_METAL=G_ONLY+[
    "silver_r1","silver_r5","silver_r21",
    "platinum_r1","platinum_r5","platinum_r21",
    "palladium_r1","palladium_r5","palladium_r21",
    "silver_age_days","platinum_age_days","palladium_age_days",
    "cross_r1_breadth_pos","cross_r5_breadth_pos",
    "cross_r1_dispersion","cross_r5_dispersion",
    "gold_comp_r1_divergence","gold_comp_r5_divergence",
]
FEATURE_BLOCKS={"G_ONLY":G_ONLY,"FOUR_METAL":FOUR_METAL}
AGE_COLS={"silver_age_days","platinum_age_days","palladium_age_days"}
CLS_TARGETS=["opp5_k050","opp5_k075","opp5_k100"]
REG_TARGETS=["mfe5","mae5"]
BLOCK_SIZE=5

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def download_stage2():
    tok=os.environ.get("GITHUB_TOKEN")
    if not tok: raise RuntimeError("GITHUB_TOKEN missing")
    url=f"https://api.github.com/repos/{REPO}/actions/artifacts/{STAGE2_ARTIFACT}/zip"
    r=requests.get(url,headers={
        "Authorization":f"Bearer {tok}",
        "Accept":"application/vnd.github+json",
        "User-Agent":"gold-intramonth-stage3"
    },timeout=90)
    r.raise_for_status()
    z=zipfile.ZipFile(io.BytesIO(r.content))
    name=[n for n in z.namelist() if n.endswith("intramonth_opportunity_stage2_dataset.csv")]
    if len(name)!=1: raise RuntimeError(f"Stage2 dataset not uniquely found: {name}")
    df=pd.read_csv(io.BytesIO(z.read(name[0])))
    return df

def prepare(df):
    for c in ["origin_date","signal_date"]:
        df[c]=pd.to_datetime(df[c])
    df=df.sort_values("origin_date").reset_index(drop=True)
    # Label MFE5/MAE5 uses observations t+1 ... t+5.
    df["label_end_date"]=df["origin_date"].shift(-5)
    return df

def fill_train_test(train,test,features):
    a=train[features].copy()
    b=test[features].copy()
    fills={}
    for col in features:
        if col in AGE_COLS:
            mx=a[col].max(skipna=True)
            val=float(mx+1.0) if pd.notna(mx) else 999.0
        else:
            med=a[col].median(skipna=True)
            val=float(med) if pd.notna(med) else 0.0
        fills[col]=val
        a[col]=a[col].fillna(val)
        b[col]=b[col].fillna(val)
    return a,b,fills

def blocks(dev_idx,size=5):
    x=list(dev_idx)
    return [x[i:i+size] for i in range(0,len(x),size)]

def matured_train(df,start_origin,target):
    # Explicitly disallow any row whose full 5-observation outcome is not known
    # at the current block start. 2025+ cannot enter because start_origin <= 2024.
    tr=df[
        df["label_end_date"].notna()
        & (df["label_end_date"]<=start_origin)
        & df[target].notna()
        & (df["signal_date"]<pd.Timestamp("2025-01-01"))
    ].copy()
    return tr

def make_cls(name):
    if name=="LOGIT_L2":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(
                C=1.0,l1_ratio=0.0,max_iter=1000,solver="lbfgs",
                random_state=SEED
            ))
        ])
    if name=="HGB_CLASS":
        return HistGradientBoostingClassifier(
            learning_rate=0.05,max_iter=100,max_leaf_nodes=7,max_depth=3,
            min_samples_leaf=40,l2_regularization=1.0,random_state=SEED
        )
    raise KeyError(name)

def make_reg(name):
    if name=="RIDGE":
        return Pipeline([("scale",StandardScaler()),("model",Ridge(alpha=1.0))])
    if name=="HUBER":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",HuberRegressor(epsilon=1.35,alpha=0.0001,max_iter=500))
        ])
    if name=="HGB_REG":
        return HistGradientBoostingRegressor(
            learning_rate=0.05,max_iter=100,max_leaf_nodes=7,max_depth=3,
            min_samples_leaf=40,l2_regularization=1.0,loss="squared_error",
            random_state=SEED
        )
    raise KeyError(name)

def safe_roc(y,p):
    try: return float(roc_auc_score(y,p))
    except: return None

def safe_pr(y,p):
    try: return float(average_precision_score(y,p))
    except: return None

def spearman(y,p):
    a=pd.Series(y).rank(method="average").to_numpy(float)
    b=pd.Series(p).rank(method="average").to_numpy(float)
    if np.std(a)==0 or np.std(b)==0: return None
    return float(np.corrcoef(a,b)[0,1])

def cls_metrics(y,p):
    y=np.asarray(y,float); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return {
        "n":int(len(y)),
        "prevalence":float(np.mean(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "pr_auc":safe_pr(y,p),
        "roc_auc":safe_roc(y,p),
        "prediction_mean":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
        "prediction_min":float(np.min(p)),
        "prediction_max":float(np.max(p)),
    }

def reg_metrics(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float)
    err=p-y
    return {
        "n":int(len(y)),
        "mae":float(np.mean(np.abs(err))),
        "rmse":float(np.sqrt(np.mean(err**2))),
        "spearman":spearman(y,p),
        "prediction_mean":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
    }

def build_dev(df):
    return df[
        (df["signal_date"]>=pd.Timestamp("2022-01-01"))
        & (df["signal_date"]<=pd.Timestamp("2024-12-31"))
    ].copy()

def baseline_for_train(train,target,kind):
    vals=train[target].astype(float)
    if kind=="cls":
        return float(vals.mean()), float(vals.iloc[-252:].mean())
    return float(vals.median()), float(vals.iloc[-252:].median())

def evaluate_cls(df,dev,feature_name,features,target,model_name):
    rows=[]
    for block_id,inds in enumerate(blocks(dev.index,BLOCK_SIZE)):
        test=df.loc[inds].copy()
        start=test["origin_date"].min()
        train=matured_train(df,start,target)
        if len(train)<252: raise RuntimeError(f"Insufficient train {len(train)} at {start}")
        Xtr,Xte,_=fill_train_test(train,test,features)
        ytr=train[target].astype(int)
        m=make_cls(model_name)
        m.fit(Xtr,ytr)
        pred=m.predict_proba(Xte)[:,1]
        pexp,proll=baseline_for_train(train,target,"cls")
        for ix,pp in zip(inds,pred):
            rows.append({
                "row_index":int(ix),"block_id":block_id,
                "origin_date":str(df.at[ix,"origin_date"].date()),
                "signal_date":str(df.at[ix,"signal_date"].date()),
                "feature_block":feature_name,"target":target,"model":model_name,
                "y":float(df.at[ix,target]),"prediction":float(pp),
                "baseline_expand":pexp,"baseline_roll252":proll,
                "train_n":int(len(train)),"train_last_label_end":str(train["label_end_date"].max().date()),
                "block_start_origin":str(start.date())
            })
    return pd.DataFrame(rows)

def evaluate_reg(df,dev,feature_name,features,target,model_name):
    rows=[]
    for block_id,inds in enumerate(blocks(dev.index,BLOCK_SIZE)):
        test=df.loc[inds].copy()
        start=test["origin_date"].min()
        train=matured_train(df,start,target)
        if len(train)<252: raise RuntimeError(f"Insufficient train {len(train)} at {start}")
        Xtr,Xte,_=fill_train_test(train,test,features)
        ytr=train[target].astype(float)
        m=make_reg(model_name)
        try:
            m.fit(Xtr,ytr)
        except Exception:
            # Huber can fail to converge in isolated expanding fits; retry with a larger cap,
            # without changing epsilon/alpha or using future information.
            if model_name=="HUBER":
                m=Pipeline([
                    ("scale",StandardScaler()),
                    ("model",HuberRegressor(epsilon=1.35,alpha=0.0001,max_iter=2000))
                ])
                m.fit(Xtr,ytr)
            else:
                raise
        pred=m.predict(Xte)
        bexp,broll=baseline_for_train(train,target,"reg")
        for ix,pp in zip(inds,pred):
            rows.append({
                "row_index":int(ix),"block_id":block_id,
                "origin_date":str(df.at[ix,"origin_date"].date()),
                "signal_date":str(df.at[ix,"signal_date"].date()),
                "feature_block":feature_name,"target":target,"model":model_name,
                "y":float(df.at[ix,target]),"prediction":float(pp),
                "baseline_expand":bexp,"baseline_roll252":broll,
                "train_n":int(len(train)),"train_last_label_end":str(train["label_end_date"].max().date()),
                "block_start_origin":str(start.date())
            })
    return pd.DataFrame(rows)

def audit_features(df,dev):
    out=[]
    hist=df[df["signal_date"]<pd.Timestamp("2025-01-01")]
    for block,features in FEATURE_BLOCKS.items():
        for f in features:
            out.append({
                "feature_block":block,"feature":f,
                "background_dev_nonmissing":int(hist[f].notna().sum()),
                "background_dev_missing":int(hist[f].isna().sum()),
                "dev_nonmissing":int(dev[f].notna().sum()),
                "dev_missing":int(dev[f].isna().sum()),
                "dev_missing_rate":float(dev[f].isna().mean()),
            })
    return pd.DataFrame(out)

def summarize(preds):
    metric_rows=[]
    status_rows=[]
    for (kind,feature,target,model),z in preds.groupby(["kind","feature_block","target","model"]):
        y=z["y"].to_numpy(float)
        p=z["prediction"].to_numpy(float)
        be=z["baseline_expand"].to_numpy(float)
        br=z["baseline_roll252"].to_numpy(float)
        if kind=="cls":
            mm=cls_metrics(y,p); me=cls_metrics(y,be); mr=cls_metrics(y,br)
            best_brier=min(me["brier"],mr["brier"])
            best_ll=min(me["logloss"],mr["logloss"])
            improve=(best_brier-mm["brier"])/best_brier
            passed=(improve>=0.01 and mm["logloss"]<=best_ll and mm["prediction_std"]>1e-4)
            metric_rows.append({
                "kind":kind,"feature_block":feature,"target":target,"model":model,
                **{f"model_{k}":v for k,v in mm.items()},
                "expand_brier":me["brier"],"expand_logloss":me["logloss"],
                "roll_brier":mr["brier"],"roll_logloss":mr["logloss"],
                "best_baseline_brier":best_brier,"best_baseline_logloss":best_ll,
                "primary_relative_improvement":improve,
                "scientific_gate":"PASS" if passed else "FAIL",
            })
        else:
            mm=reg_metrics(y,p); me=reg_metrics(y,be); mr=reg_metrics(y,br)
            best_mae=min(me["mae"],mr["mae"])
            best_rmse=min(me["rmse"],mr["rmse"])
            improve=(best_mae-mm["mae"])/best_mae
            passed=(improve>=0.01 and mm["rmse"]<=best_rmse)
            metric_rows.append({
                "kind":kind,"feature_block":feature,"target":target,"model":model,
                **{f"model_{k}":v for k,v in mm.items()},
                "expand_mae":me["mae"],"expand_rmse":me["rmse"],
                "roll_mae":mr["mae"],"roll_rmse":mr["rmse"],
                "best_baseline_mae":best_mae,"best_baseline_rmse":best_rmse,
                "primary_relative_improvement":improve,
                "scientific_gate":"PASS" if passed else "FAIL",
            })
    metrics=pd.DataFrame(metric_rows)
    # best eligible by target/kind; if none pass, retain best observed but mark NO_PASS
    for (kind,target),z in metrics.groupby(["kind","target"]):
        zp=z[z["scientific_gate"]=="PASS"]
        if len(zp):
            best=zp.sort_values("primary_relative_improvement",ascending=False).iloc[0]
            status="PASS"
        else:
            best=z.sort_values("primary_relative_improvement",ascending=False).iloc[0]
            status="NO_PASS"
        status_rows.append({
            "kind":kind,"target":target,"target_status":status,
            "best_feature_block":best["feature_block"],"best_model":best["model"],
            "best_relative_improvement":float(best["primary_relative_improvement"]),
            "best_scientific_gate":best["scientific_gate"],
        })
    return metrics,pd.DataFrame(status_rows)

def main():
    df=prepare(download_stage2())
    # Hard governance asserts.
    assert df["signal_date"].max()>=pd.Timestamp("2025-12-31")
    dev=build_dev(df)
    assert len(dev)==749
    assert dev["signal_date"].max()<pd.Timestamp("2025-01-01")

    fa=audit_features(df,dev)
    fa.to_csv(OUT/"feature_availability_audit.csv",index=False)

    allpred=[]
    for fname,features in FEATURE_BLOCKS.items():
        for target in CLS_TARGETS:
            for model in ["LOGIT_L2","HGB_CLASS"]:
                print("RUN",fname,target,model,flush=True)
                z=evaluate_cls(df,dev,fname,features,target,model)
                z["kind"]="cls"
                allpred.append(z)
        for target in REG_TARGETS:
            for model in ["RIDGE","HUBER","HGB_REG"]:
                print("RUN",fname,target,model,flush=True)
                z=evaluate_reg(df,dev,fname,features,target,model)
                z["kind"]="reg"
                allpred.append(z)

    preds=pd.concat(allpred,ignore_index=True)
    preds.to_csv(OUT/"stage3_dev_predictions_long.csv",index=False)

    metrics,status=summarize(preds)
    metrics=metrics.sort_values(["kind","target","scientific_gate","primary_relative_improvement"],ascending=[True,True,True,False])
    metrics.to_csv(OUT/"stage3_metrics.csv",index=False)
    status.to_csv(OUT/"stage3_target_status.csv",index=False)

    passes=metrics[metrics["scientific_gate"]=="PASS"].copy()
    overall="PASS" if len(passes)>0 else "FAIL_NO_PREDICTIVE_SIGNAL"

    summary={
        "status":overall,
        "dev_n":int(len(dev)),
        "refit_block_size":BLOCK_SIZE,
        "stage2_artifact":STAGE2_ARTIFACT,
        "feature_blocks":{k:len(v) for k,v in FEATURE_BLOCKS.items()},
        "model_count":int(metrics.shape[0]),
        "pass_count":int(len(passes)),
        "targets":status.to_dict(orient="records"),
        "passes":passes[["kind","feature_block","target","model","primary_relative_improvement"]].to_dict(orient="records"),
    }

    # concise tables for result doc
    lines=[
        "# GOLD INTRAMONTH OPPORTUNITY — Stage 3 Predictability Screen Result",
        "",
        f"**Status:** **{overall}**",
        "",
        "## Scientific protocol",
        f"- DEV predictions: {len(dev)} origins, 2022-2024",
        f"- refit: every {BLOCK_SIZE} Gold origins",
        "- full 5-observation label maturity required before any training row enters",
        "- 2025/2026 not evaluated or used",
        "- no monthly ChHHO context used",
        "",
        "## Target decisions",
        "",
        "| Kind | Target | Status | Best feature | Best model | Primary improvement |",
        "|---|---|---|---|---|---:|",
    ]
    for _,r in status.sort_values(["kind","target"]).iterrows():
        lines.append(f"| {r['kind']} | {r['target']} | {r['target_status']} | {r['best_feature_block']} | {r['best_model']} | {100*r['best_relative_improvement']:.2f}% |")
    lines += ["","## All model metrics","","### Binary"]
    cm=metrics[metrics["kind"]=="cls"].copy()
    lines += [
        "| Target | Feature | Model | Brier | Best baseline | Rel. improv. | Log loss | Baseline LL | Gate |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for _,r in cm.sort_values(["target","primary_relative_improvement"],ascending=[True,False]).iterrows():
        lines.append(
            f"| {r['target']} | {r['feature_block']} | {r['model']} | {r['model_brier']:.5f} | "
            f"{r['best_baseline_brier']:.5f} | {100*r['primary_relative_improvement']:.2f}% | "
            f"{r['model_logloss']:.5f} | {r['best_baseline_logloss']:.5f} | {r['scientific_gate']} |"
        )
    lines += ["","### Continuous",
        "| Target | Feature | Model | MAE | Best baseline | Rel. improv. | RMSE | Baseline RMSE | Gate |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    rm=metrics[metrics["kind"]=="reg"].copy()
    for _,r in rm.sort_values(["target","primary_relative_improvement"],ascending=[True,False]).iterrows():
        lines.append(
            f"| {r['target']} | {r['feature_block']} | {r['model']} | {r['model_mae']:.6f} | "
            f"{r['best_baseline_mae']:.6f} | {100*r['primary_relative_improvement']:.2f}% | "
            f"{r['model_rmse']:.6f} | {r['best_baseline_rmse']:.6f} | {r['scientific_gate']} |"
        )

    if overall=="PASS":
        lines += [
            "",
            "## Binding conclusion",
            "At least one origin-safe core target/model beats its frozen matured-history baseline under the pre-registered gate.",
            "Stage 4 may test monthly ChHHO context incrementally, but only on the frozen Stage-3 core winner(s).",
        ]
    else:
        lines += [
            "",
            "## Binding conclusion",
            "No core candidate clears the frozen predictive gate.",
            "Do not proceed to monthly-context Stage 4 as if a core daily signal exists; redesign target/features on DEV only.",
        ]

    # Save summary before hashes.
    (OUT/"STAGE3_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=[
        OUT/"feature_availability_audit.csv",OUT/"stage3_dev_predictions_long.csv",
        OUT/"stage3_metrics.csv",OUT/"stage3_target_status.csv",OUT/"STAGE3_RESULT.md"
    ]
    summary["hashes"]={p.name:sha256_file(p) for p in files}
    (OUT/"stage3_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

    print("STAGE3_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE3_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
