from __future__ import annotations
import argparse, io, json, math, os, urllib.request, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss, matthews_corrcoef
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

IDENTITY="GOLD_CONTROL_TECHNICAL_AND_MACRO_TREE_PILOT_V1_RESEARCH"
START=pd.Timestamp("2022-03-01")
END=pd.Timestamp("2026-09-01")
MIN_TRAIN=252
REFIT_EVERY=20
EPS=1e-12

FRED_SERIES={
 "USD_BROAD":"DTWEXBGS",
 "TBILL_3M":"DGS3MO",
 "UST_2Y":"DGS2",
 "UST_10Y":"DGS10",
 "REAL_10Y":"DFII10",
 "BE_10Y":"T10YIE",
 "VIX":"VIXCLS",
 "OVX":"OVXCLS",
 "WTI":"DCOILWTICO",
}
LEVEL_SERIES={"TBILL_3M","UST_2Y","UST_10Y","REAL_10Y","BE_10Y"}
PRICE_LIKE={"USD_BROAD","VIX","OVX","WTI"}

def authority(cur):
 out={}
 for n in ("monthly_forecast_contracts","decision_signal_snapshots","decision_runs","decision_events"):
  cur.execute(f"select count(*) from {n}"); out[n]=int(cur.fetchone()[0])
 return out

def load_ny17(cur):
 cur.execute("""select observation_ts,value,available_as_of
                from observations
                where series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1'
                order by observation_ts""")
 d=pd.DataFrame(cur.fetchall(),columns=["ts","close","available_as_of"])
 d["ts"]=pd.to_datetime(d.ts,utc=True)
 d["date"]=d.ts.dt.tz_convert("America/New_York").dt.date
 d["date"]=pd.to_datetime(d.date)
 d["close"]=pd.to_numeric(d.close,errors="coerce")
 d=d[np.isfinite(d.close)].sort_values("ts").groupby("date",as_index=False).tail(1).sort_values("date").reset_index(drop=True)
 # Weekday-only provider sessions; no silent jump across >4 calendar days.
 d=d[d.date.dt.weekday<5].copy().reset_index(drop=True)
 d["target_date"]=d.date.shift(-1); d["target_close"]=d.close.shift(-1)
 d["gap_days"]=(d.target_date-d.date).dt.days
 d=d[d.target_date.notna() & d.gap_days.between(1,4)].copy().reset_index(drop=True)
 d["r_next"]=np.log(d.target_close/d.close)
 d["flat"]=(d.r_next.abs()<1e-12)
 d["y_up"]=np.where(d.flat,np.nan,(d.r_next>0).astype(int))
 return d

def load_intraday(cur):
 sql=r"""
 with raw as (
   select observation_ts,close::double precision as close,
          ((observation_ts at time zone 'America/New_York') + interval '7 hours')::date as trade_date,
          date_bin(interval '5 minutes',observation_ts,timestamptz '2000-01-01 00:00:00+00') as b5
   from xau_intraday_research_cache_1m
   where observation_ts >= timestamptz '2021-01-01 00:00:00+00'
     and observation_ts < timestamptz '2026-09-02 00:00:00+00'
     and close>0
 ), five as (
   select distinct on (trade_date,b5) trade_date,b5,observation_ts,close
   from raw order by trade_date,b5,observation_ts desc
 ), rr as (
   select trade_date,b5,close,ln(close/lag(close) over(partition by trade_date order by b5)) r5
   from five
 )
 select trade_date,
        min(close) lo,max(close) hi,
        min(close) filter(where b5=(select min(x.b5) from five x where x.trade_date=rr.trade_date)) as open_approx,
        max(close) filter(where b5=(select max(x.b5) from five x where x.trade_date=rr.trade_date)) as close_approx,
        sum(r5*r5) rv,
        sum(r5*r5) filter(where r5<0) rs_minus,
        sum(r5*r5) filter(where r5>0) rs_plus,
        count(r5) n5
 from rr group by trade_date order by trade_date
 """
 cur.execute(sql)
 d=pd.DataFrame(cur.fetchall(),columns=["date","lo","hi","open_approx","close_approx","rv","rs_minus","rs_plus","n5"])
 d["date"]=pd.to_datetime(d.date)
 for c in d.columns[1:]:d[c]=pd.to_numeric(d[c],errors="coerce")
 d["range_pct"]=(d.hi-d.lo)/d.close_approx.replace(0,np.nan)
 d["close_location"]=(d.close_approx-d.lo)/(d.hi-d.lo).replace(0,np.nan)
 d["downside_share"]=d.rs_minus/d.rv.replace(0,np.nan)
 return d[["date","range_pct","close_location","rv","rs_minus","rs_plus","downside_share","n5"]]

