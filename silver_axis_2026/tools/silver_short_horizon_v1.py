from __future__ import annotations
import json, math, hashlib, urllib.request
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, balanced_accuracy_score, recall_score

OUT=Path("silver_axis_2026/SILVER_SHORT_HORIZON_V1_OUT")
OUT.mkdir(parents=True,exist_ok=True)

STAK_REF="54fdf1c8d39b7b6c7b874d0f30f784296e886044"
SEED=20261005
BLOCK=5

HORIZONS=[1,3,5]
BLOCKS={
    "SILVER_ONLY":[
        "silver_r1","silver_r3","silver_r5","silver_r10","silver_r21","silver_sigma20"
    ],
    "CORE3":[
        "silver_r1","silver_r3","silver_r5","silver_r10","silver_r21","silver_sigma20",
        "gold_r1","gold_r5","gold_r21",
        "platinum_r1","platinum_r5","platinum_r21"
    ],
    "CORE4":[
        "silver_r1","silver_r3","silver_r5","silver_r10","silver_r21","silver_sigma20",
        "gold_r1","gold_r5","gold_r21",
        "platinum_r1","platinum_r5","platinum_r21",
        "palladium_r1","palladium_r5","palladium_r21"
    ]
}

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"silver-short-horizon-v1/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def load_metals():
    wanted={"Silver":"silver","Gold":"gold","Platinum":"platinum","Palladium":"palladium"}
    by=defaultdict(dict)
    hashes={}
    for year in range(2010,2027):
        url=f"https://raw.githubusercontent.com/lbruton/StakTrakr/{STAK_REF}/data/spot-history-{year}.json"
        raw=get_bytes(url)
        hashes[str(year)]=hashlib.sha256(raw).hexdigest()
        rows=json.loads(raw)
        for r in rows:
            metal=str(r.get("metal") or "")
            if metal not in wanted: continue
            ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
            if pd.isna(ts): continue
            d=ts.normalize()
            if d.weekday()>=5: continue
            try: v=float(r.get("spot"))
            except Exception: continue
            if np.isfinite(v) and v>0:
                by[metal][d]=v
    common=sorted(set.intersection(*(set(by[m]) for m in wanted)))
    if not common:
        raise RuntimeError("NO_COMMON_METAL_DATES")
    df=pd.DataFrame({"date":common})
    for metal,key in wanted.items():
        df[key]=[by[metal][d] for d in common]
    return df,hashes

def build_panel():
    m,hashes=load_metals()
    df=m.copy().sort_values("date").reset_index(drop=True)
    df["feature_cutoff_date"]=df["date"]
    df["forecast_issue_date"]=df["date"].shift(-1)

    ls=np.log(df["silver"])
    for h in HORIZONS:
        df[f"target_end_date_h{h}"]=df["date"].shift(-h)
        df[f"target_r{h}"]=np.log(df["silver"].shift(-h)/df["silver"])

    for h in [1,3,5,10,21]:
        df[f"silver_r{h}"]=ls.diff(h)
    df["silver_sigma20"]=ls.diff().rolling(20).std(ddof=0)

    for metal in ["gold","platinum","palladium"]:
        lm=np.log(df[metal])
        for h in [1,5,21]:
            df[f"{metal}_r{h}"]=lm.diff(h)

    df=df[df["forecast_issue_date"].notna()].copy().reset_index(drop=True)
    df["role"]=np.select(
        [
            df["forecast_issue_date"].dt.year<=2021,
            df["forecast_issue_date"].dt.year.between(2022,2024),
            df["forecast_issue_date"].dt.year==2025,
            df["forecast_issue_date"].dt.year==2026,
        ],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025","OPENED_2026"],
        default="OTHER"
    )
    return df,hashes

def make_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,penalty="l2",solver="lbfgs",max_iter=3000,random_state=SEED
        ))
    ])

def fit_xy(df,features,target):
    x=df[features].apply(pd.to_numeric,errors="coerce")
    y=(pd.to_numeric(df[target],errors="coerce")>0).astype(int)
    ok=x.notna().all(axis=1)&pd.to_numeric(df[target],errors="coerce").notna()
    return x.loc[ok].to_numpy(float),y.loc[ok].to_numpy(int),df.loc[ok].copy()

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
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
        "prediction_std":float(np.std(p)),
    }

