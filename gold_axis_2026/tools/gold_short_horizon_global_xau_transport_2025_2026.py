from __future__ import annotations
import io, json, os, zipfile, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, balanced_accuracy_score, precision_score, recall_score

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=11181284118
OUT=Path(os.environ.get("OUT_DIR","global_xau_transport_out"))
OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
H=3
BLOCK=5
CORE3=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-transport"},timeout=120)
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
    df=read_csv(z,"global_xau_readiness_panel.csv")
    for c in ["date","signal_date"]:
        df[c]=pd.to_datetime(df[c])
    df=df.sort_values("date").reset_index(drop=True)
    df["maturity_date_h3"]=df["date"].shift(-H)
    return df

def model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED))
    ])

def fill(train,test):
    a=train[CORE3].copy(); b=test[CORE3].copy(); meds={}
    for c in CORE3:
        med=pd.to_numeric(a[c],errors="coerce").median(skipna=True)
        val=float(med) if pd.notna(med) else 0.0
        meds[c]=val
        a[c]=pd.to_numeric(a[c],errors="coerce").fillna(val)
        b[c]=pd.to_numeric(b[c],errors="coerce").fillna(val)
    return a,b,meds

def band(p):
    if p>=0.55: return "HIGH_UP"
    if p<=0.45: return "LOW_UP"
    return "NEUTRAL"

