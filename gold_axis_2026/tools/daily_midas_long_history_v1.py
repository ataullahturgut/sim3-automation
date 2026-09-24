from __future__ import annotations
import argparse, calendar, json, math, os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd, psycopg
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

IDENTITY="GOLD_CONTROL_DAILY_MIDAS_LONG_HISTORY_V1_RESEARCH"
METALS=("Gold","Silver","Platinum","Palladium")
SIDS={"Gold":"XAU_STAKTRAKR_RESEARCH_DAILY_R1","Silver":"XAG_STAKTRAKR_RESEARCH_DAILY_R1","Platinum":"XPT_STAKTRAKR_RESEARCH_DAILY_R1","Palladium":"XPD_STAKTRAKR_RESEARCH_DAILY_R1"}
GPR="GPR_OFFICIAL_GIT_PIT"
FAST_LAGS=60; SLOW_LAGS=12; MIN_TRAIN=250; TAIL_MIN=120; TAIL_Q=.67
PRED_START=pd.Timestamp("2022-01-01")

def mk(x): return x[:7] if isinstance(x,str) else f"{x.year:04d}-{x.month:02d}"
def mshift(m,d):
 y,mo=map(int,m.split("-")); z=y*12+mo-1+d; return f"{z//12:04d}-{z%12+1:02d}"
def mend(m):
 y,mo=map(int,m.split("-")); return datetime(y,mo,calendar.monthrange(y,mo)[1],23,59,59,tzinfo=timezone.utc)

def invariants(cur):
 out={}
 for n in ("monthly_forecast_contracts","decision_signal_snapshots","decision_runs","decision_events"):
  cur.execute(f"select count(*) from {n}"); out[n]=int(cur.fetchone()[0])
 return out

def load(cur):
 raw={}
 for metal,sid in SIDS.items():
  cur.execute("select observation_ts,value from observations where series_id=%s order by observation_ts",(sid,))
  raw[metal]={ts.date():float(v) for ts,v in cur.fetchall()}
 common=sorted(set.intersection(*(set(raw[m]) for m in METALS)))
 d=pd.DataFrame({"date":pd.to_datetime(common)})
 for m in METALS: d[m]=[raw[m][x] for x in common]
 for m in METALS: d[f"r_{m}"]=np.log(d[m]/d[m].shift(1))
 d["abs_Gold"]=d["r_Gold"].abs(); d["neg_Gold"]=np.minimum(d["r_Gold"],0)
 d["target_date"]=d["date"].shift(-1); d["r_next"]=np.log(d["Gold"].shift(-1)/d["Gold"])
 d=d[d.target_date.notna() & np.isfinite(d.r_next)].reset_index(drop=True)

 # completed monthly return maps from same four-series source
 monthly={}
 for metal in METALS:
  g=d.groupby(d["date"].dt.to_period("M"))[metal].mean()
  rr=np.log(g/g.shift(1))
  monthly[metal]={str(k):float(v) for k,v in rr.items() if np.isfinite(v)}

 cur.execute("select observation_ts,value,available_as_of,metadata->>'origin_month' from observations where series_id=%s order by metadata->>'origin_month',observation_ts",(GPR,))
 vint=defaultdict(dict); avail={}
 for ts,v,a,om in cur.fetchall():
  if not om: continue
  vint[om][mk(ts)]=float(v); avail[om]=min(avail.get(om,a),a)
 return d,monthly,dict(vint),avail,{"common_daily_n":len(common),"first":common[0].isoformat(),"last":common[-1].isoformat(),"gpr_vintages":len(vint)}

def basis(seq):
 x=np.asarray(seq,float); ok=np.isfinite(x)
 if len(x)<2 or ok.mean()<.5:return [np.nan]*3
 x=np.where(ok,x,float(np.nanmedian(x[ok]))); u=np.linspace(0,1,len(x))
 return [float(np.mean(x)),float(np.mean(x*(1-2*u))),float(np.mean(x*(6*u*u-6*u+1)))]

def monthseq(mp,metal,od,L):
 cur=mshift(mk(od),-1); vals=[]
 for _ in range(L):
  if cur not in mp[metal]: return None
  vals.append(mp[metal][cur]); cur=mshift(cur,-1)
 return vals

