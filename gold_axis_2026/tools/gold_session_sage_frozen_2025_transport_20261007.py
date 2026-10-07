from __future__ import annotations
import importlib.util,json
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2];AX=ROOT/"gold_axis_2026"
V1=AX/"tools"/"gold_session_sage_v1_stage1_20261007.py"
WARM=AX/"GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
R22=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
R35=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_SAGE_FROZEN_2025_TRANSPORT_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v1=loadmod("sagev1",V1);res1h=v1.res1h;base=v1.base.base
NY=ZoneInfo("America/New_York");BLOCK=5;MIN=120;SEED=20261007

def raw():
 a=pd.read_csv(R22);b=pd.read_csv(R35)
 for q in (a,b):
  q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True)
  for c in ["open","high","low","close"]:q[c]=pd.to_numeric(q[c],errors="raise")
 q=pd.concat([a,b],ignore_index=True).sort_values("dt_utc")
 d=q[q.duplicated("dt_utc",keep=False)]
 if not d.empty:
  for c in ["open","high","low","close"]:
   if d.groupby("dt_utc")[c].nunique().gt(1).any():raise RuntimeError("RAW_OVERLAP_CONFLICT")
 return q.drop_duplicates("dt_utc",keep="last").reset_index(drop=True)

def targets():
 w=pd.read_csv(WARM);w=w[w.final_trainable.astype(str).str.lower().eq("true")]
 z=[]
 for p in [WGC,SOB]:
  q=pd.read_csv(p);q=q[q.final_trainable.astype(str).str.lower().eq("true")];z.append(q)
 q=pd.concat([w]+z,ignore_index=True,sort=False)
 q["start_utc"]=pd.to_datetime(q.start_utc,utc=True);q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
 q["year"]=q.start_utc.dt.year;q["y_up"]=(q.direction=="UP").astype(int)
 return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def ny(d,h,m=0):return pd.Timestamp(datetime(d.year,d.month,d.day,h,m,tzinfo=NY)).tz_convert("UTC")
def cycles(r):
 op=dict(zip(r.dt_utc,r.open.astype(float)));rows=[]
 for d in pd.date_range("2022-01-01","2025-12-31",freq="D").date:
  p=d-timedelta(days=1);ts=[ny(p,18),ny(d,3),ny(d,8),ny(d,12),ny(d,16)]
  if not all(t in op for t in ts):continue
  lp=np.log([op[t] for t in ts]);a,e,u1,u2=np.diff(lp);seq=np.array([a,e,u1,u2]);us=u1+u2;west=e+us;sg=np.sign(seq)
  rows.append({"sage_ready_utc":ny(d,16,15),"sess_asia":a,"sess_europe":e,"sess_us_am":u1,"sess_us_pm":u2,
   "sess_us_total":us,"sess_west_total":west,"sess_east_west":a-west,"sess_us_reversal":u2-u1,
   "sess_dispersion":float(np.std(seq)),"sess_sign_changes":float(np.sum(sg[1:]*sg[:-1]<0)),
   "sess_dominance":float(np.max(np.abs(seq))/(np.sum(np.abs(seq))+1e-10)),
   "sess_asia_us_interaction":float(a*us),"sess_east_west_conflict":float(a*west<0),"sess_us_conflict":float(u1*u2<0)})
 return pd.DataFrame(rows).sort_values("sage_ready_utc")

def x1h(r):
 q=r[["dt_utc","close"]].rename(columns={"dt_utc":"ts","close":"value"}).copy()
 q["hour"]=q.ts.dt.floor("1h");q["minute"]=q.ts.dt.minute;rows=[]
 for h,g in q.groupby("hour"):
  if len(g)==4 and tuple(sorted(set(map(int,g.minute))))==(0,15,30,45):
   rows.append({"ts":h,"available_at_utc":h+pd.Timedelta(hours=1),"value":float(g.sort_values("ts").iloc[-1].value)})
 return pd.DataFrame(rows)

def fit(tr,te,fs):
 X=tr[fs].astype(float).to_numpy();Y=te[fs].astype(float).to_numpy();sc=StandardScaler().fit(X)
 m=LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED).fit(sc.transform(X),tr.y_up.to_numpy(int))
 return m.predict_proba(sc.transform(Y))[:,1]

