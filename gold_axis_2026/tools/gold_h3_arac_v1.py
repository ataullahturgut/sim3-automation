from __future__ import annotations
import io, json, os, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","gold_h3_arac_v1_out"))
OUT.mkdir(parents=True,exist_ok=True)

SEED=20261001
BLOCK=5
META_N=126
META_HALFLIFE=63.0
META_ETA=30.0
ANALOG_K=75
ANALOG_PSEUDO=20.0
REGIME_PSEUDO=25.0

CORE3=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]
EXPERTS=["GLOBAL_EN","RECENT504_BAL_LOGIT","LOCAL_ANALOG","REGIME_PRIOR"]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(
        u,
        headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"arac-h3-v1"},
        timeout=120,
    )
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
    if len(names)!=1:
        raise RuntimeError(names)
    df=pd.read_csv(io.BytesIO(z.read(names[0])))
    for c in ["date","feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
    df=df.sort_values("feature_cutoff_date").reset_index(drop=True)
    return df

def fill_xy(tr,te):
    a=tr[CORE3].copy()
    b=te[CORE3].copy()
    med={}
    for c in CORE3:
        a[c]=pd.to_numeric(a[c],errors="coerce")
        b[c]=pd.to_numeric(b[c],errors="coerce")
        m=a[c].median(skipna=True)
        v=float(m) if pd.notna(m) else 0.0
        med[c]=v
        a[c]=a[c].fillna(v)
        b[c]=b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float), med

def global_en():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=0.30,penalty="elasticnet",l1_ratio=0.50,solver="saga",
            max_iter=5000,tol=1e-4,random_state=SEED
        ))
    ])

def l2_model(class_weight=None):
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,solver="lbfgs",max_iter=3000,class_weight=class_weight,random_state=SEED
        ))
    ])

def prob_global_en(tr,te):
    Xtr,Xte,_=fill_xy(tr,te)
    y=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
    m=global_en(); m.fit(Xtr,y)
    return m.predict_proba(Xte)[:,1]

def prob_recent504(tr,te):
    rr=tr.tail(504).copy()
    Xtr,Xte,_=fill_xy(rr,te)
    y=(rr.target_r3.astype(float)>0).astype(int).to_numpy()
    m=l2_model(class_weight="balanced"); m.fit(Xtr,y)
    return m.predict_proba(Xte)[:,1]

def standardized_train_test(tr,te):
    a=tr[CORE3].copy()
    b=te[CORE3].copy()
    for c in CORE3:
        a[c]=pd.to_numeric(a[c],errors="coerce")
        b[c]=pd.to_numeric(b[c],errors="coerce")
        med=a[c].median(skipna=True)
        med=float(med) if pd.notna(med) else 0.0
        a[c]=a[c].fillna(med)
        b[c]=b[c].fillna(med)
    mu=a.mean(axis=0).to_numpy(float)
    sd=a.std(axis=0,ddof=0).to_numpy(float)
    sd=np.where(np.isfinite(sd)&(sd>1e-12),sd,1.0)
    A=(a.to_numpy(float)-mu)/sd
    B=(b.to_numpy(float)-mu)/sd
    return A,B

def prob_local_analog(tr,te):
    A,B=standardized_train_test(tr,te)
    y=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
    prior=float(y.mean())
    out=[]
    k=min(ANALOG_K,len(tr))
    for x in B:
        d=np.sqrt(np.mean((A-x)**2,axis=1))
        idx=np.argpartition(d,k-1)[:k]
        dd=d[idx]
        scale=float(np.median(dd[dd>0])) if np.any(dd>0) else 1.0
        if not np.isfinite(scale) or scale<=1e-12:
            scale=1.0
        w=np.exp(-dd/scale)
        local=float(np.sum(w*y[idx])/np.sum(w)) if np.sum(w)>0 else prior
        eff=float(np.sum(w))
        p=(eff*local + ANALOG_PSEUDO*prior)/(eff+ANALOG_PSEUDO)
        out.append(float(p))
    return np.array(out,float)

