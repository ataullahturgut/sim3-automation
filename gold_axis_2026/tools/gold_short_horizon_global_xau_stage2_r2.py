import os,io,json,math,hashlib,zipfile,warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, balanced_accuracy_score

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_r2_stage2_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
BLOCK=5

GOLD_ONLY=["gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20"]
CORE3=GOLD_ONLY+[
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
]
CORE4=CORE3+["palladium_r1","palladium_r5","palladium_r21","palladium_age_days"]
RAW_EXT=[
    "DGS10","DFII10","BREAKEVEN10_PROXY",
    "BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD",
    "VIX","NDX"
]
RATE_EXT=["DGS10","DFII10","BREAKEVEN10_PROXY"]
LOG_EXT=["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD","VIX","NDX"]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-stage2"},timeout=120)
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
    df=read_csv(z,"global_xau_r2_readiness_panel.csv")
    for c in ["date","feature_cutoff_date","forecast_issue_date","target_start_date","target_end_date_h1","target_end_date_h3","target_end_date_h5"]:
        df[c]=pd.to_datetime(df[c])
    df=df.sort_values("date").reset_index(drop=True)
    # Frozen transformed-external representation.
    for c in RATE_EXT:
        df[f"{c}_d5"]=pd.to_numeric(df[c],errors="coerce").diff(5)
    for c in LOG_EXT:
        x=pd.to_numeric(df[c],errors="coerce")
        df[f"{c}_lr5"]=np.log(x.where(x>0)).diff(5)
    return df

CHG_EXT=[f"{c}_d5" for c in RATE_EXT]+[f"{c}_lr5" for c in LOG_EXT]
BLOCKS={
    "GOLD_ONLY":GOLD_ONLY,
    "CORE3":CORE3,
    "CORE4":CORE4,
    "CORE3_SAFE_EXTERNAL_RAW":CORE3+RAW_EXT,
    "CORE3_SAFE_EXTERNAL_CHG":CORE3+CHG_EXT,
}

def mature_mask(df,start,h):
    maturity=df[f"target_end_date_h{h}"]
    return maturity.notna() & (maturity<=start) & (df["forecast_issue_date"]<pd.Timestamp("2025-01-01"))

def fill_train_test(train,test,features):
    a=train[features].copy(); b=test[features].copy()
    for c in features:
        med=pd.to_numeric(a[c],errors="coerce").median(skipna=True)
        val=float(med) if pd.notna(med) else 0.0
        a[c]=pd.to_numeric(a[c],errors="coerce").fillna(val)
        b[c]=pd.to_numeric(b[c],errors="coerce").fillna(val)
    return a,b

def fit_logit(X,y):
    m=Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED))
    ])
    m.fit(X,y)
    return m

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "prediction_std":float(np.std(p)),
    }

def run_horizon(df,horizon, reps, collect_coef=False):
    target=f"target_r{horizon}"
    dev=df[(df.role=="DEV") & df[target].notna()].copy()
    preds=[]
    coef_rows=[]
    for block_start in range(0,len(dev),BLOCK):
        te=dev.iloc[block_start:block_start+BLOCK].copy()
        start=te.feature_cutoff_date.min()
        mm=mature_mask(df,start,horizon) & df[target].notna()
        tr=df[mm].copy()
        if len(tr)<252: raise RuntimeError(f"H{horizon} insufficient train {len(tr)}")

        ytr=(tr[target].astype(float)>0).astype(int)
        yte=(te[target].astype(float)>0).astype(int)
        p_exp=float(ytr.mean()); p_roll=float(ytr.iloc[-252:].mean())

        for ix,yu in zip(te.index,yte):
            common={
                "horizon":horizon,"row_index":int(ix),"feature_cutoff_date":str(df.at[ix,"feature_cutoff_date"].date()),
                "forecast_issue_date":str(df.at[ix,"forecast_issue_date"].date()),
                "target_end_date":str(df.at[ix,f"target_end_date_h{horizon}"].date()),"y_up":int(yu),
                "sigma20":float(df.at[ix,"sigma20"]) if pd.notna(df.at[ix,"sigma20"]) else None,
                "block_id":block_start//BLOCK,"train_n":int(len(tr))
            }
            preds.append({**common,"representation":"BASE","model":"EXPAND_PREV","prediction":p_exp})
            preds.append({**common,"representation":"BASE","model":"ROLL252_PREV","prediction":p_roll})

        for rep in reps:
            feats=BLOCKS[rep]
            Xtr,Xte=fill_train_test(tr,te,feats)
            m=fit_logit(Xtr,ytr)
            pp=m.predict_proba(Xte)[:,1]
            for ix,yu,pv in zip(te.index,yte,pp):
                preds.append({
                    "horizon":horizon,"row_index":int(ix),"feature_cutoff_date":str(df.at[ix,"feature_cutoff_date"].date()),
                    "forecast_issue_date":str(df.at[ix,"forecast_issue_date"].date()),
                    "target_end_date":str(df.at[ix,f"target_end_date_h{horizon}"].date()),"y_up":int(yu),
                    "sigma20":float(df.at[ix,"sigma20"]) if pd.notna(df.at[ix,"sigma20"]) else None,
                    "block_id":block_start//BLOCK,"train_n":int(len(tr)),
                    "representation":rep,"model":"LOGIT_L2","prediction":float(pv)
                })
            if collect_coef and rep=="CORE3":
                coefs=m.named_steps["model"].coef_[0]
                for f,v in zip(feats,coefs):
                    coef_rows.append({
                        "block_id":block_start//BLOCK,"test_start":str(start.date()),"train_n":int(len(tr)),
                        "feature":f,"coef_std":float(v)
                    })
    return pd.DataFrame(preds),pd.DataFrame(coef_rows)