def gprseq(vint,avail,od,L):
 m=mk(od); vo=mshift(m,-1); h=vint.get(vo)
 if h is None or avail.get(vo) is None or avail[vo]>mend(vo):return None
 cur=mshift(m,-2); vals=[]
 for _ in range(L):
  if cur not in h:return None
  vals.append(h[cur]); cur=mshift(cur,-1)
 return vals

def panelize(d,monthly,vint,avail):
 arr={c:d[c].to_numpy(float) for c in [f"r_{m}" for m in METALS]+["abs_Gold","neg_Gold"]}
 rows=[]
 for i,r in d.iterrows():
  if i<FAST_LAGS-1: continue
  z={"origin_date":pd.Timestamp(r.date),"target_date":pd.Timestamp(r.target_date),"r_next":float(r.r_next)}
  for c,a in arr.items():
   for j,v in enumerate(basis(a[i-FAST_LAGS+1:i+1][::-1])): z[f"F_{c}_A{j}"]=v
  sok=True
  for m in METALS:
   s=monthseq(monthly,m,r.date,SLOW_LAGS)
   if s is None: sok=False; break
   for j,v in enumerate(basis(s)): z[f"M_{m}_A{j}"]=v
  gs=gprseq(vint,avail,r.date,SLOW_LAGS)
  if gs is None:sok=False
  else:
   for j,v in enumerate(basis(gs)):z[f"M_GPR_A{j}"]=v
  z["slow_available"]=sok; rows.append(z)
 p=pd.DataFrame(rows).sort_values("origin_date").reset_index(drop=True)
 p["tail_cutoff"]=p.r_next.abs().shift(1).expanding(min_periods=252).quantile(TAIL_Q)
 p["y_up"]=(p.r_next>0).astype(int)
 p["y_tail_up"]=(p.r_next>p.tail_cutoff).astype(int); p["y_tail_down"]=(p.r_next<-p.tail_cutoff).astype(int)
 return p

def logit():return Pipeline([("i",SimpleImputer(strategy="median")),("s",StandardScaler()),("m",LogisticRegression(C=1,solver="lbfgs",max_iter=3000,random_state=0))])
def ridge():return Pipeline([("i",SimpleImputer(strategy="median")),("s",StandardScaler()),("m",Ridge(alpha=1))])

def walk(p,features):
 rows=[]
 for i,r in p.iterrows():
  if r.origin_date<PRED_START:continue
  h=p.iloc[:i]
  if len(h)<MIN_TRAIN:continue
  X=h[features]; x=p.loc[[i],features]; y=h.y_up.to_numpy(int)
  if len(np.unique(y))<2:continue
  lm=logit().fit(X,y); pr=float(lm.predict_proba(x)[0,1])
  rm=ridge().fit(X,h.r_next); rh=float(rm.predict(x)[0])
  th=h[np.isfinite(h.tail_cutoff)]
  if len(th)<TAIL_MIN:continue
  up=logit().fit(th[features],th.y_tail_up); dn=logit().fit(th[features],th.y_tail_down)
  pu=float(up.predict_proba(x)[0,1]); pdn=float(dn.predict_proba(x)[0,1])
  rows.append({"origin_date":r.origin_date.strftime("%Y-%m-%d"),"target_date":r.target_date.strftime("%Y-%m-%d"),"r_next":float(r.r_next),"actual_up":int(r.y_up),
   "actual_tail_up":int(r.y_tail_up),"actual_tail_down":int(r.y_tail_down),"p_up":pr,"rhat":rh,"p_tail_up":pu,"p_tail_down":pdn,"margin":pu-pdn,"train_n":len(h),"tail_train_n":len(th)})
 return pd.DataFrame(rows)

def div(a,b):return None if b==0 else float(a/b)
def dm(g,score,pred):
 y=g.actual_up.to_numpy(int); yh=np.asarray(pred,int); sc=np.asarray(score,float)
 tp=int(((yh==1)&(y==1)).sum());fp=int(((yh==1)&(y==0)).sum());tn=int(((yh==0)&(y==0)).sum());fn=int(((yh==0)&(y==1)).sum())
 ur=div(tp,tp+fn); dr=div(tn,tn+fp); fpr=div(fp,fp+tn)
 return {"n":len(g),"tp":tp,"fp":fp,"tn":tn,"fn":fn,"up_precision":div(tp,tp+fp),"up_recall":ur,"false_up_fpr":fpr,"down_recall":dr,
 "balanced_accuracy":None if ur is None or dr is None else (ur+dr)/2,"auc":float(roc_auc_score(y,sc)) if len(np.unique(y))==2 else None,"youden_j":None if ur is None else ur-fpr}
