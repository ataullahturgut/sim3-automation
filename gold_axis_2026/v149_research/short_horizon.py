from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from gold_axis_2026.hs_sdl_dma_v1.model import apply_platt, binary_log_loss, fit_platt
from .common import canonical_frame_hash, sha256_file
from .stats import circular_block_superior_set

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data_pipeline/audits/component_role_replays_v145/ny17_context_role_replay_v145.csv"
MIN_TRAIN=80
MIN_CAL=40
EPS=1e-6

BLOCK0=["ret_1","ret_2","ret_3","mom_3","mom_5","mom_10","rv_5","rv_10","rv_20"]
BLOCK4_PREFIXES=["fast_state__","slow_state__","monthly_direction_3m__","emergency_level__","emergency_reversal__"]
LEVELS={
 "fast_state":["MIXED","ROBUST_DOWN","ROBUST_UP"],
 "slow_state":["NOT_YET_ROBUST","ROBUST_DOWN","ROBUST_UP"],
 "monthly_direction_3m":["NEUTRAL","DOWN","UP"],
 "emergency_level":["NEUTRAL","DOWN","UP"],
 "emergency_reversal":["OFF","DOWN_ALERT","UP_ALERT"],
}


def load_features() -> pd.DataFrame:
    d=pd.read_csv(SOURCE,parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    if d.date.duplicated().any(): raise ValueError("DUPLICATE_ORIGIN")
    r=np.log(d.close).diff()
    d["ret_1"]=r
    d["ret_2"]=r.shift(1)
    d["ret_3"]=r.shift(2)
    for k in [3,5,10]: d[f"mom_{k}"]=np.log(d.close/d.close.shift(k))
    for k in [5,10,20]: d[f"rv_{k}"]=r.rolling(k,min_periods=k).std(ddof=0)
    for field,levels in LEVELS.items():
        unknown=set(d[field].dropna().unique())-set(levels)
        if unknown: raise ValueError(f"UNKNOWN_STATE_{field}_{sorted(unknown)}")
        if d[field].isna().any(): raise ValueError(f"MISSING_STATE_{field}")
        for level in levels[1:]: d[f"{field}__{level}"]=(d[field]==level).astype(float)
    return d


def feature_columns(blocks: list[int]) -> list[str]:
    cols=list(BLOCK0)
    if 4 in blocks:
        cols += [f"{field}__{level}" for field,levels in LEVELS.items() for level in levels[1:]]
    return cols


def target_arrays(d: pd.DataFrame,h: int):
    ret=np.log(d.close.shift(-h)/d.close)
    y=(ret>0).astype(float)
    y.iloc[-h:]=np.nan
    return y,ret


def model_configs():
    return [
      ("LOGISTIC_C0.1", "LOGISTIC", {"C":0.1}),
      ("LOGISTIC_C1", "LOGISTIC", {"C":1.0}),
      ("LOGISTIC_C10", "LOGISTIC", {"C":10.0}),
      ("GBRT_D1", "GBRT", {"max_depth":1,"learning_rate":0.05,"n_estimators":60}),
      ("GBRT_D2", "GBRT", {"max_depth":2,"learning_rate":0.05,"n_estimators":60}),
      ("HISTGB_D2", "HISTGB", {"max_depth":2,"learning_rate":0.05,"max_iter":60}),
      ("HISTGB_D3", "HISTGB", {"max_depth":3,"learning_rate":0.05,"max_iter":60}),
    ]


def _classifier(kind,params):
    if kind=="LOGISTIC": return make_pipeline(StandardScaler(),LogisticRegression(C=params["C"],solver="lbfgs",max_iter=500,random_state=20260911))
    if kind=="GBRT": return GradientBoostingClassifier(random_state=20260911,**params)
    if kind=="HISTGB": return HistGradientBoostingClassifier(random_state=20260911,l2_regularization=1.0,**params)
    raise ValueError(kind)


def _regressor(kind,params):
    if kind=="LOGISTIC": return make_pipeline(StandardScaler(),Ridge(alpha=1.0))
    if kind=="GBRT": return GradientBoostingRegressor(random_state=20260911,loss="huber",**params)
    if kind=="HISTGB": return HistGradientBoostingRegressor(random_state=20260911,l2_regularization=1.0,**params)
    raise ValueError(kind)


def raw_paths(d:pd.DataFrame,h:int,blocks:list[int],end_index:int|None=None,configs=None):
    cols=feature_columns(blocks); X=d[cols]
    y,ret=target_arrays(d,h)
    stop=len(d)-h if end_index is None else min(end_index,len(d)-h)
    configs=model_configs() if configs is None else configs
    paths={cid:{} for cid,_,_ in configs}; rpaths={cid:{} for cid,_,_ in configs}
    for t in range(20,stop):
        train=[j for j in range(t) if j+h<=t and pd.notna(y.iloc[j]) and X.iloc[j].notna().all()]
        if len(train)<MIN_TRAIN or not X.iloc[t].notna().all(): continue
        yy=y.iloc[train].astype(int).to_numpy(); rr=ret.iloc[train].to_numpy(float)
        if len(np.unique(yy))<2: continue
        for cid,kind,params in configs:
            clf=_classifier(kind,params); clf.fit(X.iloc[train],yy)
            p=float(np.clip(clf.predict_proba(X.iloc[[t]])[0,1],EPS,1-EPS)); paths[cid][t]=p
            reg=_regressor(kind,params); reg.fit(X.iloc[train],rr); rpaths[cid][t]=float(reg.predict(X.iloc[[t]])[0])
    return paths,rpaths,y,ret


def _select_prior(paths,target,t,h,loss):
    choices=[]
    for cid,path in paths.items():
        prior=[j for j in sorted(path) if j<t and j+h<=t and pd.notna(target.iloc[j])]
        if len(prior)<MIN_CAL: continue
        pred=np.array([path[j] for j in prior]); yy=target.iloc[prior].to_numpy(float)
        score=float(np.mean((pred-yy)**2)) if loss=="squared" else binary_log_loss(pred,yy)
        choices.append((score,cid,prior))
    return min(choices,key=lambda x:(x[0],x[1])) if choices else None


def development_block_audit(dev_end_index:int=240) -> dict:
    d=load_features(); result={}
    parsimonious=[c for c in model_configs() if c[1]=="LOGISTIC"]
    for h in [1,3]:
        variants={}
        for name,blocks in [("BLOCK0",[0]),("BLOCK0_PLUS_BLOCK4",[0,4])]:
            paths,_,y,_=raw_paths(d,h,blocks,end_index=dev_end_index,configs=parsimonious)
            rec=[]
            for t in range(dev_end_index):
                sel=_select_prior(paths,y,t,h,"brier")
                if not sel or pd.isna(y.iloc[t]): continue
                _,cid,prior=sel
                cal=[j for j in prior if j in paths[cid]]
                if len(cal)<MIN_CAL: continue
                coef=fit_platt([paths[cid][j] for j in cal],y.iloc[cal].astype(int),epsilon=EPS)
                rec.append((t,apply_platt(paths[cid][t],coef,EPS),int(y.iloc[t])))
            p=np.array([x[1] for x in rec]); yy=np.array([x[2] for x in rec])
            variants[name]={"n":len(rec),"brier":float(np.mean((p-yy)**2)),"log_loss":binary_log_loss(p,yy)}
        gain=variants["BLOCK0"]["brier"]-variants["BLOCK0_PLUS_BLOCK4"]["brier"]
        retain=gain>=0.002 and variants["BLOCK0_PLUS_BLOCK4"]["log_loss"]<=variants["BLOCK0"]["log_loss"]
        result[f"NEXT_NY17_{h}D"]={"variants":variants,"block4_brier_gain":gain,"block4_decision":"RETAIN" if retain else "REDUNDANT_NOT_PROVEN"}
    return result


def run_outer(freeze:dict) -> tuple[dict[str,pd.DataFrame],dict]:
    d=load_features(); frames={}; summary={}
    hs={h:pd.read_csv(ROOT/f"data_pipeline/audits/hs_sdl_dma_replay_v1/hs_sdl_dma_{h}d_outer.csv") for h in [1,3]}
    for h in [1,3]:
        key=f"NEXT_NY17_{h}D"; blocks=freeze["short_horizon"][key]["retained_blocks"]
        paths,rpaths,y,ret=raw_paths(d,h,blocks)
        records=[]; family_records={cid:[] for cid,_,_ in model_configs()}
        for t in range(freeze["short_horizon"][key]["outer_start_index"],len(d)-h):
            sel=_select_prior(paths,y,t,h,"brier"); rsel=_select_prior(rpaths,ret,t,h,"squared")
            if not sel or not rsel or t not in paths.get(sel[1],{}) or t not in rpaths.get(rsel[1],{}): continue
            _,cid,prior=sel; _,rcid,_=rsel
            coef=fit_platt([paths[cid][j] for j in prior],y.iloc[prior].astype(int),epsilon=EPS)
            p=apply_platt(paths[cid][t],coef,EPS)
            matured=[j for j in range(t) if j+h<=t and pd.notna(y.iloc[j])]
            freq=(float(y.iloc[matured].sum())+0.5)/(len(matured)+1.0)
            hsm=hs[h]; match=hsm[hsm.origin_date==d.at[t,"date"].strftime("%Y-%m-%d")]
            records.append({"origin_index":t,"origin_date":d.at[t,"date"],"target_date":d.at[t+h,"date"],"y":int(y.iloc[t]),"realized_return":float(ret.iloc[t]),"p_cal":p,"expected_return":rpaths[rcid][t],"p_50":0.5,"p_frequency":freq,"p_hs_sdl_dma":float(match.p_cal.iloc[0]) if len(match) else np.nan,"probability_config":cid,"return_config":rcid,"calibration_n":len(prior),"calibration_intercept":float(coef[0]),"calibration_slope":float(coef[1])})
            for family_id,path in paths.items():
                fprior=[j for j in sorted(path) if j<t and j+h<=t and pd.notna(y.iloc[j])]
                if t not in path or len(fprior)<MIN_CAL: continue
                fcoef=fit_platt([path[j] for j in fprior],y.iloc[fprior].astype(int),epsilon=EPS)
                family_records[family_id].append((t,apply_platt(path[t],fcoef,EPS),int(y.iloc[t])))
        f=pd.DataFrame(records); frames[key]=f
        probs={"V149":f.p_cal,"P50":f.p_50,"UP_FREQUENCY":f.p_frequency}
        if f.p_hs_sdl_dma.notna().all(): probs["HS_SDL_DMA_V1"]=f.p_hs_sdl_dma
        metrics={}
        losses={}
        for name,p in probs.items():
            pp=np.asarray(p,float); yy=f.y.to_numpy(float); pred=pp>=0.5
            metrics[name]={"n":len(f),"brier":float(np.mean((pp-yy)**2)),"log_loss":binary_log_loss(pp,yy),"accuracy":float(np.mean(pred==yy)),"balanced_accuracy":float((np.mean(pred[yy==1])+np.mean(~pred[yy==0]))/2)}
            losses[name]=(pp-yy)**2
        cal=fit_platt(f.p_cal,f.y,lam=0.0,epsilon=EPS) if len(f.y.unique())==2 else [None,None]
        rerr=f.expected_return-f.realized_return
        stability={"first_half_brier":float(np.mean((f.p_cal.iloc[:len(f)//2]-f.y.iloc[:len(f)//2])**2)),"second_half_brier":float(np.mean((f.p_cal.iloc[len(f)//2:]-f.y.iloc[len(f)//2:])**2)),"worst_origin":f.loc[((f.p_cal-f.y)**2).idxmax(),"origin_date"].strftime("%Y-%m-%d")}
        inference=circular_block_superior_set(losses,block=max(3,h+1),seed=20260911+h)
        improvement=metrics["P50"]["brier"]-metrics["V149"]["brier"]
        promoted=improvement>=0.005 and cal[1] is not None and 0.5<=cal[1]<=1.5 and abs(cal[0])<=0.25 and stability["second_half_brier"]<=stability["first_half_brier"]+0.02
        family_metrics={}
        for family_id,vals in family_records.items():
            pp=np.array([v[1] for v in vals]); yy=np.array([v[2] for v in vals])
            family_metrics[family_id]={"n":len(vals),"brier":float(np.mean((pp-yy)**2)),"log_loss":binary_log_loss(pp,yy),"accuracy":float(np.mean((pp>=0.5)==yy))}
        summary[key]={"blocks":blocks,"metrics":metrics,"model_family_metrics":family_metrics,"selected_probability_config_counts":f.probability_config.value_counts().sort_index().to_dict(),"selected_return_config_counts":f.return_config.value_counts().sort_index().to_dict(),"calibration":{"intercept":None if cal[0] is None else float(cal[0]),"slope":None if cal[1] is None else float(cal[1])},"expected_return":{"mae":float(np.mean(abs(rerr))),"rmse":float(np.sqrt(np.mean(rerr**2))),"direction_accuracy":float(np.mean((f.expected_return>0)==(f.realized_return>0)))},"stability":stability,"dependence_aware_inference":inference,"promotion":"ELIGIBLE_FOR_PROSPECTIVE_SHADOW" if promoted else "NOT_PROVEN","future_target_violations":0}
    return frames,summary


def inventory() -> dict:
    d=load_features()
    return {
      "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha256_file(SOURCE),"origins":len(d),"first_origin":d.date.min().strftime("%Y-%m-%d"),"last_origin":d.date.max().strftime("%Y-%m-%d"),
      "targets":{"NEXT_NY17_1D":len(d)-1,"NEXT_NY17_3D":len(d)-3,"TODAY_TO_NY17":"BLOCKED_CONTRACT"},
      "blocks":{"0":{"status":"READY_TO_REPLAY","features":BLOCK0,"clock":"completed NY17 anchors only"},"1":{"status":"BLOCKED_CONTRACT","reason":"cross-metal daily timestamps are not proven at the exact NY17 origin clock"},"2":{"status":"BLOCKED_PIT","reason":"FX/rate month-end PIT snapshots do not supply daily NY17-origin history"},"3":{"status":"BLOCKED_PIT","reason":"risk/equity histories in production were retrieved after historical origins or lack NY17 parity"},"4":{"status":"READY_TO_REPLAY","reason":"frozen chronological context replay; context semantics retained, not votes"},"5":{"status":"BLOCKED_PIT","reason":"no governed historical positioning/flow/news timestamp panel"}},
      "evidence_class":"RETROSPECTIVE_HISTORICAL_RECONSTRUCTION_NOT_PROSPECTIVE"
    }
