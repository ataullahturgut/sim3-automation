from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
RAW15=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
OUT=AX/"SESSION_IRIS_HOURLY_RAW_REPLAY_V1_OUT"; OUT.mkdir(exist_ok=True)

SERIES_ID="XAU_USD_TWELVE_1H_RESEARCH_V1"
SEED=20261006
BLOCK=5
MIN_TRAIN=180

PATH=[
 "h_ret_1","h_ret_3","h_ret_6","h_ret_12","h_ret_24","h_ret_48",
 "h_lag2","h_session_ret",
]
VOL=[
 "h_rv_6","h_rv_12","h_rv_24","h_rv_48",
 "h_up_semivol_24","h_down_semivol_24","h_down_up_semivol_ratio_24",
 "h_jump_concentration_24","h_range_24",
]
SHAPE=[
 "h_upfrac_24","h_slope_6","h_slope_24","h_max_drawdown_24",
 "h_recovery_24","h_close_location_24","h_age_max_pos_24","h_age_max_neg_24",
]
ALL_HOURLY=PATH+VOL+SHAPE

def sha(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def load_hourly_raw():
 dsn=os.environ["NEON_DATABASE_URL"]
 with psycopg.connect(dsn,autocommit=False) as conn:
  with conn.cursor() as cur:
   cur.execute("SET TRANSACTION READ ONLY")
   cur.execute("""
     SELECT observation_ts,value,retrieved_at
     FROM observations
     WHERE series_id=%s
     ORDER BY observation_ts,retrieved_at
   """,(SERIES_ID,))
   rows=cur.fetchall()
  conn.rollback()
 if not rows: raise RuntimeError("NO_NEON_HOURLY_ROWS")
 x=pd.DataFrame(rows,columns=["ts","value","retrieved_at"])
 x["ts"]=pd.to_datetime(x.ts,utc=True)
 x["value"]=pd.to_numeric(x.value,errors="coerce")
 x=x.dropna(subset=["ts","value"])
 x=x[x.value>0].copy()
 # raw observation vintage rule: latest retrieved value for a timestamp.
 x=x.sort_values(["ts","retrieved_at"]).drop_duplicates("ts",keep="last").sort_values("ts").reset_index(drop=True)
 # Twelve datetime is bar-open; stored value is close. It only becomes usable at ts+1h.
 x["available_at_utc"]=x.ts+pd.Timedelta(hours=1)
 return x[["ts","available_at_utc","value"]].copy()

def slope(a):
 a=np.asarray(a,float)
 if len(a)<2 or not np.isfinite(a).all():return np.nan
 xx=np.arange(len(a),dtype=float); xm=xx.mean(); ym=a.mean()
 den=np.sum((xx-xm)**2)
 return np.nan if den<=0 else float(np.sum((xx-xm)*(a-ym))/den)

def max_drawdown(a):
 a=np.asarray(a,float)
 if len(a)<2 or not np.isfinite(a).all():return np.nan
 return float(np.min(a-np.maximum.accumulate(a)))

def age_extreme(a,which):
 a=np.asarray(a,float)
 if len(a)==0 or not np.isfinite(a).all():return np.nan
 r=a[::-1]
 return float(np.argmax(r) if which=="max" else np.argmin(r))

def build_hourly_features(raw):
 q=raw.copy().sort_values("ts").reset_index(drop=True)
 q["ts_ny"]=q.ts.dt.tz_convert("America/New_York")
 q["local_date"]=q.ts_ny.dt.date
 q["logp"]=np.log(q.value.astype(float))
 q["hr"]=q.logp.diff()
 for h in [1,3,6,12,24,48]:q[f"h_ret_{h}"]=q.logp-q.logp.shift(h)
 q["h_lag2"]=q.hr.shift(2)
 for h in [6,12,24,48]:q[f"h_rv_{h}"]=np.sqrt(q.hr.pow(2).rolling(h,min_periods=h).sum())
 pos=q.hr.clip(lower=0).pow(2); neg=q.hr.clip(upper=0).pow(2)
 q["h_up_semivol_24"]=np.sqrt(pos.rolling(24,min_periods=24).sum())
 q["h_down_semivol_24"]=np.sqrt(neg.rolling(24,min_periods=24).sum())
 q["h_down_up_semivol_ratio_24"]=q.h_down_semivol_24/(q.h_up_semivol_24+1e-8)
 q["h_jump_concentration_24"]=q.hr.abs().rolling(24,min_periods=24).max()/(q.h_rv_24+1e-8)
 q["h_range_24"]=q.logp.rolling(24,min_periods=24).max()-q.logp.rolling(24,min_periods=24).min()
 q["h_upfrac_24"]=(q.hr>0).astype(float).rolling(24,min_periods=24).mean()
 q["h_slope_6"]=q.logp.rolling(6,min_periods=6).apply(slope,raw=True)
 q["h_slope_24"]=q.logp.rolling(24,min_periods=24).apply(slope,raw=True)
 q["h_max_drawdown_24"]=q.logp.rolling(24,min_periods=24).apply(max_drawdown,raw=True)
 trough=q.logp.rolling(24,min_periods=24).min(); hi=q.logp.rolling(24,min_periods=24).max()
 q["h_recovery_24"]=q.logp-trough
 q["h_close_location_24"]=(q.logp-trough)/(hi-trough+1e-8)
 q["h_age_max_pos_24"]=q.hr.rolling(24,min_periods=24).apply(lambda a:age_extreme(a,"max"),raw=True)
 q["h_age_max_neg_24"]=q.hr.rolling(24,min_periods=24).apply(lambda a:age_extreme(a,"min"),raw=True)
 first_log=q.groupby("local_date")["logp"].transform("first")
 q["h_session_ret"]=q.logp-first_log
 return q.dropna(subset=ALL_HOURLY).copy()

def verify_targets():
 raw=pd.read_csv(RAW15)
 raw["dt_utc"]=pd.to_datetime(raw.dt_utc,utc=True)
 op=dict(zip(raw.dt_utc,raw.open.astype(float)))
 cl=dict(zip(raw.dt_utc,raw.close.astype(float)))
 frames=[]
 for p in [WGC,SOB]:
  z=pd.read_csv(p)
  z=z[z.final_trainable.astype(str).str.lower().eq("true")].copy()
  z["source_file"]=p.name
  frames.append(z)
 q=pd.concat(frames,ignore_index=True)
 errs=[]
 for r in q.itertuples(index=False):
  s=pd.Timestamp(r.start_utc); e=pd.Timestamp(r.end_utc); ep=e-pd.Timedelta(minutes=15)
  ps=op.get(s); pe=cl.get(ep)
  if ps is None or pe is None:
   errs.append((r.label_date,r.partition,r.window,"RAW_BOUNDARY_MISSING")); continue
  ret=pe/ps-1.0
  d="UP" if ret>0 else ("DOWN" if ret<0 else "FLAT")
  if abs(float(r.start_price)-ps)>1e-9:errs.append((r.label_date,r.partition,r.window,"START_PRICE"))
  if abs(float(r.end_price)-pe)>1e-9:errs.append((r.label_date,r.partition,r.window,"END_PRICE"))
  if abs(float(r.return)-ret)>1e-12:errs.append((r.label_date,r.partition,r.window,"RETURN"))
  if str(r.direction)!=d:errs.append((r.label_date,r.partition,r.window,"DIRECTION"))
 if errs: raise RuntimeError(f"V5_TARGET_REPRO_FAIL n={len(errs)} sample={errs[:10]}")
 return q

def align_features(targets,hf):
 t=targets.copy()
 t["start_utc"]=pd.to_datetime(t.start_utc,utc=True)
 t["end_utc"]=pd.to_datetime(t.end_utc,utc=True)
 # select latest hourly close whose availability time <= session start.
 left=t.sort_values("start_utc")
 right=hf.sort_values("available_at_utc")
 out=pd.merge_asof(left,right,left_on="start_utc",right_on="available_at_utc",direction="backward")
 out["feature_lag_minutes"]=(out.start_utc-out.available_at_utc).dt.total_seconds()/60.0
 out["feature_bar_open_utc"]=out.ts
 out["feature_bar_close_available_utc"]=out.available_at_utc
 if (out.feature_bar_close_available_utc>out.start_utc).any():raise RuntimeError("HOURLY_FEATURE_LEAK")
 # Never use target outcome before it matured.
 out["y_up"]=(out.direction=="UP").astype(int)
 return out.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def model():
 return Pipeline([
  ("scale",StandardScaler()),
  ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))
 ])

