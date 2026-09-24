from __future__ import annotations
import argparse, json, math, os, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss, matthews_corrcoef
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

IDENTITY="GOLD_CONTROL_DAILY_MIDAS_CLEAN_PILOT_V2_RESEARCH"
SERIES={
 "Gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1",
 "Silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1",
 "Platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1",
 "Palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
 "SP500":"SP500_FRED",
 "NY17H":"XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1",
 "GPR":"GPR_OFFICIAL_GIT_PIT",
}
FAST_LAGS=60
SLOW_LAGS=12
TAIL_Q=.67
MIN_TRAIN=252
START_SCORE=pd.Timestamp("2022-01-01")
END_SCORE=pd.Timestamp("2026-09-01")

def asdf(x):
 return pd.to_datetime(x,utc=True,errors="coerce")

def month_key(ts):
 t=pd.Timestamp(ts)
 return f"{t.year:04d}-{t.month:02d}"

def month_shift(m,delta):
 y,mo=map(int,m.split("-")); z=y*12+mo-1+delta
 return f"{z//12:04d}-{z%12+1:02d}"

def authority(cur):
 out={}
 for n in ("monthly_forecast_contracts","decision_signal_snapshots","decision_runs","decision_events"):
  cur.execute(f"SELECT count(*) FROM {n}"); out[n]=int(cur.fetchone()[0])
 return out

def load_scalar(cur,sid):
 cur.execute("SELECT observation_ts,value,available_as_of FROM observations WHERE series_id=%s ORDER BY observation_ts",(sid,))
 rows=cur.fetchall()
 if not rows:return pd.DataFrame(columns=["ts","value","available_as_of"])
 d=pd.DataFrame(rows,columns=["ts","value","available_as_of"])
 d["ts"]=asdf(d["ts"]);d["available_as_of"]=asdf(d["available_as_of"])
 d["value"]=pd.to_numeric(d["value"],errors="coerce")
 return d[np.isfinite(d["value"])].copy()

def load_gpr(cur):
 cur.execute("""SELECT observation_ts,value,available_as_of,metadata->>'origin_month'
                FROM observations WHERE series_id=%s
                ORDER BY available_as_of,observation_ts""",(SERIES["GPR"],))
 d=pd.DataFrame(cur.fetchall(),columns=["obs_ts","value","available_as_of","origin_month"])
 if d.empty:return d
 d["obs_ts"]=asdf(d.obs_ts); d["available_as_of"]=asdf(d.available_as_of)
 d["value"]=pd.to_numeric(d.value,errors="coerce")
 return d[np.isfinite(d.value)&d.available_as_of.notna()].copy()

def daily_map(d):
 # exact source date, one value per date; if duplicates retain last timestamp
 if d.empty:return pd.DataFrame(columns=["date","value","available_as_of"])
 z=d.sort_values("ts").copy()
 z["date"]=z.ts.dt.date
 z=z.groupby("date",as_index=False).tail(1).sort_values("date").reset_index(drop=True)
 z["date"]=pd.to_datetime(z["date"])
 return z[["date","value","available_as_of","ts"]]

def market_calendar_gate(d,label):
 z=d.sort_values("date").drop_duplicates("date",keep="last").reset_index(drop=True).copy()
 z["target_date"]=z.date.shift(-1)
 z["gap_days"]=(z.target_date-z.date).dt.days
 z["origin_weekday"]=z.date.dt.weekday
 z["target_weekday"]=z.target_date.dt.weekday
 # Conservative provider-business-session gate: weekdays only, next source session no more than 4 calendar days away.
 z["calendar_ok"]=(z.origin_weekday<5)&(z.target_weekday<5)&z.gap_days.between(1,4)
 audit={
  "label":label,"rows":int(len(z)),"first":z.date.min().strftime("%Y-%m-%d"),"last":z.date.max().strftime("%Y-%m-%d"),
  "weekend_origins":int((z.origin_weekday>=5).sum()),"weekend_targets":int((z.target_weekday>=5).sum()),
  "gap_gt4":int((z.gap_days>4).fillna(False).sum()),"calendar_ok_rows":int(z.calendar_ok.sum()),
  "max_gap_days":int(z.gap_days.dropna().max()) if z.gap_days.notna().any() else None,
 }
 return z[z.calendar_ok].copy().reset_index(drop=True),audit

def almon2(x):
 x=np.asarray(x,float)
 ok=np.isfinite(x)
 if ok.mean()<.75:return [np.nan]*3
 med=float(np.nanmedian(x[ok]));x=np.where(ok,x,med)
 u=np.linspace(0,1,len(x))
 return [float(np.mean(x)),float(np.mean(x*(1-2*u))),float(np.mean(x*(6*u*u-6*u+1)))]

