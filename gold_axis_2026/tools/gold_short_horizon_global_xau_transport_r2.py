from __future__ import annotations
import io,json,os,zipfile,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss,balanced_accuracy_score,precision_score,recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=int(os.environ["READINESS_ARTIFACT"])
OUT=Path(os.environ.get("OUT_DIR","global_xau_r2_transport_out"));OUT.mkdir(parents=True,exist_ok=True)
SEED=20261001
CORE3=[
 "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
 "silver_r1","silver_r5","silver_r21","silver_age_days",
 "platinum_r1","platinum_r5","platinum_r21","platinum_age_days",
]

def get_zip(aid):
 tok=os.environ["GITHUB_TOKEN"];u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
 r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"global-xau-r2-transport"},timeout=120);r.raise_for_status()
 return zipfile.ZipFile(io.BytesIO(r.content))

def load():
 z=get_zip(READINESS_ARTIFACT)
 names=[n for n in z.namelist() if n.endswith("global_xau_r2_readiness_panel.csv")]
 if len(names)!=1:raise RuntimeError(names)
 df=pd.read_csv(io.BytesIO(z.read(names[0])))
 for c in ["date","feature_cutoff_date","forecast_issue_date","target_start_date","target_end_date_h3"]:
  df[c]=pd.to_datetime(df[c])
 return df.sort_values("feature_cutoff_date").reset_index(drop=True)

def model():
 return Pipeline([("scale",StandardScaler()),("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=1000,random_state=SEED))])

def fill(train,test):
 a=train[CORE3].copy();b=test[CORE3].copy()
 for c in CORE3:
  m=pd.to_numeric(a[c],errors="coerce").median();v=0.0 if pd.isna(m) else float(m)
  a[c]=pd.to_numeric(a[c],errors="coerce").fillna(v);b[c]=pd.to_numeric(b[c],errors="coerce").fillna(v)
 return a,b

def metrics(y,p):
 y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-9,1-1e-9);pred=(p>=.5).astype(int)
 return {
  "n":int(len(y)),"accuracy":float(np.mean(pred==y)),
  "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
  "brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,p,labels=[0,1])),
  "up_precision":float(precision_score(y,pred,zero_division=0)),
  "up_recall":float(recall_score(y,pred,zero_division=0)),
  "down_recall":float(recall_score(1-y,1-pred,zero_division=0)),
  "pred_sd":float(np.std(p)),"mean_p_up":float(np.mean(p)),"actual_up_rate":float(np.mean(y))
 }

def main():
 df=load()
 eligible=df[df.target_r3.notna() & df.target_end_date_h3.notna()].copy()
 train=eligible[eligible.target_end_date_h3<=pd.Timestamp("2024-12-31")].copy()
 test=eligible[(eligible.forecast_issue_date.dt.year.isin([2025,2026])) &
               (eligible.target_end_date_h3<=pd.Timestamp("2026-09-30"))].copy()
 Xtr,Xte=fill(train,test);m=model();m.fit(Xtr,(train.target_r3>0).astype(int));pp=m.predict_proba(Xte)[:,1]
 rows=[]
 for r,p in zip(test.itertuples(),pp):
  y=int(r.target_r3>0);pred=int(p>=.5)
  rows.append({
   "feature_cutoff_date":str(r.feature_cutoff_date.date()),
   "forecast_issue_date":str(r.forecast_issue_date.date()),
   "target_start_date":str(r.target_start_date.date()),
   "target_end_date_h3":str(r.target_end_date_h3.date()),
   "actual_h3_return":float(r.target_r3),"actual_direction":"UP" if y else "DOWN",
   "p_up":float(p),"predicted_direction":"UP" if pred else "DOWN","correct":bool(pred==y),
   "conviction_band":"HIGH_UP" if p>=.55 else ("LOW_UP" if p<=.45 else "NEUTRAL"),
   "year":int(r.forecast_issue_date.year),"month":str(r.forecast_issue_date.strftime("%Y-%m")),
   "train_n":int(len(train))
  })
 led=pd.DataFrame(rows);led.to_csv(OUT/"global_xau_r2_h3_transport_predictions.csv",index=False)
 mets=[]
 for label,g in list(led.groupby(led.year.astype(str)))+list(led[led.year==2026].groupby("month")):
  y=(g.actual_direction=="UP").astype(int);mm=metrics(y,g.p_up)
  hi=g[g.p_up>=.55];lo=g[g.p_up<=.45]
  mets.append({"period":str(label),**mm,"high_up_n":int(len(hi)),
    "high_up_realized_up":None if not len(hi) else float((hi.actual_direction=="UP").mean()),
    "low_up_n":int(len(lo)),"low_up_realized_up":None if not len(lo) else float((lo.actual_direction=="UP").mean())})
 mdf=pd.DataFrame(mets);mdf.to_csv(OUT/"global_xau_r2_h3_transport_metrics.csv",index=False)
 coef={f:float(v) for f,v in zip(CORE3,m.named_steps["model"].coef_[0])}
 aug=led[led.month=="2026-08"];sep=led[led.month=="2026-09"]
 summary={"identity":"GLOBAL_XAU_PUBLIC_STAKTRAKR_R2","engine":"H3_CORE3_LOGIT_L2_RAW",
  "readiness_artifact":READINESS_ARTIFACT,"train_n":int(len(train)),
  "train_last_target_end":str(train.target_end_date_h3.max().date()),
  "last_scored_issue":str(pd.to_datetime(led.forecast_issue_date).max().date()),
  "last_scored_target_end":str(pd.to_datetime(led.target_end_date_h3).max().date()),
  "august_n":int(len(aug)),"september_n":int(len(sep)),
  "metrics":mdf.to_dict(orient="records"),"coefficients":coef,
  "governance":{"strict_frozen_fit":True,"threshold":0.5,"conviction_high":0.55,"conviction_low":0.45,
                "no_2025_2026_tuning":True}}
 (OUT/"global_xau_r2_transport_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
 lines=["# GOLD SHORT-HORIZON GLOBAL XAU R2 — Frozen H3 Transport","",
  "Engine: **H3 / CORE3 / Logistic L2 / RAW**","",
  f"Training rows: {len(train)}; last mature target end: {train.target_end_date_h3.max().date()}.",
  f"Scored through issue {summary['last_scored_issue']} / target end {summary['last_scored_target_end']}.",
  f"August 2026 n={len(aug)}; September 2026 n={len(sep)}.","",
  "| Period | N | Accuracy | Bal acc | Brier | Log loss | UP recall | DOWN recall |",
  "|---|---:|---:|---:|---:|---:|---:|---:|"]
 for r in mdf.itertuples():
  if r.period in ["2025","2026","2026-08","2026-09"]:
   lines.append(f"| {r.period} | {int(r.n)} | {100*r.accuracy:.1f}% | {100*r.balanced_accuracy:.1f}% | {r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.1f}% | {100*r.down_recall:.1f}% |")
 lines += ["","No 2025/2026 observation was used for model, feature, threshold or calibration selection."]
 (OUT/"R2_TRANSPORT_RESULT.md").write_text("\n".join(lines)+"\n")
 print("GLOBAL_XAU_R2_TRANSPORT="+json.dumps(summary,separators=(",",":")))
 print((OUT/"R2_TRANSPORT_RESULT.md").read_text())

if __name__=="__main__":main()