def metrics(y,p):
 y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6); pred=(p>=.5).astype(int)
 tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
 return {
  "n":int(len(y)),"accuracy":float(np.mean(pred==y)),
  "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
  "brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,p,labels=[0,1])),
  "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
  "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
  "tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp),
  "prediction_std":float(np.std(p))
 }

def replay_window(g):
 g=g.sort_values("start_utc").reset_index(drop=True)
 rows=[]
 # Evaluate 2023-2024 only. Training may use earlier 2023 rows, but a row is scored only after MIN_TRAIN matured same-window outcomes exist.
 test=g[g.start_utc.dt.year.isin([2023,2024])].copy()
 for bs in range(0,len(test),BLOCK):
  te=test.iloc[bs:bs+BLOCK].copy()
  if te.empty:continue
  cutoff=te.start_utc.min()
  tr=g[(g.end_utc<=cutoff)&(g.start_utc<te.start_utc.min())].copy()
  tr=tr[tr.start_utc.dt.year.isin([2023,2024])]
  if len(tr)<MIN_TRAIN:continue
  Xtr=tr[ALL_HOURLY].astype(float)
  Xte=te[ALL_HOURLY].astype(float)
  ytr=tr.y_up.to_numpy(int)
  m=model();m.fit(Xtr,ytr)
  p=m.predict_proba(Xte)[:,1]
  for r,pp in zip(te.itertuples(index=False),p):
   rows.append({
    "label_date":r.label_date,"partition":r.partition,"window":r.window,
    "start_utc":r.start_utc.isoformat(),"end_utc":r.end_utc.isoformat(),
    "feature_bar_open_utc":r.feature_bar_open_utc.isoformat(),
    "feature_available_utc":r.feature_bar_close_available_utc.isoformat(),
    "feature_lag_minutes":float(r.feature_lag_minutes),
    "year":int(r.start_utc.year),"y_up":int(r.y_up),"direction":r.direction,
    "p_up":float(pp),"pred":"UP" if pp>=.5 else "DOWN","train_n":int(len(tr))
   })
 return pd.DataFrame(rows)