def replay(p):
 rows=[];f1=res1h.feature_names("g1h")
 for (part,win),g0 in p.groupby(["partition","window"],sort=True):
  if (part,win) not in {("WGC_2026_NY3","ASIA"),("SOBTI_5_ET","NY_LONDON_LIT"),("WGC_2026_NY3","US")}:continue
  g=g0.sort_values("start_utc").reset_index(drop=True);teall=g[g.year.eq(2025)].reset_index(drop=True)
  for bs in range(0,len(teall),BLOCK):
   te=teall.iloc[bs:bs+BLOCK];cut=te.start_utc.min();tr=g[(g.end_utc<=cut)&(g.start_utc<cut)]
   if len(tr)<MIN or tr.y_up.nunique()<2:continue
   models={}
   if (part,win)==("WGC_2026_NY3","ASIA"):models["S15_SESSION_ONLY"]=v1.SESSION_ALL
   else:
    models["S16_PATH_GLOBAL_MATCHED"]=f1;models["S16_PATH_SESSION"]=f1+v1.SESSION_ALL
   for name,fs in models.items():
    pp=fit(tr,te,fs)
    for r,pv in zip(te.itertuples(index=False),pp):
     rows.append({"model":name,"partition":part,"window":win,"label_date":r.label_date,"start_utc":r.start_utc,
                  "y_up":int(r.y_up),"p_up":float(pv),"train_n":len(tr)})
 return pd.DataFrame(rows)

def main():
 r=raw();p=targets()
 c=cycles(r);p=pd.merge_asof(p.sort_values("start_utc"),c,left_on="start_utc",right_on="sage_ready_utc",direction="backward",allow_exact_matches=False)
 if not (p.loc[p.sage_ready_utc.notna(),"sage_ready_utc"]<p.loc[p.sage_ready_utc.notna(),"start_utc"]).all():raise RuntimeError("SAGE_LEAK")
 p=res1h.attach(p,x1h(r),"g1h","1h")
 f1=res1h.feature_names("g1h");p=p.dropna(subset=v1.SESSION_ALL+f1+["direction"])
 pred=replay(p);rows=[]
 for (m,part,win),g in pred.groupby(["model","partition","window"]):
  rows.append({"model":m,"partition":part,"window":win,**base.metrics(g.y_up,g.p_up)})
 met=pd.DataFrame(rows);pairs=[]
 for part,win in [("SOBTI_5_ET","NY_LONDON_LIT"),("WGC_2026_NY3","US")]:
  a=pred[(pred.model=="S16_PATH_SESSION")&(pred.partition==part)&(pred.window==win)]
  b=pred[(pred.model=="S16_PATH_GLOBAL_MATCHED")&(pred.partition==part)&(pred.window==win)]
  z=a.merge(b,on=["partition","window","label_date","start_utc","y_up"],suffixes=("_c","_b"))
  mc=base.metrics(z.y_up,z.p_up_c);mb=base.metrics(z.y_up,z.p_up_b)
  pairs.append({"partition":part,"window":win,"n":len(z),"candidate_ba":mc["balanced_accuracy"],"comparator_ba":mb["balanced_accuracy"],
                "delta_ba_pp":100*(mc["balanced_accuracy"]-mb["balanced_accuracy"]),"candidate_brier":mc["brier"],"comparator_brier":mb["brier"]})
 pred.to_csv(OUT/"predictions.csv",index=False);met.to_csv(OUT/"metrics.csv",index=False);pd.DataFrame(pairs).to_csv(OUT/"paired.csv",index=False)
 s={"status":"SAGE_FROZEN_2025_TRANSPORT_COMPLETE","scope":"2025 only; frozen preregistered candidates; causal expanding updates",
    "metrics":rows,"paired":pairs,"guardrails":["Only WGC Asia S1.5 and Sobti NY/London + WGC US S1.6 were opened.","No feature/clock/C/threshold retuning.","2026 unopened."]}
 (OUT/"summary.json").write_text(json.dumps(s,indent=2)+"\n")
 print(json.dumps(s,indent=2))

if __name__=="__main__":main()