def exp_basis(x):
 x=np.asarray(x,float)
 ok=np.isfinite(x)
 if ok.mean()<.75:return [np.nan]*2
 med=float(np.nanmedian(x[ok]));x=np.where(ok,x,med)
 age=np.arange(len(x),dtype=float)
 out=[]
 for half in (5.0,20.0):
  w=np.exp(-math.log(2)*age/half);w/=w.sum();out.append(float(w@x))
 return out

def gpr_features_at(gpr,origin_date):
 # Row-level PIT: only records actually available no later than the origin date 23:59 UTC.
 cutoff=pd.Timestamp(origin_date,tz="UTC")+pd.Timedelta(hours=23,minutes=59,seconds=59)
 h=gpr[gpr.available_as_of<=cutoff].copy()
 if h.empty:return None
 # For each observation month choose latest vintage that was actually available at cutoff.
 h["obs_month"]=h.obs_ts.dt.strftime("%Y-%m")
 h=h.sort_values(["obs_month","available_as_of"]).groupby("obs_month",as_index=False).tail(1)
 vals={r.obs_month:float(r.value) for r in h.itertuples()}
 cur=month_shift(month_key(origin_date),-1) # completed month before origin month
 seq=[]
 for _ in range(SLOW_LAGS):
  if cur not in vals:return None
  seq.append(vals[cur]);cur=month_shift(cur,-1)
 return almon2(seq)+exp_basis(seq)

def prepare_features(gold,metal_maps,sp500,gpr,target_kind):
 base=gold.copy()
 base["r"]=np.log(base.value/base.value.shift(1))
 base["abs_r"]=base.r.abs()
 base["neg_r"]=np.minimum(base.r,0.0)
 if target_kind=="proxy":
  # target on same provider's next accepted business session
  base["target_value"]=base.value.shift(-1)
  base["r_next"]=np.log(base.target_value/base.value)
 else:
  raise ValueError(target_kind)

 # maps for other daily sources
 other={}
 for name,z in metal_maps.items():
  q=z.copy();q[f"r_{name}"]=np.log(q.value/q.value.shift(1));other[name]=q.set_index("date")[f"r_{name}"]
 s=sp500.copy();s["r_SP500"]=np.log(s.value/s.value.shift(1));sp=s.set_index("date")["r_SP500"]

 rows=[]
 arrays={"Gold":base.r.to_numpy(float),"GoldAbs":base.abs_r.to_numpy(float),"GoldNeg":base.neg_r.to_numpy(float)}
 for i,r in base.iterrows():
  if i<FAST_LAGS-1 or not np.isfinite(r.r_next):continue
  od=pd.Timestamp(r.date)
  z={"origin_date":od,"target_date":pd.Timestamp(r.target_date),"r_next":float(r.r_next)}
  # Gold fast features
  for key,a in arrays.items():
   seq=a[i-FAST_LAGS+1:i+1][::-1]
   for j,v in enumerate(almon2(seq)):z[f"G_{key}_A{j}"]=v
   for j,v in enumerate(exp_basis(seq)):z[f"G_{key}_E{j}"]=v
  # other metals: current/origin date observation required
  ok=True
  for name,ser in other.items():
   hist=ser.loc[:od].tail(FAST_LAGS)
   if len(hist)<FAST_LAGS or od not in ser.index:ok=False;break
   seq=hist.to_numpy(float)[::-1]
   for j,v in enumerate(almon2(seq)):z[f"M_{name}_A{j}"]=v
   for j,v in enumerate(exp_basis(seq)):z[f"M_{name}_E{j}"]=v
  z["metals_ok"]=ok
  # SP500 is deliberately lagged one source date to avoid same-close timing ambiguity.
  sph=sp.loc[sp.index<od].tail(FAST_LAGS)
  spok=len(sph)>=FAST_LAGS
  if spok:
   seq=sph.to_numpy(float)[::-1]
   for j,v in enumerate(almon2(seq)):z[f"X_SP500_A{j}"]=v
   for j,v in enumerate(exp_basis(seq)):z[f"X_SP500_E{j}"]=v
  z["sp500_ok"]=spok
  gf=gpr_features_at(gpr,od)
  z["gpr_ok"]=gf is not None
  if gf is not None:
   for j,v in enumerate(gf):z[f"S_GPR_{j}"]=v
  rows.append(z)
 p=pd.DataFrame(rows).sort_values("origin_date").reset_index(drop=True)
 return p