def download_fred(series_id):
 url=f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
 with urllib.request.urlopen(url,timeout=60) as r:
  raw=r.read()
 d=pd.read_csv(io.BytesIO(raw))
 d.columns=["date","value"]
 d["date"]=pd.to_datetime(d.date,errors="coerce")
 d["value"]=pd.to_numeric(d.value,errors="coerce")
 return d.dropna(subset=["date"]).sort_values("date").reset_index(drop=True),url

def rsi(s,n=14):
 delta=s.diff()
 up=delta.clip(lower=0).ewm(alpha=1/n,adjust=False,min_periods=n).mean()
 dn=(-delta.clip(upper=0)).ewm(alpha=1/n,adjust=False,min_periods=n).mean()
 rs=up/dn.replace(0,np.nan)
 return 100-100/(1+rs)

def technical_panel(ny,intra):
 d=ny.copy().sort_values("date").reset_index(drop=True)
 c=d.close.astype(float)
 r=np.log(c/c.shift(1))
 d["ret1"]=r
 for k in (2,3,5,10,20):
  d[f"ret{k}"]=np.log(c/c.shift(k))
 d["rsi14"]=rsi(c,14)
 ema12=c.ewm(span=12,adjust=False,min_periods=12).mean()
 ema26=c.ewm(span=26,adjust=False,min_periods=26).mean()
 macd=ema12-ema26
 sig=macd.ewm(span=9,adjust=False,min_periods=9).mean()
 d["macd_pct"]=macd/c
 d["macd_signal_pct"]=sig/c
 d["macd_hist_pct"]=(macd-sig)/c
 for k in (5,10,20,50,100):
  ma=c.rolling(k,min_periods=k).mean()
  d[f"sma{k}_ratio"]=c/ma-1
 for k in (10,20,50):
  em=c.ewm(span=k,adjust=False,min_periods=k).mean()
  d[f"ema{k}_ratio"]=c/em-1
 ma20=c.rolling(20,min_periods=20).mean()
 sd20=c.rolling(20,min_periods=20).std()
 d["boll_z"]=(c-ma20)/sd20.replace(0,np.nan)
 d["boll_width"]=(4*sd20)/ma20.replace(0,np.nan)
 for k in (5,10,20):
  d[f"roc{k}"]=c/c.shift(k)-1
 for k in (5,10,20,60):
  d[f"vol{k}"]=r.rolling(k,min_periods=k).std()
 for k in (10,20):
  d[f"downshare{k}"]=(r<0).rolling(k,min_periods=k).mean()
 d["skew20"]=r.rolling(20,min_periods=20).skew()
 for k in (20,60):
  d[f"drawdown{k}"]=c/c.rolling(k,min_periods=k).max()-1
 d["dow"]=d.date.dt.weekday
 d["month"]=d.date.dt.month
 d=d.merge(intra,on="date",how="left")
 return d

