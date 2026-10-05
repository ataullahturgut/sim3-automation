from __future__ import annotations
import io, json, os, zipfile, urllib.request
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import requests
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

REPO="ataullahturgut/sim3-automation"
EXT_ARTIFACT=11028494060
STAK_REF="54fdf1c8d39b7b6c7b874d0f30f784296e886044"
OUT=Path("silver_axis_2026/SILVER_SHORT_HORIZON_V3_OUT")
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261005
BLOCK=5
H=5

BASE=["silver_r1","silver_r3","silver_r5","silver_r10","silver_r21","silver_sigma20"]
RATES=BASE+["DGS10_chg5","DFII10_chg5","BREAKEVEN10_PROXY_chg5"]
FX=BASE+["BROAD_USD_INDEX_ret5","EURUSD_QUOTE_ret5","GBPUSD_QUOTE_ret5","JPY_PER_USD_ret5","CHF_PER_USD_ret5","CNY_PER_USD_ret5"]
RISK=BASE+["VIX_level","VIX_chg5","NDX_ret5"]
MACRO_RISK=BASE+[
    "DGS10_chg5","DFII10_chg5","BREAKEVEN10_PROXY_chg5",
    "BROAD_USD_INDEX_ret5","EURUSD_QUOTE_ret5","JPY_PER_USD_ret5",
    "VIX_level","VIX_chg5","NDX_ret5"
]
BLOCKS={"BASE":BASE,"RATES":RATES,"FX":FX,"RISK":RISK,"MACRO_RISK":MACRO_RISK}
MODELS=["LOGIT_L2","HGB"]