def ny17_panel(ny17,metal_maps,sp500,gpr):
 # Separate research clock. Target is next accepted NY17-derived provider session.
 z,audit=market_calendar_gate(ny17,"NY17_HOURLY_DERIVED_RESEARCH_CLOCK")
 z["r_next"]=np.log(z.value.shift(-1)/z.value)
 # after gate, recompute target carefully within accepted rows
 z["target_date"]=z.date.shift(-1);z["target_value"]=z.value.shift(-1);z["r_next"]=np.log(z.target_value/z.value)
 z=z[z.target_date.notna()].copy().reset_index(drop=True)
 z["r"]=np.log(z.value/z.value.shift(1));z["abs_r"]=z.r.abs();z["neg_r"]=np.minimum(z.r,0)
 rows=[]
 other={}
 for name,q in metal_maps.items():
  qq=q.copy();qq[f"r_{name}"]=np.log(qq.value/qq.value.shift(1));other[name]=qq.set_index("date")[f"r_{name}"]
 ss=sp500.copy();ss["r_SP500"]=np.log(ss.value/ss.value.shift(1));sp=ss.set_index("date")["r_SP500"]
 for i,r in z.iterrows():
  if i<FAST_LAGS-1 or not np.isfinite(r.r_next):continue
  od=pd.Timestamp(r.date);row={"origin_date":od,"target_date":pd.Timestamp(r.target_date),"r_next":float(r.r_next)}
  for key,col in [("Gold","r"),("GoldAbs","abs_r"),("GoldNeg","neg_r")]:
   seq=z[col].iloc[i-FAST_LAGS+1:i+1].to_numpy(float)[::-1]
   for j,v in enumerate(almon2(seq)):row[f"G_{key}_A{j}"]=v
   for j,v in enumerate(exp_basis(seq)):row[f"G_{key}_E{j}"]=v
  ok=True
  for name,ser in other.items():
   hist=ser.loc[ser.index<od].tail(FAST_LAGS) # lag one calendar source day due clock ambiguity
   if len(hist)<FAST_LAGS:ok=False;break
   seq=hist.to_numpy(float)[::-1]
   for j,v in enumerate(almon2(seq)):row[f"M_{name}_A{j}"]=v
   for j,v in enumerate(exp_basis(seq)):row[f"M_{name}_E{j}"]=v
  row["metals_ok"]=ok
  sph=sp.loc[sp.index<od].tail(FAST_LAGS);row["sp500_ok"]=len(sph)>=FAST_LAGS
  if row["sp500_ok"]:
   seq=sph.to_numpy(float)[::-1]
   for j,v in enumerate(almon2(seq)):row[f"X_SP500_A{j}"]=v
   for j,v in enumerate(exp_basis(seq)):row[f"X_SP500_E{j}"]=v
  gf=gpr_features_at(gpr,od);row["gpr_ok"]=gf is not None
  if gf is not None:
   for j,v in enumerate(gf):row[f"S_GPR_{j}"]=v
  rows.append(row)
 return pd.DataFrame(rows).sort_values("origin_date").reset_index(drop=True),audit

def add_targets(p):
 p=p.copy()
 p["y_up"]=(p.r_next>0).astype(int)
 # target-specific threshold computed only from already matured target returns.
 cuts=[]
 for i,r in p.iterrows():
  hist=p.iloc[:i]
  hist=hist[hist.target_date<r.origin_date]
  vals=hist.r_next.abs().dropna().to_numpy(float)
  cuts.append(float(np.quantile(vals,TAIL_Q)) if len(vals)>=252 else np.nan)
 p["tail_cutoff"]=cuts
 p["y_mat_down"]=(p.r_next < -p.tail_cutoff).astype(int)
 return p

def model_logit(kind):
 if kind=="L2":
  return Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler()),("m",LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=0))])
 if kind=="L1":
  return Pipeline([("imp",SimpleImputer(strategy="median")),("sc",StandardScaler()),("m",LogisticRegression(C=.25,penalty="l1",solver="liblinear",max_iter=5000,random_state=0))])
 raise ValueError(kind)

def model_hgb():
 return Pipeline([("imp",SimpleImputer(strategy="median")),("m",HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=7,learning_rate=.05,l2_regularization=1.0,random_state=0))])