def macro_features():
 pieces=[];src={}
 for name,sid in FRED_SERIES.items():
  z,url=download_fred(sid);src[name]={"series_id":sid,"url":url,"first":z.date.min().strftime("%Y-%m-%d"),"last":z.date.max().strftime("%Y-%m-%d"),"n":int(z.value.notna().sum())}
  z=z.rename(columns={"value":name})
  pieces.append(z)
 all_dates=pd.DataFrame({"date":pd.date_range("2000-01-01","2026-09-30",freq="D")})
 d=all_dates
 for z in pieces:d=d.merge(z,on="date",how="left")
 # Carry last published market observation through holidays, then lag one full calendar/source day before use.
 for name in FRED_SERIES:
  s=d[name].ffill()
  if name in PRICE_LIKE:
   for k in (1,5,20):
    d[f"MX_{name}_r{k}"]=np.log(s/s.shift(k))
   d[f"MX_{name}_lvl"]=s
  else:
   d[f"MX_{name}_lvl"]=s
   for k in (1,5,20):d[f"MX_{name}_d{k}"]=s-s.shift(k)
 # curve slope
 d["MX_SLOPE10Y2Y"]=d["UST_10Y"].ffill()-d["UST_2Y"].ffill()
 # Strict lag by one calendar row: at origin date t use state through t-1 only.
 mx=[c for c in d if c.startswith("MX_")]
 d[mx]=d[mx].shift(1)
 return d[["date"]+mx],src

def feature_sets(p):
 exclude={"ts","date","close","available_as_of","target_date","target_close","gap_days","r_next","flat","y_up"}
 tech=[c for c in p.columns if c not in exclude and not c.startswith("MX_")]
 # remove raw fields/ids that aren't intended features
 tech=[c for c in tech if c not in {"lo","hi","open_approx","close_approx"}]
 macro=[c for c in p if c.startswith("MX_")]
 return tech,tech+macro

def models():
 return {
  "RF":RandomForestClassifier(n_estimators=300,max_depth=6,min_samples_leaf=8,max_features="sqrt",random_state=0,n_jobs=-1),
  "EXTRA_TREES":ExtraTreesClassifier(n_estimators=300,max_depth=7,min_samples_leaf=8,max_features="sqrt",random_state=0,n_jobs=-1),
  "HGB":HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=15,learning_rate=.05,l2_regularization=1.0,random_state=0),
  "XGBOOST":XGBClassifier(n_estimators=250,max_depth=3,learning_rate=.035,subsample=.85,colsample_bytree=.85,min_child_weight=5,reg_lambda=2.0,reg_alpha=0.0,objective="binary:logistic",eval_metric="logloss",random_state=0,n_jobs=2,tree_method="hist")
 }

def score(g):
 y=g.actual.to_numpy(int);p=g.prob.to_numpy(float);pred=(p>=.5).astype(int)
 tp=int(((pred==1)&(y==1)).sum());fp=int(((pred==1)&(y==0)).sum());tn=int(((pred==0)&(y==0)).sum());fn=int(((pred==0)&(y==1)).sum())
 div=lambda a,b:None if b==0 else float(a/b)
 rec=div(tp,tp+fn);fpr=div(fp,fp+tn);spec=div(tn,tn+fp)
 return {"n":int(len(g)),"actual_up":int(y.sum()),"actual_down":int((1-y).sum()),"tp":tp,"fp":fp,"tn":tn,"fn":fn,
  "up_precision":div(tp,tp+fp),"up_recall":rec,"false_up_fpr":fpr,"down_recall":spec,
  "balanced_accuracy":None if rec is None or spec is None else float((rec+spec)/2),
  "mcc":float(matthews_corrcoef(y,pred)) if len(np.unique(y))>1 and len(np.unique(pred))>1 else 0.0,
  "auc":float(roc_auc_score(y,p)) if len(np.unique(y))>1 else None,
  "ap":float(average_precision_score(y,p)) if len(np.unique(y))>1 else None,
  "brier":float(brier_score_loss(y,p)) if len(np.unique(y))>1 else None,
  "logloss":float(log_loss(y,np.clip(p,1e-6,1-1e-6),labels=[0,1])) if len(np.unique(y))>1 else None,
  "youden_j":None if rec is None or fpr is None else float(rec-fpr)}