def baseline_choice(pred):
    base=pred[pred.representation=="BASE"].copy()
    rows=[]
    for model,z in base.groupby("model"):
        mm=metrics(z.y_up,z.prediction)
        rows.append({"model":model,**mm})
    b=pd.DataFrame(rows).sort_values(["brier","logloss"]).reset_index(drop=True)
    return str(b.iloc[0].model),b

def slice_compare(pred,rep,baseline_model,mask=None):
    z=pred.copy()
    if mask is not None:
        idx=set(mask)
        z=z[z.row_index.isin(idx)]
    m=z[(z.representation==rep)&(z.model=="LOGIT_L2")].sort_values("row_index")
    b=z[(z.representation=="BASE")&(z.model==baseline_model)].sort_values("row_index")
    if len(m)!=len(b) or len(m)==0:
        raise RuntimeError((rep,baseline_model,len(m),len(b)))
    mm=metrics(m.y_up,m.prediction); bb=metrics(b.y_up,b.prediction)
    rel=(bb["brier"]-mm["brier"])/bb["brier"]
    return {**mm,
            "baseline_brier":bb["brier"],"baseline_logloss":bb["logloss"],
            "relative_brier_improvement":float(rel)}

def main():
    df=load_panel()

    # H3 all representations.
    h3,coef=run_horizon(df,3,list(BLOCKS),collect_coef=True)
    h3.to_csv(OUT/"global_xau_r2_stage2_h3_predictions.csv",index=False)
    coef.to_csv(OUT/"global_xau_r2_stage2_h3_core3_coefficients.csv",index=False)

    baseline_model,btable=baseline_choice(h3)
    btable.to_csv(OUT/"global_xau_r2_stage2_h3_baselines.csv",index=False)

    agg=[]
    for rep in BLOCKS:
        r=slice_compare(h3,rep,baseline_model)
        agg.append({"representation":rep,"baseline_model":baseline_model,**r})
    adf=pd.DataFrame(agg)
    adf.to_csv(OUT/"global_xau_r2_stage2_h3_aggregate.csv",index=False)

    # Annual.
    h3["year"]=pd.to_datetime(h3.forecast_issue_date).dt.year
    yrows=[]
    for rep in BLOCKS:
        for yr in [2022,2023,2024]:
            rows=h3[(h3.representation==rep)&(h3.model=="LOGIT_L2")&(h3.year==yr)].row_index.unique()
            r=slice_compare(h3,rep,baseline_model,rows)
            yrows.append({"representation":rep,"year":yr,**r})
    ydf=pd.DataFrame(yrows)
    ydf.to_csv(OUT/"global_xau_r2_stage2_h3_years.csv",index=False)

    # Volatility terciles using one row per origin.
    orig=h3[(h3.representation=="CORE3")&(h3.model=="LOGIT_L2")][["row_index","sigma20"]].drop_duplicates("row_index")
    orig["vol_bucket"]=pd.qcut(orig.sigma20.rank(method="first"),3,labels=["LOW","MID","HIGH"])
    vrows=[]
    for rep in BLOCKS:
        for vb in ["LOW","MID","HIGH"]:
            rows=orig[orig.vol_bucket==vb].row_index.tolist()
            r=slice_compare(h3,rep,baseline_model,rows)
            vrows.append({"representation":rep,"vol_bucket":vb,**r})
    vdf=pd.DataFrame(vrows)
    vdf.to_csv(OUT/"global_xau_r2_stage2_h3_volatility.csv",index=False)

    # Coefficient stability.
    cs=[]
    for f,z in coef.groupby("feature"):
        pos=float((z.coef_std>0).mean()); neg=float((z.coef_std<0).mean())
        sc=max(pos,neg)
        cs.append({
            "feature":f,"n_refits":int(len(z)),
            "mean_coef":float(z.coef_std.mean()),"median_coef":float(z.coef_std.median()),
            "coef_sd":float(z.coef_std.std(ddof=0)),
            "positive_share":pos,"negative_share":neg,"sign_consistency":sc,
            "median_abs_coef":float(z.coef_std.abs().median()),
            "stability_flag":"STABLE_DIRECTIONAL" if sc>=0.80 else "UNSTABLE"
        })
    cdf=pd.DataFrame(cs).sort_values("median_abs_coef",ascending=False)
    cdf.to_csv(OUT/"global_xau_r2_stage2_h3_coefficient_stability.csv",index=False)

    # H5 secondary CORE3 only.
    h5,_=run_horizon(df,5,["CORE3"],collect_coef=False)
    h5base,h5bt=baseline_choice(h5)
    h5agg=slice_compare(h5,"CORE3",h5base)
    h5["year"]=pd.to_datetime(h5.forecast_issue_date).dt.year
    h5years=[]
    for yr in [2022,2023,2024]:
        rows=h5[(h5.representation=="CORE3")&(h5.model=="LOGIT_L2")&(h5.year==yr)].row_index.unique()
        h5years.append({"year":yr,**slice_compare(h5,"CORE3",h5base,rows)})
    pd.DataFrame([{"baseline_model":h5base,**h5agg}]).to_csv(OUT/"global_xau_r2_stage2_h5_secondary.csv",index=False)
    pd.DataFrame(h5years).to_csv(OUT/"global_xau_r2_stage2_h5_years.csv",index=False)

    core=adf[adf.representation=="CORE3"].iloc[0]
    coreyrs=ydf[ydf.representation=="CORE3"]
    positive_years=int((coreyrs.relative_brier_improvement>0).sum())
    worst_year=float(coreyrs.relative_brier_improvement.min())
    year_n_ok=bool((coreyrs.n>=200).all())
    robust=bool(
        core.relative_brier_improvement>=0.01 and
        core.logloss<=core.baseline_logloss and
        core.prediction_std>=0.02 and
        positive_years>=2 and
        worst_year>=-0.03 and
        year_n_ok
    )

    # Representation replacement gate.
    core_rel=float(core.relative_brier_improvement)
    rep_decisions=[]
    for _,r in adf.iterrows():
        yrs=ydf[ydf.representation==r.representation]
        ann_ok=(int((yrs.relative_brier_improvement>0).sum())>=2 and float(yrs.relative_brier_improvement.min())>=-0.03 and bool((yrs.n>=200).all()))
        promote=bool(
            r.representation!="CORE3" and
            float(r.relative_brier_improvement)>=core_rel+0.005 and
            ann_ok and
            float(r.logloss)<=float(core.logloss) and
            float(r.prediction_std)>=0.02
        )
        rep_decisions.append({"representation":r.representation,"promote_over_core3":promote,"annual_guard_pass":bool(ann_ok)})
    rdf=pd.DataFrame(rep_decisions)
    rdf.to_csv(OUT/"global_xau_r2_stage2_representation_decisions.csv",index=False)
    promoted=rdf[rdf.promote_over_core3]
    final_rep="CORE3" if promoted.empty else str(
        adf[adf.representation.isin(promoted.representation)].sort_values(["brier","logloss"]).iloc[0].representation
    )

    h5_secondary=bool(h5agg["relative_brier_improvement"]>=0.01)
    status="ROBUST_PASS" if robust else "FRAGILE_NO_PROMOTION"

    lines=[
        "# GOLD SHORT-HORIZON GLOBAL XAU R2 — Stage 2 H3 Direction Robustness Result","",
        f"**Status:** **{status}**","",
        f"Binding baseline: **{baseline_model}**","",
        "## H3 aggregate representations","",
        "| Representation | Brier | Baseline | Rel improvement | Logloss | Pred SD |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for _,r in adf.iterrows():
        lines.append(f"| {r.representation} | {r.brier:.6f} | {r.baseline_brier:.6f} | {100*r.relative_brier_improvement:.2f}% | {r.logloss:.6f} | {r.prediction_std:.4f} |")
    lines += ["","## CORE3 annual robustness","",
              "| Year | N | Brier | Baseline | Rel improvement |",
              "|---|---:|---:|---:|---:|"]
    for _,r in coreyrs.iterrows():
        lines.append(f"| {int(r.year)} | {int(r.n)} | {r.brier:.6f} | {r.baseline_brier:.6f} | {100*r.relative_brier_improvement:.2f}% |")
    lines += ["","## Binding decision",
              f"- CORE3 robust: **{robust}**",
              f"- final representation: **{final_rep}**",
              f"- H5 secondary >=1% gate: **{h5_secondary}**",
              f"- positive CORE3 years: {positive_years}/3",
              f"- worst CORE3 annual relative Brier improvement: {100*worst_year:.2f}%."]

    (OUT/"STAGE2_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary={
        "status":status,"baseline_model":baseline_model,"robust_pass":robust,
        "final_representation":final_rep,"positive_years":positive_years,"worst_year_rel_improve":worst_year,
        "h5_secondary_pass":h5_secondary,
        "core3_aggregate":core.to_dict(),
        "core3_years":coreyrs.to_dict(orient="records"),
        "representations":adf.to_dict(orient="records"),
        "hashes":{p.name:sha(p) for p in files}
    }
    (OUT/"stage2_summary.json").write_text(json.dumps(summary,indent=2,default=str),encoding="utf-8")
    print("GLOBAL_XAU_R2_STAGE2_SUMMARY="+json.dumps(summary,separators=(",",":"),default=str),flush=True)
    print((OUT/"STAGE2_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