def score(y,p,pred):
 y=np.asarray(y,int);p=np.asarray(p,float);pred=np.asarray(pred,int)
 tp=int(((pred==1)&(y==1)).sum());fp=int(((pred==1)&(y==0)).sum());tn=int(((pred==0)&(y==0)).sum());fn=int(((pred==0)&(y==1)).sum())
 div=lambda a,b: None if b==0 else float(a/b)
 tpr=div(tp,tp+fn);fpr=div(fp,fp+tn);tnr=div(tn,tn+fp)
 return {
  "n":int(len(y)),"positive":int(y.sum()),"negative":int((1-y).sum()),
  "tp":tp,"fp":fp,"tn":tn,"fn":fn,
  "precision":div(tp,tp+fp),"recall":tpr,"fpr":fpr,
  "specificity":tnr,"balanced_accuracy":None if tpr is None or tnr is None else float((tpr+tnr)/2),
  "mcc":float(matthews_corrcoef(y,pred)) if len(np.unique(pred))>1 and len(np.unique(y))>1 else 0.0,
  "auc":float(roc_auc_score(y,p)) if len(np.unique(y))>1 else None,
  "ap":float(average_precision_score(y,p)) if len(np.unique(y))>1 else None,
  "brier":float(brier_score_loss(y,p)) if len(np.unique(y))>1 else None,
  "logloss":float(log_loss(y,np.clip(p,1e-6,1-1e-6),labels=[0,1])) if len(np.unique(y))>1 else None,
  "youden_j":None if tpr is None or fpr is None else float(tpr-fpr)
 }

def walk(p,features,model_kind,target):
 rows=[]
 for i,r in p.iterrows():
  if r.origin_date<START_SCORE or r.origin_date>=END_SCORE:continue
  hist=p.iloc[:i].copy()
  hist=hist[hist.target_date<r.origin_date].copy()
  if target=="mat_down":
   hist=hist[np.isfinite(hist.tail_cutoff)].copy()
  if len(hist)<MIN_TRAIN:continue
  ycol="y_up" if target=="up" else "y_mat_down"
  y=hist[ycol].to_numpy(int)
  if len(np.unique(y))<2:continue
  X=hist[features];x=p.loc[[i],features]
  if model_kind in ("L2","L1"):m=model_logit(model_kind)
  else:m=model_hgb()
  m.fit(X,y);prob=float(m.predict_proba(x)[0,1])
  rows.append({"origin_date":r.origin_date.strftime("%Y-%m-%d"),"target_date":r.target_date.strftime("%Y-%m-%d"),
               "actual":int(r[ycol]),"prob":prob,"pred":int(prob>=.5),"r_next":float(r.r_next),"tail_cutoff":None if not np.isfinite(r.tail_cutoff) else float(r.tail_cutoff)})
 return pd.DataFrame(rows)

def periods(df):
 if df.empty:return {}
 out={}
 specs={"2022":["2022"],"2023":["2023"],"2024":["2024"],"PRE2025":["2022","2023","2024"],"2025":["2025"],"2026":["2026"]}
 for n,ys in specs.items():
  g=df[df.target_date.str[:4].isin(ys)]
  if g.empty:continue
  out[n]=score(g.actual,g.prob,g.pred)
 return out

def fit_block(p,features,name):
 res={"features":features,"models":{}}
 for kind in ("L2","L1","HGB"):
  up=walk(p,features,kind,"up")
  dn=walk(p,features,kind,"mat_down")
  res["models"][kind]={"UP":periods(up),"MAT_DOWN":periods(dn),"prediction_counts":{"UP":len(up),"MAT_DOWN":len(dn)}}
 return res

def build_equal_support(panel):
 p=add_targets(panel)
 # full support gate first; every ablation uses this exact row set.
 p=p[p.metals_ok & p.sp500_ok & p.gpr_ok].copy().reset_index(drop=True)
 # require all generated feature columns finite enough; imputer remains training-only for rare gaps.
 gold=[c for c in p if c.startswith("G_")]
 metals=[c for c in p if c.startswith("M_")]
 cross=[c for c in p if c.startswith("X_")]
 slow=[c for c in p if c.startswith("S_")]
 blocks={
  "GOLD_ONLY":gold,
  "GOLD_PLUS_METALS":gold+metals,
  "GOLD_PLUS_CROSS":gold+cross,
  "GOLD_PLUS_SLOW_MIDAS":gold+slow,
  "GOLD_METALS_CROSS":gold+metals+cross,
  "FULL_MIXED_FREQ_MIDAS":gold+metals+cross+slow,
 }
 return p,blocks