def tm(g,label,score):
 y=g[label].to_numpy(int); s=np.asarray(score,float); pred=(s>=.5).astype(int)
 if len(np.unique(y))<2:return {"n":len(g),"auc":None}
 tp=int(((pred==1)&(y==1)).sum());fp=int(((pred==1)&(y==0)).sum());tn=int(((pred==0)&(y==0)).sum());fn=int(((pred==0)&(y==1)).sum())
 return {"n":len(g),"positive_n":int(y.sum()),"auc":float(roc_auc_score(y,s)),"brier":float(brier_score_loss(y,s)),"calls":int(pred.sum()),"precision":div(tp,tp+fp),"recall":div(tp,tp+fn),"fpr":div(fp,fp+tn)}
def metrics(pr):
 out={}
 for name,years in {"2022":["2022"],"2023":["2023"],"2024":["2024"],"PRE2025":["2022","2023","2024"],"2025":["2025"],"2026":["2026"]}.items():
  g=pr[pr.origin_date.str[:4].isin(years)]
  if g.empty:continue
  out[name]={"logistic":dm(g,g.p_up,g.p_up>=.5),"ridge":dm(g,g.rhat,g.rhat>0),"two_head":dm(g,g.margin,g.margin>=0),
   "tail_up":tm(g,"actual_tail_up",g.p_tail_up),"tail_down":tm(g,"actual_tail_down",g.p_tail_down)}
 return out

def run(dsn):
 with psycopg.connect(dsn,autocommit=True) as conn:
  with conn.cursor() as cur:
   cur.execute("set default_transaction_read_only=on"); before=invariants(cur); d,monthly,vint,avail,src=load(cur)
 p=panelize(d,monthly,vint,avail)
 fast=[c for c in p if c.startswith("F_")]; slow=[c for c in p if c.startswith("M_")]
 pf=p.copy(); pm=p[p.slow_available].reset_index(drop=True)
 rf=walk(pf,fast); rm=walk(pm,fast+slow)
 with psycopg.connect(dsn,autocommit=True) as conn:
  with conn.cursor() as cur:cur.execute("set default_transaction_read_only=on"); after=invariants(cur)
 return {"identity":IDENTITY,"status":"RESEARCH_ONLY_NOT_RUNTIME","source":src,"panel":{"n":len(p),"mixed_n":len(pm),"first":p.origin_date.min().strftime("%Y-%m-%d"),"last":p.origin_date.max().strftime("%Y-%m-%d"),"fast_features":len(fast),"slow_features":len(slow)},
  "method":{"random_split":False,"hyperparameter_search":"NONE","2025_tuning":False,"2026_tuning":False,"target":"next common daily Gold return from original VW-MIDAS metal spine","tail_q":TAIL_Q},
  "FAST_ONLY":{"metrics":metrics(rf),"rows":rf.to_dict("records")},"MIXED_FREQ_MIDAS":{"metrics":metrics(rm),"rows":rm.to_dict("records")},
  "authority_invariants_unchanged":before==after,"governance":{"db_writes":"NONE","runtime":"NONE","canonical_modified":False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIDAS_LONG_HISTORY_V1_RESULT_2026-09-24.json");a=ap.parse_args()
 dsn=os.environ.get("NEON_DATABASE_URL")
 if not dsn:raise SystemExit("NEON_DATABASE_URL required")
 o=run(dsn);Path(a.out).write_text(json.dumps(o,indent=2,default=str))
 print(json.dumps({"identity":o["identity"],"source":o["source"],"panel":o["panel"],"FAST":o["FAST_ONLY"]["metrics"],"MIXED":o["MIXED_FREQ_MIDAS"]["metrics"],"invariants":o["authority_invariants_unchanged"]},indent=2,default=str))
if __name__=="__main__":main()
