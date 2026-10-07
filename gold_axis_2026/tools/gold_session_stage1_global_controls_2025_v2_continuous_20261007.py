from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

ROOT=Path(__file__).resolve().parents[2];AX=ROOT/"gold_axis_2026"
A0P=AX/"tools"/"gold_session_nova_a0_core3_raw_replay_v1_20261006.py"
MA15P=AX/"tools"/"gold_session_iris15_crossmetal_v2_maintaware_20261006.py"
R1HP=AX/"tools"/"gold_session_iris_resolution_matched_v2_derivedxau_20261006.py"
WARM=AX/"GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
R22=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv";R35=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_OUT";OUT.mkdir(exist_ok=True)

def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a0=mod("a0",A0P);ma15=mod("ma15",MA15P);r1h=mod("r1h",R1HP);base=ma15.base
CORE3=list(a0.CORE3);BLOCK=5;RECENT=252;MINPATH=180;SEED=20261007

def targets():
 w=pd.read_csv(WARM);w=w[w.final_trainable.astype(str).str.lower().eq("true")]
 z=[]
 for p in [WGC,SOB]:
  q=pd.read_csv(p);q=q[q.final_trainable.astype(str).str.lower().eq("true")];z.append(q)
 q=pd.concat([w]+z,ignore_index=True,sort=False)
 q["start_utc"]=pd.to_datetime(q.start_utc,utc=True);q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
 q["year"]=q.start_utc.dt.year;q["y_up"]=(q.direction=="UP").astype(int)
 return q

def panel():
 old=a0.YEARS;a0.YEARS=range(2010,2026)
 try:m,h=a0.load_raw_metals()
 finally:a0.YEARS=old
 q=a0.align_daily_features(targets(),m).dropna(subset=CORE3+["direction","obs_date"]).copy()
 q["year"]=q.start_utc.dt.year;q["y_up"]=(q.direction=="UP").astype(int)
 return q,h

def lr(bal=False):
 return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED,class_weight="balanced" if bal else None)

def structural(p):
 rows=[]
 for (part,win),g0 in p.groupby(["partition","window"],sort=True):
  g=g0.sort_values("start_utc").reset_index(drop=True);teall=g[g.year.isin([2023,2024,2025])].reset_index(drop=True)
  for bs in range(0,len(teall),BLOCK):
   te=teall.iloc[bs:bs+BLOCK];cut=te.start_utc.min();tr=g[(g.end_utc<=cut)&(g.start_utc<cut)]
   if len(tr)<RECENT or tr.y_up.nunique()<2:continue
   X=tr[CORE3].astype(float).to_numpy();Xt=te[CORE3].astype(float).to_numpy()
   sc=StandardScaler().fit(X);m0=lr().fit(sc.transform(X),tr.y_up.to_numpy(int));p0=m0.predict_proba(sc.transform(Xt))[:,1]
   rr=tr.tail(RECENT);Xr=rr[CORE3].astype(float).to_numpy();scr=StandardScaler().fit(Xr)
   mr=lr(True).fit(scr.transform(Xr),rr.y_up.to_numpy(int));pr=mr.predict_proba(scr.transform(Xt))[:,1];p1=.75*p0+.25*pr
   for r,x,y in zip(te.itertuples(index=False),p0,p1):
    rows.append({"model":"A0_CORE3","partition":part,"window":win,"label_date":r.label_date,"start_utc":r.start_utc,"y_up":int(r.y_up),"p_up":float(x)})
    rows.append({"model":"A1_ARCR","partition":part,"window":win,"label_date":r.label_date,"start_utc":r.start_utc,"y_up":int(r.y_up),"p_up":float(y)})
 return pd.DataFrame(rows)

def raw15():
 a=pd.read_csv(R22,usecols=["dt_utc","close"]);b=pd.read_csv(R35,usecols=["dt_utc","close"])
 for q in [a,b]:q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True);q["close"]=pd.to_numeric(q.close,errors="raise")
 q=pd.concat([a,b],ignore_index=True).sort_values("dt_utc").drop_duplicates("dt_utc",keep="last")
 q=q.rename(columns={"dt_utc":"ts","close":"value"});q["available_at_utc"]=q.ts+pd.Timedelta(minutes=15)
 return q

def x1h(q):
 z=q.copy();z["hour"]=z.ts.dt.floor("1h");z["minute"]=z.ts.dt.minute;rows=[]
 for h,g in z.groupby("hour"):
  if len(g)==4 and tuple(sorted(set(map(int,g.minute))))==(0,15,30,45):
   rows.append({"ts":h,"available_at_utc":h+pd.Timedelta(hours=1),"value":float(g.sort_values("ts").iloc[-1].value)})
 return pd.DataFrame(rows)

def path(p):
 p=p.reset_index(drop=True);p["row_id"]=np.arange(len(p));p=r1h.attach(p,x1h(raw15()),"g1h","1h")
 fs=r1h.feature_names("g1h");p=p.dropna(subset=fs+["direction"]);rows=[]
 for (part,win),g0 in p.groupby(["partition","window"],sort=True):
  g=g0.sort_values("start_utc").reset_index(drop=True);teall=g[g.year.isin([2023,2024,2025])].reset_index(drop=True)
  for bs in range(0,len(teall),BLOCK):
   te=teall.iloc[bs:bs+BLOCK];cut=te.start_utc.min();tr=g[(g.end_utc<=cut)&(g.start_utc<cut)]
   if len(tr)<MINPATH or tr.y_up.nunique()<2:continue
   X=tr[fs].astype(float).to_numpy();Xt=te[fs].astype(float).to_numpy();sc=StandardScaler().fit(X)
   m=lr().fit(sc.transform(X),tr.y_up.to_numpy(int));pp=m.predict_proba(sc.transform(Xt))[:,1]
   for r,v in zip(te.itertuples(index=False),pp):
    rows.append({"model":"PATH_GLOBAL_1H","partition":part,"window":win,"label_date":r.label_date,"start_utc":r.start_utc,"y_up":int(r.y_up),"p_up":float(v)})
 return pd.DataFrame(rows)

def main():
 p,h=panel();pred=pd.concat([structural(p),path(p)],ignore_index=True);rows=[]
 for (m,part,win),g in pred.groupby(["model","partition","window"],sort=True):
  rows.append({"model":m,"partition":part,"window":win,**base.metrics(g.y_up,g.p_up)})
 pred.to_csv(OUT/"predictions.csv",index=False);pd.DataFrame(rows).to_csv(OUT/"metrics.csv",index=False)
 out={"status":"STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_COMPLETE","scope":"2025 frozen causal transport; 2023-2025 block phase continuous","metrics":rows,
      "daily_last_obs":str(p.obs_date.max()),"guardrails":["A0/A1 preserve the original 5-row block phase continuously across 2023-2025 and only 2025 rows are reported.","PATH_GLOBAL uses only valid 1h path rows.","No 2025 retuning.","2026 unopened."]}
 (OUT/"summary.json").write_text(json.dumps(out,indent=2,default=str)+"\n");print(json.dumps(out,indent=2,default=str))
if __name__=="__main__":main()
