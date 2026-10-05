from __future__ import annotations
import json, hashlib, urllib.request
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, balanced_accuracy_score, recall_score

OUT=Path("silver_axis_2026/SILVER_SHORT_HORIZON_V2_OUT")
OUT.mkdir(parents=True,exist_ok=True)

STAK_REF="54fdf1c8d39b7b6c7b874d0f30f784296e886044"
SEED=20261005
BLOCK=5
HORIZONS=[1,3,5]

SILVER_PATH=[
    "silver_r1","silver_r3","silver_r5","silver_r10","silver_r21","silver_sigma20"
]
RELATIVE_VALUE=SILVER_PATH+[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21",
    "sg_spread_r1","sg_spread_r3","sg_spread_r5","sg_spread_r10","sg_spread_r21",
    "gsr_z20","gsr_z60","gsr_chg1","gsr_chg5","gsr_chg21"
]
METAL_STATE=RELATIVE_VALUE+[
    "platinum_r1","platinum_r5","platinum_r21",
    "palladium_r1","palladium_r5","palladium_r21",
    "breadth_r1","breadth_r5","breadth_r21",
    "dispersion_r1","dispersion_r5","dispersion_r21",
    "silver_ind_spread_r1","silver_ind_spread_r5","silver_ind_spread_r21"
]
FEATURE_BLOCKS={"SILVER_PATH":SILVER_PATH,"RELATIVE_VALUE":RELATIVE_VALUE,"METAL_STATE":METAL_STATE}
MODELS=["LOGIT_L2","HGB"]

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"silver-relative-v2/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def load_metals():
    wanted={"Silver":"silver","Gold":"gold","Platinum":"platinum","Palladium":"palladium"}
    by=defaultdict(dict); hashes={}
    for year in range(2010,2027):
        raw=get_bytes(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{STAK_REF}/data/spot-history-{year}.json")
        hashes[str(year)]=hashlib.sha256(raw).hexdigest()
        for r in json.loads(raw):
            metal=str(r.get("metal") or "")
            if metal not in wanted: continue
            ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
            if pd.isna(ts): continue
            d=ts.normalize()
            if d.weekday()>=5: continue
            try: v=float(r.get("spot"))
            except Exception: continue
            if np.isfinite(v) and v>0: by[metal][d]=v
    common=sorted(set.intersection(*(set(by[m]) for m in wanted)))
    df=pd.DataFrame({"date":common})
    for metal,key in wanted.items(): df[key]=[by[metal][d] for d in common]
    return df,hashes

def zscore(s,w):
    mu=s.rolling(w).mean(); sd=s.rolling(w).std(ddof=0)
    return (s-mu)/sd.replace(0,np.nan)

def build_panel():
    df,hashes=load_metals()
    df=df.sort_values("date").reset_index(drop=True)
    df["feature_cutoff_date"]=df.date
    df["forecast_issue_date"]=df.date.shift(-1)

    logs={m:np.log(df[m]) for m in ["silver","gold","platinum","palladium"]}
    for h in HORIZONS:
        df[f"target_end_date_h{h}"]=df.date.shift(-h)
        df[f"target_r{h}"]=np.log(df.silver.shift(-h)/df.silver)

    for h in [1,3,5,10,21]:
        df[f"silver_r{h}"]=logs["silver"].diff(h)
        df[f"gold_r{h}"]=logs["gold"].diff(h)
        df[f"sg_spread_r{h}"]=df[f"silver_r{h}"]-df[f"gold_r{h}"]
    df["silver_sigma20"]=logs["silver"].diff().rolling(20).std(ddof=0)

    gsr=logs["gold"]-logs["silver"]
    df["gsr_z20"]=zscore(gsr,20)
    df["gsr_z60"]=zscore(gsr,60)
    for h in [1,5,21]: df[f"gsr_chg{h}"]=gsr.diff(h)

    for m in ["platinum","palladium"]:
        for h in [1,5,21]: df[f"{m}_r{h}"]=logs[m].diff(h)

    for h in [1,5,21]:
        cols=[f"{m}_r{h}" for m in ["silver","gold","platinum","palladium"]]
        vals=df[cols]
        df[f"breadth_r{h}"]=(vals>0).mean(axis=1)
        df[f"dispersion_r{h}"]=vals.std(axis=1,ddof=0)
        ind=(df[f"platinum_r{h}"]+df[f"palladium_r{h}"])/2.0
        df[f"silver_ind_spread_r{h}"]=df[f"silver_r{h}"]-ind

    df=df[df.forecast_issue_date.notna()].copy().reset_index(drop=True)
    df["role"]=np.select(
        [
            df.forecast_issue_date.dt.year<=2021,
            df.forecast_issue_date.dt.year.between(2022,2024),
            df.forecast_issue_date.dt.year==2025,
            df.forecast_issue_date.dt.year==2026,
        ],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025","OPENED_2026"],
        default="OTHER"
    )
    return df,hashes

def make_model(name):
    if name=="LOGIT_L2":
        return Pipeline([
            ("scale",StandardScaler()),
            ("model",LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",max_iter=3000,random_state=SEED))
        ])
    if name=="HGB":
        return HistGradientBoostingClassifier(
            learning_rate=0.05,max_iter=150,max_depth=3,min_samples_leaf=30,
            l2_regularization=1.0,random_state=SEED
        )
    raise KeyError(name)

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "actual_up_rate":float(np.mean(y)),
        "pred_up_rate":float(np.mean(pred)),
        "prediction_std":float(np.std(p))
    }

def mature_train(df,start,h,features,pre2025_only=False):
    t=f"target_r{h}"
    m=df[f"target_end_date_h{h}"].notna()&(df[f"target_end_date_h{h}"]<=start)&df[t].notna()
    if pre2025_only: m &= df.forecast_issue_date<pd.Timestamp("2025-01-01")
    q=df.loc[m].copy()
    return q[q[features].notna().all(axis=1)].copy()

def dev_predictions(df,h,b,features,mname):
    t=f"target_r{h}"
    dev=df[(df.role=="DEV")&df[t].notna()].copy()
    dev=dev[dev[features].notna().all(axis=1)].reset_index(drop=True)
    rows=[]
    for bs in range(0,len(dev),BLOCK):
        te=dev.iloc[bs:bs+BLOCK].copy(); start=te.feature_cutoff_date.min()
        tr=mature_train(df,start,h,features,pre2025_only=True)
        if len(tr)<500: raise RuntimeError(f"train too small {h} {b} {mname} {len(tr)}")
        model=make_model(mname)
        model.fit(tr[features].to_numpy(float),(tr[t].to_numpy(float)>0).astype(int))
        pp=model.predict_proba(te[features].to_numpy(float))[:,1]
        for r,p in zip(te.itertuples(),pp):
            rows.append({
                "horizon":h,"feature_block":b,"model":mname,
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "year":int(r.forecast_issue_date.year),
                "y_up":int(getattr(r,t)>0),"p_up":float(p),"train_n":int(len(tr))
            })
    return pd.DataFrame(rows)

def choose(met):
    agg=met[(met.period=="2022-2024")&(met.balanced_accuracy>0.5)].copy()
    if agg.empty: return None
    best=float(agg.brier.min())
    c=agg[agg.brier<=best+0.002].copy()
    c=c.sort_values(["balanced_accuracy","accuracy","brier"],ascending=[False,False,True]).reset_index(drop=True)
    r=c.iloc[0].to_dict()
    annual=met[(met.horizon==r["horizon"])&(met.feature_block==r["feature_block"])&(met.model==r["model"])&met.period.isin(["2022","2023","2024"])]
    r["dev_years_ba_below_50"]=int((annual.balanced_accuracy<0.5).sum())
    r["annual_stable"]=bool(r["dev_years_ba_below_50"]<=1)
    return r

def transport(df,h,features,mname,year,adaptive):
    t=f"target_r{h}"
    test=df[(df.forecast_issue_date.dt.year==year)&df[t].notna()].copy()
    test=test[test[features].notna().all(axis=1)].reset_index(drop=True)
    rows=[]
    if not adaptive:
        tr=df[
            (df.forecast_issue_date<pd.Timestamp("2025-01-01"))&
            df[t].notna()&df[f"target_end_date_h{h}"].notna()&
            (df[f"target_end_date_h{h}"]<=pd.Timestamp("2024-12-31"))
        ].copy()
        tr=tr[tr[features].notna().all(axis=1)]
        m=make_model(mname);m.fit(tr[features].to_numpy(float),(tr[t].to_numpy(float)>0).astype(int))
        pp=m.predict_proba(test[features].to_numpy(float))[:,1]
        for r,p in zip(test.itertuples(),pp):
            rows.append({"forecast_issue_date":str(r.forecast_issue_date.date()),"y_up":int(getattr(r,t)>0),"p_up":float(p),"train_n":len(tr)})
    else:
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy(); start=te.feature_cutoff_date.min()
            tr=mature_train(df,start,h,features,pre2025_only=False)
            m=make_model(mname);m.fit(tr[features].to_numpy(float),(tr[t].to_numpy(float)>0).astype(int))
            pp=m.predict_proba(te[features].to_numpy(float))[:,1]
            for r,p in zip(te.itertuples(),pp):
                rows.append({"forecast_issue_date":str(r.forecast_issue_date.date()),"y_up":int(getattr(r,t)>0),"p_up":float(p),"train_n":len(tr)})
    return pd.DataFrame(rows)

def main():
    df,hashes=build_panel()
    ledgers=[]; mets=[]
    for h in HORIZONS:
        for b,features in FEATURE_BLOCKS.items():
            for mname in MODELS:
                led=dev_predictions(df,h,b,features,mname); ledgers.append(led)
                for period,g in [("2022-2024",led)]+[(str(y),led[led.year==y]) for y in [2022,2023,2024]]:
                    mets.append({"horizon":h,"feature_block":b,"model":mname,"period":period,**metrics(g.y_up,g.p_up)})
    led=pd.concat(ledgers,ignore_index=True); met=pd.DataFrame(mets)
    champ=choose(met)
    trans=[]; transled=[]
    if champ:
        h=int(champ["horizon"]);b=str(champ["feature_block"]);mname=str(champ["model"]);features=FEATURE_BLOCKS[b]
        for y in [2025,2026]:
            for adaptive,mode in [(False,"STATIC_PRE2025"),(True,"ADAPTIVE_ORIGIN_SAFE")]:
                q=transport(df,h,features,mname,y,adaptive)
                mm=metrics(q.y_up,q.p_up)
                trans.append({"mode":mode,"year":y,"horizon":h,"feature_block":b,"model":mname,**mm})
                z=q.copy();z["mode"]=mode;z["year"]=y;transled.append(z)
    led.to_csv(OUT/"SILVER_V2_DEV_PREDICTIONS.csv",index=False)
    met.to_csv(OUT/"SILVER_V2_DEV_METRICS.csv",index=False)
    pd.DataFrame(trans).to_csv(OUT/"SILVER_V2_TRANSPORT_METRICS.csv",index=False)
    if transled: pd.concat(transled,ignore_index=True).to_csv(OUT/"SILVER_V2_TRANSPORT_PREDICTIONS.csv",index=False)

    summary={"identity":"GLOBAL_XAG_RELATIVE_VALUE_V2","stak_ref":STAK_REF,"champion":champ,"transport":trans,
             "first_date":str(df.date.min().date()),"last_date":str(df.date.max().date()),"n_rows":len(df),"hashes":hashes}
    (OUT/"SILVER_V2_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")
    head=met[met.period=="2022-2024"].sort_values(["brier","balanced_accuracy"],ascending=[True,False])
    lines=["# SILVER SHORT-HORIZON V2 — RELATIVE-VALUE RESULT","",
           "**Evidence:** DEV selection 2022-2024 only; 2025/2026 opened after frozen V2 selection.","",
           "## DEV candidates","",
           "| H | Block | Model | Accuracy | BA | Brier | Log loss |",
           "|---|---|---|---:|---:|---:|---:|"]
    for _,r in head.iterrows():
        lines.append(f"| H{int(r.horizon)} | {r.feature_block} | {r.model} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} |")
    lines += ["","## Frozen champion",""]
    if champ:
        lines += [
          f"- **H{int(champ['horizon'])} / {champ['feature_block']} / {champ['model']}**",
          f"- DEV accuracy **{100*champ['accuracy']:.2f}%**",
          f"- DEV BA **{100*champ['balanced_accuracy']:.2f}%**",
          f"- DEV Brier **{champ['brier']:.4f}**",
          f"- annual stability flag **{champ['annual_stable']}**; DEV years BA<50% = {champ['dev_years_ba_below_50']}",
          "","## Transport","",
          "| Mode | Year | N | Accuracy | BA | Brier | Log loss |",
          "|---|---:|---:|---:|---:|---:|---:|"
        ]
        for r in trans:
            lines.append(f"| {r['mode']} | {r['year']} | {r['n']} | {100*r['accuracy']:.2f}% | {100*r['balanced_accuracy']:.2f}% | {r['brier']:.4f} | {r['logloss']:.4f} |")
    else:
        lines.append("No eligible DEV candidate.")
    (OUT/"SILVER_V2_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"SILVER_V2_RESULT.md").read_text())

if __name__=="__main__": main()