def walk(panel,features,model_name):
 base=models()[model_name]
 rows=[]; fitted=None; last_fit_i=None
 # Complete-case support is fixed before the split so technical and macro variants are compared on identical rows.
 p=panel.dropna(subset=features+["y_up"]).copy().reset_index(drop=True)
 for i,r in p.iterrows():
  if r.target_date<START or r.target_date>=END:continue
  hist=p.iloc[:i].copy()
  hist=hist[hist.target_date<r.date]
  if len(hist)<MIN_TRAIN:continue
  if fitted is None or last_fit_i is None or (i-last_fit_i)>=REFIT_EVERY:
   fitted=base.__class__(**base.get_params())
   fitted.fit(hist[features],hist.y_up.astype(int))
   last_fit_i=i
  prob=float(fitted.predict_proba(p.loc[[i],features])[0,1])
  rows.append({"origin_date":r.date.strftime("%Y-%m-%d"),"target_date":r.target_date.strftime("%Y-%m-%d"),"actual":int(r.y_up),"prob":prob})
 return pd.DataFrame(rows)

def periods(pred):
 out={}
 for name,yrs in {"2023":["2023"],"2024":["2024"],"PRE2025":["2023","2024"],"2025":["2025"],"2026":["2026"]}.items():
  g=pred[pred.target_date.str[:4].isin(yrs)]
  if len(g):out[name]=score(g)
 return out

def run(dsn):
 with psycopg.connect(dsn,autocommit=True) as conn:
  with conn.cursor() as cur:
   cur.execute("set default_transaction_read_only=on");before=authority(cur);ny=load_ny17(cur);intra=load_intraday(cur)
 tech=technical_panel(ny,intra)
 macro,src=macro_features()
 p=tech.merge(macro,on="date",how="left")
 techf,macrof=feature_sets(p)
 # Equal support for experiment 1 vs 2: rows must have both technical and macro features.
 common=p.dropna(subset=techf+macrof+["y_up"]).copy().reset_index(drop=True)
 results={"TECHNICAL_TREE":{"features":techf,"models":{}},"MACRO_TECHNICAL_TREE":{"features":macrof,"models":{}}}
 for family,features in [("TECHNICAL_TREE",techf),("MACRO_TECHNICAL_TREE",macrof)]:
  for model_name in models():
   pred=walk(common,features,model_name)
   results[family]["models"][model_name]={"metrics":periods(pred),"prediction_n":int(len(pred))}
 with psycopg.connect(dsn,autocommit=True) as conn:
  with conn.cursor() as cur:cur.execute("set default_transaction_read_only=on");after=authority(cur)
 return {
  "identity":IDENTITY,"status":"RESEARCH_ONLY_NO_PROMOTION",
  "target":{"clock":"XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1","meaning":"next accepted weekday provider NY17-derived session; not canonical 16:59 minute close","flat_handling":"exact zero return excluded"},
  "panel":{"raw_ny17_n":int(len(ny)),"common_complete_n":int(len(common)),"first":common.date.min().strftime("%Y-%m-%d"),"last":common.date.max().strftime("%Y-%m-%d"),
           "technical_feature_n":len(techf),"macro_total_feature_n":len(macrof)},
  "external_macro_sources":src,
  "macro_governance":{"download":"current FRED historical snapshot","PIT_status":"NOT_PROVEN / NOT ALFRED VINTAGE","timing_safety":"all macro features lagged one full calendar/source day before origin","purpose":"research pilot only"},
  "method":{"random_split":False,"expanding_history":True,"refit_every_sessions":REFIT_EVERY,"min_train":MIN_TRAIN,
            "hyperparameter_tuning":"NONE; four predeclared fixed tree families","2025_tuning":False,"2026_tuning":False,
            "equal_support":"Technical and Macro+Technical are scored on identical complete rows"},
  "results":results,
  "authority_invariants_unchanged":before==after,
  "governance":{"database_writes":"NONE","canonical_modified":False,"runtime_promotion":"NONE"}
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="GOLD_CONTROL_TECHNICAL_AND_MACRO_TREE_PILOT_V1_RESULT_2026-09-25.json");a=ap.parse_args()
 dsn=os.environ.get("NEON_DATABASE_URL")
 if not dsn:raise SystemExit("NEON_DATABASE_URL required")
 o=run(dsn);Path(a.out).write_text(json.dumps(o,indent=2,default=str),encoding="utf-8")
 print(json.dumps({"identity":o["identity"],"status":o["status"],"panel":o["panel"],"macro":o["macro_governance"],"results":o["results"],"invariants":o["authority_invariants_unchanged"]},indent=2,default=str))
if __name__=="__main__":main()