def mature_train(df,start,h,features,pre2025_only=False):
    target=f"target_r{h}"
    m=df[f"target_end_date_h{h}"].notna() & (df[f"target_end_date_h{h}"]<=start) & df[target].notna()
    if pre2025_only:
        m &= df["forecast_issue_date"]<pd.Timestamp("2025-01-01")
    x=df.loc[m,features].apply(pd.to_numeric,errors="coerce")
    m2=x.notna().all(axis=1)
    return df.loc[m].loc[m2].copy()

def dev_predictions(df,h,block_name,features):
    target=f"target_r{h}"
    dev=df[(df.role=="DEV") & df[target].notna()].copy()
    dev=dev[dev[features].notna().all(axis=1)].reset_index(drop=True)
    rows=[]
    for bs in range(0,len(dev),BLOCK):
        te=dev.iloc[bs:bs+BLOCK].copy()
        start=te.feature_cutoff_date.min()
        tr=mature_train(df,start,h,features,pre2025_only=True)
        if len(tr)<500:
            raise RuntimeError(f"DEV train too small H{h} {block_name} n={len(tr)}")
        model=make_model()
        model.fit(tr[features].to_numpy(float),(tr[target].to_numpy(float)>0).astype(int))
        pp=model.predict_proba(te[features].to_numpy(float))[:,1]
        for r,p in zip(te.itertuples(),pp):
            rows.append({
                "horizon":h,"feature_block":block_name,
                "feature_cutoff_date":str(r.feature_cutoff_date.date()),
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "year":int(r.forecast_issue_date.year),
                "y_up":int(getattr(r,target)>0),
                "p_up":float(p),"train_n":int(len(tr))
            })
    return pd.DataFrame(rows)

def choose_champion(met):
    z=met[(met.period=="2022-2024") & (met.balanced_accuracy>0.5)].copy()
    if z.empty:
        return None
    best_brier=float(z.brier.min())
    c=z[z.brier<=best_brier+0.002].copy()
    c=c.sort_values(["balanced_accuracy","accuracy","brier"],
                    ascending=[False,False,True]).reset_index(drop=True)
    return c.iloc[0].to_dict()

def static_transport(df,h,features,year):
    target=f"target_r{h}"
    train=df[
        (df["forecast_issue_date"]<pd.Timestamp("2025-01-01")) &
        df[target].notna() &
        df[f"target_end_date_h{h}"].notna() &
        (df[f"target_end_date_h{h}"]<=pd.Timestamp("2024-12-31"))
    ].copy()
    train=train[train[features].notna().all(axis=1)]
    test=df[(df.forecast_issue_date.dt.year==year)&df[target].notna()].copy()
    test=test[test[features].notna().all(axis=1)]
    model=make_model()
    model.fit(train[features].to_numpy(float),(train[target].to_numpy(float)>0).astype(int))
    p=model.predict_proba(test[features].to_numpy(float))[:,1]
    return test,p

def adaptive_transport(df,h,features,year):
    target=f"target_r{h}"
    te=df[(df.forecast_issue_date.dt.year==year)&df[target].notna()].copy()
    te=te[te[features].notna().all(axis=1)].reset_index(drop=True)
    ps=[]; ys=[]; rows=[]
    for bs in range(0,len(te),BLOCK):
        block=te.iloc[bs:bs+BLOCK].copy()
        start=block.feature_cutoff_date.min()
        tr=mature_train(df,start,h,features,pre2025_only=False)
        model=make_model()
        model.fit(tr[features].to_numpy(float),(tr[target].to_numpy(float)>0).astype(int))
        pp=model.predict_proba(block[features].to_numpy(float))[:,1]
        for r,p in zip(block.itertuples(),pp):
            rows.append({
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "year":year,"y_up":int(getattr(r,target)>0),"p_up":float(p),
                "train_n":int(len(tr))
            })
    return pd.DataFrame(rows)

