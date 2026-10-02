from __future__ import annotations
import io, json, os, zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import requests
from sklearn.metrics import balanced_accuracy_score, log_loss
from sklearn.tree import DecisionTreeClassifier, export_text

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_raw_source_cart_out"))
OUT.mkdir(parents=True,exist_ok=True)

SEED=20261001
BLOCK=5

BLOCKS={
    "GOLD_ONLY":[
        "gold_r1","gold_r5","gold_r21","sigma20",
    ],
    "METALS4":[
        "gold_r1","gold_r5","gold_r21","sigma20",
        "silver_r1","silver_r5","silver_r21",
        "platinum_r1","platinum_r5","platinum_r21",
        "palladium_r1","palladium_r5","palladium_r21",
    ],
    "GOLD_EQUITY3":[
        "gold_r1","gold_r5","gold_r21","sigma20",
        "nasdaq_r1","nasdaq_r5","nasdaq_r21",
        "sp500_r1","sp500_r5","sp500_r21",
        "djia_r1","djia_r5","djia_r21",
    ],
    "ALL7":[
        "gold_r1","gold_r5","gold_r21","sigma20",
        "silver_r1","silver_r5","silver_r21",
        "platinum_r1","platinum_r5","platinum_r21",
        "palladium_r1","palladium_r5","palladium_r21",
        "nasdaq_r1","nasdaq_r5","nasdaq_r21",
        "sp500_r1","sp500_r5","sp500_r21",
        "djia_r1","djia_r5","djia_r21",
    ],
}

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"raw-source-cart"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def load_r2():
    z=get_zip(READINESS_ARTIFACT)
    names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
    if len(names)!=1:
        raise RuntimeError(names)
    df=pd.read_csv(io.BytesIO(z.read(names[0])))
    for c in ["date","feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        df[c]=pd.to_datetime(df[c])
    return df.sort_values("feature_cutoff_date").reset_index(drop=True)

def load_equity_raw():
    dsn=os.environ["NEON_DATABASE_URL"]
    ids={
        "nasdaq":"NASDAQ100_FRED",
        "sp500":"SP500_FRED",
        "djia":"DJIA_FRED",
    }
    out={}
    with psycopg.connect(dsn,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for key,sid in ids.items():
                cur.execute("""
                    SELECT observation_ts::date, value, retrieved_at
                    FROM observations
                    WHERE series_id=%s
                    ORDER BY observation_ts, retrieved_at
                """,(sid,))
                rows=cur.fetchall()
                if not rows:
                    raise RuntimeError(f"NO_ROWS {sid}")
                q=pd.DataFrame(rows,columns=["obs_date","value","retrieved_at"])
                q["obs_date"]=pd.to_datetime(q.obs_date)
                q["value"]=pd.to_numeric(q.value,errors="coerce")
                q=q.dropna(subset=["value"]).sort_values(["obs_date","retrieved_at"]).drop_duplicates("obs_date",keep="last")
                q=q[q.value>0].copy()
                lv=np.log(q.value)
                for h in [1,5,21]:
                    q[f"{key}_r{h}"]=lv.diff(h)
                out[key]=q[["obs_date",f"{key}_r1",f"{key}_r5",f"{key}_r21"]].copy()
        conn.rollback()
    return out

def align_equities(df,eq):
    q=df.copy().sort_values("feature_cutoff_date")
    for key,src in eq.items():
        x=src.copy().sort_values("obs_date")
        x=x.rename(columns={"obs_date":f"{key}_obs_date"})
        q=pd.merge_asof(
            q.sort_values("feature_cutoff_date"),
            x.sort_values(f"{key}_obs_date"),
            left_on="feature_cutoff_date",
            right_on=f"{key}_obs_date",
            direction="backward"
        )
        q[f"{key}_age_days"]=(q.feature_cutoff_date-q[f"{key}_obs_date"]).dt.days
    return q.sort_values("feature_cutoff_date").reset_index(drop=True)

def tree():
    return DecisionTreeClassifier(
        criterion="log_loss",
        max_depth=3,
        min_samples_leaf=60,
        random_state=SEED,
    )

def metric(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "prediction_std":float(np.std(p)),
        "mean_p_up":float(np.mean(p)),
        "actual_up_rate":float(np.mean(y)),
    }

def valid_rows(df,features):
    return df[features].apply(pd.to_numeric,errors="coerce").notna().all(axis=1)

def run_block(df,name,features):
    dev=df[
        df.forecast_issue_date.dt.year.between(2022,2024) &
        df.target_r3.notna() &
        valid_rows(df,features)
    ].copy().reset_index(drop=True)
    rows=[]; split_counter=Counter(); block_rules=[]
    for bs in range(0,len(dev),BLOCK):
        te=dev.iloc[bs:bs+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()
        tr=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=cutoff) &
            (df.forecast_issue_date<pd.Timestamp("2025-01-01")) &
            valid_rows(df,features)
        ].copy()
        if len(tr)<500:
            raise RuntimeError(f"{name}: TRAIN_TOO_SMALL {len(tr)}")
        Xtr=tr[features].astype(float).to_numpy()
        Xte=te[features].astype(float).to_numpy()
        ytr=(tr.target_r3>0).astype(int).to_numpy()
        m=tree(); m.fit(Xtr,ytr)
        p=m.predict_proba(Xte)
        # sklearn can theoretically see one class in pathological early train
        if p.shape[1]==1:
            pup=np.repeat(float(m.classes_[0]),len(te))
        else:
            pos_idx=list(m.classes_).index(1)
            pup=p[:,pos_idx]
        feat_ids=m.tree_.feature
        for fi in feat_ids[feat_ids>=0]:
            split_counter[features[int(fi)]]+=1
        block_rules.append({
            "block":bs//BLOCK,
            "test_start":str(te.forecast_issue_date.min().date()),
            "train_n":int(len(tr)),
            "rules":export_text(m,feature_names=features,decimals=6),
        })
        for r,pp in zip(te.itertuples(),pup):
            rows.append({
                "block":name,
                "feature_cutoff_date":str(r.feature_cutoff_date.date()),
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "target_end_date_h3":str(r.target_end_date_h3.date()),
                "y_up":int(r.target_r3>0),
                "p_up":float(pp),
            })
    led=pd.DataFrame(rows)
    met=metric(led.y_up,led.p_up)
    led["year"]=pd.to_datetime(led.forecast_issue_date).dt.year
    annual=[]
    for yr,g in led.groupby("year"):
        annual.append({"block":name,"year":int(yr),**metric(g.y_up,g.p_up)})
    split_df=pd.DataFrame([{"block":name,"feature":f,"split_count":int(n)} for f,n in split_counter.most_common()])
    # final frozen pre-2025 tree solely for rule inspection, not scoring
    final=df[
        df.target_r3.notna() &
        df.target_end_date_h3.notna() &
        (df.target_end_date_h3<=pd.Timestamp("2024-12-31")) &
        valid_rows(df,features)
    ].copy()
    fm=tree(); fm.fit(final[features].astype(float).to_numpy(),(final.target_r3>0).astype(int).to_numpy())
    final_rules=export_text(fm,feature_names=features,decimals=6)
    imp=pd.DataFrame({
        "block":name,
        "feature":features,
        "importance":fm.feature_importances_,
    }).sort_values("importance",ascending=False)
    return led,met,pd.DataFrame(annual),split_df,block_rules,final_rules,imp

def main():
    df=align_equities(load_r2(),load_equity_raw())
    # Fail closed on equity staleness in DEV.
    for key in ["nasdaq","sp500","djia"]:
        dev_age=df.loc[df.forecast_issue_date.dt.year.between(2022,2024),f"{key}_age_days"].dropna()
        if dev_age.empty or float(dev_age.max())>7:
            raise RuntimeError(f"{key} DEV age invalid max={dev_age.max() if len(dev_age) else None}")

    all_led=[]; summary=[]; annual=[]; splits=[]; imps=[]; logs={}
    for name,features in BLOCKS.items():
        led,met,ann,sp,br,fr,imp=run_block(df,name,features)
        all_led.append(led); summary.append({"block":name,**met})
        annual.append(ann); splits.append(sp); imps.append(imp)
        logs[name]={"block_rules":br,"final_pre2025_tree":fr}

    pd.concat(all_led,ignore_index=True).to_csv(OUT/"raw_source_cart_dev_predictions.csv",index=False)
    sm=pd.DataFrame(summary).sort_values(["brier","logloss"])
    sm.to_csv(OUT/"raw_source_cart_summary.csv",index=False)
    pd.concat(annual,ignore_index=True).to_csv(OUT/"raw_source_cart_annual.csv",index=False)
    pd.concat(splits,ignore_index=True).to_csv(OUT/"raw_source_cart_split_usage.csv",index=False)
    pd.concat(imps,ignore_index=True).to_csv(OUT/"raw_source_cart_final_importances.csv",index=False)
    (OUT/"raw_source_cart_rules.json").write_text(json.dumps(logs,indent=2,sort_keys=True)+"\n")

    best=sm.iloc[0].to_dict()
    result={
        "schema":"GLOBAL_XAU_RAW_SOURCE_CART_V1",
        "model":{"criterion":"log_loss","max_depth":3,"min_samples_leaf":60,"random_state":SEED},
        "blocks":summary,
        "best_by_brier":best,
        "governance":{"dev":"2022-2024","opened_2025_2026_used":False,"random_split":False},
    }
    (OUT/"raw_source_cart_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GLOBAL XAU DAILY H3 — Raw-Source CART Pattern Screen","",
        "Model: shallow CART, depth=3, min leaf=60. 2025/2026 were not used.","",
        "| Source block | N | Accuracy | Balanced acc | Brier | Log loss | Pred SD |",
        "|---|---:|---:|---:|---:|---:|---:|"
    ]
    for r in sm.itertuples():
        lines.append(f"| {r.block} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {r.brier:.6f} | {r.logloss:.6f} | {r.prediction_std:.4f} |")
    lines += ["",f"Best block by Brier: **{best['block']}**.","",
              "Split/rule logs and final pre-2025 tree rules were saved for later inspection."]
    (OUT/"RAW_SOURCE_CART_RESULT.md").write_text("\n".join(lines)+"\n")
    print("RAW_SOURCE_CART_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"RAW_SOURCE_CART_RESULT.md").read_text())

if __name__=="__main__":
    main()
