import os,io,json,hashlib,zipfile,warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.metrics import log_loss, roc_auc_score, average_precision_score
from lightgbm import LGBMRegressor
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=11166972412
OUT=Path(os.environ.get("OUT_DIR","stage2_h3_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5
H=3

GOLD_ONLY=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
CORE3=GOLD_ONLY+[
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
]
CORE4=CORE3+["palladium_r1","palladium_r5","palladium_r21","palladium_age_days"]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage2"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1: raise RuntimeError((suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    df=read_csv(z,"short_horizon_readiness_panel.csv")
    df["date"]=pd.to_datetime(df["date"])
    df["signal_date"]=pd.to_datetime(df["signal_date"])
    df=df.sort_values("date").reset_index(drop=True)

    # Causal transforms on already conservative as-of joined external levels.
    for c in ["DGS10","DFII10","BREAKEVEN10_PROXY"]:
        df[f"{c}_d1"]=df[c].diff(1)
        df[f"{c}_d5"]=df[c].diff(5)
    df["REAL_NOM_SPREAD"]=df["DGS10"]-df["DFII10"]
    df["REAL_NOM_SPREAD_d5"]=df["REAL_NOM_SPREAD"].diff(5)

    for c in ["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]:
        lc=np.log(df[c].where(df[c]>0))
        df[f"{c}_lr1"]=lc.diff(1)
        df[f"{c}_lr5"]=lc.diff(5)

    lv=np.log(df["VIX"].where(df["VIX"]>0))
    df["VIX_lr1"]=lv.diff(1)
    df["VIX_lr5"]=lv.diff(5)
    roll_mean=df["VIX"].rolling(20,min_periods=20).mean()
    roll_std=df["VIX"].rolling(20,min_periods=20).std(ddof=0)
    df["VIX_z20"]=(df["VIX"]-roll_mean)/roll_std.replace(0,np.nan)

    ln=np.log(df["NDX"].where(df["NDX"]>0))
    for k in [1,5,21]:
        df[f"NDX_lr{k}"]=ln.diff(k)

    return df

RATES_X=["DGS10_d1","DGS10_d5","DFII10_d1","DFII10_d5","BREAKEVEN10_PROXY_d1","BREAKEVEN10_PROXY_d5","REAL_NOM_SPREAD","REAL_NOM_SPREAD_d5"]
FX_X=[]
for c in ["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]:
    FX_X += [f"{c}_lr1",f"{c}_lr5"]
VIX_X=["VIX_lr1","VIX_lr5","VIX_z20"]
NDX_X=["NDX_lr1","NDX_lr5","NDX_lr21"]

BLOCKS={
    "GOLD_ONLY":GOLD_ONLY,
    "CORE3":CORE3,
    "CORE4":CORE4,
    "CORE3_RATES_XFORM":CORE3+RATES_X,
    "CORE3_FX_XFORM":CORE3+FX_X,
    "CORE3_VIX_XFORM":CORE3+VIX_X,
    "CORE3_NDX_XFORM":CORE3+NDX_X,
    "CORE3_ALL_XFORM":CORE3+RATES_X+FX_X+VIX_X+NDX_X,
}

def maturity_date(df):
    return df["date"].shift(-H)

def xgb_cls():
    return XGBClassifier(
        n_estimators=100,learning_rate=0.03,max_depth=3,min_child_weight=20,
        subsample=1.0,colsample_bytree=1.0,reg_lambda=1.0,
        objective="binary:logistic",eval_metric="logloss",
        random_state=SEED,n_jobs=1,tree_method="hist"
    )

def lgb_reg():
    return LGBMRegressor(
        n_estimators=100,learning_rate=0.03,num_leaves=7,max_depth=3,
        min_child_samples=40,reg_lambda=1.0,random_state=SEED,n_jobs=1,verbosity=-1
    )

def lgb_quant(q):
    return LGBMRegressor(
        objective="quantile",alpha=q,n_estimators=100,learning_rate=0.03,
        num_leaves=7,max_depth=3,min_child_samples=40,reg_lambda=1.0,
        random_state=SEED,n_jobs=1,verbosity=-1
    )

def cls_metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    out={
        "n":len(y),"brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean((p>=0.5)==y)),
        "prediction_std":float(np.std(p))
    }
    try: out["roc_auc"]=float(roc_auc_score(y,p))
    except: out["roc_auc"]=None
    try: out["pr_auc"]=float(average_precision_score(y,p))
    except: out["pr_auc"]=None
    return out

def reg_metrics(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float); e=p-y
    return {
        "n":len(y),"mae":float(np.mean(np.abs(e))),
        "rmse":float(np.sqrt(np.mean(e**2))),
        "direction_accuracy":float(np.mean((p>0)==(y>0))),
        "prediction_std":float(np.std(p))
    }

def pinball(y,p,q):
    e=np.asarray(y,float)-np.asarray(p,float)
    return float(np.mean(np.maximum(q*e,(q-1)*e)))

def run_block(df,dev,bname,features):
    rows=[]; qrows=[]
    mat=maturity_date(df)
    for start_i in range(0,len(dev),BLOCK):
        te=dev.iloc[start_i:start_i+BLOCK].copy()
        start=te["date"].min()
        trmask=mat.notna() & (mat<=start) & df["target_r3"].notna() & (df["signal_date"]<pd.Timestamp("2025-01-01"))
        tr=df[trmask].dropna(subset=features).copy()
        te2=te.dropna(subset=features).copy()
        if len(te2)!=len(te): raise RuntimeError(f"DEV missing in {bname} block {start}")
        if len(tr)<500: raise RuntimeError(f"Too little training {bname} {start} {len(tr)}")
        Xtr=tr[features]; Xte=te[features]
        ytr=tr["target_r3"].astype(float)
        yte=te["target_r3"].astype(float).to_numpy()
        uptr=(ytr>0).astype(int); upte=(yte>0).astype(int)

        m=xgb_cls(); m.fit(Xtr,uptr); pp=m.predict_proba(Xte)[:,1]
        r=lgb_reg(); r.fit(Xtr,ytr); rp=r.predict(Xte)
        qpred={}
        for q in [0.1,0.5,0.9]:
            qm=lgb_quant(q); qm.fit(Xtr,ytr); qpred[q]=qm.predict(Xte)

        for k,ix in enumerate(te.index):
            common={
                "row_index":int(ix),"origin_date":str(df.at[ix,"date"].date()),
                "signal_date":str(df.at[ix,"signal_date"].date()),
                "feature_block":bname,"y_return":float(yte[k]),"y_up":int(upte[k]),
                "train_n":int(len(tr)),"block_id":start_i//BLOCK,
                "sigma20":float(df.at[ix,"sigma20"])
            }
            rows.append({**common,"head":"direction","prediction":float(pp[k])})
            rows.append({**common,"head":"return","prediction":float(rp[k])})
            for q in [0.1,0.5,0.9]:
                qrows.append({**common,"quantile":q,"prediction":float(qpred[q][k])})
    return pd.DataFrame(rows),pd.DataFrame(qrows)

def main():
    df=load_panel()
    dev=df[(df["role"]=="DEV") & df["target_r3"].notna()].copy()
    if len(dev)!=749: raise RuntimeError(len(dev))

    # Fixed pre-DEV volatility terciles for diagnostics, avoiding DEV look-ahead.
    hist=df[(df["signal_date"]<pd.Timestamp("2022-01-01")) & df["sigma20"].notna()]
    cuts=hist["sigma20"].quantile([1/3,2/3]).to_numpy()
    def bucket(s):
        return np.where(s<=cuts[0],"LOW",np.where(s<=cuts[1],"MID","HIGH"))
    dev["vol_bucket"]=bucket(dev["sigma20"].to_numpy())

    pred=[]; qp=[]
    avail=[]
    jobs={}
    for b,feats in BLOCKS.items():
        valid_hist=df[(df["signal_date"]<pd.Timestamp("2022-01-01")) & df["target_r3"].notna()].dropna(subset=feats)
        avail.append({
            "feature_block":b,"n_features":len(feats),"predev_complete_rows":len(valid_hist),
            "first_complete_signal":str(valid_hist["signal_date"].min().date()),
            "dev_complete_rows":int(dev[feats].notna().all(axis=1).sum())
        })
    with ThreadPoolExecutor(max_workers=4) as ex:
        for b,feats in BLOCKS.items():
            print("SUBMIT",b,flush=True)
            jobs[ex.submit(run_block,df,dev,b,feats)]=b
        results={}
        for fut in as_completed(jobs):
            b=jobs[fut]
            p,q=fut.result()
            print("COMPLETE_BLOCK",b,flush=True)
            results[b]=(p,q)
    for b in BLOCKS:
        p,q=results[b]
        p=p.merge(dev[["date","vol_bucket"]].rename(columns={"date":"origin_date_dt"}),left_on=pd.to_datetime(p["origin_date"]),right_on="origin_date_dt",how="left")
        q=q.merge(dev[["date","vol_bucket"]].rename(columns={"date":"origin_date_dt"}),left_on=pd.to_datetime(q["origin_date"]),right_on="origin_date_dt",how="left")
        pred.append(p); qp.append(q)

    pred=pd.concat(pred,ignore_index=True)
    qp=pd.concat(qp,ignore_index=True)
    pd.DataFrame(avail).to_csv(OUT/"stage2_feature_availability.csv",index=False)
    pred.to_csv(OUT/"stage2_h3_predictions.csv",index=False)
    qp.to_csv(OUT/"stage2_h3_quantile_predictions.csv",index=False)

    agg=[]; year=[]; vol=[]
    for (b,head),z in pred.groupby(["feature_block","head"]):
        if head=="direction": mm=cls_metrics(z["y_up"],z["prediction"])
        else: mm=reg_metrics(z["y_return"],z["prediction"])
        agg.append({"feature_block":b,"head":head,**mm})
        z2=z.copy(); z2["year"]=pd.to_datetime(z2["signal_date"]).dt.year
        for yr,zz in z2.groupby("year"):
            mm=cls_metrics(zz["y_up"],zz["prediction"]) if head=="direction" else reg_metrics(zz["y_return"],zz["prediction"])
            year.append({"feature_block":b,"head":head,"year":int(yr),**mm})
        for vb,zz in z.groupby("vol_bucket"):
            mm=cls_metrics(zz["y_up"],zz["prediction"]) if head=="direction" else reg_metrics(zz["y_return"],zz["prediction"])
            vol.append({"feature_block":b,"head":head,"vol_bucket":vb,**mm})

    qagg=[]; qyear=[]; qvol=[]
    for (b,q),z in qp.groupby(["feature_block","quantile"]):
        qagg.append({"feature_block":b,"quantile":q,"pinball":pinball(z["y_return"],z["prediction"],q),"coverage":float((z["y_return"]<=z["prediction"]).mean())})
        z2=z.copy(); z2["year"]=pd.to_datetime(z2["signal_date"]).dt.year
        for yr,zz in z2.groupby("year"):
            qyear.append({"feature_block":b,"quantile":q,"year":int(yr),"pinball":pinball(zz["y_return"],zz["prediction"],q),"coverage":float((zz["y_return"]<=zz["prediction"]).mean())})
        for vb,zz in z.groupby("vol_bucket"):
            qvol.append({"feature_block":b,"quantile":q,"vol_bucket":vb,"pinball":pinball(zz["y_return"],zz["prediction"],q),"coverage":float((zz["y_return"]<=zz["prediction"]).mean())})

    agg=pd.DataFrame(agg); year=pd.DataFrame(year); vol=pd.DataFrame(vol)
    qagg=pd.DataFrame(qagg); qyear=pd.DataFrame(qyear); qvol=pd.DataFrame(qvol)
    qsum=qagg.groupby("feature_block",as_index=False)["pinball"].mean().rename(columns={"pinball":"mean_pinball"})
    qys=qyear.groupby(["feature_block","year"],as_index=False)["pinball"].mean().rename(columns={"pinball":"mean_pinball"})
    qvs=qvol.groupby(["feature_block","vol_bucket"],as_index=False)["pinball"].mean().rename(columns={"pinball":"mean_pinball"})

    agg.to_csv(OUT/"stage2_aggregate_metrics.csv",index=False)
    year.to_csv(OUT/"stage2_year_metrics.csv",index=False)
    vol.to_csv(OUT/"stage2_volatility_metrics.csv",index=False)
    qagg.to_csv(OUT/"stage2_quantile_metrics.csv",index=False)
    qsum.to_csv(OUT/"stage2_quantile_summary.csv",index=False)
    qys.to_csv(OUT/"stage2_quantile_year_summary.csv",index=False)
    qvs.to_csv(OUT/"stage2_quantile_volatility_summary.csv",index=False)

    current={"direction":"CORE3","return":"GOLD_ONLY","quantile":"GOLD_ONLY"}
    decisions=[]
    for head in ["direction","return"]:
        z=agg[agg["head"]==head].set_index("feature_block")
        base=z.loc[current[head]]
        primary="brier" if head=="direction" else "mae"
        co="logloss" if head=="direction" else "rmse"
        by=year[year["head"]==head]
        candidates=[]
        for b,row in z.iterrows():
            if b==current[head]: continue
            rel=(base[primary]-row[primary])/base[primary]
            co_ok=row[co]<=base[co]
            year_ok=True; yrrel={}
            for yr in [2022,2023,2024]:
                br=by[(by["feature_block"]==current[head])&(by["year"]==yr)].iloc[0]
                cr=by[(by["feature_block"]==b)&(by["year"]==yr)].iloc[0]
                rr=(br[primary]-cr[primary])/br[primary]
                yrrel[str(yr)]=float(rr)
                if rr < -0.03: year_ok=False
            gate=rel>=0.005 and co_ok and year_ok
            candidates.append((b,float(rel),bool(gate),bool(co_ok),bool(year_ok),yrrel))
        passing=[x for x in candidates if x[2]]
        if passing:
            best=max(passing,key=lambda x:x[1]); selected=best[0]; status="PROMOTE"
        else:
            selected=current[head]; status="RETAIN"
            best=max(candidates,key=lambda x:x[1])
        decisions.append({
            "head":head,"status":status,"current":current[head],"selected":selected,
            "best_challenger":best[0],"best_challenger_rel_improve":best[1],
            "best_challenger_gate":best[2],"best_challenger_year_rel":json.dumps(best[5],sort_keys=True)
        })

    # Quantile head
    z=qsum.set_index("feature_block"); base=z.loc[current["quantile"]]
    candidates=[]
    for b,row in z.iterrows():
        if b==current["quantile"]: continue
        rel=(base["mean_pinball"]-row["mean_pinball"])/base["mean_pinball"]
        year_ok=True; yrrel={}
        for yr in [2022,2023,2024]:
            br=qys[(qys.feature_block==current["quantile"])&(qys.year==yr)].iloc[0]
            cr=qys[(qys.feature_block==b)&(qys.year==yr)].iloc[0]
            rr=(br["mean_pinball"]-cr["mean_pinball"])/br["mean_pinball"]
            yrrel[str(yr)]=float(rr)
            if rr < -0.03: year_ok=False
        gate=rel>=0.005 and year_ok
        candidates.append((b,float(rel),bool(gate),bool(year_ok),yrrel))
    passing=[x for x in candidates if x[2]]
    if passing:
        best=max(passing,key=lambda x:x[1]); selected=best[0]; status="PROMOTE"
    else:
        selected=current["quantile"]; status="RETAIN"; best=max(candidates,key=lambda x:x[1])
    decisions.append({
        "head":"quantile","status":status,"current":current["quantile"],"selected":selected,
        "best_challenger":best[0],"best_challenger_rel_improve":best[1],
        "best_challenger_gate":best[2],"best_challenger_year_rel":json.dumps(best[4],sort_keys=True)
    })

    dec=pd.DataFrame(decisions)
    dec.to_csv(OUT/"stage2_decisions.csv",index=False)

    lines=[
        "# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 2 H3 Robustness & Feature Representation Result","",
        "## Head decisions","",
        "| Head | Decision | Current | Selected | Best challenger | Challenger relative improvement | Gate |",
        "|---|---|---|---|---|---:|---|",
    ]
    for _,r in dec.iterrows():
        lines.append(f"| {r['head']} | {r['status']} | {r['current']} | {r['selected']} | {r['best_challenger']} | {100*r['best_challenger_rel_improve']:.2f}% | {r['best_challenger_gate']} |")

    lines += ["","## Aggregate H3 metrics",""]
    for head in ["direction","return"]:
        lines.append(f"### {head}")
        z=agg[agg["head"]==head]
        metric="brier" if head=="direction" else "mae"
        for _,r in z.sort_values(metric).iterrows():
            lines.append(f"- {r['feature_block']}: {metric}={r[metric]:.6f}")
    lines += ["","### quantile"]
    for _,r in qsum.sort_values("mean_pinball").iterrows():
        lines.append(f"- {r['feature_block']}: mean_pinball={r['mean_pinball']:.6f}")

    (OUT/"STAGE2_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary={
        "status":"PASS",
        "volatility_cutoffs":cuts.tolist(),
        "decisions":dec.to_dict(orient="records"),
        "hashes":{p.name:sha(p) for p in files},
    }
    (OUT/"stage2_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("STAGE2_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)
    print((OUT/"STAGE2_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