def regime_labels(tr,te):
    sig=pd.to_numeric(tr["sigma20"],errors="coerce")
    q1=float(sig.quantile(1/3)); q2=float(sig.quantile(2/3))
    def label_df(x):
        s=pd.to_numeric(x["sigma20"],errors="coerce").fillna(float(sig.median()))
        vol=np.where(s<=q1,"LOW",np.where(s<=q2,"MID","HIGH"))
        gt=np.where(pd.to_numeric(x["gold_r21"],errors="coerce").fillna(0.0)>0,"UP_TREND","DOWN_TREND")
        breadth=np.where(
            pd.to_numeric(x["silver_r21"],errors="coerce").fillna(0.0)+
            pd.to_numeric(x["platinum_r21"],errors="coerce").fillna(0.0)>0,
            "POS","NEG"
        )
        return np.array([f"{a}|{b}|{c}" for a,b,c in zip(vol,gt,breadth)],dtype=object)
    return label_df(tr),label_df(te)

def prob_regime_prior(tr,te):
    y=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
    prior=float(y.mean())
    rtr,rte=regime_labels(tr,te)
    out=[]
    for reg in rte:
        m=(rtr==reg)
        n=int(m.sum())
        s=float(y[m].sum()) if n else 0.0
        p=(s+REGIME_PSEUDO*prior)/(n+REGIME_PSEUDO)
        out.append(float(p))
    return np.array(out,float)

def expert_probs(tr,te):
    return {
        "GLOBAL_EN":prob_global_en(tr,te),
        "RECENT504_BAL_LOGIT":prob_recent504(tr,te),
        "LOCAL_ANALOG":prob_local_analog(tr,te),
        "REGIME_PRIOR":prob_regime_prior(tr,te),
    }

def meta_weights(history,cutoff):
    if not history:
        return {e:1/len(EXPERTS) for e in EXPERTS}
    h=pd.DataFrame(history)
    h["target_end_date_h3"]=pd.to_datetime(h["target_end_date_h3"])
    h=h[h.target_end_date_h3<=cutoff].copy()
    if len(h)<40:
        return {e:1/len(EXPERTS) for e in EXPERTS}
    h=h.tail(META_N).reset_index(drop=True)
    age=np.arange(len(h)-1,-1,-1,dtype=float)
    rec=np.exp(-np.log(2.0)*age/META_HALFLIFE)
    vals={}
    y=h.y_up.to_numpy(float)
    for e in EXPERTS:
        p=h[f"p_{e}"].to_numpy(float)
        loss=(p-y)**2
        ew=float(np.sum(rec*loss)/np.sum(rec))
        vals[e]=float(np.exp(-META_ETA*ew))
    s=sum(vals.values())
    if not np.isfinite(s) or s<=0:
        return {e:1/len(EXPERTS) for e in EXPERTS}
    return {e:v/s for e,v in vals.items()}

def basic_metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
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
        "tn":tn,"fp":fp,"fn":fn,"tp":tp,
    }

def selective_metrics(g,threshold):
    mask=g.reliability_score.to_numpy(float)>=float(threshold)
    if mask.sum()==0:
        return {"n_calls":0,"coverage":0.0}
    y=g.y_up.to_numpy(int)[mask]
    p=g.p_ARAC.to_numpy(float)[mask]
    m=basic_metrics(y,p)
    return {"n_calls":int(mask.sum()),"coverage":float(mask.mean()),**m}

