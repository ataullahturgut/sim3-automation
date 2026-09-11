from __future__ import annotations

import hashlib, json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
from sklearn.calibration import calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data_pipeline/audits/v149_thesis"
CONTRACT=ROOT/"v149_thesis/contracts/short_horizon_rich_panel_freeze_v1.json"
SEED=20260911
SERIES={
 "xag":"XAG_STAKTRAKR_RESEARCH_DAILY_R1","xpt":"XPT_STAKTRAKR_RESEARCH_DAILY_R1","xpd":"XPD_STAKTRAKR_RESEARCH_DAILY_R1",
 "nasdaq":"NASDAQ100_FRED","sp500":"SP500_FRED","djia":"DJIA_FRED","vix":"VIX_CBOE","gvz":"GVZ_CBOE",
 "dgs10":"DGS10_FRB_H15","dff":"DFF_ALFRED_PIT_ME","fx":"DEXCHUS_FRB_H10"}

def frame_hash(d): return hashlib.sha256(d.to_csv(index=False,float_format="%.12g",lineterminator="\n").encode()).hexdigest()
def query(conn,sql,params=None): return pd.read_sql_query(sql,conn,params=params)

def load_panel(conn):
    ny=query(conn,"""select (observation_ts at time zone 'America/New_York')::date date, close
      from xau_intraday_research_cache_1m
      where (observation_ts at time zone 'America/New_York')::time='16:59:00'
      order by observation_ts""")
    ny["date"]=pd.to_datetime(ny.date); ny=ny.drop_duplicates("date",keep=False).reset_index(drop=True)
    if len(ny)<500: raise RuntimeError(f"BLOCKED_INSUFFICIENT_EXACT_NY17:{len(ny)}")
    r=np.log(ny.close).diff()
    for k in [1,2,3]: ny[f"gold_ret_lag{k}"]=r.shift(k-1)
    for k in [3,5,10,20]: ny[f"gold_mom{k}"]=np.log(ny.close/ny.close.shift(k))
    for k in [5,10,20]: ny[f"gold_rv{k}"]=r.rolling(k).std(ddof=0)
    obs=query(conn,"""select series_id, observation_ts::date date, value, available_as_of
      from observations where series_id=any(%s) order by series_id,observation_ts""",(list(SERIES.values()),))
    obs["date"]=pd.to_datetime(obs.date)
    for name,sid in SERIES.items():
        z=obs[obs.series_id==sid].drop_duplicates("date",keep="last").sort_values("date")[["date","value"]]
        z[f"{name}_ret"]=np.log(z.value).diff(); z=z.rename(columns={"date":"source_date","value":f"{name}_level"})
        # One-origin lag is mandatory: a same-date close is never silently assumed available at NY17.
        z["join_date"]=z.source_date
        ny=pd.merge_asof(ny.sort_values("date"),z.sort_values("join_date"),left_on="date",right_on="join_date",direction="backward",allow_exact_matches=False)
        if (ny.source_date>=ny.date).fillna(False).any(): raise RuntimeError(f"FUTURE_SOURCE_{name}")
        ny=ny.drop(columns=["source_date","join_date"])
    states=pd.read_csv(ROOT/"data_pipeline/audits/component_role_replays_v145/ny17_context_role_replay_v145.csv",parse_dates=["date"])
    ny=ny.merge(states.drop(columns=["close","target_month","monthly_reference"]),on="date",how="left")
    macro=query(conn,"""select observation_ts,available_as_of,value,series_id from observations
      where series_id in ('MACRO_EVENT_V3_EMPLOYMENT_SCORE','MACRO_EVENT_V3_INFLATION_SCORE') order by observation_ts""")
    macro["date"]=pd.to_datetime(macro.observation_ts,utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    macro["available_as_of"]=pd.to_datetime(macro.available_as_of,utc=True)
    m=macro.groupby("date").agg(macro_score=("value","sum"),macro_event_count=("value","size"),macro_available=("available_as_of","max")).reset_index()
    ny=ny.merge(m,on="date",how="left"); origin_utc=(ny.date.dt.tz_localize("America/New_York")+pd.Timedelta(hours=17)).dt.tz_convert("UTC")
    bad=ny.macro_available.notna() & (ny.macro_available>origin_utc)
    ny.loc[bad,["macro_score","macro_event_count"]]=np.nan
    ny["macro_event_count"]=ny.macro_event_count.fillna(0); ny["macro_score"]=ny.macro_score.fillna(0)
    return ny

B0=["gold_ret_lag1","gold_ret_lag2","gold_ret_lag3","gold_mom3","gold_mom5","gold_mom10","gold_mom20","gold_rv5","gold_rv10","gold_rv20"]
BLOCKS={"B0":B0,"B1":["xag_ret","xpt_ret","xpd_ret"],"B2":["dgs10_level","dff_level","fx_ret"],"B3":["nasdaq_ret","sp500_ret","djia_ret","vix_level","gvz_level"],"B6":["macro_score","macro_event_count"]}
CONFIGS=[("LOGIT_C01","logit",.1),("LOGIT_C1","logit",1.0),("HGB_D2","hgb",2)]

def estimator(kind,p):
    if kind=="logit": return make_pipeline(StandardScaler(),LogisticRegression(C=p,max_iter=1000,random_state=SEED))
    return HistGradientBoostingClassifier(max_depth=p,max_iter=80,learning_rate=.05,l2_regularization=1,random_state=SEED)

def raw_paths(d,h,cols,end=None):
    ret=np.log(d.close.shift(-h)/d.close); y=(ret>0).astype(float); y.iloc[-h:]=np.nan
    stop=min(end or len(d)-h,len(d)-h); paths={k:{} for k,_,_ in CONFIGS}
    for t in range(120,stop):
        train=[j for j in range(t) if j+h<=t and pd.notna(y.iloc[j]) and d.loc[j,cols].notna().all()]
        if len(train)<120 or not d.loc[t,cols].notna().all(): continue
        for cid,kind,p in CONFIGS:
            model=estimator(kind,p); model.fit(d.loc[train,cols],y.iloc[train].astype(int)); paths[cid][t]=float(model.predict_proba(d.loc[[t],cols])[0,1])
    return paths,y,ret

def prior_best(paths,y,t,h):
    best=None
    for cid,path in paths.items():
        idx=[j for j in path if j<t and j+h<=t and pd.notna(y.iloc[j])]
        if len(idx)<60: continue
        loss=np.mean([(path[j]-y.iloc[j])**2 for j in idx]); cand=(loss,cid,idx)
        if best is None or cand[:2]<best[:2]: best=cand
    return best

def platt(raw,y):
    x=np.asarray(raw); x=np.log(np.clip(x,1e-6,1-1e-6)/(1-np.clip(x,1e-6,1-1e-6)))[:,None]
    m=LogisticRegression(C=1,max_iter=1000,random_state=SEED).fit(x,np.asarray(y,int)); return m

def replay(d,h,cols,start):
    paths,y,ret=raw_paths(d,h,cols); out=[]
    for t in range(start,len(d)-h):
        sel=prior_best(paths,y,t,h)
        if not sel or t not in paths[sel[1]]: continue
        _,cid,idx=sel; cal=platt([paths[cid][j] for j in idx],y.iloc[idx]); raw=paths[cid][t]
        p=float(cal.predict_proba([[math.log(raw/(1-raw))]])[0,1]); mature=[j for j in range(t) if j+h<=t and pd.notna(y.iloc[j])]
        freq=(y.iloc[mature].sum()+.5)/(len(mature)+1)
        out.append({"origin_index":t,"origin_date":d.date.iloc[t],"target_date":d.date.iloc[t+h],"y":int(y.iloc[t]),"return":ret.iloc[t],"p":p,"p50":.5,"pfreq":freq,"config":cid,"calibration_n":len(idx)})
    return pd.DataFrame(out)

def metrics(f):
    if f.empty:
        return {"status":"BLOCKED_INSUFFICIENT_COMPLETE_CASE","n":0}
    out={}
    for k in ["p","p50","pfreq"]:
        p=f[k].to_numpy(); y=f.y.to_numpy(); out[k]={"n":len(f),"brier":brier_score_loss(y,p),"log_loss":log_loss(y,p),"balanced_accuracy":balanced_accuracy_score(y,p>=.5)}
    try:
        slope=platt(f.p,f.y); out["calibration"]={"intercept":float(slope.intercept_[0]),"slope":float(slope.coef_[0,0])}
    except Exception: out["calibration"]={"status":"NOT_PROVEN"}
    return out

def main():
    freeze=json.loads(CONTRACT.read_text()); assert freeze["status"]=="FROZEN_BEFORE_RICH_PANEL_SCORING"
    OUT.mkdir(parents=True,exist_ok=True)
    with psycopg.connect(os.environ["NEON_DATABASE_URL"]) as conn: d=load_panel(conn)
    dev_end=int(np.searchsorted(d.date.values,np.datetime64("2025-01-01")))
    coverage={b:int(d[cols].notna().all(axis=1).sum()) for b,cols in BLOCKS.items()}
    print(json.dumps({"origin_rows":len(d),"development_end_index":dev_end,"complete_case_coverage":coverage},sort_keys=True))
    audit={}; retained=["B0"]
    base_cols=B0
    for b in ["B1","B2","B3","B6"]:
        trial=base_cols+BLOCKS[b]; row={}
        for h in [1,3]:
            a=replay(d.iloc[:dev_end].copy(),h,base_cols,180); z=replay(d.iloc[:dev_end].copy(),h,trial,180)
            ma,mz=metrics(a),metrics(z)
            gain=None if "p" not in ma or "p" not in mz else ma["p"]["brier"]-mz["p"]["brier"]
            row[f"{h}D"]={"base":ma,"trial":mz,"brier_gain":gain}
        keep=all(row[f"{h}D"]["brier_gain"] is not None and row[f"{h}D"]["brier_gain"]>=.002 and row[f"{h}D"]["trial"]["p"]["log_loss"]<=row[f"{h}D"]["base"]["p"]["log_loss"] for h in [1,3])
        row["decision"]="RETAIN" if keep else "REDUNDANT_NOT_PROVEN"; audit[b]=row
        if keep: retained.append(b); base_cols=trial
    summary={"contract":freeze["contract_id"],"evidence_class":freeze["evidence_class"],"origins":len(d),"development_end_index":dev_end,"complete_case_coverage":coverage,"retained_blocks":retained,"incremental_audit":audit,"outer":{},"auto_selector":"OFF","auto_ensemble":"OFF","production_authority":False,"production_writes":"NONE"}
    for h in [1,3]:
        f=replay(d,h,base_cols,dev_end); f.to_csv(OUT/f"rich_{h}d_outer.csv",index=False)
        mm=metrics(f); gain=mm["p50"]["brier"]-mm["p"]["brier"]
        mm["promotion"]="ELIGIBLE_FOR_PROSPECTIVE_SHADOW" if gain>=.005 and mm.get("calibration",{}).get("slope",0)>=.5 and abs(mm.get("calibration",{}).get("intercept",99))<=.25 else "NOT_PROVEN"
        summary["outer"][f"NEXT_NY17_{h}D"]=mm
    summary["panel_hash"]=frame_hash(d); summary["output_hashes"]={str(h):frame_hash(pd.read_csv(OUT/f"rich_{h}d_outer.csv")) for h in [1,3]}
    (OUT/"rich_short_horizon_results.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__": main()