def metrics(z):
    y=z["y_up"].astype(int).to_numpy()
    p=np.clip(z["p_up"].astype(float).to_numpy(),1e-6,1-1e-6)
    pred=(p>=0.5).astype(int)
    hi=z[z.p_up>=0.55]; lo=z[z.p_up<=0.45]
    return {
        "n":int(len(z)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "up_precision":float(precision_score(y,pred,zero_division=0)),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "prediction_std":float(np.std(p)),
        "mean_p_up":float(np.mean(p)),
        "actual_up_rate":float(np.mean(y)),
        "high_up_n":int(len(hi)),
        "high_up_realized_up_rate":float(hi.y_up.mean()) if len(hi) else None,
        "low_up_n":int(len(lo)),
        "low_up_realized_up_rate":float(lo.y_up.mean()) if len(lo) else None,
    }

def add_rows(rows,te,pp,mode,train_n):
    for (_,r),p in zip(te.iterrows(),pp):
        yret=float(r.target_r3); yup=int(yret>0); pred=int(p>=0.5)
        rows.append({
            "mode":mode,
            "origin_date":str(r.date.date()),
            "signal_date":str(r.signal_date.date()),
            "actual_h3_return":yret,
            "actual_direction":"UP" if yup else "DOWN",
            "y_up":int(yup),
            "p_up":float(p),
            "predicted_direction":"UP" if pred else "DOWN",
            "correct":bool(pred==yup),
            "conviction_band":band(float(p)),
            "train_n":int(train_n),
        })

def main():
    df=load_panel()
    eligible=df[df.target_r3.notna() & df.maturity_date_h3.notna()].copy()
    transport=eligible[eligible.signal_date.dt.year.isin([2025,2026])].copy()
    if transport.empty: raise RuntimeError("NO_TRANSPORT_ROWS")
    if transport.signal_date.dt.year.min()!=2025 or transport.signal_date.dt.year.max()!=2026:
        raise RuntimeError("EXPECTED_2025_AND_2026")

    rows=[]

    # Binding primary: fit exactly once on labels mature by 2024-12-31.
    train=eligible[eligible.maturity_date_h3<=pd.Timestamp("2024-12-31")].copy()
    Xtr,Xte,meds=fill(train,transport)
    m=model(); m.fit(Xtr,(train.target_r3>0).astype(int))
    pp=m.predict_proba(Xte)[:,1]
    add_rows(rows,transport,pp,"STRICT_FROZEN_FIT",len(train))

    coef=m.named_steps["model"].coef_[0]
    frozen_model={
        "train_n":int(len(train)),
        "train_first_origin":str(train.date.min().date()),
        "train_last_origin":str(train.date.max().date()),
        "last_maturity_date":str(train.maturity_date_h3.max().date()),
        "intercept":float(m.named_steps["model"].intercept_[0]),
        "coefficients":{f:float(v) for f,v in zip(CORE3,coef)},
        "medians":meds,
    }

    # Secondary diagnostic: same frozen specification; refit every 5 transport origins with only matured prior labels.
    for start in range(0,len(transport),BLOCK):
        te=transport.iloc[start:start+BLOCK].copy()
        first_origin=te.date.min()
        tr=eligible[(eligible.maturity_date_h3<=first_origin) & (eligible.date<first_origin)].copy()
        Xtr,Xte,_=fill(tr,te)
        mm=model(); mm.fit(Xtr,(tr.target_r3>0).astype(int))
        pp=mm.predict_proba(Xte)[:,1]
        add_rows(rows,te,pp,"FROZEN_WALK_FORWARD_PROTOCOL",len(tr))

    ledger=pd.DataFrame(rows)
    ledger["signal_year"]=pd.to_datetime(ledger.signal_date).dt.year
    ledger.to_csv(OUT/"global_xau_h3_transport_2025_2026_predictions.csv",index=False)

    metric_rows=[]
    for (mode,yr),z in ledger.groupby(["mode","signal_year"]):
        metric_rows.append({"mode":mode,"year":int(yr),**metrics(z)})
    mdf=pd.DataFrame(metric_rows).sort_values(["mode","year"])
    mdf.to_csv(OUT/"global_xau_h3_transport_2025_2026_metrics.csv",index=False)

    strict=mdf[mdf["mode"]=="STRICT_FROZEN_FIT"].set_index("year")
    summary={
        "status":"COMPLETE",
        "frozen_engine":"H3_CORE3_LOGIT_L2_RAW",
        "primary_mode":"STRICT_FROZEN_FIT",
        "secondary_mode":"FROZEN_WALK_FORWARD_PROTOCOL",
        "selection_use":"NONE",
        "years":{
            str(int(r.year)):{k:(None if pd.isna(v) else v) for k,v in r.to_dict().items() if k not in ["mode","year"]}
            for _,r in mdf[mdf["mode"]=="STRICT_FROZEN_FIT"].iterrows()
        },
        "frozen_model":frozen_model,
    }

    lines=[
        "# GOLD SHORT-HORIZON GLOBAL XAU — Frozen 2025 / 2026 Transport Result","",
        "**Status:** COMPLETE","",
        "Binding model: **H3 / CORE3 / Logistic L2 / RAW probability**","",
        "Primary score mode: **STRICT_FROZEN_FIT** — one fit using only H3 labels mature by 2024-12-31; unchanged through 2025/2026.","",
        "## Primary transport metrics","",
        "| Year | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | p>=0.55 N / UP rate | p<=0.45 N / UP rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for yr in [2025,2026]:
        r=strict.loc[yr]
        hir="—" if pd.isna(r.high_up_realized_up_rate) else f"{100*r.high_up_realized_up_rate:.1f}%"
        lor="—" if pd.isna(r.low_up_realized_up_rate) else f"{100*r.low_up_realized_up_rate:.1f}%"
        lines.append(f"| {yr} | {int(r.n)} | {100*r.accuracy:.1f}% | {100*r.balanced_accuracy:.1f}% | {r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.1f}% | {100*r.down_recall:.1f}% | {int(r.high_up_n)} / {hir} | {int(r.low_up_n)} / {lor} |")

    lines += ["","## Secondary walk-forward diagnostic","",
              "| Year | N | Accuracy | Balanced acc | Brier | Log loss |",
              "|---|---:|---:|---:|---:|---:|"]
    wf=mdf[mdf["mode"]=="FROZEN_WALK_FORWARD_PROTOCOL"].set_index("year")
    for yr in [2025,2026]:
        r=wf.loc[yr]
        lines.append(f"| {yr} | {int(r.n)} | {100*r.accuracy:.1f}% | {100*r.balanced_accuracy:.1f}% | {r.brier:.4f} | {r.logloss:.4f} |")

    lines += ["","No 2025/2026 result was used to retune the model, calibration, probability threshold or conviction bands."]
    (OUT/"TRANSPORT_RESULT.md").write_text("\n".join(lines)+"\n")

    files=[p for p in OUT.iterdir() if p.is_file()]
    summary["hashes"]={p.name:sha(p) for p in files}
    (OUT/"transport_summary.json").write_text(json.dumps(summary,indent=2,default=str,sort_keys=True)+"\n")
    print("GLOBAL_XAU_TRANSPORT_SUMMARY="+json.dumps(summary,sort_keys=True,default=str))
    print((OUT/"TRANSPORT_RESULT.md").read_text())

if __name__=="__main__":
    main()