def run_sequence(df,start_year,end_year):
    test=df[
        df.forecast_issue_date.dt.year.between(start_year,end_year) &
        df.target_r3.notna()
    ].copy().reset_index(drop=True)
    history=[]
    rows=[]
    for bs in range(0,len(test),BLOCK):
        te=test.iloc[bs:bs+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=cutoff)
        ].copy()
        if len(tr)<1000:
            raise RuntimeError(f"TRAIN_TOO_SMALL {len(tr)} at {cutoff}")
        probs=expert_probs(tr,te)
        w=meta_weights(history,cutoff)
        final=np.zeros(len(te),float)
        for e in EXPERTS:
            final+=w[e]*probs[e]
        dirs=np.vstack([(probs[e]>=0.5).astype(int) for e in EXPERTS]).T
        fdir=(final>=0.5).astype(int)
        agreement=np.mean(dirs==fdir[:,None],axis=1)
        reliability=agreement*np.abs(final-0.5)

        # Comparators using same training rows.
        Xtr,Xte,_=fill_xy(tr,te)
        ytr=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
        l2=l2_model(); l2.fit(Xtr,ytr)
        p_l2=l2.predict_proba(Xte)[:,1]
        en=global_en(); en.fit(Xtr,ytr)
        p_en=en.predict_proba(Xte)[:,1]
        p_prior=float(ytr.mean())

        yte=(te.target_r3.astype(float)>0).astype(int).to_numpy()
        for j,(r,yy) in enumerate(zip(te.itertuples(),yte)):
            rec={
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "target_end_date_h3":str(r.target_end_date_h3.date()),
                "year":int(r.forecast_issue_date.year),
                "y_up":int(yy),
                "p_ARAC":float(final[j]),
                "agreement_fraction":float(agreement[j]),
                "reliability_score":float(reliability[j]),
                "p_CORE3_LOGIT_L2":float(p_l2[j]),
                "p_CORE3_LOGIT_EN":float(p_en[j]),
                "p_EXPANDING_PRIOR":float(p_prior),
                "w_GLOBAL_EN":float(w["GLOBAL_EN"]),
                "w_RECENT504_BAL_LOGIT":float(w["RECENT504_BAL_LOGIT"]),
                "w_LOCAL_ANALOG":float(w["LOCAL_ANALOG"]),
                "w_REGIME_PRIOR":float(w["REGIME_PRIOR"]),
            }
            for e in EXPERTS:
                rec[f"p_{e}"]=float(probs[e][j])
            rows.append(rec)
            history.append(rec.copy())
    return pd.DataFrame(rows)

def choose_reliability_threshold(dev):
    cand=[]
    scores=dev.reliability_score.to_numpy(float)
    for nominal in [0.70,0.60,0.50,0.40,0.30]:
        thr=float(np.quantile(scores,1.0-nominal))
        m=selective_metrics(dev,thr)
        if m.get("n_calls",0)>=120 and m.get("coverage",0)>=0.30:
            cand.append({"nominal_coverage":nominal,"threshold":thr,**m})
    if not cand:
        raise RuntimeError("NO_RELIABILITY_CANDIDATE")
    c=pd.DataFrame(cand)
    c=c.sort_values(
        ["balanced_accuracy","accuracy","false_call_rate","coverage"],
        ascending=[False,False,True,False]
    ).reset_index(drop=True)
    return c.iloc[0].to_dict(),c

def summarize_period(g,label,threshold):
    rows=[]
    models=["ARAC","CORE3_LOGIT_L2","CORE3_LOGIT_EN","EXPANDING_PRIOR"]
    cols={
        "ARAC":"p_ARAC",
        "CORE3_LOGIT_L2":"p_CORE3_LOGIT_L2",
        "CORE3_LOGIT_EN":"p_CORE3_LOGIT_EN",
        "EXPANDING_PRIOR":"p_EXPANDING_PRIOR",
    }
    for m in models:
        rows.append({"period":label,"scope":"FULL","model":m,**basic_metrics(g.y_up,g[cols[m]])})
    sm=selective_metrics(g,threshold)
    rows.append({"period":label,"scope":"SELECTIVE","model":"ARAC",**sm})
    return rows