def get_bytes(url,timeout=120):
    req=urllib.request.Request(url,headers={"User-Agent":"silver-macro-v3/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"silver-macro-v3"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_ext():
    z=get_zip(EXT_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith(".json")]
    if len(names)!=1: raise RuntimeError(f"EXT_JSON_NAMES {names}")
    return json.loads(z.read(names[0]))

def series_from_dict(dct,field=None,name="value"):
    rows=[]
    for ds,v in dct.items():
        val=v if field is None else v.get(field)
        if val is None: continue
        try: fv=float(val)
        except Exception: continue
        if np.isfinite(fv): rows.append((pd.to_datetime(ds),fv))
    return pd.DataFrame(rows,columns=["obs_date",name]).sort_values("obs_date").drop_duplicates("obs_date",keep="last")

def add_source_transforms(s,name,kind):
    q=s.copy().sort_values("obs_date").reset_index(drop=True)
    v=pd.to_numeric(q[name],errors="coerce")
    if kind=="rate":
        q[f"{name}_chg5"]=v-v.shift(5)
    elif kind=="price":
        lv=np.log(v.where(v>0))
        q[f"{name}_ret5"]=lv-lv.shift(5)
    elif kind=="vix":
        q[f"{name}_level"]=v
        q[f"{name}_chg5"]=v-v.shift(5)
    return q

def load_metals():
    wanted={"Silver":"silver","Gold":"gold","Platinum":"platinum","Palladium":"palladium"}
    by=defaultdict(dict)
    for year in range(2010,2027):
        raw=get_bytes(f"https://raw.githubusercontent.com/lbruton/StakTrakr/{STAK_REF}/data/spot-history-{year}.json")
        for r in json.loads(raw):
            metal=str(r.get("metal") or "")
            if metal not in wanted: continue
            ts=pd.to_datetime(r.get("timestamp"),errors="coerce")
            if pd.isna(ts): continue
            d=ts.normalize()
            if d.weekday()>=5: continue
            try:v=float(r.get("spot"))
            except Exception:continue
            if np.isfinite(v) and v>0:by[metal][d]=v
    common=sorted(set.intersection(*(set(by[m]) for m in wanted)))
    df=pd.DataFrame({"date":common})
    for metal,key in wanted.items():df[key]=[by[metal][d] for d in common]
    return df

def build_panel():
    df=load_metals().sort_values("date").reset_index(drop=True)
    df["feature_cutoff_date"]=df.date
    df["forecast_issue_date"]=df.date.shift(-1)
    ls=np.log(df.silver)
    df["target_end_date_h5"]=df.date.shift(-5)
    df["target_r5"]=np.log(df.silver.shift(-5)/df.silver)
    for h in [1,3,5,10,21]:df[f"silver_r{h}"]=ls.diff(h)
    df["silver_sigma20"]=ls.diff().rolling(20).std(ddof=0)
    df=df[df.forecast_issue_date.notna()].copy().reset_index(drop=True)

    ext=read_ext()
    # Conservative availability cutoffs copied from Gold R2 research contract.
    df["cut_h15"]=df.forecast_issue_date-pd.Timedelta(days=2)
    df["cut_h10"]=df.forecast_issue_date-pd.Timedelta(days=7)
    df["cut_us"]=df.forecast_issue_date-pd.Timedelta(days=1)
    df["rid"]=np.arange(len(df))

    source_specs=[]
    for name in ["DGS10","DFII10","BREAKEVEN10_PROXY"]:
        s=series_from_dict(ext["h15_daily"],name,name)
        source_specs.append((name,add_source_transforms(s,name,"rate"),"cut_h15",[f"{name}_chg5"]))
    for name in ["BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]:
        s=series_from_dict(ext["h10_daily"],name,name)
        source_specs.append((name,add_source_transforms(s,name,"price"),"cut_h10",[f"{name}_ret5"]))
    s=series_from_dict(ext["vix_daily"],None,"VIX")
    source_specs.append(("VIX",add_source_transforms(s,"VIX","vix"),"cut_us",["VIX_level","VIX_chg5"]))
    s=series_from_dict(ext["nasdaq100_daily"],None,"NDX")
    source_specs.append(("NDX",add_source_transforms(s,"NDX","price"),"cut_us",["NDX_ret5"]))

    for name,s,cut,keep in source_specs:
        rr=s[["obs_date"]+keep].rename(columns={"obs_date":f"{name}_obs_date"})
        df=df.sort_values(cut)
        df=pd.merge_asof(df,rr,left_on=cut,right_on=f"{name}_obs_date",direction="backward")
    df=df.sort_values("rid").reset_index(drop=True)

    df["role"]=np.select(
        [df.forecast_issue_date.dt.year<=2021,df.forecast_issue_date.dt.year.between(2022,2024),
         df.forecast_issue_date.dt.year==2025,df.forecast_issue_date.dt.year==2026],
        ["TRAIN_HISTORY","DEV","TRANSPORT_2025","OPENED_2026"],default="OTHER")
    return df

def make_model(name):
    if name=="LOGIT_L2":
        return Pipeline([("scale",StandardScaler()),("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))])
    if name=="HGB":
        return HistGradientBoostingClassifier(learning_rate=.05,max_iter=150,max_depth=3,min_samples_leaf=30,l2_regularization=1.0,random_state=SEED)
    raise KeyError(name)

def metrics(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6);pred=(p>=.5).astype(int)
    return {"n":int(len(y)),"accuracy":float(np.mean(pred==y)),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),
      "brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,p,labels=[0,1])),
      "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
      "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
      "actual_up_rate":float(np.mean(y)),"pred_up_rate":float(np.mean(pred)),"prediction_std":float(np.std(p))}

def mature_train(df,start,features,pre2025=False):
    m=df.target_end_date_h5.notna()&(df.target_end_date_h5<=start)&df.target_r5.notna()
    if pre2025:m &= df.forecast_issue_date<pd.Timestamp("2025-01-01")
    q=df.loc[m].copy()
    return q[q[features].notna().all(axis=1)].copy()

def dev_ledger(df,b,features,mname):
    dev=df[(df.role=="DEV")&df.target_r5.notna()].copy()
    dev=dev[dev[features].notna().all(axis=1)].reset_index(drop=True)
    rows=[]
    for bs in range(0,len(dev),BLOCK):
        te=dev.iloc[bs:bs+BLOCK].copy();start=te.feature_cutoff_date.min()
        tr=mature_train(df,start,features,True)
        if len(tr)<500:raise RuntimeError(f"TRAIN_SMALL {b} {mname} {len(tr)}")
        m=make_model(mname);m.fit(tr[features].to_numpy(float),(tr.target_r5.to_numpy(float)>0).astype(int))
        pp=m.predict_proba(te[features].to_numpy(float))[:,1]
        for r,p in zip(te.itertuples(),pp):
            rows.append({"feature_block":b,"model":mname,"forecast_issue_date":str(r.forecast_issue_date.date()),
              "year":int(r.forecast_issue_date.year),"y_up":int(r.target_r5>0),"p_up":float(p),"train_n":len(tr)})
    return pd.DataFrame(rows)

def choose(met):
    z=met[(met.period=="2022-2024")&(met.balanced_accuracy>0.5)].copy()
    if z.empty:return None
    best=z.brier.min();c=z[z.brier<=best+.002].copy()
    c=c.sort_values(["balanced_accuracy","accuracy","brier"],ascending=[False,False,True]).reset_index(drop=True)
    r=c.iloc[0].to_dict()
    ann=met[(met.feature_block==r["feature_block"])&(met.model==r["model"])&met.period.isin(["2022","2023","2024"])]
    r["dev_years_ba_below_50"]=int((ann.balanced_accuracy<.5).sum())
    r["annual_stable"]=bool(r["dev_years_ba_below_50"]<=1)
    return r

def transport(df,features,mname,year,adaptive):
    te=df[(df.forecast_issue_date.dt.year==year)&df.target_r5.notna()].copy()
    te=te[te[features].notna().all(axis=1)].reset_index(drop=True)
    rows=[]
    if not adaptive:
        tr=df[(df.forecast_issue_date<pd.Timestamp("2025-01-01"))&df.target_r5.notna()&
              df.target_end_date_h5.notna()&(df.target_end_date_h5<=pd.Timestamp("2024-12-31"))].copy()
        tr=tr[tr[features].notna().all(axis=1)]
        m=make_model(mname);m.fit(tr[features].to_numpy(float),(tr.target_r5.to_numpy(float)>0).astype(int))
        pp=m.predict_proba(te[features].to_numpy(float))[:,1]
        for r,p in zip(te.itertuples(),pp):rows.append({"forecast_issue_date":str(r.forecast_issue_date.date()),"y_up":int(r.target_r5>0),"p_up":float(p),"train_n":len(tr)})
    else:
        for bs in range(0,len(te),BLOCK):
            b=te.iloc[bs:bs+BLOCK].copy();start=b.feature_cutoff_date.min()
            tr=mature_train(df,start,features,False)
            m=make_model(mname);m.fit(tr[features].to_numpy(float),(tr.target_r5.to_numpy(float)>0).astype(int))
            pp=m.predict_proba(b[features].to_numpy(float))[:,1]
            for r,p in zip(b.itertuples(),pp):rows.append({"forecast_issue_date":str(r.forecast_issue_date.date()),"y_up":int(r.target_r5>0),"p_up":float(p),"train_n":len(tr)})
    return pd.DataFrame(rows)

def main():
    df=build_panel()
    ledgers=[];mets=[]
    for b,features in BLOCKS.items():
        for mn in MODELS:
            led=dev_ledger(df,b,features,mn);ledgers.append(led)
            for period,g in [("2022-2024",led)]+[(str(y),led[led.year==y]) for y in [2022,2023,2024]]:
                mets.append({"feature_block":b,"model":mn,"period":period,**metrics(g.y_up,g.p_up)})
    led=pd.concat(ledgers,ignore_index=True);met=pd.DataFrame(mets);champ=choose(met)
    trans=[];tled=[]
    if champ:
        b=champ["feature_block"];mn=champ["model"];features=BLOCKS[b]
        for y in [2025,2026]:
            for adaptive,mode in [(False,"STATIC_PRE2025"),(True,"ADAPTIVE_ORIGIN_SAFE")]:
                q=transport(df,features,mn,y,adaptive);mm=metrics(q.y_up,q.p_up)
                trans.append({"mode":mode,"year":y,"feature_block":b,"model":mn,**mm})
                q["mode"]=mode;q["year"]=y;tled.append(q)
    led.to_csv(OUT/"SILVER_V3_DEV_PREDICTIONS.csv",index=False)
    met.to_csv(OUT/"SILVER_V3_DEV_METRICS.csv",index=False)
    pd.DataFrame(trans).to_csv(OUT/"SILVER_V3_TRANSPORT_METRICS.csv",index=False)
    if tled:pd.concat(tled,ignore_index=True).to_csv(OUT/"SILVER_V3_TRANSPORT_PREDICTIONS.csv",index=False)
    summary={"identity":"GLOBAL_XAG_MACRO_RISK_V3","champion":champ,"transport":trans,
      "external_artifact":EXT_ARTIFACT,"stak_ref":STAK_REF}
    (OUT/"SILVER_V3_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    head=met[met.period=="2022-2024"].sort_values(["brier","balanced_accuracy"],ascending=[True,False])
    lines=["# SILVER SHORT-HORIZON V3 — MACRO/RISK RESULT","",
      "**DEV selection uses 2022-2024 only. 2025/2026 transport is opened only after the V3 winner is frozen.**","",
      "| Block | Model | Accuracy | BA | Brier | Log loss |",
      "|---|---|---:|---:|---:|---:|"]
    for _,r in head.iterrows():
        lines.append(f"| {r.feature_block} | {r.model} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | {r.logloss:.4f} |")
    lines += ["","## Frozen V3 champion",""]
    if champ:
        lines += [f"- **{champ['feature_block']} / {champ['model']}**",
          f"- DEV accuracy **{100*champ['accuracy']:.2f}%**",
          f"- DEV BA **{100*champ['balanced_accuracy']:.2f}%**",
          f"- DEV Brier **{champ['brier']:.4f}**",
          f"- annual stability **{champ['annual_stable']}**, years BA<50% = {champ['dev_years_ba_below_50']}",
          "","## Transport","",
          "| Mode | Year | N | Accuracy | BA | Brier | Log loss |",
          "|---|---:|---:|---:|---:|---:|---:|"]
        for r in trans:lines.append(f"| {r['mode']} | {r['year']} | {r['n']} | {100*r['accuracy']:.2f}% | {100*r['balanced_accuracy']:.2f}% | {r['brier']:.4f} | {r['logloss']:.4f} |")
    else:lines.append("No eligible V3 candidate.")
    (OUT/"SILVER_V3_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"SILVER_V3_RESULT.md").read_text())

if __name__=="__main__":main()

# workflow trigger 2026-10-05

# rerun via established hourly workflow