def main():
    df,hashes=build_panel()
    all_pred=[]; met_rows=[]
    for h in HORIZONS:
        for b,features in BLOCKS.items():
            led=dev_predictions(df,h,b,features)
            all_pred.append(led)
            for period,g in [("2022-2024",led)]+[(str(y),led[led.year==y]) for y in [2022,2023,2024]]:
                m=metrics(g.y_up,g.p_up)
                met_rows.append({"horizon":h,"feature_block":b,"period":period,**m})
    preds=pd.concat(all_pred,ignore_index=True)
    met=pd.DataFrame(met_rows)
    champion=choose_champion(met)

    transport_rows=[]; transport_pred=[]
    if champion is not None:
        h=int(champion["horizon"]); b=str(champion["feature_block"]); features=BLOCKS[b]
        for year in [2025,2026]:
            t,p=static_transport(df,h,features,year)
            mr=metrics((t[f"target_r{h}"].to_numpy(float)>0).astype(int),p)
            transport_rows.append({"mode":"STATIC_PRE2025","year":year,"horizon":h,"feature_block":b,**mr})
            for r,pv in zip(t.itertuples(),p):
                transport_pred.append({
                    "mode":"STATIC_PRE2025","year":year,"forecast_issue_date":str(r.forecast_issue_date.date()),
                    "y_up":int(getattr(r,f"target_r{h}")>0),"p_up":float(pv)
                })

            a=adaptive_transport(df,h,features,year)
            mr=metrics(a.y_up,a.p_up)
            transport_rows.append({"mode":"ADAPTIVE_ORIGIN_SAFE","year":year,"horizon":h,"feature_block":b,**mr})
            for r in a.itertuples():
                transport_pred.append({
                    "mode":"ADAPTIVE_ORIGIN_SAFE","year":year,"forecast_issue_date":r.forecast_issue_date,
                    "y_up":int(r.y_up),"p_up":float(r.p_up),"train_n":int(r.train_n)
                })

    preds.to_csv(OUT/"SILVER_SHORT_HORIZON_V1_DEV_PREDICTIONS.csv",index=False)
    met.to_csv(OUT/"SILVER_SHORT_HORIZON_V1_DEV_METRICS.csv",index=False)
    pd.DataFrame(transport_rows).to_csv(OUT/"SILVER_SHORT_HORIZON_V1_TRANSPORT_METRICS.csv",index=False)
    pd.DataFrame(transport_pred).to_csv(OUT/"SILVER_SHORT_HORIZON_V1_TRANSPORT_PREDICTIONS.csv",index=False)

    summary={
        "identity":"GLOBAL_XAG_PUBLIC_STAKTRAKR_V1",
        "status":"COMPLETE",
        "stak_ref":STAK_REF,
        "source_hashes":hashes,
        "first_date":str(df.date.min().date()),
        "last_date":str(df.date.max().date()),
        "n_rows":int(len(df)),
        "dev_selection_rule":"lowest Brier; within 0.002 choose higher balanced accuracy, then accuracy; BA must exceed 0.5",
        "champion":champion,
        "transport":transport_rows,
    }
    (OUT/"SILVER_SHORT_HORIZON_V1_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    head=met[met.period=="2022-2024"].sort_values(["horizon","brier"])
    lines=[
      "# SILVER SHORT-HORIZON V1 — TARGET / BASELINE RESULT","",
      f"**Identity:** `GLOBAL_XAG_PUBLIC_STAKTRAKR_V1`  ",
      f"**Pinned source:** `{STAK_REF}`  ",
      f"**Common-metal coverage:** {summary['first_date']} .. {summary['last_date']} (n={summary['n_rows']})","",
      "## DEV 2022-2024","",
      "| H | Block | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |",
      "|---|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for _,r in head.iterrows():
        lines.append(
          f"| H{int(r.horizon)} | {r.feature_block} | {int(r.n)} | {100*r.accuracy:.2f}% | "
          f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} | "
          f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    lines += ["","## Frozen DEV selection",""]
    if champion is None:
        lines += ["No candidate clears balanced accuracy > 50%. No transport promotion."]
    else:
        lines += [
          f"- Horizon: **H{int(champion['horizon'])}**",
          f"- Feature block: **{champion['feature_block']}**",
          f"- DEV accuracy: **{100*champion['accuracy']:.2f}%**",
          f"- DEV balanced accuracy: **{100*champion['balanced_accuracy']:.2f}%**",
          f"- DEV Brier: **{champion['brier']:.4f}**",
          "",
          "## 2025 / 2026 transport opened only after DEV selection","",
          "| Mode | Year | N | Accuracy | Balanced acc | Brier | Log loss |",
          "|---|---:|---:|---:|---:|---:|---:|"
        ]
        for r in transport_rows:
            lines.append(
              f"| {r['mode']} | {r['year']} | {r['n']} | {100*r['accuracy']:.2f}% | "
              f"{100*r['balanced_accuracy']:.2f}% | {r['brier']:.4f} | {r['logloss']:.4f} |"
            )
    lines += ["","## Governance","",
      "The horizon/block winner is selected from 2022-2024 only. 2025/2026 results are report-only transport evidence and may not change V1 configuration."
    ]
    (OUT/"SILVER_SHORT_HORIZON_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"SILVER_SHORT_HORIZON_V1_RESULT.md").read_text())

if __name__=="__main__":
    main()
