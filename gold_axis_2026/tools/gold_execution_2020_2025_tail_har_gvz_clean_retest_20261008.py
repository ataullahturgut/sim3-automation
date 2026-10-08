"""Strict clean-source old magnitude-risk model rerun (NOT directional UP/DOWN).
Rebuild 2022-25 overnight source targets and historical prior-matured RV5/20/60.
Re-use original HAR/GVZ logit and signed-tail ridge functions unmodified.
GVZ joins strictly D-1, no 2025 model re-fit. Respect later Friday 64h flags.
No forecast policy reselected and no PIT quote-release guarantee asserted.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,time,os
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,average_precision_score
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/'tools'))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as common
import gold_execution_har_gvz_warmup2022_20261008 as h
import gold_execution_gvz_signed_tail_hazard_20261008 as sg
NAME="GOLD_EXECUTION_2020_2025_TAIL_HAR_GVZ_CLEAN_SOURCE_RETEST_20261008"
OUT=AX/(NAME+"_METRICS.csv")
SUMMARY=AX/(NAME+"_SUMMARY.json")
PRED=AX/(NAME+"_PREDICTIONS.csv")
GVZ=AX/'GOLD_GVZCLS_RAW_2021_2025.csv'
FEATURES={"HAR":["score"],"GVZ":["gvz"],"HAR_GVZ":["score","gvz"]}
SIGNED={"SCORE":["logscore"],"GVZ":["loggvz"],"SCORE_GVZ":["logscore","loggvz"]}
def data():
    _,target=common.source_load()
    z=target[(target.year>=2022)&target.ret_OVN.notna()].copy().sort_values('date')
    z["r"]=z.ret_OVN.astype(float)
    z["event_abs1"]=z.r.abs().ge(.01).astype(int)
    z["event_down1"]=z.r.le(-.01).astype(int)
    z["event_up1"]=z.r.ge(.01).astype(int)
    z["is_weekend_64h"]=(z.date.dt.dayofweek==4)
    # Strict lag: today's target cannot be included at its own decision origin.
    for k in (5,20,60):
        z[f"rv{k}"]=np.sqrt(z.r.pow(2).shift(1).rolling(k,min_periods=k).mean())
    z["score"]=np.sqrt(.5*z.rv5.pow(2)+.3*z.rv20.pow(2)+.2*z.rv60.pow(2))
    g=pd.read_csv(GVZ,usecols=["date","value"]).rename(columns={'date':'gvz_date','value':'gvz'})
    g['gvz_date']=pd.to_datetime(g.gvz_date);g["gvz"]=pd.to_numeric(g.gvz,errors='coerce')
    g=g.dropna().sort_values('gvz_date').drop_duplicates('gvz_date',keep='last')
    z=pd.merge_asof(z.sort_values('date'),g,left_on='date',right_on='gvz_date',
         direction='backward',allow_exact_matches=False)
    z=z[(z.score>0)&(z.gvz>0)].copy().reset_index(drop=True)
    assert (z.gvz_date<z.date).all()
    assert z[z.year==2022].shape[0]>160 and z[z.year==2023].shape[0]>200
    z["y"]=z.event_abs1.astype(int)  # original HAR helper expects the binary absolute-tail label in y
    z["logscore"]=np.log(z.score)
    z["loggvz"]=np.log(z.gvz)
    z['tail1']=z.event_abs1
    z['target_down']=z.event_down1
    z['target_up']=z.event_up1
    return z
def evaluate(z):
    frozen=z[z.year<=2024].copy()
    if len(frozen)<650:raise RuntimeError("RISK_TRAINING_TOO_SHORT")
    models={name:h.fit_model(frozen,feats) for name,feats in FEATURES.items()}
    out=[]
    for i,r in z.iterrows():
        if r.year<2023:continue
        hist=frozen if r.year==2025 else z.iloc[:i]
        if len(hist)<120:continue
        if not (hist.date<r.date).all():raise RuntimeError("RISK_FUTURE_LABEL_LEAK")
        q={"date":r.date.strftime("%Y-%m-%d"),"year":int(r.year),
           "hold_type":"FRI_TO_MON_64H" if r.is_weekend_64h else "WEEKDAY_16H",
           "train_n":len(hist),"y_abs":int(r.event_abs1),
           "y_down":int(r.event_down1),"y_up":int(r.event_up1),
           "event_magnitude_abs_logreturn":abs(r.r),
           "rvscore_known_at_origin":float(r.score),
           "gvz_asof":r.gvz_date.strftime("%Y-%m-%d")}
        q["prob_abs_BASE"]=float((1+hist.event_abs1.sum())/(2+len(hist)))
        for name,cols in FEATURES.items():
            fun=models[name] if r.year==2025 else h.fit_model(hist,cols)
            q["prob_abs_"+name]=float(fun(r))
        for side,col in [("down","target_down"),("up","target_up")]:
            q["prob_"+side+"_BASE"]=float((1+hist[col].sum())/(2+len(hist)))
            for name,cols in SIGNED.items():
                q["prob_"+side+"_"+name]=sg.regularized_logit_prediction(hist,r,col,cols)
        out.append(q)
    return pd.DataFrame(out)

def metrics(p):
    rows=[]
    for year,g in p.groupby('year'):
        for side,yi,choices in [
          ("ABS_1PCT","y_abs",["BASE","HAR","GVZ","HAR_GVZ"]),
          ("DOWN_1PCT","y_down",["BASE","SCORE","GVZ","SCORE_GVZ"]),
          ("UP_1PCT","y_up",["BASE","SCORE","GVZ","SCORE_GVZ"])]:
            for model in choices:
                s="prob_abs_"+model if side=="ABS_1PCT" else "prob_"+side.split("_")[0].lower()+"_"+model
                y=g[yi].to_numpy(int); prob=g[s].to_numpy(float)
                if not ((prob>0)&(prob<1)).all():raise RuntimeError("INVALID_RISK_PROBABILITY")
                rows.append({"year":int(year),"risk_type":side,"method":model,
                  "n":len(g),"event_count":int(y.sum()),
                  "brier":float(np.mean((prob-y)**2)),
                  "roc_auc":float(roc_auc_score(y,prob)) if len(np.unique(y))==2 else None,
                  "avg_precision":float(average_precision_score(y,prob)) if len(np.unique(y))==2 else None,
                  "mean_prob":float(prob.mean())})
    return pd.DataFrame(rows)

def main():
    t0=time.time();z=data()
    p=evaluate(z);m=metrics(p)
    PRED.parent.mkdir(parents=True,exist_ok=True)
    p.to_csv(PRED,index=False)
    m.to_csv(OUT,index=False)
    r={"status":"ORIGINAL_TAIL_RISK_MODELS_RERUN_ON_AUDITED_BID_SOURCE",
       "original_method_families":["HAR_LOGISTIC_RV5_20_60","GVZ_D1","HAR_GVZ","SIGNED_SCORE","SIGNED_GVZ","SIGNED_SCORE_GVZ"],
       "scope":"MAGNITUDE_PROBABILITY_ONLY_NOT_UP_DOWN_DIRECTION_FORECAST",
       "source_id":common.SOURCE,"gvz_pit":"D-1 observation dates strictly older than trade origin; historical release-lag metadata not independently audited",
       "origin":"17:00 Europe/Istanbul","source_2020_2025_bars":141890,
       "risk_data_history":"2022 source-complete warmup; 2023-24 prequential; 2025 frozen past history",
       "2025_warning":"RETROSPECTIVE archive already inspected, not future OOS",
       "2019_2021_note":"Years 2020-21 were source-verified but are not reused for this earlier published model's GVZ warmup contract",
       "macro_calendar":"Not used, incomplete event ledger never turned into no-event records",
       "run_date":"2026-10-08","risk_predictions":len(p),
       "target_quality_gate":"Only source-mature overnight returns; prior realized targets lagged once before each decision, including different Friday weekend hold type",
       "2025_not_for_feature_selection":True,"no_direction_promoted":True,
       "data_value_touched":False,"existing_forecast_unchanged":True,
       "metrics_file":OUT.name,"forecast_artifact":PRED.name,
       "elapsed_seconds":int(time.time()-t0)}
    SUMMARY.write_text(json.dumps(r,indent=2)+"\n")
    print("RISK_MODEL_RETEST_COMPLETED",json.dumps(r),flush=True)
    print(m.to_string(index=False),flush=True)
if __name__=='__main__':main()