def main():
 rawh=load_hourly_raw()
 if rawh.ts.min()>pd.Timestamp("2022-01-03",tz="UTC") or rawh.ts.max()<pd.Timestamp("2024-12-31 20:00",tz="UTC"):
  raise RuntimeError(f"HOURLY_COVERAGE_FAIL {rawh.ts.min()} {rawh.ts.max()}")
 hf=build_hourly_features(rawh)
 targets=verify_targets()
 # Hard quarantine: 2025 remains unopened for this first development replay.
 targets=targets[pd.to_datetime(targets.label_date).dt.year.isin([2023,2024])].copy()
 panel=align_features(targets,hf)
 panel=panel.dropna(subset=ALL_HOURLY+["direction"]).copy()
 panel.to_csv(OUT/"iris_hourly_raw_feature_panel_2023_2024.csv",index=False)

 preds=[]
 for (part,win),g in panel.groupby(["partition","window"],sort=True):
  z=replay_window(g)
  if not z.empty:preds.append(z)
 pred=pd.concat(preds,ignore_index=True) if preds else pd.DataFrame()
 pred.to_csv(OUT/"iris_hourly_raw_predictions_2023_2024.csv",index=False)

 mrows=[]
 if not pred.empty:
  for (part,win,yr),g in pred.groupby(["partition","window","year"],sort=True):
   mrows.append({"partition":part,"window":win,"period":str(yr),**metrics(g.y_up,g.p_up)})
  for (part,win),g in pred.groupby(["partition","window"],sort=True):
   mrows.append({"partition":part,"window":win,"period":"2023-2024_SCORED",**metrics(g.y_up,g.p_up)})
 mdf=pd.DataFrame(mrows)
 mdf.to_csv(OUT/"iris_hourly_raw_metrics_2023_2024.csv",index=False)

 cov=[]
 for (part,win),g in panel.groupby(["partition","window"],sort=True):
  p=pred[(pred.partition==part)&(pred.window==win)] if not pred.empty else pd.DataFrame()
  cov.append({
   "partition":part,"window":win,"feature_rows_2023_2024":int(len(g)),
   "scored_rows":int(len(p)),
   "first_feature_start":None if g.empty else str(g.start_utc.min()),
   "first_scored_start":None if p.empty else str(p.start_utc.min()),
   "last_scored_start":None if p.empty else str(p.start_utc.max()),
   "median_feature_lag_minutes":float(g.feature_lag_minutes.median()) if len(g) else None
  })

 summary={
  "status":"IRIS_HOURLY_RAW_SESSION_REPLAY_V1_COMPLETE",
  "scope":"Correctly runnable IRIS hourly-only branch; full A1+PATH IRIS remains blocked pending pre-2023 session-target training history or separately governed structural warm-up.",
  "raw_sources":{
   "hourly_neon_series_id":SERIES_ID,
   "hourly_first":str(rawh.ts.min()),"hourly_last":str(rawh.ts.max()),"hourly_rows":int(len(rawh)),
   "target_raw_15m":RAW15.name,"target_raw_15m_sha256":sha(RAW15)
  },
  "feature_semantics":"Hourly API datetime is bar-open and stored value is bar-close; feature is usable only at ts+1h. Latest completed hourly close <= target start is used.",
  "target_reproduction":"PASS",
  "training":{
   "model":"original IRIS HOURLY_ONLY_ALL Logistic L2 candidate",
   "features":ALL_HOURLY,"block":BLOCK,"min_matured_same_window_train":MIN_TRAIN,
   "evaluation":"2023-2024 only; 2025 not read for scoring/selection"
  },
  "coverage":cov,
  "metrics":mdf.to_dict("records"),
  "full_iris_status":"BLOCKED_PRE2023_SESSION_TARGET_HISTORY_FOR_STRUCTURAL_A1",
  "guardrails":[
   "No historical IRIS FEATURE_PANEL/PREDICTIONS/STATE/SCORES file used as model input.",
   "V5 target reconstructed from raw 15m before fitting.",
   "No hourly bar whose close occurs after target start is used.",
   "2025 outcomes are not used in this replay."
  ]
 }
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
 lines=["# IRIS SESSION RAW REPLAY V1 — HOURLY BRANCH","",
  "**Status:** IRIS hourly-only branch completed from raw sources.","",
  "- Historical derived IRIS files used as input: **NO**",
  "- V5 targets independently reconstructed from raw 15m: **PASS**",
  "- Hourly close availability leakage check: **PASS**",
  "- Scoring: **2023-2024 only**",
  "- 2025: **UNOPENED in this replay**","",
  "## Important limitation","",
  "The original full IRIS A1+PATH candidate needs a structural A1 logit. Rebuilding that logit against the new session targets requires sufficient earlier session-target history. The current governed V5 target history begins in 2023, so the full structural branch is not silently substituted with old H3 predictions.",
  "",
  "## Metrics","",
  "| Partition | Window | Period | N | Accuracy | Balanced | UP recall | DOWN recall | Brier |",
  "|---|---|---|---:|---:|---:|---:|---:|---:|"]
 for r in mdf.itertuples(index=False):
  lines.append(f"| {r.partition} | {r.window} | {r.period} | {int(r.n)} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
 (OUT/"result.md").write_text("\n".join(lines)+"\n")
 print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":main()