def run(dsn):
 with psycopg.connect(dsn,autocommit=True) as conn:
  with conn.cursor() as cur:
   cur.execute("SET default_transaction_read_only=on");before=authority(cur)
   raw={k:load_scalar(cur,v) for k,v in SERIES.items() if k!="GPR"}
   gpr=load_gpr(cur)
 # daily maps
 dm={k:daily_map(v) for k,v in raw.items()}
 # long proxy gold calendar
 proxy_base,proxy_cal=market_calendar_gate(dm["Gold"],"STAKTRAKR_PROXY_PROVIDER_BUSINESS_SESSION")
 # target must be recomputed after calendar filtering to avoid skipping excluded rows
 proxy_base["target_date"]=proxy_base.date.shift(-1);proxy_base["target_value"]=proxy_base.value.shift(-1)
 proxy_base=proxy_base[proxy_base.target_date.notna()].copy().reset_index(drop=True)
 metals={k:dm[k] for k in ("Silver","Platinum","Palladium")}
 proxy=prepare_features(proxy_base,metals,dm["SP500"],gpr,"proxy")
 proxy_eq,proxy_blocks=build_equal_support(proxy)

 ny17,ny17_cal=ny17_panel(dm["NY17H"],metals,dm["SP500"],gpr)
 ny17_eq,ny17_blocks=build_equal_support(ny17)

 results={}
 for clock,p,blocks in [("PROXY",proxy_eq,proxy_blocks),("NY17_RESEARCH",ny17_eq,ny17_blocks)]:
  results[clock]={"panel":{"n":len(p),"first":p.origin_date.min().strftime("%Y-%m-%d") if len(p) else None,
                           "last":p.origin_date.max().strftime("%Y-%m-%d") if len(p) else None,
                           "tail_ready":int(np.isfinite(p.tail_cutoff).sum())},
                  "blocks":{}}
  for name,features in blocks.items():
   results[clock]["blocks"][name]=fit_block(p,features,name)
 with psycopg.connect(dsn,autocommit=True) as conn:
  with conn.cursor() as cur:cur.execute("SET default_transaction_read_only=on");after=authority(cur)
 source={}
 for k,d in dm.items():
  source[k]={"n":len(d),"first":d.date.min().strftime("%Y-%m-%d") if len(d) else None,"last":d.date.max().strftime("%Y-%m-%d") if len(d) else None,
             "available_as_of_nonnull":int(d.available_as_of.notna().sum()) if "available_as_of" in d else 0}
 source["GPR"]={"n":len(gpr),"available_as_of_nonnull":int(gpr.available_as_of.notna().sum()) if len(gpr) else 0,
                "first_available_as_of":gpr.available_as_of.min().isoformat() if len(gpr) else None,
                "last_available_as_of":gpr.available_as_of.max().isoformat() if len(gpr) else None}
 return {
  "identity":IDENTITY,"status":"RESEARCH_ONLY_NO_PROMOTION",
  "source_audit":source,"calendar_audit":{"PROXY":proxy_cal,"NY17_RESEARCH":ny17_cal},
  "method":{
   "comparison_support":"ALL ABLATIONS USE SAME ROWS/TRAINING HISTORY WITHIN CLOCK",
   "proxy_clock":"STAKTRAKR provider business-session discovery only; not canonical NY17",
   "ny17_clock":"hourly-derived research clock; not claimed equal to canonical 16:59 minute close",
   "SP500_timing":"lagged strictly before origin date",
   "GPR_PIT":"row-level available_as_of <= origin cutoff; latest available vintage per observation month",
   "fast_lags":FAST_LAGS,"slow_lags":SLOW_LAGS,"tail_q":TAIL_Q,
   "model_families":["L2 logistic","L1 logistic fixed C=.25","small fixed HGB"],
   "hyperparameter_search":"NONE in V2; variants are predeclared and all reported",
   "random_split":False,"2025_tuning":False,"2026_tuning":False
  },
  "results":results,
  "authority_invariants_before":before,"authority_invariants_after":after,"authority_invariants_unchanged":before==after,
  "governance":{"database_writes":"NONE","canonical_modified":False,"runtime_promotion":"NONE"}
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIDAS_CLEAN_PILOT_V2_RESULT_2026-09-25.json");a=ap.parse_args()
 dsn=os.environ.get("NEON_DATABASE_URL")
 if not dsn:raise SystemExit("NEON_DATABASE_URL required")
 o=run(dsn);Path(a.out).write_text(json.dumps(o,indent=2,default=str),encoding="utf-8")
 slim={"identity":o["identity"],"status":o["status"],"source_audit":o["source_audit"],"calendar_audit":o["calendar_audit"],"method":o["method"],"results":o["results"],"invariants":o["authority_invariants_unchanged"]}
 print(json.dumps(slim,indent=2,default=str))
if __name__=="__main__":main()