def main():
    df=load_panel()

    # One continuous chronological sequence so 2022+ weights can use matured prior ARAC performance.
    all_oos=run_sequence(df,2019,2024)
    dev=all_oos[all_oos.year.between(2019,2021)].copy()
    conf=all_oos[all_oos.year.between(2022,2024)].copy()

    chosen,candidates=choose_reliability_threshold(dev)
    candidates.to_csv(OUT/"arac_v1_reliability_candidates_2019_2021.csv",index=False)

    summary=[]
    summary+=summarize_period(dev,"DEV_2019_2021",chosen["threshold"])
    summary+=summarize_period(conf,"CONFIRM_2022_2024",chosen["threshold"])
    for yr in [2019,2020,2021,2022,2023,2024]:
        g=all_oos[all_oos.year==yr]
        summary+=summarize_period(g,str(yr),chosen["threshold"])
    sdf=pd.DataFrame(summary)
    sdf.to_csv(OUT/"arac_v1_metrics.csv",index=False)
    all_oos.to_csv(OUT/"arac_v1_predictions.csv",index=False)

    # Weight diagnostics.
    weight_cols=["year","w_GLOBAL_EN","w_RECENT504_BAL_LOGIT","w_LOCAL_ANALOG","w_REGIME_PRIOR"]
    wdf=all_oos[weight_cols].groupby("year",as_index=False).mean()
    wdf.to_csv(OUT/"arac_v1_mean_weights_by_year.csv",index=False)

    result={
        "schema":"GOLD_H3_ARAC_V1",
        "model":"Adaptive Regime-Analog Consensus",
        "development":"2019-2021",
        "confirmation":"2022-2024",
        "chosen_reliability_rule":chosen,
        "metrics":sdf.to_dict(orient="records"),
        "mean_weights_by_year":wdf.to_dict(orient="records"),
    }
    (OUT/"arac_v1_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD H3 — ARAC-H3-v1 RESULT","",
        "Adaptive Regime-Analog Consensus: global Elastic-Net + recent balanced Logistic + local analog + regime prior, with online Brier weighting.","",
        f"Frozen reliability threshold from 2019-2021: **{chosen['threshold']:.6f}** "
        f"(development coverage {100*chosen['coverage']:.2f}%).","",
        "## Full coverage","",
        "| Period | Model | N | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for per in ["DEV_2019_2021","CONFIRM_2022_2024"]:
        for m in ["EXPANDING_PRIOR","CORE3_LOGIT_L2","CORE3_LOGIT_EN","ARAC"]:
            r=sdf[(sdf.period==per)&(sdf.scope=="FULL")&(sdf.model==m)].iloc[0]
            lines.append(
                f"| {per} | {m} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {100*r.false_call_rate:.2f}% | "
                f"{r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )
    lines += ["","## ARAC selective calls using the development-frozen reliability rule","",
              "| Period | Calls | Coverage | Accuracy | Balanced acc | False calls | UP recall | DOWN recall |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for per in ["DEV_2019_2021","CONFIRM_2022_2024","2022","2023","2024"]:
        r=sdf[(sdf.period==per)&(sdf.scope=="SELECTIVE")&(sdf.model=="ARAC")].iloc[0]
        lines.append(
            f"| {per} | {int(r.n_calls)} | {100*r.coverage:.2f}% | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {100*r.false_call_rate:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    lines += ["","## Annual full-coverage ARAC","",
              "| Year | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
              "|---:|---:|---:|---:|---:|---:|"]
    for yr in [2019,2020,2021,2022,2023,2024]:
        r=sdf[(sdf.period==str(yr))&(sdf.scope=="FULL")&(sdf.model=="ARAC")].iloc[0]
        lines.append(
            f"| {yr} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{r.brier:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    lines += ["","2022-2024 is confirmation inside already-opened project history, not a pristine blind lockbox."]
    (OUT/"ARAC_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"ARAC_V1_RESULT.md").read_text())

if __name__=="__main__":
    main()
